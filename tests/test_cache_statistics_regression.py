#!/usr/bin/env python3
"""
Cache Statistics Regression Test
Prevents NoneType.__format__ errors in cache statistics
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from backend.api_optimizer import ResponseCache


class TestCacheStatisticsRegression:
    """Test cache statistics to prevent NoneType.__format__ errors."""
    
    def test_cache_statistics_initialization(self):
        """Test that cache statistics are properly initialized."""
        cache = ResponseCache("test_cache.json")
        
        # Get statistics
        stats = cache.get_statistics()
        
        # Verify all required keys exist with proper types
        assert 'entries' in stats
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'hit_rate' in stats
        
        # Verify hit_rate is numeric (not None)
        assert isinstance(stats['hit_rate'], (int, float))
        assert stats['hit_rate'] >= 0
        assert stats['hit_rate'] <= 100
    
    def test_cache_statistics_with_no_operations(self):
        """Test cache statistics when no operations have been performed."""
        cache = ResponseCache("test_cache.json")
        
        # Get statistics before any operations
        stats = cache.get_statistics()
        
        # Should have default values, not None
        assert stats['entries'] == 0
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['hit_rate'] == 0.0
    
    def test_cache_statistics_after_operations(self):
        """Test cache statistics after cache operations."""
        cache = ResponseCache("test_cache.json")
        
        # Perform cache operations
        cache.set("key1", {"data": "test1"}, "etag1")
        cache.get("key1", "etag1")  # Hit
        cache.get("key2", "etag2")  # Miss
        
        # Get statistics
        stats = cache.get_statistics()
        
        # Verify statistics are correct
        assert stats['entries'] == 1
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 50.0  # 1 hit out of 2 total requests
    
    def test_cache_statistics_format_safety(self):
        """Test that cache statistics can be safely formatted."""
        cache = ResponseCache("test_cache.json")
        
        # Get statistics
        stats = cache.get_statistics()
        
        # Test format operations that previously failed
        hit_rate = stats.get('hit_rate')
        
        # These should not raise TypeError
        formatted_rate = f"{hit_rate:.1f}%"
        assert isinstance(formatted_rate, str)
        assert formatted_rate.endswith('%')
        
        # Test with None safety (should not happen but test defensive code)
        safe_rate = hit_rate or 0
        safe_formatted = f"{safe_rate:.1f}%"
        assert isinstance(safe_formatted, str)
    
    def test_automator_cache_statistics_integration(self):
        """Test automator integration with cache statistics."""
        from services.automator import YouTubeToSheetsAutomator
        
        config = {
            'youtube_api_key': 'test_key',
            'google_sheets_service_account_json': 'test.json',
            'default_spreadsheet_url': 'https://docs.google.com/spreadsheets/d/test/edit'
        }
        
        with patch('services.automator.YouTubeService'), \
             patch('services.automator.SheetsService'), \
             patch('services.automator.VideoDeduplicator'), \
             patch('services.automator.APICreditTracker'):
            
            automator = YouTubeToSheetsAutomator(config)
            
            # Test optimization status (where the error occurred)
            status = automator.get_optimization_status()
            
            # Verify cache_hit_rate is properly formatted
            assert 'cache_hit_rate' in status
            cache_hit_rate = status['cache_hit_rate']
            assert isinstance(cache_hit_rate, str)
            assert cache_hit_rate.endswith('%')
            
            # Verify no None values in format operations
            assert 'None' not in cache_hit_rate
            assert 'None' not in str(status)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
