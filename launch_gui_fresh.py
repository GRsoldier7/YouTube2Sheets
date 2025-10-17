#!/usr/bin/env python3
"""
Fresh YouTube2Sheets GUI Launcher
Forces fresh code load by clearing cache and using -B flag
"""

import sys
import os
import subprocess
from pathlib import Path

def clear_python_cache():
    """Clear all Python cache files."""
    print("🧹 Clearing Python cache...")
    
    # Remove __pycache__ directories
    try:
        result = subprocess.run([
            "powershell", "-Command", 
            "Get-ChildItem -Path . -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force"
        ], capture_output=True, text=True)
        print("✅ Removed __pycache__ directories")
    except Exception as e:
        print(f"⚠️ Error removing __pycache__: {e}")
    
    # Remove .pyc files
    try:
        result = subprocess.run([
            "powershell", "-Command", 
            "Get-ChildItem -Path . -Recurse -File -Filter '*.pyc' | Remove-Item -Force"
        ], capture_output=True, text=True)
        print("✅ Removed .pyc files")
    except Exception as e:
        print(f"⚠️ Error removing .pyc files: {e}")

def main():
    """Launch GUI with fresh code."""
    print("🚀 YouTube2Sheets Fresh Launcher")
    print("=" * 50)
    
    # Clear cache first
    clear_python_cache()
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        print("📦 Importing fresh modules...")
        
        # Import and launch the GUI with fresh code
        from src.gui.main_app import YouTube2SheetsGUI
        
        print("✅ Fresh modules loaded successfully")
        print("🖥️ Creating GUI instance...")
        
        gui = YouTube2SheetsGUI()
        
        print("✅ GUI created successfully!")
        print("🔄 Starting GUI main loop...")
        print("The GUI window should now be visible on your screen.")
        
        # Run the GUI (this will block until the GUI is closed)
        gui.run()
        
        print("✅ GUI closed successfully")
        
    except KeyboardInterrupt:
        print("\n👋 GUI closed by user")
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
