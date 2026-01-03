# TerminallyQuick v3.0

A **high-performance** command-line suite for bulk image optimization, resizing, and conversion. Designed for engineers and photographers who need speed, precision, and professional results without the bloat.

## 🚀 Key Features

- **Blazing Fast**: Uses **Multi-Threaded Parallel Processing** to optimize images using all your CPU cores.
- **Modern Format Support**: Native support for **HEIC** (iPhone), **AVIF**, **CR3** (Canon RAW), **WEBP**, and standard formats (JPEG/PNG).
- **Custom Profiles**: Save your frequently used settings (e.g., "Web Banners", "Thumbnails") and apply them instantly via "Fast Track".
- **Smart or Manual**: Let the app suggest optimal settings (`Smart Mode`) or take full control (`Manual Mode`).
- **Safe & Local**: Runs in an isolated virtual environment. **No system-wide installations** or side effects.

## 📋 Quick Start

1.  **Drop Images**: Place your images in the `input_images/` folder.
2.  **Launch**:
    *   **macOS**: Double-click `TerminallyQuick.command`
    *   **Windows**: Double-click `TerminallyQuick.bat`
3.  **Choose Mode**:
    *   **[1] Manual**: Full control over Size, Quality, Aspect Ratio, and Format.
    *   **[2] Smart Mode**: Auto-detects optimal settings.
    *   **[4+] Fast Track**: Select a saved Profile to process instantly.

## 📖 Step-by-Step Tutorial

### Your First Session (Manual Mode)
1.  **Prepare**: Put your photos path in `input_images/`.
2.  **Start**: Run the launcher. Choose **[1] Manual Configuration**.
3.  **Settings**:
    *   Select your **Format** (e.g., WEBP for web).
    *   Set the **Short Edge** size (e.g., 800px).
    *   Set **Quality** (typically 80% is the sweet spot).
4.  **Process**: Watch the parallel engine work! Once finished, a summary report is generated.
5.  **Save**: The app will ask if you want to save these settings as a **Profile**. Say `Yes` and name it (e.g., "StandardWeb").

### The "Fast Track" Workflow (Pro Speed)
Once you have saved a profile:
1.  Run the launcher.
2.  Your profile will appear in the **FAST TRACK** section (e.g., `[4] Profile: StandardWeb`).
3.  Press **4**.
4.  **Done!** Every image in your folder is instantly processed with those exact settings. No questions asked.

### Using the "One-Image Test"
Unsure about the quality at 70%?
- In the manual flow, choose **[T] Test Run** before starting the full batch.
- The app processes only the first image and automatically opens the folder for you to inspect.

## ⚡ High Performance Workflow

v3.0 introduces a production-grade workflow for large batches:

1.  **Pre-Batch Analysis**: Scans your input folder and reports exactly how many images will be downscaled, upscaled, or kept as-is *before* you proceed.
2.  **Real-Time Feedback**: A sleek ASCII progress bar (`████░░░░`) with an **Estimated Time Remaining (ETA)** timer.
3.  **Quiet Mode**: During batch runs, the terminal stays clean, updating only the progress bar to prevent text spam.

## 🛠 Supported Formats

| Category | Formats |
| :--- | :--- |
| **Web Next-Gen** | WEBP, AVIF |
| **Mobile/RAW** | HEIC, CR3 (Canon)* |
| **Standard** | JPEG, PNG, BMP, TIFF |
| **Legacy** | ICO, PPM, TGA |

*\*CR3 support requires `exiftool` to be installed on your system. All other formats are supported native out-of-the-box.*

## ⚙️ Requirements

- **Python 3.6+** (The launcher will guide you if it's missing)
- **Zero Configuration**: Dependencies (`Pillow`, `pillow-heif`, `colorama`) are auto-installed into a local `venv`.

## 📄 License

**MIT License**. Free for personal and commercial use. Open source and privacy-focused.
