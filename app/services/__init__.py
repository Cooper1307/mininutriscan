# app/services/__init__.py
# 服务层模块初始化文件

"""
服务层模块
包含各种外部服务的集成，如AI服务、OCR服务、微信服务等
"""

from .ai_service import AIService
from .ocr_service import OCRService
from .wechat_service import WeChatService

__all__ = [
    "AIService",
    "OCRService", 
    "WeChatService"
]