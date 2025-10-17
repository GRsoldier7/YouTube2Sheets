"""
Tkinter Scrolling Utilities
Cross-platform fast scrolling helpers for CustomTkinter.
"""
import customtkinter as ctk
from typing import Union


def bind_fast_scroll(widget: Union[ctk.CTkScrollableFrame, ctk.CTkCanvas], factor: float = 10.0) -> None:
    """
    Bind fast scrolling to a CustomTkinter scrollable widget.
    
    Args:
        widget: The scrollable widget (CTkScrollableFrame or CTkCanvas)
        factor: Scroll speed multiplier (higher = faster)
    """
    def on_wheel(event):
        """Handle mouse wheel scrolling."""
        try:
            # Get the canvas for scrolling
            if hasattr(widget, '_parent_canvas'):
                canvas = widget._parent_canvas
            elif hasattr(widget, 'canvas'):
                canvas = widget.canvas
            else:
                canvas = widget
            
            # Calculate scroll delta
            if hasattr(event, 'delta') and event.delta:
                # Windows/Mac wheel
                delta = -1 if event.delta > 0 else 1
            elif hasattr(event, 'num') and event.num in (4, 5):
                # Linux wheel
                delta = -1 if event.num == 4 else 1
            else:
                return
            
            # Apply scroll with factor
            canvas.yview_scroll(int(delta * factor), "units")
            
        except Exception as e:
            print(f"Error in scroll handler: {e}")
    
    # Bind wheel events
    widget.bind_all("<MouseWheel>", on_wheel, add="+")
    widget.bind_all("<Button-4>", on_wheel, add="+")  # Linux up
    widget.bind_all("<Button-5>", on_wheel, add="+")  # Linux down


def bind_horizontal_scroll(widget: Union[ctk.CTkScrollableFrame, ctk.CTkCanvas], factor: float = 10.0) -> None:
    """
    Bind horizontal scrolling to a CustomTkinter scrollable widget.
    
    Args:
        widget: The scrollable widget
        factor: Scroll speed multiplier
    """
    def on_horizontal_wheel(event):
        """Handle horizontal mouse wheel scrolling."""
        try:
            # Get the canvas for scrolling
            if hasattr(widget, '_parent_canvas'):
                canvas = widget._parent_canvas
            elif hasattr(widget, 'canvas'):
                canvas = widget.canvas
            else:
                canvas = widget
            
            # Calculate scroll delta
            if hasattr(event, 'delta') and event.delta:
                delta = -1 if event.delta > 0 else 1
            else:
                return
            
            # Apply horizontal scroll
            canvas.xview_scroll(int(delta * factor), "units")
            
        except Exception as e:
            print(f"Error in horizontal scroll handler: {e}")
    
    # Bind horizontal wheel events (Shift + Wheel)
    widget.bind_all("<Shift-MouseWheel>", on_horizontal_wheel, add="+")
    widget.bind_all("<Shift-Button-4>", on_horizontal_wheel, add="+")
    widget.bind_all("<Shift-Button-5>", on_horizontal_wheel, add="+")


def setup_smooth_scrolling(widget: Union[ctk.CTkScrollableFrame, ctk.CTkCanvas]) -> None:
    """
    Setup smooth scrolling with optimal settings.
    
    Args:
        widget: The scrollable widget
    """
    # Bind fast vertical scrolling
    bind_fast_scroll(widget, factor=3.0)
    
    # Bind horizontal scrolling
    bind_horizontal_scroll(widget, factor=2.0)
    
    # Configure smooth scrolling behavior
    if hasattr(widget, '_parent_canvas'):
        canvas = widget._parent_canvas
        # Enable smooth scrolling
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Configure scrollbar behavior
        if hasattr(widget, '_parent_scrollbar'):
            scrollbar = widget._parent_scrollbar
            scrollbar.configure(command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)


def auto_scroll_to_bottom(widget: Union[ctk.CTkScrollableFrame, ctk.CTkCanvas]) -> None:
    """
    Automatically scroll to the bottom of a scrollable widget.
    
    Args:
        widget: The scrollable widget
    """
    try:
        if hasattr(widget, '_parent_canvas'):
            canvas = widget._parent_canvas
            canvas.yview_moveto(1.0)  # Scroll to bottom
        elif hasattr(widget, 'canvas'):
            widget.canvas.yview_moveto(1.0)
    except Exception as e:
        print(f"Error auto-scrolling to bottom: {e}")


def scroll_to_top(widget: Union[ctk.CTkScrollableFrame, ctk.CTkCanvas]) -> None:
    """
    Scroll to the top of a scrollable widget.
    
    Args:
        widget: The scrollable widget
    """
    try:
        if hasattr(widget, '_parent_canvas'):
            canvas = widget._parent_canvas
            canvas.yview_moveto(0.0)  # Scroll to top
        elif hasattr(widget, 'canvas'):
            widget.canvas.yview_moveto(0.0)
    except Exception as e:
        print(f"Error scrolling to top: {e}")
