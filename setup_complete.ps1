# Food Safety AI Guardian - Complete Setup Script
# PowerShell version to avoid batch file encoding issues

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   Food Safety AI Guardian - Setup Tool" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python environment..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✅ Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python not found" -ForegroundColor Red
    Write-Host "Please install Python 3.8+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check project directory
if (-not (Test-Path "main.py")) {
    Write-Host "❌ Error: Please run in project root directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Project directory confirmed" -ForegroundColor Green
Write-Host ""

$continue = Read-Host "Continue with setup? (y/n)"
if ($continue -ne "y" -and $continue -ne "Y") {
    Write-Host "Setup cancelled" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host ""
Write-Host "Step 1: Setting up development environment..." -ForegroundColor Yellow
try {
    & ".\快速设置开发环境.bat"
    if ($LASTEXITCODE -ne 0) {
        throw "Environment setup failed"
    }
    Write-Host "✅ Environment setup completed" -ForegroundColor Green
} catch {
    Write-Host "❌ Environment setup failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 2: Database configuration check" -ForegroundColor Yellow
$dbOk = Read-Host "Is DATABASE_URL configured in .env file? (y/n)"
if ($dbOk -ne "y" -and $dbOk -ne "Y") {
    Write-Host "Please configure DATABASE_URL in .env file first" -ForegroundColor Red
    Write-Host "Example: DATABASE_URL=sqlite:///./food_safety.db" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host ""
Write-Host "Step 3: Initializing database..." -ForegroundColor Yellow
try {
    python "初始化数据库.py"
    if ($LASTEXITCODE -ne 0) {
        throw "Database initialization failed"
    }
    Write-Host "✅ Database initialization completed" -ForegroundColor Green
} catch {
    Write-Host "❌ Database initialization failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 4: Checking project status..." -ForegroundColor Yellow
python "检查项目状态.py"

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "   Setup completed successfully!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run '启动所有服务.bat' to start services" -ForegroundColor White
Write-Host "2. Access API docs at http://localhost:8000/docs" -ForegroundColor White
Write-Host "3. Configure WeChat developer tools" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"