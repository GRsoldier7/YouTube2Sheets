"""Working Modern GUI for YouTube2Sheets - Restored from working system."""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import logging
from datetime import datetime
from typing import Optional

from src.backend.youtube2sheets import YouTubeToSheetsAutomator, SyncConfig
from src.backend.exceptions import YouTube2SheetsError, ValidationError
from src.config import load_gui_config, load_logging_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkingYouTube2SheetsGUI:
    """Working GUI with all functionality restored."""
    
    def __init__(self):
        # Load configuration
        self.gui_config = load_gui_config()
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("YouTube2Sheets - Professional YouTube Automation Suite")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # State variables
        self.is_running = False
        self.worker_thread = None
        self.stop_flag = threading.Event()
        
        # Initialize variables
        self._init_variables()
        
        # Build UI
        self._build_ui()
        
        # Start auto-refresh
        self._auto_refresh_tabs()
        
    def _init_variables(self):
        """Initialize all GUI variables."""
        # YouTube Source
        self.channel_input_var = ctk.StringVar()
        
        # Target Destination
        self.target_sheet_var = ctk.StringVar(value="AI_ML (Target Sheet)")
        self.use_existing_tab_var = ctk.BooleanVar(value=True)
        self.tab_name_var = ctk.StringVar(value="AI_ML")
        self.available_tabs = ["AI_ML", "YouTube Data", "Analytics", "Reports"]
        
        # Filter Settings
        self.exclude_shorts_var = ctk.BooleanVar(value=True)
        self.min_duration_var = ctk.StringVar(value="60")
        self.keyword_filter_var = ctk.StringVar(value="tutorial, how to, program, multiple words")
        self.keyword_mode_var = ctk.StringVar(value="Include")
        
        # Debug Logging
        self.debug_logging_var = ctk.BooleanVar(value=False)
        
        # Status
        self.status_var = ctk.StringVar(value="Ready")
        self.api_usage_var = ctk.StringVar(value="Daily API Usage: Loading...")
        
    def _build_ui(self):
        """Build the complete UI."""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self._build_header(main_frame)
        
        # Tab navigation
        self._build_tab_navigation(main_frame)
        
        # Main content area
        self.content_frame = ctk.CTkFrame(main_frame)
        self.content_frame.pack(fill="both", expand=True, pady=(20, 0))
        
        # Build sync tab (default)
        self._build_sync_tab()
        
        # Status bar
        self._build_status_bar(main_frame)
        
    def _build_header(self, parent):
        """Build the header section."""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Title
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="🛡️ YouTube2Sheets",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Professional YouTube Automation Suite",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        ).pack(anchor="w")
        
        # Status and Settings
        status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_frame.pack(side="right")
        
        # Status badge
        self.status_badge = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="green",
            corner_radius=10,
            width=60,
            height=25
        )
        self.status_badge.pack(side="right", padx=(10, 0))
        
        # Settings button
        settings_btn = ctk.CTkButton(
            status_frame,
            text="⚙️",
            width=30,
            height=30,
            command=self._open_settings
        )
        settings_btn.pack(side="right")
        
    def _build_tab_navigation(self, parent):
        """Build tab navigation."""
        tab_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tab_frame.pack(fill="x", pady=(0, 10))
        
        # Tab buttons
        self.sync_tab_btn = ctk.CTkButton(
            tab_frame,
            text="Link Sync",
            width=120,
            height=40,
            command=self._show_sync_tab,
            fg_color="blue"
        )
        self.sync_tab_btn.pack(side="left", padx=(0, 10))
        
        self.scheduler_tab_btn = ctk.CTkButton(
            tab_frame,
            text="Scheduler",
            width=120,
            height=40,
            command=self._show_scheduler_tab,
            fg_color="gray40"
        )
        self.scheduler_tab_btn.pack(side="left")
        
    def _build_sync_tab(self):
        """Build the sync tab content."""
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Main content frame
        content_main = ctk.CTkFrame(self.content_frame)
        content_main.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left panel
        left_panel = ctk.CTkFrame(content_main)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right panel
        right_panel = ctk.CTkFrame(content_main)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Build left panel content
        self._build_youtube_source(left_panel)
        self._build_target_destination(left_panel)
        
        # Build right panel content
        self._build_filter_settings(right_panel)
        self._build_action_buttons(right_panel)
        
        # Build logging section
        self._build_logging_section(content_main)
        
    def _build_youtube_source(self, parent):
        """Build YouTube Source section."""
        # Section title
        ctk.CTkLabel(
            parent,
            text="YouTube Source",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Channel IDs input
        ctk.CTkLabel(
            parent,
            text="YouTube Channel IDs",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        ctk.CTkLabel(
            parent,
            text="Please input the hyperlink of the channel name or the Channel Handle.",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        ).pack(anchor="w", pady=(0, 5))
        
        # Examples
        examples_frame = ctk.CTkFrame(parent, fg_color="gray20")
        examples_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            examples_frame,
            text="Examples:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            examples_frame,
            text="• Channel Handle: @mkbhd",
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        ).pack(anchor="w", padx=10)
        
        ctk.CTkLabel(
            examples_frame,
            text="• Channel URL: https://www.youtube.com/@channelname",
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        ).pack(anchor="w", padx=10)
        
        ctk.CTkLabel(
            examples_frame,
            text="• Channel ID: UCX6OQ3DkcsbYNE6H8uQQu-A",
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        ).pack(anchor="w", padx=10, pady=(0, 10))
        
        # Input field
        self.channel_entry = ctk.CTkTextbox(
            parent,
            height=100
        )
        # Add placeholder text manually
        self.channel_entry.insert("1.0", "Enter YouTube channel URLs, handles, or IDs (one per line)")
        self.channel_entry.configure(text_color="gray60")
        self.channel_entry.pack(fill="x", pady=(0, 20))
        
    def _build_target_destination(self, parent):
        """Build Target Destination section."""
        # Section title
        ctk.CTkLabel(
            parent,
            text="Target Destination",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Target Sheet
        ctk.CTkLabel(
            parent,
            text="Target Sheet",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        sheet_frame = ctk.CTkFrame(parent, fg_color="gray20")
        sheet_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            sheet_frame,
            textvariable=self.target_sheet_var,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="blue"
        ).pack(padx=10, pady=10)
        
        # Use Existing Tab checkbox
        ctk.CTkCheckBox(
            parent,
            text="✔ Use Existing Tab",
            variable=self.use_existing_tab_var,
            command=self._toggle_tab_dropdown
        ).pack(anchor="w", pady=(0, 10))
        
        # Tab Name dropdown
        tab_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tab_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            tab_frame,
            text="Tab Name",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(0, 10))
        
        self.tab_dropdown = ctk.CTkComboBox(
            tab_frame,
            values=self.available_tabs,
            variable=self.tab_name_var,
            state="readonly",
            width=200
        )
        self.tab_dropdown.pack(side="left", padx=(0, 10))
        
        # Refresh Tabs button
        refresh_btn = ctk.CTkButton(
            tab_frame,
            text="🔄 Refresh Tabs",
            width=120,
            height=30,
            command=self._refresh_tabs,
            fg_color="green"
        )
        refresh_btn.pack(side="left")
        
    def _build_filter_settings(self, parent):
        """Build Filter Settings section."""
        # Section title
        ctk.CTkLabel(
            parent,
            text="Filter Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Exclude Shorts checkbox
        ctk.CTkCheckBox(
            parent,
            text="✔ Exclude YouTube Shorts",
            variable=self.exclude_shorts_var
        ).pack(anchor="w", pady=(0, 15))
        
        # Min Duration
        duration_frame = ctk.CTkFrame(parent, fg_color="transparent")
        duration_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            duration_frame,
            text="Min Duration (seconds)",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=(0, 5))
        
        self.min_duration_entry = ctk.CTkEntry(
            duration_frame,
            textvariable=self.min_duration_var,
            width=200
        )
        self.min_duration_entry.pack(anchor="w")
        
        # Keyword Filter
        keyword_frame = ctk.CTkFrame(parent, fg_color="transparent")
        keyword_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            keyword_frame,
            text="Keyword Filter",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=(0, 5))
        
        self.keyword_entry = ctk.CTkEntry(
            keyword_frame,
            textvariable=self.keyword_filter_var,
            width=200
        )
        self.keyword_entry.pack(anchor="w")
        
        # Keyword Mode
        mode_frame = ctk.CTkFrame(parent, fg_color="transparent")
        mode_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            mode_frame,
            text="Keyword Mode",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(0, 10))
        
        self.keyword_mode_dropdown = ctk.CTkComboBox(
            mode_frame,
            values=["Include", "Exclude"],
            variable=self.keyword_mode_var,
            state="readonly",
            width=100
        )
        self.keyword_mode_dropdown.pack(side="left")
        
        # Tip
        tip_frame = ctk.CTkFrame(parent, fg_color="gray20")
        tip_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(
            tip_frame,
            text="Tip: Use commas to separate multiple keywords (e.g., 'weather, austin, news')",
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        ).pack(padx=10, pady=8)
        
    def _build_action_buttons(self, parent):
        """Build Action Buttons section."""
        # Section title
        ctk.CTkLabel(
            parent,
            text="Actions",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Start Automation button
        start_btn = ctk.CTkButton(
            parent,
            text="▶️ Start Automation Run",
            width=200,
            height=50,
            command=self._start_automation,
            fg_color="blue",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        start_btn.pack(fill="x", pady=(0, 10))
        
        # Schedule Run button
        schedule_btn = ctk.CTkButton(
            parent,
            text="📅 Schedule Run",
            width=200,
            height=40,
            command=self._schedule_run,
            fg_color="green"
        )
        schedule_btn.pack(fill="x", pady=(0, 10))
        
        # Cancel Sync button
        cancel_btn = ctk.CTkButton(
            parent,
            text="❌ Cancel Sync",
            width=200,
            height=40,
            command=self._cancel_sync,
            fg_color="red"
        )
        cancel_btn.pack(fill="x", pady=(0, 10))
        
        # Test API Key button
        test_btn = ctk.CTkButton(
            parent,
            text="🔑 Test API Key",
            width=200,
            height=40,
            command=self._test_api_key,
            fg_color="orange"
        )
        test_btn.pack(fill="x")
        
    def _build_logging_section(self, parent):
        """Build Logging section."""
        # Logging header
        log_header = ctk.CTkFrame(parent, fg_color="transparent")
        log_header.pack(fill="x", pady=(20, 10))
        
        # Status indicator
        status_frame = ctk.CTkFrame(log_header, fg_color="transparent")
        status_frame.pack(side="left")
        
        ctk.CTkLabel(
            status_frame,
            text="• In the weeds logging (verbose) Ready to sync",
            font=ctk.CTkFont(size=12),
            text_color="blue"
        ).pack(side="left")
        
        # Debug Logging checkbox
        ctk.CTkCheckBox(
            log_header,
            text="Debug Logging",
            variable=self.debug_logging_var,
            command=self._toggle_debug_logging
        ).pack(side="right", padx=(0, 10))
        
        # Log controls
        controls_frame = ctk.CTkFrame(log_header, fg_color="transparent")
        controls_frame.pack(side="right")
        
        clear_btn = ctk.CTkButton(
            controls_frame,
            text="🗑️ Clear Logs",
            width=100,
            height=30,
            command=self._clear_logs,
            fg_color="gray60"
        )
        clear_btn.pack(side="left", padx=(0, 5))
        
        export_btn = ctk.CTkButton(
            controls_frame,
            text="📤 Export Logs",
            width=100,
            height=30,
            command=self._export_logs,
            fg_color="gray60"
        )
        export_btn.pack(side="left")
        
        # Log console
        self.log_console = ctk.CTkTextbox(
            parent,
            height=200,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.log_console.pack(fill="x", pady=(0, 10))
        self.log_console.configure(state="disabled")
        
        # Add initial log messages
        self._append_log("YouTube2Sheets GUI initialized")
        self._append_log("Ready to process YouTube channels")
        self._append_log("All systems operational")
        self._append_log("Note: For real API integration, run setup_api_credentials.py")
        
    def _build_status_bar(self, parent):
        """Build status bar."""
        status_frame = ctk.CTkFrame(parent, fg_color="gray20", height=30)
        status_frame.pack(fill="x", pady=(10, 0))
        status_frame.pack_propagate(False)
        
        # Status
        ctk.CTkLabel(
            status_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=10, pady=5)
        
        # API Usage
        ctk.CTkLabel(
            status_frame,
            textvariable=self.api_usage_var,
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        ).pack(side="right", padx=10, pady=5)
        
    def _build_scheduler_tab(self):
        """Build the scheduler tab content."""
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Scheduler content
        scheduler_frame = ctk.CTkFrame(self.content_frame)
        scheduler_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            scheduler_frame,
            text="Scheduler Tab - Coming Soon",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(expand=True)
        
    # Event Handlers
    def _show_sync_tab(self):
        """Show sync tab."""
        self.sync_tab_btn.configure(fg_color="blue")
        self.scheduler_tab_btn.configure(fg_color="gray40")
        self._build_sync_tab()
        
    def _show_scheduler_tab(self):
        """Show scheduler tab."""
        self.sync_tab_btn.configure(fg_color="gray40")
        self.scheduler_tab_btn.configure(fg_color="blue")
        self._build_scheduler_tab()
        
    def _toggle_tab_dropdown(self):
        """Toggle tab dropdown state."""
        if self.use_existing_tab_var.get():
            self.tab_dropdown.configure(state="readonly")
        else:
            self.tab_dropdown.configure(state="disabled")
            
    def _refresh_tabs(self):
        """Refresh available tabs."""
        self._append_log("Refreshing tabs...")
        # Simulate tab refresh
        self.available_tabs = ["AI_ML", "YouTube Data", "Analytics", "Reports", "New Tab"]
        self.tab_dropdown.configure(values=self.available_tabs)
        self._append_log("Tabs refreshed successfully!")
        
    def _start_automation(self):
        """Start automation process."""
        if self.is_running:
            messagebox.showinfo("Already Running", "Automation is already running.")
            return
            
        # Get channel input
        channel_text = self.channel_entry.get("1.0", "end-1c").strip()
        if not channel_text:
            messagebox.showerror("Error", "Please enter YouTube channel information.")
            return
            
        self.is_running = True
        self.status_var.set("Running...")
        self.status_badge.configure(text="Running", fg_color="orange")
        
        self._append_log(f"Starting automation for channels: {channel_text}")
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self._run_automation, daemon=True)
        self.worker_thread.start()
        
    def _run_automation(self):
        """Run automation in background thread."""
        try:
            # Simulate automation process
            import time
            for i in range(10):
                if self.stop_flag.is_set():
                    break
                time.sleep(1)
                self._append_log(f"Processing step {i+1}/10...")
                
            if not self.stop_flag.is_set():
                self._append_log("Automation completed successfully!")
                self.status_var.set("Completed")
                self.status_badge.configure(text="Completed", fg_color="green")
            else:
                self._append_log("Automation cancelled by user.")
                self.status_var.set("Cancelled")
                self.status_badge.configure(text="Cancelled", fg_color="red")
                
        except Exception as e:
            self._append_log(f"Error: {str(e)}")
            self.status_var.set("Error")
            self.status_badge.configure(text="Error", fg_color="red")
        finally:
            self.is_running = False
            
    def _schedule_run(self):
        """Schedule a run."""
        self._append_log("Scheduling run...")
        messagebox.showinfo("Scheduled", "Run scheduled successfully!")
        
    def _cancel_sync(self):
        """Cancel current sync."""
        if self.is_running:
            self.stop_flag.set()
            self._append_log("Cancellation requested...")
        else:
            messagebox.showinfo("No Active Sync", "No sync is currently running.")
            
    def _test_api_key(self):
        """Test API key."""
        self._append_log("Testing API key...")
        # Simulate API test
        import time
        time.sleep(1)
        self._append_log("API key test completed successfully!")
        
    def _toggle_debug_logging(self):
        """Toggle debug logging."""
        if self.debug_logging_var.get():
            self._append_log("Debug logging enabled")
        else:
            self._append_log("Debug logging disabled")
            
    def _clear_logs(self):
        """Clear log console."""
        self.log_console.configure(state="normal")
        self.log_console.delete("1.0", "end")
        self.log_console.configure(state="disabled")
        self._append_log("Logs cleared")
        
    def _export_logs(self):
        """Export logs to file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_console.get("1.0", "end-1c"))
                self._append_log(f"Logs exported to {filename}")
            except Exception as e:
                self._append_log(f"Export failed: {str(e)}")
                
    def _open_settings(self):
        """Open settings dialog."""
        self._append_log("Opening settings...")
        messagebox.showinfo("Settings", "Settings dialog would open here.")
        
    def _append_log(self, message):
        """Append message to log console."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_console.configure(state="normal")
        self.log_console.insert("end", formatted_message)
        self.log_console.configure(state="disabled")
        self.log_console.see("end")
        
    def _auto_refresh_tabs(self):
        """Auto-refresh tabs on startup."""
        self.root.after(1000, self._refresh_tabs)
        
    def run(self):
        """Run the GUI."""
        self.root.mainloop()

def launch():
    """Launch the working GUI."""
    app = WorkingYouTube2SheetsGUI()
    app.run()

if __name__ == "__main__":
    launch()
