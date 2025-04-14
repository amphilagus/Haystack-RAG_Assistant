# 设置错误操作首选项
$ErrorActionPreference = "Stop"

Write-Host "Starting RAG Web Interface..." -ForegroundColor Green

# 检查是否存在 Python 虚拟环境
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    . .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found, using system Python..." -ForegroundColor Yellow
}

# 检查是否已安装依赖
try {
    python -c "import streamlit" 2>$null
} catch {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# 运行web界面
try {
    Write-Host "Starting web interface..." -ForegroundColor Green
    Write-Host "To exit: Press Ctrl+C in this terminal" -ForegroundColor Cyan
    python rag_assistant/main.py --interface web
} catch {
    Write-Host "Error occurred while running the web interface." -ForegroundColor Red
    Write-Host $_.Exception.Message
    Read-Host "Press Enter to exit"
}

# 如果使用了虚拟环境，退出虚拟环境
if (Test-Path "venv\Scripts\Activate.ps1") {deactivate}