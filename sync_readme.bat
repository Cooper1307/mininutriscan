@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ===================================================================
REM 社区食安AI小卫士 - README自动同步脚本 (Windows批处理版本)
REM 
REM 功能说明:
REM 1. 自动检测项目文件变化
REM 2. 更新README文档统计信息
REM 3. 提交并推送到远程仓库
REM 4. 提供用户友好的操作界面
REM 
REM 使用方法:
REM     双击运行 sync_readme.bat
REM     或在命令行中执行: sync_readme.bat
REM 
REM 作者: 陈露
REM 创建时间: 2025年8月
REM ===================================================================

echo.
echo 🛡️ 社区食安AI小卫士 - README自动同步工具
echo ==================================================
echo.

REM 检查是否在正确的项目目录
if not exist ".git" (
    echo ❌ 错误: 当前目录不是Git仓库
    echo 请确保在项目根目录下运行此脚本
    pause
    exit /b 1
)

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo 请确保已安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 检查Git是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Git
    echo 请确保已安装Git
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.

REM 显示当前项目状态
echo 📊 当前项目状态:
echo ----------------------------------------
for /f "tokens=*" %%i in ('git branch --show-current') do echo 🌿 当前分支: %%i
for /f "tokens=*" %%i in ('git log -1 --pretty=format:"%%h - %%s (%%cr)"') do echo 🔄 最后提交: %%i

REM 检查工作区状态
git status --porcelain > temp_status.txt
set /p git_status=<temp_status.txt
del temp_status.txt

if "%git_status%"=="" (
    echo 📊 工作区状态: 干净
) else (
    echo 📊 工作区状态: 有未提交的更改
)
echo.

REM 询问用户是否继续
set /p user_choice=是否继续同步README文档? (Y/N): 
if /i not "%user_choice%"=="Y" if /i not "%user_choice%"=="y" (
    echo 操作已取消
    pause
    exit /b 0
)

echo.
echo 🚀 开始同步README文档...
echo ----------------------------------------

REM 执行Python同步脚本
python sync_readme.py
set sync_result=%errorlevel%

echo.
if %sync_result% equ 0 (
    echo ✅ README文档同步成功！
    echo.
    echo 📝 同步完成的操作:
    echo    - 更新了项目统计信息
    echo    - 更新了Git仓库信息
    echo    - 提交了所有更改
    echo    - 推送到远程仓库
    echo.
    echo 🔗 可以访问以下链接查看更新:
    for /f "tokens=*" %%i in ('git remote get-url origin') do (
        set repo_url=%%i
        echo    GitHub仓库: !repo_url!
    )
) else (
    echo ❌ README文档同步失败！
    echo.
    echo 🔍 可能的原因:
    echo    - 网络连接问题
    echo    - Git权限问题
    echo    - 文件权限问题
    echo.
    echo 📝 请查看 sync_readme.log 文件获取详细错误信息
)

echo.
echo 📋 操作日志已保存到: sync_readme.log
echo.

REM 询问是否查看日志
if %sync_result% neq 0 (
    set /p view_log=是否查看错误日志? (Y/N): 
    if /i "%view_log%"=="Y" if exist sync_readme.log (
        echo.
        echo 📄 最近的日志内容:
        echo ----------------------------------------
        powershell -Command "Get-Content sync_readme.log -Tail 20"
    )
)

echo.
echo 感谢使用社区食安AI小卫士项目管理工具！
echo.
pause
exit /b %sync_result%