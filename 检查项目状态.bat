@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ===============================================
echo   社区食安AI小卫士 - 项目状态检查工具
echo ===============================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.8+
    echo.
    pause
    exit /b 1
)

REM 检查是否在项目目录
if not exist "main.py" (
    echo ❌ 请在项目根目录运行此脚本
    echo 当前目录: %CD%
    echo.
    pause
    exit /b 1
)

REM 运行检查脚本
echo 🔍 开始检查项目状态...
echo.
python 检查项目状态.py

REM 检查执行结果
if errorlevel 1 (
    echo.
    echo ⚠️  检查发现问题，请根据上述建议进行修复
) else (
    echo.
    echo ✅ 项目状态良好！
)

echo.
echo ===============================================
echo 检查完成
echo ===============================================
pause