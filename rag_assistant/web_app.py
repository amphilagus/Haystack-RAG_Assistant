"""
Web Interface Module

This module provides a web interface for the RAG assistant using Streamlit.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from typing import List, Optional
import chromadb

from document_loader import load_documents, chunk_documents
from rag_pipeline import RAGPipeline

# Try to load API key from various sources
def get_api_key() -> Optional[str]:
    """
    Try to get API key from various sources
    
    Returns:
        API key or None
    """
    # Try from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # Try to load from .env file
    load_dotenv(override=True)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # Try to read directly from .env file
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(current_dir, '.env')
        if os.path.isfile(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY'):
                        api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                        # Manually set environment variable
                        os.environ["OPENAI_API_KEY"] = api_key
                        return api_key
    except Exception as e:
        st.error(f"Error reading .env file directly: {e}")
    
    return None

# Load API key
api_key = get_api_key()

# Session state initialization
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = None
if "documents_loaded" not in st.session_state:
    st.session_state.documents_loaded = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "collection_name" not in st.session_state:
    st.session_state.collection_name = "documents"
if "persist_dir" not in st.session_state:
    st.session_state.persist_dir = "chroma_db"
if "show_delete_confirm" not in st.session_state:
    st.session_state.show_delete_confirm = False
if "chunk_overlap" not in st.session_state:
    st.session_state.chunk_overlap = 50
if "current_model" not in st.session_state:
    st.session_state.current_model = "gpt-4o-mini"

def get_collections(persist_dir: str) -> List[str]:
    """
    Get all existing collections in the specified directory
    
    Args:
        persist_dir: ChromaDB storage directory
    
    Returns:
        List[str]: Collection name list
    """
    try:
        if not os.path.exists(persist_dir):
            return []
            
        client = chromadb.PersistentClient(path=persist_dir)
        collections = client.list_collections()
        return [col.name for col in collections]
    except Exception as e:
        st.warning(f"Unable to get existing collections: {e}")
        return []

def get_collection_info(persist_dir: str, collection_name: str) -> dict:
    """
    Get information about the specified collection
    
    Args:
        persist_dir: ChromaDB storage directory
        collection_name: Collection name
        
    Returns:
        dict: Collection information, including document count
    """
    try:
        if not os.path.exists(persist_dir):
            return {"exists": False, "count": 0}
            
        client = chromadb.PersistentClient(path=persist_dir)
        collections = client.list_collections()
        collection_names = [col.name for col in collections]
        
        if collection_name in collection_names:
            collection = client.get_collection(collection_name)
            count = collection.count()
            return {"exists": True, "count": count}
        return {"exists": False, "count": 0}
    except Exception as e:
        st.warning(f"Unable to get collection info: {e}")
        return {"exists": False, "count": 0, "error": str(e)}

def delete_all_documents(persist_dir: str, collection_name: str) -> bool:
    """
    Delete all documents in the collection
    
    Args:
        persist_dir: ChromaDB storage directory
        collection_name: Collection name
        
    Returns:
        bool: Whether deletion was successful
    """
    try:
        if not os.path.exists(persist_dir):
            return False
            
        client = chromadb.PersistentClient(path=persist_dir)
        collections = client.list_collections()
        collection_names = [col.name for col in collections]
        
        if collection_name in collection_names:
            collection = client.get_collection(collection_name)
            # Get all document IDs
            result = collection.get()
            if result and "ids" in result and result["ids"]:
                # Delete all documents
                collection.delete(result["ids"])
                return True
            return True  # No documents is also considered success
        return False
    except Exception as e:
        st.error(f"Error deleting documents: {e}")
        import traceback
        st.error(traceback.format_exc())
        return False

def initialize_pipeline(api_key: str, embedding_model: str, llm_model: str, top_k: int, 
                        collection_name: str, reset_collection: bool = False, hard_reset: bool = False) -> None:
    """
    Initialize the RAG pipeline.
    
    Args:
        api_key: OpenAI API key
        embedding_model: Model to use for document and query embedding
        llm_model: LLM model to use for answer generation
        top_k: Number of documents to retrieve
        collection_name: Name of the collection to use
        reset_collection: Whether to reset the collection
        hard_reset: If True, completely delete the collection instead of creating a new one with timestamp
    """
    try:
        # Check if model has changed
        model_changed = "current_model" in st.session_state and st.session_state.current_model != llm_model
        
        st.session_state.rag_pipeline = RAGPipeline(
            embedding_model=embedding_model,
            llm_model=llm_model,
            top_k=top_k,
            api_key=api_key,
            persist_dir=st.session_state.persist_dir,
            collection_name=collection_name,
            reset_collection=reset_collection,
            hard_reset=hard_reset
        )
        
        # Save current model
        st.session_state.current_model = llm_model
        
        # Get model introduction
        model_intro = st.session_state.rag_pipeline.get_model_introduction()
        
        # Display different message depending on whether model was changed
        if model_changed:
            st.session_state.model_message = f"Model switched to {llm_model}. {model_intro}"
        else:
            st.session_state.model_message = f"Pipeline initialized with {llm_model}. {model_intro}"
        
        return True
    except Exception as e:
        st.error(f"Error initializing pipeline: {e}")
        return False

def load_and_process_documents(directory_path: str, chunk_size: int, chunk_overlap: int) -> None:
    """
    Load and process documents from a directory.
    
    Args:
        directory_path: Path to the directory containing documents
        chunk_size: Maximum size of document chunks
        chunk_overlap: Overlap between document chunks
    """
    try:
        with st.spinner("Loading documents..."):
            # Ensure directory exists
            if not os.path.exists(directory_path):
                st.error(f"Directory does not exist: {directory_path}")
                return
                
            documents = load_documents(directory_path)
            
            if not documents:
                st.warning(f"No documents found in directory {directory_path}.")
                st.info("Supported formats: PDF, TXT, DOCX, MD, HTML")
                return
            
            st.info(f"Loaded {len(documents)} documents.")
            
            with st.spinner("Chunking documents..."):
                chunked_documents = chunk_documents(documents, chunk_size, chunk_overlap)
                st.info(f"Created {len(chunked_documents)} text chunks.")
            
            with st.spinner("Embedding documents (this may take a few minutes)..."):
                start_count = 0
                # Get document count before processing
                if "collection_name" in st.session_state:
                    info = get_collection_info(st.session_state.persist_dir, st.session_state.collection_name)
                    start_count = info.get("count", 0)
                
                # Add documents
                st.session_state.rag_pipeline.add_documents(chunked_documents)
                st.session_state.documents_loaded = True
                
                # Get document count after processing
                if "collection_name" in st.session_state:
                    info = get_collection_info(st.session_state.persist_dir, st.session_state.collection_name)
                    end_count = info.get("count", 0)
                    added_count = end_count - start_count
                    
                    st.success(f"Successfully added {added_count} documents to knowledge base!")
                else:
                    st.success("Documents processed and added to knowledge base!")
    except Exception as e:
        st.error(f"Error processing documents: {e}")
        import traceback
        st.error(traceback.format_exc())

def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(
        page_title="Local Knowledge Base RAG Assistant",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Local Knowledge Base RAG Assistant")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # If API key exists, display partial content
        if api_key:
            default_api_key = api_key
            api_key_help = f"Loaded from environment or .env file (starts with {api_key[:5]}...)"
        else:
            default_api_key = ""
            api_key_help = "Please enter your OpenAI API key"
            
        input_api_key = st.text_input("OpenAI API Key", 
                                      type="password", 
                                      value=default_api_key,
                                      help=api_key_help)
        
        # Get existing collections
        collections = get_collections(st.session_state.persist_dir)
        
        # Collection selection area
        st.subheader("Collection Settings")
        
        # Whether to create a new collection
        create_new = st.checkbox("Create New Collection", value=False)
        
        if create_new:
            collection_name = st.text_input("New Collection Name", value="documents")
            reset_collection = True
            st.info(f"Will create a new collection: {collection_name}")
            
            # Hard reset option
            hard_reset = st.checkbox("Hard Reset (Delete Existing Collection)", value=False, 
                                    help="If checked and a collection with this name exists, it will be completely deleted.")
            if hard_reset:
                st.warning(f"⚠️ WARNING: Enabling hard reset will permanently delete the collection '{collection_name}' if it exists!")
                
        else:
            # Default collection name
            default_collection = "documents"
            # If existing collections, provide selection
            if collections:
                collection_options = collections
                default_index = 0 if default_collection not in collections else collections.index(default_collection)
                collection_name = st.selectbox(
                    "Select Existing Collection",
                    options=collection_options,
                    index=default_index
                )
                st.info(f"Will use existing collection: {collection_name}")
            else:
                collection_name = st.text_input("Collection Name", value=default_collection)
                st.info(f"No existing collections found, will create: {collection_name}")
            
            reset_collection = st.checkbox("Reset Collection (clear existing data)", value=False)
            if reset_collection:
                st.warning(f"⚠️ Warning: This will delete all data in collection '{collection_name}'!")
        
        # Collection information display
        if "collection_name" in st.session_state and st.session_state.rag_pipeline:
            collection_info = get_collection_info(st.session_state.persist_dir, st.session_state.collection_name)
            if collection_info["exists"]:
                st.success(f"Current Collection: {st.session_state.collection_name}")
                st.info(f"Contains {collection_info['count']} documents")
                
                # Add export functionality
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Export Collection"):
                        try:
                            st.info("Export feature coming soon...")
                            # TODO: Implement export feature
                        except Exception as e:
                            st.error(f"Export failed: {e}")
                
                with col2:
                    if collection_info["count"] > 0:
                        if st.button("Clear Documents", type="primary"):
                            st.session_state.show_delete_confirm = True
                
                # Show confirmation dialog
                if st.session_state.get("show_delete_confirm", False):
                    st.warning("⚠️ Are you sure you want to delete all documents? This cannot be undone!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Cancel"):
                            st.session_state.show_delete_confirm = False
                            st.rerun()
                    with col2:
                        if st.button("Confirm Delete", type="primary"):
                            success = delete_all_documents(
                                st.session_state.persist_dir, 
                                st.session_state.collection_name
                            )
                            if success:
                                st.success("All documents have been deleted!")
                                st.session_state.documents_loaded = False
                            else:
                                st.error("Failed to delete documents")
                            st.session_state.show_delete_confirm = False
                            st.rerun()
        
        st.subheader("Models")
        embedding_model = st.selectbox(
            "Embedding Model",
            options=[
                "sentence-transformers/all-MiniLM-L6-v2",
                "sentence-transformers/all-mpnet-base-v2",
                "sentence-transformers/multi-qa-mpnet-base-dot-v1"
            ],
            index=0
        )
        
        llm_model = st.selectbox(
            "LLM Model",
            options=[
                "gpt-4o-mini",
                "gpt-3.5-turbo",
                "gpt-4o",
                "o1"
            ],
            index=0
        )
        
        top_k = st.slider("Number of documents to retrieve", min_value=1, max_value=10, value=5)
        
        st.subheader("Document Processing")
        chunk_size = st.slider("Chunk Size", min_value=100, max_value=2000, value=1000, step=100)
        chunk_overlap = st.slider("Chunk Overlap", min_value=0, max_value=500, value=50, step=10)
        
        # Use user-input API key or previously loaded key
        used_api_key = input_api_key or api_key
        
        # Initialize button
        if st.button("Initialize Pipeline"):
            if not used_api_key:
                st.error("Please provide an OpenAI API key.")
            else:
                # Add confirmation for hard reset
                proceed = True
                hard_reset_param = False
                
                # Check if hard reset is enabled
                if reset_collection and 'hard_reset' in locals() and hard_reset:
                    hard_reset_param = True
                    # Display confirmation message
                    st.warning(f"⚠️ WARNING: You are about to permanently delete collection '{collection_name}'. This cannot be undone!")
                    
                    # Store confirmation state
                    if "hard_reset_confirmed" not in st.session_state:
                        st.session_state.hard_reset_confirmed = False
                        
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Cancel"):
                            proceed = False
                    with col2:
                        if st.button("Yes, Delete Collection"):
                            st.session_state.hard_reset_confirmed = True
                    
                    proceed = st.session_state.hard_reset_confirmed
                else:
                    # No hard reset, so get the value if it exists, otherwise False
                    hard_reset_param = hard_reset if 'hard_reset' in locals() else False
                
                if proceed:
                    if initialize_pipeline(
                        used_api_key, 
                        embedding_model, 
                        llm_model, 
                        top_k, 
                        collection_name, 
                        reset_collection, 
                        hard_reset_param
                    ):
                        if hard_reset_param:
                            st.success(f"Collection '{collection_name}' was hard reset and pipeline initialized successfully!")
                        elif reset_collection:
                            st.success(f"Created new collection with timestamp and initialized pipeline successfully!")
                        else:
                            st.success(f"Pipeline initialized successfully with collection '{collection_name}'!")
                        
                        # Save collection name to session state
                        st.session_state.collection_name = collection_name
                        
                        # Reset confirmation state
                        if "hard_reset_confirmed" in st.session_state:
                            st.session_state.hard_reset_confirmed = False
        
        # Document loading section
        st.subheader("Document Loading")
        directory_path = st.text_input("Document Directory Path", "data")
        
        if st.button("Load Documents"):
            if not st.session_state.rag_pipeline:
                st.error("Please initialize the pipeline first.")
            else:
                load_and_process_documents(directory_path, chunk_size, chunk_overlap)
    
    # Main area
    if not st.session_state.rag_pipeline:
        st.info("Please initialize the pipeline in the sidebar to get started.")
        
        # Add some usage guidelines
        with st.expander("Usage Guide", expanded=True):
            st.markdown("""
            ### Getting Started
            1. **Initialize Pipeline**: Provide an OpenAI API key and select or create a Collection in the sidebar
            2. **Import Documents**: After initialization, load documents into your knowledge base
            3. **Ask Questions**: Once documents are loaded, use the chat interface below to query your knowledge base
            
            ### About Collections
            Collections are storage containers for documents and their embeddings:
            - Different topics or projects can be stored in separate Collections
            - Creating a new Collection generates an independent knowledge base space
            - Resetting a Collection will clear all its data
            """)
            
    else:
        # Display Model Introduction
        if "model_message" in st.session_state:
            st.success(st.session_state.model_message)
            # Clear message after displaying once
            st.session_state.model_message = None
        
        # Display current Collection status
        if "collection_name" in st.session_state:
            collection_info = get_collection_info(st.session_state.persist_dir, st.session_state.collection_name)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"📚 Collection: **{st.session_state.collection_name}**")
            with col2:
                if collection_info["exists"]:
                    st.info(f"📊 Document Count: **{collection_info['count']}**")
                else:
                    st.warning("⚠️ Collection not initialized or does not exist")
            with col3:
                from datetime import datetime
                st.info(f"🕒 Current Time: **{datetime.now().strftime('%Y-%m-%d %H:%M')}**")
        
        st.divider()
        
        if not st.session_state.documents_loaded and "collection_name" in st.session_state:
            collection_info = get_collection_info(st.session_state.persist_dir, st.session_state.collection_name)
            if collection_info["count"] == 0:
                st.info("当前知识库为空。您可以在侧边栏中加载文档，或继续使用现有集合来提问。")
            else:
                st.info(f"您正在使用已有的知识库集合，包含{collection_info['count']}个文档。")
        
        # Chat interface
        st.subheader("Chat with Your Knowledge Base")
        
        # Display chat history
        for i, (query, answer) in enumerate(st.session_state.chat_history):
            with st.chat_message("user"):
                st.write(query)
            with st.chat_message("assistant"):
                st.write(answer)
        
        # User input
        user_query = st.chat_input("Ask a question about your documents...")
        
        if user_query:
            with st.chat_message("user"):
                st.write(user_query)
            
            with st.chat_message("assistant"):
                with st.spinner("Generating answer..."):
                    try:
                        # 如果是第一个问题，显示模型介绍
                        intro_text = ""
                        if not st.session_state.chat_history:
                            intro_text = f"_{st.session_state.rag_pipeline.get_model_introduction()}_\n\n"
                            
                        # 生成回答
                        answer = st.session_state.rag_pipeline.get_answer(user_query)
                        
                        # 显示带有介绍的答案（如果需要）
                        if intro_text:
                            st.markdown(intro_text)
                        st.write(answer)
                        
                        # 将问题和回答存储在历史记录中
                        st.session_state.chat_history.append((user_query, answer))
                    except Exception as e:
                        st.error(f"Error generating answer: {e}")
                        import traceback
                        st.error(traceback.format_exc())

if __name__ == "__main__":
    main() 