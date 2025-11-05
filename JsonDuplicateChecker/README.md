# JSON重复字段检查器

这是一个用于检查大型JSON文件中指定字段重复值的Python脚本。

## 功能特点

- 🚀 **高效处理大文件**: 逐行读取，适合处理10M+的大文件
- 🔍 **灵活字段检查**: 可以检查任意字段的重复值
- 📊 **详细统计报告**: 显示重复值、出现次数、行号等信息
- 💾 **结果导出**: 可将重复记录导出到JSON文件
- 🛡️ **错误处理**: 完善的异常处理和错误提示

## 使用方法

### 命令行使用

```bash
# 基本用法
python json_duplicate_checker.py <文件路径> <字段名>

# 示例：检查email字段重复
python json_duplicate_checker.py data.txt email

# 将结果保存到文件
python json_duplicate_checker.py data.txt email --output duplicates.json
```

### 作为模块使用

```python
from json_duplicate_checker import find_duplicates_in_json_file, print_duplicate_statistics

# 查找重复值
duplicates = find_duplicates_in_json_file('data.txt', 'email')

# 打印统计信息
print_duplicate_statistics(duplicates, 'email')
```

## 输入文件格式

输入文件应该是纯文本文件，每行包含一个JSON对象：

```
{"id": "001", "name": "张三", "email": "zhangsan@example.com"}
{"id": "002", "name": "李四", "email": "lisi@example.com"}
{"id": "003", "name": "王五", "email": "zhangsan@example.com"}
```

## 运行测试

```bash
# 运行测试示例
python example_usage.py
```

这将创建测试数据并演示如何检查不同字段的重复值。

## 输出示例

```
📊 重复值统计报告
字段名: email
发现 2 个重复的字段值
总共涉及 4 条记录

============================================================

🔄 重复值: zhangsan@example.com
   出现次数: 2
   所在行号: [1, 3]
   重复记录详情:
     [1] 行号 1: {"id":"001","name":"张三","email":"zhangsan@example.com"}
     [2] 行号 3: {"id":"003","name":"王五","email":"zhangsan@example.com"}
```

## 性能说明

- 使用逐行读取方式，内存占用低
- 适合处理10M+的大文件
- 时间复杂度: O(n)，其中n为记录数量
- 空间复杂度: O(k)，其中k为唯一字段值数量

## 注意事项

1. 确保输入文件编码为UTF-8
2. 每行必须是有效的JSON对象
3. 字段值会转换为字符串进行比较
4. 缺少指定字段的记录会显示警告但不会中断处理