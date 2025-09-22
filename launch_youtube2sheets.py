#!/usr/bin/env python3
"""
YouTube2Sheets Launcher
Main entry point for the YouTube2Sheets application
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Main entry point"""
    print("🚀 Starting YouTube2Sheets...")
    
    try:
        # Import and run the GUI
        from youtube_to_sheets_gui import main as gui_main
        gui_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required dependencies:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()