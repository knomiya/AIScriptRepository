"""
可配置的规则引擎
支持通过JSON配置文件定义规则和参数
"""
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

class ConfigurableRuleEngine:
    """可配置的规则引擎"""
    
    def __init__(self, config_path: str = None):
        """
        初始化规则引擎
        
        Args:
            config_path: 规则配置文件路径
        """
        if config_path is None:
            config_path = Path(__file__).parent / "rule_config.json"
        
        self.config_path = config_path
        self.rules = {}
        self.global_settings = {}
        self.load_config()
    
    def load_config(self):
        """加载规则配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.rules = {
                'excel': config.get('excel_rules', {}),
                'word': config.get('word_rules', {})
            }
            self.global_settings = config.get('global_settings', {})
            
            print(f"规则引擎配置加载成功: {len(self.rules['excel'])} Excel规则, {len(self.rules['word'])} Word规则")
            
        except Exception as e:
            print(f"加载规则配置失败: {e}")
            self._load_default_rules()
    
    def _load_default_rules(self):
        """加载默认规则（配置文件不可用时）"""
        self.rules = {
            'excel': {
                'calculate': {
                    'keywords': ['统计', '计算', '求和', '平均'],
                    'confidence_boost': 0.2
                },
                'filter': {
                    'keywords': ['筛选', '过滤', '查找'],
                    'confidence_boost': 0.15
                }
            },
            'word': {
                'format': {
                    'keywords': ['格式', '样式', '字体'],
                    'confidence_boost': 0.2
                },
                'replace': {
                    'keywords': ['替换', '修改', '更改'],
                    'confidence_boost': 0.3
                }
            }
        }
        self.global_settings = {
            'min_confidence': 0.3,
            'max_operations': 5
        }
    
    def analyze_requirement(self, user_input: str, file_type: str) -> Dict[str, Any]:
        """
        分析用户需求
        
        Args:
            user_input: 用户输入
            file_type: 文件类型
            
        Returns:
            分析结果
        """
        user_input_lower = user_input.lower()
        operations = []
        total_confidence = 0
        
        # 获取对应文件类型的规则
        file_rules = self.rules.get(file_type, {})
        
        for operation_type, rule_config in file_rules.items():
            match_result = self._match_rule(user_input_lower, rule_config)
            
            if match_result['matched']:
                operation = {
                    "type": operation_type,
                    "action": self._get_action_name(operation_type, file_type),
                    "description": self._get_description(operation_type, file_type),
                    "parameters": match_result['parameters'],
                    "confidence": match_result['confidence'],
                    "matched_keywords": match_result['matched_keywords'],
                    "matched_patterns": match_result['matched_patterns']
                }
                
                operations.append(operation)
                total_confidence += match_result['confidence']
        
        # 限制操作数量
        max_ops = self.global_settings.get('max_operations', 5)
        if len(operations) > max_ops:
            # 按置信度排序，取前N个
            operations.sort(key=lambda x: x['confidence'], reverse=True)
            operations = operations[:max_ops]
        
        # 计算平均置信度
        avg_confidence = total_confidence / max(len(operations), 1)
        
        # 如果没有匹配到操作，添加默认分析操作
        if not operations:
            operations.append({
                "type": "analyze",
                "action": "文档分析",
                "description": f"分析{file_type}文档内容",
                "parameters": {},
                "confidence": 0.5,
                "matched_keywords": [],
                "matched_patterns": []
            })
            avg_confidence = 0.5
        
        return {
            "operations": operations,
            "confidence": min(avg_confidence, 1.0),
            "rule_engine_version": "configurable_v1.0",
            "total_matches": len(operations)
        }
    
    def _match_rule(self, user_input: str, rule_config: Dict) -> Dict[str, Any]:
        """
        匹配单个规则
        
        Args:
            user_input: 用户输入（小写）
            rule_config: 规则配置
            
        Returns:
            匹配结果
        """
        matched_keywords = []
        matched_patterns = []
        confidence = 0.0
        parameters = {}
        
        # 关键词匹配
        keywords = rule_config.get('keywords', [])
        for keyword in keywords:
            if keyword in user_input:
                matched_keywords.append(keyword)
                confidence += 0.1
        
        # 正则模式匹配
        if self.global_settings.get('enable_regex', True):
            patterns = rule_config.get('patterns', [])
            for pattern in patterns:
                try:
                    if re.search(pattern, user_input):
                        matched_patterns.append(pattern)
                        confidence += 0.15
                except re.error:
                    continue
        
        # 参数提取
        parameters = self._extract_parameters(user_input, rule_config)
        
        # 置信度加成
        if matched_keywords or matched_patterns:
            confidence += rule_config.get('confidence_boost', 0.0)
        
        # 应用最小置信度阈值
        min_confidence = self.global_settings.get('min_confidence', 0.3)
        matched = confidence >= min_confidence
        
        return {
            'matched': matched,
            'confidence': min(confidence, 1.0),
            'matched_keywords': matched_keywords,
            'matched_patterns': matched_patterns,
            'parameters': parameters
        }
    
    def _extract_parameters(self, user_input: str, rule_config: Dict) -> Dict[str, Any]:
        """
        从用户输入中提取参数
        
        Args:
            user_input: 用户输入
            rule_config: 规则配置
            
        Returns:
            提取的参数
        """
        parameters = {}
        param_config = rule_config.get('parameters', {})
        
        for param_name, param_values in param_config.items():
            if isinstance(param_values, list):
                # 简单关键词匹配
                for value in param_values:
                    if value in user_input:
                        parameters[param_name] = True
                        break
                else:
                    parameters[param_name] = False
            
            elif isinstance(param_values, dict):
                # 分类参数匹配
                for category, keywords in param_values.items():
                    for keyword in keywords:
                        if keyword in user_input:
                            parameters[param_name] = category
                            break
                    if param_name in parameters:
                        break
        
        return parameters
    
    def _get_action_name(self, operation_type: str, file_type: str) -> str:
        """获取操作名称"""
        action_names = {
            'excel': {
                'calculate': '数据统计分析',
                'filter': '数据筛选',
                'sort': '数据排序',
                'visualize': '数据可视化'
            },
            'word': {
                'format': '格式调整',
                'replace': '内容替换',
                'analyze': '结构分析',
                'proofread': '文档校对'
            }
        }
        
        return action_names.get(file_type, {}).get(operation_type, f"{operation_type}操作")
    
    def _get_description(self, operation_type: str, file_type: str) -> str:
        """获取操作描述"""
        descriptions = {
            'excel': {
                'calculate': '对数据进行统计计算，包括求和、平均值、最大最小值等',
                'filter': '根据指定条件筛选数据行',
                'sort': '对数据进行排序操作',
                'visualize': '创建数据图表和可视化'
            },
            'word': {
                'format': '调整文档格式和样式',
                'replace': '替换文档中的指定内容',
                'analyze': '分析文档结构和内容统计',
                'proofread': '检查文档中的错误和问题'
            }
        }
        
        return descriptions.get(file_type, {}).get(operation_type, f"执行{operation_type}操作")
    
    def add_custom_rule(self, file_type: str, operation_type: str, rule_config: Dict):
        """
        添加自定义规则
        
        Args:
            file_type: 文件类型
            operation_type: 操作类型
            rule_config: 规则配置
        """
        if file_type not in self.rules:
            self.rules[file_type] = {}
        
        self.rules[file_type][operation_type] = rule_config
        print(f"已添加自定义规则: {file_type}.{operation_type}")
    
    def save_config(self, output_path: str = None):
        """
        保存当前配置到文件
        
        Args:
            output_path: 输出文件路径
        """
        if output_path is None:
            output_path = self.config_path
        
        config = {
            'excel_rules': self.rules.get('excel', {}),
            'word_rules': self.rules.get('word', {}),
            'global_settings': self.global_settings
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"配置已保存到: {output_path}")
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get_rule_info(self) -> Dict[str, Any]:
        """获取规则引擎信息"""
        return {
            'config_path': str(self.config_path),
            'excel_rules_count': len(self.rules.get('excel', {})),
            'word_rules_count': len(self.rules.get('word', {})),
            'global_settings': self.global_settings,
            'supported_operations': {
                'excel': list(self.rules.get('excel', {}).keys()),
                'word': list(self.rules.get('word', {}).keys())
            }
        }
    
    def test_rule(self, user_input: str, file_type: str) -> Dict[str, Any]:
        """
        测试规则匹配（调试用）
        
        Args:
            user_input: 测试输入
            file_type: 文件类型
            
        Returns:
            详细的匹配结果
        """
        result = self.analyze_requirement(user_input, file_type)
        
        # 添加调试信息
        debug_info = {
            'input': user_input,
            'file_type': file_type,
            'analysis_result': result,
            'rule_details': {}
        }
        
        # 获取每个规则的详细匹配信息
        user_input_lower = user_input.lower()
        file_rules = self.rules.get(file_type, {})
        
        for operation_type, rule_config in file_rules.items():
            match_result = self._match_rule(user_input_lower, rule_config)
            debug_info['rule_details'][operation_type] = match_result
        
        return debug_info