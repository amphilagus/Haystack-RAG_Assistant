"""
任务管理相关路由模块
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from ... import manager

# 创建Blueprint
tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@tasks_bp.route('/')
def view_tasks():
    """查看所有任务"""
    tasks = manager.task.get_all_tasks()
    # 按创建时间倒序排序
    tasks.sort(key=lambda t: t.created_at, reverse=True)
    return render_template('tasks.html', tasks=tasks)

@tasks_bp.route('/<task_id>')
def view_task(task_id):
    """查看单个任务详情"""
    task = manager.task.get_task(task_id)
    if not task:
        flash('任务不存在', 'error')
        return redirect(url_for('tasks.view_tasks'))
    return render_template('task_details.html', task=task)

@tasks_bp.route('/api/<task_id>/status')
def get_task_status(task_id):
    """获取任务状态 API"""
    status = manager.task.get_task_status(task_id)
    if status:
        return jsonify(status)
    return jsonify({"error": "任务不存在"}), 404

@tasks_bp.route('/api/<task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """删除任务 API"""
    success, message = manager.task.delete_task(task_id)
    return jsonify({"success": success, "message": message})

@tasks_bp.route('/api/clear-completed', methods=['POST'])
def clear_completed_tasks():
    """清除已完成的任务 API"""
    count = manager.task.clear_completed_tasks()
    return jsonify({"success": True, "message": f"已清除 {count} 个已完成的任务"}) 