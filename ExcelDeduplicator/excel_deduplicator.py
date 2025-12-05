#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel列去重工具
读取Excel文件指定列，去除重复数据并导出到文本文件
"""

import pandas as pd
import argparse
import sys
from pathlib import Path


def read_excel_column(file_path, column_name, sheet_name=None):
    """
    读取Excel文件指定列数据
    
    Args:
        file_path (str): Excel文件路径
        column_name (str): 列名
        sheet_name (str, optional): 工作表名称，默认读取第一个工作表
    
    Returns:
        pandas.Series: 列数据
    """
    try:
        # 读取Excel文件
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(file_path)
        
        # 检查列是否存在
        if column_name not in df.columns:
            available_columns = ', '.join(df.columns.tolist())
            raise ValueError(f"列 '{column_name}' 不存在。可用列: {available_columns}")
        
        return df[column_name]
    
    except FileNotFoundError:
        raise FileNotFoundError(f"文件 '{file_path}' 不存在")
    except Exception as e:
        raise Exception(f"读取Excel文件时出错: {str(e)}")


def remove_duplicates(data):
    """
    去除重复数据并排序
    
    Args:
        data (pandas.Series): 原始数据
    
    Returns:
        list: 去重后的数据列表
    """
    # 去除空值和重复值
    unique_data = data.dropna().drop_duplicates()
    
    # 转换为列表并排序
    result = sorted(unique_data.astype(str).tolist())
    
    return result


def export_to_text(data, output_path):
    """
    导出数据到文本文件
    
    Args:
        data (list): 要导出的数据
        output_path (str): 输出文件路径
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(f"{item}\n")
        
        print(f"✅ 成功导出 {len(data)} 条唯一数据到: {output_path}")
    
    except Exception as e:
        raise Exception(f"导出文件时出错: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description="Excel列去重工具 - 提取指定列的唯一值并导出到文本文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python excel_deduplicator.py data.xlsx -c "姓名"
  python excel_deduplicator.py data.xlsx -c "邮箱" -s "Sheet1" -o result.txt
        """
    )
    
    parser.add_argument('excel_file', help='Excel文件路径')
    parser.add_argument('-c', '--column', required=True, help='要处理的列名')
    parser.add_argument('-s', '--sheet', help='工作表名称（可选，默认第一个工作表）')
    parser.add_argument('-o', '--output', help='输出文件路径（可选，默认自动生成）')
    
    args = parser.parse_args()
    
    try:
        # 检查输入文件
        excel_path = Path(args.excel_file)
        if not excel_path.exists():
            print(f"❌ 错误: 文件 '{args.excel_file}' 不存在")
            sys.exit(1)
        
        # 生成输出文件名
        if args.output:
            output_path = args.output
        else:
            output_path = f"{excel_path.stem}_{args.column}_unique.txt"
        
        print(f"📖 正在读取文件: {args.excel_file}")
        print(f"📋 处理列: {args.column}")
        if args.sheet:
            print(f"📄 工作表: {args.sheet}")
        
        # 读取Excel数据
        column_data = read_excel_column(args.excel_file, args.column, args.sheet)
        print(f"📊 原始数据行数: {len(column_data)}")
        
        # 去重处理
        unique_data = remove_duplicates(column_data)
        print(f"🔄 去重后数据行数: {len(unique_data)}")
        
        # 导出结果
        export_to_text(unique_data, output_path)
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()