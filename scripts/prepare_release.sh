#!/bin/bash

# Release Preparation Script for TerminallyQuick
echo "📦 Preparing TerminallyQuick for GitHub release..."

# Clean up any temporary files
echo "🧹 Cleaning temporary files..."
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove any old build artifacts
echo "🗑️  Removing old build artifacts..."
rm -rf build/ dist/

# Build all platforms
echo "🏗️  Building executables..."
./scripts/build_all.sh

# Create release directory structure
echo "📁 Creating release structure..."
mkdir -p release/TerminallyQuick_v2.0

# Copy essential files to release directory
cp README.md release/TerminallyQuick_v2.0/
cp LICENSE release/TerminallyQuick_v2.0/
cp requirements.txt release/TerminallyQuick_v2.0/
cp TerminallyQuick.command release/TerminallyQuick_v2.0/
cp TerminallyQuick.bat release/TerminallyQuick_v2.0/
cp run.sh release/TerminallyQuick_v2.0/
cp run.bat release/TerminallyQuick_v2.0/
cp -r scripts/ release/TerminallyQuick_v2.0/
cp -r src/ release/TerminallyQuick_v2.0/

# Copy input_images folder structure
mkdir -p release/TerminallyQuick_v2.0/input_images
cp input_images/.gitkeep release/TerminallyQuick_v2.0/input_images/

# Copy built executables if they exist
if [ -d "dist/mac" ]; then
    cp -r dist/mac release/TerminallyQuick_v2.0/dist_mac/
fi

echo ""
echo "🎉 Release preparation completed!"
echo ""
echo "📋 Release contents:"
echo "└── release/TerminallyQuick_v2.0/"
echo "    ├── README.md                    # Documentation"
echo "    ├── LICENSE                      # MIT License"
echo "    ├── TerminallyQuick.command      # macOS double-click launcher"
echo "    ├── TerminallyQuick.bat          # Windows double-click launcher"
echo "    ├── run.sh                       # macOS/Linux script runner"
echo "    ├── run.bat                      # Windows script runner"
echo "    ├── requirements.txt             # Python dependencies"
echo "    ├── src/                         # Source code"
echo "    ├── scripts/                     # Setup and build scripts"
echo "    ├── input_images/                # Input folder (empty with .gitkeep)"
echo "    └── dist_mac/                    # macOS executable (if built)"
echo ""
echo "🚀 Ready for GitHub!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Upload the contents of release/TerminallyQuick_v2.0/"
echo "3. Create a release with the executables"
echo "4. Share with the world! 🌍"
