"""
AI需求分析器 - 分析用户需求并生成处理指令
支持多种AI提供商的统一接口
"""
import sys
from pathlib import Path
from typing import Dict, Any

# 添加ai_providers目录到路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / 'ai_providers'))

from ai_providers.provider_manager import AIProviderManager

class AIAnalyzer:
    def __init__(self, config_file: str = None):
        """
        初始化AI分析器
        
        Args:
            config_file: 可选的配置文件路径
        """
        self.provider_manager = AIProviderManager(config_file)
        
        # 显示当前使用的提供商信息
        current_provider = self.provider_manager.get_current_provider_info()
        provider_name = current_provider.get('name', 'Unknown')
        print(f"AI分析器已初始化，当前提供商: {provider_name}")
    
    def analyze_requirement(self, user_input: str, file_type: str, file_info: Dict, 
                          scenario: str = None) -> Dict[str, Any]:
        """
        分析用户需求并返回处理指令
        
        Args:
            user_input: 用户输入的需求描述
            file_type: 文件类型 ('excel' 或 'word')
            file_info: 文件基本信息
            scenario: 场景名称（可选）
            
        Returns:
            包含处理指令的字典
        """
        try:
            result = self.provider_manager.analyze_requirement(
                user_input, file_type, file_info, scenario
            )
            
            # 添加分析器元信息
            provider_info = result.get('provider_info', {})
            result['analyzer_info'] = {
                'provider': provider_info.get('name', 'Unknown'),
                'scenario': provider_info.get('scenario', 'default'),
                'is_primary': provider_info.get('is_primary', True),
                'available_providers': len(self.provider_manager.providers),
                'retry_attempt': provider_info.get('retry_attempt'),
                'config_summary': self.provider_manager.get_config_summary()
            }
            
            return result
            
        except Exception as e:
            # 如果所有提供商都失败，返回错误信息
            return {
                "error": f"AI分析失败: {str(e)}",
                "user_requirement": user_input,
                "file_type": file_type,
                "operations": [{
                    "type": "error",
                    "action": "分析失败",
                    "description": "无法分析用户需求，请检查AI服务配置"
                }],
                "confidence": 0.0,
                "suggestions": [
                    "请检查AI服务配置",
                    "确保网络连接正常",
                    "或使用更具体的需求描述"
                ],
                "analyzer_info": {
                    "provider": "error",
                    "scenario": scenario or "default",
                    "error_details": str(e)
                }
            }
    
    def get_available_providers(self) -> list:
        """获取所有可用的AI提供商信息"""
        return self.provider_manager.get_available_providers()
    
    def switch_provider(self, provider_name: str) -> bool:
        """
        切换AI提供商
        
        Args:
            provider_name: 提供商名称 ('openai', 'claude', 'local', 'rule_based')
            
        Returns:
            是否切换成功
        """
        return self.provider_manager.switch_provider(provider_name)
    
    def test_providers(self) -> Dict[str, Any]:
        """测试所有提供商的可用性"""
        return self.provider_manager.test_all_providers()
    
    def get_current_provider_info(self) -> Dict[str, Any]:
        """获取当前提供商信息"""
        return self.provider_manager.get_current_provider_info()
    
    def add_custom_provider(self, name: str, provider_instance):
        """
        添加自定义AI提供商
        
        Args:
            name: 提供商名称
            provider_instance: 提供商实例（需要继承BaseAIProvider）
        """
        self.provider_manager.add_custom_provider(name, provider_instance)
    
    def set_scenario(self, scenario: str):
        """
        设置当前处理场景
        
        Args:
            scenario: 场景名称
        """
        self.provider_manager.set_scenario(scenario)
    
    def enable_provider(self, provider_name: str) -> bool:
        """
        启用指定提供商
        
        Args:
            provider_name: 提供商名称
            
        Returns:
            是否启用成功
        """
        return self.provider_manager.enable_provider(provider_name)
    
    def disable_provider(self, provider_name: str) -> bool:
        """
        禁用指定提供商
        
        Args:
            provider_name: 提供商名称
            
        Returns:
            是否禁用成功
        """
        return self.provider_manager.disable_provider(provider_name)
    
    def reload_config(self, config_file: str = None):
        """
        重新加载配置
        
        Args:
            config_file: 配置文件路径
        """
        self.provider_manager.reload_config(config_file)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return self.provider_manager.get_config_summary()
    
    def get_provider_health(self) -> Dict[str, Any]:
        """获取提供商健康状态"""
        return self.provider_manager.get_provider_health()