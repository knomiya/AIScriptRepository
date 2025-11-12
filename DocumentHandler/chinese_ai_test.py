"""
国产AI提供商专项测试工具
专门测试DeepSeek、Kimi、智谱AI、豆包等国产AI服务商
"""
import sys
from pathlib import Path
import json
import time

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from ai_analyzer import AIAnalyzer

def test_chinese_providers():
    """测试所有国产AI提供商"""
    print("=== 国产AI提供商测试 ===")
    
    analyzer = AIAnalyzer()
    
    # 国产AI提供商列表
    chinese_providers = ['deepseek', 'kimi', 'zhipu', 'doubao']
    
    # 获取可用的国产提供商
    all_providers = analyzer.get_available_providers()
    available_chinese = [p for p in all_providers if p['name'] in chinese_providers and p['is_available']]
    
    print(f"发现 {len(available_chinese)} 个可用的国产AI提供商:")
    for provider in available_chinese:
        features = provider.get('features', [])
        print(f"  ✓ {provider['name']}: {', '.join(features)}")
    
    if not available_chinese:
        print("❌ 没有可用的国产AI提供商")
        print("请检查API密钥配置:")
        print("  - DEEPSEEK_API_KEY")
        print("  - KIMI_API_KEY") 
        print("  - ZHIPU_API_KEY")
        print("  - DOUBAO_API_KEY")
        return
    
    # 中文测试用例
    chinese_test_cases = [
        ("计算销售数据的平均值和总和", "excel", "基础数据统计"),
        ("筛选出年龄大于30岁且薪资超过8000的员工", "excel", "复杂条件筛选"),
        ("按销售额从高到低排序，并生成前10名的柱状图", "excel", "排序和可视化"),
        ("将文档中所有的'甲方'替换为'北京科技有限公司'", "word", "中文内容替换"),
        ("调整文档格式：标题用黑体二号，正文用宋体小四", "word", "中文格式要求"),
        ("分析合同文档结构，生成目录，检查是否有错别字", "word", "综合文档处理")
    ]
    
    print(f"\n=== 中文理解能力测试 ===")
    
    results = {}
    
    for provider in available_chinese:
        provider_name = provider['name']
        print(f"\n测试提供商: {provider_name}")
        
        # 切换到当前提供商
        if not analyzer.switch_provider(provider_name):
            print(f"  ❌ 切换到 {provider_name} 失败")
            continue
        
        provider_results = []
        
        for user_input, file_type, test_desc in chinese_test_cases:
            print(f"  测试: {test_desc}")
            
            try:
                start_time = time.time()
                
                result = analyzer.analyze_requirement(
                    user_input,
                    file_type,
                    {"test_case": test_desc}
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # 评估结果质量
                operations = result.get('operations', [])
                confidence = result.get('confidence', 0)
                
                quality_score = 0
                if operations:
                    quality_score += 0.4  # 有操作识别
                if confidence > 0.7:
                    quality_score += 0.3  # 高置信度
                if len(operations) > 1 and "复杂" in test_desc:
                    quality_score += 0.2  # 复杂需求识别多操作
                if any('中文' in op.get('description', '') for op in operations):
                    quality_score += 0.1  # 中文处理
                
                provider_results.append({
                    "test_desc": test_desc,
                    "success": True,
                    "response_time": response_time,
                    "confidence": confidence,
                    "operations_count": len(operations),
                    "quality_score": quality_score
                })
                
                print(f"    ✓ 响应时间: {response_time:.2f}s, 置信度: {confidence:.2f}, 操作数: {len(operations)}")
                
            except Exception as e:
                provider_results.append({
                    "test_desc": test_desc,
                    "success": False,
                    "error": str(e)
                })
                print(f"    ❌ 失败: {e}")
        
        results[provider_name] = provider_results
    
    # 生成测试报告
    print(f"\n=== 测试报告 ===")
    
    for provider_name, provider_results in results.items():
        success_count = sum(1 for r in provider_results if r.get('success', False))
        total_count = len(provider_results)
        
        if success_count > 0:
            avg_time = sum(r.get('response_time', 0) for r in provider_results if r.get('success', False)) / success_count
            avg_confidence = sum(r.get('confidence', 0) for r in provider_results if r.get('success', False)) / success_count
            avg_quality = sum(r.get('quality_score', 0) for r in provider_results if r.get('success', False)) / success_count
            
            print(f"\n{provider_name}:")
            print(f"  成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
            print(f"  平均响应时间: {avg_time:.2f}秒")
            print(f"  平均置信度: {avg_confidence:.2f}")
            print(f"  平均质量分: {avg_quality:.2f}")
        else:
            print(f"\n{provider_name}: 全部测试失败")

def test_chinese_specific_features():
    """测试中文特有功能"""
    print(f"\n=== 中文特有功能测试 ===")
    
    analyzer = AIAnalyzer()
    
    # 中文特色测试用例
    chinese_features = [
        ("统计各省市的GDP数据，按从高到低排序", "excel", "中文地名处理"),
        ("计算春节、清明、端午、中秋、国庆假期的销售额", "excel", "中文节日识别"),
        ("将合同中的'人民币'统一替换为'RMB'", "word", "中文货币单位"),
        ("检查文档中是否有繁体字，如有请转换为简体字", "word", "繁简转换"),
        ("按照国标GB/T 7714格式调整参考文献", "word", "中文标准格式"),
        ("统计文档中成语、俗语的使用情况", "word", "中文语言特色")
    ]
    
    # 尝试使用最佳的国产AI提供商
    chinese_providers = ['deepseek', 'kimi', 'zhipu', 'doubao']
    
    selected_provider = None
    for provider_name in chinese_providers:
        if analyzer.switch_provider(provider_name):
            selected_provider = provider_name
            break
    
    if not selected_provider:
        print("❌ 没有可用的国产AI提供商进行中文特色测试")
        return
    
    print(f"使用提供商: {selected_provider}")
    
    for user_input, file_type, feature_desc in chinese_features:
        print(f"\n测试功能: {feature_desc}")
        print(f"需求: {user_input}")
        
        try:
            result = analyzer.analyze_requirement(user_input, file_type, {"feature_test": True})
            
            operations = result.get('operations', [])
            confidence = result.get('confidence', 0)
            
            print(f"  置信度: {confidence:.2f}")
            print(f"  识别操作:")
            for i, op in enumerate(operations, 1):
                print(f"    {i}. {op.get('action', 'N/A')}: {op.get('description', 'N/A')}")
            
            # 检查是否有中文相关的参数
            has_chinese_params = False
            for op in operations:
                params = op.get('parameters', {})
                if any('中文' in str(v) or '中国' in str(v) for v in params.values()):
                    has_chinese_params = True
                    break
            
            if has_chinese_params:
                print(f"  ✓ 检测到中文相关参数处理")
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")

def compare_chinese_vs_foreign():
    """对比国产AI与国外AI的中文处理能力"""
    print(f"\n=== 中外AI中文处理对比 ===")
    
    analyzer = AIAnalyzer()
    
    # 对比测试用例（偏向中文语境）
    comparison_cases = [
        "计算各部门的绩效考核平均分，筛选出优秀员工名单",
        "将报告中的'贵公司'统一替换为'华为技术有限公司'",
        "按照公文格式要求调整通知文档的标题和落款"
    ]
    
    # 测试提供商分组
    chinese_providers = ['deepseek', 'kimi', 'zhipu', 'doubao']
    foreign_providers = ['openai', 'claude']
    
    all_providers = analyzer.get_available_providers()
    available_chinese = [p['name'] for p in all_providers if p['name'] in chinese_providers and p['is_available']]
    available_foreign = [p['name'] for p in all_providers if p['name'] in foreign_providers and p['is_available']]
    
    print(f"国产AI: {', '.join(available_chinese) if available_chinese else '无'}")
    print(f"国外AI: {', '.join(available_foreign) if available_foreign else '无'}")
    
    if not available_chinese and not available_foreign:
        print("❌ 没有可用的AI提供商进行对比测试")
        return
    
    comparison_results = {}
    
    # 测试国产AI
    if available_chinese:
        print(f"\n测试国产AI (使用 {available_chinese[0]}):")
        analyzer.switch_provider(available_chinese[0])
        
        chinese_scores = []
        for case in comparison_cases:
            try:
                result = analyzer.analyze_requirement(case, "excel", {"comparison_test": True})
                confidence = result.get('confidence', 0)
                operations_count = len(result.get('operations', []))
                
                # 简单评分：置信度 + 操作识别数量
                score = confidence + (operations_count * 0.1)
                chinese_scores.append(score)
                
                print(f"  '{case[:20]}...': 置信度 {confidence:.2f}, 操作数 {operations_count}")
                
            except Exception as e:
                chinese_scores.append(0)
                print(f"  '{case[:20]}...': 失败 - {e}")
        
        comparison_results['chinese'] = sum(chinese_scores) / len(chinese_scores) if chinese_scores else 0
    
    # 测试国外AI
    if available_foreign:
        print(f"\n测试国外AI (使用 {available_foreign[0]}):")
        analyzer.switch_provider(available_foreign[0])
        
        foreign_scores = []
        for case in comparison_cases:
            try:
                result = analyzer.analyze_requirement(case, "excel", {"comparison_test": True})
                confidence = result.get('confidence', 0)
                operations_count = len(result.get('operations', []))
                
                score = confidence + (operations_count * 0.1)
                foreign_scores.append(score)
                
                print(f"  '{case[:20]}...': 置信度 {confidence:.2f}, 操作数 {operations_count}")
                
            except Exception as e:
                foreign_scores.append(0)
                print(f"  '{case[:20]}...': 失败 - {e}")
        
        comparison_results['foreign'] = sum(foreign_scores) / len(foreign_scores) if foreign_scores else 0
    
    # 显示对比结果
    if comparison_results:
        print(f"\n=== 对比结果 ===")
        if 'chinese' in comparison_results:
            print(f"国产AI平均得分: {comparison_results['chinese']:.2f}")
        if 'foreign' in comparison_results:
            print(f"国外AI平均得分: {comparison_results['foreign']:.2f}")
        
        if 'chinese' in comparison_results and 'foreign' in comparison_results:
            if comparison_results['chinese'] > comparison_results['foreign']:
                print("🏆 国产AI在中文处理方面表现更好")
            elif comparison_results['foreign'] > comparison_results['chinese']:
                print("🏆 国外AI在中文处理方面表现更好")
            else:
                print("🤝 两者在中文处理方面表现相当")

def interactive_chinese_test():
    """交互式中文AI测试"""
    print(f"\n=== 交互式中文AI测试 ===")
    
    analyzer = AIAnalyzer()
    
    while True:
        print(f"\n选择测试类型:")
        print("1. 基础中文理解测试")
        print("2. 中文特色功能测试")
        print("3. 中外AI对比测试")
        print("4. 自定义中文测试")
        print("5. 退出")
        
        choice = input("请选择 (1-5): ").strip()
        
        if choice == '1':
            test_chinese_providers()
        elif choice == '2':
            test_chinese_specific_features()
        elif choice == '3':
            compare_chinese_vs_foreign()
        elif choice == '4':
            user_input = input("请输入中文需求描述: ").strip()
            file_type = input("文件类型 (excel/word): ").strip().lower()
            
            if file_type in ['excel', 'word'] and user_input:
                # 尝试所有可用的国产AI
                chinese_providers = ['deepseek', 'kimi', 'zhipu', 'doubao']
                
                for provider_name in chinese_providers:
                    if analyzer.switch_provider(provider_name):
                        print(f"\n使用 {provider_name} 分析:")
                        try:
                            result = analyzer.analyze_requirement(user_input, file_type, {"custom_test": True})
                            
                            print(f"  置信度: {result.get('confidence', 0):.2f}")
                            operations = result.get('operations', [])
                            print(f"  识别操作 ({len(operations)}):")
                            for i, op in enumerate(operations, 1):
                                print(f"    {i}. {op.get('action', 'N/A')}")
                            
                            suggestions = result.get('suggestions', [])
                            if suggestions:
                                print(f"  建议: {suggestions[0]}")
                            
                        except Exception as e:
                            print(f"  ❌ 分析失败: {e}")
                        
                        break
                else:
                    print("❌ 没有可用的国产AI提供商")
            else:
                print("无效输入")
        elif choice == '5':
            break
        else:
            print("无效选择")

def main():
    """主函数"""
    print("DocumentHandler 国产AI提供商测试工具")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'basic':
            test_chinese_providers()
        elif command == 'features':
            test_chinese_specific_features()
        elif command == 'compare':
            compare_chinese_vs_foreign()
        elif command == 'interactive':
            interactive_chinese_test()
        else:
            print(f"未知命令: {command}")
            print("可用命令: basic, features, compare, interactive")
    else:
        # 默认运行基础测试
        test_chinese_providers()
        
        # 询问是否运行更多测试
        if input("\n是否测试中文特色功能? (y/n): ").lower().startswith('y'):
            test_chinese_specific_features()
        
        if input("\n是否运行中外AI对比测试? (y/n): ").lower().startswith('y'):
            compare_chinese_vs_foreign()

if __name__ == "__main__":
    main()