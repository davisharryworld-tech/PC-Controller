@echo off
setlocal
cd /d "E:\personal AI\PCController"

:: Check if already running
netstat -ano | findstr :8000 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    exit /b 0
)

:: Run python main.py
".venv\Scripts\python.exe" main.py

