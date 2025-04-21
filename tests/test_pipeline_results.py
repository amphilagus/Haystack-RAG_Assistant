import os
import sys
import json
from typing import Dict, Any
from pprint import pprint

# Add the parent directory to the path to import rag_assistant modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from rag_assistant.rag_pipeline import RAGPipeline

def pretty_print_nested_dict(data, indent=0):
    """Recursively pretty print a nested dictionary structure with types."""
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{' ' * indent}{key} (dict):")
            pretty_print_nested_dict(value, indent + 4)
        elif isinstance(value, list):
            print(f"{' ' * indent}{key} (list, length={len(value)}):")
            if value and isinstance(value[0], dict):
                pretty_print_nested_dict(value[0], indent + 4)
            elif value:
                print(f"{' ' * (indent + 4)}First item type: {type(value[0]).__name__}")
                if hasattr(value[0], "__dict__"):
                    print(f"{' ' * (indent + 4)}First item attributes:")
                    for attr, attr_value in value[0].__dict__.items():
                        print(f"{' ' * (indent + 8)}{attr}: {type(attr_value).__name__}")
        else:
            print(f"{' ' * indent}{key} ({type(value).__name__}): {value}")

def test_pipeline_run_results():
    """
    Test function to examine the structure of results returned by the RAGPipeline.run method.
    """
    print("\n=== Testing RAGPipeline.run Results Structure ===\n")
    
    # Create a RAGPipeline instance with minimal configuration
    # Using a small test collection to ensure quick execution
    pipeline = RAGPipeline(
        collection_name="test_results_collection",
        reset_collection=True,
        llm_model="gpt-4o-mini"  # Use a smaller model for testing
    )
    
    # Add a simple test document to ensure the pipeline has something to retrieve
    from haystack import Document
    test_doc = Document(
        content="This is a test document about artificial intelligence. AI is transforming many industries.",
        meta={"title": "AI Test Document", "source": "test"}
    )
    pipeline.add_documents([test_doc])
    
    # Run a simple query
    query = "What is artificial intelligence?"
    print(f"Running query: '{query}'\n")
    
    # Get the results
    results = pipeline.run(query)
    
    # Print the top-level keys in the results
    print("Top-level keys in results:")
    for key in results.keys():
        print(f"- {key}")
    print()
    
    # Detailed examination of the structure
    print("Detailed structure of results:\n")
    pretty_print_nested_dict(results)
    print("--------------------------------")
    print("--------------------------------")
    print(results)
    # Check for expected keys based on the pipeline structure
    assert "retriever" in results, "Expected 'retriever' in results"
    assert "documents" in results["retriever"], "Expected 'documents' in retriever results"
    
    # If using LLM, check for LLM results
    if "llm" in results:
        assert "responses" in results["llm"] or "replies" in results["llm"], \
            "Expected 'responses' or 'replies' in LLM results"
    
    print("\n=== Test completed successfully ===")
    
    return results

def test_get_answer_with_references():
    """
    Test the get_answer method, particularly the include_references parameter.
    """
    print("\n=== Testing get_answer with References ===\n")
    
    # Create a RAGPipeline instance with minimal configuration
    pipeline = RAGPipeline(
        collection_name="test_references_collection",
        reset_collection=True,
        llm_model="gpt-4o-mini"  # Use a smaller model for testing
    )
    
    # Add multiple test documents with different titles to test references sorting
    from haystack import Document
    
    docs = [
        Document(
            content="AI is a branch of computer science focused on creating intelligent machines.",
            meta={"title": "AI Definition", "source": "test1"}
        ),
        Document(
            content="Machine learning is a subset of AI that focuses on algorithms that can learn from data.",
            meta={"title": "Machine Learning", "source": "test2"}
        ),
        Document(
            content="Deep learning is a subset of machine learning based on neural networks.",
            meta={"title": "Deep Learning", "source": "test3"}
        ),
        Document(
            content="Natural Language Processing allows computers to understand human language.",
            meta={"title": "NLP", "source": "test4"}
        )
    ]
    
    pipeline.add_documents(docs)
    
    # Run a query
    query = "What is artificial intelligence and its subfields?"
    print(f"Running query: '{query}'\n")
    
    # First, get answer without references
    print("Testing get_answer without references:")
    answer = pipeline.get_answer(query, top_k=3)
    print(f"Answer type: {type(answer).__name__}")
    print(f"Answer: {answer[:100]}...\n")
    
    # Then, get answer with references
    print("Testing get_answer with references:")
    result_with_refs = pipeline.get_answer(query, top_k=3, include_references=True)
    print(f"Result type: {type(result_with_refs).__name__}")
    
    # Print the results with references
    if isinstance(result_with_refs, dict):
        print("Answer:", result_with_refs.get("answer", "")[:100], "...")
        print("References:", result_with_refs.get("references", []))
    else:
        print("Unexpected result type. Expected dict, got:", type(result_with_refs).__name__)
    
    print("\n=== Test completed successfully ===")
    
    return result_with_refs

if __name__ == "__main__":
    # Run the test functions
    print("Running test_pipeline_run_results...")
    test_results = test_pipeline_run_results()
    
    print("\nRunning test_get_answer_with_references...")
    references_results = test_get_answer_with_references()
    
    # Optional: Save results to a JSON file for later inspection
    try:
        # Convert complex objects to serializable format
        import json
        from haystack.utils import serialize_documents_to_dict
        
        serializable_results = {}
        for key, value in test_results.items():
            if key == "retriever" and "documents" in value:
                # Convert Document objects to dictionaries
                serializable_results[key] = {
                    "documents": serialize_documents_to_dict(value["documents"])
                }
            elif key == "llm" and "responses" in value:
                # Extract content from ChatMessage objects
                serializable_results[key] = {
                    "responses": [
                        {"content": msg.content, "type": msg.type} 
                        for msg in value["responses"]
                    ]
                }
            else:
                # Try to add the key/value as is
                try:
                    json.dumps({key: value})  # Test if serializable
                    serializable_results[key] = value
                except (TypeError, OverflowError):
                    serializable_results[key] = str(value)
        
        with open("pipeline_results.json", "w") as f:
            json.dump(serializable_results, f, indent=2)
        print("Results saved to pipeline_results.json")
        
        # Save reference results separately
        with open("reference_results.json", "w") as f:
            if isinstance(references_results, dict):
                json.dump(references_results, f, indent=2)
            else:
                json.dump({"answer": str(references_results)}, f, indent=2)
        print("Reference results saved to reference_results.json")
        
    except Exception as e:
        print(f"Could not save results to JSON: {e}") 