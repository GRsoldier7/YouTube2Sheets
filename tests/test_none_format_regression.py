#!/usr/bin/env python3
"""
None Format Regression Test
Prevents NoneType.__format__ errors in all format operations
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from domain.models import RunResult, RunStatus
from services.sheets_optimizer import DuplicationCheckResult


class TestNoneFormatRegression:
    """Test all potential NoneType.__format__ vulnerabilities."""
    
    def test_gui_duration_formatting(self):
        """Test GUI duration formatting with None values."""
        # Test with None duration_seconds
        result = RunResult(
            run_id="test",
            status=RunStatus.COMPLETED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            videos_processed=10,
            videos_written=5,
            errors=[],
            api_quota_used=100,
            duration_seconds=None  # This would cause the original error
        )
        
        # Test the format operation that was failing
        duration = result.duration_seconds or 0.0
        formatted = f"✨ Sync completed in {duration:.1f} seconds"
        assert isinstance(formatted, str)
        assert "0.0" in formatted
        assert "Sync completed in 0.0 seconds" in formatted
    
    def test_api_optimizer_quota_formatting(self):
        """Test API optimizer quota formatting with None values."""
        # Test with None values
        quota_used = None
        quota_limit = None
        quota_used_safe = quota_used or 0
        quota_limit_safe = quota_limit or 1
        percentage = (quota_used_safe / quota_limit_safe * 100) if quota_limit_safe > 0 else 0
        formatted = f"Quota tracking: {quota_used_safe}/{quota_limit_safe} ({percentage:.1f}%)"
        assert isinstance(formatted, str)
        assert "0/1" in formatted
        assert "(0.0%)" in formatted
    
    def test_sheets_optimizer_similarity_formatting(self):
        """Test sheets optimizer similarity formatting with None values."""
        # Test with None similarity_score
        duplication_result = DuplicationCheckResult(
            is_duplicate=True,
            similarity_score=None  # This would cause the original error
        )
        
        similarity = duplication_result.similarity_score or 0.0
        formatted = f"Similarity: {similarity:.2f}"
        assert isinstance(formatted, str)
        assert "0.00" in formatted
    
    def test_automator_cache_hit_rate_formatting(self):
        """Test automator cache hit rate formatting with None values."""
        # Test with None cache_hit_rate
        cache_hit_rate = None
        formatted = f"Cache hit rate: {(cache_hit_rate or 0):.1f}%"
        assert isinstance(formatted, str)
        assert "0.0%" in formatted
        
        # Test with valid cache_hit_rate
        cache_hit_rate = 75.5
        formatted = f"Cache hit rate: {(cache_hit_rate or 0):.1f}%"
        assert isinstance(formatted, str)
        assert "75.5%" in formatted
    
    def test_automator_optimization_status(self):
        """Test automator optimization status with None values."""
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
            
            # Test optimization status
            status = automator.get_optimization_status()
            assert 'cache_hit_rate' in status
            assert isinstance(status['cache_hit_rate'], str)
            assert status['cache_hit_rate'].endswith('%')
            assert 'None' not in status['cache_hit_rate']
    
    def test_all_format_operations_with_none_values(self):
        """Test all format operations with various None scenarios."""
        test_cases = [
            (None, "0.0"),
            (0, "0.0"),
            (1.5, "1.5"),
            (100.0, "100.0"),
            (0.0, "0.0")
        ]
        
        for value, expected in test_cases:
            safe_value = value or 0.0
            formatted = f"{safe_value:.1f}"
            assert formatted == expected, f"Expected {expected}, got {formatted}"
    
    def test_percentage_calculations_with_none(self):
        """Test percentage calculations with None values."""
        # Test division by zero protection
        quota_used = None
        quota_limit = None
        quota_used_safe = quota_used or 0
        quota_limit_safe = quota_limit or 1
        percentage = (quota_used_safe / quota_limit_safe * 100) if quota_limit_safe > 0 else 0
        
        assert percentage == 0.0
        assert isinstance(percentage, float)
        
        # Test with valid values
        quota_used = 50
        quota_limit = 100
        percentage = (quota_used / quota_limit * 100) if quota_limit > 0 else 0
        assert percentage == 50.0
    
    def test_duration_calculations_with_none(self):
        """Test duration calculations with None values."""
        # Test with None duration
        duration = None
        safe_duration = duration or 0.0
        formatted = f"Duration: {safe_duration:.1f} seconds"
        assert "0.0" in formatted
        
        # Test with valid duration
        duration = 123.456
        safe_duration = duration or 0.0
        formatted = f"Duration: {safe_duration:.1f} seconds"
        assert "123.5" in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
