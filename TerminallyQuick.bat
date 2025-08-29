@echo off
setlocal enabledelayedexpansion

REM TerminallyQuick Windows Launcher - 100% Safe & Non-Invasive
REM Double-click this file to run TerminallyQuick
REM NEVER modifies your system - only works within this folder!

cd /d "%~dp0"

REM Create required folders automatically
if not exist input_images mkdir input_images
if not exist resized_images mkdir resized_images

REM Add welcome file to input_images if empty
dir /b input_images 2>nul | findstr /r ".*" >nul
if %errorlevel% neq 0 (
    echo Welcome to TerminallyQuick! > input_images\README_ADD_IMAGES_HERE.txt
    echo. >> input_images\README_ADD_IMAGES_HERE.txt  
    echo Drop your images in this folder, then run TerminallyQuick again. >> input_images\README_ADD_IMAGES_HERE.txt
    echo Supported formats: PNG, JPEG, WEBP, CR3, BMP, TIFF, and more! >> input_images\README_ADD_IMAGES_HERE.txt
)

echo 🚀 TerminallyQuick v2.0 - 100% Safe Launcher
echo ===============================================
echo ℹ️ This launcher NEVER modifies your system!
echo 📁 Everything stays within this project folder.
echo 🔓 Open Source: All dependencies respect their licenses
echo 💚 100% local: No system-wide installations
echo.

REM === Enhanced Python Detection ===
echo 🔍 Searching for Python installations...

set "best_python="
set "best_version=0"

REM Check for Python in PATH first
echo 🔍 Checking PATH for Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "python_version=%%i"
    echo   ✅ Found in PATH: python (v!python_version!)
    
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
    echo 🔍 Checking for python3...
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set "python_version=%%i"
        echo   ✅ Found: python3 (v!python_version!)
        
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
    echo 🔍 Checking common installation locations...
    
    REM Check Program Files
    if exist "C:\Program Files\Python3*\python.exe" (
        for /d %%i in ("C:\Program Files\Python3*") do (
            if exist "%%i\python.exe" (
                "%%i\python.exe" --version >nul 2>&1
                if !errorlevel! equ 0 (
                    for /f "tokens=2" %%j in ('"%%i\python.exe" --version 2^>^&1') do set "python_version=%%j"
                    echo   ✅ Found: %%i\python.exe (v!python_version!)
                    
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
                    echo   ✅ Found: %%i\python.exe (v!python_version!)
                    
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
                    echo   ✅ Found: %%i\python.exe (v!python_version!)
                    
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

if not defined best_python (
    echo ❌ No compatible Python 3.6+ found on your system!
    echo.
    echo 🚀 CHOOSE YOUR INSTALLATION METHOD:
    echo    [1] Download Python installer (Recommended - installs system-wide)
    echo    [2] Use Microsoft Store: Search for "Python 3.11"
    echo    [3] Manually specify Python path
    echo    [Q] Quit
    echo.
    echo 🛡️ This launcher will NOT auto-install Python to keep your system safe.
    echo.
    
    :choice_loop
    set /p choice="Choose option [1/2/3/Q]: "
    
    if /i "!choice!"=="1" (
        echo.
        echo 🌐 Opening Python download page...
        start https://www.python.org/downloads/
        echo 💡 After installing Python, run this launcher again!
        echo Press any key to exit...
        pause >nul
        exit /b 1
    ) else if /i "!choice!"=="2" (
        echo.
        echo 🏪 Opening Microsoft Store...
        start ms-windows-store://pdp/?ProductId=9NRWMJP3717K
        echo 💡 After installing Python from Store, run this launcher again!
        echo Press any key to exit...
        pause >nul
        exit /b 1
    ) else if /i "!choice!"=="3" (
        echo.
        echo 🔍 Manual Python path specification:
        echo 💡 Examples:
        echo    • C:\Python311\python.exe
        echo    • C:\Program Files\Python311\python.exe
        echo    • C:\Users\username\AppData\Local\Programs\Python\Python311\python.exe
        echo.
        set /p custom_python="Enter full path to Python executable: "
        
        if exist "!custom_python!" (
            "!custom_python!" --version >nul 2>&1
            if !errorlevel! equ 0 (
                for /f "tokens=2" %%i in ('"!custom_python!" --version 2^>^&1') do set "python_version=%%i"
                echo ✅ Custom Python found: !custom_python! (v!python_version!)
                
                for /f "tokens=1,2 delims=." %%a in ("!python_version!") do (
                    set "major=%%a"
                    set "minor=%%b"
                )
                
                if !major! equ 3 (
                    if !minor! geq 6 (
                        set "best_python=!custom_python!"
                        set "best_version=!python_version!"
                    ) else (
                        echo ❌ Python version too old: !python_version!
                        echo    TerminallyQuick requires Python 3.6+
                        echo Press any key to exit...
                        pause >nul
                        exit /b 1
                    )
                ) else (
                    echo ❌ Python version too old: !python_version!
                    echo    TerminallyQuick requires Python 3.6+
                    echo Press any key to exit...
                    pause >nul
                    exit /b 1
                )
            ) else (
                echo ❌ Python verification failed!
                echo Press any key to exit...
                pause >nul
                exit /b 1
            )
        ) else (
            echo ❌ Invalid path: !custom_python!
            echo Press any key to exit...
            pause >nul
            exit /b 1
        )
    ) else if /i "!choice!"=="Q" (
        exit /b 0
    ) else (
        echo Please choose 1, 2, 3, or Q
        goto choice_loop
    )
)

REM Use the detected best Python
echo ✅ Using Python: !best_python! (v!best_version!)

REM Verify the Python works
"!best_python!" -c "import sys; print('Python check passed')" >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Python verification failed!
    echo 💡 The detected Python installation may be corrupted.
    echo 📋 Try reinstalling Python or use the manual path option.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo.
echo 📦 Setting up project dependencies...
echo 🛡️ All libraries install ONLY in this folder - your system stays clean!

REM Check if virtual environment exists
if not exist venv\Scripts\activate.bat (
    echo 🏗️ Creating isolated environment in this folder...
    "!best_python!" -m venv venv
    if !errorlevel! neq 0 (
        echo ❌ Failed to create virtual environment.
        echo 💡 This might happen if you have an incomplete Python installation.
        echo 📋 Try reinstalling Python from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    echo ✅ Isolated environment created successfully!
) else (
    echo ✅ Found existing isolated environment - using it!
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo ⬇️ Installing required libraries in isolated environment...
echo 📚 Libraries: Pillow (image processing), colorama (colors)
echo 📍 Install location: %CD%\venv (NOT your system!)

REM Upgrade pip first
pip install --quiet --upgrade pip

REM Try to install from requirements.txt first
echo 📦 Installing from requirements.txt...
pip install --quiet -r requirements.txt
if !errorlevel! equ 0 (
    echo ✅ Dependencies installed successfully from requirements.txt!
) else (
    echo ⚠️ Package list install failed. Trying individual packages...
    
    REM Install packages individually with better error handling
    echo 📦 Installing Pillow (image processing)...
    pip install --quiet Pillow
    if !errorlevel! equ 0 (
        echo ✅ Pillow installed successfully!
    ) else (
        echo ❌ Failed to install Pillow
        echo 💡 This might be due to missing system dependencies or network issues
        echo 🌐 Please check your internet connection and try again
        pause
        exit /b 1
    )
    
    echo 📦 Installing colorama (terminal colors)...
    pip install --quiet colorama
    if !errorlevel! equ 0 (
        echo ✅ colorama installed successfully!
    ) else (
        echo ❌ Failed to install colorama
        echo 💡 This might be due to missing system dependencies or network issues
        echo 🌐 Please check your internet connection and try again
        pause
        exit /b 1
    )
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

REM Check for exiftool (optional, for CR3 RAW support)
echo.
echo 🔍 Checking for optional tools...
exiftool -ver >nul 2>&1
if !errorlevel! neq 0 (
    echo ℹ️ exiftool not found (needed only for Canon CR3/RAW files)
    echo 📸 You can still process: PNG, JPEG, WEBP, AVIF, BMP, TIFF, etc.
    echo 🔧 To add CR3 support later, install exiftool:
    echo    • Download from: https://exiftool.org/install.html#Windows
    echo    • Or use Chocolatey: choco install exiftool
    echo ⏭️ Continuing without CR3 support...
) else (
    echo ✅ exiftool found - CR3/RAW support available! 📸
)

echo.
echo ✅ All dependencies ready! Everything is contained in this folder. 🛡️
echo.
echo 🚀 Starting TerminallyQuick v2.0...
echo.

REM Run the application using the virtual environment Python
python src\terminallyquick_combined.py

REM Keep terminal open so user can see any final messages
echo.
echo 📁 Check the 'resized_images' folder for your processed images!
pause
