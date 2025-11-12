"""
基于规则的提供商实现
当没有AI服务可用时的备用方案，支持可配置规则引擎
"""
import sys
from pathlib import Path
from typing import Dict, Any, List

# 添加rule_engine目录到路径
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

from .base_provider import BaseAIProvider
from rule_engine.configurable_rule_engine import ConfigurableRuleEngine

class RuleBasedProvider(BaseAIProvider):
    """基于规则的分析提供商（备用方案）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = {}
        
        # 初始化可配置规则引擎
        rule_config_path = config.get('rule_config_path')
        self.rule_engine = ConfigurableRuleEngine(rule_config_path)
        
        super().__init__(config)
    
    def _check_availability(self) -> bool:
        """规则引擎始终可用"""
        return True
    
    def analyze_requirement(self, user_input: str, file_type: str, file_info: Dict) -> Dict[str, Any]:
        """使用可配置规则引擎分析需求"""
        try:
            # 使用可配置规则引擎进行分析
            analysis_result = self.rule_engine.analyze_requirement(user_input, file_type)
            
            # 生成建议
            suggestions = self._generate_suggestions(
                analysis_result.get('operations', []), 
                file_type, 
                analysis_result.get('confidence', 0.5)
            )
            
            # 构建最终结果
            result = {
                "user_requirement": user_input,
                "file_type": file_type,
                "operations": analysis_result.get('operations', []),
                "confidence": analysis_result.get('confidence', 0.5),
                "suggestions": suggestions,
                "provider": "RuleBased",
                "model": "configurable_rule_engine_v1.0",
                "rule_engine_info": {
                    "total_matches": analysis_result.get('total_matches', 0),
                    "rule_version": analysis_result.get('rule_engine_version', 'unknown')
                }
            }
            
            return result
            
        except Exception as e:
            # 如果规则引擎失败，使用简化的备用逻辑
            return self._fallback_analysis(user_input, file_type, file_info)
    
    def _fallback_analysis(self, user_input: str, file_type: str, file_info: Dict) -> Dict[str, Any]:
        """备用分析方法（当规则引擎失败时使用）"""
        user_input_lower = user_input.lower()
        operations = []
        
        # 简化的关键词匹配
        if file_type == 'excel':
            if any(word in user_input_lower for word in ['统计', '计算', '平均', '求和']):
                operations.append({
                    "type": "calculate",
                    "action": "数据统计",
                    "description": "对数据进行基础统计计算",
                    "parameters": {}
                })
            
            if any(word in user_input_lower for word in ['筛选', '过滤']):
                operations.append({
                    "type": "filter",
                    "action": "数据筛选",
                    "description": "筛选数据",
                    "parameters": {}
                })
        
        elif file_type == 'word':
            if any(word in user_input_lower for word in ['格式', '字体']):
                operations.append({
                    "type": "format",
                    "action": "格式调整",
                    "description": "调整文档格式",
                    "parameters": {}
                })
            
            if any(word in user_input_lower for word in ['替换', '修改']):
                operations.append({
                    "type": "replace",
                    "action": "内容替换",
                    "description": "替换文档内容",
                    "parameters": {}
                })
        
        # 如果没有匹配到操作，添加默认分析
        if not operations:
            operations.append({
                "type": "analyze",
                "action": "文档分析",
                "description": f"分析{file_type}文档内容",
                "parameters": {}
            })
        
        return {
            "user_requirement": user_input,
            "file_type": file_type,
            "operations": operations,
            "confidence": 0.4,
            "suggestions": ["使用简化规则分析，建议提供更具体的需求描述"],
            "provider": "RuleBased",
            "model": "fallback_rules_v1.0"
        }
    
    def _generate_suggestions(self, operations: List[Dict], file_type: str, confidence: float) -> List[str]:
        """生成处理建议"""
        suggestions = []
        
        if len(operations) == 0:
            suggestions.append("未能识别具体操作，请提供更明确的需求描述")
            if file_type == 'excel':
                suggestions.append("Excel示例: '计算销售额的平均值', '筛选年龄大于30的员工'")
            else:
                suggestions.append("Word示例: '将标题设为黑体', '替换公司名称'")
        
        elif confidence < 0.6:
            suggestions.append("识别置信度较低，建议使用更具体的关键词")
            
        elif len(operations) > 3:
            suggestions.append("识别到多个操作，建议分步骤处理")
        
        else:
            operation_names = [op.get('action', '') for op in operations]
            suggestions.append(f"识别操作: {', '.join(operation_names)}")
        
        # 添加规则引擎特定建议
        suggestions.append("提示: 可以通过修改规则配置文件来改进识别效果")
        
        return suggestions
    
    def get_rule_engine_info(self) -> Dict[str, Any]:
        """获取规则引擎信息"""
        return self.rule_engine.get_rule_info()
    
    def test_rule_matching(self, user_input: str, file_type: str) -> Dict[str, Any]:
        """测试规则匹配（调试用）"""
        return self.rule_engine.test_rule(user_input, file_type)
    
    def add_custom_rule(self, file_type: str, operation_type: str, rule_config: Dict):
        """添加自定义规则"""
        self.rule_engine.add_custom_rule(file_type, operation_type, rule_config)
    
    def get_provider_info(self) -> Dict[str, Any]:
        """获取规则引擎提供商信息"""
        info = super().get_provider_info()
        info.update({
            "description": "基于规则的需求分析引擎",
            "supported_operations": [
                "calculate", "filter", "sort", "visualize",  # Excel
                "format", "replace", "analyze", "proofread"   # Word
            ]
        })
        return info