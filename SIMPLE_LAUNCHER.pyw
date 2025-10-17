#!/usr/bin/env python3
"""
YouTube2Sheets - Simple Bulletproof Launcher
============================================
Minimal launcher that avoids CustomTkinter issues.
"""

import sys
import os
from pathlib import Path

def main():
    """Simple launcher that just runs the GUI."""
    try:
        # Add project root to path
        project_root = Path(__file__).resolve().parent
        sys.path.insert(0, str(project_root))
        sys.path.insert(0, str(project_root / "src"))
        
        # Change to project directory
        os.chdir(project_root)
        
        # Set environment variables for proper module resolution
        os.environ['PYTHONPATH'] = f"{project_root}{os.pathsep}{project_root / 'src'}"
        
        # Import and run
        from src.gui.main_app import YouTube2SheetsGUI
        app = YouTube2SheetsGUI()
        app.root.mainloop()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
