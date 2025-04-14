# Haystack RAG Assistant

基于Haystack框架的本地知识库检索增强生成系统，支持中英文文档检索和问答。

## 功能特点

- **文档导入**：支持PDF、TXT、DOCX、MD、HTML等多种格式文档导入，递归扫描所有子目录
- **多语言支持**：集成多种嵌入模型，包括专为中文优化的BAAI/bge系列模型
- **持久化存储**：基于ChromaDB的向量数据库，保存文档嵌入和元数据
- **集合管理**：支持创建和管理多个知识库集合，适用于不同主题或项目
- **命令行和Web界面**：同时提供CLI和用户友好的Web界面
- **先进语言模型**：支持OpenAI最新的GPT-4o、GPT-4o-mini等模型
- **自动嵌入模型匹配**：自动记录集合使用的嵌入模型，确保检索一致性
- **多层级文档组织**：支持递归扫描和加载多级目录结构中的文档

## 安装指南

### 前提条件

- Python 3.8+
- 有效的OpenAI API密钥

### 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/haystack-rag.git
cd haystack-rag
```

2. 创建并激活虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\Activate.ps1  # Windows PowerShell
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 配置API密钥：
   - 在项目根目录创建`.env`文件
   - 添加您的OpenAI API密钥：`OPENAI_API_KEY=your_api_key_here`

## 使用说明

### 命令行界面

```bash
# Windows PowerShell
.\run_cli.ps1

# Linux/Mac
python rag_assistant/main.py --interface cli
```

### Web界面

```bash
# Windows PowerShell
cd 项目根目录
python rag_assistant/main.py --interface web

# 或使用streamlit直接运行
streamlit run rag_assistant/web_app.py
```

### 添加文档

1. 将文档放入`raw_data`目录（可以创建子目录组织文档）
   - 系统会自动递归扫描所有子目录并加载其中的文档
   - 支持的格式：PDF、TXT、DOCX、MD、HTML
2. 通过CLI或Web界面选择导入文档
3. 选择适合文档语言的嵌入模型（中文推荐使用BAAI/bge模型）

### 集合管理

- 使用不同名称的集合来组织不同主题的知识库
- 可以随时重置或创建新集合
- 系统会自动记录集合的嵌入模型信息，确保检索一致性

## 项目结构

```
haystack-rag/
├── rag_assistant/       # 主要代码目录
│   ├── collection_metadata.py  # 集合元数据管理
│   ├── collection_utils.py     # 集合工具函数
│   ├── custom_document_store.py # 自定义文档存储
│   ├── document_loader.py      # 文档加载和处理
│   ├── main.py                 # 主入口
│   ├── rag_pipeline.py         # RAG管道实现
│   └── web_app.py              # Web界面
├── raw_data/            # 原始文档目录（需手动创建）
├── chroma_db/           # ChromaDB数据存储（自动创建）
├── collection_metadata.json  # 集合元数据（自动创建）
├── requirements.txt     # 项目依赖
├── run_cli.ps1          # Windows PowerShell启动脚本
└── .env                 # 环境变量（需手动创建）
```

## 注意事项

- 首次运行Web界面时，需要初始化管道并加载文档
- 选择嵌入模型时注意匹配文档语言（中文推荐BGE或M3E模型）
- 大型文档集合的嵌入过程可能需要一些时间
- 确保OpenAI API密钥有足够的额度

## 许可证

MIT 

## 最近更新

- **递归目录扫描**: 现在文档加载器会递归扫描所有子目录，方便组织大型文档集合
- **新增格式支持**: 增加对DOCX文档格式的支持
- **改进日志输出**: 文档加载过程中显示更详细的目录和文件信息 