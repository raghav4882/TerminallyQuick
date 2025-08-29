#!/bin/bash

# TerminallyQuick macOS Launcher - 100% Safe & Non-Invasive
# Double-click this file to run TerminallyQuick
# NEVER modifies your system - only works within this folder!

cd "$(dirname "$0")"

# Create required folders automatically
mkdir -p input_images resized_images

# Add welcome file to input_images if empty
if [ ! "$(ls -A input_images 2>/dev/null)" ]; then
    echo "Welcome to TerminallyQuick!" > input_images/README_ADD_IMAGES_HERE.txt
    echo "" >> input_images/README_ADD_IMAGES_HERE.txt
    echo "Drop your images in this folder, then run TerminallyQuick again." >> input_images/README_ADD_IMAGES_HERE.txt
    echo "Supported formats: PNG, JPEG, WEBP, CR3, BMP, TIFF, and more!" >> input_images/README_ADD_IMAGES_HERE.txt
fi

echo "🚀 TerminallyQuick v2.0 - 100% Safe Launcher"
echo "============================================="
echo "ℹ️ This launcher NEVER modifies your system!"
echo "📁 Everything stays within this project folder."
echo "🔓 Open Source: All dependencies respect their licenses"
echo "💚 100% local: No system-wide installations"
echo ""

# === Enhanced Python Detection ===
echo "🔍 Searching for Python installations..."

# Function to get Python version as comparable number
get_python_version_number() {
    local python_path="$1"
    if [ -x "$python_path" ]; then
        $python_path -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor:02d}{sys.version_info.micro:02d}')" 2>/dev/null
    else
        echo "0"
    fi
}

# Function to check if Python version is compatible (3.6+)
is_python_compatible() {
    local version_num="$1"
    if [ -z "$version_num" ] || [ "$version_num" = "0" ]; then
        return 1
    fi
    
    # Extract major and minor version
    local major="${version_num:0:1}"
    local minor="${version_num:1:2}"
    
    # Python 3.6+ means major=3 and minor>=6
    if [ "$major" = "3" ] && [ "$minor" -ge 6 ]; then
        return 0
    fi
    
    return 1
}

# Function to get readable Python version
get_python_version_readable() {
    local python_path="$1"
    if [ -x "$python_path" ]; then
        $python_path -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null
    else
        echo "unknown"
    fi
}

# Search for Python installations in common locations
declare -a python_candidates=()
declare -a python_paths=()

# Homebrew locations (prefer these)
echo "🔍 Checking Homebrew locations..."
# Use find to locate Python executables in Homebrew directories
for py_path in $(find /opt/homebrew/bin/python3* -type f -executable 2>/dev/null | head -10); do
    if [ -x "$py_path" ]; then
        version_num=$(get_python_version_number "$py_path")
        if is_python_compatible "$version_num"; then
            python_candidates+=("$version_num")
            python_paths+=("$py_path")
            echo "  ✅ Found: $py_path (v$(get_python_version_readable "$py_path"))"
        fi
    fi
done

# Also check /usr/local for older Homebrew installations
for py_path in $(find /usr/local/bin/python3* -type f -executable 2>/dev/null | head -10); do
    if [ -x "$py_path" ]; then
        version_num=$(get_python_version_number "$py_path")
        if is_python_compatible "$version_num"; then
            python_candidates+=("$version_num")
            python_paths+=("$py_path")
            echo "  ✅ Found: $py_path (v$(get_python_version_readable "$py_path"))"
        fi
    fi
done

# System Python (lower priority)
echo "🔍 Checking system locations..."
# Use find to locate Python executables in system directories
for py_path in $(find /usr/bin/python3* -type f -executable 2>/dev/null | head -10); do
    if [ -x "$py_path" ]; then
        version_num=$(get_python_version_number "$py_path")
        if is_python_compatible "$version_num"; then
            python_candidates+=("$version_num")
            python_paths+=("$py_path")
            echo "  ✅ Found: $py_path (v$(get_python_version_readable "$py_path"))"
        fi
    fi
done

# Python Framework locations (common on macOS)
echo "🔍 Checking Python Framework locations..."
# Use find to locate Python executables in framework directories
for py_path in $(find /Library/Frameworks/Python.framework/Versions/ -name "python3*" -type f 2>/dev/null | grep "/bin/python3" | head -10); do
    if [ -x "$py_path" ]; then
        version_num=$(get_python_version_number "$py_path")
        if is_python_compatible "$version_num"; then
            python_candidates+=("$version_num")
            python_paths+=("$py_path")
            echo "  ✅ Found: $py_path (v$(get_python_version_readable "$py_path"))"
        fi
    fi
done

# Also check System frameworks
for py_path in $(find /System/Library/Frameworks/Python.framework/Versions/ -name "python3*" -type f 2>/dev/null | grep "/bin/python3" | head -10); do
    if [ -x "$py_path" ]; then
        version_num=$(get_python_version_number "$py_path")
        if is_python_compatible "$version_num"; then
            python_candidates+=("$version_num")
            python_paths+=("$py_path")
            echo "  ✅ Found: $py_path (v$(get_python_version_readable "$py_path"))"
        fi
    fi
done

# Check PATH for python3
echo "🔍 Checking PATH..."
if command -v python3 &> /dev/null; then
    path_python=$(command -v python3)
    version_num=$(get_python_version_number "$path_python")
    if is_python_compatible "$version_num"; then
        # Only add if not already in our list
        if [[ ! " ${python_paths[@]} " =~ " ${path_python} " ]]; then
            python_candidates+=("$version_num")
            python_paths+=("$path_python")
            echo "  ✅ Found in PATH: $path_python (v$(get_python_version_readable "$path_python"))"
        fi
    fi
fi

# Find the best Python version
best_python=""
best_version_num=0
best_index=-1

for i in "${!python_candidates[@]}"; do
    if [ "${python_candidates[$i]}" -gt "$best_version_num" ]; then
        best_version_num="${python_candidates[$i]}"
        best_python="${python_paths[$i]}"
        best_index=$i
    fi
done

if [ -z "$best_python" ]; then
    echo "❌ No compatible Python 3.6+ found on your system!"
    echo ""
    echo "🚀 CHOOSE YOUR INSTALLATION METHOD:"
    echo "   [1] Download Python installer (Recommended - installs system-wide)"
    echo "   [2] Use Homebrew: brew install python@3.11"
    echo "   [3] Manually specify Python path"
    echo "   [Q] Quit"
    echo ""
    echo "🛡️ This launcher will NOT auto-install Python to keep your system safe."
    echo ""
    
    while true; do
        read -p "Choose option [1/2/3/Q]: " choice
        case $choice in
            [1])
                echo "\n🌐 Opening Python download page..."
                open "https://www.python.org/downloads/"
                echo "💡 After installing Python, run this launcher again!"
                echo "Press any key to exit..."
                read -n 1 -s
                exit 0
                ;;
            [2])
                echo "\n📋 Run this command in Terminal:"
                echo "   brew install python@3.11"
                echo "💡 Then run this launcher again!"
                echo "Press any key to exit..."
                read -n 1 -s
                exit 0
                ;;
            [3])
                echo "\n🔍 Manual Python path specification:"
                echo "💡 Examples:"
                echo "   • /opt/homebrew/bin/python3.11"
                echo "   • /usr/local/bin/python3.9"
                echo "   • /Users/username/.pyenv/versions/3.11.0/bin/python"
                echo ""
                read -p "Enter full path to Python executable: " custom_python
                
                if [ -x "$custom_python" ]; then
                    version_num=$(get_python_version_number "$custom_python")
                    if is_python_compatible "$version_num"; then
                        best_python="$custom_python"
                        echo "✅ Custom Python found: $custom_python (v$(get_python_version_readable "$custom_python"))"
                        break
                    else
                        echo "❌ Python version too old: $(get_python_version_readable "$custom_python")"
                        echo "   TerminallyQuick requires Python 3.6+"
                        echo "Press any key to exit..."
                        read -n 1 -s
                        exit 1
                    fi
                else
                    echo "❌ Invalid path or not executable: $custom_python"
                    echo "Press any key to exit..."
                    read -n 1 -s
                    exit 1
                fi
                ;;
            [Qq])
                exit 0
                ;;
            *)
                echo "Please choose 1, 2, 3, or Q"
                ;;
        esac
    done
fi

# Use the detected best Python
echo "✅ Using Python: $best_python (v$(get_python_version_readable "$best_python"))"

# Verify the Python works
if ! "$best_python" -c "import sys; print('Python check passed')" &> /dev/null; then
    echo "❌ Python verification failed!"
    echo "💡 The detected Python installation may be corrupted."
    echo "📋 Try reinstalling Python or use the manual path option."
    echo "Press any key to exit..."
    read -n 1 -s
    exit 1
fi

echo ""
echo "📦 Setting up project dependencies..."
echo "🛡️ All libraries install ONLY in this folder - your system stays clean!"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🏗️ Creating isolated environment in this folder..."
    "$best_python" -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment."
        echo "💡 This might happen if you have an incomplete Python installation."
        echo "📋 Try reinstalling Python from https://www.python.org/downloads/"
        echo "Press any key to exit..."
        read -n 1 -s
        exit 1
    fi
    echo "✅ Isolated environment created successfully!"
else
    echo "✅ Found existing isolated environment - using it!"
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "⬇️ Installing required libraries in isolated environment..."
echo "📚 Libraries: Pillow (image processing), colorama (colors)"
echo "📍 Install location: $(pwd)/venv (NOT your system!)"

# Upgrade pip first
pip install --quiet --upgrade pip

# Try to install from requirements.txt first
echo "📦 Installing from requirements.txt..."
if pip install --quiet -r requirements.txt; then
    echo "✅ Dependencies installed successfully from requirements.txt!"
else
    echo "⚠️ Package list install failed. Trying individual packages..."
    
    # Install packages individually with better error handling
    echo "📦 Installing Pillow (image processing)..."
    if pip install --quiet Pillow; then
        echo "✅ Pillow installed successfully!"
    else
        echo "❌ Failed to install Pillow"
        echo "💡 This might be due to missing system dependencies or network issues"
        echo "🌐 Please check your internet connection and try again"
        echo "Press any key to exit..."
        read -n 1 -s
        exit 1
    fi
    
    echo "📦 Installing colorama (terminal colors)..."
    if pip install --quiet colorama; then
        echo "✅ colorama installed successfully!"
    else
        echo "❌ Failed to install colorama"
        echo "💡 This might be due to missing system dependencies or network issues"
        echo "🌐 Please check your internet connection and try again"
        echo "Press any key to exit..."
        read -n 1 -s
        exit 1
    fi
fi

# Verify the packages are installed
echo "🔍 Verifying installed packages..."
if python -c "import PIL; print('✅ PIL/Pillow found')" 2>/dev/null; then
    echo "✅ PIL/Pillow verification successful!"
else
    echo "❌ PIL/Pillow not found in virtual environment!"
    echo "💡 Trying to reinstall..."
    pip install --quiet --force-reinstall Pillow
    if python -c "import PIL; print('✅ PIL/Pillow found')" 2>/dev/null; then
        echo "✅ PIL/Pillow reinstall successful!"
    else
        echo "❌ Failed to install PIL/Pillow"
        echo "💡 This might be due to missing system dependencies"
        echo "📋 On macOS, you might need: brew install libjpeg zlib"
        echo "Press any key to exit..."
        read -n 1 -s
        exit 1
    fi
fi

if python -c "import colorama; print('✅ colorama found')" 2>/dev/null; then
    echo "✅ colorama verification successful!"
else
    echo "❌ colorama not found in virtual environment!"
    echo "💡 Trying to reinstall..."
    pip install --quiet --force-reinstall colorama
    if python -c "import colorama; print('✅ colorama found')" 2>/dev/null; then
        echo "✅ colorama reinstall successful!"
    else
        echo "❌ Failed to install colorama"
        echo "Press any key to exit..."
        read -n 1 -s
        exit 1
    fi
fi

# Check for exiftool (optional, for CR3 RAW support)
echo ""
echo "🔍 Checking for optional tools..."
if ! command -v exiftool &> /dev/null; then
    echo "ℹ️ exiftool not found (needed only for Canon CR3/RAW files)"
    echo "📸 You can still process: PNG, JPEG, WEBP, AVIF, BMP, TIFF, etc."
    echo "🔧 To add CR3 support later, install exiftool:"
    echo "   • Via Homebrew: brew install exiftool"
    echo "   • Or download from: https://exiftool.org/install.html"
    echo "⏭️ Continuing without CR3 support..."
else
    echo "✅ exiftool found - CR3/RAW support available! 📸"
fi

echo "\n✅ All dependencies ready! Everything is contained in this folder. 🛡️"
echo ""

# Run the application using the virtual environment Python
echo "🚀 Starting TerminallyQuick v2.0..."
echo ""

# Use the virtual environment's Python to ensure dependencies are available
python src/terminallyquick_combined.py

# Keep terminal open so user can see any final messages
echo ""
echo "📁 Check the 'resized_images' folder for your processed images!"
echo "Press any key to exit..."
read -n 1 -s
