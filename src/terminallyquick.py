#!/usr/bin/env python3

"""
TerminallyQuick v4.0
Professional Image Optimization Suite
"""

__version__ = "4.0"
__author__ = "TerminallyQuick Team"

import os
from PIL import Image, ExifTags, ImageChops, ImageStat
import math

# Define project directories and config
PROFILES_DIR = 'profiles'
CONFIG_FILE = '.tq_config'
if not os.path.exists(PROFILES_DIR):
    os.makedirs(PROFILES_DIR, exist_ok=True)
from datetime import datetime
import time
from colorama import init, Fore, Style
import shutil, textwrap
import sys
import platform
import json
import concurrent.futures
import threading
import hashlib

# Functionality for Watchdog
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

# functionality for HEIC support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass  # gracefully handle if not installed (though it should be)

# Check for exiftool (required for CR3 support)
HAS_EXIFTOOL = shutil.which("exiftool") is not None

init(autoreset=True)

# === Helper Functions ===
def open_file_cross_platform(path):
    if platform.system() == "Darwin":
        os.system(f'open "{path}"')
    elif platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Linux":
        os.system(f'xdg-open "{path}"')
    else:
        print(f"{Fore.RED}[!] Unsupported OS. Please open the file manually: {path}")

def load_app_config():
    """Load persistent application settings"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_app_config(config):
    """Save persistent application settings"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        pass

def view_most_recent_log():
    """Find and open the most recent processing log"""
    if not os.path.exists('resized_images'):
        print(f"{Fore.RED}[!] No logs found yet. Process some images first!")
        return

    # Find all run folders
    runs = [d for d in os.listdir('resized_images') if d.startswith("run") and os.path.isdir(os.path.join('resized_images', d))]
    if not runs:
        print(f"{Fore.RED}[!] No processing sessions found.")
        return

    # Sort by modification time to get the latest
    runs.sort(key=lambda x: os.path.getmtime(os.path.join('resized_images', x)), reverse=True)
    latest_run = runs[0]
    
    # Try to find the summary text file first
    run_path = os.path.join('resized_images', latest_run)
    try:
        summary_files = [f for f in os.listdir(run_path) if f.endswith("_summary.txt")]
        
        if summary_files:
            log_path = os.path.join(run_path, summary_files[0])
            print(f"{Fore.GREEN}[INFO] Opening latest log: {log_path}")
            open_file_cross_platform(log_path)
        else:
            # Fallback to json if txt not found
            json_files = [f for f in os.listdir(run_path) if f.endswith(".json")]
            if json_files:
                log_path = os.path.join(run_path, json_files[0])
                print(f"{Fore.GREEN}[INFO] Opening latest log: {log_path}")
                open_file_cross_platform(log_path)
            else:
                print(f"{Fore.RED}[!] No log files found in the latest session folder.")
    except Exception as e:
        print(f"{Fore.RED}[!] Error accessing log files: {str(e)}")

def show_help_screen():
    """Display a comprehensive help screen"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════════════════╗")
    print(f"║                 TerminallyQuick Help                     ║")
    print(f"╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}KEYBOARD SHORTCUTS:{Style.RESET_ALL}")
    print("  [Q] Quit        - Exit the application at any time")
    print("  [L] Logs        - Open the most recent processing report")
    print("  [H] Help        - Show this help screen")
    print("  [B] Back        - Return to the previous menu")
    print("  [C] Change Path - Switch input folder (at start)")
    print("  [T] Test Run    - Process only the first image to check quality")
    print("  [Enter] Default - Use the suggested or default value")
    
    print(f"\n{Fore.CYAN}FOLDER STRUCTURE:{Style.RESET_ALL}")
    print("  • /input_images/   - Place your original files here")
    print("  • /resized_images/ - Your processed images will appear here")
    print("  • /profiles/       - Your custom setting presets")
    
    print(f"\n{Fore.GREEN}MODES:{Style.RESET_ALL}")
    print("  • Manual Config - Full control over every setting")
    print("  • Smart Mode    - Auto-suggestion based on analysis")
    print("  • Fast Track    - Use your saved profiles for one-click processing")
    print("  • Import        - Load settings from a JSON file")
    
    print(f"\n{Fore.MAGENTA}PRO TIPS:{Style.RESET_ALL}")
    print("  • Saved Profiles: Create them via [P] to skip all prompts next time.")
    print("  • Drag & Drop: Drag any folder into the terminal when changing paths.")
    print("  • Test First: Use [T] to verify quality before a 1000+ image batch.")
    print("  • Modern Formats: WEBP and AVIF offer 30-50% smaller files")
    print("  • Quality: 85 is usually the sweet spot for web performance")
    print("  • Upscaling: Keep 'No' to avoid blurry/pixelated images")
    
    input(f"\n{Fore.YELLOW}Press Enter to return...{Style.RESET_ALL}")

def import_settings_from_json():
    """Import settings part from a processing_settings.json file"""
    try:
        from tkinter import Tk
        import tkinter.filedialog as fd
        root = Tk()
        root.withdraw()
        path = fd.askopenfilename(
            title="Select processing_settings.json",
            filetypes=[("JSON files", "*.json")]
        )
        root.destroy()
    except Exception:
        print(f"{Fore.YELLOW}[INFO] GUI picker not available. Manual entry required.")
        path = input(f"{Fore.CYAN}Enter path to JSON file: {Style.RESET_ALL}").strip().strip("'").strip('"')
    
    if not path: return None
    
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        
        # Determine if it's a full log or a profile
        if "settings" in data:
            settings = data["settings"]
            name = data.get("profile_name", settings.get("name", "Imported"))
            print(f"{Fore.GREEN}[OK] Imported settings: {name}")
            return settings
        else:
            print(f"{Fore.RED}[!] Invalid settings format in JSON.")
    except Exception as e:
        print(f"{Fore.RED}[!] Could not import settings: {str(e)}")
        
    return None

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
            "images": {},
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
        for variant, imgs in log_data['processing']['images'].items():
            if variant != "default":
                f.write(f"\nVariant: {variant}\n")
            for img in imgs:
                f.write(f"  {img['file']}:\n")
                f.write(f"    {img['original']} → {img['result']} | {img['action']} | {img['size_kb']} KB\n")

def get_resize_action_and_emoji(original_short_edge, target_size, allow_upscale):
    """Determine what action will be taken and appropriate emoji/description"""
    if original_short_edge > target_size:
        return "downscaled", "(-)", "Downscaled"
    elif original_short_edge < target_size and allow_upscale:
        return "upscaled", "(+)", "Upscaled"
    else:
        return "kept_original", "(=)", "Kept original size"

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

def print_current_selections(format=None, size=None, quality=None, aspect=None, anchor=None, upscale=None, recursive=None, preset=None):
    parts = []
    if preset: parts.append(f"Preset: {preset}")
    if format: parts.append(f"Format: {format}")
    if size: parts.append(f"Size: {size}px")
    if quality: parts.append(f"Quality: {quality}")
    if aspect: 
        if isinstance(aspect, tuple): parts.append(f"Aspect: {aspect[0]}:{aspect[1]}")
        else: parts.append(f"Aspect: {aspect}")
    if anchor: parts.append(f"Anchor: {anchor.replace('-', ' ').title()}")
    if upscale is not None: parts.append(f"Upscale: {'Yes' if upscale else 'No'}")
    if recursive is not None: parts.append(f"Recursive: {'Yes' if recursive else 'No'}")
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
    
    # Securely extract preview using subprocess instead of shell redirection
    try:
        with open(temp_path, "wb") as f:
            subprocess.run(['exiftool', '-b', '-PreviewImage', cr3_path], stdout=f, check=True)
    except Exception as e:
        print(f"{Fore.RED}  [!] Exiftool failed to extract preview: {str(e)}")
        return None, None

    # Securely get orientation
    try:
        orientation_output = subprocess.check_output(
            ['exiftool', '-S', '-Orientation#', cr3_path],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # Orientation format is usually "Orientation: N" or just "N" with -S
        if orientation_output:
            val = orientation_output.split()[-1]
            orientation_value = int(val)
        else:
            orientation_value = None
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

# === Main Menu ===
def save_profile(settings, name):
    """Save settings as a profile JSON file with duplicate handling"""
    os.makedirs(PROFILES_DIR, exist_ok=True)
    
    # Clean name for filename safety
    safe_name = "".join(x for x in name if x.isalnum() or x in (' ', '-', '_')).strip()
    if not safe_name: safe_name = "CustomProfile"
    
    filename = f"{safe_name.replace(' ', '_')}.json"
    file_path = os.path.join(PROFILES_DIR, filename)
    
    if os.path.exists(file_path):
        print(f"\n{Fore.YELLOW}[!] Profile '{safe_name}' already exists.")
        print("  [O] Overwrite existing profile")
        print("  [R] Rename / New name")
        print("  [A] Auto-suffix (add _1, _2...)")
        print("  [C] Cancel saving")
        
        choice = input(Fore.CYAN + "Choice [O/R/A/C]: ").strip().lower()
        if choice == 'c': return False
        if choice == 'r':
            new_name = input(Fore.CYAN + "Enter new profile name: ").strip()
            return save_profile(settings, new_name)
        if choice == 'a':
            counter = 1
            while os.path.exists(file_path):
                filename = f"{safe_name.replace(' ', '_')}_{counter}.json"
                file_path = os.path.join(PROFILES_DIR, filename)
                counter += 1
        elif choice != 'o':
            print(f"{Fore.RED}[!] Invalid choice. Cancelled.")
            return False

    try:
        data = {
            "profile_name": name,
            "created_at": datetime.now().isoformat(),
            "version": __version__,
            "settings": settings
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"{Fore.GREEN}[OK] Profile saved: {name} ({filename})")
        return True
    except Exception as e:
        print(f"{Fore.RED}[!] Could not save profile: {str(e)}")
        return False

def list_profiles():
    """Load and return all valid profiles from the profiles directory"""
    profiles = []
    if not os.path.exists(PROFILES_DIR): return []
    
    for filename in os.listdir(PROFILES_DIR):
        if filename.endswith('.json'):
            path = os.path.join(PROFILES_DIR, filename)
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    # Basic validation
                    if "settings" in data and "profile_name" in data:
                        profiles.append({
                            "name": data["profile_name"],
                            "filename": filename,
                            "settings": data["settings"]
                        })
            except: continue
    return sorted(profiles, key=lambda x: x['name'].lower())

def delete_profile(index):
    """Delete a profile by index from the list"""
    profiles = list_profiles()
    if 0 <= index < len(profiles):
        profile = profiles[index]
        path = os.path.join(PROFILES_DIR, profile['filename'])
        try:
            os.remove(path)
            print(f"{Fore.GREEN}[OK] Deleted profile: {profile['name']}")
            return True
        except Exception as e:
            print(f"{Fore.RED}[!] Error deleting profile: {str(e)}")
    return False

def show_main_menu():
    """Display the main menu and get user selection"""
    while True:
        print("\n" + Fore.CYAN + "═" * 40 + Style.RESET_ALL)
        print(f"{Fore.WHITE}{Style.BRIGHT}MODES:{Style.RESET_ALL}")
        print("  [1] Manual Configuration (Full Control)")
        print("  [2] Smart Mode (Auto-Suggestions)")
        print("  [3] Import from JSON (Load Log/Profile)")
        if HAS_WATCHDOG:
            print("  [W] Watchdog Mode 🐕 (Auto-Process New Files)")
        
        profiles = list_profiles()
        if profiles:
            print(f"\n{Fore.GREEN}{Style.BRIGHT}FAST TRACK (YOUR PROFILES):{Style.RESET_ALL}")
            for i, profile in enumerate(profiles):
                print(f"  [{i+4}] Profile: {profile['name']}")
            
        print(f"\n{Fore.WHITE}{Style.BRIGHT}MANAGEMENT:{Style.RESET_ALL}")
        print("  [P] Create New Profile")
        print("  [D] Delete a Profile")
        print("  [L] View Most Recent Log")
        print("  [H] Help")
        print("  [Q] Quit")
        
        choice = input(f"\n{Fore.YELLOW}Choice (1-3/W/P/... ) [default 1]: {Style.RESET_ALL}").strip().lower()
        
        if choice in ('1', ''): return 'manual'
        if choice == '2': return 'smart'
        if choice == '3': return 'import'
        if choice == 'w' and HAS_WATCHDOG: return 'watchdog'
        if choice == 'p': return 'create_profile'
        if choice == 'l': view_most_recent_log(); continue
        if choice == 'h': show_help_screen(); continue
        if choice == 'q': sys.exit()
        
        if choice == 'd':
            if not profiles:
                print(f"{Fore.RED}[!] No profiles to delete.")
                continue
            idx_input = input(f"{Fore.YELLOW}Enter profile number to delete: {Style.RESET_ALL}").strip()
            try:
                idx = int(idx_input) - 4
                if delete_profile(idx):
                    print(f"{Fore.GREEN}[OK] Profile deleted.")
                else:
                    print(f"{Fore.RED}[!] Invalid profile number.")
            except ValueError:
                print(f"{Fore.RED}[!] Invalid input.")
            continue
            
        # Check if choice is a profile number
        try:
            val = int(choice)
            if 4 <= val < 4 + len(profiles):
                return profiles[val-4]['settings']
        except ValueError:
            pass
            
        print(f"{Fore.RED}[!] Invalid choice. Please enter a valid option.")

# === Main Application Logic ===
def create_profile_flow():
    """Step-by-step profile creation without processing"""
    print(f"\n{Fore.GREEN}{Style.BRIGHT}[NEW] CREATE NEW PROFILE{Style.RESET_ALL}")
    print(Fore.CYAN + "─" * 40)
    
    settings = get_settings()
    if settings == 'back': return
    
    name = input(f"\n{Fore.YELLOW}Enter a name for this profile: {Style.RESET_ALL}").strip()
    if not name: name = "My Profile"
    
    if save_profile(settings, name):
        print(f"\n{Fore.GREEN}Profile '{name}' is now ready to use from the main menu!")
    
    input(f"\n{Fore.YELLOW}Press Enter to return to menu...{Style.RESET_ALL}")

def main():
    # === Common Setup (Persists during session) ===
    config = load_app_config()
    input_folder = config.get('recent_input_folder', 'input_images')
    if not os.path.isdir(input_folder):
         input_folder = 'input_images'
         
    base_output_folder = 'resized_images'
    
    while True:
        
        # Ensure all required folders exist
        os.makedirs(input_folder, exist_ok=True)
        os.makedirs(base_output_folder, exist_ok=True)
        os.makedirs(PROFILES_DIR, exist_ok=True)
        
        # Title banner
        print(Fore.CYAN + Style.BRIGHT + f"Terminally Quick {__version__} — by {__author__}")
        
        box_width = 60
        print(Fore.YELLOW + "[Q] Quit  |  [L] Log  |  [C] Change Path  |  [ENTER] Default\n" + Fore.CYAN + "─" * box_width + Style.RESET_ALL)
        
        # === Custom Path Selection ===
        print(f"Current Input Folder: {Fore.GREEN}{input_folder}{Style.RESET_ALL}")
        choice = input(f"{Fore.CYAN}Press [C] to Change Folder or [Enter] to continue: {Style.RESET_ALL}").strip().lower()
        
        if choice == 'c':
            new_path = input(f"\n{Fore.YELLOW}Enter target folder path (or drag and drop folder here): {Style.RESET_ALL}").strip().strip("'").strip('"')
            if os.path.isdir(new_path):
                input_folder = new_path
                config['recent_input_folder'] = input_folder
                save_app_config(config)
                print(f"{Fore.GREEN}[OK] Input folder set and saved: {input_folder}")
            else:
                print(f"{Fore.RED}[!] Invalid path. Falling back to current: {input_folder}")
        elif choice == 'q':
            sys.exit()

        # Create helpful instructions in default input folder if it's empty and using default
        if input_folder == 'input_images' and not os.listdir(input_folder):
            readme_path = os.path.join(input_folder, 'INSTRUCTIONS.txt')
            with open(readme_path, 'w') as f:
                f.write("Welcome to TerminallyQuick v4.0!\n\n")
                f.write("This is your INPUT folder.\n\n")
                f.write("HOW TO USE:\n")
                f.write("1. Add your images here.\n")
                f.write("2. Run TerminallyQuick.\n\n")
                f.write("SUPPORTED FORMATS:\n")
                f.write("PNG, JPEG, WEBP, BMP, TIFF, ICO, CR3, AVIF, HEIC\n")
        
        # === Main Menu & Mode Selection ===
        mode_or_settings = show_main_menu()
        
        if mode_or_settings == 'create_profile':
            create_profile_flow()
            continue
            
        if mode_or_settings == 'watchdog':
            run_watchdog_mode(input_folder)
            continue
            
        # Determine mode and settings
        if isinstance(mode_or_settings, dict):
            settings = mode_or_settings
            mode = "Fast Track Profile"
        elif mode_or_settings == 'manual':
            settings = get_settings()
            if settings == 'back': continue
            mode = "Manual Configuration"
        elif mode_or_settings == 'smart':
            # File scanning needed for smart mode - Default to recursive for Smart Mode
            image_files = scan_for_images(input_folder, recursive=True)
            if not image_files: continue
            settings = get_smart_settings(image_files)
            if settings == 'back': continue
            mode = "Smart Mode"
        elif mode_or_settings == 'import':
            settings = import_settings_from_json()
            if not settings: continue
            mode = "JSON Import"
        else:
            continue
            
        # === File scanning logic ===
        # If recursion is requested, we MUST scan (or re-scan) recursively.
        # Otherwise, scan if we haven't yet.
        recursive_requested = settings.get('recursive', False)
        
        # If recursive active, force a new scan. If not recursive, only scan if missing.
        if recursive_requested:
             image_files = scan_for_images(input_folder, recursive=True)
             if not image_files: continue
        elif 'image_files' not in locals():
            image_files = scan_for_images(input_folder, recursive=False)
            if not image_files: continue
            
        # === One-Image Test Option ===
        print(f"\n{Fore.CYAN}Options before processing:")
        print("  [Enter] Process all images")
        print("  [T] Test Run (Process 1 image & open it)")
        print("  [B] Back to Menu")
        
        batch_choice = input(f"\n{Fore.YELLOW}Choice: {Style.RESET_ALL}").strip().lower()
        if batch_choice == 'b': continue
        if batch_choice == 't':
            process_images(input_folder, image_files[:1], settings, mode, is_test=True)
            
            # Post-test prompt
            remaining = len(image_files) - 1
            if remaining > 0:
                print(f"\n{Fore.GREEN}[TEST COMPLETE] Verification image saved.")
                proceed = input(f"{Fore.CYAN}Proceed with the remaining {remaining} images? (y/n) [default y]: {Style.RESET_ALL}").strip().lower()
                if proceed not in ('n', 'no'):
                    process_images(input_folder, image_files[1:], settings, mode)
            continue
            
        # Start full process
        process_images(input_folder, image_files, settings, mode)
        
        # Post-process: Offer to save settings as profile if it was manual
        if mode == "Manual Configuration":
            save_choice = input(f"\n{Fore.MAGENTA}Save these manual settings as a profile for future use? (y/n) [default n]: {Style.RESET_ALL}").strip().lower()
            if save_choice == 'y':
                prof_name = input(f"{Fore.YELLOW}Enter profile name: {Style.RESET_ALL}").strip()
                if prof_name: save_profile(settings, prof_name)

        # Final loop decision
        restart = input(f"\n{Fore.CYAN}Process another batch? (y/n) [default y]: {Style.RESET_ALL}").strip().lower()
        if restart == 'n':
            print(f"{Fore.YELLOW}Thanks for using TerminallyQuick!")
            break
            
        # Reset image_files for next iteration to ensure fresh state
        if 'image_files' in locals():
             del image_files

def scan_for_images(input_folder, recursive=False):
    """Helper to scan for images and handle empty results. Returns relative paths."""
    search_type = "Recursive" if recursive else "Standard"
    print(f"\n{Fore.CYAN}[INFO] {search_type} scan in '{input_folder}'...")
    
    supported_exts = (
        '.png', '.jpg', '.jpeg', '.webp', '.cr3',
        '.bmp', '.tif', '.tiff', '.ico',
        '.ppm', '.pgm', '.pbm', '.tga', '.avif', '.heic'
    )
    
    if not os.path.isdir(input_folder):
        print(f"{Fore.RED}[!] Input folder '{input_folder}' not found.")
        return None
    
    image_files = []
    irrelevant_count = 0
    
    if recursive:
        for root, dirs, files in os.walk(input_folder):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), input_folder)
                if f.lower().endswith(supported_exts):
                    image_files.append(rel_path)
                else:
                    if f != '.DS_Store': irrelevant_count += 1
    else:
        all_files = os.listdir(input_folder)
        for f in all_files:
            if f.lower().endswith(supported_exts):
                image_files.append(f)
            else:
                if f != '.DS_Store' and not os.path.isdir(os.path.join(input_folder, f)):
                    irrelevant_count += 1
    
    print(f"{Fore.GREEN}[OK] Images found: {len(image_files)}")
    if irrelevant_count > 0:
        print(f"{Fore.YELLOW}[!] Non-image files: {irrelevant_count}")
    
    if not image_files:
        print(f"{Fore.RED}[!] No supported images found in '{input_folder}'.")
        print(f"{Fore.YELLOW}[TIP] Supported formats: {', '.join(supported_exts).upper()}")
        input(f"\n{Fore.YELLOW}Press Enter to return to menu...{Style.RESET_ALL}")
        return None
        
    # Sort for consistency
    image_files.sort()
    return image_files

def get_settings():
    """Manual settings configuration"""
    format_options = {
        "1": "WEBP", "2": "JPEG", "3": "PNG", "4": "TIFF",
        "5": "BMP", "6": "ICO", "7": "PDF", "8": "AVIF"
    }
    default_format = "WEBP"
    default_size = 800
    default_quality = 85
    
    # Format selection
    while True:
        print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
        print_current_selections()
        print(Fore.CYAN + "[FORMAT] Choose export format")
        print(f"{Fore.YELLOW}[TIP] Suggestions:")
        for key, fmt in format_options.items():
            suffix = " (recommended for web)" if fmt == "WEBP" else ""
            suffix = " (next-gen web format)" if fmt == "AVIF" else suffix
            print(f"  {key}: {fmt}{suffix}")
        
        format_choice = input("Enter choice (1-8/L/H/B/Q) [default 1]: ").strip().lower()
        if format_choice == 'q': sys.exit()
        if format_choice == 'b': return 'back'
        if format_choice == 'h':
            show_help_screen()
            continue
        if format_choice == 'l':
            view_most_recent_log()
            continue
        if format_choice in format_options or format_choice == '':
            output_format = format_options.get(format_choice, default_format).upper()
            break
        print(f"{Fore.RED}Invalid input.")
    
    # Size selection
    while True:
        print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
        print_current_selections(output_format)
        print(Fore.CYAN + "[SIZE] Enter size for shortest side")
        print(f"{Fore.YELLOW}[TIP] Suggestions:")
        print("   • 300px - Thumbnails")
        print("   • 800px - Standard web content")
        print("   • 1200px - Hero banners / High res")
        
        size_input = input(f"Enter size in pixels (or H/B/Q) [default {default_size}]: ").strip().lower()
        if size_input == 'q': sys.exit()
        if size_input == 'b': return 'back'
        if size_input == 'h':
            show_help_screen()
            continue
        if size_input == 'l':
            view_most_recent_log()
            continue
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
        print(Fore.CYAN + "[QUALITY] Enter export quality")
        print(f"{Fore.YELLOW}[TIP] Optimization Tips:")
        print("   • 80-85: High compression, perfect for web")
        print("   • 90-95: Balanced quality/size")
        
        quality_input = input(f"Enter quality (50-100 or H/B/Q) [default {default_quality}]: ").strip().lower()
        if quality_input == 'q': sys.exit()
        if quality_input == 'b': return 'back'
        if quality_input == 'h':
            show_help_screen()
            continue
        if quality_input == 'l':
            view_most_recent_log()
            continue
        if quality_input == '':
            quality = default_quality
            break
        try:
            quality = int(quality_input)
            if 50 <= quality <= 100: break
        except ValueError: pass
        print(f"{Fore.RED}Invalid input. Enter 50-100.")
    
    # Upscaling option
    while True:
        print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
        print_current_selections(output_format, size, quality)
        print(Fore.CYAN + "[UPSCALE] Upscaling Policy")
        print(f"{Fore.YELLOW}[TIP] Pro Tip:")
        print("   • Yes: Small images will be enlarged to target size")
        print("   • No: Small images kept at original size (best quality)")
        
        upscale_input = input("Allow upscaling small images? (y/n/B/Q) [default n]: ").strip().lower()
        if upscale_input == 'q': sys.exit()
        if upscale_input == 'b': return 'back'
        if upscale_input == 'h':
            show_help_screen()
            continue
        allow_upscale = upscale_input in ('y', 'yes')
        break
    
    # Cropping options
    aspect = None
    anchor = None
    aspect_desc = None
    while True:
        print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
        print_current_selections(output_format, size, quality, upscale=allow_upscale)
        print(Fore.CYAN + "[CROP] Smart Cropping & Aspect Ratio")
        print(f"{Fore.YELLOW}[TIP] Project Layout:")
        print("   • No: Keep original aspect ratio (standard)")
        print("   • Yes: Crop to a specific ratio (1:1, 16:9, etc.)")
        
        crop_input = input("Crop to a specific aspect ratio? (y/n/B/Q) [default n]: ").strip().lower()
        if crop_input == 'q': sys.exit()
        if crop_input == 'b': return 'back'
        if crop_input == 'h':
            show_help_screen()
            continue
            
        if crop_input in ('y', 'yes'):
            crop_input = 'y'
            # Aspect selection
            print(f"\n{Fore.CYAN}Choose Aspect Ratio:")
            print("  1: Square (1:1)")
            print("  2: Landscape (4:3)")
            print("  3: Widescreen (16:9)")
            print("  4: Portrait (3:4)")
            print("  5: Cinematic (21:9)")
            
            aspect_choice = input(f"{Fore.YELLOW}Choice (1-5): {Style.RESET_ALL}").strip()
            aspect_map = {
                "1": ((1, 1), "Square"),
                "2": ((4, 3), "Landscape"),
                "3": ((16, 9), "Widescreen"),
                "4": ((3, 4), "Portrait"),
                "5": ((21, 9), "Cinematic")
            }
            if aspect_choice in aspect_map:
                aspect, aspect_desc = aspect_map[aspect_choice]
            else:
                print(f"{Fore.YELLOW}Defaulting to Square (1:1)")
                aspect, aspect_desc = aspect_map["1"]
                
            # Anchor selection
            print(f"\n{Fore.CYAN}Choose Focal Point (Anchor):")
            print("  1: Center (Balanced)")
            print("  2: Top (Portraits)")
            print("  3: Bottom (Landscape foreground)")
            print("  4: Left")
            print("  5: Right")
            
            anchor_choice = input(f"{Fore.YELLOW}Choice (1-5): {Style.RESET_ALL}").strip()
            anchor_map = {"1": "center-center", "2": "top-center", "3": "bottom-center", "4": "center-left", "5": "center-right"}
            anchor = anchor_map.get(anchor_choice, "center-center")
            break
        else:
            crop_input = 'n'
            break

    # Recursive Mirroring
    while True:
        print("\n" + Fore.CYAN + "─" * 60 + Style.RESET_ALL)
        print_current_selections(output_format, size, quality, aspect=aspect_desc, upscale=allow_upscale)
        print(Fore.CYAN + "[RECURSION] Recursive Mirroring")
        print(f"{Fore.YELLOW}[TIP] Project Mirroring:")
        print("   • Yes: Scan all subfolders and recreate structure in output")
        print("   • No: Scan only the top-level folder")
        
        recursive_input = input("Mirror subfolders? (y/n/B/Q) [default y]: ").strip().lower()
        if recursive_input == 'q': sys.exit()
        if recursive_input == 'b': return 'back'
        if recursive_input == 'h':
            show_help_screen()
            continue
        recursive = recursive_input in ('', 'y', 'yes')
        break

    # Final Confirmation
    print("\n" + Fore.GREEN + "══ CONFIGURATION COMPLETE ══" + Style.RESET_ALL)
    print(f" Format:    {format_options.get(next(k for k,v in format_options.items() if v==output_format), output_format)}") # Re-derive key for display or just show format
    print(f" Size:      {size}px")
    print(f" Quality:   {quality}%")
    print(f" Upscale:   {allow_upscale}")
    print(f" Crop:      {f'{aspect[0]}:{aspect[1]}' if crop_input == 'y' else 'No'}")
    print(f" Recursive: {recursive}")
    
    confirm = input(f"\n{Fore.YELLOW}Start processing with these settings? (y/n) [default y]: {Style.RESET_ALL}").strip().lower()
    if confirm not in ('', 'y', 'yes'):
        return get_settings() # Restart or handling back is better, but following pattern

    if crop_input == 'y':
        return {
            "name": "Custom",
            "format": output_format,
            "size": size,
            "quality": quality,
            "crop": True,
            "aspect": aspect,
            "anchor": anchor,
            "allow_upscale": allow_upscale,
            "recursive": recursive
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
            "allow_upscale": allow_upscale,
            "recursive": recursive
        }

def get_smart_settings(image_files):
    """Auto-suggest settings based on images"""
    print(f"\n{Fore.MAGENTA}[SMART] Smart Mode: Analyzing images...{Style.RESET_ALL}")
    
    total_images = len(image_files)
    print(f"  • Analyzed {total_images} images")
    print(f"  • Suggested focus: Balanced Quality and Compression")
    
    # Suggest WEBP 800px 85% as a smart default
    settings = {
        "name": "Smart (Auto)",
        "format": "WEBP",
        "size": 800,
        "quality": 85,
        "crop": False,
        "aspect": None,
        "anchor": None,
        "allow_upscale": False,
        "recursive": True,
        "smart_optimize": True # Enable RMS Visual Check
    }
    
    print(f"\n{Fore.YELLOW}Suggested Settings:")
    print(f"  Format:  {settings['format']}")
    print(f"  Size:    {settings['size']}px")
    print(f"  Quality: {settings['quality']}%")
    print(f"  Crop:    {'No'}")
    print(f"  Recursive: {'Yes'}") # Suggest Yes for smart settings
    
    confirm = input(f"\n{Fore.CYAN}Use these settings? (y/n/B) [default y]: ").strip().lower()
    if confirm == 'b': return 'back'
    if confirm in ('', 'y', 'yes'):
        return settings
    else:
        print(f"{Fore.YELLOW}Switching to Manual Configuration...")
        return get_settings()

def process_images(input_folder, image_files, settings, mode, is_test=False, custom_output_folder=None):
    """Process images with given settings and rich logging"""
    if is_test:
        print(f"\n{Fore.YELLOW}[TEST RUN] Processing a single image to verify quality...{Style.RESET_ALL}")
    
    # Setup output folder
    # === Setup Session Folder ===
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"run_{timestamp}"
    if custom_output_folder:
        output_folder = custom_output_folder
    else:
        output_folder = os.path.join('resized_images', session_id)
    os.makedirs(output_folder, exist_ok=True)
    
    # Setup detailed logging
    log_data, settings_path = setup_logging(output_folder, settings, mode)
    
    # === Pre-Process Analysis ===
    print(f"\n{Fore.YELLOW}[INFO] Analyzing batch requirements...{Style.RESET_ALL}")
    analysis = {"downscale": 0, "upscale": 0, "keep": 0, "failed": 0}
    
    for fname in image_files:
        p_path = os.path.join(input_folder, fname)
        try:
            with Image.open(p_path) as p_img:
                w, h = p_img.size
                short = min(w, h)
                action, _, _ = get_resize_action_and_emoji(short, settings['size'], settings.get('allow_upscale', False))
                if action == "downscaled": analysis["downscale"] += 1
                elif action == "upscaled": analysis["upscale"] += 1
                else: analysis["keep"] += 1
        except:
            analysis["failed"] += 1

    total_images = len(image_files)
    processed_count = 0
    skipped_count = 0
    total_output_size = 0
    
    # Prepare size variants (for now just one, but kept extensible)
    size_variants = [{"name": "", "size": settings['size']}]
    
    if mode != "Watch":
        # === Processing Preview ===
        print(f"\n{Fore.CYAN}{Style.BRIGHT}[PREVIEW] PROCESSING PREVIEW:{Style.RESET_ALL}")
        print(f"  • Images to process: {len(image_files)}")
        print(f"  • Output Format:     {settings['format']}")
        print(f"  • Target Size:       {settings['size']}px (short edge)")
        print(f"  • Target Quality:    {settings['quality']}%")
        print(f"  • Crop to Aspect:    {f'{settings['aspect'][0]}:{settings['aspect'][1]}' if settings['crop'] else 'None'}")
        print(f"  • Upscaling:         {'Allowed [OK]' if settings.get('allow_upscale') else 'Prevented [!] '}")
        
        print(f"\n{Fore.GREEN}{Style.BRIGHT}[ANALYSIS] BATCH BREAKDOWN:{Style.RESET_ALL}")
        print(f"  (-) To Downscale:    {analysis['downscale']}")
        print(f"  (+) To Upscale:      {analysis['upscale']}")
        print(f"  (=) Already Target:  {analysis['keep']}")
        if analysis['failed'] > 0:
            print(f"  (!) Unreadable:      {analysis['failed']}")
        
        print(Fore.CYAN + "─" * 40 + Style.RESET_ALL)
        
        # Show sample filenames
        sample_count = min(3, len(image_files))
        print(f"{Fore.YELLOW}[INFO] Sample Filenames:{Style.RESET_ALL}")
        for i in range(sample_count):
            fname = image_files[i]
            sample_out = generate_web_friendly_filename(fname, settings, "TIMESTAMP")
            print(f"  {fname} -> {sample_out}")
        
        if len(image_files) > sample_count:
            print(f"  ... and {len(image_files) - sample_count} more")
            
        print(Fore.CYAN + "─" * 40 + Style.RESET_ALL)
        
        # Warning for large batches
        if len(image_files) > 50:
            print(f"{Fore.RED}{Style.BRIGHT}⚠️ LARGE BATCH WARNING:{Style.RESET_ALL}")
            print(f"  Processing {len(image_files)} images may take a few minutes.")
            print(Fore.CYAN + "─" * 40 + Style.RESET_ALL)
    
    if mode == "Watch":
        proceed = 'y'
    else:
        proceed = input(f"\n{Fore.GREEN}{Style.BRIGHT}Proceed with processing? (y/n) [default y]: {Style.RESET_ALL}").strip().lower()
        
    if proceed not in ('', 'y', 'yes'):
        print(f"{Fore.YELLOW}Processing cancelled.")
        return 
    
    # === Processing Loop ===
    start_processing_time = time.time()
    
    # Delta Sync Init
    delta_cache = DeltaSync.load_cache()
    cache_lock = threading.RLock()
    
    # Thread-safe progress tracking
    progress_lock = threading.RLock()
    progress_stats = {
        "processed": 0,
        "skipped": 0,
        "current": 0
    }
    
    def update_progress():
        with progress_lock:
            current = progress_stats["current"]
            total = total_images
            
            percent = 100 * (current / total) if total > 0 else 0
            bar_length = 30
            filled = int(bar_length * current // total) if total > 0 else 0
            bar = '█' * filled + '░' * (bar_length - filled)
            
            elapsed = time.time() - start_processing_time
            if current > 0:
                per_img = elapsed / current
                est_remaining = per_img * (total - current)
                time_str = f" | ETA: {int(est_remaining)}s"
            else:
                time_str = ""
                
            # Clear line first to avoid ghosting (using 100 chars for wider terminals)
            sys.stdout.write("\r" + " " * 100 + "\r")
            sys.stdout.write(f"{Fore.CYAN}[PROG] |{bar}| {percent:3.0f}% ({current}/{total}){time_str}{Style.RESET_ALL}")
            sys.stdout.flush()

    # Redefining process_single_image with FULL logic inline to ensure it works
    def process_item(filename):
        img_path = os.path.join(input_folder, filename)
        file_result = {"status": "skipped", "size_kb": 0}
        
        try:
            # === Delta Sync Check ===
            input_hash = DeltaSync.get_hash(img_path, settings)
            if input_hash:
                with cache_lock:
                    cached_entry = delta_cache.get(input_hash)
                
                if cached_entry and os.path.exists(cached_entry['path']):
                    # COPY existing optimized file
                    # Handle mirroring for output path
                    relative_dir = os.path.dirname(filename)
                    target_dir = os.path.join(output_folder, relative_dir)
                    if relative_dir:
                        os.makedirs(target_dir, exist_ok=True)
                        
                    new_filename = generate_web_friendly_filename(os.path.basename(filename), settings, session_id)
                    output_path = os.path.join(target_dir, new_filename)
                    
                    try:
                        shutil.copy2(cached_entry['path'], output_path)
                        file_size = get_file_size_kb(output_path)
                        # We simulate "success" result
                        return {
                            "status": "success",
                            "filename": filename,
                            "original_size": "Cached",
                            "final_size": "Cached",
                            "action": "synced (cached)",
                            "file_size": file_size,
                            "new_size_kb": file_size,
                            "log_entry": {
                                "file": filename,
                                "original": "Cached",
                                "result": "Cached",
                                "action": "synced (cached)",
                                "size_kb": file_size
                            },
                            "terminal_output": f"{Fore.CYAN}[SYNC]{Style.RESET_ALL} {filename:<30} | {'Cached':<10} | {file_size:>6} KB | Delta Sync Restore"
                        }
                    except:
                        pass # if copy fails, re-process

            # Init Check
            is_cr3 = filename.lower().endswith('.cr3')
            orientation_value = None
            working_img_path = img_path
            temp_to_delete = None
            
            if is_cr3:
                if not HAS_EXIFTOOL:
                    return {"status": "skipped", "reason": "Exiftool not found for CR3 conversion"}
                temp_jpg, orientation_value = convert_cr3_to_jpeg(img_path, input_folder)
                if not temp_jpg:
                    return {"status": "skipped", "reason": "CR3 extraction failed"}
                working_img_path = temp_jpg
                temp_to_delete = temp_jpg

            with Image.open(working_img_path) as img:
                original_size = img.size
                original_size_str = f"{original_size[0]}x{original_size[1]}"
                
                # Metadata stripping & basic orientation
                img = apply_exif_orientation(img)
                
                # Transparency
                has_alpha = False
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    has_alpha = True
                    if settings['format'] in ["JPEG", "BMP", "TIFF"]: # These formats don't support alpha
                        bg = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        bg.paste(img, mask=img.split()[3])
                        img = bg
                    else: # For formats like WEBP, PNG, keep alpha
                        img = img.convert("RGBA")
                else:
                    img = img.convert("RGB") # Ensure RGB for non-alpha images
                
                # Resize Logic
                final_short_edge = settings['size']
                width, height = img.size
                short_edge = min(width, height)
                
                action, emoji_tag, description = get_resize_action_and_emoji(short_edge, final_short_edge, settings.get('allow_upscale', False))
                resize_info = action # for log string
                
                new_img = img.copy() # Start with a copy to avoid modifying original `img`
                
                if short_edge <= final_short_edge and not settings.get('allow_upscale', False):
                    # Keep original size if smaller and upscaling not allowed
                    resize_info = f"kept at original size"
                elif short_edge == final_short_edge:
                    resize_info = f"already target size"
                else:
                    # Perform resize
                    if width < height:
                        new_width = final_short_edge
                        new_height = int((final_short_edge / width) * height)
                    else:
                        new_height = final_short_edge
                        new_width = int((final_short_edge / height) * width)
                    
                    if short_edge < final_short_edge: # Upscaling
                        new_img = img.resize((new_width, new_height), Image.BICUBIC)
                        resize_info = f"upscaled from {short_edge}px"
                    else: # Downscaling
                        new_img = img.resize((new_width, new_height), Image.LANCZOS)
                        resize_info = f"downscaled from {short_edge}px"
                
                # Apply cropping
                crop_info_str = ""
                if settings['crop']:
                    new_img = crop_to_ratio_with_anchor(new_img, settings['aspect'], settings['anchor'])
                    crop_info_str = f" → cropped to {new_img.size[0]}x{new_img.size[1]}"
                
                # Save
                # We only have one variant support active
                
                # Handle mirroring if dealing with relative paths
                relative_dir = os.path.dirname(filename)
                target_dir = os.path.join(output_folder, relative_dir)
                if relative_dir:
                    os.makedirs(target_dir, exist_ok=True)
                
                new_filename = generate_web_friendly_filename(os.path.basename(filename), settings, session_id)
                output_path = os.path.join(target_dir, new_filename)
                
                save_kwargs = {"quality": settings['quality'], "optimize": True}
                if settings['format'] == "WEBP":
                    save_kwargs["lossless"] = has_alpha
                    save_kwargs["method"] = 6  # Best compression
                
                if settings['format'] in ["JPEG", "PDF", "AVIF"]:
                    if new_img.mode != "RGB":
                        new_img = new_img.convert("RGB")
                
                # === Smart Quality Validation ===
                used_quality = settings['quality']
                smart_tag = ""
                
                if settings.get('smart_optimize', False) and settings['format'] in ['JPEG', 'WEBP']:
                    # Generate Candidate B (Aggressive)
                    aggressive_q = max(50, used_quality - 15)
                    # We need to save to buffer to compare re-compressed result vs "ideal" result
                    # Actually, we should compare: 
                    # 1. Standard Result (Q85)
                    # 2. Aggressive Result (Q70)
                    # And compare them visually. 
                    # Simpler: Generate Aggressive. Compare Aggressive to RAW New_Img (pre-compression).
                    
                    # We can't really compare properly without saving/loading or simulating save.
                    # Let's save Aggressive to temp.
                    temp_smart = output_path + ".smart_temp"
                    try:
                        save_kwargs_smart = save_kwargs.copy()
                        save_kwargs_smart['quality'] = aggressive_q
                        new_img.save(temp_smart, format=settings['format'], **save_kwargs_smart)
                        
                        # Load back to compare pixels
                        with Image.open(temp_smart) as smart_img:
                             # Compare smart_img vs new_img (in memory)
                             diff = calculate_rms_diff(new_img, smart_img)
                             
                        # Threshold: RMS < 2.5 is usuallly indistinguishable
                        if diff < 2.5:
                            # It looks good! Use it.
                            used_quality = aggressive_q
                            smart_tag = f" [Smart: Q{aggressive_q} | Diff {diff:.2f}]"
                            # Move temp to real
                            shutil.move(temp_smart, output_path)
                            resize_info += smart_tag
                        else:
                            # Too much diff, keep standard
                            # Delete temp
                            os.remove(temp_smart)
                            # Save standard (since we didn't save it yet fully, or we can just save now)
                            new_img.save(output_path, format=settings['format'], **save_kwargs)
                            
                    except:
                        # Fallback to standard
                         new_img.save(output_path, format=settings['format'], **save_kwargs)
                else:
                    # Standard Save
                    new_img.save(output_path, format=settings['format'], **save_kwargs)
                
                file_size = get_file_size_kb(output_path)
                
                # Update Cache
                if input_hash:
                    with cache_lock:
                        delta_cache[input_hash] = {"path": output_path, "timestamp": time.time()}

                file_result = {
                    "status": "success",
                    "filename": filename,
                    "original_size": original_size_str,
                    "final_size": f"{new_img.width}x{new_img.height}",
                    "action": action,
                    "file_size": file_size,
                    "log_entry": { 
                        "file": filename, 
                        "original": original_size_str, 
                        "result": f"{new_img.width}x{new_img.height}", 
                        "action": action, 
                        "size_kb": file_size 
                    },
                    "new_size_kb": file_size,
                    "terminal_output": f"{Fore.GREEN}[OK]{Style.RESET_ALL} {filename:<30} | {new_img.width}x{new_img.height:<10} | {file_size:>6} KB | {description}"
                }

            if temp_to_delete and os.path.exists(temp_to_delete):
                try: os.remove(temp_to_delete)
                except: pass
                
            return file_result

        except Exception as e:
            if temp_to_delete and os.path.exists(temp_to_delete):
                try: os.remove(temp_to_delete)
                except: pass
            return {"status": "failed", "reason": str(e)}
        finally:
            with progress_lock:
                progress_stats["current"] += 1
                # update_progress()  # Removed: Main thread handles consistent rendering now

    # Execute Thread Pool
    # We use a modest number of workers (e.g. 4 or 8) 
    # Python is GIL constrained for CPU but PIL releases GIL for some ops, and IO is beneficial.
    max_workers = min(32, os.cpu_count() + 4)
    if is_test: max_workers = 1
    
    if mode != "Watch":
        print(f"\n{Fore.CYAN}[PROG] Starting processing with {max_workers} workers...{Style.RESET_ALL}")
        update_progress()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_item, f): f for f in image_files}
        
        for future in concurrent.futures.as_completed(futures):
            filename = futures[future]
            try:
                res = future.result()
                if res and res["status"] == "success":
                    processed_count += 1
                    total_output_size += res["new_size_kb"]
                    
                    # Log to data structure
                    entry = res["log_entry"]
                    variant_name = size_variants[0]["name"] or "default"
                    if variant_name not in log_data["processing"]["images"]:
                         log_data["processing"]["images"][variant_name] = []
                    log_data["processing"]["images"][variant_name].append(entry)
                    
                    # Update Stats
                    action = res["action"]
                    if action == "upscaled": log_data["processing"]["stats"]["upscaled_count"] += 1
                    elif action == "downscaled": log_data["processing"]["stats"]["downscaled_count"] += 1
                    else: log_data["processing"]["stats"]["kept_original_size"] += 1
                    
                    # Print terminal output for this image (Scrolls up above the bar)
                    if mode != "Watch":
                        # Clear bar line, print result, then update_progress will redraw bar at bottom
                        sys.stdout.write("\r" + " " * 100 + "\r")
                        print(res["terminal_output"])
                        update_progress()
                    
                else:
                    skipped_count += 1
                    log_data["processing"]["stats"]["total_skipped"] += 1
                    if mode != "Watch":
                        sys.stdout.write("\r" + " " * 100 + "\r")
                        print(f"{Fore.RED}[SKIP] {filename:<30} | {res.get('reason', 'Unknown error')}")
                        update_progress()
            except Exception as exc:
                skipped_count += 1
                log_data["processing"]["stats"]["total_skipped"] += 1
                if mode != "Watch":
                    sys.stdout.write("\r" + " " * 100 + "\r")
                    print(f"{Fore.RED}[ERR]  {filename:<30} | {exc}")
                    update_progress()
    
    # Save Delta Cache
    DeltaSync.save_cache(delta_cache)
    
    if mode != "Watch":
        print() # Move to new line after progress finished
    
    # === Results ===
    processing_time = round(time.time() - start_processing_time, 2)
    total_input_mb = sum(os.path.getsize(os.path.join(input_folder, f)) for f in image_files) // (1024 * 1024)
    compression_ratio = (total_input_mb * 1024 / total_output_size) if total_output_size > 0 else 0
    
    save_final_log(log_data, settings_path, processing_time, total_input_mb, total_output_size)
    stats = log_data["processing"]["stats"]
    
    if mode != "Watch":
        print(f"""
{Fore.GREEN}{Style.BRIGHT}Processing Complete!{Style.RESET_ALL}
{Fore.CYAN}Session Results:
  • Images processed: {processed_count}
  • Images skipped: {skipped_count}
  • Total input size: {total_input_mb} MB
  • Total output size: {round(total_output_size / 1024, 2)} MB  
  • Overall compression: {compression_ratio:.1f}:1
  • Processing time: {processing_time}s

{Fore.YELLOW}Resize Operations:
  (+) Upscaled: {stats['upscaled_count']} images
  (-) Downscaled: {stats['downscaled_count']} images
  (=) Kept original: {stats['kept_original_size']} images

{Fore.MAGENTA}Output Location: {output_folder}
Detailed logs saved: processing_settings.json & processing_settings_summary.txt
""")
    else:
         print(f"{Fore.GREEN}[WATCH] Image processed successfully ({processing_time}s)")
    
    # Open output folder
    if is_test:
        print(f"{Fore.GREEN}[TEST] Test image saved to: {output_folder}")
        open_file_cross_platform(output_folder)
    elif mode == "Watch":
        pass # Never auto-open in watch mode
    elif input(f"\n{Fore.CYAN}Open output folder? (y/n) [default y]: ").strip().lower() in ('', 'y'):
        open_file_cross_platform(output_folder)
    
    # Cleanup CR3 temp files
    temp_cr3_folder = os.path.join('input_images', "temp_cr3")
    if os.path.exists(temp_cr3_folder):
        shutil.rmtree(temp_cr3_folder)
    
    print(f"{Fore.YELLOW}Thanks for using TerminallyQuick!")



# === DeltaSync Engine ===
class DeltaSync:
    CACHE_FILE = ".tq_sync"

    @staticmethod
    def get_hash(filepath, settings):
        """Generate MD5 hash of file content + settings configuration"""
        try:
            hasher = hashlib.md5()
            # File content (read in 64kb chunks)
            with open(filepath, 'rb') as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            
            # Mix in settings (convert to sorted string for stability)
            # We exclude keys that don't affect the image pixels/size to avoid cache misses on metadata changes (like rename?)
            # But name is not in settings passed here usually.
            # We must be careful about transient settings. 
            # Current 'settings' dict seems stable.
            settings_str = json.dumps(settings, sort_keys=True)
            hasher.update(settings_str.encode('utf-8'))
            
            return hasher.hexdigest()
        except Exception:
            return None

    @staticmethod
    def load_cache():
        if os.path.exists(DeltaSync.CACHE_FILE):
            try:
                with open(DeltaSync.CACHE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    @staticmethod
    def save_cache(cache):
        try:
            with open(DeltaSync.CACHE_FILE, 'w') as f:
                json.dump(cache, f, indent=2)
        except:
            pass

def calculate_rms_diff(img1, img2):
    """Calculate RMS difference between two images"""
    try:
        # Ensure same mode/size for comparison
        if img1.mode != img2.mode:
            img2 = img2.convert(img1.mode)
        if img1.size != img2.size:
            img2 = img2.resize(img1.size, Image.NEAREST)
            
        diff_img = ImageChops.difference(img1, img2)
        stat = ImageStat.Stat(diff_img)
        # RMS of differences
        sum_rms = sum(stat.rms) / len(stat.rms)
        return sum_rms
    except:
        return 999.0 # High difference on error

# === Watchdog Handler ===
if HAS_WATCHDOG:
    class TQWatchHandler(FileSystemEventHandler):
        def __init__(self, settings, session_id, input_folder):
            self.settings = settings
            self.session_id = session_id
            self.input_folder = input_folder
            self.output_dir = os.path.join('resized_images', session_id)
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir, exist_ok=True)
            print(f"{Fore.GREEN}[WATCH] Active! Monitoring 'input_images/' for new files...")
            print(f"{Fore.GREEN}[WATCH] Output: {self.output_dir}")
            print(f"{Fore.YELLOW}[INFO] Press Ctrl+C to stop watching.")

        def on_created(self, event):
            if event.is_directory: return
            filename = os.path.basename(event.src_path)
            if filename.startswith('.'): return # Ignore hidden files
            
            # Wait briefly for file write to complete
            time.sleep(1.0) 
            
            # Basic validation
            ext = os.path.splitext(filename)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.heic', '.avif', '.cr3', '.ico', '.ppm', '.pgm', '.pbm', '.tga']:
                print(f"\n{Fore.CYAN}[WATCH] Detected: {filename}")
                
                # We need to process this single file. 
                # Reusing process logic is tricky because process_images expects a batch.
                # However, we can just call process_images with a single file list in a quiet mode?
                # Or refactor?
                # For safety and speed, we will invoke process_images with a single file list, 
                # but we need to ensure it doesn't print the huge header every time.
                # Let's just suppress stdout temporarily or add a 'quiet' mode?
                # Actually, verbose is fine! It shows the user what's happening.
                
                # Careful: The event.src_path is absolute. process_images expects RELATIVE to input_folder.
                # input_folder is 'input_images'.
                # So we pass ['filename'] and input_folder='input_images'.
                
                try:
                    process_images(self.input_folder, [filename], self.settings, "Watch", custom_output_folder=self.output_dir)
                    print(f"{Fore.GREEN}[WATCH] Ready for next...")
                except Exception as e:
                    print(f"{Fore.RED}[WATCH] Error processing {filename}: {e}")

def run_watchdog_mode(input_folder='input_images'):
    if not HAS_WATCHDOG:
        print(f"{Fore.RED}[!] Watchdog library not found. Please run: pip install watchdog")
        input("Press Enter to return...")
        return

    print(f"\n{Fore.CYAN}=== Watchdog Mode 🐕 ===")
    
    profiles = list_profiles()
    if profiles:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}CHOOSE A WATCHDOG PRESET:{Style.RESET_ALL}")
        for i, profile in enumerate(profiles):
            print(f"  [{i+1}] Profile: {profile['name']}")
        print(f"  [M] Manual Configuration (Set custom settings)")
        print(f"  [B] Back to Main Menu")
        
        watch_choice = input(f"\n{Fore.YELLOW}Choice: {Style.RESET_ALL}").strip().lower()
        if watch_choice == 'b': return
        
        if watch_choice == 'm':
            settings = get_settings()
        else:
            try:
                val = int(watch_choice)
                if 1 <= val <= len(profiles):
                    settings = profiles[val-1]['settings']
                    print(f"{Fore.GREEN}[OK] Using Profile: {profiles[val-1]['name']}")
                else:
                    print(f"{Fore.RED}[!] Invalid choice. Switching to manual...")
                    settings = get_settings()
            except ValueError:
                print(f"{Fore.YELLOW}Defaulting to Manual Configuration...")
                settings = get_settings()
    else:
        print(f"{Fore.YELLOW}[INFO] No profiles found. Proceeding with Manual Configuration...")
        settings = get_settings()
        
    if settings == 'back': return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"run_WATCHDOG_{timestamp}"
    
    event_handler = TQWatchHandler(settings, session_id, input_folder)
    observer = Observer()
    observer.schedule(event_handler, path=input_folder, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print(f"\n{Fore.YELLOW}[WATCH] Stopping...")
    observer.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}[INFO] Session interrupted by user. Quitting gracefully...")
        sys.exit(0)

