# Markdown 科研文献清洗工具

这是一个用于清洗Markdown格式科研文献的工具，可以根据配置文件中定义的规则删除指定章节或部分内容。

## 快速开始

最简单的使用方法是：

```powershell
.\clean_md_files.ps1 <输入文件夹> <输出文件夹> <文档类型>
```

例如：

```powershell
.\clean_md_files.ps1 .\raw_files\papers .\cleaned_papers jctc
```

这将递归处理 `raw_files\papers` 目录及其子目录中的所有 `.md` 文件，使用 `jctc` 文档类型的规则进行清洗，并将结果保存到 `cleaned_papers` 目录中，保持原有的目录结构。

## 配置文件

配置文件 `md_cleaner_config.json` 定义了不同类型文档的清洗规则。文件结构如下：

```json
{
  "文档类型1": {
    "规则ID1": {
      "start": "起始关键词",
      "end": null
    },
    "规则ID2": {
      "start": "另一个起始关键词",
      "end": "结束关键词"
    }
  },
  "文档类型2": {
    ...
  }
}
```

### 规则说明

- 如果 `end` 为 `null`，表示删除 `start` 关键词及其后面的所有内容
- 如果 `end` 有值，表示删除从 `start` 到 `end` 之间的内容（包括 `start` 但保留 `end`）

### 添加新的文档类型

要添加新的文档类型，只需编辑 `md_cleaner_config.json` 文件，添加新的顶层键和相应的规则即可。

例如，添加新的 `nature_articles` 类型：

```json
{
  "nature_articles": {
    "remove_methods": {
      "start": "Methods",
      "end": "Results"
    },
    "remove_references": {
      "start": "References",
      "end": null
    }
  }
}
```

## 高级用法

### 应用特定规则

如果只想应用特定规则而不是文档类型中的所有规则：

```powershell
.\clean_md_files.ps1 .\raw_files .\cleaned_data jctc -Rules "remove_references,remove_acknowledgements"
```

### 使用自定义配置文件

```powershell
.\clean_md_files.ps1 .\raw_files .\cleaned_data custom_type -ConfigFile ".\my_config.json"
```

## 工作原理

该工具通过以下步骤工作：

1. 递归查找输入目录中所有的 `.md` 文件
2. 对每个文件应用配置文件中指定文档类型的规则
3. 保持原有目录结构输出到目标目录

清洗过程使用正则表达式匹配Markdown标题格式（`#`、`##` 等开头的行），因此该工具最适合处理结构良好的Markdown文件。 