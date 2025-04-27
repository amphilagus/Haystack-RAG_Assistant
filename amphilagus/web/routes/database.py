"""
数据库管理相关路由模块
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from ... import manager
from ...logger import get_logger

# 配置日志
logger = get_logger('web_app')

# 创建Blueprint
database_bp = Blueprint('database', __name__, url_prefix='/database')

@database_bp.route('/')
def database_dashboard():
    """数据库管理面板"""
    try:
        # 使用manager.database而不是直接调用导入的函数
        collections_info = manager.database.list_collections()
        
        # 获取数据库路径和状态统计
        chroma_db_path = manager.database.get_db_path()
        db_stats = manager.database.get_db_stats()
        
        # 打印调试信息
        logger.debug(f"从manager.database获取到的集合列表: {collections_info}")
        
        if not collections_info:
            logger.warning("未检索到任何集合")
        
        # 创建Chroma客户端实例检查
        if not manager.database.client:
            logger.error("ChromaDB客户端未初始化")
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
        logger.error(f"读取集合列表时出错: {str(e)}\n{traceback.format_exc()}")
        return render_template('database.html', 
                              collections=[],
                              chroma_db_path=manager.database.get_db_path() if manager.database else "未知",
                              db_stats={"total_collections": 0, "normal_collections": 0, 
                                        "missing_metadata": 0, "orphaned_metadata": 0, 
                                        "total_documents": 0},
                              error=f"读取集合列表时出错: {str(e)}")

@database_bp.route('/reload', methods=['POST'])
def reload_database():
    """重新加载数据库集合信息"""
    try:
        # 重新初始化数据库管理器的客户端连接
        if manager.database.client is not None:
            # 关闭现有客户端连接
            try:
                del manager.database.client
            except:
                pass
            
        # 重新创建客户端连接
        import chromadb
        try:
            manager.database.client = chromadb.PersistentClient(path=str(manager.database.chroma_db_path))
            logger.info("成功重新初始化ChromaDB客户端连接")
            
            # 刷新集合列表
            manager.database.list_collections()
            
            return jsonify({"success": True, "message": "数据库集合信息已重新加载"}), 200
        except Exception as e:
            logger.error(f"重新初始化ChromaDB客户端时出错: {str(e)}")
            return jsonify({"success": False, "message": f"重新加载失败: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"重新加载数据库集合信息时出错: {str(e)}")
        return jsonify({"success": False, "message": f"重新加载失败: {str(e)}"}), 500

@database_bp.route('/collections/<collection_name>/delete', methods=['POST'])
def delete_collection(collection_name):
    """删除集合"""
    try:
        # 使用manager.database删除集合
        success, message = manager.database.delete_collection(collection_name)
        
        if success:
            return redirect(url_for('database.database_dashboard', success=f'集合"{collection_name}"已成功删除'))
        else:
            return redirect(url_for('database.database_dashboard', error=f'删除集合失败: {message}'))
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return redirect(url_for('database.database_dashboard', error=f'删除集合时出错: {str(e)}')) 