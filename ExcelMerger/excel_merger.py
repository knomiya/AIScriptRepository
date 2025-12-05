#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel文件合并工具
功能：将多个Excel文件按相同列名进行合并
作者：Kiro AI Assistant
"""

import pandas as pd
import os
import sys
import glob
from pathlib import Path
import argparse
from typing import List, Dict, Set


class ExcelMerger:
    def __init__(self):
        self.files_data = []
        self.common_columns = set()
        self.column_order = []  # 保存列的顺序
        
    def load_excel_files(self, file_paths: List[str]) -> bool:
        """
        加载多个Excel文件
        
        Args:
            file_paths: Excel文件路径列表
            
        Returns:
            bool: 是否成功加载所有文件
        """
        print("开始加载Excel文件...")
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"错误：文件不存在 - {file_path}")
                return False
                
            try:
                # 尝试读取Excel文件
                df = pd.read_excel(file_path)
                print(f"成功加载: {file_path} (行数: {len(df)}, 列数: {len(df.columns)})")
                
                # 存储文件数据和元信息
                self.files_data.append({
                    'path': file_path,
                    'data': df,
                    'columns': set(df.columns)
                })
                
            except Exception as e:
                print(f"错误：无法读取文件 {file_path} - {str(e)}")
                return False
                
        return True
    
    def find_common_columns(self) -> Set[str]:
        """
        找到所有文件的共同列名，并保持第一个文件的列顺序
        
        Returns:
            Set[str]: 共同列名集合
        """
        if not self.files_data:
            return set()
            
        # 获取第一个文件的列名作为基础（保持顺序）
        first_file_columns = list(self.files_data[0]['data'].columns)
        self.common_columns = self.files_data[0]['columns'].copy()
        
        # 与其他文件的列名求交集
        for file_info in self.files_data[1:]:
            self.common_columns &= file_info['columns']
        
        # 保持第一个文件中共同列的顺序
        self.column_order = [col for col in first_file_columns if col in self.common_columns]
            
        return self.common_columns
    
    def show_column_analysis(self):
        """显示列名分析结果"""
        print("\n=== 列名分析 ===")
        
        # 显示每个文件的列名
        for i, file_info in enumerate(self.files_data, 1):
            print(f"\n文件 {i}: {os.path.basename(file_info['path'])}")
            print(f"列名: {list(file_info['columns'])}")
            
        # 显示共同列名
        print(f"\n共同列名 ({len(self.common_columns)} 个):")
        print(list(self.common_columns))
        
        # 显示每个文件独有的列名
        for i, file_info in enumerate(self.files_data, 1):
            unique_cols = file_info['columns'] - self.common_columns
            if unique_cols:
                print(f"\n文件 {i} 独有列名: {list(unique_cols)}")
    
    def merge_files(self, output_path: str, merge_mode: str = 'common') -> bool:
        """
        合并Excel文件
        
        Args:
            output_path: 输出文件路径
            merge_mode: 合并模式 ('common': 只保留共同列, 'all': 保留所有列)
            
        Returns:
            bool: 是否成功合并
        """
        if not self.files_data:
            print("错误：没有加载任何文件")
            return False
            
        print(f"\n开始合并文件 (模式: {merge_mode})...")
        
        try:
            merged_data = []
            
            # 如果是all模式，需要确定所有列的顺序
            if merge_mode == 'all':
                all_columns = []
                seen_columns = set()
                
                # 按文件顺序收集所有列名，保持第一次出现的顺序
                for file_info in self.files_data:
                    for col in file_info['data'].columns:
                        if col not in seen_columns:
                            all_columns.append(col)
                            seen_columns.add(col)
            
            for file_info in self.files_data:
                df = file_info['data'].copy()
                
                if merge_mode == 'common':
                    # 只保留共同列，并按第一个文件的顺序排列
                    df = df[self.column_order]
                elif merge_mode == 'all':
                    # 重新排列列顺序，确保所有文件的列顺序一致
                    existing_cols = [col for col in all_columns if col in df.columns]
                    df = df[existing_cols]
                
                # 添加源文件信息列
                df['源文件'] = os.path.basename(file_info['path'])
                merged_data.append(df)
            
            # 合并所有数据
            result_df = pd.concat(merged_data, ignore_index=True, sort=False)
            
            # 调整最终列顺序：先是数据列，最后是源文件列
            if merge_mode == 'all':
                final_columns = [col for col in all_columns if col in result_df.columns] + ['源文件']
                result_df = result_df[final_columns]
            elif merge_mode == 'common':
                final_columns = self.column_order + ['源文件']
                result_df = result_df[final_columns]
            
            # 保存到Excel文件
            result_df.to_excel(output_path, index=False)
            
            print(f"合并完成！")
            print(f"输出文件: {output_path}")
            print(f"总行数: {len(result_df)}")
            print(f"总列数: {len(result_df.columns)}")
            
            return True
            
        except Exception as e:
            print(f"合并失败: {str(e)}")
            return False


def expand_file_patterns(file_patterns: List[str]) -> List[str]:
    """
    展开文件模式（支持通配符）
    
    Args:
        file_patterns: 文件模式列表，可能包含通配符
        
    Returns:
        List[str]: 展开后的文件路径列表
    """
    expanded_files = []
    
    for pattern in file_patterns:
        # 使用glob展开通配符
        matches = glob.glob(pattern)
        if matches:
            # 只保留Excel文件
            excel_files = [f for f in matches if f.lower().endswith(('.xlsx', '.xls'))]
            expanded_files.extend(excel_files)
        else:
            # 如果没有匹配到，可能是具体的文件路径
            if pattern.lower().endswith(('.xlsx', '.xls')):
                expanded_files.append(pattern)
    
    # 去重并排序
    return sorted(list(set(expanded_files)))


def main():
    parser = argparse.ArgumentParser(description='Excel文件合并工具')
    parser.add_argument('files', nargs='+', help='要合并的Excel文件路径（支持通配符，如 *.xlsx）')
    parser.add_argument('-o', '--output', default='merged_excel.xlsx', 
                       help='输出文件名 (默认: merged_excel.xlsx)')
    parser.add_argument('-m', '--mode', choices=['common', 'all'], default='common',
                       help='合并模式: common=只保留共同列, all=保留所有列 (默认: common)')
    parser.add_argument('--analyze-only', action='store_true',
                       help='只分析列名，不进行合并')
    
    args = parser.parse_args()
    
    # 展开文件模式（支持通配符）
    expanded_files = expand_file_patterns(args.files)
    
    if not expanded_files:
        print("错误：没有找到匹配的Excel文件")
        print(f"搜索模式: {args.files}")
        sys.exit(1)
    
    print(f"找到 {len(expanded_files)} 个Excel文件:")
    for i, file in enumerate(expanded_files, 1):
        print(f"  {i}. {file}")
    
    # 创建合并器实例
    merger = ExcelMerger()
    
    # 加载文件
    if not merger.load_excel_files(expanded_files):
        sys.exit(1)
    
    # 分析列名
    merger.find_common_columns()
    merger.show_column_analysis()
    
    # 如果只是分析模式，则退出
    if args.analyze_only:
        return
    
    # 检查是否有共同列名
    if not merger.common_columns and args.mode == 'common':
        print("\n警告：没有找到共同列名，无法使用 'common' 模式合并")
        print("建议使用 'all' 模式: python excel_merger.py -m all file1.xlsx file2.xlsx")
        return
    
    # 执行合并
    if merger.merge_files(args.output, args.mode):
        print(f"\n✅ 合并成功！文件已保存为: {args.output}")
    else:
        print("\n❌ 合并失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()