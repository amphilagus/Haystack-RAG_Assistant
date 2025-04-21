"""
Web application for Amphilagus project management.
"""
import os
import json
import time
import shutil
import datetime
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, send_file
from werkzeug.utils import secure_filename

from .main import Amphilagus
from .file_manager import Tag
from .task_manager import TaskManager

# 导入PDF处理模块
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag_assistant.utils.pdf_converter.pdf_to_markdown import convert_pdf_to_markdown
from rag_assistant.utils.md_cleaner.md_cleaner import clean_markdown

# 导入本地模块
from .database_manager import DatabaseManager

# 添加RAG Assistant相关导入
try:
    from rag_assistant.utils.pdf_converter.pdf_to_markdown import convert_pdf_to_markdown
    from rag_assistant.document_loader import load_documents
    from rag_assistant.rag_pipeline import RAGPipeline
    from rag_assistant.collection_metadata import get_embedding_model
    from dotenv import load_dotenv
    RAG_IMPORT_SUCCESS = True
except ImportError:
    print("Warning: RAG Assistant modules not found. Vector database functions will be limited.")
    RAG_IMPORT_SUCCESS = False

# 获取API密钥的函数
def get_api_key():
    """
    Try to get API key from various sources
    
    Returns:
        API key or None
    """
    # Try from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # Try to load from .env file
    load_dotenv(override=True)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # Try to read directly from .env file
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(current_dir, '.env')
        if os.path.isfile(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY'):
                        api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                        # Manually set environment variable
                        os.environ["OPENAI_API_KEY"] = api_key
                        return api_key
    except Exception as e:
        print(f"Error reading .env file directly: {e}")
    
    return None

# 配置路径 - 正确的配置文件路径
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          'rag_assistant/utils/md_cleaner/md_cleaner_config.json')

# 设置ChromaDB路径
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'chroma_db')

# 尝试加载配置文件
try:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            MD_CLEANER_CONFIG = json.load(f)
    else:
        print(f"Warning: MD cleaner config file not found at {CONFIG_PATH}")
        MD_CLEANER_CONFIG = {}
except Exception as e:
    print(f"Error loading MD cleaner config: {str(e)}")
    MD_CLEANER_CONFIG = {}

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_replace_in_production')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'raw_data')

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'md', 'docx', 'html', 'csv', 'xlsx', 'json', 'xml'}

def allowed_file(filename):
    """检查文件是否有允许的扩展名"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 基础类标签定义
BASE_TAGS = {
    "期刊类型": "对文献来源期刊的分类",
    "发表时间": "文献发表的年份或时间段",
    "研究领域": "文献所属的研究方向或领域",
    "评分": "文献的评分或重要性分级",
    "其他": "用户自定义分类，可用于特殊目的或临时分类"
}

# 预设次级标签定义
PRESET_SUBTAGS = {
    "期刊类型": [
        "Nature", "Science", "JCTC", "npj Computational Materials", "PRL", "PRE"
    ],
    "发表时间": [
        "2025年", "2024年", "2023年", "2022年", "2021年", "2020年", "2019年", "2018年"
    ],
    "研究领域": [
        "量子化学", "分子动力学", "机器学习"
    ],
    "评分": [
        "五星 (必读)", "四星 (重要)", "三星 (有用)", "二星 (一般)", "一星 (参考)"
    ]
}

# Initialize the Amphilagus instance
amphilagus = Amphilagus()

# 初始化数据库管理器
db_manager = DatabaseManager(chroma_db_path=CHROMA_DB_PATH)

# 初始化任务管理器
task_manager = None

# 确保基础类标签和预设次级标签存在
def ensure_base_tags():
    existing_tags = {tag.name: tag for tag in amphilagus.list_tags()}
    
    # 创建/更新基础类标签
    for tag_name, description in BASE_TAGS.items():
        if tag_name not in existing_tags:
            tag = amphilagus.create_tag(tag_name)
            # 标记为基础类标签，不可删除
            tag.is_base_tag = True
            # 不是预设标签
            if hasattr(tag, 'is_preset_tag'):
                tag.is_preset_tag = False
        else:
            # 确保现有标签也被标记为基础类
            existing_tags[tag_name].is_base_tag = True
            # 不是预设标签
            if hasattr(existing_tags[tag_name], 'is_preset_tag'):
                existing_tags[tag_name].is_preset_tag = False
    
    # 收集所有当前配置的预设标签名字（扁平列表）
    current_preset_tags = []
    for parent_name, subtags in PRESET_SUBTAGS.items():
        current_preset_tags.extend(subtags)
    
    # 先将所有标签的预设标签属性设置为False，除非它们在当前的预设列表中
    for tag_name, tag in existing_tags.items():
        # 确保所有标签都有is_preset_tag属性
        if not hasattr(tag, 'is_preset_tag'):
            tag.is_preset_tag = False
            
        # 如果标签在当前预设列表中，标记为预设
        if tag_name in current_preset_tags:
            tag.is_preset_tag = True
        
        # 确保基础类标签不是预设标签
        if tag.is_base_tag and not tag.parent:
            tag.is_preset_tag = False
    
    # 创建/更新当前配置的预设次级标签
    for parent_name, subtags in PRESET_SUBTAGS.items():
        # 确保父标签存在
        if parent_name not in existing_tags:
            continue
            
        parent_tag = existing_tags[parent_name]
        
        for subtag_name in subtags:
            # 尝试创建标签（如果已存在则获取现有标签）
            if subtag_name in existing_tags:
                subtag = existing_tags[subtag_name]
                # 标记为预设标签
                subtag.is_preset_tag = True
                # 不是基础类标签（可删除）
                subtag.is_base_tag = False
                # 确保父标签关系正确（可能是从其他类别转移过来的）
                subtag.parent = parent_tag
            else:
                # 创建新的预设次级标签
                try:
                    subtag = amphilagus.create_tag(subtag_name, parent_name=parent_name)
                    # 标记为预设标签
                    subtag.is_preset_tag = True
                    # 不是基础类标签（可删除）
                    subtag.is_base_tag = False
                except ValueError:
                    # 如果标签已存在但命名不同，则跳过
                    continue
    
    # 保存更改
    amphilagus.file_manager._save_metadata()

# 移除 @app.before_first_request 装饰器，改为在应用启动前直接调用
# 在每个请求前执行初始化检查
@app.before_request
def before_request():
    global task_manager
    ensure_base_tags()
    
    # 延迟初始化任务管理器，确保amphilagus实例已经初始化
    if task_manager is None:
        task_manager = TaskManager.get_instance(amphilagus=amphilagus)
    
    # 配置默认日期格式
    if 'datetime' not in app.jinja_env.filters:
        app.jinja_env.filters['datetime'] = datetime.datetime.strftime

# RAG Assistant 相关路由

# 初始化会话状态
if 'rag_session' not in app.config:
    app.config['rag_session'] = {
        'messages': [],
        'query_history': [],
        'chat_history': [],
        'result_history': [],
        'last_retrieval_score': 0,
        'last_result': None,
        'document_store': app.config.get('DOCUMENT_STORE', 'inmemory'),
        'embedding_model': None,
        'llm_model': None,
        'prompt_template': 'balanced',
        'top_k': 10  # 默认top_k值
    }

@app.route('/rag_assistant')
def rag_assistant():
    """RAG Assistant页面路由"""
    if not RAG_IMPORT_SUCCESS:
        flash('未能导入RAG Assistant模块，请确保安装了所有依赖', 'error')
        return redirect(url_for('index'))
    
    # 检查环境变量中是否有API密钥
    api_key = get_api_key()
    if not api_key:
        flash('未找到环境变量中的OpenAI API密钥，请设置OPENAI_API_KEY环境变量', 'warning')
    
    # 获取可用集合
    collections = db_manager.list_collections()
    collection_names = [col["name"] for col in collections if col.get("exists_in_chroma", False)]
    
    # 获取当前集合信息
    current_collection = app.config['rag_session'].get('collection_name', 'documents')
    collection_info = None
    
    if current_collection in collection_names:
        try:
            chroma_client = db_manager.client
            if chroma_client:
                collection = chroma_client.get_collection(current_collection)
                collection_info = {"exists": True, "count": collection.count()}
        except Exception as e:
            app.logger.error(f"获取集合信息时出错: {str(e)}")
            collection_info = {"exists": False, "count": 0, "error": str(e)}
    
    # 准备模板变量
    template_vars = {
        'collections': collection_names,
        'current_collection': current_collection,
        'collection_info': collection_info,
        'current_model': app.config['rag_session'].get('current_model', 'gpt-4o-mini'),
        'current_template': app.config['rag_session'].get('prompt_template', 'balanced'),
        'top_k': app.config['rag_session'].get('top_k', 10),
        'chat_history': app.config['rag_session'].get('chat_history', []),
        'initialized': app.config['rag_session'].get('initialized', False)
    }
    
    return render_template('rag_assistant.html', **template_vars)

@app.route('/rag_assistant/config', methods=['POST'])
def rag_assistant_config():
    """处理RAG Assistant配置更新"""
    if not RAG_IMPORT_SUCCESS:
        flash('未能导入RAG Assistant模块，请确保安装了所有依赖', 'error')
        return redirect(url_for('rag_assistant'))
    
    # 检查环境变量中是否有API密钥
    api_key = get_api_key()
    if not api_key:
        flash('未找到环境变量中的OpenAI API密钥，请设置OPENAI_API_KEY环境变量', 'error')
        return redirect(url_for('rag_assistant'))
    
    # 获取表单数据
    collection_name = request.form.get('collection_name', 'documents')
    llm_model = request.form.get('llm_model', 'gpt-4o-mini')
    prompt_template = request.form.get('prompt_template', 'balanced')
    
    try:
        # 获取正确的嵌入模型
        embedding_model = get_embedding_model(collection_name)
        if not embedding_model:
            embedding_model = "sentence-transformers/all-MiniLM-L6-v2"  # 默认嵌入模型
        
        # 检查模型和模板是否更改
        model_changed = app.config['rag_session'].get('current_model') != llm_model
        template_changed = app.config['rag_session'].get('prompt_template') != prompt_template
        
        # 初始化RAG管道 - 使用默认top_k
        rag_pipeline = RAGPipeline(
            embedding_model=embedding_model,
            llm_model=llm_model,
            persist_dir=CHROMA_DB_PATH,
            collection_name=collection_name,
            prompt_template=prompt_template
        )
        
        # 更新会话状态
        app.config['rag_session']['rag_pipeline'] = rag_pipeline
        app.config['rag_session']['current_model'] = llm_model
        app.config['rag_session']['prompt_template'] = prompt_template
        app.config['rag_session']['collection_name'] = collection_name
        app.config['rag_session']['top_k'] = 10  # 设置默认top_k值
        app.config['rag_session']['initialized'] = True
        
        # 获取模型信息
        model_intro = rag_pipeline.get_model_introduction() if hasattr(rag_pipeline, 'get_model_introduction') else ""
        template_info = rag_pipeline.get_current_template_info() if hasattr(rag_pipeline, 'get_current_template_info') else {"name": prompt_template}
        
        # 构建成功消息
        message = ""
        if model_changed:
            message += f"模型已切换为 {llm_model}。"
        if template_changed:
            message += f"提示词模板已切换为{template_info.get('name', prompt_template)}。"
        
        if message:
            flash(message + model_intro, 'success')
        else:
            flash(f"RAG助手已成功初始化，使用{llm_model}模型和{template_info.get('name', prompt_template)}模板。{model_intro}", 'success')
        
    except Exception as e:
        app.logger.error(f"初始化RAG管道时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'初始化RAG助手时出错: {str(e)}', 'error')
    
    return redirect(url_for('rag_assistant'))

def find_backup_file_by_title(title):
    """
    通过标题查找backup_data文件夹中可能匹配的文件
    
    Args:
        title: 文档标题
        
    Returns:
        找到的文件名（如果存在），否则返回None
    """
    # 构建备份数据文件夹路径
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backup_data')
    
    # 如果目录不存在，返回None
    if not os.path.exists(backup_dir):
        return None
    
    # 将标题转换为可能的文件名模式（移除特殊字符）
    import re
    title_pattern = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
    
    # 查找匹配的文件
    matching_files = []
    for filename in os.listdir(backup_dir):
        file_base = os.path.splitext(filename)[0]
        # 两种匹配方式：1. 正则表达式模糊匹配 2. 标题是文件名的一部分
        if (re.search(title_pattern, file_base, re.IGNORECASE) or 
            title.lower() in file_base.lower().replace('_', ' ')):
            matching_files.append(filename)
    
    # 如果找到匹配的文件，返回第一个
    if matching_files:
        return matching_files[0]
    
    return None

@app.route('/rag_assistant/chat', methods=['POST'])
def rag_assistant_chat():
    """处理RAG Assistant聊天请求"""
    if not RAG_IMPORT_SUCCESS:
        flash('未能导入RAG Assistant模块，请确保安装了所有依赖', 'error')
        return redirect(url_for('rag_assistant'))
    
    # 检查是否已初始化
    if not app.config['rag_session'].get('initialized', False) or app.config['rag_session'].get('rag_pipeline') is None:
        flash('请先初始化RAG助手', 'warning')
        return redirect(url_for('rag_assistant'))
    
    # 获取用户查询
    user_query = request.form.get('user_query', '').strip()
    if not user_query:
        flash('请输入有效的问题', 'warning')
        return redirect(url_for('rag_assistant'))
    
    try:
        # 从表单获取top_k参数
        try:
            top_k = int(request.form.get('top_k', 10))
            if top_k < 1:
                top_k = 1
            elif top_k > 100:
                top_k = 100
        except (ValueError, TypeError):
            # 如果解析出错，使用默认值
            top_k = app.config['rag_session'].get('top_k', 10)
        
        # 获取是否显示参考文献的选项
        include_references = request.form.get('include_references') == 'on'
        
        # 记录用户消息
        user_message = {
            "role": "user",
            "content": user_query,
            "timestamp": datetime.datetime.now()
        }
        app.config['rag_session']['chat_history'].append(user_message)
        
        # 获取rag_pipeline
        rag_pipeline = app.config['rag_session']['rag_pipeline']
        
        # 生成回答，传递top_k和include_references参数
        result = rag_pipeline.get_answer(user_query, top_k=top_k, include_references=include_references)
        
        # 处理结果
        if isinstance(result, dict) and include_references:
            answer = result.get("answer", "")
            references = result.get("references", [])
            
            # 构建包含参考文献和链接的回答
            if references:
                references_html = "<br><br><hr><small><strong>参考文献:</strong><br>"
                for i, ref in enumerate(references, 1):
                    # 查找匹配的备份文件
                    backup_file = find_backup_file_by_title(ref)
                    if backup_file:
                        # 创建链接到备份文件
                        references_html += f'{i}. <a href="{url_for("view_backup_file", filename=backup_file)}" target="_blank">{ref}</a><br>'
                    else:
                        references_html += f"{i}. {ref}<br>"
                references_html += "</small>"
                answer_with_info = f"{answer}{references_html}<br><small class='text-muted'>检索文档数: {top_k}</small>"
            else:
                answer_with_info = f"{answer}<br><br><small class='text-muted'>检索文档数: {top_k}</small>"
        else:
            # 如果不包含参考文献或结果不是字典
            answer = result if isinstance(result, str) else "无法生成回答"
            answer_with_info = f"{answer}<br><br><small class='text-muted'>检索文档数: {top_k}</small>"
        
        # 记录助手消息
        assistant_message = {
            "role": "assistant",
            "content": answer_with_info,
            "template": app.config['rag_session']['prompt_template'],
            "timestamp": datetime.datetime.now(),
            "top_k": top_k,  # 同时记录top_k值
            "include_references": include_references  # 记录是否包含参考文献
        }
        app.config['rag_session']['chat_history'].append(assistant_message)
        
    except Exception as e:
        app.logger.error(f"生成回答时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'生成回答时出错: {str(e)}', 'error')
    
    return redirect(url_for('rag_assistant'))

@app.route('/rag_assistant/clear', methods=['POST'])
def rag_assistant_clear():
    """清空聊天历史"""
    app.config['rag_session']['chat_history'] = []
    flash('聊天历史已清空', 'success')
    return redirect(url_for('rag_assistant'))

@app.route('/')
def index():
    """首页路由 - 显示炫酷的3D动画首页"""
    now = datetime.datetime.now()
    return render_template('home.html', now=now)


@app.route('/files')
def list_files():
    """List all files."""
    files = amphilagus.list_raw_data()
    # Pass BASE_TAGS to template for filtering in the frontend
    return render_template('files.html', files=files, filter_tags=None, exact=False, base_tag_names=list(BASE_TAGS.keys()))


@app.route('/files/filter', methods=['GET'])
def filter_files():
    """Filter files by multiple tags."""
    tags = request.args.getlist('tags')
    exact = request.args.get('exact', 'false').lower() == 'true'
    
    # 保持向后兼容性 - 如果使用旧格式的tag参数
    tag_name = request.args.get('tag')
    if tag_name and not tags:
        tags = [tag_name]
    
    if not tags:
        # 没有标签，显示所有文件
        files = amphilagus.list_raw_data()
    elif len(tags) == 1:
        # 单个标签过滤，使用现有方法
        files = amphilagus.get_raw_data_by_tag(tags[0], include_subclasses=not exact)
    else:
        # 多个标签过滤 - 使用文件名（可哈希）而不是Metadata对象（不可哈希）
        
        # 获取所有文件作为参考集
        all_files = {file.filename: file for file in amphilagus.list_raw_data()}
        
        # 获取第一个标签的文件名集合
        first_tag_files = set(file.filename for file in 
                             amphilagus.get_raw_data_by_tag(tags[0], include_subclasses=not exact))
        
        # 与其他标签文件名集合求交集
        matching_filenames = first_tag_files
        for tag in tags[1:]:
            tag_filenames = set(file.filename for file in 
                               amphilagus.get_raw_data_by_tag(tag, include_subclasses=not exact))
            matching_filenames = matching_filenames.intersection(tag_filenames)
        
        # 转换回Metadata对象列表
        files = [all_files[filename] for filename in matching_filenames if filename in all_files]
    
    # Pass BASE_TAGS to template for filtering in the frontend
    return render_template('files.html', files=files, filter_tags=tags, exact=exact, base_tag_names=list(BASE_TAGS.keys()))


# Import the PDF converter
try:
    from rag_assistant.utils.pdf_converter.pdf_to_markdown import convert_pdf_to_markdown
    pdf_converter_available = True
except ImportError:
    app.logger.warning("PDF converter module not available. PDF processing will be disabled.")
    pdf_converter_available = False


@app.route('/files/upload', methods=['GET', 'POST'])
def upload_file():
    """文件上传页面与处理"""
    if request.method == 'GET':
        # 获取标签列表用于显示
        tags = amphilagus.list_tags()
        recent_tasks = task_manager.get_recent_tasks(5)
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
            return redirect(url_for('upload_file'))
        
        # 获取表单数据
        tags = request.form.get('tags', '')
        description = request.form.get('description', '')
        
        # 获取PDF处理选项
        use_llm = request.form.get('use_llm', 'off')
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
        task = task_manager.create_task(
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
            return redirect(url_for('view_tasks'))
            
    except Exception as e:
        error_msg = f"创建上传任务时出错: {str(e)}"
        app.logger.error(error_msg)
        import traceback
        traceback.print_exc()
        
        if is_ajax:
            return jsonify({"success": False, "message": error_msg})
        
        flash(error_msg, 'error')
        return redirect(url_for('upload_file'))


@app.route('/files/<filename>/delete', methods=['POST'])
def delete_file(filename):
    """Delete a file."""
    if amphilagus.delete_raw_data(filename):
        flash(f'File {filename} deleted successfully')
    else:
        flash(f'Error deleting file {filename}')
    
    return redirect(url_for('list_files'))


@app.route('/files/batch_delete', methods=['POST'])
def batch_delete_files():
    """批量删除文件"""
    filenames = request.form.getlist('filenames[]')
    
    if not filenames:
        flash('未选择任何文件', 'warning')
        return redirect(url_for('list_files'))
    
    success_count = 0
    failed_files = []
    
    for filename in filenames:
        try:
            if amphilagus.delete_raw_data(filename):
                success_count += 1
            else:
                failed_files.append(filename)
        except Exception as e:
            app.logger.error(f"删除文件 {filename} 时出错: {str(e)}")
            failed_files.append(filename)
    
    # 显示结果消息
    if success_count > 0:
        flash(f'成功删除 {success_count} 个文件', 'success')
    
    if failed_files:
        flash(f'无法删除以下文件: {", ".join(failed_files)}', 'error')
    
    return redirect(url_for('list_files'))


@app.route('/files/batch_embed', methods=['POST'])
def batch_embed_files():
    """批量嵌入文件到向量数据库"""
    try:
        # 获取表单数据
        collection_name = request.form.get('collection_name')
        chunk_size = int(request.form.get('chunk_size', 1000))
        chunk_overlap = int(request.form.get('chunk_overlap', 200))
        check_duplicates = request.form.get('check_duplicates') == 'on'
        filenames = request.form.getlist('filenames[]')
        
        # 验证输入
        if not collection_name:
            flash('请选择一个向量数据库集合', 'error')
            return redirect(url_for('list_files'))
        
        if not filenames:
            flash('未选择任何文件', 'warning')
            return redirect(url_for('list_files'))
        
        # 获取完整的文件路径
        file_paths = []
        for filename in filenames:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                file_paths.append(file_path)
            else:
                flash(f'文件不存在: {filename}', 'warning')
        
        if not file_paths:
            flash('没有找到可处理的文件', 'error')
            return redirect(url_for('list_files'))
        
        # 创建批量嵌入任务，而不是直接处理
        task = task_manager.create_task(
            task_type='batch_embed',
            params={
                'collection_name': collection_name,
                'chunk_size': chunk_size,
                'chunk_overlap': chunk_overlap,
                'check_duplicates': check_duplicates,
                'file_paths': file_paths,
                'filenames': filenames  # 保存原始文件名用于显示
            }
        )
        
        # 显示任务创建成功
        flash(f'批量嵌入任务已创建，将在后台处理 {len(file_paths)} 个文件', 'success')
        
        # 重定向到任务查看页面
        return redirect(url_for('view_task', task_id=task.task_id))
        
    except Exception as e:
        app.logger.error(f"创建批量嵌入任务时出错: {str(e)}")
        flash(f'创建批量嵌入任务时出错: {str(e)}', 'error')
        return redirect(url_for('list_files'))


@app.route('/files/<filename>/tags', methods=['GET', 'POST'])
def manage_file_tags(filename):
    """Manage tags for a file."""
    file_metadata = amphilagus.get_raw_data_metadata(filename)
    
    if not file_metadata:
        flash(f'File {filename} not found')
        return redirect(url_for('list_files'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        tags = request.form.get('tags', '').split(',')
        tags = [tag.strip() for tag in tags if tag.strip()]
        
        if action == 'add' and tags:
            if amphilagus.add_tags(filename, tags):
                flash(f'Tags added to {filename}')
            else:
                flash(f'Error adding tags to {filename}')
        
        elif action == 'remove' and tags:
            if amphilagus.remove_tags(filename, tags):
                flash(f'Tags removed from {filename}')
            else:
                flash(f'Error removing tags from {filename}')
        
        return redirect(url_for('manage_file_tags', filename=filename))
    
    # GET request
    all_tags = amphilagus.list_tags()
    return render_template('file_tags.html', file=file_metadata, all_tags=all_tags)


@app.route('/files/<filename>/details')
def file_details(filename):
    """通过重定向在新页面查看文件"""
    file_metadata = amphilagus.get_raw_data_metadata(filename)
    
    if not file_metadata:
        flash(f'文件 {filename} 不存在')
        return redirect(url_for('list_files'))
    
    # 重定向到新的文件查看页面路由
    return redirect(url_for('view_backup_file', filename=filename))

@app.route('/files/<filename>/view')
def view_backup_file(filename):
    """在新页面中查看备份文件"""
    # 构建备份数据文件夹路径
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backup_data')
    
    # 获取文件名（不含扩展名）
    filename_no_ext = os.path.splitext(filename)[0]
    
    # 查找同名文件（可能有不同的扩展名）
    matching_files = []
    if os.path.exists(backup_dir):
        for f in os.listdir(backup_dir):
            if os.path.splitext(f)[0] == filename_no_ext:
                matching_files.append(f)
    
    # 如果找到多个文件，报错
    if len(matching_files) > 1:
        flash(f'在backup_data中找到多个同名文件: {", ".join(matching_files)}', 'error')
        return redirect(url_for('list_files'))
    
    # 如果没有找到文件，显示错误
    if not matching_files:
        flash(f'在backup_data中未找到{filename_no_ext}的文件', 'error')
        return redirect(url_for('list_files'))
    
    # 构建完整文件路径
    file_path = os.path.join(backup_dir, matching_files[0])
    backup_filename = matching_files[0]
    
    # 发送文件
    try:
        return send_file(file_path, as_attachment=False)
    except Exception as e:
        flash(f'打开文件时出错: {str(e)}', 'error')
        return redirect(url_for('list_files'))


@app.route('/files/<filename>/update_description', methods=['POST'])
def update_description(filename):
    """Update file description."""
    file_metadata = amphilagus.get_raw_data_metadata(filename)
    
    if not file_metadata:
        flash(f'File {filename} not found')
        return redirect(url_for('list_files'))
    
    new_description = request.form.get('description', '').strip()
    
    try:
        # 更新描述
        file_metadata.description = new_description
        amphilagus.file_manager._save_metadata()
        flash(f'文件描述已更新')
    except Exception as e:
        flash(f'更新描述时出错: {str(e)}')
    
    return redirect(url_for('file_details', filename=filename))


@app.route('/tags')
def list_tags():
    """List all tags."""
    tags = amphilagus.list_tags()
    # 确保基础类标签已标记
    ensure_base_tags()
    return render_template('tags.html', tags=tags)


@app.route('/tags/restore_presets', methods=['POST'])
def restore_preset_tags():
    """恢复所有预设标签"""
    # 强制更新所有预设标签
    ensure_base_tags()
    flash('已恢复所有预设标签')
    return redirect(url_for('list_tags'))


@app.route('/tags/create', methods=['GET', 'POST'])
def create_tag():
    """Create a new tag."""
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
            tag = amphilagus.create_tag(name, parent_name=parent)
            # 确保新标签不是预设标签和基础类标签
            tag.is_preset_tag = False
            tag.is_base_tag = False
            flash(f'标签 {tag.name} 创建成功')
            return redirect(url_for('list_tags'))
        except ValueError as e:
            flash(f'创建标签错误: {str(e)}')
            return redirect(request.url)
    
    # GET request
    existing_tags = amphilagus.list_tags()
    # 确保基础类标签存在
    ensure_base_tags()
    # 过滤出基础类标签作为父标签选项
    base_tags = [tag for tag in existing_tags if hasattr(tag, 'is_base_tag') and tag.is_base_tag and not tag.parent]
    return render_template('create_tag.html', existing_tags=existing_tags, base_tags=base_tags)


@app.route('/tags/<tag_name>/delete', methods=['POST'])
def delete_tag(tag_name):
    """Delete a tag."""
    # 获取标签
    tag = amphilagus.get_tag(tag_name)
    
    if not tag:
        flash(f'标签 {tag_name} 不存在')
        return redirect(url_for('list_tags'))
    
    # 检查是否是基础类标签，基础类标签不允许删除
    if hasattr(tag, 'is_base_tag') and tag.is_base_tag:
        flash(f'基础类标签 {tag_name} 不能删除')
        return redirect(url_for('list_tags'))
    
    # 预设标签可以删除，但会给予提示
    is_preset = hasattr(tag, 'is_preset_tag') and tag.is_preset_tag
    
    # 实现标签删除逻辑
    try:
        # 获取所有使用此标签的文件
        files_with_tag = amphilagus.get_raw_data_by_tag(tag_name)
        
        # 从文件中移除此标签
        for file in files_with_tag:
            amphilagus.remove_tags(file.filename, [tag_name])
        
        # 从标签注册表中删除
        if hasattr(amphilagus.file_manager, 'delete_tag'):
            amphilagus.file_manager.delete_tag(tag_name)
            if is_preset:
                flash(f'预设标签 {tag_name} 已删除，可通过"恢复预设标签"按钮恢复')
            else:
                flash(f'标签 {tag_name} 已删除')
        else:
            # 临时方案：如果没有删除方法，则仅从文件中移除
            flash(f'标签 {tag_name} 已从所有文件中移除，但无法从系统中完全删除')
    except Exception as e:
        flash(f'删除标签时出错: {str(e)}')
    
    return redirect(url_for('list_tags'))


@app.route('/api/files', methods=['GET'])
def api_list_files():
    """API endpoint to list files."""
    files = amphilagus.list_raw_data()
    return jsonify([file.to_dict() for file in files])


@app.route('/api/tags', methods=['GET'])
def api_list_tags():
    """API endpoint to list tags."""
    tags = amphilagus.list_tags()
    return jsonify([{"name": tag.name, "parent": tag.parent.name if tag.parent else None} for tag in tags])


@app.route('/api/collections', methods=['GET'])
def api_list_collections():
    """API endpoint to list vector database collections."""
    try:
        collections_info = db_manager.list_collections()
        collections = []
        
        for collection_info in collections_info:
            if collection_info["exists_in_chroma"]:
                collections.append({
                    'name': collection_info["name"],
                    'document_count': collection_info["doc_count"],
                    'embedding_model': collection_info.get("embedding_model", "Unknown")
                })
                
        return jsonify(collections)
    except Exception as e:
        app.logger.error(f"API获取集合列表时出错: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/database')
def database_dashboard():
    """数据库管理面板"""
    try:
        # 使用db_manager而不是直接调用导入的函数
        collections_info = db_manager.list_collections()
        
        # 获取数据库路径和状态统计
        chroma_db_path = db_manager.get_db_path()
        db_stats = db_manager.get_db_stats()
        
        # 打印调试信息
        app.logger.debug(f"从db_manager获取到的集合列表: {collections_info}")
        
        if not collections_info:
            app.logger.warning("未检索到任何集合")
        
        # 创建Chroma客户端实例检查
        if not db_manager.client:
            app.logger.error("ChromaDB客户端未初始化")
            return render_template('database.html', 
                                  collections=[],
                                  chroma_db_path=chroma_db_path,
                                  db_stats=db_stats,
                                  error="ChromaDB客户端未初始化，请检查数据库路径")
                
        return render_template('database.html', 
                              collections=collections_info,
                              chroma_db_path=chroma_db_path,
                              db_stats=db_stats,
                              success=request.args.get('success'),
                              error=request.args.get('error'))
    except Exception as e:
        import traceback
        app.logger.error(f"读取集合列表时出错: {str(e)}\n{traceback.format_exc()}")
        return render_template('database.html', 
                              collections=[],
                              chroma_db_path=db_manager.get_db_path() if db_manager else "未知",
                              db_stats={"total_collections": 0, "normal_collections": 0, 
                                        "missing_metadata": 0, "orphaned_metadata": 0, 
                                        "total_documents": 0},
                              error=f"读取集合列表时出错: {str(e)}")


@app.route('/database/reload', methods=['POST'])
def reload_database():
    """重新加载数据库集合信息"""
    try:
        # 重新初始化数据库管理器的客户端连接
        if db_manager.client is not None:
            # 关闭现有客户端连接
            try:
                del db_manager.client
            except:
                pass
            
        # 重新创建客户端连接
        import chromadb
        try:
            db_manager.client = chromadb.PersistentClient(path=str(db_manager.chroma_db_path))
            app.logger.info("成功重新初始化ChromaDB客户端连接")
            
            # 刷新集合列表
            db_manager.list_collections()
            
            return jsonify({"success": True, "message": "数据库集合信息已重新加载"}), 200
        except Exception as e:
            app.logger.error(f"重新初始化ChromaDB客户端时出错: {str(e)}")
            return jsonify({"success": False, "message": f"重新加载失败: {str(e)}"}), 500
    except Exception as e:
        app.logger.error(f"重新加载数据库集合信息时出错: {str(e)}")
        return jsonify({"success": False, "message": f"重新加载失败: {str(e)}"}), 500


@app.route('/database/collections/<collection_name>')
def view_collection(collection_name):
    """查看集合详情"""
    try:
        if not RAG_IMPORT_SUCCESS:
            return redirect(url_for('database_dashboard', error='RAG模块未导入，无法查看集合'))
        
        # 使用db_manager获取集合详情
        collection_details = db_manager.get_collection_details(collection_name)
        if not collection_details:
            return redirect(url_for('database_dashboard', error=f'集合"{collection_name}"不存在'))
        
        # 检查ChromaDB客户端是否已初始化
        if not db_manager.client:
            return redirect(url_for('database_dashboard', error='ChromaDB客户端未初始化，请检查数据库路径'))
        
        try:
            # 直接从ChromaDB获取数据
            chroma_collection = db_manager.client.get_collection(collection_name)
            # 获取总文档数
            doc_count = chroma_collection.count()
            
            # 获取所有文档
            raw_data = None
            documents = []
            
            # 直接获取所有文档
            raw_data = chroma_collection.get()
            
            # 处理文档数据
            for i, doc_id in enumerate(raw_data.get("ids", [])):
                metadata = raw_data.get("metadatas", [])[i] if raw_data.get("metadatas") and i < len(raw_data.get("metadatas", [])) else {}
                content = raw_data.get("documents", [])[i] if raw_data.get("documents") and i < len(raw_data.get("documents", [])) else ""
                
                documents.append({
                    "id": doc_id,
                    "metadata": metadata,
                    "content_preview": content[:50] + "..." if content and len(content) > 50 else content
                })
            
            app.logger.info(f"直接从ChromaDB获取到 {len(documents)} 个文档")
            
        except Exception as e:
            app.logger.error(f"直接从ChromaDB获取文档失败: {str(e)}")
            # 如果直接获取失败，尝试使用db_manager方法获取
            docs_result = db_manager.get_document_details(collection_name)
            
            if not docs_result["success"]:
                app.logger.error(f"通过db_manager获取文档列表失败: {docs_result['message']}")
                documents = []
            else:
                documents = docs_result.get("documents", [])
            
            app.logger.info(f"通过db_manager获取到 {len(documents)} 个文档")
        
        # 计算标签集
        all_tags = set()
        
        # 将文档按标题分组
        documents_by_title = {}
        unique_titles = set()
        
        for doc in documents:
            metadata = doc.get("metadata", {})
            if "tags" in metadata:
                all_tags.update(metadata.get("tags", []))
            
            # 提取标题
            title = metadata.get("title", "无标题文档")
            unique_titles.add(title)
            
            # 准备展示数据
            doc_for_display = {
                'id': doc.get("id", ""),
                'title': title,
                'text': doc.get("content_preview", ""),
                'tags': metadata.get("tags", []),
                'created_at': metadata.get("creation_time", datetime.datetime.now())
            }
            
            # 添加到分组字典
            if title not in documents_by_title:
                documents_by_title[title] = []
            documents_by_title[title].append(doc_for_display)
        
        # 随机排序每个标题下的文档
        import random
        for title in documents_by_title:
            random.shuffle(documents_by_title[title])
        
        # 构建集合信息
        collection_info = {
            'name': collection_name,
            'description': collection_details.get("metadata", {}).get("description", ""),
            'embedding_model': collection_details.get("embedding_model", "Unknown"),
            'document_count': doc_count if 'doc_count' in locals() else collection_details.get("doc_count", 0) or len(documents),
            'unique_tags': sorted(list(all_tags)),
            'unique_titles': len(unique_titles),
            'creation_time': collection_details.get("created_at", datetime.datetime.now())
        }
        
        # 处理文档列表 - 为了兼容性保留这个变量
        docs_for_display = []
        for doc in documents:
            metadata = doc.get("metadata", {})
            docs_for_display.append({
                'id': doc.get("id", ""),
                'title': metadata.get("title", "") or doc.get("id", "")[:8],
                'text': doc.get("content_preview", ""),
                'tags': metadata.get("tags", []),
                'created_at': metadata.get("creation_time", datetime.datetime.now())
            })
        
        return render_template('collection_view.html', 
                            collection=collection_info,
                            documents=docs_for_display,
                            documents_by_title=documents_by_title,
                            success=request.args.get('success'),
                            error=request.args.get('error'))
    except Exception as e:
        import traceback
        app.logger.error(f"加载集合时出错: {str(e)}\n{traceback.format_exc()}")
        return redirect(url_for('database_dashboard', error=f'加载集合时出错: {str(e)}'))


@app.route('/database/collections/<collection_name>/edit', methods=['POST'])
def edit_collection(collection_name):
    """编辑集合信息"""
    try:
        if not RAG_IMPORT_SUCCESS:
            return redirect(url_for('database_dashboard', error='RAG模块未导入，无法编辑集合'))
            
        description = request.form.get('description', '')
        
        # 使用db_manager获取集合
        collection_details = db_manager.get_collection_details(collection_name)
        if not collection_details:
            return redirect(url_for('view_collection', 
                                  collection_name=collection_name, 
                                  error='集合不存在或无法访问'))
        
        # 初始化pipeline以便访问document_store
        success, message, pipeline = db_manager.init_pipeline(collection_name)
        if not success:
            return redirect(url_for('view_collection', 
                                  collection_name=collection_name, 
                                  error=f'无法初始化Pipeline: {message}'))
        
        # 更新描述 - 通过collection_utils或直接修改元数据
        from rag_assistant.collection_metadata import update_collection_metadata
        update_collection_metadata(collection_name, {"description": description})
        
        return redirect(url_for('view_collection', 
                              collection_name=collection_name, 
                              success='集合信息已更新'))
    except Exception as e:
        return redirect(url_for('view_collection', 
                              collection_name=collection_name, 
                              error=f'更新集合信息时出错: {str(e)}'))


@app.route('/database/collections/<collection_name>/delete', methods=['POST'])
def delete_collection(collection_name):
    """删除集合"""
    try:
        if not RAG_IMPORT_SUCCESS:
            return redirect(url_for('database_dashboard', error='RAG模块未导入，无法删除集合'))
        
        # 使用db_manager删除集合
        success, message = db_manager.delete_collection(collection_name)
        
        if success:
            return redirect(url_for('database_dashboard', success=f'集合"{collection_name}"已成功删除'))
        else:
            return redirect(url_for('database_dashboard', error=f'删除集合失败: {message}'))
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return redirect(url_for('database_dashboard', error=f'删除集合时出错: {str(e)}'))


@app.route('/collections/<collection_name>/documents/<document_id>', methods=['GET'])
def view_document_details(collection_name, document_id):
    """View a document's details."""
    try:
        # Get document details directly from the global db_manager
        try:
            result = db_manager.get_document_details(collection_name, document_id)
            
            # Debug logging
            app.logger.debug(f"Retrieved document details: {result}")
            
            if not result["success"] or not result["documents"]:
                flash('文档不存在。Document does not exist.', 'error')
                return redirect(url_for('view_collection', collection_name=collection_name))
            
            # Get the first document from the result
            document = result["documents"][0]
            
            # Ensure document has required fields
            if not hasattr(document, 'metadata') or document.metadata is None:
                document.metadata = {}
                
            # Ensure content exists
            if not hasattr(document, 'content') or document.content is None:
                document.content = '<em>该文档没有内容或内容无法显示。</em>'
                
            return render_template('document_view.html', document=document, collection_name=collection_name)
            
        except Exception as e:
            app.logger.error(f"Error retrieving document details: {str(e)}")
            flash(f'获取文档详情时出错: {str(e)}', 'error')
            return redirect(url_for('view_collection', collection_name=collection_name))
            
    except Exception as e:
        app.logger.error(f"Error in view_document_details: {str(e)}")
        flash(f'查看文档详情时发生错误: {str(e)}', 'error')
        return redirect(url_for('database_dashboard'))


@app.route('/database/debug/collection/<collection_name>')
def debug_collection(collection_name):
    """调试集合内容 - 仅在开发环境使用"""
    if not app.debug:
        return jsonify({"error": "只在调试模式下可用"}), 403
    
    try:
        # 获取集合详情
        collection_details = db_manager.get_collection_details(collection_name)
        
        # 直接访问ChromaDB集合获取原始数据
        if db_manager.client:
            try:
                chroma_collection = db_manager.client.get_collection(collection_name)
                raw_data = chroma_collection.get()
                
                # 获取文档详情结果
                docs_result = db_manager.get_document_details(collection_name)
                
                results = {
                    "collection_details": collection_details,
                    "chroma_raw_data": {
                        "ids": raw_data.get("ids", [])[:10],  # 仅显示前10个ID
                        "metadatas_count": len(raw_data.get("metadatas", [])),
                        "documents_count": len(raw_data.get("documents", [])),
                        "sample_metadata": raw_data.get("metadatas", [])[:2] if raw_data.get("metadatas") else []
                    },
                    "document_details_result": {
                        "success": docs_result.get("success"),
                        "message": docs_result.get("message"),
                        "total": docs_result.get("total", 0),
                        "document_count": len(docs_result.get("documents", [])),
                        "sample_documents": docs_result.get("documents", [])[:2]
                    }
                }
                
                return jsonify(results)
            except Exception as e:
                return jsonify({"error": f"访问ChromaDB失败: {str(e)}"})
        else:
            return jsonify({"error": "ChromaDB客户端未初始化"})
    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        })


# 添加日期格式化过滤器
@app.template_filter('datetimeformat')
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


@app.route('/tasks')
def view_tasks():
    """查看所有任务"""
    tasks = task_manager.get_all_tasks()
    # 按创建时间倒序排序
    tasks.sort(key=lambda t: t.created_at, reverse=True)
    return render_template('tasks.html', tasks=tasks)


@app.route('/tasks/<task_id>')
def view_task(task_id):
    """查看单个任务详情"""
    task = task_manager.get_task(task_id)
    if not task:
        flash('任务不存在', 'error')
        return redirect(url_for('view_tasks'))
    return render_template('task_details.html', task=task)


@app.route('/api/tasks/<task_id>/status')
def get_task_status(task_id):
    """获取任务状态 API"""
    status = task_manager.get_task_status(task_id)
    if status:
        return jsonify(status)
    return jsonify({"error": "任务不存在"}), 404


@app.route('/api/tasks/<task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """删除任务 API"""
    success, message = task_manager.delete_task(task_id)
    return jsonify({"success": success, "message": message})


@app.route('/api/tasks/clear-completed', methods=['POST'])
def clear_completed_tasks():
    """清除已完成的任务 API"""
    count = task_manager.clear_completed_tasks()
    return jsonify({"success": True, "message": f"已清除 {count} 个已完成的任务"})


def run_app(host='0.0.0.0', port=5000, debug=False):
    """Run the web application."""
    # Create instance path for temporary files
    os.makedirs(app.instance_path, exist_ok=True)
    # 确保基础类标签存在
    ensure_base_tags()
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_app(debug=True) 