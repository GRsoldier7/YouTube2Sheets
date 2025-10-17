"""
Tests for Async Wrapper
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.services.async_wrapper import AsyncWrapper
from src.services.youtube_service import YouTubeService, YouTubeConfig
from src.services.sheets_service import SheetsService, SheetsConfig

class TestAsyncWrapper:
    """Test cases for AsyncWrapper."""
    
    @pytest.fixture
    def async_wrapper(self, youtube_config, sheets_config):
        """Async wrapper fixture."""
        return AsyncWrapper(youtube_config, sheets_config)
    
    @pytest.mark.asyncio
    async def test_fetch_videos_async(self, async_wrapper):
        """Test async video fetching."""
        with patch.object(YouTubeService, 'fetch_channel_videos') as mock_fetch:
            mock_fetch.return_value = [{"video_id": "test1"}, {"video_id": "test2"}]
            
            videos = await async_wrapper.fetch_videos_async(["UC_test1", "UC_test2"])
            
            assert len(videos) == 4  # 2 videos per channel
            assert mock_fetch.call_count == 2
    
    @pytest.mark.asyncio
    async def test_write_videos_async(self, async_wrapper):
        """Test async video writing."""
        with patch.object(SheetsService, 'write_videos_to_sheet') as mock_write:
            mock_write.return_value = True
            
            videos = [{"video_id": "test1"}, {"video_id": "test2"}]
            success = await async_wrapper.write_videos_async(videos, "TestTab")
            
            assert success is True
            mock_write.assert_called_once_with(videos, "TestTab")
    
    @pytest.mark.asyncio
    async def test_get_tabs_async(self, async_wrapper):
        """Test async tab fetching."""
        with patch.object(SheetsService, 'get_sheet_tabs') as mock_tabs:
            mock_tabs.return_value = ["Tab1", "Tab2", "Tab3"]
            
            tabs = await async_wrapper.get_tabs_async()
            
            assert len(tabs) == 3
            assert "Tab1" in tabs
            assert "Tab2" in tabs
            assert "Tab3" in tabs
    
    def test_run_async_operation(self, async_wrapper):
        """Test running async operations."""
        async def test_coro():
            return "test_result"
        
        result = async_wrapper.run_async_operation(test_coro())
        assert result == "test_result"
