"""
Claude (Anthropic) 提供商实现
"""
import json
from typing import Dict, Any
from .base_provider import BaseAIProvider

class ClaudeProvider(BaseAIProvider):
    """Claude API提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get('api_key')
        self.model = config.get('model', 'claude-3-sonnet-20240229')
        self.max_tokens = config.get('max_tokens', 2000)
        super().__init__(config)
    
    def _check_availability(self) -> bool:
        """检查Claude是否可用"""
        if not self.api_key:
            return False
        
        try:
            import anthropic
            return True
        except ImportError:
            print("警告: 未安装anthropic包，请运行: pip install anthropic")
            return False
    
    def analyze_requirement(self, user_input: str, file_type: str, file_info: Dict) -> Dict[str, Any]:
        """使用Claude分析需求"""
        if not self.is_available:
            raise Exception("Claude提供商不可用")
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            prompt = self._build_base_prompt(user_input, file_type, file_info)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": f"你是一个文档处理专家，能够理解用户需求并生成具体的处理指令。请始终返回有效的JSON格式。\n\n{prompt}"
                    }
                ]
            )
            
            result_text = response.content[0].text.strip()
            
            # 尝试解析JSON
            try:
                result = json.loads(result_text)
                result["provider"] = "Claude"
                result["model"] = self.model
                return result
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    result["provider"] = "Claude"
                    result["model"] = self.model
                    return result
                else:
                    raise Exception("无法解析AI返回的JSON格式")
            
        except Exception as e:
            raise Exception(f"Claude API调用失败: {e}")
    
    def get_provider_info(self) -> Dict[str, Any]:
        """获取Claude提供商信息"""
        info = super().get_provider_info()
        info.update({
            "model": self.model,
            "max_tokens": self.max_tokens,
            "has_api_key": bool(self.api_key)
        })
        return info