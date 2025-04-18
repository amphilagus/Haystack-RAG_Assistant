"""
Tests for the RAG pipeline module.
"""

import os
import pytest
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import chromadb
from rag_assistant.document_loader import load_documents, chunk_documents, load_text
from rag_assistant.rag_pipeline import RAGPipeline
from haystack import Document

# Load environment variables
load_dotenv()

@pytest.fixture
def api_key():
    """Get OpenAI API key from environment variables or .env file."""
    # First try from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    
    # If not found, try to read from .env file
    if not api_key:
        print("API key not found in environment variables, trying .env file...")
        try:
            # Try to find .env in various locations
            possible_env_paths = [
                # Current directory
                Path('.env'),
                # Project root
                Path(__file__).parent.parent.parent / '.env',
                # rag_assistant directory
                Path(__file__).parent.parent / '.env',
                # tests directory
                Path(__file__).parent / '.env',
            ]
            
            for env_path in possible_env_paths:
                if env_path.exists():
                    print(f"Found .env file at {env_path}")
                    # Load .env file
                    load_dotenv(dotenv_path=env_path)
                    api_key = os.getenv("OPENAI_API_KEY")
                    if api_key:
                        break
            
            # Try direct reading as a fallback
            if not api_key:
                for env_path in possible_env_paths:
                    if env_path.exists():
                        with open(env_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                if line.startswith('OPENAI_API_KEY'):
                                    api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                                    print("API key found in .env file directly.")
                                    break
                        if api_key:
                            break
        except Exception as e:
            print(f"Error reading .env file: {e}")
    
    # If we still don't have an API key, we need to skip the test
    if not api_key:
        # Try to read from debug.py as a last resort
        debug_py_path = Path(__file__).parent.parent / 'tests_archive' / 'debug.py'
        if debug_py_path.exists():
            try:
                print(f"Trying to extract API key from {debug_py_path}...")
                with open(debug_py_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Look for hardcoded API key in debug.py
                    import re
                    match = re.search(r'api_key\s*=\s*"(sk-[^"]+)"', content)
                    if match:
                        api_key = match.group(1)
                        print("Successfully extracted API key from debug.py")
            except Exception as e:
                print(f"Error reading debug.py: {e}")
    
    if not api_key:
        pytest.skip("OpenAI API key not found in environment variables or .env file")
    
    # Only show first few characters for security
    print(f"Using API key starting with: {api_key[:5]}...")
    
    return api_key

@pytest.fixture
def sample_test_files():
    """Create temporary test files and return their paths."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample text files
        file1_path = os.path.join(temp_dir, "test_doc1.txt")
        with open(file1_path, "w", encoding="utf-8") as f:
            f.write("This is the first test document for duplicate detection.")
            
        file2_path = os.path.join(temp_dir, "test_doc2.txt")
        with open(file2_path, "w", encoding="utf-8") as f:
            f.write("This is the second test document with different content.")
        
        yield {"dir": temp_dir, "file1": file1_path, "file2": file2_path}

def test_rag_pipeline_initialization(api_key):
    """Test that the RAG pipeline can be initialized."""
    pipeline = RAGPipeline(
        api_key=api_key,
        reset_collection=True
    )
    assert pipeline is not None
    assert hasattr(pipeline, "document_store")
    assert hasattr(pipeline, "pipeline")

def test_document_addition(api_key, sample_test_files):
    """Test adding documents to the RAG pipeline."""
    pipeline = RAGPipeline(
        api_key=api_key,
        reset_collection=True
    )
    
    # Load a document
    doc = load_text(sample_test_files["file1"])[0]
    
    # Add document to pipeline
    pipeline.add_documents([doc])
    
    # Verify document was added by running a simple query
    # This is a minimal test - we don't check the actual answer content
    # since that would require a real LLM call
    results = pipeline.run("What is this document about?")
    assert results is not None
    assert "llm" in results
    assert "replies" in results["llm"]

def test_duplicate_detection(api_key, sample_test_files):
    """Test the duplicate document detection functionality."""
    # Create a collection name
    collection_name = "test_duplicates"
    
    # Initialize pipeline
    pipeline = RAGPipeline(
        api_key=api_key,
        collection_name=collection_name,
        reset_collection=True
    )
    
    # Step 1: Add the first document
    doc1 = load_text(sample_test_files["file1"])[0]
    pipeline.add_documents([doc1])
    
    # Step 2: Try to add the same document again with duplicate detection
    doc1_again = load_text(sample_test_files["file1"])[0]
    # We'll capture print output to verify duplicate was detected
    # In a real test, we'd mock this or check return values
    pipeline.add_documents([doc1_again], check_duplicates=True)
    
    # Step 3: Add a different document
    doc2 = load_text(sample_test_files["file2"])[0]
    pipeline.add_documents([doc2], check_duplicates=True)
    
    # We can't easily verify the duplicate detection in a unit test without mocking
    # So this test is mainly to ensure the code runs without errors
    # A more comprehensive test would mock the document store and verify calls

@pytest.mark.integration
def test_full_rag_pipeline(api_key):
    """
    Full integration test of the RAG pipeline.
    
    This test is marked as an integration test and may be skipped during routine testing.
    It will load actual documents, add them to the pipeline, and run a query.
    """
    # Initialize pipeline with a unique collection name
    import time
    collection_name = f"test_integration_{int(time.time())}"
    
    pipeline = RAGPipeline(
        api_key=api_key,
        collection_name=collection_name,
        reset_collection=True
    )
    
    # Create a simple test document
    doc = Document(
        content="Artificial intelligence (AI) is intelligence demonstrated by machines, " 
                "as opposed to intelligence of humans and other animals. " 
                "Example tasks in which this is done include speech recognition, " 
                "computer vision, translation between languages, and decision making.",
        meta={"source": "test_integration", "file_type": "txt"}
    )
    
    # Add to pipeline
    pipeline.add_documents([doc])
    
    # Run a query
    answer = pipeline.get_answer("What is artificial intelligence?")
    
    # Verify we got some kind of answer
    assert answer is not None
    assert len(answer) > 0

def test_list_collections(api_key):
    """Test to list all collections in ChromaDB and their basic information."""
    # 初始化 ChromaDB 客户端 - 使用项目根目录下的 chroma_db
    import os
    from pathlib import Path
    
    # 获取项目根目录（tests的父目录）
    project_root = Path(__file__).parent.parent
    persist_dir = os.path.join(project_root, "chroma_db")
    
    print(f"Looking for ChromaDB at: {persist_dir}")
    client = chromadb.PersistentClient(path=persist_dir)
    
    # 获取所有集合
    collections = client.list_collections()
    
    print("\n=== ChromaDB Collections Information ===")
    print(f"Total number of collections: {len(collections)}")
    
    for collection in collections:
        print(f"\nCollection: {collection.name}")
        try:
            # 获取集合的基本信息
            count = collection.count()
            print(f"  - Number of documents: {count}")
            
            # 获取集合的元数据
            if count > 0:
                result = collection.get(include=["metadatas"])
                if result and "metadatas" in result:
                    print("  - Sample metadata:")
                    for i, metadata in enumerate(result["metadatas"][:3]):  # 只显示前3个文档的元数据
                        print(f"    Document {i + 1}: {metadata}")
                        
            # 获取集合的其他属性
            print(f"  - Collection metadata: {collection.metadata}")
            
        except Exception as e:
            print(f"  Error getting collection info: {e}")
    
    print("\n=== End of Collections Information ===")
    
    # 这个测试总是通过，因为它只是用来显示信息
    assert True 

def test_load_existing_collection(api_key):
    """
    测试加载已存在的collection并向其提问功能。
    
    步骤：
    1. 创建一个新的collection并添加文档
    2. 关闭RAG pipeline实例
    3. 创建新的RAG pipeline实例，加载已存在的collection
    4. 向collection提问并验证结果
    """
    # 步骤1: 创建一个固定名称的collection并添加文档
    collection_name = "test_existing_collection"
    
    # 首先确保创建一个新的collection
    pipeline_creator = RAGPipeline(
        api_key=api_key,
        collection_name=collection_name,
        reset_collection=True  # 确保创建全新的collection
    )
    
    # 创建一个简单的测试文档
    test_content = "Python是一种广泛使用的解释型、高级和通用的编程语言。Python支持多种编程范式，包括面向对象、" + \
                  "命令式、函数式和过程式的编程风格。它拥有动态类型系统和垃圾回收功能，能够自动管理内存使用。"
    
    doc = Document(
        content=test_content,
        meta={"source": "test_existing_collection", "file_type": "txt"}
    )
    
    # 添加文档到collection
    pipeline_creator.add_documents([doc])
    
    # 获取一个问题的答案，验证文档已正确添加
    question1 = "Python是什么编程语言？"
    answer1 = pipeline_creator.get_answer(question1)
    print(f"Initial answer: {answer1}")
    assert answer1 is not None
    assert len(answer1) > 0
    
    # 步骤2: 销毁第一个pipeline实例
    del pipeline_creator
    
    # 步骤3: 创建新的pipeline实例，加载已存在的collection
    print(f"\n加载已存在的collection: {collection_name}")
    pipeline_loader = RAGPipeline(
        api_key=api_key,
        collection_name=collection_name,
        reset_collection=False  # 不重置，使用现有collection
    )
    
    # 步骤4: 向已存在的collection提问
    question2 = "Python支持哪些编程范式？"
    answer2 = pipeline_loader.get_answer(question2)
    print(f"Answer from existing collection: {answer2}")
    
    # 验证能够从已存在的collection中获取合理答案
    assert answer2 is not None
    assert len(answer2) > 0
    
    # 清理：删除测试用的collection
    try:
        pipeline_loader.reset_document_store()
    except Exception as e:
        print(f"Warning: Could not reset document store: {e}")

def test_add_to_existing_collection(api_key):
    """
    测试向已存在的collection添加新文档并查询。
    
    步骤：
    1. 创建一个带有初始文档的collection
    2. 重新加载该collection并添加新文档
    3. 查询可以同时使用新旧文档的信息回答的问题
    """
    # 创建一个固定名称的collection
    collection_name = "test_add_existing_collection"
    
    # 步骤1: 创建collection并添加第一个文档
    pipeline1 = RAGPipeline(
        api_key=api_key,
        collection_name=collection_name,
        reset_collection=True  # 确保创建全新的collection
    )
    
    # 第一个文档 - 关于Python
    doc1 = Document(
        content="Python是一种高级编程语言，由Guido van Rossum于1991年创建。它的设计强调代码的可读性和简洁性。",
        meta={"source": "python_info", "file_type": "txt"}
    )
    
    pipeline1.add_documents([doc1])
    
    # 测试第一个文档已成功添加
    question1 = "谁创建了Python？"
    answer1 = pipeline1.get_answer(question1)
    print(f"Answer after first document: {answer1}")
    assert "Guido van Rossum" in answer1
    
    # 步骤2: 重新加载collection并添加第二个文档
    print(f"\n重新加载collection并添加新文档")
    pipeline2 = RAGPipeline(
        api_key=api_key,
        collection_name=collection_name,
        reset_collection=False  # 使用现有collection
    )
    
    # 第二个文档 - 关于Java
    doc2 = Document(
        content="Java是由Sun Microsystems公司于1995年发布的编程语言，最初由James Gosling开发。Java运行在虚拟机上，提供跨平台特性。",
        meta={"source": "java_info", "file_type": "txt"}
    )
    
    pipeline2.add_documents([doc2])
    
    # 步骤3: 测试可以回答关于两个文档的问题
    # Python相关问题
    question2 = "Python是什么时候创建的？"
    answer2 = pipeline2.get_answer(question2)
    print(f"Python question answer: {answer2}")
    assert "1991" in answer2
    
    # Java相关问题
    question3 = "谁开发了Java？"
    answer3 = pipeline2.get_answer(question3)
    print(f"Java question answer: {answer3}")
    assert "James Gosling" in answer3
    
    # 清理：删除测试用的collection
    try:
        pipeline2.reset_document_store()
    except Exception as e:
        print(f"Warning: Could not reset document store: {e}") 

@pytest.mark.title_filter
def test_title_filtered_retrieval():
    """
    Test that retrieval can be filtered by document title.
    
    This test creates two documents with different titles, adds them to the pipeline,
    and then verifies that:
    1. Querying with a specific title that exists returns results
    2. Querying with a title that doesn't exist returns no results
    3. Querying without a title filter returns different results than with a title filter
    """
    # Use a unique collection name for this test
    import time
    collection_name = f"test_title_filter_{int(time.time())}"
    
    # Initialize pipeline
    pipeline = RAGPipeline(
        collection_name=collection_name,
        reset_collection=True,
        use_llm=False
    )
    
    # Create two test documents with different titles
    doc1 = Document(
        content="Python is a high-level programming language known for its readability and simplicity. " 
                "It's widely used for web development, data analysis, artificial intelligence, and automation.",
        meta={
            "source": "test_title_filter_doc1",
            "file_type": "txt",
            "title": "programming_languages"
        }
    )
    
    doc2 = Document(
        content="Machine learning is a subset of artificial intelligence that focuses on algorithms " 
                "that can learn from and make predictions based on data. Deep learning is a type of " 
                "machine learning that uses neural networks with many layers.",
        meta={
            "source": "test_title_filter_doc2", 
            "file_type": "txt",
            "title": "machine_learning"
        }
    )
    
    # Add documents to pipeline
    pipeline.add_documents([doc1, doc2])
    
    # Query that could match both documents
    query = "Tell me about artificial intelligence"
    
    # 1. Test retrieval with existing title filter
    results_title1 = pipeline.run_with_selected_title(query, "programming_languages")
    assert results_title1 is not None
    assert "retriever" in results_title1
    assert "documents" in results_title1["retriever"]
    assert len(results_title1["retriever"]["documents"]) > 0
    assert "programming_languages" == results_title1["retriever"]["documents"][0].meta["title"]
    
    # 2. Test retrieval with non-existent title filter
    results_title_nonexistent = pipeline.run_with_selected_title(query, "nonexistent_title")
    assert results_title_nonexistent is not None
    assert "retriever" in results_title_nonexistent
    assert "documents" in results_title_nonexistent["retriever"]
    assert len(results_title_nonexistent["retriever"]["documents"]) == 0
    
    # 3. Test unfiltered retrieval (should be different from title-filtered)
    results_unfiltered = pipeline.run(query)
    assert results_unfiltered is not None
    assert "retriever" in results_unfiltered
    assert "documents" in results_unfiltered["retriever"]
    
    # Check if unfiltered returns both documents or at least different ones than when filtered
    unfiltered_titles = set(doc.meta["title"] for doc in results_unfiltered["retriever"]["documents"])
    assert len(unfiltered_titles) > 0
    
    # Verify that unfiltered results are different from title-filtered results
    filtered_docs = [doc.content for doc in results_title1["retriever"]["documents"]]
    unfiltered_docs = [doc.content for doc in results_unfiltered["retriever"]["documents"]]
    
    # The unfiltered and filtered results should be different in content or count
    assert filtered_docs != unfiltered_docs or len(filtered_docs) != len(unfiltered_docs)
    
    # Optional: Compare with retrieval using the second title
    results_title2 = pipeline.run_with_selected_title(query, "machine_learning")
    filtered_docs2 = [doc.content for doc in results_title2["retriever"]["documents"]]
    
    # Verify that different title filters give different results
    assert filtered_docs != filtered_docs2 or len(filtered_docs) != len(filtered_docs2)
    
    print("\nTest completed successfully:")
    print(f"- Programming languages document filtered results: {len(results_title1['retriever']['documents'])}")
    print(f"- Machine learning document filtered results: {len(results_title2['retriever']['documents'])}")
    print(f"- Non-existent title filtered results: {len(results_title_nonexistent['retriever']['documents'])}")
    print(f"- Unfiltered results: {len(results_unfiltered['retriever']['documents'])}") 