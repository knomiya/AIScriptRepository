"""
Excel文档处理器
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import os

class ExcelProcessor:
    def __init__(self, file_path: str):
        """初始化Excel处理器"""
        self.file_path = file_path
        self.workbook = None
        self.sheets = {}
        self.load_file()
    
    def load_file(self):
        """加载Excel文件"""
        try:
            # 读取所有工作表
            excel_file = pd.ExcelFile(self.file_path)
            self.sheet_names = excel_file.sheet_names
            
            for sheet_name in self.sheet_names:
                self.sheets[sheet_name] = pd.read_excel(self.file_path, sheet_name=sheet_name)
            
            print(f"成功加载Excel文件，包含 {len(self.sheet_names)} 个工作表")
            
        except Exception as e:
            raise Exception(f"加载Excel文件失败: {e}")
    
    def get_file_info(self) -> Dict[str, Any]:
        """获取文件基本信息"""
        info = {
            "file_path": self.file_path,
            "file_size": os.path.getsize(self.file_path),
            "sheet_count": len(self.sheet_names),
            "sheet_names": self.sheet_names,
            "sheets_info": {}
        }
        
        for sheet_name, df in self.sheets.items():
            info["sheets_info"][sheet_name] = {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist()
            }
        
        return info
    
    def execute_operations(self, operations: List[Dict]) -> Dict[str, Any]:
        """执行处理操作"""
        results = []
        
        for operation in operations:
            try:
                result = self._execute_single_operation(operation)
                results.append({
                    "operation": operation,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "operation": operation,
                    "success": False,
                    "error": str(e)
                })
        
        return {"results": results}
    
    def _execute_single_operation(self, operation: Dict) -> Any:
        """执行单个操作"""
        op_type = operation.get("type")
        
        if op_type == "calculate":
            return self._calculate_statistics()
        elif op_type == "filter":
            return self._filter_data(operation.get("parameters", {}))
        elif op_type == "sort":
            return self._sort_data(operation.get("parameters", {}))
        elif op_type == "analyze":
            return self._analyze_data()
        else:
            return f"未知操作类型: {op_type}"
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """计算统计信息"""
        stats = {}
        
        for sheet_name, df in self.sheets.items():
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_columns) > 0:
                stats[sheet_name] = {
                    "numeric_columns": numeric_columns.tolist(),
                    "statistics": df[numeric_columns].describe().to_dict()
                }
            else:
                stats[sheet_name] = {"message": "该工作表没有数值列"}
        
        return stats
    
    def _filter_data(self, parameters: Dict) -> Dict[str, Any]:
        """筛选数据"""
        # 这里可以根据参数实现具体的筛选逻辑
        # 目前返回基本的数据概览
        filtered_info = {}
        
        for sheet_name, df in self.sheets.items():
            # 示例：显示前10行数据
            filtered_info[sheet_name] = {
                "total_rows": len(df),
                "sample_data": df.head(10).to_dict('records'),
                "data_types": df.dtypes.to_dict()
            }
        
        return filtered_info
    
    def _sort_data(self, parameters: Dict) -> Dict[str, Any]:
        """排序数据"""
        sort_info = {}
        
        for sheet_name, df in self.sheets.items():
            # 默认按第一列排序
            if len(df.columns) > 0:
                first_column = df.columns[0]
                sorted_df = df.sort_values(by=first_column)
                sort_info[sheet_name] = {
                    "sorted_by": first_column,
                    "sample_sorted_data": sorted_df.head(10).to_dict('records')
                }
            else:
                sort_info[sheet_name] = {"message": "该工作表没有可排序的列"}
        
        return sort_info
    
    def _analyze_data(self) -> Dict[str, Any]:
        """分析数据"""
        analysis = {}
        
        for sheet_name, df in self.sheets.items():
            analysis[sheet_name] = {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "data_types": df.dtypes.to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "memory_usage": df.memory_usage(deep=True).sum()
            }
        
        return analysis
    
    def save_processed_file(self, output_path: str, processed_data: Dict = None):
        """保存处理后的文件"""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, df in self.sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"处理后的文件已保存到: {output_path}")
            return True
            
        except Exception as e:
            print(f"保存文件失败: {e}")
            return False