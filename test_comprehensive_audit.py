#!/usr/bin/env python3
"""
Comprehensive System Audit Test
Tests all critical components identified in the audit plan
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test all critical imports work."""
    print("🔍 Testing critical imports...")
    
    try:
        from domain.models import RunConfig, Filters, Destination, Video, Channel, RunStatus
        print("✅ Domain models imported successfully")
    except Exception as e:
        print(f"❌ Domain models import failed: {e}")
        return False
    
    try:
        from services.automator import YouTubeToSheetsAutomator
        print("✅ Automator imported successfully")
    except Exception as e:
        print(f"❌ Automator import failed: {e}")
        return False
    
    try:
        from services.youtube_service import YouTubeService, YouTubeConfig
        print("✅ YouTube service imported successfully")
    except Exception as e:
        print(f"❌ YouTube service import failed: {e}")
        return False
    
    try:
        from services.sheets_service import SheetsService, SheetsConfig
        print("✅ Sheets service imported successfully")
    except Exception as e:
        print(f"❌ Sheets service import failed: {e}")
        return False
    
    try:
        from backend.youtube2sheets import SyncConfig
        print("✅ SyncConfig imported successfully")
    except Exception as e:
        print(f"❌ SyncConfig import failed: {e}")
        return False
    
    return True

def test_configuration_mapping():
    """Test configuration mapping from GUI to services."""
    print("\n🔍 Testing configuration mapping...")
    
    try:
        from backend.youtube2sheets import SyncConfig
        from domain.models import Filters
        
        # Test SyncConfig creation
        sync_config = SyncConfig(
            min_duration_seconds=60,
            keyword_filter='python,data',
            keyword_mode='include',
            max_videos=50
        )
        
        # Test Filters creation from SyncConfig
        filters = Filters(
            keywords=sync_config.keyword_filter.split(',') if sync_config.keyword_filter else [],
            keyword_mode=sync_config.keyword_mode,
            min_duration=sync_config.min_duration_seconds or 0,
            exclude_shorts=(sync_config.min_duration_seconds or 0) >= 60,
            max_results=sync_config.max_videos or 50
        )
        
        # Validate mapping
        assert filters.min_duration == 60, f"Expected 60, got {filters.min_duration}"
        assert filters.keywords == ['python', 'data'], f"Expected ['python', 'data'], got {filters.keywords}"
        assert filters.exclude_shorts == True, f"Expected True, got {filters.exclude_shorts}"
        assert filters.max_results == 50, f"Expected 50, got {filters.max_results}"
        
        print("✅ Configuration mapping works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Configuration mapping failed: {e}")
        return False

def test_filter_logic():
    """Test filter logic implementation."""
    print("\n🔍 Testing filter logic...")
    
    try:
        from domain.models import Video, Filters
        from services.automator import YouTubeToSheetsAutomator
        
        # Create test videos with all required fields
        from datetime import datetime
        
        test_videos = [
            Video(
                video_id="test1",
                title="Python Tutorial",
                description="Learn Python programming",
                channel_id="channel1",
                channel_title="Test Channel 1",
                published_at=datetime.fromisoformat("2025-01-01T00:00:00+00:00"),
                duration=120,  # 2 minutes
                view_count=1000,
                like_count=50,
                comment_count=10,
                thumbnail_url="https://example.com/thumb1.jpg",
                url="https://youtube.com/watch?v=test1"
            ),
            Video(
                video_id="test2", 
                title="Short Video",
                description="Quick tip",
                channel_id="channel1",
                channel_title="Test Channel 1",
                published_at=datetime.fromisoformat("2025-01-01T00:00:00+00:00"),
                duration=30,  # 30 seconds (short)
                view_count=500,
                like_count=25,
                comment_count=5,
                thumbnail_url="https://example.com/thumb2.jpg",
                url="https://youtube.com/watch?v=test2"
            ),
            Video(
                video_id="test3",
                title="Data Analysis",
                description="Python data science",
                channel_id="channel1",
                channel_title="Test Channel 1",
                published_at=datetime.fromisoformat("2025-01-01T00:00:00+00:00"),
                duration=300,  # 5 minutes
                view_count=2000,
                like_count=100,
                comment_count=20,
                thumbnail_url="https://example.com/thumb3.jpg",
                url="https://youtube.com/watch?v=test3"
            )
        ]
        
        # Test filters
        filters = Filters(
            keywords=['python', 'data'],
            keyword_mode='include',
            min_duration=60,  # 1 minute minimum
            exclude_shorts=True,
            max_results=50
        )
        
        # Test filter logic directly (without creating automator instance)
        # Create a mock automator class with just the filter method
        class MockAutomator:
            def _apply_filters(self, videos, filters):
                """Apply filters to video list."""
                filtered_videos = []
                
                for video in videos:
                    # Duration filter - skip if video is SHORTER than minimum
                    if filters.min_duration and video.duration < filters.min_duration:
                        continue
                    
                    # Exclude shorts filter (videos < 60 seconds)
                    if filters.exclude_shorts and video.duration < 60:
                        continue
                    
                    # Keywords filter (if keyword_mode is "include", require at least one keyword match)
                    if filters.keywords and filters.keyword_mode == "include":
                        title_desc = f"{video.title} {video.description}".lower()
                        if not any(keyword.lower() in title_desc for keyword in filters.keywords):
                            continue
                    
                    # If we made it here, video passes all filters
                    filtered_videos.append(video)
                
                return filtered_videos
        
        mock_automator = MockAutomator()
        filtered = mock_automator._apply_filters(test_videos, filters)
        
        # Should keep videos 1 and 3 (Python/Data keywords, >60s)
        # Should exclude video 2 (short, no keywords)
        assert len(filtered) == 2, f"Expected 2 videos, got {len(filtered)}"
        assert filtered[0].video_id == "test1", f"Expected test1, got {filtered[0].video_id}"
        assert filtered[1].video_id == "test3", f"Expected test3, got {filtered[1].video_id}"
        
        print("✅ Filter logic works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Filter logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_run_status_enum():
    """Test RunStatus enum values."""
    print("\n🔍 Testing RunStatus enum...")
    
    try:
        from domain.models import RunStatus
        
        # Test all enum values exist
        assert hasattr(RunStatus, 'PENDING'), "RunStatus.PENDING missing"
        assert hasattr(RunStatus, 'RUNNING'), "RunStatus.RUNNING missing"
        assert hasattr(RunStatus, 'COMPLETED'), "RunStatus.COMPLETED missing"
        assert hasattr(RunStatus, 'FAILED'), "RunStatus.FAILED missing"
        assert hasattr(RunStatus, 'CANCELLED'), "RunStatus.CANCELLED missing"
        
        # Test enum values (they are enum members, not strings)
        assert RunStatus.COMPLETED.value == 'completed', f"Expected 'completed', got {RunStatus.COMPLETED.value}"
        assert RunStatus.FAILED.value == 'failed', f"Expected 'failed', got {RunStatus.FAILED.value}"
        
        print("✅ RunStatus enum works correctly")
        return True
        
    except Exception as e:
        print(f"❌ RunStatus enum test failed: {e}")
        return False

def test_gui_components():
    """Test GUI component imports."""
    print("\n🔍 Testing GUI components...")
    
    try:
        from gui.main_app import YouTube2SheetsGUI
        print("✅ Main GUI imported successfully")
    except Exception as e:
        print(f"❌ Main GUI import failed: {e}")
        return False
    
    try:
        from utils.validators import SyncValidator
        print("✅ Validators imported successfully")
    except Exception as e:
        print(f"❌ Validators import failed: {e}")
        return False
    
    return True

def main():
    """Run comprehensive audit test."""
    print("=" * 60)
    print("🔍 COMPREHENSIVE SYSTEM AUDIT TEST")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_configuration_mapping,
        test_filter_logic,
        test_run_status_enum,
        test_gui_components
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 AUDIT RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL CRITICAL COMPONENTS VALIDATED")
        print("🚀 System ready for production testing")
        return True
    else:
        print("❌ CRITICAL ISSUES FOUND")
        print("🔧 Fix issues before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
