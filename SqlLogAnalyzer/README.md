# SQL日志分析工具

这是一个用于分析SQL日志文件的Python脚本，可以提取方法名称和参数信息。

## 功能特性

- 解析SQL日志文件，提取关键信息
- 识别方法名称和SQL参数
- 支持多种参数格式（IN子句、等号赋值、LIKE语句等）
- 提供过滤功能（按方法名或参数过滤）
- 智能参数搜索：既在提取的参数中搜索，也在原始SQL语句中搜索
- 支持通配符文件匹配（*.log、**/*.log等）
- 支持目录批量处理
- 生成分析摘要统计
- 自动导出JSON格式结果
- 支持JSON和CSV格式导出
- 显示前10条记录预览，包含完整SQL语句

## 使用方法

### 基本用法

```bash
# 分析单个文件
python sql_log_analyzer.py your_log_file.log

# 分析多个文件
python sql_log_analyzer.py file1.log file2.log file3.log

# 使用通配符分析当前目录所有.log文件
python sql_log_analyzer.py *.log

# 分析指定目录下所有.log文件
python sql_log_analyzer.py logs/

# 使用通配符分析指定目录下所有.log文件
python sql_log_analyzer.py logs/*.log

# 递归分析所有子目录的.log文件
python sql_log_analyzer.py **/*.log
```

### 高级用法

```bash
# 按方法名过滤（单个文件）
python sql_log_analyzer.py log_file.log --method-filter listByVcrNos selectById

# 按参数过滤（多个文件）- 支持在SQL语句中直接搜索
python sql_log_analyzer.py file1.log file2.log --param-filter OBO25112410400001

# 搜索特定方法和参数（在SQL中搜索参数值）
python sql_log_analyzer.py *.log --method-filter updateBatchByPk --param-filter 35904

# 生成摘要统计（自动导出JSON文件）
python sql_log_analyzer.py log_file.log --summary

# 分析多个文件并显示各文件统计
python sql_log_analyzer.py *.log --summary

# 指定输出文件名和格式
python sql_log_analyzer.py log_file.log --output results.json --format json

# 导出结果到CSV文件
python sql_log_analyzer.py file1.log file2.log --output results.csv --format csv

# 组合使用：多文件分析+过滤+导出
python sql_log_analyzer.py app1.log app2.log app3.log --method-filter listByVcrNos --summary --output filtered_results.json

# 使用通配符分析所有日志文件
python sql_log_analyzer.py logs/*.log --summary

# 分析当前目录所有.log文件并生成摘要
python sql_log_analyzer.py *.log --summary

# 分析指定目录下所有.log文件
python sql_log_analyzer.py logs/ --summary

# 递归分析所有子目录的.log文件
python sql_log_analyzer.py **/*.log --method-filter listByVcrNos --output recursive_results.csv --format csv
```

## 参数说明

- `log_files`: SQL日志文件路径（必需，支持以下格式）：
  - 单个文件：`file.log`
  - 多个文件：`file1.log file2.log`
  - 通配符：`*.log`、`logs/*.log`
  - 目录：`logs/`（自动查找目录下所有.log文件）
  - 递归通配符：`**/*.log`（查找所有子目录）
- `--method-filter`: 方法名过滤器，可以指定多个方法名
- `--param-filter`: 参数过滤器，可以指定多个参数值
- `--output, -o`: 输出文件路径
- `--format`: 输出格式，支持json和csv
- `--summary`: 显示分析摘要
- `--merge-files`: 合并多个文件的结果（默认行为）

## 新功能说明

### 智能参数搜索
脚本现在支持两种参数搜索方式：
1. **提取参数搜索**：从SQL语句中提取的参数列表中搜索
2. **SQL语句搜索**：直接在原始SQL语句中搜索参数值

例如，搜索 `35904` 时，既会在提取的参数 `['T01']` 中搜索，也会在SQL语句 `WHERE outbound_order_detail_id = 35904` 中搜索。

### 自动导出功能
- 如果不指定 `--output` 参数，脚本会自动生成带时间戳的JSON文件
- 文件名格式：`sql_analysis_YYYYMMDD_HHMMSS.json`
- 确保每次运行都有结果备份

### 增强预览功能
- 显示前10条记录（而不是3条）
- 预览中包含SQL语句内容（前100个字符）
- 更详细的记录信息展示

## 日志格式支持

脚本支持以下格式的SQL日志：

```
2025-11-24 10:40:14.543 [http-nio-8026-exec-4] DEBUG com.framework.common.core.db.SqlLogUtils - [fe848d62d5ac4c83a7663bea9966005d]******* <192.168.56.11> | <SYSTEM> *******com.sunlord.psm.dao.IStockLotTradeLogDao.listByVcrNosSELECT ... WHERE vcr_no IN ( 'OBO25112410400001' )[SQL_EXECUTE_TIME(ms)]:7, [LOG_EXECUTE_TIME(ms)]:0, [MATCH_ROWS]:1
```

## 输出信息

脚本会提取以下信息：

- 时间戳
- 线程名
- 日志级别
- 类名
- 请求ID
- IP地址
- 用户
- 方法名称
- SQL语句
- 参数列表
- SQL执行时间
- 日志执行时间
- 匹配行数

## 示例输出

### JSON格式输出
```json
{
  "timestamp": "2025-11-24 10:20:00.433",
  "thread": "http-nio-8026-exec-5",
  "level": "DEBUG",
  "class_name": "com.framework.common.core.db.SqlLogUtils",
  "request_id": "12d4f04178ba434993023cf043a9f80f",
  "ip": "192.168.56.11",
  "user": "SYSTEM",
  "method_name": "com.sunlord.psm.dao.IOutboundOrderLineDao.updateBatchByPk",
  "sql": "UPDATE psm.outbound_order_line set to_bill_status = 'T01', to_bill_qty = 3000 WHERE outbound_order_detail_id = 35904",
  "parameters": ["T01"],
  "sql_execute_time_ms": 1,
  "log_execute_time_ms": 0,
  "match_rows": 1,
  "entry_number": 492,
  "source_file": "sql.log.2025-11-24.7.log"
}
```

### 控制台预览输出
```
=== 前10条记录预览 ===

记录 1:
  文件: sql.log.2025-11-24.7.log
  时间: 2025-11-24 10:20:00.433
  方法: com.sunlord.psm.dao.IOutboundOrderLineDao.updateBatchByPk
  参数: ['T01']
  SQL: UPDATE psm.outbound_order_line set to_bill_status = 'T01', to_bill_qty = 3000 WHERE outbound_or...
  执行时间: 1ms
```

## 注意事项

1. 确保日志文件编码为UTF-8
2. 大文件处理时可能需要较长时间
3. 参数提取基于常见的SQL模式，复杂的SQL可能需要调整正则表达式
4. 建议先用小文件测试，确认解析效果后再处理大文件
5. 脚本会自动生成JSON结果文件，注意磁盘空间
6. 使用通配符时注意文件数量，避免处理过多文件导致内存不足

## 性能建议

- 对于大量文件，建议分批处理
- 使用过滤器可以显著提高处理速度
- 大文件建议先用 `--summary` 查看概况
- JSON格式比CSV格式处理更快

## 版本更新

### v2.0 新功能
- ✅ 支持通配符文件匹配（*.log、**/*.log等）
- ✅ 支持目录批量处理
- ✅ 智能参数搜索（SQL语句中直接搜索）
- ✅ 自动导出JSON文件
- ✅ 增强预览功能（10条记录，包含SQL内容）
- ✅ 改进日志解析算法

### v1.0 基础功能
- ✅ 基本SQL日志解析
- ✅ 方法名和参数提取
- ✅ JSON/CSV导出
- ✅ 分析摘要统计

## 扩展功能

如果需要更多功能，可以考虑：

- 添加时间范围过滤
- 支持更多SQL参数格式
- 添加性能分析功能
- 支持实时日志监控
- 添加图形化界面
- 支持多种日志格式
- 添加SQL性能分析报告