# PDF 转 Markdown 转换工具

这是一个使用 Marker 库将 PDF 文件转换为 Markdown 格式的工具。它专为科研文献设计，能够处理复杂的文档结构，包括表格、图形和多列布局。

## 功能特点

- 支持单个 PDF 文件或整个目录的批量处理
- 并行处理多个 PDF 文件以提高效率
- 支持 OCR（光学字符识别）以处理扫描的文档
- 可选的 LLM（大型语言模型）增强以改进转换质量
- 内存管理优化，适用于处理大型 PDF 文件

## 使用方法

### 命令行使用

直接使用 Python 脚本：

```bash
python pdf_to_markdown.py <input_path> <output_dir> [options]
```

参数说明：
- `input_path`: 输入 PDF 文件或包含 PDF 文件的目录的路径
- `output_dir`: 保存 Markdown 文件的输出目录
- 选项：
  - `--max_pages`: 每个 PDF 处理的最大页数
  - `--langs`: OCR 使用的语言，逗号分隔（例如 "en,fr,de"）
  - `--workers`: 并行处理的 PDF 文件数量（处理目录时）
  - `--max_files`: 从目录处理的最大 PDF 文件数
  - `--min_length`: 处理的最小文件大小（以字节为单位）
  - `--use_llm`: 使用 LLM 增强转换质量

### 通过 PowerShell 脚本使用

更方便的方式是使用提供的 PowerShell 脚本 `convert_pdf.ps1`：

```powershell
.\convert_pdf.ps1 -InputPath <input_path> -OutputDir <output_dir> [options]
```

PowerShell 脚本提供了交互式提示和更多选项，请参考脚本帮助：

```powershell
Get-Help .\convert_pdf.ps1 -Full
```

## 要求

- Python 3.8 或更高版本
- 安装 marker-pdf 库：`pip install marker-pdf`
- 对于 LLM 增强：需要 API 密钥（可在 .env 文件中配置）

## 示例

处理单个 PDF 文件：

```bash
python pdf_to_markdown.py paper.pdf ./markdown_output
```

处理整个目录，使用并行处理和 LLM 增强：

```bash
python pdf_to_markdown.py ./papers ./markdown_output --workers 4 --use_llm
``` 