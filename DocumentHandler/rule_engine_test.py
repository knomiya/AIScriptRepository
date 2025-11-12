"""
规则引擎测试工具
用于测试和调试可配置规则引擎
"""
import sys
from pathlib import Path
import json

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from rule_engine.configurable_rule_engine import ConfigurableRuleEngine
from ai_providers.rule_based_provider import RuleBasedProvider

def test_rule_engine():
    """测试规则引擎基本功能"""
    print("=== 规则引擎基本功能测试 ===")
    
    engine = ConfigurableRuleEngine()
    
    # 显示规则引擎信息
    info = engine.get_rule_info()
    print(f"规则引擎信息:")
    print(f"  Excel规则数量: {info['excel_rules_count']}")
    print(f"  Word规则数量: {info['word_rules_count']}")
    print(f"  支持的Excel操作: {', '.join(info['supported_operations']['excel'])}")
    print(f"  支持的Word操作: {', '.join(info['supported_operations']['word'])}")
    
    # 测试用例
    test_cases = [
        # Excel测试
        ("计算销售数据的平均值和总和", "excel"),
        ("筛选出年龄大于30岁的员工", "excel"),
        ("按销售额从高到低排序", "excel"),
        ("生成销售额柱状图", "excel"),
        
        # Word测试
        ("调整文档格式，统一字体样式", "word"),
        ("将所有甲方替换为ABC公司", "word"),
        ("分析文档结构并生成目录", "word"),
        ("检查文档中的语法错误", "word"),
        
        # 复杂测试
        ("分析销售数据，计算平均值，筛选前10名，生成图表", "excel"),
        ("调整文档格式，替换公司名称，检查错误", "word")
    ]
    
    print(f"\n=== 测试用例分析 ===")
    for i, (user_input, file_type) in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {user_input}")
        print(f"文件类型: {file_type}")
        
        result = engine.analyze_requirement(user_input, file_type)
        
        print(f"  置信度: {result['confidence']:.2f}")
        print(f"  识别操作数: {len(result['operations'])}")
        
        for j, op in enumerate(result['operations'], 1):
            print(f"    {j}. {op['action']} (置信度: {op.get('confidence', 'N/A'):.2f})")
            if op.get('matched_keywords'):
                print(f"       匹配关键词: {', '.join(op['matched_keywords'])}")

def test_rule_provider():
    """测试规则提供商"""
    print(f"\n=== 规则提供商测试 ===")
    
    provider = RuleBasedProvider()
    
    test_cases = [
        ("计算每列的平均值", "excel", {"test": True}),
        ("调整标题格式", "word", {"test": True})
    ]
    
    for user_input, file_type, file_info in test_cases:
        print(f"\n测试: {user_input}")
        
        result = provider.analyze_requirement(user_input, file_type, file_info)
        
        print(f"  提供商: {result.get('provider')}")
        print(f"  模型: {result.get('model')}")
        print(f"  置信度: {result.get('confidence', 0):.2f}")
        print(f"  操作数量: {len(result.get('operations', []))}")
        
        for op in result.get('operations', []):
            print(f"    - {op.get('action')}: {op.get('description')}")
        
        suggestions = result.get('suggestions', [])
        if suggestions:
            print(f"  建议:")
            for suggestion in suggestions[:2]:  # 只显示前2个建议
                print(f"    • {suggestion}")

def test_rule_debugging():
    """测试规则调试功能"""
    print(f"\n=== 规则调试测试 ===")
    
    engine = ConfigurableRuleEngine()
    
    test_input = "计算销售数据的平均值和总和"
    file_type = "excel"
    
    print(f"调试输入: {test_input}")
    print(f"文件类型: {file_type}")
    
    debug_result = engine.test_rule(test_input, file_type)
    
    print(f"\n调试结果:")
    print(f"  分析结果: {debug_result['analysis_result']}")
    
    print(f"\n规则详情:")
    for rule_name, rule_detail in debug_result['rule_details'].items():
        print(f"  {rule_name}:")
        print(f"    匹配: {'是' if rule_detail['matched'] else '否'}")
        print(f"    置信度: {rule_detail['confidence']:.2f}")
        if rule_detail['matched_keywords']:
            print(f"    匹配关键词: {', '.join(rule_detail['matched_keywords'])}")
        if rule_detail['matched_patterns']:
            print(f"    匹配模式: {', '.join(rule_detail['matched_patterns'])}")

def test_custom_rules():
    """测试自定义规则"""
    print(f"\n=== 自定义规则测试 ===")
    
    engine = ConfigurableRuleEngine()
    
    # 添加自定义规则
    custom_rule = {
        "keywords": ["导出", "保存", "输出"],
        "patterns": ["导出.*文件", "保存.*"],
        "confidence_boost": 0.2,
        "parameters": {
            "export_formats": {
                "pdf": ["pdf", "PDF"],
                "csv": ["csv", "CSV"],
                "txt": ["txt", "文本"]
            }
        }
    }
    
    engine.add_custom_rule("excel", "export", custom_rule)
    
    # 测试自定义规则
    test_input = "将处理后的数据导出为CSV文件"
    result = engine.analyze_requirement(test_input, "excel")
    
    print(f"测试自定义规则: {test_input}")
    print(f"识别操作: {[op['action'] for op in result['operations']]}")
    
    # 查找导出操作
    export_ops = [op for op in result['operations'] if op['type'] == 'export']
    if export_ops:
        print(f"导出操作参数: {export_ops[0].get('parameters', {})}")

def interactive_rule_test():
    """交互式规则测试"""
    print(f"\n=== 交互式规则测试 ===")
    
    engine = ConfigurableRuleEngine()
    provider = RuleBasedProvider()
    
    while True:
        print(f"\n选择测试模式:")
        print("1. 测试规则引擎")
        print("2. 测试规则提供商")
        print("3. 规则调试模式")
        print("4. 查看规则信息")
        print("5. 退出")
        
        choice = input("请选择 (1-5): ").strip()
        
        if choice == '1':
            user_input = input("请输入需求描述: ").strip()
            file_type = input("文件类型 (excel/word): ").strip().lower()
            
            if file_type in ['excel', 'word']:
                result = engine.analyze_requirement(user_input, file_type)
                print(f"\n分析结果:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print("无效的文件类型")
        
        elif choice == '2':
            user_input = input("请输入需求描述: ").strip()
            file_type = input("文件类型 (excel/word): ").strip().lower()
            
            if file_type in ['excel', 'word']:
                result = provider.analyze_requirement(user_input, file_type, {"interactive": True})
                print(f"\n提供商分析结果:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print("无效的文件类型")
        
        elif choice == '3':
            user_input = input("请输入需求描述: ").strip()
            file_type = input("文件类型 (excel/word): ").strip().lower()
            
            if file_type in ['excel', 'word']:
                debug_result = engine.test_rule(user_input, file_type)
                print(f"\n调试结果:")
                print(json.dumps(debug_result, indent=2, ensure_ascii=False))
            else:
                print("无效的文件类型")
        
        elif choice == '4':
            info = engine.get_rule_info()
            print(f"\n规则引擎信息:")
            print(json.dumps(info, indent=2, ensure_ascii=False))
        
        elif choice == '5':
            break
        
        else:
            print("无效的选择")

def benchmark_rule_engine():
    """规则引擎性能基准测试"""
    print(f"\n=== 规则引擎性能测试 ===")
    
    import time
    
    engine = ConfigurableRuleEngine()
    
    # 准备测试数据
    test_data = [
        ("计算平均值", "excel"),
        ("筛选数据", "excel"),
        ("排序", "excel"),
        ("调整格式", "word"),
        ("替换内容", "word"),
        ("分析结构", "word")
    ] * 100  # 重复100次
    
    print(f"测试数据量: {len(test_data)} 个请求")
    
    start_time = time.time()
    
    for user_input, file_type in test_data:
        engine.analyze_requirement(user_input, file_type)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"总耗时: {total_time:.2f} 秒")
    print(f"平均每个请求: {(total_time / len(test_data)) * 1000:.2f} 毫秒")
    print(f"每秒处理请求数: {len(test_data) / total_time:.2f}")

def main():
    """主函数"""
    print("DocumentHandler 规则引擎测试工具")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'basic':
            test_rule_engine()
        elif command == 'provider':
            test_rule_provider()
        elif command == 'debug':
            test_rule_debugging()
        elif command == 'custom':
            test_custom_rules()
        elif command == 'interactive':
            interactive_rule_test()
        elif command == 'benchmark':
            benchmark_rule_engine()
        else:
            print(f"未知命令: {command}")
            print("可用命令: basic, provider, debug, custom, interactive, benchmark")
    else:
        # 默认运行基础测试
        test_rule_engine()
        test_rule_provider()
        test_rule_debugging()
        
        # 询问是否运行交互式测试
        if input("\n是否运行交互式测试? (y/n): ").lower().startswith('y'):
            interactive_rule_test()

if __name__ == "__main__":
    main()