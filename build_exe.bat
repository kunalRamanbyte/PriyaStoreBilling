@echo off
:: ============================================================
:: build_exe.bat — Build Kunal's FMCG Billing System .exe
:: Run this from the billing\ folder
:: Output:  dist\KunalBilling\KunalBilling.exe
:: ============================================================

echo.
echo ================================================
echo   Kunal's FMCG Billing System — EXE Builder
echo ================================================
echo.

:: Step 1: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Make sure Python is in PATH.
    pause
    exit /b 1
)

:: Step 2: Install / upgrade required packages
echo [1/4] Installing required packages...
python -m pip install --upgrade pyinstaller customtkinter pillow openpyxl reportlab --quiet
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)

:: Step 3: Clean previous build
echo [2/4] Cleaning previous build...
if exist build     rmdir /s /q build
if exist dist      rmdir /s /q dist

:: Step 4: Run PyInstaller
echo [3/4] Building EXE with PyInstaller...
python -m PyInstaller billing.spec --noconfirm
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed. See above for details.
    pause
    exit /b 1
)

:: Step 5: Copy sample DB placeholder so app can find its path
echo [4/4] Finalising output folder...
if not exist dist\KunalBilling\backups mkdir dist\KunalBilling\backups

echo.
echo ================================================
echo   BUILD SUCCESSFUL!
echo   Output: dist\KunalBilling\KunalBilling.exe
echo.
echo   To distribute, zip the entire dist\KunalBilling\
echo   folder and share it. The exe runs without Python.
echo ================================================
echo.
pause
