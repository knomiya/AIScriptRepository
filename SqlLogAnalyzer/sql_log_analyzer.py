#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL日志分析工具
用于从SQL日志文件中提取方法名称和参数信息
"""

import re
import json
import argparse
import glob
import os
from typing import List, Dict, Optional
from datetime import datetime


class SqlLogAnalyzer:
    def __init__(self):
        # 正则表达式模式，用于匹配SQL日志
        self.log_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\s+'  # 时间戳
            r'\[([^\]]+)\]\s+'  # 线程名
            r'(\w+)\s+'  # 日志级别
            r'([^\s]+)\s+-\s+'  # 类名
            r'\[([^\]]+)\]'  # 请求ID
            r'.*?<([^>]+)>\s+\|\s+<([^>]+)>\s+'  # IP和用户
            r'\*+\s*'  # 星号分隔符
            r'([^\r\n]+?)(?:\r?\n|\s+)'  # 方法名（可能换行或空格分隔）
            r'(.*?)'  # SQL语句
            r'\[SQL_EXECUTE_TIME\(ms\)\]:(\d+),\s+'  # SQL执行时间
            r'\[LOG_EXECUTE_TIME\(ms\)\]:(\d+),\s+'  # 日志执行时间
            r'\[MATCH_ROWS\]:(\d+)'  # 匹配行数
            , re.DOTALL  # 允许.匹配换行符
        )
        
        # 提取参数的正则表达式
        self.param_patterns = [
            # IN 子句中的参数
            re.compile(r"IN\s*\(\s*([^)]+)\s*\)", re.IGNORECASE),
            # = 后面的参数
            re.compile(r"=\s*'([^']+)'", re.IGNORECASE),
            # LIKE 后面的参数
            re.compile(r"LIKE\s*'([^']+)'", re.IGNORECASE),
        ]

    def extract_parameters(self, sql: str) -> List[str]:
        """从SQL语句中提取参数"""
        parameters = []
        
        for pattern in self.param_patterns:
            matches = pattern.findall(sql)
            for match in matches:
                if "IN" in pattern.pattern.upper():
                    # 处理IN子句中的多个参数
                    params = [p.strip().strip("'\"") for p in match.split(',')]
                    parameters.extend(params)
                else:
                    parameters.append(match.strip().strip("'\""))
        
        return list(set(parameters))  # 去重

    def parse_log_entry(self, log_entry: str) -> Optional[Dict]:
        """解析日志条目（可能包含多行）"""
        match = self.log_pattern.search(log_entry)
        if not match:
            return None
        
        timestamp, thread, level, class_name, request_id, ip, user, method_name, sql, sql_time, log_time, match_rows = match.groups()
        
        # 提取参数
        parameters = self.extract_parameters(sql)
        
        return {
            'timestamp': timestamp,
            'thread': thread,
            'level': level,
            'class_name': class_name,
            'request_id': request_id,
            'ip': ip,
            'user': user,
            'method_name': method_name.strip(),
            'sql': sql.strip(),
            'parameters': parameters,
            'sql_execute_time_ms': int(sql_time),
            'log_execute_time_ms': int(log_time),
            'match_rows': int(match_rows)
        }

    def analyze_log_file(self, file_path: str, method_filter: List[str] = None, 
                        param_filter: List[str] = None) -> List[Dict]:
        """分析单个日志文件"""
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # 按日志条目分割（每个条目以时间戳开始）
                log_entries = re.split(r'(?=\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})', content)
                
                for entry_num, entry in enumerate(log_entries, 1):
                    if not entry.strip():
                        continue
                        
                    try:
                        parsed = self.parse_log_entry(entry.strip())
                        if parsed:
                            # 应用过滤器
                            if method_filter and not any(method in parsed['method_name'] for method in method_filter):
                                continue
                            
                            # 参数过滤：既在提取的参数中搜索，也在原始SQL中搜索
                            if param_filter:
                                param_found = False
                                
                                # 方法1：将参数列表重新组合成完整的搜索字符串
                                search_text = ' '.join(param_filter)
                                if search_text in parsed['sql'] or search_text in str(parsed['parameters']):
                                    param_found = True
                                
                                # 方法2：如果组合搜索失败，检查是否所有参数都在SQL中
                                if not param_found:
                                    all_params_found = True
                                    for param in param_filter:
                                        if param not in parsed['sql'] and param not in str(parsed['parameters']):
                                            all_params_found = False
                                            break
                                    if all_params_found:
                                        param_found = True
                                
                                # 方法3：如果还是失败，尝试逐个参数搜索（至少匹配一个）
                                if not param_found:
                                    for param in param_filter:
                                        if param in str(parsed['parameters']) or param in parsed['sql']:
                                            param_found = True
                                            break
                                
                                if not param_found:
                                    continue
                            
                            parsed['entry_number'] = entry_num
                            parsed['source_file'] = file_path
                            results.append(parsed)
                    except Exception as e:
                        print(f"文件 {file_path} 第{entry_num}个条目解析出错: {e}")
                        continue
        
        except FileNotFoundError:
            print(f"文件未找到: {file_path}")
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {e}")
        
        return results

    def expand_file_patterns(self, patterns: List[str]) -> List[str]:
        """展开文件模式，支持通配符"""
        expanded_files = []
        
        for pattern in patterns:
            if '*' in pattern or '?' in pattern:
                # 使用glob匹配通配符
                matched_files = glob.glob(pattern)
                if matched_files:
                    expanded_files.extend(matched_files)
                    print(f"通配符 '{pattern}' 匹配到 {len(matched_files)} 个文件")
                else:
                    print(f"警告: 通配符 '{pattern}' 没有匹配到任何文件")
            elif os.path.isdir(pattern):
                # 如果是目录，自动查找目录下的所有.log文件
                log_files = glob.glob(os.path.join(pattern, "*.log"))
                if log_files:
                    expanded_files.extend(log_files)
                    print(f"目录 '{pattern}' 中找到 {len(log_files)} 个.log文件")
                else:
                    print(f"警告: 目录 '{pattern}' 中没有找到.log文件")
            elif os.path.isfile(pattern):
                # 普通文件
                expanded_files.append(pattern)
            else:
                print(f"警告: 路径 '{pattern}' 不存在")
        
        # 去重并排序
        return sorted(list(set(expanded_files)))

    def analyze_log_files(self, file_patterns: List[str], method_filter: List[str] = None, 
                         param_filter: List[str] = None) -> List[Dict]:
        """分析多个日志文件，支持通配符模式"""
        # 展开文件模式
        file_paths = self.expand_file_patterns(file_patterns)
        
        if not file_paths:
            print("错误: 没有找到任何匹配的日志文件")
            return []
        
        print(f"总共将分析 {len(file_paths)} 个文件")
        
        all_results = []
        
        for file_path in file_paths:
            print(f"正在分析文件: {file_path}")
            results = self.analyze_log_file(file_path, method_filter, param_filter)
            all_results.extend(results)
            print(f"文件 {file_path} 找到 {len(results)} 条记录")
        
        return all_results

    def generate_summary(self, results: List[Dict]) -> Dict:
        """生成分析摘要"""
        if not results:
            return {}
        
        method_stats = {}
        param_stats = {}
        
        for result in results:
            method = result['method_name']
            method_stats[method] = method_stats.get(method, 0) + 1
            
            for param in result['parameters']:
                param_stats[param] = param_stats.get(param, 0) + 1
        
        return {
            'total_records': len(results),
            'unique_methods': len(method_stats),
            'unique_parameters': len(param_stats),
            'method_frequency': dict(sorted(method_stats.items(), key=lambda x: x[1], reverse=True)),
            'parameter_frequency': dict(sorted(param_stats.items(), key=lambda x: x[1], reverse=True)[:20])  # 只显示前20个
        }

    def export_results(self, results: List[Dict], output_file: str, format_type: str = 'json'):
        """导出结果"""
        try:
            if format_type.lower() == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            elif format_type.lower() == 'csv':
                import csv
                if results:
                    with open(output_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=results[0].keys())
                        writer.writeheader()
                        for result in results:
                            # 将参数列表转换为字符串
                            result_copy = result.copy()
                            result_copy['parameters'] = ', '.join(result['parameters'])
                            writer.writerow(result_copy)
            
            print(f"结果已导出到: {output_file}")
        except Exception as e:
            print(f"导出结果时出错: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='SQL日志分析工具',
        epilog='''
使用示例:
  %(prog)s file.log                    # 分析单个文件
  %(prog)s *.log                       # 分析当前目录所有.log文件
  %(prog)s logs/                       # 分析logs目录下所有.log文件
  %(prog)s logs/*.log                  # 分析logs目录下所有.log文件
  %(prog)s file1.log file2.log         # 分析多个指定文件
  %(prog)s **/*.log                    # 递归分析所有子目录的.log文件
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('log_files', nargs='+', 
                       help='SQL日志文件路径（支持通配符如*.log，目录路径，或多个文件）')
    parser.add_argument('--method-filter', nargs='+', help='方法名过滤器')
    parser.add_argument('--param-filter', nargs='+', help='参数过滤器')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', choices=['json', 'csv'], default='json', help='输出格式')
    parser.add_argument('--summary', action='store_true', help='显示分析摘要')
    parser.add_argument('--merge-files', action='store_true', help='合并多个文件的结果')
    
    args = parser.parse_args()
    
    analyzer = SqlLogAnalyzer()
    
    # 统一使用analyze_log_files方法，它现在支持通配符和目录
    print("正在查找和分析日志文件...")
    results = analyzer.analyze_log_files(
        args.log_files, 
        args.method_filter, 
        args.param_filter
    )
    
    print(f"\n总共找到 {len(results)} 条匹配记录")
    
    if args.summary:
        summary = analyzer.generate_summary(results)
        print("\n=== 分析摘要 ===")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        
        # 如果是多个文件，显示每个文件的统计
        if len(args.log_files) > 1:
            print("\n=== 各文件统计 ===")
            file_stats = {}
            for result in results:
                file_name = result['source_file']
                file_stats[file_name] = file_stats.get(file_name, 0) + 1
            
            for file_name, count in file_stats.items():
                print(f"  {file_name}: {count} 条记录")
    

    
    # 默认导出JSON文件
    if not args.output and results:
        # 生成默认文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_output = f"sql_analysis_{timestamp}.json"
        analyzer.export_results(results, default_output, 'json')
    elif args.output:
        analyzer.export_results(results, args.output, args.format)
    
    # 显示前10条记录作为预览
    if results:
        preview_count = min(10, len(results))
        print(f"\n=== 前{preview_count}条记录预览 ===")
        for i, result in enumerate(results[:preview_count], 1):
            print(f"\n记录 {i}:")
            print(f"  文件: {result.get('source_file', 'N/A')}")
            print(f"  时间: {result['timestamp']}")
            print(f"  方法: {result['method_name']}")
            print(f"  参数: {result['parameters']}")
            print(f"  SQL: {result['sql'][:100]}{'...' if len(result['sql']) > 100 else ''}")
            print(f"  执行时间: {result['sql_execute_time_ms']}ms")


if __name__ == '__main__':
    main()