"""
Performance Optimization System for Modern GUI
Designed by the Back End Architect & Performance Engineer
"""

from __future__ import annotations

import threading
import time
import queue
import math
from typing import Callable, Any, Optional, Dict
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, Future
import customtkinter as ctk


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking."""
    frame_rate: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    render_time: float = 0.0
    update_time: float = 0.0


class PerformanceMonitor:
    """
    Real-time performance monitoring and optimization.
    """
    
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.metrics = PerformanceMetrics()
        self.is_monitoring = False
        self.monitor_thread = None
        self.frame_times = []
        self.max_frame_samples = 60  # 1 second at 60 FPS
        
        # Performance thresholds
        self.target_fps = 60
        self.min_fps = 30
        self.max_memory_mb = 500
        self.max_cpu_percent = 80
        
    def start_monitoring(self):
        """Start performance monitoring."""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
            
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                # Measure frame time
                start_time = time.time()
                
                # Update metrics
                self._update_metrics()
                
                # Check performance thresholds
                self._check_performance_thresholds()
                
                # Calculate frame rate
                frame_time = time.time() - start_time
                self.frame_times.append(frame_time)
                
                if len(self.frame_times) > self.max_frame_samples:
                    self.frame_times.pop(0)
                    
                if self.frame_times:
                    self.metrics.frame_rate = 1.0 / (sum(self.frame_times) / len(self.frame_times))
                    
                time.sleep(0.016)  # ~60 FPS monitoring
                
            except Exception:
                break
                
    def _update_metrics(self):
        """Update performance metrics."""
        # Memory usage (simplified)
        import psutil
        process = psutil.Process()
        self.metrics.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        
        # CPU usage
        self.metrics.cpu_usage = process.cpu_percent()
        
    def _check_performance_thresholds(self):
        """Check if performance is below thresholds."""
        if self.metrics.frame_rate < self.min_fps:
            self._optimize_performance()
            
        if self.metrics.memory_usage > self.max_memory_mb:
            self._optimize_memory()
            
        if self.metrics.cpu_usage > self.max_cpu_percent:
            self._optimize_cpu()
            
    def _optimize_performance(self):
        """Optimize performance when FPS is low."""
        # Reduce animation complexity
        # Disable non-essential visual effects
        # Reduce update frequency
        pass
        
    def _optimize_memory(self):
        """Optimize memory usage."""
        # Clear caches
        # Reduce buffer sizes
        # Garbage collect
        import gc
        gc.collect()
        
    def _optimize_cpu(self):
        """Optimize CPU usage."""
        # Reduce update frequency
        # Use more efficient algorithms
        # Defer non-critical operations
        pass


class AsyncTaskManager:
    """
    Asynchronous task management for non-blocking UI operations.
    """
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, Future] = {}
        self.callbacks: Dict[str, Callable] = {}
        
    def submit_task(
        self,
        task_id: str,
        func: Callable,
        *args,
        callback: Optional[Callable] = None,
        **kwargs
    ) -> Future:
        """Submit an asynchronous task."""
        # Cancel existing task with same ID
        if task_id in self.tasks:
            self.cancel_task(task_id)
            
        # Submit new task
        future = self.executor.submit(func, *args, **kwargs)
        self.tasks[task_id] = future
        
        if callback:
            self.callbacks[task_id] = callback
            
        # Set up completion handling
        future.add_done_callback(lambda f: self._on_task_complete(task_id, f))
        
        return future
        
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        if task_id in self.tasks:
            future = self.tasks[task_id]
            cancelled = future.cancel()
            if cancelled:
                del self.tasks[task_id]
                if task_id in self.callbacks:
                    del self.callbacks[task_id]
            return cancelled
        return False
        
    def _on_task_complete(self, task_id: str, future: Future):
        """Handle task completion."""
        if task_id in self.callbacks:
            try:
                result = future.result()
                self.callbacks[task_id](result)
            except Exception as e:
                self.callbacks[task_id](None, e)
            finally:
                del self.callbacks[task_id]
                
        if task_id in self.tasks:
            del self.tasks[task_id]
            
    def shutdown(self, wait: bool = True):
        """Shutdown the task manager."""
        self.executor.shutdown(wait=wait)


class UIUpdateQueue:
    """
    Queue-based UI updates for smooth performance.
    """
    
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.update_queue = queue.Queue()
        self.is_processing = False
        self.max_updates_per_frame = 10
        
    def schedule_update(self, func: Callable, *args, **kwargs):
        """Schedule a UI update."""
        self.update_queue.put((func, args, kwargs))
        if not self.is_processing:
            self._process_updates()
            
    def _process_updates(self):
        """Process queued UI updates."""
        if self.is_processing:
            return
            
        self.is_processing = True
        
        def process():
            updates_processed = 0
            while not self.update_queue.empty() and updates_processed < self.max_updates_per_frame:
                try:
                    func, args, kwargs = self.update_queue.get_nowait()
                    func(*args, **kwargs)
                    updates_processed += 1
                except queue.Empty:
                    break
                except Exception as e:
                    print(f"Error processing UI update: {e}")
                    
            self.is_processing = False
            
            # Schedule next batch if queue is not empty
            if not self.update_queue.empty():
                self.root.after(16, self._process_updates)  # ~60 FPS
                
        # Process updates in the main thread
        self.root.after(0, process)


class SmoothAnimator:
    """
    Smooth animation system for UI elements.
    """
    
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.animations: Dict[str, Dict] = {}
        self.animation_id = None
        
    def animate_property(
        self,
        widget,
        property_name: str,
        start_value: Any,
        end_value: Any,
        duration: float = 0.3,
        easing: str = "ease_out_cubic",
        callback: Optional[Callable] = None
    ):
        """Animate a widget property."""
        animation_id = f"{id(widget)}_{property_name}"
        
        # Cancel existing animation
        if animation_id in self.animations:
            self._cancel_animation(animation_id)
            
        # Create animation
        animation = {
            "widget": widget,
            "property": property_name,
            "start_value": start_value,
            "end_value": end_value,
            "duration": duration,
            "easing": easing,
            "callback": callback,
            "start_time": time.time(),
            "current_value": start_value
        }
        
        self.animations[animation_id] = animation
        
        # Start animation loop if not running
        if not self.animation_id:
            self._animation_loop()
            
    def _animation_loop(self):
        """Main animation loop."""
        if not self.animations:
            self.animation_id = None
            return
            
        current_time = time.time()
        completed_animations = []
        
        for animation_id, animation in self.animations.items():
            elapsed = current_time - animation["start_time"]
            progress = min(elapsed / animation["duration"], 1.0)
            
            # Apply easing
            eased_progress = self._apply_easing(progress, animation["easing"])
            
            # Calculate current value
            start_val = animation["start_value"]
            end_val = animation["end_value"]
            
            if isinstance(start_val, (int, float)) and isinstance(end_val, (int, float)):
                current_value = start_val + (end_val - start_val) * eased_progress
            else:
                current_value = end_val if progress >= 1.0 else start_val
                
            # Apply to widget
            try:
                setattr(animation["widget"], animation["property"], current_value)
                animation["current_value"] = current_value
            except Exception as e:
                print(f"Error animating {animation['property']}: {e}")
                
            # Check if animation is complete
            if progress >= 1.0:
                completed_animations.append(animation_id)
                if animation["callback"]:
                    animation["callback"](current_value)
                    
        # Remove completed animations
        for animation_id in completed_animations:
            del self.animations[animation_id]
            
        # Schedule next frame
        if self.animations:
            self.animation_id = self.root.after(16, self._animation_loop)  # ~60 FPS
        else:
            self.animation_id = None
            
    def _apply_easing(self, t: float, easing: str) -> float:
        """Apply easing function to animation progress."""
        easing_functions = {
            "linear": lambda t: t,
            "ease_in": lambda t: t * t,
            "ease_out": lambda t: 1 - (1 - t) * (1 - t),
            "ease_in_out": lambda t: 2 * t * t if t < 0.5 else 1 - 2 * (1 - t) * (1 - t),
            "ease_out_cubic": lambda t: 1 - (1 - t) ** 3,
            "ease_in_cubic": lambda t: t ** 3,
            "ease_in_out_cubic": lambda t: 4 * t * t * t if t < 0.5 else 1 - 4 * (1 - t) ** 3,
            "ease_out_quart": lambda t: 1 - (1 - t) ** 4,
            "ease_in_quart": lambda t: t ** 4,
            "ease_in_out_quart": lambda t: 8 * t * t * t * t if t < 0.5 else 1 - 8 * (1 - t) ** 4,
            "ease_out_expo": lambda t: 1 - (2 ** (-10 * t)) if t < 1 else 1,
            "ease_in_expo": lambda t: 2 ** (10 * (t - 1)) if t > 0 else 0,
            "ease_in_out_expo": lambda t: 2 ** (10 * (2 * t - 1)) / 2 if t < 0.5 else (2 - 2 ** (-10 * (2 * t - 1))) / 2,
            "ease_out_back": lambda t: 1 + 2.7 * (t - 1) ** 3 + 1.7 * (t - 1) ** 2,
            "ease_in_back": lambda t: 2.7 * t ** 3 - 1.7 * t ** 2,
            "ease_in_out_back": lambda t: 1.7 * t * t * (2.7 * t - 1.7) if t < 0.5 else 1 + 1.7 * (t - 1) * (t - 1) * (2.7 * (t - 1) + 1.7),
            "ease_out_elastic": lambda t: 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1 if t > 0 else 0,
            "ease_in_elastic": lambda t: 2 ** (10 * (t - 1)) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) if t > 0 else 0,
            "ease_in_out_elastic": lambda t: 2 ** (10 * (2 * t - 1)) * math.sin((2 * t * 10 - 0.75) * (2 * math.pi) / 3) / 2 if t < 0.5 else (2 - 2 ** (-10 * (2 * t - 1)) * math.sin((2 * t * 10 - 0.75) * (2 * math.pi) / 3)) / 2,
            "ease_out_bounce": lambda t: 1 - (1 - t) ** 4 if t < 0.75 else 1 - (1 - t) ** 2 if t < 0.875 else 1 - (1 - t) ** 1.5,
            "ease_in_bounce": lambda t: t ** 4 if t < 0.25 else t ** 2 if t < 0.375 else t ** 1.5,
            "ease_in_out_bounce": lambda t: 2 * t ** 4 if t < 0.25 else 2 * t ** 2 if t < 0.375 else 2 * t ** 1.5 if t < 0.5 else 2 - 2 * (1 - t) ** 4 if t < 0.75 else 2 - 2 * (1 - t) ** 2 if t < 0.875 else 2 - 2 * (1 - t) ** 1.5,
        }
        
        return easing_functions.get(easing, easing_functions["ease_out_cubic"])(t)
        
    def _cancel_animation(self, animation_id: str):
        """Cancel a specific animation."""
        if animation_id in self.animations:
            del self.animations[animation_id]
            
    def stop_all_animations(self):
        """Stop all running animations."""
        self.animations.clear()
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None


class ResponsiveLayout:
    """
    Responsive layout system for different screen sizes.
    """
    
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.breakpoints = {
            "mobile": 768,
            "tablet": 1024,
            "desktop": 1200,
            "large": 1600
        }
        self.current_breakpoint = "desktop"
        self.layout_callbacks: Dict[str, Callable] = {}
        
        # Bind resize events
        self.root.bind("<Configure>", self._on_resize)
        
    def register_layout_callback(self, breakpoint: str, callback: Callable):
        """Register a callback for layout changes."""
        self.layout_callbacks[breakpoint] = callback
        
    def _on_resize(self, event):
        """Handle window resize events."""
        if event.widget != self.root:
            return
            
        width = event.width
        new_breakpoint = self._get_breakpoint(width)
        
        if new_breakpoint != self.current_breakpoint:
            self.current_breakpoint = new_breakpoint
            self._apply_layout(new_breakpoint)
            
    def _get_breakpoint(self, width: int) -> str:
        """Get breakpoint for given width."""
        if width < self.breakpoints["mobile"]:
            return "mobile"
        elif width < self.breakpoints["tablet"]:
            return "tablet"
        elif width < self.breakpoints["desktop"]:
            return "desktop"
        else:
            return "large"
            
    def _apply_layout(self, breakpoint: str):
        """Apply layout for breakpoint."""
        if breakpoint in self.layout_callbacks:
            self.layout_callbacks[breakpoint]()
