#!/usr/bin/env python
"""
Test runner script for RAG Assistant tests.

This script runs the tests for the RAG Assistant project.
It can be used to run specific test groups or all tests.
"""

import os
import sys
import pytest
from pathlib import Path

def main():
    """Run the tests based on command line arguments."""
    # Get the directory of this script
    script_dir = Path(__file__).parent
    
    # Add the project root to sys.path if needed
    project_root = script_dir.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Default to running all tests with verbose output and showing prints
    args = ["-v", "-s"]
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "document_loader":
            args.append(str(script_dir / "test_document_loader.py"))
        elif test_type == "rag_pipeline":
            args.append(str(script_dir / "test_rag_pipeline.py"))
        elif test_type == "duplicate":
            args.append(str(script_dir / "test_rag_pipeline.py::test_duplicate_detection"))
        elif test_type == "integration":
            args.extend(["-m", "integration"])
        elif test_type == "list_collections":
            args.append(str(script_dir / "test_rag_pipeline.py::test_list_collections"))
        elif test_type == "existing_collections":
            args.append(str(script_dir / "test_rag_pipeline.py::test_load_existing_collection"))
            args.append(str(script_dir / "test_rag_pipeline.py::test_add_to_existing_collection"))
        elif test_type == "embedding_retrieval":
            args.append(str(script_dir / "test_embedding_retrieval.py"))
        elif test_type == "all":
            # Run all tests
            pass
        else:
            print(f"Unknown test type: {test_type}")
            print("Available test types: document_loader, rag_pipeline, duplicate, integration, list_collections, existing_collections, embedding_retrieval, all")
            return 1
        
        # Add any additional pytest arguments passed from command line
        if len(sys.argv) > 2:
            args.extend(sys.argv[2:])
    
    # Run the tests
    return pytest.main(args)

if __name__ == "__main__":
    sys.exit(main()) 