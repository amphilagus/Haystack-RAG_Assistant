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
from dotenv import load_dotenv
import logging
import uuid
import re
import openai

from .assistant import MCPToolAgent
from .literature import Literature

from .logger import get_logger
from .file_manager import FileManager
from . import config

# Import RAG components with fallback
try:
    from .rag.document_loader import load_documents
    from .rag.rag_pipeline import RAGPipeline
    from .rag.collection_metadata import get_embedding_model
    HAS_RAG = True
except ImportError:
    logger.warning("RAG Assistant modules not found. Vector database functions will be limited.")
    HAS_RAG = False

# 解决循环引用问题，延迟导入
def get_task_manager():
    from .task_manager import TaskManager
    return TaskManager

def get_database_manager():
    from .database_manager import DatabaseManager
    return DatabaseManager

# Configure logger based on environment variable
logger = get_logger('web_app')
logger.info("初始化Web应用")

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
        logger.error(f"Error reading .env file directly: {e}")
    
    return None

# 设置工作空间目录 - 优先使用环境变量中的工作空间目录
config.WORKSPACE_DIR = os.environ.get('AMPHILAGUS_WORKSPACE')
if config.WORKSPACE_DIR:
    # 使用环境变量中设置的工作空间目录
    logger.info(f"使用环境变量设置的工作空间目录: {config.WORKSPACE_DIR}")
else:
    # 如果未设置环境变量，则使用默认的项目根目录（仅用于开发环境）
    config.WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logger.warning(f"未设置AMPHILAGUS_WORKSPACE环境变量，使用默认目录: {config.WORKSPACE_DIR}")

# 配置文件路径 
MD_CLEANER_CONFIG_PATH = os.path.join(config.WORKSPACE_DIR, 'configs','md_cleaner_config.json')
# 标题提取配置路径
TITLE_EXTRACTOR_CONFIG_PATH = os.path.join(config.WORKSPACE_DIR, 'configs','title_extractor_config.json')

## 数据存储相关路径
# 设置ChromaDB路径
CHROMA_DB_PATH = os.path.join(config.WORKSPACE_DIR, 'chroma_db')
# 设置files目录
FILES_DIR = os.path.join(config.WORKSPACE_DIR, 'files')
# 确保files目录存在
os.makedirs(FILES_DIR, exist_ok=True)
# 设置raw_files路径
RAW_FILES_PATH = os.path.join(FILES_DIR, 'raw_files')
os.makedirs(RAW_FILES_PATH, exist_ok=True)
# 设置raw_files_metadata路径
RAW_FILES_METADATA_PATH = os.path.join(FILES_DIR, 'raw_files_metadata.json')
# 设置backup_files路径
BACKUP_FILES_PATH = os.path.join(FILES_DIR, 'backup_files')
os.makedirs(BACKUP_FILES_PATH, exist_ok=True)
# 设置tasks路径
TASKS_PATH = os.path.join(config.WORKSPACE_DIR, 'tasks')
os.makedirs(TASKS_PATH, exist_ok=True)

# 记录所有路径变量
logger.debug("Initialized paths:")
logger.debug(f"MD_CLEANER_CONFIG_PATH: {MD_CLEANER_CONFIG_PATH}")
logger.debug(f"CHROMA_DB_PATH: {CHROMA_DB_PATH}")
logger.debug(f"RAW_FILES_PATH: {RAW_FILES_PATH}")
logger.debug(f"RAW_FILES_METADATA_PATH: {RAW_FILES_METADATA_PATH}")
logger.debug(f"BACKUP_FILES_PATH: {BACKUP_FILES_PATH}")
logger.debug(f"TITLE_EXTRACTOR_CONFIG_PATH: {TITLE_EXTRACTOR_CONFIG_PATH}")

# 尝试加载配置文件
try:
    # 加载MD清理配置
    if os.path.exists(MD_CLEANER_CONFIG_PATH):
        with open(MD_CLEANER_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config.MD_CLEANER_CONFIG = json.load(f)
    else:
        logger.error(f"MD cleaner config file not found at {MD_CLEANER_CONFIG_PATH}")
        raise FileNotFoundError(f"必需的配置文件未找到: {MD_CLEANER_CONFIG_PATH}")
        
    # 加载标题提取配置
    if os.path.exists(TITLE_EXTRACTOR_CONFIG_PATH):
        with open(TITLE_EXTRACTOR_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config.TITLE_EXTRACTOR_CONFIG = json.load(f)
    else:
        logger.error(f"Title extractor config file not found at {TITLE_EXTRACTOR_CONFIG_PATH}")
        raise FileNotFoundError(f"必需的配置文件未找到: {TITLE_EXTRACTOR_CONFIG_PATH}")
    
    # 验证配置文件格式
    if "first_non_empty" not in config.TITLE_EXTRACTOR_CONFIG or "journals" not in config.TITLE_EXTRACTOR_CONFIG["first_non_empty"] or "default" not in config.TITLE_EXTRACTOR_CONFIG["first_non_empty"]["journals"]:
        raise ValueError("标题提取配置文件结构不正确，缺少 'first_non_empty.journals.default' 路径")
        
except Exception as e:
    logger.error(f"配置文件加载失败: {str(e)}")
    raise RuntimeError(f"配置文件加载失败，应用无法启动: {str(e)}")

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_replace_in_production')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload
app.config['UPLOAD_FOLDER'] = RAW_FILES_PATH

# 记录Flask应用配置
logger.debug(f"Flask app initialized with UPLOAD_FOLDER: {app.config['UPLOAD_FOLDER']}")
logger.debug(f"Flask app MAX_CONTENT_LENGTH: {app.config['MAX_CONTENT_LENGTH']} bytes")

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'md'}

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

# Initialize the FileManager directly
file_manager = FileManager(raw_files_dir=RAW_FILES_PATH, backup_files_dir=BACKUP_FILES_PATH)

# 初始化数据库管理器
db_manager = get_database_manager()(chroma_db_path=CHROMA_DB_PATH)

# 初始化任务管理器
try:
    task_manager = get_task_manager()(TASKS_PATH, file_manager, db_manager)
    logger.info("Task manager successfully initialized")
except Exception as e:
    logger.error(f"Error initializing task manager: {str(e)}")
    task_manager = None

# 确保基础类标签和预设次级标签存在
def ensure_base_tags():
    existing_tags = {tag.name: tag for tag in file_manager.list_tags()}
    
    # 创建/更新基础类标签
    for tag_name, description in BASE_TAGS.items():
        if tag_name not in existing_tags:
            tag = file_manager.create_tag(tag_name)
            # 标记为基础类标签，不可删除
            tag.is_base_tag = True
            # 不是预设标签
            if hasattr(tag, 'is_preset_tag'):
                tag.is_preset_tag = False
            logger.debug(f"Created base tag: {tag_name}")
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
                    subtag = file_manager.create_tag(subtag_name, parent_name=parent_name)
                    # 标记为预设标签
                    subtag.is_preset_tag = True
                    # 不是基础类标签（可删除）
                    subtag.is_base_tag = False
                except ValueError:
                    # 如果标签已存在但命名不同，则跳过
                    continue
    
    # 保存更改
    file_manager._save_metadata()

# 移除 @app.before_first_request 装饰器，改为在应用启动前直接调用
# 在每个请求前执行初始化检查
@app.before_request
def before_request():
    global task_manager
    ensure_base_tags()
    
    # 延迟初始化任务管理器，确保amphilagus实例已经初始化
    if task_manager is None:
        task_manager = get_task_manager().get_instance(amphilagus=file_manager)
    
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
    if not HAS_RAG:
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
    if not HAS_RAG:
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

def find_backup_files_by_title(title):
    """
    通过标题查找backup_files文件夹中可能匹配的文件
    
    Args:
        title: 文档标题
        
    Returns:
        找到的文件名（如果存在），否则返回None
    """

    # 如果目录不存在，返回None
    if not os.path.exists(BACKUP_FILES_PATH):
        return None
    
    # 将标题转换为可能的文件名模式（移除特殊字符）
    import re
    title_pattern = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
    
    # 查找匹配的文件
    matching_files = []
    for filename in os.listdir(BACKUP_FILES_PATH):
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
    if not HAS_RAG:
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
                    backup_files = find_backup_files_by_title(ref)
                    if backup_files:
                        # 创建链接到备份文件
                        references_html += f'{i}. <a href="{url_for("view_backup_files", filename=backup_files)}" target="_blank">{ref}</a><br>'
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
    files = file_manager.list_files()
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
        files = file_manager.list_files()
    elif len(tags) == 1:
        # 单个标签过滤，使用现有方法
        files = file_manager.get_files_by_tag(tags[0], include_subclasses=not exact)
    else:
        # 多个标签过滤 - 使用文件名（可哈希）而不是Metadata对象（不可哈希）
        
        # 获取所有文件作为参考集
        all_files = {file.filename: file for file in file_manager.list_files()}
        
        # 获取第一个标签的文件名集合
        first_tag_files = set(file.filename for file in 
                             file_manager.get_files_by_tag(tags[0], include_subclasses=not exact))
        
        # 与其他标签文件名集合求交集
        matching_filenames = first_tag_files
        for tag in tags[1:]:
            tag_filenames = set(file.filename for file in 
                               file_manager.get_files_by_tag(tag, include_subclasses=not exact))
            matching_filenames = matching_filenames.intersection(tag_filenames)
        
        # 转换回Metadata对象列表
        files = [all_files[filename] for filename in matching_filenames if filename in all_files]
    
    # Pass BASE_TAGS to template for filtering in the frontend
    return render_template('files.html', files=files, filter_tags=tags, exact=exact, base_tag_names=list(BASE_TAGS.keys()))


# Import the PDF converter
try:
    from .utils.pdf_converter.pdf2md import convert_pdf_to_markdown
    pdf_converter_available = True
except ImportError:
    app.logger.warning("PDF converter module not available. PDF processing will be disabled.")
    pdf_converter_available = False


@app.route('/files/upload', methods=['GET', 'POST'])
def upload_file():
    """文件上传页面与处理"""
    if request.method == 'GET':
        # 获取标签列表用于显示
        tags = file_manager.list_tags()
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
    if file_manager.delete_file(filename):
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
            if file_manager.delete_file(filename):
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
            return redirect(url_for('list_files'))
        
        if not filenames:
            flash('未选择任何文件', 'warning')
            return redirect(url_for('list_files'))
        
        # 获取完整的文件路径
        file_paths = []
        for filename in filenames:
            file_path = os.path.join(RAW_FILES_PATH, filename)
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
        return redirect(url_for('view_task', task_id=task.task_id))
        
    except Exception as e:
        app.logger.error(f"创建批量嵌入任务时出错: {str(e)}")
        flash(f'创建批量嵌入任务时出错: {str(e)}', 'error')
        return redirect(url_for('list_files'))


@app.route('/files/<filename>/tags', methods=['GET', 'POST'])
def manage_file_tags(filename):
    """Manage tags for a file."""
    file_metadata = file_manager.get_file_metadata(filename)
    
    if not file_metadata:
        flash(f'File {filename} not found')
        return redirect(url_for('list_files'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        tags = request.form.get('tags', '').split(',')
        tags = [tag.strip() for tag in tags if tag.strip()]
        
        if action == 'add' and tags:
            if file_manager.add_tags_to_file(filename, tags):
                flash(f'Tags added to {filename}')
            else:
                flash(f'Error adding tags to {filename}')
        
        elif action == 'remove' and tags:
            if file_manager.remove_tags_from_file(filename, tags):
                flash(f'Tags removed from {filename}')
            else:
                flash(f'Error removing tags from {filename}')
        
        return redirect(url_for('manage_file_tags', filename=filename))
    
    # GET request
    all_tags = file_manager.list_tags()
    return render_template('file_tags.html', file=file_metadata, all_tags=all_tags)


@app.route('/files/<filename>/details')
def file_details(filename):
    """通过重定向在新页面查看文件"""
    file_metadata = file_manager.get_file_metadata(filename)
    
    if not file_metadata:
        flash(f'文件 {filename} 不存在')
        return redirect(url_for('list_files'))
    
    # 重定向到新的文件查看页面路由
    return redirect(url_for('view_backup_files', filename=filename))

@app.route('/files/<filename>/view')
def view_backup_files(filename):
    """在新页面中查看备份文件"""
    # 获取文件名（不含扩展名）
    filename_no_ext = os.path.splitext(filename)[0]
    
    # 查找同名文件（可能有不同的扩展名）
    matching_files = []
    if os.path.exists(BACKUP_FILES_PATH):
        for f in os.listdir(BACKUP_FILES_PATH):
            if os.path.splitext(f)[0] == filename_no_ext:
                matching_files.append(f)
    
    # 如果找到多个文件，报错
    if len(matching_files) > 1:
        flash(f'在backup_files中找到多个同名文件: {", ".join(matching_files)}', 'error')
        return redirect(url_for('list_files'))
    
    # 如果没有找到文件，显示错误
    if not matching_files:
        flash(f'在backup_files中未找到{filename_no_ext}的文件', 'error')
        return redirect(url_for('list_files'))
    
    # 构建完整文件路径
    file_path = os.path.join(BACKUP_FILES_PATH, matching_files[0])
    backup_filesname = matching_files[0]
    
    # 发送文件
    try:
        return send_file(file_path, as_attachment=False)
    except Exception as e:
        flash(f'打开文件时出错: {str(e)}', 'error')
        return redirect(url_for('list_files'))


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


@app.route('/database/collections/<collection_name>/delete', methods=['POST'])
def delete_collection(collection_name):
    """删除集合"""
    try:
        if not HAS_RAG:
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

@app.route('/files/<filename>/update_description', methods=['POST'])
def update_description(filename):
    """Update file description."""
    file_metadata = file_manager.get_file_metadata(filename)
    
    if not file_metadata:
        flash(f'File {filename} not found')
        return redirect(url_for('list_files'))
    
    new_description = request.form.get('description', '').strip()
    
    try:
        # 更新描述
        file_metadata.description = new_description
        file_manager._save_metadata()
        flash(f'文件描述已更新')
    except Exception as e:
        flash(f'更新描述时出错: {str(e)}')
    
    return redirect(url_for('file_details', filename=filename))


@app.route('/tags')
def list_tags():
    """List all tags."""
    tags = file_manager.list_tags()
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
            tag = file_manager.create_tag(name, parent_name=parent)
            # 确保新标签不是预设标签和基础类标签
            tag.is_preset_tag = False
            tag.is_base_tag = False
            flash(f'标签 {tag.name} 创建成功')
            return redirect(url_for('list_tags'))
        except ValueError as e:
            flash(f'创建标签错误: {str(e)}')
            return redirect(request.url)
    
    # GET request
    existing_tags = file_manager.list_tags()
    # 确保基础类标签存在
    ensure_base_tags()
    # 过滤出基础类标签作为父标签选项
    base_tags = [tag for tag in existing_tags if hasattr(tag, 'is_base_tag') and tag.is_base_tag and not tag.parent]
    return render_template('create_tag.html', existing_tags=existing_tags, base_tags=base_tags)


@app.route('/tags/<tag_name>/delete', methods=['POST'])
def delete_tag(tag_name):
    """Delete a tag."""
    # 获取标签
    tag = file_manager.get_tag(tag_name)
    
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
        files_with_tag = file_manager.get_files_by_tag(tag_name)
        
        # 从文件中移除此标签
        for file in files_with_tag:
            file_manager.remove_tags_from_file(file.filename, [tag_name])
        
        # 从标签注册表中删除
        if hasattr(file_manager, 'delete_tag'):
            file_manager.delete_tag(tag_name)
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
    files = file_manager.list_files()
    return jsonify([file.to_dict() for file in files])


@app.route('/api/tags', methods=['GET'])
def api_list_tags():
    """API endpoint to list tags."""
    tags = file_manager.list_tags()
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


# 初始化全能助手会话状态
if 'universal_assistant_session' not in app.config:
    app.config['universal_assistant_session'] = {
        'initialized': False,
        'chat_history': [],
        'current_model': None,
        'agent': None,
        'debug_mode': False  # 添加debug模式状态
    }

@app.route('/universal_assistant')
def universal_assistant():
    """全能助手页面路由"""
    
    # 检查环境变量中是否有API密钥
    api_key = get_api_key()
    if not api_key:
        flash('未找到环境变量中的OpenAI API密钥，请设置OPENAI_API_KEY环境变量', 'warning')
    
    # 初始化临时代理以获取可用工具
    available_tools = []
    try:
        temp_agent = MCPToolAgent(api_key=api_key)
        available_tools = temp_agent.get_available_tools()
    except Exception as e:
        app.logger.error(f"获取可用工具时出错: {str(e)}")
        flash(f'无法连接到MCP服务器，请确保MCP服务器正在运行', 'error')
    
    # 准备模板变量
    template_vars = {
        'current_model': app.config['universal_assistant_session'].get('current_model', 'gpt-4o'),
        'chat_history': app.config['universal_assistant_session'].get('chat_history', []),
        'initialized': app.config['universal_assistant_session'].get('initialized', False),
        'available_tools': available_tools,
        'debug_mode': app.config['universal_assistant_session'].get('debug_mode', False)  # 传递debug状态到模板
    }
    
    return render_template('universal_assistant.html', **template_vars)

@app.route('/universal_assistant/config', methods=['POST'])
def universal_assistant_config():
    """处理全能助手配置更新"""
    
    # 检查环境变量中是否有API密钥
    api_key = get_api_key()
    if not api_key:
        flash('未找到环境变量中的OpenAI API密钥，请设置OPENAI_API_KEY环境变量', 'error')
        return redirect(url_for('universal_assistant'))
    
    # 获取表单数据
    llm_model = request.form.get('llm_model', 'gpt-4o')
    
    # 获取debug模式状态
    debug_mode = request.form.get('debug_mode') == 'on'
    
    try:
        # 初始化MCPToolAgent
        mcp_agent = MCPToolAgent(
            model=llm_model,
            server_url="http://localhost:8000",  # MCP服务器URL
            api_key=api_key
        )
        
        # 更新会话状态
        app.config['universal_assistant_session']['agent'] = mcp_agent
        app.config['universal_assistant_session']['current_model'] = llm_model
        app.config['universal_assistant_session']['initialized'] = True
        app.config['universal_assistant_session']['debug_mode'] = debug_mode  # 保存debug模式状态
        
        # 获取可用工具
        available_tools = mcp_agent.get_available_tools()
        
        # 包含debug模式状态在消息中
        debug_info = "（调试模式已启用）" if debug_mode else ""
        flash(f"全能助手已成功初始化，使用 {llm_model} 模型和 {len(available_tools)} 个工具 {debug_info}", 'success')
        
    except Exception as e:
        app.logger.error(f"初始化全能助手时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'初始化全能助手时出错: {str(e)}', 'error')
    
    return redirect(url_for('universal_assistant'))

@app.route('/universal_assistant/chat', methods=['POST'])
def universal_assistant_chat():
    """处理全能助手聊天请求"""
    
    # 检查是否已初始化
    if not app.config['universal_assistant_session'].get('initialized', False) or app.config['universal_assistant_session'].get('agent') is None:
        return jsonify({
            "success": False,
            "content": "请先初始化全能助手",
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    # 获取用户查询
    user_query = request.form.get('user_query', '').strip()
    if not user_query:
        return jsonify({
            "success": False,
            "content": "请输入有效的问题",
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    try:
        # 记录用户消息
        user_message = {
            "role": "user",
            "content": user_query,
            "timestamp": datetime.datetime.now()
        }
        app.config['universal_assistant_session']['chat_history'].append(user_message)
        
        # 获取MCPToolAgent和debug模式状态
        mcp_agent = app.config['universal_assistant_session']['agent']
        debug_mode = app.config['universal_assistant_session'].get('debug_mode', False)
        
        # 生成回答，根据debug模式决定返回内容
        result = mcp_agent.run(user_query, debug=debug_mode)
        
        if debug_mode:
            # Debug模式：返回所有消息步骤
            # 处理消息列表并构建HTML
            debug_content = ""
            for idx, msg in enumerate(result):
                role_badge = f'<span class="badge bg-primary">{msg.role}</span>'
                step_badge = f'<span class="badge bg-secondary">步骤 {idx+1}</span>'
                content = msg._content
                debug_content += f'<div class="debug-message mb-2 p-2 border-bottom">{role_badge} {step_badge}<br>{content}</div>'
            
            # 记录助手回复
            assistant_message = {
                "role": "assistant",
                "content": f'<div class="debug-panel p-2 border rounded"><h6>调试模式输出：</h6>{debug_content}</div>',
                "timestamp": datetime.datetime.now()
            }
            app.config['universal_assistant_session']['chat_history'].append(assistant_message)
            
            # 返回JSON响应
            return jsonify({
                "success": True,
                "content": assistant_message["content"],
                "timestamp": assistant_message["timestamp"].isoformat(),
                "is_debug": True
            })
        else:
            # 正常模式：只返回最终回答
            # 记录助手回复
            assistant_message = {
                "role": "assistant",
                "content": result,
                "timestamp": datetime.datetime.now()
            }
            app.config['universal_assistant_session']['chat_history'].append(assistant_message)
            
            # 返回JSON响应
            return jsonify({
                "success": True,
                "content": result,
                "timestamp": assistant_message["timestamp"].isoformat(),
                "is_debug": False
            })
        
    except Exception as e:
        app.logger.error(f"生成回答时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 记录错误消息
        error_message = {
            "role": "assistant",
            "content": f"<span class='text-danger'>生成回答时出错: {str(e)}</span>",
            "timestamp": datetime.datetime.now()
        }
        app.config['universal_assistant_session']['chat_history'].append(error_message)
        
        # 返回错误JSON响应
        return jsonify({
            "success": False,
            "content": error_message["content"],
            "timestamp": error_message["timestamp"].isoformat(),
            "is_debug": False
        })

@app.route('/universal_assistant/clear', methods=['POST'])
def universal_assistant_clear():
    """清空全能助手聊天历史"""
    app.config['universal_assistant_session']['chat_history'] = []
    flash('对话历史已清空', 'success')
    return redirect(url_for('universal_assistant'))

@app.route('/batch_clean', methods=['POST'])
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
        task = task_manager.create_task(
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

@app.route('/reload_config')
def reload_config():
    """重新加载配置文件"""
    global config
    logger.info("收到重新加载配置文件请求")
    
    try:
        # 记录当前配置的相关信息（用于前后对比）
        md_config_before = len(config.MD_CLEANER_CONFIG.keys()) if hasattr(config, 'MD_CLEANER_CONFIG') else 0
        title_config_before = len(config.TITLE_EXTRACTOR_CONFIG.keys()) if hasattr(config, 'TITLE_EXTRACTOR_CONFIG') else 0
        
        # 重新加载MD清理配置
        if os.path.exists(MD_CLEANER_CONFIG_PATH):
            with open(MD_CLEANER_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config.MD_CLEANER_CONFIG = json.load(f)
                logger.info(f"已重新加载MD清理配置文件: {MD_CLEANER_CONFIG_PATH}")
                # 在调试级别输出完整的配置内容
                logger.debug(f"MD_CLEANER_CONFIG完整内容: {json.dumps(config.MD_CLEANER_CONFIG, ensure_ascii=False, indent=2)}")
        else:
            logger.error(f"MD清理配置文件不存在: {MD_CLEANER_CONFIG_PATH}")
            flash(f"MD清理配置文件不存在: {MD_CLEANER_CONFIG_PATH}", "danger")
            return redirect(request.referrer or url_for('index'))
        
        # 重新加载标题提取配置
        if os.path.exists(TITLE_EXTRACTOR_CONFIG_PATH):
            with open(TITLE_EXTRACTOR_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config.TITLE_EXTRACTOR_CONFIG = json.load(f)
                logger.info(f"已重新加载标题提取配置文件: {TITLE_EXTRACTOR_CONFIG_PATH}")
                # 在调试级别输出完整的配置内容
                logger.debug(f"TITLE_EXTRACTOR_CONFIG完整内容: {json.dumps(config.TITLE_EXTRACTOR_CONFIG, ensure_ascii=False, indent=2)}")
        else:
            logger.error(f"标题提取配置文件不存在: {TITLE_EXTRACTOR_CONFIG_PATH}")
            flash(f"标题提取配置文件不存在: {TITLE_EXTRACTOR_CONFIG_PATH}", "danger")
            return redirect(request.referrer or url_for('index'))
        
        # 验证配置文件格式
        if "default" not in config.TITLE_EXTRACTOR_CONFIG.get("first_non_empty", {}).get("journals", {}):
            error_msg = "标题提取配置文件缺少 'first_non_empty.journals.default' 策略"
            logger.error(error_msg)
            flash(error_msg, "danger")
            return redirect(request.referrer or url_for('index'))
        
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
    return redirect(request.referrer or url_for('index'))

def run_app(host='0.0.0.0', port=5000, debug=False):
    """Run the web application."""
    # Create instance path for temporary files
    os.makedirs(app.instance_path, exist_ok=True)
    # 确保基础类标签存在
    ensure_base_tags()
    app.run(host=host, port=port, debug=debug)

@app.route('/files/<filename>/rename', methods=['POST'])
def rename_file(filename):
    """重命名文件"""
    logger.info(f"收到重命名文件请求: {filename}")
    
    new_filename = request.form.get('new_filename', '').strip()
    
    if not new_filename:
        flash('新文件名不能为空', 'error')
        return redirect(url_for('list_files'))
    
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
        return redirect(url_for('list_files'))
    
    # 确保文件名有效且扩展名相同
    if not config.allowed_file(new_filename):
        flash('文件扩展名必须是允许的类型', 'error')
        return redirect(url_for('list_files'))
    
    # 文件重命名操作
    if file_manager.rename_file(filename, new_filename):
        flash(f'文件 {filename} 成功重命名为 {new_filename}', 'success')
    else:
        flash(f'重命名文件 {filename} 失败', 'error')
    
    return redirect(url_for('list_files'))


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

@app.route('/literature')
def list_literature():
    """List all literature."""
    # 加载所有文献
    literature_list = Literature.list_all()
    # 通过BASE_TAGS传递基础标签类型给前端，用于过滤
    return render_template('literature.html', literature=literature_list, filter_tags=None, exact=False, base_tag_names=list(BASE_TAGS.keys()))


@app.route('/literature/filter', methods=['GET'])
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
    return render_template('literature.html', literature=filtered_literature, filter_tags=tags, exact=exact, base_tag_names=list(BASE_TAGS.keys()))


@app.route('/literature/sync', methods=['POST'])
def sync_literature_tags():
    """同步文献与文件系统中的标签"""
    try:
        # 获取所有文献
        literature_list = Literature.list_all()
        
        # 遍历每篇文献，加载标签并更新
        for lit in literature_list:
            # 从文件管理器中加载标签
            lit.load_tags_from_json(file_manager)
            # 根据标签更新文献属性
            lit.update_from_tags(file_manager)
            # 保存更新后的文献
            lit.save()
        
        flash('文献标签同步完成', 'success')
    except Exception as e:
        flash(f'同步文献标签时出错: {str(e)}', 'error')
    
    return redirect(url_for('list_literature'))


@app.route('/literature/update_files', methods=['POST'])
def update_literature_files():
    """将文献属性更新到文件标签"""
    try:
        # 获取所有文献
        literature_list = Literature.list_all()
        
        # 遍历每篇文献，更新文件标签
        success_count = 0
        for lit in literature_list:
            # 更新文件标签，自动创建不存在的标签
            if lit.update_file_tags(file_manager, auto_create_tags=True):
                success_count += 1
        
        flash(f'已更新 {success_count} 篇文献的文件标签', 'success')
    except Exception as e:
        flash(f'更新文件标签时出错: {str(e)}', 'error')
    
    return redirect(url_for('list_literature'))

if __name__ == '__main__':
    run_app(debug=True) 