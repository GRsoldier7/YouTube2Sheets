#!/usr/bin/env python3
"""
Multi-Spreadsheet Support Test
Tests the new multi-spreadsheet management functionality
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.spreadsheet_manager import SpreadsheetManager
from services.sheets_service import SheetsService, SheetsConfig
from dotenv import load_dotenv

def test_multi_spreadsheet():
    """Test multi-spreadsheet management."""
    print("[MULTI-SPREADSHEET TEST] Testing multi-spreadsheet support...")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    service_account_file = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON')
    
    if not service_account_file:
        print("[ERROR] Missing GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON environment variable")
        return False
    
    # Test 1: Initialize spreadsheet manager
    print("\n[TEST 1] Initializing spreadsheet manager...")
    manager = SpreadsheetManager(
        config_file="spreadsheets.json",
        service_account_file=service_account_file
    )
    print("[OK] Spreadsheet manager initialized")
    
    # Test 2: Get existing spreadsheets
    print("\n[TEST 2] Getting existing spreadsheets...")
    spreadsheets = manager.get_spreadsheets()
    print(f"[INFO] Found {len(spreadsheets)} spreadsheets:")
    for i, sheet in enumerate(spreadsheets, 1):
        print(f"  {i}. {sheet.name} (Default: {sheet.is_default})")
        print(f"     ID: {sheet.id}")
    
    # Test 3: Get spreadsheet names
    print("\n[TEST 3] Getting spreadsheet names...")
    names = manager.get_spreadsheet_names()
    print(f"[INFO] Spreadsheet names: {names}")
    
    # Test 4: Get default spreadsheet
    print("\n[TEST 4] Getting default spreadsheet...")
    default_sheet = manager.get_default_spreadsheet()
    if default_sheet:
        print(f"[INFO] Default spreadsheet: {default_sheet.name}")
        print(f"[INFO] ID: {default_sheet.id}")
    else:
        print("[WARN] No default spreadsheet set")
    
    # Test 5: Get last used spreadsheet
    print("\n[TEST 5] Getting last used spreadsheet...")
    last_used = manager.get_last_used_spreadsheet()
    if last_used:
        print(f"[INFO] Last used spreadsheet: {last_used.name}")
        print(f"[INFO] ID: {last_used.id}")
    else:
        print("[WARN] No last used spreadsheet")
    
    # Test 6: Verify spreadsheet access
    print("\n[TEST 6] Verifying spreadsheet access...")
    if default_sheet:
        sheets_config = SheetsConfig(
            service_account_file=service_account_file,
            spreadsheet_id=default_sheet.id
        )
        sheets_service = SheetsService(sheets_config)
        has_access = sheets_service.verify_access()
        print(f"[ACCESS] Service account has access: {has_access}")
        
        if has_access:
            # Get tabs from spreadsheet
            tabs = sheets_service.get_existing_tabs()
            print(f"[INFO] Found {len(tabs)} tabs:")
            for i, tab in enumerate(tabs[:10], 1):  # Show first 10
                print(f"  {i}. {tab}")
            if len(tabs) > 10:
                print(f"  ... and {len(tabs) - 10} more")
    
    print("\n" + "=" * 60)
    print("[MULTI-SPREADSHEET TEST] Test completed!")
    
    return True

if __name__ == "__main__":
    success = test_multi_spreadsheet()
    if success:
        print("\n[SUCCESS] Multi-spreadsheet test completed!")
    else:
        print("\n[ERROR] Multi-spreadsheet test failed!")
        sys.exit(1)

