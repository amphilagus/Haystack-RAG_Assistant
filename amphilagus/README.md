# Amphilagus - RAG Assistant 项目管理模块

Amphilagus 是 Haystack RAG Assistant 项目的管理模块，提供以下功能：

- 文件管理：管理 raw_data 文件的添加、删除
- 标签系统：对文件进行标签分类，支持标签继承关系
- RAG 助手：集成 RAG Assistant 功能（规划中）
- 外部工具：调用外部工具（规划中）

## 文件管理系统

Amphilagus 实现了对 raw_data 的标签化扁平管理：

- 每个 raw_data 文件都有对应的元数据（metadata）
- 一个文件可以拥有多个标签
- 标签支持继承特性，例如 "JCTC文献" 是 "科研文献" 的子类

## 主要功能

### 文件管理

- 添加文件：上传新文件到 raw_data 目录
- 删除文件：从 raw_data 目录删除文件
- 管理标签：为文件添加或删除标签
- 查看文件：按标签筛选文件

### 标签系统

- 创建标签：创建新标签，可设置父标签
- 继承关系：子标签继承父标签的属性
- 标签查询：查询时可选择包含子标签的文件

## 使用方法

### 运行 Web 应用

```bash
python run_web_app.py
```

然后在浏览器中访问：`http://localhost:5000`

### 使用 Python API

```python
from amphilagus.main import Amphilagus

# 初始化
amph = Amphilagus()

# 创建标签
science_tag = amph.create_tag("科研文献")
jctc_tag = amph.create_tag("JCTC文献", parent_name="科研文献")

# 添加文件
amph.add_raw_data(
    "path/to/file.pdf",
    tags=["JCTC文献"],
    description="这是一篇 JCTC 文献"
)

# 查找文件
science_papers = amph.get_raw_data_by_tag("科研文献")  # 包含 JCTC 文献
```

## 技术实现

- 文件系统：使用 Python 的标准库进行文件操作
- 元数据存储：使用 JSON 存储元数据
- Web 界面：使用 Flask 框架实现 