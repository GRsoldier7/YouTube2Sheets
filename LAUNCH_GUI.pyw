"""
YouTube2Sheets - Robust GUI Launcher
This launcher ensures the GUI window appears and is visible
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import subprocess

# Change to script directory
os.chdir(Path(__file__).parent)

def launch_gui():
    """Launch the GUI with proper window management"""
    try:
        # Import and launch the working GUI
        from src.gui.main_app import YouTube2SheetsGUI

        # Create the GUI instance
        gui = YouTube2SheetsGUI()
        
        # Ensure window is visible and on top
        gui.root.lift()
        gui.root.attributes('-topmost', True)
        gui.root.after(100, lambda: gui.root.attributes('-topmost', False))
        
        # Center the window on screen
        gui.root.update_idletasks()
        width = gui.root.winfo_width()
        height = gui.root.winfo_height()
        x = (gui.root.winfo_screenwidth() // 2) - (width // 2)
        y = (gui.root.winfo_screenheight() // 2) - (height // 2)
        gui.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Start the GUI
        gui.root.mainloop()
        
    except Exception as e:
        # Show error in a message box
        root = tk.Tk()
        root.withdraw()
        
        error_msg = f"Failed to launch YouTube2Sheets GUI:\n\n{str(e)}\n\n"
        error_msg += "Please check:\n"
        error_msg += "1. Python is installed\n"
        error_msg += "2. Dependencies: pip install -r requirements.txt\n"
        error_msg += "3. Check logs for details"
        
        messagebox.showerror("YouTube2Sheets Error", error_msg)
        
        # Write to log file
        log_file = Path("logs/launcher_error.log")
        log_file.parent.mkdir(exist_ok=True)
        with open(log_file, "w") as f:
            f.write(f"Error launching GUI: {str(e)}\n")
            import traceback
            f.write(traceback.format_exc())
        
        sys.exit(1)

if __name__ == "__main__":
    launch_gui()

