# main.py - MiniNutriScan FastAPI应用主入口
# 这是整个应用的启动文件，配置FastAPI实例和路由

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
from app.database import engine, Base, check_database_connection
from app.api import api_router

# 加载环境变量
load_dotenv()

# 检查数据库连接（不再自动创建表，使用Alembic迁移）
print("检查数据库连接...")
if check_database_connection():
    print("数据库连接成功")
else:
    print("数据库连接失败，请检查配置")

# 创建FastAPI应用实例
app = FastAPI(
    title="MiniNutriScan API",
    description="智能营养扫描小程序后端API",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI文档地址
    redoc_url="/redoc"  # ReDoc文档地址
)

# 配置CORS中间件
# 允许微信小程序和开发环境访问API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://servicewechat.com",  # 微信小程序域名
        "http://localhost:3000",      # 本地开发前端
        "http://127.0.0.1:3000",      # 本地开发前端
        "http://localhost:8080",      # 可能的前端端口
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 静态文件服务（用于提供上传的图片等）
# 创建uploads目录如果不存在
uploads_dir = "uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# 小程序静态资源服务（用于提供小程序的图片资源）
miniprogram_assets_dir = "miniprogram/assets"
if os.path.exists(miniprogram_assets_dir):
    app.mount("/assets", StaticFiles(directory=miniprogram_assets_dir), name="assets")

# 根路径 - 健康检查接口
@app.get("/")
async def root():
    """
    根路径健康检查接口
    返回API基本信息和状态
    """
    return {
        "message": "MiniNutriScan API 正在运行",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# 健康检查接口
@app.get("/health")
async def health_check():
    """
    详细的健康检查接口
    检查各个服务的连接状态
    """
    health_status = {
        "api": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "timestamp": None
    }
    
    try:
        # 检查数据库连接
        if check_database_connection():
            health_status["database"] = "healthy"
        else:
            health_status["database"] = "connection failed"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
    
    try:
        # 检查Redis连接
        # TODO: 添加Redis连接检查
        health_status["redis"] = "healthy"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
    
    # 添加时间戳
    from datetime import datetime
    health_status["timestamp"] = datetime.now().isoformat()
    
    return health_status

# API版本信息
@app.get("/api/v1/info")
async def api_info():
    """
    API版本和功能信息
    """
    return {
        "name": "MiniNutriScan API",
        "version": "1.0.0",
        "description": "智能营养扫描小程序后端API",
        "features": [
            "用户认证与管理",
            "食物图片识别",
            "营养成分分析",
            "AI营养建议",
            "扫描历史记录",
            "个人营养档案"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "auth": "/api/v1/auth",
            "scan": "/api/v1/scan",
            "nutrition": "/api/v1/nutrition",
            "user": "/api/v1/user"
        }
    }

# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    HTTP异常处理器
    统一处理HTTP异常并返回标准格式
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    通用异常处理器
    处理未捕获的异常
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "内部服务器错误",
            "status_code": 500,
            "path": str(request.url),
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None
        }
    )

# 注册API路由
# 使用统一的API路由器，包含所有子路由
app.include_router(api_router)

if __name__ == "__main__":
    # 开发环境启动配置
    # 生产环境建议使用 gunicorn 或其他WSGI服务器
    
    # 从环境变量获取配置
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print("🚀 启动 MiniNutriScan API 服务器")
    print(f"📍 地址: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,  # 开发模式下启用热重载
        log_level="info" if not debug else "debug"
    )