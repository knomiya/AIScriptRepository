# GitCommitAnalysis - Git提交分析工具

一个简洁高效的本地Git提交记录分析工具，专注于分析你自己的提交统计和生成详细报告。

## 功能特性

- 🔍 **本地项目分析**: 专注于本地Git项目，无需远程克隆
- � ***个人提交过滤**: 只分析指定作者的提交记录
- 🌿 **分支指定**: 精确分析指定分支的提交
- 📊 **详细统计**: 提交频率、文件变更、时间分布等多维度分析
- � **Markd*own报告**: 自动生成美观的分析报告
- ⏰ **灵活时间范围**: 支持自定义时间段分析
- 🚀 **批量扫描**: 自动发现目录下的所有Git项目

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法（所有参数都是必填的）

```bash
# 基本用法（必须指定作者、分支、扫描目录）
python main.py --author "你的邮箱" --branch main --scan-dir ~/projects

# 分析指定时间范围
python main.py --author "your-email@example.com" --branch develop --scan-dir ~/work --since 2024-01-01 --until 2024-01-31

# 分析最近7天
python main.py --author "张三" --branch main --scan-dir . --days 7

# 指定输出目录
python main.py --author "你的邮箱" --branch main --scan-dir ~/projects --output ./reports
```

## 命令行参数

### 必填参数
- `--author`: 指定要分析的作者姓名或邮箱（必填）
- `--branch`: 指定要分析的分支名称（必填）
- `--scan-dir`: 扫描指定目录下的所有Git项目（必填）

### 可选参数
- `--output, -o`: 输出目录 (默认: reports)
- `--since`: 开始时间 (格式: YYYY-MM-DD)
- `--until`: 结束时间 (格式: YYYY-MM-DD)
- `--days`: 分析最近N天的提交，当未指定since/until时使用 (默认: 30)

## 报告内容

生成的报告包含以下内容：

### 总体概览
- 分析项目数量
- 总提交数统计
- 参与开发者数量
- 项目活跃度排行

### 项目详细分析
- 基础统计信息
- 开发者贡献排行
- 文件修改频率
- 文件类型分布
- 提交活跃度时间分布
- 最近提交记录

### 汇总统计
- 全局开发者排行
- 全局文件类型统计

## 注意事项

1. 工具只分析本地Git项目，不进行远程克隆
2. 确保指定的目录包含Git仓库（包含.git文件夹）
3. 作者匹配支持姓名和邮箱的模糊匹配
4. 如果指定分支不存在，会尝试从远程创建或使用当前分支
5. 大型仓库的分析可能需要较长时间

## 示例输出

```
分析作者: 张三
分析分支: main
扫描目录: ~/projects
分析时间范围: 2024-01-01 到 2024-01-31

正在扫描目录: ~/projects
  发现项目: my-app (~/projects/my-app)
  发现项目: website (~/projects/website)
发现 2 个本地Git项目

正在分析项目: my-app
  分析分支: main
  过滤后的提交数: 15 / 25
✓ my-app 分析完成

正在分析项目: website
  分析分支: main
  过滤后的提交数: 8 / 12
✓ website 分析完成

📊 报告已生成: reports/git_analysis_report_20241119_143022.md
```

## 快速开始

### 1. 安装依赖
```bash
cd GitCommitAnalysis
pip install -r requirements.txt
```

### 2. 运行分析
```bash
# 分析当前目录下所有Git项目的main分支，最近30天的提交
python main.py --author "你的邮箱" --branch main --scan-dir .

# 分析指定目录和时间范围
python main.py --author "your-email@example.com" --branch develop --scan-dir ~/work --since 2024-01-01 --until 2024-01-31
```

### 3. 查看报告
分析完成后，在 `reports` 目录下查看生成的Markdown报告。

## 时间参数使用说明

### 时间格式要求
- 必须使用 `YYYY-MM-DD` 格式
- 注意每月的天数限制：
  - 1,3,5,7,8,10,12月：31天
  - 4,6,9,11月：30天  
  - 2月：28天（平年）或29天（闰年）
- 例如：`2024-01-01`、`2024-11-30`、`2024-12-31`
- 开始时间不能晚于结束时间

### 常用时间段示例
```bash
# 分析指定时间段
python main.py --author "你的邮箱" --branch main --scan-dir ~/projects --since 2024-01-01 --until 2024-01-31

# 分析最近7天
python main.py --author "你的邮箱" --branch main --scan-dir ~/projects --days 7

# 分析从指定日期到现在
python main.py --author "你的邮箱" --branch main --scan-dir ~/projects --since 2024-01-01
```