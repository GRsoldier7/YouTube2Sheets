"""
YouTube2Sheets Parsing Utilities
Channel normalization, keyword parsing, and data validation.
"""
import re
from typing import List, Set, Optional
from urllib.parse import urlparse, parse_qs


def parse_channels(input_text: str) -> List[str]:
    """
    Parse YouTube channel input text into normalized channel identifiers.
    
    Args:
        input_text: Raw input text containing channels
        
    Returns:
        List of normalized channel identifiers
    """
    if not input_text or not input_text.strip():
        return []
    
    # Split by common delimiters
    raw_channels = re.split(r'[,\n\r\s]+', input_text.strip())
    
    normalized_channels = []
    seen_channels = set()
    
    for channel in raw_channels:
        if not channel or channel.isspace():
            continue
            
        normalized = normalize_channel_identifier(channel.strip())
        if normalized and normalized not in seen_channels:
            normalized_channels.append(normalized)
            seen_channels.add(normalized)
    
    return normalized_channels


def normalize_channel_identifier(channel: str) -> Optional[str]:
    """
    Normalize a channel identifier to a standard format.
    
    Args:
        channel: Raw channel identifier (URL, @handle, or ID)
        
    Returns:
        Normalized channel identifier or None if invalid
    """
    if not channel:
        return None
    
    # Remove extra whitespace
    channel = channel.strip()
    
    # Handle @username format
    if channel.startswith('@'):
        return channel[1:]  # Remove @ prefix
    
    # Handle YouTube URLs
    if 'youtube.com' in channel or 'youtu.be' in channel:
        return extract_channel_from_url(channel)
    
    # Handle channel IDs (UC... format)
    if channel.startswith('UC') and len(channel) == 24:
        return channel
    
    # Handle channel handles (without @)
    if re.match(r'^[a-zA-Z0-9_-]+$', channel):
        return channel
    
    return None


def extract_channel_from_url(url: str) -> Optional[str]:
    """
    Extract channel identifier from YouTube URL.
    
    Args:
        url: YouTube URL
        
    Returns:
        Channel identifier or None if not found
    """
    try:
        parsed = urlparse(url)
        
        # Handle youtu.be URLs
        if 'youtu.be' in parsed.netloc:
            return parsed.path[1:]  # Remove leading slash
        
        # Handle youtube.com URLs
        if 'youtube.com' in parsed.netloc:
            path = parsed.path
            
            # Channel page: /@username or /c/username or /channel/UC...
            if path.startswith('/@'):
                return path[2:]  # Remove /@
            elif path.startswith('/c/'):
                return path[3:]  # Remove /c/
            elif path.startswith('/channel/'):
                return path[9:]  # Remove /channel/
            elif path.startswith('/user/'):
                return path[6:]  # Remove /user/
            
            # Video page: extract from query params
            query_params = parse_qs(parsed.query)
            if 'v' in query_params:
                # This is a video URL, we can't extract channel directly
                return None
        
        return None
        
    except Exception:
        return None


def parse_keywords(keyword_text: str) -> List[str]:
    """
    Parse keyword input text into a list of keywords.
    
    Args:
        keyword_text: Raw keyword text
        
    Returns:
        List of normalized keywords
    """
    if not keyword_text or not keyword_text.strip():
        return []
    
    # Split by commas and clean up
    keywords = [kw.strip() for kw in keyword_text.split(',')]
    
    # Filter out empty keywords and normalize
    normalized_keywords = []
    for keyword in keywords:
        if keyword and not keyword.isspace():
            # Convert to lowercase and remove extra spaces
            normalized = ' '.join(keyword.lower().split())
            if normalized:
                normalized_keywords.append(normalized)
    
    return normalized_keywords


def validate_duration(duration_str: str) -> Optional[int]:
    """
    Validate and parse duration input.
    
    Args:
        duration_str: Duration string (e.g., "60", "1:30", "90s")
        
    Returns:
        Duration in seconds or None if invalid
    """
    if not duration_str or not duration_str.strip():
        return None
    
    duration_str = duration_str.strip().lower()
    
    try:
        # Handle seconds format (e.g., "60", "90s")
        if duration_str.endswith('s'):
            return int(duration_str[:-1])
        elif duration_str.isdigit():
            return int(duration_str)
        
        # Handle MM:SS format (e.g., "1:30")
        if ':' in duration_str:
            parts = duration_str.split(':')
            if len(parts) == 2:
                minutes, seconds = int(parts[0]), int(parts[1])
                return minutes * 60 + seconds
            elif len(parts) == 3:
                hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
                return hours * 3600 + minutes * 60 + seconds
        
        return None
        
    except (ValueError, IndexError):
        return None


def validate_tab_name(tab_name: str) -> bool:
    """
    Validate Google Sheets tab name.
    
    Args:
        tab_name: Tab name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not tab_name or not tab_name.strip():
        return False
    
    # Google Sheets tab names cannot contain certain characters
    invalid_chars = ['[', ']', '*', '?', '\\', '/']
    
    for char in invalid_chars:
        if char in tab_name:
            return False
    
    # Tab name cannot be empty or too long
    if len(tab_name.strip()) == 0 or len(tab_name) > 100:
        return False
    
    return True


def sanitize_tab_name(tab_name: str) -> str:
    """
    Sanitize a tab name for Google Sheets.
    
    Args:
        tab_name: Raw tab name
        
    Returns:
        Sanitized tab name
    """
    if not tab_name:
        return "Sheet1"
    
    # Remove invalid characters
    sanitized = re.sub(r'[\[\]*?\\/]', '', tab_name)
    
    # Remove leading/trailing whitespace
    sanitized = sanitized.strip()
    
    # Ensure it's not empty
    if not sanitized:
        return "Sheet1"
    
    # Truncate if too long
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    return sanitized


def extract_video_id_from_url(url: str) -> Optional[str]:
    """
    Extract video ID from YouTube URL.
    
    Args:
        url: YouTube URL
        
    Returns:
        Video ID or None if not found
    """
    try:
        parsed = urlparse(url)
        
        # Handle youtu.be URLs
        if 'youtu.be' in parsed.netloc:
            return parsed.path[1:]  # Remove leading slash
        
        # Handle youtube.com URLs
        if 'youtube.com' in parsed.netloc:
            query_params = parse_qs(parsed.query)
            if 'v' in query_params:
                return query_params['v'][0]
        
        return None
        
    except Exception:
        return None


def is_youtube_short(video_id: str, duration: int) -> bool:
    """
    Check if a video is a YouTube Short.
    
    Args:
        video_id: YouTube video ID
        duration: Video duration in seconds
        
    Returns:
        True if it's a Short, False otherwise
    """
    # YouTube Shorts are typically 60 seconds or less
    return duration <= 60


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "1:30", "2:15:30")
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}:{remaining_seconds:02d}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        return f"{hours}:{minutes:02d}:{remaining_seconds:02d}"
