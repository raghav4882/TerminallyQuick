from setuptools import setup, find_packages

setup(
    name="TerminallyQuick",
    version="2.0",
    author="Daedraheart", 
    description="Enhanced image processing tool with AI analysis and web optimization",
    long_description="""TerminallyQuick v2.0 is an enhanced cross-platform tool for batch image processing.
    
    Features:
    • Three usage modes: Quick (presets), Smart (AI analysis), Expert (full control)
    • Progress tracking with ETA calculations  
    • Web developer focus with SEO-friendly filenames
    • 14+ format support including modern WEBP/AVIF
    • Intelligent upscaling controls and compression analytics
    • Team configuration sharing via JSON export/import
    • Enhanced error handling and recovery options
    """,
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "Pillow>=11.0.0",
        "colorama>=0.4.0",
    ],
    entry_points={
        "console_scripts": [
            "terminallyquick=src.terminallyquick_combined:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
