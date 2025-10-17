"""
Quick Google Sheets Permissions Verification
Run this after granting permissions to verify the fix
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def verify_google_sheets_permissions():
    """Quick verification of Google Sheets permissions."""
    print("🔍 Verifying Google Sheets Permissions...")
    print("=" * 50)
    
    try:
        from services.sheets_service import SheetsService, SheetsConfig
        from config_loader import load_config
        
        # Load config
        config = load_config()
        service_account_file = config.get('google_sheets_service_account_json')
        spreadsheet_url = config.get('default_spreadsheet_url')
        
        if not service_account_file or not spreadsheet_url:
            print("❌ Configuration missing")
            return False
        
        # Extract spreadsheet ID
        import re
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', spreadsheet_url)
        if not sheet_id_match:
            print("❌ Invalid spreadsheet URL")
            return False
        
        sheet_id = sheet_id_match.group(1)
        print(f"📊 Testing spreadsheet: {sheet_id}")
        
        # Create sheets service
        sheets_config = SheetsConfig(
            service_account_file=service_account_file,
            spreadsheet_id=sheet_id
        )
        sheets_service = SheetsService(sheets_config)
        
        # Test connection
        print("🔄 Testing connection...")
        tabs = sheets_service.get_existing_tabs()
        
        if tabs:
            print(f"✅ SUCCESS! Found {len(tabs)} tabs:")
            for i, tab in enumerate(tabs, 1):
                print(f"  {i}. {tab}")
            print(f"\n🎯 Dropdown will work perfectly!")
            return True
        else:
            print("❌ No tabs found")
            print("🔧 Please check permissions:")
            print("   n8n-sa@n8n-integrations-452015.iam.gserviceaccount.com")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
        if "403" in str(e) or "PERMISSION_DENIED" in str(e):
            print("\n🔧 PERMISSIONS STILL NOT GRANTED!")
            print("📋 To fix:")
            print("1. Open: https://docs.google.com/spreadsheets/d/13WluwYBj5EPg5-zpvAtDVHtekAwPUnayNArKrMAOxAE/edit")
            print("2. Click 'Share'")
            print("3. Add: n8n-sa@n8n-integrations-452015.iam.gserviceaccount.com")
            print("4. Set to 'Viewer'")
            print("5. Click 'Send'")
        
        return False

if __name__ == "__main__":
    success = verify_google_sheets_permissions()
    if success:
        print("\n🎉 PERMISSIONS VERIFIED! System is ready!")
    else:
        print("\n❌ Permissions not granted yet. Please follow the steps above.")
    sys.exit(0 if success else 1)


