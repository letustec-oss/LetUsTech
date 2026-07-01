@echo off
title Invoice Generator

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

:: Install dependencies if needed
echo Checking dependencies...
pip install reportlab Pillow --quiet --break-system-packages 2>nul || pip install reportlab Pillow --quiet

:: Launch app
echo Starting Invoice Generator...
python invoice_app.py

if errorlevel 1 (
    echo.
    echo [ERROR] App failed to start. Make sure Python and pip are installed.
    pause
)
