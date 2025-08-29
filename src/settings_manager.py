#!/usr/bin/env python3

"""
TerminallyQuick Settings Manager
Import/Export configurations for team sharing
"""

import json
import os
import sys
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

def load_settings_from_file(file_path):
    """Load settings from JSON file"""
    try:
        with open(file_path, 'r') as f:
            settings = json.load(f)
        return settings
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to load settings: {e}")
        return None

def save_settings_to_file(settings, file_path):
    """Save settings to JSON file"""
    try:
        # Add metadata
        settings_with_meta = {
            "terminallyquick_version": "2.0",
            "exported_on": datetime.now().isoformat(),
            "settings": settings
        }
        
        with open(file_path, 'w') as f:
            json.dump(settings_with_meta, f, indent=2)
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to save settings: {e}")
        return False

def create_team_preset(name, description):
    """Interactive creation of team preset"""
    print(f"{Fore.CYAN}🏗️ Creating team preset: {name}")
    
    # Web Developer presets as templates
    templates = {
        "1": {"format": "WEBP", "size": 300, "quality": 85, "crop": True, "aspect": (1, 1)},
        "2": {"format": "WEBP", "size": 1200, "quality": 90, "crop": True, "aspect": (16, 9)},
        "3": {"format": "WEBP", "size": 800, "quality": 85, "crop": False},
        "4": {"format": "JPEG", "size": 1080, "quality": 90, "crop": True, "aspect": (1, 1)}
    }
    
    print("Base on existing preset?")
    print("  1: Web Thumbnails | 2: Hero Images | 3: Blog Images | 4: Social Media")
    print("  5: Start from scratch")
    
    choice = input("Choose template [1-5]: ").strip()
    
    if choice in templates:
        settings = templates[choice].copy()
        settings["name"] = name
        settings["description"] = description
    else:
        # Custom from scratch
        settings = {
            "name": name,
            "description": description,
            "format": "WEBP",
            "size": 800,
            "quality": 85,
            "crop": False
        }
    
    # Allow customization
    print(f"\n{Fore.YELLOW}Customize settings for {name}:")
    
    # Format
    format_choice = input(f"Format [{settings['format']}]: ").strip().upper()
    if format_choice:
        settings['format'] = format_choice
    
    # Size  
    size_choice = input(f"Size [{settings['size']}px]: ").strip()
    if size_choice:
        try:
            settings['size'] = int(size_choice)
        except ValueError:
            pass
    
    # Quality
    quality_choice = input(f"Quality [{settings['quality']}%]: ").strip()
    if quality_choice:
        try:
            settings['quality'] = int(quality_choice)
        except ValueError:
            pass
    
    return settings

def main():
    print(f"""{Fore.CYAN}{Style.BRIGHT}
╔══════════════════════════════════════════════════════════╗
║              TerminallyQuick Settings Manager           ║
║                  Team Configuration Tool                ║
╚══════════════════════════════════════════════════════════╝
{Style.RESET_ALL}""")
    
    print("What would you like to do?")
    print("  1: Export current settings")
    print("  2: Import team settings") 
    print("  3: Create new team preset")
    print("  4: View existing settings")
    print("  q: Quit")
    
    choice = input("\nChoice: ").strip().lower()
    
    if choice == '1':
        # Export recent settings
        recent_file = os.path.join(os.path.expanduser("~"), ".terminallyquick_recent.json")
        if os.path.exists(recent_file):
            with open(recent_file, 'r') as f:
                recent_settings = json.load(f)
            
            export_path = input("Export filename [team_settings.json]: ").strip()
            if not export_path:
                export_path = "team_settings.json"
            
            if save_settings_to_file(recent_settings, export_path):
                print(f"{Fore.GREEN}✅ Settings exported to {export_path}")
            
        else:
            print(f"{Fore.RED}❌ No recent settings found. Run TerminallyQuick first.")
    
    elif choice == '2':
        # Import settings
        import_path = input("Settings file path: ").strip()
        if os.path.exists(import_path):
            settings = load_settings_from_file(import_path)
            if settings:
                print(f"{Fore.GREEN}✅ Settings loaded:")
                print(f"  Preset: {settings.get('settings', {}).get('name', 'Unknown')}")
                print(f"  Format: {settings.get('settings', {}).get('format', 'Unknown')}")
                print(f"  Size: {settings.get('settings', {}).get('size', 'Unknown')}px")
                
                # Save as recent settings
                recent_file = os.path.join(os.path.expanduser("~"), ".terminallyquick_recent.json")
                with open(recent_file, 'w') as f:
                    json.dump(settings.get('settings', {}), f, indent=2)
                
                print(f"{Fore.CYAN}💾 Settings imported! They'll be available as 'recent settings' in TerminallyQuick.")
        else:
            print(f"{Fore.RED}❌ File not found: {import_path}")
    
    elif choice == '3':
        # Create new preset
        name = input("Preset name: ").strip()
        description = input("Description: ").strip()
        
        if name:
            settings = create_team_preset(name, description)
            
            filename = f"{name.lower().replace(' ', '_')}_preset.json"
            if save_settings_to_file(settings, filename):
                print(f"{Fore.GREEN}✅ Team preset created: {filename}")
    
    elif choice == '4':
        # View settings
        recent_file = os.path.join(os.path.expanduser("~"), ".terminallyquick_recent.json")
        if os.path.exists(recent_file):
            with open(recent_file, 'r') as f:
                recent = json.load(f)
            
            print(f"{Fore.CYAN}📋 Current Settings:")
            for key, value in recent.items():
                print(f"  {key}: {value}")
        else:
            print(f"{Fore.YELLOW}ℹ️ No recent settings found.")
    
    elif choice == 'q':
        print(f"{Fore.YELLOW}Goodbye!")
    else:
        print(f"{Fore.RED}❌ Invalid choice.")

if __name__ == "__main__":
    main()
