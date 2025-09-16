@echo off
REM YouTube2Sheets Windows Launcher
REM ================================

echo 🚀 Starting YouTube2Sheets...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Launch the application
echo 🎯 Launching YouTube2Sheets...
python launch_youtube2sheets.py

pause