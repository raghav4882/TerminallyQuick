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

# === Cross-platform file opener ===
def open_file_cross_platform(path):
    if platform.system() == "Darwin":
        os.system(f'open "{path}"')
    elif platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Linux":
        os.system(f'xdg-open "{path}"')
    else:
        print(f"{Fore.RED}⚠️ Unsupported OS. Please open the file manually: {path}")

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
        "description": "Square thumbnails for web galleries"
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
    },
    "5": {
        "name": "E-commerce Product",
        "format": "WEBP",
        "size": 600,
        "quality": 95,
        "crop": True,
        "aspect": (4, 5),
        "anchor": "center",
        "description": "Product catalog images"
    },
    "6": {
        "name": "Profile Pictures",
        "format": "WEBP",
        "size": 250,
        "quality": 90,
        "crop": True,
        "aspect": (1, 1),
        "anchor": "center",
        "description": "User profile avatars"
    },
    "7": {
        "name": "Mobile Optimized",
        "format": "WEBP",
        "size": 480,
        "quality": 80,
        "crop": False,
        "aspect": None,
        "anchor": None,
        "description": "Mobile-first responsive images"
    }
}

# === File size and naming functions ===
def get_file_size_kb(path):
    return os.path.getsize(path) // 1024

def generate_web_friendly_filename(original_name, settings, timestamp):
    """Generate SEO-friendly filenames"""
    base = os.path.splitext(original_name)[0]
    # Remove spaces, special chars, make lowercase
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

# Suppress PIL DecompressionBombWarning
import warnings
warnings.simplefilter("ignore", Image.DecompressionBombWarning)

# === Title Banner ===
box_width = 60
print(Fore.CYAN + Style.BRIGHT + f"Terminally Quick {__version__} — Enhanced for Web Developers")
print(Fore.YELLOW + "[Q] Quit  |  [L] Log  |  [↵] Default\n" + Fore.CYAN + "─" * box_width + Style.RESET_ALL)

# === Folder setup ===
input_folder = 'input_images'
base_output_folder = 'resized_images'

# Ensure base output folder exists
os.makedirs(base_output_folder, exist_ok=True)

# === File Type Scan Before Proceeding ===
print(f"\n{Fore.CYAN}📂 Scanning '{input_folder}'...")

supported_exts = (
    '.png', '.jpg', '.jpeg', '.webp', '.cr3',
    '.bmp', '.tif', '.tiff', '.ico',
    '.ppm', '.pgm', '.pbm', '.tga', '.avif', '.heic'
)

if not os.path.isdir(input_folder):
    print(f"{Fore.RED}❌ Input folder '{input_folder}' not found. Please create it and add images.")
    sys.exit()

all_files = os.listdir(input_folder)
image_files = [f for f in all_files if f.lower().endswith(supported_exts)]
irrelevant_files = [f for f in all_files if not f.lower().endswith(supported_exts)]

print(f"{Fore.GREEN}✅ Images found: {len(image_files)}")
print(f"{Fore.YELLOW}❌ Irrelevant files: {len(irrelevant_files)}")

# Calculate total input size
total_input_size = sum(os.path.getsize(os.path.join(input_folder, f)) for f in image_files) // (1024 * 1024)
print(f"{Fore.MAGENTA}📊 Total input size: {total_input_size} MB")

tmp_log_path = os.path.join(base_output_folder, f"session_file_log_{datetime.now().strftime('%H%M%S')}.txt")
with open(tmp_log_path, "w") as f:
    f.write("=== Files Scanned ===\n")
    f.write(f"\nTotal Input Size: {total_input_size} MB\n")
    f.write("\nFound Images:\n")
    for img in image_files:
        size_kb = os.path.getsize(os.path.join(input_folder, img)) // 1024
        f.write(f"✔️ {img} ({size_kb} KB)\n")
    f.write("\nSkipped Files:\n")
    for irr in irrelevant_files:
        f.write(f"❌ {irr}\n")

print(f"{Fore.MAGENTA}ℹ️  File list saved for this scan: {tmp_log_path}")

if len(image_files) == 0:
    print(f"\n{Fore.RED}🚫 No supported images found. Please add image files to '{input_folder}' and try again.")
    sys.exit()

# === Web Developer Quick Start ===
print(f"\n{Fore.GREEN}🚀 Web Developer Quick Presets:")
print(f"{Fore.YELLOW}Choose a preset or go custom:")

for key, preset in WEB_DEV_PRESETS.items():
    print(f"  {key}: {preset['name']} - {preset['description']}")
print(f"  8: Custom Settings (advanced)")

preset_choice = None
while True:
    print(f"\n{Fore.CYAN}Enter preset (1-8) [default 3 - Blog Images]:")
    choice = input("> ").strip().lower()
    
    if choice == 'q':
        print(Fore.RED + "Aborted.")
        sys.exit()
    if choice == 'l':
        print(Fore.MAGENTA + "Opening scan log file...\n")
        open_file_cross_platform(tmp_log_path)
        continue
    
    if choice in WEB_DEV_PRESETS:
        preset_choice = WEB_DEV_PRESETS[choice]
        break
    elif choice == "" or choice == "3":  # Default
        preset_choice = WEB_DEV_PRESETS["3"]
        break
    elif choice == "8":
        preset_choice = None  # Custom
        break
    
    print(f"{Fore.RED}Invalid input. Please enter 1-8, Enter, 'q', or 'l'.")

# === Custom Settings or Preset Confirmation ===
if preset_choice:
    print(f"\n{Fore.GREEN}📋 Selected Preset: {preset_choice['name']}")
    print(f"  - Format: {preset_choice['format']}")
    print(f"  - Size: {preset_choice['size']}px")
    print(f"  - Quality: {preset_choice['quality']}") 
    if preset_choice['crop']:
        print(f"  - Aspect Ratio: {preset_choice['aspect'][0]}:{preset_choice['aspect'][1]}")
        print(f"  - Anchor: {preset_choice['anchor'].replace('-', ' ').title()}")
    else:
        print(f"  - Cropping: Disabled")
    
    confirm = input(f"\n{Fore.CYAN}Use this preset? (y/n) [default y]: ").strip().lower()
    if confirm not in ('', 'y'):
        preset_choice = None  # Fall back to custom

if not preset_choice:
    # === Custom Settings (Original Logic) ===
    format_options = {
        "1": "WEBP",
        "2": "JPEG", 
        "3": "PNG",
        "4": "TIFF",
        "5": "BMP",
        "6": "ICO",
        "7": "PDF",
        "8": "AVIF"  # Added AVIF for modern web
    }
    
    # Step 1: Export format
    while True:
        print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
        print_current_selections()
        print(Fore.CYAN + "🔧 Choose export format")
        print("  1: WEBP (recommended for web)")
        print("  2: JPEG (universal compatibility)")
        print("  3: PNG (lossless)")
        print("  4: TIFF")
        print("  5: BMP")
        print("  6: ICO")
        print("  7: PDF")
        print("  8: AVIF (next-gen web format)")
        prompt = "Enter choice (1-8) [default 1]:"
        print("\n" + "\n".join(textwrap.wrap(prompt, width=60)))
        format_choice = input("> ").strip().lower()
        if format_choice == 'q':
            sys.exit()
        if format_choice == 'l':
            open_file_cross_platform(tmp_log_path)
            continue
        if format_choice in format_options or format_choice == '':
            output_format = format_options.get(format_choice, "WEBP").upper()
            break
        print(f"{Fore.RED}Invalid input. Please enter 1–8, Enter, 'q', or 'l'.")
    
    # Step 2: Size with web dev suggestions
    while True:
        print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
        print_current_selections(output_format)
        print(Fore.CYAN + "🔢 Enter size for shortest side")
        print(f"{Fore.YELLOW}💡 Web Dev Suggestions:")
        print("   • 300px - Thumbnails")
        print("   • 480px - Mobile")
        print("   • 800px - Blog/content")
        print("   • 1200px - Hero images")
        prompt = "Enter size in pixels [default 800]:"
        print("\n" + "\n".join(textwrap.wrap(prompt, width=60)))
        size_input = input("> ").strip().lower()
        if size_input == 'q': sys.exit()
        if size_input == 'l':
            open_file_cross_platform(tmp_log_path)
            continue
        if size_input == '':
            size = 800  # Better default for web
            break
        try:
            size = int(size_input)
            if size > 0: break
        except ValueError: pass
        print(f"{Fore.RED}Invalid input. Enter a positive integer.")
    
    # Step 3: Quality with web optimization tips
    while True:
        print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
        print_current_selections(output_format, size)
        print(Fore.CYAN + "🎚️ Enter export quality")
        print(f"{Fore.YELLOW}💡 Web Optimization Tips:")
        print("   • 80-85: High compression, good for web")
        print("   • 90-95: Balanced quality/size")
        print("   • 95-100: Maximum quality")
        prompt = "Enter quality (50 to 100) [default 85]:"
        print("\n" + "\n".join(textwrap.wrap(prompt, width=60)))
        quality_input = input("> ").strip().lower()
        if quality_input == 'q': sys.exit()
        if quality_input == 'l':
            open_file_cross_platform(tmp_log_path)
            continue
        if quality_input == '':
            quality = 85  # Better default for web
            break
        try:
            quality = int(quality_input)
            if 50 <= quality <= 100: break
        except ValueError: pass
        print(f"{Fore.RED}Invalid input. Enter an integer between 50 and 100.")
    
    # Step 4: Crop with web-focused ratios
    while True:
        print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
        print_current_selections(output_format, size, quality)
        crop_input = input("Do you want to crop to a specific aspect ratio? (y/n): ").strip().lower()
        if crop_input == 'q': sys.exit()
        if crop_input == 'l':
            open_file_cross_platform(tmp_log_path)
            continue
        if crop_input in ('y', 'n', ''):
            crop_to_ratio = (crop_input == 'y')
            break
        print(f"{Fore.RED}Invalid input. Enter 'y', 'n', Enter, 'q', or 'l'.")
    
    if crop_to_ratio:
        while True:
            print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
            print_current_selections(output_format, size, quality)
            print(Fore.CYAN + "📐 Choose aspect ratio")
            print("  1: 1:1 (Square - Social, thumbnails)")
            print("  2: 16:9 (Widescreen - Hero banners)")
            print("  3: 4:3 (Standard - Blog images)")
            print("  4: 3:2 (Photography)")
            print("  5: 4:5 (Portrait - E-commerce)")
            print("  6: 21:9 (Ultra-wide banners)")
            print("  7: 2:1 (Facebook cover)")
            print("  8: 9:16 (Vertical - Stories)")
            ratio_choice = input("Enter choice (1-8) [default 1]: ").strip().lower()
            if ratio_choice == 'q': sys.exit()
            if ratio_choice == 'l':
                open_file_cross_platform(tmp_log_path)
                continue
            ratio_map = {
                "1": (1, 1), "2": (16, 9), "3": (4, 3), "4": (3, 2),
                "5": (4, 5), "6": (21, 9), "7": (2, 1), "8": (9, 16)
            }
            aspect_ratio = ratio_map.get(ratio_choice, (1, 1))
            break
        
        # Anchor selection
        crop_anchor_map = {
            "1": "top-left", "2": "top-center", "3": "top-right",
            "4": "middle-left", "5": "center", "6": "middle-right", 
            "7": "bottom-left", "8": "bottom-center", "9": "bottom-right"
        }
        
        while True:
            print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
            print_current_selections(output_format, size, quality, aspect_ratio)
            print(Fore.CYAN + "🎯 Choose crop anchor point")
            for key, label in crop_anchor_map.items():
                print(f"  {key}: {label.replace('-', ' ').title()}")
            crop_anchor_choice = input("Enter choice (1-9) [default 5]: ").strip().lower()
            if crop_anchor_choice == 'q': sys.exit()
            if crop_anchor_choice == 'l':
                open_file_cross_platform(tmp_log_path)
                continue
            crop_anchor = crop_anchor_map.get(crop_anchor_choice, "center")
            break
    else:
        aspect_ratio = None
        crop_anchor = None
    
    # Package custom settings
    preset_choice = {
        "name": "Custom",
        "format": output_format,
        "size": size,
        "quality": quality,
        "crop": crop_to_ratio,
        "aspect": aspect_ratio,
        "anchor": crop_anchor
    }

# === Multiple Size Generation Option ===
multi_size = False
size_variants = []

print(f"\n{Fore.CYAN}🔄 Multiple Size Generation")
multi_input = input("Generate multiple sizes for responsive web? (y/n) [default n]: ").strip().lower()
if multi_input == 'y':
    multi_size = True
    print(f"{Fore.CYAN}📱 Common responsive sizes:")
    print("  Small: 480px (mobile)")
    print("  Medium: 800px (tablet)")  
    print("  Large: 1200px (desktop)")
    
    size_variants = [
        {"name": "small", "size": 480},
        {"name": "medium", "size": 800}, 
        {"name": "large", "size": 1200}
    ]

# === Final Confirmation ===
print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
if multi_size:
    print_current_selections(preset_choice['format'], "Multiple", preset_choice['quality'], 
                            preset_choice['aspect'] if preset_choice['crop'] else None,
                            preset_choice['anchor'] if preset_choice['crop'] else None, 
                            preset_choice['name'])
else:
    print_current_selections(preset_choice['format'], preset_choice['size'], preset_choice['quality'],
                            preset_choice['aspect'] if preset_choice['crop'] else None,
                            preset_choice['anchor'] if preset_choice['crop'] else None,
                            preset_choice['name'])

print(Fore.CYAN + "✅ Confirm settings")
print(f"\n{Fore.YELLOW}You selected:")
print(f"- Preset: {preset_choice['name']}")
print(f"- Format: {preset_choice['format']}")
if multi_size:
    print(f"- Sizes: {', '.join([f'{v['size']}px ({v['name']})' for v in size_variants])}")
else:
    print(f"- Size: {preset_choice['size']}px")
print(f"- Quality: {preset_choice['quality']}")
if preset_choice['crop']:
    print(f"- Cropping: {preset_choice['aspect'][0]}:{preset_choice['aspect'][1]} ({preset_choice['anchor']})")

confirm = input(f"\n{Fore.CYAN}Proceed? (y/n) [default y]: ").strip().lower()
if confirm not in ('', 'y'):
    sys.exit()

# === Processing Setup ===
timestamp = datetime.now().strftime("%d%m%y_%H%M%S")
existing_runs = [d for d in os.listdir(base_output_folder) if d.startswith("run")]
run_count = len(existing_runs) + 1

if multi_size:
    output_folder = os.path.join(base_output_folder, f"run{run_count}_responsive_{timestamp}")
else:
    output_folder = os.path.join(base_output_folder, f"run{run_count}_{preset_choice['name'].lower().replace(' ', '_')}_{timestamp}")
os.makedirs(output_folder)

# Create subfolders for multi-size
if multi_size:
    for variant in size_variants:
        os.makedirs(os.path.join(output_folder, variant['name']), exist_ok=True)

# === Helper Functions (same as before) ===
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

# === Processing Loop ===
start_time = time.time()
total = len(image_files)
count_cropped = 0
count_upscaled = 0
log_lines = []
total_output_size = 0

log_lines.append(f"Processed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log_lines.append("")
log_lines.append("=== Settings ===")
log_lines.append(f"Preset: {preset_choice['name']}")
log_lines.append(f"Format: {preset_choice['format']}")
if multi_size:
    log_lines.append(f"Sizes: {', '.join([f'{v['size']}px ({v['name']})' for v in size_variants])}")
else:
    log_lines.append(f"Size: {preset_choice['size']}px")
log_lines.append(f"Quality: {preset_choice['quality']}")
if preset_choice['crop']:
    log_lines.append(f"Aspect Ratio: {preset_choice['aspect'][0]}:{preset_choice['aspect'][1]}")
log_lines.append("")

def print_progress_bar(current, total, filename, start_time):
    """Print a nice progress bar with ETA"""
    percent = (current / total) * 100
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    # Calculate ETA
    elapsed = time.time() - start_time
    if current > 0:
        eta = (elapsed / current) * (total - current)
        eta_str = f"ETA: {int(eta//60)}:{int(eta%60):02d}"
    else:
        eta_str = "ETA: --:--"
    
    # Truncate filename if too long
    display_name = filename[:25] + "..." if len(filename) > 28 else filename
    
    print(f"\r{Fore.CYAN}[{bar}] {percent:5.1f}% ({current}/{total}) {eta_str} | {display_name}", end="", flush=True)

for i, filename in enumerate(image_files, 1):
    print_progress_bar(i, total, filename, start_time)
    
    img_path = os.path.join(input_folder, filename)
    
    # Handle CR3 files
    if filename.lower().endswith(".cr3"):
        if not HAS_EXIFTOOL:
            print(f"{Fore.RED}⚠️ CR3 file detected but exiftool not available: {filename}. Skipping.")
            continue
        print(f"{Fore.MAGENTA}🔄 Extracting JPEG preview from CR3...")
        converted_path, orientation_value = convert_cr3_to_jpeg(img_path, input_folder)
        if not converted_path:
            print(f"{Fore.RED}⚠️ Failed to extract CR3 preview: {filename}. Skipping.")
            continue
        img_path = converted_path
    else:
        orientation_value = None
    
    try:
        with Image.open(img_path) as img:
            # Apply orientation
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
            
            original_size = img.size
            
            # Process for multiple sizes or single size
            sizes_to_process = size_variants if multi_size else [{"name": "", "size": preset_choice['size']}]
            
            for size_variant in sizes_to_process:
                current_size = size_variant['size']
                variant_name = size_variant['name']
                
                # Resize logic
                width, height = img.size
                short_edge = min(width, height)
                
                if short_edge <= current_size:
                    new_img = img
                else:
                    if width < height:
                        new_width = current_size
                        new_height = int((current_size / width) * height)
                    else:
                        new_height = current_size
                        new_width = int((current_size / height) * width)
                    new_img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Apply cropping if needed
                if preset_choice['crop']:
                    new_img = crop_to_ratio_with_anchor(new_img, preset_choice['aspect'], preset_choice['anchor'])
                    count_cropped += 1
                
                # Generate web-friendly filename
                web_filename = generate_web_friendly_filename(filename, {
                    'format': preset_choice['format'],
                    'size': current_size,
                    'crop': preset_choice['crop']
                }, timestamp)
                
                # Determine output path
                if multi_size:
                    output_path = os.path.join(output_folder, variant_name, web_filename)
                else:
                    output_path = os.path.join(output_folder, web_filename)
                
                # Save settings
                save_kwargs = {"quality": preset_choice['quality']}
                if preset_choice['format'] == "WEBP":
                    save_kwargs["lossless"] = has_alpha
                    save_kwargs["method"] = 6  # Better compression
                elif preset_choice['format'] == "AVIF":
                    save_kwargs["quality"] = preset_choice['quality']
                
                if preset_choice['format'] in ["JPEG", "PDF", "AVIF"]:
                    new_img = new_img.convert("RGB")
                
                try:
                    new_img.save(output_path, format=preset_choice['format'], **save_kwargs)
                    file_size_kb = get_file_size_kb(output_path)
                    total_output_size += file_size_kb
                    
                    if multi_size:
                        print(f"  📱 {variant_name}: {new_img.size[0]}x{new_img.size[1]} ({file_size_kb} KB)")
                    else:
                        print(f"  ✅ Saved: {new_img.size[0]}x{new_img.size[1]} ({file_size_kb} KB)")
                    
                except Exception as e:
                    print(f"{Fore.RED}❌ Failed to save: {e}")
                    continue
            
            # Log entry per original image
            log_lines.append(f"Image: {filename}")
            log_lines.append(f"  Original: {original_size[0]}x{original_size[1]}")
            if multi_size:
                for variant in sizes_to_process:
                    log_lines.append(f"  {variant['name'].title()}: {variant['size']}px")
            else:
                log_lines.append(f"  Output: {new_img.size[0]}x{new_img.size[1]}")
            log_lines.append("")
                
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to process {filename}: {e}")
        continue

# === Final Summary ===
compression_ratio = ((total_input_size * 1024) / total_output_size) if total_output_size > 0 else 0
processing_time = round(time.time() - start_time, 2)

log_lines.append("=== Summary ===")
log_lines.append(f"Images processed: {total}")
log_lines.append(f"Total input size: {total_input_size} MB")
log_lines.append(f"Total output size: {round(total_output_size / 1024, 2)} MB")
log_lines.append(f"Compression ratio: {compression_ratio:.1f}:1")
log_lines.append(f"Processing time: {processing_time}s")
log_lines.append(f"Output folder: {output_folder}")

# Save log
log_path = os.path.join(output_folder, "processing_log.txt")
with open(log_path, "w") as log_file:
    log_file.write("\n".join(log_lines))

# Save settings as JSON for reuse
settings_path = os.path.join(output_folder, "settings.json")
with open(settings_path, "w") as settings_file:
    json.dump({
        "preset": preset_choice['name'],
        "format": preset_choice['format'],
        "size": preset_choice['size'] if not multi_size else "responsive",
        "quality": preset_choice['quality'],
        "crop": preset_choice['crop'],
        "aspect_ratio": preset_choice['aspect'],
        "multi_size": multi_size,
        "timestamp": timestamp
    }, settings_file, indent=2)

# Clean up CR3 temp files
temp_cr3_folder = os.path.join(input_folder, "temp_cr3")
if os.path.exists(temp_cr3_folder):
    shutil.rmtree(temp_cr3_folder)

# === Success Message ===
print(f"""
{Fore.GREEN}{Style.BRIGHT}🎉 Processing Complete!{Style.RESET_ALL}
{Fore.CYAN}📊 Results:
  • Images processed: {total}
  • Input size: {total_input_size} MB
  • Output size: {round(total_output_size / 1024, 2)} MB  
  • Compression: {compression_ratio:.1f}:1 ratio
  • Time: {processing_time}s
  • Location: {output_folder}
""")

# === Next Actions ===
print(f"{Fore.CYAN}What would you like to do next?")
print("  [r] Run another batch")
print("  [o] Open output folder")
print("  [v] View processing log")  
print("  [s] View settings JSON")
print("  [q] Quit")

while True:
    next_action = input("> ").strip().lower()
    if next_action == 'o':
        open_file_cross_platform(output_folder)
        continue
    elif next_action == 'v':
        open_file_cross_platform(log_path)
        continue
    elif next_action == 's':
        open_file_cross_platform(settings_path)
        continue
    elif next_action == 'r':
        os.execv(sys.executable, [sys.executable] + sys.argv)
    elif next_action == 'q' or next_action == '':
        print(f"{Fore.YELLOW}Happy coding! 💻")
        sys.exit()
    else:
        print(f"{Fore.RED}Invalid input. Enter 'r', 'o', 'v', 's', or 'q'.")
