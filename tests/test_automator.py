#!/usr/bin/env python3
"""
Test Suite for YouTube2Sheets Automator
Tests core functionality, error handling, and resource cleanup
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.automator import YouTubeToSheetsAutomator, AutomatorConfig
from domain.models import RunConfig, Filters, Destination, RunStatus


class TestYouTubeToSheetsAutomator:
    """Test cases for YouTubeToSheetsAutomator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            'youtube_api_key': 'test_key',
            'google_sheets_service_account_json': 'test_service_account.json',
            'default_spreadsheet_url': 'https://docs.google.com/spreadsheets/d/test123/edit'
        }
        
        # Mock the services to avoid actual API calls
        with patch('services.automator.YouTubeService'), \
             patch('services.automator.SheetsService'), \
             patch('services.automator.ResponseCache'), \
             patch('services.automator.VideoDeduplicator'), \
             patch('services.automator.APICreditTracker'):
            self.automator = YouTubeToSheetsAutomator(self.config)
    
    def test_initialization(self):
        """Test automator initializes correctly."""
        assert self.automator.config.youtube_api_key == 'test_key'
        assert self.automator.config.service_account_file == 'test_service_account.json'
        assert hasattr(self.automator, 'background_tasks')
        assert isinstance(self.automator.background_tasks, set)
    
    def test_background_task_tracking(self):
        """Test background task tracking works correctly."""
        # Simulate adding a background task
        task = asyncio.create_task(asyncio.sleep(0.1))
        self.automator.background_tasks.add(task)
        task.add_done_callback(self.automator.background_tasks.discard)
        
        assert len(self.automator.background_tasks) == 1
        assert task in self.automator.background_tasks
        
        # Wait for task to complete
        asyncio.run(task)
        
        # Task should be removed from set
        assert len(self.automator.background_tasks) == 0
    
    def test_cleanup_cancels_background_tasks(self):
        """Test cleanup properly cancels background tasks."""
        # Create a mock task that won't complete
        mock_task = Mock()
        mock_task.done.return_value = False
        mock_task.cancel.return_value = True
        
        self.automator.background_tasks.add(mock_task)
        
        # Call cleanup
        self.automator.cleanup()
        
        # Verify task was cancelled
        mock_task.cancel.assert_called_once()
    
    def test_configuration_status(self):
        """Test configuration status reporting."""
        status = self.automator.get_configuration_status()
        
        assert status['youtube_api_configured'] is True
        assert status['sheets_configured'] is True
        assert status['spreadsheet_configured'] is True
        assert status['optimization_enabled'] is True
    
    def test_service_status(self):
        """Test service status reporting."""
        status = self.automator.get_service_status()
        
        assert 'youtube_service' in status
        assert 'sheets_service' in status
        assert 'optimization_active' in status
    
    def test_optimization_status(self):
        """Test optimization status reporting."""
        status = self.automator.get_optimization_status()
        
        assert 'etag_caching' in status
        assert 'deduplication' in status
        assert 'batch_processing' in status
        assert 'cache_hit_rate' in status
        assert 'duplicates_prevented' in status
    
    def test_extract_spreadsheet_id(self):
        """Test spreadsheet ID extraction from URL."""
        # Valid URL
        url = "https://docs.google.com/spreadsheets/d/1CIKN4b8L6Awdys5tv4Ht_LirSvHgx0Hscj9MMzBKjZg/edit"
        spreadsheet_id = self.automator._extract_spreadsheet_id(url)
        assert spreadsheet_id == "1CIKN4b8L6Awdys5tv4Ht_LirSvHgx0Hscj9MMzBKjZg"
        
        # URL with query parameters
        url_with_params = "https://docs.google.com/spreadsheets/d/1CIKN4b8L6Awdys5tv4Ht_LirSvHgx0Hscj9MMzBKjZg/edit#gid=0"
        spreadsheet_id = self.automator._extract_spreadsheet_id(url_with_params)
        assert spreadsheet_id == "1CIKN4b8L6Awdys5tv4Ht_LirSvHgx0Hscj9MMzBKjZg"
        
        # Invalid URL
        invalid_url = "https://example.com"
        spreadsheet_id = self.automator._extract_spreadsheet_id(invalid_url)
        assert spreadsheet_id == ""
        
        # Empty URL
        spreadsheet_id = self.automator._extract_spreadsheet_id("")
        assert spreadsheet_id == ""
    
    def test_apply_filters(self):
        """Test video filtering logic."""
        from domain.models import Video
        
        # Create test videos
        videos = [
            Video(
                video_id="test1",
                title="Test Video 1",
                description="A test video",
                duration=120,  # 2 minutes
                published_at="2023-01-01T00:00:00Z",
                view_count=1000,
                like_count=50,
                comment_count=10,
                channel_id="test_channel",
                channel_title="Test Channel"
            ),
            Video(
                video_id="test2",
                title="Short Video",
                description="A short test",
                duration=30,  # 30 seconds
                published_at="2023-01-01T00:00:00Z",
                view_count=500,
                like_count=25,
                comment_count=5,
                channel_id="test_channel",
                channel_title="Test Channel"
            )
        ]
        
        # Test duration filter
        filters = Filters(min_duration=60, keywords=[], keyword_mode="include", exclude_shorts=False, max_results=50)
        filtered = self.automator._apply_filters(videos, filters)
        assert len(filtered) == 1  # Only the 2-minute video should pass
        
        # Test exclude shorts filter
        filters = Filters(min_duration=0, keywords=[], keyword_mode="include", exclude_shorts=True, max_results=50)
        filtered = self.automator._apply_filters(videos, filters)
        assert len(filtered) == 1  # Only the 2-minute video should pass (30s is a short)
        
        # Test keyword include filter
        filters = Filters(min_duration=0, keywords=["test"], keyword_mode="include", exclude_shorts=False, max_results=50)
        filtered = self.automator._apply_filters(videos, filters)
        assert len(filtered) == 2  # Both videos contain "test"
        
        # Test keyword exclude filter
        filters = Filters(min_duration=0, keywords=["short"], keyword_mode="exclude", exclude_shorts=False, max_results=50)
        filtered = self.automator._apply_filters(videos, filters)
        assert len(filtered) == 1  # Only the first video should pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
