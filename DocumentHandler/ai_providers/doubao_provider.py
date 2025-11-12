"""
豆包 (字节跳动) AI提供商实现
"""
import json
import requests
from typing import Dict, Any
from .base_provider import BaseAIProvider

class DoubaoProvider(BaseAIProvider):
    """豆包 API提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url', 'https://ark.cn-beijing.volces.com/api/v3')
        self.model = config.get('model', 'doubao-pro-4k')
        self.temperature = config.get('temperature', 0.3)
        self.max_tokens = config.get('max_tokens', 2000)
        super().__init__(config)
    
    def _check_availability(self) -> bool:
        """检查豆包是否可用"""
        if not self.api_key:
            return False
        
        try:
            # 测试API连接
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # 豆包可能需要不同的测试端点
            test_payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=test_payload,
                timeout=5
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"豆包连接测试失败: {e}")
            return False
    
    def analyze_requirement(self, user_input: str, file_type: str, file_info: Dict) -> Dict[str, Any]:
        """使用豆包分析需求"""
        if not self.is_available:
            raise Exception("豆包提供商不可用")
        
        try:
            prompt = self._build_base_prompt(user_input, file_type, file_info)
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是豆包AI助手，专门处理文档分析任务。你对中文语境有深入理解，能够准确把握用户的文档处理需求，并生成详细的操作指令。请确保输出格式为标准JSON。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"豆包API返回错误: {response.status_code} - {response.text}")
            
            result_data = response.json()
            result_text = result_data['choices'][0]['message']['content'].strip()
            
            # 尝试解析JSON
            try:
                result = json.loads(result_text)
                result["provider"] = "Doubao"
                result["model"] = self.model
                return result
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    result["provider"] = "Doubao"
                    result["model"] = self.model
                    return result
                else:
                    raise Exception("无法解析豆包返回的JSON格式")
            
        except Exception as e:
            raise Exception(f"豆包API调用失败: {e}")
    
    def get_provider_info(self) -> Dict[str, Any]:
        """获取豆包提供商信息"""
        info = super().get_provider_info()
        info.update({
            "base_url": self.base_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "has_api_key": bool(self.api_key),
            "features": ["中文优化", "多模态支持", "企业级服务"]
        })
        return info