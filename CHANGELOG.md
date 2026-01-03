# Changelog: TerminallyQuick v3.0 → v4.0

## [4.0] — 2026-01-03
### "High Performance" Release

#### ⚡ Performance & Engine
- **Turbo Engine (Parallelism)**: Introduced `ThreadPoolExecutor` for concurrent image processing. Experience up to **32x speedup** on multi-core systems.
- **Delta Sync Engine**: New MD5-based content hashing. TerminallyQuick now remembers processed files and skips them if settings haven't changed, making re-runs nearly instant.
- **Smart AI Quality thresholding**: Automated quality analysis using RMS (Root Mean Square) difference. It aggressively compresses images but detects and preserves quality if artifacts appear.
- **Native HEIC/AVIF/CR3 Support**: Fully integrated `pillow-heif` and `exiftool` bridge for professional photography workflows.

#### 🐕 Automation
- **Watchdog Mode**: Real-time folder monitoring. Drop a file into `input_images/` and it gets processed automatically in the background.
- **Watchdog Profiles**: Launch Watch Mode directly using any of your saved **FAST TRACK** presets.
- **Non-Interactive Silent Mode**: Refined background output for a distraction-free experience.

#### 📊 UX & Interface Overhaul
- **Persistent Progress Engine**: A pro-grade ASCII progress bar that stays pinned to the bottom of your terminal window with real-time ETA.
- **Condensed Scrolling Logs**: Replaced noisy multi-line output with elegant, single-line status reports that scroll above the persistent bar.
- **Persistent Session Config**: Your last-used input folder is now remembered across application restarts via `.tq_config`.
- **Intelligent Defaults**: "Manual Configuration" and "Recursive Mirroring" are now the default selections for a faster workflow.

#### 🛡️ Stability & Security
- **Unified Launcher (macOS/Win)**: Refined `.command` and `.bat` scripts with robust dependency auto-installers.
- **Golden Gitignore**: Hardened ignore rules to ensure user caches and session logs never leak into repositories.
- **Auto-Mirroring**: Now preserves full sub-directory structures by default during processing.
- **Master Test Suite**: Comprehensive `stress_test.py` for verifying all v4.0 flagship features.

---
*Thank you for being part of the TerminallyQuick journey!* 🚀
