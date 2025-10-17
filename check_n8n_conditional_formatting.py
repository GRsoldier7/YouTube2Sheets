"""
Check n8n Tab Conditional Formatting
=====================================
Reads the actual conditional formatting rules from the n8n tab.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def check_conditional_formatting():
    """Check conditional formatting on n8n tab."""
    
    # Setup credentials
    service_account = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON', 'credentials/service-account.json')
    spreadsheet_id = '1CIKN4b8L6Awdys5tv4Ht_LirSvHgx0Hscj9MMzBKjZg'
    
    print(f"Using service account: {service_account}")
    print(f"Using spreadsheet ID: {spreadsheet_id}\n")
    
    # Initialize Google Sheets API
    creds = Credentials.from_service_account_file(
        service_account,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=creds)
    
    print("="*80)
    print("  CHECKING n8n TAB CONDITIONAL FORMATTING")
    print("="*80)
    
    # Get spreadsheet metadata including conditional format rules
    spreadsheet = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        includeGridData=False
    ).execute()
    
    # Find n8n sheet
    n8n_sheet = None
    for sheet in spreadsheet.get('sheets', []):
        if sheet['properties']['title'] == 'n8n':
            n8n_sheet = sheet
            break
    
    if not n8n_sheet:
        print("❌ n8n tab not found")
        return
    
    print(f"\n✅ Found n8n tab (Sheet ID: {n8n_sheet['properties']['sheetId']})\n")
    
    # Check for conditional format rules
    conditional_rules = n8n_sheet.get('conditionalFormats', [])
    
    if not conditional_rules:
        print("📋 NO conditional formatting rules found on n8n tab")
        print("   (This is actually good - means it's clean!)")
    else:
        print(f"📋 Found {len(conditional_rules)} conditional formatting rules:\n")
        
        for i, rule in enumerate(conditional_rules, 1):
            print(f"Rule #{i}:")
            
            # Get ranges
            ranges = rule.get('ranges', [])
            for r in ranges:
                start_row = r.get('startRowIndex', 0)
                end_row = r.get('endRowIndex', 'unlimited')
                start_col = r.get('startColumnIndex', 0)
                end_col = r.get('endColumnIndex', 'unlimited')
                
                # Convert column indices to letters
                start_col_letter = chr(65 + start_col) if start_col < 26 else 'Z+'
                end_col_letter = chr(65 + end_col - 1) if end_col < 26 else 'Z+'
                
                print(f"   Range: {start_col_letter}{start_row+1}:{end_col_letter}{end_row}")
                print(f"   (Rows {start_row+1} to {end_row}, Columns {start_col_letter} to {end_col_letter})")
            
            # Get rule type
            if 'booleanRule' in rule:
                condition_type = rule['booleanRule']['condition'].get('type', 'UNKNOWN')
                values = rule['booleanRule']['condition'].get('values', [])
                print(f"   Condition: {condition_type}")
                if values:
                    print(f"   Values: {[v.get('userEnteredValue') for v in values]}")
                
                if 'format' in rule['booleanRule']:
                    bg_color = rule['booleanRule']['format'].get('backgroundColor')
                    if bg_color:
                        print(f"   Background Color: RGB({bg_color.get('red', 0)}, {bg_color.get('green', 0)}, {bg_color.get('blue', 0)})")
            
            print()
    
    # Also check sheet properties
    print("\n" + "="*80)
    print("  n8n TAB PROPERTIES")
    print("="*80)
    props = n8n_sheet['properties']
    grid_props = props.get('gridProperties', {})
    
    print(f"\nTab Name: {props.get('title')}")
    print(f"Sheet ID: {props.get('sheetId')}")
    print(f"Row Count: {grid_props.get('rowCount', 'unknown')}")
    print(f"Column Count: {grid_props.get('columnCount', 'unknown')}")
    print(f"Frozen Rows: {grid_props.get('frozenRowCount', 0)}")
    print(f"Frozen Columns: {grid_props.get('frozenColumnCount', 0)}")
    
    print("\n" + "="*80)
    print("  ANALYSIS COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    check_conditional_formatting()

