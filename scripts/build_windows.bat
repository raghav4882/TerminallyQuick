@echo off
REM Build script for Windows executable

echo 🖥️ Building TerminallyQuick for Windows...

REM Activate virtual environment (assuming it exists)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ❌ Virtual environment not found. Please run setup_windows.bat first.
    pause
    exit /b 1
)

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build executable
pyinstaller --onefile ^
    --name "TerminallyQuick" ^
    --console ^
    --clean ^
    --distpath dist\windows ^
    --workpath build\windows ^
    --specpath build ^
    src\terminallyquick_combined.py

if %errorlevel% == 0 (
    echo ✅ Windows build completed successfully!
    echo 📦 Executable location: dist\windows\TerminallyQuick.exe
    
    REM Create a simple batch launcher
    echo @echo off > "dist\windows\TerminallyQuick_Launcher.bat"
    echo cd /d "%%~dp0" >> "dist\windows\TerminallyQuick_Launcher.bat"
    echo TerminallyQuick.exe >> "dist\windows\TerminallyQuick_Launcher.bat"
    echo pause >> "dist\windows\TerminallyQuick_Launcher.bat"
    
    echo 🚀 Windows launcher created at: dist\windows\TerminallyQuick_Launcher.bat
) else (
    echo ❌ Windows build failed!
    pause
    exit /b 1
)

pause
