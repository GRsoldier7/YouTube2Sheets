"""
Batch Google Sheets writer for YouTube2Sheets.
Handles efficient batch writing to Google Sheets with proper formatting.
"""

from typing import List, Dict, Any, Optional
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)


class BatchSheetsWriter:
    """Efficient batch writer for Google Sheets."""
    
    def __init__(self, credentials_file: str):
        """
        Initialize the batch sheets writer.
        
        Args:
            credentials_file: Path to Google service account JSON file
        """
        self.credentials_file = credentials_file
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self) -> None:
        """Initialize Google Sheets service."""
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("Google Sheets service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets service: {e}")
            raise
    
    def write_batch(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> bool:
        """
        Write a batch of values to Google Sheets.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            range_name: Range to write to (e.g., 'Sheet1!A1:Z100')
            values: List of rows to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            body = {'values': values}
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            updated_cells = result.get('updatedCells', 0)
            logger.info(f"Successfully updated {updated_cells} cells in {range_name}")
            return True
            
        except HttpError as e:
            logger.error(f"Failed to write batch to Google Sheets: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error writing batch: {e}")
            return False
    
    def append_batch(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> bool:
        """
        Append a batch of values to Google Sheets.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            range_name: Range to append to (e.g., 'Sheet1!A:Z')
            values: List of rows to append
            
        Returns:
            True if successful, False otherwise
        """
        try:
            body = {'values': values}
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            updated_cells = result.get('updatedCells', 0)
            logger.info(f"Successfully appended {updated_cells} cells to {range_name}")
            return True
            
        except HttpError as e:
            logger.error(f"Failed to append batch to Google Sheets: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error appending batch: {e}")
            return False
    
    def format_as_table(self, spreadsheet_id: str, range_name: str) -> bool:
        """
        Format a range as a table with headers.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            range_name: Range to format
            
        Returns:
            True if successful, False otherwise
        """
        try:
            requests = [{
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': 0,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 12  # Adjust based on your columns
                    }
                }
            }, {
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': 12
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
                            'textFormat': {
                                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            }]
            
            body = {'requests': requests}
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            logger.info(f"Successfully formatted {range_name} as table")
            return True
            
        except HttpError as e:
            logger.error(f"Failed to format table: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error formatting table: {e}")
            return False
