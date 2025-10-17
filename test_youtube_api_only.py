#!/usr/bin/env python3
"""
YouTube API Only Test
Tests YouTube API functionality without Google Sheets integration
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.automator import YouTubeToSheetsAutomator
from domain.models import RunConfig, Destination, Filters

def test_youtube_api_only():
    """Test YouTube API functionality without Google Sheets."""
    print("[YOUTUBE API TEST] Testing YouTube API functionality...")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get configuration
    config = {
        'youtube_api_key': os.getenv('YOUTUBE_API_KEY'),
        'google_sheets_service_account_json': os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON'),
        'default_spreadsheet_url': os.getenv('DEFAULT_SPREADSHEET_URL')
    }
    
    if not config['youtube_api_key']:
        print("[FAIL] YouTube API key not found")
        return False
    
    # Initialize automator (without sheets service)
    print("[INIT] Initializing automator...")
    automator = YouTubeToSheetsAutomator(config)
    
    # Test with 2 channels
    test_channels = ["@TechTFQ", "@DataWithBaraa"]
    
    print(f"[CONFIG] Testing with channels: {test_channels}")
    
    # Test YouTube service directly
    print("[YOUTUBE] Testing YouTube service...")
    
    for channel in test_channels:
        print(f"[FETCH] Fetching videos from {channel}...")
        start_time = time.time()
        
        try:
            # Get videos directly from YouTube service
            videos = automator.youtube_service.get_channel_videos(channel, 10)  # Limit to 10 for test
            duration = time.time() - start_time
            
            print(f"[SUCCESS] {channel}: {len(videos)} videos in {duration:.2f}s")
            
            if videos:
                # Show first video details
                first_video = videos[0]
                print(f"[SAMPLE] First video: {first_video.title}")
                print(f"[SAMPLE] Duration: {first_video.duration}")
                print(f"[SAMPLE] Views: {first_video.view_count}")
                print(f"[SAMPLE] Published: {first_video.published_at}")
            
        except Exception as e:
            print(f"[ERROR] {channel}: {e}")
            return False
    
    print("\n[YOUTUBE API TEST] All tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_youtube_api_only()
    sys.exit(0 if success else 1)
