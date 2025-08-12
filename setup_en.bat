@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ===============================================
echo   Food Safety AI Guardian - Setup Tool
echo ===============================================
echo.

REM Check Python installation
echo Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Please install Python 3.8+
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: !PYTHON_VERSION!

REM Check project directory
if not exist "main.py" (
    echo Error: Please run in project root directory
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo Project directory confirmed
echo.

set /p continue="Continue with setup? (y/n): "
if /i not "!continue!"=="y" (
    echo Setup cancelled
    pause
    exit /b 0
)

echo.
echo Step 1: Setting up development environment...
call "快速设置开发环境.bat"
if errorlevel 1 (
    echo Environment setup failed
    pause
    exit /b 1
)

echo.
echo Step 2: Database configuration check
set /p db_ok="Is DATABASE_URL configured in .env file? (y/n): "
if /i not "!db_ok!"=="y" (
    echo Please configure DATABASE_URL in .env file first
    echo Example: DATABASE_URL=sqlite:///./food_safety.db
    pause
    exit /b 0
)

echo.
echo Step 3: Initializing database...
python "初始化数据库.py"
if errorlevel 1 (
    echo Database initialization failed
    pause
    exit /b 1
)

echo.
echo Step 4: Checking project status...
python "检查项目状态.py"

echo.
echo ===============================================
echo   Setup completed successfully!
echo ===============================================
echo.
echo Next steps:
echo 1. Run "启动所有服务.bat" to start services
echo 2. Access API docs at http://localhost:8000/docs
echo 3. Configure WeChat developer tools
echo.
pause
exit /b 0