#!/usr/bin/env python3
"""
YouTube2Sheets Launcher
======================

Main launcher script for the YouTube to Google Sheets automation tool.
This script handles environment setup and launches the appropriate interface.

Author: AI Assistant
Version: 2.0
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'google-api-python-client',
        'google-auth',
        'google-auth-oauthlib',
        'google-auth-httplib2',
        'python-dotenv',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment():
    """Check if environment is properly configured."""
    env_file = Path('.env')
    credentials_file = Path('credentials.json')
    
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("   Run: python setup_secure_environment.py")
        return False
    
    if not credentials_file.exists():
        print("⚠️  credentials.json file not found")
        print("   Run: python setup_secure_environment.py")
        return False
    
    return True

def launch_gui():
    """Launch the GUI application."""
    try:
        from youtube_to_sheets_gui import main
        main()
    except ImportError as e:
        print(f"❌ Error importing GUI: {e}")
        return False
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        return False
    
    return True

def launch_cli():
    """Launch the CLI application."""
    try:
        from youtube_to_sheets import main
        main()
    except ImportError as e:
        print(f"❌ Error importing CLI: {e}")
        return False
    except Exception as e:
        print(f"❌ Error launching CLI: {e}")
        return False
    
    return True

def main():
    """Main launcher function."""
    print("🚀 YouTube2Sheets Launcher")
    print("=" * 40)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        return 1
    
    print("✅ All dependencies found")
    
    # Check environment
    print("\n🔍 Checking environment...")
    if not check_environment():
        print("\n💡 To set up your environment:")
        print("   1. Run: python setup_secure_environment.py")
        print("   2. Edit .env file with your actual API keys")
        print("   3. Replace credentials.json with your Google Sheets credentials")
        return 1
    
    print("✅ Environment configured")
    
    # Choose interface
    print("\n🎯 Choose interface:")
    print("   1. GUI (Graphical Interface)")
    print("   2. CLI (Command Line Interface)")
    
    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == '1':
            print("\n🖥️  Launching GUI...")
            if launch_gui():
                return 0
            else:
                return 1
        elif choice == '2':
            print("\n💻 Launching CLI...")
            if launch_cli():
                return 0
            else:
                return 1
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    sys.exit(main())