# -*- coding: utf-8 -*-
"""
报告生成模块
"""

from datetime import datetime
from typing import List, Dict, Any
import os

class ReportGenerator:
    def generate_statistics_report(self, results: List[Dict[str, Any]], 
                                  output_path: str, since_date: datetime, until_date: datetime):
        """生成统计分析报告"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # 报告标题
            f.write("# Git 提交统计分析报告\n\n")
            f.write(f"**分析时间范围**: {since_date.strftime('%Y-%m-%d')} 至 {until_date.strftime('%Y-%m-%d')}\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # 总体概览
            self._write_overview(f, results)
            
            # 各项目统计分析
            for result in results:
                self._write_project_statistics(f, result)
            
            # 汇总统计
            self._write_summary_statistics(f, results)
    
    def generate_commits_report(self, results: List[Dict[str, Any]], 
                               output_path: str, since_date: datetime, until_date: datetime):
        """生成详细提交记录报告"""
        
        # 收集所有提交记录并按时间排序
        all_commits = []
        for result in results:
            for commit in result['commits']:
                commit['project_name'] = result['project_name']
                all_commits.append(commit)
        
        # 按时间倒序排序（最新的在前）
        all_commits.sort(key=lambda x: x['date'], reverse=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # 报告标题
            f.write("# Git 详细提交记录报告\n\n")
            f.write(f"**分析时间范围**: {since_date.strftime('%Y-%m-%d')} 至 {until_date.strftime('%Y-%m-%d')}\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**总提交数**: {len(all_commits)}\n\n")
            f.write("---\n\n")
            
            # 按时间顺序列出所有提交
            self._write_all_commits(f, all_commits)
    
    def generate_markdown_report(self, results: List[Dict[str, Any]], 
                                output_path: str, since_date: datetime, until_date: datetime):
        """生成完整的Markdown格式分析报告（保持兼容性）"""
        self.generate_statistics_report(results, output_path, since_date, until_date)
    
    def _write_overview(self, f, results: List[Dict[str, Any]]):
        """写入总体概览"""
        f.write("## 📊 总体概览\n\n")
        
        total_commits = sum(r['total_commits'] for r in results)
        total_authors = len(set().union(*[set(r['author_commits'].keys()) for r in results]))
        total_projects = len(results)
        
        f.write(f"- **分析项目数**: {total_projects}\n")
        f.write(f"- **总提交数**: {total_commits}\n")
        f.write(f"- **参与开发者**: {total_authors} 人\n")
        f.write(f"- **平均每项目提交数**: {total_commits // total_projects if total_projects > 0 else 0}\n\n")
        
        # 项目活跃度排行
        f.write("### 项目活跃度排行\n\n")
        f.write("| 排名 | 项目名称 | 提交数 | 开发者数 |\n")
        f.write("|------|----------|--------|----------|\n")
        
        sorted_results = sorted(results, key=lambda x: x['total_commits'], reverse=True)
        for i, result in enumerate(sorted_results, 1):
            f.write(f"| {i} | {result['project_name']} | {result['total_commits']} | {result['total_authors']} |\n")
        
        f.write("\n---\n\n")
    
    def _write_project_analysis(self, f, result: Dict[str, Any]):
        """写入单个项目的详细分析"""
        project_name = result['project_name']
        f.write(f"## 🚀 {project_name}\n\n")
        
        # 基础统计
        f.write("### 基础统计\n\n")
        f.write(f"- **总提交数**: {result['total_commits']}\n")
        f.write(f"- **参与开发者**: {result['total_authors']} 人\n")
        f.write(f"- **修改文件数**: {len(result['file_changes'])}\n")
        f.write(f"- **涉及文件类型**: {len(result['file_extensions'])} 种\n\n")
        
        # 开发者贡献排行
        if result['author_commits']:
            f.write("### 👥 开发者贡献排行\n\n")
            f.write("| 排名 | 开发者 | 提交数 | 修改文件数 | 贡献占比 |\n")
            f.write("|------|--------|--------|------------|----------|\n")
            
            sorted_authors = sorted(result['author_commits'].items(), key=lambda x: x[1], reverse=True)
            for i, (author, commits) in enumerate(sorted_authors, 1):
                files_count = result['author_files'].get(author, 0)
                percentage = (commits / result['total_commits']) * 100
                f.write(f"| {i} | {author} | {commits} | {files_count} | {percentage:.1f}% |\n")
            f.write("\n")
        
        # 文件修改频率
        if result['file_changes']:
            f.write("### 📁 文件修改频率 (Top 10)\n\n")
            f.write("| 排名 | 文件路径 | 修改次数 |\n")
            f.write("|------|----------|----------|\n")
            
            sorted_files = sorted(result['file_changes'].items(), key=lambda x: x[1], reverse=True)[:10]
            for i, (file_path, count) in enumerate(sorted_files, 1):
                f.write(f"| {i} | `{file_path}` | {count} |\n")
            f.write("\n")
        
        # 文件类型分布
        if result['file_extensions']:
            f.write("### 📊 文件类型分布\n\n")
            f.write("| 文件类型 | 修改次数 | 占比 |\n")
            f.write("|----------|----------|------|\n")
            
            total_file_changes = sum(result['file_extensions'].values())
            sorted_extensions = sorted(result['file_extensions'].items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_extensions:
                percentage = (count / total_file_changes) * 100
                f.write(f"| `{ext}` | {count} | {percentage:.1f}% |\n")
            f.write("\n")
        
        # 提交活跃度时间分布
        if result['daily_commits']:
            f.write("### 📅 提交活跃度时间分布\n\n")
            f.write("| 日期 | 提交数 |\n")
            f.write("|------|--------|\n")
            
            sorted_days = sorted(result['daily_commits'].items())
            for date, count in sorted_days:
                f.write(f"| {date} | {count} |\n")
            f.write("\n")
        
        # 最近提交记录
        f.write("### 📝 最近提交记录 (最新10条)\n\n")
        recent_commits = sorted(result['commits'], 
                              key=lambda x: x['date'], reverse=True)[:10]
        
        for commit in recent_commits:
            date = commit['date'][:19].replace('T', ' ')  # 格式化日期
            f.write(f"**{date}** - {commit['author_name']}\n")
            f.write(f"```\n{commit['message']}\n```\n")
            if commit['files']:
                f.write("修改文件:\n")
                for file_path in commit['files'][:5]:  # 只显示前5个文件
                    f.write(f"- `{file_path}`\n")
                if len(commit['files']) > 5:
                    f.write(f"- ... 还有 {len(commit['files']) - 5} 个文件\n")
            f.write("\n")
        
        f.write("---\n\n")
    
    def _write_summary_statistics(self, f, results: List[Dict[str, Any]]):
        """写入汇总统计"""
        f.write("## 📈 汇总统计\n\n")
        
        # 全局开发者统计
        all_authors = {}
        all_file_extensions = {}
        
        for result in results:
            for author, commits in result['author_commits'].items():
                all_authors[author] = all_authors.get(author, 0) + commits
            
            for ext, count in result['file_extensions'].items():
                all_file_extensions[ext] = all_file_extensions.get(ext, 0) + count
        
        # 全局开发者排行
        if all_authors:
            f.write("### 🏆 全局开发者排行\n\n")
            f.write("| 排名 | 开发者 | 总提交数 | 参与项目数 |\n")
            f.write("|------|--------|----------|------------|\n")
            
            sorted_global_authors = sorted(all_authors.items(), key=lambda x: x[1], reverse=True)
            for i, (author, total_commits) in enumerate(sorted_global_authors, 1):
                project_count = sum(1 for r in results if author in r['author_commits'])
                f.write(f"| {i} | {author} | {total_commits} | {project_count} |\n")
            f.write("\n")
        
        # 全局文件类型统计
        if all_file_extensions:
            f.write("### 🗂️ 全局文件类型统计\n\n")
            f.write("| 文件类型 | 总修改次数 | 占比 |\n")
            f.write("|----------|------------|------|\n")
            
            total_changes = sum(all_file_extensions.values())
            sorted_global_extensions = sorted(all_file_extensions.items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_global_extensions:
                percentage = (count / total_changes) * 100
                f.write(f"| `{ext}` | {count} | {percentage:.1f}% |\n")
            f.write("\n")
        
        f.write("---\n\n")
        f.write("*报告由 GitCommitAnalysis 工具自动生成*\n")
    
    def _write_project_statistics(self, f, result: Dict[str, Any]):
        """写入单个项目的统计分析（简化版）"""
        project_name = result['project_name']
        f.write(f"## 📊 {project_name} - 统计概览\n\n")
        
        # 基础统计
        f.write("### 基础统计\n\n")
        f.write(f"- **总提交数**: {result['total_commits']}\n")
        f.write(f"- **修改文件数**: {len(result['file_changes'])}\n")
        f.write(f"- **涉及文件类型**: {len(result['file_extensions'])} 种\n\n")
        
        # 文件修改频率 Top 10
        if result['file_changes']:
            f.write("### 📁 文件修改频率 (Top 10)\n\n")
            f.write("| 排名 | 文件路径 | 修改次数 |\n")
            f.write("|------|----------|----------|\n")
            
            sorted_files = sorted(result['file_changes'].items(), key=lambda x: x[1], reverse=True)[:10]
            for i, (file_path, count) in enumerate(sorted_files, 1):
                f.write(f"| {i} | `{file_path}` | {count} |\n")
            f.write("\n")
        
        # 文件类型分布
        if result['file_extensions']:
            f.write("### 📊 文件类型分布\n\n")
            f.write("| 文件类型 | 修改次数 | 占比 |\n")
            f.write("|----------|----------|------|\n")
            
            total_file_changes = sum(result['file_extensions'].values())
            sorted_extensions = sorted(result['file_extensions'].items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_extensions:
                percentage = (count / total_file_changes) * 100
                f.write(f"| `{ext}` | {count} | {percentage:.1f}% |\n")
            f.write("\n")
        
        # 提交活跃度时间分布
        if result['daily_commits']:
            f.write("### 📅 提交活跃度时间分布\n\n")
            f.write("| 日期 | 提交数 |\n")
            f.write("|------|--------|\n")
            
            sorted_days = sorted(result['daily_commits'].items())
            for date, count in sorted_days:
                f.write(f"| {date} | {count} |\n")
            f.write("\n")
        
        f.write("---\n\n")
    
    def _write_all_commits(self, f, all_commits: List[Dict[str, Any]]):
        """写入所有提交记录的详细信息"""
        f.write("## 📝 详细提交记录\n\n")
        f.write("*按时间倒序排列，最新提交在前*\n\n")
        
        current_date = None
        for i, commit in enumerate(all_commits, 1):
            commit_date = commit['date'][:10]  # 取日期部分
            
            # 如果是新的日期，添加日期分隔符
            if commit_date != current_date:
                current_date = commit_date
                f.write(f"### 📅 {commit_date}\n\n")
            
            # 提交信息
            time_part = commit['date'][11:19]  # 取时间部分
            f.write(f"#### #{i} - {time_part} - [{commit['project_name']}]\n\n")
            
            # 提交消息
            f.write(f"**提交消息**: {commit['message']}\n\n")
            
            # 提交哈希
            f.write(f"**提交哈希**: `{commit['hash'][:8]}`\n\n")
            
            # 修改的文件
            if commit['files']:
                f.write(f"**修改文件** ({len(commit['files'])} 个):\n\n")
                
                # 按文件类型分组
                file_groups = {}
                for file_path in commit['files']:
                    if '.' in file_path:
                        ext = '.' + file_path.split('.')[-1].lower()
                    else:
                        ext = '无扩展名'
                    
                    if ext not in file_groups:
                        file_groups[ext] = []
                    file_groups[ext].append(file_path)
                
                # 输出分组的文件
                for ext, files in sorted(file_groups.items()):
                    f.write(f"- **{ext}** ({len(files)} 个):\n")
                    for file_path in sorted(files):
                        f.write(f"  - `{file_path}`\n")
                    f.write("\n")
            else:
                f.write("**修改文件**: 无\n\n")
            
            f.write("---\n\n")