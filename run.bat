@echo off

REM TerminallyQuick Runner Script for Windows
REM This script activates the virtual environment and runs the application

setlocal enabledelayedexpansion

REM Enhanced Python detection
echo 🔍 Detecting best Python installation...

set "best_python="
set "best_version=0"

REM Check for Python in PATH first
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "python_version=%%i"
    
    REM Extract version number for comparison
    for /f "tokens=1,2 delims=." %%a in ("!python_version!") do (
        set "major=%%a"
        set "minor=%%b"
    )
    
    REM Check if version is 3.6+
    if !major! equ 3 (
        if !minor! geq 6 (
            set "best_python=python"
            set "best_version=!python_version!"
        )
    )
)

REM Check for Python3 specifically
if not defined best_python (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set "python_version=%%i"
        
        for /f "tokens=1,2 delims=." %%a in ("!python_version!") do (
            set "major=%%a"
            set "minor=%%b"
        )
        
        if !major! equ 3 (
            if !minor! geq 6 (
                set "best_python=python3"
                set "best_version=!python_version!"
            )
        )
    )
)

REM Check common Python installation locations
if not defined best_python (
    REM Check Program Files
    if exist "C:\Program Files\Python3*\python.exe" (
        for /d %%i in ("C:\Program Files\Python3*") do (
            if exist "%%i\python.exe" (
                "%%i\python.exe" --version >nul 2>&1
                if !errorlevel! equ 0 (
                    for /f "tokens=2" %%j in ('"%%i\python.exe" --version 2^>^&1') do set "python_version=%%j"
                    
                    for /f "tokens=1,2 delims=." %%a in ("!python_version!") do (
                        set "major=%%a"
                        set "minor=%%b"
                    )
                    
                    if !major! equ 3 (
                        if !minor! geq 6 (
                            set "best_python=%%i\python.exe"
                            set "best_version=!python_version!"
                        )
                    )
                )
            )
        )
    )
    
    REM Check Program Files (x86)
    if exist "C:\Program Files (x86)\Python3*\python.exe" (
        for /d %%i in ("C:\Program Files (x86)\Python3*") do (
            if exist "%%i\python.exe" (
                "%%i\python.exe" --version >nul 2>&1
                if !errorlevel! equ 0 (
                    for /f "tokens=2" %%j in ('"%%i\python.exe" --version 2^>^&1') do set "python_version=%%j"
                    
                    for /f "tokens=1,2 delims=." %%a in ("!python_version!") do (
                        set "major=%%a"
                        set "minor=%%b"
                    )
                    
                    if !major! equ 3 (
                        if !minor! geq 6 (
                            set "best_python=%%i\python.exe"
                            set "best_version=!python_version!"
                        )
                    )
                )
            )
        )
    )
    
    REM Check user AppData
    if exist "%LOCALAPPDATA%\Programs\Python\Python3*\python.exe" (
        for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
            if exist "%%i\python.exe" (
                "%%i\python.exe" --version >nul 2>&1
                if !errorlevel! equ 0 (
                    for /f "tokens=2" %%j in ('"%%i\python.exe" --version 2^>^&1') do set "python_version=%%j"
                    
                    for /f "tokens=1,2 delims=." %%a in ("!python_version!") do (
                        set "major=%%a"
                        set "minor=%%b"
                    )
                    
                    if !major! equ 3 (
                        if !minor! geq 6 (
                            set "best_python=%%i\python.exe"
                            set "best_version=!python_version!"
                        )
                    )
                )
            )
        )
    )
)

REM Fallback to python if detection failed
if not defined best_python (
    if command -v python >nul 2>&1 (
        set "best_python=python"
        echo ⚠️ Using fallback: python
    ) else (
        echo ❌ No compatible Python found!
        echo Please install Python 3.6+ and try again.
        pause
        exit /b 1
    )
) else (
    echo ✅ Using Python: !best_python! (v!best_version!)
)

REM Check if virtual environment exists
if not exist venv\Scripts\activate.bat (
    echo Creating virtual environment...
    "!best_python!" -m venv venv
    
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Install/upgrade dependencies
echo Installing dependencies...
pip install --quiet --upgrade pip

REM Try to install from requirements.txt first
echo 📦 Installing from requirements.txt...
pip install --quiet -r requirements.txt
if !errorlevel! equ 0 (
    echo ⚠️ Package list install failed. Trying individual packages...
    
    REM Install packages individually with better error handling
    echo 📦 Installing Pillow (image processing)...
    pip install --quiet Pillow
    if !errorlevel! equ 0 (
        echo ❌ Failed to install Pillow
        echo 💡 This might be due to missing system dependencies or network issues
        echo 🌐 Please check your internet connection and try again
        pause
        exit /b 1
    ) else (
        echo ✅ Pillow installed successfully!
    )
    
    echo 📦 Installing colorama (terminal colors)...
    pip install --quiet colorama
    if !errorlevel! equ 0 (
        echo ❌ Failed to install colorama
        echo 💡 This might be due to missing system dependencies or network issues
        echo 🌐 Please check your internet connection and try again
        pause
        exit /b 1
    ) else (
        echo ✅ colorama installed successfully!
    )
) else (
    echo ✅ Dependencies installed successfully from requirements.txt!
)

REM Verify the packages are installed
echo 🔍 Verifying installed packages...
python -c "import PIL; print('✅ PIL/Pillow found')" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ PIL/Pillow verification successful!
) else (
    echo ❌ PIL/Pillow not found in virtual environment!
    echo 💡 Trying to reinstall...
    pip install --quiet --force-reinstall Pillow
    python -c "import PIL; print('✅ PIL/Pillow found')" >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ PIL/Pillow reinstall successful!
    ) else (
        echo ❌ Failed to install PIL/Pillow
        echo 💡 This might be due to missing system dependencies
        echo 📋 On Windows, you might need Visual C++ redistributables
        pause
        exit /b 1
    )
)

python -c "import colorama; print('✅ colorama found')" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ colorama verification successful!
) else (
    echo ❌ colorama not found in virtual environment!
    echo 💡 Trying to reinstall...
    pip install --quiet --force-reinstall colorama
    python -c "import colorama; print('✅ colorama found')" >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ colorama reinstall successful!
    ) else (
        echo ❌ Failed to install colorama
        pause
        exit /b 1
    )
)

REM Run the application
echo Starting TerminallyQuick...
python src\terminallyquick_combined.py

pause
