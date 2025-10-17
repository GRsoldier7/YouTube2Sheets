#!/usr/bin/env python3
"""
Production Readiness Test
Final validation before production deployment
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_production_readiness():
    """Test production readiness with real API keys."""
    print("🚀 PRODUCTION READINESS TEST")
    print("=" * 50)
    
    # Check environment variables
    youtube_key = os.getenv("YOUTUBE_API_KEY")
    service_account = os.getenv("GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON")
    
    if not youtube_key:
        print("❌ YOUTUBE_API_KEY not found in environment")
        return False
    
    if not service_account:
        print("❌ GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON not found in environment")
        return False
    
    print("✅ Environment variables configured")
    
    # Test YouTube API
    try:
        from services.youtube_service import YouTubeService, YouTubeConfig
        
        config = YouTubeConfig(api_key=youtube_key)
        service = YouTubeService(config)
        
        # Test channel resolution
        channel_id = service.resolve_channel_id("TechTFQ")
        if channel_id:
            print(f"✅ YouTube API working - resolved @TechTFQ to {channel_id}")
        else:
            print("❌ YouTube API failed - could not resolve @TechTFQ")
            return False
            
    except Exception as e:
        print(f"❌ YouTube API test failed: {e}")
        return False
    
    # Test Google Sheets API
    try:
        from services.sheets_service import SheetsService, SheetsConfig
        
        # Use a test spreadsheet ID (you can replace this)
        test_sheet_id = "1CIKN4b8L6Awdys5tv4Ht_LirSvHgx0Hscj9MMzBKjZg"
        
        config = SheetsConfig(
            service_account_file=service_account,
            spreadsheet_id=test_sheet_id
        )
        service = SheetsService(config)
        
        # Test spreadsheet access
        if service.verify_access():
            print("✅ Google Sheets API working - verified access")
        else:
            print("❌ Google Sheets API failed - no access")
            return False
            
    except Exception as e:
        print(f"❌ Google Sheets API test failed: {e}")
        return False
    
    # Test GUI initialization
    try:
        from gui.main_app import YouTube2SheetsGUI
        
        # This will test GUI initialization without showing window
        gui = YouTube2SheetsGUI()
        print("✅ GUI initialization working")
        
    except Exception as e:
        print(f"❌ GUI initialization failed: {e}")
        return False
    
    print("\n🎉 ALL PRODUCTION SYSTEMS READY!")
    print("✅ YouTube API: Working")
    print("✅ Google Sheets API: Working") 
    print("✅ GUI: Working")
    print("✅ Environment: Configured")
    
    return True

if __name__ == "__main__":
    success = test_production_readiness()
    sys.exit(0 if success else 1)
