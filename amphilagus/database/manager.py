"""
Database management module for interacting with ChromaDB vector database.
"""
import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Union, Tuple

# 导入ChromaDB相关
import chromadb

# 导入rag_assistant的相关模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .collection_metadata import list_collections, get_collection_metadata, delete_collection_metadata
from .document_loader import load_documents, chunk_documents
from ..pipeline.basic import RAGPipeline
from .custom_document_store import CustomChromaDocumentStore


class DatabaseManager:
    """
    Manages ChromaDB databases and collections.
    """
    def __init__(self, chroma_db_path: str = 'chroma_db', 
                 metadata_file: str = 'collection_metadata.json'):
        """
        Initialize the database manager.
        
        Args:
            chroma_db_path: Path to the ChromaDB database directory
            metadata_file: Path to the collection metadata file
        """
        self.chroma_db_path = Path(chroma_db_path)
        self.metadata_file = Path(metadata_file)
        self.pipelines = {}  # 存储已初始化的pipelines
        
        # 尝试加载ChromaDB客户端
        try:
            if os.path.exists(self.chroma_db_path):
                self.client = chromadb.PersistentClient(path=str(self.chroma_db_path))
            else:
                os.makedirs(self.chroma_db_path, exist_ok=True)
                self.client = chromadb.PersistentClient(path=str(self.chroma_db_path))
        except Exception as e:
            print(f"Error initializing ChromaDB client: {str(e)}")
            self.client = None
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all collections with their details.
        
        Returns:
            List of collection details including metadata and statistics
        """
        # 获取元数据中记录的collections
        metadata_collections = list_collections()
        
        collections_info = []
        chroma_collection_names = []
        collection_details = {}
        
        # 获取实际存在的collections
        if self.client:
            try:
                chroma_collections = self.client.list_collections()
                chroma_collection_names = [col.name for col in chroma_collections]
                
                # 获取更多详细信息
                for col in chroma_collections:
                    try:
                        count = col.count()
                        collection_details[col.name] = {
                            "count": count,
                            "metadata": col.metadata or {}
                        }
                    except Exception as e:
                        print(f"Error getting details for collection {col.name}: {str(e)}")
                        collection_details[col.name] = {
                            "count": 0,
                            "metadata": {}
                        }
            except Exception as e:
                print(f"Error listing collections: {str(e)}")
        
        # 合并信息
        # 首先添加实际存在的collections
        for col_name in chroma_collection_names:
            info = {
                "name": col_name,
                "exists_in_chroma": True,
                "exists_in_metadata": col_name in metadata_collections,
                "doc_count": collection_details.get(col_name, {}).get("count", 0),
                "metadata": collection_details.get(col_name, {}).get("metadata", {})
            }
            
            # 添加元数据信息（如果存在）
            if col_name in metadata_collections:
                info.update({
                    "embedding_model": metadata_collections[col_name].get("embedding_model", "未知"),
                    "created_at": metadata_collections[col_name].get("created_at", "未知")
                })
            else:
                info.update({
                    "embedding_model": "未知",
                    "created_at": "未知"
                })
                
            collections_info.append(info)
        
        # 添加仅在元数据中存在的collections
        for col_name, col_meta in metadata_collections.items():
            if col_name not in chroma_collection_names:
                collections_info.append({
                    "name": col_name,
                    "exists_in_chroma": False,
                    "exists_in_metadata": True,
                    "doc_count": 0,
                    "embedding_model": col_meta.get("embedding_model", "未知"),
                    "created_at": col_meta.get("created_at", "未知"),
                    "metadata": {}
                })
        
        # 按名称排序
        collections_info.sort(key=lambda x: x["name"])
        
        return collections_info
    
    def get_collection_details(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """
        获取单个collection的详细信息
        
        Args:
            collection_name: Collection名称
            
        Returns:
            包含collection详细信息的字典，如果不存在则返回None
        """
        if not self.client:
            return None
            
        try:
            # 获取元数据
            metadata = get_collection_metadata(collection_name)
            
            # 检查collection是否存在
            collections = self.client.list_collections()
            collection_names = [col.name for col in collections]
            
            if collection_name in collection_names:
                # 获取ChromaDB中的collection
                collection = self.client.get_collection(collection_name)
                doc_count = collection.count()
                
                return {
                    "name": collection_name,
                    "exists_in_chroma": True,
                    "exists_in_metadata": metadata is not None,
                    "doc_count": doc_count,
                    "embedding_model": metadata.get("embedding_model", "未知") if metadata else "未知",
                    "created_at": metadata.get("created_at", "未知") if metadata else "未知",
                    "metadata": collection.metadata or {}
                }
            elif metadata:
                # 只在元数据中存在
                return {
                    "name": collection_name,
                    "exists_in_chroma": False,
                    "exists_in_metadata": True,
                    "doc_count": 0,
                    "embedding_model": metadata.get("embedding_model", "未知"),
                    "created_at": metadata.get("created_at", "未知"),
                    "metadata": {}
                }
            
            return None
        except Exception as e:
            print(f"Error getting collection details: {str(e)}")
            return None
    
    def delete_collection(self, collection_name: str) -> Tuple[bool, str]:
        """
        删除一个collection
        
        Args:
            collection_name: 要删除的collection名称
            
        Returns:
            (成功标志, 消息)
        """
        if not self.client:
            return False, "ChromaDB客户端未初始化"
        
        try:
            # 检查collection是否存在
            collections = self.client.list_collections()
            collection_names = [col.name for col in collections]
            
            if collection_name in collection_names:
                # 删除ChromaDB中的collection
                self.client.delete_collection(collection_name)
                
                # 删除元数据
                delete_collection_metadata(collection_name)
                
                return True, f"Collection '{collection_name}' 已成功删除"
            else:
                # 检查是否只在元数据中存在
                metadata = get_collection_metadata(collection_name)
                if metadata:
                    # 只删除元数据
                    delete_collection_metadata(collection_name)
                    return True, f"Collection '{collection_name}' 的元数据已删除"
                
                return False, f"Collection '{collection_name}' 不存在"
        except Exception as e:
            return False, f"删除Collection时出错: {str(e)}"
    
    def get_db_path(self) -> str:
        """
        获取数据库路径
        
        Returns:
            ChromaDB数据库的路径
        """
        return str(self.chroma_db_path)
    
    def get_db_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            包含统计信息的字典
        """
        collections = self.list_collections()
        
        normal_collections = [c for c in collections if c["exists_in_chroma"] and c["exists_in_metadata"]]
        missing_metadata = [c for c in collections if c["exists_in_chroma"] and not c["exists_in_metadata"]]
        orphaned_metadata = [c for c in collections if not c["exists_in_chroma"] and c["exists_in_metadata"]]
        
        # 计算总文档数
        total_docs = sum(c["doc_count"] for c in collections if c["exists_in_chroma"])
        
        return {
            "total_collections": len(collections),
            "normal_collections": len(normal_collections),
            "missing_metadata": len(missing_metadata),
            "orphaned_metadata": len(orphaned_metadata),
            "total_documents": total_docs
        }
    
    def get_document_details(self, collection_name: str, document_id: str = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        获取collection中的文档详情
        
        Args:
            collection_name: Collection名称
            document_id: 特定文档ID，如果为None则获取所有文档
            limit: 每页显示的文档数量
            offset: 分页偏移量
            
        Returns:
            文档详情字典
        """
        if not self.client:
            return {
                "success": False,
                "message": "ChromaDB客户端未初始化",
                "documents": [],
                "total": 0
            }
            
        # 获取文档详情
        if document_id:
            # 获取特定文档
            chroma_collection = self.client.get_collection(collection_name)
            result = chroma_collection.get(ids=[document_id])
            
            if not result["ids"]:
                return {
                    "success": False,
                    "message": f"未找到ID为{document_id}的文档",
                    "documents": [],
                    "total": 0
                }
            
            documents = [{
                "id": result["ids"][0],
                "metadata": result["metadatas"][0] if result["metadatas"] else {},
                "content": result["documents"][0] if result["documents"] else "",
                "embedding_available": len(result["embeddings"]) > 0 if "embeddings" in result else False
            }]
            
            return {
                "success": True,
                "message": "成功获取文档详情",
                "documents": documents,
                "total": 1
            }
        else:
            # 获取所有文档（分页）
            chroma_collection = self.client.get_collection(collection_name)
            
            # 获取总文档数
            total_docs = chroma_collection.count()
            
            # 限制查询数量
            if offset >= total_docs:
                return {
                    "success": True,
                    "message": "没有更多文档",
                    "documents": [],
                    "total": total_docs,
                    "offset": offset,
                    "limit": limit
                }
            
            # 获取文档列表
            result = chroma_collection.get(limit=limit, offset=offset)
            
            documents = []
            for i, doc_id in enumerate(result["ids"]):
                documents.append({
                    "id": doc_id,
                    "metadata": result["metadatas"][i] if result["metadatas"] else {},
                    "content_preview": result["documents"][i][:200] + "..." if result["documents"] and len(result["documents"][i]) > 200 else result["documents"][i],
                    "embedding_available": True  # ChromaDB默认都有嵌入
                })
            
            return {
                "success": True,
                "message": "成功获取文档列表",
                "documents": documents,
                "total": total_docs,
                "offset": offset,
                "limit": limit
            }

    
    def init_pipeline(self, collection_name: str) -> Tuple[bool, str, Optional[RAGPipeline]]:
        """
        为特定collection初始化RAG Pipeline
        
        Args:
            collection_name: Collection名称
            
        Returns:
            (成功标志, 消息, pipeline对象)
        """
        # 如果已经初始化过，直接返回
        if collection_name in self.pipelines:
            return True, f"Pipeline已初始化", self.pipelines[collection_name]
            
        try:
            # 检查collection是否存在
            metadata = get_collection_metadata(collection_name)
            if not metadata:
                return False, f"未找到Collection '{collection_name}'的元数据，无法初始化Pipeline", None
                
            # 获取嵌入模型名称
            embedding_model = metadata.get("embedding_model")
            if not embedding_model:
                return False, f"Collection '{collection_name}'的元数据中未找到嵌入模型信息", None
                
            # 初始化pipeline (不包含LLM组件)
            pipeline = RAGPipeline(
                collection_name=collection_name,
                embedding_model=embedding_model,
                use_llm=False  # 不使用LLM生成
            )
            
            # 保存pipeline实例
            self.pipelines[collection_name] = pipeline
            
            return True, f"成功初始化Collection '{collection_name}'的Pipeline", pipeline
            
        except Exception as e:
            return False, f"初始化Pipeline时出错: {str(e)}", None
    
    def add_files(self, collection_name: str, document_content: str, metadata: Dict[str, Any] = None) -> Tuple[bool, str, Optional[str]]:
        """
        添加文档到collection
        
        Args:
            collection_name: Collection名称
            document_content: 文档内容
            metadata: 文档元数据
            
        Returns:
            (成功标志, 消息, 文档ID)
        """
        # 检查pipeline是否已初始化
        if collection_name not in self.pipelines:
            success, message, pipeline = self.init_pipeline(collection_name)
            if not success:
                return False, message, None
        else:
            pipeline = self.pipelines[collection_name]
        
        try:
            # 使用RAG Pipeline添加文档
            pipeline.add_document(document_content, check_duplicates=True)
            
            return True, f"成功添加文档", document_id
            
        except Exception as e:
            return False, f"添加文档时出错: {str(e)}", None

    def search_documents(self, collection_name: str, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        在collection中搜索文档
        
        Args:
            collection_name: Collection名称
            query: 搜索查询
            top_k: 返回结果数量
            
        Returns:
            搜索结果字典
        """
        # 检查pipeline是否已初始化
        if collection_name not in self.pipelines:
            success, message, pipeline = self.init_pipeline(collection_name)
            if not success:
                return {
                    "success": False,
                    "message": message,
                    "results": []
                }
        else:
            pipeline = self.pipelines[collection_name]
        
        try:
            # 使用pipeline执行搜索
            results = pipeline.retrieve(query, top_k=top_k)
            
            # 格式化结果
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "id": doc.id,
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "score": doc.score if hasattr(doc, 'score') else None
                })
                
            return {
                "success": True,
                "message": f"搜索成功，找到 {len(formatted_results)} 个结果",
                "results": formatted_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"搜索时出错: {str(e)}",
                "results": []
            }
    
    def delete_document(self, collection_name: str, document_id: str) -> Tuple[bool, str]:
        """
        从collection中删除文档
        
        Args:
            collection_name: Collection名称
            document_id: 文档ID
            
        Returns:
            (成功标志, 消息)
        """
        if not self.client:
            return False, "ChromaDB客户端未初始化"
        
        try:
            # 获取collection
            chroma_collection = self.client.get_collection(collection_name)
            
            # 检查文档是否存在
            result = chroma_collection.get(ids=[document_id])
            if not result["ids"]:
                return False, f"未找到ID为{document_id}的文档"
                
            # 删除文档
            chroma_collection.delete(ids=[document_id])
            
            return True, f"成功删除文档 {document_id}"
            
        except Exception as e:
            return False, f"删除文档时出错: {str(e)}"

    def embed_files(self, collection_name: str, file_paths: List[str], 
                    chunk_size: int = 1000, chunk_overlap: int = 200,
                    check_duplicates: bool = True) -> Tuple[bool, str, Dict[str, Any]]:
        """
        将文件嵌入到向量数据库中
        
        步骤:
        1. 检查pipeline是否已初始化
        2. 使用rag_assistant的load_documents方法把files转化为haystack的document
        3. 使用rag_assistant的chunk_documents切片
        4. 使用rag_pipeline.add_documents嵌入
        
        Args:
            collection_name: 集合名称
            file_paths: 文件路径列表
            chunk_size: 文档切片大小
            chunk_overlap: 切片重叠大小
            check_duplicates: 是否检查重复文档
            
        Returns:
            (成功标志, 消息, 结果统计)
        """
        # 1. 检查pipeline是否已初始化
        if collection_name not in self.pipelines:
            success, message, pipeline = self.init_pipeline(collection_name)
            if not success:
                return False, message, {"processed": 0, "errors": [message]}
        else:
            pipeline = self.pipelines[collection_name]
        
        stats = {
            "processed": 0,
            "chunked": 0,
            "errors": [],
            "skipped": [],
            "files": []
        }
        
        try:
            # 确保文件存在
            existing_files = []
            for file_path in file_paths:
                if os.path.exists(file_path):
                    existing_files.append(file_path)
                else:
                    stats["errors"].append(f"文件不存在: {file_path}")
            
            if not existing_files:
                return False, "没有找到可处理的文件", stats
            
            # 2. 使用rag_assistant的load_documents方法直接加载指定文件
            # 获取文件类型(扩展名)，不带点号
            file_types = set()
            for file_path in existing_files:
                ext = os.path.splitext(file_path)[1].lower().lstrip('.')
                if ext:  # 只添加非空扩展名
                    file_types.add(ext)
            
            # 如果没有识别到文件类型，使用默认值
            if not file_types:
                file_types = ['pdf', 'txt', 'md', 'html', 'htm', 'docx']
            
            try:
                # 以指定文件模式调用load_documents
                # 使用当前目录作为基准目录（仅影响日志输出）
                documents = load_documents(".", file_types=list(file_types), specific_files=existing_files)
                
                # 更新统计信息
                stats["processed"] = len(existing_files)
                stats["files"] = [os.path.basename(f) for f in existing_files]
                
            except Exception as e:
                return False, f"加载文档时出错: {str(e)}", stats
            
            if not documents:
                return False, "未能从文件中提取任何文档", stats
            
            # 3. 使用rag_assistant的chunk_documents切片
            try:
                chunked_documents = chunk_documents(documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
                stats["chunked"] = len(chunked_documents)
            except Exception as e:
                return False, f"文档切片时出错: {str(e)}", stats
            
            # 4. 使用rag_pipeline.add_documents嵌入
            try:
                pipeline.add_documents(chunked_documents, check_duplicates=check_duplicates)
                
                return True, f"成功处理 {stats['processed']} 个文件，生成 {stats['chunked']} 个文档片段", stats
                
            except Exception as e:
                return False, f"文档嵌入时出错: {str(e)}", stats
            
        except Exception as e:
            return False, f"文件嵌入处理时出错: {str(e)}", stats 