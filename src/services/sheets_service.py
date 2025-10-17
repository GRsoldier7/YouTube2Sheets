"""
Google Sheets Service
Handles all Google Sheets API interactions
Following @PolyChronos-Omega.md framework and @QualityMandate.md standards
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError
from src.domain.models import SheetsConfig


class SheetsService:
    """Service for Google Sheets operations."""
    
    def __init__(self, config: SheetsConfig):
        """Initialize the Sheets service."""
        self.config = config
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the Google Sheets service."""
        try:
            # Set up credentials
            credentials = Credentials.from_service_account_file(
                self.config.service_account_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=credentials)
            print("Google Sheets service initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Google Sheets service: {e}")
            self.service = None
    
    def create_sheet_tab(self, tab_name: str) -> bool:
        """Create a new sheet tab with retry logic."""
        if not self.service:
            return False
        
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                request_body = {
                    'requests': [{
                        'addSheet': {
                            'properties': {
                                'title': tab_name
                            }
                        }
                    }]
                }
                
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.config.spreadsheet_id,
                    body=request_body
                ).execute()
                
                print(f"[OK] Created sheet tab: {tab_name}")
                return True
                
            except HttpError as e:
                error_message = str(e)
                if "10000000 cells" in error_message:
                    print(f"Error creating sheet tab: Spreadsheet has reached the 10 million cell limit. Cannot create new tabs.")
                    return False
                elif "already exists" in error_message:
                    print(f"[WARN] Sheet tab '{tab_name}' already exists")
                    return True  # Consider this a success
                elif e.resp.status == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        print(f"[WARN] Rate limited, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        print(f"[ERROR] Rate limit exceeded after {max_retries} attempts")
                        return False
                else:
                    print(f"Error creating sheet tab: {e}")
                    return False
            except Exception as e:
                error_msg = str(e)
                if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                    if attempt < max_retries - 1:
                        print(f"[WARN] Timeout, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        print(f"[ERROR] Timeout after {max_retries} attempts: {e}")
                        return False
                else:
                    print(f"Unexpected error creating sheet tab: {e}")
                    return False
        
        return False
    
    def write_data(self, tab_name: str, data: List[List[str]]) -> bool:
        """Write data to a sheet tab with proper formatting."""
        if not self.service or not data:
            return False
        
        try:
            # Prepare data for batch write - match existing table structure exactly
            values = []
            
            # Add headers ONLY if writing to empty sheet (first write)
            # Check if we need headers by trying to read first row
            should_add_headers = False
            try:
                existing_data = self.service.spreadsheets().values().get(
                    spreadsheetId=self.config.spreadsheet_id,
                    range=f"{tab_name}!A1:L1"
                ).execute()
                if not existing_data.get('values'):
                    should_add_headers = True
            except:
                should_add_headers = True
            
            if should_add_headers and len(data) > 0:
                # EXACT n8n tab headers
                headers = [
                    'ChannelID',         # Column A: Video ID (matches n8n tab exactly)
                    'YT Channel',        # Column B: Channel Name
                    'Date of Video',     # Column C: Publish Date (M/D/YYYY format)
                    'Short_Long',        # Column D: Video Type
                    'Video Length',      # Column E: Duration (H:MM:SS format)
                    'Video Title',       # Column F: Title
                    'Video Link',        # Column G: URL
                    'Views',             # Column H: View Count (no comma if <1000)
                    'Likes',             # Column I: Like Count (no comma if <1000)
                    'Comments',          # Column J: Comment Count (no comma if <1000)
                    'NotebookLM',        # Column K: Text "FALSE" (not checkbox symbol)
                    'Date Added'         # Column L: Timestamp (MM/DD/YYYY H:MM:SS 24hr)
                ]
                values.append(headers)
            
            # Add video data - EXACT n8n tab format
            for video in data:
                if isinstance(video, dict):
                    # Parse duration
                    duration_seconds = video.get('duration', 0)
                    
                    # Format duration: ALWAYS H:MM:SS format (matching n8n exactly)
                    hours = duration_seconds // 3600
                    minutes = (duration_seconds % 3600) // 60
                    seconds = duration_seconds % 60
                    duration_formatted = f"{hours}:{minutes:02d}:{seconds:02d}"
                    
                    # Format date: M/D/YYYY format (matching n8n exactly)
                    if video.get('published_at'):
                        from datetime import datetime as dt
                        pub_date = dt.fromisoformat(video.get('published_at').replace('Z', '+00:00'))
                        # Format as M/D/YYYY (remove leading zeros)
                        formatted = pub_date.strftime('%m/%d/%Y')
                        parts = formatted.split('/')
                        published_date = f"{int(parts[0])}/{int(parts[1])}/{parts[2]}"
                    else:
                        published_date = ''
                    
                    # Format numbers: NO commas for <1000, commas for >=1000 (matching n8n exactly)
                    views = video.get('view_count', 0)
                    views_formatted = f"{views:,}" if views >= 1000 else str(views)
                    
                    likes = video.get('like_count', 0)
                    likes_formatted = f"{likes:,}" if likes >= 1000 else str(likes)
                    
                    comments = video.get('comment_count', 0)
                    comments_formatted = f"{comments:,}" if comments >= 1000 else str(comments)
                    
                    # Extract video ID from URL or use 'id' field
                    video_id = video.get('id', '')
                    if not video_id and video.get('url'):
                        # Extract from URL: https://youtube.com/watch?v=VIDEO_ID
                        url = video.get('url', '')
                        if 'watch?v=' in url:
                            video_id = url.split('watch?v=')[1].split('&')[0]
                    
                    row = [
                        video_id,                                        # Column A: Video ID (NOT Channel ID!)
                        video.get('channel_title', ''),                  # Column B: YT Channel
                        published_date,                                   # Column C: Date of Video (M/D/YYYY)
                        'Short' if duration_seconds < 60 else 'Long',    # Column D: Short_Long
                        duration_formatted,                               # Column E: Video Length (H:MM:SS)
                        video.get('title', ''),                           # Column F: Video Title
                        video.get('url', ''),                             # Column G: Video Link
                        views_formatted,                                  # Column H: Views (no comma if <1000)
                        likes_formatted,                                  # Column I: Likes (no comma if <1000)
                        comments_formatted,                               # Column J: Comments (no comma if <1000)
                        'FALSE',                                          # Column K: NotebookLM (text "FALSE")
                        datetime.now().strftime('%m/%d/%Y %H:%M:%S').lstrip('0').replace('/0', '/')  # Column L: Date Added (MM/DD/YYYY H:MM:SS 24hr)
                    ]
                else:
                    # Handle list data
                    row = video if isinstance(video, list) else [str(video)]
                    # Ensure row has correct number of columns
                    while len(row) < 12:
                        row.append('')
                    row = row[:12]  # Truncate if too long
                
                values.append(row)
            
            # Batch write to sheet
            range_name = f"{tab_name}!A:L"
            body = {'values': values}
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.config.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
            
        except HttpError as e:
            print(f"Error writing to sheet: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error writing to sheet: {e}")
            return False
    
    def read_data(self, tab_name: str, range_name: str = "A1:Z1000") -> List[List[str]]:
        """Read data from a sheet tab."""
        if not self.service:
            return []
        
        try:
            full_range = f"{tab_name}!{range_name}"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.config.spreadsheet_id,
                range=full_range
            ).execute()
            
            values = result.get('values', [])
            return values
            
        except HttpError as e:
            print(f"Error reading data from sheet: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error reading data from sheet: {e}")
            return []
    
    def create_table_structure(self, tab_name: str, num_rows: int = 10000) -> bool:
        """Create an actual Google Sheets TABLE (Format → Convert to table)."""
        if not self.service:
            return False
        
        try:
            # Get the sheet ID for the tab
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.config.spreadsheet_id
            ).execute()
            
            sheet_id = None
            for sheet in spreadsheet.get('sheets', []):
                if sheet['properties']['title'] == tab_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            if sheet_id is None:
                print(f"Sheet tab '{tab_name}' not found for table creation")
                return False
            
            # Define column properties with types
            column_properties = [
                {'columnName': 'ChannelID'},  # Column A - Video ID (text)
                {'columnIndex': 1, 'columnName': 'YT Channel'},  # Column B (text)
                {'columnIndex': 2, 'columnName': 'Date of Video', 'columnType': 'DATE'},  # Column C (date)
                {'columnIndex': 3, 'columnName': 'Short_Long'},  # Column D (text)
                {'columnIndex': 4, 'columnName': 'Video Length'},  # Column E (text/duration)
                {'columnIndex': 5, 'columnName': 'Video Title'},  # Column F (text)
                {'columnIndex': 6, 'columnName': 'Video Link'},  # Column G (text/URL)
                {'columnIndex': 7, 'columnName': 'Views', 'columnType': 'DOUBLE'},  # Column H (number)
                {'columnIndex': 8, 'columnName': 'Likes'},  # Column I (number/text for N/A)
                {'columnIndex': 9, 'columnName': 'Comments'},  # Column J (number)
                {'columnIndex': 10, 'columnName': 'NotebookLM', 'columnType': 'BOOLEAN'},  # Column K (boolean)
                {'columnIndex': 11, 'columnName': 'Date Added'}  # Column L (datetime text)
            ]
            
            # Create the actual table using AddTableRequest
            requests = [
                {
                    'addTable': {
                        'table': {
                            'name': tab_name,  # Table name = Tab name
                            'range': {
                                'sheetId': sheet_id,
                                'startRowIndex': 0,
                                'endRowIndex': num_rows,
                                'startColumnIndex': 0,
                                'endColumnIndex': 12
                            },
                            'rowsProperties': {
                                'headerColorStyle': {
                                    'rgbColor': {
                                        'red': 0.20784314,
                                        'green': 0.40784314,
                                        'blue': 0.32941177
                                    }
                                },
                                'firstBandColorStyle': {
                                    'rgbColor': {
                                        'red': 1.0,
                                        'green': 1.0,
                                        'blue': 1.0
                                    }
                                },
                                'secondBandColorStyle': {
                                    'rgbColor': {
                                        'red': 0.9647059,
                                        'green': 0.972549,
                                        'blue': 0.9764706
                                    }
                                }
                            },
                            'columnProperties': column_properties
                        }
                    }
                }
            ]
            
            # Apply table
            body = {'requests': requests}
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.config.spreadsheet_id,
                body=body
            ).execute()
            
            print(f"[OK] Google Sheets TABLE created: '{tab_name}' (with column types and banding)")
            return True
            
        except Exception as e:
            # If table already exists, that's okay
            if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                print(f"[WARN]  Table '{tab_name}' already exists (this is okay)")
                return True
            print(f"Error creating table: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def apply_conditional_formatting(self, tab_name: str) -> bool:
        """Apply conditional formatting to match EXACT n8n tab format."""
        if not self.service:
            return False
        
        try:
            # Get the sheet ID for the tab
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.config.spreadsheet_id
            ).execute()
            
            sheet_id = None
            for sheet in spreadsheet.get('sheets', []):
                if sheet['properties']['title'] == tab_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            if sheet_id is None:
                print(f"Sheet tab '{tab_name}' not found")
                return False
            
            # EXACT n8n tab conditional formatting rules
            # Apply to ENTIRE COLUMNS (row 2 to 10000) to avoid bloat
            requests = [
                # Rule 1: Column A-B - Red if NotebookLM is checked
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 10000, 'startColumnIndex': 0, 'endColumnIndex': 2}],
                            'booleanRule': {
                                'condition': {
                                    'type': 'CUSTOM_FORMULA',
                                    'values': [{'userEnteredValue': '=$K2'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 1.0, 'green': 0.0, 'blue': 0.0}
                                }
                            }
                        },
                        'index': 0
                    }
                },
                # Rule 2: Column G (Video Link) - Red if NotebookLM is checked
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 10000, 'startColumnIndex': 6, 'endColumnIndex': 7}],
                            'booleanRule': {
                                'condition': {
                                    'type': 'CUSTOM_FORMULA',
                                    'values': [{'userEnteredValue': '=$K2'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 1.0, 'green': 0.0, 'blue': 0.0}
                                }
                            }
                        },
                        'index': 1
                    }
                },
                # Rule 3: Column F (Title) - Red if NotebookLM is checked
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 10000, 'startColumnIndex': 5, 'endColumnIndex': 6}],
                            'booleanRule': {
                                'condition': {
                                    'type': 'CUSTOM_FORMULA',
                                    'values': [{'userEnteredValue': '=$K2'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 1.0, 'green': 0.0, 'blue': 0.0}
                                }
                            }
                        },
                        'index': 2
                    }
                },
                # Rule 4: Column K (NotebookLM) - Red if checked
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 10000, 'startColumnIndex': 10, 'endColumnIndex': 11}],
                            'booleanRule': {
                                'condition': {
                                    'type': 'CUSTOM_FORMULA',
                                    'values': [{'userEnteredValue': '=$K2'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 1.0, 'green': 0.0, 'blue': 0.0}
                                }
                            }
                        },
                        'index': 3
                    }
                },
                # Rule 5: Column C (Date) - Purple for 2026
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 10000, 'startColumnIndex': 2, 'endColumnIndex': 3}],
                            'booleanRule': {
                                'condition': {
                                    'type': 'CUSTOM_FORMULA',
                                    'values': [{'userEnteredValue': '=YEAR($C2)=2026'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 1.0, 'green': 0.6, 'blue': 1.0}
                                }
                            }
                        },
                        'index': 4
                    }
                },
                # Rule 6: Column C (Date) - Green for 2025
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 10000, 'startColumnIndex': 2, 'endColumnIndex': 3}],
                            'booleanRule': {
                                'condition': {
                                    'type': 'CUSTOM_FORMULA',
                                    'values': [{'userEnteredValue': '=YEAR($C2)=2025'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 0.0, 'green': 0.49803922, 'blue': 0.0}
                                }
                            }
                        },
                        'index': 5
                    }
                },
                # Rule 7: Column C (Date) - Light purple for 2024
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 10000, 'startColumnIndex': 2, 'endColumnIndex': 3}],
                            'booleanRule': {
                                'condition': {
                                    'type': 'CUSTOM_FORMULA',
                                    'values': [{'userEnteredValue': '=YEAR($C2)=2024'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 0.8, 'green': 0.6, 'blue': 1.0}
                                }
                            }
                        },
                        'index': 6
                    }
                },
                # Rule 8: Column C (Date) - Orange for 2023
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 10000, 'startColumnIndex': 2, 'endColumnIndex': 3}],
                            'booleanRule': {
                                'condition': {
                                    'type': 'CUSTOM_FORMULA',
                                    'values': [{'userEnteredValue': '=YEAR($C2)=2023'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 1.0, 'green': 0.8, 'blue': 0.6}
                                }
                            }
                        },
                        'index': 7
                    }
                },
                # Rule 9: Column E (Duration) - Blue if "Long"
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 10000, 'startColumnIndex': 4, 'endColumnIndex': 5}],
                            'booleanRule': {
                                'condition': {
                                    'type': 'CUSTOM_FORMULA',
                                    'values': [{'userEnteredValue': '=$D2="Long"'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 0.8, 'green': 0.8980392, 'blue': 1.0}
                                }
                            }
                        },
                        'index': 8
                    }
                },
                # Rule 10: Column E (Duration) - Pink if "Short"
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 10000, 'startColumnIndex': 4, 'endColumnIndex': 5}],
                            'booleanRule': {
                                'condition': {
                                    'type': 'CUSTOM_FORMULA',
                                    'values': [{'userEnteredValue': '=$D2="Short"'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 1.0, 'green': 0.8, 'blue': 0.8}
                                }
                            }
                        },
                        'index': 9
                    }
                },
                # Rule 11: Column D (Short_Long) - Blue if "Long"
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 10000, 'startColumnIndex': 3, 'endColumnIndex': 4}],
                            'booleanRule': {
                                'condition': {
                                    'type': 'TEXT_EQ',
                                    'values': [{'userEnteredValue': 'Long'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 0.8, 'green': 0.8980392, 'blue': 1.0}
                                }
                            }
                        },
                        'index': 10
                    }
                },
                # Rule 12: Column D (Short_Long) - Pink if "Short"
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 10000, 'startColumnIndex': 3, 'endColumnIndex': 4}],
                            'booleanRule': {
                                'condition': {
                                    'type': 'TEXT_EQ',
                                    'values': [{'userEnteredValue': 'Short'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 1.0, 'green': 0.8, 'blue': 0.8}
                                }
                            }
                        },
                        'index': 11
                    }
                }
            ]
            
            # Apply conditional formatting
            body = {'requests': requests}
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.config.spreadsheet_id,
                body=body
            ).execute()
            
            print(f"[OK] Conditional formatting applied to '{tab_name}' (12 COLUMN-WIDE rules, matching n8n exactly)")
            return True
            
        except HttpError as e:
            print(f"Error applying conditional formatting: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error applying conditional formatting: {e}")
            return False


    def write_videos_to_sheet(self, tab_name: str, videos: List[Dict[str, Any]]) -> bool:
        """Write videos to a sheet tab."""
        if not self.service or not videos:
            return False
        
        try:
            # Prepare data for batch write
            values = []
            
            # Add headers if this is the first write - match existing table structure
            if len(videos) > 0:
                headers = [
                    'PERMISSION_TEST', 'Testing write permission', 'Test', '100', '50',
                    '2025-01-27', 'Video Link', 'Views', 'Likes', 'Comments', 'NotebookLM', 'Date Added'
                ]
                values.append(headers)
            
            # Add video data - match existing table structure
            for video in videos:
                # Map to existing table structure
                duration_seconds = video.get('duration', 0)
                duration_formatted = f"{duration_seconds//60}:{duration_seconds%60:02d}" if duration_seconds > 0 else "0:00"
                
                row = [
                    video.get('id', ''),  # Column A: Video ID
                    video.get('channel_title', ''),  # Column B: Channel Title
                    video.get('published_at', '').split('T')[0] if video.get('published_at') else '',  # Column C: Date
                    'Long' if duration_seconds > 300 else 'Short',  # Column D: Duration Type
                    duration_formatted,  # Column E: Duration
                    video.get('title', ''),  # Column F: Title
                    f"https://youtube.com/watch?v={video.get('id', '')}",  # Column G: Video Link
                    str(video.get('view_count', 0)),  # Column H: Views
                    str(video.get('like_count', 0)),  # Column I: Likes
                    str(video.get('comment_count', 0)),  # Column J: Comments
                    'FALSE',  # Column K: NotebookLM
                    datetime.now().strftime('%m/%d/%Y %H:%M:%S')  # Column L: Date Added
                ]
                values.append(row)
            
            # Batch write to sheet
            range_name = f"{tab_name}!A:L"
            body = {'values': values}
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.config.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
            
        except HttpError as e:
            print(f"Error writing to sheet: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error writing to sheet: {e}")
            return False

    def get_existing_tabs(self) -> List[str]:
        """Get list of existing tab names in the spreadsheet."""
        if not self.service:
            return []
        
        try:
            # Get spreadsheet metadata
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.config.spreadsheet_id
            ).execute()
            
            # Extract tab names
            tab_names = []
            for sheet in spreadsheet.get('sheets', []):
                properties = sheet.get('properties', {})
                title = properties.get('title', '')
                if title:
                    tab_names.append(title)
            
            return tab_names
            
        except Exception as e:
            print(f"Error getting existing tabs: {e}")
            return []
    
    def verify_access(self) -> bool:
        """Verify service account has access to the spreadsheet."""
        if not self.service:
            return False
        
        try:
            # Try to get spreadsheet metadata
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.config.spreadsheet_id
            ).execute()
            return True
        except HttpError as e:
            print(f"Access denied to spreadsheet: {e}")
            return False
        except Exception as e:
            print(f"Error verifying access: {e}")
            return False

    def is_at_cell_limit(self) -> bool:
        """Check if the spreadsheet is at the 10 million cell limit."""
        if not self.service:
            return False
        
        try:
            # Get spreadsheet metadata
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.config.spreadsheet_id
            ).execute()
            
            # Count total cells across all sheets
            total_cells = 0
            for sheet in spreadsheet.get('sheets', []):
                properties = sheet.get('properties', {})
                grid_properties = properties.get('gridProperties', {})
                row_count = grid_properties.get('rowCount', 0)
                column_count = grid_properties.get('columnCount', 0)
                total_cells += row_count * column_count
            
            # Check if approaching or at limit (use 9.5M as threshold for safety)
            return total_cells >= 9500000
            
        except Exception as e:
            print(f"Error checking cell limit: {e}")
            return False

    def check_for_duplicates(self, tab_name: str, video_id: str) -> bool:
        """Check if a video ID already exists in the sheet."""
        if not self.service:
            return False
        
        try:
            # Read existing data
            data = self.read_data(tab_name)
            
            if not data or len(data) < 2:  # No data or only headers
                return False
            
            # Check if video ID exists in first column
            for row in data[1:]:  # Skip header row
                if len(row) > 0 and row[0] == video_id:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking for duplicates: {e}")
            return False
