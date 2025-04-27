"""
Retriever Module

This module provides specialized RAG pipelines focused on embedding and retrieval without LLM components.
These pipelines are optimized for scenarios where only document retrieval is needed, without answer generation.
"""

import os
from typing import List, Dict, Any, Optional

from haystack import Pipeline, Document
from haystack.components.embedders import SentenceTransformersTextEmbedder

from .basic import RAGPipeline
from ..logger import get_logger

# Get logger
logger = get_logger("retriever")

class EmbeddingOnlyPipeline(RAGPipeline):
    """
    A specialized RAGPipeline that focuses only on embedding-based retrieval without LLM components.
    This pipeline is optimized for scenarios where only document retrieval is needed, without answer generation.
    """
    
    def __init__(self, 
                embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                top_k: int = 5,
                api_key: Optional[str] = None,
                persist_dir: str = None,
                collection_name: str = "documents",
                reset_collection: bool = False,
                hard_reset: bool = False):
        """
        Initialize an embedding-only pipeline.
        
        Args:
            embedding_model: Model to use for document and query embedding
            top_k: Number of documents to retrieve
            api_key: OpenAI API key (for compatibility with parent class)
            persist_dir: Directory for persistent storage of Chroma embeddings
            collection_name: Name of the Chroma collection to use
            reset_collection: Whether to reset (clear) the collection if it exists
            hard_reset: If True, completely delete the existing collection
        """
        # Initialize parent class with use_llm=False to skip LLM components
        super().__init__(
            embedding_model=embedding_model,
            top_k=top_k,
            api_key=api_key,
            persist_dir=persist_dir, 
            collection_name=collection_name,
            reset_collection=reset_collection,
            hard_reset=hard_reset,
            use_llm=False  # Key setting: don't initialize LLM components
        )
        
        logger.info(f"Initialized EmbeddingOnlyPipeline with model {embedding_model}")
    
    def run(self, query: str, only_most_related_articles: bool = False) -> Dict[str, Any]:
        """
        Override the run method to provide additional metadata with retrieved documents.
        
        Args:
            query: User query text
            only_most_related_articles: If True, only return most related articles based on scores (default: False)
            
        Returns:
            Dictionary with retrieved documents and organized metadata
        """
        results = self.current_pipeline.run({
                "text_embedder": {"text": query},
            })
        # logger.debug(results)
        retrieved_documents = results["retriever"]["documents"]
        retrieved_contents = []
        
        for doc in retrieved_documents:
            doc_info = {'content': doc.content, 'score': doc.score}
            if doc.meta and "title" in doc.meta and only_most_related_articles:
                doc_info.update({'title': doc.meta['title']})
            retrieved_contents.append(doc_info)
            
        # 当only_most_related_articles为True时，处理最相关文章
        if only_most_related_articles:
            # 按score排序
            sorted_docs = sorted(retrieved_contents, key=lambda x: x.get('score', 0), reverse=True)
            
            # 选出前五个高分文档
            top_five_docs = sorted_docs[:5] if len(sorted_docs) >= 5 else sorted_docs
            
            # 按title分组并计算总分
            title_scores = {}
            for doc in top_five_docs:
                title = doc.get('title', 'Unknown')
                if title in title_scores:
                    title_scores[title] += doc.get('score', 0)
                else:
                    title_scores[title] = doc.get('score', 0)
            
            # 按总分排序
            sorted_titles = sorted(title_scores.items(), key=lambda x: x[1], reverse=True)
            
            # 构建结果
            most_related_articles = []
            for title, total_score in sorted_titles:
                most_related_articles.append({
                    'title': title,
                    'total_score': total_score
                })
            
            return {
                "most_related_articles": most_related_articles
            }
        
        # logger.debug(retrieved_contents)
        return {"retrieved_contents": retrieved_contents}
