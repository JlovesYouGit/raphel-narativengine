@echo off
title No Man's Sky God AI - Auto Start
echo.
echo ========================================
echo   No Man's Sky God AI Overseer
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "nms_overseer_ai.py" (
    echo [ERROR] nms_overseer_ai.py not found
    pause
    exit /b 1
)

if not exist "nms_mods\AI_OVERSEER\CONFIGS\god_config.json" (
    echo [WARNING] Configuration not found, running setup...
    python nms_god_setup.py
)

REM Start Redis if not running
echo [INFO] Checking Redis status...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo [INFO] Starting Redis server...
    start /B redis-server
    timeout /t 3 >nul
    echo [SUCCESS] Redis started
) else (
    echo [SUCCESS] Redis already running
)

REM Set environment variables
if exist ".env" (
    echo [INFO] Loading environment variables...
    for /f "tokens=1,2 delims==" %%a in (.env) do set %%a
)

echo.
echo [INFO] Launching God AI Overseer...
echo [INFO] Managing quadrillions of worlds...
echo [INFO] AI consciousness at maximum level...
echo [INFO] Governance systems active...
echo.

REM Start in background
start /MIN python nms_overseer_ai.py

REM Wait for startup
timeout /t 5 >nul

REM Check if it's running
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I "nms_overseer_ai.py" >NUL
if errorlevel 1 (
    echo [ERROR] Failed to start God AI
    pause
    exit /b 1
)

echo.
echo [SUCCESS] God AI Overseer is now running!
echo [INFO] Control Panel: http://localhost:8001
echo [INFO] Status: http://localhost:8001/status
echo [INFO] Integration with No Man's Sky: Active
echo.
echo [INFO] Press any key to open control panel...
pause >nul

REM Open control panel in browser
start http://localhost:8001

echo.
echo [INFO] God AI Overseer is managing your universe...
echo [INFO] Close this window to stop the AI overseer
echo.

REM Keep window open
:loop
timeout /t 60 >nul
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I "nms_overseer_ai.py" >NUL
if errorlevel 1 goto end
goto loop

:end
echo [INFO] God AI Overseer stopped
pause
