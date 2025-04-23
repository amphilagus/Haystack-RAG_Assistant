#!/usr/bin/env pwsh
<#
.SYNOPSIS
    递归清洗Markdown文件的PowerShell脚本。

.DESCRIPTION
    此脚本递归查找输入目录及其子目录中的所有Markdown文件，
    使用md_cleaner.py清洗它们，并将所有文件平行地放在指定输出目录中。

.PARAMETER InputDir
    包含Markdown文件的输入目录。

.PARAMETER OutputDir
    清洗后文件的输出目录。

.PARAMETER DocType
    文档类型，对应md_cleaner_config.json中的类型。

.PARAMETER Rules
    可选。要应用的规则ID，用逗号分隔。

.PARAMETER ConfigFile
    可选。配置文件路径。

.EXAMPLE
    .\clean_md_files.ps1 .\raw_data .\cleaned_data jctc
#>

param (
    [Parameter(Mandatory=$true, Position=0)]
    [string]$InputDir,
    
    [Parameter(Mandatory=$true, Position=1)]
    [string]$OutputDir,
    
    [Parameter(Mandatory=$true, Position=2)]
    [string]$DocType,
    
    [Parameter(Mandatory=$false)]
    [string]$Rules,
    
    [Parameter(Mandatory=$false)]
    [string]$ConfigFile = ".\rag_assistant\utils\md_cleaner\md_cleaner_config.json"
)

# 设置UTF-8编码
$OutputEncoding = [System.Text.Encoding]::UTF8

# 检查参数
if (-not (Test-Path $InputDir -PathType Container)) {
    Write-Error "Input directory does not exist: $InputDir"
    exit 1
}

# 创建输出目录
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
    Write-Host "Created output directory: $OutputDir"
}

# 获取脚本所在目录的绝对路径
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$mdCleanerPath = Join-Path $scriptDir "rag_assistant\utils\md_cleaner\md_cleaner.py"

# 检查md_cleaner.py是否存在
if (-not (Test-Path $mdCleanerPath)) {
    Write-Error "Could not find md_cleaner.py: $mdCleanerPath"
    exit 1
}

# 检查配置文件是否存在
$configPath = Join-Path $scriptDir $ConfigFile
if (-not (Test-Path $configPath)) {
    Write-Error "Could not find config file: $configPath"
    exit 1
}

# 构建基本命令
$baseCommand = "python `"$mdCleanerPath`" --doc-type $DocType --config `"$configPath`""
if ($Rules) {
    $baseCommand += " --rules $Rules"
}

# 统计信息
$totalFiles = 0
$processedFiles = 0
$errorFiles = 0

# 递归处理所有.md文件
Write-Host "Starting file processing..."
Write-Host "Input directory: $InputDir"
Write-Host "Output directory: $OutputDir"
Write-Host "Document type: $DocType"
if ($Rules) {
    Write-Host "Applied rules: $Rules"
}

# 这将在Windows操作系统上启用长路径支持
try {
    # 这需要管理员权限，如果没有将会失败但不会阻止脚本继续执行
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -Type DWord
} catch {
    Write-Host "Could not enable long path support. Very long file paths may cause issues." -ForegroundColor Yellow
}

Get-ChildItem -Path $InputDir -Filter "*.md" -Recurse | ForEach-Object {
    $totalFiles++
    $inputFile = $_.FullName
    
    # 只使用文件名，不保留目录结构，防止"套娃"结构
    $outputFile = Join-Path $OutputDir $_.Name
    
    # 构建并执行命令
    $command = "$baseCommand `"$inputFile`" `"$outputFile`""
    
    try {
        Write-Host "Processing file: $($_.Name)" -ForegroundColor Cyan
        # 直接执行Python脚本，避免通过PowerShell管道处理，减少编码问题
        $processInfo = New-Object System.Diagnostics.ProcessStartInfo
        $processInfo.FileName = "python"
        $processInfo.Arguments = "`"$mdCleanerPath`" --doc-type $DocType --config `"$configPath`" `"$inputFile`" `"$outputFile`""
        if ($Rules) {
            $processInfo.Arguments += " --rules $Rules"
        }
        $processInfo.RedirectStandardOutput = $true
        $processInfo.RedirectStandardError = $true
        $processInfo.UseShellExecute = $false
        $processInfo.CreateNoWindow = $true
        $processInfo.StandardOutputEncoding = [System.Text.Encoding]::UTF8
        $processInfo.StandardErrorEncoding = [System.Text.Encoding]::UTF8
        
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $processInfo
        $process.Start() | Out-Null
        $process.WaitForExit()
        
        $stdout = $process.StandardOutput.ReadToEnd()
        $stderr = $process.StandardError.ReadToEnd()
        
        if ($process.ExitCode -eq 0) {
            $processedFiles++
            Write-Host "  Successfully processed" -ForegroundColor Green
        } else {
            $errorFiles++
            Write-Host "  Processing failed: $stderr" -ForegroundColor Red
        }
    } catch {
        $errorFiles++
        Write-Host "  Error processing file: $_" -ForegroundColor Red
    }
}

# 显示处理结果
Write-Host "`nProcessing complete!" -ForegroundColor Green
Write-Host "Total files: $totalFiles" -ForegroundColor White
Write-Host "Successfully processed: $processedFiles" -ForegroundColor Green
if ($errorFiles -gt 0) {
    Write-Host "Failed to process: $errorFiles" -ForegroundColor Red
} else {
    Write-Host "Failed to process: 0" -ForegroundColor Green
} 