@echo off
chcp 65001 >nul 2>&1

echo.
echo Food Safety AI Guardian - Setup Tool
echo ====================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    pause
    exit /b 1
)

if not exist "main.py" (
    echo Error: Please run in project root directory
    pause
    exit /b 1
)

echo Environment check passed
echo.

set /p continue="Continue setup? (y/n): "
if /i not "%continue%"=="y" (
    echo Setup cancelled
    pause
    exit /b 0
)

echo.
echo Step 1: Configure environment
call "快速设置开发环境.bat"
if errorlevel 1 (
    echo Environment setup failed
    pause
    exit /b 1
)

echo.
echo Step 2: Check database configuration
set /p db_ok="Is database configured in .env? (y/n): "
if /i not "%db_ok%"=="y" (
    echo Please configure DATABASE_URL in .env file first
    pause
    exit /b 0
)

echo.
echo Step 3: Initialize database
python 初始化数据库.py
if errorlevel 1 (
    echo Database initialization failed
    pause
    exit /b 1
)

echo.
echo Step 4: Check project status
python 检查项目状态.py

echo.
echo Setup completed!
echo Next: Run 启动所有服务.bat to start services
echo.
pause
exit /b 0