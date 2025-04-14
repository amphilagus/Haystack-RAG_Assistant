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
except (ImportError, ValueError):
    # 如果失败，尝试绝对路径导入
    try:
        from rag_assistant.custom_document_store import CustomChromaDocumentStore
        from rag_assistant.collection_metadata import save_collection_metadata, get_embedding_model, delete_collection_metadata
    except ImportError:
        # 最后尝试直接导入
        from custom_document_store import CustomChromaDocumentStore
        from collection_metadata import save_collection_metadata, get_embedding_model, delete_collection_metadata

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
                hard_reset: bool = False):
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
        """
        # Save parameters
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.top_k = top_k
        
        # Get API key from environment or parameter
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # 调试输出
        if not self.api_key:
            print("WARNING: API key not found in environment variables.")
            # 尝试直接从.env文件读取
            try:
                with open(os.path.join(os.path.dirname(__file__), '.env'), 'r') as f:
                    for line in f:
                        if line.startswith('OPENAI_API_KEY'):
                            self.api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                            print("API key found in .env file directly.")
                            break
            except Exception as e:
                print(f"Error reading .env file directly: {e}")
            
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set it as an environment variable or pass it as a parameter.")
        
        # Create persist directory if it doesn't exist
        self.persist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chroma_db"))
        os.makedirs(self.persist_dir, exist_ok=True)
        print(f"Using persistent storage at: {self.persist_dir}")
        
        # 处理集合名称和重置
        self.collection_name = collection_name
        
        # 如果需要硬重置，直接删除原有collection
        if reset_collection and hard_reset:
            print(f"Hard resetting collection: {collection_name}")
            try:
                success = CustomChromaDocumentStore.delete_collection(self.persist_dir, collection_name)
                if success:
                    print(f"Successfully deleted collection: {collection_name}")
                    # 同时删除元数据
                    delete_collection_metadata(collection_name)
                else:
                    print(f"Collection {collection_name} not found or could not be deleted")
            except Exception as e:
                print(f"Error deleting collection: {e}")
        # 如果只是软重置，使用时间戳创建新集合
        elif reset_collection:
            # 使用时间戳作为集合名称后缀以确保唯一性
            import time
            timestamp = int(time.time())
            self.collection_name = f"{collection_name}_{timestamp}"
            print(f"Soft reset: Using new collection with timestamp: {self.collection_name}")
        
        # Initialize components with the determined collection name
        print(f"Initializing document store with collection: {self.collection_name}")
        self.text_embedder = SentenceTransformersTextEmbedder(model=embedding_model)
        self.document_embedder = SentenceTransformersDocumentEmbedder(model=embedding_model)
        
        # 尝试初始化文档存储
        try:
            # 初始化文档存储 - ChromaDocumentStore会自动检测collection是否存在
            embedding_dim = 384  # 默认值
            
            # 检查是否有特定嵌入模型的维度设置
            if "bge-large" in embedding_model:
                embedding_dim = 1024
            elif "bge" in embedding_model:
                embedding_dim = 768
            elif "m3e" in embedding_model:
                embedding_dim = 768
            elif "multilingual" in embedding_model and "L12" in embedding_model:
                embedding_dim = 384
            
            self.document_store = CustomChromaDocumentStore(
                embedding_dim=embedding_dim,
                persist_dir=self.persist_dir,
                collection_name=self.collection_name
            )
            
            print(f"Using persistent storage at: {self.persist_dir}")
            print(f"Using collection: {self.collection_name}")
            
            # 保存collection元数据（嵌入模型信息）
            # 注意：只有在创建新collection或重置时才保存元数据
            if reset_collection or not get_embedding_model(self.collection_name):
                save_collection_metadata(self.collection_name, embedding_model)
            
            # 获取collection中的文档数量
            try:
                all_docs = self.document_store.filter_documents({})
                print(f"Collection contains {len(all_docs)} documents")
            except Exception as e:
                print(f"Could not get document count: {e}")
                
        except Exception as e:
            print(f"Error initializing document store: {e}")
            raise ValueError(f"Failed to initialize ChromaDocumentStore: {e}")
        
        # Warm up the embedders to load the models
        print("Warming up embedding models...")
        self.text_embedder.warm_up()
        self.document_embedder.warm_up()
        
        # Initialize chat prompt template and chat messages
        self.chat_template = [
            ChatMessage.from_user(
                """
        Answer the question based on the given context. If the answer cannot be derived from the context, 
        say "Sorry, I don't know either =-=" Include only information that is 
        present in the context and do not add any additional information.

        Context:
        {% for document in documents %}
        {{ document.content }}
        {% endfor %}

        Question: {{question}}
        Answer:
        """
            )
        ]
        
        # Create components
        try:
            # Create retriever using the existing document store
            self.retriever = ChromaEmbeddingRetriever(
                document_store=self.document_store,
                top_k=top_k
            )
            
            self.prompt_builder = ChatPromptBuilder(template=self.chat_template)
            
            self.generator = OpenAIChatGenerator(
                model=llm_model,
                api_key=Secret.from_token(self.api_key)
            )
            
            # Initialize pipeline
            self.pipeline = self._create_pipeline()
        except Exception as e:
            print(f"Error creating pipeline components: {e}")
            raise ValueError(f"Failed to initialize RAG pipeline components: {e}")

    def _create_pipeline(self) -> Pipeline:
        """
        Create and connect the RAG pipeline components.
        
        Returns:
            Haystack Pipeline
        """
        try:
            # 先确保检索器正确初始化
            try:
                # 检查检索器是否需要重新初始化
                if not hasattr(self, 'retriever') or self.retriever is None:
                    self.retriever = ChromaEmbeddingRetriever(
                        document_store=self.document_store,
                        top_k=self.top_k
                    )
            except Exception as retriever_error:
                print(f"Error initializing retriever: {retriever_error}")
                self.retriever = ChromaEmbeddingRetriever(
                    document_store=self.document_store,
                    top_k=self.top_k
                )
            
            # Create pipeline
            pipeline = Pipeline()
            
            # Add components
            pipeline.add_component("text_embedder", self.text_embedder)
            pipeline.add_component("retriever", self.retriever)
            pipeline.add_component("prompt_builder", self.prompt_builder)
            pipeline.add_component("llm", self.generator)
            
            # Connect components
            pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
            pipeline.connect("retriever", "prompt_builder.documents")
            pipeline.connect("prompt_builder.prompt", "llm.messages")
            
            return pipeline
        except Exception as e:
            print(f"Error creating pipeline: {e}")
            
            # 尝试重新创建检索器和pipeline
            try:
                print("重新创建pipeline和组件...")
                
                # 重新创建检索器
                self.retriever = ChromaEmbeddingRetriever(
                    document_store=self.document_store,
                    top_k=self.top_k
                )
                
                # 完全重新创建pipeline
                pipeline = Pipeline()
                pipeline.add_component("text_embedder", self.text_embedder)
                pipeline.add_component("retriever", self.retriever)
                pipeline.add_component("prompt_builder", self.prompt_builder)
                pipeline.add_component("llm", self.generator)
                
                pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
                pipeline.connect("retriever", "prompt_builder.documents")
                pipeline.connect("prompt_builder.prompt", "llm.messages")
                
                return pipeline
            except Exception as retry_error:
                print(f"Pipeline重建失败: {retry_error}")
                raise ValueError(f"无法初始化RAG pipeline: {retry_error}")

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

    def run(self, query: str) -> Dict[str, Any]:
        """
        Run the RAG pipeline with a user query.
        
        Args:
            query: User question
        
        Returns:
            Pipeline results containing the generated answer
        """
        try:
            # 运行pipeline
            results = self.pipeline.run({
                "text_embedder": {"text": query},
                "prompt_builder": {
                    "question": query
                    # 不再手动设置documents，因为它已经通过pipeline连接由retriever提供
                }
            })
            return results
        except Exception as e:
            # 抛出异常
            raise ValueError(f"查询处理失败: {e}")

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
        
        return introductions.get(self.llm_model, introductions["default"])

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