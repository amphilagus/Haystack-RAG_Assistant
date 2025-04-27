from haystack_integrations.document_stores.chroma import ChromaDocumentStore
import logging
import chromadb
import os

logger = logging.getLogger(__name__)

class CustomChromaDocumentStore(ChromaDocumentStore):
    """
    A custom document store extending ChromaDocumentStore with fixed collection existence check.
    """
    
    @staticmethod
    def delete_collection(persist_dir: str, collection_name: str) -> bool:
        """
        Delete a collection from the ChromaDB.
        
        Args:
            persist_dir: Path to the persistent directory
            collection_name: Name of the collection to delete
            
        Returns:
            bool: True if collection was deleted, False otherwise
        """
        try:
            if not os.path.exists(persist_dir):
                logger.warning(f"Persistent directory does not exist: {persist_dir}")
                return False
                
            client = chromadb.PersistentClient(path=persist_dir)
            collections = client.list_collections()
            collection_names = [col.name for col in collections]
            
            if collection_name in collection_names:
                client.delete_collection(name=collection_name)
                logger.info(f"Successfully deleted collection: {collection_name}")
                return True
            else:
                logger.warning(f"Collection does not exist: {collection_name}")
                return False
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            return False
    
    def __init__(
        self,
        collection_name: str = "documents",
        embedding_function: str = "default",
        persist_dir: str = None,
        host: str = None,
        port: int = None,
        distance_function: str = "l2",
        metadata: dict = None,
        **embedding_function_params,
    ):
        """
        Extended initialization with persist_dir parameter for compatibility with the project.
        """
        # 将persist_dir映射到persist_path
        super().__init__(
            collection_name=collection_name,
            embedding_function=embedding_function,
            persist_path=persist_dir,  # 将persist_dir映射到persist_path
            host=host,
            port=port,
            distance_function=distance_function,
            metadata=metadata,
            **embedding_function_params,
        )
        # 不再存储和处理embedding_dim
    
    def _ensure_initialized(self):
        if not self._initialized:
            # Create the client instance
            if self._persist_path and (self._host or self._port is not None):
                error_message = (
                    "You must specify `persist_path` for local persistent storage or, "
                    "alternatively, `host` and `port` for remote HTTP client connection. "
                    "You cannot specify both options."
                )
                raise ValueError(error_message)
            if self._host and self._port is not None:
                # Remote connection via HTTP client
                client = chromadb.HttpClient(
                    host=self._host,
                    port=self._port,
                )
            elif self._persist_path is None:
                # In-memory storage
                client = chromadb.Client()
            else:
                # Local persistent storage
                client = chromadb.PersistentClient(path=self._persist_path)

            self._metadata = self._metadata or {}
            if "hnsw:space" not in self._metadata:
                self._metadata["hnsw:space"] = self._distance_function

            # 修复的集合检查逻辑
            collection_names = [col.name for col in client.list_collections()]
            if self._collection_name in collection_names:
                self._collection = client.get_collection(self._collection_name, embedding_function=self._embedding_func)

                if self._metadata != self._collection.metadata:
                    logger.warning(
                        "Collection already exists. "
                        "The `distance_function` and `metadata` parameters will be ignored."
                    )
            else:
                self._collection = client.create_collection(
                    name=self._collection_name,
                    metadata=self._metadata,
                    embedding_function=self._embedding_func,
                )

            self._initialized = True 