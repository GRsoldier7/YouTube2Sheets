"""
YouTube2Sheets - Simple GUI Launcher
Double-click this file to start the application
"""

import os
import sys
from pathlib import Path

# Change to script directory
os.chdir(Path(__file__).parent)

# Launch the GUI
try:
    from src.gui.beautiful_ui import launch
    launch()
except Exception as e:
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()
    
    error_details = f"Failed to start:\n\n{str(e)}\n\n"
    error_details += "Please ensure:\n"
    error_details += "1. Python is installed\n"
    error_details += "2. Dependencies installed: pip install -r requirements.txt\n"
    error_details += "3. Check logs/youtube2sheets.log for details"
    
    messagebox.showerror("YouTube2Sheets Error", error_details)
    
    # Also write to a log file for debugging
    log_file = Path(__file__).parent / "logs" / "launcher_error.log"
    log_file.parent.mkdir(exist_ok=True)
    with open(log_file, "w") as f:
        f.write(f"Error launching YouTube2Sheets:\n{str(e)}\n")
        import traceback
        f.write(traceback.format_exc())
    
    sys.exit(1)


