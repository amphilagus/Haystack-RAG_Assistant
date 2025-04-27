from . import config
from .file_manager import FileManager
from .database.manager import DatabaseManager
from .task_manager import TaskManager
from .pipeline.manager import PipelineManager

from .logger import get_logger

# Configure logger based on environment variable
logger = get_logger('manager')
logger.info("初始化模块管理器")

# Initialize the FileManager directly
file = FileManager(raw_files_dir=config.RAW_FILES_PATH, backup_files_dir=config.BACKUP_FILES_PATH)

# 初始化数据库管理器
database = DatabaseManager(chroma_db_path=config.CHROMA_DB_PATH)

# 初始化任务管理器
task = TaskManager(config.TASKS_PATH, file, database)

# 初始化管道管理器
pipeline = PipelineManager()