"""
Tests for the document_loader module.
"""

import os
import pytest
from rag_assistant.document_loader import load_documents, chunk_documents
from haystack import Document

@pytest.fixture
def sample_document():
    """Create a sample document for testing."""
    return Document(
        content="This is a test document. It contains multiple sentences. "
                "Each sentence should be processed correctly. "
                "The document chunker should split this into smaller pieces "
                "based on the provided chunk size and overlap.",
        meta={"source": "test", "file_type": "txt"}
    )

@pytest.fixture
def sample_documents():
    """Create a list of sample documents for testing."""
    return [
        Document(
            content="Document 1 with some content.",
            meta={"source": "test1", "file_type": "txt"}
        ),
        Document(
            content="Document 2 with some other content that is longer than document 1.",
            meta={"source": "test2", "file_type": "txt"}
        ),
        Document(
            content="Document 3 is the longest document in this collection with multiple sentences. "
                    "It should be processed differently than the shorter documents when chunking.",
            meta={"source": "test3", "file_type": "txt"}
        ),
    ]

def test_chunk_documents_small_chunk(sample_document):
    """Test chunking with a small chunk size."""
    # Use a small chunk size to ensure multiple chunks are created
    chunked_docs = chunk_documents([sample_document], chunk_size=50, chunk_overlap=10)
    
    # Check that we have more than one chunk
    assert len(chunked_docs) > 1
    
    # Check that each chunk is not larger than the chunk size
    for doc in chunked_docs:
        assert len(doc.content) <= 50
        
    # Check that metadata is preserved
    for doc in chunked_docs:
        assert "source" in doc.meta
        assert doc.meta["source"] == "test"
        assert "file_type" in doc.meta
        assert doc.meta["file_type"] == "txt"
        assert "chunk_id" in doc.meta

def test_chunk_documents_large_chunk(sample_document):
    """Test chunking with a chunk size larger than the document."""
    # Use a large chunk size to ensure the document stays as one chunk
    chunked_docs = chunk_documents([sample_document], chunk_size=1000, chunk_overlap=10)
    
    # Check that we have only one chunk
    assert len(chunked_docs) == 1
    
    # Check that content is preserved
    assert chunked_docs[0].content == sample_document.content
        
    # Check that metadata is preserved
    assert chunked_docs[0].meta["source"] == sample_document.meta["source"]
    assert chunked_docs[0].meta["file_type"] == sample_document.meta["file_type"]

def test_chunk_documents_multiple(sample_documents):
    """Test chunking with multiple documents."""
    # Chunk the documents
    chunked_docs = chunk_documents(sample_documents, chunk_size=50, chunk_overlap=10)
    
    # There should be multiple chunks
    assert len(chunked_docs) > len(sample_documents)
    
    # Each chunk should have metadata
    for doc in chunked_docs:
        assert "source" in doc.meta
        assert "file_type" in doc.meta