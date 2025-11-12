# DocumentHandler - 智能文档处理工具

一个基于AI的文档处理工具，支持Excel和Word文档的智能分析和处理。

## 功能特性

- 🤖 **AI需求理解**: 自然语言描述处理需求，AI自动分析并生成处理方案
- 📊 **Excel处理**: 支持数据统计、筛选、排序、分析等操作
- 📝 **Word处理**: 支持格式调整、内容替换、结构分析等操作
- 🔧 **灵活扩展**: 模块化设计，易于添加新的处理功能
- 💡 **智能建议**: 提供处理建议和优化方案

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 命令行使用

```bash
# Excel文档处理
python document_handler.py data.xlsx "统计每列的平均值和总和"

# Word文档处理
python document_handler.py report.docx "调整文档格式，统一字体样式"
```

### 2. 代码调用

```python
from document_handler import DocumentHandler

# 创建处理器实例
handler = DocumentHandler()

# 处理文档
result = handler.process_document(
    file_path="your_document.xlsx",
    user_requirement="你的处理需求描述"
)

# 查看结果
if result.get("success"):
    print("处理成功!")
    print(result["ai_analysis"])
    print(result["processing_result"])
else:
    print(f"处理失败: {result.get('error')}")
```

## 支持的文件格式

- **Excel**: `.xlsx`, `.xls`
- **Word**: `.docx`, `.doc`

## 支持的操作类型

### Excel操作
- **数据统计**: 计算平均值、总和、最大值、最小值等
- **数据筛选**: 根据条件筛选数据
- **数据排序**: 按指定列排序
- **数据分析**: 分析数据结构、缺失值、数据类型等

### Word操作
- **格式调整**: 统一字体、段落样式、对齐方式等
- **内容替换**: 批量替换文本内容
- **结构分析**: 分析文档结构、统计字数、段落数等
- **样式优化**: 优化文档样式和排版

## 配置AI功能

DocumentHandler支持多种AI提供商，你可以根据需要选择和配置：

### 支持的AI提供商

#### 国产AI服务商（推荐）
1. **DeepSeek** - 成本友好，中文理解优秀
2. **Kimi (月之暗面)** - 长文本处理能力强
3. **智谱AI (GLM)** - 逻辑推理能力突出
4. **豆包 (字节跳动)** - 多模态支持，企业级服务

#### 国外AI服务商
5. **OpenAI GPT** - 综合能力强
6. **Claude (Anthropic)** - 文档理解能力优秀

#### 其他选项
7. **本地AI模型** - 通过Ollama等本地部署
8. **规则引擎** - 无需API的备用方案

### 配置方法

#### 方法1: 交互式配置向导（推荐新手）
```bash
# 运行配置向导，按提示选择提供商
python config_manager.py interactive

# 或者直接运行
python config_manager.py
```

#### 方法2: 快速配置（推荐）
```bash
# 创建只使用DeepSeek和Kimi的配置
python config_manager.py create deepseek,kimi

# 创建使用多个提供商的配置
python config_manager.py create deepseek,kimi,zhipu,rule_based my_config.json

# 验证配置文件
python config_manager.py validate ai_config.json

# 测试配置
python config_manager.py test ai_config.json
```

#### 方法3: 高级JSON配置（推荐高级用户）
复制 `ai_config_advanced.json` 为 `ai_config.json` 并修改：
```json
{
  "provider_strategy": {
    "mode": "priority_with_fallback",
    "enabled_providers": ["deepseek", "kimi", "rule_based"],
    "primary_provider": "deepseek",
    "fallback_chain": ["kimi", "rule_based"],
    "retry_on_failure": true,
    "max_retries": 2
  },
  "providers": {
    "deepseek": {
      "enabled": true,
      "api_key": "your_deepseek_api_key_here",
      "model": "deepseek-chat",
      "priority": 1
    },
    "kimi": {
      "enabled": true,
      "api_key": "your_kimi_api_key_here", 
      "model": "moonshot-v1-8k",
      "priority": 2
    }
  },
  "scenarios": {
    "excel_processing": {
      "preferred_providers": ["deepseek", "kimi"],
      "special_config": {
        "temperature": 0.2
      }
    }
  }
}
```

#### 方法4: 环境变量配置（简单场景）
创建 `.env` 文件：
```bash
# 国产AI配置（推荐）
DEEPSEEK_API_KEY=your_deepseek_api_key_here
KIMI_API_KEY=your_kimi_api_key_here
ZHIPU_API_KEY=your_zhipu_api_key_here

# 国外AI配置（可选）
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
```

#### 方法5: 传统JSON配置
复制 `ai_config.json.example` 为 `ai_config.json` 并修改配置：
```json
{
  "providers": {
    "deepseek": {
      "api_key": "your_deepseek_key_here",
      "model": "deepseek-chat"
    },
    "kimi": {
      "api_key": "your_kimi_key_here",
      "model": "moonshot-v1-8k"
    },
    "zhipu": {
      "api_key": "your_zhipu_key_here",
      "model": "glm-4"
    }
  },
  "priority": ["deepseek", "kimi", "zhipu", "doubao", "rule_based"]
}
```

### 安装AI提供商依赖

```bash
# 安装基础依赖（支持所有国产AI）
pip install requests PyJWT

# 可选：安装国外AI提供商支持
pip install openai          # 仅OpenAI
pip install anthropic       # 仅Claude
```

### 获取API密钥

#### 国产AI服务商
- **DeepSeek**: [https://platform.deepseek.com/](https://platform.deepseek.com/)
- **Kimi**: [https://platform.moonshot.cn/](https://platform.moonshot.cn/)
- **智谱AI**: [https://open.bigmodel.cn/](https://open.bigmodel.cn/)
- **豆包**: [https://console.volcengine.com/ark](https://console.volcengine.com/ark)

#### 国外AI服务商
- **OpenAI**: [https://platform.openai.com/](https://platform.openai.com/)
- **Claude**: [https://console.anthropic.com/](https://console.anthropic.com/)

### 本地AI设置

使用Ollama运行本地模型：
```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull llama2
ollama pull codellama

# 启动服务 (默认端口11434)
ollama serve
```

## 使用示例

### Excel处理示例

```python
# 数据统计
handler.process_document("sales.xlsx", "计算每个月的销售总额和平均值")

# 数据筛选
handler.process_document("employees.xlsx", "筛选出年龄大于30岁的员工")

# 数据排序
handler.process_document("scores.xlsx", "按成绩从高到低排序")
```

### Word处理示例

```python
# 格式调整
handler.process_document("report.docx", "将所有标题设置为黑体，正文设置为宋体12号")

# 内容替换
handler.process_document("contract.docx", "将所有的'甲方'替换为'ABC公司'")

# 文档分析
handler.process_document("manual.docx", "分析文档结构并统计字数")
```

### AI提供商管理

```python
from ai_analyzer import AIAnalyzer

# 创建分析器（使用配置文件）
analyzer = AIAnalyzer("ai_config.json")

# 查看配置摘要
config_summary = analyzer.get_config_summary()
print(f"主要提供商: {config_summary['strategy']['primary_provider']}")
print(f"启用的提供商: {config_summary['strategy']['enabled_providers']}")

# 查看提供商健康状态
health = analyzer.get_provider_health()
for name, status in health.items():
    print(f"{name}: {status['status']}")

# 设置处理场景
analyzer.set_scenario('excel_processing')  # Excel处理场景
analyzer.set_scenario('word_processing')   # Word处理场景
analyzer.set_scenario('complex_analysis')  # 复杂分析场景

# 动态启用/禁用提供商
analyzer.enable_provider('kimi')    # 启用Kimi
analyzer.disable_provider('zhipu')  # 禁用智谱AI

# 重新加载配置
analyzer.reload_config("new_config.json")

# 测试所有提供商
test_results = analyzer.test_providers()
```

### 智能配置特性

#### 1. 场景感知处理
系统会根据不同场景自动选择最适合的提供商：
- **Excel处理**: 优先使用数据分析能力强的提供商
- **Word处理**: 优先使用文本理解能力强的提供商  
- **复杂分析**: 使用推理能力最强的提供商

#### 2. 智能故障转移
- **主提供商失败**: 自动切换到备用提供商
- **多重备用**: 支持配置多个备用提供商
- **最终保障**: 规则引擎作为最终备用方案

#### 3. 灵活的配置策略
```json
{
  "provider_strategy": {
    "mode": "priority_with_fallback",
    "enabled_providers": ["A", "B"],
    "primary_provider": "A",
    "fallback_chain": ["B", "rule_based"],
    "retry_on_failure": true,
    "max_retries": 2
  }
}
```

这样配置后：
- 🎯 **优先使用A**: 所有请求首先尝试提供商A
- 🔄 **A失败时使用B**: 如果A返回错误，自动切换到B
- 🛡 **最终使用规则引擎**: 如果B也失败，使用规则引擎保底

### 命令行AI测试

```bash
# 测试所有提供商
python provider_test.py test

# 测试提供商切换
python provider_test.py switch

# 性能基准测试
python provider_test.py benchmark

# 交互式测试
python provider_test.py interactive
```

## AI提供商对比

| 提供商 | 优势 | 适用场景 | 成本 | 中文支持 |
|--------|------|----------|------|----------|
| **DeepSeek** | 成本友好，响应快速 | 日常文档处理 | 极低 | ⭐⭐⭐⭐⭐ |
| **Kimi** | 长文本处理，上下文理解强 | 大型文档分析 | 低 | ⭐⭐⭐⭐⭐ |
| **智谱AI** | 逻辑推理，多轮对话 | 复杂需求分析 | 低 | ⭐⭐⭐⭐⭐ |
| **豆包** | 多模态，企业级服务 | 企业文档处理 | 中 | ⭐⭐⭐⭐⭐ |
| **OpenAI GPT** | 综合能力强，生态完善 | 国际化需求 | 高 | ⭐⭐⭐ |
| **Claude** | 安全性高，文档理解好 | 敏感文档处理 | 高 | ⭐⭐⭐ |
| **本地AI** | 数据隐私，无网络依赖 | 离线环境 | 硬件成本 | ⭐⭐⭐ |
| **规则引擎** | 快速响应，无依赖 | 简单需求，备用 | 免费 | ⭐⭐⭐⭐ |

## 项目结构

```
DocumentHandler/
├── document_handler.py           # 主处理器
├── ai_analyzer.py               # AI需求分析器
├── processors/                  # 文档处理器模块
│   ├── __init__.py
│   ├── excel_processor.py       # Excel处理器
│   └── word_processor.py        # Word处理器
├── ai_providers/                # AI提供商模块
│   ├── __init__.py
│   ├── base_provider.py         # 提供商基类
│   ├── openai_provider.py       # OpenAI提供商
│   ├── claude_provider.py       # Claude提供商
│   ├── local_provider.py        # 本地AI提供商
│   ├── rule_based_provider.py   # 规则引擎提供商
│   └── provider_manager.py      # 提供商管理器
├── rule_engine/                 # 可配置规则引擎
│   ├── __init__.py
│   ├── configurable_rule_engine.py  # 规则引擎核心
│   └── rule_config.json        # 规则配置文件
├── examples/                    # 示例管理模块
│   ├── __init__.py
│   ├── example_manager.py       # 示例管理器
│   └── prompt_examples.json     # 提示示例数据
├── provider_test.py             # AI提供商测试工具
├── rule_engine_test.py          # 规则引擎测试工具
├── example_test.py              # 示例管理测试工具
├── example_usage.py             # 使用示例
├── ai_config.json.example       # AI配置示例
├── requirements.txt             # 依赖包列表
└── README.md                   # 说明文档
```

## 扩展开发

### 添加新的处理器

1. 在 `processors/` 目录下创建新的处理器文件
2. 继承基础处理器接口
3. 实现必要的方法：`get_file_info()`, `execute_operations()`
4. 在主处理器中注册新的文件类型

### 添加新的操作类型

1. 在对应的处理器中添加新的操作方法
2. 在AI分析器中添加对应的识别规则
3. 更新操作类型文档

## 注意事项

- 确保有足够的磁盘空间处理大文件
- 处理敏感文档时注意数据安全
- 建议在处理前备份原始文件
- 大型文档可能需要较长处理时间

## 故障排除

### 常见问题

1. **文件无法打开**: 检查文件路径和权限
2. **依赖包缺失**: 运行 `pip install -r requirements.txt`
3. **AI分析失败**: 检查网络连接和API密钥配置
4. **内存不足**: 处理大文件时可能需要更多内存

### 获取帮助

如果遇到问题，请检查：
1. 文件格式是否支持
2. 依赖包是否正确安装
3. 需求描述是否清晰明确
4. 系统资源是否充足

## 更新日志

- v1.0.0: 初始版本，支持基础Excel和Word处理功能
- 支持AI需求分析和自动处理方案生成
## AI提供
商对比

| 提供商 | 优势 | 适用场景 | 成本 |
|--------|------|----------|------|
| **OpenAI GPT** | 理解能力强，响应准确 | 复杂需求分析 | 按使用付费 |
| **Claude** | 文档处理专长，安全性高 | 敏感文档处理 | 按使用付费 |
| **本地AI** | 数据隐私，无网络依赖 | 离线环境，隐私要求高 | 硬件成本 |
| **规则引擎** | 快速响应，无依赖 | 简单需求，备用方案 | 免费 |

## 高级功能

### 可配置规则引擎

系统包含一个强大的可配置规则引擎，支持通过JSON配置文件自定义规则：

```bash
# 测试规则引擎
python rule_engine_test.py basic

# 交互式规则测试
python rule_engine_test.py interactive

# 规则性能测试
python rule_engine_test.py benchmark
```

#### 自定义规则配置

编辑 `rule_engine/rule_config.json` 来添加或修改规则：

```json
{
  "excel_rules": {
    "custom_operation": {
      "keywords": ["自定义", "特殊处理"],
      "patterns": ["自定义.*处理"],
      "confidence_boost": 0.2,
      "parameters": {
        "custom_param": ["参数1", "参数2"]
      }
    }
  }
}
```

### AI提示示例管理

系统使用示例管理器为AI提供商提供高质量的提示示例：

```bash
# 测试示例管理器
python example_test.py load

# 交互式示例管理
python example_test.py interactive
```

#### 添加自定义示例

编辑 `examples/prompt_examples.json` 或通过代码添加：

```python
from examples.example_manager import ExampleManager

manager = ExampleManager()
manager.add_example(
    "excel",
    "计算ROI指标",
    {
        "operations": [{"type": "calculate", "action": "ROI计算"}],
        "confidence": 0.9
    }
)
```

### 自定义AI提供商

你可以添加自己的AI提供商：

```python
from ai_providers.base_provider import BaseAIProvider

class CustomAIProvider(BaseAIProvider):
    def _check_availability(self):
        # 检查你的AI服务是否可用
        return True
    
    def analyze_requirement(self, user_input, file_type, file_info):
        # 实现你的AI分析逻辑
        return {
            "user_requirement": user_input,
            "operations": [...],
            "confidence": 0.8
        }

# 添加到系统
analyzer = AIAnalyzer()
analyzer.add_custom_provider('my_ai', CustomAIProvider({}))
```

### 智能提供商选择

系统会根据以下策略自动选择最佳提供商：

1. **优先级顺序**: 按配置的priority顺序尝试
2. **可用性检查**: 自动跳过不可用的提供商  
3. **故障转移**: 主提供商失败时自动切换到备用
4. **性能监控**: 记录各提供商的响应时间和成功率

### 批量处理

```python
# 批量处理多个文档
documents = [
    ("file1.xlsx", "统计销售数据"),
    ("file2.docx", "调整格式"),
    ("file3.xlsx", "数据筛选")
]

for file_path, requirement in documents:
    result = handler.process_document(file_path, requirement)
    print(f"{file_path}: {'成功' if result.get('success') else '失败'}")
```

## 性能优化建议

1. **选择合适的提供商**：
   - 简单需求使用规则引擎
   - 复杂需求使用GPT/Claude
   - 隐私敏感使用本地AI

2. **配置优化**：
   - 设置合理的timeout值
   - 调整temperature参数控制创造性
   - 限制max_tokens避免过长响应

3. **缓存策略**：
   - 相似需求可以复用分析结果
   - 定期清理缓存避免内存占用

## 故障排除

### 常见问题

**Q: AI提供商连接失败**
A: 检查网络连接、API密钥配置和服务状态

**Q: 分析结果不准确**  
A: 尝试更具体的需求描述或切换到其他提供商

**Q: 本地AI响应慢**
A: 检查硬件配置，考虑使用更小的模型

**Q: 规则引擎识别不准确**
A: 使用更明确的关键词或配置AI提供商

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 测试特定提供商
analyzer = AIAnalyzer()
result = analyzer.test_providers()
print(json.dumps(result, indent=2, ensure_ascii=False))
```

## 测试工具

系统提供了完整的测试工具集：

### 配置管理工具
```bash
# 交互式配置向导
python config_manager.py interactive

# 快速创建配置
python config_manager.py create deepseek,kimi

# 验证配置文件
python config_manager.py validate ai_config.json

# 测试配置
python config_manager.py test ai_config.json
```

### AI提供商测试
```bash
python provider_test.py test        # 测试所有提供商
python provider_test.py benchmark   # 性能基准测试
python provider_test.py interactive # 交互式测试
```

### 规则引擎测试
```bash
python rule_engine_test.py basic      # 基础功能测试
python rule_engine_test.py debug      # 调试模式
python rule_engine_test.py custom     # 自定义规则测试
```

### 示例管理测试
```bash
python example_test.py load       # 示例加载测试
python example_test.py similar    # 相似示例查找测试
python example_test.py prompt     # 提示生成测试
```

## 更新日志

- **v2.2.0**: 
  - 🎯 **智能配置管理**: 新增配置向导和验证工具
  - 🔄 **场景感知处理**: 根据处理场景自动选择最佳提供商
  - 🛡 **智能故障转移**: 多重备用机制，确保服务可用性
  - 🇨🇳 **国产AI优先**: 优先支持DeepSeek、Kimi、智谱AI、豆包等
  - ⚙️ **灵活配置策略**: 支持"配置A优先，A失败用B"的策略
  - 📊 **健康状态监控**: 实时监控提供商可用性
- **v2.1.0**: 
  - 新增可配置规则引擎
  - 添加AI提示示例管理系统
  - 完善测试工具集
  - 支持自定义规则和示例
- **v2.0.0**: 
  - 新增多AI提供商支持
  - 添加Claude和本地AI支持
  - 智能提供商选择和故障转移
  - 性能监控和基准测试工具
- **v1.0.0**: 初始版本，支持基础Excel和Word处理功能