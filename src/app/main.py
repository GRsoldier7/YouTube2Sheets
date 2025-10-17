"""
YouTube2Sheets Main Application
Entry point for the modular YouTube2Sheets application.
"""
import customtkinter as ctk
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.container import AppContainer
from app.state import app_state, event_bus
from ui.theme.tokens import tokens
from ui.theme.theme_loader import load_theme
from ui.views.link_sync.view import LinkSyncView
from ui.views.link_sync.vm import LinkSyncViewModel
from ui.components.sticky_bar import StickyActionsBar
from ui.components.log_view import ActivityLog
from utils.tk_scroll import setup_smooth_scrolling


class YouTube2SheetsApp:
    """Main application class."""
    
    def __init__(self):
        self.root = None
        self.container = None
        self.link_sync_view = None
        self.link_sync_vm = None
        self.sticky_bar = None
        self.activity_log = None
        
    def run(self):
        """Run the application."""
        try:
            # Initialize CustomTkinter
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            
            # Create main window
            self.root = ctk.CTk()
            self.root.title("YouTube2Sheets - Production Ready")
            self.root.configure(fg_color=tokens.colors['background'])
            
            # Set window size and position
            self._setup_window()
            
            # Load theme
            load_theme(self.root)
            
            # Initialize dependency injection container
            self.container = AppContainer()
            
            # Setup UI
            self._setup_ui()
            
            # Setup event handlers
            self._setup_event_handlers()
            
            # Start the application
            self.root.mainloop()
            
        except Exception as e:
            print(f"Error starting application: {e}")
            import traceback
            traceback.print_exc()
    
    def _setup_window(self):
        """Setup window size and position."""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate window size (90% of screen)
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1200, 800)
        
        # Try to maximize on Windows
        try:
            self.root.wm_state('zoomed')
        except:
            pass
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main container
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Create scrollable frame
        from ui.components.scrollable_frame import ScrollableFrame
        self.scrollable_frame = ScrollableFrame(main_container)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")
        
        # Setup smooth scrolling
        setup_smooth_scrolling(self.scrollable_frame)
        
        # Create LinkSync view
        self.link_sync_vm = LinkSyncViewModel(
            app_state=app_state,
            event_bus=event_bus,
            container=self.container
        )
        
        self.link_sync_view = LinkSyncView(
            master=self.scrollable_frame,
            vm=self.link_sync_vm,
            tokens=tokens
        )
        self.link_sync_view.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Create sticky actions bar
        self.sticky_bar = StickyActionsBar(
            master=self.root,
            vm=self.link_sync_vm,
            tokens=tokens
        )
        
        # Create activity log
        self.activity_log = ActivityLog(
            master=self.root,
            tokens=tokens
        )
        self.activity_log.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
    
    def _setup_event_handlers(self):
        """Setup event handlers."""
        # Subscribe to app state changes
        event_bus.on("status_changed", self._on_status_changed)
        event_bus.on("progress_changed", self._on_progress_changed)
        event_bus.on("error_occurred", self._on_error_occurred)
        event_bus.on("log_message", self._on_log_message)
    
    def _on_status_changed(self, status):
        """Handle status changes."""
        if self.sticky_bar:
            self.sticky_bar.update_status(status)
    
    def _on_progress_changed(self, progress, text):
        """Handle progress changes."""
        if self.sticky_bar:
            self.sticky_bar.update_progress(progress, text)
    
    def _on_error_occurred(self, error):
        """Handle errors."""
        if self.activity_log:
            self.activity_log.add_error(f"Error: {error}")
    
    def _on_log_message(self, message, level="info"):
        """Handle log messages."""
        if self.activity_log:
            self.activity_log.add_message(message, level)


def main():
    """Main entry point."""
    app = YouTube2SheetsApp()
    app.run()


if __name__ == "__main__":
    main()
