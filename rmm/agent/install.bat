@echo off
:: LetUsTech RMM Agent - Installer
:: Must be run as Administrator

echo LetUsTech RMM Agent Installer
echo ================================

:: Check admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Please run this script as Administrator.
    pause
    exit /b 1
)

:: Check config.json exists
if not exist "%~dp0config.json" (
    echo ERROR: config.json not found.
    echo Please copy config-template.json to config.json and fill in your Firebase details.
    pause
    exit /b 1
)

set AGENT_PATH=%~dp0agent.ps1
set TASK_NAME=LetUsTechRMMAgent

:: Remove old task if exists
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

:: Create scheduled task - runs every 5 minutes as SYSTEM
schtasks /create ^
  /tn "%TASK_NAME%" ^
  /tr "powershell.exe -ExecutionPolicy Bypass -NonInteractive -WindowStyle Hidden -File \"%AGENT_PATH%\"" ^
  /sc MINUTE ^
  /mo 5 ^
  /ru SYSTEM ^
  /rl HIGHEST ^
  /f

if %errorlevel% equ 0 (
    echo.
    echo Agent installed successfully!
    echo Task: %TASK_NAME%
    echo Runs every 5 minutes as SYSTEM.
    echo.
    echo Running first check now...
    powershell.exe -ExecutionPolicy Bypass -NonInteractive -WindowStyle Hidden -File "%AGENT_PATH%"
    echo Done! Device will appear in the dashboard within 30 seconds.
) else (
    echo ERROR: Failed to create scheduled task.
)

pause
