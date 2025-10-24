#!/usr/bin/env python3
"""
Backup system for CMP Mapper
Allows you to save and restore working versions
"""

import os
import shutil
import datetime
from pathlib import Path

class CMPMapperBackup:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, name=None):
        """Create a backup of the current working state"""
        if name is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"backup_{timestamp}"
        
        backup_path = self.backup_dir / name
        backup_path.mkdir(exist_ok=True)
        
        # Files to backup
        files_to_backup = [
            "web_ui.py",
            "templates/index.html",
            "src/",
            "version.py",
            "requirements.txt"
        ]
        
        print(f"Creating backup: {name}")
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    shutil.copy2(file_path, backup_path / os.path.basename(file_path))
                    print(f"  ✓ Backed up {file_path}")
                elif os.path.isdir(file_path):
                    dest_dir = backup_path / os.path.basename(file_path)
                    shutil.copytree(file_path, dest_dir, dirs_exist_ok=True)
                    print(f"  ✓ Backed up directory {file_path}")
        
        # Create backup info file
        info_file = backup_path / "backup_info.txt"
        with open(info_file, 'w') as f:
            f.write(f"Backup created: {datetime.datetime.now()}\n")
            f.write(f"Backup name: {name}\n")
            f.write("Files included:\n")
            for file_path in files_to_backup:
                if os.path.exists(file_path):
                    f.write(f"  - {file_path}\n")
        
        print(f"✅ Backup created successfully: {backup_path}")
        return backup_path
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        for item in self.backup_dir.iterdir():
            if item.is_dir() and (item / "backup_info.txt").exists():
                with open(item / "backup_info.txt", 'r') as f:
                    info = f.read()
                backups.append((item.name, info))
        
        return backups
    
    def restore_backup(self, backup_name):
        """Restore from a backup"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            print(f"❌ Backup '{backup_name}' not found")
            return False
        
        print(f"Restoring from backup: {backup_name}")
        
        # Restore files
        for item in backup_path.iterdir():
            if item.is_file() and item.name != "backup_info.txt":
                shutil.copy2(item, item.name)
                print(f"  ✓ Restored {item.name}")
            elif item.is_dir():
                if os.path.exists(item.name):
                    shutil.rmtree(item.name)
                shutil.copytree(item, item.name)
                print(f"  ✓ Restored directory {item.name}")
        
        print(f"✅ Restored from backup: {backup_name}")
        return True
    
    def delete_backup(self, backup_name):
        """Delete a backup"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            print(f"❌ Backup '{backup_name}' not found")
            return False
        
        shutil.rmtree(backup_path)
        print(f"✅ Deleted backup: {backup_name}")
        return True

def main():
    backup_system = CMPMapperBackup()
    
    print("🍪 CMP Mapper Backup System")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Create backup")
        print("2. List backups")
        print("3. Restore backup")
        print("4. Delete backup")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            name = input("Enter backup name (or press Enter for auto-generated): ").strip()
            if not name:
                name = None
            backup_system.create_backup(name)
        
        elif choice == "2":
            backups = backup_system.list_backups()
            if not backups:
                print("No backups found")
            else:
                print("\nAvailable backups:")
                for name, info in backups:
                    print(f"\n📁 {name}")
                    print(info)
        
        elif choice == "3":
            backups = backup_system.list_backups()
            if not backups:
                print("No backups found")
            else:
                print("\nAvailable backups:")
                for i, (name, _) in enumerate(backups, 1):
                    print(f"{i}. {name}")
                
                try:
                    idx = int(input("Enter backup number to restore: ")) - 1
                    if 0 <= idx < len(backups):
                        backup_system.restore_backup(backups[idx][0])
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")
        
        elif choice == "4":
            backups = backup_system.list_backups()
            if not backups:
                print("No backups found")
            else:
                print("\nAvailable backups:")
                for i, (name, _) in enumerate(backups, 1):
                    print(f"{i}. {name}")
                
                try:
                    idx = int(input("Enter backup number to delete: ")) - 1
                    if 0 <= idx < len(backups):
                        confirm = input(f"Are you sure you want to delete '{backups[idx][0]}'? (y/N): ")
                        if confirm.lower() == 'y':
                            backup_system.delete_backup(backups[idx][0])
                        else:
                            print("Cancelled")
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")
        
        elif choice == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
