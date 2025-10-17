# ============================================================================
# YouTube2Sheets - PowerShell Launcher
# ============================================================================
# This PowerShell script launches the YouTube2Sheets GUI
# ============================================================================

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  YouTube2Sheets - YouTube to Google Sheets Automation" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting application..." -ForegroundColor Yellow
Write-Host ""

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "========================================================================" -ForegroundColor Red
    Write-Host "  ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "========================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Please install Python from https://www.python.org/downloads/"
    Write-Host "  Make sure to check 'Add Python to PATH' during installation"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if GUI file exists
if (-not (Test-Path "youtube_to_sheets_gui.py")) {
    Write-Host "========================================================================" -ForegroundColor Red
    Write-Host "  ERROR: youtube_to_sheets_gui.py not found" -ForegroundColor Red
    Write-Host "========================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Current directory: $(Get-Location)"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] GUI file found" -ForegroundColor Green
Write-Host ""

# Check if dependencies are installed
try {
    python -c "import customtkinter" 2>&1 | Out-Null
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "========================================================================" -ForegroundColor Yellow
    Write-Host "  WARNING: Dependencies may not be installed" -ForegroundColor Yellow
    Write-Host "========================================================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Installing required dependencies..." -ForegroundColor Yellow
    Write-Host ""
    
    python -m pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "  ERROR: Failed to install dependencies" -ForegroundColor Red
        Write-Host "  Please run manually: pip install -r requirements.txt"
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  Launching YouTube2Sheets GUI..." -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Launch the GUI
python youtube_to_sheets_gui.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "========================================================================" -ForegroundColor Red
    Write-Host "  ERROR: Application failed to start" -ForegroundColor Red
    Write-Host "========================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Please check the error message above"
    Write-Host "  Check logs in: logs\youtube2sheets.log"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "  Application closed successfully" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host ""


