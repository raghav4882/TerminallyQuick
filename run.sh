#!/bin/bash

# Terminally Quick Runner Script
# This script activates the virtual environment and runs the application

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

# Enhanced Python detection
echo "🔍 Detecting best Python installation..."

declare -a python_candidates=()
declare -a python_paths=()

# Homebrew locations (prefer these)
for py_path in $(find /opt/homebrew/bin/python3* -type f -executable 2>/dev/null | head -10); do
    if [ -x "$py_path" ]; then
        version_num=$(get_python_version_number "$py_path")
        if is_python_compatible "$version_num"; then
            python_candidates+=("$version_num")
            python_paths+=("$py_path")
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
        fi
    fi
done

# System Python (lower priority)
for py_path in $(find /usr/bin/python3* -type f -executable 2>/dev/null | head -10); do
    if [ -x "$py_path" ]; then
        version_num=$(get_python_version_number "$py_path")
        if is_python_compatible "$version_num"; then
            python_candidates+=("$version_num")
            python_paths+=("$py_path")
        fi
    fi
done

# Check PATH for python3
if command -v python3 &> /dev/null; then
    path_python=$(command -v python3)
    version_num=$(get_python_version_number "$path_python")
    if is_python_compatible "$version_num"; then
        # Only add if not already in our list
        if [[ ! " ${python_paths[@]} " =~ " ${path_python} " ]]; then
            python_candidates+=("$version_num")
            python_paths+=("$path_python")
        fi
    fi
fi

# Python Framework locations (common on macOS)
for py_path in $(find /Library/Frameworks/Python.framework/Versions/ -name "python3*" -type f 2>/dev/null | grep "/bin/python3" | head -10); do
    if [ -x "$py_path" ]; then
        version_num=$(get_python_version_number "$py_path")
        if is_python_compatible "$version_num"; then
            python_candidates+=("$version_num")
            python_paths+=("$py_path")
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
        fi
    fi
done

# Find the best Python version
best_python=""
best_version_num=0

for i in "${!python_candidates[@]}"; do
    if [ "${python_candidates[$i]}" -gt "$best_version_num" ]; then
        best_version_num="${python_candidates[$i]}"
        best_python="${python_paths[$i]}"
    fi
done

# Fallback to python3 if detection failed
if [ -z "$best_python" ]; then
    if command -v python3 &> /dev/null; then
        best_python="python3"
        echo "⚠️ Using fallback: python3"
    else
        echo "❌ No compatible Python found!"
        echo "Please install Python 3.6+ and try again."
        exit 1
    fi
else
    echo "✅ Using Python: $best_python (v$(get_python_version_readable "$best_python"))"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    "$best_python" -m venv venv
    
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Install/upgrade dependencies
echo "Installing dependencies..."
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
        exit 1
    fi
    
    echo "📦 Installing colorama (terminal colors)..."
    if pip install --quiet colorama; then
        echo "✅ colorama installed successfully!"
    else
        echo "❌ Failed to install colorama"
        echo "💡 This might be due to missing system dependencies or network issues"
        echo "🌐 Please check your internet connection and try again"
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
        exit 1
    fi
fi

# Run the application
echo "Starting Terminally Quick..."
python src/terminallyquick_combined.py
