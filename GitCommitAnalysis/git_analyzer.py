# -*- coding: utf-8 -*-
"""
Git分析模块
"""

import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import subprocess
import re

def run_git_command(cmd, cwd, description=""):
    """运行Git命令并打印日志"""
    cmd_str = ' '.join(cmd)
    print(f"  🔧 执行命令: {cmd_str}")
    if description:
        print(f"     目的: {description}")
    
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                              encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            output_lines = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            print(f"     ✅ 成功，输出 {output_lines} 行")
        elif result.returncode == 128 and 'dubious ownership' in result.stderr:
            print(f"     ⚠️  检测到所有权问题，尝试自动修复...")
            # 自动添加到安全目录
            safe_cmd = ['git', 'config', '--global', '--add', 'safe.directory', cwd]
            safe_result = subprocess.run(safe_cmd, capture_output=True, text=True,
                                       encoding='utf-8', errors='ignore')
            if safe_result.returncode == 0:
                print(f"     🔧 已添加到安全目录，重新执行命令...")
                # 重新执行原命令
                result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                                      encoding='utf-8', errors='ignore')
                if result.returncode == 0:
                    output_lines = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                    print(f"     ✅ 修复后成功，输出 {output_lines} 行")
                else:
                    print(f"     ❌ 修复后仍失败，返回码: {result.returncode}")
            else:
                print(f"     ❌ 无法自动修复所有权问题")
        else:
            print(f"     ❌ 失败，返回码: {result.returncode}")
            if result.stderr:
                print(f"     错误: {result.stderr.strip()[:100]}")
        
        return result
    except Exception as e:
        print(f"     ❌ 异常: {str(e)}")
        return None

class GitAnalyzer:
    def __init__(self):
        self.clone_dir = "./repos"
        
    def analyze_project(self, project: Dict[str, Any], since_date: datetime, 
                       until_date: datetime, author_filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """分析单个项目"""
        try:
            # 使用本地路径
            local_path = project.get('local_path') or project.get('url')
            if not os.path.exists(local_path) or not os.path.exists(os.path.join(local_path, '.git')):
                print(f"  本地路径不存在或不是Git仓库: {local_path}")
                return None
            
            # 获取提交记录
            branch = project.get('branch', 'main')
            print(f"  分析分支: {branch}")
            commits = self._get_commits(local_path, since_date, until_date, branch)
            
            if not commits:
                print(f"  未找到指定时间范围内的提交记录")
                return None
            
            # 过滤作者
            commits = self._filter_commits_by_author(commits, author_filter)
            if not commits:
                print(f"  未找到指定作者的提交记录")
                return None
            
            # 过滤合并提交和无实际代码的提交
            commits = self._filter_meaningful_commits(commits)
            if not commits:
                print(f"  过滤后没有有效的代码提交")
                return None
            
            # 分析提交数据
            analysis_result = self._analyze_commits(commits, project['name'])
            
            return analysis_result
            
        except Exception as e:
            print(f"  项目分析失败: {str(e)}")
            return None
    
    def _prepare_repository(self, project: Dict[str, Any], git_config: Dict[str, Any]) -> Optional[str]:
        """准备本地仓库"""
        clone_dir = git_config.get('clone_dir', self.clone_dir)
        os.makedirs(clone_dir, exist_ok=True)
        
        project_name = project['name'].replace(' ', '_').replace('/', '_')
        local_path = os.path.join(clone_dir, project_name)
        
        # 如果指定了本地路径，直接使用
        if project.get('local_path') and os.path.exists(project['local_path']):
            return project['local_path']
        
        # 检查是否已存在本地仓库
        if os.path.exists(local_path) and os.path.exists(os.path.join(local_path, '.git')):
            print(f"  更新本地仓库: {local_path}")
            result = run_git_command(['git', 'fetch', '--all'], local_path, "获取远程更新")
            if result and result.returncode == 0:
                return local_path
            else:
                print(f"  仓库更新失败，删除并重新克隆")
                shutil.rmtree(local_path)
        
        # 克隆仓库
        print(f"  克隆仓库: {project['url']}")
        result = run_git_command(['git', 'clone', project['url'], local_path], 
                                os.path.dirname(local_path), "克隆远程仓库")
        if result and result.returncode == 0:
            return local_path
        else:
            print(f"  克隆失败")
            return None
    
    def _get_commits(self, repo_path: str, since_date: datetime, 
                    until_date: datetime, branch: str = 'main') -> List[Dict[str, Any]]:
        """获取提交记录"""
        try:
            # 获取所有分支
            branches_result = run_git_command(['git', 'branch', '-a'], repo_path, "获取所有分支")
            
            # 尝试切换到指定分支，如果失败则使用当前分支
            current_branch = self._get_current_branch(repo_path)
            target_branch = branch
            
            if branches_result and branches_result.returncode == 0:
                branches = branches_result.stdout
                # 检查分支是否存在
                if f'origin/{branch}' in branches and f'* {branch}' not in branches:
                    # 远程分支存在但本地不存在，创建并切换
                    run_git_command(['git', 'checkout', '-b', branch, f'origin/{branch}'], 
                                  repo_path, f"创建并切换到分支 {branch}")
                elif branch in branches.replace('*', '').replace(' ', ''):
                    # 分支存在，直接切换
                    run_git_command(['git', 'checkout', branch], repo_path, f"切换到分支 {branch}")
                else:
                    # 分支不存在，使用当前分支
                    target_branch = current_branch or 'HEAD'
                    print(f"  分支 {branch} 不存在，使用当前分支: {target_branch}")
            
            # 构建git log命令
            since_str = since_date.strftime('%Y-%m-%d')
            until_str = until_date.strftime('%Y-%m-%d')
            
            # 先检查是否有任何提交
            check_result = run_git_command(['git', 'log', '--oneline', '-1'], repo_path, "检查是否有提交记录")
            
            if not check_result or check_result.returncode != 0 or not check_result.stdout.strip():
                print(f"  仓库没有提交记录")
                return []
            
            cmd = [
                'git', 'log',
                f'--since={since_str}',
                f'--until={until_str}',
                '--pretty=format:%H|%an|%ae|%ad|%s',
                '--date=iso',
                '--name-only',
                target_branch  # 只搜索指定分支
            ]
            
            result = run_git_command(cmd, repo_path, f"获取 {since_str} 到 {until_str} 的提交记录")
            
            if not result or result.returncode != 0:
                print(f"  获取提交记录失败")
                return []
            
            if not result.stdout.strip():
                print(f"  时间范围 {since_str} 到 {until_str} 内没有提交记录")
                # 尝试获取最近的几个提交来验证
                recent_result = run_git_command(['git', 'log', '--oneline', '-5', target_branch], 
                                              repo_path, "获取最近5个提交用于验证")
                if recent_result and recent_result.returncode == 0 and recent_result.stdout.strip():
                    print(f"  最近的提交:")
                    for line in recent_result.stdout.strip().split('\n')[:3]:
                        print(f"    {line}")
                return []
            
            return self._parse_git_log(result.stdout)
            
        except Exception as e:
            print(f"  获取提交记录失败: {e}")
            # 尝试不指定时间范围获取最近提交
            fallback_result = run_git_command(['git', 'log', '--oneline', '-10', target_branch], 
                                            repo_path, "获取最近10个提交作为备用")
            if fallback_result and fallback_result.returncode == 0 and fallback_result.stdout.strip():
                print(f"  仓库存在提交记录，但指定时间范围内没有找到")
                print(f"  最近的提交:")
                for line in fallback_result.stdout.strip().split('\n')[:3]:
                    print(f"    {line}")
            return []
    
    def _filter_commits_by_author(self, commits: List[Dict[str, Any]], 
                                 author_filter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据作者过滤提交记录"""
        
        author_names = author_filter.get('author_names', [])
        author_emails = author_filter.get('author_emails', [])
        
        print(f"  🔍 作者过滤条件: 姓名={author_names}, 邮箱={author_emails}")
        
        # 转换为小写进行比较
        author_names_lower = [name.lower() for name in author_names]
        author_emails_lower = [email.lower() for email in author_emails]
        
        # 收集所有作者信息用于调试
        all_authors = set()
        filtered_commits = []
        
        for commit in commits:
            author_name = commit['author_name'].lower()
            author_email = commit['author_email'].lower()
            all_authors.add(f"{commit['author_name']} <{commit['author_email']}>")
            
            # 检查作者姓名或邮箱是否匹配
            matched = False
            if (author_name in author_names_lower or 
                author_email in author_emails_lower or
                any(name in author_name for name in author_names_lower) or
                any(email in author_email for email in author_emails_lower)):
                filtered_commits.append(commit)
                matched = True
            
            # 调试信息：显示前几个提交的匹配情况
            if len(filtered_commits) + len([c for c in commits if c != commit]) <= 5:
                match_status = "✅ 匹配" if matched else "❌ 不匹配"
                print(f"    {match_status}: {commit['author_name']} <{commit['author_email']}> - {commit['message'][:30]}")
        
        print(f"  📊 仓库中的所有作者 ({len(all_authors)} 个):")
        for author in sorted(list(all_authors)): 
            print(f"    {author}")
        
        print(f"  ✅ 作者过滤结果: {len(filtered_commits)} / {len(commits)} 个提交匹配")
        return filtered_commits
    
    def _filter_meaningful_commits(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤掉合并提交和无实际代码的提交"""
        meaningful_commits = []
        merge_commits = []
        no_files_commits = []
        no_code_files_commits = []
        
        print(f"  🔍 开始过滤无意义提交...")
        
        for commit in commits:
            message = commit['message'].lower().strip()
            
            # 跳过合并提交
            if (message.startswith('merge') or 
                'merge branch' in message or 
                'merge pull request' in message or
                'merge remote-tracking branch' in message):
                merge_commits.append(commit)
                print(f"    🔀 跳过合并提交: {commit['message'][:50]}")
                continue
            
            # 跳过没有文件修改的提交
            if not commit['files']:
                no_files_commits.append(commit)
                print(f"    📁 跳过无文件修改: {commit['message'][:50]}")
                continue
            
            # 跳过只修改了非代码文件的提交（可选）
            code_files = []
            for file_path in commit['files']:
                # 检查是否是代码文件
                if self._is_code_file(file_path):
                    code_files.append(file_path)
            
            # 如果有代码文件修改，保留这个提交
            if code_files:
                # 更新提交记录，只保留代码文件
                original_file_count = len(commit['files'])
                commit['files'] = code_files
                meaningful_commits.append(commit)
                print(f"    ✅ 保留提交: {commit['message'][:50]} (代码文件: {len(code_files)}/{original_file_count})")
            else:
                no_code_files_commits.append(commit)
                print(f"    📄 跳过非代码文件: {commit['message'][:50]} (文件: {', '.join(commit['files'][:3])})")
        
        print(f"  📊 过滤统计:")
        print(f"    - 合并提交: {len(merge_commits)} 个")
        print(f"    - 无文件修改: {len(no_files_commits)} 个")
        print(f"    - 仅非代码文件: {len(no_code_files_commits)} 个")
        print(f"    - 保留的有效提交: {len(meaningful_commits)} 个")
        print(f"  ✅ 过滤结果: {len(meaningful_commits)} / {len(commits)} 个提交保留")
        return meaningful_commits
    
    def _is_code_file(self, file_path: str) -> bool:
        """判断是否是代码文件"""
        if not file_path or '.' not in file_path:
            return False
        
        # 代码文件扩展名
        code_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp', 
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.html', '.css', '.scss', '.less', '.vue', '.jsx', '.tsx',
            '.sql', '.xml', '.json', '.yaml', '.yml', '.sh', '.bat',
            '.dockerfile', '.makefile', '.gradle', '.maven'
        }
        
        # 非代码文件扩展名（排除）
        non_code_extensions = {
            '.md', '.txt', '.doc', '.docx', '.pdf', '.png', '.jpg', '.jpeg', 
            '.gif', '.svg', '.ico', '.zip', '.tar', '.gz', '.log', '.tmp'
        }
        
        ext = '.' + file_path.split('.')[-1].lower()
        
        # 如果是明确的非代码文件，返回False
        if ext in non_code_extensions:
            return False
        
        # 如果是明确的代码文件，返回True
        if ext in code_extensions:
            return True
        
        # 对于未知扩展名，检查文件名
        filename = file_path.lower()
        if ('makefile' in filename or 'dockerfile' in filename or 
            'jenkinsfile' in filename or 'rakefile' in filename):
            return True
        
        # 默认认为是代码文件（保守策略）
        return True
    
    def discover_local_projects(self, scan_dir: str) -> List[Dict[str, Any]]:
        """扫描目录下的所有Git项目"""
        projects = []
        
        if not os.path.exists(scan_dir):
            print(f"扫描目录不存在: {scan_dir}")
            return projects
        
        print(f"正在扫描目录: {scan_dir}")
        
        # 遍历目录
        for root, dirs, files in os.walk(scan_dir):
            # 如果当前目录包含.git文件夹，说明是Git项目
            if '.git' in dirs:
                project_name = os.path.basename(root)
                
                # 获取当前分支
                current_branch = self._get_current_branch(root)
                
                project = {
                    'name': project_name,
                    'url': root,
                    'platform': 'local',
                    'local_path': root,
                    'branch': current_branch or 'main'
                }
                
                projects.append(project)
                print(f"  发现项目: {project_name} ({root})")
                
                # 不再深入.git目录
                dirs.remove('.git')
        
        return projects
    
    
    def _get_current_branch(self, repo_path: str) -> Optional[str]:
        """获取当前分支名"""
        result = run_git_command(['git', 'branch', '--show-current'], repo_path, "获取当前分支")
        if result and result.returncode == 0:
            return result.stdout.strip()
        return None
    
    def _parse_git_log(self, git_log_output: str) -> List[Dict[str, Any]]:
        """解析git log输出"""
        commits = []
        lines = git_log_output.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
                
            # 解析提交信息行
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 5:
                    commit_hash = parts[0]
                    author_name = parts[1]
                    author_email = parts[2]
                    date_str = parts[3]
                    message = '|'.join(parts[4:])
                    
                    # 获取修改的文件
                    files = []
                    i += 1
                    while i < len(lines) and lines[i].strip() and '|' not in lines[i]:
                        file_path = lines[i].strip()
                        if file_path:
                            files.append(file_path)
                        i += 1
                    
                    commits.append({
                        'hash': commit_hash,
                        'author_name': author_name,
                        'author_email': author_email,
                        'date': date_str,
                        'message': message,
                        'files': files
                    })
                    continue
            
            i += 1
        
        return commits
    
    def _analyze_commits(self, commits: List[Dict[str, Any]], project_name: str) -> Dict[str, Any]:
        """分析提交数据"""
        # 基础统计
        total_commits = len(commits)
        authors = set(commit['author_name'] for commit in commits)
        
        # 文件变更统计
        file_changes = Counter()
        file_extensions = Counter()
        
        # 作者统计
        author_commits = Counter()
        author_files = defaultdict(set)
        
        # 日期统计
        daily_commits = Counter()
        monthly_commits = Counter()
        weekly_commits = Counter()
        
        # 提交规模统计
        commit_file_counts = []  # 每次提交修改的文件数
        large_commits = []  # 大型提交（修改文件数 > 10）
        
        # 时间段统计
        hour_commits = Counter()
        weekday_commits = Counter()
        
        for commit in commits:
            author = commit['author_name']
            author_commits[author] += 1
            
            # 日期和时间统计
            date_str = commit['date'][:10]  # 取日期部分
            daily_commits[date_str] += 1
            
            # 月份统计
            month_str = commit['date'][:7]  # YYYY-MM
            monthly_commits[month_str] += 1
            
            # 解析日期获取星期几
            try:
                from datetime import datetime
                commit_datetime = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
                weekday = commit_datetime.strftime('%A')  # 星期几
                weekday_commits[weekday] += 1
                
                hour = commit_datetime.hour
                hour_commits[hour] += 1
            except:
                pass
            
            # 文件统计
            file_count = len(commit['files'])
            commit_file_counts.append(file_count)
            
            # 大型提交统计
            if file_count > 10:
                large_commits.append({
                    'hash': commit['hash'][:8],
                    'message': commit['message'],
                    'date': commit['date'][:19],
                    'file_count': file_count,
                    'files': commit['files']
                })
            
            for file_path in commit['files']:
                file_changes[file_path] += 1
                author_files[author].add(file_path)
                
                # 文件扩展名统计
                if '.' in file_path:
                    ext = '.' + file_path.split('.')[-1].lower()
                    file_extensions[ext] += 1
        
        # 计算提交规模统计
        avg_files_per_commit = sum(commit_file_counts) / len(commit_file_counts) if commit_file_counts else 0
        max_files_commit = max(commit_file_counts) if commit_file_counts else 0
        
        # 找出修改文件最多的提交记录（前10）
        commits_by_file_count = sorted(commits, key=lambda x: len(x['files']), reverse=True)[:10]
        top_commits_by_files = []
        for commit in commits_by_file_count:
            top_commits_by_files.append({
                'hash': commit['hash'][:8],
                'message': commit['message'][:100] + ('...' if len(commit['message']) > 100 else ''),
                'date': commit['date'][:19],
                'file_count': len(commit['files']),
                'author': commit['author_name']
            })
        
        # 活跃度分析
        active_days = len(daily_commits)
        total_days = (max(daily_commits.keys()) if daily_commits else datetime.now().strftime('%Y-%m-%d')) 
        
        return {
            'project_name': project_name,
            'total_commits': total_commits,
            'total_authors': len(authors),
            'commits': commits,
            'author_commits': dict(author_commits.most_common()),
            'file_changes': dict(file_changes.most_common(20)),  # 前20个最常修改的文件
            'file_extensions': dict(file_extensions.most_common()),
            'daily_commits': dict(daily_commits),
            'monthly_commits': dict(monthly_commits),
            'weekday_commits': dict(weekday_commits),
            'hour_commits': dict(hour_commits),
            'author_files': {author: len(files) for author, files in author_files.items()},
            # 新增的个人开发统计
            'commit_stats': {
                'avg_files_per_commit': round(avg_files_per_commit, 2),
                'max_files_per_commit': max_files_commit,
                'total_files_modified': len(file_changes),
                'active_days': active_days
            },
            'top_commits_by_files': top_commits_by_files,
            'large_commits': large_commits[:10]  # 只保留前10个大型提交
        }