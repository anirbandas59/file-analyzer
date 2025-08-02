@echo off
setlocal EnableDelayedExpansion

echo ========================================
echo     FileAnalyzer - Smart File Management
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Found Python !PYTHON_VERSION!

:: Check Python version (minimum 3.10)
for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set MAJOR=%%a
    set MINOR=%%b
)
if !MAJOR! LSS 3 (
    echo ERROR: Python 3.10+ required, found !PYTHON_VERSION!
    pause
    exit /b 1
)
if !MAJOR! EQU 3 if !MINOR! LSS 10 (
    echo ERROR: Python 3.10+ required, found !PYTHON_VERSION!
    pause
    exit /b 1
)

echo Python version check passed
echo.

:: Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Check if requirements are installed
python -c "import PyQt6; import src.main" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install --upgrade pip
    if exist "requirements.txt" (
        pip install -r requirements.txt
    ) else (
        pip install .
    )
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully
) else (
    echo Dependencies already installed
)

echo.
echo ========================================
echo Starting FileAnalyzer...
echo ========================================
echo.

:: Launch the application
python -m src.main

:: Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    pause
)

echo.
echo Application closed. Press any key to exit.
pause >nul