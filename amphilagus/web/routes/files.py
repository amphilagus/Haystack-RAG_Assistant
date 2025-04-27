"""
文件管理相关路由模块
"""
import os
import tempfile
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename

from ... import config
from ... import manager
from ...logger import get_logger

# 配置日志
logger = get_logger('web_app')

# 创建Blueprint
files_bp = Blueprint('files', __name__, url_prefix='/files')

@files_bp.route('/')
def list_files():
    """列出所有文件"""
    files = manager.file.list_files()
    # 传递BASE_TAGS到模板用于前端过滤
    return render_template('files.html', files=files, filter_tags=None, exact=False, base_tag_names=list(config.BASE_TAGS.keys()))

@files_bp.route('/filter', methods=['GET'])
def filter_files():
    """根据标签过滤文件"""
    tags = request.args.getlist('tags')
    exact = request.args.get('exact', 'false').lower() == 'true'
    
    # 保持向后兼容性 - 如果使用旧格式的tag参数
    tag_name = request.args.get('tag')
    if tag_name and not tags:
        tags = [tag_name]
    
    if not tags:
        # 没有标签，显示所有文件
        files = manager.file.list_files()
    elif len(tags) == 1:
        # 单个标签过滤，使用现有方法
        files = manager.file.get_files_by_tag(tags[0], include_subclasses=not exact)
    else:
        # 多个标签过滤 - 使用文件名（可哈希）而不是Metadata对象（不可哈希）
        
        # 获取所有文件作为参考集
        all_files = {file.filename: file for file in manager.file.list_files()}
        
        # 获取第一个标签的文件名集合
        first_tag_files = set(file.filename for file in 
                             manager.file.get_files_by_tag(tags[0], include_subclasses=not exact))
        
        # 与其他标签文件名集合求交集
        matching_filenames = first_tag_files
        for tag in tags[1:]:
            tag_filenames = set(file.filename for file in 
                               manager.file.get_files_by_tag(tag, include_subclasses=not exact))
            matching_filenames = matching_filenames.intersection(tag_filenames)
        
        # 转换回Metadata对象列表
        files = [all_files[filename] for filename in matching_filenames if filename in all_files]
    
    # 传递BASE_TAGS到模板用于前端过滤
    return render_template('files.html', files=files, filter_tags=tags, exact=exact, base_tag_names=list(config.BASE_TAGS.keys()))

@files_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """文件上传页面与处理"""
    if request.method == 'GET':
        # 获取标签列表用于显示
        tags = manager.file.list_tags()
        recent_tasks = manager.task.get_recent_tasks(5)
        return render_template('upload.html', tags=tags, recent_tasks=recent_tasks)
    
    # 处理AJAX和表单上传
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        files = request.files.getlist('files[]')
        
        if not files or files[0].filename == '':
            error_msg = '未选择文件'
            if is_ajax:
                return jsonify({"success": False, "message": error_msg})
            flash(error_msg, 'error')
            return redirect(url_for('files.upload_file'))
        
        # 获取表单数据
        tags = request.form.get('tags', '')
        description = request.form.get('description', '')
        
        # 获取PDF处理选项，默认值改为'on'
        use_llm = request.form.get('use_llm', 'on')
        clean_md = request.form.get('clean_md', 'off')
        
        # 处理标签
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
        tag_list = [tag for tag in tag_list if tag]  # 移除空标签
        
        # 将文件保存到临时位置，然后创建后台任务
        task_files = []
        for file in files:
            if file and file.filename:
                # 安全处理文件名
                filename = secure_filename(file.filename)
                
                # 创建临时目录（如果不存在）
                temp_dir = os.path.join(tempfile.gettempdir(), 'amphilagus_uploads')
                os.makedirs(temp_dir, exist_ok=True)
                
                # 临时文件路径
                temp_path = os.path.join(temp_dir, f"{filename}")
                
                # 保存到临时位置
                file.save(temp_path)
                
                # 添加到任务文件列表
                task_files.append({
                    "filename": filename,
                    "temp_path": temp_path,
                    "size": os.path.getsize(temp_path)
                })
        
        # 创建上传任务
        task = manager.task.create_task(
            task_type='file_upload',
            files=task_files,
            params={
                'tags': tag_list,
                'description': description,
                'use_llm': use_llm,
                'clean_md': clean_md
            }
        )
        
        # 构建响应消息
        if is_ajax:
            return jsonify({
                "success": True,
                "message": f"已创建上传任务，包含 {len(task_files)} 个文件",
                "task_id": task.task_id
            })
        else:
            flash(f"已创建上传任务，包含 {len(task_files)} 个文件", 'success')
            return redirect(url_for('tasks.view_tasks'))
            
    except Exception as e:
        error_msg = f"创建上传任务时出错: {str(e)}"
        logger.error(error_msg)
        import traceback
        traceback.print_exc()
        
        if is_ajax:
            return jsonify({"success": False, "message": error_msg})
        
        flash(error_msg, 'error')
        return redirect(url_for('files.upload_file'))

@files_bp.route('/<filename>/delete', methods=['POST'])
def delete_file(filename):
    """删除文件"""
    if manager.file.delete_file(filename):
        flash(f'文件 {filename} 已成功删除')
    else:
        flash(f'删除文件 {filename} 时出错')
    
    return redirect(url_for('files.list_files'))

@files_bp.route('/batch_delete', methods=['POST'])
def batch_delete_files():
    """批量删除文件"""
    filenames = request.form.getlist('filenames[]')
    
    if not filenames:
        flash('未选择任何文件', 'warning')
        return redirect(url_for('files.list_files'))
    
    success_count = 0
    failed_files = []
    
    for filename in filenames:
        try:
            if manager.file.delete_file(filename):
                success_count += 1
            else:
                failed_files.append(filename)
        except Exception as e:
            logger.error(f"删除文件 {filename} 时出错: {str(e)}")
            failed_files.append(filename)
    
    # 显示结果消息
    if success_count > 0:
        flash(f'成功删除 {success_count} 个文件', 'success')
    
    if failed_files:
        flash(f'无法删除以下文件: {", ".join(failed_files)}', 'error')
    
    return redirect(url_for('files.list_files'))

@files_bp.route('/batch_embed', methods=['POST'])
def batch_embed_files():
    """批量嵌入文件到向量数据库"""
    try:
        # 获取表单数据
        collection_name = request.form.get('collection_name')
        chunk_size = int(request.form.get('chunk_size', 1000))
        chunk_overlap = int(request.form.get('chunk_overlap', 200))
        check_duplicates = request.form.get('check_duplicates') == 'on'
        filenames = request.form.getlist('filenames[]')
        
        # 获取新增参数
        create_collection = request.form.get('create_collection') == 'on'
        embedding_model = request.form.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
        reset_collection = request.form.get('reset_collection') == 'on'
        new_collection_name = request.form.get('new_collection_name', '')
        
        # 如果是创建新集合，使用新集合名称
        if create_collection and new_collection_name:
            collection_name = new_collection_name
        
        # 验证输入
        if not collection_name:
            flash('请选择或输入一个向量数据库集合名称', 'error')
            return redirect(url_for('files.list_files'))
        
        if not filenames:
            flash('未选择任何文件', 'warning')
            return redirect(url_for('files.list_files'))
        
        # 获取完整的文件路径
        file_paths = []
        for filename in filenames:
            file_path = os.path.join(config.RAW_FILES_PATH, filename)
            if os.path.exists(file_path):
                file_paths.append(file_path)
            else:
                flash(f'文件不存在: {filename}', 'warning')
        
        if not file_paths:
            flash('没有找到可处理的文件', 'error')
            return redirect(url_for('files.list_files'))
        
        # 创建批量嵌入任务，而不是直接处理
        task = manager.task.create_task(
            task_type='batch_embed',
            params={
                'collection_name': collection_name,
                'chunk_size': chunk_size,
                'chunk_overlap': chunk_overlap,
                'check_duplicates': check_duplicates,
                'file_paths': file_paths,
                'filenames': filenames,  # 保存原始文件名用于显示
                'create_collection': create_collection,  # 是否创建新集合
                'embedding_model': embedding_model,  # 嵌入模型
                'reset_collection': reset_collection  # 是否重置现有集合
            }
        )
        
        # 显示任务创建成功
        message = f'批量嵌入任务已创建，将在后台处理 {len(file_paths)} 个文件'
        if create_collection:
            message += f'，并{"重置" if reset_collection else "创建"}向量集合 "{collection_name}"'
        
        flash(message, 'success')
        
        # 重定向到任务查看页面
        return redirect(url_for('tasks.view_task', task_id=task.task_id))
        
    except Exception as e:
        logger.error(f"创建批量嵌入任务时出错: {str(e)}")
        flash(f'创建批量嵌入任务时出错: {str(e)}', 'error')
        return redirect(url_for('files.list_files'))

@files_bp.route('/<filename>/tags', methods=['GET', 'POST'])
def manage_file_tags(filename):
    """管理文件标签"""
    file_metadata = manager.file.get_file_metadata(filename)
    
    if not file_metadata:
        flash(f'文件 {filename} 不存在')
        return redirect(url_for('files.list_files'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        tags = request.form.get('tags', '').split(',')
        tags = [tag.strip() for tag in tags if tag.strip()]
        
        if action == 'add' and tags:
            if manager.file.add_tags_to_file(filename, tags):
                flash(f'已向 {filename} 添加标签')
            else:
                flash(f'向 {filename} 添加标签时出错')
        
        elif action == 'remove' and tags:
            if manager.file.remove_tags_from_file(filename, tags):
                flash(f'已从 {filename} 移除标签')
            else:
                flash(f'从 {filename} 移除标签时出错')
        
        return redirect(url_for('files.manage_file_tags', filename=filename))
    
    # GET请求
    all_tags = manager.file.list_tags()
    return render_template('file_tags.html', file=file_metadata, all_tags=all_tags)

@files_bp.route('/<filename>/details')
def file_details(filename):
    """通过重定向在新页面查看文件"""
    file_metadata = manager.file.get_file_metadata(filename)
    
    if not file_metadata:
        flash(f'文件 {filename} 不存在')
        return redirect(url_for('files.list_files'))
    
    # 重定向到新的文件查看页面路由
    return redirect(url_for('files.view_backup_files', filename=filename))

@files_bp.route('/<filename>/view')
def view_backup_files(filename):
    """在新页面中查看备份文件"""
    # 获取文件名（不含扩展名）
    filename_no_ext = os.path.splitext(filename)[0]
    
    # 查找同名文件（可能有不同的扩展名）
    matching_files = []
    if os.path.exists(config.BACKUP_FILES_PATH):
        for f in os.listdir(config.BACKUP_FILES_PATH):
            if os.path.splitext(f)[0] == filename_no_ext:
                matching_files.append(f)
    
    # 如果找到多个文件，报错
    if len(matching_files) > 1:
        flash(f'在backup_files中找到多个同名文件: {", ".join(matching_files)}', 'error')
        return redirect(url_for('files.list_files'))
    
    # 如果没有找到文件，显示错误
    if not matching_files:
        flash(f'在backup_files中未找到{filename_no_ext}的文件', 'error')
        return redirect(url_for('files.list_files'))
    
    # 构建完整文件路径
    file_path = os.path.join(config.BACKUP_FILES_PATH, matching_files[0])
    backup_filesname = matching_files[0]
    
    # 发送文件
    try:
        return send_file(file_path, as_attachment=False)
    except Exception as e:
        flash(f'打开文件时出错: {str(e)}', 'error')
        return redirect(url_for('files.list_files'))

@files_bp.route('/<filename>/update_description', methods=['POST'])
def update_description(filename):
    """更新文件描述"""
    file_metadata = manager.file.get_file_metadata(filename)
    
    if not file_metadata:
        flash(f'文件 {filename} 不存在')
        return redirect(url_for('files.list_files'))
    
    new_description = request.form.get('description', '').strip()
    
    try:
        # 更新描述
        file_metadata.description = new_description
        manager.file._save_metadata()
        flash(f'文件描述已更新')
    except Exception as e:
        flash(f'更新描述时出错: {str(e)}')
    
    return redirect(url_for('files.file_details', filename=filename))

@files_bp.route('/<filename>/rename', methods=['POST'])
def rename_file(filename):
    """重命名文件"""
    logger.info(f"收到重命名文件请求: {filename}")
    
    new_filename = request.form.get('new_filename', '').strip()
    
    if not new_filename:
        flash('新文件名不能为空', 'error')
        return redirect(url_for('files.list_files'))
    
    # 保留原文件扩展名
    old_ext = os.path.splitext(filename)[1]
    new_ext = os.path.splitext(new_filename)[1]
    
    # 如果新文件名没有扩展名，使用原文件的扩展名
    if not new_ext and old_ext:
        new_filename = f"{new_filename}{old_ext}"
        logger.debug(f"添加原文件扩展名: {new_filename}")
    
    # 验证新文件名
    if not new_filename or not new_filename.strip():
        flash('新文件名不能为空', 'error')
        return redirect(url_for('files.list_files'))
    
    # 确保文件名有效且扩展名相同
    if not config.allowed_file(new_filename):
        flash('文件扩展名必须是允许的类型', 'error')
        return redirect(url_for('files.list_files'))
    
    # 文件重命名操作
    if manager.file.rename_file(filename, new_filename):
        flash(f'文件 {filename} 成功重命名为 {new_filename}', 'success')
    else:
        flash(f'重命名文件 {filename} 失败', 'error')
    
    return redirect(url_for('files.list_files'))

@files_bp.route('/batch_clean', methods=['POST'])
def batch_clean_files():
    """批量清洗文件路由"""
    logger.info("收到批量清洗文件请求")
    
    try:
        # 获取文件列表
        data = request.get_json()
        
        if not data or 'files' not in data or not data['files']:
            logger.warning("批量清洗请求中没有指定文件")
            return jsonify({
                'status': 'error',
                'message': '未指定要清洗的文件'
            })
            
        files = data['files']
        logger.info(f"批量清洗文件列表: {files}, 总数: {len(files)}")
        
        # 创建批量清洗任务
        task = manager.task.create_task(
            task_type='batch_clean',
            params={
                'files': files
            }
        )
        
        logger.info(f"创建了批量清洗任务: {task.task_id}")
        
        return jsonify({
            'status': 'success',
            'message': '批量清洗任务已创建',
            'task_id': task.task_id
        })
        
    except Exception as e:
        logger.error(f"批量清洗文件时发生错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'批量清洗出错: {str(e)}'
        }) 