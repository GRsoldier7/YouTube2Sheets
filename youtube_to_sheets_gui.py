"""
YouTube to Google Sheets Automation - GUI
=========================================

This module contains the graphical user interface for the YouTube to Google
Sheets automation tool.

Author: AI Assistant
Version: 2.0
"""

import os
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font as tkfont
import json
from typing import List, Optional

from dotenv import load_dotenv

from youtube_to_sheets import YouTubeToSheetsAutomator

# Load environment variables
load_dotenv()

# Custom logging handler to capture backend logs
class GUILogHandler(logging.Handler):
    def __init__(self, gui_instance):
        super().__init__()
        self.gui = gui_instance
        
    def emit(self, record):
        if self.gui and hasattr(self.gui, 'log_message'):
            # Format the log message
            msg = self.format(record)
            # Send to GUI (non-blocking)
            try:
                self.gui.root.after(0, lambda: self.gui.log_message(msg, debug=True))
            except:
                pass

# Color constants
DARK_BG = "#1e1e1e"
DARK_PANEL = "#1a1f2e"
DARK_ENTRY = "#2d2d2d"
DARK_TEXT = "#ffffff"
BLUE_ACCENT = "#007acc"
BLUE_ACCENT_HOVER = "#29b6f6"
GREEN_SUCCESS = "#4caf50"
RED_ERROR = "#f44336"
ORANGE_WARNING = "#ff9800"

class YouTube2SheetsGUI:
    """Main GUI class for YouTube to Google Sheets automation."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.automator = None
        self.setup_logging()
        self.setup_gui()
        self.load_config()
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('youtube2sheets.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_gui(self):
        """Setup the main GUI interface."""
        self.root.title("YouTube to Google Sheets - Automation Tool")
        self.root.geometry("1000x700")
        self.root.configure(bg=DARK_BG)
        
        # Configure style
        self.setup_styles()
        
        # Create main frame
        self.create_main_frame()
        
        # Create menu
        self.create_menu()
        
    def setup_styles(self):
        """Setup custom styles for the GUI."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', 
                       background=DARK_BG, 
                       foreground=DARK_TEXT,
                       font=('Arial', 16, 'bold'))
        
        style.configure('Heading.TLabel',
                       background=DARK_BG,
                       foreground=DARK_TEXT,
                       font=('Arial', 12, 'bold'))
        
        style.configure('Info.TLabel',
                       background=DARK_BG,
                       foreground=DARK_TEXT,
                       font=('Arial', 10))
        
        style.configure('Custom.TButton',
                       background=BLUE_ACCENT,
                       foreground=DARK_TEXT,
                       font=('Arial', 10, 'bold'),
                       padding=(10, 5))
        
        style.map('Custom.TButton',
                 background=[('active', BLUE_ACCENT_HOVER)])
        
    def create_main_frame(self):
        """Create the main application frame."""
        # Title
        title_label = ttk.Label(self.root, text="YouTube to Google Sheets Automation", 
                               style='Title.TLabel')
        title_label.pack(pady=20)
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Configuration
        self.create_config_panel(main_frame)
        
        # Right panel - Logs and Status
        self.create_status_panel(main_frame)
        
    def create_config_panel(self, parent):
        """Create the configuration panel."""
        config_frame = ttk.LabelFrame(parent, text="Configuration", padding=10)
        config_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # YouTube Channel Input
        ttk.Label(config_frame, text="YouTube Channel:", style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.channel_var = tk.StringVar()
        channel_entry = ttk.Entry(config_frame, textvariable=self.channel_var, width=50)
        channel_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Google Sheets URL Input
        ttk.Label(config_frame, text="Google Sheets URL:", style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.sheets_var = tk.StringVar()
        sheets_entry = ttk.Entry(config_frame, textvariable=self.sheets_var, width=50)
        sheets_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Tab Name Input
        ttk.Label(config_frame, text="Tab Name:", style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.tab_var = tk.StringVar(value="YouTube Videos")
        tab_entry = ttk.Entry(config_frame, textvariable=self.tab_var, width=50)
        tab_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.sync_button = ttk.Button(button_frame, text="Sync to Sheets", 
                                     command=self.start_sync, style='Custom.TButton')
        self.sync_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.test_button = ttk.Button(button_frame, text="Test Connection", 
                                     command=self.test_connection, style='Custom.TButton')
        self.test_button.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(config_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10)
        
    def create_status_panel(self, parent):
        """Create the status and logs panel."""
        status_frame = ttk.LabelFrame(parent, text="Status & Logs", padding=10)
        status_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Status text
        self.status_text = scrolledtext.ScrolledText(status_frame, height=25, width=50,
                                                   bg=DARK_ENTRY, fg=DARK_TEXT,
                                                   font=('Consolas', 9))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
    def create_menu(self):
        """Create the application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Configuration", command=self.load_config)
        file_menu.add_command(label="Save Configuration", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def log_message(self, message, debug=False):
        """Add a message to the status log."""
        if debug:
            self.status_text.insert(tk.END, f"[DEBUG] {message}\n")
        else:
            self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_sync(self):
        """Start the synchronization process."""
        channel = self.channel_var.get().strip()
        sheets_url = self.sheets_var.get().strip()
        tab_name = self.tab_var.get().strip()
        
        if not channel or not sheets_url:
            messagebox.showerror("Error", "Please enter both YouTube channel and Google Sheets URL")
            return
            
        # Disable button and start progress
        self.sync_button.config(state='disabled')
        self.progress.start()
        
        # Start sync in separate thread
        sync_thread = threading.Thread(target=self.run_sync, args=(channel, sheets_url, tab_name))
        sync_thread.daemon = True
        sync_thread.start()
        
    def run_sync(self, channel, sheets_url, tab_name):
        """Run the synchronization process."""
        try:
            self.log_message("Starting synchronization...")
            
            # Initialize automator
            self.automator = YouTubeToSheetsAutomator()
            
            # Perform sync
            result = self.automator.sync_channel_to_sheet(channel, sheets_url, tab_name)
            
            if result:
                self.log_message("✅ Synchronization completed successfully!")
            else:
                self.log_message("❌ Synchronization failed. Check logs for details.")
                
        except Exception as e:
            self.log_message(f"❌ Error during sync: {str(e)}")
        finally:
            # Re-enable button and stop progress
            self.root.after(0, self.sync_complete)
            
    def sync_complete(self):
        """Called when sync is complete."""
        self.sync_button.config(state='normal')
        self.progress.stop()
        
    def test_connection(self):
        """Test the connection to YouTube and Google Sheets."""
        try:
            self.log_message("Testing connections...")
            
            # Test YouTube API
            youtube_key = os.getenv('YOUTUBE_API_KEY')
            if not youtube_key:
                self.log_message("❌ YouTube API key not found in environment")
                return
            else:
                self.log_message("✅ YouTube API key found")
                
            # Test Google Sheets
            sheets_file = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON')
            if not sheets_file or not os.path.exists(sheets_file):
                self.log_message("❌ Google Sheets credentials not found")
                return
            else:
                self.log_message("✅ Google Sheets credentials found")
                
            self.log_message("✅ All connections verified!")
            
        except Exception as e:
            self.log_message(f"❌ Connection test failed: {str(e)}")
            
    def load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists('gui_config.json'):
                with open('gui_config.json', 'r') as f:
                    config = json.load(f)
                    self.channel_var.set(config.get('channel', ''))
                    self.sheets_var.set(config.get('sheets_url', ''))
                    self.tab_var.set(config.get('tab_name', 'YouTube Videos'))
        except Exception as e:
            self.log_message(f"Error loading config: {str(e)}")
            
    def save_config(self):
        """Save configuration to file."""
        try:
            config = {
                'channel': self.channel_var.get(),
                'sheets_url': self.sheets_var.get(),
                'tab_name': self.tab_var.get()
            }
            with open('gui_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            self.log_message("Configuration saved successfully!")
        except Exception as e:
            self.log_message(f"Error saving config: {str(e)}")
            
    def show_about(self):
        """Show about dialog."""
        about_text = """YouTube to Google Sheets Automation Tool
Version 2.0

This tool automatically syncs YouTube channel videos to Google Sheets.

Features:
• Extract video data from YouTube channels
• Write data to Google Sheets
• Filter videos by duration and keywords
• Modern, user-friendly interface

For support, please check the documentation."""
        
        messagebox.showinfo("About", about_text)
        
    def run(self):
        """Start the GUI application."""
        self.log_message("YouTube to Google Sheets Automation Tool started")
        self.log_message("Please configure your settings and click 'Sync to Sheets'")
        self.root.mainloop()

def main():
    """Main entry point."""
    app = YouTube2SheetsGUI()
    app.run()

if __name__ == "__main__":
    main()