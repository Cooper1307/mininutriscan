# app/core/database.py - 数据库连接管理
# 管理PostgreSQL和Redis连接，提供数据库会话

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import redis
from typing import Generator
import logging
from .config import settings

# 配置日志
logger = logging.getLogger(__name__)

# ===========================================
# PostgreSQL 数据库配置
# ===========================================

# 创建数据库引擎
# echo=True 在开发模式下显示SQL语句
engine = create_engine(
    settings.database_url,
    echo=settings.DEBUG,  # 开发模式下显示SQL
    pool_pre_ping=True,   # 连接前检查连接是否有效
    pool_recycle=3600,    # 1小时后回收连接
    pool_size=10,         # 连接池大小
    max_overflow=20       # 最大溢出连接数
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 创建基础模型类
Base = declarative_base()

# 元数据对象，用于表结构管理
metadata = MetaData()

def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    这是一个依赖注入函数，用于FastAPI的Depends
    
    使用方法:
    @app.get("/users/")
    def read_users(db: Session = Depends(get_db)):
        return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """
    创建所有数据库表
    在应用启动时调用
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"创建数据库表失败: {e}")
        raise

def test_db_connection() -> bool:
    """
    测试数据库连接
    返回连接是否成功
    """
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("数据库连接测试成功")
            return True
    except Exception as e:
        logger.error(f"数据库连接测试失败: {e}")
        return False

# ===========================================
# Redis 连接配置
# ===========================================

# 创建Redis连接池
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,  # 自动解码响应为字符串
    max_connections=20,     # 最大连接数
    retry_on_timeout=True   # 超时重试
)

# 创建Redis客户端
redis_client = redis.Redis(connection_pool=redis_pool)

def get_redis() -> redis.Redis:
    """
    获取Redis客户端
    这是一个依赖注入函数，用于FastAPI的Depends
    
    使用方法:
    @app.get("/cache/")
    def read_cache(redis_db: redis.Redis = Depends(get_redis)):
        return redis_db.get("key")
    """
    return redis_client

def test_redis_connection() -> bool:
    """
    测试Redis连接
    返回连接是否成功
    """
    try:
        response = redis_client.ping()
        if response:
            logger.info("Redis连接测试成功")
            return True
        else:
            logger.error("Redis连接测试失败: 无响应")
            return False
    except Exception as e:
        logger.error(f"Redis连接测试失败: {e}")
        return False

# ===========================================
# 缓存工具函数
# ===========================================

class CacheManager:
    """
    缓存管理器
    提供常用的缓存操作方法
    """
    
    def __init__(self, redis_client: redis.Redis = redis_client):
        self.redis = redis_client
    
    def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒），默认1小时
        
        Returns:
            是否设置成功
        """
        try:
            return self.redis.setex(key, expire, value)
        except Exception as e:
            logger.error(f"设置缓存失败 {key}: {e}")
            return False
    
    def get(self, key: str) -> str:
        """
        获取缓存
        
        Args:
            key: 缓存键
        
        Returns:
            缓存值，不存在返回None
        """
        try:
            return self.redis.get(key)
        except Exception as e:
            logger.error(f"获取缓存失败 {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
        
        Returns:
            是否删除成功
        """
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"删除缓存失败 {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 缓存键
        
        Returns:
            是否存在
        """
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            logger.error(f"检查缓存存在性失败 {key}: {e}")
            return False
    
    def set_hash(self, key: str, mapping: dict, expire: int = 3600) -> bool:
        """
        设置哈希缓存
        
        Args:
            key: 缓存键
            mapping: 哈希字典
            expire: 过期时间（秒）
        
        Returns:
            是否设置成功
        """
        try:
            pipe = self.redis.pipeline()
            pipe.hset(key, mapping=mapping)
            pipe.expire(key, expire)
            pipe.execute()
            return True
        except Exception as e:
            logger.error(f"设置哈希缓存失败 {key}: {e}")
            return False
    
    def get_hash(self, key: str) -> dict:
        """
        获取哈希缓存
        
        Args:
            key: 缓存键
        
        Returns:
            哈希字典，不存在返回空字典
        """
        try:
            return self.redis.hgetall(key)
        except Exception as e:
            logger.error(f"获取哈希缓存失败 {key}: {e}")
            return {}
    
    def increment(self, key: str, amount: int = 1, expire: int = 3600) -> int:
        """
        递增计数器
        
        Args:
            key: 缓存键
            amount: 递增量
            expire: 过期时间（秒）
        
        Returns:
            递增后的值
        """
        try:
            pipe = self.redis.pipeline()
            pipe.incrby(key, amount)
            pipe.expire(key, expire)
            result = pipe.execute()
            return result[0]
        except Exception as e:
            logger.error(f"递增计数器失败 {key}: {e}")
            return 0

# 创建全局缓存管理器实例
cache_manager = CacheManager()

# ===========================================
# 数据库初始化函数
# ===========================================

def init_database():
    """
    初始化数据库
    在应用启动时调用
    """
    logger.info("开始初始化数据库...")
    
    # 测试数据库连接
    if not test_db_connection():
        raise Exception("数据库连接失败，请检查配置")
    
    # 测试Redis连接
    if not test_redis_connection():
        logger.warning("Redis连接失败，缓存功能将不可用")
    
    # 创建数据库表
    create_tables()
    
    logger.info("数据库初始化完成")

def get_db_status() -> dict:
    """
    获取数据库状态
    """
    return {
        "postgresql": {
            "connected": test_db_connection(),
            "url": settings.database_url.replace(settings.DB_PASSWORD, "***") if settings.DB_PASSWORD else settings.database_url
        },
        "redis": {
            "connected": test_redis_connection(),
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
            "db": settings.REDIS_DB
        }
    }