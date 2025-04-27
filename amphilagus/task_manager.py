"""
文件上传任务管理器
用于将文件上传任务放入队列中后台处理
"""
import logging
import os
import time
import uuid
import json
import threading
import queue
from datetime import datetime
from pathlib import Path
import tempfile

from .logger import get_logger
from .file_manager import FileManager, Tag
from werkzeug.utils import secure_filename
from . import config
from .utils.pdf_converter.pdf2md import convert_pdf_to_markdown

# 配置日志
logger = get_logger('task_manager')

class Task:
    """任务类，表示一个文件处理任务"""
    
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    
    def __init__(self, task_id=None, task_type=None, files=None, params=None):
        self.task_id = task_id or str(uuid.uuid4())
        self.task_type = task_type
        self.status = self.STATUS_PENDING
        self.progress = 0
        self.files = files or []
        self.params = params or {}
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.error = None
        self.result = {}
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'status': self.status,
            'progress': self.progress,
            'file_count': len(self.files),
            'params': self.params,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error': self.error,
            'result': self.result
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建任务"""
        task = cls(
            task_id=data.get('task_id'),
            task_type=data.get('task_type'),
            files=data.get('files', []),
            params=data.get('params', {})
        )
        task.status = data.get('status', cls.STATUS_PENDING)
        task.progress = data.get('progress', 0)
        task.created_at = datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None
        task.started_at = datetime.fromisoformat(data.get('started_at')) if data.get('started_at') else None
        task.completed_at = datetime.fromisoformat(data.get('completed_at')) if data.get('completed_at') else None
        task.error = data.get('error')
        task.result = data.get('result', {})
        return task


class TaskManager:
    """任务管理器，用于管理文件上传和处理任务"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls, storage_path=None, file_manager=None, db_manager=None):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls(storage_path, file_manager, db_manager)
        return cls._instance
    
    def __init__(self, storage_path=None, file_manager=None, db_manager=None):
        """初始化任务管理器"""
        if storage_path is None:
            storage_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tasks')
        
        self.storage_path = Path(storage_path)
        self.file_manager = file_manager
        self.db_manager = db_manager
        self.task_queue = queue.Queue()
        self.tasks = {}  # 任务ID到任务对象的映射
        self.current_task = None
        self.is_processing = False
        self.worker_thread = None
        
        # 确保存储目录存在
        os.makedirs(self.storage_path, exist_ok=True)
        
        # 从磁盘加载任务
        self._load_tasks()
        
        # 启动工作线程
        self._start_worker()
        
        logger.info(f"任务管理器初始化完成，存储路径: {self.storage_path}")
    
    def _load_tasks(self):
        """从磁盘加载任务"""
        try:
            tasks_file = self.storage_path / 'tasks.json'
            if tasks_file.exists():
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    tasks_data = json.load(f)
                    for task_data in tasks_data:
                        task = Task.from_dict(task_data)
                        self.tasks[task.task_id] = task
                logger.info(f"从磁盘加载了 {len(self.tasks)} 个任务")
            else:
                logger.debug(f"任务文件不存在：{tasks_file}")
        except Exception as e:
            logger.error(f"加载任务失败: {str(e)}")
    
    def _save_tasks(self):
        """保存任务到磁盘"""
        try:
            tasks_data = [task.to_dict() for task in self.tasks.values()]
            tasks_file = self.storage_path / 'tasks.json'
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
            logger.debug(f"已将 {len(tasks_data)} 个任务保存到磁盘")
        except Exception as e:
            logger.error(f"保存任务失败: {str(e)}")
    
    def _start_worker(self):
        """启动工作线程"""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            logger.info("工作线程已启动")
    
    def _worker_loop(self):
        """工作线程主循环"""
        logger.debug("工作线程主循环开始运行")
        while True:
            try:
                # 如果当前没有处理任务，则从队列中获取一个
                if not self.is_processing:
                    try:
                        task = self.task_queue.get(timeout=1)  # 1秒超时
                        self.current_task = task
                        self.is_processing = True
                        logger.debug(f"从队列中获取到任务：{task.task_id}")
                        self._process_task(task)
                    except queue.Empty:
                        # 队列为空，继续等待
                        pass
                else:
                    # 等待当前任务完成
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"工作线程处理出错: {str(e)}")
                self.is_processing = False
                self.current_task = None
    
    def _process_task(self, task):
        """处理任务"""
        try:
            logger.info(f"开始处理任务: {task.task_id}, 类型: {task.task_type}")
            task.status = Task.STATUS_PROCESSING
            task.started_at = datetime.now()
            self._save_tasks()
            
            # 根据任务类型处理
            if task.task_type == 'file_upload':
                logger.info(f"处理文件上传任务: {task.task_id}, 文件数: {len(task.files)}")
                self._process_file_upload_task(task)
            elif task.task_type == 'batch_embed':
                logger.info(f"处理批量嵌入任务: {task.task_id}")
                self._process_batch_embed_task(task)
            elif task.task_type == 'batch_clean':
                logger.info(f"处理批量清洗任务: {task.task_id}")
                self._process_batch_clean_task(task)
            else:
                task.error = f"未知任务类型: {task.task_type}"
                task.status = Task.STATUS_FAILED
                logger.error(f"未知任务类型: {task.task_type}")
            
            # 更新任务状态
            if task.status != Task.STATUS_FAILED:
                task.status = Task.STATUS_COMPLETED
                task.progress = 100
                logger.info(f"任务 {task.task_id} 处理完成")
            else:
                logger.error(f"任务 {task.task_id} 处理失败: {task.error}")
            
            task.completed_at = datetime.now()
            self._save_tasks()
            logger.info(f"任务处理完成: {task.task_id}, 状态: {task.status}, 耗时: {(task.completed_at - task.started_at).total_seconds():.2f}秒")
        except Exception as e:
            logger.error(f"处理任务 {task.task_id} 出错: {str(e)}")
            task.status = Task.STATUS_FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            self._save_tasks()
        finally:
            self.is_processing = False
            self.current_task = None
            self.task_queue.task_done()
            logger.debug(f"任务 {task.task_id} 处理结束，任务队列剩余任务数: {self.task_queue.qsize()}")
    
    def _process_file_upload_task(self, task):
        """处理文件上传任务"""

        if not self.file_manager:
            logger.error("FileManager实例未初始化")
            raise ValueError("FileManager实例未初始化")
        
        if not self.db_manager:
            logger.error("DatabaseManager实例未初始化")
            raise ValueError("DatabaseManager实例未初始化")
        
        # 获取任务参数
        tags = task.params.get('tags', [])
        description = task.params.get('description', '')
        
        # 获取PDF处理选项，默认值改为'on'
        use_llm = task.params.get('use_llm', 'on') == 'on'
        clean_md = task.params.get('clean_md', 'off') == 'on'
        
        logger.info(f"文件上传任务参数: 标签={tags}, 使用LLM={use_llm}, 清理MD={clean_md}")
        
        total_files = len(task.files)
        processed_files = 0
        results = {'success': [], 'error': []}
        
        for file_info in task.files:
            filename = file_info.get('filename')
            temp_path = file_info.get('temp_path')
            
            logger.info(f"开始处理文件: {filename}")
            
            if not os.path.exists(temp_path):
                logger.error(f"临时文件不存在: {temp_path}")
                results['error'].append({
                    "filename": filename,
                    "message": "临时文件不存在"
                })
                continue
            
            if not config.allowed_file(filename):
                logger.warning(f"不支持的文件类型: {filename}")
                results['error'].append({
                    "filename": filename,
                    "message": f"不支持的文件类型 ({filename})"
                })
                continue
            
            # 检查是否为PDF文件
            is_pdf = filename.lower().endswith('.pdf')
            
            # 如果是PDF文件且PDF转换器可用，转换为Markdown
            if is_pdf and config.PDF_CONVERTER_AVAILABLE:
                logger.info(f"处理PDF文件: {filename}")
                
                # 不使用with语句，手动创建临时目录以便于调试
                import tempfile
                # 使用mkdtemp()创建一个持久的临时目录
                temp_output_dir = tempfile.mkdtemp(prefix=f"pdf_convert_{os.path.splitext(filename)[0]}_")
                logger.info(f"创建临时目录: {temp_output_dir}")
                
                # 调用PDF转换器
                logger.debug(f"调用PDF转换器，输入路径: {temp_path}, 输出目录: {temp_output_dir}, 使用LLM: {use_llm}")
                conversion_success = convert_pdf_to_markdown(
                    input_path=temp_path,
                    output_dir=temp_output_dir,
                    use_llm=use_llm  # 使用用户选择的LLM选项
                )
                
                # 处理转换结果
                if conversion_success:
                    logger.info(f"PDF文件 {filename} 转换成功")
                    # 基本文件名（不含扩展名）
                    base_name = os.path.splitext(filename)[0]
                    
                    # 查找生成的markdown文件和meta.json文件
                    md_file_path = os.path.join(temp_output_dir, base_name, f"{base_name}.md")
                    meta_json_path = os.path.join(temp_output_dir, base_name, f"{base_name}_meta.json")
                    
                    logger.debug(f"查找生成的文件: MD={md_file_path}, Meta={meta_json_path}")
                    
                    # 如果meta.json文件存在，提取标题
                    if os.path.exists(meta_json_path):
                        try:
                            with open(meta_json_path, 'r', encoding='utf-8') as f:
                                meta_data = json.load(f)
                                # 确定使用哪种标题提取策略
                                method = "first_non_empty"  # 目前只支持first_non_empty方法
                                journal = "default"  # 默认期刊配置
                                
                                # 查找匹配的期刊类型标签
                                # 创建小写版本的配置键映射到原始键
                                journals = config.TITLE_EXTRACTOR_CONFIG.get(method, {}).get("journals", {})
                                lowercase_journal_keys = {k.lower(): k for k in journals.keys()}
                                
                                for tag in tags:
                                    # 检查标签是否是已配置的期刊类型（忽略大小写）
                                    if tag.lower() in lowercase_journal_keys:
                                        # 使用原始大小写的配置键
                                        journal = lowercase_journal_keys[tag.lower()]
                                        logger.debug(f"找到匹配的期刊: {journal}")
                                        break
                                
                                # 获取策略配置
                                journal_config = journals.get(journal, journals.get("default", {}))
                                start_index = journal_config.get("start_index", 0)
                                logger.info(f"使用标题提取方法: {method}, 期刊: {journal}, 起始索引: {start_index} ({journal_config.get('description', '无描述')})")
                                
                                # 基于策略提取标题
                                title = base_name  # 默认使用基本文件名
                                
                                # 从目录中提取标题，使用start_index参数
                                if meta_data.get('table_of_contents') and len(meta_data['table_of_contents']) > 0:
                                    # 找出所有非空标题
                                    non_empty_titles = []
                                    for toc_item in meta_data['table_of_contents']:
                                        raw_title = toc_item.get('title', '')
                                        if raw_title and raw_title.strip():
                                            non_empty_titles.append(raw_title)
                                    
                                    # 根据start_index获取标题
                                    if len(non_empty_titles) > start_index:
                                        # 处理标题，移除换行符
                                        raw_title = non_empty_titles[start_index]
                                        title = raw_title.replace('\n', ' ').strip()
                                        logger.debug(f"从meta.json提取到标题 (索引 {start_index}): {title}")
                                    else:
                                        logger.warning(f"meta.json中找不到索引为 {start_index} 的非空标题，使用默认标题: {title}")
                                else:
                                    logger.warning(f"meta.json中没有table_of_contents或为空，使用默认标题: {title}")
                        except (json.JSONDecodeError, KeyError, IndexError) as e:
                            logger.error(f"从meta.json提取标题时出错: {str(e)}")
                            title = base_name
                    else:
                        # 直接报错 终止程序
                        logger.error(f"未找到meta.json文件，理论路径为：{meta_json_path}，临时目录：{temp_output_dir}")
                        raise ValueError(f"未找到meta.json文件，理论路径为：{meta_json_path}，临时目录：{temp_output_dir}")
                        
                    # 安全处理标题，去除非法字符
                    safe_title = secure_filename(title)
                    if not safe_title:
                        safe_title = base_name
                        logger.warning(f"安全处理后标题为空，使用基本文件名: {base_name}")
                    else:
                        logger.debug(f"安全处理后的标题: {safe_title}")
                    
                    # 如果markdown文件存在
                    if os.path.exists(md_file_path):
                        logger.debug(f"找到markdown文件: {md_file_path}")
                        # 读取原始Markdown内容
                        with open(md_file_path, 'r', encoding='utf-8') as src:
                            md_content = src.read()

                        # 如果选择了清理选项，则应用清理规则
                        if clean_md:
                            try:
                                # 使用文件管理器清理Markdown内容
                                logger.debug(f"请求清理Markdown，使用标签: {tags}")
                                original_content = md_content
                                md_content = self.file_manager.clean_markdown_content(md_content, tags)
                                
                                # 检查内容是否有变化
                                if md_content == original_content:
                                    logger.info("内容未发生变化，没有应用清理规则")
                                    clean_md = False
                                else:
                                    logger.info("已应用Markdown清理规则")
                            except Exception as e:
                                logger.error(f"清理Markdown时出错: {str(e)}")
                                clean_md = False
                        
                        # 生成新的文件名
                        md_filename = f"{safe_title}.md"
                        md_file_path = os.path.join(temp_output_dir, md_filename)
                        logger.debug(f"保存处理后的markdown文件: {md_file_path}")
                        with open(md_file_path, 'w', encoding='utf-8') as dst:
                            dst.write(md_content)

                        # 添加到数据库
                        md_description = description or f"由PDF文件自动转换生成{'，已进行内容清理' if clean_md else ''}"
                        logger.info(f"添加文件到数据库: {md_filename}, 描述: {md_description}")
                        add_result = self.file_manager.add_file(md_file_path, temp_path, tags, md_description)
                        
                        if add_result:
                            logger.info(f"文件 {md_filename} 添加成功")
                            results['success'].append({
                                "filename": md_filename,
                                "message": f"PDF已转换为Markdown: {md_filename}"
                            })
                        else:
                            logger.error(f"文件 {md_filename} 添加到数据库失败")
                            results['error'].append({
                                "filename": md_filename,
                                "message": "PDF转换成功但添加到数据库失败"
                            })
                    else:
                        logger.error(f"未找到转换后的Markdown文件: {md_file_path}")
                        results['error'].append({
                            "filename": filename,
                            "message": "PDF转换后未找到Markdown文件"
                        })
                else:
                    # PDF转换失败，直接报错
                    logger.error(f"PDF文件 {filename} 转换失败")
                    raise ValueError(f"PDF转换失败!!!")
                
                # DEBUG模式会保留临时文件
                # 检查logger记录等级是否为DEBUG级，如果是，不删除临时目录
                if logger.getEffectiveLevel() <= logging.DEBUG:
                    logger.debug(f"DEBUG模式下保留临时目录: {temp_output_dir}")
                    continue
                import shutil
                shutil.rmtree(temp_output_dir, ignore_errors=True)
                logger.info(f"已删除临时目录: {temp_output_dir}")

            else:
                # 非PDF文件或PDF转换器不可用时直接报错
                logger.error(f"文件 {filename} 不是PDF文件或PDF转换器不可用")
                results['error'].append({
                    "filename": filename,
                    "message": "不是PDF文件或PDF转换器不可用"
                })
                raise ValueError(f"文件 {filename} 不是PDF文件或PDF转换器不可用")

            # 清理临时文件
            try:
                if os.path.exists(temp_path):
                    logger.debug(f"清理临时文件: {temp_path}")
                    os.remove(temp_path)
            except Exception as e:
                logger.error(f"清理临时文件 {temp_path} 时出错: {str(e)}")
            
            # 更新进度
            processed_files += 1
            task.progress = int((processed_files / total_files) * 100)
            logger.debug(f"文件处理进度: {task.progress}% ({processed_files}/{total_files})")
            
        # 保存结果
        task.result = {
            "total": total_files,
            "success_count": len(results['success']),
            "error_count": len(results['error']),
            "details": results
        }
        logger.info(f"文件上传任务完成: 总计={total_files}, 成功={len(results['success'])}, 失败={len(results['error'])}")

    def _process_batch_embed_task(self, task):
        """处理批量嵌入任务"""
        # 导入依赖项
        try:
            # 动态导入RAGPipeline，避免循环导入
            from .pipeline.basic import RAGPipeline
            from .database.collection_metadata import get_embedding_model
        except ImportError:
            logger.error("无法导入RAGPipeline，请确保RAG组件已正确安装")
            task.error = "无法导入RAGPipeline，请确保RAG组件已正确安装"
            task.status = Task.STATUS_FAILED
            return
        
        # 获取任务参数
        collection_name = task.params.get('collection_name')
        chunk_size = task.params.get('chunk_size', 1000)
        chunk_overlap = task.params.get('chunk_overlap', 200)
        check_duplicates = task.params.get('check_duplicates', False)
        file_paths = task.params.get('file_paths', [])
        
        # 新增参数
        create_collection = task.params.get('create_collection', False)
        embedding_model = task.params.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
        reset_collection = task.params.get('reset_collection', False)
        
        logger.info(f"批量嵌入任务参数: 集合名称={collection_name}, 块大小={chunk_size}, 块重叠={chunk_overlap}, "
                   f"检查重复={check_duplicates}, 文件数={len(file_paths)}, 创建集合={create_collection}, "
                   f"嵌入模型={embedding_model}, 重置集合={reset_collection}")
        
        if not collection_name:
            logger.error("未指定集合名称")
            task.error = "未指定集合名称"
            task.status = Task.STATUS_FAILED
            return
            
        if not file_paths:
            logger.error("未指定文件路径")
            task.error = "未指定文件路径"
            task.status = Task.STATUS_FAILED
            return
        
        # 更新进度
        task.progress = 5
        self._save_tasks()
        logger.debug(f"嵌入任务开始进度: {task.progress}%")
        
        # 检查是否需要创建新集合
        if create_collection:
            try:
                # 检查集合是否已存在
                existing_model = get_embedding_model(collection_name)
                
                # 如果集合存在且不需要重置，使用现有集合
                if existing_model and not reset_collection:
                    logger.info(f"集合 '{collection_name}' 已存在，使用现有嵌入模型: {existing_model}")
                    embedding_model = existing_model
                else:
                    # 创建或重置集合
                    logger.info(f"创建/重置集合 '{collection_name}' 使用嵌入模型: {embedding_model}")
                    
                    # 初始化 RAGPipeline 实例来创建集合
                    chroma_db_path = config.CHROMA_DB_PATH if hasattr(config, 'CHROMA_DB_PATH') else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'chroma_db')
                    
                    pipeline = RAGPipeline(
                        embedding_model=embedding_model,
                        collection_name=collection_name,
                        persist_dir=chroma_db_path,
                        reset_collection=reset_collection,
                        hard_reset=True,
                        use_llm=False  # 不使用LLM
                    )
                    
                    logger.info(f"成功创建/初始化集合 '{collection_name}'")
                    
                # 更新进度
                task.progress = 10
                self._save_tasks()
            except Exception as e:
                logger.error(f"创建/初始化集合 '{collection_name}' 时出错: {str(e)}")
                task.error = f"创建/初始化集合失败: {str(e)}"
                task.status = Task.STATUS_FAILED
                return
        else:
            # 更新进度
            task.progress = 10
            self._save_tasks()
        
        try:
            # 调用数据库管理器的embed_files方法处理嵌入
            logger.info(f"开始执行嵌入，集合: {collection_name}, 文件数: {len(file_paths)}")
            success, message, stats = self.db_manager.embed_files(
                collection_name=collection_name,
                file_paths=file_paths,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                check_duplicates=check_duplicates
            )
            
            # 更新进度
            task.progress = 90
            self._save_tasks()
            logger.debug(f"嵌入任务完成进度: {task.progress}%")
            
            # 设置任务结果
            task.result = {
                "success": success,
                "message": message,
                "stats": stats
            }
            
            # 如果失败，设置错误信息
            if not success:
                logger.error(f"嵌入任务失败: {message}")
                task.error = message
                task.status = Task.STATUS_FAILED
            else:
                logger.info(f"嵌入任务成功: {message}")
                
        except Exception as e:
            logger.error(f"批量嵌入任务处理失败: {str(e)}")
            task.error = f"批量嵌入任务处理失败: {str(e)}"
            task.status = Task.STATUS_FAILED

    def _process_batch_clean_task(self, task):
        """处理批量清洗任务"""
        if not self.file_manager:
            logger.error("FileManager实例未初始化")
            task.error = "FileManager实例未初始化"
            task.status = Task.STATUS_FAILED
            return

        # 获取任务参数
        files = task.params.get('files', [])
        
        if not files:
            logger.error("未指定文件列表")
            task.error = "未指定文件列表"
            task.status = Task.STATUS_FAILED
            return
        
        logger.info(f"开始批量清洗任务，文件数: {len(files)}")
        
        # 初始化结果
        results = []
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        # 更新进度初始值
        task.progress = 10
        self._save_tasks()
        
        # 计算每个文件的进度增量
        progress_per_file = 80 / len(files) if len(files) > 0 else 0
        
        # 逐个清洗文件
        for index, filename in enumerate(files):
            try:
                logger.debug(f"开始清洗文件 ({index+1}/{len(files)}): {filename}")
                
                # 判断是否为Markdown文件
                if not filename.lower().endswith('.md'):
                    logger.debug(f"文件 {filename} 不是Markdown文件，跳过")
                    skipped_count += 1
                    results.append({
                        'filename': filename,
                        'status': 'skipped',
                        'message': '不是Markdown文件'
                    })
                    continue
                
                # 调用文件管理器的单个文件清洗方法
                if self.file_manager.clean_markdown_file(filename):
                    logger.info(f"成功清洗文件: {filename}")
                    
                    # 更新文件描述，添加清洗标记
                    try:
                        file_metadata = self.file_manager.get_file_metadata(filename)
                        if file_metadata:
                            # 避免重复添加清洗标记
                            if "已进行内容清理" not in file_metadata.description:
                                file_metadata.description += "，已进行内容清理"
                                self.file_manager._save_metadata()
                                logger.debug(f"已更新文件 {filename} 的描述，添加了清洗标记")
                    except Exception as e:
                        logger.warning(f"更新文件 {filename} 描述时出错: {str(e)}")
                    
                    success_count += 1
                    results.append({
                        'filename': filename,
                        'status': 'success',
                        'message': '清洗成功'
                    })
                else:
                    logger.debug(f"文件 {filename} 无需清洗或清洗失败")
                    skipped_count += 1
                    results.append({
                        'filename': filename,
                        'status': 'skipped',
                        'message': '无需清洗或清洗失败'
                    })
            except Exception as e:
                logger.error(f"清洗文件 {filename} 时出错: {str(e)}")
                error_count += 1
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'message': str(e)
                })
            
            # 更新进度
            task.progress = 10 + int((index + 1) * progress_per_file)
            self._save_tasks()
        
        # 设置任务结果
        summary_message = f"批量清洗完成: 总数={len(files)}, 成功={success_count}, 跳过={skipped_count}, 错误={error_count}"
        logger.info(summary_message)
        
        task.result = {
            'success_count': success_count,
            'error_count': error_count,
            'skipped_count': skipped_count,
            'details': results,
            'message': summary_message
        }
        
        # 设置最终进度
        task.progress = 90
        self._save_tasks()

    
    def create_task(self, task_type, files=None, params=None):
        """创建新任务"""
        task = Task(task_type=task_type, files=files, params=params)
        self.tasks[task.task_id] = task
        self.task_queue.put(task)
        self._save_tasks()
        logger.info(f"创建新任务: {task.task_id}, 类型: {task.task_type}, 文件数: {len(files) if files else 0}")
        return task
    
    def get_task(self, task_id):
        """获取任务"""
        logger.debug(f"获取任务: {task_id}")
        return self.tasks.get(task_id)
    
    def get_all_tasks(self):
        """获取所有任务"""
        logger.debug(f"获取所有任务，总数: {len(self.tasks)}")
        return list(self.tasks.values())
    
    def get_recent_tasks(self, limit=10):
        """获取最近的任务"""
        tasks = list(self.tasks.values())
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        logger.debug(f"获取最近 {limit} 个任务")
        return tasks[:limit]
    
    def get_task_status(self, task_id):
        """获取任务状态"""
        task = self.get_task(task_id)
        if task:
            logger.debug(f"获取任务 {task_id} 状态: {task.status}, 进度: {task.progress}%")
            return {
                'task_id': task.task_id,
                'status': task.status,
                'progress': task.progress,
                'error': task.error
            }
        logger.warning(f"获取任务状态失败，任务不存在: {task_id}")
        return None
    
    def delete_task(self, task_id):
        """删除任务"""
        if task_id in self.tasks:
            # 不能删除正在处理的任务
            if self.current_task and self.current_task.task_id == task_id and self.current_task.status == Task.STATUS_PROCESSING:
                logger.warning(f"无法删除正在处理的任务: {task_id}")
                return False, "不能删除正在处理的任务"
            
            del self.tasks[task_id]
            self._save_tasks()
            logger.info(f"删除任务: {task_id}")
            return True, "任务已删除"
        
        logger.warning(f"删除任务失败，任务不存在: {task_id}")
        return False, "任务不存在"
    
    def clear_completed_tasks(self):
        """清除已完成的任务"""
        completed_task_ids = [
            task_id for task_id, task in self.tasks.items()
            if task.status in [Task.STATUS_COMPLETED, Task.STATUS_FAILED]
        ]
        
        for task_id in completed_task_ids:
            del self.tasks[task_id]
        
        self._save_tasks()
        logger.info(f"清除了 {len(completed_task_ids)} 个已完成的任务")
        return len(completed_task_ids) 