"""
Title Matcher Module

提供标题匹配、缓存和规范化功能，支持精确匹配和模糊匹配。
"""

import difflib
import unicodedata
import time
import json
import os
from typing import List, Dict, Any, Optional, Set, Tuple, Union

import pandas as pd

# 替换原来的logging导入和logger初始化
from rag.logger import get_logger
logger = get_logger("title_matcher")

class TitleMatcher:
    """标题匹配器，提供精确和模糊标题匹配功能，并支持标题缓存"""
    
    def __init__(self):
        """初始化标题匹配器"""
        # 标题缓存: {集合名称: {标题集合}}
        self._collections_titles_cache = {}
        # 缓存过期时间（秒）
        self.cache_ttl = 3600  # 1小时
        # 缓存过期时间戳: {集合名称: 过期时间戳}
        self._cache_expire_time = {}
        # 上次使用时间: {集合名称: 上次使用时间戳}
        self._last_used = {}
        # 最大缓存集合数量
        self.max_collections = 20
        logger.debug("标题匹配器已初始化")
    
    def add_titles_to_cache(self, collection_name: str, titles: List[str]) -> None:
        """
        将标题添加到缓存
        
        Args:
            collection_name: 集合名称
            titles: 标题列表
        """
        # 转换为集合以确保唯一性
        self._collections_titles_cache[collection_name] = set(titles)
        # 设置过期时间
        current_time = time.time()
        self._cache_expire_time[collection_name] = current_time + self.cache_ttl
        self._last_used[collection_name] = current_time
        logger.debug(f"集合 '{collection_name}' 的 {len(titles)} 个标题已添加到缓存")
        
        # 如果缓存集合数量超过最大值，删除最旧的
        self._cleanup_cache()
    
    def _cleanup_cache(self) -> None:
        """清理过期和最旧的缓存"""
        current_time = time.time()
        
        # 删除过期的缓存
        expired_collections = [
            name for name, expire_time in self._cache_expire_time.items()
            if current_time > expire_time
        ]
        
        for name in expired_collections:
            logger.debug(f"缓存过期: 删除集合 '{name}' 的标题缓存")
            self._remove_from_cache(name)
        
        # 如果缓存集合数量仍然超过最大值，删除最旧的
        if len(self._collections_titles_cache) > self.max_collections:
            oldest_collection = min(
                self._last_used.keys(),
                key=lambda k: self._last_used.get(k, 0)
            )
            logger.debug(f"缓存管理: 删除最旧的集合 '{oldest_collection}' 的标题缓存")
            self._remove_from_cache(oldest_collection)
    
    def _remove_from_cache(self, collection_name: str) -> None:
        """从缓存中删除集合"""
        if collection_name in self._collections_titles_cache:
            del self._collections_titles_cache[collection_name]
        
        if collection_name in self._cache_expire_time:
            del self._cache_expire_time[collection_name]
            
        if collection_name in self._last_used:
            del self._last_used[collection_name]
    
    def has_cached_titles(self, collection_name: str) -> bool:
        """
        检查集合是否有缓存的标题列表
        
        Args:
            collection_name: 集合名称
            
        Returns:
            是否有缓存的标题
        """
        # 更新最后使用时间
        if collection_name in self._collections_titles_cache:
            self._last_used[collection_name] = time.time()
            # 检查是否过期
            if time.time() > self._cache_expire_time.get(collection_name, 0):
                logger.debug(f"集合 '{collection_name}' 的标题缓存已过期")
                self._remove_from_cache(collection_name)
                return False
            return True
        return False
    
    def get_cached_titles(self, collection_name: str) -> List[str]:
        """
        获取缓存的标题列表
        
        Args:
            collection_name: 集合名称
            
        Returns:
            标题列表，如果没有缓存则返回空列表
        """
        if self.has_cached_titles(collection_name):
            return list(self._collections_titles_cache[collection_name])
        return []
    
    def normalize_title(self, title: str) -> str:
        """
        规范化标题，处理特殊字符和编码问题
        
        Args:
            title: 原始标题
            
        Returns:
            规范化后的标题
        """
        try:
            # 尝试规范化标题文本，消除特殊字符可能造成的编码问题
            normalized_title = unicodedata.normalize('NFKD', title)
            
            # 如果标题包含非ASCII字符，记录日志
            if not all(ord(c) < 128 for c in title):
                logger.debug(f"标题包含非ASCII字符: '{title}' → '{normalized_title}'")
            
            return normalized_title
        except Exception as e:
            logger.warning(f"规范化标题时出错: {e}")
            # 继续使用原始标题
            return title
    
    def find_closest_title(self, collection_name: str, title: str, 
                           similarity_threshold: float = 0.6) -> Optional[str]:
        """
        在集合中找到与给定标题最相似的标题
        
        Args:
            collection_name: 集合名称
            title: 要匹配的标题
            similarity_threshold: 相似度阈值，低于此值的匹配将被忽略

        Returns:
            最相似的标题，如果没有找到则返回None
        """
        # 如果集合标题未缓存，返回None
        if not self.has_cached_titles(collection_name):
            logger.debug(f"集合 '{collection_name}' 没有缓存的标题")
            return None
        
        titles = self._collections_titles_cache[collection_name]
        if not titles:
            logger.debug(f"集合 '{collection_name}' 的标题列表为空")
            return None
        
        # 尝试先规范化标题
        normalized_query_title = self.normalize_title(title)
        
        # 计算最相似的标题
        try:
            # 使用difflib中的SequenceMatcher计算相似度
            def similarity(a: str, b: str) -> float:
                return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
            
            # 计算所有标题与目标标题的相似度
            similarities = [(t, similarity(t, normalized_query_title)) for t in titles]
            
            # 按相似度排序并返回最相似的
            if not similarities:
                return None
                
            closest = max(similarities, key=lambda x: x[1])
            
            # 如果相似度低于阈值，返回None
            if closest[1] < similarity_threshold:
                logger.info(f"未找到足够相似的标题: '{title}' (最佳匹配 '{closest[0]}' 相似度: {closest[1]:.2f}, 阈值: {similarity_threshold})")
                return None
            
            logger.info(f"未找到精确匹配标题 '{title}'，使用最相似的标题: '{closest[0]}' (相似度: {closest[1]:.2f})")
            
            return closest[0]
            
        except Exception as e:
            logger.error(f"查找相似标题时出错: {e}")
            return None

# 创建全局标题匹配器实例
title_matcher = TitleMatcher() 