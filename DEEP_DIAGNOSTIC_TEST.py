"""
DEEP DIAGNOSTIC TEST
====================
This will trace EXACTLY what's happening when the tool runs.
We'll capture every step, every API call, every error.

Author: @TheDiagnostician
Date: October 11, 2025
"""

import sys
import os
from pathlib import Path
import traceback
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_imports():
    """Test if all imports work."""
    print_section("STEP 1: TESTING IMPORTS")
    
    results = {}
    
    # Test domain models
    try:
        from src.domain.models import Video, Filters, Destination, RunConfig, RunResult, RunStatus
        print("✅ Domain models imported successfully")
        results['domain_models'] = True
    except Exception as e:
        print(f"❌ Domain models import failed: {e}")
        traceback.print_exc()
        results['domain_models'] = False
    
    # Test services
    try:
        from src.services.automator import YouTubeToSheetsAutomator
        print("✅ Automator imported successfully")
        results['automator'] = True
    except Exception as e:
        print(f"❌ Automator import failed: {e}")
        traceback.print_exc()
        results['automator'] = False
    
    # Test YouTube service
    try:
        from src.services.youtube_service import YouTubeService, YouTubeConfig
        print("✅ YouTube service imported successfully")
        results['youtube_service'] = True
    except Exception as e:
        print(f"❌ YouTube service import failed: {e}")
        traceback.print_exc()
        results['youtube_service'] = False
    
    # Test Sheets service
    try:
        from src.services.sheets_service import SheetsService, SheetsConfig
        print("✅ Sheets service imported successfully")
        results['sheets_service'] = True
    except Exception as e:
        print(f"❌ Sheets service import failed: {e}")
        traceback.print_exc()
        results['sheets_service'] = False
    
    # Test backend SyncConfig
    try:
        from src.backend.youtube2sheets import SyncConfig
        print("✅ Backend SyncConfig imported successfully")
        results['sync_config'] = True
    except Exception as e:
        print(f"❌ Backend SyncConfig import failed: {e}")
        traceback.print_exc()
        results['sync_config'] = False
    
    return all(results.values())

def test_configuration():
    """Test configuration and credentials."""
    print_section("STEP 2: TESTING CONFIGURATION")
    
    # Check environment variables
    print("Checking environment variables...")
    
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    if youtube_key:
        print(f"✅ YOUTUBE_API_KEY found (length: {len(youtube_key)})")
        print(f"   Starts with: {youtube_key[:10]}..." if len(youtube_key) > 10 else f"   Value: {youtube_key}")
    else:
        print("❌ YOUTUBE_API_KEY not found in environment")
    
    sheets_creds = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON')
    if sheets_creds:
        print(f"✅ GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON found")
        print(f"   Path: {sheets_creds}")
        if os.path.exists(sheets_creds):
            print(f"   File exists: ✅")
        else:
            print(f"   File exists: ❌ NOT FOUND")
    else:
        print("❌ GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON not found in environment")
    
    return youtube_key is not None and sheets_creds is not None

def test_youtube_service_directly():
    """Test YouTube service with actual API call."""
    print_section("STEP 3: TESTING YOUTUBE SERVICE DIRECTLY")
    
    try:
        from src.services.youtube_service import YouTubeService, YouTubeConfig
        
        youtube_key = os.getenv('YOUTUBE_API_KEY')
        if not youtube_key:
            print("❌ Cannot test - no API key")
            return False
        
        # Initialize service
        print("Initializing YouTube service...")
        config = YouTubeConfig(api_key=youtube_key)
        service = YouTubeService(config)
        print("✅ YouTube service initialized")
        
        # Test with a single channel
        test_channel = "@TechTFQ"
        print(f"\nTesting with channel: {test_channel}")
        
        # Test channel resolution
        print(f"\n--- Testing channel resolution ---")
        if test_channel.startswith('@'):
            handle = test_channel[1:]
            print(f"Resolving handle: {handle}")
            
            try:
                channel_id = service.resolve_channel_id(handle)
                print(f"Resolved channel ID: {channel_id}")
                
                if not channel_id:
                    print("❌ Channel resolution returned None")
                    return False
                else:
                    print("✅ Channel resolution succeeded")
            except Exception as e:
                print(f"❌ Channel resolution failed: {e}")
                traceback.print_exc()
                return False
        
        # Test video retrieval
        print(f"\n--- Testing video retrieval ---")
        print(f"Calling get_channel_videos('{test_channel}', max_results=5)")
        
        try:
            videos = service.get_channel_videos(test_channel, max_results=5)
            print(f"\nRetrieved {len(videos)} videos")
            
            if len(videos) > 0:
                print("\n✅ VIDEO RETRIEVAL SUCCESSFUL!")
                print("\nFirst video details:")
                video = videos[0]
                print(f"  - ID: {video.video_id}")
                print(f"  - Title: {video.title}")
                print(f"  - Duration: {video.duration} seconds")
                print(f"  - Views: {video.view_count}")
                print(f"  - Likes: {video.like_count}")
                print(f"  - Comments: {video.comment_count}")
                print(f"  - Published: {video.published_at}")
                
                # Check if stats are real (not zeros)
                if video.duration == 0 and video.view_count == 0:
                    print("\n⚠️ WARNING: Video stats are all zeros - details not being fetched!")
                    return False
                else:
                    print("\n✅ Video has REAL stats!")
                    return True
            else:
                print("❌ NO VIDEOS RETRIEVED")
                return False
                
        except Exception as e:
            print(f"❌ Video retrieval failed: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ YouTube service test failed: {e}")
        traceback.print_exc()
        return False

def test_automator_flow():
    """Test the complete automator flow."""
    print_section("STEP 4: TESTING AUTOMATOR FLOW")
    
    try:
        from src.services.automator import YouTubeToSheetsAutomator
        from src.backend.youtube2sheets import SyncConfig
        
        # Get credentials
        youtube_key = os.getenv('YOUTUBE_API_KEY')
        sheets_creds = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON')
        sheets_url = os.getenv('DEFAULT_SPREADSHEET_URL', '')
        
        if not youtube_key or not sheets_creds:
            print("❌ Missing credentials")
            return False
        
        # Initialize automator
        print("Initializing automator...")
        automator = YouTubeToSheetsAutomator({
            'youtube_api_key': youtube_key,
            'google_sheets_service_account_json': sheets_creds,
            'default_spreadsheet_url': sheets_url
        })
        print("✅ Automator initialized")
        
        # Create SyncConfig
        print("\nCreating SyncConfig...")
        config = SyncConfig(
            min_duration_seconds=60,
            max_duration_seconds=None,
            keyword_filter=None,
            keyword_mode="include",
            max_videos=5  # Just 5 for testing
        )
        print("✅ SyncConfig created")
        print(f"   - min_duration_seconds: {config.min_duration_seconds}")
        print(f"   - max_videos: {config.max_videos}")
        
        # Test with single channel
        test_channel = "@TechTFQ"
        test_tab = "DIAGNOSTIC_TEST"
        
        print(f"\nCalling sync_channel_to_sheet...")
        print(f"   - Channel: {test_channel}")
        print(f"   - Tab: {test_tab}")
        print(f"   - URL: {sheets_url}")
        
        try:
            result = automator.sync_channel_to_sheet(
                channel_input=test_channel,
                spreadsheet_url=sheets_url,
                tab_name=test_tab,
                config=config
            )
            
            print(f"\nResult: {result}")
            
            if result:
                print("✅ sync_channel_to_sheet returned True")
                print(f"\nAutomator state:")
                print(f"   - Videos processed: {automator.videos_processed}")
                print(f"   - Videos written: {automator.videos_written}")
                print(f"   - Errors: {automator.errors}")
                
                if automator.videos_processed > 0:
                    print("\n✅ VIDEOS WERE PROCESSED!")
                else:
                    print("\n❌ NO VIDEOS PROCESSED")
                
                return automator.videos_processed > 0
            else:
                print("❌ sync_channel_to_sheet returned False")
                print(f"\nAutomator state:")
                print(f"   - Errors: {automator.errors}")
                return False
                
        except Exception as e:
            print(f"❌ sync_channel_to_sheet failed: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Automator flow test failed: {e}")
        traceback.print_exc()
        return False

def test_api_call_trace():
    """Trace actual API calls being made."""
    print_section("STEP 5: TRACING API CALLS")
    
    try:
        from src.services.youtube_service import YouTubeService, YouTubeConfig
        
        youtube_key = os.getenv('YOUTUBE_API_KEY')
        if not youtube_key:
            print("❌ Cannot test - no API key")
            return False
        
        # Monkey-patch _make_request to see what's being called
        config = YouTubeConfig(api_key=youtube_key)
        service = YouTubeService(config)
        
        original_make_request = service._make_request
        api_calls = []
        
        def traced_make_request(endpoint, params):
            api_calls.append({
                'endpoint': endpoint,
                'params': params
            })
            print(f"\n📡 API Call: {endpoint}")
            print(f"   Params: {json.dumps(params, indent=2)}")
            
            result = original_make_request(endpoint, params)
            
            print(f"   Response items: {len(result.get('items', []))}")
            return result
        
        service._make_request = traced_make_request
        
        # Make a test call
        print("Making test call to get_channel_videos...")
        videos = service.get_channel_videos("@TechTFQ", max_results=2)
        
        print(f"\n{'='*80}")
        print(f"TOTAL API CALLS MADE: {len(api_calls)}")
        print(f"TOTAL VIDEOS RETRIEVED: {len(videos)}")
        print(f"{'='*80}")
        
        return len(videos) > 0
        
    except Exception as e:
        print(f"❌ API trace failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run deep diagnostic tests."""
    print(f"\n{'#'*80}")
    print("#  DEEP DIAGNOSTIC TEST - YOUTUBE2SHEETS")
    print("#  Tracing every step to find the root cause")
    print(f"#  {'='*76}")
    print(f"{'#'*80}\n")
    
    results = {}
    
    # Run all tests
    results['imports'] = test_imports()
    results['configuration'] = test_configuration()
    results['youtube_service'] = test_youtube_service_directly()
    results['automator_flow'] = test_automator_flow()
    results['api_trace'] = test_api_call_trace()
    
    # Summary
    print_section("DIAGNOSTIC SUMMARY")
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    overall = all(results.values())
    
    print(f"\n{'='*80}")
    if overall:
        print("🎉 ALL TESTS PASSED - System should be working!")
    else:
        print("🚨 TESTS FAILED - Issues identified above")
        print("\nFailed tests:")
        for test_name, passed in results.items():
            if not passed:
                print(f"  ❌ {test_name}")
    print(f"{'='*80}\n")
    
    return 0 if overall else 1

if __name__ == "__main__":
    sys.exit(main())

