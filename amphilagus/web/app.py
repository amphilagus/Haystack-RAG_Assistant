"""
Web application for Amphilagus project management.
"""
import os
from flask import Flask

from .. import config
from .. import manager
from ..logger import get_logger

from .routes import register_blueprints

# 配置日志
logger = get_logger('web_app')
logger.info("初始化Web应用")

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
    
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_replace_in_production')
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload
    app.config['UPLOAD_FOLDER'] = config.RAW_FILES_PATH
    
    # 初始化助手存储
    app.config['agents'] = {}
    
    # 记录Flask应用配置
    logger.debug(f"Flask app initialized with UPLOAD_FOLDER: {app.config['UPLOAD_FOLDER']}")
    logger.debug(f"Flask app MAX_CONTENT_LENGTH: {app.config['MAX_CONTENT_LENGTH']} bytes")
    
    # 注册所有Blueprint
    register_blueprints(app)
    
    # 注册请求前处理器
    @app.before_request
    def before_request():
        # 确保配置和目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

def run_app(host='0.0.0.0', port=5000, debug=False):
    """运行Web应用"""
    app = create_app()
    # 创建实例路径用于临时文件
    os.makedirs(app.instance_path, exist_ok=True)
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_app(debug=True) 