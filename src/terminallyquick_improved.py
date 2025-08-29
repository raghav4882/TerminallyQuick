#!/usr/bin/env python3

"""
TerminallyQuick v2.0 - Improved UX Edition
A fast and user-friendly image processing tool with enhanced UX
"""

__version__ = "2.0"
__author__ = "Daedraheart"

from PIL import Image, ExifTags
import os
import signal
from datetime import datetime
import time
from colorama import init, Fore, Style
import shutil, textwrap
import sys
import platform
import json
import threading
from contextlib import contextmanager

# === Enhanced UX Features ===
init(autoreset=True)

# Global state for graceful shutdown
processing_interrupted = False
current_batch_folder = None

def signal_handler(signum, frame):
    global processing_interrupted, current_batch_folder
    processing_interrupted = True
    print(f"\n{Fore.YELLOW}⏸️  Processing interrupted. Cleaning up...")
    if current_batch_folder and os.path.exists(current_batch_folder):
        print(f"{Fore.CYAN}📁 Partial results saved in: {current_batch_folder}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Check for exiftool (required for CR3 support)
HAS_EXIFTOOL = shutil.which("exiftool") is not None

# === Recent Settings Management ===
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".terminallyquick_recent.json")

def load_recent_settings():
    """Load recently used settings"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def save_recent_settings(settings):
    """Save settings for next time"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except:
        pass  # Fail silently if can't save

# === Web Developer Presets ===
WEB_DEV_PRESETS = {
    "1": {
        "name": "Web Thumbnails",
        "format": "WEBP",
        "size": 300,
        "quality": 85,
        "crop": True,
        "aspect": (1, 1),
        "anchor": "center",
        "description": "Square thumbnails for galleries"
    },
    "2": {
        "name": "Hero Images",
        "format": "WEBP", 
        "size": 1200,
        "quality": 90,
        "crop": True,
        "aspect": (16, 9),
        "anchor": "center",
        "description": "Widescreen hero banners"
    },
    "3": {
        "name": "Blog Images",
        "format": "WEBP",
        "size": 800,
        "quality": 85,
        "crop": False,
        "aspect": None,
        "anchor": None,
        "description": "Optimized blog post images"
    },
    "4": {
        "name": "Social Media",
        "format": "JPEG",
        "size": 1080,
        "quality": 90,
        "crop": True,
        "aspect": (1, 1),
        "anchor": "center",
        "description": "Instagram/social posts"
    }
}

# === Smart Image Analysis ===
def analyze_images(image_files, input_folder):
    """Analyze images to suggest optimal settings"""
    total_pixels = 0
    max_dimension = 0
    min_dimension = float('inf')
    photo_count = 0
    graphic_count = 0
    
    sample_size = min(10, len(image_files))  # Analyze up to 10 images for speed
    
    print(f"{Fore.CYAN}🔍 Analyzing {sample_size} sample images...")
    
    for i, filename in enumerate(image_files[:sample_size]):
        try:
            img_path = os.path.join(input_folder, filename)
            with Image.open(img_path) as img:
                w, h = img.size
                total_pixels += w * h
                max_dimension = max(max_dimension, max(w, h))
                min_dimension = min(min_dimension, min(w, h))
                
                # Simple heuristic: photos usually have more colors and gradients
                colors = len(img.getcolors(maxcolors=256*256*256)) if img.mode == 'RGB' else 256
                if colors > 10000:  # Likely a photo
                    photo_count += 1
                else:  # Likely a graphic/screenshot
                    graphic_count += 1
                    
        except Exception:
            continue
    
    avg_pixels = total_pixels / sample_size if sample_size > 0 else 0
    is_photo_heavy = photo_count > graphic_count
    
    # Suggest settings based on analysis
    suggested_preset = "3"  # Blog Images default
    if max_dimension > 3000:  # High-res images
        suggested_preset = "2" if is_photo_heavy else "3"
    elif min_dimension < 500:  # Small images
        suggested_preset = "1"  # Thumbnails
    
    return {
        "suggested_preset": suggested_preset,
        "is_photo_heavy": is_photo_heavy,
        "avg_size": f"{int((avg_pixels**0.5)):,}px",
        "size_range": f"{int(min_dimension):,}px - {int(max_dimension):,}px",
        "warnings": []
    }

# === Enhanced Progress Bar ===
def print_progress_bar(current, total, filename, start_time, action="Processing"):
    """Enhanced progress bar with better formatting"""
    percent = (current / total) * 100
    bar_length = 40
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    # Calculate ETA
    elapsed = time.time() - start_time
    if current > 0:
        eta = (elapsed / current) * (total - current)
        if eta > 3600:  # More than an hour
            eta_str = f"ETA: {int(eta//3600)}h{int((eta%3600)//60):02d}m"
        elif eta > 60:  # More than a minute
            eta_str = f"ETA: {int(eta//60)}:{int(eta%60):02d}"
        else:
            eta_str = f"ETA: {int(eta)}s"
    else:
        eta_str = "ETA: calculating..."
    
    # Truncate filename if too long
    display_name = filename[:20] + "..." if len(filename) > 23 else filename
    
    print(f"\r{Fore.GREEN}[{bar}] {percent:5.1f}% ({current}/{total}) {eta_str}")
    print(f"{Fore.CYAN}🔄 {action}: {display_name}", end="                    \r", flush=True)

# === Input Validation and Warnings ===
def validate_and_warn_images(image_files, input_folder):
    """Check images and warn about potential issues"""
    warnings = []
    large_images = []
    small_images = []
    
    for filename in image_files:
        try:
            img_path = os.path.join(input_folder, filename)
            with Image.open(img_path) as img:
                w, h = img.size
                file_size_mb = os.path.getsize(img_path) / (1024 * 1024)
                
                if max(w, h) > 5000:  # Very large images
                    large_images.append((filename, f"{w}x{h}", f"{file_size_mb:.1f}MB"))
                elif min(w, h) < 100:  # Very small images
                    small_images.append((filename, f"{w}x{h}"))
                    
        except Exception:
            warnings.append(f"⚠️  Could not read: {filename}")
    
    if large_images:
        warnings.append(f"🐘 {len(large_images)} very large images detected - processing may be slow")
    if small_images:
        warnings.append(f"🔍 {len(small_images)} very small images - upscaling may reduce quality")
    
    return warnings

# === Helper Functions ===
def open_file_cross_platform(path):
    if platform.system() == "Darwin":
        os.system(f'open "{path}"')
    elif platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Linux":
        os.system(f'xdg-open "{path}"')
    else:
        print(f"{Fore.RED}⚠️ Unsupported OS. Please open the file manually: {path}")

def get_file_size_kb(path):
    return os.path.getsize(path) // 1024

def generate_web_friendly_filename(original_name, settings, timestamp):
    """Generate SEO-friendly filenames"""
    base = os.path.splitext(original_name)[0]
    clean_base = "".join(c.lower() if c.isalnum() else "_" for c in base)
    clean_base = clean_base.strip("_")
    
    size_suffix = f"{settings['size']}w" if not settings['crop'] else f"{settings['size']}x{settings['size']}"
    extension = settings['format'].lower()
    
    return f"{clean_base}_{size_suffix}_{timestamp}.{extension}"

def print_current_selections(format=None, size=None, quality=None, aspect=None, anchor=None, preset=None):
    parts = []
    if preset: parts.append(f"Preset: {preset}")
    if format: parts.append(f"Format: {format}")
    if size: parts.append(f"Size: {size}px")
    if quality: parts.append(f"Quality: {quality}")
    if aspect: parts.append(f"Aspect: {aspect[0]}:{aspect[1]}")
    if anchor: parts.append(f"Anchor: {anchor.replace('-', ' ').title()}")
    if parts:
        print(Fore.CYAN + "[" + " | ".join(parts) + "]\n")
    else:
        print(Fore.CYAN + "[No selections made yet.]\n")

# === Improved Navigation Helper ===
def show_navigation_help():
    print(f"{Fore.YELLOW}Navigation: [Q]uit | [B]ack | [L]ogs | [H]elp | [↵]Default")

def get_user_input(prompt, default=None, valid_options=None, allow_back=False):
    """Enhanced input function with consistent navigation"""
    while True:
        show_navigation_help()
        user_input = input(f"{Fore.CYAN}{prompt}: ").strip().lower()
        
        if user_input == 'q':
            print(f"{Fore.RED}Goodbye!")
            sys.exit()
        elif user_input == 'h':
            print(f"{Fore.YELLOW}📖 Help:")
            print("  • Press Enter for default option")
            print("  • Type 'q' to quit anytime") 
            print("  • Type 'l' to view scan logs")
            if allow_back:
                print("  • Type 'b' to go back")
            continue
        elif user_input == 'l':
            open_file_cross_platform(tmp_log_path)
            continue
        elif user_input == 'b' and allow_back:
            return 'back'
        elif user_input == '' and default is not None:
            return default
        elif valid_options and user_input in valid_options:
            return user_input
        elif valid_options:
            print(f"{Fore.RED}❌ Invalid option. Valid choices: {', '.join(valid_options)}")
        else:
            return user_input

# === Mode Selection ===
def select_mode():
    """Select Quick, Smart, or Expert mode"""
    print(f"""{Fore.CYAN}{Style.BRIGHT}
╔══════════════════════════════════════════════════════════╗
║                 TerminallyQuick v{__version__}                   ║
║                Choose Your Experience                    ║
╚══════════════════════════════════════════════════════════╝
{Style.RESET_ALL}""")

    print(f"{Fore.GREEN}🚀 Quick Mode{Style.RESET_ALL}")
    print("  Perfect for: Most web developers")
    print("  Time: ~5 seconds setup")
    print("  Choose from 4 optimized web presets")
    
    print(f"\n{Fore.CYAN}🧠 Smart Mode{Style.RESET_ALL}")  
    print("  Perfect for: Mixed content creators")
    print("  Time: ~15 seconds setup")
    print("  AI analyzes your images and suggests optimal settings")
    
    print(f"\n{Fore.MAGENTA}🔧 Expert Mode{Style.RESET_ALL}")
    print("  Perfect for: Advanced users & specific requirements")
    print("  Time: ~60 seconds setup")
    print("  Full control over all settings")
    
    mode = get_user_input("Choose mode [1] Quick [2] Smart [3] Expert", "1", ["1", "2", "3"])
    return {"1": "quick", "2": "smart", "3": "expert"}[mode]

# === Image Analysis & Smart Suggestions ===
def smart_analyze_and_suggest(image_files, input_folder):
    """Smart mode: analyze images and suggest settings"""
    analysis = analyze_images(image_files, input_folder)
    
    print(f"\n{Fore.CYAN}🧠 Smart Analysis Results:")
    print(f"  📊 Image type: {'Photos' if analysis['is_photo_heavy'] else 'Graphics/Screenshots'}")
    print(f"  📐 Size range: {analysis['size_range']}")
    print(f"  💡 Recommended preset: {WEB_DEV_PRESETS[analysis['suggested_preset']]['name']}")
    
    if analysis['warnings']:
        print(f"\n{Fore.YELLOW}⚠️  Recommendations:")
        for warning in analysis['warnings']:
            print(f"  {warning}")
    
    # Show suggested preset details
    suggested = WEB_DEV_PRESETS[analysis['suggested_preset']]
    print(f"\n{Fore.GREEN}🎯 Suggested Settings:")
    print(f"  Format: {suggested['format']} | Size: {suggested['size']}px | Quality: {suggested['quality']}%")
    if suggested['crop']:
        print(f"  Crop: {suggested['aspect'][0]}:{suggested['aspect'][1]} ratio")
    
    use_suggestion = get_user_input("Use AI suggestion? [y/n]", "y", ["y", "n"])
    
    if use_suggestion == "y":
        return suggested
    else:
        return quick_mode_selection()

# === Quick Mode (Streamlined Presets) ===
def quick_mode_selection():
    """Quick mode with just the essential presets"""
    print(f"\n{Fore.GREEN}🚀 Quick Mode - Choose Your Use Case:")
    
    # Show only the most common 4 presets
    quick_presets = {k: v for k, v in list(WEB_DEV_PRESETS.items())[:4]}
    
    for key, preset in quick_presets.items():
        print(f"  {key}: {preset['name']} - {preset['description']}")
    
    choice = get_user_input("Select preset [1-4]", "3", list(quick_presets.keys()))
    return WEB_DEV_PRESETS[choice]

# === Expert Mode (Full Control) ===
def expert_mode_selection():
    """Expert mode with simplified choices but full control"""
    
    # Load recent settings if available
    recent = load_recent_settings()
    if recent:
        print(f"\n{Fore.CYAN}📋 Recent Settings Available:")
        print(f"  Last used: {recent.get('name', 'Custom')} ({recent.get('format', 'WEBP')} {recent.get('size', 800)}px)")
        
        use_recent = get_user_input("Use recent settings? [y/n]", "n", ["y", "n"])
        if use_recent == "y":
            return recent
    
    # Simplified format selection
    format_options = {
        "1": "WEBP",    # Most common for web
        "2": "JPEG",    # Universal compatibility  
        "3": "PNG",     # Lossless/transparency
        "4": "More..."  # Advanced options
    }
    
    print(f"\n{Fore.CYAN}🎨 Choose Format (simplified):")
    print("  1: WEBP (recommended - smaller files)")
    print("  2: JPEG (universal compatibility)")
    print("  3: PNG (transparency support)")
    print("  4: More formats...")
    
    format_choice = get_user_input("Format choice [1-4]", "1", ["1", "2", "3", "4"])
    
    if format_choice == "4":
        # Show advanced formats
        advanced_formats = {"5": "TIFF", "6": "BMP", "7": "AVIF", "8": "PDF"}
        print(f"\n{Fore.MAGENTA}Advanced Formats:")
        for k, v in advanced_formats.items():
            print(f"  {k}: {v}")
        
        format_choice = get_user_input("Advanced format [5-8]", "5", list(advanced_formats.keys()))
        output_format = advanced_formats[format_choice]
    else:
        output_format = format_options[format_choice]
    
    # Smart size suggestions based on format
    size_suggestions = {
        "WEBP": "800 (optimal for web)",
        "JPEG": "1000 (good for photos)", 
        "PNG": "600 (smaller for graphics)"
    }
    
    print(f"\n{Fore.CYAN}📏 Choose Size:")
    print(f"  💡 Suggested for {output_format}: {size_suggestions.get(output_format, '800')}px")
    print(f"  📱 Common sizes: 300 (thumbnails) | 800 (content) | 1200 (hero)")
    
    size_input = get_user_input("Size in pixels", "800")
    try:
        size = int(size_input)
    except ValueError:
        size = 800
    
    # Quality with format-specific defaults
    quality_defaults = {"WEBP": 85, "JPEG": 90, "PNG": 95, "AVIF": 80}
    default_quality = quality_defaults.get(output_format, 85)
    
    print(f"\n{Fore.CYAN}🎚️ Quality Setting:")
    print(f"  💡 Recommended for {output_format}: {default_quality}%")
    print(f"  🌐 Web-optimized: 80-85% | Balanced: 90-95% | Maximum: 95-100%")
    
    quality_input = get_user_input("Quality (50-100)", str(default_quality))
    try:
        quality = max(50, min(100, int(quality_input)))
    except ValueError:
        quality = default_quality
    
    # Simplified cropping
    crop_choice = get_user_input("Crop to specific aspect ratio? [y/n]", "n", ["y", "n"])
    
    if crop_choice == "y":
        print(f"\n{Fore.CYAN}📐 Common Aspect Ratios:")
        print("  1: Square (1:1) - Social media, thumbnails")
        print("  2: Widescreen (16:9) - Hero images, banners") 
        print("  3: Portrait (4:5) - E-commerce, mobile")
        print("  4: More ratios...")
        
        ratio_choice = get_user_input("Aspect ratio [1-4]", "1", ["1", "2", "3", "4"])
        
        if ratio_choice == "4":
            # Advanced ratios
            advanced_ratios = {
                "5": (4, 3), "6": (3, 2), "7": (21, 9), "8": (2, 1), "9": (9, 16)
            }
            print(f"\n{Fore.MAGENTA}More Ratios:")
            print("  5: Standard (4:3) | 6: Photo (3:2) | 7: Ultra-wide (21:9)")
            print("  8: Cover (2:1) | 9: Vertical (9:16)")
            
            ratio_choice = get_user_input("Advanced ratio [5-9]", "5", list(advanced_ratios.keys()))
            aspect_ratio = advanced_ratios[ratio_choice]
        else:
            ratio_map = {"1": (1, 1), "2": (16, 9), "3": (4, 5)}
            aspect_ratio = ratio_map[ratio_choice]
        
        # Simplified anchor (just 3 options)
        print(f"\n{Fore.CYAN}🎯 Crop Position:")
        print("  1: Center (recommended)")
        print("  2: Top")
        print("  3: Bottom")
        
        anchor_choice = get_user_input("Crop position [1-3]", "1", ["1", "2", "3"])
        anchor_map = {"1": "center", "2": "top-center", "3": "bottom-center"}
        anchor = anchor_map[anchor_choice]
        
        crop = True
    else:
        aspect_ratio = None
        anchor = None
        crop = False
    
    settings = {
        "name": "Expert Custom",
        "format": output_format,
        "size": size,
        "quality": quality,
        "crop": crop,
        "aspect": aspect_ratio,
        "anchor": anchor
    }
    
    # Save for next time
    save_recent_settings(settings)
    
    return settings

# === Dry Run Preview ===
def show_preview(settings, sample_images):
    """Show what will happen to sample images"""
    print(f"\n{Fore.CYAN}🔍 Preview Mode - Showing what will happen:")
    
    sample_count = min(3, len(sample_images))
    for i, filename in enumerate(sample_images[:sample_count]):
        try:
            img_path = os.path.join(input_folder, filename)
            with Image.open(img_path) as img:
                original_size = img.size
                
                # Calculate what the output would be
                w, h = original_size
                short_edge = min(w, h)
                
                if short_edge <= settings['size']:
                    new_size = original_size
                    action = "Keep original size"
                else:
                    if w < h:
                        new_w = settings['size'] 
                        new_h = int((settings['size'] / w) * h)
                    else:
                        new_h = settings['size']
                        new_w = int((settings['size'] / h) * w)
                    new_size = (new_w, new_h)
                    action = "Resize"
                
                if settings['crop']:
                    # Estimate crop size (simplified)
                    target_w, target_h = settings['aspect']
                    target_aspect = target_w / target_h
                    current_aspect = new_size[0] / new_size[1]
                    
                    if current_aspect > target_aspect:
                        crop_w = int(new_size[1] * target_aspect)
                        crop_h = new_size[1]
                    else:
                        crop_w = new_size[0]
                        crop_h = int(new_size[0] / target_aspect)
                    
                    new_size = (crop_w, crop_h)
                    action += " + Crop"
                
                print(f"  📸 {filename}")
                print(f"     {original_size[0]}x{original_size[1]} → {new_size[0]}x{new_size[1]} ({action})")
                
        except Exception as e:
            print(f"     ⚠️  Could not preview: {e}")
    
    print(f"\n{Fore.YELLOW}This preview shows {sample_count} of {len(sample_images)} images")

# === Enhanced Error Handling ===
@contextmanager
def error_context(operation, filename=None):
    """Context manager for better error handling"""
    try:
        yield
    except KeyboardInterrupt:
        raise
    except Exception as e:
        error_msg = f"Failed to {operation}"
        if filename:
            error_msg += f" for {filename}"
        error_msg += f": {str(e)}"
        print(f"\n{Fore.RED}❌ {error_msg}")
        
        retry = get_user_input("Retry this operation? [y/n/s=skip]", "s", ["y", "n", "s"])
        if retry == "y":
            return "retry"
        elif retry == "s":
            return "skip" 
        else:
            sys.exit()

# Suppress PIL DecompressionBombWarning
import warnings
warnings.simplefilter("ignore", Image.DecompressionBombWarning)

# === Main Application Flow ===
def main():
    global current_batch_folder, tmp_log_path
    
    # === Folder setup ===
    input_folder = 'input_images'
    base_output_folder = 'resized_images'
    os.makedirs(base_output_folder, exist_ok=True)
    
    # === File scanning with warnings ===
    print(f"{Fore.CYAN}📂 Scanning '{input_folder}'...")
    
    supported_exts = (
        '.png', '.jpg', '.jpeg', '.webp', '.cr3',
        '.bmp', '.tif', '.tiff', '.ico', '.avif', '.heic',
        '.ppm', '.pgm', '.pbm', '.tga'
    )
    
    if not os.path.isdir(input_folder):
        print(f"{Fore.RED}❌ Input folder '{input_folder}' not found.")
        print(f"{Fore.YELLOW}💡 Create the folder and add images, then restart.")
        input("Press Enter to exit...")
        sys.exit()
    
    all_files = os.listdir(input_folder)
    image_files = [f for f in all_files if f.lower().endswith(supported_exts)]
    irrelevant_files = [f for f in all_files if not f.lower().endswith(supported_exts)]
    
    print(f"{Fore.GREEN}✅ Images found: {len(image_files)}")
    if irrelevant_files:
        print(f"{Fore.YELLOW}📋 Other files: {len(irrelevant_files)} (will be ignored)")
    
    # Enhanced batch warnings
    if len(image_files) > 100:
        estimated_time = len(image_files) * 2  # Rough estimate: 2 seconds per image
        print(f"{Fore.YELLOW}⏱️  Large batch detected! Estimated time: ~{estimated_time//60}min {estimated_time%60}s")
        
        continue_large = get_user_input("Continue with large batch? [y/n]", "y", ["y", "n"])
        if continue_large == "n":
            sys.exit()
    
    # Calculate total input size
    total_input_size = sum(os.path.getsize(os.path.join(input_folder, f)) for f in image_files) // (1024 * 1024)
    print(f"{Fore.MAGENTA}📊 Total input size: {total_input_size} MB")
    
    # Validation warnings
    warnings = validate_and_warn_images(image_files, input_folder)
    if warnings:
        print(f"\n{Fore.YELLOW}⚠️  Image Analysis Warnings:")
        for warning in warnings:
            print(f"  {warning}")
        
        continue_anyway = get_user_input("Continue anyway? [y/n]", "y", ["y", "n"])
        if continue_anyway == "n":
            sys.exit()
    
    # Create session log
    tmp_log_path = os.path.join(base_output_folder, f"session_scan_{datetime.now().strftime('%H%M%S')}.txt")
    with open(tmp_log_path, "w") as f:
        f.write(f"=== TerminallyQuick v{__version__} Session Log ===\n")
        f.write(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total Images: {len(image_files)} ({total_input_size} MB)\n")
        f.write(f"Other Files: {len(irrelevant_files)}\n\n")
        f.write("Image Details:\n")
        for img in image_files:
            size_kb = os.path.getsize(os.path.join(input_folder, img)) // 1024
            f.write(f"✔️ {img} ({size_kb} KB)\n")
        if irrelevant_files:
            f.write("\nIgnored Files:\n")
            for irr in irrelevant_files:
                f.write(f"❌ {irr}\n")
    
    if len(image_files) == 0:
        print(f"\n{Fore.RED}🚫 No supported images found.")
        print(f"{Fore.YELLOW}💡 Add PNG, JPEG, WEBP, or other image files to '{input_folder}'")
        input("Press Enter to exit...")
        sys.exit()
    
    # === Mode Selection and Settings ===
    mode = select_mode()
    
    if mode == "quick":
        settings = quick_mode_selection()
    elif mode == "smart":
        settings = smart_analyze_and_suggest(image_files, input_folder)
    else:  # expert
        settings = expert_mode_selection()
    
    # === Preview Option ===
    show_preview_option = get_user_input("Show preview before processing? [y/n]", "y", ["y", "n"])
    if show_preview_option == "y":
        show_preview(settings, image_files)
        
        proceed = get_user_input("Proceed with processing? [y/n]", "y", ["y", "n"])
        if proceed == "n":
            print(f"{Fore.YELLOW}Processing cancelled.")
            sys.exit()
    
    # === Processing Setup ===
    timestamp = datetime.now().strftime("%d%m%y_%H%M%S")
    existing_runs = [d for d in os.listdir(base_output_folder) if d.startswith("run")]
    run_count = len(existing_runs) + 1
    
    output_folder = os.path.join(base_output_folder, 
                                f"run{run_count}_{settings['name'].lower().replace(' ', '_')}_{timestamp}")
    os.makedirs(output_folder)
    current_batch_folder = output_folder
    
    print(f"\n{Fore.GREEN}🚀 Starting processing...")
    print(f"{Fore.CYAN}📁 Output: {output_folder}")
    
    # === Enhanced Processing Loop ===
    return process_images_with_enhanced_ux(image_files, settings, input_folder, output_folder, timestamp, total_input_size)

# === Enhanced Processing Function ===
def process_images_with_enhanced_ux(image_files, settings, input_folder, output_folder, timestamp, total_input_size):
    """Process images with enhanced UX feedback"""
    
    start_time = time.time()
    total = len(image_files)
    processed_count = 0
    skipped_count = 0
    error_count = 0
    total_output_size = 0
    
    log_lines = [
        f"TerminallyQuick v{__version__} Processing Log",
        f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "=== Settings ===",
        f"Preset: {settings['name']}",
        f"Format: {settings['format']}",
        f"Size: {settings['size']}px",
        f"Quality: {settings['quality']}%",
        f"Cropping: {'Yes' if settings['crop'] else 'No'}",
        ""
    ]
    
    if settings['crop']:
        log_lines.append(f"Aspect Ratio: {settings['aspect'][0]}:{settings['aspect'][1]}")
        log_lines.append(f"Anchor: {settings['anchor']}")
        log_lines.append("")
    
    # Processing loop with enhanced error handling
    failed_images = []
    
    for i, filename in enumerate(image_files, 1):
        if processing_interrupted:
            break
            
        print_progress_bar(i, total, filename, start_time)
        
        with error_context("process image", filename) as ctx:
            result = process_single_image(filename, settings, input_folder, output_folder, timestamp)
            
            if result == "retry":
                continue  # Retry this image
            elif result == "skip":
                skipped_count += 1
                failed_images.append(filename)
                continue
            elif result:
                processed_count += 1
                total_output_size += result['file_size_kb']
                
                # Add to log
                log_lines.append(f"✅ {filename}")
                log_lines.append(f"   {result['original_size']} → {result['final_size']}")
                log_lines.append(f"   File size: {result['file_size_kb']} KB")
                log_lines.append("")
    
    # Clear progress bar
    print("\n" + " " * 80 + "\r", end="")
    
    # === Final Results ===
    processing_time = round(time.time() - start_time, 2)
    compression_ratio = (total_input_size * 1024 / total_output_size) if total_output_size > 0 else 0
    
    # Enhanced success message
    print(f"""
{Fore.GREEN}{Style.BRIGHT}🎉 Processing Complete!{Style.RESET_ALL}

{Fore.CYAN}📊 Results Summary:
  ✅ Processed: {processed_count} images
  ⏭️  Skipped: {skipped_count} images  
  ❌ Errors: {error_count} images
  📁 Output: {os.path.basename(output_folder)}
  
📈 Size Analysis:
  📥 Input: {total_input_size} MB
  📤 Output: {round(total_output_size / 1024, 2)} MB
  🗜️  Compression: {compression_ratio:.1f}:1 ratio
  ⏱️  Time: {processing_time}s ({round(processing_time/processed_count, 1)}s per image)
""")
    
    # Save enhanced log
    log_lines.extend([
        "=== Final Results ===",
        f"Successfully processed: {processed_count}/{total}",
        f"Skipped: {skipped_count}",
        f"Total processing time: {processing_time}s",
        f"Average per image: {round(processing_time/processed_count, 1)}s",
        f"Compression ratio: {compression_ratio:.1f}:1",
        f"Output folder: {output_folder}"
    ])
    
    if failed_images:
        log_lines.append("\nFailed Images:")
        for failed in failed_images:
            log_lines.append(f"❌ {failed}")
    
    log_path = os.path.join(output_folder, "processing_log.txt")
    with open(log_path, "w") as log_file:
        log_file.write("\n".join(log_lines))
    
    # Auto-open results folder
    auto_open = get_user_input("Open results folder? [y/n]", "y", ["y", "n"])
    if auto_open == "y":
        open_file_cross_platform(output_folder)
    
    # === Enhanced Next Actions ===
    print(f"\n{Fore.CYAN}What's next?")
    print("  [r] Process another batch")
    print("  [s] Process same images with different settings")
    print("  [v] View detailed log") 
    print("  [o] Open output folder")
    print("  [q] Quit")
    
    while True:
        action = get_user_input("Next action", "q", ["r", "s", "v", "o", "q"])
        
        if action == "r":
            os.execv(sys.executable, [sys.executable] + sys.argv)
        elif action == "s":
            # Restart with same images but new settings
            main()
        elif action == "v":
            open_file_cross_platform(log_path)
            continue
        elif action == "o": 
            open_file_cross_platform(output_folder)
            continue
        elif action == "q":
            print(f"{Fore.GREEN}Happy developing! 🚀")
            break

def process_single_image(filename, settings, input_folder, output_folder, timestamp):
    """Process a single image with error handling"""
    try:
        img_path = os.path.join(input_folder, filename)
        
        # Handle CR3 files
        if filename.lower().endswith(".cr3"):
            if not HAS_EXIFTOOL:
                print(f"\n{Fore.RED}⚠️ CR3 requires exiftool. Install from: https://exiftool.org/")
                return "skip"
                
            converted_path, orientation_value = convert_cr3_to_jpeg(img_path, input_folder)
            if not converted_path:
                return "skip"
            img_path = converted_path
        else:
            orientation_value = None
        
        with Image.open(img_path) as img:
            original_size = img.size
            
            # Apply orientation correction
            if orientation_value is not None:
                if orientation_value == 3: img = img.rotate(180, expand=True)
                elif orientation_value == 6: img = img.rotate(270, expand=True) 
                elif orientation_value == 8: img = img.rotate(90, expand=True)
            
            # Convert to appropriate mode
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                img = apply_exif_orientation(img.convert("RGBA"))
                has_alpha = True
            else:
                img = apply_exif_orientation(img.convert("RGB"))
                has_alpha = False
            
            # Resize
            width, height = img.size
            short_edge = min(width, height)
            
            if short_edge <= settings['size']:
                new_img = img.copy()
            else:
                if width < height:
                    new_width = settings['size']
                    new_height = int((settings['size'] / width) * height)
                else:
                    new_height = settings['size']
                    new_width = int((settings['size'] / height) * width)
                new_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Apply cropping
            if settings['crop']:
                new_img = crop_to_ratio_with_anchor(new_img, settings['aspect'], settings['anchor'])
            
            # Generate filename and save
            web_filename = generate_web_friendly_filename(filename, settings, timestamp)
            output_path = os.path.join(output_folder, web_filename)
            
            # Save with appropriate settings
            save_kwargs = {"quality": settings['quality']}
            if settings['format'] == "WEBP":
                save_kwargs["lossless"] = has_alpha
                save_kwargs["method"] = 6  # Better compression
            
            if settings['format'] in ["JPEG", "PDF"]:
                new_img = new_img.convert("RGB")
            
            new_img.save(output_path, format=settings['format'], **save_kwargs)
            file_size_kb = get_file_size_kb(output_path)
            
            return {
                'original_size': f"{original_size[0]}x{original_size[1]}",
                'final_size': f"{new_img.size[0]}x{new_img.size[1]}",
                'file_size_kb': file_size_kb
            }
            
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error processing {filename}: {e}")
        return "skip"

# === Helper Functions (CR3, EXIF, Cropping) ===
def convert_cr3_to_jpeg(cr3_path, input_folder):
    import subprocess
    temp_cr3_folder = os.path.join(input_folder, "temp_cr3")
    os.makedirs(temp_cr3_folder, exist_ok=True)
    base = os.path.splitext(os.path.basename(cr3_path))[0]
    temp_path = os.path.join(temp_cr3_folder, f"{base}_preview.jpg")
    extract_cmd = f'exiftool -b -PreviewImage "{cr3_path}" > "{temp_path}"'
    os.system(extract_cmd)
    try:
        orientation_output = subprocess.check_output(
            ['exiftool', '-Orientation#', cr3_path],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        orientation_value = int(orientation_output.split(":")[-1].strip())
    except Exception:
        orientation_value = None
    return temp_path if os.path.exists(temp_path) else None, orientation_value

def apply_exif_orientation(image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation, None)
            if orientation_value == 3:
                image = image.rotate(180, expand=True)
            elif orientation_value == 6:
                image = image.rotate(270, expand=True)
            elif orientation_value == 8:
                image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        pass
    return image

def crop_to_ratio_with_anchor(img, target_ratio, anchor='center'):
    width, height = img.size
    target_w, target_h = target_ratio
    target_aspect = target_w / target_h
    current_aspect = width / height

    if current_aspect > target_aspect:
        new_width = int(height * target_aspect)
        new_height = height
    else:
        new_width = width
        new_height = int(width / target_aspect)

    left = {
        'left': 0,
        'center': (width - new_width) // 2,
        'right': width - new_width
    }[anchor.split('-')[-1]]

    top = {
        'top': 0,
        'center': (height - new_height) // 2,
        'bottom': height - new_height
    }[anchor.split('-')[0]]

    return img.crop((left, top, left + new_width, top + new_height))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n{Fore.RED}💥 Unexpected error: {e}")
        print(f"{Fore.YELLOW}💡 Please report this issue on GitHub")
        input("Press Enter to exit...")
