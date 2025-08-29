#!/bin/bash

echo "🍎 Setting up TerminallyQuick development environment for macOS..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    echo "   You can install it from https://www.python.org/ or using Homebrew:"
    echo "   brew install python"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if exiftool is installed (required for CR3 support)
if ! command -v exiftool &> /dev/null; then
    echo "⚠️  exiftool not found. Installing via Homebrew (required for CR3 support)..."
    if command -v brew &> /dev/null; then
        brew install exiftool
    else
        echo "❌ Homebrew not found. Please install exiftool manually:"
        echo "   Visit: https://exiftool.org/install.html"
        echo "   Or install Homebrew first: https://brew.sh/"
    fi
else
    echo "✅ exiftool found: $(which exiftool)"
fi

# Create virtual environment
echo "🏗️  Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Run the application: ./run.sh"
echo "   2. Build executable: ./scripts/build_mac.sh"
echo "   3. Build all platforms: ./scripts/build_all.sh"
