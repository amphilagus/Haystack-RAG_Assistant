"""
路由模块初始化文件，用于注册所有Blueprint到Flask应用
"""
from flask import Flask

def register_blueprints(app: Flask):
    """
    注册所有Blueprint到Flask应用
    
    Args:
        app: Flask应用实例
    """
    from .files import files_bp
    from .database import database_bp
    from .agent import agent_bp
    from .tasks import tasks_bp
    from .tags import tags_bp
    from .literature import literature_bp
    from .api import api_bp
    from .base import base_bp
    
    # 注册所有Blueprint
    app.register_blueprint(base_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(database_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(literature_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(api_bp) 