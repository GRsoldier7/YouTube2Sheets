"""
Comprehensive Keyboard Shortcuts and Navigation System
Designed by the Front End Architect & Designer
"""

from __future__ import annotations

import tkinter as tk
from typing import Dict, Callable, Optional, List
import customtkinter as ctk


class KeyboardShortcutManager:
    """
    Centralized keyboard shortcut management system.
    """
    
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.shortcuts: Dict[str, Callable] = {}
        self.context_shortcuts: Dict[str, Dict[str, Callable]] = {}
        self.current_context = "default"
        
        # Bind global key events
        self.root.bind("<Key>", self._handle_key_event)
        self.root.focus_set()
        
    def register_shortcut(
        self,
        key_combination: str,
        callback: Callable,
        context: str = "default",
        description: str = ""
    ):
        """Register a keyboard shortcut."""
        shortcut_key = f"{context}:{key_combination}"
        
        if context == "default":
            self.shortcuts[key_combination] = callback
        else:
            if context not in self.context_shortcuts:
                self.context_shortcuts[context] = {}
            self.context_shortcuts[context][key_combination] = callback
            
    def set_context(self, context: str):
        """Set the current context for shortcuts."""
        self.current_context = context
        
    def _handle_key_event(self, event):
        """Handle keyboard events."""
        # Build key combination string
        modifiers = []
        if event.state & 0x4:  # Ctrl
            modifiers.append("Ctrl")
        if event.state & 0x8:  # Alt
            modifiers.append("Alt")
        if event.state & 0x1:  # Shift
            modifiers.append("Shift")
            
        key = event.keysym
        if modifiers:
            key_combination = "+".join(modifiers + [key])
        else:
            key_combination = key
            
        # Try to find shortcut in current context
        callback = None
        
        # Check context-specific shortcuts first
        if self.current_context in self.context_shortcuts:
            callback = self.context_shortcuts[self.current_context].get(key_combination)
            
        # Fall back to default shortcuts
        if not callback:
            callback = self.shortcuts.get(key_combination)
            
        # Execute callback if found
        if callback:
            try:
                callback()
                return "break"
            except Exception as e:
                print(f"Error executing shortcut {key_combination}: {e}")
                
        return None


class ModernNavigation:
    """
    Modern navigation system with focus management.
    """
    
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.focusable_widgets: List[tk.Widget] = []
        self.current_focus_index = 0
        self.focus_groups: Dict[str, List[tk.Widget]] = {}
        
    def register_widget(self, widget: tk.Widget, group: str = "default"):
        """Register a widget for navigation."""
        if widget not in self.focusable_widgets:
            self.focusable_widgets.append(widget)
            
        if group not in self.focus_groups:
            self.focus_groups[group] = []
        self.focus_groups[group].append(widget)
        
    def focus_next(self, group: str = "default"):
        """Focus the next widget in the group."""
        if group not in self.focus_groups:
            return
            
        widgets = self.focus_groups[group]
        if not widgets:
            return
            
        # Find current focused widget
        current_widget = self.root.focus_get()
        if current_widget in widgets:
            current_index = widgets.index(current_widget)
        else:
            current_index = -1
            
        # Focus next widget
        next_index = (current_index + 1) % len(widgets)
        widgets[next_index].focus_set()
        
    def focus_previous(self, group: str = "default"):
        """Focus the previous widget in the group."""
        if group not in self.focus_groups:
            return
            
        widgets = self.focus_groups[group]
        if not widgets:
            return
            
        # Find current focused widget
        current_widget = self.root.focus_get()
        if current_widget in widgets:
            current_index = widgets.index(current_widget)
        else:
            current_index = 0
            
        # Focus previous widget
        prev_index = (current_index - 1) % len(widgets)
        widgets[prev_index].focus_set()
        
    def focus_first(self, group: str = "default"):
        """Focus the first widget in the group."""
        if group in self.focus_groups and self.focus_groups[group]:
            self.focus_groups[group][0].focus_set()
            
    def focus_last(self, group: str = "default"):
        """Focus the last widget in the group."""
        if group in self.focus_groups and self.focus_groups[group]:
            self.focus_groups[group][-1].focus_set()


class AccessibilityManager:
    """
    Accessibility features for better user experience.
    """
    
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.announcements: List[str] = []
        self.announcement_callback: Optional[Callable] = None
        
    def announce(self, message: str):
        """Announce a message to screen readers."""
        self.announcements.append(message)
        if self.announcement_callback:
            self.announcement_callback(message)
            
    def set_announcement_callback(self, callback: Callable[[str], None]):
        """Set callback for announcements."""
        self.announcement_callback = callback
        
    def get_announcements(self) -> List[str]:
        """Get all announcements."""
        return self.announcements.copy()
        
    def clear_announcements(self):
        """Clear all announcements."""
        self.announcements.clear()


class ModernShortcuts:
    """
    Predefined modern keyboard shortcuts.
    """
    
    @staticmethod
    def setup_default_shortcuts(shortcut_manager: KeyboardShortcutManager, app_instance):
        """Setup default keyboard shortcuts for the application."""
        
        # File operations
        shortcut_manager.register_shortcut("Ctrl+o", app_instance.open_file, description="Open file")
        shortcut_manager.register_shortcut("Ctrl+s", app_instance.save_file, description="Save file")
        shortcut_manager.register_shortcut("Ctrl+n", app_instance.new_file, description="New file")
        
        # Edit operations
        shortcut_manager.register_shortcut("Ctrl+z", app_instance.undo, description="Undo")
        shortcut_manager.register_shortcut("Ctrl+y", app_instance.redo, description="Redo")
        shortcut_manager.register_shortcut("Ctrl+c", app_instance.copy, description="Copy")
        shortcut_manager.register_shortcut("Ctrl+v", app_instance.paste, description="Paste")
        shortcut_manager.register_shortcut("Ctrl+x", app_instance.cut, description="Cut")
        shortcut_manager.register_shortcut("Ctrl+a", app_instance.select_all, description="Select all")
        
        # View operations
        shortcut_manager.register_shortcut("F11", app_instance.toggle_fullscreen, description="Toggle fullscreen")
        shortcut_manager.register_shortcut("Ctrl+=", app_instance.zoom_in, description="Zoom in")
        shortcut_manager.register_shortcut("Ctrl+-", app_instance.zoom_out, description="Zoom out")
        shortcut_manager.register_shortcut("Ctrl+0", app_instance.zoom_reset, description="Reset zoom")
        
        # Navigation
        shortcut_manager.register_shortcut("Tab", app_instance.focus_next, description="Focus next")
        shortcut_manager.register_shortcut("Shift+Tab", app_instance.focus_previous, description="Focus previous")
        shortcut_manager.register_shortcut("Home", app_instance.focus_first, description="Focus first")
        shortcut_manager.register_shortcut("End", app_instance.focus_last, description="Focus last")
        
        # Application specific
        shortcut_manager.register_shortcut("F5", app_instance.refresh, description="Refresh")
        shortcut_manager.register_shortcut("Ctrl+r", app_instance.refresh, description="Refresh")
        shortcut_manager.register_shortcut("F1", app_instance.show_help, description="Show help")
        shortcut_manager.register_shortcut("Ctrl+?", app_instance.show_help, description="Show help")
        shortcut_manager.register_shortcut("Ctrl+Shift+?", app_instance.show_shortcuts, description="Show shortcuts")
        
        # YouTube2Sheets specific
        shortcut_manager.register_shortcut("Ctrl+Enter", app_instance.start_sync, description="Start sync")
        shortcut_manager.register_shortcut("Escape", app_instance.stop_sync, description="Stop sync")
        shortcut_manager.register_shortcut("Ctrl+Shift+S", app_instance.run_scheduler, description="Run scheduler")
        shortcut_manager.register_shortcut("Ctrl+Shift+O", app_instance.open_settings, description="Open settings")
        
        # Window management
        shortcut_manager.register_shortcut("Alt+F4", app_instance.quit, description="Quit application")
        shortcut_manager.register_shortcut("Ctrl+Q", app_instance.quit, description="Quit application")
        shortcut_manager.register_shortcut("Ctrl+W", app_instance.close_window, description="Close window")
        
        # Debug and development
        shortcut_manager.register_shortcut("F12", app_instance.toggle_debug, description="Toggle debug mode")
        shortcut_manager.register_shortcut("Ctrl+Shift+D", app_instance.show_debug, description="Show debug info")
        
    @staticmethod
    def setup_context_shortcuts(shortcut_manager: KeyboardShortcutManager, app_instance):
        """Setup context-specific shortcuts."""
        
        # Settings dialog shortcuts
        shortcut_manager.register_shortcut(
            "Escape", 
            app_instance.close_settings, 
            context="settings",
            description="Close settings"
        )
        shortcut_manager.register_shortcut(
            "Enter", 
            app_instance.save_settings, 
            context="settings",
            description="Save settings"
        )
        
        # Log console shortcuts
        shortcut_manager.register_shortcut(
            "Ctrl+a", 
            app_instance.select_all_logs, 
            context="logs",
            description="Select all logs"
        )
        shortcut_manager.register_shortcut(
            "Ctrl+c", 
            app_instance.copy_logs, 
            context="logs",
            description="Copy logs"
        )
        shortcut_manager.register_shortcut(
            "Ctrl+f", 
            app_instance.search_logs, 
            context="logs",
            description="Search logs"
        )
        shortcut_manager.register_shortcut(
            "Ctrl+l", 
            app_instance.clear_logs, 
            context="logs",
            description="Clear logs"
        )
        
        # Progress view shortcuts
        shortcut_manager.register_shortcut(
            "Space", 
            app_instance.toggle_progress, 
            context="progress",
            description="Toggle progress animation"
        )
        shortcut_manager.register_shortcut(
            "Ctrl+Shift+P", 
            app_instance.show_progress_details, 
            context="progress",
            description="Show progress details"
        )


class ShortcutHelpDialog(ctk.CTkToplevel):
    """
    Dialog showing all available keyboard shortcuts.
    """
    
    def __init__(self, parent, shortcut_manager: KeyboardShortcutManager):
        super().__init__(parent)
        self.shortcut_manager = shortcut_manager
        self.title("Keyboard Shortcuts")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (800 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (600 // 2)
        self.geometry(f"+{x}+{y}")
        
        self._build_ui()
        
    def _build_ui(self):
        """Build the shortcuts help UI."""
        # Main container
        container = ctk.CTkScrollableFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            container,
            text="⌨️ Keyboard Shortcuts",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # Shortcuts sections
        self._add_shortcuts_section(container, "General", self.shortcut_manager.shortcuts)
        
        for context, shortcuts in self.shortcut_manager.context_shortcuts.items():
            self._add_shortcuts_section(container, context.title(), shortcuts)
            
        # Close button
        close_btn = ctk.CTkButton(
            container,
            text="Close",
            command=self.destroy,
            width=100
        )
        close_btn.pack(pady=(20, 0))
        
    def _add_shortcuts_section(self, parent, title: str, shortcuts: Dict[str, Callable]):
        """Add a section of shortcuts."""
        if not shortcuts:
            return
            
        # Section title
        section_title = ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        section_title.pack(anchor="w", pady=(20, 10))
        
        # Shortcuts list
        for key_combo, callback in shortcuts.items():
            shortcut_frame = ctk.CTkFrame(parent)
            shortcut_frame.pack(fill="x", pady=2)
            
            # Key combination
            key_label = ctk.CTkLabel(
                shortcut_frame,
                text=key_combo,
                font=ctk.CTkFont(size=14, weight="bold"),
                width=150,
                anchor="w"
            )
            key_label.pack(side="left", padx=10, pady=5)
            
            # Description
            desc_label = ctk.CTkLabel(
                shortcut_frame,
                text=getattr(callback, '__name__', 'Unknown'),
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            desc_label.pack(side="left", padx=10, pady=5)
