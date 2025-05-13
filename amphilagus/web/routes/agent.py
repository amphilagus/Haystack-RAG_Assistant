"""
智能助手相关路由模块
"""
import datetime
import json
import ast
from flask import Blueprint, render_template, request, jsonify, url_for, current_app
from typing import Tuple, Dict, Any, Optional, Union, Type

from ... import manager
from ...logger import get_logger
from ...agent.assistant import Collection_QA_Assistant, Collection_Ref_Assistant, Collection_Sum_Assistant, Collection_Chat_Assistant
from ..routes.base import find_backup_files_by_title

# 配置日志
logger = get_logger('web_app')

# 创建Blueprint
agent_bp = Blueprint('agent', __name__)

# 辅助函数：验证并获取请求数据
def _get_request_data() -> Tuple[Dict[str, Any], Optional[Tuple[Dict[str, Any], int]]]:
    """
    从请求中获取并验证数据
    
    Returns:
        Tuple[Dict, Optional[Tuple]]: (请求数据, 错误响应) - 如果有错误，返回错误响应，否则返回None
    """
    data = request.json
    agent_id = data.get('agent_id')
    query = data.get('query')
    collection_name = data.get('collection_name')
    model = data.get('model', 'gpt-4o')
    top_k = int(data.get('top_k', 5))
    debug_mode = data.get('debug_mode', False)
    
    # 验证必要参数
    if not query or not collection_name or not agent_id:
        return {}, (jsonify({'error': '缺少必要参数'}), 400)
    
    return {
        'agent_id': agent_id,
        'query': query,
        'collection_name': collection_name,
        'model': model,
        'top_k': top_k,
        'debug_mode': debug_mode
    }, None

# 辅助函数：获取或创建助手实例
def _get_or_create_agent(
    agent_id: str, 
    collection_name: str, 
    model: str, 
    top_k: int, 
    agent_class: Type[Union[Collection_QA_Assistant, Collection_Ref_Assistant, Collection_Sum_Assistant, Collection_Chat_Assistant]]
) -> Union[Collection_QA_Assistant, Collection_Ref_Assistant, Collection_Sum_Assistant, Collection_Chat_Assistant]:
    """
    获取现有的助手实例或创建新实例
    
    Args:
        agent_id: 助手ID
        collection_name: 集合名称
        model: 模型名称
        top_k: 返回结果数量
        agent_class: 助手类
        
    Returns:
        助手实例
    """
    # 检查是否已经存在此助手实例
    if agent_id not in current_app.config['agents']:
        # 创建新的助手实例
        agent = agent_class(
            model=model,
            collection_name=collection_name,
            top_k=top_k
        )
        current_app.config['agents'][agent_id] = agent
        logger.info(f"创建了新的智能助手: {agent_id}, 集合: {collection_name}, 类型: {agent_class.__name__}")
    else:
        # 使用现有助手实例
        agent = current_app.config['agents'][agent_id]
    
    return agent

# 辅助函数：处理调试模式响应
def _format_debug_response(response, agent_id: str, collection_name: str) -> Dict[str, Any]:
    """
    格式化调试模式的响应
    
    Args:
        response: 助手返回的响应
        agent_id: 助手ID
        collection_name: 集合名称
        
    Returns:
        格式化后的JSON响应
    """
    # 处理消息列表并构建HTML
    debug_content = ""
    for idx, msg in enumerate(response):
        role_badge = f'<span class="badge bg-primary">{msg.role}</span>'
        step_badge = f'<span class="badge bg-secondary">步骤 {idx+1}</span>'
        content = msg._content
        debug_content += f'<div class="debug-message mb-2 p-2 border-bottom" style="color: inherit;">{role_badge} {step_badge}<br>{content}</div>'
    
    # 记录助手回复
    assistant_message = {
        "role": "assistant",
        "content": f'<div class="debug-panel p-2 border rounded" style="color: inherit;"><h6>调试模式输出：</h6>{debug_content}</div>',
        "timestamp": datetime.datetime.now()
    }
    
    # 返回JSON响应
    return {
        'agent_id': agent_id,
        'response': assistant_message["content"],
        'collection_name': collection_name
    }

# 辅助函数：解析字符串为字典
def _parse_string_to_dict(response_str: str) -> Tuple[Optional[Dict], Optional[Tuple[Dict[str, Any], int]]]:
    """
    尝试将字符串响应解析为字典
    
    Args:
        response_str: 需要解析的字符串响应
        
    Returns:
        Tuple[Optional[Dict], Optional[Tuple]]: (解析后的字典, 错误响应)
    """
    try:
        # 先尝试JSON解析
        try:
            return json.loads(response_str), None
        except json.JSONDecodeError:
            # 如果JSON解析失败，尝试使用ast.literal_eval
            try:
                return ast.literal_eval(response_str), None
            except (SyntaxError, ValueError):
                # 如果两种方法都失败，记录错误并返回错误响应
                logger.error(f"Failed to parse response string to dictionary: {response_str}")
                return None, (jsonify({'error': '无法解析助手返回的响应格式'}), 400)
    except Exception as e:
        logger.error(f"Error converting response string to dictionary: {str(e)}")
        return None, (jsonify({'error': f'处理响应格式时出错: {str(e)}'}), 400)

# 辅助函数：处理引用助手的响应并格式化
def _format_ref_response(response, agent_id: str, collection_name: str) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    """
    格式化引用助手的响应，构建带引用的Markdown
    
    Args:
        response: 引用助手返回的响应
        agent_id: 助手ID
        collection_name: 集合名称
        
    Returns:
        JSON响应或错误响应
    """
    # 如果响应是字符串，尝试解析为字典
    if isinstance(response, str):
        response_dict, error = _parse_string_to_dict(response)
        if error:
            return error
        response = response_dict
    
    # 验证响应格式
    if not isinstance(response, dict):
        logger.debug("The response with wrong format:")
        logger.debug(type(response))
        logger.debug(response)
        error_message = f"无效的响应格式：引用助手应返回包含main_text和references_list的字典"
        logger.error(error_message)
        return jsonify({'error': error_message}), 400
    
    # 从字典中获取主文本和引用列表
    main_text = response.get("main_text", "")
    references_list = response.get("references_list", [])
    
    # 构建带引用的Markdown文本
    if references_list:
        markdown_text = main_text
        
        # 添加引用章节
        markdown_text += "\n\n## References\n\n"
        
        for i, ref in enumerate(references_list, 1):
            # 查找匹配的备份文件
            backup_files = find_backup_files_by_title(ref)
            if backup_files:
                # 创建链接格式
                markdown_text += f"{i}. [{ref}]({url_for('files.view_backup_files', filename=backup_files, _external=True)})\n"
            else:
                markdown_text += f"{i}. {ref}\n"
        
        # 返回带引用的响应
        return {
            'agent_id': agent_id,
            'response': markdown_text,
            'collection_name': collection_name,
            'is_markdown': True
        }
    else:
        # 无引用的响应
        return {
            'agent_id': agent_id,
            'response': main_text,
            'collection_name': collection_name,
            'is_markdown': True
        }

@agent_bp.route('/agent_assistant')
def agent_assistant():
    """集合智能助手页面路由"""
    
    # 获取可用集合
    collections = manager.database.list_collections()
    collection_names = [col["name"] for col in collections if col.get("exists_in_chroma", False)]
    
    return render_template('agent_assistant.html', collections=collection_names)

@agent_bp.route('/agent_assistant/collection_qa', methods=['POST'])
def collection_qa_process():
    """处理集合智能助手的聊天请求"""
    
    # 获取并验证请求数据
    data, error = _get_request_data()
    if error:
        return error
    
    agent_id = data['agent_id']
    query = data['query']
    collection_name = data['collection_name']
    model = data['model']
    top_k = data['top_k']
    debug_mode = data['debug_mode']
    
    try:
        # 获取或创建助手实例
        agent = _get_or_create_agent(
            agent_id=agent_id,
            collection_name=collection_name,
            model=model,
            top_k=top_k,
            agent_class=Collection_QA_Assistant
        )
        
        # 执行查询
        response = agent.run(query, debug=debug_mode)
        logger.debug(response)
        
        # 处理响应
        if debug_mode:
            # 调试模式：返回所有消息步骤
            return jsonify(_format_debug_response(response, agent_id, collection_name))
        else:
            # 普通模式：返回最终响应
            return jsonify({
                'agent_id': agent_id,
                'response': response,
                'collection_name': collection_name,
                'is_markdown': True  # 添加标记表示响应是Markdown格式
            })
            
    except Exception as e:
        logger.error(f"智能助手处理请求时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': f'处理请求时出错: {str(e)}'}), 500

@agent_bp.route('/agent_assistant/collection_ref', methods=['POST'])
def collection_ref_process():
    """处理集合引用助手的参考文献请求"""
    
    # 获取并验证请求数据
    data, error = _get_request_data()
    if error:
        return error
    
    agent_id = data['agent_id']
    statement = data['query']  # 使用相同的query字段接收陈述内容
    collection_name = data['collection_name']
    model = data['model']
    top_k = data['top_k']
    debug_mode = data['debug_mode']
    
    try:
        # 获取或创建助手实例
        agent = _get_or_create_agent(
            agent_id=agent_id,
            collection_name=collection_name,
            model=model,
            top_k=top_k,
            agent_class=Collection_Ref_Assistant
        )
        
        # 执行引用处理
        response = agent.run(statement, debug=debug_mode)
        logger.debug(response)
        
        # 处理响应
        if debug_mode:
            # 调试模式：返回所有消息步骤
            return jsonify(_format_debug_response(response, agent_id, collection_name))
        else:
            # 处理引用助手的返回结果
            ref_response = _format_ref_response(response, agent_id, collection_name)
            return jsonify(ref_response) if isinstance(ref_response, dict) else ref_response
            
    except Exception as e:
        logger.error(f"引用助手处理请求时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': f'处理引用请求时出错: {str(e)}'}), 500

@agent_bp.route('/agent_assistant/collection_sum', methods=['POST'])
def collection_sum_process():
    """处理集合文章总结助手的请求"""
    
    # 获取并验证请求数据
    data, error = _get_request_data()
    if error:
        return error
    
    agent_id = data['agent_id']
    article_title = data['query']  # 使用相同的query字段接收文章标题
    collection_name = data['collection_name']
    model = data['model']
    top_k = data['top_k']
    debug_mode = data['debug_mode']
    
    try:
        # 获取或创建总结助手实例
        agent = _get_or_create_agent(
            agent_id=agent_id,
            collection_name=collection_name,
            model=model,
            top_k=top_k,
            agent_class=Collection_Sum_Assistant
        )
        
        # 执行文章总结
        logger.info(f"开始总结文章: '{article_title}', 集合: {collection_name}")
        response = agent.run(article_title, debug=debug_mode)
        logger.debug(f"总结完成，响应长度: {len(str(response))}")
        
        # 处理响应
        if debug_mode:
            # 调试模式：返回所有消息步骤
            return jsonify(_format_debug_response(response, agent_id, collection_name))
        else:
            # 普通模式：返回Markdown格式的总结
            return jsonify({
                'agent_id': agent_id,
                'response': response,
                'collection_name': collection_name,
                'is_markdown': True,  # 标记为Markdown格式
                'article_title': article_title  # 返回文章标题用于显示
            })
            
    except Exception as e:
        logger.error(f"文章总结助手处理请求时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': f'处理文章总结请求时出错: {str(e)}'}), 500

@agent_bp.route('/agent_assistant/collection_chat', methods=['POST'])
def collection_chat_process():
    """处理集合聊天助手的请求，该助手可以调用各种专业化工具"""
    
    # 获取并验证请求数据
    data, error = _get_request_data()
    if error:
        return error
    
    agent_id = data['agent_id']
    message = data['query']
    collection_name = data['collection_name']
    model = data['model']
    top_k = data['top_k']
    debug_mode = data['debug_mode']
    
    try:
        # 获取或创建聊天助手实例
        agent = _get_or_create_agent(
            agent_id=agent_id,
            collection_name=collection_name,
            model=model,
            top_k=top_k,
            agent_class=Collection_Chat_Assistant
        )
        
        # 执行聊天处理
        logger.info(f"处理聊天消息，集合: {collection_name}, 用户消息长度: {len(message)}")
        response = agent.run(message, debug=debug_mode)
        logger.debug(f"聊天响应完成，响应长度: {len(str(response))}")
        
        # 处理响应
        if debug_mode:
            # 调试模式：返回所有消息步骤
            return jsonify(_format_debug_response(response, agent_id, collection_name))
        else:
            # 检查响应是否是字典格式（可能包含 main_text 和 references_list）
            if isinstance(response, dict) and "main_text" in response and "references_list" in response:
                # 这是引用格式的响应，使用引用助手的格式化方法
                ref_response = _format_ref_response(response, agent_id, collection_name)
                return jsonify(ref_response) if isinstance(ref_response, dict) else ref_response
            else:
                # 普通文本响应，假设是Markdown格式
                return jsonify({
                    'agent_id': agent_id,
                    'response': response,
                    'collection_name': collection_name,
                    'is_markdown': True
                })
            
    except Exception as e:
        logger.error(f"聊天助手处理请求时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': f'处理聊天请求时出错: {str(e)}'}), 500 