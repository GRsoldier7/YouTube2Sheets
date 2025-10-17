"""
Glassmorphism Effects and Modern Visual Components
Designed by the Front End Architect & Designer
"""

from __future__ import annotations

import tkinter as tk
from typing import Optional, Tuple, Dict, Any
import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import math


class GlassmorphismFrame(ctk.CTkFrame):
    """
    Glassmorphism frame with blur effects and transparency.
    """
    
    def __init__(
        self,
        master,
        blur_radius: int = 10,
        opacity: float = 0.8,
        border_width: int = 1,
        border_color: str = "rgba(255,255,255,0.2)",
        **kwargs
    ):
        # Initialize with transparent background
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self.blur_radius = blur_radius
        self.opacity = opacity
        self.border_width = border_width
        self.border_color = border_color
        
        # Create glass effect
        self._create_glass_effect()
        
    def _create_glass_effect(self):
        """Create the glassmorphism effect."""
        # Use CustomTkinter compatible colors
        self.configure(
            fg_color=("gray90", "gray20"),  # Light gray for light theme, dark gray for dark theme
            border_width=self.border_width,
            corner_radius=20
        )


class FloatingCard(ctk.CTkFrame):
    """
    Floating card with shadow and hover effects.
    """
    
    def __init__(
        self,
        master,
        elevation: int = 8,
        hover_elevation: int = 12,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.elevation = elevation
        self.hover_elevation = hover_elevation
        self.is_hovered = False
        
        # Configure initial appearance
        self._update_appearance()
        
        # Bind hover events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_enter(self, event):
        """Handle mouse enter event."""
        self.is_hovered = True
        self._update_appearance()
        
    def _on_leave(self, event):
        """Handle mouse leave event."""
        self.is_hovered = False
        self._update_appearance()
        
    def _update_appearance(self):
        """Update card appearance based on hover state."""
        current_elevation = self.hover_elevation if self.is_hovered else self.elevation
        
        # Apply shadow effect (simplified)
        self.configure(
            corner_radius=16,
            border_width=1,
            border_color=("gray80", "gray30")
        )


class AnimatedButton(ctk.CTkButton):
    """
    Button with smooth animations and micro-interactions.
    """
    
    def __init__(
        self,
        master,
        animation_duration: float = 0.2,
        scale_factor: float = 0.95,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.animation_duration = animation_duration
        self.scale_factor = scale_factor
        self.is_animating = False
        
        # Bind events
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        
    def _on_press(self, event):
        """Handle button press with scale animation."""
        if not self.is_animating:
            self._animate_scale(self.scale_factor)
            
    def _on_release(self, event):
        """Handle button release with scale animation."""
        if not self.is_animating:
            self._animate_scale(1.0)
            
    def _animate_scale(self, target_scale: float):
        """Animate button scale."""
        # This is a simplified implementation
        # In a real implementation, you'd use proper animation techniques
        pass


class GradientFrame(ctk.CTkFrame):
    """
    Frame with gradient background.
    """
    
    def __init__(
        self,
        master,
        gradient_colors: Tuple[str, str],
        gradient_direction: str = "horizontal",
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.gradient_colors = gradient_colors
        self.gradient_direction = gradient_direction
        
        # Create gradient effect
        self._create_gradient()
        
    def _create_gradient(self):
        """Create gradient background."""
        # This is a simplified implementation
        # In a real implementation, you'd create an actual gradient
        pass


class ModernProgressBar(ctk.CTkProgressBar):
    """
    Modern progress bar with gradient and animation effects.
    """
    
    def __init__(
        self,
        master,
        gradient_colors: Tuple[str, str] = ("#007AFF", "#5856D6"),
        animation_duration: float = 0.3,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.gradient_colors = gradient_colors
        self.animation_duration = animation_duration
        
        # Configure appearance
        self.configure(
            corner_radius=8,
            height=8,
            progress_color=self.gradient_colors[0]
        )
        
    def set_progress(self, value: float, animate: bool = True):
        """Set progress with smooth animation."""
        if animate:
            # Animate progress change
            self._animate_progress(value)
        else:
            super().set(value)
            
    def _animate_progress(self, target_value: float):
        """Animate progress bar to target value."""
        # This is a simplified implementation
        # In a real implementation, you'd use proper animation techniques
        super().set(target_value)


class StatusBadge(ctk.CTkLabel):
    """
    Modern status badge with color coding and animations.
    """
    
    def __init__(
        self,
        master,
        status: str = "idle",
        animated: bool = True,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.status = status
        self.animated = animated
        
        # Status colors
        self.status_colors = {
            "idle": "#8E8E93",
            "running": "#007AFF",
            "success": "#34C759",
            "warning": "#FF9500",
            "error": "#FF3B30",
            "stopping": "#FF6B6B"
        }
        
        # Configure appearance
        self._update_appearance()
        
    def set_status(self, status: str):
        """Set status with color update."""
        self.status = status
        self._update_appearance()
        
    def _update_appearance(self):
        """Update badge appearance based on status."""
        color = self.status_colors.get(self.status, self.status_colors["idle"])
        
        self.configure(
            text=self.status.upper(),
            text_color=color,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=12,
            fg_color=("gray90", "gray20"),  # Use compatible colors
            width=80,
            height=24
        )


class ModernTooltip:
    """
    Modern tooltip with glassmorphism effect.
    """
    
    def __init__(
        self,
        widget,
        text: str,
        delay: int = 500,
        **kwargs
    ):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.after_id = None
        
        # Bind events
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<Motion>", self._on_motion)
        
    def _on_enter(self, event):
        """Handle mouse enter."""
        self._schedule_tooltip()
        
    def _on_leave(self, event):
        """Handle mouse leave."""
        self._cancel_tooltip()
        
    def _on_motion(self, event):
        """Handle mouse motion."""
        if self.tooltip_window:
            self._position_tooltip(event)
            
    def _schedule_tooltip(self):
        """Schedule tooltip display."""
        self._cancel_tooltip()
        self.after_id = self.widget.after(self.delay, self._show_tooltip)
        
    def _cancel_tooltip(self):
        """Cancel tooltip display."""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
            
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            
    def _show_tooltip(self):
        """Show the tooltip."""
        if self.tooltip_window:
            return
            
        # Create tooltip window
        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_attributes("-topmost", True)
        
        # Create tooltip content
        tooltip_frame = ctk.CTkFrame(
            self.tooltip_window,
            fg_color=("gray20", "gray80"),
            corner_radius=8
        )
        tooltip_frame.pack()
        
        tooltip_label = ctk.CTkLabel(
            tooltip_frame,
            text=self.text,
            text_color="white",
            font=ctk.CTkFont(size=12),
            padx=12,
            pady=8
        )
        tooltip_label.pack()
        
        # Position tooltip
        self._position_tooltip()
        
    def _position_tooltip(self, event=None):
        """Position tooltip near mouse cursor."""
        if not self.tooltip_window:
            return
            
        # Get widget position
        widget_x = self.widget.winfo_rootx()
        widget_y = self.widget.winfo_rooty()
        widget_width = self.widget.winfo_width()
        widget_height = self.widget.winfo_height()
        
        # Calculate tooltip position
        tooltip_x = widget_x + widget_width // 2
        tooltip_y = widget_y - 40
        
        # Position tooltip
        self.tooltip_window.geometry(f"+{tooltip_x}+{tooltip_y}")


class ModernIcon:
    """
    Modern icon system with consistent styling.
    """
    
    @staticmethod
    def get_icon(icon_name: str, size: int = 24) -> str:
        """Get icon character for given name."""
        icons = {
            "play": "▶",
            "pause": "⏸",
            "stop": "⏹",
            "settings": "⚙",
            "refresh": "🔄",
            "download": "⬇",
            "upload": "⬆",
            "check": "✓",
            "cross": "✗",
            "warning": "⚠",
            "info": "ℹ",
            "error": "❌",
            "success": "✅",
            "loading": "⏳",
            "youtube": "📺",
            "sheets": "📊",
            "sync": "🔄",
            "schedule": "⏰",
            "filter": "🔍",
            "export": "📤",
            "import": "📥",
            "edit": "✏",
            "delete": "🗑",
            "add": "➕",
            "remove": "➖",
            "up": "⬆",
            "down": "⬇",
            "left": "⬅",
            "right": "➡",
            "home": "🏠",
            "back": "↩",
            "forward": "↪",
            "menu": "☰",
            "close": "✕",
            "minimize": "➖",
            "maximize": "⬜",
            "restore": "⤢"
        }
        
        return icons.get(icon_name, "?")
