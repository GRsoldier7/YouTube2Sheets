"""
Comprehensive Input Validation Utilities
Security-first input validation and sanitization
"""
import re
import logging
from typing import Any, List, Optional, Union
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom validation error."""
    pass

def validate_youtube_channel_id(channel_id: str) -> str:
    """Validate and normalize YouTube channel ID."""
    logger.info(f"[VALIDATION] Checking channel ID: {channel_id}")
    if not channel_id or not isinstance(channel_id, str):
        logger.error(f"[VALIDATION] FAILED: Invalid channel_id type or empty")
        raise ValidationError("Channel ID must be a non-empty string")
    
    # Remove whitespace
    channel_id = channel_id.strip()
    
    # Check if it's a valid channel ID format
    if channel_id.startswith('UC') and len(channel_id) == 24:
        return channel_id
    
    # Check if it's a YouTube URL
    if 'youtube.com' in channel_id or 'youtu.be' in channel_id:
        # Extract channel ID from URL
        channel_id = extract_channel_id_from_url(channel_id)
        if channel_id:
            return channel_id
    
    # Check if it's a handle (@username)
    if channel_id.startswith('@'):
        # Convert handle to channel ID (would need API call in real implementation)
        logger.warning(f"Handle {channel_id} needs API resolution")
        return channel_id
    
    raise ValidationError(f"Invalid channel ID format: {channel_id}")

def extract_channel_id_from_url(url: str) -> Optional[str]:
    """Extract channel ID from YouTube URL."""
    try:
        parsed = urlparse(url)
        
        # Handle different YouTube URL formats
        if 'youtube.com' in parsed.netloc:
            if '/channel/' in parsed.path:
                match = re.search(r'/channel/([a-zA-Z0-9_-]+)', parsed.path)
                if match:
                    return match.group(1)
            elif '/@' in parsed.path:
                # Handle @username format
                match = re.search(r'/@([a-zA-Z0-9_-]+)', parsed.path)
                if match:
                    return f"@{match.group(1)}"
        
        return None
    except Exception as e:
        logger.error(f"Error extracting channel ID from URL {url}: {e}")
        return None

def validate_spreadsheet_url(url: str) -> str:
    """Validate Google Spreadsheet URL."""
    if not url or not isinstance(url, str):
        raise ValidationError("Spreadsheet URL must be a non-empty string")
    
    url = url.strip()
    
    # Check if it's a valid Google Sheets URL
    if not ('docs.google.com/spreadsheets' in url or 'sheets.google.com' in url):
        raise ValidationError("Invalid Google Sheets URL format")
    
    # Extract spreadsheet ID
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
    if not match:
        raise ValidationError("Could not extract spreadsheet ID from URL")
    
    return url

def validate_tab_name(tab_name: str) -> str:
    """Validate sheet tab name."""
    if not tab_name or not isinstance(tab_name, str):
        raise ValidationError("Tab name must be a non-empty string")
    
    tab_name = tab_name.strip()
    
    # Check for invalid characters
    invalid_chars = ['[', ']', '*', '?', '\\', '/', ':', '|']
    for char in invalid_chars:
        if char in tab_name:
            raise ValidationError(f"Tab name contains invalid character: {char}")
    
    # Check length
    if len(tab_name) > 100:
        raise ValidationError("Tab name too long (max 100 characters)")
    
    return tab_name

def validate_duration(duration: Any) -> int:
    """Validate duration in seconds."""
    if isinstance(duration, int):
        if duration < 0:
            raise ValidationError("Duration must be non-negative")
        return duration
    
    if isinstance(duration, str):
        try:
            duration = int(duration)
            if duration < 0:
                raise ValidationError("Duration must be non-negative")
            return duration
        except ValueError:
            raise ValidationError("Duration must be a valid integer")
    
    raise ValidationError("Duration must be an integer or string representation of integer")

def validate_keywords(keywords: Any) -> List[str]:
    """Validate and parse keywords."""
    if not keywords:
        return []
    
    if isinstance(keywords, str):
        # Split by comma and clean up
        keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
    elif isinstance(keywords, list):
        keyword_list = [str(kw).strip() for kw in keywords if str(kw).strip()]
    else:
        raise ValidationError("Keywords must be a string or list")
    
    # Validate each keyword
    for keyword in keyword_list:
        if len(keyword) > 100:
            raise ValidationError(f"Keyword too long: {keyword}")
        
        # Check for potentially dangerous characters
        if any(char in keyword for char in ['<', '>', '"', "'", '&']):
            raise ValidationError(f"Keyword contains potentially dangerous characters: {keyword}")
    
    return keyword_list

def validate_max_results(max_results: Any) -> int:
    """Validate max results parameter."""
    logger.info(f"[VALIDATION] Checking max_results: {max_results}")
    if isinstance(max_results, int):
        if not 1 <= max_results <= 50:
            raise ValidationError("Max results must be between 1 and 50")
        return max_results
    
    if isinstance(max_results, str):
        try:
            max_results = int(max_results)
            if not 1 <= max_results <= 50:
                raise ValidationError("Max results must be between 1 and 50")
            return max_results
        except ValueError:
            raise ValidationError("Max results must be a valid integer")
    
    raise ValidationError("Max results must be an integer or string representation of integer")

def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize string input."""
    if not isinstance(value, str):
        value = str(value)
    
    # Remove null bytes and control characters
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    
    # Limit length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()

def validate_api_key(api_key: str, key_type: str = "YouTube") -> str:
    """Validate API key format."""
    if not api_key or not isinstance(api_key, str):
        raise ValidationError(f"{key_type} API key must be a non-empty string")
    
    api_key = api_key.strip()
    
    if key_type.lower() == "youtube":
        if not api_key.startswith('AIza'):
            raise ValidationError("Invalid YouTube API key format")
        if len(api_key) != 39:
            raise ValidationError("Invalid YouTube API key length")
    
    return api_key

def validate_file_path(file_path: str, must_exist: bool = True) -> str:
    """Validate file path."""
    if not file_path or not isinstance(file_path, str):
        raise ValidationError("File path must be a non-empty string")
    
    file_path = file_path.strip()
    
    # Check for path traversal attempts
    if '..' in file_path or file_path.startswith('/'):
        raise ValidationError("Invalid file path: potential path traversal")
    
    if must_exist and not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")
    
    return file_path

def validate_boolean(value: Any) -> bool:
    """Validate boolean value."""
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    
    if isinstance(value, int):
        return bool(value)
    
    raise ValidationError("Value must be a boolean, string, or integer")

# Import os for file validation
import os

