@echo off
setlocal

echo.
echo 🧪 TESTING YOUTUBE2SHEETS ICON LAUNCHER
echo ======================================
echo.

:: Get the directory of the batch script
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo 📍 Working directory: %CD%
echo.

:: Check if files exist
echo 🔍 Checking required files...
if exist "LAUNCH_GUI.pyw" (
    echo ✅ LAUNCH_GUI.pyw found
) else (
    echo ❌ LAUNCH_GUI.pyw NOT found
    goto :error
)

if exist "YouTube2Sheets.ico" (
    echo ✅ YouTube2Sheets.ico found
) else (
    echo ❌ YouTube2Sheets.ico NOT found
    goto :error
)

:: Check Python
echo.
echo 🐍 Checking Python...
where pythonw >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ pythonw.exe found
    set "PYTHON_EXE=pythonw"
) else (
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ python.exe found
        set "PYTHON_EXE=python"
    ) else (
        echo ❌ Python not found
        goto :error
    )
)

:: Test the launcher
echo.
echo 🚀 Testing launcher...
echo This should open the YouTube2Sheets GUI window...
echo.

start "" "%PYTHON_EXE%" "LAUNCH_GUI.pyw"

echo.
echo ✅ Launcher started! Check for the GUI window.
echo If you don't see a window, it might be behind other windows.
echo.

pause
goto :end

:error
echo.
echo ❌ ERROR: Missing required files or Python
echo Please ensure all files are present and Python is installed.
echo.
pause
exit /b 1

:end
endlocal

