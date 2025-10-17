"""
Diagnose Google Sheets 403 Error
Test the exact API call and authentication to identify the issue
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def diagnose_google_sheets_403():
    """Diagnose the 403 error with detailed logging."""
    print("🔍 Diagnosing Google Sheets 403 Error...")
    print("=" * 60)
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        from config_loader import load_config
        
        # Load config
        config = load_config()
        service_account_file = config.get('google_sheets_service_account_json')
        spreadsheet_url = config.get('default_spreadsheet_url')
        
        print(f"📊 Service Account File: {service_account_file}")
        print(f"📊 Spreadsheet URL: {spreadsheet_url}")
        
        if not service_account_file or not spreadsheet_url:
            print("❌ Configuration missing")
            return False
        
        # Extract spreadsheet ID
        import re
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', spreadsheet_url)
        if not sheet_id_match:
            print("❌ Invalid spreadsheet URL format")
            return False
        
        sheet_id = sheet_id_match.group(1)
        print(f"📊 Spreadsheet ID: {sheet_id}")
        
        # Check if service account file exists
        if not os.path.exists(service_account_file):
            print(f"❌ Service account file not found: {service_account_file}")
            return False
        
        print(f"✅ Service account file exists")
        
        # Load credentials
        print("🔄 Loading credentials...")
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        print(f"✅ Credentials loaded successfully")
        print(f"📧 Service account email: {credentials.service_account_email}")
        
        # Build service
        print("🔄 Building Google Sheets service...")
        service = build('sheets', 'v4', credentials=credentials)
        print(f"✅ Service built successfully")
        
        # Test 1: Try to get spreadsheet metadata
        print(f"\n🧪 Test 1: Getting spreadsheet metadata...")
        try:
            spreadsheet = service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            print(f"✅ SUCCESS! Got spreadsheet metadata")
            print(f"📊 Title: {spreadsheet.get('properties', {}).get('title', 'Unknown')}")
            
            # Get sheets
            sheets = spreadsheet.get('sheets', [])
            print(f"📋 Found {len(sheets)} sheets:")
            for i, sheet in enumerate(sheets, 1):
                title = sheet.get('properties', {}).get('title', 'Unknown')
                print(f"  {i}. {title}")
            
            return True
            
        except HttpError as e:
            print(f"❌ HTTP Error: {e}")
            print(f"📊 Status Code: {e.resp.status}")
            print(f"📊 Error Details: {e.error_details}")
            
            if e.resp.status == 403:
                print(f"\n🔧 403 PERMISSION_DENIED Analysis:")
                print(f"   - Service account: {credentials.service_account_email}")
                print(f"   - Spreadsheet ID: {sheet_id}")
                print(f"   - Scopes: {credentials.scopes}")
                
                # Check if the spreadsheet ID is correct
                print(f"\n🔍 Verifying spreadsheet ID...")
                print(f"   Expected format: 13WluwYBj5EPg5-zpvAtDVHtekAwPUnayNArKrMAOxAE")
                print(f"   Actual ID: {sheet_id}")
                
                if len(sheet_id) != 44:
                    print(f"❌ Spreadsheet ID length is incorrect (should be 44 characters)")
                    return False
                
                print(f"✅ Spreadsheet ID format looks correct")
                
                # Check if the service account has the right permissions
                print(f"\n🔍 Checking service account permissions...")
                print(f"   Service account email: {credentials.service_account_email}")
                print(f"   This account needs to be added to the spreadsheet with 'Viewer' permission")
                
                return False
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_alternative_approach():
    """Test alternative approach to Google Sheets access."""
    print(f"\n🔄 Testing Alternative Approach...")
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from config_loader import load_config
        
        config = load_config()
        service_account_file = config.get('google_sheets_service_account_json')
        spreadsheet_url = config.get('default_spreadsheet_url')
        
        # Extract spreadsheet ID
        import re
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', spreadsheet_url)
        sheet_id = sheet_id_match.group(1)
        
        # Try with different scopes
        print("🧪 Testing with different scopes...")
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        
        # Try to get just the spreadsheet properties
        print("🧪 Testing with minimal request...")
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=sheet_id,
            fields='properties.title,sheets.properties.title'
        ).execute()
        
        print(f"✅ Alternative approach worked!")
        return True
        
    except Exception as e:
        print(f"❌ Alternative approach failed: {e}")
        return False

def main():
    """Run the diagnosis."""
    print("🚀 Google Sheets 403 Error Diagnosis")
    print("=" * 60)
    
    # Test 1: Standard diagnosis
    success1 = diagnose_google_sheets_403()
    
    # Test 2: Alternative approach
    success2 = test_alternative_approach()
    
    print(f"\n📊 Diagnosis Results:")
    print(f"  Standard approach: {'✅ SUCCESS' if success1 else '❌ FAILED'}")
    print(f"  Alternative approach: {'✅ SUCCESS' if success2 else '❌ FAILED'}")
    
    if success1 or success2:
        print(f"\n🎉 ISSUE RESOLVED!")
        return True
    else:
        print(f"\n❌ Issue persists. Service account needs proper permissions.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


