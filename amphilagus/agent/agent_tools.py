from typing import List, Dict, Any, Annotated, Optional
import logging
import os

from .. import manager
from .assistant import Collection_Sum_Assistant
from .. import config
from .tools import get_collection_titles

# 获取日志记录器
logger = logging.getLogger(__name__)


def batch_summarize_articles(
    collection_name: Annotated[str, "Name of the collection containing articles to summarize"],
    model: Annotated[Optional[str], "Model to use for summarization"] = "gpt-4.1-2025-04-14",
    top_k: Annotated[Optional[int], "Number of results to return for each query"] = 5,
    overwrite: Annotated[Optional[bool], "Whether to overwrite existing summary files"] = False,
) -> Dict[str, Any]:
    """
    Summarize all articles in a collection and save the summaries as markdown files.
    
    This tool will:
    1. Get all article titles in the specified collection
    2. Create a summary of each article using Collection_Sum_Assistant
    3. Save each summary as a markdown file in the SUM_FILES_PATH directory
    
    Args:
        collection_name: Name of the collection containing articles to summarize
        model: Model to use for summarization (default: gpt-4o)
        top_k: Number of results to return for each query (default: 10)
        overwrite: Whether to overwrite existing summary files (default: False)
        
    Returns:
        Dictionary containing results of the summarization process
        
    Example:
        Calling this tool with:
        {
            "collection_name": "research_papers",
            "model": "gpt-4o",
            "top_k": 10,
            "overwrite": false
        }
    """
    try:
        # Get list of article titles in the collection
        titles_result = get_collection_titles(collection_name=collection_name)
        
        if "error" in titles_result and titles_result["error"]:
            return {
                "error": f"Error retrieving titles: {titles_result['error']}",
                "collection_name": collection_name,
                "succeeded": 0,
                "failed": 0,
                "total": 0
            }
        
        titles = titles_result.get("titles", [])
        
        if not titles:
            return {
                "message": f"No articles found in collection '{collection_name}'",
                "collection_name": collection_name,
                "succeeded": 0,
                "failed": 0,
                "total": 0
            }
        
        # Create the directory for summaries if it doesn't exist
        os.makedirs(config.SUM_FILES_PATH, exist_ok=True)
        
        # Initialize counters
        succeeded = 0
        failed = 0
        skipped = 0
        errors = []
        
        # Create a summarization assistant
        summarizer = Collection_Sum_Assistant(
            model=model,
            collection_name=collection_name,
            top_k=top_k
        )
        
        # Process each article
        for title in titles:
            try:
                # Create filename
                filename = os.path.join(config.SUM_FILES_PATH, f"{title}.md")
                
                # Check if file already exists and skip if needed
                if os.path.exists(filename) and not overwrite:
                    logger.info(f"Skipping existing summary: {filename}")
                    skipped += 1
                    continue
                
                logger.info(f"Summarizing article: {title}")
                
                # Generate summary
                summary = summarizer.run(article_title=title)
                
                # Save summary to file
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(summary)
                
                succeeded += 1
                logger.info(f"Successfully summarized and saved: {filename}")
                
            except Exception as e:
                failed += 1
                error_msg = f"Error summarizing article '{title}': {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg, exc_info=True)
        
        # Prepare result
        result = {
            "collection_name": collection_name,
            "succeeded": succeeded,
            "failed": failed,
            "skipped": skipped,
            "total": len(titles),
            "summaries_dir": os.path.abspath(config.SUM_FILES_PATH)
        }
        
        if errors:
            result["errors"] = errors
        
        return result
        
    except Exception as e:
        logger.error(f"Error in batch_summarize_articles: {str(e)}", exc_info=True)
        return {
            "error": f"Error in batch summarization: {str(e)}",
            "collection_name": collection_name,
            "succeeded": 0,
            "failed": 0,
            "total": 0
        }