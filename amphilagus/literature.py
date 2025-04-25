"""
文献管理模块，用于存储和管理学术文献信息。
"""
import os
import json
import re
from typing import List, Dict, Any, Optional, ClassVar
from dataclasses import dataclass, field, asdict
import datetime
from pathlib import Path

from .logger import get_logger
from . import config

logger = get_logger('literature')

# 创建知识库目录
os.makedirs(config.KNOWLEDGE_DIR, exist_ok=True)

@dataclass
class Literature:
    """
    文献类，用于存储学术文献的元数据和内容。
    """
    title: str                      # 文献名
    journal: str                    # 发表期刊
    publish_year: int               # 发表年份
    background: str = ""            # 研究背景
    methodology: str = ""           # 研究方法
    content: str = ""               # 研究内容
    research_field: List[str] = field(default_factory=list)  # 研究领域
    highlights: str = ""            # 研究亮点
    authors: List[str] = field(default_factory=list)     # 作者列表
    tags: List[str] = field(default_factory=list)        # 标签列表
    review: str = ""                                     # 评价
    
    # 额外信息
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    # 类变量，用于缓存所有文献数据
    _literature_cache: ClassVar[Dict[str, 'Literature']] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """将文献对象转换为字典以便序列化"""
        data = asdict(self)
        
        # 将日期时间转换为ISO格式字符串
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Literature':
        """从字典创建文献对象"""
        # 处理日期时间字段
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.datetime.fromisoformat(data['updated_at'])
            
        return cls(**data)
    
    def save(self) -> None:
        """保存文献到JSON文件"""
        # 更新修改时间
        self.updated_at = datetime.datetime.now()
        
        # 更新缓存
        Literature._literature_cache[self.title] = self
        
        # 将所有缓存中的文献保存到文件
        cls = self.__class__
        cls._save_all_to_file()
        
        logger.info(f"文献 '{self.title}' 已保存")
    
    @classmethod
    def _save_all_to_file(cls) -> None:
        """将所有文献保存到JSON文件"""
        try:
            literature_data = {
                "literature": [lit.to_dict() for lit in cls._literature_cache.values()]
            }
            
            with open(config.LITERATURE_DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(literature_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"保存文献数据时出错: {str(e)}")
            raise
    
    @classmethod
    def load_all(cls) -> Dict[str, 'Literature']:
        """加载所有文献数据"""
        if not os.path.exists(config.LITERATURE_DATA_PATH):
            logger.info(f"文献数据文件不存在: {config.LITERATURE_DATA_PATH}")
            return {}
        
        try:
            with open(config.LITERATURE_DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            literature_data = data.get("literature", [])
            cls._literature_cache = {
                item["title"]: cls.from_dict(item) 
                for item in literature_data
            }
            
            logger.info(f"已加载 {len(cls._literature_cache)} 篇文献")
            return cls._literature_cache
            
        except Exception as e:
            logger.error(f"加载文献数据时出错: {str(e)}")
            return {}
    
    @classmethod
    def get_by_title(cls, title: str) -> Optional['Literature']:
        """通过文献名获取文献实例"""
        # 如果缓存为空，先加载所有文献
        if not cls._literature_cache:
            cls.load_all()
            
        return cls._literature_cache.get(title)
    
    @classmethod
    def list_all(cls) -> List['Literature']:
        """列出所有文献"""
        # 如果缓存为空，先加载所有文献
        if not cls._literature_cache:
            cls.load_all()
            
        return list(cls._literature_cache.values())
    
    @classmethod
    def search(cls, keyword: str) -> List['Literature']:
        """搜索文献"""
        # 如果缓存为空，先加载所有文献
        if not cls._literature_cache:
            cls.load_all()
            
        keyword = keyword.lower()
        results = []
        
        for lit in cls._literature_cache.values():
            # 在标题、期刊、背景、内容、作者中搜索
            if (keyword in lit.title.lower() or 
                keyword in lit.journal.lower() or
                keyword in lit.background.lower() or
                keyword in lit.content.lower() or
                any(keyword in author.lower() for author in lit.authors)):
                results.append(lit)
                
        return results
    
    def delete(self) -> bool:
        """删除文献"""
        cls = self.__class__
        
        if self.title in cls._literature_cache:
            del cls._literature_cache[self.title]
            cls._save_all_to_file()
            logger.info(f"文献 '{self.title}'.已删除")
            return True
        
        return False
    
    def __str__(self) -> str:
        """获取文献的字符串表示"""
        authors_str = ", ".join(self.authors) if self.authors else "未知"
        return f"{self.title} ({self.publish_year}) - {authors_str}. {self.journal}"
        
    def load_tags_from_json(self, file_manager) -> None:
        """
        从FileManager中加载标签
        
        Args:
            file_manager: FileManager实例
        """
        filename = f"{self.title}.md"
        if filename in file_manager.metadata:
            # 从file_manager获取标签
            metadata = file_manager.metadata[filename]
            # 将Tag对象转换为字符串列表
            self.tags = [tag.name for tag in metadata.tags]
            logger.info(f"从文件 {filename} 加载了 {len(self.tags)} 个标签")
        else:
            logger.warning(f"未找到文件 {filename} 的元数据，无法加载标签")
            
    def update_from_tags(self, file_manager) -> None:
        """
        根据标签更新文献属性
        
        Args:
            file_manager: FileManager实例，用于获取标签信息
        """
        if not self.tags:
            logger.warning(f"文献 '{self.title}' 没有标签，无法更新属性")
            return
            
        # 遍历所有标签，查看它们的父标签类型
        for tag_name in self.tags:
            if tag_name not in file_manager.tag_registry:
                logger.warning(f"标签 '{tag_name}' 不在标签注册表中，跳过")
                continue
                
            tag = file_manager.tag_registry[tag_name]
            parent_tag = tag.parent
            
            if not parent_tag:
                logger.debug(f"标签 '{tag_name}' 没有父标签，跳过")
                continue
                
            # 根据父标签类型更新不同的属性
            if parent_tag.name == "期刊类型":
                self.journal = tag_name
                logger.info(f"从标签更新文献 '{self.title}' 的期刊: {tag_name}")
                
            elif parent_tag.name == "发表时间":
                # 提取年份数字
                year_match = re.search(r'(\d{4})年?', tag_name)
                if year_match:
                    try:
                        year = int(year_match.group(1))
                        self.publish_year = year
                        logger.info(f"从标签更新文献 '{self.title}' 的发表年份: {year}")
                    except ValueError:
                        logger.error(f"标签 '{tag_name}' 中的年份格式无效")
                        
            elif parent_tag.name == "研究领域":
                if tag_name not in self.research_field:
                    self.research_field.append(tag_name)
                    logger.info(f"从标签添加文献 '{self.title}' 的研究领域: {tag_name}")
                    
            elif parent_tag.name == "评分":
                self.review = tag_name
                logger.info(f"从标签更新文献 '{self.title}' 的评价: {tag_name}")
    
    def update_file_tags(self, file_manager, auto_create_tags: bool = False) -> bool:
        """
        将文献属性更新到文件标签
        
        Args:
            file_manager: FileManager实例
            auto_create_tags: 是否自动创建不存在的标签
            
        Returns:
            成功返回True，失败返回False
        """
        filename = f"{self.title}.md"
        if filename not in file_manager.metadata:
            logger.warning(f"未找到文件 {filename} 的元数据，无法更新标签")
            return False
            
        try:
            # 获取当前的标签对象集合
            current_tag_objs = file_manager.metadata[filename].tags
            # 获取当前标签的名称列表
            current_tags = [tag.name for tag in current_tag_objs]
            
            # 需要移除的标签
            tags_to_remove = []
            # 保留的非分类标签
            other_tags = []
            
            # 处理现有标签，识别基础分类标签和其他标签
            for tag_name in current_tags:
                if tag_name in file_manager.tag_registry:
                    tag = file_manager.tag_registry[tag_name]
                    parent = tag.parent
                    
                    # 如果有父标签，且父标签是基础分类之一，标记为需要移除
                    if parent and parent.name in ["期刊类型", "发表时间", "研究领域", "评分"]:
                        tags_to_remove.append(tag_name)
                    else:
                        # 保留其他非分类标签
                        other_tags.append(tag_name)
                else:
                    # 不在注册表中的标签也保留
                    other_tags.append(tag_name)
            
            # 新标签列表，先添加所有保留的非分类标签
            new_tags = other_tags.copy()
            
            # 添加期刊标签
            if self.journal:
                # 检查期刊是否已经在标签注册表中
                journal_tag_exists = False
                for tag_name, tag in file_manager.tag_registry.items():
                    if tag_name.lower() == self.journal.lower() and tag.parent and tag.parent.name == "期刊类型":
                        new_tags.append(tag_name)  # 使用已存在的标签名（保持原大小写）
                        journal_tag_exists = True
                        break
                
                # 如果不存在，可能需要创建新标签
                if not journal_tag_exists and self.journal not in new_tags:
                    if auto_create_tags:
                        # 创建新标签，设置父标签为"期刊类型"
                        try:
                            file_manager.create_tag(self.journal, "期刊类型")
                            logger.info(f"自动创建期刊标签: {self.journal}")
                        except Exception as e:
                            logger.error(f"创建期刊标签 {self.journal} 失败: {str(e)}")
                    new_tags.append(self.journal)
                    
            # 添加年份标签
            if self.publish_year:
                year_tag = f"{self.publish_year}年"
                # 检查年份标签是否存在
                year_tag_exists = False
                for tag_name, tag in file_manager.tag_registry.items():
                    if tag.parent and tag.parent.name == "发表时间" and str(self.publish_year) in tag_name:
                        new_tags.append(tag_name)
                        year_tag_exists = True
                        break
                
                if not year_tag_exists and year_tag not in new_tags:
                    if auto_create_tags:
                        # 创建新年份标签
                        try:
                            file_manager.create_tag(year_tag, "发表时间")
                            logger.info(f"自动创建年份标签: {year_tag}")
                        except Exception as e:
                            logger.error(f"创建年份标签 {year_tag} 失败: {str(e)}")
                    new_tags.append(year_tag)
            
            # 添加研究领域标签
            for field in self.research_field:
                if field not in new_tags:
                    # 检查研究领域标签是否存在
                    field_tag_exists = False
                    for tag_name, tag in file_manager.tag_registry.items():
                        if tag_name.lower() == field.lower() and tag.parent and tag.parent.name == "研究领域":
                            if tag_name not in new_tags:
                                new_tags.append(tag_name)
                            field_tag_exists = True
                            break
                    
                    if not field_tag_exists:
                        if auto_create_tags:
                            # 创建新研究领域标签
                            try:
                                file_manager.create_tag(field, "研究领域")
                                logger.info(f"自动创建研究领域标签: {field}")
                            except Exception as e:
                                logger.error(f"创建研究领域标签 {field} 失败: {str(e)}")
                        new_tags.append(field)
            
            # 添加评价标签
            if self.review:
                # 检查评价标签是否存在
                review_tag_exists = False
                for tag_name, tag in file_manager.tag_registry.items():
                    if tag.parent and tag.parent.name == "评分" and tag_name.lower() == self.review.lower():
                        new_tags.append(tag_name)
                        review_tag_exists = True
                        break
                
                if not review_tag_exists and self.review not in new_tags:
                    if auto_create_tags:
                        # 创建新评价标签
                        try:
                            file_manager.create_tag(self.review, "评分")
                            logger.info(f"自动创建评价标签: {self.review}")
                        except Exception as e:
                            logger.error(f"创建评价标签 {self.review} 失败: {str(e)}")
                    new_tags.append(self.review)
            
            # 移除所有待移除的标签
            if tags_to_remove:
                file_manager.remove_tags_from_file(filename, tags_to_remove)
            
            # 添加新标签（避免重复添加）
            tags_to_add = [tag for tag in new_tags if tag not in current_tags]
            if tags_to_add:
                file_manager.add_tags_to_file(filename, tags_to_add)
            
            logger.info(f"已更新文件 {filename} 的标签: {new_tags}")
            return True
            
        except Exception as e:
            logger.error(f"更新文件 {filename} 的标签时出错: {str(e)}")
            return False 