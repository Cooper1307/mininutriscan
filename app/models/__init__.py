# app/models/__init__.py
# 数据库模型模块初始化文件

from .user import User
from .detection import Detection
from .report import Report
from .volunteer import Volunteer
from .education import EducationContent

# 导出所有模型类
__all__ = [
    "User",
    "Detection", 
    "Report",
    "Volunteer",
    "EducationContent"
]