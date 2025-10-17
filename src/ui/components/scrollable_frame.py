"""
Scrollable Frame Component
Custom scrollable frame with fast scrolling support.
"""
import customtkinter as ctk
from utils.tk_scroll import setup_smooth_scrolling


class ScrollableFrame(ctk.CTkScrollableFrame):
    """Enhanced scrollable frame with fast scrolling."""
    
    def __init__(self, master, **kwargs):
        # Set default styling
        default_kwargs = {
            'fg_color': 'transparent',
            'corner_radius': 0
        }
        default_kwargs.update(kwargs)
        
        super().__init__(master, **default_kwargs)
        
        # Setup fast scrolling
        setup_smooth_scrolling(self)
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the frame."""
        try:
            self._parent_canvas.yview_moveto(1.0)
        except:
            pass
    
    def scroll_to_top(self):
        """Scroll to the top of the frame."""
        try:
            self._parent_canvas.yview_moveto(0.0)
        except:
            pass
