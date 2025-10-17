"""
Domain models for YouTube2Sheets
Core business entities and data structures
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class RunStatus(Enum):
    """Status of a run operation."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Video:
    """YouTube video data model."""
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: datetime
    duration: int  # in seconds
    view_count: int
    like_count: int
    comment_count: int
    thumbnail_url: str
    url: str
    tags: List[str] = field(default_factory=list)
    category_id: Optional[str] = None
    etag: Optional[str] = None


    def to_dict(self) -> dict:
        """Convert Video object to dictionary for Google Sheets writing."""
        return {
            'id': self.video_id,
            'title': self.title,
            'description': self.description,
            'channel_id': self.channel_id,
            'channel_title': self.channel_title,
            'published_at': self.published_at,
            'thumbnail_url': self.thumbnail_url,
            'url': self.url,
            'duration': self.duration,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'etag': self.etag
        }

@dataclass
class Channel:
    """YouTube channel data model."""
    channel_id: str
    title: str
    description: str
    subscriber_count: int
    video_count: int
    view_count: int
    thumbnail_url: str
    url: str
    etag: Optional[str] = None


@dataclass
class Filters:
    """Video filtering criteria."""
    keywords: List[str] = field(default_factory=list)
    keyword_mode: str = "include"  # "include" or "exclude"
    min_duration: int = 0  # in seconds
    exclude_shorts: bool = False
    max_results: int = 50


@dataclass
class Destination:
    """Google Sheets destination configuration."""
    spreadsheet_id: str
    tab_name: str
    create_tab_if_missing: bool = True


@dataclass
class RunConfig:
    """Configuration for a YouTube2Sheets run."""
    channels: List[str]
    filters: Filters
    destination: Destination
    batch_size: int = 100
    rate_limit_delay: float = 1.0


@dataclass
class RunResult:
    """Result of a YouTube2Sheets run."""
    run_id: str
    status: RunStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    videos_processed: int = 0
    videos_written: int = 0
    errors: List[str] = field(default_factory=list)
    api_quota_used: int = 0
    duration_seconds: Optional[float] = None

    @property
    def is_complete(self) -> bool:
        """Check if the run is complete."""
        return self.status in [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED]

    @property
    def success_rate(self) -> float:
        """Calculate success rate of video processing."""
        if self.videos_processed == 0:
            return 0.0
        return self.videos_written / self.videos_processed


@dataclass
class AppConfig:
    """Application configuration."""
    youtube_api_key: str
    google_sheets_service_account_file: str
    default_spreadsheet_url: str
    debug: bool = False
    log_level: str = "INFO"
    max_workers: int = 4
    cache_ttl: int = 3600  # 1 hour in seconds


@dataclass
class Job:
    """Background job data model."""
    job_id: str
    config: RunConfig
    status: RunStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[RunResult] = None
    error_message: Optional[str] = None


@dataclass
class SheetRef:
    """Google Sheets reference."""
    spreadsheet_id: str
    tab_name: str
    range: Optional[str] = None


@dataclass
class YouTubeConfig:
    """YouTube API configuration."""
    api_key: str
    secondary_api_key: Optional[str] = None
    rate_limit_delay: float = 1.0
    max_retries: int = 3


@dataclass
class SheetsConfig:
    """Google Sheets API configuration."""
    service_account_file: str
    spreadsheet_id: str
    tab_name: str = "YouTube Data"
    create_tab_if_missing: bool = True