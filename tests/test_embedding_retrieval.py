"""
测试嵌入检索功能

这个测试模块用于验证从特定集合（如刘慈欣小说）中检索文档的功能，
并测试不同top_k值的效果。
"""

import os
import sys
import pytest
from typing import List, Dict, Any
from pathlib import Path

# 确保能正确导入RAGPipeline
sys.path.insert(0, str(Path(__file__).parent.parent))
from rag_assistant.rag_pipeline import RAGPipeline

# 测试查询和预期结果
LIUCIXIN_QUERIES = [
    "三体中的黑暗森林法则是什么？",
    "刘慈欣如何描述未来的地球文明？",
    "死神永生中的智子有什么作用？",
    "童话中的黄金时代指的是什么？",
    "三体人与地球人的交流方式是什么？"
]

# 测试的top_k值
TOP_K_VALUES = [1, 3, 5, 10, 20]

@pytest.fixture(scope="module")
def rag_pipeline():
    """创建RAG管道实例作为测试夹具"""
    # 尝试从环境变量获取API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        from dotenv import load_dotenv
        load_dotenv(override=True)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("未找到OpenAI API密钥，跳过测试")
    
    # 初始化管道
    collection_name = "liucixin"
    persist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chroma_db"))
    
    try:
        pipeline = RAGPipeline(
            collection_name=collection_name,
            api_key=api_key,
            persist_dir=persist_dir,
            embedding_model="BAAI/bge-small-zh-v1.5",
            top_k=1  # 初始top_k设置为1，后面会根据测试需要更改
        )
        return pipeline
    except Exception as e:
        pytest.skip(f"初始化RAG管道失败: {e}")

@pytest.mark.parametrize("top_k", TOP_K_VALUES)
def test_top_k_retrieval(rag_pipeline, top_k):
    """测试不同top_k值的文档检索效果"""
    # 创建具有新top_k值的pipeline，不使用LLM以加快测试速度
    rag_pipeline.create_new_pipeline(top_k=top_k, use_llm=False)
    
    # 选择第一个查询进行测试
    query = LIUCIXIN_QUERIES[0]
    
    # 执行检索
    results = rag_pipeline.run(query)
    
    # 验证结果
    assert "retriever" in results, "结果中应包含retriever键"
    assert "documents" in results["retriever"], "检索结果中应包含documents键"
    
    documents = results["retriever"]["documents"]
    assert len(documents) <= top_k, f"检索到的文档数量({len(documents)})不应超过top_k({top_k})"
    assert len(documents) > 0, "至少应检索到一个文档"
    
    # 验证文档内容
    for doc in documents:
        assert hasattr(doc, "content"), "文档应包含content属性"
        assert len(doc.content) > 0, "文档内容不应为空"
        assert hasattr(doc, "meta"), "文档应包含meta属性"

@pytest.mark.parametrize("query", LIUCIXIN_QUERIES)
def test_query_relevance(rag_pipeline, query):
    """测试不同查询的相关性"""
    # 使用固定的top_k值(3)进行测试，不使用LLM以加快测试速度
    rag_pipeline.create_new_pipeline(top_k=3, use_llm=False)
    
    # 执行检索
    results = rag_pipeline.run(query)
    
    # 验证结果
    assert "retriever" in results, "结果中应包含retriever键"
    assert "documents" in results["retriever"], "检索结果中应包含documents键"
    
    documents = results["retriever"]["documents"]
    assert len(documents) > 0, "至少应检索到一个文档"
    
    # 此测试主要是验证检索功能正常工作，并不验证语义相关性
    # 因为语义相关性验证需要人工判断或更复杂的评估指标
    print(f"\n查询: {query}")
    print(f"检索到 {len(documents)} 个文档")
    for i, doc in enumerate(documents):
        content_preview = doc.content[:500] + "..." if len(doc.content) > 500 else doc.content
        print(f"\n文档 {i+1}: {content_preview}")

@pytest.mark.skipif(not os.environ.get("RUN_SLOW_TESTS"), reason="慢速测试，只有在RUN_SLOW_TESTS环境变量设置时才运行")
@pytest.mark.parametrize("query", LIUCIXIN_QUERIES)
@pytest.mark.parametrize("top_k", TOP_K_VALUES)
def test_comprehensive_retrieval(rag_pipeline, query, top_k):
    """综合测试不同查询和不同top_k值的组合（慢速测试）"""

    # 创建具有新top_k值的pipeline，不使用LLM以加快测试速度
    rag_pipeline.create_new_pipeline(top_k=top_k, use_llm=False)
    
    # 执行检索
    results = rag_pipeline.run(query)
    
    # 验证结果
    assert "retriever" in results, "结果中应包含retriever键"
    assert "documents" in results["retriever"], "检索结果中应包含documents键"
    
    documents = results["retriever"]["documents"]
    assert len(documents) <= top_k, f"检索到的文档数量({len(documents)})不应超过top_k({top_k})"
    assert len(documents) > 0, "至少应检索到一个文档"
    
    print(f"\n查询: {query}, top_k: {top_k}")
    print(f"检索到 {len(documents)} 个文档")

def test_set_top_k(rag_pipeline):
    """测试直接设置top_k参数的功能"""
    # 选择一个查询用于测试
    query = LIUCIXIN_QUERIES[0]
    
    # 初始化一个较小的top_k
    initial_top_k = 2
    rag_pipeline.create_new_pipeline(top_k=initial_top_k, use_llm=False)
    
    # 执行初始检索并验证结果
    initial_results = rag_pipeline.run(query)
    initial_documents = initial_results["retriever"]["documents"]
    assert len(initial_documents) <= initial_top_k, f"检索到的文档数量({len(initial_documents)})不应超过top_k({initial_top_k})"
    
    # 直接设置一个较大的top_k
    new_top_k = 5
    rag_pipeline.set_top_k(new_top_k)
    
    # 不重新创建管道，直接执行检索
    new_results = rag_pipeline.run(query)
    new_documents = new_results["retriever"]["documents"]
    
    # 验证结果数量符合新的top_k
    assert len(new_documents) <= new_top_k, f"检索到的文档数量({len(new_documents)})不应超过新的top_k({new_top_k})"
    assert len(new_documents) > initial_top_k, f"检索到的文档数量({len(new_documents)})应该超过初始top_k({initial_top_k})"
    
    # 确认默认设置也已更新
    assert rag_pipeline.default_settings["top_k"] == new_top_k, "默认设置中的top_k应该已更新"
    
    # 测试设置无效的top_k值
    with pytest.raises(ValueError):
        rag_pipeline.set_top_k(-1)
    
    with pytest.raises(ValueError):
        rag_pipeline.set_top_k(0)
    
    with pytest.raises(ValueError):
        rag_pipeline.set_top_k("invalid") 