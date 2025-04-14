# RAG Assistant Tests

This directory contains tests for the RAG Assistant.

## Test Structure

- `test_document_loader.py` - Tests for the document loader module
- `test_rag_pipeline.py` - Tests for the RAG pipeline module
- `run_tests.py` - Script to run tests
- `cleanup.py` - Script to clean up test files and directories

## Running Tests

You can run tests using VS Code's Run and Debug feature, or from the command line.

### Using VS Code

1. Open the Run and Debug panel (Ctrl+Shift+D)
2. Select a test configuration:
   - `Test - Document Loader` - Run document loader tests
   - `Test - RAG Pipeline` - Run RAG pipeline tests 
   - `Test - Duplicate Detection` - Run duplicate detection tests
   - `Test - Integration Tests` - Run integration tests
   - `Test - All Tests` - Run all tests
3. Click the Run button or press F5

### Using Command Line

Run tests using the `run_tests.py` script:

```bash
# Run document loader tests
python rag_assistant/tests/run_tests.py document_loader

# Run RAG pipeline tests
python rag_assistant/tests/run_tests.py rag_pipeline

# Run duplicate detection tests
python rag_assistant/tests/run_tests.py duplicate

# Run integration tests
python rag_assistant/tests/run_tests.py integration

# Run all tests
python rag_assistant/tests/run_tests.py all
```

## Cleaning Up

After running tests, you can clean up test files and directories using the `cleanup.py` script:

```bash
python rag_assistant/tests/cleanup.py
```

This will remove any temporary files and directories created during testing. 