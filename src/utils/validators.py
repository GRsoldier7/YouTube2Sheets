"""
Pre-flight Validation System
Validates all inputs before sync starts to prevent runtime errors
"""

from typing import List, Tuple, Optional
import re
from src.services.sheets_service import SheetsService, SheetsConfig
from src.services.youtube_service import YouTubeService, YouTubeConfig
from src.backend.exceptions import ValidationError

class SyncValidator:
    """Validates all sync inputs before processing."""
    
    def __init__(self, youtube_api_key: str, service_account_file: str):
        self.youtube_api_key = youtube_api_key
        self.service_account_file = service_account_file
        self._youtube_service = None
        self._sheets_service = None
    
    def _get_youtube_service(self) -> YouTubeService:
        """Get YouTube service instance."""
        if not self._youtube_service:
            config = YouTubeConfig(api_key=self.youtube_api_key)
            self._youtube_service = YouTubeService(config)
        return self._youtube_service
    
    def _get_sheets_service(self, spreadsheet_id: str) -> SheetsService:
        """Get Sheets service instance."""
        if not self._sheets_service:
            config = SheetsConfig(
                service_account_file=self.service_account_file,
                spreadsheet_id=spreadsheet_id
            )
            self._sheets_service = SheetsService(config)
        return self._sheets_service
    
    def validate_spreadsheet(self, spreadsheet_id: str) -> Tuple[bool, str]:
        """Validate spreadsheet access and permissions."""
        try:
            if not spreadsheet_id or not spreadsheet_id.strip():
                return False, "Spreadsheet ID is required"
            
            # Validate ID format
            if not re.match(r'^[a-zA-Z0-9-_]+$', spreadsheet_id):
                return False, "Invalid spreadsheet ID format"
            
            # Test access
            sheets_service = self._get_sheets_service(spreadsheet_id)
            if not sheets_service.verify_access():
                return False, "Service account does not have access to this spreadsheet"
            
            return True, "Spreadsheet access verified"
            
        except Exception as e:
            return False, f"Error validating spreadsheet: {str(e)}"
    
    def validate_tab_name(self, tab_name: str) -> Tuple[bool, str]:
        """Validate tab name."""
        try:
            if not tab_name or not tab_name.strip():
                return False, "Tab name is required"
            
            tab_name = tab_name.strip()
            
            # Check for reserved names
            reserved_names = ['ranking', 'data', 'summary', 'temp']
            if tab_name.lower() in reserved_names:
                return False, f"'{tab_name}' is a reserved name. Please choose a different name."
            
            # Check for invalid characters
            if not re.match(r'^[a-zA-Z0-9_\s-]+$', tab_name):
                return False, "Tab name contains invalid characters. Use only letters, numbers, spaces, hyphens, and underscores."
            
            # Check length
            if len(tab_name) > 50:
                return False, "Tab name is too long. Maximum 50 characters."
            
            return True, "Tab name is valid"
            
        except Exception as e:
            return False, f"Error validating tab name: {str(e)}"
    
    def validate_channels(self, channels: List[str]) -> Tuple[bool, str]:
        """Validate channel list."""
        try:
            if not channels:
                return False, "At least one channel is required"
            
            if len(channels) > 100:
                return False, "Too many channels. Maximum 100 channels per sync."
            
            # Validate each channel format
            for i, channel in enumerate(channels):
                if not channel or not channel.strip():
                    return False, f"Channel {i+1} is empty"
                
                channel = channel.strip()
                
                # Check if it looks like a valid channel identifier
                if not (channel.startswith('@') or channel.startswith('UC') or 'youtube.com' in channel):
                    return False, f"Channel {i+1} '{channel}' doesn't look like a valid YouTube channel"
            
            return True, f"Validated {len(channels)} channels"
            
        except Exception as e:
            return False, f"Error validating channels: {str(e)}"
    
    def validate_api_access(self) -> Tuple[bool, str]:
        """Validate API access."""
        try:
            # Test YouTube API
            youtube_service = self._get_youtube_service()
            # Try a simple API call
            test_channels = youtube_service.get_channel_videos("@TechTFQ", max_results=1)
            if not test_channels:
                return False, "YouTube API returned no data. Check API key and quota."
            
            return True, "API access verified"
            
        except Exception as e:
            return False, f"Error validating API access: {str(e)}"
    
    def validate_min_duration(self, min_duration: Optional[int]) -> Tuple[bool, str]:
        """Validate minimum duration setting."""
        try:
            if min_duration is None:
                return True, "No minimum duration set"
            
            if not isinstance(min_duration, int):
                return False, "Minimum duration must be a number"
            
            if min_duration < 0:
                return False, "Minimum duration cannot be negative"
            
            if min_duration > 3600:  # 1 hour
                return False, "Minimum duration too high. Maximum 3600 seconds (1 hour)."
            
            return True, f"Minimum duration set to {min_duration} seconds"
            
        except Exception as e:
            return False, f"Error validating minimum duration: {str(e)}"
    
    def validate_keywords(self, keywords: List[str]) -> Tuple[bool, str]:
        """Validate keyword filter."""
        try:
            if not keywords:
                return True, "No keyword filter set"
            
            if len(keywords) > 20:
                return False, "Too many keywords. Maximum 20 keywords."
            
            for i, keyword in enumerate(keywords):
                if not keyword or not keyword.strip():
                    return False, f"Keyword {i+1} is empty"
                
                if len(keyword.strip()) > 50:
                    return False, f"Keyword {i+1} is too long. Maximum 50 characters."
            
            return True, f"Validated {len(keywords)} keywords"
            
        except Exception as e:
            return False, f"Error validating keywords: {str(e)}"
    
    def validate_all(self, 
                    spreadsheet_id: str, 
                    tab_name: str, 
                    channels: List[str], 
                    min_duration: Optional[int] = None,
                    keywords: List[str] = None) -> List[str]:
        """Validate all inputs and return list of errors."""
        errors = []
        
        # Validate each component
        valid, msg = self.validate_spreadsheet(spreadsheet_id)
        if not valid:
            errors.append(f"Spreadsheet: {msg}")
        
        valid, msg = self.validate_tab_name(tab_name)
        if not valid:
            errors.append(f"Tab: {msg}")
        
        valid, msg = self.validate_channels(channels)
        if not valid:
            errors.append(f"Channels: {msg}")
        
        valid, msg = self.validate_api_access()
        if not valid:
            errors.append(f"API: {msg}")
        
        valid, msg = self.validate_min_duration(min_duration)
        if not valid:
            errors.append(f"Duration: {msg}")
        
        if keywords:
            valid, msg = self.validate_keywords(keywords)
            if not valid:
                errors.append(f"Keywords: {msg}")
        
        return errors
