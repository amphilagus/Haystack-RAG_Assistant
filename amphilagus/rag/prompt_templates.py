"""
Prompt Templates Module

This module defines various pre-set prompt templates for the RAG pipeline.
Each template has a different focus and style for different use cases.
"""

from haystack.dataclasses import ChatMessage

# 精准模式 - 严格遵循文档内容，注重准确性
PRECISE_TEMPLATE = [
    ChatMessage.from_user(
        """
Answer the question based ONLY on the given context. If the answer cannot be derived from the context, 
say "I don't have enough information to answer this question". Provide a direct, concise answer 
without adding any speculative information beyond what is explicitly stated in the context.

Context:
{% for document in documents %}
{{ document.content }}
{% endfor %}

Question: {{question}}
Answer:
"""
    )
]

# 平衡模式 - 平衡准确性和流畅性
BALANCED_TEMPLATE = [
    ChatMessage.from_user(
        """
Answer the question based on the given context. If the answer cannot be precisely derived from the context, 
try to give a not that accurate but at least not wrong answer, otherwise say "Sorry, I don't know either =-=".

Context:
{% for document in documents %}
{{ document.content }}
{% endfor %}

Question: {{question}}
Answer:
"""
    )
]

# 创意模式 - 在保持准确的同时，允许更具解释性和创造性的回答
CREATIVE_TEMPLATE = [
    ChatMessage.from_user(
        """
Answer the question based on the given context. You may elaborate and provide additional explanations 
to make your answer more helpful, but ensure the core information is derived from the context.
If the question cannot be answered from the context, acknowledge this limitation but you may offer 
related insights or suggestions based on the available information.

Context:
{% for document in documents %}
{{ document.content }}
{% endfor %}

Question: {{question}}
Answer:
"""
    )
]

# 模板字典，便于通过名称引用
TEMPLATES = {
    "precise": {
        "name": "Precise",
        "description": "严格遵循文档内容，提供简洁准确的回答",
        "template": PRECISE_TEMPLATE
    },
    "balanced": {
        "name": "Balanced",
        "description": "平衡准确性和流畅性，默认模式",
        "template": BALANCED_TEMPLATE
    },
    "creative": {
        "name": "Creative",
        "description": "在保持准确的同时提供更详细的解释和见解",
        "template": CREATIVE_TEMPLATE
    }
}

def get_template(template_name: str = "balanced"):
    """
    Get prompt template by name
    
    Args:
        template_name: Name of the template (precise, balanced, creative)
        
    Returns:
        Template object with messages
    """
    template_name = template_name.lower()
    if template_name not in TEMPLATES:
        template_name = "balanced"  # 默认使用平衡模式
    
    return TEMPLATES[template_name]["template"]

def get_all_templates():
    """
    Get all available templates
    
    Returns:
        Dictionary of templates
    """
    return TEMPLATES 