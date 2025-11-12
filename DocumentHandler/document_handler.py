"""
文档处理主程序
支持Excel和Word文档的智能处理
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from ai_analyzer import AIAnalyzer
from processors.excel_processor import ExcelProcessor
from processors.word_processor import WordProcessor

class DocumentHandler:
    def __init__(self):
        """初始化文档处理器"""
        self.ai_analyzer = AIAnalyzer()
        self.supported_extensions = {
            '.xlsx': 'excel',
            '.xls': 'excel',
            '.docx': 'word',
            '.doc': 'word'
        }
    
    def process_document(self, file_path: str, user_requirement: str) -> Dict[str, Any]:
        """
        处理文档的主要方法
        
        Args:
            file_path: 文档文件路径
            user_requirement: 用户需求描述
            
        Returns:
            处理结果字典
        """
        try:
            # 1. 验证文件
            if not os.path.exists(file_path):
                return {"error": f"文件不存在: {file_path}"}
            
            file_type = self._get_file_type(file_path)
            if not file_type:
                return {"error": f"不支持的文件类型: {Path(file_path).suffix}"}
            
            print(f"开始处理 {file_type} 文档: {file_path}")
            print(f"用户需求: {user_requirement}")
            
            # 2. 加载文档处理器
            processor = self._create_processor(file_path, file_type)
            if not processor:
                return {"error": f"无法创建 {file_type} 处理器"}
            
            # 3. 获取文件信息
            file_info = processor.get_file_info()
            print(f"文件信息: {file_info}")
            
            # 4. AI分析需求
            analysis_result = self.ai_analyzer.analyze_requirement(
                user_requirement, file_type, file_info
            )
            print(f"AI分析结果: {analysis_result}")
            
            # 5. 执行处理操作
            processing_result = processor.execute_operations(analysis_result.get('operations', []))
            
            # 6. 组装最终结果
            final_result = {
                "success": True,
                "file_info": file_info,
                "ai_analysis": analysis_result,
                "processing_result": processing_result,
                "output_suggestions": self._generate_output_suggestions(file_path, analysis_result)
            }
            
            return final_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"处理过程中发生错误: {str(e)}"
            }
    
    def _get_file_type(self, file_path: str) -> Optional[str]:
        """获取文件类型"""
        extension = Path(file_path).suffix.lower()
        return self.supported_extensions.get(extension)
    
    def _create_processor(self, file_path: str, file_type: str):
        """创建对应的文档处理器"""
        try:
            if file_type == 'excel':
                return ExcelProcessor(file_path)
            elif file_type == 'word':
                return WordProcessor(file_path)
            else:
                return None
        except Exception as e:
            print(f"创建处理器失败: {e}")
            return None
    
    def _generate_output_suggestions(self, original_path: str, analysis_result: Dict) -> Dict[str, str]:
        """生成输出建议"""
        base_name = Path(original_path).stem
        extension = Path(original_path).suffix
        
        suggestions = {
            "processed_file": f"{base_name}_processed{extension}",
            "report_file": f"{base_name}_report.txt",
            "backup_file": f"{base_name}_backup{extension}"
        }
        
        return suggestions

def main():
    """主函数 - 命令行接口"""
    if len(sys.argv) != 3:
        print("使用方法: python document_handler.py <文件路径> <需求描述>")
        print("示例: python document_handler.py data.xlsx '统计每列的平均值'")
        return
    
    file_path = sys.argv[1]
    user_requirement = sys.argv[2]
    
    handler = DocumentHandler()
    result = handler.process_document(file_path, user_requirement)
    
    if result.get("success"):
        print("\n" + "="*50)
        print("处理完成!")
        print("="*50)
        
        # 显示AI分析结果
        ai_analysis = result.get("ai_analysis", {})
        print(f"\nAI理解的需求: {ai_analysis.get('user_requirement', 'N/A')}")
        print(f"置信度: {ai_analysis.get('confidence', 'N/A')}")
        
        operations = ai_analysis.get('operations', [])
        if operations:
            print(f"\n识别的操作:")
            for i, op in enumerate(operations, 1):
                print(f"  {i}. {op.get('action', 'N/A')}: {op.get('description', 'N/A')}")
        
        # 显示处理结果
        processing_result = result.get("processing_result", {})
        results = processing_result.get("results", [])
        
        print(f"\n执行结果:")
        for i, res in enumerate(results, 1):
            status = "✓" if res.get("success") else "✗"
            op_name = res.get("operation", {}).get("action", "未知操作")
            print(f"  {status} {op_name}")
            
            if not res.get("success"):
                print(f"    错误: {res.get('error', 'N/A')}")
        
        # 显示建议
        suggestions = ai_analysis.get('suggestions', [])
        if suggestions:
            print(f"\n建议:")
            for suggestion in suggestions:
                print(f"  • {suggestion}")
        
    else:
        print(f"处理失败: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    main()