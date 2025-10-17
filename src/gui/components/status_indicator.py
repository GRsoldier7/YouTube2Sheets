"""
Status Indicator Component
Professional status display with color-coded states
"""

import customtkinter as ctk
from typing import Literal

StatusType = Literal["ready", "running", "success", "error", "warning"]


class StatusIndicator(ctk.CTkFrame):
    """Professional status indicator with color-coded visual feedback"""

    COLORS = {
        "ready": "#00FF9D",      # Bright green
        "running": "#00D9FF",    # Cyan
        "success": "#00FF9D",    # Green
        "error": "#FF4D6A",      # Red
        "warning": "#FFC107",    # Yellow/Orange
    }

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.indicator = ctk.CTkLabel(
            self,
            text="●",
            font=ctk.CTkFont(size=18),
            text_color=self.COLORS["ready"]
        )
        self.indicator.pack(side="left", padx=(0, 5))
        
        self.text = ctk.CTkLabel(
            self,
            text="Ready",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FFFFFF"
        )
        self.text.pack(side="left")
    
    def update_status(self, message: str, status_type: StatusType = "ready"):
        """Update the status indicator"""
        color = self.COLORS.get(status_type, self.COLORS["ready"])
        self.indicator.configure(text_color=color)
        self.text.configure(text=message)

