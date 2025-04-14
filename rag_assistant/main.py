"""
Main Entry Point Module

This module serves as the main entry point for the RAG assistant application.
It can run either the command-line interface or the web interface.
"""

import argparse
import sys
import os
from dotenv import load_dotenv

# 尝试多种方式加载环境变量
def load_api_key():
    """
    尝试多种方式加载API密钥，确保在Windows环境下也能正常工作
    
    Returns:
        str or None: API密钥，如果未找到则返回None
    """
    # 首先尝试直接从环境变量获取
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # 尝试加载.env文件
    load_dotenv(override=True)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # 尝试从.env文件直接读取
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(current_dir, '.env')
        if os.path.isfile(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY'):
                        api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                        # 手动设置环境变量，确保其他模块能读取到
                        os.environ["OPENAI_API_KEY"] = api_key
                        return api_key
    except Exception as e:
        print(f"Warning: Failed to read .env file directly: {e}")
    
    return None

def main():
    """Main entry point for the application."""
    # 先加载API密钥
    api_key = load_api_key()
    if not api_key:
        print("Warning: API key not found. You need to provide it via the --api-key parameter or set it in the .env file")
    
    parser = argparse.ArgumentParser(
        description="Local Knowledge Base RAG Assistant",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "--interface",
        type=str,
        choices=["cli", "web"],
        default="cli",
        help="Interface to run (cli or web)"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API key (if not set as environment variable)"
    )
    
    args, remaining_args = parser.parse_known_args()
    
    # 如果通过命令行提供了API密钥，设置环境变量
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
        print("Using API key provided via command line")
    
    if args.interface == "cli":
        # Run the CLI
        sys.argv = [sys.argv[0]] + remaining_args
        from cli import main as cli_main
        cli_main()
    else:
        # Run the web interface
        import subprocess
        import web_app
        web_app_path = web_app.__file__
        
        # 构建streamlit命令
        cmd = ["streamlit", "run", web_app_path]
        if remaining_args:
            cmd.extend(remaining_args)
            
        # 运行streamlit
        print("Starting Streamlit web interface...")
        subprocess.run(cmd)

if __name__ == "__main__":
    main() 