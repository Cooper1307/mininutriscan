@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ===============================================
echo   社区食安AI小卫士 - 开发环境快速设置
echo ===============================================
echo.

REM 检查Python是否安装
echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%

REM 检查是否在项目目录
if not exist "main.py" (
    echo ❌ 请在项目根目录运行此脚本
    echo 当前目录: %CD%
    echo.
    pause
    exit /b 1
)

echo ✅ 项目目录确认

REM 创建虚拟环境（如果不存在）
echo.
echo 🔧 设置虚拟环境...
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
) else (
    echo ✅ 虚拟环境已存在
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活

REM 升级pip
echo.
echo 📦 更新包管理器...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ⚠️  pip更新失败，继续安装依赖
) else (
    echo ✅ pip更新成功
)

REM 安装依赖
echo.
echo 📦 安装项目依赖...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        echo 请检查网络连接或手动安装
        pause
        exit /b 1
    )
    echo ✅ 依赖安装成功
) else (
    echo ❌ requirements.txt文件不存在
    echo 手动安装核心依赖...
    pip install fastapi uvicorn sqlalchemy psycopg2-binary redis python-dotenv pydantic requests
    if errorlevel 1 (
        echo ❌ 核心依赖安装失败
        pause
        exit /b 1
    )
    echo ✅ 核心依赖安装成功
)

REM 检查.env文件
echo.
echo 🔧 检查配置文件...
if not exist ".env" (
    echo ⚠️  .env文件不存在，创建示例配置...
    echo # 数据库配置 > .env
    echo DATABASE_URL=postgresql://postgres:123456@localhost:5432/mininutriscan >> .env
    echo. >> .env
    echo # JWT配置 >> .env
    echo SECRET_KEY=your-secret-key-here >> .env
    echo ALGORITHM=HS256 >> .env
    echo ACCESS_TOKEN_EXPIRE_MINUTES=30 >> .env
    echo. >> .env
    echo # AI服务配置 >> .env
    echo QWEN_API_KEY=your-qwen-api-key-here >> .env
    echo QWEN_API_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation >> .env
    echo QWEN_MODEL=qwen-turbo >> .env
    echo. >> .env
    echo # 微信小程序配置 >> .env
    echo WECHAT_APP_ID=your-wechat-app-id-here >> .env
    echo WECHAT_APP_SECRET=your-wechat-app-secret-here >> .env
    echo. >> .env
    echo # Redis配置 >> .env
    echo REDIS_URL=redis://localhost:6379/0 >> .env
    echo REDIS_HOST=localhost >> .env
    echo REDIS_PORT=6379 >> .env
    echo REDIS_DB=0 >> .env
    echo REDIS_PASSWORD= >> .env
    echo.
    echo ✅ .env示例文件已创建
    echo ⚠️  请编辑.env文件，填入真实的配置信息
) else (
    echo ✅ .env文件已存在
)

REM 创建数据库（如果需要）
echo.
echo 🗄️  检查数据库...
echo 尝试连接数据库...
python -c "from app.database import check_database_connection; print('✅ 数据库连接成功' if check_database_connection() else '❌ 数据库连接失败')" 2>nul
if errorlevel 1 (
    echo ⚠️  数据库连接检查失败，请确保PostgreSQL已安装并运行
    echo 数据库配置信息请查看.env文件
)

REM 运行项目状态检查
echo.
echo 🔍 运行项目状态检查...
if exist "检查项目状态.py" (
    python 检查项目状态.py
) else (
    echo ⚠️  项目状态检查脚本不存在
)

echo.
echo ===============================================
echo 🎉 开发环境设置完成！
echo ===============================================
echo.
echo 📋 下一步操作:
echo    1. 编辑 .env 文件，配置API密钥
echo    2. 确保PostgreSQL和Redis服务运行
echo    3. 运行 启动服务.bat 启动后端
echo    4. 使用微信开发者工具打开小程序项目
echo.
echo 📚 参考文档:
echo    - 配置指南.md
echo    - 小程序开发指南.md
echo    - 快速使用指南.md
echo.
pause