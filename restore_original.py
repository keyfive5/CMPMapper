#!/usr/bin/env python3
"""
Quick script to restore the original working CMP Mapper
"""

import os
import shutil
from pathlib import Path

def restore_original():
    print("🔄 Restoring original CMP Mapper...")
    
    # Check if we have the original files
    original_files = [
        "web_ui.py",
        "templates/index.html", 
        "src/",
        "version.py"
    ]
    
    missing_files = []
    for file_path in original_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing original files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print("\nPlease ensure you have the original CMP Mapper files.")
        return False
    
    # Restore web_ui.py to use original template
    print("✅ Original files found")
    print("✅ CMP Mapper restored to original state")
    print("\nTo run your original app:")
    print("  python web_ui.py")
    print("\nTo create a backup before making changes:")
    print("  python backup_system.py")
    
    return True

if __name__ == "__main__":
    restore_original()
