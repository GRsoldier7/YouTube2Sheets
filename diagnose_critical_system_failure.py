"""
Diagnose Critical System Failure
Diagnose why all channels are failing with warnings
"""
import sys
import os
from pathlib import Path
import traceback

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def diagnose_critical_failure():
    """Diagnose why all channels are failing."""
    print("🔍 DIAGNOSING CRITICAL SYSTEM FAILURE")
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
        
        # Test with a single channel to see the actual error
        test_channel = "@TechTFQ"
        print(f"Testing single channel: {test_channel}")
        
        # Create a minimal sync config
        from src.domain.models import RunConfig, Filters, Destination
        
        run_config = RunConfig(
            channels=[test_channel],
            filters=Filters(
                keywords=[],
                keyword_mode="include",
                min_duration=0,
                exclude_shorts=False,
                max_results=3
            ),
            destination=Destination(
                spreadsheet_id=sheet_id,
                tab_name="Google_BigQuery"
            )
        )
        
        print("Running sync with detailed error logging...")
        result = automator.sync_channels_to_sheets(run_config)
        
        print(f"Sync completed")
        print(f"  Status: {result.status}")
        print(f"  Videos processed: {result.videos_processed}")
        print(f"  Videos written: {result.videos_written}")
        print(f"  Errors: {len(result.errors)}")
        
        if result.errors:
            print("Error details:")
            for i, error in enumerate(result.errors):
                print(f"  Error {i+1}: {error}")
        
        # Check if data was actually written
        print("Checking if data was written...")
        from src.services.sheets_service import SheetsService, SheetsConfig
        
        sheets_config = SheetsConfig(
            service_account_file=config['google_sheets_service_account_json'],
            spreadsheet_id=sheet_id
        )
        sheets_service = SheetsService(sheets_config)
        
        # Read data from the sheet
        data = sheets_service.read_data("Google_BigQuery", "A1:Z10")
        print(f"Data in sheet: {len(data) if data else 0} rows")
        
        if data:
            print("Sample data:")
            for i, row in enumerate(data[:5]):
                print(f"  Row {i+1}: {row}")
        
        return result
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
        traceback.print_exc()
        return None

def test_youtube_service_directly():
    """Test YouTube service directly to see if it's working."""
    print("\n🧪 TESTING YOUTUBE SERVICE DIRECTLY")
    print("=" * 60)
    
    try:
        from src.services.youtube_service import YouTubeService, YouTubeConfig
        from config_loader import load_config
        
        config = load_config()
        youtube_config = YouTubeConfig(api_key=config['youtube_api_key'])
        youtube_service = YouTubeService(youtube_config)
        
        # Test channel resolution
        print("Testing channel resolution...")
        channel_id = youtube_service.resolve_channel_id("@TechTFQ")
        print(f"Channel ID: {channel_id}")
        
        if channel_id:
            # Test getting channel info
            print("Testing channel info...")
            channel_info = youtube_service.get_channel_info(channel_id)
            print(f"Channel info: {channel_info}")
            
            # Test getting videos
            print("Testing video retrieval...")
            videos = youtube_service.get_channel_videos(channel_id, 3)
            print(f"Videos retrieved: {len(videos)}")
            
            if videos:
                print("Sample video:")
                video = videos[0]
                print(f"  ID: {video.video_id}")
                print(f"  Title: {video.title}")
                print(f"  Channel: {video.channel_title}")
                print(f"  Published: {video.published_at}")
                print(f"  Views: {video.view_count}")
                print(f"  Likes: {video.like_count}")
                print(f"  Comments: {video.comment_count}")
                return True
            else:
                print("❌ No videos retrieved")
                return False
        else:
            print("❌ Channel resolution failed")
            return False
        
    except Exception as e:
        print(f"❌ YouTube service test failed: {e}")
        traceback.print_exc()
        return False

def test_sheets_service_directly():
    """Test Sheets service directly to see if it's working."""
    print("\n🧪 TESTING SHEETS SERVICE DIRECTLY")
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
        
        # Test writing data
        print("Testing data writing...")
        test_data = [
            ["Video ID", "Title", "Channel", "Published", "Views", "Likes", "Comments"],
            ["test123", "Test Video", "Test Channel", "2025-01-01", "1000", "50", "10"]
        ]
        
        success = sheets_service.write_data("Google_BigQuery", test_data)
        print(f"Write success: {success}")
        
        if success:
            # Test reading data
            print("Testing data reading...")
            data = sheets_service.read_data("Google_BigQuery", "A1:Z10")
            print(f"Data read: {len(data) if data else 0} rows")
            
            if data:
                print("Sample data:")
                for i, row in enumerate(data[:3]):
                    print(f"  Row {i+1}: {row}")
                return True
            else:
                print("❌ No data read")
                return False
        else:
            print("❌ Data write failed")
            return False
        
    except Exception as e:
        print(f"❌ Sheets service test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Diagnose the critical system failure."""
    print("🚨 DIAGNOSING CRITICAL SYSTEM FAILURE")
    print("=" * 70)
    print("All 32 channels are failing with warnings - investigating root cause")
    print("=" * 70)
    
    # Test individual components
    tests = [
        ("YouTube Service", test_youtube_service_directly),
        ("Sheets Service", test_sheets_service_directly),
        ("Complete System", diagnose_critical_failure)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                print(f"✅ PASS: {test_name}")
            else:
                print(f"❌ FAIL: {test_name}")
        except Exception as e:
            print(f"❌ ERROR: {test_name} - {e}")
            results[test_name] = False
    
    print("\n" + "=" * 70)
    print("DIAGNOSIS RESULTS")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    # Analyze results
    if results.get("YouTube Service") and results.get("Sheets Service"):
        print("\n🔍 ANALYSIS:")
        print("✅ YouTube Service is working")
        print("✅ Sheets Service is working")
        print("❌ Complete System is failing")
        print("\n💡 CONCLUSION: The issue is in the automator integration")
        print("The individual services work, but the automator is not properly")
        print("processing the data or handling the workflow correctly.")
    elif not results.get("YouTube Service"):
        print("\n🔍 ANALYSIS:")
        print("❌ YouTube Service is failing")
        print("💡 CONCLUSION: The issue is in YouTube API integration")
    elif not results.get("Sheets Service"):
        print("\n🔍 ANALYSIS:")
        print("❌ Sheets Service is failing")
        print("💡 CONCLUSION: The issue is in Google Sheets integration")
    else:
        print("\n🔍 ANALYSIS:")
        print("❌ Multiple components are failing")
        print("💡 CONCLUSION: There are multiple issues to fix")
    
    return results

if __name__ == "__main__":
    results = main()
    sys.exit(0)
