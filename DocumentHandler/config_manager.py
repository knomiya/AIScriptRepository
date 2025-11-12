"""
配置管理工具
用于管理AI提供商配置
"""
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from ai_analyzer import AIAnalyzer

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file or "ai_config_advanced.json"
        self.analyzer = None
        
    def create_config_from_template(self, providers: List[str], output_file: str = None):
        """
        从模板创建配置文件
        
        Args:
            providers: 要启用的提供商列表
            output_file: 输出文件路径
        """
        if output_file is None:
            output_file = self.config_file
        
        # 基础配置模板
        config = {
            "provider_strategy": {
                "mode": "priority_with_fallback",
                "enabled_providers": providers,
                "primary_provider": providers[0] if providers else "rule_based",
                "fallback_chain": providers[1:] + ["rule_based"] if len(providers) > 1 else ["rule_based"],
                "retry_on_failure": True,
                "max_retries": min(len(providers), 3),
                "timeout_seconds": 30
            },
            "providers": {},
            "scenarios": {
                "excel_processing": {
                    "preferred_providers": providers[:2] if len(providers) >= 2 else providers,
                    "fallback_providers": ["rule_based"],
                    "special_config": {
                        "temperature": 0.2,
                        "max_tokens": 1500
                    }
                },
                "word_processing": {
                    "preferred_providers": providers[:2] if len(providers) >= 2 else providers,
                    "fallback_providers": ["rule_based"],
                    "special_config": {
                        "temperature": 0.3,
                        "max_tokens": 2000
                    }
                }
            },
            "global_settings": {
                "log_level": "INFO",
                "enable_caching": True,
                "cache_ttl_seconds": 300
            }
        }
        
        # 添加提供商配置
        provider_templates = {
            "deepseek": {
                "enabled": True,
                "api_key": "your_deepseek_api_key_here",
                "model": "deepseek-chat",
                "temperature": 0.3,
                "max_tokens": 2000,
                "priority": 1
            },
            "kimi": {
                "enabled": True,
                "api_key": "your_kimi_api_key_here",
                "model": "moonshot-v1-8k",
                "temperature": 0.3,
                "max_tokens": 2000,
                "priority": 2
            },
            "zhipu": {
                "enabled": True,
                "api_key": "your_zhipu_api_key_here",
                "model": "glm-4",
                "temperature": 0.3,
                "max_tokens": 2000,
                "priority": 3
            },
            "doubao": {
                "enabled": True,
                "api_key": "your_doubao_api_key_here",
                "model": "doubao-pro-4k",
                "temperature": 0.3,
                "max_tokens": 2000,
                "priority": 4
            },
            "openai": {
                "enabled": True,
                "api_key": "your_openai_api_key_here",
                "model": "gpt-3.5-turbo",
                "temperature": 0.3,
                "max_tokens": 2000,
                "priority": 5
            },
            "claude": {
                "enabled": True,
                "api_key": "your_claude_api_key_here",
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 2000,
                "priority": 6
            },
            "local": {
                "enabled": True,
                "base_url": "http://localhost:11434",
                "model": "llama2",
                "timeout": 60,
                "priority": 7
            },
            "rule_based": {
                "enabled": True,
                "rule_config_path": None,
                "priority": 99
            }
        }
        
        # 添加选中的提供商配置
        for i, provider in enumerate(providers, 1):
            if provider in provider_templates:
                template = provider_templates[provider].copy()
                template["priority"] = i
                config["providers"][provider] = template
        
        # 确保规则引擎始终存在
        if "rule_based" not in config["providers"]:
            config["providers"]["rule_based"] = provider_templates["rule_based"]
        
        # 保存配置
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✓ 配置文件已创建: {output_file}")
            print(f"  启用的提供商: {', '.join(providers)}")
            print(f"  主要提供商: {config['provider_strategy']['primary_provider']}")
            print(f"  备用链: {' -> '.join(config['provider_strategy']['fallback_chain'])}")
            
        except Exception as e:
            print(f"✗ 创建配置文件失败: {e}")
    
    def validate_config(self, config_file: str = None) -> Dict[str, Any]:
        """
        验证配置文件
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            验证结果
        """
        if config_file is None:
            config_file = self.config_file
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": {}
        }
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 检查必需的顶级字段
            required_fields = ["provider_strategy", "providers"]
            for field in required_fields:
                if field not in config:
                    validation_result["errors"].append(f"缺少必需字段: {field}")
                    validation_result["valid"] = False
            
            if not validation_result["valid"]:
                return validation_result
            
            # 检查提供商策略
            strategy = config.get("provider_strategy", {})
            enabled_providers = strategy.get("enabled_providers", [])
            primary_provider = strategy.get("primary_provider")
            
            if not enabled_providers:
                validation_result["warnings"].append("没有启用任何提供商")
            
            if primary_provider and primary_provider not in enabled_providers:
                validation_result["errors"].append(f"主要提供商 {primary_provider} 不在启用列表中")
                validation_result["valid"] = False
            
            # 检查提供商配置
            providers = config.get("providers", {})
            configured_providers = []
            
            for provider_name, provider_config in providers.items():
                if provider_config.get("enabled", False):
                    configured_providers.append(provider_name)
                    
                    # 检查API密钥
                    if provider_name not in ["rule_based", "local"]:
                        api_key = provider_config.get("api_key", "")
                        if not api_key or "your_" in api_key:
                            validation_result["warnings"].append(f"提供商 {provider_name} 的API密钥未配置")
            
            # 检查启用的提供商是否都有配置
            for provider in enabled_providers:
                if provider not in providers:
                    validation_result["errors"].append(f"启用的提供商 {provider} 没有配置")
                    validation_result["valid"] = False
                elif not providers[provider].get("enabled", False):
                    validation_result["warnings"].append(f"提供商 {provider} 在策略中启用但在配置中禁用")
            
            # 统计信息
            validation_result["info"] = {
                "total_providers": len(providers),
                "enabled_providers": len(configured_providers),
                "configured_providers": configured_providers,
                "primary_provider": primary_provider,
                "has_fallback": "rule_based" in configured_providers
            }
            
        except FileNotFoundError:
            validation_result["errors"].append(f"配置文件不存在: {config_file}")
            validation_result["valid"] = False
        except json.JSONDecodeError as e:
            validation_result["errors"].append(f"JSON格式错误: {e}")
            validation_result["valid"] = False
        except Exception as e:
            validation_result["errors"].append(f"验证失败: {e}")
            validation_result["valid"] = False
        
        return validation_result
    
    def test_config(self, config_file: str = None) -> Dict[str, Any]:
        """
        测试配置文件
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            测试结果
        """
        if config_file is None:
            config_file = self.config_file
        
        print(f"🧪 测试配置文件: {config_file}")
        
        # 首先验证配置
        validation = self.validate_config(config_file)
        if not validation["valid"]:
            return {
                "success": False,
                "error": "配置验证失败",
                "validation": validation
            }
        
        try:
            # 创建分析器实例
            analyzer = AIAnalyzer(config_file)
            
            # 获取配置摘要
            config_summary = analyzer.get_config_summary()
            
            # 测试提供商健康状态
            health_status = analyzer.get_provider_health()
            
            # 执行简单的分析测试
            test_cases = [
                ("计算平均值", "excel"),
                ("调整格式", "word")
            ]
            
            test_results = {}
            for user_input, file_type in test_cases:
                try:
                    result = analyzer.analyze_requirement(
                        user_input, 
                        file_type, 
                        {"test": True}
                    )
                    
                    test_results[f"{file_type}_{user_input}"] = {
                        "success": True,
                        "provider": result.get("analyzer_info", {}).get("provider"),
                        "confidence": result.get("confidence", 0),
                        "operations_count": len(result.get("operations", []))
                    }
                    
                except Exception as e:
                    test_results[f"{file_type}_{user_input}"] = {
                        "success": False,
                        "error": str(e)
                    }
            
            return {
                "success": True,
                "validation": validation,
                "config_summary": config_summary,
                "health_status": health_status,
                "test_results": test_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"测试失败: {e}",
                "validation": validation
            }
    
    def interactive_config(self):
        """交互式配置"""
        print("🔧 DocumentHandler 配置向导")
        print("=" * 40)
        
        # 选择提供商
        available_providers = [
            "deepseek", "kimi", "zhipu", "doubao", 
            "openai", "claude", "local", "rule_based"
        ]
        
        print("可用的AI提供商:")
        for i, provider in enumerate(available_providers, 1):
            print(f"  {i}. {provider}")
        
        selected_providers = []
        
        while True:
            choice = input(f"\n请选择提供商 (1-{len(available_providers)}, 回车完成): ").strip()
            
            if not choice:
                break
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_providers):
                    provider = available_providers[idx]
                    if provider not in selected_providers:
                        selected_providers.append(provider)
                        print(f"✓ 已选择: {provider}")
                    else:
                        print(f"⚠ {provider} 已经选择过了")
                else:
                    print("无效的选择")
            except ValueError:
                print("请输入有效的数字")
        
        if not selected_providers:
            selected_providers = ["rule_based"]
            print("未选择提供商，将使用规则引擎")
        
        # 确保规则引擎在列表中
        if "rule_based" not in selected_providers:
            selected_providers.append("rule_based")
        
        print(f"\n选择的提供商: {', '.join(selected_providers)}")
        
        # 选择输出文件
        output_file = input(f"配置文件名 (默认: {self.config_file}): ").strip()
        if not output_file:
            output_file = self.config_file
        
        # 创建配置
        self.create_config_from_template(selected_providers, output_file)
        
        # 询问是否测试
        if input("\n是否测试配置? (y/n): ").lower().startswith('y'):
            test_result = self.test_config(output_file)
            
            if test_result["success"]:
                print("✓ 配置测试通过")
                
                health = test_result["health_status"]
                healthy_count = sum(1 for status in health.values() if status["status"] == "healthy")
                print(f"  健康的提供商: {healthy_count}/{len(health)}")
                
            else:
                print("✗ 配置测试失败")
                print(f"  错误: {test_result.get('error', 'Unknown')}")

def main():
    """主函数"""
    print("DocumentHandler 配置管理工具")
    print("=" * 40)
    
    manager = ConfigManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'create':
            if len(sys.argv) > 2:
                providers = sys.argv[2].split(',')
                output_file = sys.argv[3] if len(sys.argv) > 3 else None
                manager.create_config_from_template(providers, output_file)
            else:
                print("用法: python config_manager.py create provider1,provider2,... [output_file]")
        
        elif command == 'validate':
            config_file = sys.argv[2] if len(sys.argv) > 2 else None
            result = manager.validate_config(config_file)
            
            print(f"验证结果: {'✓ 有效' if result['valid'] else '✗ 无效'}")
            
            if result['errors']:
                print("错误:")
                for error in result['errors']:
                    print(f"  ✗ {error}")
            
            if result['warnings']:
                print("警告:")
                for warning in result['warnings']:
                    print(f"  ⚠ {warning}")
            
            if result['info']:
                print("信息:")
                info = result['info']
                print(f"  总提供商: {info.get('total_providers', 0)}")
                print(f"  启用提供商: {info.get('enabled_providers', 0)}")
                print(f"  主要提供商: {info.get('primary_provider', 'None')}")
        
        elif command == 'test':
            config_file = sys.argv[2] if len(sys.argv) > 2 else None
            result = manager.test_config(config_file)
            
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif command == 'interactive':
            manager.interactive_config()
        
        else:
            print(f"未知命令: {command}")
            print("可用命令: create, validate, test, interactive")
    
    else:
        # 默认运行交互式配置
        manager.interactive_config()

if __name__ == "__main__":
    main()