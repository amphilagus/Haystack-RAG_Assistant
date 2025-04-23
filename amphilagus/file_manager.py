"""
File management module for raw_files with tagging system.
"""
import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Union
from dataclasses import dataclass, field, asdict
import re

from .logger import get_logger
from . import config

logger = get_logger('file_manager')
# 测试logger是否被激活
logger.debug("FileManager logger initialized")

class Tag:
    """
    Base class for all tags. Tags have inheritance properties similar to Python classes.
    """
    def __init__(self, name: str, parent: Optional['Tag'] = None):
        self.name = name
        self.parent = parent
        self.is_base_tag = False  # 标记是否为基础类标签
        self.is_preset_tag = False  # 标记是否为预设标签
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other: 'Tag') -> bool:
        if not isinstance(other, Tag):
            return False
        return self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)
    
    def is_subclass_of(self, other: 'Tag') -> bool:
        """Check if this tag is a subclass of another tag."""
        if self == other:
            return True
        
        current = self.parent
        while current is not None:
            if current == other:
                return True
            current = current.parent
        
        return False


@dataclass
class Metadata:
    """Metadata for raw_files files."""
    filename: str
    filepath: Path
    tags: Set[Tag] = field(default_factory=set)
    description: str = ""
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        result = asdict(self)
        # Convert Path to string
        result['filepath'] = str(result['filepath'])
        # Convert Tags to string representations
        result['tags'] = [t.name for t in self.tags]
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], tag_registry: Dict[str, Tag]) -> 'Metadata':
        """Create Metadata from dictionary with tag registry."""
        tags = {tag_registry.get(tag_name, Tag(tag_name)) for tag_name in data.get('tags', [])}
        
        return cls(
            filename=data['filename'],
            filepath=Path(data['filepath']),
            tags=tags,
            description=data.get('description', ''),
            additional_info=data.get('additional_info', {})
        )


class FileManager:
    """
    Manages raw_files files with a tag-based system.
    """
    def __init__(self, raw_files_dir: str = 'files/raw_files', metadata_file: str = 'files/raw_files_metadata.json',
                 backup_files_dir: str = 'files/backup_files'):
        self.raw_files_dir = Path(raw_files_dir)
        self.backup_files_dir = Path(backup_files_dir)
        self.metadata_file =  metadata_file
        self.metadata: Dict[str, Metadata] = {}
        self.tag_registry: Dict[str, Tag] = {}
        
        # Create raw_files directory if it doesn't exist
        os.makedirs(self.raw_files_dir, exist_ok=True)
        os.makedirs(self.backup_files_dir, exist_ok=True)
        # Load metadata if file exists
        if os.path.exists(self.metadata_file):
            self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load metadata from file."""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # First pass: create all tags
            for tag_data in data.get('tags', []):
                name = tag_data['name']
                self.tag_registry[name] = Tag(name)
                # 加载标签的is_base_tag属性
                if 'is_base_tag' in tag_data:
                    self.tag_registry[name].is_base_tag = tag_data['is_base_tag']
                # 加载标签的is_preset_tag属性
                if 'is_preset_tag' in tag_data:
                    self.tag_registry[name].is_preset_tag = tag_data['is_preset_tag']
            
            # Second pass: establish parent relationships
            for tag_data in data.get('tags', []):
                name = tag_data['name']
                parent_name = tag_data.get('parent')
                if parent_name and parent_name in self.tag_registry:
                    self.tag_registry[name].parent = self.tag_registry[parent_name]
            
            # Load file metadata
            for file_data in data.get('files', []):
                metadata = Metadata.from_dict(file_data, self.tag_registry)
                self.metadata[metadata.filename] = metadata
                
        except (json.JSONDecodeError, FileNotFoundError):
            # Initialize with empty data if file doesn't exist or is corrupted
            self.metadata = {}
            self.tag_registry = {}
    
    def _save_metadata(self) -> None:
        """Save metadata to file."""
        # Prepare tag data
        tag_data = []
        for tag in self.tag_registry.values():
            tag_info = {
                'name': tag.name,
                'is_base_tag': getattr(tag, 'is_base_tag', False),
                'is_preset_tag': getattr(tag, 'is_preset_tag', False)
            }
            if tag.parent:
                tag_info['parent'] = tag.parent.name
            tag_data.append(tag_info)
        
        # Prepare file data
        file_data = [metadata.to_dict() for metadata in self.metadata.values()]
        
        # Save to file
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                'tags': tag_data,
                'files': file_data
            }, f, indent=2, ensure_ascii=False)
    
    def create_tag(self, name: str, parent_name: Optional[str] = None) -> Tag:
        """
        Create a new tag with optional parent.
        
        Args:
            name: Name of the tag to create
            parent_name: Name of the parent tag if any
            
        Returns:
            The created Tag object
        """
        if name in self.tag_registry:
            raise ValueError(f"Tag '{name}' already exists")
        
        parent = None
        if parent_name:
            if parent_name not in self.tag_registry:
                raise ValueError(f"Parent tag '{parent_name}' does not exist")
            parent = self.tag_registry[parent_name]
        
        tag = Tag(name, parent)
        self.tag_registry[name] = tag
        self._save_metadata()
        return tag
    
    def delete_tag(self, name: str) -> bool:
        """
        Delete a tag from the registry.
        
        Args:
            name: Name of the tag to delete
            
        Returns:
            True if the tag was deleted, False otherwise
        """
        if name not in self.tag_registry:
            return False
            
        tag = self.tag_registry[name]
        
        # 检查是否为基础类标签，不允许删除
        # 注意：预设标签(is_preset_tag=True)可以删除
        if getattr(tag, 'is_base_tag', False):
            raise ValueError(f"基础类标签 '{name}' 不能被删除")
        
        # 检查是否有子标签依赖此标签
        children = [t for t in self.tag_registry.values() if t.parent and t.parent.name == name]
        if children:
            child_names = ", ".join([c.name for c in children])
            raise ValueError(f"标签 '{name}' 有子标签依赖: {child_names}")
        
        # 从所有文件中移除此标签
        for metadata in self.metadata.values():
            metadata.tags = {t for t in metadata.tags if t.name != name}
        
        # 从注册表中移除
        del self.tag_registry[name]
        
        self._save_metadata()
        return True
    
    def get_tag(self, name: str) -> Optional[Tag]:
        """Get a tag by name."""
        return self.tag_registry.get(name)
    
    def list_tags(self) -> List[Tag]:
        """List all available tags."""
        return list(self.tag_registry.values())
    
    def add_file(self, file_path: Union[str, Path], backup_files_path: Union[str, Path], tags: List[str] = None, 
                description: str = "", additional_info: Dict[str, Any] = None) -> str:
        """
        Add a file to raw_files with optional tags and metadata.
        """
        logger.debug(f"add_file called with file_path={file_path}, backup_files_path={backup_files_path}, tags={tags}, description={description}, additional_info={additional_info}")
        file_path = Path(file_path)
        backup_files_path = Path(backup_files_path)
        logger.debug(f"Resolved paths: file_path={file_path}, backup_files_path={backup_files_path}")
        if not file_path.exists():
            logger.error(f"Source file does not exist: {file_path}")
            raise FileNotFoundError(f"File {file_path} does not exist")
        
        # Copy file to raw_files directory
        destination = self.raw_files_dir / file_path.name
        logger.debug(f"Copying file to raw_files directory: {file_path} -> {destination}")
        shutil.copy2(file_path, destination)
        logger.debug(f"File copy completed to {destination}")
        description_backup = self.backup_files_dir / (file_path.name.split('.')[0] + '.' + backup_files_path.name.split('.')[-1])
        logger.debug(f"Copying backup file to backup_files directory: {backup_files_path} -> {description_backup}")
        shutil.copy2(backup_files_path, description_backup)
        logger.debug(f"Backup file copy completed to {description_backup}")
        
        # Create metadata
        tag_objects = set()
        logger.debug(f"Processing tags list: {tags}")
        if tags:
            for tag_name in tags:
                if tag_name in self.tag_registry:
                    logger.debug(f"Existing tag found: {tag_name}")
                    tag_objects.add(self.tag_registry[tag_name])
                else:
                    logger.debug(f"Creating new tag: {tag_name}")
                    tag = Tag(tag_name)
                    self.tag_registry[tag_name] = tag
                    tag_objects.add(tag)
        
        metadata = Metadata(
            filename=file_path.name,
            filepath=destination,
            tags=tag_objects,
            description=description,
            additional_info=additional_info or {}
        )
        logger.debug(f"Metadata object created: {metadata}")
        
        self.metadata[file_path.name] = metadata
        logger.debug(f"Metadata stored in registry for file: {file_path.name}")
        self._save_metadata()
        logger.debug(f"Metadata file saved to disk at {self.metadata_file if hasattr(self, 'metadata_file') else 'default location'}")
        
        return file_path.name
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from raw_files.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if the file was deleted, False otherwise
        """
        logger.debug(f"delete_file called for filename: {filename}")
        if filename not in self.metadata:
            logger.warning(f"File {filename} not found in metadata, cannot delete")
            return False
        
        file_path = self.raw_files_dir / filename
        logger.debug(f"Attempting to delete file from raw_files: {file_path}")
        if file_path.exists():
            os.remove(file_path)
            logger.debug(f"Deleted file from raw_files: {file_path}")
        else:
            logger.warning(f"File {file_path} does not exist in raw_files directory")
        
        # 删除backup_files目录中的对应文件
        # 构建备份文件名（与add_file方法中相同的逻辑）
        backup_file_base = filename.split('.')[0]
        backup_files = list(self.backup_files_dir.glob(f"{backup_file_base}.*"))
        if backup_files:
            for backup_file in backup_files:
                logger.debug(f"Deleting backup file: {backup_file}")
                try:
                    os.remove(backup_file)
                    logger.debug(f"Deleted backup file: {backup_file}")
                except Exception as e:
                    logger.error(f"Failed to delete backup file {backup_file}: {str(e)}")
        else:
            logger.warning(f"No backup files found for {filename} in {self.backup_files_dir}")
        
        del self.metadata[filename]
        logger.debug(f"Removed metadata entry for {filename}")
        self._save_metadata()
        logger.debug(f"Saved metadata after deleting {filename}")
        
        return True
    
    def add_tags_to_file(self, filename: str, tags: List[str]) -> bool:
        """
        Add tags to a file.
        
        Args:
            filename: Name of the file to tag
            tags: List of tag names to apply
            
        Returns:
            True if the tags were added, False if the file doesn't exist
        """
        if filename not in self.metadata:
            return False
        
        for tag_name in tags:
            if tag_name not in self.tag_registry:
                # Create tag if it doesn't exist
                self.tag_registry[tag_name] = Tag(tag_name)
            
            self.metadata[filename].tags.add(self.tag_registry[tag_name])
        
        self._save_metadata()
        return True
    
    def remove_tags_from_file(self, filename: str, tags: List[str]) -> bool:
        """
        Remove tags from a file.
        
        Args:
            filename: Name of the file
            tags: List of tag names to remove
            
        Returns:
            True if the tags were removed, False if the file doesn't exist
        """
        if filename not in self.metadata:
            return False
        
        for tag_name in tags:
            if tag_name in self.tag_registry:
                tag = self.tag_registry[tag_name]
                if tag in self.metadata[filename].tags:
                    self.metadata[filename].tags.remove(tag)
        
        self._save_metadata()
        return True
    
    def get_files_by_tag(self, tag_name: str, include_subclasses: bool = True) -> List[Metadata]:
        """
        Get all files with a specific tag.
        
        Args:
            tag_name: Name of the tag to filter by
            include_subclasses: Whether to include files with tags that are subclasses of the given tag
            
        Returns:
            List of Metadata objects for matching files
        """
        if tag_name not in self.tag_registry:
            return []
        
        tag = self.tag_registry[tag_name]
        result = []
        
        for metadata in self.metadata.values():
            for file_tag in metadata.tags:
                if file_tag == tag or (include_subclasses and file_tag.is_subclass_of(tag)):
                    result.append(metadata)
                    break
        
        return result
    
    def get_file_metadata(self, filename: str) -> Optional[Metadata]:
        """Get metadata for a specific file."""
        return self.metadata.get(filename)
    
    def list_files(self) -> List[Metadata]:
        """List all files in raw_files."""
        return list(self.metadata.values())
    
    def clean_markdown_content(self, content: str, tags: List[str]) -> str:
        """
        根据标签应用清理规则处理Markdown内容
        
        Args:
            content: 原始Markdown内容
            tags: 适用于该内容的标签列表
            
        Returns:
            处理后的Markdown内容
        """
        logger.debug(f"开始清理Markdown内容，应用标签: {tags}")
        
        try:
            # 查找匹配的期刊类型标签
            journal_type = None
            
            # 规范化配置键和标签，以提高匹配成功率
            # 转为小写，移除多余空格，替换特殊字符
            def normalize_text(text):
                normalized = text.lower().strip()
                normalized = re.sub(r'[^a-z0-9]', '', normalized)
                return normalized
                
            # 创建规范化的配置键映射到原始键
            config_keys_normalized = {}
            logger.debug(f"MD_CLEANER_CONFIG中的原始键: {list(config.MD_CLEANER_CONFIG.keys())}")
            
            for k in config.MD_CLEANER_CONFIG.keys():
                normalized_key = normalize_text(k)
                config_keys_normalized[normalized_key] = k
                logger.debug(f"规范化配置键: '{k}' -> '{normalized_key}'")
            
            logger.debug(f"规范化后的配置键映射: {config_keys_normalized}")
            
            for tag in tags:
                logger.debug(f"检查标签: {tag}")
                # 规范化标签
                normalized_tag = normalize_text(tag)
                logger.debug(f"规范化后的标签: '{tag}' -> '{normalized_tag}'")
                
                # 检查标签是否是已配置的期刊类型（使用规范化后的比较）
                if normalized_tag in config_keys_normalized:
                    # 使用原始大小写的配置键
                    journal_type = config_keys_normalized[normalized_tag]
                    logger.debug(f"找到匹配的期刊类型: {journal_type} (匹配标签: {tag})")
                    break
            
            # 如果找到匹配的期刊类型，应用对应的清理规则
            if journal_type:
                logger.info(f"应用 {journal_type} 期刊的清理规则")
                rules = config.MD_CLEANER_CONFIG[journal_type]
                cleaned_content = config.clean_markdown(content, rules)
                return cleaned_content
            else:
                logger.info("未找到匹配的期刊类型，不应用清理规则")
                logger.debug(f"所有标签均未能匹配配置键。标签: {tags}, 可用键: {list(config.MD_CLEANER_CONFIG.keys())}")
                return content
        except Exception as e:
            logger.error(f"清理Markdown时出错: {str(e)}")
            # 出错时返回原始内容
            return content
            
    def clean_markdown_file(self, filename: str) -> bool:
        """
        清洗已上传的Markdown文件
        
        Args:
            filename: 要清洗的文件名
            
        Returns:
            是否成功清洗文件
        """
        logger.debug(f"开始清洗文件: {filename}")
        
        # 检查文件是否存在
        if filename not in self.metadata:
            logger.error(f"文件 {filename} 不存在")
            return False
            
        metadata = self.metadata[filename]
        file_path = metadata.filepath
        
        # 检查文件是否为Markdown
        if not str(file_path).lower().endswith('.md'):
            logger.warning(f"文件 {filename} 不是Markdown文件，跳过清洗")
            return False
            
        # 读取原始内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            logger.error(f"读取文件 {filename} 时出错: {str(e)}")
            return False
            
        # 获取标签名列表
        tag_names = [tag.name for tag in metadata.tags]
        
        # 应用清洗规则
        cleaned_content = self.clean_markdown_content(original_content, tag_names)
        
        # 检查内容是否有变化
        if cleaned_content == original_content:
            logger.info(f"文件 {filename} 内容未发生变化，不需要清洗")
            return False
            
        # 写入清洗后的内容
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            logger.info(f"文件 {filename} 清洗成功")
            return True
        except Exception as e:
            logger.error(f"写入清洗后的内容到文件 {filename} 时出错: {str(e)}")
            return False
            
    def _clean_markdown_content(self, content):
        """
        清洗Markdown内容
        
        Args:
            content (str): 原始Markdown内容
            
        Returns:
            str: 清洗后的内容
        """
        logger.debug("执行Markdown内容清洗")
        
        # 移除多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 规范化标题格式（确保#后有空格）
        content = re.sub(r'(^|\n)(#{1,6})([^\s#])', r'\1\2 \3', content)
        
        # 规范化列表项格式（确保-后有空格）
        content = re.sub(r'(^|\n)-([^\s-])', r'\1- \2', content)
        
        # 规范化代码块（确保```后有语言标识或空行）
        content = re.sub(r'```(\w*)(?!\n)', r'```\1\n', content)
        content = re.sub(r'(?<!\n)```', r'\n```', content)
        
        # 修复表格格式问题
        lines = content.split('\n')
        for i in range(len(lines) - 1):
            if re.match(r'\|.*\|', lines[i]) and not re.match(r'\|[\s-]*\|', lines[i+1]) and '|' in lines[i+1]:
                header_cells = lines[i].count('|') - 1
                lines[i+1] = '|' + '|'.join([' --- ' for _ in range(header_cells)]) + '|'
        
        content = '\n'.join(lines)
        
        # 去除文档首尾多余的空行
        content = content.strip()
        
        logger.debug("Markdown内容清洗完成")
        return content
    
    def rename_file(self, old_filename: str, new_filename: str) -> bool:
        """
        重命名文件
        
        Args:
            old_filename: 原文件名
            new_filename: 新文件名
            
        Returns:
            成功返回True，失败返回False
        """
        logger.debug(f"开始重命名文件: {old_filename} -> {new_filename}")
        
        # 检查原文件是否存在
        if old_filename not in self.metadata:
            logger.error(f"文件 {old_filename} 不存在，无法重命名")
            return False
            
        # 检查新文件名是否已存在
        if new_filename in self.metadata:
            logger.error(f"文件名 {new_filename} 已存在，无法重命名")
            return False
            
        try:
            # 获取原文件的元数据和路径
            old_metadata = self.metadata[old_filename]
            old_raw_path = old_metadata.filepath
            
            # 构建新文件的路径
            new_raw_path = self.raw_files_dir / new_filename
            
            # 重命名raw_files目录中的文件
            if os.path.exists(old_raw_path):
                logger.debug(f"重命名raw_files中的文件: {old_raw_path} -> {new_raw_path}")
                shutil.move(old_raw_path, new_raw_path)
            else:
                logger.warning(f"raw_files中的文件不存在: {old_raw_path}")
            
            # 查找并重命名backup_files目录中的备份文件
            old_name_base = os.path.splitext(old_filename)[0]
            new_name_base = os.path.splitext(new_filename)[0]
            
            # 查找原备份文件（可能有多个扩展名）
            backup_files = list(self.backup_files_dir.glob(f"{old_name_base}.*"))
            for backup_file in backup_files:
                # 保持原扩展名
                ext = os.path.splitext(backup_file)[1]
                new_backup_path = self.backup_files_dir / f"{new_name_base}{ext}"
                logger.debug(f"重命名backup_files中的文件: {backup_file} -> {new_backup_path}")
                shutil.move(backup_file, new_backup_path)
            
            # 更新元数据
            new_metadata = Metadata(
                filename=new_filename,
                filepath=new_raw_path,
                tags=old_metadata.tags,
                description=old_metadata.description,
                additional_info=old_metadata.additional_info
            )
            
            # 更新元数据字典
            del self.metadata[old_filename]
            self.metadata[new_filename] = new_metadata
            
            # 保存元数据
            self._save_metadata()
            logger.info(f"文件重命名成功: {old_filename} -> {new_filename}")
            return True
            
        except Exception as e:
            logger.error(f"重命名文件时出错: {str(e)}")
            return False