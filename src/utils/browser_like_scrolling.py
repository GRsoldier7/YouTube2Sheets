"""
Browser-Like Scrolling for CustomTkinter
Implements smooth, fast scrolling that feels like a real browser
"""
import customtkinter as ctk
from typing import Union, Callable, Optional
import time


class BrowserLikeScrolling:
    """
    Implements browser-like scrolling behavior for CustomTkinter widgets.
    Provides smooth, fast scrolling that feels natural and responsive.
    """
    
    def __init__(self, widget: Union[ctk.CTkScrollableFrame, ctk.CTkCanvas], 
                 scroll_speed: float = 20.0, smooth_factor: float = 0.8):
        """
        Initialize browser-like scrolling.
        
        Args:
            widget: The scrollable widget
            scroll_speed: Base scroll speed multiplier (higher = faster)
            smooth_factor: Smoothness factor (0.1-1.0, higher = smoother)
        """
        self.widget = widget
        self.scroll_speed = scroll_speed
        self.smooth_factor = smooth_factor
        self.last_scroll_time = 0
        self.scroll_velocity = 0
        self.is_scrolling = False
        
        # Get the canvas for scrolling
        if hasattr(widget, '_parent_canvas'):
            self.canvas = widget._parent_canvas
        elif hasattr(widget, 'canvas'):
            self.canvas = widget.canvas
        else:
            self.canvas = widget
        
        # Bind scroll events
        self._bind_scroll_events()
    
    def _bind_scroll_events(self):
        """Bind all scroll events for cross-platform compatibility."""
        # Windows/Mac mouse wheel
        self.widget.bind_all("<MouseWheel>", self._on_mouse_wheel, add="+")
        # Linux mouse wheel
        self.widget.bind_all("<Button-4>", self._on_mouse_wheel, add="+")
        self.widget.bind_all("<Button-5>", self._on_mouse_wheel, add="+")
        # Touchpad scrolling (if supported)
        self.widget.bind_all("<Shift-MouseWheel>", self._on_horizontal_wheel, add="+")
    
    def _on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling with browser-like behavior."""
        current_time = time.time()
        time_delta = current_time - self.last_scroll_time
        self.last_scroll_time = current_time
        
        # Calculate scroll delta
        delta = 0
        if hasattr(event, 'delta') and event.delta:
            # Windows/Mac: normalize delta
            delta = -event.delta / 120
        elif hasattr(event, 'num') and event.num in (4, 5):
            # Linux: 4 = up, 5 = down
            delta = -1 if event.num == 4 else 1
        
        if delta == 0:
            return
        
        # Apply browser-like scrolling
        self._scroll_with_momentum(delta, time_delta)
    
    def _on_horizontal_wheel(self, event):
        """Handle horizontal scrolling (Shift + Wheel)."""
        delta = 0
        if hasattr(event, 'delta') and event.delta:
            delta = -event.delta / 120
        
        if delta != 0:
            self._scroll_horizontal(delta)
    
    def _scroll_with_momentum(self, delta: float, time_delta: float):
        """
        Scroll with momentum for smooth, browser-like behavior.
        """
        # TRIPLE scroll for maximum speed and responsiveness
        # 1. Immediate response (primary scroll)
        immediate_scroll = int(delta * self.scroll_speed)
        if immediate_scroll != 0:
            self.canvas.yview_scroll(immediate_scroll, "units")
        
        # 2. Secondary immediate scroll for extra speed
        secondary_scroll = int(delta * self.scroll_speed * 0.8)
        if secondary_scroll != 0:
            self.canvas.yview_scroll(secondary_scroll, "units")
        
        # 3. Momentum scroll for smooth continuation
        if time_delta > 0:
            self.scroll_velocity = (self.scroll_velocity * self.smooth_factor + 
                                  delta * self.scroll_speed * 0.6 * (1 - self.smooth_factor))
        else:
            self.scroll_velocity = delta * self.scroll_speed * 0.6
        
        # Apply momentum scroll
        momentum_scroll = int(self.scroll_velocity)
        if momentum_scroll != 0:
            self.canvas.yview_scroll(momentum_scroll, "units")
            
            # Reset velocity if it's very small
            if abs(self.scroll_velocity) < 0.02:
                self.scroll_velocity = 0
    
    def _scroll_horizontal(self, delta: float):
        """Handle horizontal scrolling."""
        scroll_amount = int(delta * self.scroll_speed)
        if scroll_amount != 0:
            self.canvas.xview_scroll(scroll_amount, "units")
    
    def set_scroll_speed(self, speed: float):
        """Dynamically adjust scroll speed."""
        self.scroll_speed = max(1.0, speed)
    
    def set_smooth_factor(self, factor: float):
        """Dynamically adjust smoothness."""
        self.smooth_factor = max(0.1, min(1.0, factor))


def setup_browser_like_scrolling(widget: Union[ctk.CTkScrollableFrame, ctk.CTkCanvas],
                                scroll_speed: float = 20.0,
                                smooth_factor: float = 0.8) -> BrowserLikeScrolling:
    """
    Setup browser-like scrolling for a CustomTkinter widget.
    
    Args:
        widget: The scrollable widget
        scroll_speed: Scroll speed multiplier (20.0 = very fast, like browser)
        smooth_factor: Smoothness factor (0.8 = very smooth)
    
    Returns:
        BrowserLikeScrolling instance for further configuration
    """
    return BrowserLikeScrolling(widget, scroll_speed, smooth_factor)


def create_ultra_fast_scrolling(widget: Union[ctk.CTkScrollableFrame, ctk.CTkCanvas]) -> BrowserLikeScrolling:
    """
    Create ultra-fast scrolling that matches browser behavior.
    
    Args:
        widget: The scrollable widget
    
    Returns:
        BrowserLikeScrolling instance configured for maximum speed
    """
    return BrowserLikeScrolling(widget, scroll_speed=50.0, smooth_factor=0.95)


def create_smooth_scrolling(widget: Union[ctk.CTkScrollableFrame, ctk.CTkCanvas]) -> BrowserLikeScrolling:
    """
    Create smooth scrolling with moderate speed.
    
    Args:
        widget: The scrollable widget
    
    Returns:
        BrowserLikeScrolling instance configured for smooth scrolling
    """
    return BrowserLikeScrolling(widget, scroll_speed=15.0, smooth_factor=0.7)


# Pre-configured scrolling presets
SCROLLING_PRESETS = {
    "rocket": lambda widget: BrowserLikeScrolling(widget, 200.0, 0.998),  # ROCKET FAST
    "lightning": lambda widget: BrowserLikeScrolling(widget, 150.0, 0.995),  # Lightning fast
    "browser": lambda widget: BrowserLikeScrolling(widget, 100.0, 0.99),  # Browser fast
    "ultra": lambda widget: create_ultra_fast_scrolling(widget),
    "smooth": lambda widget: create_smooth_scrolling(widget),
    "fast": lambda widget: BrowserLikeScrolling(widget, 60.0, 0.9),
    "medium": lambda widget: BrowserLikeScrolling(widget, 30.0, 0.8),
    "slow": lambda widget: BrowserLikeScrolling(widget, 15.0, 0.6)
}


def apply_scrolling_preset(widget: Union[ctk.CTkScrollableFrame, ctk.CTkCanvas], 
                          preset: str = "browser") -> BrowserLikeScrolling:
    """
    Apply a pre-configured scrolling preset.
    
    Args:
        widget: The scrollable widget
        preset: Preset name ("browser", "smooth", "fast", "medium", "slow")
    
    Returns:
        BrowserLikeScrolling instance
    """
    if preset not in SCROLLING_PRESETS:
        preset = "browser"
    
    return SCROLLING_PRESETS[preset](widget)
