# 设置错误操作首选项
$ErrorActionPreference = "Stop"

Write-Host "Starting RAG CLI Interface..." -ForegroundColor Green

# 检查是否存在 Python 虚拟环境
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    . .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found, using system Python..." -ForegroundColor Yellow
}

# 检查是否已安装依赖
try {
    python -c "import haystack" 2>$null
} catch {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

function Test-CollectionName {
    param (
        [string]$name
    )
    return $name -match "^[a-zA-Z0-9][a-zA-Z0-9._-]{1,61}[a-zA-Z0-9]$"
}

# 检查collection是否存在，并获取其嵌入模型信息
function Get-CollectionEmbeddingModel {
    param (
        [string]$collectionName
    )
    
    try {
        # 调用专门的Python工具脚本来获取嵌入模型
        $result = python rag_assistant/collection_utils.py --get-embedding-model $collectionName
        return $result.Trim()
    } catch {
        Write-Host "Error getting embedding model: $_" -ForegroundColor Red
        return ""
    }
}

# 获取collection是否存在
function Test-CollectionExists {
    param (
        [string]$collectionName
    )
    
    try {
        # 调用专门的Python工具脚本来检查集合是否存在
        $output = python rag_assistant/collection_utils.py --check-exists $collectionName
        return $output.Trim() -eq "True"
    } catch {
        Write-Host "Error checking collection existence: $_" -ForegroundColor Red
        return $false
    }
}

# 运行 CLI 界面
try {
    Write-Host "Starting CLI interface..." -ForegroundColor Green
    Write-Host "Type 'help' for available commands, 'exit' to quit" -ForegroundColor Cyan

    # 询问是否指定 collection
    do {
        $collection = Read-Host "Enter the collection name to use (default: documents)"
        if ([string]::IsNullOrWhiteSpace($collection)) {
            $collection = "documents"
        }

        if (-not (Test-CollectionName $collection)) {
            Write-Host "Invalid collection name. Name must:" -ForegroundColor Red
            Write-Host "- Be 3-63 characters long" -ForegroundColor Red
            Write-Host "- Contain only letters, numbers, dots, underscores, or hyphens" -ForegroundColor Red
            Write-Host "- Start and end with a letter or number" -ForegroundColor Red
            continue
        }
        break
    } while ($true)

    # 检查collection是否存在
    $collectionExists = Test-CollectionExists -collectionName $collection
    if ($collectionExists) {
        Write-Host "Collection '$collection' already exists." -ForegroundColor Cyan
        # 获取已有collection的嵌入模型
        $existingEmbeddingModel = Get-CollectionEmbeddingModel -collectionName $collection
        if ($existingEmbeddingModel) {
            Write-Host "This collection was created with embedding model: $existingEmbeddingModel" -ForegroundColor Cyan
        }
    } else {
        Write-Host "Collection '$collection' will be created." -ForegroundColor Cyan
    }

    Write-Host "Using collection: $collection" -ForegroundColor Cyan

    # 询问是否重置 collection
    $resetCollection = $false
    $hardReset = $false

    $resetChoice = Read-Host "`nDo you want to reset the collection? (y/n)"
    Write-Host "You selected: $resetChoice"
    
    if ($resetChoice -eq 'y') {
        $resetCollection = $true

        # 询问是否进行硬重置
        Write-Host "`nHard reset will completely delete the existing collection."
        $hardResetChoice = Read-Host "Do you want to use hard reset? (y/n)"
        Write-Host "You selected for hard reset: $hardResetChoice"
        
        if ($hardResetChoice -eq 'y') {
            Write-Host "WARNING: Hard reset will completely delete the existing collection!" -ForegroundColor Red
            $confirm = Read-Host "Are you sure? (y/n)"
            if ($confirm -eq 'y') {
                $hardReset = $true
                Write-Host "Hard reset enabled - collection will be deleted if it exists" -ForegroundColor Red
            } else {
                Write-Host "Hard reset disabled, will use soft reset (create new collection with timestamp)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "Using soft reset (create new collection with timestamp)" -ForegroundColor Yellow
        }
    }

    # 选择 OpenAI 模型
    Write-Host "`nSelect OpenAI model to use:" -ForegroundColor Yellow
    Write-Host "  1) GPT-4o Mini (default)" -ForegroundColor Cyan
    Write-Host "  2) GPT-3.5 Turbo" -ForegroundColor Cyan
    Write-Host "  3) GPT-4o" -ForegroundColor Cyan
    Write-Host "  4) GPT-o1" -ForegroundColor Cyan

    $modelChoice = Read-Host "Enter your choice (1-4)"
    $modelName = "gpt-4o-mini"

    switch ($modelChoice) {
        "2" { $modelName = "gpt-3.5-turbo"; Write-Host "Selected GPT-3.5 Turbo" -ForegroundColor Green }
        "3" { $modelName = "gpt-4o"; Write-Host "Selected GPT-4o" -ForegroundColor Green }
        "4" { $modelName = "o1"; Write-Host "Selected GPT-o1" -ForegroundColor Green }
        default { Write-Host "Selected GPT-4o Mini (default)" -ForegroundColor Green }
    }
    
    # 选择提示词模板
    Write-Host "`nSelect prompt template to use:" -ForegroundColor Yellow
    Write-Host "  1) Balanced (default) - Balance accuracy and fluency" -ForegroundColor Cyan
    Write-Host "  2) Precise - Strictly follow document content with concise answers" -ForegroundColor Cyan
    Write-Host "  3) Creative - Provide detailed explanations while maintaining accuracy" -ForegroundColor Cyan

    $templateChoice = Read-Host "Enter your choice (1-3)"
    $promptTemplate = "balanced"

    switch ($templateChoice) {
        "2" { $promptTemplate = "precise"; Write-Host "Selected Precise template" -ForegroundColor Green }
        "3" { $promptTemplate = "creative"; Write-Host "Selected Creative template" -ForegroundColor Green }
        default { Write-Host "Selected Balanced template (default)" -ForegroundColor Green }
    }
    
    # 选择嵌入模型，但只在以下情况才提示选择：
    # 1. collection不存在
    # 2. collection存在但要重置
    # 3. collection存在但没有嵌入模型记录
    $embeddingModel = $existingEmbeddingModel
    
    if ($resetCollection -or -not $collectionExists -or -not $embeddingModel) {
        Write-Host "`nSelect Embedding model to use:" -ForegroundColor Yellow
        Write-Host "  1) sentence-transformers/all-MiniLM-L6-v2 (default, fast, multilingual)" -ForegroundColor Cyan
        Write-Host "  2) sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (better multilingual)" -ForegroundColor Cyan
        Write-Host "  3) BAAI/bge-small-zh-v1.5 (optimized for Chinese)" -ForegroundColor Cyan 
        Write-Host "  4) BAAI/bge-large-zh-v1.5 (high quality Chinese, slower)" -ForegroundColor Cyan
        Write-Host "  5) moka-ai/m3e-base (Chinese + English, balanced)" -ForegroundColor Cyan

        $embeddingChoice = Read-Host "Enter your choice (1-5)"
        
        switch ($embeddingChoice) {
            "2" { $embeddingModel = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"; Write-Host "Selected paraphrase-multilingual-MiniLM-L12-v2" -ForegroundColor Green }
            "3" { $embeddingModel = "BAAI/bge-small-zh-v1.5"; Write-Host "Selected BAAI/bge-small-zh-v1.5 (Chinese optimized)" -ForegroundColor Green }
            "4" { $embeddingModel = "BAAI/bge-large-zh-v1.5"; Write-Host "Selected BAAI/bge-large-zh-v1.5 (High quality Chinese)" -ForegroundColor Green }
            "5" { $embeddingModel = "moka-ai/m3e-base"; Write-Host "Selected moka-ai/m3e-base (Chinese + English)" -ForegroundColor Green }
            default { $embeddingModel = "sentence-transformers/all-MiniLM-L6-v2"; Write-Host "Selected all-MiniLM-L6-v2 (default)" -ForegroundColor Green }
        }
    } else {
        Write-Host "`nUsing existing collection's embedding model: $embeddingModel" -ForegroundColor Green
        Write-Host "This ensures compatibility with previously embedded documents" -ForegroundColor Cyan
    }

    # 添加文档加载参数
    $loadDocs = Read-Host "`nDo you want to load documents from raw_data directory? (y/n)"
    if ($loadDocs -eq 'y') {
        Write-Host "Available subdirectories in raw_data:" -ForegroundColor Yellow
        Get-ChildItem "raw_data" -Directory | ForEach-Object { Write-Host "  - $($_.Name)" }

        $subDir = Read-Host "Enter the subdirectory name from raw_data (e.g. percolation_theory)"
        $docPath = if ([string]::IsNullOrWhiteSpace($subDir)) { "raw_data" } else { "raw_data/$subDir" }

        if (Test-Path $docPath) {
            if ($collection -ne "documents") {
                Write-Host "`nYou are adding documents to collection: '$collection'" -ForegroundColor Cyan
                $confirm = Read-Host "Continue? (y/n)"
                if ($confirm -ne 'y') {
                    Write-Host "Operation cancelled." -ForegroundColor Yellow
                    exit 0
                }
            }

            $args = @(
                "rag_assistant/main.py",
                "--interface", "cli",
                "--add-docs", $docPath,
                "--collection", $collection,
                "--llm-model", $modelName,
                "--embedding-model", $embeddingModel,
                "--prompt-template", $promptTemplate
            )
            if ($resetCollection) { $args += "--reset-collection" }
            if ($hardReset) { $args += "--hard-reset" }

            python $args
        } else {
            Write-Host "Error: Directory '$docPath' does not exist." -ForegroundColor Red
            exit 1
        }
    } else {
        $args = @(
            "rag_assistant/main.py",
            "--interface", "cli",
            "--collection", $collection,
            "--llm-model", $modelName,
            "--embedding-model", $embeddingModel,
            "--prompt-template", $promptTemplate
        )
        if ($resetCollection) { $args += "--reset-collection" }
        if ($hardReset) { $args += "--hard-reset" }

        python $args
    }
} catch {
    Write-Host "Error occurred while running the CLI interface." -ForegroundColor Red
    Write-Host $_.Exception.Message
    Read-Host "Press Enter to exit"
}

# 如果使用了虚拟环境，退出虚拟环境
if (Test-Path "venv\Scripts\Activate.ps1") {
    # PowerShell中deactivate是一个函数，不是命令，所以需要正确调用它
    if (Get-Command "deactivate" -ErrorAction SilentlyContinue) {
        deactivate
    } else {
        Write-Host "Deactivate function not found. Virtual environment may still be active." -ForegroundColor Yellow
    }
}
