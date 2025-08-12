@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo Community Food Safety AI Guardian - Complete Setup Tool
echo ================================================
echo This tool will help you complete the project setup process
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found, please install Python 3.8+
    echo.
    echo Installation suggestions:
    echo    1. Visit https://www.python.org/downloads/
    echo    2. Download and install Python 3.8 or higher
    echo    3. Check Add Python to PATH during installation
    echo.
    pause
    exit /b 1
)

REM Check if running in project root directory
if not exist "main.py" (
    echo Error: Please run this script in the project root directory
    echo Current directory: %CD%
    echo.
    echo Solution:
    echo    1. Open the project root directory containing main.py
    echo    2. Run this script in that directory
    echo.
    pause
    exit /b 1
)

echo Environment check passed
echo.
echo Setup process overview:
echo    1. Configure development environment
echo    2. Initialize database
echo    3. Configure QWEN API key optional
echo    4. Verify project status
echo    5. Start service test
echo.
echo Note: The entire process may take 5-10 minutes
echo.
set /p continue="Continue? (y/n): "
if /i not "%continue%"=="y" (
    echo Setup cancelled
    pause
    exit /b 0
)

echo.
echo ================================================
echo Step 1/5: Configure development environment
echo ================================================
echo.

REM Step 1: Configure development environment
echo Running development environment configuration...
call "快速设置开发环境.bat"
set ENV_RESULT=%ERRORLEVEL%

if not %ENV_RESULT%==0 (
    echo.
    echo Development environment configuration failed
    echo Suggestion: Please manually run the quick setup script
    pause
    exit /b 1
)

echo.
echo Development environment configuration completed
echo.
echo Important reminder: Please ensure .env file database connection is configured
echo.
set /p db_configured="Is database connection configured? (y/n): "
if /i not "%db_configured%"=="y" (
    echo.
    echo Please configure database following these steps:
    echo    1. Open .env file
    echo    2. Modify DATABASE_URL to your PostgreSQL connection string
    echo    3. Example: postgresql://username:password@localhost:5432/database_name
    echo.
    echo Please re-run this script after configuration
    pause
    exit /b 0
)

echo.
echo ================================================
echo Step 2/5: Initialize database
echo ================================================
echo.

REM Step 2: Initialize database
echo Initializing database...
python 初始化数据库.py
set DB_RESULT=%ERRORLEVEL%

if not %DB_RESULT%==0 (
    echo.
    echo Database initialization failed
    echo Suggestions: 
    echo    1. Check if PostgreSQL service is running
    echo    2. Verify database configuration in .env file
    echo    3. Manually run database init script for details
    pause
    exit /b 1
)

echo.
echo Database initialization completed
echo.

echo ================================================
echo Step 3/5: Configure QWEN API key optional
echo ================================================
echo.

echo QWEN API is used for AI detection features
set /p config_qwen="Configure QWEN API key? (y/n): "

if /i "%config_qwen%"=="y" (
    echo.
    echo Configuring QWEN API key...
    python 配置QWEN密钥.py
    set QWEN_RESULT=!ERRORLEVEL!
    
    if not !QWEN_RESULT!==0 (
        echo.
        echo QWEN API key configuration incomplete
        echo You can configure it manually later
    ) else (
        echo.
        echo QWEN API key configuration completed
    )
) else (
    echo.
    echo Skipped QWEN API key configuration
    echo You can configure it later if needed
)

echo.
echo ================================================
echo Step 4/5: Verify project status
echo ================================================
echo.

REM Step 4: Verify project status
echo Checking project status...
python 检查项目状态.py
set STATUS_RESULT=%ERRORLEVEL%

if not %STATUS_RESULT%==0 (
    echo.
    echo Project status check found issues
    echo Suggestion: Resolve issues according to the report above
    echo.
    set /p continue_anyway="Continue with service test? (y/n): "
    if /i not "!continue_anyway!"=="y" (
        echo Setup process paused
        pause
        exit /b 0
    )
) else (
    echo.
    echo Project status check passed
)

echo.
echo ================================================
echo Step 5/5: Start service test
echo ================================================
echo.

echo About to start backend service for testing
echo After service starts visit http://127.0.0.1:8000/docs to test API
echo.
set /p start_service="Start service? (y/n): "

if /i "%start_service%"=="y" (
    echo.
    echo Starting service...
    echo ================================================
    echo.
    echo Tip: Press Ctrl+C to stop service
    echo API documentation: http://127.0.0.1:8000/docs
    echo.
    
    REM Activate virtual environment if exists
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
    )
    
    REM Start FastAPI service
    python main.py
) else (
    echo.
    echo Skipped service startup
)

echo.
echo ================================================
echo Setup process completed!
echo ================================================
echo.
echo Setup results summary:
echo    Development environment - Completed
echo    Database initialization - Completed
if /i "%config_qwen%"=="y" (
    if %QWEN_RESULT%==0 (
        echo    QWEN API key configuration - Completed
    ) else (
        echo    QWEN API key configuration - Needs manual completion
    )
) else (
    echo    QWEN API key configuration - Skipped
)
echo    Project status verification - Completed
echo.
echo Next steps:
echo    1. Run startup script to start backend service
echo    2. Visit http://127.0.0.1:8000/docs to view API documentation
echo    3. Refer to development guide to configure WeChat Developer Tools
echo    4. Start developing your Food Safety AI Guardian!
echo.
echo Reference documents:
echo    - Project tools overview
echo    - Mini-program development guide
echo    - Configuration guide
echo.
echo Press any key to exit...
pause >nul
exit /b 0