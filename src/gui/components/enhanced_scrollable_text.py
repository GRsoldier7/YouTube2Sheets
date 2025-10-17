"""
Enhanced Scrollable Text Widget with Smooth Scrolling and Performance Optimizations
"""

from __future__ import annotations

import tkinter as tk
from typing import Optional, Callable
import customtkinter as ctk


class SmoothScrollableText(ctk.CTkTextbox):
    """
    Enhanced text widget with smooth scrolling, momentum, and performance optimizations.
    """
    
    def __init__(
        self,
        master,
        smooth_scroll: bool = True,
        scroll_speed: float = 0.1,
        momentum: bool = True,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.smooth_scroll = smooth_scroll
        self.scroll_speed = scroll_speed
        self.momentum = momentum
        
        # Smooth scrolling state
        self._scroll_velocity = 0
        self._scroll_target = 0
        self._scroll_animation_id = None
        self._is_scrolling = False
        
        # Performance optimizations
        self._update_pending = False
        self._last_scroll_time = 0
        
        # Bind events for smooth scrolling
        self._bind_scroll_events()
        
    def _bind_scroll_events(self):
        """Bind mouse wheel and scroll events for smooth scrolling."""
        # Mouse wheel events
        self.bind("<MouseWheel>", self._on_mouse_wheel)
        self.bind("<Button-4>", self._on_mouse_wheel)  # Linux scroll up
        self.bind("<Button-5>", self._on_mouse_wheel)  # Linux scroll down
        
        # Touchpad scroll events
        self.bind("<Shift-MouseWheel>", self._on_mouse_wheel)
        
        # Keyboard scroll events
        self.bind("<Up>", self._on_key_scroll)
        self.bind("<Down>", self._on_key_scroll)
        self.bind("<Page_Up>", self._on_key_scroll)
        self.bind("<Page_Down>", self._on_key_scroll)
        self.bind("<Home>", self._on_key_scroll)
        self.bind("<End>", self._on_key_scroll)
        
    def _on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling with smooth animation."""
        if not self.smooth_scroll:
            return
            
        # Calculate scroll direction and amount
        if event.delta:
            delta = event.delta
        elif event.num == 4:
            delta = 120
        elif event.num == 5:
            delta = -120
        else:
            delta = 0
            
        if delta == 0:
            return
            
        # Calculate scroll amount based on delta
        scroll_amount = -delta / 120 * 3  # 3 lines per wheel click
        
        # Apply momentum if enabled
        if self.momentum:
            self._scroll_velocity += scroll_amount * self.scroll_speed
        else:
            self._scroll_velocity = scroll_amount * self.scroll_speed
            
        # Start smooth scrolling animation
        self._start_smooth_scroll()
        
        return "break"
        
    def _on_key_scroll(self, event):
        """Handle keyboard scrolling with smooth animation."""
        if not self.smooth_scroll:
            return
            
        scroll_amount = 0
        if event.keysym == "Up":
            scroll_amount = -1
        elif event.keysym == "Down":
            scroll_amount = 1
        elif event.keysym == "Page_Up":
            scroll_amount = -10
        elif event.keysym == "Page_Down":
            scroll_amount = 10
        elif event.keysym == "Home":
            self.see("1.0")
            return
        elif event.keysym == "End":
            self.see("end")
            return
            
        if scroll_amount != 0:
            self._scroll_velocity = scroll_amount * self.scroll_speed
            self._start_smooth_scroll()
            
        return "break"
        
    def _start_smooth_scroll(self):
        """Start the smooth scrolling animation."""
        if self._scroll_animation_id:
            self.after_cancel(self._scroll_animation_id)
            
        self._is_scrolling = True
        self._animate_scroll()
        
    def _animate_scroll(self):
        """Animate smooth scrolling with momentum."""
        if not self._is_scrolling or abs(self._scroll_velocity) < 0.1:
            self._is_scrolling = False
            self._scroll_velocity = 0
            return
            
        # Apply scroll
        if self._scroll_velocity > 0:
            self.yview_scroll(int(self._scroll_velocity), "units")
        else:
            self.yview_scroll(int(self._scroll_velocity), "units")
            
        # Apply momentum (gradual deceleration)
        if self.momentum:
            self._scroll_velocity *= 0.9  # Deceleration factor
            
        # Schedule next frame
        self._scroll_animation_id = self.after(16, self._animate_scroll)  # ~60 FPS
        
    def smooth_scroll_to_top(self):
        """Smoothly scroll to the top of the text."""
        self._scroll_velocity = -50
        self._start_smooth_scroll()
        
    def smooth_scroll_to_bottom(self):
        """Smoothly scroll to the bottom of the text."""
        self._scroll_velocity = 50
        self._start_smooth_scroll()
        
    def smooth_scroll_to_line(self, line_number: int):
        """Smoothly scroll to a specific line number."""
        self.see(f"{line_number}.0")
        
    def append_text(self, text: str, scroll_to_bottom: bool = True):
        """Append text with optional smooth scrolling to bottom."""
        self.configure(state="normal")
        self.insert("end", text)
        if scroll_to_bottom:
            self.smooth_scroll_to_bottom()
        self.configure(state="disabled")
        
    def clear_text(self):
        """Clear all text content."""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")
        
    def get_line_count(self) -> int:
        """Get the total number of lines in the text widget."""
        return int(self.index("end-1c").split('.')[0])
        
    def get_visible_line_range(self) -> tuple[int, int]:
        """Get the range of visible lines."""
        top_line = int(self.index("@0,0").split('.')[0])
        bottom_line = int(self.index("@0,{}".format(self.winfo_height())).split('.')[0])
        return top_line, bottom_line


class EnhancedLogConsole(SmoothScrollableText):
    """
    Enhanced log console with real-time updates and performance optimizations.
    """
    
    def __init__(self, master, max_lines: int = 1000, **kwargs):
        super().__init__(master, **kwargs)
        self.max_lines = max_lines
        self._line_count = 0
        
    def append_log(self, message: str, level: str = "INFO", color: str = None):
        """Append a log message with optional color coding."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding for different log levels
        if not color:
            if level == "ERROR":
                color = "#FF6B6B"
            elif level == "WARNING":
                color = "#FFD93D"
            elif level == "SUCCESS":
                color = "#6BCF7F"
            elif level == "INFO":
                color = "#4DABF7"
            else:
                color = "#FFFFFF"
                
        # Format log message
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        # Append with color
        self.configure(state="normal")
        self.insert("end", formatted_message)
        
        # Apply color to the last line
        start_index = f"end-{len(formatted_message)}c"
        end_index = "end-1c"
        self.tag_add(f"log_{level}", start_index, end_index)
        # Configure tag colors - CTkTextbox uses different method
        try:
            self.tag_configure(f"log_{level}", foreground=color)
        except AttributeError:
            # Fallback for CTkTextbox - use configure method
            self.configure(tag_foreground=color)
        
        # Manage line count
        self._line_count += 1
        if self._line_count > self.max_lines:
            self._trim_old_lines()
            
        self.configure(state="disabled")
        self.smooth_scroll_to_bottom()
        
    def _trim_old_lines(self):
        """Remove old lines to maintain performance."""
        lines_to_remove = self._line_count - self.max_lines
        if lines_to_remove > 0:
            self.configure(state="normal")
            self.delete("1.0", f"{lines_to_remove}.0")
            self.configure(state="disabled")
            self._line_count = self.max_lines
            
    def clear_logs(self):
        """Clear all log messages."""
        self.clear_text()
        self._line_count = 0
