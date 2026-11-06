@echo off
setlocal
cd /d "E:\personal AI\PCController"

:: Kill any existing process on port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

exit /b 0
