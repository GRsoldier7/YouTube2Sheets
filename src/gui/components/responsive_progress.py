"""
Responsive Progress Components with Real-time Updates and Smooth Animations
"""

from __future__ import annotations

import tkinter as tk
from typing import Optional, Callable
import customtkinter as ctk
import threading
import time


class ResponsiveProgressBar(ctk.CTkProgressBar):
    """
    Enhanced progress bar with smooth animations and real-time updates.
    """
    
    def __init__(
        self,
        master,
        animation_duration: float = 0.3,
        update_interval: int = 16,  # ~60 FPS
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.animation_duration = animation_duration
        self.update_interval = update_interval
        
        # Animation state
        self._target_value = 0.0
        self._current_value = 0.0
        self._animation_id = None
        self._is_animating = False
        
        # Smooth animation
        self._start_time = 0
        self._start_value = 0.0
        
    def set_progress(self, value: float, animate: bool = True):
        """Set progress value with optional smooth animation."""
        # Clamp value between 0 and 1
        value = max(0.0, min(1.0, value))
        
        if not animate:
            self._target_value = value
            self._current_value = value
            super().set(value)
            return
            
        # Start smooth animation
        self._target_value = value
        self._start_value = self._current_value
        self._start_time = time.time()
        
        if not self._is_animating:
            self._is_animating = True
            self._animate_progress()
            
    def _animate_progress(self):
        """Animate progress bar smoothly."""
        if not self._is_animating:
            return
            
        current_time = time.time()
        elapsed = current_time - self._start_time
        
        if elapsed >= self.animation_duration:
            # Animation complete
            self._current_value = self._target_value
            super().set(self._current_value)
            self._is_animating = False
            return
            
        # Calculate eased progress
        progress = elapsed / self.animation_duration
        eased_progress = self._ease_out_cubic(progress)
        
        # Interpolate between start and target
        self._current_value = self._start_value + (self._target_value - self._start_value) * eased_progress
        super().set(self._current_value)
        
        # Schedule next frame
        self._animation_id = self.after(self.update_interval, self._animate_progress)
        
    def _ease_out_cubic(self, t: float) -> float:
        """Cubic ease-out function for smooth animation."""
        return 1 - (1 - t) ** 3
        
    def increment(self, amount: float = 0.01, animate: bool = True):
        """Increment progress by a small amount."""
        new_value = self._target_value + amount
        self.set_progress(new_value, animate)
        
    def reset(self, animate: bool = True):
        """Reset progress to 0."""
        self.set_progress(0.0, animate)
        
    def complete(self, animate: bool = True):
        """Set progress to 100%."""
        self.set_progress(1.0, animate)


class StatusIndicator(ctk.CTkLabel):
    """
    Animated status indicator with color coding and smooth transitions.
    """
    
    def __init__(
        self,
        master,
        status_colors: Optional[dict] = None,
        animation_duration: float = 0.5,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.animation_duration = animation_duration
        
        # Default status colors
        self.status_colors = status_colors or {
            "idle": "#6C757D",
            "running": "#007BFF",
            "success": "#28A745",
            "warning": "#FFC107",
            "error": "#DC3545",
            "stopping": "#FD7E14"
        }
        
        # Animation state
        self._current_status = "idle"
        self._animation_id = None
        self._is_animating = False
        
        # Set initial status
        self.set_status("idle", animate=False)
        
    def set_status(self, status: str, message: str = "", animate: bool = True):
        """Set status with optional smooth color transition."""
        if status not in self.status_colors:
            status = "idle"
            
        if not animate:
            self._current_status = status
            self._update_display()
            return
            
        # Start color transition animation
        if not self._is_animating:
            self._is_animating = True
            self._animate_status_transition(status, message)
        else:
            # Queue the new status
            self._target_status = status
            self._target_message = message
            
    def _animate_status_transition(self, status: str, message: str):
        """Animate status transition with color interpolation."""
        if not self._is_animating:
            return
            
        # Update display
        self._current_status = status
        if message:
            self.configure(text=message)
        else:
            self.configure(text=status.upper())
            
        # Get target color
        target_color = self.status_colors.get(status, self.status_colors["idle"])
        
        # Apply color
        self.configure(text_color=target_color)
        
        # Complete animation
        self._is_animating = False
        
    def _update_display(self):
        """Update the display with current status."""
        color = self.status_colors.get(self._current_status, self.status_colors["idle"])
        self.configure(text=self._current_status.upper(), text_color=color)


class LiveProgressTracker:
    """
    Real-time progress tracker with threading and callbacks.
    """
    
    def __init__(
        self,
        progress_bar: ResponsiveProgressBar,
        status_indicator: StatusIndicator,
        update_callback: Optional[Callable] = None
    ):
        self.progress_bar = progress_bar
        self.status_indicator = status_indicator
        self.update_callback = update_callback
        
        # Progress state
        self._current_progress = 0.0
        self._total_steps = 100
        self._current_step = 0
        self._is_running = False
        self._start_time = 0
        
        # Threading
        self._update_thread = None
        self._stop_event = threading.Event()
        
    def start(self, total_steps: int = 100, status_message: str = "Starting..."):
        """Start progress tracking."""
        self._total_steps = total_steps
        self._current_step = 0
        self._current_progress = 0.0
        self._is_running = True
        self._start_time = time.time()
        self._stop_event.clear()
        
        # Update UI
        self.progress_bar.reset(animate=True)
        self.status_indicator.set_status("running", status_message, animate=True)
        
        # Start update thread
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
        
    def update(self, step: int, message: str = ""):
        """Update progress to a specific step."""
        if not self._is_running:
            return
            
        self._current_step = min(step, self._total_steps)
        self._current_progress = self._current_step / self._total_steps
        
        # Update progress bar
        self.progress_bar.set_progress(self._current_progress, animate=True)
        
        # Update status
        if message:
            self.status_indicator.set_status("running", message, animate=True)
            
        # Call update callback
        if self.update_callback:
            self.update_callback(self._current_progress, message)
            
    def increment(self, message: str = ""):
        """Increment progress by one step."""
        self.update(self._current_step + 1, message)
        
    def complete(self, message: str = "Completed successfully"):
        """Mark progress as complete."""
        self._is_running = False
        self._stop_event.set()
        
        # Update UI
        self.progress_bar.complete(animate=True)
        self.status_indicator.set_status("success", message, animate=True)
        
        # Call completion callback
        if self.update_callback:
            self.update_callback(1.0, message)
            
    def error(self, message: str = "An error occurred"):
        """Mark progress as failed."""
        self._is_running = False
        self._stop_event.set()
        
        # Update UI
        self.status_indicator.set_status("error", message, animate=True)
        
    def stop(self, message: str = "Stopped by user"):
        """Stop progress tracking."""
        self._is_running = False
        self._stop_event.set()
        
        # Update UI
        self.status_indicator.set_status("stopping", message, animate=True)
        
    def _update_loop(self):
        """Background update loop for real-time progress."""
        while self._is_running and not self._stop_event.is_set():
            try:
                # Calculate elapsed time
                elapsed = time.time() - self._start_time
                
                # Update progress if needed
                if self._current_progress < 1.0:
                    # Estimate progress based on time if no updates
                    estimated_progress = min(0.95, elapsed / 30)  # Assume 30s max
                    if estimated_progress > self._current_progress:
                        self.progress_bar.set_progress(estimated_progress, animate=True)
                        
                time.sleep(0.1)  # Update every 100ms
                
            except Exception:
                break
                
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self._start_time if self._start_time else 0.0
        
    def get_estimated_remaining(self) -> float:
        """Get estimated remaining time in seconds."""
        if self._current_progress <= 0:
            return 0.0
            
        elapsed = self.get_elapsed_time()
        return (elapsed / self._current_progress) - elapsed
