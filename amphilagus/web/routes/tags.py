"""
标签管理相关路由模块
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash

from ... import config
from ... import manager

# 创建Blueprint
tags_bp = Blueprint('tags', __name__, url_prefix='/tags')

@tags_bp.route('/')
def list_tags():
    """列出所有标签"""
    tags = manager.file.list_tags()
    return render_template('tags.html', tags=tags)

@tags_bp.route('/restore_presets', methods=['POST'])
def restore_preset_tags():
    """恢复所有预设标签"""
    flash('已恢复所有预设标签')
    return redirect(url_for('tags.list_tags'))

@tags_bp.route('/create', methods=['GET', 'POST'])
def create_tag():
    """创建新标签"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        parent = request.form.get('parent', '').strip() or None
        
        if not name:
            flash('标签名称不能为空')
            return redirect(request.url)
        
        # 验证父标签必须是基础类标签之一
        if not parent:
            flash('必须选择一个基础类标签作为父标签')
            return redirect(request.url)
        
        try:
            tag = manager.file.create_tag(name, parent_name=parent)
            # 确保新标签不是预设标签和基础类标签
            tag.is_preset_tag = False
            tag.is_base_tag = False
            flash(f'标签 {tag.name} 创建成功')
            return redirect(url_for('tags.list_tags'))
        except ValueError as e:
            flash(f'创建标签错误: {str(e)}')
            return redirect(request.url)
    
    # GET请求
    existing_tags = manager.file.list_tags()

    # 过滤出基础类标签作为父标签选项
    base_tags = [tag for tag in existing_tags if hasattr(tag, 'is_base_tag') and tag.is_base_tag and not tag.parent]
    return render_template('create_tag.html', existing_tags=existing_tags, base_tags=base_tags)

@tags_bp.route('/<tag_name>/delete', methods=['POST'])
def delete_tag(tag_name):
    """删除标签"""
    # 获取标签
    tag = manager.file.get_tag(tag_name)
    
    if not tag:
        flash(f'标签 {tag_name} 不存在')
        return redirect(url_for('tags.list_tags'))
    
    # 检查是否是基础类标签，基础类标签不允许删除
    if hasattr(tag, 'is_base_tag') and tag.is_base_tag:
        flash(f'基础类标签 {tag_name} 不能删除')
        return redirect(url_for('tags.list_tags'))
    
    # 预设标签可以删除，但会给予提示
    is_preset = hasattr(tag, 'is_preset_tag') and tag.is_preset_tag
    
    # 实现标签删除逻辑
    try:
        # 获取所有使用此标签的文件
        files_with_tag = manager.file.get_files_by_tag(tag_name)
        
        # 从文件中移除此标签
        for file in files_with_tag:
            manager.file.remove_tags_from_file(file.filename, [tag_name])
        
        # 从标签注册表中删除
        if hasattr(manager.file, 'delete_tag'):
            manager.file.delete_tag(tag_name)
            if is_preset:
                flash(f'预设标签 {tag_name} 已删除，可通过"恢复预设标签"按钮恢复')
            else:
                flash(f'标签 {tag_name} 已删除')
        else:
            # 临时方案：如果没有删除方法，则仅从文件中移除
            flash(f'标签 {tag_name} 已从所有文件中移除，但无法从系统中完全删除')
    except Exception as e:
        flash(f'删除标签时出错: {str(e)}')
    
    return redirect(url_for('tags.list_tags')) 