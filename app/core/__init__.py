# app/core/__init__.py - 核心模块初始化文件
# 导出核心配置和数据库连接

from .config import settings
from .database import (
    get_db,
    get_redis,
    cache_manager,
    init_database,
    get_db_status
)

__all__ = [
    "settings",
    "get_db",
    "get_redis",
    "cache_manager",
    "init_database",
    "get_db_status"
]