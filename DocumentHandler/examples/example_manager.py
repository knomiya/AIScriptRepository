"""
示例管理器
管理AI提示中使用的示例数据
"""
import json
import random
from typing import Dict, List, Any, Optional
from pathlib import Path

class ExampleManager:
    """示例管理器"""
    
    def __init__(self, examples_path: str = None):
        """
        初始化示例管理器
        
        Args:
            examples_path: 示例文件路径
        """
        if examples_path is None:
            examples_path = Path(__file__).parent / "prompt_examples.json"
        
        self.examples_path = examples_path
        self.examples = {}
        self.load_examples()
    
    def load_examples(self):
        """加载示例数据"""
        try:
            with open(self.examples_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.examples = {
                'excel': data.get('excel_examples', []),
                'word': data.get('word_examples', []),
                'complex': data.get('complex_examples', [])
            }
            
            total_examples = sum(len(examples) for examples in self.examples.values())
            print(f"示例管理器加载成功: {total_examples} 个示例")
            
        except Exception as e:
            print(f"加载示例失败: {e}")
            self._load_default_examples()
    
    def _load_default_examples(self):
        """加载默认示例"""
        self.examples = {
            'excel': [
                {
                    'user_input': '计算平均值',
                    'expected_output': {
                        'operations': [{'type': 'calculate', 'action': '数据统计'}]
                    }
                }
            ],
            'word': [
                {
                    'user_input': '调整格式',
                    'expected_output': {
                        'operations': [{'type': 'format', 'action': '格式调整'}]
                    }
                }
            ],
            'complex': []
        }
    
    def get_examples_for_prompt(self, file_type: str, max_examples: int = 3, 
                               include_complex: bool = True) -> List[Dict[str, Any]]:
        """
        获取用于AI提示的示例
        
        Args:
            file_type: 文件类型 ('excel' 或 'word')
            max_examples: 最大示例数量
            include_complex: 是否包含复杂示例
            
        Returns:
            示例列表
        """
        selected_examples = []
        
        # 获取对应文件类型的示例
        type_examples = self.examples.get(file_type, [])
        
        # 随机选择基础示例
        if type_examples:
            basic_count = min(max_examples - (1 if include_complex else 0), len(type_examples))
            selected_examples.extend(random.sample(type_examples, basic_count))
        
        # 添加复杂示例
        if include_complex and self.examples.get('complex'):
            complex_examples = [ex for ex in self.examples['complex'] 
                              if ex.get('expected_output', {}).get('file_type') == file_type]
            if complex_examples:
                selected_examples.append(random.choice(complex_examples))
        
        return selected_examples[:max_examples]
    
    def format_examples_for_prompt(self, examples: List[Dict[str, Any]]) -> str:
        """
        将示例格式化为提示文本
        
        Args:
            examples: 示例列表
            
        Returns:
            格式化的提示文本
        """
        if not examples:
            return ""
        
        prompt_text = "\n以下是一些示例，请参考这些示例的格式和结构：\n\n"
        
        for i, example in enumerate(examples, 1):
            user_input = example.get('user_input', '')
            expected_output = example.get('expected_output', {})
            
            prompt_text += f"示例 {i}:\n"
            prompt_text += f"用户需求: {user_input}\n"
            prompt_text += f"期望输出: {json.dumps(expected_output, ensure_ascii=False, indent=2)}\n\n"
        
        return prompt_text
    
    def add_example(self, file_type: str, user_input: str, expected_output: Dict[str, Any], 
                   category: str = 'basic'):
        """
        添加新示例
        
        Args:
            file_type: 文件类型
            user_input: 用户输入
            expected_output: 期望输出
            category: 示例类别 ('basic' 或 'complex')
        """
        new_example = {
            'user_input': user_input,
            'expected_output': expected_output
        }
        
        if category == 'complex':
            self.examples['complex'].append(new_example)
        else:
            if file_type not in self.examples:
                self.examples[file_type] = []
            self.examples[file_type].append(new_example)
        
        print(f"已添加新示例: {file_type} - {category}")
    
    def get_similar_examples(self, user_input: str, file_type: str, 
                           max_examples: int = 2) -> List[Dict[str, Any]]:
        """
        获取与用户输入相似的示例
        
        Args:
            user_input: 用户输入
            file_type: 文件类型
            max_examples: 最大示例数量
            
        Returns:
            相似示例列表
        """
        all_examples = []
        
        # 收集所有相关示例
        all_examples.extend(self.examples.get(file_type, []))
        
        # 添加复杂示例中相关的
        for example in self.examples.get('complex', []):
            if example.get('expected_output', {}).get('file_type') == file_type:
                all_examples.append(example)
        
        if not all_examples:
            return []
        
        # 简单的相似度计算（基于关键词匹配）
        user_words = set(user_input.lower().split())
        scored_examples = []
        
        for example in all_examples:
            example_words = set(example.get('user_input', '').lower().split())
            similarity = len(user_words & example_words) / len(user_words | example_words)
            scored_examples.append((similarity, example))
        
        # 按相似度排序并返回前N个
        scored_examples.sort(key=lambda x: x[0], reverse=True)
        return [example for _, example in scored_examples[:max_examples]]
    
    def validate_example(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证示例格式
        
        Args:
            example: 示例数据
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        # 检查必需字段
        if 'user_input' not in example:
            errors.append("缺少 'user_input' 字段")
        
        if 'expected_output' not in example:
            errors.append("缺少 'expected_output' 字段")
        else:
            expected = example['expected_output']
            
            # 检查期望输出的结构
            if 'operations' not in expected:
                errors.append("期望输出中缺少 'operations' 字段")
            
            if 'confidence' not in expected:
                warnings.append("建议添加 'confidence' 字段")
            
            # 检查操作格式
            operations = expected.get('operations', [])
            for i, op in enumerate(operations):
                if 'type' not in op:
                    errors.append(f"操作 {i+1} 缺少 'type' 字段")
                if 'action' not in op:
                    errors.append(f"操作 {i+1} 缺少 'action' 字段")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def export_examples(self, output_path: str, file_type: str = None):
        """
        导出示例到文件
        
        Args:
            output_path: 输出文件路径
            file_type: 指定文件类型，None表示导出全部
        """
        if file_type:
            export_data = {
                f'{file_type}_examples': self.examples.get(file_type, [])
            }
        else:
            export_data = {
                'excel_examples': self.examples.get('excel', []),
                'word_examples': self.examples.get('word', []),
                'complex_examples': self.examples.get('complex', [])
            }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            print(f"示例已导出到: {output_path}")
        except Exception as e:
            print(f"导出示例失败: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取示例统计信息"""
        stats = {
            'total_examples': 0,
            'by_type': {},
            'operation_types': set(),
            'avg_operations_per_example': 0
        }
        
        total_operations = 0
        total_examples = 0
        
        for file_type, examples in self.examples.items():
            stats['by_type'][file_type] = len(examples)
            total_examples += len(examples)
            
            for example in examples:
                operations = example.get('expected_output', {}).get('operations', [])
                total_operations += len(operations)
                
                for op in operations:
                    stats['operation_types'].add(op.get('type', 'unknown'))
        
        stats['total_examples'] = total_examples
        stats['operation_types'] = list(stats['operation_types'])
        stats['avg_operations_per_example'] = total_operations / max(total_examples, 1)
        
        return stats
    
    def create_prompt_with_examples(self, file_type: str, user_input: str, 
                                  file_info: Dict[str, Any]) -> str:
        """
        创建包含示例的完整提示
        
        Args:
            file_type: 文件类型
            user_input: 用户输入
            file_info: 文件信息
            
        Returns:
            完整的提示文本
        """
        # 获取相似示例
        similar_examples = self.get_similar_examples(user_input, file_type, max_examples=2)
        
        # 如果没有相似示例，获取随机示例
        if not similar_examples:
            similar_examples = self.get_examples_for_prompt(file_type, max_examples=2)
        
        # 构建提示
        prompt = f"""请分析以下文档处理需求，并返回JSON格式的处理指令：

用户需求: {user_input}
文件类型: {file_type}
文件信息: {file_info}

{self.format_examples_for_prompt(similar_examples)}

请返回以下格式的JSON:
{{
    "user_requirement": "用户原始需求",
    "file_type": "文件类型",
    "operations": [
        {{
            "type": "操作类型",
            "action": "具体操作",
            "description": "操作描述",
            "parameters": {{}}
        }}
    ],
    "confidence": 0.9,
    "suggestions": ["建议1", "建议2"]
}}

支持的操作类型包括但不限于:
- calculate: 数据计算统计
- filter: 数据筛选过滤
- sort: 数据排序
- format: 格式调整
- replace: 内容替换
- analyze: 内容分析
- visualize: 数据可视化
- proofread: 文档校对
"""
        
        return prompt