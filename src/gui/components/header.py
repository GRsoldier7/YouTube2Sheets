"""
Header Component
Application header with title, subtitle, status, and settings button
"""

import customtkinter as ctk
from .status_indicator import StatusIndicator


class Header(ctk.CTkFrame):
    """Professional application header"""

    def __init__(self, parent, on_settings_click, **kwargs):
        super().__init__(parent, fg_color="transparent", height=60, **kwargs)
        self.pack_propagate(False)
        
        self.on_settings_click = on_settings_click
        self._build_ui()
    
    def _build_ui(self):
        # Left: Title and subtitle
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", fill="y")
        
        title_container = ctk.CTkFrame(left, fg_color="transparent")
        title_container.pack(anchor="w")
        
        # Icon
        ctk.CTkLabel(
            title_container,
            text="📺",
            font=ctk.CTkFont(size=28)
        ).pack(side="left", padx=(0, 10))
        
        # Text
        text_container = ctk.CTkFrame(title_container, fg_color="transparent")
        text_container.pack(side="left")
        
        ctk.CTkLabel(
            text_container,
            text="YouTube2Sheets",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            text_container,
            text="Professional YouTube Automation Suite",
            font=ctk.CTkFont(size=12),
            text_color="#A0A0A0"
        ).pack(anchor="w")
        
        # Right: Status and Settings
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right", fill="y", padx=(0, 10))
        
        # Status indicator
        self.status_indicator = StatusIndicator(right)
        self.status_indicator.pack(side="left", padx=(0, 20))
        
        # Settings button
        ctk.CTkButton(
            right,
            text="⚙️ Settings",
            command=self.on_settings_click,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3A3A3A",
            hover_color="#4A4A4A",
            corner_radius=10
        ).pack(side="left")
    
    def update_status(self, message: str, status_type: str = "ready"):
        """Update the status indicator"""
        self.status_indicator.update_status(message, status_type)

