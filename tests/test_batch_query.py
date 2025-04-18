#!/usr/bin/env python
"""
Test for batch query functionality using title filtering
This test will:
1. Specify collection jctc_recent_0417
2. Cache all titles and randomly select one
3. Run batch queries with various parameters using run_with_selected_title
4. Output the retrieved document content to the terminal
"""

import os
import sys
import random
from typing import List, Dict, Any
import json
import datetime

# Ensure we can import from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag_assistant.rag_pipeline import RAGPipeline
from rag_assistant.logger import get_logger
from rag_assistant.title_matcher import title_matcher

logger = get_logger("test_batch_query")

def test_batch_query_with_title():
    """Test batch query with title filtering"""
    
    # Collection name to test
    collection_name = "jctc_recent_0418"
    
    # Initialize RAG pipeline
    logger.info(f"Initializing RAG pipeline for collection: {collection_name}")
    pipeline = RAGPipeline(
        collection_name=collection_name,
        use_llm=False,  # We don't need LLM for this test
        top_k=5  # Default top_k, will be overridden in queries
    )
    
    # Cache all titles
    logger.info("Caching all titles...")
    if not title_matcher.has_cached_titles(collection_name):
        # Initialize the document store to cache titles
        pipeline._cache_all_titles(collection_name)
    
    # Get all cached titles
    all_titles = title_matcher.get_cached_titles(collection_name)
    logger.info(f"Found {len(all_titles)} titles in collection")
    
    if not all_titles:
        logger.error(f"No titles found in collection {collection_name}")
        return
    
    # Randomly select one title
    selected_title = random.choice(all_titles)
    logger.info(f"Randomly selected title: {selected_title}")
    
    # Define batch queries with specified parameters
    queries = [
        {
            "query": "Background of this study",
            "mode": "run_with_selected_title",
            "title": selected_title,
            "top_k": 12
        },
        {
            "query": "Objective of this study",
            "mode": "run_with_selected_title",
            "title": selected_title,
            "top_k": 5
        },
        {
            "query": "Methods of this study",
            "mode": "run_with_selected_title",
            "title": selected_title,
            "top_k": 8
        },
        {
            "query": "Results of this study",
            "mode": "run_with_selected_title",
            "title": selected_title,
            "top_k": 20
        },
        {
            "query": "Discussion of this study",
            "mode": "run_with_selected_title",
            "title": selected_title,
            "top_k": 12
        },
        {
            "query": "Publication Timeline of this study",
            "mode": "run_with_selected_title",
            "title": selected_title,
            "top_k": 5
        },
    ]
    
    # Run batch query
    logger.info("Running batch query...")
    results = pipeline.run_batch(queries)
    
    # Create timestamp for the output file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create directory for results if it doesn't exist
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Create a sanitized title for the filename (remove characters that are invalid in filenames)
    sanitized_title = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in selected_title)
    sanitized_title = sanitized_title[:50]  # Limit the length
    
    # Create the output file path
    output_file = os.path.join(results_dir, f"batch_query_{sanitized_title}_{timestamp}.md")
    
    # Prepare the output content
    header = f"# BATCH QUERY RESULTS FOR TITLE: {selected_title}\n\n"
    header += f"**Collection:** {collection_name}\n"
    header += f"**Timestamp:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    header += "---\n\n"
    
    # Print the header to console
    print("\n" + "="*80)
    print(f"BATCH QUERY RESULTS FOR TITLE: {selected_title}")
    print("="*80)
    print(f"Results will be saved to: {output_file}")
    
    # Initialize the content for the markdown file
    md_content = header
    
    # Process and print each result
    for i, result in enumerate(results):
        query_header = f"\n## [{i+1}] {queries[i]['query']} (top_k={queries[i]['top_k']})\n\n"
        console_header = f"\n[Query {i+1}] {queries[i]['query']} (top_k={queries[i]['top_k']})"
        
        # Print to console
        print(console_header)
        print("-" * 60)
        
        # Add to markdown content
        md_content += query_header
        
        if "error" in result:
            error_msg = f"ERROR: {result['error']}"
            print(error_msg)
            md_content += f"**{error_msg}**\n\n"
            continue
        
        # Check if we have retriever results
        if "retriever" in result and "documents" in result["retriever"]:
            docs = result["retriever"]["documents"]
            docs_count_msg = f"Retrieved {len(docs)} documents"
            
            print(docs_count_msg)
            md_content += f"{docs_count_msg}\n\n"
            
            for j, doc in enumerate(docs):
                doc_header = f"\nDocument {j+1} (score: {doc.score:.4f}):"
                print(doc_header)
                print("-" * 40)
                
                # Add to markdown
                md_content += f"### Document {j+1} (score: {doc.score:.4f})\n\n"
                
                # Print content 
                content = doc.content
                print(content)
                
                # Add content to markdown with proper formatting
                md_content += f"```\n{content}\n```\n\n"
                
                # Print and add metadata
                meta_str = f"\nMetadata: {json.dumps(doc.meta, indent=2)}"
                print(meta_str)
                
                md_content += f"**Metadata:**\n\n```json\n{json.dumps(doc.meta, indent=2)}\n```\n\n"
                md_content += "---\n\n"
        else:
            no_docs_msg = "No documents retrieved or unexpected result format"
            print(no_docs_msg)
            md_content += f"*{no_docs_msg}*\n\n"
    
    # Final separator for console output
    print("\n" + "="*80)
    
    # Write to the markdown file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    logger.info(f"Results saved to: {output_file}")
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    test_batch_query_with_title() 