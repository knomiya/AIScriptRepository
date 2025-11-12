"""
AI提供商测试工具
用于测试和管理不同的AI提供商
"""
import sys
from pathlib import Path

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from ai_analyzer import AIAnalyzer
import json

def test_all_providers():
    """测试所有AI提供商"""
    print("=== AI提供商测试 ===")
    
    analyzer = AIAnalyzer()
    
    # 获取可用提供商
    providers = analyzer.get_available_providers()
    print(f"\n发现 {len(providers)} 个提供商:")
    
    for provider in providers:
        status = "✓ 可用" if provider['is_available'] else "✗ 不可用"
        active = " (当前活动)" if provider['is_active'] else ""
        print(f"  - {provider['name']}: {status}{active}")
    
    # 测试当前提供商
    print(f"\n=== 测试当前提供商 ===")
    current_info = analyzer.get_current_provider_info()
    print(f"当前提供商: {current_info.get('name', 'Unknown')}")
    
    # 执行测试分析
    test_cases = [
        ("test_data.xlsx", "计算每列的平均值和总和"),
        ("report.docx", "调整文档格式，统一字体样式"),
        ("sales.xlsx", "筛选出销售额大于10000的记录并排序")
    ]
    
    for file_path, requirement in test_cases:
        print(f"\n测试需求: {requirement}")
        print(f"文件类型: {Path(file_path).suffix}")
        
        try:
            result = analyzer.analyze_requirement(
                requirement, 
                'excel' if file_path.endswith('.xlsx') else 'word',
                {"file_path": file_path, "test": True}
            )
            
            print(f"  ✓ 分析成功")
            print(f"  置信度: {result.get('confidence', 'N/A')}")
            print(f"  识别操作: {len(result.get('operations', []))}")
            
            operations = result.get('operations', [])
            for i, op in enumerate(operations[:2], 1):  # 只显示前2个操作
                print(f"    {i}. {op.get('action', 'N/A')}")
            
        except Exception as e:
            print(f"  ✗ 分析失败: {e}")

def test_provider_switching():
    """测试提供商切换功能"""
    print("\n=== 提供商切换测试 ===")
    
    analyzer = AIAnalyzer()
    
    # 获取所有提供商
    providers = analyzer.get_available_providers()
    available_providers = [p['name'] for p in providers if p['is_available']]
    
    print(f"可用提供商: {', '.join(available_providers)}")
    
    # 测试切换到每个可用提供商
    test_requirement = "统计数据的基本信息"
    
    for provider_name in available_providers:
        print(f"\n切换到提供商: {provider_name}")
        
        if analyzer.switch_provider(provider_name):
            try:
                result = analyzer.analyze_requirement(
                    test_requirement,
                    'excel',
                    {"test": True}
                )
                
                provider_info = result.get('provider', 'Unknown')
                confidence = result.get('confidence', 0)
                print(f"  ✓ 切换成功，提供商: {provider_info}, 置信度: {confidence}")
                
            except Exception as e:
                print(f"  ✗ 测试失败: {e}")
        else:
            print(f"  ✗ 切换失败")

def benchmark_providers():
    """性能基准测试"""
    print("\n=== 提供商性能测试 ===")
    
    analyzer = AIAnalyzer()
    
    # 测试用例
    test_cases = [
        ("简单需求", "计算平均值", "excel"),
        ("复杂需求", "筛选年龄大于30的员工，按薪资排序，计算各部门平均薪资", "excel"),
        ("Word需求", "调整文档格式，将标题设为黑体，正文设为宋体12号", "word")
    ]
    
    providers = analyzer.get_available_providers()
    available_providers = [p['name'] for p in providers if p['is_available']]
    
    results = {}
    
    for provider_name in available_providers:
        print(f"\n测试提供商: {provider_name}")
        results[provider_name] = {}
        
        if analyzer.switch_provider(provider_name):
            for case_name, requirement, file_type in test_cases:
                try:
                    import time
                    start_time = time.time()
                    
                    result = analyzer.analyze_requirement(
                        requirement,
                        file_type,
                        {"test": True}
                    )
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    results[provider_name][case_name] = {
                        "success": True,
                        "response_time": response_time,
                        "confidence": result.get('confidence', 0),
                        "operations_count": len(result.get('operations', []))
                    }
                    
                    print(f"  {case_name}: ✓ {response_time:.2f}s, 置信度: {result.get('confidence', 0)}")
                    
                except Exception as e:
                    results[provider_name][case_name] = {
                        "success": False,
                        "error": str(e)
                    }
                    print(f"  {case_name}: ✗ {e}")
    
    # 显示汇总结果
    print(f"\n=== 性能汇总 ===")
    for provider_name, provider_results in results.items():
        success_count = sum(1 for r in provider_results.values() if r.get('success', False))
        total_count = len(provider_results)
        avg_time = sum(r.get('response_time', 0) for r in provider_results.values() if r.get('success', False))
        avg_time = avg_time / max(success_count, 1)
        
        print(f"{provider_name}: {success_count}/{total_count} 成功, 平均响应时间: {avg_time:.2f}s")

def interactive_test():
    """交互式测试"""
    print("\n=== 交互式测试 ===")
    
    analyzer = AIAnalyzer()
    
    while True:
        print(f"\n当前提供商: {analyzer.get_current_provider_info().get('name', 'Unknown')}")
        print("选择操作:")
        print("1. 测试需求分析")
        print("2. 切换提供商")
        print("3. 查看提供商信息")
        print("4. 退出")
        
        choice = input("请选择 (1-4): ").strip()
        
        if choice == '1':
            requirement = input("请输入需求描述: ").strip()
            file_type = input("文件类型 (excel/word): ").strip().lower()
            
            if file_type not in ['excel', 'word']:
                print("无效的文件类型")
                continue
            
            try:
                result = analyzer.analyze_requirement(requirement, file_type, {"interactive": True})
                
                print(f"\n分析结果:")
                print(f"置信度: {result.get('confidence', 'N/A')}")
                print(f"提供商: {result.get('provider', 'N/A')}")
                
                operations = result.get('operations', [])
                print(f"识别操作 ({len(operations)}):")
                for i, op in enumerate(operations, 1):
                    print(f"  {i}. {op.get('action', 'N/A')}: {op.get('description', 'N/A')}")
                
                suggestions = result.get('suggestions', [])
                if suggestions:
                    print(f"建议:")
                    for suggestion in suggestions:
                        print(f"  • {suggestion}")
                
            except Exception as e:
                print(f"分析失败: {e}")
        
        elif choice == '2':
            providers = analyzer.get_available_providers()
            available_providers = [p['name'] for p in providers if p['is_available']]
            
            print("可用提供商:")
            for i, name in enumerate(available_providers, 1):
                print(f"  {i}. {name}")
            
            try:
                idx = int(input("选择提供商编号: ")) - 1
                if 0 <= idx < len(available_providers):
                    provider_name = available_providers[idx]
                    if analyzer.switch_provider(provider_name):
                        print(f"已切换到: {provider_name}")
                    else:
                        print("切换失败")
                else:
                    print("无效的编号")
            except ValueError:
                print("请输入有效的数字")
        
        elif choice == '3':
            providers = analyzer.get_available_providers()
            print("\n提供商信息:")
            for provider in providers:
                status = "可用" if provider['is_available'] else "不可用"
                active = " (当前)" if provider['is_active'] else ""
                print(f"  {provider['name']}: {status}{active}")
        
        elif choice == '4':
            break
        
        else:
            print("无效的选择")

def main():
    """主函数"""
    print("DocumentHandler AI提供商测试工具")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            test_all_providers()
        elif command == 'switch':
            test_provider_switching()
        elif command == 'benchmark':
            benchmark_providers()
        elif command == 'interactive':
            interactive_test()
        else:
            print(f"未知命令: {command}")
            print("可用命令: test, switch, benchmark, interactive")
    else:
        # 默认运行所有测试
        test_all_providers()
        test_provider_switching()
        
        # 询问是否运行性能测试
        if input("\n是否运行性能测试? (y/n): ").lower().startswith('y'):
            benchmark_providers()

if __name__ == "__main__":
    main()