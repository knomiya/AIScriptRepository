#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本分析器 - 统计文本长度和检测重复字串
"""

import re
from collections import Counter


def find_duplicate_substrings(text, min_length=2):
    """
    查找文本中重复的子字符串
    
    Args:
        text (str): 输入文本
        min_length (int): 最小子字符串长度
    
    Returns:
        dict: 重复的子字符串及其出现次数
    """
    duplicates = {}
    text_length = len(text)
    
    # 遍历所有可能的子字符串长度
    for length in range(min_length, text_length // 2 + 1):
        substring_counts = Counter()
        
        # 提取所有指定长度的子字符串
        for i in range(text_length - length + 1):
            substring = text[i:i + length]
            # 过滤掉只包含空格或特殊字符的子字符串
            if substring.strip() and not substring.isspace():
                substring_counts[substring] += 1
        
        # 找出出现次数大于1的子字符串
        for substring, count in substring_counts.items():
            if count > 1:
                # 只保留最长的重复子字符串，避免包含关系的重复
                if substring not in duplicates or len(substring) > len(list(duplicates.keys())[0]):
                    duplicates[substring] = count
    
    return duplicates


def analyze_text(text):
    """
    分析文本的各种统计信息
    
    Args:
        text (str): 输入文本
    
    Returns:
        dict: 包含各种统计信息的字典
    """
    # 基本长度统计
    total_chars = len(text)
    chars_no_spaces = len(text.replace(' ', ''))
    words = len(text.split())
    lines = len(text.splitlines())
    
    # 字符类型统计
    letters = sum(1 for c in text if c.isalpha())
    digits = sum(1 for c in text if c.isdigit())
    spaces = sum(1 for c in text if c.isspace())
    punctuation = sum(1 for c in text if not c.isalnum() and not c.isspace())
    
    # 查找重复字串
    duplicates = find_duplicate_substrings(text)
    
    return {
        'total_chars': total_chars,
        'chars_no_spaces': chars_no_spaces,
        'words': words,
        'lines': lines,
        'letters': letters,
        'digits': digits,
        'spaces': spaces,
        'punctuation': punctuation,
        'duplicates': duplicates
    }


def print_analysis_results(analysis):
    """
    打印分析结果
    
    Args:
        analysis (dict): 分析结果字典
    """
    print("\n" + "="*50)
    print("📊 文本分析结果")
    print("="*50)
    
    print(f"📏 总字符数: {analysis['total_chars']}")
    print(f"📝 不含空格字符数: {analysis['chars_no_spaces']}")
    print(f"📖 单词数: {analysis['words']}")
    print(f"📄 行数: {analysis['lines']}")
    
    print(f"\n📋 字符类型统计:")
    print(f"   字母: {analysis['letters']}")
    print(f"   数字: {analysis['digits']}")
    print(f"   空格: {analysis['spaces']}")
    print(f"   标点符号: {analysis['punctuation']}")
    
    if analysis['duplicates']:
        print(f"\n🔄 发现重复字串:")
        # 按长度和出现次数排序
        sorted_duplicates = sorted(
            analysis['duplicates'].items(), 
            key=lambda x: (len(x[0]), x[1]), 
            reverse=True
        )
        
        for substring, count in sorted_duplicates:
            print(f"   '{substring}' - 出现 {count} 次 (长度: {len(substring)})")
    else:
        print(f"\n✅ 未发现重复字串")


def main():
    """
    主函数
    """
    print("🔍 文本长度和重复字串分析器")
    print("输入 'quit' 或 'exit' 退出程序")
    print("-" * 50)
    
    while True:
        try:
            print("\n请输入要分析的文本:")
            text = input("> ")
            
            if text.lower() in ['quit', 'exit', '退出']:
                print("👋 再见!")
                break
            
            if not text.strip():
                print("⚠️  请输入有效的文本内容")
                continue
            
            # 分析文本
            analysis = analyze_text(text)
            
            # 打印结果
            print_analysis_results(analysis)
            
        except KeyboardInterrupt:
            print("\n\n👋 程序已退出")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    main()