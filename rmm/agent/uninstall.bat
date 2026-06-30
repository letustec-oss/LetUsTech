@echo off
:: LetUsTech RMM Agent - Uninstaller

echo LetUsTech RMM Agent Uninstaller
echo ==================================

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Please run this script as Administrator.
    pause
    exit /b 1
)

set TASK_NAME=LetUsTechRMMAgent

schtasks /delete /tn "%TASK_NAME%" /f
if %errorlevel% equ 0 (
    echo Agent removed successfully.
) else (
    echo Task not found or already removed.
)

pause
