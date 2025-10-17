"""Backend package for YouTube2Sheets."""

from .api_optimizer import APICreditTracker, ResponseCache, VideoDeduplicator
from .data_processor import VideoRecord, build_video_record
from .exceptions import (
    APIError,
    ConfigurationError,
    ProcessingError,
    SchedulerError,
    ValidationError,
    YouTube2SheetsError,
)
from .filters import apply_filters
from .scheduler_runner import main as scheduler_main
from .scheduler_sheet_manager import JobConfiguration, JobStatus, ScheduleType, SchedulerSheetManager
from .security_manager import default_spreadsheet_url, get_env_var, validate_service_account_path
from .sheet_formatter import SheetFormatter
from .youtube2sheets import SyncConfig, YouTubeToSheetsAutomator

__all__ = [
    # Core Automator
    "YouTubeToSheetsAutomator",
    "SyncConfig",
    # API Optimization
    "APICreditTracker",
    "ResponseCache",
    "VideoDeduplicator",
    # Data Processing
    "VideoRecord",
    "build_video_record",
    "apply_filters",
    # Sheet Formatting
    "SheetFormatter",
    # Scheduler
    "SchedulerSheetManager",
    "JobConfiguration",
    "JobStatus",
    "ScheduleType",
    "scheduler_main",
    # Security
    "get_env_var",
    "validate_service_account_path",
    "default_spreadsheet_url",
    # Exceptions
    "YouTube2SheetsError",
    "APIError",
    "ValidationError",
    "ProcessingError",
    "ConfigurationError",
    "SchedulerError",
]