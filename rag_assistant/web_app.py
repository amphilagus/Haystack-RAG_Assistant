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
if "prompt_template" not in st.session_state:
    st.session_state.prompt_template = "balanced"

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

def initialize_pipeline(api_key: str, llm_model: str, top_k: int, collection_name: str, prompt_template: str = "balanced") -> bool:
    """
    Initialize the RAG pipeline.
    
    Args:
        api_key: OpenAI API key
        llm_model: LLM model to use for answer generation
        top_k: Number of documents to retrieve
        collection_name: Name of the collection to use
        prompt_template: Prompt template to use (precise, balanced, creative)
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
        template_changed = "prompt_template" in st.session_state and st.session_state.prompt_template != prompt_template
        
        # 保存当前模板
        st.session_state.prompt_template = prompt_template
        
        st.session_state.rag_pipeline = RAGPipeline(
            embedding_model=embedding_model,
            llm_model=llm_model,
            top_k=top_k,
            api_key=api_key,
            persist_dir=st.session_state.persist_dir,
            collection_name=collection_name,
            prompt_template=prompt_template
        )
        
        # 保存当前模型
        st.session_state.current_model = llm_model
        
        # 获取模型介绍
        model_intro = st.session_state.rag_pipeline.get_model_introduction()
        template_info = st.session_state.rag_pipeline.get_current_template_info()
        
        # 根据模型和模板是否更改显示不同消息
        message = ""
        if model_changed:
            message += f"Model switched to {llm_model}. "
        if template_changed:
            message += f"Template switched to {template_info['name']}. "
        
        if message:
            st.session_state.model_message = message + model_intro
        else:
            st.session_state.model_message = f"Pipeline initialized with {llm_model} and {template_info['name']} template. {model_intro}"
        
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
        
        # 模型选择区域
        st.subheader("Model Settings")
        
        model_options = {
            "gpt-4o-mini": "GPT-4o Mini (快速)",
            "gpt-3.5-turbo": "GPT-3.5 Turbo (快速)",
            "gpt-4o": "GPT-4o (高质量)"
        }
        
        # 模型选择
        default_model = "gpt-4o-mini"
        selected_model = st.selectbox(
            "Select LLM Model",
            options=list(model_options.keys()),
            format_func=lambda x: model_options.get(x, x),
            index=list(model_options.keys()).index(default_model)
        )
        
        # 添加提示词模板选择
        st.subheader("Prompt Template")
        template_options = {
            "precise": "Precise (精准模式)",
            "balanced": "Balanced (平衡模式)",
            "creative": "Creative (创意模式)"
        }
        
        template_descriptions = {
            "precise": "严格遵循文档内容，提供简洁准确的回答",
            "balanced": "平衡准确性和流畅性，默认模式",
            "creative": "在保持准确的同时提供更详细的解释和见解"
        }
        
        # 获取当前模板
        current_template = st.session_state.get("prompt_template", "balanced")
        
        selected_template = st.selectbox(
            "Select Prompt Template",
            options=list(template_options.keys()),
            format_func=lambda x: template_options.get(x, x),
            index=list(template_options.keys()).index(current_template),
            help="选择不同的提示词模板来控制AI回答的风格",
            key="template_selector"
        )
        
        # 显示所选模板的描述
        st.caption(template_descriptions.get(selected_template, ""))
        
        # 如果已初始化pipeline且模板被更改，更新模板
        if (st.session_state.rag_pipeline is not None and 
            selected_template != current_template and 
            "template_selector" in st.session_state):
            with st.spinner(f"Updating template to {template_options[selected_template]}..."):
                success = st.session_state.rag_pipeline.set_prompt_template(selected_template)
                if success:
                    st.session_state.prompt_template = selected_template
                    st.success(f"Template changed to {template_options[selected_template]}")
                    template_info = st.session_state.rag_pipeline.get_current_template_info()
                    st.session_state.model_message = f"Template switched to {template_info['name']}. {template_info['description']}"
                    st.rerun()
                else:
                    st.error("Failed to change template")
        
        # 检索参数设置
        top_k = st.slider("Number of documents to retrieve (top_k)", min_value=1, max_value=20, value=5)
        
        # 初始化按钮
        if st.button("Initialize Pipeline", type="primary"):
            # 检查是否选择了集合
            if not collection_name:
                st.error("Please select a collection first")
            else:
                # 显示加载指示器
                with st.spinner("Initializing pipeline..."):
                    # 尝试初始化pipeline
                    success = initialize_pipeline(
                        api_key=input_api_key or api_key,
                        llm_model=selected_model,
                        top_k=top_k,
                        collection_name=collection_name,
                        prompt_template=selected_template
                    )
                    if success:
                        st.success("Pipeline initialized successfully!")
                    else:
                        st.error("Failed to initialize pipeline. Check the error message above.")

    # 右侧主区域
    if st.session_state.rag_pipeline is not None:
        # 显示模型信息
        if "model_message" in st.session_state:
            st.info(st.session_state.model_message)
            
        # 获取当前模板信息
        template_info = st.session_state.rag_pipeline.get_current_template_info()
        
        # 显示聊天标题和当前使用的模板信息
        st.subheader("Chat")
        st.caption(f"Using template: {template_info['name']} - {template_info['description']}")
        
        # 根据模板设置头像
        avatar_emojis = {
            "precise": "🔍",  # 精确模式 - 放大镜
            "balanced": "⚖️",  # 平衡模式 - 天平
            "creative": "🎨"   # 创意模式 - 调色板
        }
        current_avatar_emoji = avatar_emojis.get(st.session_state.prompt_template, "⚖️")
        
        # 添加模板图标说明
        st.caption("模板图标: 🔍精确模式 | ⚖️平衡模式 | 🎨创意模式")
        
        # 修复旧的历史记录，确保每条消息都有模板信息
        for message in st.session_state.chat_history:
            if message["role"] == "assistant" and "template" not in message:
                message["template"] = "balanced"  # 为旧消息添加默认模板
        
        # 显示聊天历史
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                # 使用消息中保存的模板对应的头像
                message_template = message.get("template", "balanced")
                message_avatar = avatar_emojis.get(message_template, "⚖️")
                st.chat_message("assistant", avatar=message_avatar).write(message["content"])
                
        # 用户输入
        user_query = st.chat_input("Ask a question about your documents...")
        
        if user_query:
            # 将用户问题添加到历史记录
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            st.chat_message("user").write(user_query)
            
            # 生成回答
            with st.chat_message("assistant", avatar=current_avatar_emoji):
                with st.spinner("Generating answer..."):
                    try:
                        answer = st.session_state.rag_pipeline.get_answer(user_query)
                        st.write(answer)
                        
                        # 添加回答到历史记录，包括当前使用的模板
                        st.session_state.chat_history.append({
                            "role": "assistant", 
                            "content": answer,
                            "template": st.session_state.prompt_template  # 保存当前使用的模板
                        })
                    except Exception as e:
                        st.error(f"Error generating answer: {e}")
    else:
        st.info("Please initialize the pipeline in the sidebar to get started.")
        
        # 添加一些使用指南
        with st.expander("Usage Guide", expanded=True):
            st.markdown("""
            ### Getting Started
            1. **Initialize Pipeline**: Select a Collection, Model and Template in the sidebar
            2. **Ask Questions**: Use the chat interface to query your knowledge base
            
            ### About Templates
            - **Precise**: Strictly follows document content with concise answers
            - **Balanced**: Balances accuracy and fluency (default)
            - **Creative**: Provides more detailed explanations while maintaining accuracy
            """)

if __name__ == "__main__":
    main() 