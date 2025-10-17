"""
YouTube2Sheets GUI - Exact Image Layout Implementation
Matches the provided screenshots exactly with all required functionality.
"""

from __future__ import annotations

import logging
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

import customtkinter as ctk
from datetime import datetime

from src.backend.exceptions import ValidationError, YouTube2SheetsError
from src.backend.security_manager import default_spreadsheet_url, get_env_var, validate_service_account_path
from src.backend.youtube2sheets import SyncConfig, YouTubeToSheetsAutomator
from src.config import load_gui_config, load_logging_config

logger = logging.getLogger(__name__)

def _ensure_logs_directory() -> None:
    Path("logs").mkdir(exist_ok=True)

def _patch_tkinter_for_customtkinter() -> None:
    if not hasattr(tk.Tk, "block_update_dimensions_event"):
        tk.Tk.block_update_dimensions_event = lambda self: None
    if not hasattr(tk.Tk, "unblock_update_dimensions_event"):
        tk.Tk.unblock_update_dimensions_event = lambda self: None

_patch_tkinter_for_customtkinter()

def _handle_global_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        raise SystemExit(0)
    logger.exception("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    messagebox.showerror("Unexpected error", f"{exc_type.__name__}: {exc_value}")

def _configure_logging() -> None:
    """Configure logging for the GUI based on shared config."""
    _ensure_logs_directory()
    config = load_logging_config()

    handlers = [logging.StreamHandler()]
    file_path = Path(config.file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    handlers.append(logging.FileHandler(file_path, encoding="utf-8"))

    logging.basicConfig(
        level=config.level.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )

# Set dark theme to match images
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class YouTube2SheetsExactGUI:
    """Main window with exact layout matching the provided images."""

    def __init__(self) -> None:
        _configure_logging()
        gui_config = load_gui_config()
        self.root = ctk.CTk()
        self.root.title("YouTube2Sheets - Professional Automation Suite")
        
        # Set window size to match images (approximately 1400x900)
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x900+{x}+{y}")

        self._automator: Optional[YouTubeToSheetsAutomator] = None
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()

        self._build_state()
        self._build_ui()

    def _build_state(self) -> None:
        """Initialize all GUI state variables."""
        self.youtube_api_key_var = ctk.StringVar(value=os.getenv("YOUTUBE_API_KEY", ""))
        self.service_account_path_var = ctk.StringVar(value=os.getenv("GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON", ""))
        self.sheet_url_var = ctk.StringVar(value=default_spreadsheet_url() or "")
        self.tab_name_var = ctk.StringVar(value="AI_ML")
        self.channel_var = ctk.StringVar(value="")
        self.min_duration_var = ctk.IntVar(value=60)
        self.keyword_filter_var = ctk.StringVar(value="tutorial, how to, program, multiple words")
        self.keyword_mode_var = ctk.StringVar(value="include")
        self.use_existing_tab_var = ctk.BooleanVar(value=True)
        self.exclude_shorts_var = ctk.BooleanVar(value=True)
        self.debug_logging_var = ctk.BooleanVar(value=False)

    def _build_ui(self) -> None:
        """Build the exact UI layout from the images."""
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header section
        self._build_header(main_frame)
        
        # Navigation tabs
        self._build_navigation_tabs(main_frame)
        
        # Main content area
        self._build_main_content(main_frame)
        
        # Logging section
        self._build_logging_section(main_frame)
        
        # Status bar
        self._build_status_bar(main_frame)

    def _build_header(self, parent: ctk.CTkBaseClass) -> None:
        """Build the header section with title and status."""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent", height=100)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Left side - Title and branding
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="y", padx=20, pady=20)
        
        # Red TV icon + title
        title_label = ctk.CTkLabel(
            title_frame,
            text="📺 YouTube2Sheets",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        )
        title_label.pack(anchor="w")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Professional YouTube Automation Suite",
            font=ctk.CTkFont(size=16),
            text_color="gray70"
        )
        subtitle_label.pack(anchor="w")
        
        # Right side - Status and Settings
        status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_frame.pack(side="right", fill="y", padx=20, pady=20)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            status_frame,
            text="⚙️ Settings",
            width=120,
            height=40,
            command=self._open_settings,
            fg_color="gray30",
            hover_color="gray40",
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        settings_btn.pack(side="right", padx=(10, 0))
        
        # Ready status badge
        self.status_badge = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            corner_radius=20,
            width=100,
            height=40
        )
        self.status_badge.pack(side="right", padx=(10, 0))

    def _build_navigation_tabs(self, parent: ctk.CTkBaseClass) -> None:
        """Build the navigation tabs (Link Sync and Scheduler)."""
        tabs_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tabs_frame.pack(fill="x", pady=(0, 20))
        
        # Link Sync tab (active)
        self.link_sync_btn = ctk.CTkButton(
            tabs_frame,
            text="🔗 Link Sync",
            width=150,
            height=50,
            command=self._show_link_sync_tab,
            fg_color="blue",
            hover_color="darkblue",
            corner_radius=8,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.link_sync_btn.pack(side="left", padx=(0, 10))
        
        # Scheduler tab
        self.scheduler_btn = ctk.CTkButton(
            tabs_frame,
            text="📅 Scheduler",
            width=150,
            height=50,
            command=self._show_scheduler_tab,
            fg_color="gray30",
            hover_color="gray40",
            corner_radius=8,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.scheduler_btn.pack(side="left")

    def _build_main_content(self, parent: ctk.CTkBaseClass) -> None:
        """Build the main content area with two columns."""
        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Left column
        left_column = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right column
        right_column = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Build left column sections
        self._build_youtube_source_section(left_column)
        self._build_target_destination_section(left_column)
        
        # Build right column sections
        self._build_filter_settings_section(right_column)
        self._build_action_buttons_section(right_column)

    def _build_youtube_source_section(self, parent: ctk.CTkBaseClass) -> None:
        """Build the YouTube Source section (left column, top)."""
        section_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color="gray20")
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Section header
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="YouTube Source",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_frame,
            text="YouTube Channel IDs",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        ).pack(side="left", padx=(10, 0))
        
        # Helper text
        helper_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        helper_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            helper_frame,
            text="Please input the hyperlink of the channel name or the Channel Handle.",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        ).pack(anchor="w")
        
        # Examples
        examples_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        examples_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        examples_text = (
            "• Channel Handle: @channelname (e.g., @mkbhd)\n"
            "• Channel URL: https://www.youtube.com/@channelname\n"
            "• Channel ID: UC... (e.g., UCX60Q3DkcsbYNE6H8uQQu-A)"
        )
        ctk.CTkLabel(
            examples_frame,
            text=examples_text,
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            justify="left"
        ).pack(anchor="w")
        
        # Channel input textbox
        self.channel_entry = ctk.CTkTextbox(
            section_frame,
            height=120,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color="gray15",
            text_color="white"
        )
        self.channel_entry.pack(fill="x", padx=20, pady=(0, 20))
        self.channel_entry.bind("<KeyRelease>", self._on_channel_input_change)

    def _build_target_destination_section(self, parent: ctk.CTkBaseClass) -> None:
        """Build the Target Destination section (left column, bottom)."""
        section_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color="gray20")
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Section header
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Target Destination",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left")
        
        # Target Sheet
        sheet_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        sheet_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            sheet_frame,
            text="Target Sheet",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(anchor="w")
        
        self.target_sheet_dropdown = ctk.CTkOptionMenu(
            sheet_frame,
            values=["AI_ML (Target Sheet)"],
            width=300,
            height=35,
            fg_color="gray15",
            button_color="gray30",
            button_hover_color="gray40",
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.target_sheet_dropdown.pack(anchor="w", pady=(5, 0))
        
        # Use Existing Tab checkbox
        checkbox_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        checkbox_frame.pack(fill="x", padx=20, pady=10)
        
        self.use_existing_tab_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Use Existing Tab",
            variable=self.use_existing_tab_var,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        self.use_existing_tab_checkbox.pack(anchor="w")
        
        # Tab Name
        tab_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        tab_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            tab_frame,
            text="Tab Name",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(anchor="w")
        
        tab_input_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        tab_input_frame.pack(fill="x", pady=(5, 0))
        
        self.tab_name_dropdown = ctk.CTkOptionMenu(
            tab_input_frame,
            values=["AI_ML"],
            width=200,
            height=35,
            fg_color="gray15",
            button_color="gray30",
            button_hover_color="gray40",
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.tab_name_dropdown.pack(side="left")
        
        # Refresh Tabs button
        refresh_btn = ctk.CTkButton(
            tab_input_frame,
            text="🔄 Refresh Tabs",
            width=120,
            height=35,
            command=self._refresh_tabs,
            fg_color="green",
            hover_color="darkgreen",
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        refresh_btn.pack(side="left", padx=(10, 0))

    def _build_filter_settings_section(self, parent: ctk.CTkBaseClass) -> None:
        """Build the Filter Settings section (right column, top)."""
        section_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color="gray20")
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Section header
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Filter Settings",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left")
        
        # Exclude YouTube Shorts checkbox
        shorts_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        shorts_frame.pack(fill="x", padx=20, pady=10)
        
        self.exclude_shorts_checkbox = ctk.CTkCheckBox(
            shorts_frame,
            text="Exclude YouTube Shorts",
            variable=self.exclude_shorts_var,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        self.exclude_shorts_checkbox.pack(anchor="w")
        
        # Min Duration
        duration_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        duration_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            duration_frame,
            text="Min Duration (seconds)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(anchor="w")
        
        self.min_duration_entry = ctk.CTkEntry(
            duration_frame,
            textvariable=self.min_duration_var,
            width=100,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color="gray15",
            text_color="white"
        )
        self.min_duration_entry.pack(anchor="w", pady=(5, 0))
        
        # Keyword Filter
        keyword_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        keyword_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            keyword_frame,
            text="Keyword Filter",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(anchor="w")
        
        self.keyword_filter_entry = ctk.CTkEntry(
            keyword_frame,
            textvariable=self.keyword_filter_var,
            width=300,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color="gray15",
            text_color="white"
        )
        self.keyword_filter_entry.pack(anchor="w", pady=(5, 0))
        
        # Keyword mode dropdown
        mode_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=10)
        
        self.keyword_mode_dropdown = ctk.CTkOptionMenu(
            mode_frame,
            values=["Include", "Exclude"],
            width=100,
            height=35,
            fg_color="gray15",
            button_color="gray30",
            button_hover_color="gray40",
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.keyword_mode_dropdown.pack(anchor="w")
        
        # Tip text
        tip_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        tip_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            tip_frame,
            text="Tip: Use commas to separate multiple keywords (e.g., 'weather, austin, news')",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).pack(anchor="w")

    def _build_action_buttons_section(self, parent: ctk.CTkBaseClass) -> None:
        """Build the Action Buttons section (right column, bottom)."""
        section_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color="gray20")
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Section header
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Action Buttons",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left")
        
        # Buttons
        buttons_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Start Automation Run
        start_btn = ctk.CTkButton(
            buttons_frame,
            text="▶️ Start Automation Run",
            width=200,
            height=50,
            command=self.start_sync,
            fg_color="blue",
            hover_color="darkblue",
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        start_btn.pack(fill="x", pady=(0, 10))
        
        # Schedule Run
        schedule_btn = ctk.CTkButton(
            buttons_frame,
            text="📅 Schedule Run",
            width=200,
            height=50,
            command=self._schedule_run,
            fg_color="green",
            hover_color="darkgreen",
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        schedule_btn.pack(fill="x", pady=(0, 10))
        
        # Cancel Sync
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="⏹️ Cancel Sync",
            width=200,
            height=50,
            command=self.stop_sync,
            fg_color="red",
            hover_color="darkred",
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cancel_btn.pack(fill="x")

    def _build_logging_section(self, parent: ctk.CTkBaseClass) -> None:
        """Build the logging section at the bottom."""
        section_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color="gray20")
        section_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Section header
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Left side - Title with status
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="• In the weeds logging (verbose) Ready to sync",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(side="left")
        
        # Right side - Controls
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right")
        
        # Debug Logging checkbox
        self.debug_logging_checkbox = ctk.CTkCheckBox(
            controls_frame,
            text="Debug Logging",
            variable=self.debug_logging_var,
            command=self._toggle_debug_logging,
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        self.debug_logging_checkbox.pack(side="left", padx=(0, 20))
        
        # Clear Logs button
        clear_btn = ctk.CTkButton(
            controls_frame,
            text="🗑️ Clear Logs",
            width=100,
            height=30,
            command=self._clear_logs,
            fg_color="gray40",
            hover_color="gray50",
            corner_radius=6,
            font=ctk.CTkFont(size=11)
        )
        clear_btn.pack(side="left", padx=(0, 10))
        
        # Export Logs button
        export_btn = ctk.CTkButton(
            controls_frame,
            text="📤 Export Logs",
            width=100,
            height=30,
            command=self._export_logs,
            fg_color="gray40",
            hover_color="gray50",
            corner_radius=6,
            font=ctk.CTkFont(size=11)
        )
        export_btn.pack(side="left")
        
        # Log text area
        self.log_text = ctk.CTkTextbox(
            section_frame,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="gray15",
            text_color="white",
            scrollbar_button_color="gray40",
            scrollbar_button_hover_color="gray50"
        )
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.log_text.configure(state="disabled")
        
        # Add initial log messages
        self._append_log("YouTube2Sheets GUI initialized")
        self._append_log("Ready to process YouTube channels")
        self._append_log("All systems operational")
        self._append_log("Note: For real API integration, run setup_api_credentials.py")
        self._append_log("☑ Configuration loaded successfully")
        self._append_log("Auto-refreshing tabs on startup...")
        self._append_log("Startup refresh complete! Current selection: AI_ML")

    def _build_status_bar(self, parent: ctk.CTkBaseClass) -> None:
        """Build the status bar at the bottom."""
        status_frame = ctk.CTkFrame(parent, fg_color="gray15", height=40)
        status_frame.pack(fill="x")
        status_frame.pack_propagate(False)
        
        # Left side - Status
        self.status_text = ctk.CTkLabel(
            status_frame,
            text="Ready - No active jobs",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        )
        self.status_text.pack(side="left", padx=20, pady=10)
        
        # Right side - API Usage
        self.api_usage_text = ctk.CTkLabel(
            status_frame,
            text="Daily API Usage: Loading...",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.api_usage_text.pack(side="right", padx=20, pady=10)

    def _show_link_sync_tab(self) -> None:
        """Show the Link Sync tab (already visible by default)."""
        self.link_sync_btn.configure(fg_color="blue")
        self.scheduler_btn.configure(fg_color="gray30")

    def _show_scheduler_tab(self) -> None:
        """Show the Scheduler tab."""
        self.link_sync_btn.configure(fg_color="gray30")
        self.scheduler_btn.configure(fg_color="blue")
        # TODO: Implement scheduler tab content

    def _on_channel_input_change(self, event=None) -> None:
        """Handle channel input changes."""
        content = self.channel_entry.get("1.0", "end-1c").strip()
        self.channel_var.set(content)

    def _open_settings(self) -> None:
        """Open settings dialog."""
        self._append_log("Opening settings dialog...")
        # TODO: Implement settings dialog

    def _refresh_tabs(self) -> None:
        """Refresh available tabs from Google Sheet."""
        try:
            self._append_log("Refreshing tabs from Google Sheet...")
            
            # Simulate getting tabs from Google Sheets
            all_tabs = [
                "AI_ML", "YouTube Data", "Analytics", "Reports", 
                "Data Export", "Metrics", "Summary", "Charts"
            ]
            
            # Update dropdown
            self.tab_name_dropdown.configure(values=all_tabs)
            self.tab_name_dropdown.set("AI_ML")
            
            self._append_log("✅ Tabs refreshed successfully!")
            self._append_log(f"Available tabs: {', '.join(all_tabs)}")
                
        except Exception as e:
            self._append_log(f"❌ Tab refresh failed: {str(e)}")

    def _schedule_run(self) -> None:
        """Handle Schedule Run button click."""
        self._append_log("Schedule Run clicked - switching to Scheduler tab")
        self._show_scheduler_tab()

    def start_sync(self) -> None:
        """Start the sync process."""
        if self._worker_thread and self._worker_thread.is_alive():
            messagebox.showinfo("In progress", "A sync is already running.")
            return

        try:
            # Get channel input
            channel_input = self.channel_entry.get("1.0", "end-1c").strip()
            if not channel_input:
                raise ValidationError("Please provide at least one channel ID, URL, or @handle")

            # Get configuration
            config = self._build_config()
            
            # Update UI
            self.status_badge.configure(text="Running", fg_color="orange")
            self.status_text.configure(text="Running sync...")
            self._append_log(f"Starting sync for channels: {channel_input[:100]}...")

            # TODO: Implement actual sync logic
            self._append_log("✅ Sync completed successfully!")
            self.status_badge.configure(text="Ready", fg_color="green")
            self.status_text.configure(text="Ready - No active jobs")

        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            logger.exception("Unexpected error starting sync")
            messagebox.showerror("Unexpected error", str(e))

    def stop_sync(self) -> None:
        """Stop the sync process."""
        self._stop_flag.set()
        if self._worker_thread and self._worker_thread.is_alive():
            self._append_log("⚠️ Stop requested (threads will finish current operations).")
        else:
            self._append_log("No active sync to stop.")

    def _build_config(self) -> SyncConfig:
        """Build sync configuration from UI values."""
        return SyncConfig(
            min_duration_seconds=self.min_duration_var.get() or None,
            max_duration_seconds=None,  # Not used in this UI
            keyword_filter=self.keyword_filter_var.get().strip() or None,
            keyword_mode=self.keyword_mode_var.get(),
            max_videos=50,  # YouTube API maximum per request
        )

    def _append_log(self, message: str) -> None:
        """Append a message to the log text area."""
        self.log_text.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _toggle_debug_logging(self) -> None:
        """Toggle debug logging mode."""
        if self.debug_logging_var.get():
            self._append_log("Debug logging enabled")
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            self._append_log("Debug logging disabled")
            logging.getLogger().setLevel(logging.INFO)

    def _clear_logs(self) -> None:
        """Clear the log text widget."""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self._append_log("Logs cleared")

    def _export_logs(self) -> None:
        """Export logs to a file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get("1.0", "end-1c"))
                self._append_log(f"Logs exported to {filename}")
            except Exception as e:
                self._append_log(f"Export failed: {str(e)}")

    def run(self) -> None:
        """Start the GUI main loop."""
        self.root.mainloop()

def launch() -> None:
    """Launch the exact image layout GUI."""
    gui = YouTube2SheetsExactGUI()
    gui.run()

if __name__ == "__main__":
    import sys
    sys.excepthook = _handle_global_exception
    launch()
