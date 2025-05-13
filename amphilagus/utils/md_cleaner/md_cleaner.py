#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MD Cleaner

一个简单的工具脚本，用于清洗Markdown格式的科研文献。
它可以根据指定的关键词标记删除段落，既可以删除单个关键词之后的所有内容，
也可以删除两个关键词之间的内容（包括第一个关键词，但保留第二个关键词）。

用法:
    python md_cleaner.py <input_file> <output_file> --doc-type <type> [--rules <rules>] [--config <config_file>]

示例:
    python md_cleaner.py paper.md cleaned_paper.md --doc-type scientific_papers
    python md_cleaner.py paper.md cleaned_paper.md --doc-type scientific_papers --rules remove_references,remove_acknowledgements
    python md_cleaner.py paper.md cleaned_paper.md --config custom_config.json --doc-type custom_type
"""

import argparse
import json
import re
import os
import sys
from typing import Dict, Optional, List, Tuple, Any


def clean_markdown(content: str, rules: Dict[str, Dict[str, Optional[str]]]) -> str:
    """
    根据规则清洗Markdown内容。
    
    参数:
        content: 要清洗的Markdown内容
        rules: 规则字典，格式为 {rule_id: {"start": start_marker, "end": end_marker}}
               当end为None时，删除start标记之后的所有内容
    
    返回:
        清洗后的Markdown内容
    """
    cleaned_content = content
    
    for rule_id, rule_config in rules.items():
        start_marker = rule_config["start"]
        end_marker = rule_config["end"]
        
        # 创建匹配标识符的模式
        # 这个模式会匹配任何包含标识符的行，不需要完全匹配
        start_pattern = rf'(^|\n).*{re.escape(start_marker)}.*?(\n|$)'
        
        if end_marker is None:
            # 如果没有结束标记，删除起始标记之后的所有内容
            match = re.search(start_pattern, cleaned_content, re.MULTILINE | re.IGNORECASE)
            if match:
                start_pos = match.start()
                # 删除起始标记及其之后的所有内容
                cleaned_content = cleaned_content[:start_pos]
        else:
            # 如果有结束标记，删除开始和结束标记之间的内容
            end_pattern = rf'(^|\n).*{re.escape(end_marker)}.*?(\n|$)'
            
            start_match = re.search(start_pattern, cleaned_content, re.MULTILINE | re.IGNORECASE)
            end_match = re.search(end_pattern, cleaned_content, re.MULTILINE | re.IGNORECASE)
            
            if start_match and end_match and start_match.start() < end_match.start():
                # 删除开始标记和结束标记之间的内容（包括开始标记）
                cleaned_content = (
                    cleaned_content[:start_match.start()] + 
                    cleaned_content[end_match.start():]
                )
    
    return cleaned_content


def process_file(input_file: str, output_file: str, rules: Dict[str, Dict[str, Optional[str]]]) -> bool:
    """
    处理单个Markdown文件。
    
    参数:
        input_file: 输入文件路径
        output_file: 输出文件路径
        rules: 规则字典
    
    返回:
        处理成功返回True，否则返回False
    """
    try:
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 清洗内容
        cleaned_content = clean_markdown(content, rules)
        
        # 将清洗后的内容写入输出文件，使用'w'模式自动覆盖已有文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"Cleaned content written to {output_file}")
        return True
    
    except Exception as e:
        print(f"Error processing file {input_file}: {str(e)}")
        return False


def batch_process_directory(
    input_dir: str, 
    output_dir: str, 
    rules: Dict[str, Dict[str, Optional[str]]], 
    file_ext: str = '.md'
) -> Tuple[int, int]:
    """
    批量处理目录中的所有Markdown文件。
    
    参数:
        input_dir: 输入目录路径
        output_dir: 输出目录路径
        rules: 规则字典
        file_ext: 文件扩展名过滤（默认: .md）
    
    返回:
        成功和失败的文件数量元组
    """
    # 如果输出目录不存在则创建
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    failure_count = 0
    
    # 处理所有指定扩展名的文件
    for filename in os.listdir(input_dir):
        if filename.endswith(file_ext):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            if process_file(input_path, output_path, rules):
                success_count += 1
            else:
                failure_count += 1
    
    return success_count, failure_count


def load_config(config_file: str) -> Dict[str, Any]:
    """
    加载配置文件。
    
    参数:
        config_file: 配置文件路径
        
    返回:
        配置字典
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config file {config_file}: {str(e)}")
        sys.exit(1)


def get_document_rules(
    config: Dict[str, Any], 
    doc_type: str, 
    rule_ids: Optional[List[str]] = None
) -> Dict[str, Dict[str, Optional[str]]]:
    """
    从配置中获取文档类型的规则。
    
    参数:
        config: 配置字典
        doc_type: 文档类型
        rule_ids: 要应用的规则ID列表，如果为None则应用文档类型的所有规则
        
    返回:
        规则字典
    """
    if doc_type not in config:
        if 'default' in config:
            print(f"Warning: Unknown document type '{doc_type}', using default rules")
            doc_type = 'default'
        else:
            print(f"Error: Unknown document type '{doc_type}' and no default rules found")
            print(f"Available document types: {', '.join(config.keys())}")
            sys.exit(1)
    
    type_rules = config[doc_type]
    
    if rule_ids is None:
        # 应用所有规则
        return type_rules
    
    # 仅应用指定的规则
    selected_rules = {}
    for rule_id in rule_ids:
        if rule_id in type_rules:
            selected_rules[rule_id] = type_rules[rule_id]
        else:
            print(f"Warning: Rule '{rule_id}' not found in document type '{doc_type}', ignored")
    
    return selected_rules


def main():
    """主函数，解析参数并处理文件。"""
    # 确保使用UTF-8编码
    if sys.stdout.encoding != 'utf-8':
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        elif hasattr(sys, 'setdefaultencoding'):
            sys.setdefaultencoding('utf-8')
    
    parser = argparse.ArgumentParser(description='Clean Markdown files by removing specified sections.')
    parser.add_argument('input', help='Input Markdown file or directory')
    parser.add_argument('output', help='Output Markdown file or directory')
    parser.add_argument('--doc-type', type=str, help='Document type, corresponding to top-level keys in config file')
    parser.add_argument('--rules', type=str, help='Rule IDs to apply, comma-separated')
    parser.add_argument('--config', type=str, default='md_cleaner_config.json', 
                      help='Config file path (default: md_cleaner_config.json)')
    parser.add_argument('--batch', action='store_true', help='Process all Markdown files in input directory')
    
    args = parser.parse_args()
    
    try:
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 如果配置文件路径是相对路径，相对于脚本所在目录解析
        if not os.path.isabs(args.config):
            config_path = os.path.join(script_dir, args.config)
        else:
            config_path = args.config
            
        # 加载配置
        config = load_config(config_path)
        
        # 如果未指定文档类型，列出可用的类型
        if args.doc_type is None:
            print(f"Error: Please specify document type with --doc-type")
            print(f"Available document types: {', '.join(config.keys())}")
            return 1
            
        # 解析规则ID
        rule_ids = args.rules.split(',') if args.rules else None
        
        # 获取规则
        rules = get_document_rules(config, args.doc_type, rule_ids)
        
        if not rules:
            print(f"Warning: No applicable rules found")
            return 1
            
        if args.batch:
            # 批量处理目录
            if not os.path.isdir(args.input):
                print(f"Error: Input must be a directory when using --batch")
                return 1
            
            success, failure = batch_process_directory(args.input, args.output, rules)
            print(f"Processed {success + failure} files: {success} successful, {failure} failed")
        else:
            # 处理单个文件
            if not os.path.isfile(args.input):
                print(f"Error: Input file '{args.input}' not found")
                return 1
            
            process_file(args.input, args.output, rules)
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 