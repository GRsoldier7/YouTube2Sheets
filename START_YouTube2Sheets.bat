@echo off
REM ============================================================================
REM YouTube2Sheets - Bulletproof Launcher
REM ============================================================================
REM This batch file launches the YouTube2Sheets GUI with robust error handling
REM ============================================================================

title YouTube2Sheets Launcher
color 0A

echo.
echo ========================================================================
echo   YouTube2Sheets - YouTube to Google Sheets Automation
echo ========================================================================
echo.
echo Starting application...
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ========================================================================
    echo   ERROR: Python is not installed or not in PATH
    echo ========================================================================
    echo.
    echo   Please install Python from https://www.python.org/downloads/
    echo   Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if youtube_to_sheets_gui.py exists
if not exist "youtube_to_sheets_gui.py" (
    echo ========================================================================
    echo   ERROR: youtube_to_sheets_gui.py not found
    echo ========================================================================
    echo.
    echo   Make sure you're running this from the project directory
    echo   Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo [OK] GUI file found
echo.

REM Check if required dependencies are installed
python -c "import customtkinter" >nul 2>&1
if errorlevel 1 (
    echo ========================================================================
    echo   WARNING: Dependencies may not be installed
    echo ========================================================================
    echo.
    echo   Installing required dependencies...
    echo.
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo   ERROR: Failed to install dependencies
        echo   Please run manually: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Dependencies installed
echo.
echo ========================================================================
echo   Launching YouTube2Sheets GUI...
echo ========================================================================
echo.

REM Launch the GUI
python youtube_to_sheets_gui.py

REM Check if the GUI launched successfully
if errorlevel 1 (
    echo.
    echo ========================================================================
    echo   ERROR: Application failed to start
    echo ========================================================================
    echo.
    echo   Please check the error message above
    echo   Check logs in: logs\youtube2sheets.log
    echo.
    pause
    exit /b 1
)

REM If we get here, everything worked
echo.
echo ========================================================================
echo   Application closed successfully
echo ========================================================================
echo.


