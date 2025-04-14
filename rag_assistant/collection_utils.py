"""
Collection Utilities Module

Provides command-line utilities for working with collection metadata.
"""

import os
import sys
import json
import argparse
from typing import Optional

# 确保可以导入其他模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from collection_metadata import get_embedding_model, get_collection_metadata
except ImportError:
    # 尝试添加父目录到路径
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    try:
        from rag_assistant.collection_metadata import get_embedding_model, get_collection_metadata
    except ImportError:
        # 最后尝试直接导入
        try:
            sys.path.insert(0, os.path.join(parent_dir, "rag_assistant"))
            from collection_metadata import get_embedding_model, get_collection_metadata
        except ImportError:
            print("ERROR: Cannot import collection_metadata module.")
            sys.exit(1)

def check_collection_exists(collection_name: str) -> bool:
    """
    检查集合是否存在
    
    Args:
        collection_name: 集合名称
        
    Returns:
        bool: 集合是否存在
    """
    try:
        metadata = get_collection_metadata(collection_name)
        return metadata is not None
    except Exception as e:
        print(f"Error checking collection: {e}")
        return False

def get_collection_embedding_model(collection_name: str) -> Optional[str]:
    """
    获取集合使用的嵌入模型
    
    Args:
        collection_name: 集合名称
        
    Returns:
        Optional[str]: 嵌入模型名称，如果不存在则返回None
    """
    try:
        model = get_embedding_model(collection_name)
        return model
    except Exception as e:
        print(f"Error getting embedding model: {e}")
        return None

def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description="Collection Metadata Utilities")
    parser.add_argument("--check-exists", type=str, help="Check if a collection exists")
    parser.add_argument("--get-embedding-model", type=str, help="Get the embedding model used by a collection")
    
    args = parser.parse_args()
    
    if args.check_exists:
        exists = check_collection_exists(args.check_exists)
        print("True" if exists else "False")
    
    if args.get_embedding_model:
        model = get_collection_embedding_model(args.get_embedding_model)
        print(model or "")

if __name__ == "__main__":
    main() 