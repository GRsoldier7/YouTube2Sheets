#!/usr/bin/env python3
"""
YouTube2Sheets GUI Launcher
Proper launcher that sets up the Python path correctly
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Now import and launch the GUI
try:
    from src.gui.main_app import launch
    print("Starting YouTube2Sheets GUI...")
    launch()
except Exception as e:
    print(f"Error launching GUI: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
