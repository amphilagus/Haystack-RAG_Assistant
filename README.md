# Amphilagus - 文档管理与RAG助手系统

Amphilagus是一个基于Web界面的文档管理和检索增强生成(RAG)系统，专为管理学术文档和知识库而设计。

## 功能特点

- **文档管理**：支持PDF、TXT、DOCX、MD、HTML等多种格式文档导入与管理
- **标签分类系统**：强大的分级标签系统，用于组织和分类文档，支持标签继承关系
- **多语言支持**：集成多种嵌入模型，包括专为中文优化的模型
- **持久化存储**：基于ChromaDB的向量数据库，保存文档嵌入和元数据
- **集合管理**：支持创建和管理多个知识库集合，适用于不同主题或项目
- **用户友好的Web界面**：直观的Web界面，易于使用
- **先进语言模型**：支持OpenAI最新的GPT-4o、GPT-4o-mini等模型
- **自动嵌入模型匹配**：自动记录集合使用的嵌入模型，确保检索一致性
- **批量处理**：支持后台批量处理文档上传和向量嵌入任务

## 技术栈

- **后端**：Flask 框架
- **前端**：Bootstrap 5 + jQuery
- **数据存储**：JSON 文件存储元数据，ChromaDB存储向量嵌入
- **AI模型**：集成OpenAI API和多种嵌入模型

## 安装指南

### 前提条件

- Python 3.11+
- 有效的OpenAI API密钥
- [uv](https://github.com/astral-sh/uv) 包管理器 (可选但推荐)

### 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/amphilagus.git
cd amphilagus
```

2. 使用uv创建并激活虚拟环境：

```bash
# 安装uv (如果尚未安装)
# Linux/Mac
curl -fsSL https://astral.sh/uv/install.sh | bash
# Windows
curl -fsSL https://astral.sh/uv/install.ps1 -o install.ps1; .\install.ps1

# 创建并激活虚拟环境
uv init .
uv venv
# Linux/Mac
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

3. 安装包及依赖：

```bash
# 开发模式安装（推荐）
uv pip install -e ".[dev,web]"

# 或使用普通安装
uv pip install .
```

4. 配置API密钥：
   - 在项目根目录创建`.env`文件
   - 添加您的OpenAI API密钥：`OPENAI_API_KEY=your_api_key_here`
   - 添加Flask密钥：`FLASK_SECRET_KEY=your_secret_key_here`

### 运行Web应用

安装后，可以通过以下方式启动web应用：

```bash
# 使用入口点启动（推荐）
amphilagus-web

# 或直接通过Python模块启动
python -m amphilagus.web_app

# 或使用运行脚本
python run_web_app.py
```

Web界面将在以下地址可访问：http://localhost:5000

## 目录结构

```
amphilagus/
├── __init__.py          # 包初始化
├── file_manager.py      # 文件管理核心模块
├── database_manager.py  # 数据库管理模块
├── task_manager.py      # 任务管理器模块
├── assistant.py         # AI助手模块
├── web_app.py           # Web应用路由和控制器
├── templates/           # HTML模板
│   ├── base.html        # 基础模板
│   ├── home.html        # 首页
│   └── ...              # 其他页面模板
└── static/              # 静态资源
    ├── css/             # CSS样式
    ├── js/              # JavaScript脚本
    └── img/             # 图片资源
```

## 数据目录

首次运行应用程序前，请确保创建以下目录：

```bash
mkdir -p raw_data backup_data chroma_db tasks
```

- `raw_data`：原始文档文件存储目录
- `backup_data`：文档备份目录
- `chroma_db`：向量数据库存储目录
- `tasks`：后台任务数据存储

## 使用指南

### 文件管理

- **查看文件**：首页或"文件"菜单可查看所有文件
- **上传文件**："上传"菜单可添加新文件，并可选择标签
- **删除文件**：在文件列表或详情页中点击删除按钮
- **文件详情**：点击文件列表中的查看按钮，查看详细信息
- **批量操作**：支持批量删除和批量嵌入到向量数据库
- **高级筛选**：按标签、日期等条件筛选文档

### 标签系统

- **查看标签**："标签"菜单可查看所有标签及其继承关系
- **创建标签**：创建新标签，可设置父标签建立继承关系
- **为文件添加标签**：在文件详情页或管理标签页面添加标签
- **按标签筛选**：在文件列表页使用标签筛选功能
- **预设标签**：系统提供基础的预设标签，可自行扩展

### RAG助手

- **知识库问答**：针对导入文档提问，获取准确答案
- **多模型支持**：支持多种OpenAI模型
- **参考引用**：显示答案来源文档链接
- **自定义参数**：可调整检索文档数量等参数
- **历史记录**：保存问答历史记录

### 向量数据库管理

- **集合管理**：创建、查看和删除向量数据库集合
- **文档嵌入**：将文档批量嵌入到向量数据库
- **模型选择**：为不同集合选择合适的嵌入模型
- **数据库统计**：查看集合和文档统计信息

### 全能助手

- **工具使用**：通过MCP工具链支持多种外部工具
- **调试模式**：查看助手思考过程和工具使用流程
- **多轮对话**：支持连续多轮对话

## 未来扩展计划

- **高级搜索**：全文搜索和元数据搜索
- **文件预览**：直接在网页中预览文件内容
- **批处理优化**：更高效的批量处理机制
- **用户管理**：添加多用户支持和权限管理
- **API接口**：提供完整的RESTful API

## 更多信息

更多详细信息，请参阅[安装指南](INSTALL.md)。

## 许可证

MIT 
