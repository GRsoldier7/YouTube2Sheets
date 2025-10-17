"""
Spreadsheet Manager Service
Manages multiple Google Sheets spreadsheets with friendly names and automatic access validation.
Following @PolyChronos-Omega.md framework and @QualityMandate.md standards
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.services.sheets_service import SheetsService, SheetsConfig


@dataclass
class SpreadsheetInfo:
    """Information about a spreadsheet."""
    name: str
    url: str
    id: str
    is_default: bool = False


class SpreadsheetManager:
    """Manages multiple Google Sheets spreadsheets."""
    
    def __init__(self, config_file: str = "spreadsheets.json", service_account_file: str = ""):
        """Initialize the spreadsheet manager."""
        self.config_file = Path(config_file)
        self.service_account_file = service_account_file
        self.spreadsheets: List[SpreadsheetInfo] = []
        self.last_used: Optional[str] = None
        self._load_spreadsheets()
    
    def _load_spreadsheets(self) -> None:
        """Load spreadsheets from config file."""
        if not self.config_file.exists():
            self._create_default_config()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.spreadsheets = [
                SpreadsheetInfo(
                    name=sheet['name'],
                    url=sheet['url'],
                    id=sheet['id'],
                    is_default=sheet.get('is_default', False)
                )
                for sheet in data.get('spreadsheets', [])
            ]
            self.last_used = data.get('last_used')
            
        except Exception as e:
            print(f"Error loading spreadsheets: {e}")
            self._create_default_config()
    
    def _save_spreadsheets(self) -> None:
        """Save spreadsheets to config file."""
        try:
            data = {
                'spreadsheets': [
                    {
                        'name': sheet.name,
                        'url': sheet.url,
                        'id': sheet.id,
                        'is_default': sheet.is_default
                    }
                    for sheet in self.spreadsheets
                ],
                'last_used': self.last_used
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving spreadsheets: {e}")
    
    def _create_default_config(self) -> None:
        """Create default config with environment variable spreadsheet."""
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        default_url = os.getenv('DEFAULT_SPREADSHEET_URL', '')
        
        if default_url:
            spreadsheet_id = self._extract_spreadsheet_id(default_url)
            if spreadsheet_id:
                self.spreadsheets = [
                    SpreadsheetInfo(
                        name="Default Spreadsheet",
                        url=default_url,
                        id=spreadsheet_id,
                        is_default=True
                    )
                ]
                self.last_used = "Default Spreadsheet"
                self._save_spreadsheets()
    
    def _extract_spreadsheet_id(self, url: str) -> Optional[str]:
        """Extract spreadsheet ID from URL."""
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        return match.group(1) if match else None
    
    def _extract_name_from_sheet(self, spreadsheet_id: str) -> Optional[str]:
        """Extract friendly name from spreadsheet title (part after underscore)."""
        try:
            sheets_config = SheetsConfig(
                service_account_file=self.service_account_file,
                spreadsheet_id=spreadsheet_id
            )
            sheets_service = SheetsService(sheets_config)
            
            # Get spreadsheet metadata
            spreadsheet = sheets_service.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            # Extract title
            title = spreadsheet.get('properties', {}).get('title', '')
            
            # Extract part after underscore
            if '_' in title:
                return title.split('_', 1)[1].strip()
            else:
                return title.strip()
                
        except Exception as e:
            print(f"Error extracting name from sheet: {e}")
            return None
    
    def add_spreadsheet(self, name: str, url: str, auto_extract_name: bool = False) -> bool:
        """Add a new spreadsheet with validation."""
        # Validate URL format
        spreadsheet_id = self._extract_spreadsheet_id(url)
        if not spreadsheet_id:
            raise ValueError("Invalid spreadsheet URL format")
        
        # Auto-extract name if requested
        if auto_extract_name:
            extracted_name = self._extract_name_from_sheet(spreadsheet_id)
            if extracted_name:
                name = extracted_name
            else:
                raise ValueError("Could not extract name from spreadsheet title")
        
        # Check for duplicate names
        if any(sheet.name.lower() == name.lower() for sheet in self.spreadsheets):
            raise ValueError(f"Spreadsheet with name '{name}' already exists")
        
        # Validate service account access
        if not self._validate_spreadsheet_access(spreadsheet_id):
            raise ValueError("Service account does not have access to this spreadsheet")
        
        # Add spreadsheet
        new_sheet = SpreadsheetInfo(
            name=name,
            url=url,
            id=spreadsheet_id,
            is_default=False
        )
        
        self.spreadsheets.append(new_sheet)
        self.last_used = name
        self._save_spreadsheets()
        
        return True
    
    def _validate_spreadsheet_access(self, spreadsheet_id: str) -> bool:
        """Validate that service account has access to the spreadsheet."""
        if not self.service_account_file:
            return False
        
        try:
            sheets_config = SheetsConfig(
                service_account_file=self.service_account_file,
                spreadsheet_id=spreadsheet_id
            )
            sheets_service = SheetsService(sheets_config)
            return sheets_service.verify_access()
        except Exception as e:
            print(f"Error validating spreadsheet access: {e}")
            return False
    
    def get_spreadsheets(self) -> List[SpreadsheetInfo]:
        """Get list of all spreadsheets."""
        return self.spreadsheets.copy()
    
    def get_spreadsheet_by_name(self, name: str) -> Optional[SpreadsheetInfo]:
        """Get specific spreadsheet by name."""
        for sheet in self.spreadsheets:
            if sheet.name == name:
                return sheet
        return None
    
    def get_spreadsheet_names(self) -> List[str]:
        """Get list of spreadsheet names for dropdown."""
        return [sheet.name for sheet in self.spreadsheets]
    
    def remove_spreadsheet(self, name: str) -> bool:
        """Remove spreadsheet from list."""
        original_count = len(self.spreadsheets)
        self.spreadsheets = [sheet for sheet in self.spreadsheets if sheet.name != name]
        
        if len(self.spreadsheets) < original_count:
            # If we removed the last used, set to first available
            if self.last_used == name:
                self.last_used = self.spreadsheets[0].name if self.spreadsheets else None
            self._save_spreadsheets()
            return True
        
        return False
    
    def set_default_spreadsheet(self, name: str) -> bool:
        """Set a spreadsheet as default."""
        for sheet in self.spreadsheets:
            sheet.is_default = (sheet.name == name)
        
        self.last_used = name
        self._save_spreadsheets()
        return True
    
    def get_default_spreadsheet(self) -> Optional[SpreadsheetInfo]:
        """Get the default spreadsheet."""
        for sheet in self.spreadsheets:
            if sheet.is_default:
                return sheet
        
        # If no default set, return first one
        return self.spreadsheets[0] if self.spreadsheets else None
    
    def get_last_used_spreadsheet(self) -> Optional[SpreadsheetInfo]:
        """Get the last used spreadsheet."""
        if self.last_used:
            return self.get_spreadsheet_by_name(self.last_used)
        return self.get_default_spreadsheet()

