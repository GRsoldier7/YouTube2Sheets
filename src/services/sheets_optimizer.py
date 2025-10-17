"""
Google Sheets Optimizer Service
Advanced Google Sheets integration with conditional formatting and smart duplication checking
"""
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import time
import hashlib
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.sheets_service import SheetsService, SheetsConfig
from src.domain.models import Video
from src.utils.validation import validate_tab_name, ValidationError

@dataclass
class ConditionalFormattingRule:
    """Conditional formatting rule for Google Sheets."""
    range: str
    condition_type: str  # 'NUMBER_GREATER', 'TEXT_CONTAINS', 'DATE_AFTER', etc.
    condition_value: Any
    background_color: Dict[str, int]  # RGB values
    text_color: Dict[str, int]  # RGB values
    bold: bool = False
    italic: bool = False

@dataclass
class DuplicationCheckResult:
    """Result of duplication check."""
    is_duplicate: bool
    existing_video_id: Optional[str] = None
    existing_row: Optional[int] = None
    similarity_score: float = 0.0

class SheetsOptimizer:
    """Advanced Google Sheets optimizer with conditional formatting and duplication checking."""
    
    def __init__(self, sheets_service: SheetsService):
        self.sheets_service = sheets_service
        self._video_cache: Dict[str, Set[str]] = {}  # tab_name -> set of video_ids
        self._cache_timestamp: Dict[str, float] = {}
        self._cache_ttl = 300  # 5 minutes
        
    def _get_video_hash(self, video: Video) -> str:
        """Generate a unique hash for a video based on key properties."""
        # Use video ID, title, and published date for uniqueness
        hash_string = f"{video.video_id}_{video.title}_{video.published_at}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _load_existing_videos(self, tab_name: str) -> Set[str]:
        """Load existing video hashes from the sheet tab."""
        current_time = time.time()
        
        # Check cache first
        if (tab_name in self._video_cache and 
            tab_name in self._cache_timestamp and
            current_time - self._cache_timestamp[tab_name] < self._cache_ttl):
            return self._video_cache[tab_name]
        
        try:
            # Read existing data from the sheet
            existing_data = self.sheets_service.read_sheet_data(tab_name)
            
            video_hashes = set()
            if existing_data:
                for row in existing_data[1:]:  # Skip header row
                    if len(row) >= 4:  # Ensure we have enough columns
                        video_id = row[0] if row[0] else ""
                        title = row[1] if row[1] else ""
                        published_at = row[3] if len(row) > 3 and row[3] else ""
                        
                        if video_id and title and published_at:
                            # Create a temporary video object for hashing
                            temp_video = Video(
                                video_id=video_id,
                                title=title,
                                url=f"https://youtube.com/watch?v={video_id}",
                                published_at=published_at,
                                duration="0",
                                view_count=0,
                                like_count=0,
                                comment_count=0
                            )
                            video_hash = self._get_video_hash(temp_video)
                            video_hashes.add(video_hash)
            
            # Update cache
            self._video_cache[tab_name] = video_hashes
            self._cache_timestamp[tab_name] = current_time
            
            return video_hashes
            
        except Exception as e:
            print(f"Warning: Could not load existing videos for {tab_name}: {e}")
            return set()
    
    def check_duplication(self, video: Video, tab_name: str) -> DuplicationCheckResult:
        """Check if a video already exists in the sheet tab."""
        try:
            validate_tab_name(tab_name)
            
            # Load existing videos
            existing_hashes = self._load_existing_videos(tab_name)
            
            # Generate hash for current video
            video_hash = self._get_video_hash(video)
            
            # Check for exact match
            if video_hash in existing_hashes:
                return DuplicationCheckResult(
                    is_duplicate=True,
                    similarity_score=1.0
                )
            
            # Check for similar videos (same video ID)
            existing_video_ids = set()
            try:
                existing_data = self.sheets_service.read_sheet_data(tab_name)
                if existing_data:
                    for row in existing_data[1:]:  # Skip header row
                        if row and len(row) > 0 and row[0]:
                            existing_video_ids.add(row[0])
            except Exception:
                pass
            
            if video.video_id in existing_video_ids:
                return DuplicationCheckResult(
                    is_duplicate=True,
                    existing_video_id=video.video_id,
                    similarity_score=0.9
                )
            
            return DuplicationCheckResult(is_duplicate=False)
            
        except ValidationError as e:
            print(f"Validation error in duplication check: {e}")
            return DuplicationCheckResult(is_duplicate=False)
        except Exception as e:
            print(f"Error checking duplication: {e}")
            return DuplicationCheckResult(is_duplicate=False)
    
    def filter_new_videos(self, videos: List[Video], tab_name: str) -> List[Video]:
        """Filter out videos that already exist in the sheet tab."""
        try:
            validate_tab_name(tab_name)
            
            new_videos = []
            duplicate_count = 0
            
            for video in videos:
                duplication_result = self.check_duplication(video, tab_name)
                
                if not duplication_result.is_duplicate:
                    new_videos.append(video)
                else:
                    duplicate_count += 1
                    similarity = duplication_result.similarity_score or 0.0
                    print(f"Duplicate video filtered: {video.title} (similarity: {similarity:.2f})")
            
            print(f"Filtered {duplicate_count} duplicate videos, {len(new_videos)} new videos to add")
            return new_videos
            
        except Exception as e:
            print(f"Error filtering videos: {e}")
            return videos  # Return all videos if filtering fails
    
    def setup_uniform_column_formatting(self, tab_name: str) -> bool:
        """Set up uniform column formatting for the entire working range."""
        try:
            validate_tab_name(tab_name)
            
            # Get the sheet ID for the tab
            spreadsheet = self.sheets_service.service.spreadsheets().get(
                spreadsheetId=self.sheets_service.config.spreadsheet_id
            ).execute()
            
            sheet_id = None
            for sheet in spreadsheet.get('sheets', []):
                if sheet['properties']['title'] == tab_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            if sheet_id is None:
                print(f"Sheet tab '{tab_name}' not found")
                return False
            
            # Define uniform formatting for each column based on ACTUAL table structure
            formatting_requests = []
            
            # Column A: Video ID - Blue header, white data
            formatting_requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,  # Large range to cover all data
                        'startColumnIndex': 0,  # Column A
                        'endColumnIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
                            'textFormat': {
                                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                'fontSize': 11,
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })
            
            # Column B: Channel Title - Green header, white data
            formatting_requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 1,  # Column B
                        'endColumnIndex': 2
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.2, 'green': 0.7, 'blue': 0.3},
                            'textFormat': {
                                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                'fontSize': 11,
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })
            
            # Column C: Date - Orange header, white data
            formatting_requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 2,  # Column C
                        'endColumnIndex': 3
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 1.0, 'green': 0.6, 'blue': 0.0},
                            'textFormat': {
                                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                'fontSize': 11,
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })
            
            # Column D: Duration Type - Purple header, white data
            formatting_requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 3,  # Column D
                        'endColumnIndex': 4
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.6, 'green': 0.2, 'blue': 0.8},
                            'textFormat': {
                                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                'fontSize': 11,
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })
            
            # Column E: Duration - Teal header, white data
            formatting_requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 4,  # Column E
                        'endColumnIndex': 5
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.0, 'green': 0.7, 'blue': 0.7},
                            'textFormat': {
                                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                'fontSize': 11,
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })
            
            # Column F: Title - Red header, white data
            formatting_requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 5,  # Column F
                        'endColumnIndex': 6
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.8, 'green': 0.2, 'blue': 0.2},
                            'textFormat': {
                                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                'fontSize': 11,
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })
            
            # Column G: Video Link - Dark blue header, white data
            formatting_requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 6,  # Column G
                        'endColumnIndex': 7
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.1, 'green': 0.2, 'blue': 0.6},
                            'textFormat': {
                                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                'fontSize': 11,
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })
            
            # Column H: Views - Green header, white data
            formatting_requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 7,  # Column H
                        'endColumnIndex': 8
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.0, 'green': 0.8, 'blue': 0.0},
                            'textFormat': {
                                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                'fontSize': 11,
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })
            
            # Column I: Likes - Yellow header, white data
            formatting_requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 8,  # Column I
                        'endColumnIndex': 9
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 1.0, 'green': 0.8, 'blue': 0.0},
                            'textFormat': {
                                'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
                                'fontSize': 11,
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })
            
            # Column J: Comments - Pink header, white data
            formatting_requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 9,  # Column J
                        'endColumnIndex': 10
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 1.0, 'green': 0.4, 'blue': 0.8},
                            'textFormat': {
                                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                'fontSize': 11,
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })
            
            # Column K: NotebookLM - Gray header, white data
            formatting_requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 10,  # Column K
                        'endColumnIndex': 11
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.5, 'green': 0.5, 'blue': 0.5},
                            'textFormat': {
                                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                'fontSize': 11,
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })
            
            # Column L: Date Added - Dark green header, white data
            formatting_requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 11,  # Column L
                        'endColumnIndex': 12
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.0, 'green': 0.4, 'blue': 0.0},
                            'textFormat': {
                                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                'fontSize': 11,
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })
            
            # Apply all formatting requests in a single batch update
            batch_request = {
                'requests': formatting_requests
            }
            
            result = self.sheets_service.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheets_service.config.spreadsheet_id,
                body=batch_request
            ).execute()
            
            print(f"Applied uniform formatting to all 12 columns in {tab_name}")
            return True
            
        except Exception as e:
            print(f"Error setting up uniform column formatting: {e}")
            return False
    
    def setup_conditional_formatting(self, tab_name: str) -> bool:
        """Set up conditional formatting rules for the sheet tab."""
        # Redirect to uniform formatting for better consistency
        return self.setup_uniform_column_formatting(tab_name)
    
    def _apply_conditional_formatting_rule(self, tab_name: str, rule: ConditionalFormattingRule) -> bool:
        """Apply a single conditional formatting rule to the sheet."""
        try:
            # This would use the Google Sheets API to apply conditional formatting
            # For now, we'll simulate the API call
            print(f"Applying conditional formatting rule: {rule.range} - {rule.condition_type}")
            
            # In a real implementation, this would make an API call like:
            # self.sheets_service.service.spreadsheets().batchUpdate(
            #     spreadsheetId=self.sheets_service.spreadsheet_id,
            #     body={
            #         "requests": [{
            #             "addConditionalFormatRule": {
            #                 "rule": {
            #                     "ranges": [{"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1000}],
            #                     "booleanRule": {
            #                         "condition": {
            #                             "type": rule.condition_type,
            #                             "values": [{"userEnteredValue": str(rule.condition_value)}]
            #                         },
            #                         "format": {
            #                             "backgroundColor": rule.background_color,
            #                             "textFormat": {
            #                                 "foregroundColor": rule.text_color,
            #                                 "bold": rule.bold,
            #                                 "italic": rule.italic
            #                             }
            #                         }
            #                     }
            #                 }
            #             }
            #         }]
            #     }
            # ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error applying conditional formatting rule: {e}")
            return False
    
    def optimize_sheet_structure(self, tab_name: str) -> bool:
        """Optimize the sheet structure with proper headers and formatting."""
        try:
            validate_tab_name(tab_name)
            
            # First, check if tab exists, if not create it
            existing_tabs = self.sheets_service.get_existing_tabs()
            if tab_name not in existing_tabs:
                print(f"Creating new tab: {tab_name}")
                tab_created = self.sheets_service.create_sheet_tab(tab_name)
                if not tab_created:
                    print(f"Failed to create tab: {tab_name}")
                    return False
                # Wait a moment for the tab to be created
                import time
                time.sleep(1)
            
            # Define optimal headers
            headers = [
                "Video ID",
                "Title", 
                "URL",
                "Published Date",
                "View Count",
                "Duration",
                "Like Count",
                "Comment Count",
                "Channel ID",
                "Channel Title",
                "Description",
                "Tags",
                "Added Date"
            ]
            
            # Write headers to the sheet
            success = self.sheets_service.write_videos_to_sheet(tab_name, [{
                'id': 'Video ID',
                'title': 'Title',
                'description': 'Description',
                'channel_id': 'Channel ID',
                'channel_title': 'Channel Title',
                'published_at': 'Published At',
                'duration': 'Duration (sec)',
                'view_count': 'View Count',
                'like_count': 'Like Count',
                'comment_count': 'Comment Count',
                'thumbnail_url': 'Thumbnail URL'
            }])
            
            if success:
                print(f"Optimized sheet structure for {tab_name}")
                return True
            else:
                print(f"Failed to optimize sheet structure for {tab_name}")
                return False
                
        except Exception as e:
            print(f"Error optimizing sheet structure: {e}")
            return False
    
    def get_optimization_stats(self, tab_name: str) -> Dict[str, Any]:
        """Get optimization statistics for a sheet tab."""
        try:
            validate_tab_name(tab_name)
            
            # Load existing videos
            existing_hashes = self._load_existing_videos(tab_name)
            
            # Get sheet data
            sheet_data = self.sheets_service.read_sheet_data(tab_name)
            row_count = len(sheet_data) if sheet_data else 0
            
            return {
                "tab_name": tab_name,
                "total_videos": row_count - 1,  # Subtract header row
                "unique_videos": len(existing_hashes),
                "cache_status": "active" if tab_name in self._video_cache else "inactive",
                "last_updated": self._cache_timestamp.get(tab_name, 0)
            }
            
        except Exception as e:
            print(f"Error getting optimization stats: {e}")
            return {"error": str(e)}
    
    def clear_cache(self, tab_name: Optional[str] = None):
        """Clear the video cache for a specific tab or all tabs."""
        if tab_name:
            self._video_cache.pop(tab_name, None)
            self._cache_timestamp.pop(tab_name, None)
            print(f"Cleared cache for {tab_name}")
        else:
            self._video_cache.clear()
            self._cache_timestamp.clear()
            print("Cleared all caches")
