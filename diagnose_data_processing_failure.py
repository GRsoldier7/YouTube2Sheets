"""
Diagnose Data Processing Failure
Find why all 32 channels are failing with warnings
"""
import sys
import os
from pathlib import Path
import traceback

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def diagnose_channel_processing_failure():
    """Diagnose why all channels are failing."""
    print("🔍 DIAGNOSING CHANNEL PROCESSING FAILURE")
    print("=" * 60)
    
    try:
        from src.services.automator import YouTubeToSheetsAutomator
        from config_loader import load_config
        import re
        
        config = load_config()
        sheet_url = config.get('default_spreadsheet_url', '')
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheet_url)
        sheet_id = sheet_id_match.group(1)
        
        # Create automator
        automator = YouTubeToSheetsAutomator(config)
        
        # Test with a single channel first
        test_channel = "@TechTFQ"
        print(f"Testing single channel: {test_channel}")
        
        # Create a test sync config
        from src.domain.models import RunConfig, Filters, Destination
        
        run_config = RunConfig(
            channels=[test_channel],
            filters=Filters(
                keywords=[],
                keyword_mode="include",
                min_duration=0,
                exclude_shorts=False,
                max_results=5  # Small number for testing
            ),
            destination=Destination(
                spreadsheet_id=sheet_id,
                tab_name="Google_BigQuery"
            )
        )
        
        print("Running sync with detailed logging...")
        
        # Enable debug logging
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        # Run the sync
        result = automator.sync_channels_to_sheets(run_config)
        
        print(f"Sync result: {result}")
        print(f"Status: {result.status}")
        print(f"Videos processed: {result.videos_processed}")
        print(f"Videos written: {result.videos_written}")
        print(f"Errors: {result.errors}")
        
        return result
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
        traceback.print_exc()
        return None

def test_youtube_api_connection():
    """Test if YouTube API is working."""
    print("\n📺 TESTING YOUTUBE API CONNECTION")
    print("=" * 60)
    
    try:
        from src.services.youtube_service import YouTubeService, YouTubeConfig
        from config_loader import load_config
        
        config = load_config()
        youtube_config = YouTubeConfig(api_key=config['youtube_api_key'])
        youtube_service = YouTubeService(youtube_config)
        
        # Test with a known channel
        test_channel = "@TechTFQ"
        print(f"Testing YouTube API with channel: {test_channel}")
        
        # Try to get channel info
        channel_info = youtube_service.get_channel_info(test_channel)
        print(f"Channel info: {channel_info}")
        
        if channel_info:
            print("✅ YouTube API connection working")
            
            # Try to get videos
            videos = youtube_service.get_channel_videos(test_channel, max_results=3)
            print(f"Videos found: {len(videos) if videos else 0}")
            
            if videos:
                print("✅ YouTube API can fetch videos")
                for i, video in enumerate(videos[:2]):
                    print(f"  Video {i+1}: {video.title}")
            else:
                print("❌ YouTube API cannot fetch videos")
                return False
        else:
            print("❌ YouTube API connection failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ YouTube API test failed: {e}")
        traceback.print_exc()
        return False

def test_sheets_writing():
    """Test if Google Sheets writing is working."""
    print("\n📊 TESTING GOOGLE SHEETS WRITING")
    print("=" * 60)
    
    try:
        from src.services.sheets_service import SheetsService, SheetsConfig
        from config_loader import load_config
        import re
        
        config = load_config()
        sheet_url = config.get('default_spreadsheet_url', '')
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheet_url)
        sheet_id = sheet_id_match.group(1)
        
        sheets_config = SheetsConfig(
            service_account_file=config['google_sheets_service_account_json'],
            spreadsheet_id=sheet_id
        )
        sheets_service = SheetsService(sheets_config)
        
        # Test writing some data
        test_data = [
            ["Video ID", "Title", "Channel", "Published", "Views"],
            ["test123", "Test Video", "Test Channel", "2025-01-01", "1000"]
        ]
        
        print("Testing data writing to Google Sheets...")
        
        # Try to write to the Google_BigQuery tab
        success = sheets_service.write_data("Google_BigQuery", test_data)
        
        if success:
            print("✅ Google Sheets writing working")
            
            # Verify the data was written
            print("Verifying data was written...")
            data = sheets_service.read_data("Google_BigQuery", "A1:E2")
            print(f"Data read back: {data}")
            
            if data and len(data) > 0:
                print("✅ Data verification successful")
                return True
            else:
                print("❌ Data verification failed")
                return False
        else:
            print("❌ Google Sheets writing failed")
            return False
        
    except Exception as e:
        print(f"❌ Sheets writing test failed: {e}")
        traceback.print_exc()
        return False

def test_complete_workflow():
    """Test the complete workflow step by step."""
    print("\n🔄 TESTING COMPLETE WORKFLOW")
    print("=" * 60)
    
    try:
        from src.services.automator import YouTubeToSheetsAutomator
        from config_loader import load_config
        import re
        
        config = load_config()
        sheet_url = config.get('default_spreadsheet_url', '')
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheet_url)
        sheet_id = sheet_id_match.group(1)
        
        # Create automator
        automator = YouTubeToSheetsAutomator(config)
        
        # Test with a single channel and very small dataset
        test_channel = "@TechTFQ"
        print(f"Testing complete workflow with: {test_channel}")
        
        # Create a minimal sync config
        from src.domain.models import RunConfig, Filters, Destination
        
        run_config = RunConfig(
            channels=[test_channel],
            filters=Filters(
                keywords=[],
                keyword_mode="include",
                min_duration=0,
                exclude_shorts=False,
                max_results=1  # Just 1 video for testing
            ),
            destination=Destination(
                spreadsheet_id=sheet_id,
                tab_name="Google_BigQuery"
            )
        )
        
        print("Step 1: Running sync...")
        result = automator.sync_channels_to_sheets(run_config)
        
        print(f"Step 2: Sync completed")
        print(f"  Status: {result.status}")
        print(f"  Videos processed: {result.videos_processed}")
        print(f"  Videos written: {result.videos_written}")
        print(f"  Errors: {len(result.errors)}")
        
        if result.errors:
            print("Step 3: Error details:")
            for i, error in enumerate(result.errors[:5]):  # Show first 5 errors
                print(f"  Error {i+1}: {error}")
        
        # Check if data was actually written
        print("Step 4: Checking if data was written...")
        from src.services.sheets_service import SheetsService, SheetsConfig
        
        sheets_config = SheetsConfig(
            service_account_file=config['google_sheets_service_account_json'],
            spreadsheet_id=sheet_id
        )
        sheets_service = SheetsService(sheets_config)
        
        # Read data from the sheet
        data = sheets_service.read_data("Google_BigQuery", "A1:Z10")
        print(f"Data in sheet: {len(data) if data else 0} rows")
        
        if data and len(data) > 1:  # More than just headers
            print("✅ Data was written to sheet")
            print(f"Sample data: {data[0] if data else 'None'}")
            return True
        else:
            print("❌ No data was written to sheet")
            return False
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Diagnose the complete data processing failure."""
    print("🚀 DIAGNOSING DATA PROCESSING FAILURE")
    print("=" * 70)
    print("Finding why all 32 channels are failing with warnings")
    print("=" * 70)
    
    tests = [
        ("YouTube API Connection", test_youtube_api_connection),
        ("Google Sheets Writing", test_sheets_writing),
        ("Complete Workflow", test_complete_workflow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
            print(f"✅ PASS: {test_name}")
        else:
            print(f"❌ FAIL: {test_name}")
    
    print("\n" + "=" * 70)
    print("DIAGNOSIS RESULTS")
    print("=" * 70)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✅ All components working - issue may be in integration")
    else:
        print(f"\n❌ Found {total - passed} broken components")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

