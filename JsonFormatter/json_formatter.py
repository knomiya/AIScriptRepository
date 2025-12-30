#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON格式化工具
用于去除JSON中的转义字符并格式化输出

使用方法:
1. 命令行指定文件: python json_formatter.py input.json
2. 命令行指定文件并保存: python json_formatter.py input.json -o output.json
3. 交互式使用: python json_formatter.py
4. 直接输入JSON: python json_formatter.py -s '{"name":"test"}'
"""

import json
import sys
import argparse
from pathlib import Path


class JsonFormatter:
    """JSON格式化处理类"""
    
    def __init__(self):
        self.input_data = None
        self.output_data = None
    
    def load_from_string(self, json_string):
        """从字符串加载JSON数据，自动处理转义字符和嵌套JSON"""
        try:
            json_string = json_string.strip()
            
            # 第一步：解析外层JSON（自动处理转义字符）
            self.input_data = json.loads(json_string)
            
            # 第二步：递归处理嵌套的JSON字符串
            self.input_data = self._parse_nested_json(self.input_data)
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"提示: 请确保输入的是有效的JSON格式")
            return False
        except Exception as e:
            print(f"处理错误: {e}")
            return False
    
    def _parse_nested_json(self, obj):
        """递归解析嵌套的JSON字符串"""
        if isinstance(obj, dict):
            # 遍历字典的每个值
            for key, value in obj.items():
                if isinstance(value, str):
                    # 尝试将字符串解析为JSON
                    try:
                        parsed = json.loads(value)
                        # 递归处理解析后的对象
                        obj[key] = self._parse_nested_json(parsed)
                    except (json.JSONDecodeError, ValueError):
                        # 如果不是JSON字符串，保持原样
                        pass
                elif isinstance(value, (dict, list)):
                    # 递归处理嵌套的字典或列表
                    obj[key] = self._parse_nested_json(value)
        elif isinstance(obj, list):
            # 遍历列表的每个元素
            for i, item in enumerate(obj):
                if isinstance(item, str):
                    # 尝试将字符串解析为JSON
                    try:
                        parsed = json.loads(item)
                        # 递归处理解析后的对象
                        obj[i] = self._parse_nested_json(parsed)
                    except (json.JSONDecodeError, ValueError):
                        # 如果不是JSON字符串，保持原样
                        pass
                elif isinstance(item, (dict, list)):
                    # 递归处理嵌套的字典或列表
                    obj[i] = self._parse_nested_json(item)
        
        return obj
    
    def load_from_file(self, file_path):
        """从文件加载JSON数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return self.load_from_string(content)
        except FileNotFoundError:
            print(f"文件不存在: {file_path}")
            return False
        except Exception as e:
            print(f"读取文件错误: {e}")
            return False
    
    def format_json(self, indent=2, ensure_ascii=False, sort_keys=False):
        """格式化JSON数据"""
        if self.input_data is None:
            print("没有可格式化的数据")
            return None
        
        try:
            self.output_data = json.dumps(
                self.input_data,
                indent=indent,
                ensure_ascii=ensure_ascii,
                sort_keys=sort_keys
            )
            return self.output_data
        except Exception as e:
            print(f"格式化错误: {e}")
            return None
    
    def save_to_file(self, file_path):
        """保存格式化后的JSON到文件"""
        if self.output_data is None:
            print("没有可保存的数据，请先格式化")
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.output_data)
            print(f"已保存到: {file_path}")
            return True
        except Exception as e:
            print(f"保存文件错误: {e}")
            return False
    
    def print_formatted(self):
        """打印格式化后的JSON"""
        if self.output_data:
            print(self.output_data)
        else:
            print("没有可打印的数据")


def interactive_mode():
    """交互式模式"""
    print("=" * 50)
    print("JSON格式化工具 - 交互模式")
    print("=" * 50)
    
    formatter = JsonFormatter()
    
    # 选择输入方式
    print("\n请选择输入方式:")
    print("1. 从文件读取")
    print("2. 直接输入JSON字符串")
    print("3. 多行输入(输入END结束)")
    
    choice = input("\n请输入选项 (1/2/3): ").strip()
    
    if choice == '1':
        file_path = input("请输入文件路径: ").strip()
        if not formatter.load_from_file(file_path):
            return
    
    elif choice == '2':
        json_string = input("请输入JSON字符串: ").strip()
        if not formatter.load_from_string(json_string):
            return
    
    elif choice == '3':
        print("请输入JSON内容(输入END结束):")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            except EOFError:
                break
        json_string = '\n'.join(lines)
        if not formatter.load_from_string(json_string):
            return
    
    else:
        print("无效的选项")
        return
    
    # 格式化选项
    print("\n格式化选项:")
    indent = input("缩进空格数 (默认2): ").strip()
    indent = int(indent) if indent.isdigit() else 2
    
    sort_keys = input("是否排序键名? (y/n, 默认n): ").strip().lower() == 'y'
    
    # 执行格式化
    formatted = formatter.format_json(indent=indent, ensure_ascii=False, sort_keys=sort_keys)
    
    if formatted:
        print("\n" + "=" * 50)
        print("格式化结果:")
        print("=" * 50)
        formatter.print_formatted()
        
        # 保存选项
        save = input("\n是否保存到文件? (y/n): ").strip().lower()
        if save == 'y':
            output_path = input("请输入输出文件路径: ").strip()
            formatter.save_to_file(output_path)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='JSON格式化工具 - 去除转义字符并格式化输出',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python json_formatter.py input.json                    # 读取文件并输出
  python json_formatter.py input.json -o output.json     # 读取文件并保存
  python json_formatter.py -s '{"name":"test"}'          # 直接输入JSON字符串
  python json_formatter.py                               # 交互式模式
  python json_formatter.py input.json --indent 4 --sort  # 自定义格式化选项
        """
    )
    
    parser.add_argument('input_file', nargs='?', help='输入JSON文件路径')
    parser.add_argument('-s', '--string', help='直接输入JSON字符串')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('--indent', type=int, default=2, help='缩进空格数 (默认: 2)')
    parser.add_argument('--sort', action='store_true', help='按键名排序')
    
    args = parser.parse_args()
    
    formatter = JsonFormatter()
    
    # 判断输入方式
    if args.string:
        # 从命令行字符串输入
        if not formatter.load_from_string(args.string):
            sys.exit(1)
    elif args.input_file:
        # 从文件输入
        if not formatter.load_from_file(args.input_file):
            sys.exit(1)
    else:
        # 交互式模式
        interactive_mode()
        return
    
    # 格式化
    formatted = formatter.format_json(indent=args.indent, ensure_ascii=False, sort_keys=args.sort)
    
    if formatted:
        if args.output:
            # 保存到文件
            formatter.save_to_file(args.output)
        else:
            # 输出到控制台
            print("=" * 50)
            print("格式化结果:")
            print("=" * 50)
            formatter.print_formatted()


if __name__ == "__main__":
    main()
