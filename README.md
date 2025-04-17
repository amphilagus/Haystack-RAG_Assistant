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
- [uv](https://github.com/astral-sh/uv) 包管理器 (可选但推荐)

### 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/haystack-rag.git
cd haystack-rag
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

3. 使用uv安装依赖：

```bash
# 安装项目依赖
uv pip install -r requirements.txt

# 安装mcp和httpx
uv add mcp[cli] httpx
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
├── run_web.ps1          # Web界面启动脚本
├── convert_pdf.ps1      # PDF转MD脚本
└── .env                 # 环境变量（需手动创建）
```

## 注意事项

- 首次运行Web界面时，需要初始化管道并加载文档
- 选择嵌入模型时注意匹配文档语言（中文推荐BGE或M3E模型）
- 大型文档集合的嵌入过程可能需要一些时间
- 确保OpenAI API密钥有足够的额度

## PDF转换工具

项目内置了PDF到Markdown的转换工具，基于[Marker](https://github.com/VikParuchuri/marker)库，支持OCR功能。

### 主要功能

- 将PDF文档转换为格式化的Markdown文本
- 支持多语言OCR识别扫描文档
- 可自定义批处理大小以优化不同硬件的性能
- 支持限制处理特定页面范围
- 支持批量处理整个文件夹中的PDF文件
- 支持并行处理多个PDF文件提高效率
- **LLM增强**：使用语言模型提高转换质量（需要在.env文件中配置Google API密钥）

### 使用方法

```bash
# 处理单个PDF文件
python rag_assistant/pdf_to_markdown.py "文档路径.pdf" "输出目录" [选项]

# 批量处理整个目录中的PDF文件
python rag_assistant/pdf_to_markdown.py "PDF文件夹路径" "输出目录" --workers 4 [选项]

# 使用LLM增强功能转换
python rag_assistant/pdf_to_markdown.py "文档路径.pdf" "输出目录" --use_llm
```

#### 通用选项
- `--batch_multiplier <值>`: 批处理大小倍数(默认: 2)，增加可提高速度但需要更多VRAM
- `--langs "<语言>"`: OCR识别的语言，逗号分隔(例如 "en,zh,fr")
- `--use_llm`: 使用语言模型增强，提高转换质量（需要Google API密钥）

#### 单文件选项
- `--max_pages <值>`: 最大处理页数，缺省则处理整个文档

#### 批量处理选项
- `--workers <值>`: 并行处理的PDF文件数(默认: 1)
- `--max_files <值>`: 最多处理的PDF文件数，缺省则处理所有文件
- `--min_length <值>`: 最小文本长度，低于此长度的PDF将被跳过(默认: 0)

### PowerShell脚本使用方法

Windows用户可以使用更便捷的PowerShell脚本：

```powershell
# 基本用法
.\convert_pdf.ps1 -InputPath "文档.pdf" -OutputDir "输出目录"

# 使用LLM增强
.\convert_pdf.ps1 -InputPath "文档.pdf" -OutputDir "输出目录" -UseLLM

# 批量处理目录
.\convert_pdf.ps1 -InputPath "PDF文件夹" -OutputDir "输出目录" -Workers 4 -UseLLM
```

### 性能提示

1. 如果有大容量显存的GPU(8GB+)，可增加`batch_multiplier`值加速处理
2. 使用OCR时，正确指定文档中实际包含的语言可提高准确性
3. 多核心CPU或多GPU系统上建议增加`workers`值实现并行处理
4. 对于主要包含图像的PDF，设置`min_length`参数可避免不必要的OCR处理
5. 对于非常大的文档，考虑使用`max_pages`参数分批处理
6. LLM增强功能可以显著提高转换质量，但会增加处理时间和API消耗

## 许可证

MIT 
