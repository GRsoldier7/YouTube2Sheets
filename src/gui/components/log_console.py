"""
Log Console Component
Production-grade logging console with emoji support and export functionality
"""

import logging
from datetime import datetime
from pathlib import Path
from tkinter import messagebox
from typing import Literal

import customtkinter as ctk

LogLevel = Literal["info", "success", "error", "warning", "debug"]

logger = logging.getLogger(__name__)


class LogConsole(ctk.CTkFrame):
    """Beautiful logging console with real-time feedback"""

    EMOJI_MAP = {
        "info": "ℹ️",
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "debug": "🐛",
    }

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#242424", corner_radius=12, border_width=1, border_color="#3A3A3A", **kwargs)
        
        self._debug_enabled = False
        self._build_ui()
    
    def _build_ui(self):
        # Header with controls
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            header,
            text="● In the weeds logging (verbose)",
            font=ctk.CTkFont(size=13),
            text_color="#00D9FF"
        ).pack(side="left")
        
        self.status_label = ctk.CTkLabel(
            header,
            text="Ready to sync",
            font=ctk.CTkFont(size=12),
            text_color="#A0A0A0"
        )
        self.status_label.pack(side="left", padx=(10, 20))
        
        # Controls
        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.pack(side="right")
        
        self.debug_checkbox = ctk.CTkCheckBox(
            controls,
            text="🐛 Debug Logging",
            command=self._toggle_debug,
            width=24,
            height=24,
            checkbox_width=20,
            checkbox_height=20,
            fg_color="#00D9FF",
            hover_color="#00B8E6",
            font=ctk.CTkFont(size=11)
        )
        self.debug_checkbox.pack(side="left", padx=5)
        
        ctk.CTkButton(
            controls,
            text="🗑️ Clear",
            command=self.clear,
            width=80,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#3A3A3A",
            hover_color="#4A4A4A",
            corner_radius=6
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            controls,
            text="📤 Export",
            command=self.export,
            width=90,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#3A3A3A",
            hover_color="#4A4A4A",
            corner_radius=6
        ).pack(side="left", padx=5)
        
        # Log textbox
        self.textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#1A1A1A",
            corner_radius=8,
            wrap="word"
        )
        self.textbox.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.textbox.configure(state="disabled")
        
        # Enable mouse wheel scrolling
        self._bind_mousewheel()
    
    def _bind_mousewheel(self):
        """Enable smooth mouse wheel scrolling"""
        def on_mouse_wheel(event):
            self.textbox.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.textbox.bind("<MouseWheel>", on_mouse_wheel)
        self.textbox.bind("<Enter>", lambda e: self.textbox.focus_set())
    
    def log(self, message: str, level: LogLevel = "info"):
        """Add a log message with emoji and timestamp"""
        if level == "debug" and not self._debug_enabled:
            return  # Skip debug messages if debug mode is off
        
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        emoji = self.EMOJI_MAP.get(level, "")
        formatted = f"{timestamp} {emoji} {message}\n"
        
        self.textbox.configure(state="normal")
        self.textbox.insert("end", formatted)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")
        
        # Also log to Python logger
        log_method = getattr(logger, level if level != "success" else "info")
        log_method(message)
    
    def _toggle_debug(self):
        """Toggle debug logging mode"""
        self._debug_enabled = not self._debug_enabled
        level = "DEBUG" if self._debug_enabled else "INFO"
        logging.getLogger().setLevel(level)
        self.log(f"Debug logging {'enabled' if self._debug_enabled else 'disabled'}", "info")
    
    def clear(self):
        """Clear the log console"""
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")
        self.log("Logs cleared", "info")
    
    def export(self):
        """Export logs to a file"""
        content = self.textbox.get("1.0", "end")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/export_{timestamp}.log"
        
        Path("logs").mkdir(exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.log(f"Logs exported to {filename}", "success")
        messagebox.showinfo("Export Logs", f"Logs exported successfully to:\n{filename}")
    
    def update_status(self, text: str):
        """Update the status label"""
        self.status_label.configure(text=text)

