"""
File management module for raw_data with tagging system.
"""
import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Union
from dataclasses import dataclass, field, asdict


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
    """Metadata for raw_data files."""
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
    Manages raw_data files with a tag-based system.
    """
    def __init__(self, raw_data_dir: str = 'raw_data', metadata_file: str = 'raw_data_metadata.json'):
        self.raw_data_dir = Path(raw_data_dir)
        self.metadata_file = self.raw_data_dir / metadata_file
        self.metadata: Dict[str, Metadata] = {}
        self.tag_registry: Dict[str, Tag] = {}
        
        # Create raw_data directory if it doesn't exist
        os.makedirs(self.raw_data_dir, exist_ok=True)
        
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
    
    def add_file(self, file_path: Union[str, Path], tags: List[str] = None, 
                description: str = "", additional_info: Dict[str, Any] = None) -> str:
        """
        Add a file to raw_data with optional tags and metadata.
        
        Args:
            file_path: Path to the file to add
            tags: List of tag names to apply to the file
            description: Description of the file
            additional_info: Additional metadata as key-value pairs
            
        Returns:
            The filename of the added file
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} does not exist")
        
        # Copy file to raw_data directory
        destination = self.raw_data_dir / file_path.name
        shutil.copy2(file_path, destination)
        
        # Create metadata
        tag_objects = set()
        if tags:
            for tag_name in tags:
                if tag_name in self.tag_registry:
                    tag_objects.add(self.tag_registry[tag_name])
                else:
                    # Create tag if it doesn't exist
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
        
        self.metadata[file_path.name] = metadata
        self._save_metadata()
        
        return file_path.name
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from raw_data.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if the file was deleted, False otherwise
        """
        if filename not in self.metadata:
            return False
        
        file_path = self.raw_data_dir / filename
        if file_path.exists():
            os.remove(file_path)
        
        del self.metadata[filename]
        self._save_metadata()
        
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
        """List all files in raw_data."""
        return list(self.metadata.values()) 