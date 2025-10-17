"""
Debug Actual Tab Creation Failure
Find the real cause and fix it with concrete evidence
"""
import sys
import os
from pathlib import Path
import traceback

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def debug_actual_failure():
    """Debug the actual tab creation failure."""
    print("🔍 DEBUGGING ACTUAL TAB CREATION FAILURE")
    print("=" * 60)
    
    try:
        from src.services.sheets_service import SheetsService, SheetsConfig
        from config_loader import load_config
        import re
        
        # Load configuration
        config = load_config()
        sheet_url = config.get('default_spreadsheet_url', '')
        
        print(f"Sheet URL: {sheet_url}")
        
        # Extract spreadsheet ID
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheet_url)
        if not sheet_id_match:
            print("❌ Could not extract sheet ID from URL")
            return False
        
        sheet_id = sheet_id_match.group(1)
        print(f"Extracted sheet ID: {sheet_id}")
        
        # Create sheets service
        sheets_config = SheetsConfig(
            service_account_file=config['google_sheets_service_account_json'],
            spreadsheet_id=sheet_id
        )
        sheets_service = SheetsService(sheets_config)
        
        print("✅ Sheets service initialized")
        
        # Test the actual tab creation that's failing
        test_tab_name = "Google_BigQuery"  # Same name that's failing
        print(f"Testing tab creation with exact name: '{test_tab_name}'")
        
        # Check if tab already exists
        try:
            spreadsheet = sheets_service.service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            existing_tabs = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
            print(f"Existing tabs: {existing_tabs}")
            
            if test_tab_name in existing_tabs:
                print(f"❌ Tab '{test_tab_name}' already exists!")
                return False
            else:
                print(f"✅ Tab '{test_tab_name}' does not exist, can create")
        except Exception as e:
            print(f"❌ Failed to check existing tabs: {e}")
            return False
        
        # Try to create the tab
        try:
            result = sheets_service.create_sheet_tab(test_tab_name)
            if result:
                print("✅ Tab creation successful!")
                return True
            else:
                print("❌ Tab creation returned False")
                return False
        except Exception as e:
            print(f"❌ Tab creation failed with exception: {e}")
            print(f"Exception type: {type(e).__name__}")
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ Debug setup failed: {e}")
        traceback.print_exc()
        return False

def test_actual_gui_workflow():
    """Test the actual GUI workflow that's failing."""
    print("\n🖥️ TESTING ACTUAL GUI WORKFLOW")
    print("=" * 60)
    
    try:
        import customtkinter as ctk
        from src.gui.main_app import YouTube2SheetsGUI
        
        # Create GUI
        root = ctk.CTk()
        root.withdraw()
        app = YouTube2SheetsGUI()
        
        # Simulate the exact workflow that's failing
        print("Simulating new tab creation workflow...")
        
        # Set up the exact scenario
        app.use_existing_tab_var.set(False)  # New tab mode
        app.new_tab_entry.insert(0, "Google_BigQuery")  # Same name
        
        print("✅ GUI setup complete")
        
        # Test the tab creation logic
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
            
            # Test the actual tab creation
            tab_name = "Google_BigQuery"
            result = sheets_service.create_sheet_tab(tab_name)
            
            if result:
                print("✅ GUI workflow tab creation successful!")
            else:
                print("❌ GUI workflow tab creation failed")
                return False
            
        except Exception as e:
            print(f"❌ GUI workflow failed: {e}")
            traceback.print_exc()
            return False
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        traceback.print_exc()
        return False

def find_real_solution():
    """Find the real solution to the tab creation problem."""
    print("\n🔧 FINDING REAL SOLUTION")
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
        
        # Check current spreadsheet state
        spreadsheet = sheets_service.service.spreadsheets().get(
            spreadsheetId=sheet_id
        ).execute()
        
        print(f"Spreadsheet title: {spreadsheet.get('properties', {}).get('title', 'Unknown')}")
        print(f"Number of sheets: {len(spreadsheet.get('sheets', []))}")
        
        # Calculate total cells
        total_cells = 0
        for sheet in spreadsheet.get('sheets', []):
            sheet_props = sheet.get('properties', {})
            grid_props = sheet_props.get('gridProperties', {})
            row_count = grid_props.get('rowCount', 0)
            column_count = grid_props.get('columnCount', 0)
            sheet_cells = row_count * column_count
            total_cells += sheet_cells
            
            print(f"Sheet '{sheet_props.get('title', 'Unknown')}': {row_count} rows × {column_count} columns = {sheet_cells:,} cells")
        
        print(f"Total cells: {total_cells:,}")
        print(f"Google Sheets limit: 10,000,000 cells")
        print(f"Available space: {10_000_000 - total_cells:,} cells")
        
        if total_cells >= 10_000_000:
            print("❌ Spreadsheet is at or over the cell limit")
            return False
        else:
            print("✅ Spreadsheet has space for new tabs")
            
            # Try creating a tab with a unique name
            import time
            unique_tab_name = f"Test_Tab_{int(time.time())}"
            print(f"Trying to create tab: {unique_tab_name}")
            
            result = sheets_service.create_sheet_tab(unique_tab_name)
            if result:
                print("✅ Tab creation successful!")
                return True
            else:
                print("❌ Tab creation still failed")
                return False
        
    except Exception as e:
        print(f"❌ Solution finding failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Debug the actual tab creation failure."""
    print("🚀 ACTUAL TAB CREATION FAILURE DEBUG")
    print("=" * 70)
    print("Finding the real cause and implementing the real fix")
    print("=" * 70)
    
    tests = [
        ("Debug Actual Failure", debug_actual_failure),
        ("Test Actual GUI Workflow", test_actual_gui_workflow),
        ("Find Real Solution", find_real_solution)
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
    print("ACTUAL DEBUG RESULTS")
    print("=" * 70)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
