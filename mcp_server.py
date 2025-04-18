from mcp.server.fastmcp import FastMCP
import os
import sys
import logging
import locale
from logging.handlers import RotatingFileHandler

# Set environment variables for proper encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '0'  # Disable legacy stdio behavior on Windows

# Windows-specific console encoding fix
if sys.platform == 'win32':
    try:
        import ctypes
        # Try to set console code page to UTF-8 (65001)
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass  # If it fails, continue anyway

# Force UTF-8 encoding for stdin/stdout/stderr
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
        sys.stdin.reconfigure(encoding='utf-8')
        logger_prefx = "Successfully reconfigured stdin/stdout/stderr to UTF-8"
    except AttributeError:
        # Python versions before 3.7 don't have reconfigure
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
        logger_prefx = "Successfully wrapped stdin/stdout/stderr with UTF-8 encoding"

# Try to set default locale to UTF-8
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except (locale.Error, AttributeError):
    try:
        locale.setlocale(locale.LC_ALL, '.UTF-8')
    except (locale.Error, AttributeError):
        pass  # If locale setting fails, continue anyway

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'rag_server.log')

# Set up logger
logger = logging.getLogger('rag_assistant')
logger.setLevel(logging.INFO)

# Set up rotating file handler (10MB max size, keep 5 backup files)
handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Log encoding information
logger.info("RAG Assistant server starting...")
logger.info(f"Python version: {sys.version}")
logger.info(f"System encoding: {sys.getdefaultencoding()}")
logger.info(f"Locale encoding: {locale.getpreferredencoding()}")
logger.info(f"Current stdout encoding: {sys.stdout.encoding}")
if 'logger_prefx' in locals():
    logger.info(logger_prefx)
logger.info(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'not set')}")

# Initialize FastMCP server
mcp = FastMCP("rag_assistant")

class RAGPipelineWrapper:
    def __init__(self):
        """初始化RAG管道包装器"""
        logger.info("初始化RAG管道包装器")
        self.pipeline = None  # 初始化管道为空
        self.initialized = False  # 初始化状态为未初始化
        self.collections_metadata = {}  # 初始化集合元数据为空字典
        self._load_collections_metadata()  # 加载集合元数据
        self._collections_titles_cache = {}  # 缓存每个集合的所有标题
        logger.info(f"已加载 {len(self.collections_metadata)} 个集合的元数据")
    
    def _load_collections_metadata(self):
        """从JSON文件加载集合元数据"""
        # 导入collection_metadata模块
        from rag_assistant.collection_metadata import list_collections
        # 使用list_collections获取所有集合元数据
        self.collections_metadata = list_collections()

    def initialize(self, collection_name, embedding_model="BAAI/bge-small-zh-v1.5", use_llm=False, top_k=5,**kwargs):
        """为特定集合初始化RAG管道"""
        pipeline_name = f"{collection_name}_usellm_topk{top_k}" if use_llm else f"{collection_name}_topk{top_k}"
        if self.initialized and hasattr(self, 'current_pipeline') and self.current_pipeline == collection_name:
            logger.debug(f"已经为集合 '{collection_name}' 初始化了管道，重用现有实例")
            return True  # 如果已经为该集合初始化，直接返回成功
            
        try:
            logger.info(f"正在为集合 '{collection_name}' 初始化RAG管道...")
            
            # 在这里导入RAG管道，以避免循环导入
            from rag_assistant.rag_pipeline import RAGPipeline

            # 从元数据中获取嵌入模型（如果可用）
            if collection_name in self.collections_metadata:
                embedding_model = self.collections_metadata[collection_name].get("embedding_model")
                logger.debug(f"使用集合 '{collection_name}' 的原有嵌入模型: {embedding_model}")

            # 初始化管道
            chroma_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db"))
            
            self.pipeline = RAGPipeline(
                collection_name=collection_name,  # 集合名称
                embedding_model=embedding_model,  # 嵌入模型
                persist_dir=chroma_path,  # 持久化目录
                use_llm=use_llm,
                **kwargs  # 其他参数
            )
            
            self.initialized = True  # 设置初始化状态为成功
            self.current_pipeline = pipeline_name  # 记录当前集合名称
            logger.info(f"集合 '{collection_name}' 的RAG管道初始化成功")
            return True  # 返回初始化成功
            
        except Exception as e:
            logger.error(f"初始化集合 '{collection_name}' 的RAG管道失败: {e}")
            return False  # 返回初始化失败
    
    def query_embeddings(self, query_text, collection_name, top_k=5):
        """查询文档嵌入并返回结果"""
        if not self.initialize(collection_name=collection_name, top_k=top_k):  # 如果初始化失败
            # 返回错误信息而不是抛出异常
            return {
                "error": f"Failed to initialize RAG pipeline for {collection_name}",
                "documents": [],
                "query": query_text,
                "collection_name": collection_name
            }
            
        try:
            # 查询嵌入
            # Query the embeddings
            results = self.pipeline.run(
                query=query_text  # 查询文本
            )
            
            # 格式化结果
            # Format the results
            documents = []
            if "retriever" in results and "documents" in results["retriever"]:
                for doc in results["retriever"]["documents"]:  # 遍历文档
                    documents.append({
                        "content": doc.content,  # 文档内容
                        "metadata": doc.meta,  # 文档元数据
                        "score": float(doc.score) if hasattr(doc, 'score') else 0.0  # 相关性得分
                    })
                
            return {
                "documents": documents,  # 文档列表
                "query": query_text,  # 查询文本
            }
            
        except Exception as e:
            # 返回错误信息而不是抛出异常
            return {
                "error": f"Error querying embeddings: {str(e)}",
                "documents": [],
                "query": query_text,
                "collection_name": collection_name
            }
    
    def query_by_title(self, query_text, collection_name, title, top_k=5, soft_match=True):
        """按文档标题过滤查询结果，支持软匹配"""
        if not self.initialize(collection_name=collection_name, top_k=top_k):  # 如果初始化失败
            # 不抛出异常，而是返回错误信息
            return {
                "error": f"Failed to initialize RAG pipeline for {collection_name}",
                "documents": [],
                "query": query_text,
                "collection_name": collection_name
            }
            
        try:
            # 确保集合的标题列表已缓存
            if collection_name not in self._collections_titles_cache:
                _ = self.verify_collection(collection_name, show_title_list=True)
            
            actual_title = title
            closest_title = None
            
            # 确保标题使用UTF-8编码，防止GBK编码错误
            try:
                # 尝试规范化标题文本，消除特殊字符可能造成的编码问题
                import unicodedata
                normalized_title = unicodedata.normalize('NFKD', title)
                logger.debug(f"Original title: '{title}', Normalized title: '{normalized_title}'")
                
                # 如果标题包含非ASCII字符，记录日志
                if not all(ord(c) < 128 for c in title):
                    logger.info(f"Title contains non-ASCII characters: '{title}'")
            except Exception as e:
                logger.warning(f"Error normalizing title: {e}")
                # 继续使用原始标题
            
            # 使用管道方法进行查询
            try:
                # 先尝试精确匹配
                logger.debug(f"Attempting exact title match for: '{actual_title}'")
                results = self.pipeline.run_with_selected_title(
                    query=query_text,  # 查询文本
                    title=actual_title  # 文档标题
                )
                
                # 如果结果为空且软匹配模式开启，尝试软匹配
                if (not results.get("retriever", {}).get("documents", []) and soft_match and 
                        collection_name in self._collections_titles_cache):
                    closest_title = self._find_closest_title(collection_name, title)
                    if closest_title and closest_title != title:
                        actual_title = closest_title
                        logger.info(f"Using closest title match: '{actual_title}'")
                        # 使用最相似的标题重新查询
                        results = self.pipeline.run_with_selected_title(
                            query=query_text,
                            title=actual_title,
                        )
                    else:
                        logger.warning(f"No close title match found for '{title}'")
            except Exception as e:
                # 记录详细的错误信息以便调试
                error_msg = f"Error in exact title match: {str(e)}"
                logger.error(error_msg)
                
                # 如果精确匹配失败并且启用了软匹配，尝试软匹配
                if soft_match:
                    try:
                        closest_title = self._find_closest_title(collection_name, title)
                        if closest_title:
                            actual_title = closest_title
                            logger.info(f"After error, using closest title: '{actual_title}'")
                            # 使用最相似的标题查询
                            results = self.pipeline.run_with_selected_title(
                                query=query_text,
                                title=actual_title
                            )
                        else:
                            # 返回错误信息，而不是抛出异常
                            return {
                                "error": f"No matching title found for '{title}' in collection '{collection_name}'",
                                "documents": [],
                                "query": query_text,
                                "collection_name": collection_name,
                                "filtered_by_title": title
                            }
                    except Exception as soft_match_e:
                        logger.error(f"Error during soft matching: {soft_match_e}")
                        return {
                            "error": f"Error in title matching: {str(e)}, then during soft matching: {str(soft_match_e)}",
                            "documents": [],
                            "query": query_text,
                            "collection_name": collection_name,
                            "filtered_by_title": title
                        }
                else:
                    # 返回错误信息，而不是抛出异常
                    return {
                        "error": f"Error querying with title '{title}': {str(e)}",
                        "documents": [],
                        "query": query_text,
                        "collection_name": collection_name,
                        "filtered_by_title": title
                    }
            
            # 格式化结果
            documents = []
            if "retriever" in results and "documents" in results["retriever"]:
                for doc in results["retriever"]["documents"]:  # 遍历文档
                    try:
                        document_entry = {
                            "content": doc.content,  # 文档内容
                            "metadata": doc.meta,  # 文档元数据
                            "score": float(doc.score) if hasattr(doc, 'score') else 0.0  # 相关性得分
                        }
                        documents.append(document_entry)
                    except Exception as doc_e:
                        # 如果处理单个文档时出错，记录错误但继续处理其他文档
                        logger.error(f"Error processing document: {doc_e}")
                
            return {
                "documents": documents,  # 文档列表
                "query": query_text,  # 查询文本
                "actual_title": actual_title,
                "closest_title": closest_title if closest_title else actual_title,
            }
            
        except Exception as e:
            logger.error(f"Unhandled error in query_by_title: {e}", exc_info=True)
            # 返回错误信息，而不是抛出异常
            return {
                "error": f"Error querying by title: {str(e)}",
                "documents": [],
                "query": query_text,
                "collection_name": collection_name,
                "filtered_by_title": title
            }
    
    def get_collections(self):
        """获取可用集合的信息"""
        try:
            collections = []
            
            for name, metadata in self.collections_metadata.items():  # 遍历集合元数据
                embedding_model = metadata.get("embedding_model", "unknown")  # 获取嵌入模型
                
                # 尝试获取文档数量
                # Try to get document count
                document_count = 0
                try:
                    # We don't want to fully initialize just for count, 
                    # maybe rely on a potentially faster method if available or skip
                    # For now, we will skip the count as initializing can be slow
                    # if self.initialize(name):  # 如果初始化成功
                    #     document_count = len(self.pipeline.document_store.get_all_documents())  # 获取文档数量
                    pass # Skipping count for performance
                except Exception as count_e:
                    logger.debug(f"Skipped document count for '{name}': {count_e}")
                    
                collections.append({
                    "name": name,  # 集合名称
                    "document_count": document_count,  # 文档数量 (Currently 0)
                    "embedding_model": embedding_model,  # 嵌入模型
                })
                
            return {"collections": collections}  # 返回集合列表
            
        except Exception as e:
            logger.error(f"Error getting collections: {e}")
            return {"error": f"Error getting collections: {e}", "collections": []}

    def verify_collection(self, collection_name: str, show_title_list: bool = False):
        """
        验证集合是否存在，并可选择性地返回其文档标题列表。

        Args:
            collection_name: 要验证的集合名称。
            show_title_list: 如果为True，则返回标题列表而不是布尔值。

        Returns:
            - 如果集合不存在，返回 False。
            - 如果集合存在且 show_title_list 为 False，返回 True。
            - 如果集合存在且 show_title_list 为 True，返回包含唯一标题的列表（set转换为list）。
            - 如果在获取标题时出错（例如，初始化失败），返回空列表 []。
        """
        if collection_name not in self.collections_metadata:
            return False  # 集合元数据中不存在

        if not show_title_list:
            return True  # 集合存在，且不需要标题列表

        # 检查是否已缓存该集合的标题列表
        if collection_name in self._collections_titles_cache:
            return list(self._collections_titles_cache[collection_name])

        # 需要获取标题列表
        try:
            # 尝试为该集合初始化（或复用已初始化的）管道
            if not self.initialize(collection_name):
                logger.warning(f"Failed to initialize pipeline for collection '{collection_name}' to get titles.")
                return [] # 初始化失败，返回空列表表示错误

            # 获取所有文档
            all_docs = self.pipeline.document_store.filter_documents({})
            
            # 提取唯一的标题
            titles = set()
            for doc in all_docs:
                if doc.meta and "title" in doc.meta and doc.meta["title"] is not None:
                    titles.add(doc.meta["title"])
            
            # 将标题列表缓存起来
            self._collections_titles_cache[collection_name] = titles
            
            return list(titles) # 返回标题列表
            
        except Exception as e:
            logger.error(f"Error verifying collection or getting titles for '{collection_name}': {e}")
            return [] # 其他获取文档或处理过程中的错误

    def _find_closest_title(self, collection_name, title):
        """
        在集合中找到与给定标题最相似的标题

        Args:
            collection_name: 集合名称
            title: 要匹配的标题

        Returns:
            最相似的标题，如果没有找到则返回None
        """
        # 如果集合标题未缓存，先获取
        if collection_name not in self._collections_titles_cache:
            titles = self.verify_collection(collection_name, show_title_list=True)
            if not titles:  # 如果无法获取标题列表，返回None
                return None
        else:
            titles = self._collections_titles_cache[collection_name]
        
        if not titles:
            return None
            
        # 计算最相似的标题
        try:
            import difflib
            
            # 使用difflib中的SequenceMatcher计算相似度
            def similarity(a, b):
                return difflib.SequenceMatcher(None, a, b).ratio()
            
            # 计算所有标题与目标标题的相似度
            similarities = [(t, similarity(t.lower(), title.lower())) for t in titles]
            
            # 按相似度排序并返回最相似的
            closest = max(similarities, key=lambda x: x[1])
            
            logger.info(f"未找到精确匹配标题 '{title}'，使用最相似的标题: '{closest[0]}' (相似度: {closest[1]:.2f})")
            
            return closest[0]
            
        except Exception as e:
            logger.error(f"Error finding closest title: {e}")
            return None

# 全局RAG管道包装器实例
rag_wrapper = RAGPipelineWrapper()

# 集合列表
@mcp.tool()
def list_collections():
    """获取所有可用的集合"""
    return rag_wrapper.get_collections()

# 查询
@mcp.tool()
def query_embeddings(query:str, collection_name:str, top_k:int):
    """执行嵌入查询并返回结果"""
    return rag_wrapper.query_embeddings(query, collection_name, top_k)

# 按标题过滤查询    
@mcp.tool()
def query_by_title(query:str, collection_name:str, title:str, top_k:int=5, soft_match:bool=True):
    """按文档标题过滤执行查询，支持软匹配最相似标题"""
    return rag_wrapper.query_by_title(query, collection_name, title, top_k, soft_match)

# 验证集合并获取标题    
@mcp.tool()
def verify_collection(collection_name: str, show_title_list: bool = False):
    """验证集合是否存在，可选返回标题列表"""
    return rag_wrapper.verify_collection(collection_name, show_title_list)
    
if __name__ == "__main__":
    # Pre-initialize collections for faster first requests
    logger.info("Starting pre-initialization of collections...")
    try:
        # Get available collections
        collections_info = rag_wrapper.get_collections()
        
        if "collections" in collections_info:
            collections = collections_info["collections"]
            logger.info(f"Found {len(collections)} collections to pre-initialize")
            
            # Initialize the first collection (if any exist) to warm up the models
            if collections:
                first_collection = collections[0]["name"]
                logger.info(f"Pre-initializing first collection: {first_collection}")
                # Initialize without LLM for faster startup
                success = rag_wrapper.initialize(first_collection, use_llm=False)
                if success:
                    logger.info(f"Successfully pre-initialized collection: {first_collection}")
                else:
                    logger.warning(f"Failed to pre-initialize collection: {first_collection}")
    except Exception as e:
        logger.error(f"Error during pre-initialization: {e}")

    # Initialize and run the server
    logger.info("Starting MCP server with stdio transport")
    mcp.run(transport='stdio')