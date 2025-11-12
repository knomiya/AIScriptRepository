"""
AI提供商管理器
统一管理和调度不同的AI提供商
"""
from typing import Dict, Any, List, Optional
import os
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from .local_provider import LocalProvider
from .rule_based_provider import RuleBasedProvider
from .deepseek_provider import DeepSeekProvider
from .kimi_provider import KimiProvider
from .zhipu_provider import ZhipuProvider
from .doubao_provider import DoubaoProvider

class AIProviderManager:
    """AI提供商管理器"""
    
    def __init__(self, config_file: str = None):
        """
        初始化AI提供商管理器
        
        Args:
            config_file: 配置文件路径，如果为None则使用环境变量
        """
        self.providers = {}
        self.active_provider = None
        self.fallback_provider = RuleBasedProvider()
        self.provider_chain = []  # 提供商链
        self.current_scenario = None  # 当前场景
        
        # 加载配置
        self.config = self._load_config(config_file)
        
        # 初始化所有提供商
        self._initialize_providers()
        
        # 构建提供商链
        self._build_provider_chain()
        
        # 选择可用的提供商
        self._select_active_provider()
    
    def _load_config(self, config_file: str = None) -> Dict[str, Any]:
        """加载配置"""
        # 默认配置
        default_config = {
            "provider_strategy": {
                "mode": "priority_with_fallback",
                "enabled_providers": ["rule_based"],
                "primary_provider": "rule_based",
                "fallback_chain": ["rule_based"],
                "retry_on_failure": True,
                "max_retries": 2,
                "timeout_seconds": 30
            },
            "providers": {
                "deepseek": {
                    "enabled": False,
                    "api_key": os.getenv('DEEPSEEK_API_KEY'),
                    "model": os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
                    "temperature": float(os.getenv('DEEPSEEK_TEMPERATURE', '0.3')),
                    "max_tokens": int(os.getenv('DEEPSEEK_MAX_TOKENS', '2000')),
                    "priority": 1
                },
                "kimi": {
                    "enabled": False,
                    "api_key": os.getenv('KIMI_API_KEY'),
                    "model": os.getenv('KIMI_MODEL', 'moonshot-v1-8k'),
                    "temperature": float(os.getenv('KIMI_TEMPERATURE', '0.3')),
                    "max_tokens": int(os.getenv('KIMI_MAX_TOKENS', '2000')),
                    "priority": 2
                },
                "zhipu": {
                    "enabled": False,
                    "api_key": os.getenv('ZHIPU_API_KEY'),
                    "model": os.getenv('ZHIPU_MODEL', 'glm-4'),
                    "temperature": float(os.getenv('ZHIPU_TEMPERATURE', '0.3')),
                    "max_tokens": int(os.getenv('ZHIPU_MAX_TOKENS', '2000')),
                    "priority": 3
                },
                "doubao": {
                    "enabled": False,
                    "api_key": os.getenv('DOUBAO_API_KEY'),
                    "model": os.getenv('DOUBAO_MODEL', 'doubao-pro-4k'),
                    "temperature": float(os.getenv('DOUBAO_TEMPERATURE', '0.3')),
                    "max_tokens": int(os.getenv('DOUBAO_MAX_TOKENS', '2000')),
                    "priority": 4
                },
                "openai": {
                    "enabled": False,
                    "api_key": os.getenv('OPENAI_API_KEY'),
                    "model": os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                    "temperature": float(os.getenv('OPENAI_TEMPERATURE', '0.3')),
                    "max_tokens": int(os.getenv('OPENAI_MAX_TOKENS', '2000')),
                    "priority": 5
                },
                "claude": {
                    "enabled": False,
                    "api_key": os.getenv('CLAUDE_API_KEY'),
                    "model": os.getenv('CLAUDE_MODEL', 'claude-3-sonnet-20240229'),
                    "max_tokens": int(os.getenv('CLAUDE_MAX_TOKENS', '2000')),
                    "priority": 6
                },
                "local": {
                    "enabled": False,
                    "base_url": os.getenv('LOCAL_AI_URL', 'http://localhost:11434'),
                    "model": os.getenv('LOCAL_AI_MODEL', 'llama2'),
                    "timeout": int(os.getenv('LOCAL_AI_TIMEOUT', '30')),
                    "priority": 7
                },
                "rule_based": {
                    "enabled": True,
                    "rule_config_path": None,
                    "priority": 99
                }
            },
            "scenarios": {},
            "global_settings": {
                "log_level": "INFO",
                "enable_caching": False,
                "cache_ttl_seconds": 300
            }
        }
        
        # 如果提供了配置文件，尝试加载并合并
        if config_file and os.path.exists(config_file):
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    # 深度合并配置
                    config = self._deep_merge_config(default_config, file_config)
                    print(f"已加载配置文件: {config_file}")
            except Exception as e:
                print(f"警告: 无法加载配置文件 {config_file}: {e}")
                config = default_config
        else:
            config = default_config
        
        return config
    
    def _deep_merge_config(self, default: Dict, override: Dict) -> Dict:
        """深度合并配置"""
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _initialize_providers(self):
        """初始化所有提供商"""
        provider_configs = self.config.get('providers', {})
        
        # 只初始化启用的提供商
        for provider_name, provider_config in provider_configs.items():
            if not provider_config.get('enabled', False):
                continue
                
            try:
                if provider_name == 'deepseek':
                    self.providers['deepseek'] = DeepSeekProvider(provider_config)
                elif provider_name == 'kimi':
                    self.providers['kimi'] = KimiProvider(provider_config)
                elif provider_name == 'zhipu':
                    self.providers['zhipu'] = ZhipuProvider(provider_config)
                elif provider_name == 'doubao':
                    self.providers['doubao'] = DoubaoProvider(provider_config)
                elif provider_name == 'openai':
                    self.providers['openai'] = OpenAIProvider(provider_config)
                elif provider_name == 'claude':
                    self.providers['claude'] = ClaudeProvider(provider_config)
                elif provider_name == 'local':
                    self.providers['local'] = LocalProvider(provider_config)
                elif provider_name == 'rule_based':
                    self.providers['rule_based'] = RuleBasedProvider(provider_config)
                    self.fallback_provider = self.providers['rule_based']
                
                print(f"✓ 已初始化提供商: {provider_name}")
                
            except Exception as e:
                print(f"✗ 初始化提供商 {provider_name} 失败: {e}")
        
        # 确保规则引擎始终可用作为最终备用
        if 'rule_based' not in self.providers:
            self.providers['rule_based'] = self.fallback_provider
    
    def _build_provider_chain(self):
        """构建提供商链"""
        strategy = self.config.get('provider_strategy', {})
        enabled_providers = strategy.get('enabled_providers', ['rule_based'])
        
        # 按优先级排序
        provider_priority = []
        for provider_name in enabled_providers:
            if provider_name in self.providers:
                provider_config = self.config.get('providers', {}).get(provider_name, {})
                priority = provider_config.get('priority', 99)
                provider_priority.append((priority, provider_name))
        
        # 排序并构建链
        provider_priority.sort(key=lambda x: x[0])
        self.provider_chain = [name for _, name in provider_priority]
        
        print(f"提供商链: {' -> '.join(self.provider_chain)}")
    
    def _select_active_provider(self):
        """根据配置选择活动提供商"""
        strategy = self.config.get('provider_strategy', {})
        primary_provider = strategy.get('primary_provider')
        
        # 如果指定了主要提供商，优先使用
        if primary_provider and primary_provider in self.providers:
            provider = self.providers[primary_provider]
            if provider.is_available:
                self.active_provider = provider
                print(f"✓ 选择主要提供商: {primary_provider}")
                return
            else:
                print(f"✗ 主要提供商 {primary_provider} 不可用")
        
        # 否则按提供商链顺序选择第一个可用的
        for provider_name in self.provider_chain:
            if provider_name in self.providers:
                provider = self.providers[provider_name]
                if provider.is_available:
                    self.active_provider = provider
                    print(f"✓ 选择提供商: {provider_name}")
                    return
        
        # 如果都不可用，使用规则引擎
        self.active_provider = self.fallback_provider
        print("⚠ 使用备用规则引擎")
    
    def analyze_requirement(self, user_input: str, file_type: str, file_info: Dict, 
                          scenario: str = None) -> Dict[str, Any]:
        """
        分析用户需求
        
        Args:
            user_input: 用户输入
            file_type: 文件类型
            file_info: 文件信息
            scenario: 场景名称（可选）
            
        Returns:
            分析结果
        """
        # 设置当前场景
        self.current_scenario = scenario or f"{file_type}_processing"
        
        # 根据场景选择提供商
        scenario_providers = self._get_scenario_providers(self.current_scenario)
        
        # 尝试场景优先提供商
        for provider_name in scenario_providers:
            if provider_name in self.providers:
                provider = self.providers[provider_name]
                if provider.is_available:
                    try:
                        print(f"🎯 使用场景提供商: {provider_name} (场景: {self.current_scenario})")
                        
                        # 应用场景特定配置
                        result = self._analyze_with_scenario_config(
                            provider, user_input, file_type, file_info, self.current_scenario
                        )
                        
                        # 添加提供商信息
                        result['provider_info'] = {
                            'name': provider_name,
                            'scenario': self.current_scenario,
                            'is_primary': provider_name == scenario_providers[0] if scenario_providers else False
                        }
                        
                        return result
                        
                    except Exception as e:
                        print(f"✗ 场景提供商 {provider_name} 失败: {e}")
                        continue
        
        # 如果场景提供商都失败，使用默认流程
        return self._analyze_with_default_flow(user_input, file_type, file_info)
    
    def _get_scenario_providers(self, scenario: str) -> List[str]:
        """获取场景对应的提供商列表"""
        scenarios = self.config.get('scenarios', {})
        scenario_config = scenarios.get(scenario, {})
        
        # 获取首选提供商
        preferred = scenario_config.get('preferred_providers', [])
        fallback = scenario_config.get('fallback_providers', [])
        
        # 合并并去重
        providers = []
        for p in preferred + fallback:
            if p not in providers and p in self.providers:
                providers.append(p)
        
        # 如果没有配置场景，使用默认提供商链
        if not providers:
            providers = self.provider_chain
        
        return providers
    
    def _analyze_with_scenario_config(self, provider, user_input: str, file_type: str, 
                                    file_info: Dict, scenario: str) -> Dict[str, Any]:
        """使用场景特定配置进行分析"""
        scenarios = self.config.get('scenarios', {})
        scenario_config = scenarios.get(scenario, {})
        special_config = scenario_config.get('special_config', {})
        
        # 临时应用场景配置（如果提供商支持）
        original_config = {}
        if hasattr(provider, 'config') and special_config:
            for key, value in special_config.items():
                if hasattr(provider, key):
                    original_config[key] = getattr(provider, key)
                    setattr(provider, key, value)
        
        try:
            result = provider.analyze_requirement(user_input, file_type, file_info)
            return result
        finally:
            # 恢复原始配置
            for key, value in original_config.items():
                setattr(provider, key, value)
    
    def _analyze_with_default_flow(self, user_input: str, file_type: str, file_info: Dict) -> Dict[str, Any]:
        """使用默认流程进行分析"""
        if not self.active_provider:
            raise Exception("没有可用的AI提供商")
        
        try:
            print(f"🔄 使用默认提供商: {self.active_provider.name}")
            result = self.active_provider.analyze_requirement(user_input, file_type, file_info)
            
            result['provider_info'] = {
                'name': self.active_provider.name,
                'scenario': 'default',
                'is_primary': True
            }
            
            return result
            
        except Exception as e:
            print(f"✗ 默认提供商失败: {e}")
            
            # 如果启用了重试机制，尝试其他提供商
            strategy = self.config.get('provider_strategy', {})
            if strategy.get('retry_on_failure', True):
                return self._retry_with_fallback(user_input, file_type, file_info)
            else:
                raise e
    
    def _retry_with_fallback(self, user_input: str, file_type: str, file_info: Dict) -> Dict[str, Any]:
        """使用备用提供商重试"""
        strategy = self.config.get('provider_strategy', {})
        fallback_chain = strategy.get('fallback_chain', [])
        max_retries = strategy.get('max_retries', 2)
        
        current_provider_name = self.active_provider.name if self.active_provider else None
        
        # 构建重试列表（排除当前失败的提供商）
        retry_providers = []
        
        # 首先尝试配置的fallback_chain
        for provider_name in fallback_chain:
            if (provider_name in self.providers and 
                provider_name != current_provider_name and
                self.providers[provider_name].is_available):
                retry_providers.append(provider_name)
        
        # 然后尝试提供商链中的其他提供商
        for provider_name in self.provider_chain:
            if (provider_name not in retry_providers and
                provider_name in self.providers and 
                provider_name != current_provider_name and
                self.providers[provider_name].is_available):
                retry_providers.append(provider_name)
        
        # 限制重试次数
        retry_providers = retry_providers[:max_retries]
        
        print(f"🔄 开始重试，备用提供商: {retry_providers}")
        
        # 尝试备用提供商
        for i, provider_name in enumerate(retry_providers, 1):
            try:
                print(f"🔄 重试 {i}/{len(retry_providers)}: {provider_name}")
                provider = self.providers[provider_name]
                result = provider.analyze_requirement(user_input, file_type, file_info)
                
                # 标记为重试成功
                result['provider_info'] = {
                    'name': provider_name,
                    'scenario': 'fallback',
                    'is_primary': False,
                    'retry_attempt': i
                }
                
                print(f"✓ 重试成功: {provider_name}")
                return result
                
            except Exception as e:
                print(f"✗ 重试失败 {provider_name}: {e}")
                continue
        
        # 最后使用规则引擎
        print("🛡 使用规则引擎作为最终备用方案")
        try:
            result = self.fallback_provider.analyze_requirement(user_input, file_type, file_info)
            result['provider_info'] = {
                'name': 'rule_based',
                'scenario': 'final_fallback',
                'is_primary': False,
                'retry_attempt': len(retry_providers) + 1
            }
            return result
        except Exception as e:
            raise Exception(f"所有提供商都失败，包括规则引擎: {e}")
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """获取所有可用提供商的信息"""
        providers_info = []
        
        for name, provider in self.providers.items():
            info = provider.get_provider_info()
            info['name'] = name
            info['is_active'] = provider == self.active_provider
            providers_info.append(info)
        
        return providers_info
    
    def switch_provider(self, provider_name: str) -> bool:
        """
        切换到指定的提供商
        
        Args:
            provider_name: 提供商名称
            
        Returns:
            是否切换成功
        """
        if provider_name not in self.providers:
            print(f"提供商 {provider_name} 不存在")
            return False
        
        provider = self.providers[provider_name]
        if not provider.is_available:
            print(f"提供商 {provider_name} 不可用")
            return False
        
        self.active_provider = provider
        print(f"已切换到提供商: {provider_name}")
        return True
    
    def add_custom_provider(self, name: str, provider_instance):
        """
        添加自定义提供商
        
        Args:
            name: 提供商名称
            provider_instance: 提供商实例
        """
        self.providers[name] = provider_instance
        print(f"已添加自定义提供商: {name}")
    
    def get_current_provider_info(self) -> Dict[str, Any]:
        """获取当前活动提供商的信息"""
        if self.active_provider:
            return self.active_provider.get_provider_info()
        else:
            return {"error": "没有活动的提供商"}
    
    def test_all_providers(self) -> Dict[str, Any]:
        """测试所有提供商的可用性"""
        test_results = {}
        
        test_input = "测试文档处理功能"
        test_file_type = "excel"
        test_file_info = {"test": True}
        
        for name, provider in self.providers.items():
            try:
                if provider.is_available:
                    result = provider.analyze_requirement(test_input, test_file_type, test_file_info)
                    test_results[name] = {
                        "status": "success",
                        "response_time": "N/A",  # 可以添加时间测量
                        "confidence": result.get('confidence', 0)
                    }
                else:
                    test_results[name] = {
                        "status": "unavailable",
                        "reason": "Provider not available"
                    }
            except Exception as e:
                test_results[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return test_results
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        strategy = self.config.get('provider_strategy', {})
        providers = self.config.get('providers', {})
        scenarios = self.config.get('scenarios', {})
        
        enabled_providers = [name for name, config in providers.items() if config.get('enabled', False)]
        
        return {
            'strategy': {
                'mode': strategy.get('mode', 'unknown'),
                'primary_provider': strategy.get('primary_provider'),
                'enabled_providers': enabled_providers,
                'retry_enabled': strategy.get('retry_on_failure', False),
                'max_retries': strategy.get('max_retries', 0)
            },
            'providers': {
                'total': len(providers),
                'enabled': len(enabled_providers),
                'available': len([p for p in self.providers.values() if p.is_available]),
                'current_active': self.active_provider.name if self.active_provider else None
            },
            'scenarios': {
                'total': len(scenarios),
                'configured': list(scenarios.keys())
            },
            'provider_chain': self.provider_chain
        }
    
    def set_scenario(self, scenario: str):
        """设置当前场景"""
        self.current_scenario = scenario
        print(f"📋 设置场景: {scenario}")
    
    def reload_config(self, config_file: str = None):
        """重新加载配置"""
        print("🔄 重新加载配置...")
        
        # 保存当前状态
        old_providers = list(self.providers.keys())
        
        # 重新加载
        self.config = self._load_config(config_file)
        self.providers.clear()
        self._initialize_providers()
        self._build_provider_chain()
        self._select_active_provider()
        
        new_providers = list(self.providers.keys())
        
        print(f"✓ 配置重新加载完成")
        print(f"  之前的提供商: {old_providers}")
        print(f"  现在的提供商: {new_providers}")
    
    def enable_provider(self, provider_name: str) -> bool:
        """启用指定提供商"""
        if provider_name not in self.config.get('providers', {}):
            print(f"✗ 提供商 {provider_name} 不存在于配置中")
            return False
        
        # 更新配置
        self.config['providers'][provider_name]['enabled'] = True
        
        # 重新初始化该提供商
        try:
            provider_config = self.config['providers'][provider_name]
            
            if provider_name == 'deepseek':
                self.providers[provider_name] = DeepSeekProvider(provider_config)
            elif provider_name == 'kimi':
                self.providers[provider_name] = KimiProvider(provider_config)
            elif provider_name == 'zhipu':
                self.providers[provider_name] = ZhipuProvider(provider_config)
            elif provider_name == 'doubao':
                self.providers[provider_name] = DoubaoProvider(provider_config)
            elif provider_name == 'openai':
                self.providers[provider_name] = OpenAIProvider(provider_config)
            elif provider_name == 'claude':
                self.providers[provider_name] = ClaudeProvider(provider_config)
            elif provider_name == 'local':
                self.providers[provider_name] = LocalProvider(provider_config)
            elif provider_name == 'rule_based':
                self.providers[provider_name] = RuleBasedProvider(provider_config)
            
            # 重新构建提供商链
            self._build_provider_chain()
            
            print(f"✓ 已启用提供商: {provider_name}")
            return True
            
        except Exception as e:
            print(f"✗ 启用提供商 {provider_name} 失败: {e}")
            return False
    
    def disable_provider(self, provider_name: str) -> bool:
        """禁用指定提供商"""
        if provider_name not in self.providers:
            print(f"✗ 提供商 {provider_name} 未初始化")
            return False
        
        # 不能禁用规则引擎（最终备用）
        if provider_name == 'rule_based':
            print(f"✗ 不能禁用规则引擎（最终备用方案）")
            return False
        
        # 更新配置
        if provider_name in self.config.get('providers', {}):
            self.config['providers'][provider_name]['enabled'] = False
        
        # 移除提供商
        del self.providers[provider_name]
        
        # 如果禁用的是当前活动提供商，重新选择
        if self.active_provider and self.active_provider.name == provider_name:
            self._select_active_provider()
        
        # 重新构建提供商链
        self._build_provider_chain()
        
        print(f"✓ 已禁用提供商: {provider_name}")
        return True
    
    def get_provider_health(self) -> Dict[str, Any]:
        """获取提供商健康状态"""
        health_status = {}
        
        for name, provider in self.providers.items():
            try:
                # 简单的健康检查
                is_available = provider.is_available
                
                # 尝试一个简单的测试请求
                test_result = None
                if is_available:
                    try:
                        test_result = provider.analyze_requirement(
                            "测试", "excel", {"health_check": True}
                        )
                        response_ok = bool(test_result.get('operations'))
                    except:
                        response_ok = False
                else:
                    response_ok = False
                
                health_status[name] = {
                    'available': is_available,
                    'responsive': response_ok,
                    'status': 'healthy' if (is_available and response_ok) else 'unhealthy',
                    'is_active': provider == self.active_provider
                }
                
            except Exception as e:
                health_status[name] = {
                    'available': False,
                    'responsive': False,
                    'status': 'error',
                    'error': str(e),
                    'is_active': False
                }
        
        return health_status