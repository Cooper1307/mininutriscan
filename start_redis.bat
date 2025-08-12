@echo off
REM Redis服务启动脚本
REM 用于启动本地Redis服务

echo ========================================
echo    Redis服务启动脚本
echo    社区食安AI小卫士项目
echo ========================================
echo.

REM 检查Redis是否已安装
if not exist "Redis-x64-5.0.14.1.zip" (
    echo ❌ 未找到Redis安装包
    echo 请确保Redis-x64-5.0.14.1.zip文件在项目根目录
    pause
    exit /b 1
)

REM 检查是否已解压
if not exist "redis-server.exe" (
    echo 📦 正在解压Redis安装包...
    powershell -command "Expand-Archive -Path 'Redis-x64-5.0.14.1.zip' -DestinationPath '.' -Force"
    if errorlevel 1 (
        echo ❌ Redis解压失败
        pause
        exit /b 1
    )
    echo ✅ Redis解压完成
)

REM 启动Redis服务器
echo 🚀 正在启动Redis服务器...
echo 端口: 6379
echo 按 Ctrl+C 停止服务
echo.

redis-server.exe

if errorlevel 1 (
    echo ❌ Redis启动失败
    echo 可能原因:
    echo   1. 端口6379已被占用
    echo   2. Redis配置文件有误
    echo   3. 权限不足
    pause
    exit /b 1
)

echo ✅ Redis服务已停止
pause