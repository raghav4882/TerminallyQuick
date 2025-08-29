@echo off

echo 🖥️ Setting up TerminallyQuick development environment for Windows...

REM Check if Python 3 is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3 is not installed. Please install Python 3.7+ first.
    echo    You can download it from https://www.python.org/
    echo    Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo ✅ Python found: 
python --version

REM Check if exiftool is installed (required for CR3 support)
exiftool -ver >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  exiftool not found. Please install it manually for CR3 support:
    echo    Visit: https://exiftool.org/install.html#Windows
    echo    Download and install exiftool for Windows
    echo    Note: The application will work without exiftool, but CR3 files won't be supported.
) else (
    echo ✅ exiftool found
)

REM Create virtual environment
echo 🏗️ Creating virtual environment...
python -m venv venv

REM Activate virtual environment and install dependencies
echo 📦 Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📋 Next steps:
echo    1. Run the application: run.bat
echo    2. Build executable: scripts\build_windows.bat

pause
