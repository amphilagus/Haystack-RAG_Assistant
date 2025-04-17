#Requires -Version 5.0

<#
.SYNOPSIS
    Converts PDF files to Markdown format using the Marker library.

.DESCRIPTION
    This script provides a PowerShell interface for converting PDF files to Markdown format.
    It supports both single PDF files and directories containing multiple PDFs.

.PARAMETER InputPath
    Path to the input PDF file or directory containing PDF files.

.PARAMETER OutputDir
    Directory where the Markdown files will be saved.

.PARAMETER BatchMultiplier
    How much to multiply default batch sizes by for conversion. Default is 2.
    Increasing this value can speed up conversion on systems with more VRAM.

.PARAMETER MaxPages
    Maximum number of pages to process per PDF. If not specified, all pages are processed.

.PARAMETER Langs
    Comma-separated list of languages in the document for OCR.
    Example: "en,fr,de"

.PARAMETER Workers
    Number of PDFs to process in parallel when processing a directory. Default is 1.

.PARAMETER MaxFiles
    Maximum number of PDF files to process from a directory. If not specified, all files are processed.

.PARAMETER MinLength
    Minimum text length to process. PDFs with less text will be skipped. Default is 0.

.PARAMETER UseLLM
    Use LLM (Language Model) to enhance conversion quality. 
    This can significantly improve formatting but may increase processing time.
    If not specified, the script will prompt you interactively.

.PARAMETER NoPrompt
    Suppresses all interactive prompts. Will not use LLM unless explicitly specified with -UseLLM.

.EXAMPLE
    # Process a single PDF file with interactive prompts
    .\convert_pdf.ps1 -InputPath "C:\Documents\paper.pdf" -OutputDir "C:\Documents\markdown"

.EXAMPLE
    # Process a single PDF with custom settings and explicitly use LLM
    .\convert_pdf.ps1 -InputPath "C:\Documents\paper.pdf" -OutputDir "C:\Documents\markdown" -BatchMultiplier 4 -Langs "en,fr" -UseLLM

.EXAMPLE
    # Process a directory of PDF files in parallel without interactive prompts
    .\convert_pdf.ps1 -InputPath "C:\Documents\papers" -OutputDir "C:\Documents\markdown" -Workers 4 -MaxFiles 20 -NoPrompt

.NOTES
    This script requires Python 3.8 or higher to be installed on the system.
#>

param (
    [Parameter(Mandatory=$true, Position=0)]
    [string]$InputPath,
    
    [Parameter(Mandatory=$true, Position=1)]
    [string]$OutputDir,
    
    [Parameter(Mandatory=$false)]
    [int]$BatchMultiplier = 2,
    
    [Parameter(Mandatory=$false)]
    [int]$MaxPages,
    
    [Parameter(Mandatory=$false)]
    [string]$Langs,
    
    [Parameter(Mandatory=$false)]
    [int]$Workers = 1,
    
    [Parameter(Mandatory=$false)]
    [int]$MaxFiles,
    
    [Parameter(Mandatory=$false)]
    [int]$MinLength = 0,
    
    [Parameter(Mandatory=$false)]
    [switch]$UseLLM,
    
    [Parameter(Mandatory=$false)]
    [switch]$NoPrompt
)

$ErrorActionPreference = "Stop"

# Check if input path exists
if (-not (Test-Path $InputPath)) {
    Write-Error "Input path not found: $InputPath"
    exit 1
}

$isDirectory = Test-Path -Path $InputPath -PathType Container
$isSingleFile = Test-Path -Path $InputPath -PathType Leaf

if (-not ($isDirectory -or $isSingleFile)) {
    Write-Error "Input path is neither a file nor a directory: $InputPath"
    exit 1
}

if ($isSingleFile -and -not $InputPath.ToLower().EndsWith('.pdf')) {
    Write-Error "Input file is not a PDF: $InputPath"
    exit 1
}

# Create output directory if it doesn't exist
if (-not (Test-Path $OutputDir -PathType Container)) {
    Write-Host "Creating output directory: $OutputDir"
    New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null
}

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Using $pythonVersion"
} catch {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.8 or later."
    exit 1
}

# Set path to the Python script
$scriptPath = Join-Path (Get-Location) "rag_assistant\pdf_to_markdown.py"
if (-not (Test-Path $scriptPath)) {
    # Try the script in the current directory
    $scriptPath = "pdf_to_markdown.py"
    if (-not (Test-Path $scriptPath)) {
        Write-Error "Could not find pdf_to_markdown.py script"
        exit 1
    }
}

# Interactive prompt for LLM if not explicitly specified and not suppressed
if (-not ($UseLLM -or $NoPrompt)) {
    Write-Host ""
    Write-Host "LLM enhancement can significantly improve conversion quality but increases processing time and API usage." -ForegroundColor Yellow
    Write-Host "Use LLM enhancement? (Y/N)" -ForegroundColor Cyan -NoNewline
    $promptResponse = Read-Host " "
    if ($promptResponse -match "^[Yy]") {
        $UseLLM = $true
        Write-Host "LLM enhancement enabled!" -ForegroundColor Green
    } else {
        Write-Host "LLM enhancement disabled." -ForegroundColor Cyan
    }
    Write-Host ""
}

# Build the command arguments
$pythonArgs = @($scriptPath, $InputPath, $OutputDir)

if ($BatchMultiplier -ne 2) {
    $pythonArgs += "--batch_multiplier"
    $pythonArgs += $BatchMultiplier
}

if ($MaxPages) {
    $pythonArgs += "--max_pages"
    $pythonArgs += $MaxPages
}

if ($Langs) {
    $pythonArgs += "--langs"
    $pythonArgs += $Langs
}

# Add directory processing arguments if input is a directory
if ($isDirectory) {
    Write-Host "Processing directory: $InputPath"
    
    if ($Workers -ne 1) {
        $pythonArgs += "--workers"
        $pythonArgs += $Workers
    }
    
    if ($MaxFiles) {
        $pythonArgs += "--max_files"
        $pythonArgs += $MaxFiles
    }
    
    if ($MinLength -ne 0) {
        $pythonArgs += "--min_length"
        $pythonArgs += $MinLength
    }
}

# Add LLM parameter if specified
if ($UseLLM) {
    Write-Host "Using LLM enhancement for improved conversion quality" -ForegroundColor Green
    $pythonArgs += "--use_llm"
}

# Display the command that will be executed
$cmdDisplay = "python " + ($pythonArgs -join " ")
Write-Host "Executing: $cmdDisplay"

# Execute the Python script
try {
    $startTime = Get-Date
    
    # Run the Python script
    & python $pythonArgs
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "PDF to Markdown conversion failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host "Conversion completed successfully in $($duration.TotalSeconds.ToString("0.00")) seconds" -ForegroundColor Green

} catch {
    Write-Error "An error occurred: $_"
    exit 1
} 