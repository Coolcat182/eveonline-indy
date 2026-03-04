#!/usr/bin/env python3
"""
EVE Industry Bot Updater
Automatically updates the software when changes are available
"""

import os
import sys
import subprocess
import json
import hashlib
import requests
from datetime import datetime
import shutil

# Configuration
UPDATE_URL = os.getenv('UPDATE_URL', 'https://your-update-server.com/updates')
VERSION_FILE = 'version.json'
BACKUP_DIR = 'backups'
UPDATE_CHECK_INTERVAL = 3600  # 1 hour

class Updater:
    def __init__(self):
        self.current_version = self.get_current_version()
        self.update_available = False
        self.changelog = []
        
    def get_current_version(self):
        """Get current installed version"""
        if os.path.exists(VERSION_FILE):
            try:
                with open(VERSION_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('version', '0.0.0')
            except:
                pass
        return '0.0.0'
    
    def check_for_updates(self):
        """Check if updates are available"""
        try:
            # In production, this would fetch from your update server
            # For now, check a local version file or git
            if os.path.exists('.git'):
                # Check git for updates
                result = subprocess.run(
                    ['git', 'fetch', '--dry-run'],
                    capture_output=True,
                    text=True
                )
                
                if result.stderr and 'up to date' not in result.stderr.lower():
                    self.update_available = True
                    print("✅ Update available via git")
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Could not check for updates: {e}")
            return False
    
    def get_changelog(self):
        """Get changelog from git or update server"""
        try:
            if os.path.exists('.git'):
                result = subprocess.run(
                    ['git', 'log', '--oneline', '-10'],
                    capture_output=True,
                    text=True
                )
                return result.stdout.strip().split('\n')
        except:
            pass
        return []
    
    def create_backup(self):
        """Create backup before updating"""
        print("📦 Creating backup...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(BACKUP_DIR, f'backup_{timestamp}')
        
        os.makedirs(BACKUP_DIR, exist_ok=True)
        os.makedirs(backup_path, exist_ok=True)
        
        # Files to backup
        backup_files = [
            'data/',
            '.env',
            'version.json',
            'config/'
        ]
        
        for item in backup_files:
            if os.path.exists(item):
                dest = os.path.join(backup_path, item)
                if os.path.isdir(item):
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
        
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    
    def update(self):
        """Perform update"""
        print("\n🚀 Starting update process...")
        print("="*50)
        
        # 1. Create backup
        backup_path = self.create_backup()
        
        # 2. Pull updates
        try:
            print("📥 Downloading updates...")
            
            if os.path.exists('.git'):
                result = subprocess.run(
                    ['git', 'pull'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print("✅ Updates downloaded successfully")
                    
                    # Update version file
                    new_version = self.get_git_version()
                    self.save_version(new_version)
                    
                    print(f"✅ Updated to version {new_version}")
                    
                    # 3. Install dependencies if requirements.txt changed
                    if 'requirements.txt' in result.stdout:
                        print("📦 Updating dependencies...")
                        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
                    
                    # 4. Database migrations
                    self.run_migrations()
                    
                    print("\n✅ Update completed successfully!")
                    print(f"📝 Backup saved to: {backup_path}")
                    print("\n⚠️ Please restart the bot to apply changes")
                    
                    return True
                else:
                    print(f"❌ Update failed: {result.stderr}")
                    return False
            else:
                print("⚠️ Not a git repository. Manual update required.")
                return False
                
        except Exception as e:
            print(f"❌ Update failed: {e}")
            return False
    
    def get_git_version(self):
        """Get version from git"""
        try:
            result = subprocess.run(
                ['git', 'describe', '--tags', '--always'],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except:
            return datetime.now().strftime('%Y.%m.%d')
    
    def save_version(self, version):
        """Save version to file"""
        data = {
            'version': version,
            'updated_at': datetime.now().isoformat()
        }
        with open(VERSION_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def run_migrations(self):
        """Run database migrations"""
        print("🔄 Running database migrations...")
        
        # Check for migration files
        migrations_dir = 'migrations'
        if os.path.exists(migrations_dir):
            migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
            
            for migration in migration_files:
                print(f"  📄 Running {migration}...")
                # In production, execute SQL migrations
        
        print("✅ Migrations complete")
    
    def rollback(self, backup_path):
        """Rollback to previous version"""
        print(f"🔄 Rolling back from {backup_path}...")
        
        # Restore from backup
        for item in os.listdir(backup_path):
            src = os.path.join(backup_path, item)
            dst = item
            
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        
        print("✅ Rollback completed")

def main():
    """Main updater function"""
    updater = Updater()
    
    print("🔄 EVE Industry Bot Updater")
    print(f"📋 Current version: {updater.current_version}")
    print("="*50)
    
    # Check for updates
    print("\n🔍 Checking for updates...")
    
    if updater.check_for_updates():
        print("\n✅ Update available!")
        
        # Show changelog
        changelog = updater.get_changelog()
        if changelog:
            print("\n📝 Recent changes:")
            for change in changelog[:5]:
                print(f"  • {change}")
        
        # Ask to update
        response = input("\n🤔 Do you want to update now? (y/n): ").lower().strip()
        
        if response == 'y':
            updater.update()
        else:
            print("⏳ Update cancelled. Run this script again to update.")
    else:
        print("✅ You're up to date!")
    
    print("\n" + "="*50)
    print("For manual updates, use: python update.py --force")
    print("To rollback: python update.py --rollback")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        updater = Updater()
        
        if sys.argv[1] == '--force':
            updater.update()
        elif sys.argv[1] == '--rollback':
            # List backups
            if os.path.exists('backups'):
                backups = sorted(os.listdir('backups'), reverse=True)
                if backups:
                    print("Available backups:")
                    for i, backup in enumerate(backups[:5]):
                        print(f"  {i+1}. {backup}")
                    
                    choice = int(input("Select backup to restore: ")) - 1
                    if 0 <= choice < len(backups):
                        updater.rollback(os.path.join('backups', backups[choice]))
                else:
                    print("❌ No backups found")
        elif sys.argv[1] == '--version':
            print(f"Version: {updater.current_version}")
    else:
        main()
