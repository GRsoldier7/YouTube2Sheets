#!/usr/bin/env python3
"""
Performance Test Suite for YouTube2Sheets
Tests performance benchmarks, caching, and optimization
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.automator import YouTubeToSheetsAutomator
from backend.api_optimizer import ResponseCache, VideoDeduplicator, APICreditTracker
from domain.models import RunConfig, Filters, Destination


class TestPerformance:
    """Test performance characteristics and optimizations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            'youtube_api_key': 'test_key',
            'google_sheets_service_account_json': 'test_service_account.json',
            'default_spreadsheet_url': 'https://docs.google.com/spreadsheets/d/test123/edit'
        }
    
    def test_cache_performance(self):
        """Test cache hit/miss performance."""
        cache = ResponseCache("test_cache.json")
        
        # Test cache miss
        start_time = time.time()
        result = cache.get("test_key", "test_etag")
        miss_time = time.time() - start_time
        
        assert result is None  # Cache miss
        assert miss_time < 0.001  # Should be very fast
        
        # Test cache set
        start_time = time.time()
        cache.set("test_key", {"data": "test"}, "test_etag")
        set_time = time.time() - start_time
        
        assert set_time < 0.001  # Should be very fast
        
        # Test cache hit
        start_time = time.time()
        result = cache.get("test_key", "test_etag")
        hit_time = time.time() - start_time
        
        assert result == {"data": "test"}  # Cache hit
        assert hit_time < 0.001  # Should be very fast
        assert hit_time < miss_time  # Hit should be faster than miss
    
    def test_deduplication_performance(self):
        """Test deduplication performance with large datasets."""
        dedup = VideoDeduplicator()
        
        # Test with large number of videos
        video_ids = [f"video_{i}" for i in range(10000)]
        
        start_time = time.time()
        new_videos = dedup.filter_new_videos(video_ids)
        filter_time = time.time() - start_time
        
        assert len(new_videos) == 10000  # All should be new
        assert filter_time < 0.1  # Should be fast even with 10k videos
        
        # Test duplicate filtering
        start_time = time.time()
        new_videos = dedup.filter_new_videos(video_ids)
        duplicate_time = time.time() - start_time
        
        assert len(new_videos) == 0  # All should be duplicates
        assert duplicate_time < 0.1  # Should be fast
    
    def test_api_quota_tracking(self):
        """Test API quota tracking performance."""
        tracker = APICreditTracker(daily_quota=1000)
        
        # Test quota consumption
        start_time = time.time()
        for _ in range(100):
            tracker.consume(1, api_name="test")
        consume_time = time.time() - start_time
        
        assert consume_time < 0.01  # Should be very fast
        assert tracker.usage_today == 100
        
        # Test status retrieval
        start_time = time.time()
        status = tracker.get_status()
        status_time = time.time() - start_time
        
        assert status_time < 0.001  # Should be very fast
        assert status['usage'] == 100
        assert status['remaining'] == 900
    
    def test_automator_initialization_performance(self):
        """Test automator initialization performance."""
        with patch('services.automator.YouTubeService'), \
             patch('services.automator.SheetsService'), \
             patch('services.automator.ResponseCache'), \
             patch('services.automator.VideoDeduplicator'), \
             patch('services.automator.APICreditTracker'):
            
            start_time = time.time()
            automator = YouTubeToSheetsAutomator(self.config)
            init_time = time.time() - start_time
            
            assert init_time < 1.0  # Should initialize quickly
            assert hasattr(automator, 'background_tasks')
    
    def test_batch_processing_performance(self):
        """Test batch processing performance."""
        # Mock the services
        with patch('services.automator.YouTubeService') as mock_yt, \
             patch('services.automator.SheetsService') as mock_sheets, \
             patch('services.automator.ResponseCache'), \
             patch('services.automator.VideoDeduplicator'), \
             patch('services.automator.APICreditTracker'):
            
            # Setup mocks
            mock_yt_instance = Mock()
            mock_yt_instance.get_channel_videos.return_value = []
            mock_yt.return_value = mock_yt_instance
            
            mock_sheets_instance = Mock()
            mock_sheets_instance.create_sheet_tab.return_value = True
            mock_sheets_instance.write_videos_to_sheet.return_value = True
            mock_sheets.return_value = mock_sheets_instance
            
            automator = YouTubeToSheetsAutomator(self.config)
            
            # Test batch processing
            run_config = RunConfig(
                channels=["test_channel"],
                filters=Filters(min_duration=0, keywords=[], keyword_mode="include", exclude_shorts=False, max_results=50),
                destination=Destination(spreadsheet_id="test", tab_name="test"),
                batch_size=100,
                rate_limit_delay=0.1
            )
            
            start_time = time.time()
            result = automator.sync_channels_to_sheets(run_config)
            sync_time = time.time() - start_time
            
            assert result.status == RunStatus.COMPLETED
            assert sync_time < 5.0  # Should complete quickly in test environment
    
    def test_memory_usage(self):
        """Test memory usage doesn't grow excessively."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create multiple automator instances
        with patch('services.automator.YouTubeService'), \
             patch('services.automator.SheetsService'), \
             patch('services.automator.ResponseCache'), \
             patch('services.automator.VideoDeduplicator'), \
             patch('services.automator.APICreditTracker'):
            
            automators = []
            for _ in range(10):
                automator = YouTubeToSheetsAutomator(self.config)
                automators.append(automator)
            
            final_memory = process.memory_info().rss
            memory_growth = final_memory - initial_memory
            
            # Memory growth should be reasonable (less than 50MB)
            assert memory_growth < 50 * 1024 * 1024
    
    def test_concurrent_operations(self):
        """Test concurrent operations don't cause race conditions."""
        cache = ResponseCache("test_concurrent_cache.json")
        
        async def concurrent_operations():
            """Run concurrent cache operations."""
            tasks = []
            for i in range(100):
                task = asyncio.create_task(self._cache_operation(cache, f"key_{i}"))
                tasks.append(task)
            
            await asyncio.gather(*tasks)
        
        async def _cache_operation(self, cache, key):
            """Single cache operation."""
            cache.set(key, {"data": "test"}, "etag")
            result = cache.get(key, "etag")
            assert result == {"data": "test"}
        
        # Run concurrent operations
        start_time = time.time()
        asyncio.run(concurrent_operations())
        concurrent_time = time.time() - start_time
        
        assert concurrent_time < 1.0  # Should complete quickly
        
        # Verify cache statistics
        stats = cache.get_statistics()
        assert stats['entries'] == 100
        assert stats['hits'] == 100
        assert stats['misses'] == 100  # Initial misses
    
    def test_error_handling_performance(self):
        """Test that error handling doesn't significantly impact performance."""
        with patch('services.automator.YouTubeService') as mock_yt, \
             patch('services.automator.SheetsService') as mock_sheets, \
             patch('services.automator.ResponseCache'), \
             patch('services.automator.VideoDeduplicator'), \
             patch('services.automator.APICreditTracker'):
            
            # Setup mocks to raise exceptions
            mock_yt_instance = Mock()
            mock_yt_instance.get_channel_videos.side_effect = Exception("API Error")
            mock_yt.return_value = mock_yt_instance
            
            mock_sheets_instance = Mock()
            mock_sheets_instance.create_sheet_tab.return_value = True
            mock_sheets.return_value = mock_sheets_instance
            
            automator = YouTubeToSheetsAutomator(self.config)
            
            run_config = RunConfig(
                channels=["test_channel"],
                filters=Filters(min_duration=0, keywords=[], keyword_mode="include", exclude_shorts=False, max_results=50),
                destination=Destination(spreadsheet_id="test", tab_name="test"),
                batch_size=100,
                rate_limit_delay=0.1
            )
            
            start_time = time.time()
            result = automator.sync_channels_to_sheets(run_config)
            error_time = time.time() - start_time
            
            assert result.status == RunStatus.FAILED
            assert error_time < 2.0  # Error handling should be fast
            assert len(result.errors) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
