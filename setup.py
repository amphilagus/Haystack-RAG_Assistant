#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import io

setup(
    name="amphilagus",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "python-dotenv>=1.0.0",
        "chromadb>=0.4.22",
        "openai>=1.12.0",
        "numpy>=1.24.0",
        "typing-extensions>=4.5.0",
        "markdown>=3.5.1",
        "haystack-ai>=2.0.0",
        "sentence-transformers>=2.2.2",
        "chroma-haystack>=0.1.2",
        "pypdf>=3.17.1",
        "beautifulsoup4>=4.12.0",
        "python-docx>=0.8.11",
        "flask>=2.3.0",
        "werkzeug>=2.3.0",
        "httpx",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-xdist>=3.5.0",
            "pytest-cov>=4.1.0",
            "black",
            "isort",
            "mypy",
        ],
        "web": [
            "streamlit>=1.31.0",
        ],
    },
    python_requires=">=3.11",
    package_data={
        "amphilagus": ["templates/*", "static/*", "static/css/*", "static/js/*", "static/img/*"],
    },
    entry_points={
        "console_scripts": [
            "amphilagus-web=amphilagus.web_app:run_app",
        ],
    },
    author="Amphilagus Team",
    author_email="example@example.com",
    description="Project management for Haystack RAG Assistant",
    long_description=io.open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/amphilagus",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 