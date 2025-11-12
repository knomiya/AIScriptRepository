"""
AI提供商基类
定义所有AI提供商需要实现的接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAIProvider(ABC):
    """AI提供商基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化AI提供商
        
        Args:
            config: 配置字典，包含API密钥等信息
        """
        self.config = config
        self.name = self.__class__.__name__
        self.is_available = self._check_availability()
    
    @abstractmethod
    def _check_availability(self) -> bool:
        """
        检查AI提供商是否可用
        
        Returns:
            bool: 是否可用
        """
        pass
    
    @abstractmethod
    def analyze_requirement(self, user_input: str, file_type: str, file_info: Dict) -> Dict[str, Any]:
        """
        分析用户需求
        
        Args:
            user_input: 用户输入的需求描述
            file_type: 文件类型
            file_info: 文件信息
            
        Returns:
            分析结果字典
        """
        pass
    
    def get_provider_info(self) -> Dict[str, Any]:
        """获取提供商信息"""
        return {
            "name": self.name,
            "is_available": self.is_available,
            "config_keys": list(self.config.keys())
        }
    
    def _build_base_prompt(self, user_input: str, file_type: str, file_info: Dict) -> str:
        """构建基础提示词"""
        # 尝试加载示例管理器
        try:
            import sys
            from pathlib import Path
            current_dir = Path(__file__).parent.parent
            sys.path.append(str(current_dir))
            
            from examples.example_manager import ExampleManager
            example_manager = ExampleManager()
            
            # 使用示例管理器创建带示例的提示
            return example_manager.create_prompt_with_examples(file_type, user_input, file_info)
            
        except Exception as e:
            # 如果示例管理器不可用，使用基础提示
            return self._build_simple_prompt(user_input, file_type, file_info)
    
    def _build_simple_prompt(self, user_input: str, file_type: str, file_info: Dict) -> str:
        """构建简单提示词（备用方案）"""
        return f"""
请分析以下文档处理需求，并返回JSON格式的处理指令：

用户需求: {user_input}
文件类型: {file_type}
文件信息: {file_info}

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