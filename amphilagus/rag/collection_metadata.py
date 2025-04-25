"""
Collection Metadata Management Module

This module provides functionality to store and retrieve metadata about collections,
particularly the embedding model used for each collection.
"""

import os
import json
from typing import Dict, Any, Optional

from .. import config

# 使用config.py中的全局配置
METADATA_FILE = config.COLLECTION_METADATA_FILE

def save_collection_metadata(collection_name: str, embedding_model: str) -> None:
    """
    保存collection的元数据信息，特别是使用的嵌入模型
    
    Args:
        collection_name: 集合名称
        embedding_model: 使用的嵌入模型名称
    """
    # 确保元数据文件存在
    metadata = {}
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            metadata = {}
    
    # 更新当前collection的元数据
    if 'collections' not in metadata:
        metadata['collections'] = {}
    
    metadata['collections'][collection_name] = {
        'embedding_model': embedding_model,
        'created_at': import_time()
    }
    
    # 保存回文件
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"保存了集合 '{collection_name}' 的元数据，嵌入模型: {embedding_model}")

def get_collection_metadata(collection_name: str) -> Optional[Dict[str, Any]]:
    """
    获取特定collection的元数据
    
    Args:
        collection_name: 集合名称
        
    Returns:
        包含元数据的字典，如果不存在则返回None
    """
    if not os.path.exists(METADATA_FILE):
        return None
    
    try:
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        if 'collections' in metadata and collection_name in metadata['collections']:
            return metadata['collections'][collection_name]
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        pass
    
    return None

def get_embedding_model(collection_name: str) -> Optional[str]:
    """
    获取特定collection使用的嵌入模型
    
    Args:
        collection_name: 集合名称
        
    Returns:
        嵌入模型名称，如果不存在则返回None
    """
    metadata = get_collection_metadata(collection_name)
    if metadata and 'embedding_model' in metadata:
        return metadata['embedding_model']
    return None

def import_time():
    """获取当前时间作为字符串"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def list_collections() -> Dict[str, Dict[str, Any]]:
    """
    列出所有已知的collections及其元数据
    
    Returns:
        包含所有collections信息的字典
    """
    if not os.path.exists(METADATA_FILE):
        return {}
    
    try:
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        if 'collections' in metadata:
            return metadata['collections']
    except (json.JSONDecodeError, FileNotFoundError):
        pass
    
    return {}

def delete_collection_metadata(collection_name: str) -> bool:
    """
    删除特定collection的元数据
    
    Args:
        collection_name: 集合名称
        
    Returns:
        是否成功删除
    """
    if not os.path.exists(METADATA_FILE):
        return False
    
    try:
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        if 'collections' in metadata and collection_name in metadata['collections']:
            del metadata['collections'][collection_name]
            
            with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            return True
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        pass
    
    return False 