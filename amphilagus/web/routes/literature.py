"""
文献管理相关路由模块
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash

from ... import config
from ... import manager
from ...literature import Literature

# 创建Blueprint
literature_bp = Blueprint('literature', __name__, url_prefix='/literature')

@literature_bp.route('/')
def list_literature():
    """列出所有文献"""
    # 加载所有文献
    literature_list = Literature.list_all()
    # 通过BASE_TAGS传递基础标签类型给前端，用于过滤
    return render_template('literature.html', literature=literature_list, filter_tags=None, exact=False, base_tag_names=list(config.BASE_TAGS.keys()))

@literature_bp.route('/filter', methods=['GET'])
def filter_literature():
    """根据标签筛选文献"""
    tags = request.args.getlist('tags')
    exact = request.args.get('exact', 'false').lower() == 'true'
    
    # 保持向后兼容性 - 如果使用旧格式的tag参数
    tag_name = request.args.get('tag')
    if tag_name and not tags:
        tags = [tag_name]
    
    # 加载所有文献
    all_literature = Literature.list_all()
    
    if not tags:
        # 没有标签，显示所有文献
        filtered_literature = all_literature
    else:
        # 按标签过滤文献
        filtered_literature = []
        for lit in all_literature:
            # 针对每篇文献，检查它是否具有所有指定的标签
            if exact:
                # 精确匹配：文献必须具有所有指定的标签
                if all(tag in lit.tags for tag in tags):
                    filtered_literature.append(lit)
            else:
                # 非精确匹配：文献至少具有一个指定的标签
                if any(tag in lit.tags for tag in tags):
                    filtered_literature.append(lit)
    
    # 通过BASE_TAGS传递基础标签类型给前端，用于过滤
    return render_template('literature.html', literature=filtered_literature, filter_tags=tags, exact=exact, base_tag_names=list(config.BASE_TAGS.keys()))

@literature_bp.route('/sync', methods=['POST'])
def sync_literature_tags():
    """同步文献与文件系统中的标签"""
    try:
        # 获取所有文献
        literature_list = Literature.list_all()
        
        # 遍历每篇文献，加载标签并更新
        for lit in literature_list:
            # 从文件管理器中加载标签
            lit.load_tags_from_json(manager.file)
            # 根据标签更新文献属性
            lit.update_from_tags(manager.file)
            # 保存更新后的文献
            lit.save()
        
        flash('文献标签同步完成', 'success')
    except Exception as e:
        flash(f'同步文献标签时出错: {str(e)}', 'error')
    
    return redirect(url_for('literature.list_literature'))

@literature_bp.route('/update_files', methods=['POST'])
def update_literature_files():
    """将文献属性更新到文件标签"""
    try:
        # 获取所有文献
        literature_list = Literature.list_all()
        
        # 遍历每篇文献，更新文件标签
        success_count = 0
        for lit in literature_list:
            # 更新文件标签，自动创建不存在的标签
            if lit.update_file_tags(manager.file, auto_create_tags=True):
                success_count += 1
        
        flash(f'已更新 {success_count} 篇文献的文件标签', 'success')
    except Exception as e:
        flash(f'更新文件标签时出错: {str(e)}', 'error')
    
    return redirect(url_for('literature.list_literature')) 