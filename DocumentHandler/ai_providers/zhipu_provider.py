"""
智谱AI (GLM) 提供商实现
"""
import json
import requests
from typing import Dict, Any
from .base_provider import BaseAIProvider

class ZhipuProvider(BaseAIProvider):
    """智谱AI API提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url', 'https://open.bigmodel.cn/api/paas/v4')
        self.model = config.get('model', 'glm-4')
        self.temperature = config.get('temperature', 0.3)
        self.max_tokens = config.get('max_tokens', 2000)
        super().__init__(config)
    
    def _check_availability(self) -> bool:
        """检查智谱AI是否可用"""
        if not self.api_key:
            return False
        
        try:
            # 智谱AI使用JWT token认证
            import jwt
            import time
            
            # 生成JWT token
            payload = {
                "api_key": self.api_key,
                "exp": int(time.time()) + 3600,  # 1小时过期
                "timestamp": int(time.time())
            }
            
            # 智谱AI的API key格式通常是 "key.secret"
            if '.' in self.api_key:
                key_id, secret = self.api_key.split('.', 1)
                token = jwt.encode(payload, secret, algorithm="HS256", headers={"alg": "HS256", "sign_type": "SIGN"})
            else:
                # 如果不是标准格式，直接使用
                token = self.api_key
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # 测试连接
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
            print(f"智谱AI连接测试失败: {e}")
            return False
    
    def analyze_requirement(self, user_input: str, file_type: str, file_info: Dict) -> Dict[str, Any]:
        """使用智谱AI分析需求"""
        if not self.is_available:
            raise Exception("智谱AI提供商不可用")
        
        try:
            # 生成JWT token
            import jwt
            import time
            
            payload = {
                "api_key": self.api_key,
                "exp": int(time.time()) + 3600,
                "timestamp": int(time.time())
            }
            
            if '.' in self.api_key:
                key_id, secret = self.api_key.split('.', 1)
                token = jwt.encode(payload, secret, algorithm="HS256", headers={"alg": "HS256", "sign_type": "SIGN"})
            else:
                token = self.api_key
            
            prompt = self._build_base_prompt(user_input, file_type, file_info)
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是智谱AI助手，专门处理文档分析和处理任务。你具有强大的中文理解能力和逻辑推理能力，能够准确理解用户的文档处理需求并生成结构化的操作方案。请确保返回标准的JSON格式。"
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
                raise Exception(f"智谱AI API返回错误: {response.status_code} - {response.text}")
            
            result_data = response.json()
            result_text = result_data['choices'][0]['message']['content'].strip()
            
            # 尝试解析JSON
            try:
                result = json.loads(result_text)
                result["provider"] = "Zhipu"
                result["model"] = self.model
                return result
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    result["provider"] = "Zhipu"
                    result["model"] = self.model
                    return result
                else:
                    raise Exception("无法解析智谱AI返回的JSON格式")
            
        except Exception as e:
            raise Exception(f"智谱AI API调用失败: {e}")
    
    def get_provider_info(self) -> Dict[str, Any]:
        """获取智谱AI提供商信息"""
        info = super().get_provider_info()
        info.update({
            "base_url": self.base_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "has_api_key": bool(self.api_key),
            "features": ["中文优化", "逻辑推理", "多轮对话", "代码生成"]
        })
        return info