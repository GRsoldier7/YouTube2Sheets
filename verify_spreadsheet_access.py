"""
Verify Spreadsheet Access
Check if the service account can access the spreadsheet
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def verify_spreadsheet_access():
    """Verify if the service account can access the spreadsheet."""
    print("🔍 Verifying Spreadsheet Access...")
    print("=" * 50)
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        from config_loader import load_config
        
        # Load config
        config = load_config()
        service_account_file = config.get('google_sheets_service_account_json')
        spreadsheet_url = config.get('default_spreadsheet_url')
        
        print(f"📊 Service Account: n8n-sa@n8n-integrations-452015.iam.gserviceaccount.com")
        print(f"📊 Spreadsheet URL: {spreadsheet_url}")
        
        # Extract spreadsheet ID
        import re
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', spreadsheet_url)
        sheet_id = sheet_id_match.group(1)
        print(f"📊 Spreadsheet ID: {sheet_id}")
        
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        # Build service
        service = build('sheets', 'v4', credentials=credentials)
        
        # Test access
        print(f"\n🧪 Testing access to spreadsheet...")
        try:
            spreadsheet = service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            print(f"✅ SUCCESS! Service account has access")
            print(f"📊 Spreadsheet title: {spreadsheet.get('properties', {}).get('title', 'Unknown')}")
            
            # Get sheets
            sheets = spreadsheet.get('sheets', [])
            print(f"📋 Found {len(sheets)} sheets:")
            for i, sheet in enumerate(sheets, 1):
                title = sheet.get('properties', {}).get('title', 'Unknown')
                print(f"  {i}. {title}")
            
            return True
            
        except HttpError as e:
            if e.resp.status == 403:
                print(f"❌ 403 PERMISSION_DENIED")
                print(f"🔧 The service account does NOT have permission to access this spreadsheet")
                print(f"\n📋 To fix this:")
                print(f"1. Open the spreadsheet: {spreadsheet_url}")
                print(f"2. Click 'Share' (top right)")
                print(f"3. Add: n8n-sa@n8n-integrations-452015.iam.gserviceaccount.com")
                print(f"4. Set permission to 'Viewer'")
                print(f"5. Click 'Send'")
                return False
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_alternative_spreadsheet():
    """Check if there's an alternative spreadsheet we should be using."""
    print(f"\n🔍 Checking for alternative spreadsheet...")
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from config_loader import load_config
        
        config = load_config()
        service_account_file = config.get('google_sheets_service_account_json')
        
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        
        # Build Drive service to search for spreadsheets
        drive_service = build('drive', 'v3', credentials=credentials)
        
        # Search for spreadsheets
        print("🔍 Searching for accessible spreadsheets...")
        results = drive_service.files().list(
            q="mimeType='application/vnd.google-apps.spreadsheet'",
            fields="files(id, name, webViewLink)"
        ).execute()
        
        files = results.get('files', [])
        if files:
            print(f"📊 Found {len(files)} accessible spreadsheets:")
            for i, file in enumerate(files, 1):
                print(f"  {i}. {file['name']}")
                print(f"     ID: {file['id']}")
                print(f"     URL: {file['webViewLink']}")
        else:
            print("❌ No accessible spreadsheets found")
        
        return len(files) > 0
        
    except Exception as e:
        print(f"❌ Error searching for spreadsheets: {e}")
        return False

def main():
    """Run the verification."""
    print("🚀 Spreadsheet Access Verification")
    print("=" * 50)
    
    # Test 1: Verify current spreadsheet access
    success1 = verify_spreadsheet_access()
    
    # Test 2: Check for alternative spreadsheets
    success2 = check_alternative_spreadsheet()
    
    print(f"\n📊 Verification Results:")
    print(f"  Current spreadsheet access: {'✅ SUCCESS' if success1 else '❌ FAILED'}")
    print(f"  Alternative spreadsheets found: {'✅ YES' if success2 else '❌ NO'}")
    
    if success1:
        print(f"\n🎉 SPREADSHEET ACCESS VERIFIED!")
        return True
    else:
        print(f"\n❌ Spreadsheet access denied. Permissions need to be granted.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


