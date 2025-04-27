#!/usr/bin/env python
"""
Script to run the Amphilagus Web App.
"""
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the Amphilagus Web App')
    parser.add_argument('--log-level', 
                        type=str, 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO',
                        help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--workspace-dir', 
                        type=str, 
                        default=os.getcwd(),
                        help='工作空间目录路径，用于存储数据文件和配置')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    # 处理并设置工作空间目录
    workspace_dir = Path(args.workspace_dir).resolve()
    os.environ['AMPHILAGUS_WORKSPACE'] = str(workspace_dir)
    print(f"工作空间目录: {workspace_dir}")
    
    # 确保工作空间目录存在
    if not workspace_dir.exists():
        os.makedirs(workspace_dir, exist_ok=True)
        print(f"已创建工作空间目录: {workspace_dir}")
    
    # Set LOG_LEVEL environment variable
    if args.debug:
        os.environ['LOG_LEVEL'] = 'DEBUG'
    else:
        os.environ['LOG_LEVEL'] = args.log_level
    print(f"日志级别: {os.environ['LOG_LEVEL']}")

    from amphilagus.web_app import app

    # Add current year for footer copyright
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    # Run the app with the provided arguments
    app.run(host=args.host, port=args.port, debug=args.debug) 