# TerminallyQuick v2.0 🚀

**The fastest and most user-friendly image processing tool for web developers, content creators, and photographers.**

Batch resize, convert, and optimize images with intelligent presets, progress tracking, and modern web formats.

![TerminallyQuick Banner](https://img.shields.io/badge/TerminallyQuick-v2.0-blue.svg) ![Python](https://img.shields.io/badge/python-3.7+-blue.svg) ![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Quick Start

### For End Users (No Python Knowledge Required)

#### macOS
1. Download the latest release
2. Double-click `TerminallyQuick.command` to run

#### Windows  
1. Download the latest release
2. Double-click `TerminallyQuick.bat` to run

#### First Time Setup (All Platforms)
1. Create an `input_images` folder in the same directory as the application
2. Add your images to the `input_images` folder
3. Run the application using the method above
4. Follow the interactive prompts to resize your images
5. Find your resized images in the `resized_images` folder

## ✨ What's New in v2.0

### 🚀 **Three Usage Modes**
- **Quick Mode**: 4 web-optimized presets, 5-second setup 
- **Expert Mode**: Full control with simplified interface

### 🎯 **Enhanced User Experience**
- **Progress Bars**: Real-time progress with ETA calculations
- **Smart Warnings**: Detect large batches, small images, processing time estimates
- **Auto-Open Results**: Instantly view your processed images
- **Recent Settings**: Remembers your last configuration
- **Better Error Handling**: Graceful failures with retry options
- **Keyboard Shortcuts**: Consistent navigation ([Q]uit, [L]ogs, [H]elp)

### 🌐 **Web Developer Focus**
- **SEO-Friendly Names**: Auto-generates clean, web-ready filenames
- **Compression Analytics**: See exact file size savings
- **Modern Formats**: WEBP, AVIF support with optimized defaults
- **Responsive Sizes**: Generate mobile/tablet/desktop variants
- **Team Settings**: Export/import configurations as JSON

## 📋 Core Features

- **Batch Processing**: Handle hundreds of images efficiently
- **14+ Formats**: PNG, JPG, JPEG, WEBP, AVIF, CR3, BMP, TIFF, ICO, HEIC, and more
- **Smart Resizing**: Intelligent resize with upscaling controls
- **Advanced Cropping**: 9 aspect ratios with 3 anchor positions
- **Quality Control**: Format-specific quality optimization (50-100%)
- **Cross-Platform**: Works on macOS, Windows, and Linux
- **Zero Dependencies**: Self-contained executables available
- **RAW Support**: Canon CR3 files (requires exiftool)

## 🛠️ Advanced Setup (For Developers)

### Prerequisites
- Python 3.7 or higher
- exiftool (optional, for CR3 support)

### macOS Setup
```bash
# Clone the repository
git clone https://github.com/raghav4882/TerminallyQuick.git
cd TerminallyQuick

# Run the setup script
chmod +x scripts/setup_mac.sh
./scripts/setup_mac.sh
```

### Windows Setup
```batch
REM Clone the repository
git clone https://github.com/raghav4882/TerminallyQuick.git
cd TerminallyQuick

REM Run the setup script
scripts\setup_windows.bat
```

### Linux Setup
```bash
# Clone the repository
git clone https://github.com/raghav4882/TerminallyQuick.git
cd TerminallyQuick

# Install dependencies
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv exiftool

# Run the macOS setup script (compatible with Linux)
chmod +x scripts/setup_mac.sh
./scripts/setup_mac.sh
```

## 🏗️ Building Executables

### Build for Current Platform
```bash
# macOS/Linux
./scripts/build_all.sh

# Windows
scripts\build_windows.bat
```

### Build Output
- `dist/mac/` - macOS executable and app bundle
- `dist/windows/` - Windows executable (when built on Windows)
- `dist/source/` - Source code distribution

## 📂 Project Structure

```
TerminallyQuick/
├── src/
│   └── terminallyquick_combined.py      # Main application
├── scripts/
│   ├── setup_mac.sh            # macOS/Linux setup
│   ├── setup_windows.bat       # Windows setup
│   ├── build_mac.sh            # macOS build script
│   ├── build_windows.bat       # Windows build script
│   └── build_all.sh            # Universal build script
├── dist/                       # Built executables (after building)
├── input_images/               # Place your images here
├── resized_images/             # Output folder (auto-created)
├── requirements.txt            # Python dependencies
├── TerminallyQuick.command     # macOS double-click launcher
├── TerminallyQuick.bat         # Windows double-click launcher
├── run.sh                      # macOS/Linux runner script
└── run.bat                     # Windows runner script
```

## 📊 Usage Modes

### 🚀 Quick Mode (Recommended for Web Developers)
1. **Add Images**: Drop images in `input_images` folder
2. **Run**: Double-click launcher or run script  
3. **Choose Preset**: Pick from 4 optimized web presets:
   - Web Thumbnails (300px squares)
   - Hero Images (1200px widescreen)
   - Blog Images (800px optimized)
   - Social Media (1080px squares)
4. **Done**: Images automatically processed and opened


### 🔧 Expert Mode (Full Control)
1. **Add Images**: Place images in `input_images` folder  
2. **Run Application**: Use launcher
3. **Custom Configuration**:
   - Choose from 8 export formats (WEBP, JPEG, PNG, AVIF, etc.)
   - Set target size with smart suggestions
   - Adjust quality with format-specific recommendations
   - Optional cropping with simplified ratios
   - Upscaling policy control
4. **Preview**: See what will happen before processing
5. **Process**: Real-time progress with detailed feedback
6. **Results**: Enhanced analytics and next action options

## 🎯 Supported Formats

### Input Formats
- PNG, JPG, JPEG
- WEBP
- CR3 (Canon RAW - requires exiftool)
- BMP, TIFF, ICO
- PPM, PGM, PBM, TGA

### Output Formats
- WEBP (recommended)
- JPEG
- PNG
- TIFF
- BMP
- ICO
- PDF

## 🔧 CR3 Support

To process Canon CR3 RAW files, you need exiftool installed:

### macOS
```bash
brew install exiftool
```

### Windows
1. Download from [exiftool.org](https://exiftool.org/install.html#Windows)
2. Install and ensure it's in your PATH

### Linux
```bash
sudo apt-get install exiftool
```

## 📊 Logs

The application automatically creates detailed logs for each processing session:
- Session scan logs in `resized_images/`
- Processing logs in each output run folder
- View logs using the `[L]` option in the application

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on multiple platforms
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 👨‍💻 Author

**Daedraheart** - Website developer, Game Designer and a serious task management app enthusiast (for a day). 

## 🐛 Issues & Support

If you encounter any issues:
1. Check the logs for detailed error information
2. Ensure all dependencies are installed
3. Create an issue on GitHub with:
   - Your operating system
   - Error messages (if any)
   - Steps to reproduce

## 🚀 Changelog

### v2.0 - Enhanced UX Edition
- **🚀 Two Usage Modes**: Quick (presets), Expert (full control)
- **📏 Progress Tracking**: Real-time progress bars with ETA calculations
- **⚠️ Smart Warnings**: Large batch detection, image size analysis
- **🖼️ Preview Mode**: See changes before processing
- **📁 Auto-Open Results**: Instant access to processed images
- **💾 Recent Settings**: Remembers last configuration
- **⌨️ Better Navigation**: Consistent keyboard shortcuts and help
- **🛠️ Error Recovery**: Retry failed images, graceful interruption handling
- **🌍 Web Optimization**: SEO filenames, compression analytics, modern formats
- **📊 Enhanced Logging**: Detailed JSON logs with processing statistics

### v1.3
- Cross-platform executable support
- Self-contained distribution
- Improved error handling
- Enhanced CR3 support with graceful fallback
- Double-click launchers for macOS and Windows

---

*Happy image processing! 📸*
