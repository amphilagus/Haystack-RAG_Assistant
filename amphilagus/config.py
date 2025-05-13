"""配置加载模块，集中处理应用程序所需的各种配置"""
import os
import json
import logging

from dotenv import load_dotenv
from .logger import get_logger
from .utils.md_cleaner.md_cleaner import clean_markdown

logger = get_logger('config')

def get_workspace_dir():
    """获取工作空间目录"""
    # 从环境变量获取工作空间目录
    workspace_dir = os.environ.get('AMPHILAGUS_WORKSPACE')
    if not workspace_dir:
        # 如果未设置环境变量，使用当前目录
        workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logger.info(f"未设置AMPHILAGUS_WORKSPACE环境变量，使用默认目录: {workspace_dir}")
    return workspace_dir

# 初始化工作空间目录
WORKSPACE_DIR = get_workspace_dir()

# 设置各种路径
CONFIGS_DIR = os.path.join(WORKSPACE_DIR, 'configs')
FILES_DIR = os.path.join(WORKSPACE_DIR, 'files')
RAW_FILES_PATH = os.path.join(FILES_DIR, 'raw_files')
RAW_FILES_METADATA_PATH = os.path.join(FILES_DIR, 'raw_files_metadata.json')
BACKUP_FILES_PATH = os.path.join(FILES_DIR, 'backup_files')
TASKS_PATH = os.path.join(WORKSPACE_DIR, 'tasks')
CHROMA_DB_PATH = os.path.join(WORKSPACE_DIR, 'chroma_db')
KNOWLEDGE_DIR = os.path.join(WORKSPACE_DIR, 'knowledge')
LITERATURE_DATA_PATH = os.path.join(KNOWLEDGE_DIR, 'literature_data.json')
COLLECTION_METADATA_FILE = os.path.join(WORKSPACE_DIR, 'collection_metadata.json')
SUM_FILES_PATH = os.path.join(FILES_DIR, 'sum_files')

# 配置文件路径
MD_CLEANER_CONFIG_PATH = os.path.join(CONFIGS_DIR, 'md_cleaner_config.json')
TITLE_EXTRACTOR_CONFIG_PATH = os.path.join(CONFIGS_DIR, 'title_extractor_config.json')

# 记录所有路径变量
logger.debug("Initialized paths:")
logger.debug(f"WORKSPACE_DIR: {WORKSPACE_DIR}")
logger.debug(f"CONFIGS_DIR: {CONFIGS_DIR}")
logger.debug(f"FILES_DIR: {FILES_DIR}")
logger.debug(f"RAW_FILES_PATH: {RAW_FILES_PATH}")
logger.debug(f"RAW_FILES_METADATA_PATH: {RAW_FILES_METADATA_PATH}")
logger.debug(f"BACKUP_FILES_PATH: {BACKUP_FILES_PATH}")
logger.debug(f"TASKS_PATH: {TASKS_PATH}")
logger.debug(f"CHROMA_DB_PATH: {CHROMA_DB_PATH}")
logger.debug(f"KNOWLEDGE_DIR: {KNOWLEDGE_DIR}")
logger.debug(f"LITERATURE_DATA_PATH: {LITERATURE_DATA_PATH}")
logger.debug(f"COLLECTION_METADATA_FILE: {COLLECTION_METADATA_FILE}")
logger.debug(f"MD_CLEANER_CONFIG_PATH: {MD_CLEANER_CONFIG_PATH}")
logger.debug(f"TITLE_EXTRACTOR_CONFIG_PATH: {TITLE_EXTRACTOR_CONFIG_PATH}")

# 创建必要的目录
os.makedirs(RAW_FILES_PATH, exist_ok=True)
os.makedirs(BACKUP_FILES_PATH, exist_ok=True)
os.makedirs(TASKS_PATH, exist_ok=True)
os.makedirs(CONFIGS_DIR, exist_ok=True)
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
os.makedirs(SUM_FILES_PATH, exist_ok=True)

# 加载配置文件
try:
    # 加载MD清理配置
    if os.path.exists(MD_CLEANER_CONFIG_PATH):
        with open(MD_CLEANER_CONFIG_PATH, 'r', encoding='utf-8') as f:
            MD_CLEANER_CONFIG = json.load(f)
    else:
        logger.error(f"MD cleaner config file not found at {MD_CLEANER_CONFIG_PATH}")
        raise FileNotFoundError(f"必需的配置文件未找到: {MD_CLEANER_CONFIG_PATH}")
        
    # 加载标题提取配置
    if os.path.exists(TITLE_EXTRACTOR_CONFIG_PATH):
        with open(TITLE_EXTRACTOR_CONFIG_PATH, 'r', encoding='utf-8') as f:
            TITLE_EXTRACTOR_CONFIG = json.load(f)
    else:
        logger.error(f"Title extractor config file not found at {TITLE_EXTRACTOR_CONFIG_PATH}")
        raise FileNotFoundError(f"必需的配置文件未找到: {TITLE_EXTRACTOR_CONFIG_PATH}")
    
    # 验证配置文件格式
    if "default" not in TITLE_EXTRACTOR_CONFIG.get("first_non_empty", {}).get("journals", {}):
        raise ValueError("标题提取配置文件缺少 'first_non_empty.journals.default' 策略")
        
except Exception as e:
    logger.error(f"配置文件加载失败: {str(e)}")
    raise RuntimeError(f"配置文件加载失败，应用无法启动: {str(e)}")

# PDF转换器可用性检查
def pdf_converter_available():
    """检查PDF转换器是否可用"""
    try:
        from .utils.pdf_converter.pdf2md import convert_pdf_to_markdown
        return True
    except ImportError:
        logger.warning("PDF转换器不可用")
        return False

# 设置PDF转换器可用性
PDF_CONVERTER_AVAILABLE = pdf_converter_available()

# 允许的文件类型
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'md', 'docx', 'html'}

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS 

# Try to load from .env file
load_dotenv(dotenv_path=WORKSPACE_DIR, override=True)
api_key = os.getenv("OPENAI_API_KEY")

# 基础类标签定义
BASE_TAGS = {
    "期刊类型": "对文献来源期刊的分类",
    "发表时间": "文献发表的年份或时间段",
    "研究领域": "文献所属的研究方向或领域",
    "评分": "文献的评分或重要性分级",
    "其他": "用户自定义分类，可用于特殊目的或临时分类"
}