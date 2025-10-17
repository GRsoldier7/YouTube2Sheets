"""
Test configuration and fixtures
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.services.youtube_service import YouTubeService, YouTubeConfig
from src.services.sheets_service import SheetsService, SheetsConfig
from src.services.enhanced_error_handler import EnhancedErrorHandler, ErrorContext
from src.services.async_wrapper import AsyncWrapper

@pytest.fixture
def youtube_config():
    """YouTube configuration fixture."""
    return YouTubeConfig(api_key="test_api_key")

@pytest.fixture
def sheets_config():
    """Sheets configuration fixture."""
    return SheetsConfig(
        service_account_file="test_credentials.json",
        spreadsheet_id="test_spreadsheet_id"
    )

@pytest.fixture
def error_handler():
    """Error handler fixture."""
    return EnhancedErrorHandler()

@pytest.fixture
def async_wrapper(youtube_config, sheets_config):
    """Async wrapper fixture."""
    return AsyncWrapper(youtube_config, sheets_config)

@pytest.fixture
def mock_video_data():
    """Mock video data fixture."""
    return {
        "video_id": "test_video_id",
        "title": "Test Video",
        "description": "Test Description",
        "channel_id": "test_channel_id",
        "channel_title": "Test Channel",
        "published_at": datetime.now(),
        "duration": 300,
        "view_count": 1000,
        "like_count": 50,
        "comment_count": 10,
        "thumbnail_url": "https://example.com/thumb.jpg",
        "url": "https://youtube.com/watch?v=test_video_id",
        "tags": ["test", "video"]
    }
