#!/bin/bash

# Universal build script for TerminallyQuick
echo "🚀 Building TerminallyQuick for all platforms..."

# Activate virtual environment
source venv/bin/activate

# Clean all previous builds
rm -rf build/ dist/

# Create dist directories
mkdir -p dist/mac dist/windows dist/source

# Build for current platform (macOS in this case)
echo ""
echo "🍎 Building macOS executable..."
pyinstaller --onefile \
    --name "TerminallyQuick" \
    --console \
    --clean \
    --distpath dist/mac \
    --workpath build/mac \
    --specpath build \
    src/terminallyquick_combined.py

if [ $? -eq 0 ]; then
    echo "✅ macOS executable built successfully!"
    
    # Create macOS app bundle
    mkdir -p "dist/mac/TerminallyQuick.app/Contents/MacOS"
    mkdir -p "dist/mac/TerminallyQuick.app/Contents/Resources"
    
    # Move executable
    cp "dist/mac/TerminallyQuick" "dist/mac/TerminallyQuick.app/Contents/MacOS/"
    
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

    # Create simple terminal launcher for macOS
    cat > "dist/mac/TerminallyQuick_Terminal.command" << EOF
#!/bin/bash
cd "\$(dirname "\$0")"
./TerminallyQuick
EOF
    chmod +x "dist/mac/TerminallyQuick_Terminal.command"
    
    echo "📱 macOS app bundle created!"
else
    echo "❌ macOS build failed!"
fi

# Create source distribution
echo ""
echo "📦 Creating source distribution..."
mkdir -p dist/source
cp -r src/ dist/source/
cp requirements.txt dist/source/
cp scripts/setup_*.* dist/source/
cp README.md dist/source/ 2>/dev/null || true

echo ""
echo "🎉 Build process completed!"
echo "📁 Check the dist/ folder for all builds:"
echo "   - dist/mac/ - macOS executable and app bundle"
echo "   - dist/windows/ - Windows executable (build on Windows)"
echo "   - dist/source/ - Source code distribution"
