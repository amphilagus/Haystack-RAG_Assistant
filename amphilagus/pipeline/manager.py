"""
Pipeline Manager Module

This module provides a manager for creating, caching, and retrieving different types of pipelines.
"""

import time
from typing import Dict, Any, Optional, List, Union, Type
import datetime

from .basic import RAGPipeline
from .retriever import EmbeddingOnlyPipeline
from ..logger import get_logger

# Get logger
logger = get_logger("pipeline")

class PipelineManager:
    """
    Manages the creation, caching, and retrieval of different types of pipelines.
    """
    
    def __init__(self):
        """Initialize the pipeline manager with an empty cache."""
        self.pipeline_cache = {}  # Dictionary to store pipelines
        self.pipeline_types = {
            "rag": RAGPipeline,
            "embedding": EmbeddingOnlyPipeline
        }
    
    def create_pipeline(self, 
                       pipeline_type: str, 
                       collection_name: str, 
                       **kwargs) -> Union[RAGPipeline, EmbeddingOnlyPipeline]:
        """
        Create a pipeline of the specified type and add it to the cache.
        
        Args:
            pipeline_type: Type of pipeline to create ("rag" or "embedding")
            collection_name: Name of the collection to use
            **kwargs: Additional arguments to pass to the pipeline constructor
            
        Returns:
            The created pipeline
        """
        # Validate pipeline type
        if pipeline_type not in self.pipeline_types:
            raise ValueError(f"Unknown pipeline type: {pipeline_type}. Available types: {list(self.pipeline_types.keys())}")
        
        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Generate a unique name for the pipeline
        pipeline_name = f"{collection_name}_{pipeline_type}_{timestamp}"
        
        # Get the pipeline class
        pipeline_class = self.pipeline_types[pipeline_type]
        
        # Create the pipeline
        logger.info(f"Creating new {pipeline_type} pipeline for collection '{collection_name}'")
        pipeline = pipeline_class(collection_name=collection_name, **kwargs)
        
        # Add a name attribute to the pipeline
        pipeline.name = pipeline_name
        
        # Cache the pipeline
        self.pipeline_cache[pipeline_name] = {
            "pipeline": pipeline,
            "type": pipeline_type,
            "collection": collection_name,
            "created_at": timestamp,
            "last_used": time.time()
        }
        
        return pipeline
    
    def get_pipeline(self, 
                    pipeline_type: Optional[str] = None,
                    collection_name: Optional[str] = None,
                    create_if_missing: bool = True,
                    **kwargs) -> Union[RAGPipeline, EmbeddingOnlyPipeline, None]:
        """
        Get a pipeline by type and collection.
        
        Args:
            pipeline_type: Type of pipeline to retrieve
            collection_name: Name of the collection to use
            create_if_missing: Whether to create a new pipeline if none exists
            **kwargs: Additional arguments to pass to the pipeline constructor if creating
            
        Returns:
            The requested pipeline, or None if not found and create_if_missing is False
        """
        # If type and collection are provided, find matching pipelines
        if pipeline_type and collection_name:
            matching_pipelines = [
                (name, info) for name, info in self.pipeline_cache.items()
                if info["type"] == pipeline_type and info["collection"] == collection_name
            ]
            
            # If matching pipelines found, return the most recently used one
            if matching_pipelines:
                # Filter to only include non-busy pipelines
                available_pipelines = [
                    (name, info) for name, info in matching_pipelines
                    if hasattr(info["pipeline"], "busy") and info["pipeline"].busy is False
                ]
                
                # If we have available (non-busy) pipelines, return the most recently used one
                if available_pipelines:
                    most_recent = max(available_pipelines, key=lambda x: x[1]["last_used"])
                    self.pipeline_cache[most_recent[0]]["last_used"] = time.time()
                    return most_recent[1]["pipeline"]
                    
                # If all matching pipelines are busy, log and proceed to create a new one
                logger.info(f"All matching pipelines are busy, creating new pipeline for {collection_name}")
                # Fall through to create_if_missing logic below
            
            # If no matching pipelines and create_if_missing is True, create a new one
            if create_if_missing:
                return self.create_pipeline(pipeline_type, collection_name, **kwargs)
        
        return None
    
    def list_pipelines(self, 
                      pipeline_type: Optional[str] = None, 
                      collection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available pipelines, optionally filtered by type or collection.
        
        Args:
            pipeline_type: Filter by pipeline type
            collection_name: Filter by collection name
            
        Returns:
            List of dictionaries containing pipeline information
        """
        results = []
        
        for name, info in self.pipeline_cache.items():
            # Skip if pipeline_type filter is provided and doesn't match
            if pipeline_type and info["type"] != pipeline_type:
                continue
                
            # Skip if collection_name filter is provided and doesn't match
            if collection_name and info["collection"] != collection_name:
                continue
                
            # Add pipeline info to results
            results.append({
                "name": name,
                "type": info["type"],
                "collection": info["collection"],
                "created_at": info["created_at"],
                "last_used": datetime.datetime.fromtimestamp(info["last_used"]).strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return results
    
    def remove_pipeline(self, name: str) -> bool:
        """
        Remove a pipeline from the cache.
        
        Args:
            name: Name of the pipeline to remove
            
        Returns:
            True if pipeline was removed, False if it didn't exist
        """
        if name in self.pipeline_cache:
            del self.pipeline_cache[name]
            return True
        return False
    
    def clear_cache(self, 
                   pipeline_type: Optional[str] = None, 
                   collection_name: Optional[str] = None) -> int:
        """
        Clear pipelines from the cache, optionally filtered by type or collection.
        
        Args:
            pipeline_type: Filter by pipeline type
            collection_name: Filter by collection name
            
        Returns:
            Number of pipelines removed
        """
        removed_count = 0
        pipeline_names = list(self.pipeline_cache.keys())
        
        for name in pipeline_names:
            info = self.pipeline_cache[name]
            
            # Skip if pipeline_type filter is provided and doesn't match
            if pipeline_type and info["type"] != pipeline_type:
                continue
                
            # Skip if collection_name filter is provided and doesn't match
            if collection_name and info["collection"] != collection_name:
                continue
                
            # Remove pipeline from cache
            del self.pipeline_cache[name]
            removed_count += 1
        
        return removed_count
