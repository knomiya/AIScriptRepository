# JSON格式化工具

一个用于去除JSON中的转义字符并格式化输出的Python工具。

## 功能特点

- 自动识别并处理转义的JSON字符串
- 支持多种输入方式（文件、直接输入、多行粘贴）
- 支持任意文件扩展名（.txt、.json、.log等），只要内容是JSON格式
- 可自定义缩进格式
- 支持键名排序
- 保留中文字符（不转义为Unicode）
- 可保存格式化结果到文件

## 使用方法

### 1. 命令行模式 - 读取文件

```bash
# 读取JSON文件并输出到控制台
python json_formatter.py input.json

# 读取TXT文件中的JSON并输出
python json_formatter.py data.txt

# 读取LOG文件中的JSON并输出
python json_formatter.py api_response.log

# 读取文件并保存到新文件
python json_formatter.py input.txt -o output.json

# 自定义缩进和排序
python json_formatter.py data.txt --indent 4 --sort
```

### 2. 命令行模式 - 直接输入

```bash
# 直接输入JSON字符串
python json_formatter.py -s '{"name":"张三","age":25}'

# 直接输入并保存
python json_formatter.py -s '{"name":"张三"}' -o output.json
```

### 3. 交互式模式

```bash
# 不带参数运行，进入交互模式
python json_formatter.py
```

按照提示选择输入方式和格式化选项。

### 4. 作为模块使用

```python
from json_formatter import JsonFormatter

# 创建格式化器
formatter = JsonFormatter()

# 从字符串加载
json_string = '{"name":"张三","age":25}'
formatter.load_from_string(json_string)

# 或从文件加载
# formatter.load_from_file('input.json')

# 格式化
formatted = formatter.format_json(indent=2, sort_keys=False)

# 打印结果
formatter.print_formatted()

# 保存到文件
formatter.save_to_file('output.json')
```

## 使用示例

### 示例1: 处理转义的JSON字符串

输入:
```
"{\"name\":\"张三\",\"age\":25,\"city\":\"北京\"}"
```

输出:
```json
{
  "name": "张三",
  "age": 25,
  "city": "北京"
}
```

### 示例2: 处理嵌套JSON

输入:
```
{"user":{"name":"李四","info":{"age":30,"email":"test@example.com"}}}
```

输出:
```json
{
  "user": {
    "name": "李四",
    "info": {
      "age": 30,
      "email": "test@example.com"
    }
  }
}
```

### 示例3: 处理数组

输入:
```
{"users":[{"name":"王五","age":28},{"name":"赵六","age":32}]}
```

输出:
```json
{
  "users": [
    {
      "name": "王五",
      "age": 28
    },
    {
      "name": "赵六",
      "age": 32
    }
  ]
}
```

## 参数说明

- `indent`: 缩进空格数，默认为2
- `ensure_ascii`: 是否将非ASCII字符转义，默认为False（保留中文）
- `sort_keys`: 是否按键名排序，默认为False

## 常见问题

### Q: 如何处理包含转义字符的JSON？
A: 工具会自动识别并处理，如果输入的字符串以引号开始和结束，会先进行一次解析。

### Q: 支持哪些文件格式？
A: 支持任意文件扩展名（.txt、.json、.log、.data等），只要文件内容是有效的JSON格式即可。

### Q: 支持哪些输入格式？
A: 支持标准JSON格式、转义的JSON字符串、从文件读取等多种方式。

### Q: 中文会被转义吗？
A: 不会，工具默认保留中文字符，不会转换为\uXXXX格式。

## 注意事项

- 确保输入的是有效的JSON格式
- 文件编码建议使用UTF-8
- 大文件处理时注意内存占用

## 依赖

- Python 3.6+
- 无需额外依赖包（仅使用标准库）
