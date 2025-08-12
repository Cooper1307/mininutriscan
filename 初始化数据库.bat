@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo 🛡️ 社区食安AI小卫士 - 数据库初始化工具
echo ================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    echo.
    echo 💡 安装建议:
    echo    1. 访问 https://www.python.org/downloads/
    echo    2. 下载并安装Python 3.8或更高版本
    echo    3. 安装时勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM 检查是否在项目根目录
if not exist "main.py" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    echo 当前目录: %CD%
    echo.
    echo 💡 解决方法:
    echo    1. 打开项目根目录（包含main.py的目录）
    echo    2. 在该目录下运行此脚本
    echo.
    pause
    exit /b 1
)

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 🔄 激活虚拟环境...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo ❌ 虚拟环境激活失败
        echo.
        echo 💡 建议操作:
        echo    1. 删除venv目录
        echo    2. 运行 '快速设置开发环境.bat' 重新创建
        echo.
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境已激活
) else (
    echo ⚠️  未找到虚拟环境，使用系统Python环境
    echo.
    echo 💡 建议: 运行 '快速设置开发环境.bat' 创建虚拟环境
    echo.
)

REM 检查.env文件
if not exist ".env" (
    echo ❌ 错误: 未找到.env配置文件
    echo.
    echo 💡 解决方法:
    echo    1. 运行 '快速设置开发环境.bat' 创建配置文件
    echo    2. 或手动复制 .env.example 为 .env
    echo    3. 编辑 .env 文件配置数据库连接
    echo.
    pause
    exit /b 1
)

echo ✅ 环境检查完成
echo.
echo 🚀 开始初始化数据库...
echo ================================================
echo.

REM 运行数据库初始化脚本
python 初始化数据库.py
set INIT_RESULT=%ERRORLEVEL%

echo.
echo ================================================

if %INIT_RESULT% equ 0 (
    echo ✅ 数据库初始化成功完成！
    echo.
    echo 🎯 接下来可以:
    echo    1. 运行 '启动所有服务.bat' 启动后端服务
    echo    2. 运行 '检查项目状态.bat' 验证项目状态
    echo    3. 使用微信开发者工具打开小程序项目
    echo.
) else (
    echo ❌ 数据库初始化失败
    echo.
    echo 🔧 故障排除:
    echo    1. 检查PostgreSQL服务是否运行
    echo    2. 验证.env文件中的数据库配置
    echo    3. 确保数据库已创建且有访问权限
    echo    4. 运行 '检查项目状态.bat' 获取详细诊断
    echo.
    echo 📚 参考文档:
    echo    - 配置指南.md
    echo    - 项目工具总览.md
    echo.
)

echo 按任意键退出...
pause >nul
exit /b %INIT_RESULT%