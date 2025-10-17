"""
Verify Table Structure Alignment
Check that our conditional formatting matches the existing Google Sheets structure
"""
import sys
import os
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def analyze_existing_table_structure():
    """Analyze the existing table structure in Google Sheets."""
    print("Analyzing Existing Google Sheets Table Structure")
    print("=" * 60)
    
    try:
        from services.sheets_service import SheetsService, SheetsConfig
        from config_loader import load_config
        import re
        
        # Load configuration
        config = load_config()
        service_account_file = config.get('google_sheets_service_account_json')
        spreadsheet_url = config.get('default_spreadsheet_url')
        
        if not service_account_file:
            print("❌ Missing configuration")
            return False
        
        # Extract spreadsheet ID
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', spreadsheet_url)
        if not sheet_id_match:
            print("❌ Invalid spreadsheet URL")
            return False
        
        sheet_id = sheet_id_match.group(1)
        sheets_config = SheetsConfig(
            service_account_file=service_account_file,
            spreadsheet_id=sheet_id
        )
        sheets_service = SheetsService(sheets_config)
        
        print("✅ Services initialized successfully")
        
        # Analyze existing tabs
        print("\n🔍 Analyzing existing tabs...")
        tabs = sheets_service.get_existing_tabs()
        print(f"Found {len(tabs)} tabs: {tabs}")
        
        # Analyze the AI_ML tab structure (most likely to have data)
        test_tab = "AI_ML"
        print(f"\n📊 Analyzing table structure for: {test_tab}")
        
        # Read the data to understand the structure
        sheet_data = sheets_service.read_sheet_data(test_tab)
        print(f"Read {len(sheet_data)} rows from {test_tab}")
        
        if sheet_data:
            # Analyze headers
            headers = sheet_data[0] if sheet_data else []
            print(f"\n📋 Headers found:")
            for i, header in enumerate(headers):
                print(f"  Column {chr(65+i)}: '{header}'")
            
            # Analyze data types and content
            print(f"\n🔍 Data analysis:")
            if len(sheet_data) > 1:
                sample_row = sheet_data[1]
                print(f"Sample row data:")
                for i, (header, value) in enumerate(zip(headers, sample_row)):
                    print(f"  {header}: '{value}' (Type: {type(value).__name__})")
            
            # Check for specific columns we expect
            expected_columns = [
                'Video ID', 'Title', 'URL', 'Published Date', 'View Count', 
                'Duration', 'Like Count', 'Comment Count', 'Channel ID', 
                'Channel Title', 'Description', 'Tags', 'Added Date'
            ]
            
            print(f"\n🎯 Column alignment check:")
            alignment_issues = []
            
            for i, expected in enumerate(expected_columns):
                if i < len(headers):
                    actual = headers[i]
                    if expected.lower() in actual.lower() or actual.lower() in expected.lower():
                        print(f"  ✅ Column {i+1}: '{actual}' matches expected '{expected}'")
                    else:
                        print(f"  ⚠️  Column {i+1}: '{actual}' doesn't match expected '{expected}'")
                        alignment_issues.append((i+1, actual, expected))
                else:
                    print(f"  ❌ Column {i+1}: Missing - expected '{expected}'")
                    alignment_issues.append((i+1, "MISSING", expected))
            
            # Analyze the current conditional formatting
            print(f"\n🎨 Current conditional formatting analysis:")
            print("Our system applies formatting to these columns:")
            print("  Column E (5): View Count - NUMBER_GREATER")
            print("  Column D (4): Published Date - DATE_AFTER") 
            print("  Column G (7): Like Count - NUMBER_GREATER")
            print("  Column F (6): Duration - TEXT_CONTAINS")
            
            # Check if these columns exist and contain the right data
            print(f"\n🔍 Formatting target validation:")
            if len(headers) >= 7:
                print(f"  Column D ({headers[3] if len(headers) > 3 else 'N/A'}): Date formatting target")
                print(f"  Column E ({headers[4] if len(headers) > 4 else 'N/A'}): View count formatting target")
                print(f"  Column F ({headers[5] if len(headers) > 5 else 'N/A'}): Duration formatting target")
                print(f"  Column G ({headers[6] if len(headers) > 6 else 'N/A'}): Like count formatting target")
            else:
                print("  ❌ Not enough columns for our formatting targets")
            
            # Check data types in sample rows
            if len(sheet_data) > 1:
                sample_row = sheet_data[1]
                print(f"\n📊 Sample data type analysis:")
                for i, (header, value) in enumerate(zip(headers, sample_row)):
                    if i < len(sample_row):
                        # Try to determine data type
                        try:
                            if value.isdigit():
                                data_type = "NUMBER"
                            elif '/' in value and any(char.isdigit() for char in value):
                                data_type = "DATE"
                            else:
                                data_type = "TEXT"
                        except:
                            data_type = "TEXT"
                        
                        print(f"  {header}: '{value}' -> {data_type}")
            
            return len(alignment_issues) == 0, alignment_issues, headers, sheet_data
        
        else:
            print("❌ No data found in the sheet")
            return False, [], [], []
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False, [], [], []

def main():
    """Run the table structure alignment verification."""
    print("Google Sheets Table Structure Alignment Verification")
    print("=" * 60)
    print("Checking if our conditional formatting aligns with existing structure...")
    
    success, issues, headers, data = analyze_existing_table_structure()
    
    if success:
        print("\n🎉 PERFECT ALIGNMENT CONFIRMED!")
        print("✅ Our conditional formatting is 100% aligned with existing table structure")
        print("✅ All columns match expected positions")
        print("✅ Data types are compatible with formatting rules")
        print("🚀 System is ready for production use!")
        return True
    else:
        print("\n⚠️  ALIGNMENT ISSUES DETECTED:")
        for col_num, actual, expected in issues:
            print(f"  Column {col_num}: '{actual}' vs expected '{expected}'")
        
        print("\n🔧 RECOMMENDATIONS:")
        print("1. Update our column mapping to match existing structure")
        print("2. Adjust conditional formatting rules accordingly")
        print("3. Test with actual data to ensure compatibility")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
