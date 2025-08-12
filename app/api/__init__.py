# app/api/__init__.py
# API路由模块初始化文件

from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .detection import router as detection_router
from .reports import router as reports_router
from .education import router as education_router
from .volunteers import router as volunteers_router

# 创建主API路由器
api_router = APIRouter(prefix="/api/v1")

# 注册各个子路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(users_router, prefix="/users", tags=["用户管理"])
api_router.include_router(detection_router, prefix="/detection", tags=["营养检测"])
api_router.include_router(reports_router, prefix="/reports", tags=["报告系统"])
api_router.include_router(education_router, prefix="/education", tags=["教育内容"])
api_router.include_router(volunteers_router, prefix="/volunteers", tags=["志愿者"])

__all__ = ["api_router"]