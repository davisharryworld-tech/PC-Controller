@echo off
setlocal
cd /d "E:\personal AI\PCController"

:: Check if port 8000 is already active
netstat -ano | findstr :8000 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    exit /b 0
)

:: Start using standard python in background process
start "" /b "E:\personal AI\PCController\.venv\Scripts\python.exe" "E:\personal AI\PCController\main.py"
exit /b 0
