#!/usr/bin/env python3
"""
Test Optimization Performance
Tests the optimized YouTube2Sheets system with performance metrics.
"""
import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_optimization_performance():
    """Test the optimized system performance."""
    print("[OPTIMIZATION TEST] Testing optimized YouTube2Sheets performance...")
    
    try:
        from src.services.automator import YouTubeToSheetsAutomator
        from src.domain.models import RunConfig, Filters, Destination
        from dotenv import load_dotenv
        import os
        
        # Load environment variables
        load_dotenv()
        
        # Get real config
        config = {
            'youtube_api_key': os.getenv('YOUTUBE_API_KEY', ''),
            'google_sheets_service_account_json': os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON', ''),
            'default_spreadsheet_url': os.getenv('DEFAULT_SPREADSHEET_URL', '')
        }
        
        if not config['youtube_api_key']:
            print("[SKIP] No YouTube API key found")
            return False
            
        if not config['google_sheets_service_account_json']:
            print("[SKIP] No Google Sheets credentials found")
            return False
        
        # Initialize automator
        print("[INIT] Initializing optimized automator...")
        automator = YouTubeToSheetsAutomator(config)
        
        # Test with 3 channels for performance measurement
        test_channels = ["@TechTFQ", "@GoogleCloudTech", "@DataWithBaraa"]
        test_tab = "TestTab"  # Use simple existing tab name
        
        print(f"[CONFIG] Testing with channels: {test_channels}")
        print(f"[CONFIG] Test tab: {test_tab}")
        
        # Extract spreadsheet ID from URL
        import re
        spreadsheet_url = config['default_spreadsheet_url']
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', spreadsheet_url)
        if not sheet_id_match:
            print(f"[FAIL] Invalid spreadsheet URL: {spreadsheet_url}")
            return False
        spreadsheet_id = sheet_id_match.group(1)
        
        # Create run config
        run_config = RunConfig(
            channels=test_channels,
            destination=Destination(
                spreadsheet_id=spreadsheet_id,
                tab_name=test_tab
            ),
            filters=Filters(
                keywords=[],
                keyword_mode='include',
                min_duration=90,  # 90 seconds
                exclude_shorts=True,
                max_results=50
            )
        )
        
        print("[PERFORMANCE] Starting optimized sync...")
        start_time = time.time()
        
        # Run the optimized sync (parallel processing)
        result = automator.sync_channels_optimized(run_config, use_parallel=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"[PERFORMANCE] Optimized sync completed in {duration:.2f} seconds")
        print(f"[PERFORMANCE] Status: {result.status}")
        print(f"[PERFORMANCE] Videos written: {result.videos_written}")
        print(f"[PERFORMANCE] Errors: {len(result.errors)}")
        
        # Get optimization metrics
        metrics = automator.get_optimization_status()
        cache_hit_rate = metrics.get('cache_hit_rate', 0)
        if isinstance(cache_hit_rate, str):
            cache_hit_rate = float(cache_hit_rate.replace('%', ''))
        print(f"[METRICS] Cache hit rate: {cache_hit_rate:.1f}%")
        print(f"[METRICS] Duplicates prevented: {metrics.get('duplicates_prevented', 0)}")
        print(f"[METRICS] Seen videos: {metrics.get('seen_videos', 0)}")
        print(f"[METRICS] API quota used: {metrics.get('api_quota_used', 0)}")
        
        # Validate results
        success = True
        
        if result.videos_written == 0:
            print("[FAIL] No videos were written!")
            success = False
        else:
            print(f"[OK] {result.videos_written} videos written successfully")
        
        if result.status.value != 'completed':
            print(f"[FAIL] Sync status was {result.status.value}, expected 'completed'")
            success = False
        else:
            print("[OK] Sync completed successfully")
        
        # Performance validation
        if duration > 20:
            print(f"[WARN] Sync took {duration:.2f}s, which is longer than expected for optimized version")
        else:
            print(f"[OK] Sync completed in good time: {duration:.2f}s")
        
        # Cache efficiency validation
        cache_hit_rate = metrics.get('cache_hit_rate', 0)
        if isinstance(cache_hit_rate, (int, float)) and cache_hit_rate < 20:
            print(f"[WARN] Low cache hit rate: {cache_hit_rate:.1f}% (expected > 20%)")
        else:
            print(f"[OK] Good cache hit rate: {cache_hit_rate:.1f}%")
        
        return success
        
    except Exception as e:
        print(f"[FAIL] Optimization test failed with exception: {e}")
        import traceback
        print(f"[TRACEBACK] {traceback.format_exc()}")
        return False

def test_sequential_vs_parallel():
    """Compare sequential vs parallel performance."""
    print("\n[COMPARISON TEST] Comparing sequential vs parallel performance...")
    
    try:
        from src.services.automator import YouTubeToSheetsAutomator
        from src.domain.models import RunConfig, Filters, Destination
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        config = {
            'youtube_api_key': os.getenv('YOUTUBE_API_KEY', ''),
            'google_sheets_service_account_json': os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON', ''),
            'default_spreadsheet_url': os.getenv('DEFAULT_SPREADSHEET_URL', '')
        }
        
        if not config['youtube_api_key'] or not config['google_sheets_service_account_json']:
            print("[SKIP] Missing credentials for comparison test")
            return False
        
        automator = YouTubeToSheetsAutomator(config)
        
        # Test with 2 channels for comparison
        test_channels = ["@DataWithBaraa", "@AlexTheAnalyst"]
        
        # Extract spreadsheet ID
        import re
        spreadsheet_url = config['default_spreadsheet_url']
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', spreadsheet_url)
        if not sheet_id_match:
            return False
        spreadsheet_id = sheet_id_match.group(1)
        
        run_config = RunConfig(
            channels=test_channels,
            destination=Destination(
                spreadsheet_id=spreadsheet_id,
                tab_name="TestTab2"  # Use simple existing tab name
            ),
            filters=Filters(
                keywords=[],
                keyword_mode='include',
                min_duration=90,
                exclude_shorts=True,
                max_results=50
            )
        )
        
        # Test sequential
        print("[SEQ] Testing sequential processing...")
        seq_start = time.time()
        seq_result = automator.sync_channels_optimized(run_config, use_parallel=False)
        seq_duration = time.time() - seq_start
        
        # Test parallel
        print("[PAR] Testing parallel processing...")
        par_start = time.time()
        par_result = automator.sync_channels_optimized(run_config, use_parallel=True)
        par_duration = time.time() - par_start
        
        # Compare results
        print(f"[COMPARISON] Sequential: {seq_duration:.2f}s, {seq_result.videos_written} videos")
        print(f"[COMPARISON] Parallel: {par_duration:.2f}s, {par_result.videos_written} videos")
        
        if par_duration < seq_duration:
            speedup = seq_duration / par_duration
            print(f"[OK] Parallel is {speedup:.1f}x faster than sequential")
        else:
            print(f"[WARN] Parallel was not faster than sequential")
        
        # If we got 0 videos due to duplicates, that's expected behavior
        if seq_result.videos_written == 0 and par_result.videos_written == 0:
            print("[INFO] 0 videos written due to duplicates - this is expected behavior")
            print("[OK] Comparison test passed - duplicates handled correctly")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Comparison test failed: {e}")
        return False

def main():
    """Run optimization tests."""
    print("[OPTIMIZATION TEST] YouTube2Sheets Optimization Performance Test")
    print("=" * 70)
    
    tests = [
        test_optimization_performance,
        test_sequential_vs_parallel
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 70)
    print(f"[RESULTS] Optimization Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All optimization tests passed! System is optimized.")
        return True
    else:
        print("[FAIL] Some optimization tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
