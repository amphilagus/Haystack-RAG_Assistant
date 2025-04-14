"""
Web Interface Module

This module provides a simplified web interface for the RAG assistant using Streamlit.
只保留：选择collection、选择LLM模型、设置top_k和对话功能
"""

import os
import streamlit as st
from dotenv import load_dotenv
from typing import List, Optional
import chromadb
from collection_metadata import get_embedding_model
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
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "collection_name" not in st.session_state:
    st.session_state.collection_name = "documents"
if "persist_dir" not in st.session_state:
    st.session_state.persist_dir = "chroma_db"
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

def initialize_pipeline(api_key: str, llm_model: str, top_k: int, collection_name: str) -> bool:
    """
    Initialize the RAG pipeline.
    
    Args:
        api_key: OpenAI API key
        llm_model: LLM model to use for answer generation
        top_k: Number of documents to retrieve
        collection_name: Name of the collection to use
    """
    try:
        # 检查集合是否存在，获取正确的嵌入模型
        embedding_model = get_embedding_model(collection_name)
        if not embedding_model:
            embedding_model = "sentence-transformers/all-MiniLM-L6-v2"  # 默认值
            st.info(f"Using default embedding model: {embedding_model}")
        else:
            st.info(f"Using embedding model from collection metadata: {embedding_model}")
        
        # 检查模型是否更改
        model_changed = "current_model" in st.session_state and st.session_state.current_model != llm_model
        
        st.session_state.rag_pipeline = RAGPipeline(
            embedding_model=embedding_model,
            llm_model=llm_model,
            top_k=top_k,
            api_key=api_key,
            persist_dir=st.session_state.persist_dir,
            collection_name=collection_name
        )
        
        # 保存当前模型
        st.session_state.current_model = llm_model
        
        # 获取模型介绍
        model_intro = st.session_state.rag_pipeline.get_model_introduction()
        
        # 根据模型是否更改显示不同消息
        if model_changed:
            st.session_state.model_message = f"Model switched to {llm_model}. {model_intro}"
        else:
            st.session_state.model_message = f"Pipeline initialized with {llm_model}. {model_intro}"
        
        return True
    except Exception as e:
        st.error(f"Error initializing pipeline: {e}")
        return False

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
        
        # 获取现有集合
        collections = get_collections(st.session_state.persist_dir)
        
        # 集合选择区域
        st.subheader("Collection Settings")
        
        # 默认集合名称
        default_collection = "documents"
        # 如果有现有集合，提供选择
        if collections:
            collection_options = collections
            default_index = 0 if default_collection not in collections else collections.index(default_collection)
            collection_name = st.selectbox(
                "Select Collection",
                options=collection_options,
                index=default_index
            )
            collection_info = get_collection_info(st.session_state.persist_dir, collection_name)
            if collection_info["exists"]:
                st.info(f"Collection contains {collection_info['count']} documents")
        else:
            collection_name = st.text_input("Collection Name", value=default_collection)
            st.info(f"No existing collections found. Please initialize a collection first via CLI.")
        
        # 模型选择
        st.subheader("Model Settings")
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
        
        # 检索文档数量设置
        top_k = st.slider("Number of documents to retrieve", min_value=1, max_value=20, value=5)
        
        # 使用用户输入的API密钥或之前加载的密钥
        used_api_key = input_api_key or api_key
        
        # 初始化按钮
        if st.button("Initialize Pipeline"):
            if not used_api_key:
                st.error("Please provide an OpenAI API key.")
            else:
                if initialize_pipeline(used_api_key, llm_model, top_k, collection_name):
                    st.success(f"Pipeline initialized successfully with collection '{collection_name}'!")
                    st.session_state.collection_name = collection_name
    
    # 主区域
    if not st.session_state.rag_pipeline:
        st.info("Please initialize the pipeline in the sidebar to get started.")
        
        # 添加一些使用指南
        with st.expander("Usage Guide", expanded=True):
            st.markdown("""
            ### Getting Started
            1. **Initialize Pipeline**: Provide an OpenAI API key and select a Collection in the sidebar
            2. **Ask Questions**: Use the chat interface below to query your knowledge base
            
            ### About Collections
            - Collections need to be created and loaded with documents using the CLI interface
            - Different topics or projects should be stored in separate Collections
            - Select the appropriate collection for your query context
            """)
            
    else:
        # 显示模型介绍
        if "model_message" in st.session_state:
            st.success(st.session_state.model_message)
            # 显示一次后清除消息
            st.session_state.model_message = None
        
        # 显示当前集合状态
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
        
        # 聊天界面
        st.subheader("Chat with Your Knowledge Base")
        
        # 显示聊天历史
        for i, (query, answer) in enumerate(st.session_state.chat_history):
            with st.chat_message("user"):
                st.write(query)
            with st.chat_message("assistant"):
                st.write(answer)
        
        # 用户输入
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