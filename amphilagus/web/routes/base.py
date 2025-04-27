"""
基础路由模块，包含首页等通用路由
"""
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from ... import config

# 创建Blueprint
base_bp = Blueprint('base', __name__)

@base_bp.route('/')
def index():
    """首页路由 - 显示炫酷的3D动画首页"""
    now = datetime.datetime.now()
    return render_template('home.html', now=now)

@base_bp.route('/reload_config')
def reload_config():
    """重新加载配置文件"""
    import os
    import json
    from ...logger import get_logger
    logger = get_logger('web_app')
    logger.info("收到重新加载配置文件请求")
    
    try:
        # 记录当前配置的相关信息（用于前后对比）
        md_config_before = len(config.MD_CLEANER_CONFIG.keys()) if hasattr(config, 'MD_CLEANER_CONFIG') else 0
        title_config_before = len(config.TITLE_EXTRACTOR_CONFIG.keys()) if hasattr(config, 'TITLE_EXTRACTOR_CONFIG') else 0
        
        # 重新加载MD清理配置
        if os.path.exists(config.MD_CLEANER_CONFIG_PATH):
            with open(config.MD_CLEANER_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config.MD_CLEANER_CONFIG = json.load(f)
                logger.info(f"已重新加载MD清理配置文件: {config.MD_CLEANER_CONFIG_PATH}")
                # 在调试级别输出完整的配置内容
                logger.debug(f"MD_CLEANER_CONFIG完整内容: {json.dumps(config.MD_CLEANER_CONFIG, ensure_ascii=False, indent=2)}")
        else:
            logger.error(f"MD清理配置文件不存在: {config.MD_CLEANER_CONFIG_PATH}")
            flash(f"MD清理配置文件不存在: {config.MD_CLEANER_CONFIG_PATH}", "danger")
            return redirect(request.referrer or url_for('base.index'))
        
        # 重新加载标题提取配置
        if os.path.exists(config.TITLE_EXTRACTOR_CONFIG_PATH):
            with open(config.TITLE_EXTRACTOR_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config.TITLE_EXTRACTOR_CONFIG = json.load(f)
                logger.info(f"已重新加载标题提取配置文件: {config.TITLE_EXTRACTOR_CONFIG_PATH}")
                # 在调试级别输出完整的配置内容
                logger.debug(f"TITLE_EXTRACTOR_CONFIG完整内容: {json.dumps(config.TITLE_EXTRACTOR_CONFIG, ensure_ascii=False, indent=2)}")
        else:
            logger.error(f"标题提取配置文件不存在: {config.TITLE_EXTRACTOR_CONFIG_PATH}")
            flash(f"标题提取配置文件不存在: {config.TITLE_EXTRACTOR_CONFIG_PATH}", "danger")
            return redirect(request.referrer or url_for('base.index'))
        
        # 验证配置文件格式
        if "default" not in config.TITLE_EXTRACTOR_CONFIG.get("first_non_empty", {}).get("journals", {}):
            error_msg = "标题提取配置文件缺少 'first_non_empty.journals.default' 策略"
            logger.error(error_msg)
            flash(error_msg, "danger")
            return redirect(request.referrer or url_for('base.index'))
        
        # 记录配置变化
        md_config_after = len(config.MD_CLEANER_CONFIG.keys())
        title_config_after = len(config.TITLE_EXTRACTOR_CONFIG.keys())
        
        # 显示成功信息以及配置变化情况
        success_msg = f"配置文件已重新加载。MD清理配置: {md_config_before} → {md_config_after}, 标题提取配置: {title_config_before} → {title_config_after}"
        logger.info(success_msg)
        flash(success_msg, "success")
        
    except Exception as e:
        error_msg = f"重新加载配置文件时出错: {str(e)}"
        logger.error(error_msg)
        flash(error_msg, "danger")
    
    # 重定向回之前的页面或首页
    return redirect(request.referrer or url_for('base.index'))

# 添加日期格式化过滤器
@base_bp.app_template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    """格式化日期时间"""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(format)

def find_backup_files_by_title(title):
    """
    通过标题查找backup_files文件夹中可能匹配的文件
    
    Args:
        title: 文档标题
        
    Returns:
        找到的文件名（如果存在），否则返回None
    """
    import os
    import re
    
    # 如果目录不存在，返回None
    if not os.path.exists(config.BACKUP_FILES_PATH):
        return None
    
    # 将标题转换为可能的文件名模式（移除特殊字符）
    title_pattern = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
    
    # 查找匹配的文件
    matching_files = []
    for filename in os.listdir(config.BACKUP_FILES_PATH):
        file_base = os.path.splitext(filename)[0]
        # 两种匹配方式：1. 正则表达式模糊匹配 2. 标题是文件名的一部分
        if (re.search(title_pattern, file_base, re.IGNORECASE) or 
            title.lower() in file_base.lower().replace('_', ' ')):
            matching_files.append(filename)
    
    # 如果找到匹配的文件，返回第一个
    if matching_files:
        return matching_files[0]
    
    return None 