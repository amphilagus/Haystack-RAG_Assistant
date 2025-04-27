#!/usr/bin/env python
"""
脚本用于更新模板文件，将旧的URL引用改为带有Blueprint前缀的新格式。
"""
import os
import re
from pathlib import Path

# 映射关系：旧的endpoint名称 -> 新的带有Blueprint前缀的endpoint名称
ENDPOINT_MAPPING = {
    'index': 'base.index',
    'reload_config': 'base.reload_config',
    
    'list_files': 'files.list_files',
    'filter_files': 'files.filter_files',
    'upload_file': 'files.upload_file',
    'delete_file': 'files.delete_file',
    'batch_delete_files': 'files.batch_delete_files',
    'batch_embed_files': 'files.batch_embed_files',
    'manage_file_tags': 'files.manage_file_tags',
    'file_details': 'files.file_details',
    'view_backup_files': 'files.view_backup_files',
    'update_description': 'files.update_description',
    'rename_file': 'files.rename_file',
    'batch_clean_files': 'files.batch_clean_files',
    
    'database_dashboard': 'database.database_dashboard',
    'reload_database': 'database.reload_database',
    'delete_collection': 'database.delete_collection',
    
    'agent_assistant': 'agent.agent_assistant',
    'agent_assistant_chat': 'agent.agent_assistant_chat',
    'agent_ref_assistant_process': 'agent.agent_ref_assistant_process',
    
    'list_tags': 'tags.list_tags',
    'restore_preset_tags': 'tags.restore_preset_tags',
    'create_tag': 'tags.create_tag',
    'delete_tag': 'tags.delete_tag',
    
    'view_tasks': 'tasks.view_tasks',
    'view_task': 'tasks.view_task',
    'get_task_status': 'tasks.get_task_status',
    'delete_task': 'tasks.delete_task',
    'clear_completed_tasks': 'tasks.clear_completed_tasks',
    
    'list_literature': 'literature.list_literature',
    'filter_literature': 'literature.filter_literature',
    'sync_literature_tags': 'literature.sync_literature_tags',
    'update_literature_files': 'literature.update_literature_files',
    
    'api_list_files': 'api.api_list_files',
    'api_list_tags': 'api.api_list_tags',
    'api_list_collections': 'api.api_list_collections',
}

def update_template_file(file_path):
    """更新单个模板文件中的URL引用"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换所有匹配的URL引用
    updated_content = content
    for old_endpoint, new_endpoint in ENDPOINT_MAPPING.items():
        pattern = rf"url_for\([\'\"]({old_endpoint})[\'\"]"
        replacement = rf"url_for(\'\1\')"
        
        # 检查模式匹配后再替换，避免重复替换已经更新过的引用
        if re.search(pattern, updated_content):
            updated_content = re.sub(pattern, f"url_for('{new_endpoint}'", updated_content)
    
    # 只有在内容有变化时才写入文件
    if content != updated_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"Updated: {file_path}")
        return True
    return False

def update_all_templates(templates_dir):
    """更新所有模板文件"""
    templates_path = Path(templates_dir)
    count = 0
    
    # 遍历所有HTML文件
    for file_path in templates_path.glob('**/*.html'):
        if update_template_file(file_path):
            count += 1
    
    print(f"Total files updated: {count}")

if __name__ == "__main__":
    # 确定模板目录路径
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    templates_dir = project_root / 'amphilagus' / 'templates'
    
    print(f"Updating templates in: {templates_dir}")
    update_all_templates(templates_dir) 