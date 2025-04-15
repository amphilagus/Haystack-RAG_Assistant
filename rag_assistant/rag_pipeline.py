"""
RAG Pipeline Module

This module implements the Retrieval-Augmented Generation (RAG) pipeline using Haystack components.
The pipeline consists of:
1. Document store for storing documents and their embeddings
2. Document embedder for converting documents to vectors
3. Text embedder for converting user queries to vectors
4. Retriever for finding relevant documents
5. Prompt builder for creating prompts for the LLM
6. Generator (LLM) for generating answers
"""

import os
import sys
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from haystack import Pipeline, Document
from haystack_integrations.document_stores.chroma import ChromaDocumentStore
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack_integrations.components.retrievers.chroma import ChromaEmbeddingRetriever
from haystack.utils import Secret
from tqdm import tqdm
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

# 导入自定义的CustomChromaDocumentStore
# 先确保当前目录在sys.path中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    # 先尝试相对路径导入
    from .custom_document_store import CustomChromaDocumentStore
    from .collection_metadata import save_collection_metadata, get_embedding_model, delete_collection_metadata
    from .prompt_templates import get_template, get_all_templates
except (ImportError, ValueError):
    # 如果失败，尝试绝对路径导入
    try:
        from rag_assistant.custom_document_store import CustomChromaDocumentStore
        from rag_assistant.collection_metadata import save_collection_metadata, get_embedding_model, delete_collection_metadata
        from rag_assistant.prompt_templates import get_template, get_all_templates
    except ImportError:
        # 最后尝试直接导入
        from custom_document_store import CustomChromaDocumentStore
        from collection_metadata import save_collection_metadata, get_embedding_model, delete_collection_metadata
        from prompt_templates import get_template, get_all_templates

# 直接在脚本开头加载环境变量
load_dotenv(override=True)

# 调试输出，查看环境变量是否正确加载
print(f"Environment variables loaded, OPENAI_API_KEY exists: {'OPENAI_API_KEY' in os.environ}")

class RAGPipeline:
    """
    Implements a Retrieval-Augmented Generation (RAG) pipeline using Haystack.
    """

    def __init__(self, 
                embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                llm_model: str = "gpt-4o-mini",
                top_k: int = 5,
                api_key: Optional[str] = None,
                persist_dir: str = "../chroma_db",
                collection_name: str = "documents",
                reset_collection: bool = False,
                hard_reset: bool = False,
                use_llm: bool = True,
                prompt_template: str = "balanced"):
        """
        Initialize the RAG pipeline.
        
        Args:
            embedding_model: Model to use for document and query embedding
            llm_model: LLM model to use for answer generation (default: gpt-4o-mini)
            top_k: Number of documents to retrieve
            api_key: OpenAI API key (if not set as environment variable)
            persist_dir: Directory for persistent storage of Chroma embeddings
            collection_name: Name of the Chroma collection to use
            reset_collection: Whether to reset (clear) the collection if it exists
            hard_reset: If True, completely delete the existing collection instead of creating a new one with timestamp
            use_llm: Whether to include LLM in the pipeline
            prompt_template: Prompt template to use (precise, balanced, creative)
        """
        # Save parameters as default settings
        self.default_settings = {
            "embedding_model": embedding_model,
            "llm_model": llm_model,
            "top_k": top_k,
            "api_key": api_key or os.getenv("OPENAI_API_KEY"),
            "persist_dir": persist_dir,
            "collection_name": collection_name,
            "reset_collection": reset_collection,
            "hard_reset": hard_reset,
            "use_llm": use_llm,
            "prompt_template": prompt_template
        }
        
        # Initialize with default settings
        self.create_new_pipeline(use_llm=use_llm)

    def _initialize_with_settings(self, settings: Dict[str, Any]) -> None:
        """
        Initialize components with given settings.
        
        Args:
            settings: Dictionary containing initialization parameters
        """
        # Get API key from settings
        self.api_key = settings["api_key"]
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set it as an environment variable or pass it as a parameter.")
        
        # Create persist directory if it doesn't exist
        self.persist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chroma_db"))
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # 处理集合名称和重置
        self.collection_name = settings["collection_name"]
        
        # 如果需要硬重置，直接删除原有collection
        if settings["reset_collection"] and settings["hard_reset"]:
            print(f"Hard resetting collection: {self.collection_name}")
            try:
                success = CustomChromaDocumentStore.delete_collection(self.persist_dir, self.collection_name)
                if success:
                    print(f"Successfully deleted collection: {self.collection_name}")
                    delete_collection_metadata(self.collection_name)
                else:
                    print(f"Collection {self.collection_name} not found or could not be deleted")
            except Exception as e:
                print(f"Error deleting collection: {e}")
        # 如果只是软重置，使用时间戳创建新集合
        elif settings["reset_collection"]:
            import time
            timestamp = int(time.time())
            self.collection_name = f"{self.collection_name}_{timestamp}"
            print(f"Soft reset: Using new collection with timestamp: {self.collection_name}")
        
        # Initialize document store
        try:
            # 不再手动指定嵌入维度，依赖模型的默认配置
            self.document_store = CustomChromaDocumentStore(
                persist_dir=self.persist_dir,
                collection_name=self.collection_name
            )
            
            # 保存collection元数据
            if settings["reset_collection"] or not get_embedding_model(self.collection_name):
                save_collection_metadata(self.collection_name, settings["embedding_model"])
            
        except Exception as e:
            print(f"Error initializing document store: {e}")
            raise ValueError(f"Failed to initialize ChromaDocumentStore: {e}")

        # 使用提示词模板
        self.chat_template = get_template(settings["prompt_template"])
        self.current_template = settings["prompt_template"]
        
        # Initialize components
        self.text_embedder = SentenceTransformersTextEmbedder(model=settings["embedding_model"])
        self.document_embedder = SentenceTransformersDocumentEmbedder(model=settings["embedding_model"])
        self.retriever = ChromaEmbeddingRetriever(
            document_store=self.document_store,
            top_k=settings["top_k"]
        )
        self.prompt_builder = ChatPromptBuilder(template=self.chat_template)
        self.generator = OpenAIChatGenerator(
            model=settings["llm_model"],
            api_key=Secret.from_token(self.api_key)
        )
        
        # Warm up the embedders
        self.text_embedder.warm_up()
        self.document_embedder.warm_up()

    def _create_pipeline(self, use_llm: bool = True) -> Pipeline:
        """
        Create a new pipeline using the current components.
        
        Args:
            use_llm: Whether to include LLM in the pipeline (if False, only retriever will be used)
            
        Returns:
            Haystack Pipeline
        """
        try:
            # Create and connect pipeline
            pipeline = Pipeline()
            pipeline.add_component("text_embedder", self.text_embedder)
            pipeline.add_component("retriever", self.retriever)

            # 根据use_llm参数决定是否添加和连接LLM相关组件
            if use_llm:
                pipeline.add_component("prompt_builder", self.prompt_builder)
                pipeline.connect("retriever", "prompt_builder.documents")
                pipeline.add_component("llm", self.generator)
                pipeline.connect("prompt_builder.prompt", "llm.messages")
            
            # 这个连接在任何情况下都需要的
            pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
            
            return pipeline
            
        except Exception as e:
            print(f"Error creating pipeline: {e}")
            raise ValueError(f"无法初始化RAG pipeline: {e}")

    def create_new_pipeline(self, use_llm: bool = True, **kwargs) -> None:
        """
        Create a new pipeline with optional parameter overrides and set it as current.
        
        Args:
            use_llm: Whether to include LLM in the pipeline
            **kwargs: Optional parameters to override default settings
        """
        # Merge default settings with overrides
        settings = self.default_settings.copy()
        settings.update(kwargs)
        
        # Initialize components with new settings
        self._initialize_with_settings(settings)
        
        # Create new pipeline
        new_pipeline = self._create_pipeline(use_llm=use_llm)
        
        # If this is the first pipeline, set it as default
        if not hasattr(self, 'default_pipeline'):
            self.default_pipeline = new_pipeline
        
        # Set as current pipeline
        self.current_pipeline = new_pipeline

    def reset_to_default_pipeline(self) -> None:
        """
        Reset the current pipeline to the default one.
        """
        self.current_pipeline = self.default_pipeline

    def run(self, query: str) -> Dict[str, Any]:
        """
        Run the current pipeline with a user query.
        
        Args:
            query: User question
        
        Returns:
            Pipeline results containing the generated answer
        """
        try:
            results = self.current_pipeline.run({
                "text_embedder": {"text": query},
                "prompt_builder": {"question": query}
            })
            return results
        except Exception as e:
            try:
                results = self.current_pipeline.run({
                    "text_embedder": {"text": query},
                })
                return results
            except Exception as e:
                raise ValueError(f"查询处理失败: {e}")

    def add_documents(self, documents: List[Document], check_duplicates: bool = False) -> None:
        """
        Add documents to the document store.
        
        Args:
            documents: List of Haystack Document objects
            check_duplicates: Whether to check for duplicates before adding
        """
        if not documents:
            print("No documents provided to add")
            return
            
        print(f"Processing {len(documents)} documents...")
        
        # 打印某个文档的元数据以便调试
        if documents and len(documents) > 0:
            print(f"Sample document metadata: {documents[0].meta}")
        
        # Check for duplicates if requested
        if check_duplicates:
            print("Checking for duplicate documents...")
            from rag_assistant.document_loader import is_duplicate_document
            filtered_docs = []
            duplicates_count = 0
            
            for doc in documents:
                if is_duplicate_document(doc, self.document_store):
                    print(f"Skipping duplicate document: {doc.meta.get('source', 'unknown')}")
                    duplicates_count += 1
                else:
                    filtered_docs.append(doc)
            
            if duplicates_count > 0:
                print(f"Skipped {duplicates_count} duplicate documents")
                documents = filtered_docs
                
            if not documents:
                print("No new documents to add after duplicate check")
                return
        
        print(f"Embedding {len(documents)} documents...")
        
        # Embed documents
        embedded_docs = self.document_embedder.run(documents)
        
        # 确保元数据正确传递
        for i, doc in enumerate(embedded_docs["documents"]):
            # 验证元数据是否保留
            if not doc.meta and documents[i].meta:
                print(f"WARNING: Document metadata lost during embedding. Restoring...")
                doc.meta = documents[i].meta
        
        # Add to document store
        print("将文档写入存储...")
        total_docs = len(embedded_docs["documents"])
        for i in tqdm(range(0, total_docs, 10), desc="写入进度", unit="batch"):
            batch = embedded_docs["documents"][i:min(i+10, total_docs)]
            self.document_store.write_documents(batch)
        print(f"Added {total_docs} documents to the document store")
        
        # ChromaDocumentStore with persist_path automatically persists data
        print("Documents are automatically persisted in ChromaDocumentStore")

    def get_answer(self, query: str) -> str:
        """
        Get an answer for a query using the RAG pipeline.
        
        Args:
            query: The user question
            
        Returns:
            The generated answer
        """
        # Show model introduction if this is the first query
        if not hasattr(self, '_shown_introduction'):
            intro = self.get_model_introduction()
            print(f"\n{intro}\n")
            self._shown_introduction = True
            
        # Run the pipeline
        try:
            results = self.run(query)
            # OpenAIChatGenerator返回responses而不是replies
            if results and "llm" in results:
                if "responses" in results["llm"]:
                    # 获取第一个响应的内容
                    return results["llm"]["responses"][0].content
                elif "replies" in results["llm"]:  # 兼容旧版本
                    return results["llm"]["replies"][0].text
            return "Sorry, I couldn't generate an answer."
        except Exception as e:
            print(f"Error generating answer: {e}")
            return f"Error: {str(e)}"
    
    def get_model_introduction(self) -> str:
        """
        Get a self-introduction message for the current LLM model.
        
        Returns:
            A model-specific introduction message
        """
        introductions = {
            "gpt-3.5-turbo": "Hello! I'm GPT-3.5 Turbo, ready to answer your questions based on the documents you've provided.",
            "gpt-4o-mini": "Hi there! I'm GPT-4o Mini, an efficient assistant ready to help you explore your knowledge base.",
            "gpt-4o": "Greetings! I'm GPT-4o, OpenAI's advanced model, ready to assist with detailed insights from your documents.",
            "o1": "Welcome! I'm Claude (o1), designed by Anthropic, prepared to provide thoughtful analysis of your knowledge base.",
            "default": "Hello! I'm your AI assistant, ready to answer questions based on your documents."
        }
        
        return introductions.get(self.default_settings["llm_model"], introductions["default"])

    def reset_document_store(self) -> None:
        """
        Reset the document store by deleting all documents.
        Call this method if you want to clear the document store without creating a new collection.
        """
        try:
            # Get all document IDs
            all_docs = self.document_store.filter_documents({})
            if all_docs:
                doc_ids = [doc.id for doc in all_docs]
                # Delete all documents
                self.document_store.delete_documents(doc_ids)
                print(f"Deleted {len(doc_ids)} documents from the document store")
            else:
                print("Document store is already empty")
        except Exception as e:
            print(f"Error resetting document store: {e}")
            print("To create a new collection, initialize a new RAGPipeline with reset_collection=True")

    def get_current_template_info(self) -> Dict[str, Any]:
        """
        Get information about the current prompt template.
        
        Returns:
            Dictionary with template name, description, and full template
        """
        templates = get_all_templates()
        if hasattr(self, 'current_template') and self.current_template in templates:
            return templates[self.current_template]
        return templates["balanced"]  # 默认返回平衡模板

    def set_prompt_template(self, template_name: str) -> bool:
        """
        Change the prompt template.
        
        Args:
            template_name: Name of the template (precise, balanced, creative)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # 获取新模板
            new_template = get_template(template_name)
            
            # 保存当前模板名称
            self.current_template = template_name.lower()
            if self.current_template not in get_all_templates():
                self.current_template = "balanced"
                
            # 更新设置
            self.default_settings["prompt_template"] = self.current_template
            
            # 创建新的prompt_builder组件
            self.chat_template = new_template
            self.prompt_builder = ChatPromptBuilder(template=self.chat_template)
            
            # 重新创建pipeline
            self.create_new_pipeline(use_llm=self.default_settings["use_llm"])
            
            return True
        except Exception as e:
            print(f"Error setting prompt template: {e}")
            return False
    
    def get_available_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Get all available prompt templates.
        
        Returns:
            Dictionary of template information
        """
        templates = get_all_templates()
        # 构建简化的模板信息，不包含实际模板对象
        return {
            name: {
                "name": info["name"],
                "description": info["description"]
            }
            for name, info in templates.items()
        }