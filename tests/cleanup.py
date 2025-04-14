#!/usr/bin/env python
"""
Cleanup script for the RAG Assistant tests.

This script cleans up the test files and directories created during testing.
"""

import os
import shutil
from pathlib import Path

def main():
    """Clean up test files and directories."""
    # Get current directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    
    # Directories to clean up
    cleanup_dirs = [
        project_dir / "test_files",
        project_dir / "chroma_db"
    ]
    
    # Clean up directories
    for directory in cleanup_dirs:
        if directory.exists():
            print(f"Cleaning up {directory}...")
            try:
                shutil.rmtree(directory)
                print(f"✓ Removed {directory}")
            except Exception as e:
                print(f"✗ Failed to remove {directory}: {e}")
    
    print("Cleanup completed.")

if __name__ == "__main__":
    main() 