"""
Logger Module for RAG Assistant

提供统一的日志记录功能，支持文件和控制台输出。
此模块可以在任何地方导入，不依赖于服务器启动。
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import time

log_level_map = {
    'DEBUG': 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40, 
    'CRITICAL': 50
}

from dotenv import load_dotenv

# 直接在脚本开头加载环境变量
load_dotenv(override=True)
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

def setup_logger(name="default", 
                level=None, 
                log_to_file=True, 
                log_to_console=True,
                log_dir=None):
    """
    设置并返回一个配置好的logger实例
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        log_to_file: 是否将日志写入文件
        log_to_console: 是否将日志输出到控制台
        log_dir: 日志文件目录，默认为项目根目录下的logs
        
    Returns:
        已配置的logger实例
    """
    logger = logging.getLogger(name)
    
    # 避免重复配置
    if logger.handlers:
        return logger
    
    if level is None:
        logger.setLevel(log_level_map.get(LOG_LEVEL, 20))
    else:
        logger.setLevel(level)
    
    # 创建标准的日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 添加控制台处理器
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 添加文件处理器
    if log_to_file:
        # 确定日志目录
        if log_dir is None:
            # 尝试找到项目的根目录
            module_dir = os.path.dirname(os.path.abspath(__file__))  # rag_assistant目录
            project_root = os.path.dirname(module_dir)  # 项目根目录
            log_dir = os.path.join(project_root, "logs")
        
        # 创建日志目录（如果不存在）
        os.makedirs(log_dir, exist_ok=True)
        
        # 设置日志文件路径
        log_file = os.path.join(log_dir, f"{name}.log")
        
        # 创建旋转文件处理器
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,           # 保存5个备份
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# 创建默认的主日志记录器
logger = setup_logger()

def get_logger(name=None):
    """
    获取一个命名的日志记录器
    
    Args:
        name: 日志记录器名称，如果为None，则使用default
        
    Returns:
        命名的logger实例
    """
    if name is None:
        return logger
    
    # 使用模块名称作为日志记录器名称前缀
    return setup_logger(name=name)

# 记录日志系统启动信息
logger.info(f"Amphilagus logging system initialized at {time.strftime('%Y-%m-%d %H:%M:%S')}")
logger.info(f"Python version: {sys.version}")
logger.info(f"Log files location: {os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs'))}")

# 记录环境编码信息（帮助调试编码问题）
logger.debug(f"System encoding: {sys.getdefaultencoding()}")
logger.debug(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'not set')}")
logger.debug(f"File system encoding: {sys.getfilesystemencoding()}") 