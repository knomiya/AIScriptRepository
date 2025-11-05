#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例和测试脚本
"""

import json
from json_duplicate_checker import find_duplicates_in_json_file, print_duplicate_statistics


def create_test_data():
    """创建测试数据文件"""
    test_data = [
        {"id": "001", "name": "张三", "email": "zhangsan@example.com", "age": 25},
        {"id": "002", "name": "李四", "email": "lisi@example.com", "age": 30},
        {"id": "003", "name": "王五", "email": "zhangsan@example.com", "age": 28},  # email重复
        {"id": "004", "name": "赵六", "email": "zhaoliu@example.com", "age": 25},  # age重复
        {"id": "005", "name": "钱七", "email": "lisi@example.com", "age": 32},     # email重复
        {"id": "006", "name": "孙八", "email": "sunba@example.com", "age": 25},    # age重复
        {"id": "007", "name": "周九", "email": "zhoujiu@example.com", "age": 30},  # age重复
    ]
    
    # 写入测试文件
    with open('test_data.txt', 'w', encoding='utf-8') as f:
        for item in test_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print("✅ 测试数据文件 'test_data.txt' 已创建")


def test_duplicate_checker():
    """测试重复检查功能"""
    # 创建测试数据
    create_test_data()
    
    print("\n" + "="*60)
    print("测试1: 检查email字段重复")
    print("="*60)
    
    duplicates = find_duplicates_in_json_file('test_data.txt', 'email')
    print_duplicate_statistics(duplicates, 'email')
    
    print("\n" + "="*60)
    print("测试2: 检查age字段重复")
    print("="*60)
    
    duplicates = find_duplicates_in_json_file('test_data.txt', 'age')
    print_duplicate_statistics(duplicates, 'age')
    
    print("\n" + "="*60)
    print("测试3: 检查不存在重复的id字段")
    print("="*60)
    
    duplicates = find_duplicates_in_json_file('test_data.txt', 'id')
    print_duplicate_statistics(duplicates, 'id')


if __name__ == "__main__":
    test_duplicate_checker()