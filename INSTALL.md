# Amphilagus Installation Guide

## Overview

Amphilagus是一个基于Web界面的项目管理工具，专为Haystack RAG Assistant设计。该应用程序提供直观的界面来管理文件、标签和向量数据库，不需要通过命令行使用。

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- git (optional, for cloning the repository)

## Installation Options

### 1. Development Mode Installation

For development purposes, install the package in "editable" mode. This allows you to modify the code and have those changes immediately reflected without needing to reinstall the package.

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/yourusername/amphilagus.git
cd amphilagus

# Create and activate a virtual environment (recommended)
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install in development mode with all extra dependencies
pip install -e ".[dev,web]"
```

For development without extras:

```bash
pip install -e .
```

### 2. From Source (Regular Installation)

If you want to install the package normally:

```bash
# Clone the repository
git clone https://github.com/yourusername/amphilagus.git
cd amphilagus

# Create and activate a virtual environment (recommended)
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install the package
pip install .
```

With specific extras:

```bash
pip install ".[web]"  # For web interface dependencies
pip install ".[dev]"  # For development dependencies
```

## Environment Setup

1. Create a `.env` file in the project root with the following configuration:

```
OPENAI_API_KEY=your_openai_api_key
FLASK_SECRET_KEY=your_secret_key
```

2. Set up the data directories:

```bash
mkdir -p raw_data backup_data chroma_db tasks
```

## Running the Web Application

After installation, you can start the web application using:

```bash
# If installed with entry points
amphilagus-web

# Or directly via Python
python -m amphilagus.web_app

# Or using the run script
python run_web_app.py
```

The web interface will be accessible at: http://localhost:5000

## Troubleshooting

### Missing Dependencies

If you encounter import errors, try reinstalling with all dependencies:

```bash
pip install -e ".[dev,web]"
```

### Permission Issues

If you encounter permission issues with directories:

```bash
# Ensure you have write permissions to the data directories
chmod -R u+w raw_data backup_data chroma_db tasks
```

### Path Issues

If you encounter module not found errors:

```bash
# Check your Python path
python -c "import sys; print(sys.path)"

# Ensure the project directory is in the Python path
export PYTHONPATH=$PYTHONPATH:/path/to/amphilagus
# On Windows:
set PYTHONPATH=%PYTHONPATH%;C:\path\to\amphilagus
```

## Uninstalling

```bash
pip uninstall amphilagus
``` 