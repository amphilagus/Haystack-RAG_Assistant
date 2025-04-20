"""
文件上传任务管理器
用于将文件上传任务放入队列中后台处理
"""
import os
import time
import uuid
import json
import threading
import queue
import logging
from datetime import datetime
from pathlib import Path
import tempfile

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TaskManager')

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
    def get_instance(cls, storage_path=None, amphilagus=None):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls(storage_path, amphilagus)
        return cls._instance
    
    def __init__(self, storage_path=None, amphilagus=None):
        """初始化任务管理器"""
        if storage_path is None:
            storage_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tasks')
        
        self.storage_path = Path(storage_path)
        self.amphilagus = amphilagus
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
        except Exception as e:
            logger.error(f"加载任务失败: {str(e)}")
    
    def _save_tasks(self):
        """保存任务到磁盘"""
        try:
            tasks_data = [task.to_dict() for task in self.tasks.values()]
            tasks_file = self.storage_path / 'tasks.json'
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
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
        while True:
            try:
                # 如果当前没有处理任务，则从队列中获取一个
                if not self.is_processing:
                    try:
                        task = self.task_queue.get(timeout=1)  # 1秒超时
                        self.current_task = task
                        self.is_processing = True
                        self._process_task(task)
                    except queue.Empty:
                        # 队列为空，继续等待
                        pass
                else:
                    # 等待当前任务完成
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"工作线程出错: {str(e)}")
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
                self._process_file_upload_task(task)
            else:
                task.error = f"未知任务类型: {task.task_type}"
                task.status = Task.STATUS_FAILED
            
            # 更新任务状态
            if task.status != Task.STATUS_FAILED:
                task.status = Task.STATUS_COMPLETED
                task.progress = 100
            
            task.completed_at = datetime.now()
            self._save_tasks()
            logger.info(f"任务处理完成: {task.task_id}, 状态: {task.status}")
        except Exception as e:
            logger.error(f"处理任务出错: {str(e)}")
            task.status = Task.STATUS_FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            self._save_tasks()
        finally:
            self.is_processing = False
            self.current_task = None
            self.task_queue.task_done()
    
    def _process_file_upload_task(self, task):
        """处理文件上传任务"""

        from .web_app import allowed_file, pdf_converter_available, convert_pdf_to_markdown, clean_markdown, MD_CLEANER_CONFIG
        
        if not self.amphilagus:
            raise ValueError("Amphilagus实例未初始化")
        
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'raw_data')
        os.makedirs(upload_folder, exist_ok=True)
        
        # 获取任务参数
        tags = task.params.get('tags', [])
        description = task.params.get('description', '')
        
        # 获取PDF处理选项
        use_llm = task.params.get('use_llm', 'off') == 'on'
        clean_md = task.params.get('clean_md', 'off') == 'on'
        
        total_files = len(task.files)
        processed_files = 0
        results = {'success': [], 'error': []}
        
        for file_info in task.files:
            filename = file_info.get('filename')
            temp_path = file_info.get('temp_path')
            
            if not os.path.exists(temp_path):
                results['error'].append({
                    "filename": filename,
                    "message": "临时文件不存在"
                })
                continue
            
            if not allowed_file(filename):
                results['error'].append({
                    "filename": filename,
                    "message": f"不支持的文件类型 ({filename})"
                })
                continue
            
            # 检查是否为PDF文件
            is_pdf = filename.lower().endswith('.pdf')
            
            # 如果是PDF文件且PDF转换器可用，转换为Markdown
            if is_pdf and pdf_converter_available:
                logger.info(f"处理PDF文件: {filename}")
                
                # 不使用with语句，手动创建临时目录以便于调试
                import tempfile
                # 使用mkdtemp()创建一个持久的临时目录
                temp_output_dir = tempfile.mkdtemp(prefix=f"pdf_convert_{os.path.splitext(filename)[0]}_")
                logger.info(f"创建临时目录: {temp_output_dir}")
                
                # 调用PDF转换器
                conversion_success = convert_pdf_to_markdown(
                    input_path=temp_path,
                    output_dir=temp_output_dir,
                    use_llm=use_llm  # 使用用户选择的LLM选项
                )
                
                # 处理转换结果
                if conversion_success:
                    # 基本文件名（不含扩展名）
                    base_name = os.path.splitext(filename)[0]
                    
                    # 查找生成的markdown文件和meta.json文件
                    md_file_path = os.path.join(temp_output_dir, base_name, f"{base_name}.md")
                    meta_json_path = os.path.join(temp_output_dir, base_name, f"{base_name}_meta.json")
                    
                    # 如果meta.json文件存在，提取标题
                    if os.path.exists(meta_json_path):
                        try:
                            with open(meta_json_path, 'r', encoding='utf-8') as f:
                                meta_data = json.load(f)
                                if meta_data.get('table_of_contents') and len(meta_data['table_of_contents']) > 0:
                                    # 遍历table_of_contents直到找到第一个非空标题
                                    for toc_item in meta_data['table_of_contents']:
                                        raw_title = toc_item['title']
                                        if raw_title and raw_title.strip():
                                            # 处理标题，移除换行符
                                            title = raw_title.replace('\n', ' ').strip()
                                            break
                                    else:
                                        # 如果未找到有效标题，使用默认标题
                                        title = base_name
                        except (json.JSONDecodeError, KeyError, IndexError) as e:
                            logger.error(f"从meta.json提取标题时出错: {str(e)}")
                            title = base_name
                    else:
                        # 直接报错 终止程序
                        raise ValueError(f"未找到meta.json文件，理论路径为：{meta_json_path}，临时目录：{temp_output_dir}")
                        
                    # 安全处理标题，去除非法字符
                    from werkzeug.utils import secure_filename
                    safe_title = secure_filename(title)
                    if not safe_title:
                        safe_title = base_name
                    
                    # 如果markdown文件存在
                    if os.path.exists(md_file_path):
                        # 读取原始Markdown内容
                        with open(md_file_path, 'r', encoding='utf-8') as src:
                            md_content = src.read()

                        # 如果选择了清理选项，则应用清理规则
                        if clean_md and 'MD_CLEANER_CONFIG' in locals() and MD_CLEANER_CONFIG:
                            try:
                                # 查找匹配的期刊类型标签
                                journal_type = None
                                # 创建小写版本的配置键映射到原始键
                                lowercase_config_keys = {k.lower(): k for k in MD_CLEANER_CONFIG.keys()}
                                
                                for tag in tags:
                                    # 检查标签是否是已配置的期刊类型（忽略大小写）
                                    if tag.lower() in lowercase_config_keys:
                                        # 使用原始大小写的配置键
                                        journal_type = lowercase_config_keys[tag.lower()]
                                        break
                                
                                # 如果找到匹配的期刊类型，应用对应的清理规则
                                if journal_type:
                                    logger.info(f"应用 {journal_type} 期刊的清理规则")
                                    rules = MD_CLEANER_CONFIG[journal_type]
                                    md_content = clean_markdown(md_content, rules)
                                else:
                                    logger.info("未找到匹配的期刊类型，不应用清理规则")
                                    clean_md = False
                            except Exception as e:
                                logger.error(f"清理Markdown时出错: {str(e)}")
                        
                        # 生成新的文件名
                        md_filename = f"{safe_title}.md"
                        md_file_path = os.path.join(temp_output_dir, md_filename)
                        with open(md_file_path, 'w', encoding='utf-8') as dst:
                            dst.write(md_content)

                        # 添加到数据库
                        md_description = description or f"由PDF文件自动转换生成{'，已进行内容清理' if clean_md else ''}"
                        add_result = self.amphilagus.add_raw_data(md_file_path, tags, md_description)
                        
                        if add_result:
                            results['success'].append({
                                "filename": md_filename,
                                "message": f"PDF已转换为Markdown: {md_filename}"
                            })
                        else:
                            results['error'].append({
                                "filename": md_filename,
                                "message": "PDF转换成功但添加到数据库失败"
                            })
                    else:
                        results['error'].append({
                            "filename": filename,
                            "message": "PDF转换后未找到Markdown文件"
                        })
                else:
                    # PDF转换失败，直接报错
                    raise ValueError(f"PDF转换失败!!!")
                
                # 如果处理成功且不想保留临时文件，可以取消下面的注释手动删除
                import shutil
                shutil.rmtree(temp_output_dir, ignore_errors=True)
                logger.info(f"已删除临时目录: {temp_output_dir}")

            else:
                # 非PDF文件或PDF转换器不可用时的常规处理
                target_path = os.path.join(upload_folder, filename)
                import shutil
                shutil.copy2(temp_path, target_path)
                
                # 添加到数据库
                add_result = self.amphilagus.add_raw_data(target_path, tags, description)
                
                if add_result:
                    results['success'].append({
                        "filename": filename,
                        "message": "文件上传成功"
                    })
                else:
                    results['error'].append({
                        "filename": filename,
                        "message": "文件保存成功但添加到数据库失败"
                    })
            
            # 清理临时文件
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as e:
                logger.error(f"清理临时文件时出错: {str(e)}")
            
            # 更新进度
            processed_files += 1
            task.progress = int((processed_files / total_files) * 100)
            
        # 保存结果
        task.result = {
            "total": total_files,
            "success_count": len(results['success']),
            "error_count": len(results['error']),
            "details": results
        }

    
    def create_task(self, task_type, files=None, params=None):
        """创建新任务"""
        task = Task(task_type=task_type, files=files, params=params)
        self.tasks[task.task_id] = task
        self.task_queue.put(task)
        self._save_tasks()
        logger.info(f"创建新任务: {task.task_id}, 类型: {task.task_type}")
        return task
    
    def get_task(self, task_id):
        """获取任务"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self):
        """获取所有任务"""
        return list(self.tasks.values())
    
    def get_recent_tasks(self, limit=10):
        """获取最近的任务"""
        tasks = list(self.tasks.values())
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks[:limit]
    
    def get_task_status(self, task_id):
        """获取任务状态"""
        task = self.get_task(task_id)
        if task:
            return {
                'task_id': task.task_id,
                'status': task.status,
                'progress': task.progress,
                'error': task.error
            }
        return None
    
    def delete_task(self, task_id):
        """删除任务"""
        if task_id in self.tasks:
            # 不能删除正在处理的任务
            if self.current_task and self.current_task.task_id == task_id and self.current_task.status == Task.STATUS_PROCESSING:
                return False, "不能删除正在处理的任务"
            
            del self.tasks[task_id]
            self._save_tasks()
            logger.info(f"删除任务: {task_id}")
            return True, "任务已删除"
        
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