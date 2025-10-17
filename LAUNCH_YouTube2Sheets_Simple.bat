@echo off
echo.
echo ========================================
echo   YouTube2Sheets - Modern 2025
echo ========================================
echo.

cd /d "%~dp0"

echo Starting YouTube2Sheets...
python RUN_ME.pyw

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start YouTube2Sheets
    echo.
    echo Please try:
    echo 1. python -m pip install -r requirements.txt
    echo 2. python -c "from src.gui.beautiful_ui import launch; launch()"
    echo.
    pause
)
