"""
Main module for Amphilagus - Project management for RAG Assistant.

This module coordinates between different components of the Haystack RAG Assistant project,
including raw_data management, RAG assistant interactions, and external tool integrations.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .file_manager import FileManager, Tag, Metadata


class Amphilagus:
    """
    Main class for Amphilagus project management.
    
    Responsibilities:
    - Manage raw_data files with tagging
    - Coordinate with RAG assistant
    - Manage external tool integrations
    """
    
    def __init__(self, raw_data_dir: str = 'raw_data'):
        """
        Initialize Amphilagus project manager.
        
        Args:
            raw_data_dir: Directory for raw data files
        """
        self.file_manager = FileManager(raw_data_dir=raw_data_dir)
        
    # Raw data management methods
    
    def add_raw_data(self, file_path: Union[str, Path], tags: List[str] = None, 
                    description: str = "", additional_info: Dict[str, Any] = None) -> str:
        """
        Add a raw data file with optional tags and metadata.
        
        Args:
            file_path: Path to the file to add
            tags: List of tag names to apply to the file
            description: Description of the file
            additional_info: Additional metadata as key-value pairs
            
        Returns:
            The filename of the added file
        """
        return self.file_manager.add_file(
            file_path, 
            tags=tags, 
            description=description,
            additional_info=additional_info
        )
    
    def delete_raw_data(self, filename: str) -> bool:
        """
        Delete a raw data file.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if the file was deleted, False otherwise
        """
        return self.file_manager.delete_file(filename)
    
    def add_tags(self, filename: str, tags: List[str]) -> bool:
        """
        Add tags to a raw data file.
        
        Args:
            filename: Name of the file to tag
            tags: List of tag names to apply
            
        Returns:
            True if the tags were added, False if the file doesn't exist
        """
        return self.file_manager.add_tags_to_file(filename, tags)
    
    def remove_tags(self, filename: str, tags: List[str]) -> bool:
        """
        Remove tags from a raw data file.
        
        Args:
            filename: Name of the file
            tags: List of tag names to remove
            
        Returns:
            True if the tags were removed, False if the file doesn't exist
        """
        return self.file_manager.remove_tags_from_file(filename, tags)
    
    def get_raw_data_by_tag(self, tag_name: str, include_subclasses: bool = True) -> List[Metadata]:
        """
        Get all raw data files with a specific tag.
        
        Args:
            tag_name: Name of the tag to filter by
            include_subclasses: Whether to include files with tags that are subclasses of the given tag
            
        Returns:
            List of Metadata objects for matching files
        """
        return self.file_manager.get_files_by_tag(tag_name, include_subclasses)
    
    def get_raw_data_metadata(self, filename: str) -> Optional[Metadata]:
        """Get metadata for a specific raw data file."""
        return self.file_manager.get_file_metadata(filename)
    
    def list_raw_data(self) -> List[Metadata]:
        """List all raw data files."""
        return self.file_manager.list_files()
    
    # Tag management methods
    
    def create_tag(self, name: str, parent_name: Optional[str] = None) -> Tag:
        """
        Create a new tag with optional parent.
        
        Args:
            name: Name of the tag to create
            parent_name: Name of the parent tag if any
            
        Returns:
            The created Tag object
        """
        return self.file_manager.create_tag(name, parent_name)
    
    def get_tag(self, name: str) -> Optional[Tag]:
        """Get a tag by name."""
        return self.file_manager.get_tag(name)
    
    def list_tags(self) -> List[Tag]:
        """List all available tags."""
        return self.file_manager.list_tags()
    
    # Future functionalities
    
    def call_rag_assistant(self, query: str) -> str:
        """
        Call the RAG assistant with a query.
        
        This is a placeholder for future implementation.
        
        Args:
            query: Query to send to the RAG assistant
            
        Returns:
            Response from the RAG assistant
        """
        # TODO: Implement integration with RAG assistant
        return f"RAG assistant would process: {query}"
    
    def call_external_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Call an external tool with parameters.
        
        This is a placeholder for future implementation.
        
        Args:
            tool_name: Name of the external tool to call
            **kwargs: Parameters to pass to the tool
            
        Returns:
            Result from the external tool
        """
        # TODO: Implement integration with external tools
        return f"Would call tool '{tool_name}' with params: {kwargs}" 