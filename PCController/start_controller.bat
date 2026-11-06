@echo off
setlocal
cd /d "E:\personal AI\PCController"

:: Check if port 8000 is already running
netstat -ano | findstr :8000 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    exit /b 0
)

:: Launch pythonw directly (pythonw runs without any console window natively)
start "" "E:\personal AI\PCController\.venv\Scripts\pythonw.exe" "E:\personal AI\PCController\main.py"
exit /b 0

