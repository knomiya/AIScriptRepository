# Excel列去重工具使用说明

## 功能描述
这个脚本可以读取Excel文件中指定列的数据，去除重复项，并将唯一值导出到文本文件中。

## 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法
```bash
python excel_deduplicator.py 文件名.xlsx -c "列名"
```

### 完整参数
```bash
python excel_deduplicator.py 文件名.xlsx -c "列名" -s "工作表名" -o "输出文件.txt"
```

## 参数说明
- `excel_file`: Excel文件路径（必需）
- `-c, --column`: 要处理的列名（必需）
- `-s, --sheet`: 工作表名称（可选，默认使用第一个工作表）
- `-o, --output`: 输出文件路径（可选，默认自动生成文件名）

## 使用示例

### 示例1：处理姓名列
```bash
python excel_deduplicator.py data.xlsx -c "姓名"
```
输出文件：`data_姓名_unique.txt`

### 示例2：指定工作表和输出文件
```bash
python excel_deduplicator.py employees.xlsx -c "邮箱" -s "员工信息" -o "unique_emails.txt"
```

### 示例3：处理包含中文的列名
```bash
python excel_deduplicator.py 客户数据.xlsx -c "客户编号"
```

## 输出格式
- 文本文件，每行一个唯一值
- 自动去除空值
- 按字母/数字顺序排序
- UTF-8编码

## 注意事项
1. 确保Excel文件存在且可读
2. 列名必须完全匹配（区分大小写）
3. 如果列名不存在，程序会显示所有可用列名
4. 输出文件会覆盖同名文件

## 错误处理
- 文件不存在：显示错误信息并退出
- 列名不存在：显示可用列名
- 读取错误：显示详细错误信息