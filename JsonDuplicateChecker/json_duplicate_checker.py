#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON重复字段检查器
用于检查大型JSON文件中指定字段的重复值
"""

import json
import sys
from collections import defaultdict, Counter
from typing import Dict, List, Any
import argparse


def find_duplicates_in_json_file(file_path: str, field_name: str) -> Dict[str, List[Dict]]:
    """
    在JSON文件中查找指定字段的重复值
    
    Args:
        file_path: JSON文件路径
        field_name: 要检查的字段名
        
    Returns:
        包含重复值的字典，键为重复的字段值，值为包含该值的所有JSON对象列表
    """
    field_values = defaultdict(list)
    duplicates = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # 逐行读取以处理大文件
            line_number = 0
            for line in file:
                line = line.strip()
                if not line:
                    continue
                    
                line_number += 1
                try:
                    # 尝试解析每行为JSON对象
                    json_obj = json.loads(line)
                    
                    # 检查字段是否存在
                    if field_name in json_obj:
                        field_value = json_obj[field_name]
                        # 将字段值转换为字符串以便比较
                        field_value_str = str(field_value)
                        field_values[field_value_str].append({
                            'line_number': line_number,
                            'data': json_obj
                        })
                    else:
                        print(f"警告: 第{line_number}行缺少字段 '{field_name}'")
                        
                except json.JSONDecodeError as e:
                    print(f"警告: 第{line_number}行JSON解析错误: {e}")
                    continue
                    
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{file_path}'")
        return {}
    except Exception as e:
        print(f"错误: 读取文件时发生异常: {e}")
        return {}
    
    # 找出重复的值
    for field_value, records in field_values.items():
        if len(records) > 1:
            duplicates[field_value] = records
            
    return duplicates


def print_duplicate_statistics(duplicates: Dict[str, List[Dict]], field_name: str):
    """
    打印重复值的统计信息
    
    Args:
        duplicates: 重复值字典
        field_name: 字段名
    """
    if not duplicates:
        print(f"✅ 没有发现字段 '{field_name}' 的重复值")
        return
    
    print(f"\n📊 重复值统计报告")
    print(f"字段名: {field_name}")
    print(f"发现 {len(duplicates)} 个重复的字段值")
    
    total_duplicate_records = sum(len(records) for records in duplicates.values())
    print(f"总共涉及 {total_duplicate_records} 条记录")
    
    print(f"\n{'='*60}")
    
    # 按重复次数排序
    sorted_duplicates = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)
    
    for field_value, records in sorted_duplicates:
        print(f"\n🔄 重复值: {field_value}")
        print(f"   出现次数: {len(records)}")
        print(f"   所在行号: {[record['line_number'] for record in records]}")
        
        # 显示前几条重复记录的详细信息
        print("   重复记录详情:")
        for i, record in enumerate(records[:3]):  # 只显示前3条
            print(f"     [{i+1}] 行号 {record['line_number']}: {json.dumps(record['data'], ensure_ascii=False, separators=(',', ':'))}")
        
        if len(records) > 3:
            print(f"     ... 还有 {len(records) - 3} 条记录")


def main():
    parser = argparse.ArgumentParser(description='检查JSON文件中指定字段的重复值')
    parser.add_argument('file_path', help='JSON文件路径')
    parser.add_argument('field_name', help='要检查重复的字段名')
    parser.add_argument('--output', '-o', help='输出重复记录到文件')
    
    args = parser.parse_args()
    
    print(f"🔍 开始检查文件: {args.file_path}")
    print(f"🎯 检查字段: {args.field_name}")
    
    # 查找重复值
    duplicates = find_duplicates_in_json_file(args.file_path, args.field_name)
    
    # 打印统计信息
    print_duplicate_statistics(duplicates, args.field_name)
    
    # 如果指定了输出文件，将重复记录写入文件
    if args.output and duplicates:
        try:
            with open(args.output, 'w', encoding='utf-8') as output_file:
                output_data = {
                    'field_name': args.field_name,
                    'duplicate_count': len(duplicates),
                    'total_duplicate_records': sum(len(records) for records in duplicates.values()),
                    'duplicates': {}
                }
                
                for field_value, records in duplicates.items():
                    output_data['duplicates'][field_value] = [record['data'] for record in records]
                
                json.dump(output_data, output_file, ensure_ascii=False, indent=2)
                print(f"\n💾 重复记录已保存到: {args.output}")
                
        except Exception as e:
            print(f"❌ 保存输出文件时发生错误: {e}")


if __name__ == "__main__":
    main()