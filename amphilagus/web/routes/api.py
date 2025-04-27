"""
API相关路由模块
"""
from flask import Blueprint, jsonify

from ... import manager

# 创建Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/files', methods=['GET'])
def api_list_files():
    """API endpoint to list files."""
    files = manager.file.list_files()
    return jsonify([file.to_dict() for file in files])

@api_bp.route('/tags', methods=['GET'])
def api_list_tags():
    """API endpoint to list tags."""
    tags = manager.file.list_tags()
    return jsonify([{"name": tag.name, "parent": tag.parent.name if tag.parent else None} for tag in tags])

@api_bp.route('/collections', methods=['GET'])
def api_list_collections():
    """API endpoint to list vector database collections."""
    try:
        collections_info = manager.database.list_collections()
        collections = []
        
        for collection_info in collections_info:
            if collection_info["exists_in_chroma"]:
                collections.append({
                    'name': collection_info["name"],
                    'document_count': collection_info["doc_count"],
                    'embedding_model': collection_info.get("embedding_model", "Unknown")
                })
                
        return jsonify(collections)
    except Exception as e:
        from ...logger import get_logger
        logger = get_logger('web_app')
        logger.error(f"API获取集合列表时出错: {str(e)}")
        return jsonify({"error": str(e)}), 500 