#!/usr/bin/env python3
"""
YouTube2Sheets - Robust Launcher
================================
Future-proof launcher with comprehensive error handling and diagnostics.
This launcher ensures the GUI always launches successfully.
"""

import sys
import os
import traceback
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

def setup_environment():
    """Setup the Python environment and paths."""
    try:
        # Add the project root to Python path
        project_root = Path(__file__).resolve().parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Set working directory
        os.chdir(project_root)
        
        print(f"✅ Environment setup complete")
        print(f"   Project root: {project_root}")
        print(f"   Python path: {sys.path[0]}")
        
        return True
    except Exception as e:
        print(f"❌ Environment setup failed: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are available."""
    try:
        import customtkinter as ctk
        print(f"✅ CustomTkinter: {ctk.__version__}")
        
        # Test CustomTkinter basic functionality
        root = tk.Tk()
        root.withdraw()  # Hide the test window
        
        test_frame = ctk.CTkFrame(root)
        test_frame.destroy()
        root.destroy()
        
        print("✅ CustomTkinter functionality test passed")
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    except Exception as e:
        print(f"❌ Dependency test failed: {e}")
        return False

def launch_gui():
    """Launch the main GUI application."""
    try:
        print("🚀 Launching YouTube2Sheets GUI...")
        
        # Import and create the GUI
        from src.gui.main_app import YouTube2SheetsGUI
        
        print("✅ GUI module imported successfully")
        
        # Create and run the GUI
        app = YouTube2SheetsGUI()
        print("✅ GUI instance created successfully")
        
        # Start the main loop
        app.root.mainloop()
        
    except Exception as e:
        print(f"❌ GUI launch failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Traceback: {traceback.format_exc()}")
        
        # Show error dialog
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "YouTube2Sheets Launch Error",
            f"Failed to launch the GUI:\n\n{str(e)}\n\n"
            f"Please check the console output for more details."
        )
        root.destroy()
        
        return False

def main():
    """Main launcher function with comprehensive error handling."""
    print("=" * 60)
    print("🎯 YouTube2Sheets - Robust Launcher")
    print("=" * 60)
    
    try:
        # Step 1: Setup environment
        if not setup_environment():
            print("❌ Environment setup failed")
            return 1
        
        # Step 2: Check dependencies
        if not check_dependencies():
            print("❌ Dependency check failed")
            return 1
        
        # Step 3: Launch GUI
        if not launch_gui():
            print("❌ GUI launch failed")
            return 1
        
        print("✅ Application closed successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
