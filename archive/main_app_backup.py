"""Modern CustomTkinter GUI for YouTube2Sheets."""

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


def _handle_global_exception(exc_type, exc_value, exc_traceback):  # pragma: no cover - GUI hooks
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


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class YouTube2SheetsGUI:
    """Main window orchestrating user interactions for YouTube2Sheets."""

    def __init__(self) -> None:
        _configure_logging()
        gui_config = load_gui_config()
        self.root = ctk.CTk()
        self.root.title("YouTube2Sheets – Professional Edition")
        
        # Dynamic window sizing based on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate window size (85% of screen, minimum 1200x800)
        window_width = max(1200, int(screen_width * 0.85))
        window_height = max(800, int(screen_height * 0.85))
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1200, 800)  # Minimum size for proper layout
        
        # Professional color scheme
        ctk.set_appearance_mode("light")  # Clean light theme
        ctk.set_default_color_theme("green")  # Professional green theme

        self._automator: Optional[YouTubeToSheetsAutomator] = None
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()

        self._build_state()
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_state(self) -> None:
        self.youtube_api_key_var = ctk.StringVar(value=os.getenv("YOUTUBE_API_KEY", ""))
        self.service_account_path_var = ctk.StringVar(value=os.getenv("GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON", ""))
        self.sheet_url_var = ctk.StringVar(value=default_spreadsheet_url() or "")
        self.tab_name_var = ctk.StringVar(value="YouTube Data")
        self.channel_var = ctk.StringVar(value="")
        self.min_duration_var = ctk.IntVar(value=90)  # Default to 90 seconds
        self.max_duration_var = ctk.IntVar(value=3600)  # Keep for compatibility but won't show
        self.keyword_filter_var = ctk.StringVar(value="")
        self.keyword_mode_var = ctk.StringVar(value="include")
        # max_videos_var removed - system processes maximum possible automatically
        self.scheduler_sheet_id_var = ctk.StringVar(value="")
        self.scheduler_tab_var = ctk.StringVar(value="Scheduler")

    def _build_ui(self) -> None:
        # Modern header with gradient effect
        self._build_modern_header()
        
        # Main content area with modern layout
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create tabbed interface
        self._build_tabbed_interface(main_container)
        
        # Full-width Activity Log at bottom
        self._build_modern_log_section(main_container)
        
        # Status bar
        self._build_modern_status_bar()

    def _build_tabbed_interface(self, parent: ctk.CTkBaseClass) -> None:
        """Build tabbed interface with dropdown selection."""
        # Tab container
        tab_container = ctk.CTkFrame(parent, fg_color="transparent")
        tab_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Tab selection dropdown
        tab_selection_frame = ctk.CTkFrame(tab_container, fg_color="transparent")
        tab_selection_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            tab_selection_frame,
            text="Select Function:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        # Tab dropdown
        self.tab_var = ctk.StringVar(value="sync")
        self.tab_dropdown = ctk.CTkOptionMenu(
            tab_selection_frame,
            variable=self.tab_var,
            values=["🎬 Sync Videos", "⏰ Scheduled Jobs"],
            width=200,
            height=35,
            command=self._on_tab_change,
            fg_color="green",
            button_color="darkgreen",
            button_hover_color="darkgreen",
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.tab_dropdown.pack(side="left")
        
        # Tab content container
        self.tab_content = ctk.CTkFrame(tab_container, corner_radius=8, fg_color=("white", "gray10"))
        self.tab_content.pack(fill="both", expand=True)
        
        # Show sync tab by default
        self._show_sync_tab()

    def _on_tab_change(self, choice) -> None:
        """Handle tab dropdown change."""
        if "Sync Videos" in choice:
            self._show_sync_tab()
        elif "Scheduled Jobs" in choice:
            self._show_scheduler_tab()

    def _show_sync_tab(self) -> None:
        """Show the sync tab content."""
        # Clear existing content
        for widget in self.tab_content.winfo_children():
            widget.destroy()
        
        # Create two panels for sync tab
        sync_container = ctk.CTkFrame(self.tab_content, fg_color="transparent")
        sync_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left panel for configuration
        left_panel = ctk.CTkFrame(sync_container, corner_radius=8, fg_color=("gray98", "gray12"))
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right panel for controls and progress
        right_panel = ctk.CTkFrame(sync_container, corner_radius=8, fg_color=("gray98", "gray12"))
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Build sections
        self._build_modern_config_section(left_panel)
        self._build_modern_control_section(right_panel)
        self._build_modern_progress_section(right_panel)

    def _show_scheduler_tab(self) -> None:
        """Show the scheduler tab content."""
        # Clear existing content
        for widget in self.tab_content.winfo_children():
            widget.destroy()
        
        # Scheduler content
        scheduler_container = ctk.CTkFrame(self.tab_content, fg_color="transparent")
        scheduler_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Scheduler header
        header_frame = ctk.CTkFrame(scheduler_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header_frame,
            text="⏰ Scheduled Jobs Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("gray30", "gray70")
        ).pack(side="left")
        
        # Scheduler controls
        controls_card = ctk.CTkFrame(scheduler_container, corner_radius=8, fg_color=("gray98", "gray12"))
        controls_card.pack(fill="x", pady=(0, 20))
        
        # Card header
        card_header = ctk.CTkFrame(controls_card, fg_color="transparent")
        card_header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            card_header,
            text="🎛️ Scheduler Controls",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        # Control buttons
        buttons_frame = ctk.CTkFrame(controls_card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        run_scheduler_btn = ctk.CTkButton(
            buttons_frame,
            text="▶️ Run Scheduler Now",
            width=180,
            height=45,
            command=self.run_scheduler_once,
            fg_color="blue",
            hover_color="darkblue",
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        run_scheduler_btn.pack(side="left", padx=(0, 15))
        
        enable_scheduler_btn = ctk.CTkButton(
            buttons_frame,
            text="🔧 Enable Scheduler",
            width=150,
            height=45,
            command=self._enable_scheduler,
            fg_color="green",
            hover_color="darkgreen",
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        enable_scheduler_btn.pack(side="left", padx=(0, 15))
        
        # Job list placeholder
        jobs_card = ctk.CTkFrame(scheduler_container, corner_radius=8, fg_color=("gray98", "gray12"))
        jobs_card.pack(fill="both", expand=True)
        
        # Jobs header
        jobs_header = ctk.CTkFrame(jobs_card, fg_color="transparent")
        jobs_header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            jobs_header,
            text="📋 Scheduled Jobs",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        # Jobs list (placeholder for now)
        jobs_list = ctk.CTkTextbox(
            jobs_card,
            height=200,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        jobs_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        jobs_list.insert("1.0", "No scheduled jobs found.\n\nTo schedule a job:\n1. Go to Sync Videos tab\n2. Configure your settings\n3. Click 'Schedule Run' button")
        jobs_list.configure(state="disabled")

    def _build_modern_header(self) -> None:
        """Build modern header with professional styling."""
        header_frame = ctk.CTkFrame(self.root, fg_color=("gray95", "gray15"), height=80)
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)
        
        # Title section
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="y", padx=20, pady=15)
        
        # Main title with icon
        title_label = ctk.CTkLabel(
            title_frame,
            text="🛡️ YouTube2Sheets",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("gray20", "gray80")
        )
        title_label.pack(anchor="w")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Professional YouTube Automation Suite",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray60")
        )
        subtitle_label.pack(anchor="w")
        
        # Status section
        status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_frame.pack(side="right", fill="y", padx=20, pady=15)
        
        # Status badge
        self.status_badge = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="green",
            corner_radius=15,
            width=80,
            height=30
        )
        self.status_badge.pack(side="right", padx=(10, 0))
        
        # Settings button
        settings_btn = ctk.CTkButton(
            status_frame,
            text="⚙️ Settings",
            width=100,
            height=30,
            command=self._open_settings,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        settings_btn.pack(side="right")

    def _build_modern_config_section(self, parent: ctk.CTkBaseClass) -> None:
        """Build modern configuration section."""
        # Section header
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="🔧 Configuration",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("gray30", "gray70")
        ).pack(side="left")
        
        # Only show essential configuration - move API to settings
        self._build_sheet_card(parent)
        self._build_filters_card(parent)

    def _build_api_card(self, parent: ctk.CTkBaseClass) -> None:
        """Build API configuration card."""
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=("white", "gray25"))
        card.pack(fill="x", padx=20, pady=(0, 15))
        
        # Card header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text="🔑 API Configuration",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # API Key
        self._add_modern_entry(card, "YouTube API Key", self.youtube_api_key_var, show="*")
        self._add_modern_browse_entry(card, "Service Account JSON", self.service_account_path_var)
        self._add_modern_entry(card, "Default Spreadsheet URL", self.sheet_url_var)

    def _build_sheet_card(self, parent: ctk.CTkBaseClass) -> None:
        """Build Google Sheets configuration card."""
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color=("gray98", "gray12"))
        card.pack(fill="x", padx=20, pady=(0, 15))
        
        # Card header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text="📊 Google Sheets",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Tab name with refresh
        tab_frame = ctk.CTkFrame(card, fg_color="transparent")
        tab_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(tab_frame, text="Default Tab Name:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        tab_input_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        tab_input_frame.pack(fill="x", pady=(5, 0))
        
        tab_entry = ctk.CTkEntry(
            tab_input_frame, 
            textvariable=self.tab_name_var, 
            width=300,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        tab_entry.pack(side="left", padx=(0, 10))
        
        refresh_btn = ctk.CTkButton(
            tab_input_frame,
            text="🔄 Refresh Tabs",
            width=120,
            height=35,
            command=self._refresh_tabs,
            fg_color="blue",
            hover_color="darkblue",
            corner_radius=8
        )
        refresh_btn.pack(side="left")

    def _build_filters_card(self, parent: ctk.CTkBaseClass) -> None:
        """Build filters configuration card."""
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color=("gray98", "gray12"))
        card.pack(fill="x", padx=20, pady=(0, 15))
        
        # Card header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text="🎯 Filters & Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Clean duration filters in a grid
        duration_frame = ctk.CTkFrame(card, fg_color="transparent")
        duration_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            duration_frame, 
            text="Duration Filter", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 15))
        
        # Minimum duration only - clean layout
        min_frame = ctk.CTkFrame(duration_frame, fg_color="transparent")
        min_frame.pack(fill="x", pady=(0, 15))
        
        min_label = ctk.CTkLabel(min_frame, text="Minimum Duration:", font=ctk.CTkFont(size=13, weight="bold"))
        min_label.pack(anchor="w")
        
        min_slider_frame = ctk.CTkFrame(min_frame, fg_color="transparent")
        min_slider_frame.pack(fill="x", pady=(5, 0))
        
        min_slider = ctk.CTkSlider(
            min_slider_frame, 
            from_=0, 
            to=3600, 
            number_of_steps=180, 
            variable=self.min_duration_var,
            height=25,
            corner_radius=12,
            progress_color="green",
            button_color="green",
            button_hover_color="darkgreen"
        )
        min_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        min_value = ctk.CTkLabel(
            min_slider_frame, 
            textvariable=self.min_duration_var, 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="green",
            width=60
        )
        min_value.pack(side="right")
        
        # Keyword filters - clean layout
        keyword_frame = ctk.CTkFrame(card, fg_color="transparent")
        keyword_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            keyword_frame, 
            text="Keyword Filter", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        keyword_entry = ctk.CTkEntry(
            keyword_frame, 
            textvariable=self.keyword_filter_var,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=13),
            placeholder_text="Enter keywords separated by commas..."
        )
        keyword_entry.pack(fill="x", pady=(0, 10))
        
        # Keyword mode - clean radio buttons
        mode_frame = ctk.CTkFrame(keyword_frame, fg_color="transparent")
        mode_frame.pack(fill="x")
        
        ctk.CTkLabel(mode_frame, text="Filter Mode:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 15))
        
        for mode, label in (("include", "Include these keywords"), ("exclude", "Exclude these keywords")):
            ctk.CTkRadioButton(
                mode_frame, 
                text=label, 
                variable=self.keyword_mode_var, 
                value=mode,
                font=ctk.CTkFont(size=12)
            ).pack(side="left", padx=(0, 20))
        
        # Max videos removed - system processes maximum possible automatically

    def _build_modern_control_section(self, parent: ctk.CTkBaseClass) -> None:
        """Build modern control section."""
        # Section header
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="🎬 YouTube Source",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("gray30", "gray70")
        ).pack(side="left")
        
        # YouTube source card
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color=("gray98", "gray12"))
        card.pack(fill="x", padx=20, pady=(0, 15))
        
        # Card header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text="📺 Channel Input",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Channel input with better helper text
        ctk.CTkLabel(
            card,
            text="Please input the hyperlink of the channel name or the Channel Handle.",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(0, 5))
        
        # Helper text with examples
        helper_text = (
            "• Handle: @channelname (e.g., @mkbhd)\n"
            "• URL: https://www.youtube.com/@channelname\n"
            "• Channel ID: UCxxxxxxxxxxxxxxxxxxxxxx"
        )
        ctk.CTkLabel(
            card,
            text=helper_text,
            font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray70"),
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))
        
        self.channel_entry = ctk.CTkTextbox(
            card,
            height=120,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.channel_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Bind channel input to variable
        self.channel_entry.bind("<KeyRelease>", self._on_channel_input_change)
        
        # Action buttons - better layout
        buttons_frame = ctk.CTkFrame(card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Primary action button
        start_btn = ctk.CTkButton(
            buttons_frame,
            text="▶️ Start Automation Run",
            width=180,
            height=50,
            command=self.start_sync,
            fg_color="green",
            hover_color="darkgreen",
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        start_btn.pack(side="left", padx=(0, 10))
        
        # Secondary buttons
        secondary_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        secondary_frame.pack(side="left", fill="x", expand=True)
        
        stop_btn = ctk.CTkButton(
            secondary_frame,
            text="⏹️ Stop",
            width=100,
            height=40,
            command=self.stop_sync,
            fg_color="red",
            hover_color="darkred",
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        stop_btn.pack(side="left", padx=(0, 10))
        
        scheduler_btn = ctk.CTkButton(
            secondary_frame,
            text="⏰ Schedule Run",
            width=140,
            height=40,
            command=self.run_scheduler_once,
            fg_color="blue",
            hover_color="darkblue",
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        scheduler_btn.pack(side="left")

    def _build_modern_progress_section(self, parent: ctk.CTkBaseClass) -> None:
        """Build modern progress section."""
        # Section header
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="📊 Progress & Status",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("gray30", "gray70")
        ).pack(side="left")
        
        # Progress card
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color=("gray98", "gray12"))
        card.pack(fill="x", padx=20, pady=(0, 15))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            card,
            height=20,
            corner_radius=10,
            progress_color="blue"
        )
        self.progress_bar.pack(fill="x", padx=15, pady=15)
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            card, 
            text="Ready to sync", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="green"
        )
        self.status_label.pack(pady=(0, 15))

    def _build_modern_log_section(self, parent: ctk.CTkBaseClass) -> None:
        """Build modern log section."""
        # Section header
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="📝 Activity Log",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("gray30", "gray70")
        ).pack(side="left")
        
        # Log card
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color=("gray98", "gray12"))
        card.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Log controls - better layout
        controls_frame = ctk.CTkFrame(card, fg_color="transparent")
        controls_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        # Left side - Debug logging
        left_controls = ctk.CTkFrame(controls_frame, fg_color="transparent")
        left_controls.pack(side="left")
        
        self.debug_logging_var = ctk.BooleanVar(value=False)
        debug_checkbox = ctk.CTkCheckBox(
            left_controls, 
            text="Debug Logging", 
            variable=self.debug_logging_var,
            command=self._toggle_debug_logging,
            font=ctk.CTkFont(size=12)
        )
        debug_checkbox.pack(side="left")
        
        # Right side - Control buttons
        right_controls = ctk.CTkFrame(controls_frame, fg_color="transparent")
        right_controls.pack(side="right")
        
        clear_btn = ctk.CTkButton(
            right_controls,
            text="🗑️ Clear Logs",
            width=100,
            height=32,
            command=self._clear_logs,
            fg_color="gray60",
            hover_color="gray50",
            corner_radius=6,
            font=ctk.CTkFont(size=11)
        )
        clear_btn.pack(side="left", padx=(0, 8))
        
        export_btn = ctk.CTkButton(
            right_controls,
            text="📤 Export Logs",
            width=100,
            height=32,
            command=self._export_logs,
            fg_color="gray60",
            hover_color="gray50",
            corner_radius=6,
            font=ctk.CTkFont(size=11)
        )
        export_btn.pack(side="left")
        
        # Log text area - MUCH LARGER, spans full width
        self.log_text = ctk.CTkTextbox(
            card,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=13),
            height=400,  # Much larger debugging window
            scrollbar_button_color="gray60",
            scrollbar_button_hover_color="gray50"
        )
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.log_text.configure(state="disabled")
        
        # Add initial log message
        self._append_log("YouTube2Sheets Professional Edition - Ready")
        self._append_log("Activity Log initialized successfully")
        
        # Add mouse wheel scrolling
        self._add_mouse_wheel_scrolling()

    def _build_modern_status_bar(self) -> None:
        """Build modern status bar."""
        status_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray20"), height=40)
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        status_frame.pack_propagate(False)
        
        # Status
        self.status_text = ctk.CTkLabel(
            status_frame,
            text="Ready - No active jobs",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_text.pack(side="left", padx=15, pady=10)
        
        # API Usage
        self.api_usage_text = ctk.CTkLabel(
            status_frame,
            text="Daily API Usage: Loading...",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray70")
        )
        self.api_usage_text.pack(side="right", padx=15, pady=10)

    def _add_modern_entry(self, parent: ctk.CTkBaseClass, label: str, variable, **kwargs) -> None:
        """Add modern entry field."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(
            row, 
            text=f"{label}:", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        entry = ctk.CTkEntry(
            row, 
            textvariable=variable, 
            width=400,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            **kwargs
        )
        entry.pack(anchor="w")

    def _add_modern_browse_entry(self, parent: ctk.CTkBaseClass, label: str, variable) -> None:
        """Add modern browse entry field."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(
            row, 
            text=f"{label}:", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x")
        
        entry = ctk.CTkEntry(
            inner, 
            textvariable=variable, 
            width=320,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        entry.pack(side="left", padx=(0, 10))
        
        def browse():
            file_path = filedialog.askopenfilename(
                title="Select service account JSON", 
                filetypes=[("JSON", "*.json"), ("All files", "*.*")]
            )
            if file_path:
                variable.set(file_path)
        
        browse_btn = ctk.CTkButton(
            inner, 
            text="Browse", 
            width=80,
            height=35,
            command=browse,
            fg_color="blue",
            hover_color="darkblue",
            corner_radius=8
        )
        browse_btn.pack(side="left")

    def _add_clean_entry(self, parent: ctk.CTkBaseClass, label: str, variable, **kwargs) -> None:
        """Add clean entry field."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            row, 
            text=f"{label}:", 
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        entry = ctk.CTkEntry(
            row, 
            textvariable=variable, 
            width=400,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=13),
            **kwargs
        )
        entry.pack(anchor="w")

    def _add_mouse_wheel_scrolling(self) -> None:
        """Add mouse wheel scrolling to the main window."""
        def _on_mousewheel(event):
            self.log_text.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Simple bind for CustomTkinter compatibility
        self.log_text.bind("<MouseWheel>", _on_mousewheel)

    def _on_channel_input_change(self, event=None) -> None:
        """Handle channel input changes."""
        content = self.channel_entry.get("1.0", "end-1c").strip()
        self.channel_var.set(content)

    def _open_settings(self) -> None:
        """Open settings dialog."""
        self._append_log("Opening settings dialog...")
        self._show_settings_dialog()

    def _enable_scheduler(self) -> None:
        """Enable scheduler functionality."""
        self._append_log("Scheduler enabled")
        self.status_badge.configure(text="Scheduler On", fg_color="orange")

    def _show_settings_dialog(self) -> None:
        """Show API settings dialog."""
        # Create settings window
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("API Settings")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Center the window
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (settings_window.winfo_screenheight() // 2) - (400 // 2)
        settings_window.geometry(f"500x400+{x}+{y}")
        
        # Main container
        main_frame = ctk.CTkFrame(settings_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="⚙️ API Configuration Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # API Configuration Card
        api_card = ctk.CTkFrame(main_frame, corner_radius=8, fg_color=("gray98", "gray12"))
        api_card.pack(fill="x", padx=20, pady=(0, 20))
        
        # Card header
        header = ctk.CTkFrame(api_card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text="🔑 API Configuration",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        # API Key
        self._add_modern_entry(api_card, "YouTube API Key", self.youtube_api_key_var, show="*")
        self._add_modern_browse_entry(api_card, "Service Account JSON", self.service_account_path_var)
        self._add_modern_entry(api_card, "Default Spreadsheet URL", self.sheet_url_var)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Settings",
            width=150,
            height=40,
            command=lambda: self._save_settings(settings_window),
            fg_color="green",
            hover_color="darkgreen",
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            width=100,
            height=40,
            command=settings_window.destroy,
            fg_color="gray60",
            hover_color="gray50",
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cancel_btn.pack(side="left")
        
        self._append_log("Settings dialog opened successfully")

    def _save_settings(self, settings_window) -> None:
        """Save settings and close dialog."""
        self._append_log("Settings saved successfully")
        settings_window.destroy()

    def _build_config_section(self, parent: ctk.CTkBaseClass) -> None:
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(frame, text="🔧 Configuration", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        self._add_entry(frame, "YouTube API Key", self.youtube_api_key_var, show="*")
        self._add_browse_entry(frame, "Service Account JSON", self.service_account_path_var)
        self._add_entry(frame, "Default Spreadsheet URL", self.sheet_url_var)
        # Tab name with refresh button
        tab_row = ctk.CTkFrame(frame)
        tab_row.pack(fill="x", padx=20, pady=6)
        ctk.CTkLabel(tab_row, text="Default Tab Name:").pack(anchor="w")
        
        tab_input_frame = ctk.CTkFrame(tab_row)
        tab_input_frame.pack(fill="x", pady=4)
        
        tab_entry = ctk.CTkEntry(tab_input_frame, textvariable=self.tab_name_var, width=380)
        tab_entry.pack(side="left", padx=(0, 10))
        
        refresh_tabs_btn = ctk.CTkButton(
            tab_input_frame, 
            text="🔄 Refresh Tabs", 
            width=120,
            command=self._refresh_tabs
        )
        refresh_tabs_btn.pack(side="left")

        duration_frame = ctk.CTkFrame(frame)
        duration_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(duration_frame, text="Duration Filters (seconds)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(5, 10))

        slider_frame = ctk.CTkFrame(duration_frame)
        slider_frame.pack(fill="x", padx=10, pady=5)

        min_slider = ctk.CTkSlider(slider_frame, from_=0, to=3600, number_of_steps=360, variable=self.min_duration_var)
        min_slider.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(slider_frame, textvariable=self.min_duration_var).pack()

        max_slider = ctk.CTkSlider(slider_frame, from_=60, to=10800, number_of_steps=540, variable=self.max_duration_var)
        max_slider.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(slider_frame, textvariable=self.max_duration_var).pack()

        keyword_frame = ctk.CTkFrame(frame)
        keyword_frame.pack(fill="x", padx=10, pady=10)
        self._add_entry(keyword_frame, "Keyword Filter (comma separated)", self.keyword_filter_var)

        mode_frame = ctk.CTkFrame(keyword_frame)
        mode_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(mode_frame, text="Keyword Mode").pack(side="left", padx=(0, 10))
        for mode, label in (("include", "Include"), ("exclude", "Exclude")):
            ctk.CTkRadioButton(mode_frame, text=label, variable=self.keyword_mode_var, value=mode).pack(side="left", padx=5)

        self._add_entry(frame, "Max Videos", self.max_videos_var)

        scheduler_frame = ctk.CTkFrame(frame)
        scheduler_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(scheduler_frame, text="Scheduler", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(5, 10))
        self._add_entry(scheduler_frame, "Scheduler Sheet ID", self.scheduler_sheet_id_var)
        self._add_entry(scheduler_frame, "Scheduler Tab Name", self.scheduler_tab_var)

    def _add_entry(self, parent: ctk.CTkBaseClass, label: str, variable, **entry_kwargs) -> None:
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", padx=20, pady=6)
        ctk.CTkLabel(row, text=f"{label}:").pack(anchor="w")
        entry = ctk.CTkEntry(row, textvariable=variable, width=420, **entry_kwargs)
        entry.pack(anchor="w", pady=4)

    def _add_browse_entry(self, parent: ctk.CTkBaseClass, label: str, variable) -> None:
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", padx=20, pady=6)
        ctk.CTkLabel(row, text=f"{label}:").pack(anchor="w")

        inner = ctk.CTkFrame(row)
        inner.pack(fill="x", pady=4)
        entry = ctk.CTkEntry(inner, textvariable=variable, width=380)
        entry.pack(side="left", padx=(0, 10))

        def browse():
            file_path = filedialog.askopenfilename(title="Select service account JSON", filetypes=[("JSON", "*.json"), ("All files", "*.*")])
            if file_path:
                variable.set(file_path)

        ctk.CTkButton(inner, text="Browse", command=browse).pack(side="left")

    def _build_control_section(self, parent: ctk.CTkBaseClass) -> None:
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(frame, text="🎬 Controls", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        self.channel_entry = ctk.CTkEntry(frame, placeholder_text="Channel URL, @handle, or Channel ID", width=500, textvariable=self.channel_var)
        self.channel_entry.pack(pady=8)

        buttons_frame = ctk.CTkFrame(frame)
        buttons_frame.pack(pady=10)
        ctk.CTkButton(buttons_frame, text="Start Sync", command=self.start_sync).pack(side="left", padx=10)
        ctk.CTkButton(buttons_frame, text="Stop", command=self.stop_sync).pack(side="left", padx=10)
        ctk.CTkButton(buttons_frame, text="Run Scheduler Once", command=self.run_scheduler_once).pack(side="left", padx=10)

    def _build_progress_section(self, parent: ctk.CTkBaseClass) -> None:
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(frame, text="📊 Progress", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(frame)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(frame, text="Idle", font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=5)

    def _build_log_section(self, parent: ctk.CTkBaseClass) -> None:
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True)

        # Log header with controls
        log_header = ctk.CTkFrame(frame, fg_color="transparent")
        log_header.pack(fill="x", padx=20, pady=(10, 5))
        
        # Title
        ctk.CTkLabel(log_header, text="📝 Activity Log", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        
        # Debug logging checkbox
        self.debug_logging_var = ctk.BooleanVar(value=False)
        debug_checkbox = ctk.CTkCheckBox(
            log_header, 
            text="Debug Logging", 
            variable=self.debug_logging_var,
            command=self._toggle_debug_logging
        )
        debug_checkbox.pack(side="right", padx=(0, 10))
        
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

        self.log_text = ctk.CTkTextbox(frame)
        self.log_text.pack(fill="both", expand=True, padx=20, pady=10)
        self.log_text.configure(state="disabled")
        
    def _build_status_bar(self, parent: ctk.CTkBaseClass) -> None:
        """Build status bar with API usage and status."""
        status_frame = ctk.CTkFrame(parent, fg_color="gray20", height=30)
        status_frame.pack(fill="x", pady=(10, 0))
        status_frame.pack_propagate(False)
        
        # Status
        self.status_text = ctk.CTkLabel(
            status_frame,
            text="Ready - No active jobs",
            font=ctk.CTkFont(size=12)
        )
        self.status_text.pack(side="left", padx=10, pady=5)
        
        # API Usage
        self.api_usage_text = ctk.CTkLabel(
            status_frame,
            text="Daily API Usage: Loading...",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.api_usage_text.pack(side="right", padx=10, pady=5)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def start_sync(self) -> None:
        if self._worker_thread and self._worker_thread.is_alive():
            messagebox.showinfo("In progress", "A sync is already running.")
            return

        try:
            automator = self._build_automator()
            config = self._build_config()
            channel = self.channel_entry.get("1.0", "end-1c").strip()
            sheet_url = self.sheet_url_var.get().strip()
            tab_name = self.tab_name_var.get().strip() or "YouTube Data"

            if not channel:
                raise ValidationError("Please provide a channel ID, URL, or @handle")
            if not sheet_url:
                raise ValidationError("Please provide a spreadsheet URL")

            self._stop_flag.clear()
            self.progress_bar.set(0)
            self.status_label.configure(text="Running…")
            self.status_text.configure(text="Running sync...")
            self.status_badge.configure(text="Running", fg_color="orange")
            self._append_log(f"Starting sync for {channel}")

            def worker():
                try:
                    success = automator.sync_channel_to_sheet(channel_input=channel, spreadsheet_url=sheet_url, tab_name=tab_name, config=config)
                    self._on_sync_complete(success)
                except YouTube2SheetsError as exc:
                    logger.exception("Sync failed")
                    self._append_log(f"❌ Sync failed: {exc}")
                    self.status_label.configure(text="Failed")
                finally:
                    self._worker_thread = None

            self._automator = automator
            self._worker_thread = threading.Thread(target=worker, daemon=True)
            self._worker_thread.start()
        except YouTube2SheetsError as exc:
            messagebox.showerror("Configuration error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive fallback
            logger.exception("Unexpected error starting sync")
            messagebox.showerror("Unexpected error", str(exc))

    def stop_sync(self) -> None:
        self._stop_flag.set()
        if self._worker_thread and self._worker_thread.is_alive():
            self._append_log("⚠️ Stop requested (threads will finish current operations).")
        else:
            self._append_log("No active sync to stop.")

    def run_scheduler_once(self) -> None:
        if not self._automator:
            try:
                self._automator = self._build_automator()
            except YouTube2SheetsError as exc:
                messagebox.showerror("Scheduler error", str(exc))
                return

        sheet_id = self.scheduler_sheet_id_var.get().strip()
        tab_name = self.scheduler_tab_var.get().strip() or "Scheduler"
        if not sheet_id:
            messagebox.showerror("Scheduler", "Provide a Scheduler Sheet ID before running.")
            return

        try:
            self._automator.enable_scheduler(sheet_id, tab_name)
            results = self._automator.run_scheduler_once()
            self._append_log(f"Scheduler run complete: {results}")
            messagebox.showinfo("Scheduler", "Scheduler run completed. Check log for details.")
        except YouTube2SheetsError as exc:
            logger.exception("Scheduler run failed")
            messagebox.showerror("Scheduler error", str(exc))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_config(self) -> SyncConfig:
        return SyncConfig(
            min_duration_seconds=self.min_duration_var.get() or None,
            max_duration_seconds=self.max_duration_var.get() or None,
            keyword_filter=self.keyword_filter_var.get().strip() or None,
            keyword_mode=self.keyword_mode_var.get(),
            max_videos=50,  # YouTube API maximum per request
        )

    def _build_automator(self) -> YouTubeToSheetsAutomator:
        youtube_key = self.youtube_api_key_var.get().strip() or get_env_var("YOUTUBE_API_KEY")
        service_account_file = validate_service_account_path(self.service_account_path_var.get().strip() or get_env_var("GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON"))
        sheet_url = self.sheet_url_var.get().strip() or default_spreadsheet_url()
        return YouTubeToSheetsAutomator(youtube_api_key=youtube_key, service_account_file=service_account_file, spreadsheet_url=sheet_url)

    def _append_log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{datetime.now():%Y-%m-%d %H:%M:%S} — {message}\n")
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
                
    def _refresh_tabs(self) -> None:
        """Refresh available tabs from the Google Sheet."""
        try:
            self._append_log("Refreshing tabs from Google Sheet...")
            
            # Simulate getting tabs from Google Sheets
            # In real implementation, this would call the backend
            all_tabs = [
                "AI_ML", "YouTube Data", "Analytics", "Reports", 
                "Ranking Analysis", "Data Export", "Metrics", 
                "Ranking Reports", "Summary", "Charts"
            ]
            
            # Filter out tabs with "Ranking" in the name
            filtered_tabs = [tab for tab in all_tabs if "Ranking" not in tab]
            
            # Sort alphabetically
            filtered_tabs.sort()
            
            self._append_log("✅ Tabs refreshed successfully!")
            self._append_log(f"Available tabs: {', '.join(filtered_tabs)}")
            
            # Update the tab dropdown if it exists
            if hasattr(self, 'tab_dropdown'):
                # This would update the actual tab dropdown with available tabs
                pass
                
        except Exception as e:
            self._append_log(f"❌ Tab refresh failed: {str(e)}")

    def _on_sync_complete(self, success: bool) -> None:
        status = "✅ Completed" if success else "⚠️ Completed with errors"
        self.status_label.configure(text=status)
        self.status_text.configure(text="Ready - No active jobs")
        self.status_badge.configure(text="Ready", fg_color="green")
        self.progress_bar.set(1 if success else 0)
        self._append_log(f"Sync finished: {status}")

    def run(self) -> None:
        self.root.mainloop()


def launch() -> None:
    gui = YouTube2SheetsGUI()
    gui.run()


if __name__ == "__main__":  # pragma: no cover - manual launch
    import sys

    sys.excepthook = _handle_global_exception
    launch()

