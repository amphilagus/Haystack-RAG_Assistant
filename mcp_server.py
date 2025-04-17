from mcp.server.fastmcp import FastMCP
import os

# Initialize FastMCP server
mcp = FastMCP("rag_assistant")

class RAGPipelineWrapper:
    def __init__(self):
        """初始化RAG管道包装器"""
        self.pipeline = None  # 初始化管道为空
        self.initialized = False  # 初始化状态为未初始化
        self.collections_metadata = {}  # 初始化集合元数据为空字典
        self._load_collections_metadata()  # 加载集合元数据
    
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
            return True  # 如果已经为该集合初始化，直接返回成功
            
        try:
            # 在这里导入RAG管道，以避免循环导入
            from rag_assistant.rag_pipeline import RAGPipeline

            # 从元数据中获取嵌入模型（如果可用）
            if collection_name in self.collections_metadata:
                embedding_model = self.collections_metadata[collection_name].get("embedding_model")

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
            return True  # 返回初始化成功
            
        except Exception as e:
            return False  # 返回初始化失败
    
    def query_embeddings(self, query_text, collection_name, top_k=5):
        """查询文档嵌入并返回结果"""
        if not self.initialize(collection_name=collection_name, top_k=top_k):  # 如果初始化失败
            raise Exception(f"Failed to initialize RAG pipeline for {collection_name}")  # 抛出异常
            
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
                "results": results,
                "documents": documents,  # 文档列表
                "query": query_text,  # 查询文本
                "collection_name": collection_name  # 集合名称
            }
            
        except Exception as e:
            raise Exception(f"Error querying embeddings: {str(e)}")  # 抛出异常
    
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
                    if self.initialize(name):  # 如果初始化成功
                        document_count = len(self.pipeline.document_store.get_all_documents())  # 获取文档数量
                except:
                    pass
                    
                collections.append({
                    "name": name,  # 集合名称
                    "document_count": document_count,  # 文档数量
                    "embedding_model": embedding_model  # 嵌入模型
                })
                
            return {"collections": collections}  # 返回集合列表
            
        except Exception as e:
            raise Exception(f"Error getting collections: {str(e)}")  # 抛出异常

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
    
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')