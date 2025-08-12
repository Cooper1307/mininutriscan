from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from typing import Generator
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'mininutriscan')}"
)

# 创建数据库引擎
# 如果是SQLite，添加特殊配置
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,  # SQLite特有配置
        },
        echo=os.getenv("DB_ECHO", "false").lower() == "true"  # 是否打印SQL语句
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=os.getenv("DB_ECHO", "false").lower() == "true"  # 是否打印SQL语句
    )

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 创建基础模型类
Base = declarative_base()

# 数据库依赖注入函数
def get_db() -> Generator:
    """
    获取数据库会话
    
    这个函数用于FastAPI的依赖注入系统，
    确保每个请求都有独立的数据库会话，
    并在请求结束后正确关闭会话。
    
    Yields:
        数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建所有数据库表
def create_tables():
    """
    创建所有数据库表
    
    这个函数会根据模型定义创建所有必要的数据库表。
    通常在应用启动时调用。
    """
    try:
        # 导入所有模型以确保它们被注册到Base.metadata
        from app.models import User, Detection, Report, Volunteer, EducationContent
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功")
        
    except Exception as e:
        print(f"创建数据库表失败: {e}")
        raise

# 删除所有数据库表（谨慎使用）
def drop_tables():
    """
    删除所有数据库表
    
    警告：这个函数会删除所有数据！
    仅在开发环境或重置数据库时使用。
    """
    try:
        Base.metadata.drop_all(bind=engine)
        print("数据库表删除成功")
    except Exception as e:
        print(f"删除数据库表失败: {e}")
        raise

# 检查数据库连接
def check_database_connection() -> bool:
    """
    检查数据库连接是否正常
    
    Returns:
        bool: 连接成功返回True，失败返回False
    """
    try:
        # 导入text函数用于SQL语句包装
        from sqlalchemy import text
        
        # 尝试执行简单查询
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("数据库连接正常")
        return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False

# 获取数据库信息
def get_database_info() -> dict:
    """
    获取数据库配置信息
    
    Returns:
        dict: 数据库配置信息
    """
    return {
        "database_url": DATABASE_URL.replace(os.getenv('DB_PASSWORD', 'password'), '***') if os.getenv('DB_PASSWORD') else DATABASE_URL,
        "engine_info": str(engine.url),
        "pool_size": getattr(engine.pool, 'size', 'N/A'),
        "echo_enabled": engine.echo
    }