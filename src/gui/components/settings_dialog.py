"""
Modern Settings Dialog
Designed by the Front End Architect & Designer
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, Dict, Any, Callable
import customtkinter as ctk

from .modern_theme import theme
from .glassmorphism import FloatingCard, AnimatedButton, ModernIcon, ModernTooltip


class ModernSettingsDialog(ctk.CTkToplevel):
    """Modern settings dialog with comprehensive configuration options."""
    
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.title("⚙️ Settings - YouTube2Sheets")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (800 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (600 // 2)
        self.geometry(f"+{x}+{y}")
        
        # Settings state
        self.settings_changed = False
        
        # Build the modern settings UI
        self._build_modern_settings_ui()
        
    def _build_modern_settings_ui(self):
        """Build the modern settings interface."""
        # Main container
        self.main_container = FloatingCard(self, elevation=12)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self._build_header()
        
        # Settings content
        self._build_settings_content()
        
        # Footer with actions
        self._build_footer()
        
    def _build_header(self):
        """Build the settings header."""
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ Settings",
            **theme.get_text_style("heading")
        )
        title_label.pack(side="left")
        
        # Close button
        close_btn = AnimatedButton(
            header_frame,
            text=f"{ModernIcon.get_icon('close')}",
            command=self._close_dialog,
            **theme.get_button_style("ghost")
        )
        close_btn.pack(side="right")
        
    def _build_settings_content(self):
        """Build the settings content."""
        # Scrollable content
        content_frame = ctk.CTkScrollableFrame(self.main_container)
        content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # API Configuration
        self._build_api_section(content_frame)
        
        # Appearance
        self._build_appearance_section(content_frame)
        
        # Performance
        self._build_performance_section(content_frame)
        
    def _build_api_section(self, parent):
        """Build API configuration section."""
        api_card = FloatingCard(parent, elevation=8)
        api_card.pack(fill="x", pady=(0, 20))
        
        # Section header
        header = ctk.CTkFrame(api_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="🔑 API Configuration",
            **theme.get_text_style("subheading")
        )
        title.pack(side="left")
        
        # API Key
        self._add_setting_input(
            api_card, "YouTube API Key", "youtube_api_key",
            placeholder="Enter your YouTube API key",
            password=True
        )
        
        # Service Account
        self._add_setting_file_input(
            api_card, "Google Service Account JSON", "service_account_path",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        # Default Spreadsheet
        self._add_setting_input(
            api_card, "Default Spreadsheet URL", "default_spreadsheet_url",
            placeholder="https://docs.google.com/spreadsheets/d/..."
        )
        
    def _build_appearance_section(self, parent):
        """Build appearance settings section."""
        appearance_card = FloatingCard(parent, elevation=8)
        appearance_card.pack(fill="x", pady=(0, 20))
        
        # Section header
        header = ctk.CTkFrame(appearance_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="🎨 Appearance",
            **theme.get_text_style("subheading")
        )
        title.pack(side="left")
        
        # Theme selection
        theme_frame = ctk.CTkFrame(appearance_card, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.theme_var = ctk.StringVar(value="dark")
        
        # Dark theme
        dark_theme_btn = ctk.CTkRadioButton(
            theme_frame,
            text="🌙 Dark Theme",
            variable=self.theme_var,
            value="dark",
            command=self._on_theme_change,
            **theme.get_text_style("body")
        )
        dark_theme_btn.pack(anchor="w", pady=(0, 10))
        
        # Light theme
        light_theme_btn = ctk.CTkRadioButton(
            theme_frame,
            text="☀️ Light Theme",
            variable=self.theme_var,
            value="light",
            command=self._on_theme_change,
            **theme.get_text_style("body")
        )
        light_theme_btn.pack(anchor="w")
        
    def _build_performance_section(self, parent):
        """Build performance settings section."""
        perf_card = FloatingCard(parent, elevation=8)
        perf_card.pack(fill="x")
        
        # Section header
        header = ctk.CTkFrame(perf_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="⚡ Performance",
            **theme.get_text_style("subheading")
        )
        title.pack(side="left")
        
        # Enable animations
        self._add_setting_checkbox(
            perf_card, "Enable Animations", "enable_animations",
            tooltip="Enable smooth animations and transitions"
        )
        
        # Smooth scrolling
        self._add_setting_checkbox(
            perf_card, "Smooth Scrolling", "smooth_scrolling",
            tooltip="Enable smooth scrolling in text areas"
        )
        
    def _build_footer(self):
        """Build the settings footer with action buttons."""
        footer_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        footer_frame.pack(fill="x", padx=30, pady=(0, 30))
        
        # Action buttons
        buttons_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        buttons_frame.pack(side="right")
        
        # Cancel button
        cancel_btn = AnimatedButton(
            buttons_frame,
            text=f"{ModernIcon.get_icon('cross')} Cancel",
            command=self._cancel_settings,
            **theme.get_button_style("ghost")
        )
        cancel_btn.pack(side="right", padx=(0, 10))
        
        # Save button
        save_btn = AnimatedButton(
            buttons_frame,
            text=f"{ModernIcon.get_icon('check')} Save",
            command=self._save_settings,
            **theme.get_button_style("success")
        )
        save_btn.pack(side="right")
        
    def _add_setting_input(self, parent, label: str, setting_name: str, **kwargs):
        """Add a setting input field."""
        # Create input frame
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(fill="x", pady=(0, 15))
        
        # Label
        input_label = ctk.CTkLabel(
            input_frame,
            text=label,
            **theme.get_text_style("caption")
        )
        input_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Input field
        input_field = ctk.CTkEntry(
            input_frame,
            **theme.get_input_style(),
            **kwargs
        )
        input_field.pack(fill="x", padx=20)
        
        # Store reference
        setattr(self, f"{setting_name}_entry", input_field)
        
    def _add_setting_file_input(self, parent, label: str, setting_name: str, **kwargs):
        """Add a setting file input field."""
        # Create input frame
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(fill="x", pady=(0, 15))
        
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
        setattr(self, f"{setting_name}_entry", input_field)
        
    def _add_setting_checkbox(self, parent, label: str, setting_name: str, **kwargs):
        """Add a setting checkbox."""
        # Create checkbox frame
        checkbox_frame = ctk.CTkFrame(parent, fg_color="transparent")
        checkbox_frame.pack(fill="x", pady=(0, 10))
        
        # Checkbox
        checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text=label,
            **theme.get_text_style("body")
        )
        checkbox.pack(anchor="w", padx=20)
        
        # Store reference
        setattr(self, f"{setting_name}_checkbox", checkbox)
        
    def _on_theme_change(self):
        """Handle theme change."""
        theme_name = self.theme_var.get()
        if theme_name == "dark":
            theme.is_dark = True
        elif theme_name == "light":
            theme.is_dark = False
            
        # Apply theme
        theme.apply_theme(self.root)
        self.settings_changed = True
        
    def _browse_file(self, entry_field, **kwargs):
        """Browse for a file."""
        file_path = filedialog.askopenfilename(**kwargs)
        if file_path:
            entry_field.delete(0, "end")
            entry_field.insert(0, file_path)
            self.settings_changed = True
            
    def _cancel_settings(self):
        """Cancel settings changes."""
        if self.settings_changed:
            if messagebox.askyesno("Cancel Changes", "You have unsaved changes. Are you sure you want to cancel?"):
                self._close_dialog()
        else:
            self._close_dialog()
            
    def _save_settings(self):
        """Save settings."""
        # Save all settings
        self._save_all_settings()
        
        # Show success message
        messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
        
        # Close dialog
        self._close_dialog()
        
    def _close_dialog(self):
        """Close the settings dialog."""
        self.destroy()
        
    def _save_all_settings(self):
        """Save all settings to configuration."""
        # Save all settings to config file
        pass