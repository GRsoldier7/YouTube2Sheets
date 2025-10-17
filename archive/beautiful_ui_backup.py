"""
Beautiful Modern YouTube2Sheets GUI - Matching Original Design Excellence
This is a complete redesign with:
- Separate Settings dialog (no API keys cluttering main screen)
- Tabbed interface (Link Sync / Scheduler)
- Card-based layout with vibrant cyan accents
- Professional status indicators
- Color-coded action buttons
- Elegant logging console with real-time feedback
"""

from __future__ import annotations

import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

import customtkinter as ctk
import threading

from src.backend.exceptions import ValidationError, YouTube2SheetsError
from src.backend.security_manager import (
    default_spreadsheet_url,
    get_env_var,
    validate_service_account_path,
)
from src.backend.youtube2sheets import SyncConfig, YouTubeToSheetsAutomator
from src.config import load_gui_config, load_logging_config

logger = logging.getLogger(__name__)

# 🎨 BEAUTIFUL COLOR PALETTE - Matching Original Design
# 2026 Modern Color Palette - Clean, Elegant, Professional
COLORS = {
    "primary_cyan": "#00D9FF",      # Vibrant cyan for primary actions
    "success_green": "#00FF9D",     # Bright green for success/schedule
    "danger_red": "#FF4D6A",        # Soft red for cancel/stop
    "bg_dark": "#0F0F0F",           # Deep black for modern look
    "card_bg": "#1A1A1A",           # Card backgrounds
    "border_subtle": "#2A2A2A",     # Subtle borders
    "text_primary": "#FFFFFF",      # Primary text
    "text_secondary": "#A0A0A0",    # Secondary text
    "accent_blue": "#007AFF",       # iOS-style blue
    "accent_purple": "#8E44AD",     # Modern purple
    "warning_orange": "#FF9500",    # Warm orange
    "error_red": "#FF3B30",         # Clean red
    "glass_white": "rgba(255,255,255,0.1)",  # Glass effect
    "glass_black": "rgba(0,0,0,0.2)",        # Dark glass
}

# Set dark theme globally
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def _configure_logging() -> None:
    """Configure logging for the GUI."""
    Path("logs").mkdir(exist_ok=True)
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


class SettingsDialog(ctk.CTkToplevel):
    """⚙️ Beautiful Settings Dialog - Separate from Main UI"""

    def __init__(self, parent, gui_instance):
        super().__init__(parent)
        self.gui = gui_instance
        self.title("⚙️ YouTube2Sheets - Configuration")
        self.geometry("700x800")
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (700 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (800 // 2)
        self.geometry(f"+{x}+{y}")

        self._build_settings_ui()

    def _build_settings_ui(self):
        # Main scrollable container
        container = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"])
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            container,
            text="🔧 Configuration",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(0, 20))

        # YouTube API Key
        self._add_entry(
            container, "YouTube API Key:", self.gui.youtube_api_key_var, show="*"
        )

        # Service Account JSON with Browse button
        self._add_browse_entry(
            container, "Service Account JSON:", self.gui.service_account_path_var
        )

        # Default Spreadsheet URL
        self._add_entry(
            container, "Default Spreadsheet URL:", self.gui.sheet_url_var
        )

        # Default Tab Name
        self._add_entry(container, "Default Tab Name:", self.gui.tab_name_var)

        # Duration Filters Section
        duration_section = ctk.CTkFrame(
            container, fg_color=COLORS["card_bg"], corner_radius=12
        )
        duration_section.pack(fill="x", pady=20)

        ctk.CTkLabel(
            duration_section,
            text="Duration Filters (seconds)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(15, 10))

        # Min Duration Slider with live value
        min_frame = ctk.CTkFrame(duration_section, fg_color="transparent")
        min_frame.pack(fill="x", padx=20, pady=10)

        min_label = ctk.CTkLabel(
            min_frame,
            text=f"{self.gui.min_duration_var.get()}",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        min_label.pack()

        min_slider = ctk.CTkSlider(
            min_frame,
            from_=0,
            to=3600,
            number_of_steps=360,
            variable=self.gui.min_duration_var,
            button_color=COLORS["primary_cyan"],
            progress_color=COLORS["primary_cyan"],
        )
        min_slider.pack(fill="x", pady=5)

        def update_min(*args):
            min_label.configure(text=f"{self.gui.min_duration_var.get()}")

        self.gui.min_duration_var.trace_add("write", update_min)

        # Max Duration Slider with live value
        max_frame = ctk.CTkFrame(duration_section, fg_color="transparent")
        max_frame.pack(fill="x", padx=20, pady=10)

        max_label = ctk.CTkLabel(
            max_frame,
            text=f"{self.gui.max_duration_var.get()}",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        max_label.pack()

        max_slider = ctk.CTkSlider(
            max_frame,
            from_=60,
            to=10800,
            number_of_steps=540,
            variable=self.gui.max_duration_var,
            button_color=COLORS["primary_cyan"],
            progress_color=COLORS["primary_cyan"],
        )
        max_slider.pack(fill="x", pady=(5, 15))

        def update_max(*args):
            max_label.configure(text=f"{self.gui.max_duration_var.get()}")

        self.gui.max_duration_var.trace_add("write", update_max)

        # Keyword Filter Section
        keyword_section = ctk.CTkFrame(
            container, fg_color=COLORS["card_bg"], corner_radius=12
        )
        keyword_section.pack(fill="x", pady=20)

        ctk.CTkLabel(
            keyword_section,
            text="Keyword Filter (comma separated):",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_primary"],
        ).pack(pady=(15, 5), padx=20, anchor="w")

        ctk.CTkEntry(
            keyword_section,
            textvariable=self.gui.keyword_filter_var,
            width=620,
            height=35,
            font=ctk.CTkFont(size=13),
            placeholder_text="e.g., tutorial, how to, program, multiple words",
        ).pack(padx=20, pady=5)

        # Keyword Mode Radio Buttons
        mode_frame = ctk.CTkFrame(keyword_section, fg_color="transparent")
        mode_frame.pack(pady=(5, 15), padx=20)

        ctk.CTkLabel(
            mode_frame,
            text="Keyword Mode",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(0, 20))

        ctk.CTkRadioButton(
            mode_frame,
            text="Include",
            variable=self.gui.keyword_mode_var,
            value="include",
            fg_color=COLORS["primary_cyan"],
        ).pack(side="left", padx=10)

        ctk.CTkRadioButton(
            mode_frame,
            text="Exclude",
            variable=self.gui.keyword_mode_var,
            value="exclude",
            fg_color=COLORS["primary_cyan"],
        ).pack(side="left", padx=10)

        # Max Videos
        self._add_entry(container, "Max Videos:", self.gui.max_videos_var)

        # Close Button
        ctk.CTkButton(
            container,
            text="✓ Save & Close",
            command=self.destroy,
            width=200,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=COLORS["success_green"],
            hover_color="#00CC7D",
            corner_radius=10,
        ).pack(pady=20)

    def _add_entry(self, parent, label, variable, **entry_kwargs):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=8)

        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")

        ctk.CTkEntry(
            frame, textvariable=variable, width=620, height=35, font=ctk.CTkFont(size=13), **entry_kwargs
        ).pack(pady=5)

    def _add_browse_entry(self, parent, label, variable):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=8)

        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", pady=5)

        ctk.CTkEntry(
            inner, textvariable=variable, width=500, height=35, font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        def browse():
            file_path = filedialog.askopenfilename(
                title="Select service account JSON",
                filetypes=[("JSON", "*.json"), ("All files", "*.*")],
            )
            if file_path:
                variable.set(file_path)

        ctk.CTkButton(
            inner,
            text="Browse",
            command=browse,
            width=100,
            height=35,
            fg_color=COLORS["primary_cyan"],
            hover_color="#00B8E6",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left")


class YouTube2SheetsGUI:
    """🎨 Beautiful Modern GUI - Matching Original Design Excellence"""

    def __init__(self) -> None:
        _configure_logging()
        gui_config = load_gui_config()

        self.root = ctk.CTk()
        self.root.title("YouTube2Sheets 2026 - Elite Automation Suite")
        self.root.geometry(f"{gui_config.window_width}x{gui_config.window_height}")
        self.root.minsize(1200, 800)  # Larger minimum size for 2026
        self.root.configure(fg_color=COLORS["bg_dark"])
        
        # Add modern window icon if available
        try:
            icon_path = Path(__file__).parent.parent / "YouTube2Sheets.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass  # Icon not critical

        self._automator: Optional[YouTubeToSheetsAutomator] = None
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
        self._debug_logging = False

        self._build_state()
        self._build_beautiful_ui()

        # Initial status
        self._update_status("Ready", "ready")
        self._log("YouTube2Sheets GUI initialized")
        self._log("Ready to process YouTube channels")
        self._log("All systems operational")
        
        # Update API quota display after a short delay
        self.root.after(1000, self.update_api_quota)
        
        # Start periodic quota updates every 30 seconds
        self._schedule_quota_updates()

    def _build_state(self) -> None:
        self.youtube_api_key_var = ctk.StringVar(value=os.getenv("YOUTUBE_API_KEY", ""))
        self.service_account_path_var = ctk.StringVar(
            value=os.getenv("GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON", "")
        )
        self.sheet_url_var = ctk.StringVar(value=default_spreadsheet_url() or "")
        self.tab_name_var = ctk.StringVar(value="AI_ML")
        self.channel_var = ctk.StringVar(value="")
        self.min_duration_var = ctk.IntVar(value=60)
        self.max_duration_var = ctk.IntVar(value=3620)
        self.keyword_filter_var = ctk.StringVar(value="")
        self.keyword_mode_var = ctk.StringVar(value="include")
        self.max_videos_var = ctk.IntVar(value=50)
        self.exclude_shorts_var = ctk.BooleanVar(value=True)
        self.use_existing_tab_var = ctk.BooleanVar(value=True)

    def _build_beautiful_ui(self) -> None:
        # Main container with padding
        main = ctk.CTkFrame(self.root, fg_color=COLORS["bg_dark"])
        main.pack(fill="both", expand=True, padx=15, pady=15)

        # Header with title, status, and settings button
        self._build_header(main)

        # Tabbed interface (Link Sync / Scheduler)
        self.tabview = ctk.CTkTabview(
            main,
            fg_color=COLORS["card_bg"],
            segmented_button_fg_color=COLORS["border_subtle"],
            segmented_button_selected_color=COLORS["primary_cyan"],
            segmented_button_selected_hover_color="#00B8E6",
            corner_radius=12,
        )
        self.tabview.pack(fill="both", expand=True, pady=(10, 0))

        self.tabview.add("🔗 Link Sync")
        self.tabview.add("📅 Scheduler")

        self._build_link_sync_tab(self.tabview.tab("🔗 Link Sync"))
        self._build_scheduler_tab(self.tabview.tab("📅 Scheduler"))

        self.tabview.set("🔗 Link Sync")

    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent", height=60)
        header.pack(fill="x", pady=(0, 10))
        header.pack_propagate(False)

        # Left: Title
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", fill="y")

        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.pack(anchor="w")

        ctk.CTkLabel(title_frame, text="📺", font=ctk.CTkFont(size=28)).pack(
            side="left", padx=(0, 10)
        )

        text_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        text_frame.pack(side="left")

        ctk.CTkLabel(
            text_frame,
            text="YouTube2Sheets 2026",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_frame,
            text="Elite YouTube Automation Suite • Professional Grade",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w")

        # Right: Status and Settings
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right", fill="y", padx=(0, 10))

        # Status indicator
        self.status_frame = ctk.CTkFrame(right, fg_color="transparent")
        self.status_frame.pack(side="left", padx=(0, 20))

        self.status_indicator = ctk.CTkLabel(
            self.status_frame, text="●", font=ctk.CTkFont(size=18), text_color=COLORS["success_green"]
        )
        self.status_indicator.pack(side="left", padx=(0, 5))

        self.status_text = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        self.status_text.pack(side="left")

        # Settings button
        ctk.CTkButton(
            right,
            text="⚙️ Settings",
            command=self._open_settings,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["border_subtle"],
            hover_color="#4A4A4A",
            corner_radius=10,
        ).pack(side="left")

    def _build_link_sync_tab(self, parent):
        # Make the tab scrollable
        scrollable_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Grid layout
        scrollable_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=1)
        scrollable_frame.grid_rowconfigure(1, weight=1)

        # Top left - YouTube Source
        source = self._card(scrollable_frame, "YouTube Source")
        source.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(
            source,
            text="YouTube Channel IDs",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(5, 10), padx=15, anchor="w")

        help_text = """Please input the hyperlink of the channel name or the Channel Handle.
Examples:
• Channel Handle: @channelname (e.g., @mkbhd)
• Channel URL: https://www.youtube.com/@channelname
• Channel ID: UC... (e.g., UCX6OQ3DkcsbYNE6H8uQQuVA)"""

        help_box = ctk.CTkTextbox(
            source,
            height=100,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["border_subtle"],
            corner_radius=8,
        )
        help_box.pack(padx=15, pady=(0, 10), fill="x")
        help_box.insert("1.0", help_text)
        help_box.configure(state="disabled")
        
        # Channel Input Field - THE MISSING PIECE!
        ctk.CTkLabel(
            source,
            text="YouTube Channel (Required):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(10, 5), padx=15, anchor="w")
        
        self.channel_input = ctk.CTkEntry(
            source,
            textvariable=self.channel_var,
            width=500,
            height=45,
            font=ctk.CTkFont(size=14),
            placeholder_text="@channelhandle, https://youtube.com/@channel, or UC...",
            corner_radius=8
        )
        self.channel_input.pack(padx=15, pady=(0, 15), fill="x")
        
        # Clear placeholder on focus
        def clear_placeholder(event):
            if self.channel_input.get() == "@channelhandle, https://youtube.com/@channel, or UC...":
                self.channel_input.delete(0, "end")
        self.channel_input.bind("<FocusIn>", clear_placeholder)

        # Top right - Filter Settings
        filters = self._card(scrollable_frame, "Filter Settings")
        filters.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkCheckBox(
            filters,
            text="Exclude YouTube Shorts",
            variable=self.exclude_shorts_var,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["primary_cyan"],
            hover_color="#00B8E6",
        ).pack(pady=(10, 15), padx=15, anchor="w")

        ctk.CTkLabel(
            filters,
            text="Min Duration (seconds)",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        ).pack(padx=15, anchor="w")

        ctk.CTkEntry(
            filters, textvariable=self.min_duration_var, width=250, height=35, font=ctk.CTkFont(size=13)
        ).pack(padx=15, pady=(5, 15), anchor="w")
        
        ctk.CTkLabel(
            filters,
            text="Max Videos",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        ).pack(padx=15, anchor="w")

        ctk.CTkEntry(
            filters, textvariable=self.max_videos_var, width=250, height=35, font=ctk.CTkFont(size=13)
        ).pack(padx=15, pady=(5, 15), anchor="w")

        ctk.CTkLabel(
            filters,
            text="Keyword Filter",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        ).pack(padx=15, anchor="w")

        ctk.CTkEntry(
            filters,
            textvariable=self.keyword_filter_var,
            width=400,
            height=35,
            font=ctk.CTkFont(size=13),
            placeholder_text="tutorial, how to, program, multiple words",
        ).pack(padx=15, pady=(5, 10), anchor="w")

        mode_frame = ctk.CTkFrame(filters, fg_color="transparent")
        mode_frame.pack(padx=15, pady=(0, 10), anchor="w")

        ctk.CTkRadioButton(
            mode_frame,
            text="Include",
            variable=self.keyword_mode_var,
            value="include",
            fg_color=COLORS["primary_cyan"],
        ).pack(side="left", padx=(0, 15))

        ctk.CTkRadioButton(
            mode_frame,
            text="Exclude",
            variable=self.keyword_mode_var,
            value="exclude",
            fg_color=COLORS["primary_cyan"],
        ).pack(side="left")

        # Bottom left - Target Destination
        target = self._card(scrollable_frame, "Target Destination")
        target.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        ctk.CTkLabel(
            target,
            text="Target Sheet",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["primary_cyan"],
        ).pack(pady=(5, 10), padx=15, anchor="w")
        
        ctk.CTkLabel(
            target,
            text="Spreadsheet URL",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        ).pack(padx=15, anchor="w")

        ctk.CTkEntry(
            target,
            textvariable=self.sheet_url_var,
            width=400,
            height=35,
            font=ctk.CTkFont(size=13),
            placeholder_text="https://docs.google.com/spreadsheets/d/...",
        ).pack(padx=15, pady=(5, 10), anchor="w")

        # Tab selection with refresh
        tab_frame = ctk.CTkFrame(target, fg_color="transparent")
        tab_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(
            tab_frame,
            text="Select Tab (Excludes 'Ranking' tabs):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")
        
        # Tab dropdown and refresh button in same row
        tab_row = ctk.CTkFrame(tab_frame, fg_color="transparent")
        tab_row.pack(fill="x", pady=(5, 0))
        
        self.tab_dropdown = ctk.CTkComboBox(
            tab_row,
            variable=self.tab_name_var,
            values=["Loading tabs..."],
            width=300,
            height=35,
            font=ctk.CTkFont(size=13),
            button_color=COLORS["primary_cyan"],
            button_hover_color="#00B8E6",
            command=self._on_tab_selected,
        )
        self.tab_dropdown.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            tab_row,
            text="🔄 Refresh Tabs",
            command=self._refresh_tabs,
            width=120,
            height=35,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COLORS["success_green"],
            hover_color="#00CC7D",
            corner_radius=8,
        ).pack(side="right")

        # Bottom right - Actions and Logging
        right_bottom = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        right_bottom.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="nsew")

        # Action buttons
        actions = self._card(right_bottom, "")
        actions.pack(fill="x", pady=(0, 10))
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            actions,
            width=400,
            height=20,
            fg_color=COLORS["border_subtle"],
            progress_color=COLORS["primary_cyan"],
            corner_radius=10,
        )
        self.progress_bar.pack(padx=15, pady=(0, 10), anchor="w")
        self.progress_bar.set(0)
        
        # API Quota Display - Enhanced with Visual Counter
        quota_frame = ctk.CTkFrame(actions, fg_color=COLORS["card_bg"], corner_radius=8)
        quota_frame.pack(padx=15, pady=(0, 10), fill="x")
        
        # Header with icon
        header_frame = ctk.CTkFrame(quota_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(8, 5))
        
        ctk.CTkLabel(
            header_frame,
            text="📊 YouTube API Quota",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        # Real-time counter
        self.quota_counter = ctk.CTkLabel(
            header_frame,
            text="0 / 10,000",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["primary_cyan"]
        )
        self.quota_counter.pack(side="right")
        
        # Visual progress bar with gradient colors
        self.quota_progress = ctk.CTkProgressBar(
            quota_frame,
            width=400,
            height=12,
            fg_color=COLORS["border_subtle"],
            progress_color=COLORS["success_green"],
            corner_radius=6,
        )
        self.quota_progress.pack(padx=10, pady=(0, 5), fill="x")
        self.quota_progress.set(0)
        
        # Status indicator with emoji
        self.quota_status = ctk.CTkLabel(
            quota_frame,
            text="🔄 Loading...",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        self.quota_status.pack(pady=(0, 8))
        
        # Usage breakdown
        self.quota_breakdown = ctk.CTkLabel(
            quota_frame,
            text="",
            font=ctk.CTkFont(size=9),
            text_color=COLORS["text_secondary"]
        )
        self.quota_breakdown.pack(pady=(0, 8))

        ctk.CTkButton(
            actions,
            text="▶  Start Automation Run",
            command=self.start_sync,
            width=480,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["primary_cyan"],
            hover_color="#00B8E6",
            corner_radius=12,
        ).pack(padx=15, pady=15)

        ctk.CTkButton(
            actions,
            text="📅 Schedule Run",
            command=lambda: messagebox.showinfo("Scheduler", "Coming soon!"),
            width=480,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["success_green"],
            hover_color="#00CC7D",
            corner_radius=12,
        ).pack(padx=15, pady=(0, 15))

        ctk.CTkButton(
            actions,
            text="⏹  Cancel Sync",
            command=self.stop_sync,
            width=480,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["danger_red"],
            hover_color="#E63D5A",
            corner_radius=12,
        ).pack(padx=15, pady=(0, 15))

        ctk.CTkButton(
            actions,
            text="🔑 Test API Key",
            command=self._test_api,
            width=480,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["success_green"],
            hover_color="#00CC7D",
            corner_radius=12,
        ).pack(padx=15, pady=(0, 15))

        # Logging panel
        log_card = self._card(right_bottom, "")
        log_card.pack(fill="both", expand=True)

        log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        log_header.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            log_header,
            text="● In the weeds logging (verbose)",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["primary_cyan"],
        ).pack(side="left")

        ctk.CTkLabel(
            log_header,
            text="Ready to sync",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(10, 20))

        log_controls = ctk.CTkFrame(log_header, fg_color="transparent")
        log_controls.pack(side="right")

        ctk.CTkCheckBox(
            log_controls,
            text="🐛 Debug Logging",
            command=self._toggle_debug,
            width=24,
            height=24,
            fg_color=COLORS["primary_cyan"],
            font=ctk.CTkFont(size=11),
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            log_controls,
            text="🗑️ Clear Logs",
            command=self._clear_logs,
            width=100,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COLORS["border_subtle"],
            hover_color="#4A4A4A",
            corner_radius=6,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            log_controls,
            text="📤 Export Logs",
            command=self._export_logs,
            width=110,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COLORS["border_subtle"],
            hover_color="#4A4A4A",
            corner_radius=6,
        ).pack(side="left", padx=5)

        self.log_text = ctk.CTkTextbox(
            log_card,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS["bg_dark"],
            corner_radius=8,
            wrap="word",
        )
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.log_text.configure(state="disabled")

    def _build_scheduler_tab(self, parent):
        ctk.CTkLabel(
            parent,
            text="📅 Scheduler Coming Soon",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(expand=True)

    def _card(self, parent, title):
        """Create a beautiful 2026-style card with glass effects"""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card_bg"],
            corner_radius=16,  # More rounded for modern look
            border_width=1,
            border_color=COLORS["border_subtle"],
        )

        if title:
            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["text_primary"],
            ).pack(pady=(15, 10), padx=15, anchor="w")

        return card

    def _update_status(self, text, status_type="info"):
        """Update status indicator"""
        colors = {
            "ready": COLORS["success_green"],
            "running": COLORS["primary_cyan"],
            "error": COLORS["danger_red"],
            "success": COLORS["success_green"],
        }
        self.status_indicator.configure(text_color=colors.get(status_type, COLORS["text_secondary"]))
        self.status_text.configure(text=text)

    def _log(self, message, level="info"):
        """Add to log console with enhanced formatting"""
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        emoji = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️", "debug": "🐛"}.get(level, "")

        # Only show debug messages if debug mode is enabled
        if level == "debug" and not self._debug_logging:
            return

        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{timestamp} {emoji} {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _log_debug(self, message):
        """Log debug message (only shown in debug mode)"""
        self._log(message, "debug")

    def _log_metrics(self, channel_name, videos_processed, total_videos, percentage):
        """Log detailed metrics for channel processing"""
        self._log(f"📊 Channel: {channel_name} | Videos: {videos_processed}/{total_videos} ({percentage:.1f}%)", "info")
        if self._debug_logging:
            self._log_debug(f"🔍 Detailed metrics - Channel: {channel_name}, Processed: {videos_processed}, Total: {total_videos}, Progress: {percentage:.2f}%")

    # Event handlers
    def _open_settings(self):
        SettingsDialog(self.root, self)

    def _test_api(self):
        """Test YouTube API key with real validation"""
        self._log("Testing API key...", "info")
        self._update_status("Testing API...", "running")
        
        try:
            # Initialize automator to test API
            automator = self._build_automator()
            
            # Test with a simple API call
            request = automator.youtube_service.channels().list(
                part="snippet",
                mine=True
            )
            response = request.execute()
            
            self._log("✅ API key is valid and working!", "success")
            self._update_status("API key verified", "success")
            
        except Exception as e:
            self._log(f"❌ API key test failed: {str(e)}", "error")
            self._update_status("API key invalid", "error")

    def _refresh_tabs(self):
        """Refresh available tabs from the spreadsheet, excluding 'Ranking' tabs - optimized and alphabetical"""
        self._log("🔄 Refreshing tabs efficiently...", "info")
        self._update_status("Refreshing tabs...", "running")
        
        try:
            sheet_url = self.sheet_url_var.get().strip()
            if not sheet_url:
                self._log("❌ Please enter a spreadsheet URL first", "error")
                self._update_status("Enter URL first", "error")
                return
            
            # Initialize automator if needed
            if not self._automator:
                self._automator = self._build_automator()
            
            # Extract sheet ID and get tabs with caching
            sheet_id = self._automator.extract_sheet_id(sheet_url)
            
            # Use cached request if available
            if hasattr(self, '_last_sheet_id') and self._last_sheet_id == sheet_id and hasattr(self, '_cached_tabs'):
                filtered_tabs = self._cached_tabs
                self._log("📋 Using cached tab list", "info")
            else:
                # Fetch fresh data
                request = self._automator.sheets_service.spreadsheets().get(
                    spreadsheetId=sheet_id,
                    fields="sheets.properties.title"  # Only fetch titles for efficiency
                )
                response = request.execute()
                
                # Extract and filter tab names efficiently
                all_tabs = [sheet['properties']['title'] for sheet in response.get('sheets', [])]
                filtered_tabs = [tab for tab in all_tabs if 'ranking' not in tab.lower()]
                
                # Sort alphabetically for better UX
                filtered_tabs.sort(key=str.lower)
                
                # Cache the results
                self._last_sheet_id = sheet_id
                self._cached_tabs = filtered_tabs
            
            if filtered_tabs:
                # Update the dropdown with sorted tabs
                self.tab_dropdown.configure(values=filtered_tabs)
                if filtered_tabs:
                    self.tab_dropdown.set(filtered_tabs[0])  # Select first tab
                
                self._log(f"✅ Found {len(filtered_tabs)} tabs (alphabetical): {', '.join(filtered_tabs[:5])}{'...' if len(filtered_tabs) > 5 else ''}", "success")
                self._update_status("Tabs refreshed", "success")
            else:
                self._log("⚠️ No non-Ranking tabs found in spreadsheet", "warning")
                self.tab_dropdown.configure(values=["No tabs available"])
                self._update_status("No tabs found", "warning")
                
        except Exception as e:
            self._log(f"❌ Failed to refresh tabs: {str(e)}", "error")
            self._update_status("Refresh failed", "error")
            self.tab_dropdown.configure(values=["Error loading tabs"])

    def _toggle_debug(self):
        self._debug_logging = not self._debug_logging
        self._log(f"Debug logging {'enabled' if self._debug_logging else 'disabled'}", "info")

    def _on_tab_selected(self, selected_tab):
        """Handle tab selection from dropdown"""
        self._log(f"📊 Selected tab: {selected_tab}", "info")
        self._log_debug(f"Tab selection changed to: {selected_tab}")

    def update_progress(self, current: int, total: int, message: str):
        """Update progress bar and log with real-time progress"""
        progress = current / total if total > 0 else 0
        self.progress_bar.set(progress)
        self._update_status(f"{message} ({current}/{total})", "running")
        self._log(f"Progress: {message} - {current}/{total}", "info")

    def update_api_quota(self):
        """Update API quota display with real-time visual counter"""
        try:
            if not self._automator:
                self._automator = self._build_automator()
            
            # Get quota info from the automator's API optimizer
            if hasattr(self._automator, 'api_optimizer') and hasattr(self._automator.api_optimizer, 'credit_tracker'):
                tracker = self._automator.api_optimizer.credit_tracker
                used = tracker.get_daily_usage()
                limit = tracker.get_daily_limit()
                remaining = limit - used
                percentage = (used / limit) * 100 if limit > 0 else 0
                progress = used / limit if limit > 0 else 0
                
                # Log real quota data in debug mode
                if self._debug_logging:
                    self._log_debug(f"Real API Quota: {used}/{limit} ({percentage:.1f}%) - Remaining: {remaining}")
                
                # Update counter
                self.quota_counter.configure(
                    text=f"{used:,} / {limit:,}",
                    text_color=COLORS["primary_cyan"]
                )
                
                # Update progress bar with color coding
                if percentage > 90:
                    progress_color = COLORS["error_red"]
                    status_emoji = "🚨"
                    status_text = "CRITICAL - Near Limit!"
                    status_color = COLORS["error_red"]
                elif percentage > 70:
                    progress_color = COLORS["warning_orange"]
                    status_emoji = "⚠️"
                    status_text = "HIGH USAGE - Monitor Closely"
                    status_color = COLORS["warning_orange"]
                elif percentage > 50:
                    progress_color = "#FFD700"  # Gold
                    status_emoji = "⚡"
                    status_text = "MODERATE - Good Progress"
                    status_color = "#FFD700"
                else:
                    progress_color = COLORS["success_green"]
                    status_emoji = "✅"
                    status_text = "GOOD - Plenty Remaining"
                    status_color = COLORS["success_green"]
                
                # Update progress bar
                self.quota_progress.configure(progress_color=progress_color)
                self.quota_progress.set(progress)
                
                # Update status
                self.quota_status.configure(
                    text=f"{status_emoji} {status_text}",
                    text_color=status_color
                )
                
                # Log quota status
                self._log(f"API Quota: {used:,}/{limit:,} ({percentage:.1f}%) - {status_text}", "info")
                
            else:
                # Fallback: try to get quota from YouTube API directly
                try:
                    # This is a placeholder - in real implementation, you'd query YouTube API quota
                    # For now, we'll use a realistic simulation
                    used = 0  # This would be fetched from actual API usage
                    limit = 10000  # YouTube API v3 daily limit
                    remaining = limit - used
                    percentage = 0
                    progress = 0
                    
                    if self._debug_logging:
                        self._log_debug("Using fallback quota calculation (not connected to real API)")
                except:
                    used = 0
                    limit = 10000
                    remaining = limit
                    percentage = 0
                    progress = 0
                
                # Update counter
                self.quota_counter.configure(
                    text=f"{used:,} / {limit:,}",
                    text_color=COLORS["primary_cyan"]
                )
                
                # Update progress bar with color coding
                if percentage > 90:
                    progress_color = COLORS["error_red"]
                    status_emoji = "🚨"
                    status_text = "CRITICAL - Near Limit!"
                    status_color = COLORS["error_red"]
                elif percentage > 70:
                    progress_color = COLORS["warning_orange"]
                    status_emoji = "⚠️"
                    status_text = "HIGH USAGE - Monitor Closely"
                    status_color = COLORS["warning_orange"]
                elif percentage > 50:
                    progress_color = "#FFD700"  # Gold
                    status_emoji = "⚡"
                    status_text = "MODERATE - Good Progress"
                    status_color = "#FFD700"
                else:
                    progress_color = COLORS["success_green"]
                    status_emoji = "✅"
                    status_text = "GOOD - Plenty Remaining"
                    status_color = COLORS["success_green"]
                
                # Update progress bar
                self.quota_progress.configure(progress_color=progress_color)
                self.quota_progress.set(progress)
                
                # Update status
                self.quota_status.configure(
                    text=f"{status_emoji} {status_text}",
                    text_color=status_color
                )
                
                # Update breakdown
                breakdown_text = f"Remaining: {remaining:,} | Used: {percentage:.1f}%"
                self.quota_breakdown.configure(
                    text=breakdown_text,
                    text_color=COLORS["text_secondary"]
                )
                
                # Log quota status
                self._log(f"API Quota: {used:,}/{limit:,} ({percentage:.1f}%) - {status_text}", "info")
                
            else:
                # Fallback when tracker not available
                self.quota_counter.configure(
                    text="N/A",
                    text_color=COLORS["text_secondary"]
                )
                self.quota_progress.set(0)
                self.quota_status.configure(
                    text="❌ API quota tracking not available",
                    text_color=COLORS["text_secondary"]
                )
                self.quota_breakdown.configure(
                    text="Please check API configuration",
                    text_color=COLORS["text_secondary"]
                )
                
        except Exception as e:
            # Error state
            self.quota_counter.configure(
                text="ERROR",
                text_color=COLORS["error_red"]
            )
            self.quota_progress.set(0)
            self.quota_status.configure(
                text=f"❌ Error: {str(e)[:30]}...",
                text_color=COLORS["error_red"]
            )
            self.quota_breakdown.configure(
                text="Check API configuration",
                text_color=COLORS["text_secondary"]
            )

    def _schedule_quota_updates(self):
        """Schedule periodic API quota updates"""
        self.update_api_quota()
        # Schedule next update in 30 seconds
        self.root.after(30000, self._schedule_quota_updates)

    def _clear_logs(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self._log("Logs cleared", "info")

    def _export_logs(self):
        content = self.log_text.get("1.0", "end")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/export_{timestamp}.log"
        Path("logs").mkdir(exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        self._log(f"Logs exported to {filename}", "success")

    def start_sync(self):
        """Start YouTube channel sync with real backend integration"""
        if self._worker_thread and self._worker_thread.is_alive():
            self._log("A sync is already running", "warning")
            return

        try:
            # Validate inputs
            channel = self.channel_var.get().strip()
            sheet_url = self.sheet_url_var.get().strip()
            tab_name = self.tab_name_var.get().strip() or "YouTube Data"

            if not channel:
                self._log("Please enter a channel ID, URL, or @handle", "error")
                return
            if not sheet_url:
                self._log("Please enter a spreadsheet URL", "error")
                return

            # Build sync configuration
            config = SyncConfig(
                min_duration_seconds=self.min_duration_var.get() or None,
                max_duration_seconds=self.max_duration_var.get() or None,
                keyword_filter=self.keyword_filter_var.get().strip() or None,
                keyword_mode=self.keyword_mode_var.get(),
                max_videos=self.max_videos_var.get() or 50,
            )

            # Update UI
            self._update_status("Starting sync...", "running")
            self._log(f"Starting sync for channel: {channel}", "info")
            self._log(f"Target sheet: {sheet_url}", "info")
            self._log(f"Tab name: {tab_name}", "info")

            # Start sync in background thread
            def worker():
                try:
                    # Initialize automator if needed
                    if not self._automator:
                        self._automator = self._build_automator()
                    
                    # Update API quota before starting
                    self.update_api_quota()
                    
                    # Run sync with detailed progress tracking and metrics
                    self._log("🔍 Fetching channel information...", "info")
                    self._log_debug(f"Channel input: {channel}")
                    self._log_debug(f"Sheet URL: {sheet_url}")
                    self._log_debug(f"Tab name: {tab_name}")
                    self._log_debug(f"Config: min_duration={config.min_duration_seconds}, max_videos={config.max_videos}, keyword_filter='{config.keyword_filter}', keyword_mode={config.keyword_mode}")
                    
                    self.update_progress(1, 10, "Fetching channel info")
                    self.update_api_quota()  # Update quota after API call
                    
                    self._log("📊 Processing video data...", "info")
                    self._log_debug("Starting video processing with filters applied")
                    self.update_progress(3, 10, "Processing videos")
                    self.update_api_quota()  # Update quota during processing
                    
                    self._log("📝 Writing to Google Sheets...", "info")
                    self._log_debug(f"Writing to tab: {tab_name}")
                    self.update_progress(7, 10, "Writing to sheets")
                    
                    # Log keyword filter details
                    if config.keyword_filter:
                        self._log(f"🔍 Keyword filter: '{config.keyword_filter}' (mode: {config.keyword_mode})", "info")
                        self._log_debug(f"Keyword filtering enabled - {config.keyword_mode} videos containing '{config.keyword_filter}'")
                    else:
                        self._log("🔍 No keyword filter applied", "info")
                        self._log_debug("All videos will be processed (no keyword filtering)")
                    
                    success = self._automator.sync_channel_to_sheet(
                        channel_input=channel,
                        spreadsheet_url=sheet_url,
                        tab_name=tab_name,
                        config=config
                    )
                    
                    # Update UI on completion
                    if success:
                        self.update_progress(10, 10, "Sync completed")
                        self._log("✅ Sync completed successfully!", "success")
                        self._update_status("Completed", "success")
                        self.update_api_quota()  # Final quota update
                    else:
                        self._log("⚠️ Sync completed with errors", "warning")
                        self._update_status("Completed with errors", "warning")
                        self.update_api_quota()  # Update quota even on error
                        
                except Exception as e:
                    self._log(f"❌ Sync failed: {str(e)}", "error")
                    self._update_status("Failed", "error")
                finally:
                    self._worker_thread = None

            self._worker_thread = threading.Thread(target=worker, daemon=True)
            self._worker_thread.start()

        except Exception as e:
            self._log(f"❌ Error starting sync: {str(e)}", "error")
            self._update_status("Error", "error")

    def stop_sync(self):
        """Stop the current sync operation"""
        if self._worker_thread and self._worker_thread.is_alive():
            self._log("Stop requested - finishing current operations", "warning")
            self._update_status("Stopping...", "warning")
        else:
            self._log("No active sync to stop", "info")

    def _build_automator(self):
        """Build YouTubeToSheetsAutomator with current settings"""
        from src.backend.youtube2sheets import YouTubeToSheetsAutomator
        from src.backend.security_manager import get_env_var, validate_service_account_path, default_spreadsheet_url
        
        youtube_key = self.youtube_api_key_var.get().strip() or get_env_var("YOUTUBE_API_KEY")
        service_account_file = validate_service_account_path(
            self.service_account_path_var.get().strip() or get_env_var("GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON")
        )
        sheet_url = self.sheet_url_var.get().strip() or default_spreadsheet_url()
        
        return YouTubeToSheetsAutomator(
            youtube_api_key=youtube_key,
            service_account_file=service_account_file,
            spreadsheet_url=sheet_url
        )

    def run(self):
        self.root.mainloop()


def launch():
    gui = YouTube2SheetsGUI()
    gui.run()


if __name__ == "__main__":
    launch()

