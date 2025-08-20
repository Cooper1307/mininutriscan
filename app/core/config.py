# app/core/config.py - 应用核心配置
# 管理数据库连接、Redis连接、API密钥等配置

import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings:
    """
    应用配置类
    从环境变量中读取配置信息
    """
    
    # ===========================================
    # 应用基本配置
    # ===========================================
    APP_NAME: str = "MiniNutriScan"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key")
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # ===========================================
    # 数据库配置
    # ===========================================
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "mininutriscan")
    
    @property
    def database_url(self) -> str:
        """
        构建数据库连接URL
        优先使用DATABASE_URL环境变量，否则根据分项构建
        """
        if os.getenv("DATABASE_URL"):
            return os.getenv("DATABASE_URL")
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # ===========================================
    # Redis配置
    # ===========================================
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    @property
    def redis_url(self) -> str:
        """
        构建Redis连接URL
        """
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ===========================================
    # JWT配置
    # ===========================================
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # ===========================================
    # 会话管理配置
    # ===========================================
    SESSION_EXPIRE_MINUTES: int = int(os.getenv("SESSION_EXPIRE_MINUTES", "60"))  # 会话过期时间（分钟）
    MAX_SESSIONS_PER_USER: int = int(os.getenv("MAX_SESSIONS_PER_USER", "5"))  # 每个用户最大会话数
    SESSION_CLEANUP_INTERVAL: int = int(os.getenv("SESSION_CLEANUP_INTERVAL", "300"))  # 会话清理间隔（秒）
    
    # ===========================================
    # AI服务配置
    # ===========================================
    # Qwen3 API配置
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    QWEN_API_URL: str = os.getenv("QWEN_API_URL", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
    QWEN_MODEL: str = os.getenv("QWEN_MODEL", "qwen-turbo")
    
    # ===========================================
    # OCR服务配置
    # ===========================================
    # 腾讯云OCR
    TENCENT_SECRET_ID: str = os.getenv("TENCENT_SECRET_ID", "")
    TENCENT_SECRET_KEY: str = os.getenv("TENCENT_SECRET_KEY", "")
    TENCENT_REGION: str = os.getenv("TENCENT_REGION", "ap-beijing")
    
    # 阿里云OCR
    ALIBABA_ACCESS_KEY_ID: str = os.getenv("ALIBABA_ACCESS_KEY_ID", "")
    ALIBABA_ACCESS_KEY_SECRET: str = os.getenv("ALIBABA_ACCESS_KEY_SECRET", "")
    ALIBABA_REGION: str = os.getenv("ALIBABA_REGION", "cn-shanghai")
    
    # ===========================================
    # 微信小程序配置
    # ===========================================
    WECHAT_APP_ID: str = os.getenv("WECHAT_APP_ID", "")
    WECHAT_APP_SECRET: str = os.getenv("WECHAT_APP_SECRET", "")
    
    # ===========================================
    # 文件上传配置
    # ===========================================
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/jpg"]
    
    # ===========================================
    # 日志配置
    # ===========================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    
    # ===========================================
    # 验证配置
    # ===========================================
    def validate_config(self) -> dict:
        """
        验证配置的完整性
        返回配置状态报告
        """
        issues = []
        warnings = []
        
        # 检查必需配置
        if not self.DB_PASSWORD:
            issues.append("数据库密码未配置")
        
        if not self.JWT_SECRET_KEY or self.JWT_SECRET_KEY == "your-jwt-secret-key":
            issues.append("JWT密钥未正确配置")
        
        # 检查可选但重要的配置
        if not self.QWEN_API_KEY:
            warnings.append("Qwen3 API密钥未配置，AI功能将不可用")
        
        if not (self.TENCENT_SECRET_ID and self.TENCENT_SECRET_KEY) and not (self.ALIBABA_ACCESS_KEY_ID and self.ALIBABA_ACCESS_KEY_SECRET):
            warnings.append("OCR服务未配置，图片识别功能将不可用")
        
        if not (self.WECHAT_APP_ID and self.WECHAT_APP_SECRET):
            warnings.append("微信小程序配置未完成，微信登录将不可用")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def get_config_summary(self) -> dict:
        """
        获取配置摘要（隐藏敏感信息）
        """
        return {
            "app": {
                "name": self.APP_NAME,
                "version": self.APP_VERSION,
                "debug": self.DEBUG,
                "host": self.HOST,
                "port": self.PORT
            },
            "database": {
                "host": self.DB_HOST,
                "port": self.DB_PORT,
                "name": self.DB_NAME,
                "user": self.DB_USER,
                "password_set": bool(self.DB_PASSWORD)
            },
            "redis": {
                "host": self.REDIS_HOST,
                "port": self.REDIS_PORT,
                "db": self.REDIS_DB,
                "password_set": bool(self.REDIS_PASSWORD)
            },
            "services": {
                "qwen_configured": bool(self.QWEN_API_KEY),
                "tencent_ocr_configured": bool(self.TENCENT_SECRET_ID and self.TENCENT_SECRET_KEY),
                "alibaba_ocr_configured": bool(self.ALIBABA_ACCESS_KEY_ID and self.ALIBABA_ACCESS_KEY_SECRET),
                "wechat_configured": bool(self.WECHAT_APP_ID and self.WECHAT_APP_SECRET)
            },
            "security": {
                "jwt_configured": bool(self.JWT_SECRET_KEY and self.JWT_SECRET_KEY != "your-jwt-secret-key"),
                "secret_key_configured": bool(self.SECRET_KEY and self.SECRET_KEY != "your-super-secret-key")
            }
        }

# 创建全局配置实例
settings = Settings()

# 提供get_settings函数用于依赖注入
def get_settings() -> Settings:
    """
    获取配置实例
    用于FastAPI的依赖注入
    """
    return settings

# 配置验证
config_validation = settings.validate_config()
if not config_validation["valid"]:
    print("⚠️  配置验证失败:")
    for issue in config_validation["issues"]:
        print(f"   ❌ {issue}")

if config_validation["warnings"]:
    print("⚠️  配置警告:")
    for warning in config_validation["warnings"]:
        print(f"   ⚠️  {warning}")