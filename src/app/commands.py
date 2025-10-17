"""
YouTube2Sheets Commands
Command pattern implementation for decoupled action handling.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .state import app_state, event_bus, AppStatus


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    message: str = ""
    data: Optional[Dict[str, Any]] = None


class Command(ABC):
    """Base command interface."""
    
    @abstractmethod
    def execute(self) -> CommandResult:
        """Execute the command."""
        pass
    
    @abstractmethod
    def can_execute(self) -> bool:
        """Check if command can be executed."""
        pass


class StartRunCommand(Command):
    """Command to start a YouTube to Sheets sync run."""
    
    def __init__(self, channels: List[str], tab: str, min_duration: int, 
                 keywords: str, exclude_shorts: bool, automator_service):
        self.channels = channels
        self.tab = tab
        self.min_duration = min_duration
        self.keywords = keywords
        self.exclude_shorts = exclude_shorts
        self.automator_service = automator_service
    
    def can_execute(self) -> bool:
        """Check if we can start a run."""
        return (app_state.status == AppStatus.READY and 
                len(self.channels) > 0 and 
                self.tab and
                self.automator_service is not None)
    
    def execute(self) -> CommandResult:
        """Execute the sync run."""
        if not self.can_execute():
            return CommandResult(
                success=False, 
                message="Cannot start run: invalid state or missing parameters"
            )
        
        try:
            # Update state
            app_state.status = AppStatus.RUNNING
            app_state.ready = False
            app_state.current_channel = ""
            app_state.processed_channels = 0
            app_state.total_channels = len(self.channels)
            app_state.progress = 0.0
            app_state.progress_text = "Starting sync..."
            app_state.last_error = None
            app_state.error_count = 0
            
            # Emit events
            event_bus.emit("status_changed", status=AppStatus.RUNNING)
            event_bus.emit("progress_changed", progress=0.0, text="Starting sync...")
            event_bus.emit("run_started", channels=self.channels, tab=self.tab)
            
            # Start the actual sync (this would be async in real implementation)
            # For now, we'll just emit a success event
            event_bus.emit("run_completed", success=True, message="Sync completed successfully")
            
            return CommandResult(
                success=True,
                message="Sync started successfully",
                data={"channels": self.channels, "tab": self.tab}
            )
            
        except Exception as e:
            app_state.status = AppStatus.ERROR
            app_state.last_error = str(e)
            app_state.error_count += 1
            
            event_bus.emit("status_changed", status=AppStatus.ERROR)
            event_bus.emit("error_occurred", error=str(e))
            
            return CommandResult(
                success=False,
                message=f"Failed to start sync: {str(e)}"
            )


class CancelRunCommand(Command):
    """Command to cancel a running sync."""
    
    def __init__(self, automator_service):
        self.automator_service = automator_service
    
    def can_execute(self) -> bool:
        """Check if we can cancel the run."""
        return app_state.status == AppStatus.RUNNING
    
    def execute(self) -> CommandResult:
        """Execute the cancellation."""
        if not self.can_execute():
            return CommandResult(
                success=False,
                message="No active run to cancel"
            )
        
        try:
            # Update state
            app_state.status = AppStatus.CANCELLING
            app_state.progress_text = "Cancelling..."
            
            # Emit events
            event_bus.emit("status_changed", status=AppStatus.CANCELLING)
            event_bus.emit("run_cancelled")
            
            # Here you would actually cancel the running operation
            # For now, we'll just complete the cancellation
            app_state.status = AppStatus.READY
            app_state.ready = True
            app_state.progress = 0.0
            app_state.progress_text = "Ready"
            
            event_bus.emit("status_changed", status=AppStatus.READY)
            
            return CommandResult(
                success=True,
                message="Run cancelled successfully"
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to cancel run: {str(e)}"
            )


class RefreshTabsCommand(Command):
    """Command to refresh Google Sheets tabs."""
    
    def __init__(self, sheets_service):
        self.sheets_service = sheets_service
    
    def can_execute(self) -> bool:
        """Check if we can refresh tabs."""
        return (app_state.status == AppStatus.READY and 
                self.sheets_service is not None)
    
    def execute(self) -> CommandResult:
        """Execute the tab refresh."""
        if not self.can_execute():
            return CommandResult(
                success=False,
                message="Cannot refresh tabs: invalid state or missing service"
            )
        
        try:
            # Update state
            app_state.progress_text = "Refreshing tabs..."
            event_bus.emit("progress_changed", progress=0.0, text="Refreshing tabs...")
            
            # Here you would actually call the sheets service
            # For now, we'll simulate with some sample tabs
            sample_tabs = ["AI_ML", "Data_Science", "Programming", "Tutorials"]
            app_state.available_tabs = sample_tabs
            
            # Emit events
            event_bus.emit("tabs_refreshed", tabs=sample_tabs)
            event_bus.emit("progress_changed", progress=100.0, text="Tabs refreshed")
            
            return CommandResult(
                success=True,
                message=f"Refreshed {len(sample_tabs)} tabs",
                data={"tabs": sample_tabs}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to refresh tabs: {str(e)}"
            )


class ScheduleRunCommand(Command):
    """Command to schedule a run."""
    
    def __init__(self, job_config: Dict[str, Any], scheduler_service):
        self.job_config = job_config
        self.scheduler_service = scheduler_service
    
    def can_execute(self) -> bool:
        """Check if we can schedule a run."""
        return (app_state.status == AppStatus.READY and 
                self.scheduler_service is not None and
                self.job_config.get("job_id") and
                self.job_config.get("channel"))
    
    def execute(self) -> CommandResult:
        """Execute the scheduling."""
        if not self.can_execute():
            return CommandResult(
                success=False,
                message="Cannot schedule run: invalid state or missing parameters"
            )
        
        try:
            # Here you would actually call the scheduler service
            # For now, we'll just simulate success
            event_bus.emit("job_scheduled", job_config=self.job_config)
            
            return CommandResult(
                success=True,
                message=f"Job '{self.job_config['job_id']}' scheduled successfully",
                data={"job_config": self.job_config}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to schedule job: {str(e)}"
            )


class CommandInvoker:
    """Command invoker that manages command execution."""
    
    def __init__(self):
        self.history: List[Command] = []
        self.max_history = 100
    
    def execute(self, command: Command) -> CommandResult:
        """Execute a command."""
        if not command.can_execute():
            return CommandResult(
                success=False,
                message="Command cannot be executed in current state"
            )
        
        try:
            result = command.execute()
            
            # Add to history
            self.history.append(command)
            if len(self.history) > self.max_history:
                self.history.pop(0)
            
            return result
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Command execution failed: {str(e)}"
            )
    
    def undo_last(self) -> CommandResult:
        """Undo the last command (if supported)."""
        if not self.history:
            return CommandResult(
                success=False,
                message="No commands to undo"
            )
        
        # For now, we don't implement undo functionality
        # This would require each command to implement an undo method
        return CommandResult(
            success=False,
            message="Undo not implemented"
        )


# Global command invoker
command_invoker = CommandInvoker()
