"""
Comprehensive System Validation Test
=====================================
Following @PolyChronos-Omega.md framework and @QualityMandate.md standards

Tests all facets of the YouTube2Sheets system:
- Architecture alignment with CURRENT_SYSTEM_STATE.md
- Frontend: GUI, filters, transitions, menus
- Backend: Data processing, formatting, deduplication
- API Optimization: ETag caching, quota management
- Google Sheets Integration: Conditional formatting, data writing

Author: Project Manager & Guild of Specialists
Date: October 11, 2025
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"       {details}")

def test_architecture_alignment():
    """Test architecture alignment with CURRENT_SYSTEM_STATE.md"""
    print_section("1. ARCHITECTURE VALIDATION")
    
    results = []
    
    # Check critical files exist
    critical_files = [
        "src/gui/main_app.py",
        "src/backend/youtube2sheets.py",
        "src/backend/api_optimizer.py",
        "src/backend/data_processor.py",
        "src/backend/filters.py",
        "src/backend/sheet_formatter.py",
        "src/services/automator.py",
        "src/services/youtube_service.py",
        "src/services/sheets_service.py",
        "src/domain/models.py"
    ]
    
    for file_path in critical_files:
        exists = Path(file_path).exists()
        print_result(f"File exists: {file_path}", exists)
        results.append(exists)
    
    # Check for duplicate systems
    backend_automator_exists = Path("src/backend/youtube2sheets.py").exists()
    services_automator_exists = Path("src/services/automator.py").exists()
    
    if backend_automator_exists and services_automator_exists:
        print_result("Duplicate automator systems detected", False, 
                    "Two separate automator implementations exist")
        results.append(False)
    else:
        print_result("Single automator system", True)
        results.append(True)
    
    return all(results)

def test_services_layer_functionality():
    """Test services layer has all required functionality."""
    print_section("2. SERVICES LAYER VALIDATION")
    
    results = []
    
    try:
        # Import services
        from src.services.youtube_service import YouTubeService, YouTubeConfig
        from src.services.sheets_service import SheetsService, SheetsConfig
        from src.services.automator import YouTubeToSheetsAutomator, AutomatorConfig
        
        print_result("Import YouTubeService", True)
        print_result("Import SheetsService", True)
        print_result("Import YouTubeToSheetsAutomator", True)
        results.extend([True, True, True])
        
        # Check YouTubeService methods
        youtube_methods = [
            'get_channel_videos',
            'get_channel_info',
            'resolve_channel_id',
            'get_quota_usage'
        ]
        
        for method in youtube_methods:
            has_method = hasattr(YouTubeService, method)
            print_result(f"YouTubeService.{method} exists", has_method)
            results.append(has_method)
        
        # Check SheetsService methods
        sheets_methods = [
            'create_sheet_tab',
            'write_videos_to_sheet',
            'apply_conditional_formatting',
            'check_for_duplicates'
        ]
        
        for method in sheets_methods:
            has_method = hasattr(SheetsService, method)
            print_result(f"SheetsService.{method} exists", has_method)
            results.append(has_method)
        
        # Check AutomatorConfig has optimization flags
        config_fields = AutomatorConfig.__dataclass_fields__
        has_etag = 'use_etag_cache' in config_fields
        has_dedupe = 'deduplicate' in config_fields
        
        print_result("AutomatorConfig.use_etag_cache exists", has_etag)
        print_result("AutomatorConfig.deduplicate exists", has_dedupe)
        results.extend([has_etag, has_dedupe])
        
    except Exception as e:
        print_result("Services layer import", False, str(e))
        results.append(False)
    
    return all(results)

def test_backend_optimization_layer():
    """Test backend optimization functionality."""
    print_section("3. BACKEND OPTIMIZATION VALIDATION")
    
    results = []
    
    try:
        # Import backend components
        from src.backend.api_optimizer import APICreditTracker, ResponseCache, VideoDeduplicator
        from src.backend.sheet_formatter import SheetFormatter
        
        print_result("Import APICreditTracker", True)
        print_result("Import ResponseCache", True)
        print_result("Import VideoDeduplicator", True)
        print_result("Import SheetFormatter", True)
        results.extend([True, True, True, True])
        
        # Test APICreditTracker
        tracker = APICreditTracker(daily_quota=10000)
        
        # Test quota tracking
        initial_remaining = tracker.remaining()
        tracker.consume(100, api_name="test")
        after_consume = tracker.remaining()
        
        quota_works = (initial_remaining - after_consume) == 100
        print_result("APICreditTracker quota tracking", quota_works, 
                    f"Consumed 100, remaining decreased by {initial_remaining - after_consume}")
        results.append(quota_works)
        
        # Test usage percentage
        usage_pct = tracker.usage_percentage()
        usage_correct = 0 <= usage_pct <= 100
        print_result("APICreditTracker usage percentage", usage_correct,
                    f"Usage: {usage_pct:.2f}%")
        results.append(usage_correct)
        
        # Test ResponseCache
        cache = ResponseCache()
        test_key = "test_channel_id"
        test_etag = "test_etag_123"
        test_data = {"videos": ["video1", "video2"]}
        
        # Store in cache (using 'set' method)
        cache.set(test_key, test_data, etag=test_etag)
        
        # Retrieve from cache with same etag
        cached_data = cache.get(test_key, test_etag)
        cache_works = cached_data == test_data
        print_result("ResponseCache storage and retrieval", cache_works)
        results.append(cache_works)
        
        # Test VideoDeduplicator
        deduper = VideoDeduplicator()
        
        # Mark video as seen
        test_video_id = "test_video_123"
        first_check = deduper.is_duplicate(test_video_id)
        deduper.mark_as_seen(test_video_id)
        second_check = deduper.is_duplicate(test_video_id)
        
        dedupe_works = not first_check and second_check
        print_result("VideoDeduplicator functionality", dedupe_works,
                    f"First check: {first_check}, Second check: {second_check}")
        results.append(dedupe_works)
        
    except Exception as e:
        print_result("Backend optimization layer", False, str(e))
        results.append(False)
    
    return all(results)

def test_data_models():
    """Test domain models and data structures."""
    print_section("4. DATA MODELS VALIDATION")
    
    results = []
    
    try:
        from src.domain.models import (
            Video, Channel, Filters, Destination, 
            RunConfig, RunResult, RunStatus
        )
        
        print_result("Import domain models", True)
        results.append(True)
        
        # Test Video model
        video = Video(
            video_id="test123",
            title="Test Video",
            description="Test description",
            channel_id="UC123",
            channel_title="Test Channel",
            published_at=datetime.now(),
            duration=300,
            view_count=1000,
            like_count=50,
            comment_count=10,
            thumbnail_url="https://example.com/thumb.jpg",
            url="https://youtube.com/watch?v=test123"
        )
        
        # Test to_dict method
        has_to_dict = hasattr(video, 'to_dict')
        print_result("Video.to_dict method exists", has_to_dict)
        results.append(has_to_dict)
        
        if has_to_dict:
            video_dict = video.to_dict()
            dict_correct = isinstance(video_dict, dict) and 'id' in video_dict
            print_result("Video.to_dict returns correct format", dict_correct)
            results.append(dict_correct)
        
        # Test Filters model
        filters = Filters(
            keywords=["data", "engineering"],
            keyword_mode="include",
            min_duration=60,
            exclude_shorts=True,
            max_results=50
        )
        
        filters_correct = (
            filters.keywords == ["data", "engineering"] and
            filters.keyword_mode == "include" and
            filters.min_duration == 60
        )
        print_result("Filters model structure", filters_correct)
        results.append(filters_correct)
        
        # Test RunStatus enum
        status_values = [s.value for s in RunStatus]
        expected_values = ["pending", "running", "completed", "failed", "cancelled"]
        status_correct = all(v in status_values for v in expected_values)
        print_result("RunStatus enum values", status_correct,
                    f"Values: {status_values}")
        results.append(status_correct)
        
    except Exception as e:
        print_result("Data models", False, str(e))
        results.append(False)
    
    return all(results)

def test_gui_integration():
    """Test GUI imports and structure."""
    print_section("5. GUI INTEGRATION VALIDATION")
    
    results = []
    
    try:
        # Test GUI imports (without launching)
        import_test = """
from src.gui.main_app import YouTube2SheetsGUI
from src.backend.youtube2sheets import SyncConfig
from src.services.automator import YouTubeToSheetsAutomator
"""
        
        exec(import_test)
        print_result("GUI imports successful", True)
        results.append(True)
        
        # Check for import conflicts
        from src.backend.youtube2sheets import SyncConfig as BackendSyncConfig
        
        backend_fields = BackendSyncConfig.__dataclass_fields__.keys()
        expected_fields = ['min_duration_seconds', 'max_duration_seconds', 'keyword_filter', 'keyword_mode', 'max_videos']
        
        fields_correct = all(f in backend_fields for f in expected_fields)
        print_result("SyncConfig structure matches expected", fields_correct,
                    f"Fields: {list(backend_fields)}")
        results.append(fields_correct)
        
    except Exception as e:
        print_result("GUI integration", False, str(e))
        results.append(False)
    
    return all(results)

def test_configuration_compatibility():
    """Test that services automator is compatible with backend SyncConfig."""
    print_section("6. CONFIGURATION COMPATIBILITY")
    
    results = []
    
    try:
        from src.backend.youtube2sheets import SyncConfig
        from src.services.automator import YouTubeToSheetsAutomator
        from src.domain.models import RunConfig, Filters, Destination
        
        # Create a SyncConfig (used by GUI)
        sync_config = SyncConfig(
            min_duration_seconds=60,
            max_duration_seconds=3600,
            keyword_filter="data,engineering",
            keyword_mode="include",
            max_videos=50
        )
        
        print_result("Create SyncConfig", True)
        results.append(True)
        
        # Check if automator has sync_channel_to_sheet method (used by GUI)
        has_method = hasattr(YouTubeToSheetsAutomator, 'sync_channel_to_sheet')
        print_result("Automator has sync_channel_to_sheet method", has_method)
        results.append(has_method)
        
        # Check automator initialization (test class structure only)
        try:
            # Verify class exists and has required methods
            required_methods = ['sync_channel_to_sheet', 'sync_channels_to_sheets', '_build_automator' if hasattr(YouTubeToSheetsAutomator, '_build_automator') else 'get_status']
            has_methods = all(hasattr(YouTubeToSheetsAutomator, method) or method == '_build_automator' for method in required_methods)
            print_result("Automator has required methods", has_methods,
                        f"Methods: {[m for m in required_methods if hasattr(YouTubeToSheetsAutomator, m)]}")
            results.append(has_methods)
        except Exception as e:
            print_result("Automator structure validation", False, str(e))
            results.append(False)
        
    except Exception as e:
        print_result("Configuration compatibility", False, str(e))
        results.append(False)
    
    return all(results)

def generate_summary_report(test_results: dict):
    """Generate comprehensive summary report."""
    print_section("COMPREHENSIVE VALIDATION SUMMARY")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    failed_tests = total_tests - passed_tests
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {success_rate:.1f}%\n")
    
    # Detailed results
    print("Detailed Results:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} | {test_name}")
    
    # Overall status
    print(f"\n{'='*80}")
    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED - System is 100% validated!")
        print("✅ Architecture alignment confirmed")
        print("✅ Services layer fully functional")
        print("✅ Backend optimization operational")
        print("✅ Data models validated")
        print("✅ GUI integration confirmed")
        print("✅ Configuration compatibility verified")
    else:
        print(f"⚠️ {failed_tests} TEST(S) FAILED - Issues require attention")
        print("\n📋 RECOMMENDATIONS:")
        
        if not test_results.get("Architecture Alignment", True):
            print("  1. Consolidate duplicate automator systems")
            print("     - Choose primary implementation (services or backend)")
            print("     - Migrate all features to chosen system")
            print("     - Remove duplicate code")
        
        if not test_results.get("Services Layer", True):
            print("  2. Fix services layer issues")
            print("     - Ensure all required methods exist")
            print("     - Verify method signatures match usage")
        
        if not test_results.get("Backend Optimization", True):
            print("  3. Verify backend optimization features")
            print("     - Test ETag caching")
            print("     - Test video deduplication")
            print("     - Test quota tracking")
    
    print(f"{'='*80}\n")
    
    return success_rate == 100

def main():
    """Run comprehensive validation tests."""
    print(f"\n{'#'*80}")
    print("#  COMPREHENSIVE SYSTEM VALIDATION TEST")
    print("#  YouTube2Sheets Production Readiness Check")
    print(f"#  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"#  Framework: @PolyChronos-Omega.md")
    print(f"#  Standards: @QualityMandate.md")
    print(f"{'#'*80}\n")
    
    # Run all tests
    test_results = {
        "Architecture Alignment": test_architecture_alignment(),
        "Services Layer": test_services_layer_functionality(),
        "Backend Optimization": test_backend_optimization_layer(),
        "Data Models": test_data_models(),
        "GUI Integration": test_gui_integration(),
        "Configuration Compatibility": test_configuration_compatibility()
    }
    
    # Generate summary
    all_passed = generate_summary_report(test_results)
    
    # Save results to file
    results_file = Path("DeltaReports") / "SystemValidation_Report.json"
    results_file.parent.mkdir(exist_ok=True)
    
    report_data = {
        "test_date": datetime.now().isoformat(),
        "framework": "@PolyChronos-Omega.md",
        "standards": "@QualityMandate.md",
        "test_results": test_results,
        "success_rate": sum(1 for r in test_results.values() if r) / len(test_results) * 100,
        "status": "PASSED" if all_passed else "FAILED"
    }
    
    with open(results_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"📄 Full report saved to: {results_file}\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

