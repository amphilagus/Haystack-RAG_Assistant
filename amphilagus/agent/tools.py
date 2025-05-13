"""
Agent Tools Module

This module provides tools that can be used by the Haystack agent to interact with embedding pipelines.
"""

from typing import List, Dict, Any, Annotated, Optional
import logging
import os
import pathlib

from .. import manager

# 获取日志记录器
logger = logging.getLogger(__name__)


def run_embedding_search(
    collection_name: Annotated[str, "Name of the collection to search in"],
    queries: Annotated[List[Dict[str, Any]], "List of query configurations, each containing at least a 'query' field with the search text"],
    top_k: Annotated[Optional[int], "Number of results to return for each query"] = 5,
    mode: Annotated[Optional[str], "Mode of the query"] = "run",
) -> Dict[str, Any]:
    """
    Run a batch of embedding searches against a specific collection.
    
    This tool uses the EmbeddingOnlyPipeline to perform semantic searches against documents 
    in the specified collection. It's useful for finding relevant documents without 
    generating answers using an LLM.
    
    Each query in the batch can specify different parameters.
    
    Args:
        collection_name: Name of the collection to search in
        queries: List of query configurations, each must have at least a 'query' field
        top_k: Default number of results to return for each query
        mode: Mode of the query
    Returns:
        Dictionary containing search results for each query
    
    Example:
        Calling this tool with:
        {
            "collection_name": "research_papers",
            "queries": [
                {"query": "quantum computing applications", "top_k": 3},
                {"query": "neural networks in medicine"}
            ]
        }
    """
    # Format queries if they're simple strings
    formatted_queries = []
    for query in queries:
        if isinstance(query, str):
            # If query is just a string, convert to proper format
            formatted_queries.append({"query": query, "mode": mode, "top_k": top_k})
        elif isinstance(query, dict):
            # If query is already a dict, ensure it has the required fields
            if "query" not in query:
                raise ValueError(f"Query missing 'query' field: {query}")
            
            # Set default values if missing
            query_config = {
                "query": query["query"],
                "mode": query.get("mode", mode),
                "top_k": query.get("top_k", top_k),
                "only_most_related_articles": query.get("only_most_related_articles", False)
            }
            title = query.get("title", False)
            if title:
                query_config["title"] = title

            formatted_queries.append(query_config)
        else:
            raise ValueError(f"Invalid query format: {query}")
    
    # Get the embedding pipeline for the specified collection
    pipeline = manager.pipeline.get_pipeline(
        pipeline_type="embedding",
        collection_name=collection_name,
        create_if_missing=True
    )
    
    if not pipeline:
        return {
            "error": f"Failed to initialize embedding pipeline for collection '{collection_name}'",
            "results": []
        }
    
    try:
        # Run the batch queries
        results = pipeline.run_batch(formatted_queries)
        # 解除 pipeline 的busy状态
        pipeline.busy = False
        return {
            "collection_name": collection_name,
            "results": results,
            "query_count": len(results)
        }
    except Exception as e:
        pipeline.busy = False
        return {
            "error": f"Error running batch queries: {str(e)}",
            "collection_name": collection_name,
            "results": []
        }

def get_collection_titles(
    collection_name: Annotated[str, "Name of the collection to retrieve titles from"],
) -> Dict[str, Any]:
    """
    Retrieve a list of all unique document titles from a specified collection.
    
    This tool fetches all unique titles from documents stored in the specified collection.
    It's useful for getting an overview of available documents or for filtering searches by title.
    
    Args:
        collection_name: Name of the collection to retrieve titles from
    
    Returns:
        Dictionary containing the collection name, list of unique titles, and title count
    
    Example:
        Calling this tool with:
        {
            "collection_name": "research_papers"
        }
        
        Returns:
        {
            "collection_name": "research_papers",
            "titles": ["Quantum Computing Basics", "Neural Networks in Medicine", ...],
            "title_count": 25
        }
    """
    try:
        # Get the pipeline for the specified collection
        pipeline = manager.pipeline.get_pipeline(
            pipeline_type="embedding",
            collection_name=collection_name,
            create_if_missing=True
        )
        
        if not pipeline:
            return {
                "error": f"Collection '{collection_name}' not found or could not be accessed",
                "collection_name": collection_name,
                "titles": [],
                "title_count": 0
            }
        
        # Retrieve titles using the pipeline's _cache_all_titles method
        try:
            # Call the pipeline's method to get and cache all titles
            unique_titles = pipeline._cache_all_titles(collection_name)
            titles = list(unique_titles)
            
            # Release pipeline
            pipeline.busy = False
            
            return {
                "collection_name": collection_name,
                "titles": titles,
                "title_count": len(titles)
            }
            
        except Exception as e:
            pipeline.busy = False
            logger.error(f"Error retrieving titles: {str(e)}", exc_info=True)
            return {
                "error": f"Error retrieving titles: {str(e)}",
                "collection_name": collection_name,
                "titles": [],
                "title_count": 0
            }
    
    except Exception as e:
        logger.error(f"Error accessing collection: {str(e)}", exc_info=True)
        return {
            "error": f"Error accessing collection: {str(e)}",
            "collection_name": collection_name,
            "titles": [],
            "title_count": 0
        }

def format_with_references(
    sections: Annotated[List[Dict[str, Any]], "List of section objects, each containing text and reference information"],
    top_k: Annotated[Optional[int], "Maximum number of references to include per section"] = 3,
) -> Dict[str, Any]:
    """
    Format sections of text with their corresponding references.
    
    This tool takes sections of text that have been processed by the search_collection_with_refs
    tool and formats them into a coherent document with proper scientific references.
    
    Args:
        sections: List of section objects, each containing text and reference information
        top_k: Maximum number of references to include per section
    
    Returns:
        Dictionary containing the main_text (with citations) and references_list separately
    
    Example structure for sections:
    [
        {
            "text": "Memristors have revolutionized neuromorphic computing.",
            "references": [
                {"title": "The Future of Memristors", "score": 0.92},
                {"title": "Neuromorphic Computing with Memristors", "score": 0.85}
            ]
        },
        {
            "text": "2D materials show promise for memory applications.",
            "references": [
                {"title": "2D Materials in Memory Devices", "score": 0.91}
            ]
        }
    ]
    """
    logger.debug(f"Beginning format_with_references, received {len(sections)} sections with top_k={top_k}")
    
    try:
        # 1. Validate input
        if not sections:
            logger.debug("No sections provided, returning empty result")
            return {
                "main_text": "",
                "references_list": [],
                "error": "No sections provided"
            }
            
        # 2. Initialize reference tracking
        all_references = {}  # Dictionary to track all unique references
        ref_counter = 1      # Counter for reference numbering
        
        # 3. Process each section and collect references
        processed_sections = []
        for i, section in enumerate(sections):
            if "text" not in section:
                logger.debug(f"Section {i} missing 'text' field, skipping")
                continue
                
            section_text = section["text"]
            section_refs = section.get("references", [])
            logger.debug(f"Processing section {i}: '{section_text[:50]}...' with {len(section_refs)} references")
            
            # Limit references to top_k
            if len(section_refs) > top_k:
                logger.debug(f"Limiting section {i} references from {len(section_refs)} to top-{top_k}")
                section_refs = section_refs[:top_k]
                
            # Track section references
            section_citations = []
            for ref in section_refs:
                ref_title = ref.get("title", "Unknown")
                ref_score = ref.get("score", 0)
                
                # Add to global references if new
                if ref_title not in all_references:
                    all_references[ref_title] = {
                        "number": ref_counter,
                        "score": ref_score
                    }
                    logger.debug(f"Added new reference #{ref_counter}: '{ref_title}' (score: {ref_score:.2f})")
                    ref_counter += 1
                
                # Add citation to this section
                section_citations.append(all_references[ref_title]["number"])
            
            # Add processed section
            processed_sections.append({
                "text": section_text,
                "citations": section_citations
            })
            logger.debug(f"Section {i} processed with citations: {section_citations}")
        
        # 4. Format the main text with citations
        main_text = ""
        for i, section in enumerate(processed_sections):
            # Add section text
            text = section["text"]
            citations = section["citations"]
            
            # Format citations if any exist
            if citations:
                citation_str = ", ".join([f"[{num}]" for num in citations])
                if not text.endswith("."):
                    text += "."
                text += f" {citation_str}"
                logger.debug(f"Added citations {citation_str} to section {i}")
            
            main_text += text + " "
        
        # 5. Prepare the references list separately
        references_list = []
        if all_references:
            # Sort references by their assigned number
            sorted_refs = sorted(all_references.items(), key=lambda x: x[1]["number"])
            for title, ref_info in sorted_refs:
                references_list.append(title)
                logger.debug(f"Added reference to list: #{ref_info['number']} - {title}")
        
        logger.debug(f"Completed formatting with {len(references_list)} total references")
        logger.debug(f"Main text (first 100 chars): {main_text[:100]}...")
        
        return {
            "main_text": main_text.strip(),
            "references_list": references_list,
        }
        
    except Exception as e:
        logger.error(f"Error in format_with_references: {str(e)}", exc_info=True)
        return {
            "error": f"Error formatting references: {str(e)}",
            "main_text": "",
            "references_list": []
        }


