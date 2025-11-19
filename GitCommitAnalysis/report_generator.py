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
        f.write("## 📊 个人开发统计概览\n\n")
        
        total_commits = sum(r['total_commits'] for r in results)
        total_projects = len(results)
        total_files_modified = sum(r['commit_stats']['total_files_modified'] for r in results)
        total_active_days = sum(r['commit_stats']['active_days'] for r in results)
        
        f.write(f"- **分析项目数**: {total_projects}\n")
        f.write(f"- **总提交数**: {total_commits}\n")
        f.write(f"- **总修改文件数**: {total_files_modified}\n")
        f.write(f"- **总活跃天数**: {total_active_days}\n")
        f.write(f"- **平均每项目提交数**: {total_commits // total_projects if total_projects > 0 else 0}\n")
        f.write(f"- **平均每天提交数**: {round(total_commits / total_active_days, 2) if total_active_days > 0 else 0}\n\n")
        
        # 项目开发强度排行
        f.write("### 项目开发强度排行\n\n")
        f.write("| 排名 | 项目名称 | 提交数 | 修改文件数 | 平均每次提交文件数 | 活跃天数 |\n")
        f.write("|------|----------|--------|------------|-------------------|----------|\n")
        
        sorted_results = sorted(results, key=lambda x: x['total_commits'], reverse=True)
        for i, result in enumerate(sorted_results, 1):
            avg_files = result['commit_stats']['avg_files_per_commit']
            active_days = result['commit_stats']['active_days']
            total_files = result['commit_stats']['total_files_modified']
            f.write(f"| {i} | {result['project_name']} | {result['total_commits']} | {total_files} | {avg_files} | {active_days} |\n")
        
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
        f.write("## 📈 个人开发习惯分析\n\n")
        
        # 汇总所有项目的统计数据
        all_file_extensions = {}
        all_weekday_commits = {}
        all_hour_commits = {}
        all_monthly_commits = {}
        all_large_commits = []
        all_top_commits = []
        
        for result in results:
            # 文件类型统计
            for ext, count in result['file_extensions'].items():
                all_file_extensions[ext] = all_file_extensions.get(ext, 0) + count
            
            # 工作时间习惯统计
            for weekday, count in result.get('weekday_commits', {}).items():
                all_weekday_commits[weekday] = all_weekday_commits.get(weekday, 0) + count
            
            for hour, count in result.get('hour_commits', {}).items():
                all_hour_commits[hour] = all_hour_commits.get(hour, 0) + count
            
            # 月度活跃度
            for month, count in result.get('monthly_commits', {}).items():
                all_monthly_commits[month] = all_monthly_commits.get(month, 0) + count
            
            # 收集大型提交和高频修改提交，添加项目信息
            large_commits_with_project = []
            for commit in result.get('large_commits', []):
                commit_with_project = commit.copy()
                commit_with_project['project'] = result['project_name']
                large_commits_with_project.append(commit_with_project)
            all_large_commits.extend(large_commits_with_project)
            
            top_commits_with_project = []
            for commit in result.get('top_commits_by_files', []):
                commit_with_project = commit.copy()
                commit_with_project['project'] = result['project_name']
                top_commits_with_project.append(commit_with_project)
            all_top_commits.extend(top_commits_with_project)
        
        # 开发技术栈分析
        if all_file_extensions:
            f.write("### 💻 开发技术栈分析\n\n")
            f.write("| 文件类型 | 修改次数 | 占比 | 技术领域 |\n")
            f.write("|----------|----------|------|----------|\n")
            
            # 定义技术领域映射
            tech_mapping = {
                '.py': 'Python开发', '.js': 'JavaScript开发', '.ts': 'TypeScript开发',
                '.java': 'Java开发', '.cpp': 'C++开发', '.c': 'C开发',
                '.html': '前端开发', '.css': '前端样式', '.vue': 'Vue.js开发',
                '.jsx': 'React开发', '.tsx': 'React TypeScript',
                '.sql': '数据库开发', '.json': '配置文件', '.yaml': '配置文件',
                '.md': '文档编写', '.txt': '文本文件', '.xml': '配置文件'
            }
            
            total_changes = sum(all_file_extensions.values())
            sorted_extensions = sorted(all_file_extensions.items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_extensions:
                percentage = (count / total_changes) * 100
                tech_area = tech_mapping.get(ext, '其他')
                f.write(f"| `{ext}` | {count} | {percentage:.1f}% | {tech_area} |\n")
            f.write("\n")
        
        # 工作时间习惯分析
        if all_weekday_commits:
            f.write("### ⏰ 工作时间习惯分析\n\n")
            
            # 星期几分布
            f.write("#### 📅 工作日分布\n\n")
            f.write("| 星期 | 提交数 | 占比 |\n")
            f.write("|------|--------|------|\n")
            
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            total_weekday_commits = sum(all_weekday_commits.values())
            
            for weekday in weekday_order:
                count = all_weekday_commits.get(weekday, 0)
                percentage = (count / total_weekday_commits) * 100 if total_weekday_commits > 0 else 0
                f.write(f"| {weekday} | {count} | {percentage:.1f}% |\n")
            f.write("\n")
            
            # 时间段分布
            if all_hour_commits:
                f.write("#### 🕐 时间段分布\n\n")
                f.write("| 时间段 | 提交数 | 工作习惯 |\n")
                f.write("|--------|--------|----------|\n")
                
                # 按时间段分组
                time_periods = {
                    '早晨 (6-9点)': sum(all_hour_commits.get(h, 0) for h in range(6, 10)),
                    '上午 (9-12点)': sum(all_hour_commits.get(h, 0) for h in range(9, 13)),
                    '下午 (12-18点)': sum(all_hour_commits.get(h, 0) for h in range(12, 19)),
                    '晚上 (18-22点)': sum(all_hour_commits.get(h, 0) for h in range(18, 23)),
                    '深夜 (22-6点)': sum(all_hour_commits.get(h, 0) for h in list(range(22, 24)) + list(range(0, 7)))
                }
                
                habit_desc = {
                    '早晨 (6-9点)': '早起型开发者',
                    '上午 (9-12点)': '标准工作时间',
                    '下午 (12-18点)': '标准工作时间',
                    '晚上 (18-22点)': '加班或业余开发',
                    '深夜 (22-6点)': '夜猫子型开发者'
                }
                
                for period, count in time_periods.items():
                    habit = habit_desc.get(period, '')
                    f.write(f"| {period} | {count} | {habit} |\n")
                f.write("\n")
        
        # 月度活跃度趋势
        if all_monthly_commits:
            f.write("### 📊 月度活跃度趋势\n\n")
            f.write("| 月份 | 提交数 | 活跃度 |\n")
            f.write("|------|--------|--------|\n")
            
            sorted_months = sorted(all_monthly_commits.items())
            max_monthly_commits = max(all_monthly_commits.values()) if all_monthly_commits else 1
            
            for month, count in sorted_months:
                activity_level = "🔥 高" if count > max_monthly_commits * 0.7 else "📈 中" if count > max_monthly_commits * 0.3 else "📉 低"
                f.write(f"| {month} | {count} | {activity_level} |\n")
            f.write("\n")
        
        # 大型提交分析
        if all_large_commits:
            f.write("### 🚀 大型提交分析 (修改文件数 > 10)\n\n")
            f.write("| 项目 | 日期 | 修改文件数 | 提交消息 |\n")
            f.write("|------|------|------------|----------|\n")
            
            # 按文件数排序，取前10个
            sorted_large_commits = sorted(all_large_commits, key=lambda x: x['file_count'], reverse=True)[:10]
            for commit in sorted_large_commits:
                message = commit['message'][:50] + ('...' if len(commit['message']) > 50 else '')
                f.write(f"| {commit.get('project', 'N/A')} | {commit['date'][:10]} | {commit['file_count']} | {message} |\n")
            f.write("\n")
        
        # 高频修改文件提交排行
        if all_top_commits:
            f.write("### 📁 单次提交修改文件数排行 (Top 10)\n\n")
            f.write("| 排名 | 项目 | 日期 | 修改文件数 | 提交消息 |\n")
            f.write("|------|------|------|------------|----------|\n")
            
            # 去重并按文件数排序
            unique_commits = {}
            for commit in all_top_commits:
                key = f"{commit['hash']}_{commit.get('project', 'N/A')}"
                if key not in unique_commits or commit['file_count'] > unique_commits[key]['file_count']:
                    unique_commits[key] = commit
            
            sorted_top_commits = sorted(unique_commits.values(), key=lambda x: x['file_count'], reverse=True)[:10]
            for i, commit in enumerate(sorted_top_commits, 1):
                message = commit['message'][:40] + ('...' if len(commit['message']) > 40 else '')
                f.write(f"| {i} | {commit.get('project', 'N/A')} | {commit['date'][:10]} | {commit['file_count']} | {message} |\n")
            f.write("\n")
        
        f.write("---\n\n")
        f.write("*报告由 GitCommitAnalysis 工具自动生成*\n")
    
    def _write_project_statistics(self, f, result: Dict[str, Any]):
        """写入单个项目的统计分析"""
        project_name = result['project_name']
        f.write(f"## 📊 {project_name} - 详细分析\n\n")
        
        # 基础统计
        commit_stats = result.get('commit_stats', {})
        f.write("### 📈 基础统计\n\n")
        f.write(f"- **总提交数**: {result['total_commits']}\n")
        f.write(f"- **修改文件总数**: {commit_stats.get('total_files_modified', 0)}\n")
        f.write(f"- **涉及文件类型**: {len(result['file_extensions'])} 种\n")
        f.write(f"- **活跃开发天数**: {commit_stats.get('active_days', 0)} 天\n")
        f.write(f"- **平均每次提交修改文件数**: {commit_stats.get('avg_files_per_commit', 0)}\n")
        f.write(f"- **单次提交最多修改文件数**: {commit_stats.get('max_files_per_commit', 0)}\n\n")
        
        # 单次提交修改文件数排行
        top_commits = result.get('top_commits_by_files', [])
        if top_commits:
            f.write("### 🏆 单次提交修改文件数排行 (Top 10)\n\n")
            f.write("| 排名 | 日期 | 修改文件数 | 提交消息 | 提交哈希 |\n")
            f.write("|------|------|------------|----------|----------|\n")
            
            for i, commit in enumerate(top_commits, 1):
                f.write(f"| {i} | {commit['date'][:10]} | {commit['file_count']} | {commit['message']} | `{commit['hash']}` |\n")
            f.write("\n")
        
        # 大型提交分析
        large_commits = result.get('large_commits', [])
        if large_commits:
            f.write("### 🚀 大型提交分析 (修改文件数 > 10)\n\n")
            f.write("| 日期 | 修改文件数 | 提交消息 | 提交哈希 |\n")
            f.write("|------|------------|----------|----------|\n")
            
            for commit in large_commits:
                message = commit['message'][:60] + ('...' if len(commit['message']) > 60 else '')
                f.write(f"| {commit['date'][:10]} | {commit['file_count']} | {message} | `{commit['hash']}` |\n")
            f.write("\n")
        
        # 文件修改频率 Top 15
        if result['file_changes']:
            f.write("### 📁 文件修改频率排行 (Top 15)\n\n")
            f.write("| 排名 | 文件路径 | 修改次数 | 文件类型 |\n")
            f.write("|------|----------|----------|----------|\n")
            
            sorted_files = sorted(result['file_changes'].items(), key=lambda x: x[1], reverse=True)[:15]
            for i, (file_path, count) in enumerate(sorted_files, 1):
                file_ext = '.' + file_path.split('.')[-1].lower() if '.' in file_path else '无扩展名'
                f.write(f"| {i} | `{file_path}` | {count} | `{file_ext}` |\n")
            f.write("\n")
        
        # 文件类型分布
        if result['file_extensions']:
            f.write("### 📊 开发技术栈分布\n\n")
            f.write("| 文件类型 | 修改次数 | 占比 | 技术领域 |\n")
            f.write("|----------|----------|------|----------|\n")
            
            # 技术领域映射
            tech_mapping = {
                '.py': 'Python开发', '.js': 'JavaScript开发', '.ts': 'TypeScript开发',
                '.java': 'Java开发', '.cpp': 'C++开发', '.c': 'C开发',
                '.html': '前端开发', '.css': '前端样式', '.vue': 'Vue.js开发',
                '.jsx': 'React开发', '.tsx': 'React TypeScript',
                '.sql': '数据库开发', '.json': '配置管理', '.yaml': '配置管理',
                '.md': '文档编写', '.txt': '文本处理', '.xml': '配置管理'
            }
            
            total_file_changes = sum(result['file_extensions'].values())
            sorted_extensions = sorted(result['file_extensions'].items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_extensions:
                percentage = (count / total_file_changes) * 100
                tech_area = tech_mapping.get(ext, '其他开发')
                f.write(f"| `{ext}` | {count} | {percentage:.1f}% | {tech_area} |\n")
            f.write("\n")
        
        # 提交活跃度时间分布
        if result['daily_commits']:
            f.write("### 📅 开发活跃度时间分布\n\n")
            
            # 按日期排序显示
            sorted_days = sorted(result['daily_commits'].items())
            
            # 如果天数太多，只显示活跃度最高的前20天
            if len(sorted_days) > 20:
                f.write("#### 最活跃的20天\n\n")
                f.write("| 日期 | 提交数 | 活跃度 |\n")
                f.write("|------|--------|--------|\n")
                
                # 按提交数排序，取前20
                top_active_days = sorted(result['daily_commits'].items(), key=lambda x: x[1], reverse=True)[:20]
                max_daily_commits = max(result['daily_commits'].values())
                
                for date, count in top_active_days:
                    activity_level = "🔥" if count > max_daily_commits * 0.7 else "📈" if count > max_daily_commits * 0.3 else "📉"
                    f.write(f"| {date} | {count} | {activity_level} |\n")
            else:
                f.write("| 日期 | 提交数 |\n")
                f.write("|------|--------|\n")
                
                for date, count in sorted_days:
                    f.write(f"| {date} | {count} |\n")
            f.write("\n")
        
        # 工作习惯分析
        weekday_commits = result.get('weekday_commits', {})
        if weekday_commits:
            f.write("### ⏰ 工作习惯分析\n\n")
            f.write("| 星期 | 提交数 | 工作偏好 |\n")
            f.write("|------|--------|----------|\n")
            
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_names = {'Monday': '周一', 'Tuesday': '周二', 'Wednesday': '周三', 
                           'Thursday': '周四', 'Friday': '周五', 'Saturday': '周六', 'Sunday': '周日'}
            
            for weekday in weekday_order:
                count = weekday_commits.get(weekday, 0)
                if weekday in ['Saturday', 'Sunday']:
                    preference = '周末开发' if count > 0 else ''
                else:
                    preference = '工作日开发' if count > 0 else ''
                
                f.write(f"| {weekday_names[weekday]} | {count} | {preference} |\n")
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