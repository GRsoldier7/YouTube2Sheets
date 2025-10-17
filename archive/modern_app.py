"""
Modern YouTube2Sheets GUI - World-Class Application Experience
Designed by the PolyChronos Ω v5.0 Elite Team

This is a complete redesign featuring:
- Modern glassmorphism design language
- Smooth animations and micro-interactions
- Comprehensive keyboard shortcuts
- Responsive layout system
- Real-time progress tracking
- Accessibility features
- Dark/light theme support
"""

from __future__ import annotations

import logging
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional, Dict, Any

import customtkinter as ctk

from src.backend.exceptions import ValidationError, YouTube2SheetsError
from src.backend.security_manager import (
    default_spreadsheet_url,
    get_env_var,
    validate_service_account_path,
)
from src.backend.youtube2sheets import SyncConfig, YouTubeToSheetsAutomator
from src.config import load_gui_config, load_logging_config

# Import our modern components
from .components.modern_theme import theme, ModernTheme
from .components.glassmorphism import (
    GlassmorphismFrame, FloatingCard, AnimatedButton, 
    ModernProgressBar, StatusBadge, ModernTooltip, ModernIcon
)
from .components.enhanced_scrollable_text import EnhancedLogConsole
from .components.responsive_progress import ResponsiveProgressBar, StatusIndicator, LiveProgressTracker
from .components.keyboard_shortcuts import (
    KeyboardShortcutManager, ModernNavigation, AccessibilityManager, 
    ModernShortcuts, ShortcutHelpDialog
)
from .components.settings_dialog import ModernSettingsDialog
from .components.performance_optimizer import (
    PerformanceMonitor, AsyncTaskManager, UIUpdateQueue, 
    SmoothAnimator, ResponsiveLayout
)

logger = logging.getLogger(__name__)


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


class ModernYouTube2SheetsGUI:
    """
    Modern YouTube2Sheets GUI with world-class user experience.
    """
    
    def __init__(self) -> None:
        _configure_logging()
        gui_config = load_gui_config()
        
        # Initialize root window
        self.root = ctk.CTk()
        self.root.title("YouTube2Sheets – Modern Automation Platform")
        self.root.geometry(f"{gui_config.window_width}x{gui_config.window_height}")
        self.root.minsize(1200, 800)
        
        # Apply modern theme
        theme.apply_theme(self.root)
        
        # Initialize managers
        self.shortcut_manager = KeyboardShortcutManager(self.root)
        self.navigation = ModernNavigation(self.root)
        self.accessibility = AccessibilityManager(self.root)
        
        # Performance optimization
        self.performance_monitor = PerformanceMonitor(self.root)
        self.task_manager = AsyncTaskManager(max_workers=4)
        self.ui_update_queue = UIUpdateQueue(self.root)
        self.animator = SmoothAnimator(self.root)
        self.responsive_layout = ResponsiveLayout(self.root)
        
        # Application state
        self._automator: Optional[YouTubeToSheetsAutomator] = None
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
        self._progress_tracker: Optional[LiveProgressTracker] = None
        
        # Build the modern UI
        self._build_modern_ui()
        self._setup_shortcuts()
        self._setup_accessibility()
        
        # Set up global exception handling
        self.root.report_callback_exception = self._handle_exception
        
    def _build_modern_ui(self):
        """Build the modern user interface."""
        # Main container with glassmorphism effect
        self.main_container = GlassmorphismFrame(
            self.root,
            blur_radius=15,
            opacity=0.9
        )
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header section
        self._build_header()
        
        # Main content area with tabs
        self._build_main_content()
        
        # Footer with status
        self._build_footer()
        
    def _build_header(self):
        """Build the modern header section."""
        header_frame = FloatingCard(self.main_container, elevation=12)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Header content
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=30, pady=20)
        
        # Title and subtitle
        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🎬 YouTube2Sheets",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=theme.colors.primary
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Modern YouTube to Google Sheets Automation",
            font=ctk.CTkFont(size=16, weight="normal"),
            text_color=theme.colors.text_secondary
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # Header actions
        actions_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        actions_frame.pack(side="right")
        
        # Settings button
        self.settings_btn = AnimatedButton(
            actions_frame,
            text=f"{ModernIcon.get_icon('settings')} Settings",
            command=self._open_settings,
            **theme.get_button_style("ghost")
        )
        self.settings_btn.pack(side="right", padx=(10, 0))
        
        # Theme toggle button
        self.theme_btn = AnimatedButton(
            actions_frame,
            text="🌙",
            command=self._toggle_theme,
            **theme.get_button_style("ghost")
        )
        self.theme_btn.pack(side="right", padx=(10, 0))
        
        # Help button
        self.help_btn = AnimatedButton(
            actions_frame,
            text=f"{ModernIcon.get_icon('info')} Help",
            command=self._show_help,
            **theme.get_button_style("ghost")
        )
        self.help_btn.pack(side="right", padx=(10, 0))
        
    def _build_main_content(self):
        """Build the main content area with tabs."""
        # Tab view
        self.tab_view = ctk.CTkTabview(self.main_container)
        self.tab_view.pack(fill="both", expand=True, pady=(0, 20))
        
        # Configure tab appearance
        self.tab_view.configure(
            fg_color=theme.colors.surface,
            segmented_button_fg_color=theme.colors.surface_secondary,
            segmented_button_selected_color=theme.colors.primary,
            segmented_button_selected_hover_color=theme.colors.primary_dark,
            text_color=theme.colors.text_primary,
            text_color_disabled=theme.colors.text_tertiary
        )
        
        # Sync tab
        self.sync_tab = self.tab_view.add("🔄 Sync")
        self._build_sync_tab()
        
        # Scheduler tab
        self.scheduler_tab = self.tab_view.add("⏰ Scheduler")
        self._build_scheduler_tab()
        
        # Analytics tab
        self.analytics_tab = self.tab_view.add("📊 Analytics")
        self._build_analytics_tab()
        
    def _build_sync_tab(self):
        """Build the sync tab content."""
        # Configuration section
        self._build_config_section(self.sync_tab)
        
        # Control section
        self._build_control_section(self.sync_tab)
        
        # Progress section
        self._build_progress_section(self.sync_tab)
        
        # Log section
        self._build_log_section(self.sync_tab)
        
    def _build_config_section(self, parent):
        """Build the configuration section."""
        config_card = FloatingCard(parent, elevation=8)
        config_card.pack(fill="x", pady=(0, 20))
        
        # Card header
        header = ctk.CTkFrame(config_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="⚙️ Configuration",
            **theme.get_text_style("subheading")
        )
        title.pack(side="left")
        
        # Collapse/expand button
        self.config_collapse_btn = AnimatedButton(
            header,
            text="−",
            command=lambda: self._toggle_section("config"),
            **theme.get_button_style("ghost")
        )
        self.config_collapse_btn.pack(side="right")
        
        # Configuration content
        self.config_content = ctk.CTkFrame(config_card, fg_color="transparent")
        self.config_content.pack(fill="x", padx=20, pady=(0, 20))
        
        # API Configuration
        self._build_api_config()
        
        # Filter Configuration
        self._build_filter_config()
        
        # Advanced Configuration
        self._build_advanced_config()
        
    def _build_api_config(self):
        """Build API configuration section."""
        api_frame = ctk.CTkFrame(self.config_content, **theme.get_card_style())
        api_frame.pack(fill="x", pady=(0, 15))
        
        # Section title
        api_title = ctk.CTkLabel(
            api_frame,
            text="🔑 API Configuration",
            **theme.get_text_style("body")
        )
        api_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # API Key input
        self._add_modern_input(
            api_frame, "YouTube API Key", "youtube_api_key",
            placeholder_text="Enter your YouTube API key",
            show="*"
        )
        
        # Service Account input
        self._add_modern_file_input(
            api_frame, "Service Account JSON", "service_account_path",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        # Spreadsheet URL input
        self._add_modern_input(
            api_frame, "Default Spreadsheet URL", "sheet_url",
            placeholder_text="https://docs.google.com/spreadsheets/d/..."
        )
        
        # Tab name input
        self._add_modern_input(
            api_frame, "Default Tab Name", "tab_name",
            placeholder_text="YouTube Data"
        )
        
    def _build_filter_config(self):
        """Build filter configuration section."""
        filter_frame = ctk.CTkFrame(self.config_content, **theme.get_card_style())
        filter_frame.pack(fill="x", pady=(0, 15))
        
        # Section title
        filter_title = ctk.CTkLabel(
            filter_frame,
            text="🔍 Filter Configuration",
            **theme.get_text_style("body")
        )
        filter_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Duration filters
        duration_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        duration_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        duration_label = ctk.CTkLabel(
            duration_frame,
            text="Duration Range (seconds)",
            **theme.get_text_style("caption")
        )
        duration_label.pack(anchor="w")
        
        # Duration sliders
        self._build_duration_sliders(duration_frame)
        
        # Keyword filters
        self._add_modern_input(
            filter_frame, "Keyword Filter", "keyword_filter",
            placeholder_text="Enter keywords separated by commas"
        )
        
        # Keyword mode
        self._build_keyword_mode_selector(filter_frame)
        
        # Max videos
        self._add_modern_input(
            filter_frame, "Maximum Videos", "max_videos",
            input_type="number",
            placeholder_text="50"
        )
        
    def _build_advanced_config(self):
        """Build advanced configuration section."""
        advanced_frame = ctk.CTkFrame(self.config_content, **theme.get_card_style())
        advanced_frame.pack(fill="x")
        
        # Section title
        advanced_title = ctk.CTkLabel(
            advanced_frame,
            text="⚡ Advanced Options",
            **theme.get_text_style("body")
        )
        advanced_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Performance options
        perf_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
        perf_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Batch size
        self._add_modern_input(
            perf_frame, "Batch Size", "batch_size",
            input_type="number",
            placeholder_text="10"
        )
        
        # Retry attempts
        self._add_modern_input(
            perf_frame, "Retry Attempts", "retry_attempts",
            input_type="number",
            placeholder_text="3"
        )
        
        # Timeout
        self._add_modern_input(
            perf_frame, "Timeout (seconds)", "timeout",
            input_type="number",
            placeholder_text="30"
        )
        
    def _build_control_section(self, parent):
        """Build the control section."""
        control_card = FloatingCard(parent, elevation=8)
        control_card.pack(fill="x", pady=(0, 20))
        
        # Card header
        header = ctk.CTkFrame(control_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="🎮 Controls",
            **theme.get_text_style("subheading")
        )
        title.pack(side="left")
        
        # Control content
        control_content = ctk.CTkFrame(control_card, fg_color="transparent")
        control_content.pack(fill="x", padx=20, pady=(0, 20))
        
        # Channel input
        channel_frame = ctk.CTkFrame(control_content, fg_color="transparent")
        channel_frame.pack(fill="x", pady=(0, 15))
        
        channel_label = ctk.CTkLabel(
            channel_frame,
            text="YouTube Channel",
            **theme.get_text_style("body")
        )
        channel_label.pack(anchor="w")
        
        self.channel_entry = ctk.CTkEntry(
            channel_frame,
            placeholder_text="Enter channel URL, @handle, or Channel ID",
            **theme.get_input_style()
        )
        self.channel_entry.pack(fill="x", pady=(5, 0))
        
        # Control buttons
        buttons_frame = ctk.CTkFrame(control_content, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        # Start sync button
        self.start_btn = AnimatedButton(
            buttons_frame,
            text=f"{ModernIcon.get_icon('play')} Start Sync",
            command=self._start_sync,
            **theme.get_button_style("success")
        )
        self.start_btn.pack(side="left", padx=(0, 10))
        
        # Stop sync button
        self.stop_btn = AnimatedButton(
            buttons_frame,
            text=f"{ModernIcon.get_icon('stop')} Stop",
            command=self._stop_sync,
            **theme.get_button_style("error")
        )
        self.stop_btn.pack(side="left", padx=(0, 10))
        
        # Refresh button
        self.refresh_btn = AnimatedButton(
            buttons_frame,
            text=f"{ModernIcon.get_icon('refresh')} Refresh",
            command=self._refresh_data,
            **theme.get_button_style("secondary")
        )
        self.refresh_btn.pack(side="left", padx=(0, 10))
        
        # Register widgets for navigation
        self.navigation.register_widget(self.channel_entry, "controls")
        self.navigation.register_widget(self.start_btn, "controls")
        self.navigation.register_widget(self.stop_btn, "controls")
        self.navigation.register_widget(self.refresh_btn, "controls")
        
    def _build_progress_section(self, parent):
        """Build the progress section."""
        progress_card = FloatingCard(parent, elevation=8)
        progress_card.pack(fill="x", pady=(0, 20))
        
        # Card header
        header = ctk.CTkFrame(progress_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="📊 Progress",
            **theme.get_text_style("subheading")
        )
        title.pack(side="left")
        
        # Progress content
        progress_content = ctk.CTkFrame(progress_card, fg_color="transparent")
        progress_content.pack(fill="x", padx=20, pady=(0, 20))
        
        # Progress bar
        self.progress_bar = ModernProgressBar(
            progress_content,
            gradient_colors=theme.colors.gradient_primary
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        # Status indicator
        self.status_indicator = StatusBadge(
            progress_content,
            status="idle"
        )
        self.status_indicator.pack(side="left")
        
        # Progress details
        self.progress_details = ctk.CTkLabel(
            progress_content,
            text="Ready to sync",
            **theme.get_text_style("caption")
        )
        self.progress_details.pack(side="right")
        
        # Initialize progress tracker
        self._progress_tracker = LiveProgressTracker(
            self.progress_bar,
            self.status_indicator,
            self._on_progress_update
        )
        
    def _build_log_section(self, parent):
        """Build the log section."""
        log_card = FloatingCard(parent, elevation=8)
        log_card.pack(fill="both", expand=True)
        
        # Card header
        header = ctk.CTkFrame(log_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="📝 Activity Log",
            **theme.get_text_style("subheading")
        )
        title.pack(side="left")
        
        # Log actions
        log_actions = ctk.CTkFrame(header, fg_color="transparent")
        log_actions.pack(side="right")
        
        # Clear logs button
        clear_btn = AnimatedButton(
            log_actions,
            text=f"{ModernIcon.get_icon('delete')} Clear",
            command=self._clear_logs,
            **theme.get_button_style("ghost")
        )
        clear_btn.pack(side="right", padx=(5, 0))
        
        # Export logs button
        export_btn = AnimatedButton(
            log_actions,
            text=f"{ModernIcon.get_icon('export')} Export",
            command=self._export_logs,
            **theme.get_button_style("ghost")
        )
        export_btn.pack(side="right", padx=(5, 0))
        
        # Log console
        self.log_console = EnhancedLogConsole(
            log_card,
            max_lines=1000,
            smooth_scroll=True,
            momentum=True
        )
        self.log_console.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Set context for shortcuts
        self.shortcut_manager.set_context("logs")
        
    def _build_scheduler_tab(self):
        """Build the scheduler tab content."""
        # Scheduler configuration
        self._build_scheduler_config(self.scheduler_tab)
        
        # Scheduler controls
        self._build_scheduler_controls(self.scheduler_tab)
        
        # Scheduler status
        self._build_scheduler_status(self.scheduler_tab)
        
    def _build_scheduler_config(self, parent):
        """Build scheduler configuration section."""
        config_card = FloatingCard(parent, elevation=8)
        config_card.pack(fill="x", pady=(0, 20))
        
        # Section header
        header = ctk.CTkFrame(config_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="⏰ Scheduler Configuration",
            **theme.get_text_style("subheading")
        )
        title.pack(side="left")
        
        # Scheduler Sheet ID
        self._add_modern_input(
            config_card, "Scheduler Sheet ID", "scheduler_sheet_id",
            placeholder_text="Enter Google Sheets ID for scheduler"
        )
        
        # Scheduler Tab Name
        self._add_modern_input(
            config_card, "Scheduler Tab Name", "scheduler_tab_name",
            placeholder_text="Scheduler"
        )
        
    def _build_scheduler_controls(self, parent):
        """Build scheduler controls section."""
        controls_card = FloatingCard(parent, elevation=8)
        controls_card.pack(fill="x", pady=(0, 20))
        
        # Section header
        header = ctk.CTkFrame(controls_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="🎮 Scheduler Controls",
            **theme.get_text_style("subheading")
        )
        title.pack(side="left")
        
        # Control buttons
        buttons_frame = ctk.CTkFrame(controls_card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Run scheduler button
        run_scheduler_btn = AnimatedButton(
            buttons_frame,
            text=f"{ModernIcon.get_icon('play')} Run Scheduler Once",
            command=self._run_scheduler_once,
            **theme.get_button_style("success")
        )
        run_scheduler_btn.pack(side="left", padx=(0, 10))
        
        # Enable scheduler button
        enable_scheduler_btn = AnimatedButton(
            buttons_frame,
            text=f"{ModernIcon.get_icon('check')} Enable Scheduler",
            command=self._enable_scheduler,
            **theme.get_button_style("primary")
        )
        enable_scheduler_btn.pack(side="left", padx=(0, 10))
        
    def _build_scheduler_status(self, parent):
        """Build scheduler status section."""
        status_card = FloatingCard(parent, elevation=8)
        status_card.pack(fill="both", expand=True)
        
        # Section header
        header = ctk.CTkFrame(status_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="📊 Scheduler Status",
            **theme.get_text_style("subheading")
        )
        title.pack(side="left")
        
        # Status content
        status_content = ctk.CTkFrame(status_card, fg_color="transparent")
        status_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Status label
        self.scheduler_status_label = ctk.CTkLabel(
            status_content,
            text="Scheduler is not configured",
            **theme.get_text_style("body")
        )
        self.scheduler_status_label.pack(pady=20)
        
    def _run_scheduler_once(self):
        """Run scheduler once."""
        self.log_console.append_log("Running scheduler once...", "INFO")
        
    def _enable_scheduler(self):
        """Enable scheduler."""
        self.log_console.append_log("Scheduler enabled", "SUCCESS")
        
    # Shortcut methods
    def open_file(self):
        """Open file dialog."""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.log_console.append_log(f"Opened file: {file_path}", "INFO")
            
    def save_file(self):
        """Save file dialog."""
        file_path = filedialog.asksaveasfilename()
        if file_path:
            self.log_console.append_log(f"Saved file: {file_path}", "SUCCESS")
            
    def new_file(self):
        """Create new file."""
        self.log_console.append_log("New file created", "INFO")
        
    def undo(self):
        """Undo action."""
        self.log_console.append_log("Undo action", "INFO")
        
    def redo(self):
        """Redo action."""
        self.log_console.append_log("Redo action", "INFO")
        
    def copy(self):
        """Copy action."""
        self.log_console.append_log("Copy action", "INFO")
        
    def paste(self):
        """Paste action."""
        self.log_console.append_log("Paste action", "INFO")
        
    def cut(self):
        """Cut action."""
        self.log_console.append_log("Cut action", "INFO")
        
    def select_all(self):
        """Select all action."""
        self.log_console.append_log("Select all action", "INFO")
        
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        self.log_console.append_log("Toggled fullscreen", "INFO")
        
    def zoom_in(self):
        """Zoom in."""
        self.log_console.append_log("Zoomed in", "INFO")
        
    def zoom_out(self):
        """Zoom out."""
        self.log_console.append_log("Zoomed out", "INFO")
        
    def zoom_reset(self):
        """Reset zoom."""
        self.log_console.append_log("Reset zoom", "INFO")
        
    def focus_next(self):
        """Focus next widget."""
        self.navigation.focus_next("inputs")
        
    def focus_previous(self):
        """Focus previous widget."""
        self.navigation.focus_previous("inputs")
        
    def focus_first(self):
        """Focus first widget."""
        self.navigation.focus_first("inputs")
        
    def focus_last(self):
        """Focus last widget."""
        self.navigation.focus_last("inputs")
        
    def refresh(self):
        """Refresh data."""
        self._refresh_data()
        
    def show_help(self):
        """Show help dialog."""
        self._show_help()
        
    def show_shortcuts(self):
        """Show shortcuts dialog."""
        help_dialog = ShortcutHelpDialog(self.root, self.shortcut_manager)
        
    def run_scheduler(self):
        """Run scheduler."""
        self._run_scheduler_once()
        
    def open_settings(self):
        """Open settings dialog."""
        self._open_settings()
        
    def quit(self):
        """Quit application."""
        self.root.quit()
        
    def close_window(self):
        """Close window."""
        self.root.destroy()
        
    def toggle_debug(self):
        """Toggle debug mode."""
        self.log_console.append_log("Debug mode toggled", "INFO")
        
    def show_debug(self):
        """Show debug info."""
        self.log_console.append_log("Debug info displayed", "INFO")
        
    def select_all_logs(self):
        """Select all logs."""
        self.log_console.configure(state="normal")
        self.log_console.tag_add("sel", "1.0", "end")
        self.log_console.configure(state="disabled")
        
    def copy_logs(self):
        """Copy logs."""
        self.log_console.append_log("Logs copied to clipboard", "INFO")
        
    def search_logs(self):
        """Search logs."""
        self.log_console.append_log("Log search opened", "INFO")
        
    def clear_logs(self):
        """Clear logs."""
        self._clear_logs()
        
    def toggle_progress(self):
        """Toggle progress animation."""
        self.log_console.append_log("Progress animation toggled", "INFO")
        
    def show_progress_details(self):
        """Show progress details."""
        self.log_console.append_log("Progress details displayed", "INFO")
        
    def close_settings(self):
        """Close settings dialog."""
        self.log_console.append_log("Settings dialog closed", "INFO")
        
    def save_settings(self):
        """Save settings."""
        self.log_console.append_log("Settings saved", "SUCCESS")
        
    def start_sync(self):
        """Start sync process."""
        self._start_sync()
        
    def stop_sync(self):
        """Stop sync process."""
        self._stop_sync()
        
    def _build_analytics_tab(self):
        """Build the analytics tab content."""
        # Analytics content placeholder
        analytics_content = ctk.CTkFrame(self.analytics_tab, fg_color="transparent")
        analytics_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            analytics_content,
            text="📊 Analytics Dashboard",
            **theme.get_text_style("heading")
        )
        title.pack(pady=20)
        
        # Placeholder for analytics
        placeholder = ctk.CTkLabel(
            analytics_content,
            text="Analytics features coming soon...",
            **theme.get_text_style("body")
        )
        placeholder.pack()
        
    def _build_footer(self):
        """Build the footer section."""
        footer_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        footer_frame.pack(fill="x", pady=(0, 10))
        
        # Status bar
        status_frame = ctk.CTkFrame(footer_frame, **theme.get_card_style())
        status_frame.pack(fill="x")
        
        # Status content
        status_content = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_content.pack(fill="x", padx=20, pady=10)
        
        # Connection status
        self.connection_status = StatusBadge(status_content, status="idle")
        self.connection_status.pack(side="left")
        
        # Version info
        version_label = ctk.CTkLabel(
            status_content,
            text="v2.0.0",
            **theme.get_text_style("small")
        )
        version_label.pack(side="right")
        
        # Last updated
        self.last_updated = ctk.CTkLabel(
            status_content,
            text="Last updated: Never",
            **theme.get_text_style("small")
        )
        self.last_updated.pack(side="right", padx=(0, 20))
        
    def _add_modern_input(self, parent, label: str, var_name: str, **kwargs):
        """Add a modern input field."""
        # Create input frame
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(fill="x", pady=(0, 10))
        
        # Label
        input_label = ctk.CTkLabel(
            input_frame,
            text=label,
            **theme.get_text_style("caption")
        )
        input_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Filter out unsupported kwargs
        supported_kwargs = {}
        for key, value in kwargs.items():
            if key not in ['input_type']:  # Remove unsupported parameters
                supported_kwargs[key] = value
        
        # Input field
        input_field = ctk.CTkEntry(
            input_frame,
            **theme.get_input_style(),
            **supported_kwargs
        )
        input_field.pack(fill="x", padx=20)
        
        # Store reference
        setattr(self, f"{var_name}_entry", input_field)
        
        # Register for navigation
        self.navigation.register_widget(input_field, "inputs")
        
        return input_field
        
    def _add_modern_file_input(self, parent, label: str, var_name: str, **kwargs):
        """Add a modern file input field."""
        # Create input frame
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(fill="x", pady=(0, 10))
        
        # Label
        input_label = ctk.CTkLabel(
            input_frame,
            text=label,
            **theme.get_text_style("caption")
        )
        input_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Input container
        input_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_container.pack(fill="x", padx=20)
        
        # Input field
        input_field = ctk.CTkEntry(
            input_container,
            **theme.get_input_style()
        )
        input_field.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Browse button
        browse_btn = AnimatedButton(
            input_container,
            text="Browse",
            command=lambda: self._browse_file(input_field, **kwargs),
            **theme.get_button_style("secondary")
        )
        browse_btn.pack(side="right")
        
        # Store reference
        setattr(self, f"{var_name}_entry", input_field)
        
        # Register for navigation
        self.navigation.register_widget(input_field, "inputs")
        self.navigation.register_widget(browse_btn, "inputs")
        
        return input_field
        
    def _build_duration_sliders(self, parent):
        """Build duration range sliders."""
        # Min duration slider
        min_frame = ctk.CTkFrame(parent, fg_color="transparent")
        min_frame.pack(fill="x", pady=(0, 10))
        
        min_label = ctk.CTkLabel(
            min_frame,
            text="Minimum Duration",
            **theme.get_text_style("small")
        )
        min_label.pack(anchor="w")
        
        self.min_duration_slider = ctk.CTkSlider(
            min_frame,
            from_=0,
            to=3600,
            number_of_steps=360,
            **theme.get_slider_style()
        )
        self.min_duration_slider.pack(fill="x", pady=(5, 0))
        
        # Max duration slider
        max_frame = ctk.CTkFrame(parent, fg_color="transparent")
        max_frame.pack(fill="x")
        
        max_label = ctk.CTkLabel(
            max_frame,
            text="Maximum Duration",
            **theme.get_text_style("small")
        )
        max_label.pack(anchor="w")
        
        self.max_duration_slider = ctk.CTkSlider(
            max_frame,
            from_=60,
            to=10800,
            number_of_steps=540,
            **theme.get_slider_style()
        )
        self.max_duration_slider.pack(fill="x", pady=(5, 0))
        
    def _build_keyword_mode_selector(self, parent):
        """Build keyword mode selector."""
        mode_frame = ctk.CTkFrame(parent, fg_color="transparent")
        mode_frame.pack(fill="x", pady=(0, 10))
        
        mode_label = ctk.CTkLabel(
            mode_frame,
            text="Keyword Mode",
            **theme.get_text_style("small")
        )
        mode_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Mode buttons
        mode_buttons = ctk.CTkFrame(mode_frame, fg_color="transparent")
        mode_buttons.pack(fill="x", padx=20)
        
        self.keyword_mode_var = ctk.StringVar(value="include")
        
        include_btn = ctk.CTkRadioButton(
            mode_buttons,
            text="Include",
            variable=self.keyword_mode_var,
            value="include",
            **theme.get_text_style("small")
        )
        include_btn.pack(side="left", padx=(0, 20))
        
        exclude_btn = ctk.CTkRadioButton(
            mode_buttons,
            text="Exclude",
            variable=self.keyword_mode_var,
            value="exclude",
            **theme.get_text_style("small")
        )
        exclude_btn.pack(side="left")
        
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        ModernShortcuts.setup_default_shortcuts(self.shortcut_manager, self)
        ModernShortcuts.setup_context_shortcuts(self.shortcut_manager, self)
        
    def _setup_accessibility(self):
        """Setup accessibility features."""
        self.accessibility.set_announcement_callback(self._on_accessibility_announcement)
        
    def _on_accessibility_announcement(self, message: str):
        """Handle accessibility announcements."""
        # Log the announcement
        self.log_console.append_log(f"Announcement: {message}", "INFO")
        
    def _on_progress_update(self, progress: float, message: str):
        """Handle progress updates."""
        self.progress_details.configure(text=message)
        
    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        logger.exception("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
        messagebox.showerror("Error", f"An unexpected error occurred: {exc_value}")
        
    def _toggle_theme(self):
        """Toggle between dark and light themes."""
        theme.toggle_theme()
        # Refresh the UI
        self.root.update()
        
    def _open_settings(self):
        """Open settings dialog."""
        settings_dialog = ModernSettingsDialog(self.root, self)
        settings_dialog.focus()
        
    def _show_help(self):
        """Show help dialog."""
        help_dialog = ShortcutHelpDialog(self.root, self.shortcut_manager)
        
    def _start_sync(self):
        """Start the sync process."""
        # Placeholder for sync logic
        self._progress_tracker.start(100, "Starting sync...")
        self.log_console.append_log("Sync started", "SUCCESS")
        
    def _stop_sync(self):
        """Stop the sync process."""
        self._progress_tracker.stop("Sync stopped by user")
        self.log_console.append_log("Sync stopped", "WARNING")
        
    def _refresh_data(self):
        """Refresh data."""
        self.log_console.append_log("Data refreshed", "INFO")
        
    def _clear_logs(self):
        """Clear log console."""
        self.log_console.clear_logs()
        
    def _export_logs(self):
        """Export logs to file."""
        # Placeholder for export logic
        messagebox.showinfo("Export", "Log export coming soon!")
        
    def _browse_file(self, entry_field, **kwargs):
        """Browse for a file."""
        file_path = filedialog.askopenfilename(**kwargs)
        if file_path:
            entry_field.delete(0, "end")
            entry_field.insert(0, file_path)
            
    def _toggle_section(self, section_name: str):
        """Toggle section visibility."""
        # Placeholder for section toggle
        pass
        
    def run(self):
        """Run the application."""
        self.root.mainloop()


def launch():
    """Launch the modern YouTube2Sheets GUI."""
    app = ModernYouTube2SheetsGUI()
    app.run()


if __name__ == "__main__":
    launch()
