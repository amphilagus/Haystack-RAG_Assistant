from mcp.server.fastmcp import FastMCP
import os
import sys
import locale
from typing import Dict, List, Optional, Any

from rag_assistant.logger import get_logger
logger = get_logger("mcp_server")

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
        self.current_pipeline = None  # 初始化当前管道名称
        self._load_collections_metadata()  # 加载集合元数据
        logger.info(f"已加载 {len(self.collections_metadata)} 个集合的元数据")
    
    def _load_collections_metadata(self):
        """从JSON文件加载集合元数据"""
        # 导入collection_metadata模块
        from rag_assistant.collection_metadata import list_collections
        # 使用list_collections获取所有集合元数据
        self.collections_metadata = list_collections()

    def initialize(self, collection_name, embedding_model="BAAI/bge-small-zh-v1.5", use_llm=False, top_k=5,**kwargs):
        """为特定集合初始化RAG管道"""
        # 不再以top_k作为管道命名的一部分，因为现在可以动态设置top_k
        pipeline_name = f"{collection_name}_usellm" if use_llm else f"{collection_name}"
        if self.initialized and hasattr(self, 'current_pipeline') and self.current_pipeline == pipeline_name:
            # 如果已经为该集合初始化了管道，检查是否需要更新top_k
            if hasattr(self.pipeline, 'set_top_k'):
                logger.debug(f"重用已有管道并设置top_k={top_k}")
                self.pipeline.set_top_k(top_k)
            return True
            
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
                top_k=top_k,  # 初始top_k值
                **kwargs  # 其他参数
            )
            
            self.initialized = True  # 设置初始化状态为成功
            self.current_pipeline = pipeline_name  # 记录当前管道名称
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
            # 查询嵌入，不再需要重新创建管道，直接运行
            results = self.pipeline.run(query=query_text)
            
            # 格式化结果
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
            # 直接使用pipeline中的run_with_selected_title方法，该方法已整合了软匹配功能
            results = self.pipeline.run_with_selected_title(
                query=query_text,          # 查询文本
                title=title,               # 文档标题
                soft_match=soft_match,     # 是否启用软匹配
                similarity_threshold=0.01  # 相似度阈值
            )
            
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
            
            # 获取实际使用的标题和软匹配信息
            actual_title = results.get("actual_title", title)
            soft_match_used = results.get("soft_match_used", False)
            
            return {
                "documents": documents,                # 文档列表
                "query": query_text,                   # 查询文本
                "collection_name": collection_name,    # 集合名称
                "filtered_by_title": title,            # 请求的标题
                "actual_title": actual_title,          # 实际使用的标题
                "soft_match_used": soft_match_used     # 是否使用了软匹配
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

        try:
            # 先尝试从title_matcher中获取缓存的标题
            from rag_assistant.title_matcher import title_matcher
            if title_matcher.has_cached_titles(collection_name):
                logger.debug(f"从title_matcher获取集合 '{collection_name}' 的缓存标题")
                return title_matcher.get_cached_titles(collection_name)

            # 尝试为该集合初始化（或复用已初始化的）管道，使用默认的top_k值
            if not self.initialize(collection_name, top_k=5):
                logger.warning(f"Failed to initialize pipeline for collection '{collection_name}' to get titles.")
                return [] # 初始化失败，返回空列表表示错误

            # 使用_cache_all_titles方法缓存并获取所有标题
            unique_titles = self.pipeline._cache_all_titles(collection_name)
            
            return list(unique_titles) # 返回标题列表
            
        except Exception as e:
            logger.error(f"Error verifying collection or getting titles for '{collection_name}': {e}")
            return [] # 其他获取文档或处理过程中的错误

    def batch_query(self, queries: List[Dict], collection_name: str):
        """
        批量执行多个查询，每个查询可以有不同的参数和运行模式。

        Args:
            queries: 查询配置列表
            collection_name: 集合名称

        Returns:
            查询结果列表，结构与run_batch方法返回相同
        """
        if not self.initialize(collection_name=collection_name):  # 如果初始化失败
            # 返回错误信息
            return {
                "error": f"Failed to initialize RAG pipeline for {collection_name}",
                "results": []
            }
            
        try:
            # 使用pipeline的run_batch方法执行批量查询
            results = self.pipeline.run_batch(queries)
            return {
                "results": results,
                "collection_name": collection_name,
                "query_count": len(results)
            }
            
        except Exception as e:
            logger.error(f"批量查询处理失败: {str(e)}", exc_info=True)
            return {
                "error": f"Error processing batch query: {str(e)}",
                "results": [],
                "collection_name": collection_name
            }
            
    def extract_research_paper_content(self, collection_name: str, title: str, soft_match: bool = True):
        """
        一次性提取科研文献的多个关键内容板块（背景、目标、方法、结果、亮点和发布时间线）。
        
        Args:
            collection_name: 集合名称
            title: 论文标题
            soft_match: 是否使用软匹配查找最相似的标题
            
        Returns:
            包含各个科研内容板块查询结果的字典
        """
        if not self.initialize(collection_name=collection_name):
            return {
                "error": f"Failed to initialize RAG pipeline for {collection_name}",
                "aspects": {},
                "title": title,
                "collection_name": collection_name
            }
            
        try:
            # 定义要查询的各个方面及其参数
            queries = [
                {
                    "query": "background of this study",
                    "mode": "run_with_selected_title",
                    "title": title,
                    "top_k": 12
                },
                {
                    "query": "objective of this study",
                    "mode": "run_with_selected_title",
                    "title": title,
                    "top_k": 5
                },
                {
                    "query": "methods of this study",
                    "mode": "run_with_selected_title",
                    "title": title,
                    "top_k": 8
                },
                {
                    "query": "results of this study",
                    "mode": "run_with_selected_title",
                    "title": title,
                    "top_k": 20
                },
                {
                    "query": "highlights of this study",
                    "mode": "run_with_selected_title",
                    "title": title,
                    "top_k": 10
                },
                {
                    "query": "publication timeline of this study",
                    "mode": "run_with_selected_title",
                    "title": title,
                    "top_k": 5
                },
            ]
            
            # 用于每个查询记录软匹配状态
            for query in queries:
                query["soft_match"] = soft_match
                query["similarity_threshold"] = 0
                
            # 执行批量查询
            batch_results = self.batch_query(queries, collection_name, )
            
            if "error" in batch_results:
                return {
                    "error": batch_results["error"],
                    "aspects": {},
                    "title": title,
                    "collection_name": collection_name
                }
                
            # 重新组织结果，以方面名称为键
            aspects = {}
            actual_title = None
            
            for i, result in enumerate(batch_results.get("results", [])):
                aspect_name = queries[i]["query"].replace(" of this study", "").lower()
                
                # 收集实际使用的标题信息（所有查询都应使用相同的实际标题）
                if actual_title is None and "actual_title" in result:
                    actual_title = result["actual_title"]
                    
                aspects[aspect_name] = {
                    "documents": result["retriever"].get("documents", []),
                    "query": queries[i]["query"]
                }
                
            return {
                "aspects": aspects,
                "title": title,
                "actual_title": actual_title or title,
                "collection_name": collection_name,
                "soft_match_used": any(r.get("soft_match_used", False) for r in batch_results.get("results", []))
            }
            
        except Exception as e:
            logger.error(f"提取科研文献内容失败: {str(e)}", exc_info=True)
            return {
                "error": f"Error extracting research paper content: {str(e)}",
                "aspects": {},
                "title": title,
                "collection_name": collection_name
            }

# 全局RAG管道包装器实例
rag_wrapper = RAGPipelineWrapper()

# 集合列表
@mcp.tool()
def list_collections():
    """获取所有可用的集合"""
    return rag_wrapper.get_collections()

# 查询
# @mcp.tool()
# def query_embeddings(query:str, collection_name:str, top_k:int):
#     """执行嵌入查询并返回结果"""
#     return rag_wrapper.query_embeddings(query, collection_name, top_k)

# 按标题过滤查询    
@mcp.tool()
def query_by_title(query:str, collection_name:str, title:str, top_k:int=5, soft_match:bool=True):
    """按文档标题过滤执行查询，支持软匹配最相似标题"""
    return rag_wrapper.query_by_title(query, collection_name, title, top_k, soft_match)

# 批量查询
@mcp.tool()
def batch_query(queries:List[Dict], collection_name:str):
    """批量执行多个查询，每个查询可以有不同的参数和运行模式"""
    return rag_wrapper.batch_query(queries, collection_name)

# 验证集合并获取标题    
@mcp.tool()
def verify_collection(collection_name: str, show_title_list: bool = False):
    """验证集合是否存在，可选返回标题列表"""
    return rag_wrapper.verify_collection(collection_name, show_title_list)

# 提取科研文献多个内容板块
@mcp.tool()
def extract_research_paper_content(collection_name: str, title: str, soft_match: bool = True):
    """一次性提取科研文献的多个关键内容板块（背景、目标、方法、结果、亮点和时间线）"""
    return rag_wrapper.extract_research_paper_content(collection_name, title, soft_match)
    
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