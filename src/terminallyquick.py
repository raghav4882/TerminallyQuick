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

term_width = shutil.get_terminal_size().columns

# === Step Header and State Print Functions ===
def print_step_header(_, title):
    print(Fore.CYAN + f"🔧 {title}")

def print_current_selections(format=None, size=None, quality=None, aspect=None, anchor=None):
    parts = []
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
print(Fore.CYAN + Style.BRIGHT + f"Terminally Quick {__version__} — by {__author__}")
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
    '.ppm', '.pgm', '.pbm', '.tga'
)
if not os.path.isdir(input_folder):
    print(f"{Fore.RED}❌ Input folder '{input_folder}' not found. Please create it and add images.")
    sys.exit()
all_files = os.listdir(input_folder)
image_files = [f for f in all_files if f.lower().endswith(supported_exts)]
irrelevant_files = [f for f in all_files if not f.lower().endswith(supported_exts)]

print(f"{Fore.GREEN}✅ Images found: {len(image_files)}")
print(f"{Fore.YELLOW}❌ Irrelevant files: {len(irrelevant_files)}")

tmp_log_path = os.path.join(base_output_folder, f"session_file_log_{datetime.now().strftime('%H%M%S')}.txt")
with open(tmp_log_path, "w") as f:
    f.write("=== Files Scanned ===\n")
    f.write("\nFound Images:\n")
    for img in image_files:
        f.write(f"✔️ {img}\n")
    f.write("\nSkipped Files:\n")
    for irr in irrelevant_files:
        f.write(f"❌ {irr}\n")
print(f"{Fore.MAGENTA}ℹ️  File list saved for this scan: {tmp_log_path}")

if len(image_files) == 0:
    print(f"\n{Fore.RED}🚫 No supported images found. Please add PNG, JPG, JPEG, WEBP, or CR3 files to '{input_folder}' and try again.")
    sys.exit()

# === Ask user for export settings (with step headers and state) ===

step_num = 1
format_options = {
    "1": "WEBP",
    "2": "JPEG",
    "3": "PNG",
    "4": "TIFF",
    "5": "BMP",
    "6": "ICO",
    "7": "PDF"
}
output_format = None
size = None
quality = None
aspect_ratio = None
crop_anchor = None
crop_to_ratio = False

# Step 1: Export format
while True:
    print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
    print_current_selections()
    print(Fore.CYAN + "🔧 Choose export format")
    print("  1: WEBP (default)")
    print("  2: JPEG")
    print("  3: PNG")
    print("  4: TIFF")
    print("  5: BMP")
    print("  6: ICO")
    print("  7: PDF")
    prompt = "Enter choice (1-8) [default 1]:"
    print("\n" + "\n".join(textwrap.wrap(prompt, width=60)))
    format_choice = input("> ").strip().lower()
    if format_choice == 'q':
        print(Fore.RED + "Aborted.")
        sys.exit()
    if format_choice == 'l':
        print(Fore.MAGENTA + "Opening scan log file...\n")
        open_file_cross_platform(tmp_log_path)
        continue
    if format_choice in format_options or format_choice == '':
        output_format = format_options.get(format_choice, "WEBP").upper()
        break
    print(f"{Fore.RED}Invalid input. Please enter 1–8, Enter, 'q', or 'l'.")

# Step 2: Shortest side size
step_num += 1
while True:
    print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
    print_current_selections(output_format)
    print(Fore.CYAN + "🔢 Enter minimum size for shortest side")
    prompt = "Enter minimum size for shortest side in pixels (e.g. 550) [default 550]:"
    print("\n" + "\n".join(textwrap.wrap(prompt, width=60)))
    size_input = input("> ").strip().lower()
    if size_input == 'q':
        print(Fore.RED + "Aborted.")
        sys.exit()
    if size_input == 'l':
        print(Fore.MAGENTA + "Opening scan log file...\n")
        open_file_cross_platform(tmp_log_path)
        continue
    if size_input == '':
        size = 550
        break
    try:
        size = int(size_input)
        if size > 0:
            break
    except ValueError:
        pass
    print(f"{Fore.RED}Invalid input. Enter a positive integer.")

# Step 3: Export quality
step_num += 1
while True:
    print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
    print_current_selections(output_format, size)
    print(Fore.CYAN + "🎚️ Enter export quality")
    prompt = "Enter quality (50 to 100) [default 95]:"
    print("\n" + "\n".join(textwrap.wrap(prompt, width=60)))
    quality_input = input("> ").strip().lower()
    if quality_input == 'q':
        print(Fore.RED + "Aborted.")
        sys.exit()
    if quality_input == 'l':
        print(Fore.MAGENTA + "Opening scan log file...\n")
        open_file_cross_platform(tmp_log_path)
        continue
    if quality_input == '':
        quality = 95
        break
    try:
        quality = int(quality_input)
        if 50 <= quality <= 100:
            break
    except ValueError:
        pass
    print(f"{Fore.RED}Invalid input. Enter an integer between 50 and 100.")

# Step 4: Crop to aspect ratio
step_num += 1
while True:
    print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
    print_current_selections(output_format, size, quality)
    crop_input = input("Do you want to crop all images to the same aspect ratio? (y/n): ").strip().lower()
    if crop_input == 'q':
        print(Fore.RED + "Aborted.")
        sys.exit()
    if crop_input == 'l':
        print(Fore.MAGENTA + "Opening scan log file...\n")
        open_file_cross_platform(tmp_log_path)
        continue
    if crop_input in ('y', 'n', ''):
        crop_to_ratio = (crop_input == 'y')
        break
    print(f"{Fore.RED}Invalid input. Enter 'y', 'n', Enter, 'q', or 'l'.")

if crop_to_ratio:
    # Step 5: Choose aspect ratio
    step_num += 1
    while True:
        print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
        print_current_selections(output_format, size, quality)
        print(Fore.CYAN + "📐 Choose crop aspect ratio")
        print("  1: 4:3 (Standard landscape)")
        print("  2: 1:1 (Square)")
        print("  3: 4:5 (Portrait)")
        print("  4: 3:2 (DSLR landscape)")
        print("  5: 16:9 (Widescreen)")
        print("  6: 2:3 (Classic portrait)")
        print("  7: 5:4 (Large format)")
        print("  8: 7:5 (Mild wide)")
        prompt = "Enter choice (1-8) [default 1]:"
        print("\n" + "\n".join(textwrap.wrap(prompt, width=60)))
        ratio_choice = input("> ").strip().lower()
        if ratio_choice == 'q':
            print(Fore.RED + "Aborted.")
            sys.exit()
        if ratio_choice == 'l':
            print(Fore.MAGENTA + "Opening scan log file...\n")
            open_file_cross_platform(tmp_log_path)
            continue
        ratio_map = {
            "1": (4, 3),
            "2": (1, 1),
            "3": (4, 5),
            "4": (3, 2),
            "5": (16, 9),
            "6": (2, 3),
            "7": (5, 4),
            "8": (7, 5),
        }
        aspect_ratio = ratio_map.get(ratio_choice, (4, 3))
        break
    # Step 5b: Choose anchor point
    step_num += 1
    while True:
        print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
        print_current_selections(output_format, size, quality, aspect_ratio)
        crop_anchor_map = {
            "1": "top-left",
            "2": "top-center",
            "3": "top-right",
            "4": "middle-left",
            "5": "center",
            "6": "middle-right",
            "7": "bottom-left",
            "8": "bottom-center",
            "9": "bottom-right"
        }
        print(Fore.CYAN + "🎯 Choose crop anchor point")
        for key, label in crop_anchor_map.items():
            print(f"  {key}: {label.replace('-', ' ').title()}")
        prompt = "Enter choice (1-9) [default 5]:"
        print("\n" + "\n".join(textwrap.wrap(prompt, width=60)))
        crop_anchor_choice = input("> ").strip().lower()
        if crop_anchor_choice == 'q':
            print(Fore.RED + "Aborted.")
            sys.exit()
        if crop_anchor_choice == 'l':
            print(Fore.MAGENTA + "Opening scan log file...\n")
            open_file_cross_platform(tmp_log_path)
            continue
        crop_anchor = crop_anchor_map.get(crop_anchor_choice, "center")
        break
else:
    aspect_ratio = None
    crop_anchor = None

# Step 6: Confirm settings
step_num += 1
print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
print_current_selections(output_format, size, quality, aspect_ratio if crop_to_ratio else None, crop_anchor if crop_to_ratio else None)
print(Fore.CYAN + "✅ Confirm settings")
print(f"\n{Fore.YELLOW}You selected:")
print(f"- Format: {output_format}")
print(f"- Shortest side: {size}px")
print(f"- Quality: {quality}")
if crop_to_ratio:
    print(f"- Cropping to ratio: {aspect_ratio[0]}:{aspect_ratio[1]}")
    print(f"- Anchor point: {crop_anchor.replace('-', ' ').title()}")
prompt = "Proceed? (y/n) [default y]:"
print("\n" + "\n".join(textwrap.wrap(prompt, width=60)))
while True:
    confirm = input("> ").strip().lower()
    if confirm == 'q':
        print(Fore.RED + "Aborted.")
        sys.exit()
    if confirm == 'l':
        print(Fore.MAGENTA + "Opening scan log file...\n")
        open_file_cross_platform(tmp_log_path)
        continue
    if confirm in ('', 'y', 'n'):
        break
    print(f"{Fore.RED}Invalid input. Enter 'y', 'n', Enter, 'q', or 'l'.")
if confirm not in ('', 'y'):
    print(f"{Fore.RED}Aborted.")
    sys.exit()

# === Create unique export subfolder ===

timestamp = datetime.now().strftime("%d%m%y_%H%M%S")
existing_runs = [d for d in os.listdir(base_output_folder) if d.startswith("run")]
run_count = len(existing_runs) + 1
output_folder = os.path.join(base_output_folder, f"run{run_count} - {timestamp}")
os.makedirs(output_folder)

log_lines = []

# Insert timestamp at the top of log_lines
log_lines.append(f"Processed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log_lines.append("")

# === Export Settings ===
log_lines.append("=== Export Settings ===")
log_lines.append(f"Format: {output_format}")
log_lines.append(f"Shortest Side: {size}px")
log_lines.append(f"Quality: {quality}")
if crop_to_ratio:
    log_lines.append(f"Cropping Enabled: Yes")
    log_lines.append(f"  - Aspect Ratio: {aspect_ratio[0]}:{aspect_ratio[1]}")
    log_lines.append(f"  - Anchor Point: {crop_anchor.replace('-', ' ').title()}")
else:
    log_lines.append("Cropping Enabled: No")
log_lines.append("")  # Blank line after settings

# === Irrelevant Files Skipped ===
log_lines.append("=== Irrelevant Files Skipped ===")
if irrelevant_files:
    for f in irrelevant_files:
        log_lines.append(f"• {f}")
else:
    log_lines.append("None")
log_lines.append("")

# === Convert CR3 to JPEG preview using ExifTool ===

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

# === Helpers ===

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

import time
start_time = time.time()

# === Image processing ===
total = len(image_files)
# Track image statistics
count_cropped = 0
count_upscaled = 0

# === Enhanced Progress Tracking ===
def print_progress_bar(current, total, filename, start_time):
    """Simple progress bar for standard version"""
    percent = (current / total) * 100
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    # Calculate ETA
    elapsed = time.time() - start_time
    if current > 0:
        eta = (elapsed / current) * (total - current)
        eta_str = f"ETA: {int(eta//60)}:{int(eta%60):02d}" if eta > 60 else f"ETA: {int(eta)}s"
    else:
        eta_str = "ETA: calculating..."
    
    display_name = filename[:20] + "..." if len(filename) > 23 else filename
    print(f"\r{Fore.GREEN}[{bar}] {percent:5.1f}% ({current}/{total}) {eta_str} | {display_name}", end="", flush=True)

# Add batch warning for large sets
if len(image_files) > 50:
    estimated_time = len(image_files) * 1.5  # Estimate 1.5s per image
    print(f"\n{Fore.YELLOW}⏱️  Large batch detected ({len(image_files)} images)")
    print(f"Estimated processing time: ~{int(estimated_time//60)}min {int(estimated_time%60)}s")
    
    proceed = input(f"{Fore.CYAN}Continue? (y/n) [default y]: ").strip().lower()
    if proceed == 'n':
        print(f"{Fore.RED}Cancelled.")
        sys.exit()

print(f"\n{Fore.GREEN}🚀 Starting processing...\n")

for i, filename in enumerate(image_files, 1):
    print_progress_bar(i, total, filename, start_time)
    
    img_path = os.path.join(input_folder, filename)
    if filename.lower().endswith(".cr3"):
        if not HAS_EXIFTOOL:
            print(f"{Fore.RED}⚠️ CR3 file detected but exiftool not available: {filename}. Skipping.")
            print(f"{Fore.YELLOW}💡 To process CR3 files, install exiftool from: https://exiftool.org/")
            continue
        print(f"{Fore.MAGENTA}🔄 Extracting JPEG preview from CR3...")
        converted_path, orientation_value = convert_cr3_to_jpeg(img_path, input_folder)
        if not converted_path:
            print(f"{Fore.RED}⚠️ Failed to extract JPEG preview from CR3: {filename}. Skipping.")
            continue
        img_path = converted_path
    else:
        orientation_value = None
    try:
        with Image.open(img_path) as img:
            if orientation_value is not None:
                if orientation_value == 3:
                    img = img.rotate(180, expand=True)
                elif orientation_value == 6:
                    img = img.rotate(270, expand=True)
                elif orientation_value == 8:
                    img = img.rotate(90, expand=True)
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                img = apply_exif_orientation(img.convert("RGBA"))
                has_alpha = True
            else:
                img = apply_exif_orientation(img.convert("RGB"))
                has_alpha = False
            width, height = img.size
            short_edge = min(width, height)
            if short_edge <= size:
                new_img = img
            else:
                if width < height:
                    new_width = size
                    new_height = int((size / width) * height)
                else:
                    new_height = size
                    new_width = int((size / height) * width)
                new_img = img.resize((new_width, new_height), Image.LANCZOS)
            before_upscale = None
            upscale_w = None
            upscale_h = None
            log_lines.append("--------------------------------------------------")
            log_lines.append(f"Image: {filename}")
            log_lines.append(f"  - Original Size: {width}x{height}")
            log_lines.append(f"  - Resized To: {new_img.size[0]}x{new_img.size[1]}")
            if crop_to_ratio:
                new_img = crop_to_ratio_with_anchor(new_img, aspect_ratio, crop_anchor)
                log_lines.append(f"  - Cropped To: {new_img.size[0]}x{new_img.size[1]}")
                count_cropped += 1
                # Upscale if either dimension is smaller than the requested size
                final_w, final_h = new_img.size
                if min(final_w, final_h) < size:
                    before_upscale = (final_w, final_h)
                    if final_w < final_h:
                        upscale_w = size
                        upscale_h = int((size / final_w) * final_h)
                    else:
                        upscale_h = size
                        upscale_w = int((size / final_h) * final_w)
                    new_img = new_img.resize((upscale_w, upscale_h), Image.LANCZOS)
                    log_lines.append(f"  - Upscaled From: {before_upscale[0]}x{before_upscale[1]} To: {upscale_w}x{upscale_h}")
                    count_upscaled += 1
            base_name = os.path.splitext(filename)[0]
            extension = output_format.lower()
            output_path = os.path.join(output_folder, f"{base_name}_{timestamp}.{extension}")
            save_kwargs = {"quality": quality}
            if output_format == "WEBP":
                save_kwargs["lossless"] = has_alpha
            if output_format in ["JPEG", "PDF"]:
                new_img = new_img.convert("RGB")
            try:
                new_img.save(output_path, format=output_format, **save_kwargs)
            except Exception as e:
                print(f"{Fore.RED}❌ Failed to save image: {filename}. Error: {e}")
                continue
            file_size_kb = os.path.getsize(output_path) // 1024
            log_lines.append(f"  - Final File Size: {file_size_kb} KB")
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to open image: {filename}. Error: {e}")
        continue

log_lines.append("")
log_lines.append("████████████████████ Summary ████████████████████")
log_lines.append(f"Total images processed: {total}")
log_lines.append(f"Images cropped: {count_cropped}")
log_lines.append(f"Images upscaled: {count_upscaled}")
log_lines.append(f"Output folder: {output_folder}")
log_lines.append("█████████████████████████████████████████████████")
log_lines.append(f"Total processing time: {round(time.time() - start_time, 2)} seconds")

log_path = os.path.join(output_folder, "log.txt")
with open(log_path, "w") as log_file:
    log_file.write("\n".join(log_lines))

 # Optionally clean up CR3 preview JPEGs after use
temp_cr3_folder = os.path.join(input_folder, "temp_cr3")
if os.path.exists(temp_cr3_folder):
    for file in os.listdir(temp_cr3_folder):
        os.remove(os.path.join(temp_cr3_folder, file))
    os.rmdir(temp_cr3_folder)
    print(Fore.GREEN + "🧹 Cleaned up temporary CR3 previews.")

# Clear progress bar
print("\n" + " " * 80 + "\r", end="")

# === Enhanced final message ===
processing_time = round(time.time() - start_time, 2)
print(f"""\n{Fore.GREEN}{Style.BRIGHT}🎉 Processing Complete!{Style.RESET_ALL}

{Fore.CYAN}📊 Results Summary:
  ✅ Images processed: {total - count_cropped + count_cropped} 
  🖼️  Images cropped: {count_cropped}
  📈 Images upscaled: {count_upscaled}
  ⏱️  Processing time: {processing_time}s
  📁 Output folder: {os.path.basename(output_folder)}
""")

# Auto-open results folder
auto_open = input(f"{Fore.CYAN}Open results folder? (y/n) [default y]: ").strip().lower()
if auto_open in ('', 'y'):
    open_file_cross_platform(output_folder)

# === Enhanced next actions ===
print(f"\n{Fore.CYAN}What would you like to do next?")
print("  [r] Run another batch")
print("  [v] View detailed log")
print("  [o] Open output folder again")
print("  [q] Quit")

while True:
    next_action = input("> ").strip().lower()
    if next_action == 'v':
        print(Fore.MAGENTA + "Opening log file...\n")
        open_file_cross_platform(log_path)
        print(f"{Fore.CYAN}\nWhat would you like to do next?")
        print("  [r] Run another batch")
        print("  [q] Quit")
        continue
    elif next_action == 'r':
        os.execv(sys.executable, [sys.executable] + sys.argv)
    elif next_action == 'q' or next_action == '':
        print(f"{Fore.YELLOW}Goodbye!")
        sys.exit()
    else:
        print(f"{Fore.RED}Invalid input. Enter 'r', 'v', or 'q'.")