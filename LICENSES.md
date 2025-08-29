# License Information for TerminallyQuick

## 📋 License Compliance Summary

TerminallyQuick is fully compliant with all applicable licenses. All dependencies use permissive licenses that allow redistribution and commercial use.

## 🏷️ Main Application License

**TerminallyQuick** is licensed under the **MIT License**
- ✅ Allows commercial use
- ✅ Allows modification and distribution
- ✅ No warranty required

## 📦 Python Dependencies

### Pillow (PIL Fork) - MIT-CMU License
- **License**: MIT-CMU (MIT-compatible)
- **Usage**: Image processing and format conversion
- **Compliance**: ✅ Bundled with executable, attribution in this file
- **Source**: https://python-pillow.github.io

### Colorama - BSD License
- **License**: BSD-3-Clause
- **Usage**: Cross-platform terminal colors
- **Compliance**: ✅ Bundled with executable, attribution in this file
- **Source**: https://github.com/tartley/colorama

### PyInstaller - GPL v2+ with Commercial Exception
- **License**: GPL v2+ with special exception for non-GPL applications
- **Usage**: Creating standalone executables (build-time only)
- **Compliance**: ✅ Not distributed with application, only used to build
- **Exception**: Allows building and distributing non-GPL programs (including commercial)
- **Source**: https://www.pyinstaller.org

## 🛠️ External Tools (Optional Dependencies)

### ExifTool - Perl Artistic License / GPL
- **License**: Dual licensed under Perl Artistic License or GPL
- **Usage**: CR3 RAW file preview extraction (optional)
- **Compliance**: ✅ **NOT bundled or distributed** - users install separately
- **Distribution**: Users download directly from https://exiftool.org
- **Graceful Handling**: Application works without exiftool (CR3 support disabled)

## 🔒 License Compliance Strategy

1. **No License Violations**: We don't bundle or redistribute exiftool
2. **User Choice**: Users can optionally install exiftool themselves
3. **Clear Documentation**: Installation instructions provided for exiftool
4. **Graceful Degradation**: Application works fully without exiftool
5. **Permissive Dependencies**: All bundled libraries use MIT/BSD licenses

## 📄 Required Attributions

### Pillow (PIL Fork)
Copyright © 2010-2024 by Jeffrey A. Clark and contributors
Licensed under MIT-CMU License

### Colorama
Copyright © 2010-2020 Jonathan Hartley and contributors
Licensed under BSD-3-Clause License

### Python Standard Library
Copyright © 2001-2024 Python Software Foundation
Licensed under Python Software Foundation License

## ✅ Commercial Use

This software and all its bundled dependencies are **safe for commercial use** without any licensing restrictions or fees.

## 🚨 Important Notes

- **ExifTool**: Not included in distribution - users must install separately if CR3 support is needed
- **All Bundled Libraries**: Use permissive licenses compatible with commercial use
- **PyInstaller**: Build tool only, not distributed with final application
- **Attribution**: This file serves as required attribution for all dependencies

## 📞 Contact

For license questions or concerns, please create an issue on the GitHub repository.

---
*Last updated: 2025-08-29*
