"""
YouTube to Google Sheets Automation - Core Logic
==============================================

This module contains the core backend logic for fetching data from the YouTube
and Google Sheets APIs, processing it, and handling all interactions with
the Google Sheet.

Author: AI Assistant
Version: 2.0
"""

import os
import re
import json
import logging
import time
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Constants ---
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
HEADERS = [
    'YT Channel', 'Date of Video', 'Short_Long', 'Video Length', 
    'Video Title', 'Video Link', 'Views', 'Likes_Dislikes (N/A=No Public Data)', 'NotebookLM'
]
DEFAULT_SPREADSHEET_URL = os.getenv("SPREADSHEET_URL")

class YouTubeToSheetsAutomator:
    """
    Handles all automation logic for fetching from YouTube and writing to Google Sheets.
    """
    
    def __init__(self, youtube_api_key: str, service_account_file: str, spreadsheet_url: Optional[str] = None):
        """
        Initialize the automator with API credentials.
        
        Args:
            youtube_api_key: YouTube Data API v3 key
            service_account_file: Path to Google service account JSON file
            spreadsheet_url: Optional default spreadsheet URL
        """
        if not youtube_api_key:
            raise ValueError("YouTube API key is required")
        if not service_account_file or not os.path.exists(service_account_file):
            raise ValueError("Valid Google service account file is required")
            
        self.youtube_api_key = youtube_api_key
        self.service_account_file = service_account_file
        self.spreadsheet_url = spreadsheet_url or DEFAULT_SPREADSHEET_URL
        
        # Initialize YouTube API
        self.youtube_service = build('youtube', 'v3', developerKey=youtube_api_key)
        
        # Initialize Google Sheets API
        credentials = Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
        self.sheets_service = build('sheets', 'v4', credentials=credentials)
        
        logger.info("YouTubeToSheetsAutomator initialized successfully")
    
    def extract_channel_id(self, channel_input: str) -> str:
        """
        Extract channel ID from various YouTube channel input formats.
        
        Args:
            channel_input: Channel URL, @username, or channel ID
            
        Returns:
            Channel ID
        """
        # If it's already a channel ID (starts with UC)
        if channel_input.startswith('UC') and len(channel_input) == 24:
            return channel_input
            
        # Handle @username format
        if channel_input.startswith('@'):
            username = channel_input[1:]
            try:
                # Search for channel by username
                search_response = self.youtube_service.search().list(
                    part='snippet',
                    q=username,
                    type='channel',
                    maxResults=1
                ).execute()
                
                if search_response['items']:
                    return search_response['items'][0]['snippet']['channelId']
            except Exception as e:
                logger.error(f"Error searching for channel @{username}: {e}")
                
        # Handle URL formats
        if 'youtube.com' in channel_input:
            # Extract from various YouTube URL formats
            patterns = [
                r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
                r'youtube\.com/c/([a-zA-Z0-9_-]+)',
                r'youtube\.com/user/([a-zA-Z0-9_-]+)',
                r'youtube\.com/@([a-zA-Z0-9_-]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, channel_input)
                if match:
                    identifier = match.group(1)
                    try:
                        # Try to get channel info
                        if pattern.endswith('channel/([a-zA-Z0-9_-]+)'):
                            return identifier
                        else:
                            # Search for channel
                            search_response = self.youtube_service.search().list(
                                part='snippet',
                                q=identifier,
                                type='channel',
                                maxResults=1
                            ).execute()
                            
                            if search_response['items']:
                                return search_response['items'][0]['snippet']['channelId']
                    except Exception as e:
                        logger.error(f"Error processing channel identifier {identifier}: {e}")
        
        # If we can't extract, assume it's a channel ID
        return channel_input
    
    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Dict]:
        """
        Fetch videos from a YouTube channel.
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to fetch
            
        Returns:
            List of video data dictionaries
        """
        videos = []
        next_page_token = None
        
        try:
            # Get channel info first
            channel_response = self.youtube_service.channels().list(
                part='snippet',
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                logger.error(f"Channel {channel_id} not found")
                return videos
                
            channel_name = channel_response['items'][0]['snippet']['title']
            logger.info(f"Fetching videos from channel: {channel_name}")
            
            # Get videos from channel
            while len(videos) < max_results:
                request_params = {
                    'part': 'snippet,statistics,contentDetails',
                    'channelId': channel_id,
                    'maxResults': min(50, max_results - len(videos)),
                    'order': 'date'
                }
                
                if next_page_token:
                    request_params['pageToken'] = next_page_token
                    
                search_response = self.youtube_service.search().list(**request_params).execute()
                
                # Process each video
                for item in search_response['items']:
                    if item['id']['kind'] == 'youtube#video':
                        video_data = self.process_video_data(item, channel_name)
                        if video_data:
                            videos.append(video_data)
                
                # Check for next page
                next_page_token = search_response.get('nextPageToken')
                if not next_page_token:
                    break
                    
        except Exception as e:
            logger.error(f"Error fetching videos from channel {channel_id}: {e}")
            
        logger.info(f"Fetched {len(videos)} videos from channel {channel_id}")
        return videos
    
    def process_video_data(self, video_item: Dict, channel_name: str) -> Optional[Dict]:
        """
        Process raw video data into standardized format.
        
        Args:
            video_item: Raw video data from YouTube API
            channel_name: Name of the YouTube channel
            
        Returns:
            Processed video data dictionary
        """
        try:
            snippet = video_item['snippet']
            statistics = video_item.get('statistics', {})
            content_details = video_item.get('contentDetails', {})
            
            # Extract video duration
            duration = content_details.get('duration', 'PT0S')
            duration_seconds = self.parse_duration(duration)
            
            # Determine if video is short or long
            video_type = "Short" if duration_seconds < 60 else "Long"
            
            # Format view count
            view_count = statistics.get('viewCount', '0')
            try:
                view_count = f"{int(view_count):,}"
            except (ValueError, TypeError):
                view_count = "0"
            
            # Format like count
            like_count = statistics.get('likeCount', '0')
            try:
                like_count = f"{int(like_count):,}"
            except (ValueError, TypeError):
                like_count = "N/A"
            
            # Format date
            published_date = snippet.get('publishedAt', '')
            if published_date:
                try:
                    dt = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d')
                except:
                    formatted_date = published_date[:10] if len(published_date) >= 10 else published_date
            else:
                formatted_date = "Unknown"
            
            return {
                'channel': channel_name,
                'date': formatted_date,
                'type': video_type,
                'duration': self.format_duration(duration_seconds),
                'title': snippet.get('title', 'No Title'),
                'url': f"https://www.youtube.com/watch?v={video_item['id']['videoId']}",
                'views': view_count,
                'likes': like_count,
                'notebooklm': '☐'  # Placeholder for NotebookLM checkbox
            }
            
        except Exception as e:
            logger.error(f"Error processing video data: {e}")
            return None
    
    def parse_duration(self, duration: str) -> int:
        """
        Parse ISO 8601 duration string to seconds.
        
        Args:
            duration: ISO 8601 duration string (e.g., 'PT4M13S')
            
        Returns:
            Duration in seconds
        """
        import re
        
        # Remove PT prefix
        duration = duration[2:]
        
        # Extract hours, minutes, seconds
        hours = re.search(r'(\d+)H', duration)
        minutes = re.search(r'(\d+)M', duration)
        seconds = re.search(r'(\d+)S', duration)
        
        total_seconds = 0
        if hours:
            total_seconds += int(hours.group(1)) * 3600
        if minutes:
            total_seconds += int(minutes.group(1)) * 60
        if seconds:
            total_seconds += int(seconds.group(1))
            
        return total_seconds
    
    def format_duration(self, seconds: int) -> str:
        """
        Format seconds into readable duration string.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string (e.g., '4:13')
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def extract_sheet_id(self, spreadsheet_url: str) -> str:
        """
        Extract Google Sheets ID from URL.
        
        Args:
            spreadsheet_url: Google Sheets URL
            
        Returns:
            Sheet ID
        """
        # Handle various Google Sheets URL formats
        patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
            r'([a-zA-Z0-9-_]{44})'  # Direct sheet ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, spreadsheet_url)
            if match:
                return match.group(1)
        
        # If no pattern matches, assume the input is already a sheet ID
        return spreadsheet_url
    
    def write_to_sheets(self, spreadsheet_url: str, tab_name: str, videos: List[Dict]) -> bool:
        """
        Write video data to Google Sheets.
        
        Args:
            spreadsheet_url: Google Sheets URL
            tab_name: Name of the tab to write to
            videos: List of video data dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            sheet_id = self.extract_sheet_id(spreadsheet_url)
            logger.info(f"Writing {len(videos)} videos to sheet {sheet_id}, tab '{tab_name}'")
            
            # Prepare data for writing
            data = [HEADERS]  # Headers first
            
            for video in videos:
                row = [
                    video['channel'],
                    video['date'],
                    video['type'],
                    video['duration'],
                    video['title'],
                    video['url'],
                    video['views'],
                    video['likes'],
                    video['notebooklm']
                ]
                data.append(row)
            
            # Write to sheet
            range_name = f"{tab_name}!A1"
            body = {'values': data}
            
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Successfully wrote {result.get('updatedCells', 0)} cells to sheet")
            return True
            
        except Exception as e:
            logger.error(f"Error writing to Google Sheets: {e}")
            return False
    
    def sync_channel_to_sheet(self, channel_input: str, spreadsheet_url: str, tab_name: str, max_videos: int = 50) -> bool:
        """
        Complete workflow: fetch videos from channel and write to Google Sheets.
        
        Args:
            channel_input: YouTube channel URL, @username, or channel ID
            spreadsheet_url: Google Sheets URL
            tab_name: Name of the tab to write to
            max_videos: Maximum number of videos to fetch
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Starting sync for channel: {channel_input}")
            
            # Extract channel ID
            channel_id = self.extract_channel_id(channel_input)
            logger.info(f"Extracted channel ID: {channel_id}")
            
            # Fetch videos
            videos = self.get_channel_videos(channel_id, max_videos)
            if not videos:
                logger.warning("No videos found for channel")
                return False
            
            # Write to sheets
            success = self.write_to_sheets(spreadsheet_url, tab_name, videos)
            
            if success:
                logger.info(f"Successfully synced {len(videos)} videos to Google Sheets")
            else:
                logger.error("Failed to write videos to Google Sheets")
                
            return success
            
        except Exception as e:
            logger.error(f"Error in sync workflow: {e}")
            return False

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube to Google Sheets Automation')
    parser.add_argument('--channel', required=True, help='YouTube channel URL, @username, or channel ID')
    parser.add_argument('--sheet', required=True, help='Google Sheets URL')
    parser.add_argument('--tab', default='YouTube Videos', help='Tab name in the sheet')
    parser.add_argument('--max-videos', type=int, default=50, help='Maximum number of videos to fetch')
    
    args = parser.parse_args()
    
    # Get credentials from environment
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    sheets_file = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON')
    
    if not youtube_key:
        print("Error: YOUTUBE_API_KEY environment variable not set")
        return 1
        
    if not sheets_file or not os.path.exists(sheets_file):
        print("Error: GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON environment variable not set or file not found")
        return 1
    
    try:
        # Initialize automator
        automator = YouTubeToSheetsAutomator(youtube_key, sheets_file)
        
        # Perform sync
        success = automator.sync_channel_to_sheet(
            args.channel, 
            args.sheet, 
            args.tab, 
            args.max_videos
        )
        
        if success:
            print("✅ Sync completed successfully!")
            return 0
        else:
            print("❌ Sync failed. Check logs for details.")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())