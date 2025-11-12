"""
OpenAI提供商实现
"""
import json
from typing import Dict, Any
from .base_provider import BaseAIProvider

class OpenAIProvider(BaseAIProvider):
    """OpenAI API提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get('api_key')
        self.model = config.get('model', 'gpt-3.5-turbo')
        self.temperature = config.get('temperature', 0.3)
        self.max_tokens = config.get('max_tokens', 2000)
        super().__init__(config)
    
    def _check_availability(self) -> bool:
        """检查OpenAI是否可用"""
        if not self.api_key:
            return False
        
        try:
            import openai
            return True
        except ImportError:
            print("警告: 未安装openai包，请运行: pip install openai")
            return False
    
    def analyze_requirement(self, user_input: str, file_type: str, file_info: Dict) -> Dict[str, Any]:
        """使用OpenAI分析需求"""
        if not self.is_available:
            raise Exception("OpenAI提供商不可用")
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            prompt = self._build_base_prompt(user_input, file_type, file_info)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一个文档处理专家，能够理解用户需求并生成具体的处理指令。请始终返回有效的JSON格式。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 尝试解析JSON
            try:
                result = json.loads(result_text)
                result["provider"] = "OpenAI"
                result["model"] = self.model
                return result
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    result["provider"] = "OpenAI"
                    result["model"] = self.model
                    return result
                else:
                    raise Exception("无法解析AI返回的JSON格式")
            
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {e}")
    
    def get_provider_info(self) -> Dict[str, Any]:
        """获取OpenAI提供商信息"""
        info = super().get_provider_info()
        info.update({
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "has_api_key": bool(self.api_key)
        })
        return info