#!/usr/bin/env python3
"""
YouTube2Sheets - Direct Python Launcher
Run this file to start the application directly
"""

import os
import sys
from pathlib import Path

# Change to script directory
os.chdir(Path(__file__).parent)

print("🎬 Starting YouTube2Sheets - Modern 2025...")
print("📍 Working directory:", os.getcwd())

try:
    # Import and launch
    from src.gui.beautiful_ui import launch
    print("✅ GUI module imported successfully")
    print("🚀 Launching application...")
    launch()
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\n🔧 Please install dependencies:")
    print("   pip install -r requirements.txt")
    input("\nPress Enter to exit...")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔧 Troubleshooting:")
    print("   1. Check that Python is installed")
    print("   2. Install dependencies: pip install -r requirements.txt")
    print("   3. Check logs/youtube2sheets.log for details")
    input("\nPress Enter to exit...")
    sys.exit(1)
