@echo off
echo Starting No Man's Sky God AI Overseer...
echo.
echo ========================================
echo God AI Overseer Control Panel
echo ========================================
echo.
echo 1. Start God AI Overseer
echo 2. View World Status
echo 3. Manual Intervention
echo 4. Configuration
echo 5. Exit
echo.
set /p choice="Select option: "
if "%choice%"=="1" goto start
if "%choice%"=="2" goto status
if "%choice%"=="3" goto intervene
if "%choice%"=="4" goto config
if "%choice%"=="5" goto exit

:start
echo Starting God AI Overseer...
python nms_overseer_ai.py
goto menu

:status
echo Getting world status...
curl http://localhost:8001/status
pause
goto menu

:intervene
echo Manual Intervention Mode
echo Available interventions: boost, disaster, migration
set /p world_id="Enter world ID: "
set /p intervention_type="Enter intervention type: "
curl -X POST http://localhost:8001/intervene/%world_id% -H "Content-Type: application/json" -d "{"type": "%intervention_type%"}"
pause
goto menu

:config
echo Opening configuration...
notepad nms_mods/AI_OVERSEER/CONFIGS/god_config.json
goto menu

:exit
exit

:menu
goto :eof
