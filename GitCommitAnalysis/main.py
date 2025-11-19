#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git提交分析工具
支持GitHub、GitLab、Gitee等平台的项目提交记录分析
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from git_analyzer import GitAnalyzer
from report_generator import ReportGenerator


def main():
    parser = argparse.ArgumentParser(description='Git提交分析工具')

    parser.add_argument('--output', '-o', default='reports', help='输出目录')
    parser.add_argument('--since', help='开始时间 (YYYY-MM-DD)')
    parser.add_argument('--until', help='结束时间 (YYYY-MM-DD)')
    parser.add_argument('--days', type=int, default=30, help='分析最近N天的提交，当未指定since/until时使用 (默认30天)')
    parser.add_argument('--author', required=True, help='指定要分析的作者姓名或邮箱（必填）')
    parser.add_argument('--scan-dir', required=True, help='扫描指定目录下的所有Git项目进行分析（必填）')
    parser.add_argument('--branch', required=True, help='指定要分析的分支名称（必填）')
    
    args = parser.parse_args()
    
    # 设置作者过滤
    author_filter = {
        'enabled': True,
        'author_names': [args.author],
        'author_emails': [args.author]
    }
    print(f"分析作者: {args.author}")
    print(f"分析分支: {args.branch}")
    print(f"扫描目录: {args.scan_dir}")
    
    # 设置时间范围
    if args.since and args.until:
        try:
            since_date = datetime.strptime(args.since, '%Y-%m-%d')
            until_date = datetime.strptime(args.until, '%Y-%m-%d')
            
            # 验证时间范围
            if since_date > until_date:
                print("❌ 错误：开始时间不能晚于结束时间")
                return
                
        except ValueError as e:
            print(f"❌ 时间格式错误: {e}")
            print("请使用 YYYY-MM-DD 格式，注意：")
            print("  - 年份：使用4位数字，如 2024")
            print("  - 月份：01-12")
            print("  - 日期：注意每月的天数限制")
            print("  - 示例：2024-01-01, 2024-11-30, 2024-12-31")
            print(f"  - 当前日期：{datetime.now().strftime('%Y-%m-%d')}")
            return
            
    elif args.since:
        try:
            since_date = datetime.strptime(args.since, '%Y-%m-%d')
            until_date = datetime.now()
        except ValueError as e:
            print(f"❌ 开始时间格式错误: {e}")
            print("请使用 YYYY-MM-DD 格式，注意每月的天数限制")
            print(f"当前日期：{datetime.now().strftime('%Y-%m-%d')}")
            return
            
    elif args.until:
        try:
            until_date = datetime.strptime(args.until, '%Y-%m-%d')
            since_date = until_date - timedelta(days=args.days)
        except ValueError as e:
            print(f"❌ 结束时间格式错误: {e}")
            print("请使用 YYYY-MM-DD 格式，注意每月的天数限制")
            print(f"当前日期：{datetime.now().strftime('%Y-%m-%d')}")
            return
            
    else:
        # 默认分析最近N天
        until_date = datetime.now()
        since_date = until_date - timedelta(days=args.days)
    
    print(f"分析时间范围: {since_date.strftime('%Y-%m-%d')} 到 {until_date.strftime('%Y-%m-%d')}")
    
    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)
    
    # 初始化分析器和报告生成器
    analyzer = GitAnalyzer()
    report_generator = ReportGenerator()
    
    all_results = []
    
    # 扫描本地Git项目
    discovered_projects = analyzer.discover_local_projects(args.scan_dir)
    if not discovered_projects:
        print("❌ 在指定目录中没有找到Git项目")
        return
    
    # 设置所有项目使用指定分支
    for project in discovered_projects:
        project['branch'] = args.branch
    
    print(f"发现 {len(discovered_projects)} 个本地Git项目")
    
    # 分析每个项目
    for project in discovered_projects:
        print(f"\n正在分析项目: {project['name']}")
        
        try:
            # 分析项目
            result = analyzer.analyze_project(
                project, 
                since_date, 
                until_date,
                author_filter
            )
            
            if result:
                all_results.append(result)
                print(f"✓ {project['name']} 分析完成")
            else:
                print(f"✗ {project['name']} 分析失败")
                
        except Exception as e:
            print(f"✗ {project['name']} 分析出错: {str(e)}")
    
    # 生成报告
    if all_results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 生成统计报告
        stats_report_path = os.path.join(args.output, f"git_statistics_{timestamp}.md")
        report_generator.generate_statistics_report(all_results, stats_report_path, since_date, until_date)
        print(f"\n📊 统计报告已生成: {stats_report_path}")
        
        # 生成详细提交记录报告
        commits_report_path = os.path.join(args.output, f"git_commits_{timestamp}.md")
        report_generator.generate_commits_report(all_results, commits_report_path, since_date, until_date)
        print(f"📝 提交记录报告已生成: {commits_report_path}")
    else:
        print("\n❌ 没有成功分析的项目，无法生成报告")

if __name__ == '__main__':
    main()