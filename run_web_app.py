#!/usr/bin/env python
"""
Script to run the Amphilagus Web App.
"""
import sys
import os
from datetime import datetime

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from amphilagus.web_app import app, ensure_base_tags

if __name__ == "__main__":
    # 确保基础标签存在
    ensure_base_tags()
    
    # Add current year for footer copyright
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True) 