# -*- coding: utf-8 -*-
"""
数据验证模块
提供API数据验证、完整性检查和数据清洗功能
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, validator, ValidationError

logger = logging.getLogger(__name__)

class ValidationResult:
    """验证结果类"""
    
    def __init__(self, is_valid: bool = True, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        
    def add_error(self, error: str):
        """添加错误信息"""
        self.errors.append(error)
        self.is_valid = False
        
    def add_warning(self, warning: str):
        """添加警告信息"""
        self.warnings.append(warning)
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings
        }

class OCRDataValidator:
    """OCR数据验证器"""
    
    @staticmethod
    def validate_ocr_result(data: Dict[str, Any]) -> ValidationResult:
        """验证OCR识别结果"""
        result = ValidationResult()
        
        # 检查必需字段
        required_fields = ['text', 'confidence']
        for field in required_fields:
            if field not in data:
                result.add_error(f"缺少必需字段: {field}")
            elif data[field] is None:
                result.add_error(f"字段 {field} 不能为空")
                
        # 验证置信度
        if 'confidence' in data:
            confidence = data['confidence']
            if not isinstance(confidence, (int, float)):
                result.add_error("置信度必须是数字")
            elif not 0 <= confidence <= 1:
                result.add_error("置信度必须在0-1之间")
            elif confidence < 0.5:
                result.add_warning("OCR识别置信度较低，可能影响准确性")
                
        # 验证文本内容
        if 'text' in data and data['text']:
            text = data['text']
            if not isinstance(text, str):
                result.add_error("文本内容必须是字符串")
            elif len(text.strip()) == 0:
                result.add_error("文本内容不能为空")
            elif len(text) > 10000:  # 限制文本长度
                result.add_warning("文本内容过长，可能包含无关信息")
                
        # 验证营养成分数据
        if 'nutrition_data' in data and data['nutrition_data']:
            nutrition_result = NutritionDataValidator.validate_nutrition_data(data['nutrition_data'])
            if not nutrition_result.is_valid:
                result.errors.extend(nutrition_result.errors)
                result.is_valid = False
            result.warnings.extend(nutrition_result.warnings)
            
        return result

class NutritionDataValidator:
    """营养数据验证器"""
    
    # 营养成分的合理范围（每100g）
    NUTRITION_RANGES = {
        'energy': (0, 900),      # 能量 kcal
        'protein': (0, 100),     # 蛋白质 g
        'fat': (0, 100),         # 脂肪 g
        'carbohydrate': (0, 100), # 碳水化合物 g
        'sodium': (0, 5000),     # 钠 mg
        'sugar': (0, 100),       # 糖 g
        'fiber': (0, 50),        # 膳食纤维 g
        'calcium': (0, 2000),    # 钙 mg
        'iron': (0, 100),        # 铁 mg
        'vitamin_c': (0, 1000)   # 维生素C mg
    }
    
    @staticmethod
    def validate_nutrition_data(data: Dict[str, Any]) -> ValidationResult:
        """验证营养成分数据"""
        result = ValidationResult()
        
        if not isinstance(data, dict):
            result.add_error("营养数据必须是字典格式")
            return result
            
        # 检查数值类型和范围
        for nutrient, value in data.items():
            if value is None:
                continue
                
            # 检查数值类型
            if not isinstance(value, (int, float)):
                result.add_error(f"营养成分 {nutrient} 的值必须是数字")
                continue
                
            # 检查负值
            if value < 0:
                result.add_error(f"营养成分 {nutrient} 的值不能为负数")
                continue
                
            # 检查合理范围
            if nutrient in NutritionDataValidator.NUTRITION_RANGES:
                min_val, max_val = NutritionDataValidator.NUTRITION_RANGES[nutrient]
                if value > max_val:
                    result.add_warning(f"营养成分 {nutrient} 的值 {value} 超出正常范围 (0-{max_val})")
                    
        # 检查营养成分逻辑关系
        if 'energy' in data and 'protein' in data and 'fat' in data and 'carbohydrate' in data:
            calculated_energy = (data['protein'] * 4) + (data['fat'] * 9) + (data['carbohydrate'] * 4)
            actual_energy = data['energy']
            
            # 允许20%的误差
            if abs(calculated_energy - actual_energy) > actual_energy * 0.2:
                result.add_warning("能量值与营养成分计算值差异较大，请检查数据准确性")
                
        return result

class AIAnalysisValidator:
    """AI分析结果验证器"""
    
    @staticmethod
    def validate_ai_analysis(data: Dict[str, Any]) -> ValidationResult:
        """验证AI分析结果"""
        result = ValidationResult()
        
        # 检查健康评分
        if 'health_score' in data:
            score = data['health_score']
            if not isinstance(score, (int, float)):
                result.add_error("健康评分必须是数字")
            elif not 0 <= score <= 100:
                result.add_error("健康评分必须在0-100之间")
                
        # 检查安全等级
        if 'safety_level' in data:
            level = data['safety_level']
            valid_levels = ['safe', 'warning', 'danger']
            if level not in valid_levels:
                result.add_error(f"安全等级必须是以下之一: {valid_levels}")
                
        # 检查建议内容
        if 'recommendations' in data:
            recommendations = data['recommendations']
            if not isinstance(recommendations, list):
                result.add_error("建议内容必须是列表格式")
            elif len(recommendations) == 0:
                result.add_warning("建议内容为空")
            else:
                for i, rec in enumerate(recommendations):
                    if not isinstance(rec, str):
                        result.add_error(f"建议内容第{i+1}项必须是字符串")
                    elif len(rec.strip()) == 0:
                        result.add_error(f"建议内容第{i+1}项不能为空")
                        
        return result

class APIResponseValidator:
    """API响应验证器"""
    
    @staticmethod
    def validate_response_structure(data: Dict[str, Any], required_fields: List[str] = None) -> ValidationResult:
        """验证API响应结构"""
        result = ValidationResult()
        
        if not isinstance(data, dict):
            result.add_error("响应数据必须是字典格式")
            return result
            
        # 检查必需字段
        if required_fields:
            for field in required_fields:
                if field not in data:
                    result.add_error(f"响应缺少必需字段: {field}")
                    
        # 检查标准响应字段
        if 'success' in data and not isinstance(data['success'], bool):
            result.add_error("success字段必须是布尔值")
            
        if 'message' in data and not isinstance(data['message'], str):
            result.add_error("message字段必须是字符串")
            
        if 'timestamp' in data:
            timestamp = data['timestamp']
            if isinstance(timestamp, str):
                try:
                    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    result.add_error("timestamp格式无效")
                    
        return result

class DataSanitizer:
    """数据清洗器"""
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """清洗文本数据"""
        if not isinstance(text, str):
            return str(text)
            
        # 移除多余空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除特殊控制字符
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text
    
    @staticmethod
    def sanitize_nutrition_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗营养数据"""
        sanitized = {}
        
        for key, value in data.items():
            if value is None:
                continue
                
            # 转换为数字
            try:
                if isinstance(value, str):
                    # 移除非数字字符（保留小数点）
                    clean_value = re.sub(r'[^\d.]', '', value)
                    if clean_value:
                        value = float(clean_value)
                    else:
                        continue
                        
                # 确保为非负数
                if isinstance(value, (int, float)) and value >= 0:
                    sanitized[key] = round(float(value), 2)
                    
            except (ValueError, TypeError):
                logger.warning(f"无法转换营养数据 {key}: {value}")
                continue
                
        return sanitized

class ComprehensiveValidator:
    """综合验证器"""
    
    @staticmethod
    def validate_detection_result(data: Dict[str, Any]) -> ValidationResult:
        """验证完整的检测结果"""
        result = ValidationResult()
        
        # 验证基本结构
        structure_result = APIResponseValidator.validate_response_structure(
            data, ['id', 'status', 'detection_type']
        )
        if not structure_result.is_valid:
            result.errors.extend(structure_result.errors)
            result.is_valid = False
        result.warnings.extend(structure_result.warnings)
        
        # 验证OCR结果
        if 'ocr_result' in data and data['ocr_result']:
            ocr_result = OCRDataValidator.validate_ocr_result(data['ocr_result'])
            if not ocr_result.is_valid:
                result.errors.extend([f"OCR验证: {error}" for error in ocr_result.errors])
                result.is_valid = False
            result.warnings.extend([f"OCR警告: {warning}" for warning in ocr_result.warnings])
            
        # 验证AI分析结果
        if 'ai_analysis' in data and data['ai_analysis']:
            ai_result = AIAnalysisValidator.validate_ai_analysis(data['ai_analysis'])
            if not ai_result.is_valid:
                result.errors.extend([f"AI分析验证: {error}" for error in ai_result.errors])
                result.is_valid = False
            result.warnings.extend([f"AI分析警告: {warning}" for warning in ai_result.warnings])
            
        return result
    
    @staticmethod
    def validate_and_sanitize(data: Dict[str, Any], data_type: str = 'detection') -> tuple[Dict[str, Any], ValidationResult]:
        """验证并清洗数据"""
        # 首先进行数据清洗
        sanitized_data = data.copy()
        
        # 清洗文本字段
        text_fields = ['product_name', 'description', 'user_notes']
        for field in text_fields:
            if field in sanitized_data and sanitized_data[field]:
                sanitized_data[field] = DataSanitizer.sanitize_text(sanitized_data[field])
                
        # 清洗营养数据
        if 'nutrition_data' in sanitized_data and sanitized_data['nutrition_data']:
            sanitized_data['nutrition_data'] = DataSanitizer.sanitize_nutrition_data(
                sanitized_data['nutrition_data']
            )
            
        # 进行验证
        if data_type == 'detection':
            validation_result = ComprehensiveValidator.validate_detection_result(sanitized_data)
        else:
            validation_result = APIResponseValidator.validate_response_structure(sanitized_data)
            
        return sanitized_data, validation_result

# 导出主要类和函数
__all__ = [
    'ValidationResult',
    'OCRDataValidator',
    'NutritionDataValidator', 
    'AIAnalysisValidator',
    'APIResponseValidator',
    'DataSanitizer',
    'ComprehensiveValidator'
]