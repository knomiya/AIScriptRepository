"""
本地AI模型提供商实现
支持通过Ollama等本地部署的模型
"""
import json
import requests
from typing import Dict, Any
from .base_provider import BaseAIProvider

class LocalProvider(BaseAIProvider):
    """本地AI模型提供商（如Ollama）"""
    
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model = config.get('model', 'llama2')
        self.timeout = config.get('timeout', 30)
        super().__init__(config)
    
    def _check_availability(self) -> bool:
        """检查本地AI服务是否可用"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def analyze_requirement(self, user_input: str, file_type: str, file_info: Dict) -> Dict[str, Any]:
        """使用本地AI分析需求"""
        if not self.is_available:
            raise Exception("本地AI服务不可用，请检查Ollama等服务是否启动")
        
        try:
            prompt = self._build_base_prompt(user_input, file_type, file_info)
            
            # Ollama API调用
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"本地AI服务返回错误: {response.status_code}")
            
            result_text = response.json().get('response', '').strip()
            
            # 尝试解析JSON
            try:
                result = json.loads(result_text)
                result["provider"] = "Local"
                result["model"] = self.model
                return result
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    result["provider"] = "Local"
                    result["model"] = self.model
                    return result
                else:
                    # 本地模型可能返回格式不标准，使用备用解析
                    return self._fallback_parse(result_text, user_input, file_type)
            
        except Exception as e:
            raise Exception(f"本地AI调用失败: {e}")
    
    def _fallback_parse(self, ai_response: str, user_input: str, file_type: str) -> Dict[str, Any]:
        """备用解析方法，当AI返回格式不标准时使用"""
        # 基于关键词的简单解析
        operations = []
        
        response_lower = ai_response.lower()
        
        if file_type == 'excel':
            if any(word in response_lower for word in ['统计', '计算', '平均', '总和']):
                operations.append({
                    "type": "calculate",
                    "action": "数据统计",
                    "description": "对数据进行统计分析"
                })
            
            if any(word in response_lower for word in ['筛选', '过滤', '查找']):
                operations.append({
                    "type": "filter",
                    "action": "数据筛选",
                    "description": "根据条件筛选数据"
                })
        
        elif file_type == 'word':
            if any(word in response_lower for word in ['格式', '样式', '字体']):
                operations.append({
                    "type": "format",
                    "action": "格式调整",
                    "description": "调整文档格式"
                })
        
        if not operations:
            operations.append({
                "type": "analyze",
                "action": "文档分析",
                "description": "分析文档内容"
            })
        
        return {
            "user_requirement": user_input,
            "file_type": file_type,
            "operations": operations,
            "confidence": 0.6,
            "suggestions": ["本地AI模型解析，建议使用更具体的需求描述"],
            "provider": "Local",
            "model": self.model,
            "raw_response": ai_response
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """获取本地提供商信息"""
        info = super().get_provider_info()
        info.update({
            "base_url": self.base_url,
            "model": self.model,
            "timeout": self.timeout
        })
        return info