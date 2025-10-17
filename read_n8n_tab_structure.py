"""
Read n8n Tab Structure
======================
Reads the exact structure of the "n8n" tab from Google Sheets to match formatting.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.services.sheets_service import SheetsService, SheetsConfig

def read_n8n_tab():
    """Read and analyze the n8n tab structure."""
    
    # Initialize service
    spreadsheet_url = os.getenv('DEFAULT_SPREADSHEET_URL', '').strip()
    
    # If not in env, try hardcoded
    if not spreadsheet_url or '/spreadsheets/d/' not in spreadsheet_url:
        spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1CIKN4b8L6Awdys5tv4Ht_LirSvHgx0Hscj9MMzBKjZg/edit'
    
    # Extract spreadsheet ID
    if '/spreadsheets/d/' in spreadsheet_url:
        start = spreadsheet_url.find('/spreadsheets/d/') + len('/spreadsheets/d/')
        end = spreadsheet_url.find('/', start)
        if end == -1:
            end = spreadsheet_url.find('?', start)
        if end == -1:
            end = len(spreadsheet_url)
        spreadsheet_id = spreadsheet_url[start:end]
    else:
        print("❌ Invalid spreadsheet URL")
        return
    
    # Get service account file
    service_account = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON', 'credentials/service-account.json')
    
    print(f"Using spreadsheet ID: {spreadsheet_id}")
    print(f"Using service account: {service_account}\n")
    
    config = SheetsConfig(
        service_account_file=service_account,
        spreadsheet_id=spreadsheet_id
    )
    
    service = SheetsService(config)
    
    print("="*80)
    print("  READING 'n8n' TAB STRUCTURE")
    print("="*80)
    
    # Read first 10 rows to see structure
    data = service.read_data('n8n', 'A1:Z10')
    
    if not data:
        print("❌ Could not read n8n tab")
        return
    
    print(f"\n✅ Found {len(data)} rows in n8n tab\n")
    
    # Analyze headers
    if len(data) > 0:
        headers = data[0]
        print("📋 COLUMN HEADERS:")
        print("-" * 80)
        for i, header in enumerate(headers):
            col_letter = chr(65 + i)  # A, B, C, etc.
            print(f"   Column {col_letter}: {header}")
        
        print(f"\n   Total Columns: {len(headers)}")
    
    # Analyze data format
    if len(data) > 1:
        print("\n📊 SAMPLE DATA (Row 2):")
        print("-" * 80)
        sample_row = data[1]
        for i, value in enumerate(sample_row):
            col_letter = chr(65 + i)
            header = headers[i] if i < len(headers) else f"Column {col_letter}"
            print(f"   {header}: {value}")
    
    # Read a few more rows to understand patterns
    if len(data) > 2:
        print("\n📊 ADDITIONAL SAMPLES:")
        print("-" * 80)
        for row_idx in range(2, min(len(data), 5)):
            print(f"\n   Row {row_idx + 1}:")
            row = data[row_idx]
            for i, value in enumerate(row):
                if i < len(headers):
                    print(f"      {headers[i]}: {value}")
    
    # Analyze data types and formats
    print("\n🔍 DATA FORMAT ANALYSIS:")
    print("-" * 80)
    
    if len(data) > 1:
        sample_row = data[1]
        
        # Check for channel ID format
        if len(sample_row) > 0:
            print(f"   Column A format: {sample_row[0]}")
            if sample_row[0].startswith('UC'):
                print("      → YouTube Channel ID format detected")
        
        # Check for date format
        for i, header in enumerate(headers):
            if 'date' in header.lower() or 'published' in header.lower():
                if i < len(sample_row):
                    print(f"   {header} format: {sample_row[i]}")
        
        # Check for number format
        for i, header in enumerate(headers):
            if 'view' in header.lower() or 'like' in header.lower() or 'comment' in header.lower():
                if i < len(sample_row):
                    value = sample_row[i]
                    has_comma = ',' in str(value)
                    print(f"   {header} format: {value} (comma-separated: {has_comma})")
        
        # Check for duration format
        for i, header in enumerate(headers):
            if 'length' in header.lower() or 'duration' in header.lower():
                if i < len(sample_row):
                    print(f"   {header} format: {sample_row[i]}")
        
        # Check for checkbox format
        for i, header in enumerate(headers):
            if 'notebook' in header.lower() or 'checkbox' in header.lower():
                if i < len(sample_row):
                    print(f"   {header} format: {sample_row[i]}")
    
    print("\n" + "="*80)
    print("  ANALYSIS COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    read_n8n_tab()

