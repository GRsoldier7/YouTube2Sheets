@echo off
REM ============================================================================
REM YouTube2Sheets - Production Launcher (Robust & Future-Proof)
REM ============================================================================
REM Version: 2.0
REM Last Updated: 2025-09-30
REM ============================================================================

title YouTube2Sheets
color 0B

REM Change to script directory
cd /d "%~dp0"

REM ============================================================================
REM STEP 1: Environment Validation
REM ============================================================================

echo.
echo ======================================================================
echo   YouTube2Sheets - Production Launcher
echo ======================================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    cls
    echo.
    echo ======================================================================
    echo   ERROR: Python Not Found
    echo ======================================================================
    echo.
    echo   Python is required but not installed or not in PATH.
    echo.
    echo   SOLUTION:
    echo   1. Download Python from: https://www.python.org/downloads/
    echo   2. During installation, CHECK "Add Python to PATH"
    echo   3. Restart this launcher after installation
    echo.
    echo ======================================================================
    pause
    exit /b 1
)

echo [1/5] Python: OK
timeout /t 1 /nobreak >nul

REM Check if GUI file exists
if not exist "youtube_to_sheets_gui.py" (
    cls
    echo.
    echo ======================================================================
    echo   ERROR: GUI File Not Found
    echo ======================================================================
    echo.
    echo   youtube_to_sheets_gui.py is missing from project directory.
    echo.
    echo   Current Location: %CD%
    echo.
    echo   SOLUTION:
    echo   Make sure you're running this from the YouTube2Sheets folder
    echo.
    echo ======================================================================
    pause
    exit /b 1
)

echo [2/5] GUI File: OK
timeout /t 1 /nobreak >nul

REM ============================================================================
REM STEP 2: Dependency Check & Auto-Install
REM ============================================================================

echo [3/5] Checking dependencies...

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo       WARNING: requirements.txt not found
    echo       Attempting to launch anyway...
    goto :launch
)

REM Quick dependency check
python -c "import customtkinter, googleapiclient, google.oauth2" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ======================================================================
    echo   Installing Missing Dependencies
    echo ======================================================================
    echo.
    echo   This is a one-time setup. Please wait...
    echo.
    
    python -m pip install --upgrade pip >nul 2>&1
    python -m pip install -r requirements.txt
    
    if errorlevel 1 (
        echo.
        echo   ERROR: Dependency installation failed
        echo.
        echo   MANUAL FIX:
        echo   Open terminal here and run: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    
    echo.
    echo   Dependencies installed successfully!
    echo.
)

echo [4/5] Dependencies: OK
timeout /t 1 /nobreak >nul

REM ============================================================================
REM STEP 3: Create logs directory if missing
REM ============================================================================

if not exist "logs" mkdir logs
echo [5/5] Environment: OK

REM ============================================================================
REM STEP 4: Launch Application
REM ============================================================================

:launch
cls
echo.
echo ======================================================================
echo   Starting YouTube2Sheets...
echo ======================================================================
echo.
echo   All systems ready. Launching GUI...
echo.
echo   TIP: This window will close when you exit the application.
echo        To see logs, check: logs\youtube2sheets.log
echo.
echo ======================================================================
echo.

REM Launch with pythonw for clean GUI (no console)
REM Fall back to python if pythonw not available
where pythonw >nul 2>&1
if not errorlevel 1 (
    start "" pythonw youtube_to_sheets_gui.py
    timeout /t 2 /nobreak >nul
    exit
) else (
    python youtube_to_sheets_gui.py
)

REM ============================================================================
REM STEP 5: Post-Exit Handler
REM ============================================================================

if errorlevel 1 (
    echo.
    echo ======================================================================
    echo   Application Exit With Error
    echo ======================================================================
    echo.
    echo   The application encountered an error.
    echo.
    echo   TROUBLESHOOTING:
    echo   1. Check logs: logs\youtube2sheets.log
    echo   2. Verify .env file exists with API keys
    echo   3. Verify credentials.json exists
    echo   4. Try running: python youtube_to_sheets_gui.py
    echo.
    echo ======================================================================
    pause
    exit /b 1
)

REM Clean exit
exit /b 0


