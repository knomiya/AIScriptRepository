#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单文本分析器 - 统计文本长度和重复字串
"""

def find_duplicates(text):
    """查找重复的字串"""
    duplicates = {}
    text_len = len(text)
    
    # 检查长度为2到文本长度一半的所有子字符串
    for length in range(2, text_len // 2 + 1):
        for i in range(text_len - length + 1):
            substring = text[i:i + length]
            
            # 跳过纯空格的子字符串
            if substring.strip():
                count = 0
                # 计算这个子字符串在文本中出现的次数
                for j in range(text_len - length + 1):
                    if text[j:j + length] == substring:
                        count += 1
                
                if count > 1:
                    duplicates[substring] = count
    
    return duplicates

def main():
    print("文本长度和重复字串分析器")
    print("输入文本，程序将分析其长度和重复字串")
    print("-" * 40)
    
    while True:
        text = input("\n请输入文本 (输入 'quit' 退出): ")
        
        if text.lower() == 'quit':
            break
            
        if not text:
            print("请输入有效文本")
            continue
        
        # 统计字符长度
        char_count = len(text)
        print(f"\n字符长度: {char_count}")
        
        # 查找重复字串
        duplicates = find_duplicates(text)
        
        if duplicates:
            print("\n重复的字串:")
            # 按字串长度排序显示
            for substring in sorted(duplicates.keys(), key=len, reverse=True):
                count = duplicates[substring]
                print(f"  '{substring}' - 重复 {count} 次")
        else:
            print("\n未发现重复字串")

if __name__ == "__main__":
    main()