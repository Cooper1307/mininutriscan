# app/core/security.py - 安全增强模块
# 提供输入验证、SQL注入防护和其他安全功能

import re
import html
from typing import Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

# 配置日志
logger = logging.getLogger(__name__)

class InputValidator:
    """
    输入验证器
    提供各种输入验证和清理功能
    """
    
    # 危险的SQL关键字模式
    SQL_INJECTION_PATTERNS = [
        r"(\b(DROP|DELETE|INSERT|UPDATE|UNION|SELECT)\b)",
        r"(--|#|/\*|\*/)",
        r"(';|'\s*OR\s*'|'\s*AND\s*')",
        r"(\bEXEC\b|\bEXECUTE\b)",
        r"(\bSP_\w+)",
        r"(\bXP_\w+)",
        r"(\bSYS\w+)",
        r"(\bINFORMATION_SCHEMA\b)"
    ]
    
    # XSS攻击模式
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>"
    ]
    
    @classmethod
    def validate_search_input(cls, search_term: str, max_length: int = 100) -> str:
        """
        验证和清理搜索输入
        
        Args:
            search_term: 搜索词
            max_length: 最大长度
            
        Returns:
            清理后的搜索词
            
        Raises:
            ValueError: 输入包含危险内容时抛出异常
        """
        if not search_term:
            return ""
        
        # 长度检查
        if len(search_term) > max_length:
            raise ValueError(f"搜索词长度不能超过{max_length}个字符")
        
        # SQL注入检查
        cls._check_sql_injection(search_term)
        
        # XSS检查
        cls._check_xss(search_term)
        
        # 清理输入
        cleaned = cls._clean_input(search_term)
        
        return cleaned
    
    @classmethod
    def validate_user_input(cls, user_input: str, field_name: str = "输入", max_length: int = 255) -> str:
        """
        验证和清理用户输入
        
        Args:
            user_input: 用户输入
            field_name: 字段名称（用于错误消息）
            max_length: 最大长度
            
        Returns:
            清理后的输入
            
        Raises:
            ValueError: 输入包含危险内容时抛出异常
        """
        if not user_input:
            return ""
        
        # 长度检查
        if len(user_input) > max_length:
            raise ValueError(f"{field_name}长度不能超过{max_length}个字符")
        
        # SQL注入检查
        cls._check_sql_injection(user_input, field_name)
        
        # XSS检查
        cls._check_xss(user_input, field_name)
        
        # 清理输入
        cleaned = cls._clean_input(user_input)
        
        return cleaned
    
    @classmethod
    def _check_sql_injection(cls, input_text: str, field_name: str = "输入"):
        """
        检查SQL注入攻击
        
        Args:
            input_text: 输入文本
            field_name: 字段名称
            
        Raises:
            ValueError: 检测到SQL注入攻击时抛出异常
        """
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_text, re.IGNORECASE):
                logger.warning(f"检测到潜在的SQL注入攻击: {field_name} = {input_text[:50]}...")
                raise ValueError(f"{field_name}包含不安全的内容")
    
    @classmethod
    def _check_xss(cls, input_text: str, field_name: str = "输入"):
        """
        检查XSS攻击
        
        Args:
            input_text: 输入文本
            field_name: 字段名称
            
        Raises:
            ValueError: 检测到XSS攻击时抛出异常
        """
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, input_text, re.IGNORECASE):
                logger.warning(f"检测到潜在的XSS攻击: {field_name} = {input_text[:50]}...")
                raise ValueError(f"{field_name}包含不安全的内容")
    
    @classmethod
    def _clean_input(cls, input_text: str) -> str:
        """
        清理输入文本
        
        Args:
            input_text: 输入文本
            
        Returns:
            清理后的文本
        """
        # HTML转义
        cleaned = html.escape(input_text)
        
        # 移除多余的空白字符
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """
        验证邮箱格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            验证结果
        """
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """
        验证手机号格式
        
        Args:
            phone: 手机号
            
        Returns:
            验证结果
        """
        if not phone:
            return False
        
        # 中国手机号格式
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))

class SafeQueryBuilder:
    """
    安全查询构建器
    提供安全的数据库查询构建功能
    """
    
    @staticmethod
    def build_search_query(db: Session, model, search_fields: List[str], search_term: str):
        """
        构建安全的搜索查询
        
        Args:
            db: 数据库会话
            model: 数据模型
            search_fields: 搜索字段列表
            search_term: 搜索词
            
        Returns:
            查询对象
        """
        # 验证搜索输入
        clean_search_term = InputValidator.validate_search_input(search_term)
        
        if not clean_search_term:
            return db.query(model)
        
        # 构建安全的搜索模式
        search_pattern = f"%{clean_search_term}%"
        
        # 构建查询条件
        from sqlalchemy import or_
        conditions = []
        
        for field_name in search_fields:
            if hasattr(model, field_name):
                field = getattr(model, field_name)
                conditions.append(field.ilike(search_pattern))
        
        if conditions:
            return db.query(model).filter(or_(*conditions))
        else:
            return db.query(model)
    
    @staticmethod
    def execute_safe_raw_query(db: Session, query_template: str, params: dict) -> Any:
        """
        执行安全的原始SQL查询
        
        Args:
            db: 数据库会话
            query_template: 查询模板（使用参数占位符）
            params: 查询参数
            
        Returns:
            查询结果
        """
        # 验证查询模板
        if not query_template or not isinstance(query_template, str):
            raise ValueError("查询模板不能为空")
        
        # 验证参数
        if params:
            for key, value in params.items():
                if isinstance(value, str):
                    # 验证字符串参数
                    InputValidator.validate_user_input(value, f"参数{key}")
        
        try:
            # 使用参数化查询
            result = db.execute(text(query_template), params or {})
            return result
        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            raise

class SecurityAudit:
    """
    安全审计工具
    记录和监控安全相关事件
    """
    
    @staticmethod
    def log_security_event(event_type: str, details: dict, user_id: Optional[int] = None):
        """
        记录安全事件
        
        Args:
            event_type: 事件类型
            details: 事件详情
            user_id: 用户ID（可选）
        """
        logger.warning(f"安全事件 [{event_type}]: {details}, 用户ID: {user_id}")
    
    @staticmethod
    def log_failed_login(username: str, ip_address: str):
        """
        记录登录失败事件
        
        Args:
            username: 用户名
            ip_address: IP地址
        """
        SecurityAudit.log_security_event(
            "LOGIN_FAILED",
            {"username": username, "ip_address": ip_address}
        )
    
    @staticmethod
    def log_suspicious_activity(activity_type: str, details: dict, user_id: Optional[int] = None):
        """
        记录可疑活动
        
        Args:
            activity_type: 活动类型
            details: 活动详情
            user_id: 用户ID（可选）
        """
        SecurityAudit.log_security_event(
            f"SUSPICIOUS_{activity_type}",
            details,
            user_id
        )

# 便捷函数
def validate_and_clean_input(user_input: str, field_name: str = "输入", max_length: int = 255) -> str:
    """
    验证和清理用户输入的便捷函数
    
    Args:
        user_input: 用户输入
        field_name: 字段名称
        max_length: 最大长度
        
    Returns:
        清理后的输入
    """
    return InputValidator.validate_user_input(user_input, field_name, max_length)

def validate_search_term(search_term: str) -> str:
    """
    验证搜索词的便捷函数
    
    Args:
        search_term: 搜索词
        
    Returns:
        清理后的搜索词
    """
    return InputValidator.validate_search_input(search_term)

def build_safe_search_query(db: Session, model, search_fields: List[str], search_term: str):
    """
    构建安全搜索查询的便捷函数
    
    Args:
        db: 数据库会话
        model: 数据模型
        search_fields: 搜索字段列表
        search_term: 搜索词
        
    Returns:
        查询对象
    """
    return SafeQueryBuilder.build_search_query(db, model, search_fields, search_term)