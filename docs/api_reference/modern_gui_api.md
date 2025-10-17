# Modern GUI API Reference

## ModernYouTube2SheetsGUI Class

The main application class that orchestrates all GUI components.

### Constructor
```python
ModernYouTube2SheetsGUI()
```

### Methods

#### UI Building Methods
- `_build_modern_ui()`: Builds the complete modern UI
- `_build_header()`: Creates the application header
- `_build_main_content()`: Builds the main content area
- `_build_sync_tab()`: Creates the sync tab
- `_build_scheduler_tab()`: Creates the scheduler tab
- `_build_analytics_tab()`: Creates the analytics tab
- `_build_logs_tab()`: Creates the logs tab

#### Configuration Methods
- `_build_config_section(parent)`: Builds configuration section
- `_build_filter_config()`: Creates filter configuration
- `_build_duration_config()`: Creates duration configuration
- `_build_keyword_mode_selector()`: Creates keyword mode selector

#### Progress Methods
- `_build_progress_section(parent)`: Builds progress section
- `_build_progress_bar()`: Creates progress bar
- `_build_status_indicator()`: Creates status indicator

#### Input Methods
- `_add_modern_input(parent, label, var_name, **kwargs)`: Adds modern input field
- `_add_modern_button(parent, text, command, **kwargs)`: Adds modern button

#### Event Handlers
- `_start_sync()`: Starts sync process
- `_stop_sync()`: Stops sync process
- `_refresh_data()`: Refreshes data
- `_clear_logs()`: Clears log console
- `_open_settings()`: Opens settings dialog
- `_show_help()`: Shows help dialog

#### Shortcut Methods
- `open_file()`: Open file dialog
- `save_file()`: Save file dialog
- `new_file()`: Create new file
- `undo()`: Undo action
- `redo()`: Redo action
- `copy()`: Copy action
- `paste()`: Paste action
- `cut()`: Cut action
- `select_all()`: Select all action
- `toggle_fullscreen()`: Toggle fullscreen mode
- `zoom_in()`: Zoom in
- `zoom_out()`: Zoom out
- `zoom_reset()`: Reset zoom
- `focus_next()`: Focus next widget
- `focus_previous()`: Focus previous widget
- `focus_first()`: Focus first widget
- `focus_last()`: Focus last widget
- `refresh()`: Refresh data
- `show_help()`: Show help dialog
- `show_shortcuts()`: Show shortcuts dialog
- `run_scheduler()`: Run scheduler
- `open_settings()`: Open settings dialog
- `quit()`: Quit application
- `close_window()`: Close window
- `toggle_debug()`: Toggle debug mode
- `show_debug()`: Show debug info
- `select_all_logs()`: Select all logs
- `copy_logs()`: Copy logs
- `search_logs()`: Search logs
- `clear_logs()`: Clear logs
- `toggle_progress()`: Toggle progress animation
- `show_progress_details()`: Show progress details
- `close_settings()`: Close settings dialog
- `save_settings()`: Save settings
- `start_sync()`: Start sync process
- `stop_sync()`: Stop sync process

## ModernTheme Class

Centralized theme management system.

### Constructor
```python
ModernTheme()
```

### Properties
- `colors`: Color palette
- `typography`: Font definitions
- `spacing`: Spacing standards
- `shadows`: Shadow definitions

### Methods
- `get_button_style(variant)`: Get button styling
- `get_input_style()`: Get input field styling
- `get_card_style()`: Get card styling
- `get_slider_style()`: Get slider styling
- `get_text_style(variant)`: Get text styling
- `apply_theme()`: Apply theme to application

## Glassmorphism Components

### FloatingCard Class
Elevated container with glassmorphism effect.

```python
FloatingCard(parent, elevation=8, **kwargs)
```

**Parameters:**
- `parent`: Parent widget
- `elevation`: Elevation level (0-10)
- `**kwargs`: Additional CTkFrame parameters

### AnimatedButton Class
Interactive button with hover effects.

```python
AnimatedButton(parent, text, command, **kwargs)
```

**Parameters:**
- `parent`: Parent widget
- `text`: Button text
- `command`: Click callback
- `**kwargs`: Additional CTkButton parameters

### StatusBadge Class
Status indicator with modern styling.

```python
StatusBadge(parent, status, **kwargs)
```

**Parameters:**
- `parent`: Parent widget
- `status`: Status text ("idle", "running", "success", "error")
- `**kwargs`: Additional CTkLabel parameters

### ModernTooltip Class
Contextual help tooltip.

```python
ModernTooltip(widget, text, delay=500)
```

**Parameters:**
- `widget`: Widget to attach tooltip to
- `text`: Tooltip text
- `delay`: Show delay in milliseconds

## Enhanced Scrolling Components

### EnhancedLogConsole Class
Enhanced log console with smooth scrolling.

```python
EnhancedLogConsole(parent, **kwargs)
```

**Methods:**
- `append_log(message, level)`: Add log message
- `clear_logs()`: Clear all logs
- `set_auto_scroll(enabled)`: Enable/disable auto-scroll

### ResponsiveProgressBar Class
Responsive progress indicator.

```python
ResponsiveProgressBar(parent, **kwargs)
```

**Methods:**
- `set_progress(value)`: Set progress (0-100)
- `set_indeterminate(enabled)`: Enable/disable indeterminate mode
- `set_status(status)`: Set status text

## Keyboard Shortcuts System

### KeyboardShortcutManager Class
Manages keyboard shortcuts and navigation.

```python
KeyboardShortcutManager(root)
```

**Methods:**
- `register_shortcut(key, callback, description)`: Register shortcut
- `unregister_shortcut(key)`: Unregister shortcut
- `set_context(context)`: Set current context
- `get_shortcuts()`: Get all shortcuts

### ModernNavigation Class
Handles widget navigation.

```python
ModernNavigation()
```

**Methods:**
- `register_widget(widget, category)`: Register widget for navigation
- `focus_next(category)`: Focus next widget
- `focus_previous(category)`: Focus previous widget
- `focus_first(category)`: Focus first widget
- `focus_last(category)`: Focus last widget

### AccessibilityManager Class
Manages accessibility features.

```python
AccessibilityManager()
```

**Methods:**
- `enable_screen_reader()`: Enable screen reader support
- `set_high_contrast(enabled)`: Enable/disable high contrast
- `set_large_text(enabled)`: Enable/disable large text

## Performance Optimization

### PerformanceMonitor Class
Monitors application performance.

```python
PerformanceMonitor()
```

**Methods:**
- `start_monitoring()`: Start performance monitoring
- `stop_monitoring()`: Stop performance monitoring
- `get_metrics()`: Get performance metrics
- `log_metric(name, value)`: Log custom metric

### AsyncTaskManager Class
Manages asynchronous tasks.

```python
AsyncTaskManager()
```

**Methods:**
- `run_async(func, *args, **kwargs)`: Run function asynchronously
- `run_in_thread(func, *args, **kwargs)`: Run function in thread
- `cancel_task(task_id)`: Cancel running task
- `get_task_status(task_id)`: Get task status

### UIUpdateQueue Class
Queues and batches UI updates.

```python
UIUpdateQueue()
```

**Methods:**
- `queue_update(func, *args, **kwargs)`: Queue UI update
- `process_updates()`: Process queued updates
- `clear_queue()`: Clear update queue

## Settings Dialog

### ModernSettingsDialog Class
Modern settings dialog.

```python
ModernSettingsDialog(parent, settings)
```

**Parameters:**
- `parent`: Parent window
- `settings`: Settings dictionary

**Methods:**
- `show()`: Show dialog
- `hide()`: Hide dialog
- `get_settings()`: Get current settings
- `set_settings(settings)`: Set settings

## Usage Examples

### Creating a Custom Component

```python
from src.gui.components.modern_theme import theme
from src.gui.components.glassmorphism import FloatingCard, AnimatedButton

# Create a floating card
card = FloatingCard(parent, elevation=8)
card.pack(fill="x", pady=10)

# Add an animated button
button = AnimatedButton(
    card,
    text="Click me",
    command=self.on_button_click,
    **theme.get_button_style("primary")
)
button.pack(pady=10)
```

### Adding Custom Shortcuts

```python
from src.gui.components.keyboard_shortcuts import KeyboardShortcutManager

# Create shortcut manager
shortcut_manager = KeyboardShortcutManager(self.root)

# Register custom shortcut
shortcut_manager.register_shortcut(
    "Ctrl+Shift+MyAction",
    self.my_custom_action,
    description="My custom action"
)
```

### Using the Theme System

```python
from src.gui.components.modern_theme import theme

# Get theme colors
primary_color = theme.colors.primary
surface_color = theme.colors.surface

# Get component styles
button_style = theme.get_button_style("primary")
input_style = theme.get_input_style()
text_style = theme.get_text_style("heading")

# Apply styles to widgets
button = ctk.CTkButton(parent, **button_style)
entry = ctk.CTkEntry(parent, **input_style)
label = ctk.CTkLabel(parent, **text_style)
```

## Error Handling

All components include comprehensive error handling:

- **Validation**: Input validation for all parameters
- **Graceful Degradation**: Fallbacks for unsupported features
- **Logging**: Detailed logging for debugging
- **User Feedback**: Clear error messages for users

## Threading and Concurrency

The GUI uses proper threading for:

- **Background Tasks**: Long-running operations
- **UI Updates**: Non-blocking interface updates
- **File Operations**: Asynchronous file I/O
- **Network Requests**: Non-blocking API calls

## Memory Management

- **Widget Cleanup**: Proper widget destruction
- **Event Unbinding**: Cleanup of event handlers
- **Resource Monitoring**: Memory usage tracking
- **Garbage Collection**: Automatic cleanup of unused objects

