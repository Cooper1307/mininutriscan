@echo off
REM 社区食安AI小卫士 - 服务启动脚本
REM 一键启动所有必要的服务

chcp 65001 >nul
echo ========================================
echo    社区食安AI小卫士 - 服务启动
echo ========================================
echo.

REM 检查Python环境
echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python环境正常

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 🔍 激活虚拟环境...
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
) else (
    echo ⚠️  未找到虚拟环境，使用系统Python
)

REM 检查依赖包
echo 🔍 检查项目依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo ❌ 项目依赖未安装
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)
echo ✅ 项目依赖正常

REM 检查配置文件
echo 🔍 检查配置文件...
if not exist ".env" (
    echo ❌ 配置文件 .env 不存在
    echo 请参考 配置指南.md 完成配置
    pause
    exit /b 1
)
echo ✅ 配置文件存在

REM 启动Redis (可选)
echo.
echo 🔧 Redis服务 (可选，提升性能)
set /p start_redis="是否启动Redis服务? (y/n): "
if /i "%start_redis%"=="y" (
    echo 🚀 启动Redis服务...
    start "Redis Server" cmd /c "start_redis.bat"
    timeout /t 3 >nul
    echo ✅ Redis服务启动中...
) else (
    echo ⚠️  跳过Redis服务 (不影响核心功能)
)

REM 启动FastAPI服务
echo.
echo 🚀 启动FastAPI后端服务...
echo 📍 服务地址: http://127.0.0.1:8000
echo 📚 API文档: http://127.0.0.1:8000/docs
echo 🔧 调试模式: 开启
echo.
echo ⚠️  请保持此窗口打开，关闭将停止服务
echo 💡 按 Ctrl+C 可停止服务
echo.

REM 启动主服务
python main.py

REM 服务停止后的清理
echo.
echo 🛑 服务已停止
echo 感谢使用社区食安AI小卫士！
pause