#!/usr/bin/env python3
"""
Simple YouTube2Sheets GUI Launcher
Launcher that avoids potential hanging issues during initialization
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Launch the GUI with error handling."""
    try:
        print("Starting YouTube2Sheets GUI...")
        print("Note: GUI must run in the main thread")
        
        # Import and launch the GUI
        from src.gui.main_app import YouTube2SheetsGUI
        
        print("Creating GUI instance...")
        gui = YouTube2SheetsGUI()
        
        print("GUI created successfully!")
        print("Starting GUI main loop...")
        print("The GUI window should now be visible on your screen.")
        
        # Run the GUI (this will block until the GUI is closed)
        gui.run()
        
        print("GUI closed successfully")
        
    except KeyboardInterrupt:
        print("\nGUI closed by user")
    except Exception as e:
        print(f"Error launching GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
