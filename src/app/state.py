"""
YouTube2Sheets App State Management
Centralized state management with EventBus for decoupled communication.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Optional
import threading
from enum import Enum


class AppStatus(Enum):
    """Application status states."""
    READY = "Ready"
    RUNNING = "Running"
    CANCELLING = "Cancelling"
    ERROR = "Error"
    COMPLETED = "Completed"


@dataclass
class AppState:
    """Centralized application state."""
    # Core status
    status: AppStatus = AppStatus.READY
    ready: bool = True
    current_job_id: Optional[str] = None
    
    # Progress tracking
    progress: float = 0.0
    progress_text: str = ""
    current_channel: str = ""
    processed_channels: int = 0
    total_channels: int = 0
    
    # API usage tracking
    youtube_quota_used: int = 0
    youtube_quota_limit: int = 10000
    sheets_requests: int = 0
    
    # Error tracking
    last_error: Optional[str] = None
    error_count: int = 0
    
    # UI state
    debug_logging: bool = False
    selected_tab: str = "AI_ML"
    available_tabs: List[str] = field(default_factory=list)
    
    # Configuration
    youtube_api_key: str = ""
    sheets_service_account: str = ""
    spreadsheet_url: str = ""


class EventBus:
    """Simple event bus for decoupled communication."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
    
    def on(self, event: str, callback: Callable) -> None:
        """Subscribe to an event."""
        with self._lock:
            if event not in self._subscribers:
                self._subscribers[event] = []
            self._subscribers[event].append(callback)
    
    def off(self, event: str, callback: Callable) -> None:
        """Unsubscribe from an event."""
        with self._lock:
            if event in self._subscribers:
                try:
                    self._subscribers[event].remove(callback)
                except ValueError:
                    pass  # Callback not found
    
    def emit(self, event: str, **data) -> None:
        """Emit an event with data."""
        with self._lock:
            callbacks = self._subscribers.get(event, []).copy()
        
        for callback in callbacks:
            try:
                callback(**data)
            except Exception as e:
                print(f"Error in event callback for {event}: {e}")


class ObservableVar:
    """Observable variable that notifies on changes."""
    
    def __init__(self, initial_value: Any = None):
        self._value = initial_value
        self._callbacks: List[Callable] = []
        self._lock = threading.Lock()
    
    @property
    def value(self) -> Any:
        return self._value
    
    @value.setter
    def value(self, new_value: Any) -> None:
        with self._lock:
            if self._value != new_value:
                old_value = self._value
                self._value = new_value
                for callback in self._callbacks:
                    try:
                        callback(new_value, old_value)
                    except Exception as e:
                        print(f"Error in observable callback: {e}")
    
    def subscribe(self, callback: Callable) -> None:
        """Subscribe to value changes."""
        with self._lock:
            self._callbacks.append(callback)
    
    def unsubscribe(self, callback: Callable) -> None:
        """Unsubscribe from value changes."""
        with self._lock:
            try:
                self._callbacks.remove(callback)
            except ValueError:
                pass


# Global instances
app_state = AppState()
event_bus = EventBus()

# Observable variables for UI binding
status_var = ObservableVar(AppStatus.READY)
progress_var = ObservableVar(0.0)
progress_text_var = ObservableVar("")
current_channel_var = ObservableVar("")
processed_channels_var = ObservableVar(0)
total_channels_var = ObservableVar(0)
error_count_var = ObservableVar(0)
debug_logging_var = ObservableVar(False)
selected_tab_var = ObservableVar("AI_ML")
available_tabs_var = ObservableVar([])
