"""
示例管理器测试工具
用于测试和管理AI提示示例
"""
import sys
from pathlib import Path
import json

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from examples.example_manager import ExampleManager

def test_example_loading():
    """测试示例加载"""
    print("=== 示例加载测试 ===")
    
    manager = ExampleManager()
    
    # 获取统计信息
    stats = manager.get_statistics()
    
    print(f"示例统计:")
    print(f"  总示例数: {stats['total_examples']}")
    print(f"  Excel示例: {stats['by_type'].get('excel', 0)}")
    print(f"  Word示例: {stats['by_type'].get('word', 0)}")
    print(f"  复杂示例: {stats['by_type'].get('complex', 0)}")
    print(f"  平均每个示例的操作数: {stats['avg_operations_per_example']:.1f}")
    print(f"  支持的操作类型: {', '.join(stats['operation_types'])}")

def test_example_selection():
    """测试示例选择"""
    print(f"\n=== 示例选择测试 ===")
    
    manager = ExampleManager()
    
    # 测试不同文件类型的示例选择
    for file_type in ['excel', 'word']:
        print(f"\n{file_type.upper()} 示例选择:")
        
        # 获取随机示例
        examples = manager.get_examples_for_prompt(file_type, max_examples=2)
        print(f"  随机选择 {len(examples)} 个示例")
        
        for i, example in enumerate(examples, 1):
            user_input = example.get('user_input', '')
            operations = example.get('expected_output', {}).get('operations', [])
            print(f"    {i}. {user_input} ({len(operations)} 个操作)")

def test_similar_examples():
    """测试相似示例查找"""
    print(f"\n=== 相似示例查找测试 ===")
    
    manager = ExampleManager()
    
    test_cases = [
        ("计算销售数据统计", "excel"),
        ("筛选员工信息", "excel"),
        ("调整文档字体", "word"),
        ("替换公司名称", "word")
    ]
    
    for user_input, file_type in test_cases:
        print(f"\n查找与 '{user_input}' 相似的 {file_type} 示例:")
        
        similar_examples = manager.get_similar_examples(user_input, file_type, max_examples=2)
        
        if similar_examples:
            for i, example in enumerate(similar_examples, 1):
                example_input = example.get('user_input', '')
                print(f"  {i}. {example_input}")
        else:
            print("  未找到相似示例")

def test_prompt_generation():
    """测试提示生成"""
    print(f"\n=== 提示生成测试 ===")
    
    manager = ExampleManager()
    
    test_cases = [
        ("计算每列的平均值和总和", "excel"),
        ("将标题设置为黑体", "word")
    ]
    
    for user_input, file_type in test_cases:
        print(f"\n为 '{user_input}' 生成 {file_type} 提示:")
        
        prompt = manager.create_prompt_with_examples(
            file_type, 
            user_input, 
            {"test": True}
        )
        
        # 只显示提示的前500个字符
        print(f"提示长度: {len(prompt)} 字符")
        print("提示预览:")
        print("-" * 40)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("-" * 40)

def test_example_validation():
    """测试示例验证"""
    print(f"\n=== 示例验证测试 ===")
    
    manager = ExampleManager()
    
    # 测试有效示例
    valid_example = {
        "user_input": "计算平均值",
        "expected_output": {
            "user_requirement": "计算平均值",
            "file_type": "excel",
            "operations": [
                {
                    "type": "calculate",
                    "action": "数据统计",
                    "description": "计算数据平均值"
                }
            ],
            "confidence": 0.9
        }
    }
    
    print("验证有效示例:")
    validation_result = manager.validate_example(valid_example)
    print(f"  有效: {validation_result['valid']}")
    if validation_result['errors']:
        print(f"  错误: {validation_result['errors']}")
    if validation_result['warnings']:
        print(f"  警告: {validation_result['warnings']}")
    
    # 测试无效示例
    invalid_example = {
        "user_input": "测试",
        "expected_output": {
            # 缺少必要字段
        }
    }
    
    print(f"\n验证无效示例:")
    validation_result = manager.validate_example(invalid_example)
    print(f"  有效: {validation_result['valid']}")
    if validation_result['errors']:
        print(f"  错误: {validation_result['errors']}")

def test_custom_examples():
    """测试自定义示例"""
    print(f"\n=== 自定义示例测试 ===")
    
    manager = ExampleManager()
    
    # 添加自定义示例
    custom_example_output = {
        "user_requirement": "生成数据透视表",
        "file_type": "excel",
        "operations": [
            {
                "type": "pivot",
                "action": "数据透视",
                "description": "创建数据透视表",
                "parameters": {
                    "rows": "auto_detect",
                    "columns": "auto_detect",
                    "values": "auto_detect"
                }
            }
        ],
        "confidence": 0.8,
        "suggestions": ["确保数据格式正确以便创建透视表"]
    }
    
    manager.add_example(
        "excel",
        "生成数据透视表",
        custom_example_output,
        "basic"
    )
    
    print("已添加自定义示例: 生成数据透视表")
    
    # 验证自定义示例是否生效
    examples = manager.get_examples_for_prompt("excel", max_examples=5)
    pivot_examples = [ex for ex in examples if "透视" in ex.get('user_input', '')]
    
    if pivot_examples:
        print("✓ 自定义示例已成功添加并可以被选择")
    else:
        print("✗ 自定义示例未被选择（可能由于随机性）")

def interactive_example_test():
    """交互式示例测试"""
    print(f"\n=== 交互式示例测试 ===")
    
    manager = ExampleManager()
    
    while True:
        print(f"\n选择操作:")
        print("1. 查看示例统计")
        print("2. 搜索相似示例")
        print("3. 生成提示")
        print("4. 添加自定义示例")
        print("5. 验证示例")
        print("6. 导出示例")
        print("7. 退出")
        
        choice = input("请选择 (1-7): ").strip()
        
        if choice == '1':
            stats = manager.get_statistics()
            print(f"\n示例统计:")
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        elif choice == '2':
            user_input = input("请输入需求描述: ").strip()
            file_type = input("文件类型 (excel/word): ").strip().lower()
            
            if file_type in ['excel', 'word']:
                similar = manager.get_similar_examples(user_input, file_type)
                print(f"\n找到 {len(similar)} 个相似示例:")
                for i, ex in enumerate(similar, 1):
                    print(f"  {i}. {ex.get('user_input', '')}")
            else:
                print("无效的文件类型")
        
        elif choice == '3':
            user_input = input("请输入需求描述: ").strip()
            file_type = input("文件类型 (excel/word): ").strip().lower()
            
            if file_type in ['excel', 'word']:
                prompt = manager.create_prompt_with_examples(file_type, user_input, {"test": True})
                print(f"\n生成的提示 ({len(prompt)} 字符):")
                print("-" * 50)
                print(prompt)
                print("-" * 50)
            else:
                print("无效的文件类型")
        
        elif choice == '4':
            user_input = input("请输入用户需求: ").strip()
            file_type = input("文件类型 (excel/word): ").strip().lower()
            
            if file_type in ['excel', 'word']:
                print("请输入期望输出的JSON格式 (可以简化):")
                try:
                    output_json = input().strip()
                    expected_output = json.loads(output_json)
                    
                    manager.add_example(file_type, user_input, expected_output)
                    print("✓ 自定义示例已添加")
                except json.JSONDecodeError:
                    print("✗ JSON格式错误")
            else:
                print("无效的文件类型")
        
        elif choice == '5':
            print("请输入要验证的示例JSON:")
            try:
                example_json = input().strip()
                example = json.loads(example_json)
                
                result = manager.validate_example(example)
                print(f"\n验证结果:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print("✗ JSON格式错误")
        
        elif choice == '6':
            output_path = input("输出文件路径 (默认: exported_examples.json): ").strip()
            if not output_path:
                output_path = "exported_examples.json"
            
            file_type = input("指定文件类型 (excel/word/all): ").strip().lower()
            if file_type == 'all':
                file_type = None
            elif file_type not in ['excel', 'word']:
                file_type = None
            
            manager.export_examples(output_path, file_type)
        
        elif choice == '7':
            break
        
        else:
            print("无效的选择")

def main():
    """主函数"""
    print("DocumentHandler 示例管理器测试工具")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'load':
            test_example_loading()
        elif command == 'select':
            test_example_selection()
        elif command == 'similar':
            test_similar_examples()
        elif command == 'prompt':
            test_prompt_generation()
        elif command == 'validate':
            test_example_validation()
        elif command == 'custom':
            test_custom_examples()
        elif command == 'interactive':
            interactive_example_test()
        else:
            print(f"未知命令: {command}")
            print("可用命令: load, select, similar, prompt, validate, custom, interactive")
    else:
        # 默认运行所有测试
        test_example_loading()
        test_example_selection()
        test_similar_examples()
        test_prompt_generation()
        test_example_validation()
        test_custom_examples()
        
        # 询问是否运行交互式测试
        if input("\n是否运行交互式测试? (y/n): ").lower().startswith('y'):
            interactive_example_test()

if __name__ == "__main__":
    main()