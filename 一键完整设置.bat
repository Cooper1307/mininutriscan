@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo 社区食安AI小卫士 - 一键完整设置工具
echo ================================================
echo 这个工具将帮您完成项目的完整设置过程
echo ================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    echo.
    echo 安装建议:
    echo    1. 访问 https://www.python.org/downloads/
    echo    2. 下载并安装Python 3.8或更高版本
    echo    3. 安装时勾选 Add Python to PATH
    echo.
    pause
    exit /b 1
)

REM 检查是否在项目根目录
if not exist "main.py" (
    echo 错误: 请在项目根目录运行此脚本
    echo 当前目录: %CD%
    echo.
    echo 解决方法:
    echo    1. 打开项目根目录（包含main.py的目录）
    echo    2. 在该目录下运行此脚本
    echo.
    pause
    exit /b 1
)

echo 环境检查通过
echo.
echo 设置流程概览:
echo    1. 配置开发环境
echo    2. 初始化数据库
echo    3. 配置QWEN API密钥（可选）
echo    4. 验证项目状态
echo    5. 启动服务测试
echo.
echo 注意: 整个过程可能需要5-10分钟
echo.
set /p continue="是否继续? (y/n): "
if /i not "%continue%"=="y" (
    echo 设置已取消
    pause
    exit /b 0
)

echo.
echo ================================================
echo 步骤 1/5: 配置开发环境
echo ================================================
echo.

REM 步骤1: 配置开发环境
echo 正在运行开发环境配置...
call "快速设置开发环境.bat"
set ENV_RESULT=%ERRORLEVEL%

if not %ENV_RESULT%==0 (
    echo.
    echo 开发环境配置失败
    echo 建议: 请手动运行 快速设置开发环境.bat 并解决问题
    pause
    exit /b 1
)

echo.
echo 开发环境配置完成
echo.
echo 重要提醒: 请确保已正确配置 .env 文件中的数据库连接信息
echo.
set /p db_configured="数据库连接是否已配置? (y/n): "
if /i not "%db_configured%"=="y" (
    echo.
    echo 请按以下步骤配置数据库:
    echo    1. 打开 .env 文件
    echo    2. 修改 DATABASE_URL 为您的PostgreSQL连接字符串
    echo    3. 示例: postgresql://username:password@localhost:5432/database_name
    echo.
    echo 配置完成后，请重新运行此脚本
    pause
    exit /b 0
)

echo.
echo ================================================
echo 步骤 2/5: 初始化数据库
echo ================================================
echo.

REM 步骤2: 初始化数据库
echo 正在初始化数据库...
python 初始化数据库.py
set DB_RESULT=%ERRORLEVEL%

if not %DB_RESULT%==0 (
    echo.
    echo 数据库初始化失败
    echo 建议: 
    echo    1. 检查PostgreSQL服务是否运行
    echo    2. 验证.env文件中的数据库配置
    echo    3. 手动运行 初始化数据库.bat 获取详细错误信息
    pause
    exit /b 1
)

echo.
echo 数据库初始化完成
echo.

echo ================================================
echo 步骤 3/5: 配置QWEN API密钥（可选）
echo ================================================
echo.

echo QWEN API用于AI检测功能，如果暂时没有密钥可以跳过
set /p config_qwen="是否配置QWEN API密钥? (y/n): "

if /i "%config_qwen%"=="y" (
    echo.
    echo 正在配置QWEN API密钥...
    python 配置QWEN密钥.py
    set QWEN_RESULT=!ERRORLEVEL!
    
    if not !QWEN_RESULT!==0 (
        echo.
        echo QWEN API密钥配置未完成
        echo 可以稍后手动运行 配置QWEN密钥.bat 进行配置
    ) else (
        echo.
        echo QWEN API密钥配置完成
    )
) else (
    echo.
    echo 跳过QWEN API密钥配置
    echo 可以稍后运行 配置QWEN密钥.bat 进行配置
)

echo.
echo ================================================
echo 步骤 4/5: 验证项目状态
echo ================================================
echo.

REM 步骤4: 验证项目状态
echo 正在检查项目状态...
python 检查项目状态.py
set STATUS_RESULT=%ERRORLEVEL%

if not %STATUS_RESULT%==0 (
    echo.
    echo 项目状态检查发现问题
    echo 建议: 根据上述报告解决问题后再继续
    echo.
    set /p continue_anyway="是否继续启动服务测试? (y/n): "
    if /i not "!continue_anyway!"=="y" (
        echo 设置流程已暂停
        pause
        exit /b 0
    )
) else (
    echo.
    echo 项目状态检查通过
)

echo.
echo ================================================
echo 步骤 5/5: 启动服务测试
echo ================================================
echo.

echo 即将启动后端服务进行测试
echo 服务启动后，请在浏览器中访问 http://127.0.0.1:8000/docs 测试API
echo.
set /p start_service="是否启动服务? (y/n): "

if /i "%start_service%"=="y" (
    echo.
    echo 正在启动服务...
    echo ================================================
    echo.
    echo 提示: 按 Ctrl+C 可以停止服务
    echo API文档地址: http://127.0.0.1:8000/docs
    echo.
    
    REM 激活虚拟环境（如果存在）
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
    )
    
    REM 启动FastAPI服务
    python main.py
) else (
    echo.
    echo 跳过服务启动
)

echo.
echo ================================================
echo 设置流程完成！
echo ================================================
echo.
echo 设置结果汇总:
echo    开发环境配置 - 完成
echo    数据库初始化 - 完成
if /i "%config_qwen%"=="y" (
    if %QWEN_RESULT%==0 (
        echo    QWEN API密钥配置 - 完成
    ) else (
        echo    QWEN API密钥配置 - 需要手动完成
    )
) else (
    echo    QWEN API密钥配置 - 已跳过
)
echo    项目状态验证 - 完成
echo.
echo 下一步操作:
echo    1. 运行 启动所有服务.bat 启动后端服务
echo    2. 访问 http://127.0.0.1:8000/docs 查看API文档
echo    3. 参考 小程序开发指南.md 配置微信开发者工具
echo    4. 开始开发您的食安AI小卫士！
echo.
echo 参考文档:
echo    - 项目工具总览.md
echo    - 小程序开发指南.md
echo    - 配置指南.md
echo.
echo 按任意键退出...
pause >nul
exit /b 0