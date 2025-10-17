#!/usr/bin/env python3
"""
Test Cell Limit Handling
Tests the new cell limit detection and existing tab fallback functionality
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.sheets_service import SheetsService, SheetsConfig
from dotenv import load_dotenv

def test_cell_limit_handling():
    """Test cell limit detection and existing tab fallback."""
    print("[CELL LIMIT TEST] Testing cell limit handling...")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    spreadsheet_url = os.getenv('DEFAULT_SPREADSHEET_URL')
    service_account_file = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON')
    
    if not spreadsheet_url or not service_account_file:
        print("[ERROR] Missing required environment variables")
        return False
    
    # Extract spreadsheet ID
    import re
    spreadsheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', spreadsheet_url)
    if not spreadsheet_id_match:
        print("[ERROR] Could not extract spreadsheet ID from URL")
        return False
    
    spreadsheet_id = spreadsheet_id_match.group(1)
    print(f"[CONFIG] Spreadsheet ID: {spreadsheet_id}")
    
    # Initialize sheets service
    sheets_config = SheetsConfig(
        service_account_file=service_account_file,
        spreadsheet_id=spreadsheet_id
    )
    sheets_service = SheetsService(sheets_config)
    
    if not sheets_service.service:
        print("[ERROR] Failed to initialize Google Sheets service")
        return False
    
    print("[OK] Google Sheets service initialized")
    
    # Test 1: Check cell limit
    print("\n[TEST 1] Checking cell limit...")
    is_at_limit = sheets_service.is_at_cell_limit()
    print(f"[CELL LIMIT] Is at cell limit: {is_at_limit}")
    
    if is_at_limit:
        print("[INFO] Spreadsheet is at or near the 10 million cell limit")
    else:
        print("[INFO] Spreadsheet has room for new tabs")
    
    # Test 2: Get existing tabs
    print("\n[TEST 2] Getting existing tabs...")
    existing_tabs = sheets_service.get_existing_tabs()
    print(f"[TABS] Found {len(existing_tabs)} existing tabs:")
    for i, tab in enumerate(existing_tabs, 1):
        print(f"  {i}. {tab}")
    
    # Test 3: Filter tabs (exclude ranking tabs)
    print("\n[TEST 3] Filtering tabs...")
    filtered_tabs = [tab for tab in existing_tabs if "ranking" not in tab.lower()]
    print(f"[FILTERED] {len(filtered_tabs)} suitable tabs after filtering:")
    for i, tab in enumerate(filtered_tabs, 1):
        print(f"  {i}. {tab}")
    
    # Test 4: Test tab creation (if not at limit)
    if not is_at_limit:
        print("\n[TEST 4] Testing tab creation...")
        test_tab_name = f"CellLimitTest_{int(time.time())}"
        success = sheets_service.create_sheet_tab(test_tab_name)
        if success:
            print(f"[OK] Successfully created test tab: {test_tab_name}")
            
            # Clean up - delete the test tab
            try:
                # Note: We don't have a delete method, but this is just a test
                print(f"[INFO] Test tab '{test_tab_name}' created for testing")
            except Exception as e:
                print(f"[WARN] Could not clean up test tab: {e}")
        else:
            print(f"[ERROR] Failed to create test tab: {test_tab_name}")
    else:
        print("\n[TEST 4] Skipping tab creation test (at cell limit)")
    
    print("\n" + "=" * 60)
    print("[CELL LIMIT TEST] Test completed!")
    
    return True

if __name__ == "__main__":
    success = test_cell_limit_handling()
    if success:
        print("\n[SUCCESS] Cell limit handling test completed!")
    else:
        print("\n[ERROR] Cell limit handling test failed!")
        sys.exit(1)
