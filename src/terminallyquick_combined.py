#!/usr/bin/env python3

"""
TerminallyQuick Combined v2.0 - Enhanced UX Edition
Standard + Enhanced Web Developer Features with Improved User Experience
"""

__version__ = "2.0"
__author__ = "Daedraheart"

from PIL import Image, ExifTags
import os
from datetime import datetime
import time
from colorama import init, Fore, Style
import shutil, textwrap
import sys
import platform
import json

# Check for exiftool (required for CR3 support)
HAS_EXIFTOOL = shutil.which("exiftool") is not None

init(autoreset=True)

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
        "description": "Square thumbnails for web galleries",
        "allow_upscale": False
    },
    "2": {
        "name": "Hero Images",
        "format": "WEBP", 
        "size": 1200,
        "quality": 90,
        "crop": True,
        "aspect": (16, 9),
        "anchor": "center",
        "description": "Widescreen hero banners",
        "allow_upscale": True
    },
    "3": {
        "name": "Blog Images",
        "format": "WEBP",
        "size": 800,
        "quality": 85,
        "crop": False,
        "aspect": None,
        "anchor": None,
        "description": "Optimized blog post images",
        "allow_upscale": True
    },
    "4": {
        "name": "Social Media",
        "format": "JPEG",
        "size": 1080,
        "quality": 90,
        "crop": True,
        "aspect": (1, 1),
        "anchor": "center",
        "description": "Instagram/social posts",
        "allow_upscale": True
    },
    "5": {
        "name": "E-commerce Product",
        "format": "WEBP",
        "size": 600,
        "quality": 95,
        "crop": True,
        "aspect": (4, 5),
        "anchor": "center",
        "description": "Product catalog images",
        "allow_upscale": True
    },
    "6": {
        "name": "Profile Pictures",
        "format": "WEBP",
        "size": 250,
        "quality": 90,
        "crop": True,
        "aspect": (1, 1),
        "anchor": "center",
        "description": "User profile avatars",
        "allow_upscale": False
    },
    "7": {
        "name": "Mobile Optimized",
        "format": "WEBP",
        "size": 480,
        "quality": 80,
        "crop": False,
        "aspect": None,
        "anchor": None,
        "description": "Mobile-first responsive images",
        "allow_upscale": False
    }
}

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

def setup_logging(output_folder, settings, version_mode):
    """Setup detailed logging for the session"""
    log_data = {
        "session": {
            "timestamp": datetime.now().isoformat(),
            "version_mode": version_mode,
            "settings": settings,
            "output_folder": output_folder
        },
        "processing": {
            "images": [],
            "stats": {
                "total_processed": 0,
                "total_skipped": 0,
                "upscaled_count": 0,
                "downscaled_count": 0,
                "kept_original_size": 0
            }
        }
    }
    
    # Save settings JSON
    settings_path = os.path.join(output_folder, "processing_settings.json")
    with open(settings_path, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    return log_data, settings_path

def log_image_processing(log_data, filename, original_size, final_size, action, file_size_kb, variant_name=""):
    """Log detailed information about each image processed"""
    image_log = {
        "filename": filename,
        "variant": variant_name,
        "original_size": original_size,
        "final_size": final_size,
        "action": action,
        "file_size_kb": file_size_kb,
        "timestamp": datetime.now().isoformat()
    }
    
    log_data["processing"]["images"].append(image_log)
    
    # Update stats
    stats = log_data["processing"]["stats"]
    if action == "upscaled":
        stats["upscaled_count"] += 1
    elif action == "downscaled":
        stats["downscaled_count"] += 1
    elif action == "kept_original":
        stats["kept_original_size"] += 1
    
    stats["total_processed"] += 1

def save_final_log(log_data, settings_path, processing_time, total_input_mb, total_output_size):
    """Save final processing log with complete stats"""
    log_data["session"]["processing_time_seconds"] = processing_time
    log_data["session"]["total_input_mb"] = total_input_mb
    log_data["session"]["total_output_kb"] = total_output_size
    log_data["session"]["compression_ratio"] = (total_input_mb * 1024 / total_output_size) if total_output_size > 0 else 0
    
    with open(settings_path, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    # Also create a readable summary
    summary_path = settings_path.replace('.json', '_summary.txt')
    with open(summary_path, 'w') as f:
        f.write(f"TerminallyQuick Processing Summary\n")
        f.write(f"{'='*50}\n\n")
        f.write(f"Session: {log_data['session']['timestamp']}\n")
        f.write(f"Mode: {log_data['session']['version_mode']}\n")
        f.write(f"Preset: {log_data['session']['settings']['name']}\n")
        f.write(f"Format: {log_data['session']['settings']['format']}\n")
        f.write(f"Target Size: {log_data['session']['settings']['size']}px\n")
        f.write(f"Quality: {log_data['session']['settings']['quality']}%\n")
        f.write(f"Upscaling: {'Enabled' if log_data['session']['settings'].get('allow_upscale') else 'Disabled'}\n")
        f.write(f"Processing Time: {processing_time}s\n\n")
        
        stats = log_data['processing']['stats']
        f.write(f"Processing Stats:\n")
        f.write(f"  Total Processed: {stats['total_processed']}\n")
        f.write(f"  Upscaled: {stats['upscaled_count']}\n")
        f.write(f"  Downscaled: {stats['downscaled_count']}\n")
        f.write(f"  Kept Original: {stats['kept_original_size']}\n\n")
        
        f.write(f"Individual Image Details:\n")
        for img in log_data['processing']['images']:
            variant_info = f" ({img['variant']})" if img['variant'] else ""
            f.write(f"  {img['filename']}{variant_info}:\n")
            f.write(f"    {img['original_size']} → {img['final_size']} | {img['action']} | {img['file_size_kb']} KB\n")

def get_resize_action_and_emoji(original_short_edge, target_size, allow_upscale):
    """Determine what action will be taken and appropriate emoji/description"""
    if original_short_edge > target_size:
        return "downscaled", "📉", "Downscaled"
    elif original_short_edge < target_size and allow_upscale:
        return "upscaled", "📈", "Upscaled"
    else:
        return "kept_original", "📍", "Kept original size"

def generate_web_friendly_filename(original_name, settings, timestamp):
    """Generate SEO-friendly filenames"""
    base = os.path.splitext(original_name)[0]
    clean_base = "".join(c.lower() if c.isalnum() else "_" for c in base)
    clean_base = clean_base.strip("_")
    
    if settings.get('responsive'):
        size_suffix = f"{settings['size']}w"
    else:
        size_suffix = f"{settings['size']}w" if not settings.get('crop') else f"{settings['size']}x{settings['size']}"
    
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

# === Version Selection ===
def show_version_selector():
    print(f"""{Fore.CYAN}{Style.BRIGHT}
╔══════════════════════════════════════════════════════════╗
║                 TerminallyQuick v{__version__}                   ║
║              Version Selection Assistant                 ║
╚══════════════════════════════════════════════════════════╝
{Style.RESET_ALL}""")

    print(f"{Fore.YELLOW}Choose your version:{Style.RESET_ALL}")
    print(f"""
{Fore.GREEN}📸 Standard Version{Style.RESET_ALL}
  ✅ Original TerminallyQuick experience
  ✅ General-purpose image resizing
  ✅ All formats supported (PNG, JPEG, WEBP, CR3, etc.)
  ✅ Custom sizing and cropping
  ✅ Perfect for photographers and general users

{Fore.CYAN}🌐 Enhanced Web Developer Version{Style.RESET_ALL}
  ✅ Everything in Standard, PLUS:
  🚀 7 Web Developer presets (thumbnails, hero images, etc.)
  📱 Responsive multi-size generation (mobile/tablet/desktop)
  🏷️ SEO-friendly filename generation
  📊 Compression ratio tracking
  ⚡ Web-optimized defaults (WEBP, 800px, 85% quality)
  📁 Organized output folders by preset type
  💾 Settings export as JSON for team sharing
  🎯 Modern web formats (AVIF support)
""")

    while True:
        print(f"{Fore.CYAN}Select version:")
        print("  [1] Standard - General image resizing")
        print("  [2] Enhanced - Web Developer focused") 
        print("  [q] Quit")
        
        choice = input(f"\n{Fore.YELLOW}Your choice [default 2]: {Style.RESET_ALL}").strip().lower()
        
        if choice == 'q':
            print(f"{Fore.RED}Goodbye!")
            sys.exit()
        elif choice == '1':
            return 'standard'
        elif choice == '2' or choice == '':
            return 'enhanced'
        else:
            print(f"{Fore.RED}Invalid choice. Please enter 1, 2, or q.")

# === Main Application Logic ===
def main():
    # Suppress PIL warnings
    import warnings
    warnings.simplefilter("ignore", Image.DecompressionBombWarning)
    
    # Get version choice
    version_mode = show_version_selector()
    
    # === Common Setup ===
    input_folder = 'input_images'
    base_output_folder = 'resized_images'
    
    # Ensure all required folders exist
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(base_output_folder, exist_ok=True)
    
    # Create helpful readme in input folder if it's empty
    if not os.listdir(input_folder):
        readme_path = os.path.join(input_folder, 'README_ADD_IMAGES_HERE.txt')
        with open(readme_path, 'w') as f:
            f.write("Welcome to TerminallyQuick v2.0!\n\n")
            f.write("📁 This is your INPUT folder\n")
            f.write("\n🎯 HOW TO USE:\n")
            f.write("1. Delete this file\n")
            f.write("2. Add your images here (drag & drop works!)\n")
            f.write("3. Run TerminallyQuick again\n\n")
            f.write("📸 SUPPORTED FORMATS:\n")
            f.write("✅ PNG, JPEG, WEBP, BMP, TIFF, ICO\n")
            f.write("✅ CR3 (Canon RAW) - requires exiftool\n")
            f.write("✅ AVIF, HEIC (modern formats)\n\n")
            f.write("🌐 PERFECT FOR:\n")
            f.write("• Web development & WordPress\n")
            f.write("• Social media content\n")
            f.write("• E-commerce product photos\n")
            f.write("• Blog images & thumbnails\n\n")
            f.write("💡 TIP: Use Quick Mode for fastest results!\n")
    
    # Title banner
    if version_mode == 'enhanced':
        print(Fore.CYAN + Style.BRIGHT + f"Terminally Quick {__version__} — Enhanced for Web Developers")
    else:
        print(Fore.CYAN + Style.BRIGHT + f"Terminally Quick {__version__} — by {__author__}")
    
    box_width = 60
    print(Fore.YELLOW + "[Q] Quit  |  [L] Log  |  [↵] Default\n" + Fore.CYAN + "─" * box_width + Style.RESET_ALL)
    
    # === File scanning ===
    print(f"\n{Fore.CYAN}📂 Scanning '{input_folder}'...")
    
    supported_exts = (
        '.png', '.jpg', '.jpeg', '.webp', '.cr3',
        '.bmp', '.tif', '.tiff', '.ico',
        '.ppm', '.pgm', '.pbm', '.tga'
    )
    
    if version_mode == 'enhanced':
        supported_exts += ('.avif', '.heic')
    
    if not os.path.isdir(input_folder):
        print(f"{Fore.RED}❌ Input folder '{input_folder}' not found. Please create it and add images.")
        sys.exit()
    
    all_files = os.listdir(input_folder)
    image_files = [f for f in all_files if f.lower().endswith(supported_exts)]
    irrelevant_files = [f for f in all_files if not f.lower().endswith(supported_exts)]
    
    print(f"{Fore.GREEN}✅ Images found: {len(image_files)}")
    print(f"{Fore.YELLOW}❌ Irrelevant files: {len(irrelevant_files)}")
    
    if version_mode == 'enhanced':
        total_input_size = sum(os.path.getsize(os.path.join(input_folder, f)) for f in image_files) // (1024 * 1024)
        print(f"{Fore.MAGENTA}📊 Total input size: {total_input_size} MB")
    
    if len(image_files) == 0:
        print(f"\n{Fore.RED}🚫 No supported images found in '{input_folder}'")
        print(f"{Fore.YELLOW}💡 What would you like to do?")
        print("   [1] Add images and retry")
        print("   [2] View supported formats")
        print("   [3] Open input folder")
        print("   [q] Quit")
        
        while True:
            choice = input(f"\n{Fore.CYAN}Your choice [1-3/q]: ").strip().lower()
            
            if choice == 'q':
                print(f"{Fore.YELLOW}👋 Thanks for using TerminallyQuick!")
                sys.exit()
            elif choice == '1':
                print(f"\n{Fore.GREEN}📁 Please add your images to the '{input_folder}' folder")
                print(f"{Fore.CYAN}💡 Supported formats: PNG, JPEG, WEBP, CR3, BMP, TIFF, AVIF, HEIC, etc.")
                input(f"{Fore.YELLOW}Press Enter when you've added images...")
                
                # Re-scan for images
                all_files = os.listdir(input_folder)
                image_files = [f for f in all_files if f.lower().endswith(supported_exts)]
                
                if len(image_files) > 0:
                    print(f"{Fore.GREEN}✅ Found {len(image_files)} images! Continuing...")
                    break
                else:
                    print(f"{Fore.RED}❌ Still no images found. Let's try again.")
                    continue
            elif choice == '2':
                print(f"\n{Fore.CYAN}📸 Supported Image Formats:")
                print("   • Common: PNG, JPEG, WEBP, BMP, TIFF")
                print("   • Professional: CR3 (Canon RAW), AVIF, HEIC")
                print("   • Legacy: ICO, PPM, PGM, PBM, TGA")
                print(f"\n{Fore.YELLOW}💡 Just drag & drop your images into '{input_folder}'")
                continue
            elif choice == '3':
                try:
                    open_file_cross_platform(input_folder)
                    print(f"{Fore.GREEN}✅ Opened '{input_folder}' folder")
                except:
                    print(f"{Fore.RED}❌ Could not open folder automatically")
                    print(f"{Fore.YELLOW}💡 Please manually navigate to: {os.path.abspath(input_folder)}")
                continue
            else:
                print(f"{Fore.RED}❌ Invalid choice. Please enter 1, 2, 3, or 'q'.")
                continue
    
    # === Settings Selection ===
    if version_mode == 'enhanced':
        settings = get_enhanced_settings()
    else:
        settings = get_standard_settings()
    
    # === Processing ===
    process_images(image_files, settings, version_mode)

def get_enhanced_settings():
    """Enhanced version with presets"""
    # Show web dev presets
    print(f"\n{Fore.GREEN}🚀 Web Developer Quick Presets:")
    print(f"{Fore.YELLOW}Choose a preset or go custom:")
    
    for key, preset in WEB_DEV_PRESETS.items():
        print(f"  {key}: {preset['name']} - {preset['description']}")
    print(f"  8: Custom Settings (advanced)")
    
    while True:
        choice = input(f"\n{Fore.CYAN}Enter preset (1-8) [default 3 - Blog Images]: ").strip().lower()
        
        if choice == 'q': sys.exit()
        if choice in WEB_DEV_PRESETS:
            return WEB_DEV_PRESETS[choice]
        elif choice == "" or choice == "3":
            return WEB_DEV_PRESETS["3"]
        elif choice == "8":
            return get_custom_settings(enhanced=True)
        
        print(f"{Fore.RED}Invalid input. Please enter 1-8 or 'q'.")

def get_standard_settings():
    """Standard version settings"""
    return get_custom_settings(enhanced=False)

def get_custom_settings(enhanced=False):
    """Get custom settings with enhanced options if enabled"""
    
    if enhanced:
        format_options = {
            "1": "WEBP", "2": "JPEG", "3": "PNG", "4": "TIFF",
            "5": "BMP", "6": "ICO", "7": "PDF", "8": "AVIF"
        }
        default_format = "WEBP"
        default_size = 800
        default_quality = 85
    else:
        format_options = {
            "1": "WEBP", "2": "JPEG", "3": "PNG", "4": "TIFF",
            "5": "BMP", "6": "ICO", "7": "PDF"
        }
        default_format = "WEBP"
        default_size = 550
        default_quality = 95
    
    # Format selection
    while True:
        print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
        print_current_selections()
        print(Fore.CYAN + "🔧 Choose export format")
        for key, fmt in format_options.items():
            suffix = " (recommended for web)" if fmt == "WEBP" and enhanced else ""
            suffix = " (next-gen web format)" if fmt == "AVIF" and enhanced else suffix
            print(f"  {key}: {fmt}{suffix}")
        
        format_choice = input("Enter choice [default 1]: ").strip().lower()
        if format_choice == 'q': sys.exit()
        if format_choice in format_options or format_choice == '':
            output_format = format_options.get(format_choice, default_format).upper()
            break
        print(f"{Fore.RED}Invalid input.")
    
    # Size selection
    while True:
        print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
        print_current_selections(output_format)
        print(Fore.CYAN + "🔢 Enter size for shortest side")
        if enhanced:
            print(f"{Fore.YELLOW}💡 Web Dev Suggestions:")
            print("   • 300px - Thumbnails")
            print("   • 480px - Mobile")
            print("   • 800px - Blog/content")
            print("   • 1200px - Hero images")
        
        size_input = input(f"Enter size in pixels [default {default_size}]: ").strip()
        if size_input.lower() == 'q': sys.exit()
        if size_input == '':
            size = default_size
            break
        try:
            size = int(size_input)
            if size > 0: break
        except ValueError: pass
        print(f"{Fore.RED}Invalid input. Enter a positive integer.")
    
    # Quality selection  
    while True:
        print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
        print_current_selections(output_format, size)
        print(Fore.CYAN + "🎚️ Enter export quality")
        if enhanced:
            print(f"{Fore.YELLOW}💡 Web Optimization:")
            print("   • 80-85: High compression, good for web")
            print("   • 90-95: Balanced quality/size")
        
        quality_input = input(f"Enter quality (50-100) [default {default_quality}]: ").strip()
        if quality_input.lower() == 'q': sys.exit()
        if quality_input == '':
            quality = default_quality
            break
        try:
            quality = int(quality_input)
            if 50 <= quality <= 100: break
        except ValueError: pass
        print(f"{Fore.RED}Invalid input. Enter 50-100.")
    
    # Upscaling option
    print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
    print_current_selections(output_format, size, quality)
    print(Fore.CYAN + "📈 Upscaling Policy")
    if enhanced:
        print(f"{Fore.YELLOW}💡 Smart Upscaling:")
        print("   • Yes: Small images will be enlarged to target size")
        print("   • No: Small images kept at original size (prevents pixelation)")
    
    upscale_input = input("Allow upscaling small images? (y/n) [default n]: ").strip().lower()
    allow_upscale = upscale_input in ('y', 'yes')
    
    # Cropping
    crop_input = input("\nDo you want to crop to an aspect ratio? (y/n): ").strip().lower()
    if crop_input == 'y':
        # Aspect ratio selection
        if enhanced:
            ratio_options = {
                "1": (1, 1, "Square - Social, thumbnails"),
                "2": (16, 9, "Widescreen - Hero banners"),
                "3": (4, 3, "Standard - Blog images"),
                "4": (4, 5, "Portrait - E-commerce"),
                "5": (21, 9, "Ultra-wide banners"),
                "6": (9, 16, "Vertical - Stories")
            }
        else:
            ratio_options = {
                "1": (4, 3, "Standard landscape"),
                "2": (1, 1, "Square"),
                "3": (16, 9, "Widescreen"),
                "4": (3, 2, "DSLR landscape"),
                "5": (4, 5, "Portrait"),
                "6": (2, 3, "Classic portrait")
            }
        
        print(Fore.CYAN + "📐 Choose aspect ratio:")
        for key, (w, h, desc) in ratio_options.items():
            print(f"  {key}: {w}:{h} ({desc})")
        
        ratio_choice = input("Enter choice [default 1]: ").strip()
        if ratio_choice.lower() == 'q': sys.exit()
        w, h, _ = ratio_options.get(ratio_choice, ratio_options["1"])
        
        anchor = "center"  # Default to center for simplicity
        
        return {
            "name": "Custom",
            "format": output_format,
            "size": size,
            "quality": quality,
            "crop": True,
            "aspect": (w, h),
            "anchor": anchor,
            "allow_upscale": allow_upscale
        }
    else:
        return {
            "name": "Custom",
            "format": output_format,
            "size": size,
            "quality": quality,
            "crop": False,
            "aspect": None,
            "anchor": None,
            "allow_upscale": allow_upscale
        }

def process_images(image_files, settings, version_mode):
    """Process images with given settings and rich logging"""
    
    # Setup output folder
    timestamp = datetime.now().strftime("%d%m%y_%H%M%S")
    existing_runs = [d for d in os.listdir('resized_images') if d.startswith("run")]
    run_count = len(existing_runs) + 1
    
    if version_mode == 'enhanced':
        output_folder = os.path.join('resized_images', f"run{run_count}_{settings['name'].lower().replace(' ', '_')}_{timestamp}")
    else:
        output_folder = os.path.join('resized_images', f"run{run_count}_{timestamp}")
    
    os.makedirs(output_folder)
    
    # Setup logging
    log_data, settings_path = setup_logging(output_folder, settings, version_mode)
    
    # Ask about responsive sizes in enhanced mode
    multi_size = False
    size_variants = []
    
    if version_mode == 'enhanced' and not settings['crop']:
        multi_input = input(f"\n{Fore.CYAN}Generate responsive sizes? (y/n) [default n]: ").strip().lower()
        if multi_input == 'y':
            multi_size = True
            size_variants = [
                {"name": "small", "size": 480},
                {"name": "medium", "size": 800}, 
                {"name": "large", "size": 1200}
            ]
            # Create subfolders
            for variant in size_variants:
                os.makedirs(os.path.join(output_folder, variant['name']), exist_ok=True)
    
    if not multi_size:
        size_variants = [{"name": "", "size": settings['size']}]
    
    # Show processing preview
    print(f"\n{Fore.GREEN}✅ Ready to process {len(image_files)} images")
    print(f"{Fore.YELLOW}Settings: {settings['format']} | {settings['size']}px | Q{settings['quality']} | Upscaling: {'✅' if settings.get('allow_upscale') else '❌'}")
    
    if input("Proceed? (y/n) [default y]: ").strip().lower() not in ('', 'y'):
        sys.exit()
    
    # === Processing Loop ===
    start_time = time.time()
    total_output_size = 0
    processed_count = 0
    skipped_count = 0
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}🚀 Processing Images...{Style.RESET_ALL}\n")
    
    for i, filename in enumerate(image_files, 1):
        print(f"{Fore.CYAN}{Style.BRIGHT}[{i}/{len(image_files)}] {filename}{Style.RESET_ALL}")
        
        img_path = os.path.join('input_images', filename)
        
        # Handle CR3
        if filename.lower().endswith(".cr3"):
            if not HAS_EXIFTOOL:
                print(f"{Fore.RED}  ⚠️ CR3 requires exiftool. Skipping...")
                skipped_count += 1
                continue
            print(f"{Fore.MAGENTA}  🔄 Extracting CR3 preview...")
            converted_path, orientation_value = convert_cr3_to_jpeg(img_path, 'input_images')
            if not converted_path:
                print(f"{Fore.RED}  ❌ Failed to extract CR3. Skipping...")
                skipped_count += 1
                continue
            img_path = converted_path
        else:
            orientation_value = None
        
        try:
            with Image.open(img_path) as img:
                # Show original dimensions
                original_width, original_height = img.size
                original_short_edge = min(original_width, original_height)
                original_size_str = f"{original_width}x{original_height}"
                
                print(f"{Fore.BLUE}  📏 Original: {original_size_str} (shortest: {original_short_edge}px)")
                
                # Apply orientation corrections
                if orientation_value is not None:
                    print(f"{Fore.YELLOW}  🔄 Applying orientation correction...")
                    if orientation_value == 3: img = img.rotate(180, expand=True)
                    elif orientation_value == 6: img = img.rotate(270, expand=True)
                    elif orientation_value == 8: img = img.rotate(90, expand=True)
                
                # Handle transparency
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    img = apply_exif_orientation(img.convert("RGBA"))
                    has_alpha = True
                    if version_mode == 'enhanced':
                        print(f"{Fore.MAGENTA}  🎨 Transparency detected, using lossless compression")
                else:
                    img = apply_exif_orientation(img.convert("RGB"))
                    has_alpha = False
                
                # Process each size variant
                for size_variant in size_variants:
                    current_size = size_variant['size']
                    variant_name = size_variant['name']
                    
                    # Determine resize action
                    action, emoji, description = get_resize_action_and_emoji(
                        original_short_edge, current_size, settings.get('allow_upscale', False)
                    )
                    
                    # Enhanced resize logic with upscaling support
                    width, height = img.size
                    short_edge = min(width, height)
                    
                    if short_edge <= current_size and not settings.get('allow_upscale', False):
                        # Keep original size (no upscaling)
                        new_img = img.copy()
                        resize_info = f"kept at original size"
                    elif short_edge == current_size:
                        # Already perfect size
                        new_img = img.copy()
                        resize_info = f"already target size"
                    else:
                        # Resize (up or down) with smart resampling
                        if width < height:
                            new_width = current_size
                            new_height = int((current_size / width) * height)
                        else:
                            new_height = current_size
                            new_width = int((current_size / height) * width)
                        
                        # Use different resampling for upscaling vs downscaling
                        if short_edge < current_size:
                            # Upscaling - use BICUBIC for better quality
                            new_img = img.resize((new_width, new_height), Image.BICUBIC)
                            resize_info = f"upscaled from {short_edge}px"
                        else:
                            # Downscaling - use LANCZOS for sharpness
                            new_img = img.resize((new_width, new_height), Image.LANCZOS)
                            resize_info = f"downscaled from {short_edge}px"
                    
                    # Apply cropping
                    pre_crop_size = new_img.size
                    if settings['crop']:
                        new_img = crop_to_ratio_with_anchor(new_img, settings['aspect'], settings['anchor'])
                        if version_mode == 'enhanced':
                            crop_info = f" → cropped to {new_img.size[0]}x{new_img.size[1]}"
                        else:
                            crop_info = " + cropped"
                    else:
                        crop_info = ""
                    
                    # Generate filename
                    if version_mode == 'enhanced':
                        web_filename = generate_web_friendly_filename(filename, {
                            'format': settings['format'],
                            'size': current_size,
                            'crop': settings['crop'],
                            'responsive': multi_size
                        }, timestamp)
                    else:
                        base_name = os.path.splitext(filename)[0]
                        extension = settings['format'].lower()
                        web_filename = f"{base_name}_{timestamp}.{extension}"
                    
                    # Save path
                    if multi_size and variant_name:
                        output_path = os.path.join(output_folder, variant_name, web_filename)
                    else:
                        output_path = os.path.join(output_folder, web_filename)
                    
                    # Save image with optimized settings
                    save_kwargs = {"quality": settings['quality']}
                    if settings['format'] == "WEBP":
                        save_kwargs["lossless"] = has_alpha
                        if version_mode == 'enhanced':
                            save_kwargs["method"] = 6  # Best compression
                    
                    if settings['format'] in ["JPEG", "PDF", "AVIF"]:
                        new_img = new_img.convert("RGB")
                    
                    try:
                        new_img.save(output_path, format=settings['format'], **save_kwargs)
                        file_size_kb = get_file_size_kb(output_path)
                        total_output_size += file_size_kb
                        
                        # Calculate compression ratio for this image
                        original_size_kb = get_file_size_kb(img_path)
                        if original_size_kb > 0:
                            compression_ratio = original_size_kb / file_size_kb
                        else:
                            compression_ratio = 1.0
                        
                        # Rich terminal output
                        final_size_str = f"{new_img.size[0]}x{new_img.size[1]}"
                        
                        if multi_size:
                            print(f"{Fore.GREEN}  {emoji} {variant_name.upper()}: {original_size_str} → {final_size_str}{crop_info}")
                            print(f"{Fore.WHITE}    📦 {file_size_kb} KB ({compression_ratio:.1f}:1 compression) | {resize_info}")
                        else:
                            print(f"{Fore.GREEN}  {emoji} {description}: {original_size_str} → {final_size_str}{crop_info}")
                            print(f"{Fore.WHITE}  📦 {file_size_kb} KB ({compression_ratio:.1f}:1 compression) | {resize_info}")
                        
                        # Log to file
                        log_image_processing(
                            log_data, filename, original_size_str, final_size_str, 
                            action, file_size_kb, variant_name
                        )
                        
                        processed_count += 1
                        
                    except Exception as e:
                        print(f"{Fore.RED}  ❌ Save failed: {str(e)}")
                        log_data["processing"]["stats"]["total_skipped"] += 1
                        skipped_count += 1
        
        except Exception as e:
            print(f"{Fore.RED}  ❌ Processing failed: {str(e)}")
            log_data["processing"]["stats"]["total_skipped"] += 1
            skipped_count += 1
        
        print()  # Add spacing between images
    
    # === Results & Final Logging ===
    processing_time = round(time.time() - start_time, 2)
    
    # Calculate final stats
    total_input_mb = sum(os.path.getsize(os.path.join('input_images', f)) for f in image_files) // (1024 * 1024)
    compression_ratio = (total_input_mb * 1024 / total_output_size) if total_output_size > 0 else 0
    
    # Save final log
    save_final_log(log_data, settings_path, processing_time, total_input_mb, total_output_size)
    
    # Get processing stats
    stats = log_data["processing"]["stats"]
    
    # Enhanced results display
    if version_mode == 'enhanced':
        print(f"""
{Fore.GREEN}{Style.BRIGHT}🎉 Processing Complete!{Style.RESET_ALL}
{Fore.CYAN}📊 Session Results:
  • Images processed: {processed_count}
  • Images skipped: {skipped_count}
  • Total input size: {total_input_mb} MB
  • Total output size: {round(total_output_size / 1024, 2)} MB  
  • Overall compression: {compression_ratio:.1f}:1
  • Processing time: {processing_time}s

{Fore.YELLOW}🔍 Resize Operations:
  📈 Upscaled: {stats['upscaled_count']} images
  📉 Downscaled: {stats['downscaled_count']} images
  📍 Kept original: {stats['kept_original_size']} images

{Fore.MAGENTA}📁 Output Location: {output_folder}
💾 Detailed logs saved: processing_settings.json & processing_settings_summary.txt
""")
    else:
        print(f"""
{Fore.GREEN}{Style.BRIGHT}✅ All images processed successfully!{Style.RESET_ALL}

{Fore.CYAN}📊 Results:
  • Images processed: {processed_count}
  • Images skipped: {skipped_count}
  • Processing time: {processing_time}s
  • Output folder: {output_folder}

{Fore.YELLOW}🔍 Operations:
  📈 Upscaled: {stats['upscaled_count']} images
  📉 Downscaled: {stats['downscaled_count']} images
  📍 Kept original: {stats['kept_original_size']} images
""")
    
    # Open output folder
    open_output = input(f"\n{Fore.CYAN}Open output folder? (y/n) [default y]: ").strip().lower()
    if open_output in ('', 'y'):
        open_file_cross_platform(output_folder)
    
    # Show log files location
    if version_mode == 'enhanced':
        view_logs = input(f"\n{Fore.CYAN}View processing summary? (y/n) [default n]: ").strip().lower()
        if view_logs == 'y':
            summary_path = settings_path.replace('.json', '_summary.txt')
            open_file_cross_platform(summary_path)
    
    # Cleanup CR3 temp files
    temp_cr3_folder = os.path.join('input_images', "temp_cr3")
    if os.path.exists(temp_cr3_folder):
        shutil.rmtree(temp_cr3_folder)
    
    print(f"{Fore.YELLOW}👋 Thanks for using TerminallyQuick!")

if __name__ == "__main__":
    main()
