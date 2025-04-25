"""
Amphilagus - Project management module for Haystack RAG Assistant
"""

__version__ = "0.1.0"

from .file_manager import FileManager, Tag, Metadata
from .database_manager import DatabaseManager
from .task_manager import TaskManager
from .assistant import MCPToolAgent
from .literature import Literature

__all__ = [
    "FileManager",
    "Tag",
    "Metadata",
    "DatabaseManager",
    "TaskManager",
    "MCPToolAgent",
    "Literature",
] 