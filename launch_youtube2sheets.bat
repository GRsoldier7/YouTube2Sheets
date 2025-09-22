@echo off
REM YouTube2Sheets Windows Launcher
REM This script launches the YouTube2Sheets application on Windows

echo 🚀 Starting YouTube2Sheets...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
if not exist "venv\Scripts\pip.exe" (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
)

REM Check if environment files exist
if not exist ".env" (
    echo 🔧 Setting up environment...
    python setup_secure_environment.py
)

REM Launch the application
echo 🎯 Launching YouTube2Sheets GUI...
python youtube_to_sheets_gui.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
echo ❌ Application exited with error
pause
)

pause