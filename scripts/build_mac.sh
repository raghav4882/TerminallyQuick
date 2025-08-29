#!/bin/bash

# Build script for macOS executable
echo "🍎 Building TerminallyQuick for macOS..."

# Activate virtual environment
source venv/bin/activate

# Clean previous builds
rm -rf build/ dist/

# Build executable
pyinstaller --onefile \
    --name "TerminallyQuick" \
    --icon="" \
    --console \
    --clean \
    --distpath dist/mac \
    --workpath build/mac \
    --specpath build \
    src/terminallyquick_combined.py

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ macOS build completed successfully!"
    echo "📦 Executable location: dist/mac/TerminallyQuick"
    
    # Create app bundle for double-click functionality
    mkdir -p "dist/mac/TerminallyQuick.app/Contents/MacOS"
    mkdir -p "dist/mac/TerminallyQuick.app/Contents/Resources"
    
    # Move executable
    mv "dist/mac/TerminallyQuick" "dist/mac/TerminallyQuick.app/Contents/MacOS/"
    
    # Create Info.plist
    cat > "dist/mac/TerminallyQuick.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>TerminallyQuick</string>
    <key>CFBundleIdentifier</key>
    <string>com.daedraheart.terminallyquick</string>
    <key>CFBundleName</key>
    <string>TerminallyQuick</string>
            <key>CFBundleVersion</key>
        <string>2.0</string>
        <key>CFBundleShortVersionString</key>
        <string>2.0</string>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
EOF
    
    echo "📱 macOS app bundle created at: dist/mac/TerminallyQuick.app"
else
    echo "❌ macOS build failed!"
    exit 1
fi
