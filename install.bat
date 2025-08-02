@echo off
echo File System Analyzer - Windows Setup Script
echo =========================================
echo.

:: Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.8 or later.
    echo Visit https://www.python.org/downloads/windows/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    echo After installing Python, run this script again.
    pause
    exit /b 1
)

echo Python is installed.
echo.

:: Ask if user wants to create a virtual environment
set /p create_venv="Do you want to create a virtual environment? (y/n): "
if /i "%create_venv%"=="y" (
    echo Creating virtual environment...
    python -m venv venv
    
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    
    echo Virtual environment created and activated.
    echo.
)

:: Install dependencies
echo Installing dependencies...
pip install PyQt6
if %errorlevel% neq 0 (
    echo Failed to install dependencies. Please check your internet connection.
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo.
echo To run the application:
if /i "%create_venv%"=="y" (
    echo - Activate the virtual environment: venv\Scripts\activate
)
echo - Run: python -m src.main
echo - Or double-click on run.bat
echo.

:: Ask if user wants to run the application now
set /p run_now="Do you want to run the application now? (y/n): "
if /i "%run_now%"=="y" (
    echo Starting File System Analyzer...
    python -m src.main
)

pause