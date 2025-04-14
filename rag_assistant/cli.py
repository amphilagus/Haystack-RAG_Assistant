"""
Command-Line Interface (CLI) Module

This module provides a command-line interface for the RAG assistant.
"""

import os
import argparse
from typing import Optional
from dotenv import load_dotenv

from document_loader import load_documents, chunk_documents
from rag_pipeline import RAGPipeline

# 尝试多种方式加载环境变量
def get_api_key(cmd_api_key: Optional[str] = None) -> Optional[str]:
    """
    尝试多种方式获取API密钥
    
    Args:
        cmd_api_key: 从命令行参数获取的API密钥
        
    Returns:
        API密钥或None
    """
    # 如果通过命令行提供，优先使用
    if cmd_api_key:
        return cmd_api_key
        
    # 尝试从环境变量获取
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # 尝试加载.env文件
    load_dotenv(override=True)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # 尝试直接从.env文件读取
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(current_dir, '.env')
        if os.path.isfile(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY'):
                        api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                        # 手动设置环境变量
                        os.environ["OPENAI_API_KEY"] = api_key
                        return api_key
    except Exception as e:
        print(f"Error reading .env file directly: {e}")
    
    return None

def setup_arg_parser() -> argparse.ArgumentParser:
    """
    Set up the argument parser for the CLI.
    
    Returns:
        Argument parser
    """
    parser = argparse.ArgumentParser(
        description="Local Knowledge Base RAG Assistant",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Command to add documents
    parser.add_argument(
        "--add-docs",
        type=str,
        help="Path to directory containing documents to add to the knowledge base"
    )
    
    # Model parameters
    parser.add_argument(
        "--embedding-model",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Model to use for document and query embedding"
    )
    
    parser.add_argument(
        "--llm-model",
        type=str,
        default="gpt-4o-mini",
        help="LLM model to use for answer generation"
    )
    
    parser.add_argument(
        "--top-k",
        type=int,
        default=20,
        help="Number of documents to retrieve for each query"
    )
    
    # Chunking parameters
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Maximum size of document chunks"
    )
    
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Overlap between document chunks"
    )
    
    # API key
    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API key (if not set as environment variable)"
    )
    
    # Persistent directory for Chroma
    parser.add_argument(
        "--persist-dir",
        type=str,
        default="chroma_db",
        help="Directory for persistent storage of document embeddings"
    )
    
    # Collection name
    parser.add_argument(
        "--collection",
        type=str,
        default="documents",
        help="Name of the Chroma collection to use. If it doesn't exist, a new one will be created."
    )
    
    # Reset collection
    parser.add_argument(
        "--reset-collection",
        action="store_true",
        help="Reset the collection. By default, this creates a new collection with timestamp."
    )
    
    # Hard reset
    parser.add_argument(
        "--hard-reset",
        action="store_true",
        help="When used with --reset-collection, completely deletes the existing collection instead of creating a new one with timestamp."
    )
    
    return parser

def main():
    """Main entry point for the CLI."""
    parser = setup_arg_parser()
    args = parser.parse_args()
    
    # 获取API密钥
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: OpenAI API key not found. Please provide it using one of these methods:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Add OPENAI_API_KEY=your_key to your .env file")
        print("3. Provide it with the --api-key parameter")
        return
    
    print(f"Using API key: {api_key[:5]}...{api_key[-5:]}")
    
    # Show warning if using hard reset
    if args.reset_collection and args.hard_reset:
        print(f"\nWARNING: You are about to completely delete collection '{args.collection}'.")
        confirm = input("Are you sure you want to proceed? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
    
    # 初始化RAG流水线
    try:
        rag_pipeline = RAGPipeline(
            embedding_model=args.embedding_model,
            llm_model=args.llm_model,
            top_k=args.top_k,
            api_key=api_key,
            persist_dir=args.persist_dir,
            collection_name=args.collection,
            reset_collection=args.reset_collection,
            hard_reset=args.hard_reset
        )
        
        # Show model introduction
        model_intro = rag_pipeline.get_model_introduction()
        print(f"\n{model_intro}\n")
        
        # 如果指定了文档目录，加载文档
        if args.add_docs:
            print(f"Loading documents from {args.add_docs}...")
            documents = load_documents(args.add_docs)
            
            if documents:
                print(f"Loaded {len(documents)} documents.")
                print(f"Chunking documents with size={args.chunk_size}, overlap={args.chunk_overlap}...")
                chunked_documents = chunk_documents(documents, args.chunk_size, args.chunk_overlap)
                print(f"Created {len(chunked_documents)} chunks.")
                
                rag_pipeline.add_documents(chunked_documents)
            else:
                print("No documents found.")
        
        # 交互式查询循环
        print("\n=== Local Knowledge Base RAG Assistant ===")
        print("Type 'exit' to quit.")
        
        while True:
            query = input("\nEnter your question: ")
            
            if query.lower() in ['exit', 'quit']:
                break
            
            if not query.strip():
                continue
            
            try:
                answer = rag_pipeline.get_answer(query)
                print(f"\nAnswer: {answer}")
            except Exception as e:
                print(f"Error: {e}")
    except Exception as e:
        print(f"Error initializing RAG pipeline: {e}")

if __name__ == "__main__":
    main() 