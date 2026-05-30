@echo off
title Kunal's FMCG Billing System - Setup
color 1F

echo ============================================
echo   Kunal's FMCG Billing System - Phase 1
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from https://python.org
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo [1/2] Installing required packages...
pip install customtkinter Pillow openpyxl reportlab --quiet --upgrade
echo       Done!
echo.

echo [2/2] Starting billing system...
echo       Login: admin / admin123
echo.
python main.py

pause
