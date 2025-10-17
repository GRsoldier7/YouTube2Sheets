"""
YouTube Service
Interface and implementation for YouTube Data API v3 operations.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests
import time
from src.domain.models import Video, Channel
from src.backend.api_optimizer import ResponseCache
from src.utils.validation import validate_api_key, validate_max_results, ValidationError
from src.services.enhanced_error_handler import EnhancedErrorHandler, ErrorContext
from src.services.enhanced_logging import get_logger, log_context, LogContext, performance_monitoring
from datetime import datetime


@dataclass
class YouTubeConfig:
    """YouTube API configuration."""
    api_key: str
    secondary_api_key: Optional[str] = None
    quota_limit: int = 10000
    rate_limit_delay: float = 0.1


class YouTubeServiceInterface(ABC):
    """Interface for YouTube service operations."""
    
    @abstractmethod
    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Video]:
        """Get videos from a channel."""
        pass
    
    @abstractmethod
    def resolve_channel_id(self, channel_handle: str) -> Optional[str]:
        """Resolve channel handle to channel ID."""
        pass
    
    @abstractmethod
    def get_video_details(self, video_id: str) -> Optional[Video]:
        """Get detailed information about a video."""
        pass
    
    @abstractmethod
    def get_quota_usage(self) -> int:
        """Get current API quota usage."""
        pass


class YouTubeService(YouTubeServiceInterface):
    """YouTube Data API v3 service implementation."""
    
    def __init__(self, config: YouTubeConfig, shared_cache: Optional[ResponseCache] = None, cache_tracker: Optional[Any] = None):
        self.error_handler = EnhancedErrorHandler()
        self.logger = get_logger("youtube_service")
        # Validate API key
        try:
            validate_api_key(config.api_key, "YouTube")
        except ValidationError as e:
            raise ValueError(f"Invalid YouTube API key: {e}")
        
        self.config = config
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.quota_used = 0
        self.last_request_time = 0
        self._cache = {}  # Simple in-memory cache for performance
        self._cache_ttl = 300  # 5 minutes cache TTL
        # Use shared cache if provided, otherwise create own
        self._etag_cache = shared_cache or ResponseCache("youtube_etag_cache.json")
        # Cache hit/miss tracker
        self.cache_tracker = cache_tracker
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to YouTube API with ETag caching and rate limiting."""
        # Create cache key
        cache_key = f"{endpoint}:{hash(frozenset(params.items()))}"
        current_time = time.time()
        
        # Check ETag cache first
        etag = None
        cached_response = self._etag_cache.get(cache_key, etag)
        if cached_response:
            print(f"[CACHE] ETag cache HIT for {endpoint}")
            if self.cache_tracker:
                self.cache_tracker.cache_hits += 1
            return cached_response
        
        # Check simple cache as fallback
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if current_time - cached_time < self._cache_ttl:
                print(f"[CACHE] Simple cache HIT for {endpoint}")
                if self.cache_tracker:
                    self.cache_tracker.cache_hits += 1
                return cached_data
        
        # Rate limiting
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.config.rate_limit_delay:
            time.sleep(self.config.rate_limit_delay - time_since_last)
        
        # Add API key
        params['key'] = self.config.api_key
        
        # Make request with proper error handling and compression
        try:
            headers = {
                'Accept-Encoding': 'gzip, deflate',
                'User-Agent': 'YouTube2Sheets/1.0'
            }
            response = requests.get(f"{self.base_url}/{endpoint}", params=params, headers=headers, timeout=15)
            self.last_request_time = time.time()
            
            # Track cache miss
            if self.cache_tracker:
                self.cache_tracker.cache_misses += 1
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract ETag from response headers
                etag = response.headers.get('ETag', '').strip('"')
                
                # Store in ETag cache if we have an ETag
                if etag:
                    self._etag_cache.set(cache_key, data, etag)
                    print(f"[CACHE] ETag cache STORED for {endpoint} (ETag: {etag[:8]}...)")
                else:
                    # Fallback to simple cache
                    self._cache[cache_key] = (data, current_time)
                    print(f"[CACHE] Simple cache STORED for {endpoint}")
                
                # Track quota usage
                self.quota_used += 1
                return data
            elif response.status_code == 403:
                error_data = response.json()
                if 'quotaExceeded' in str(error_data):
                    raise Exception("YouTube API quota exceeded. Please try again later.")
                else:
                    raise Exception(f"YouTube API access forbidden: {error_data}")
            else:
                error_data = response.json() if response.content else {}
                raise Exception(f"YouTube API error {response.status_code}: {error_data}")
                
        except requests.exceptions.Timeout:
            raise Exception("YouTube API request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"YouTube API request failed: {str(e)}")
    
    def get_channel_videos(self, channel_input: str, max_results: int = 50) -> List[Video]:
        """Get videos from a channel (handles both channel IDs and handles)."""
        try:
            self.logger.info(f"[FETCH] Starting video fetch for channel: {channel_input}")
            
            # First resolve channel ID if it's a handle
            if channel_input.startswith('@'):
                self.logger.info(f"[FETCH] Resolving handle: {channel_input}")
                channel_id = self.resolve_channel_id(channel_input[1:])  # Remove @
                if not channel_id:
                    self.logger.error(f"[FETCH] FAILED to resolve handle: {channel_input}")
                    return []
                self.logger.info(f"[FETCH] Resolved {channel_input} -> {channel_id}")
            else:
                channel_id = channel_input
                self.logger.info(f"[FETCH] Using direct channel ID: {channel_id}")
            
            # Validate max_results only (channel_id already validated/resolved above)
            from src.utils.validation import validate_max_results
            max_results = validate_max_results(max_results)
            self.logger.info(f"[FETCH] max_results validated: {max_results}")
            
            # First, get the uploads playlist ID
            self.logger.info(f"[FETCH] About to fetch uploads playlist for: {channel_id}")
            channel_params = {
                'part': 'contentDetails',
                'id': channel_id
            }
            channel_data = self._make_request('channels', channel_params)
            
            self.logger.info(f"[FETCH] Channel API response received for: {channel_id}")
            self.logger.info(f"[FETCH] Response items count: {len(channel_data.get('items', []))}")
            
            if not channel_data.get('items'):
                self.logger.error(f"[FETCH] No channel data for ID: {channel_id}")
                self.logger.error(f"[FETCH] API response: {channel_data}")
                return []
            
            self.logger.info(f"[FETCH] Found channel data for: {channel_id}")
            uploads_playlist_id = channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            self.logger.info(f"[FETCH] Uploads playlist ID: {uploads_playlist_id}")
            
            # Get videos from uploads playlist
            playlist_params = {
                'part': 'snippet',
                'playlistId': uploads_playlist_id,
                'maxResults': max_results
            }
            playlist_data = self._make_request('playlistItems', playlist_params)
            
            self.logger.info(f"[FETCH] Playlist API returned {len(playlist_data.get('items', []))} items")
            
            videos = []
            video_ids = []
            
            # First, collect all video IDs
            for item in playlist_data.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']
                video_ids.append(video_id)
            
            self.logger.info(f"[FETCH] Collected {len(video_ids)} video IDs from playlist")
            
            # OPTIMIZED BATCH PROCESSING: Get full details for all videos in batches of 50
            if video_ids:
                self.logger.info(f"[BATCH] Processing {len(video_ids)} videos in batches of 50")
                
                # Process video IDs in batches of 50 (YouTube API limit)
                for i in range(0, len(video_ids), 50):
                    batch = video_ids[i:i+50]
                    video_ids_str = ','.join(batch)
                    
                    self.logger.info(f"[BATCH] Processing batch {i//50 + 1}/{(len(video_ids) + 49)//50} ({len(batch)} videos)")
                    
                    video_params = {
                        'part': 'snippet,contentDetails,statistics',
                        'id': video_ids_str
                    }
                    video_data = self._make_request('videos', video_params)
                    
                    # Build Video objects with full details
                    for item in video_data.get('items', []):
                        try:
                            # Parse duration
                            duration_str = item['contentDetails']['duration']
                            duration = self._parse_duration(duration_str)
                            
                            video = Video(
                                video_id=item['id'],
                                title=item['snippet']['title'],
                                description=item['snippet'].get('description', ''),
                                channel_id=channel_id,
                                channel_title=item['snippet'].get('channelTitle', ''),
                                published_at=item['snippet'].get('publishedAt', ''),
                                thumbnail_url=item['snippet'].get('thumbnails', {}).get('default', {}).get('url', ''),
                                url=f"https://www.youtube.com/watch?v={item['id']}",
                                duration=duration,
                                view_count=int(item['statistics'].get('viewCount', 0)),
                                like_count=int(item['statistics'].get('likeCount', 0)),
                                comment_count=int(item['statistics'].get('commentCount', 0))
                            )
                            videos.append(video)
                        except Exception as e:
                            self.logger.error(f"Error parsing video {item.get('id')}: {e}")
                            continue
                
                self.logger.info(f"[BATCH] Successfully processed {len(videos)} videos from {len(video_ids)} video IDs")
            
            print(f"Retrieved {len(videos)} videos with full details")
            return videos
            
        except Exception as e:
            self.logger.error(f"[FETCH] EXCEPTION in get_channel_videos: {e}")
            self.logger.error(f"[FETCH] Channel: {channel_input}, Resolved ID: {channel_id if 'channel_id' in locals() else 'NOT SET'}")
            import traceback
            self.logger.error(f"[FETCH] Stack trace: {traceback.format_exc()}")
            print(f"Error getting channel videos: {e}")
            traceback.print_exc()
            return []
    
    def resolve_channel_id(self, channel_handle: str) -> Optional[str]:
        """Resolve channel handle to channel ID using modern YouTube API."""
        try:
            self.logger.info(f"[RESOLVE] Attempting to resolve: {channel_handle}")
            
            # Modern YouTube uses @ handles - use forHandle parameter
            params = {
                'part': 'id',
                'forHandle': channel_handle
            }
            data = self._make_request('channels', params)
            self.logger.info(f"[RESOLVE] forHandle API returned {len(data.get('items', []))} items")
            
            if data.get('items'):
                channel_id = data['items'][0]['id']
                self.logger.info(f"[RESOLVE] SUCCESS via forHandle: {channel_handle} -> {channel_id}")
                return channel_id
            
            # If that fails, try using the search API
            self.logger.info(f"[RESOLVE] forHandle failed, trying search API")
            search_params = {
                'part': 'snippet',
                'q': channel_handle,
                'type': 'channel',
                'maxResults': 1
            }
            search_data = self._make_request('search', search_params)
            self.logger.info(f"[RESOLVE] Search API returned {len(search_data.get('items', []))} items")
            
            if search_data.get('items'):
                channel_id = search_data['items'][0]['id']['channelId']
                self.logger.info(f"[RESOLVE] SUCCESS via search: {channel_handle} -> {channel_id}")
                return channel_id
            
            self.logger.error(f"[RESOLVE] FAILED: Could not resolve {channel_handle}")
            return None
            
        except Exception as e:
            self.logger.error(f"[RESOLVE] EXCEPTION resolving {channel_handle}: {e}")
            import traceback
            self.logger.error(f"[RESOLVE] Traceback: {traceback.format_exc()}")
            return None
    
    def get_video_details(self, video_id: str) -> Optional[Video]:
        """Get detailed information about a video."""
        try:
            params = {
                'part': 'snippet,statistics,contentDetails',
                'id': video_id
            }
            data = self._make_request('videos', params)
            
            if not data.get('items'):
                return None
            
            item = data['items'][0]
            snippet = item['snippet']
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})
            
            # Parse duration (ISO 8601 format)
            duration_str = content_details.get('duration', 'PT0S')
            duration = self._parse_duration(duration_str)
            
            video = Video(
                id=video_id,
                title=snippet['title'],
                description=snippet.get('description', ''),
                channel_id=snippet['channelId'],
                channel_title=snippet.get('channelTitle', ''),
                published_at=snippet.get('publishedAt', ''),
                thumbnail_url=snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                duration=duration,
                view_count=int(statistics.get('viewCount', 0)),
                like_count=int(statistics.get('likeCount', 0)),
                comment_count=int(statistics.get('commentCount', 0))
            )
            
            return video
            
        except Exception as e:
            print(f"Error getting video details: {e}")
            return None
    
    def get_quota_usage(self) -> int:
        """Get current API quota usage."""
        return self.quota_used
    

    def get_channel_info(self, channel_handle: str) -> Optional[Dict[str, Any]]:
        """Get channel information."""
        try:
            # First resolve channel ID if it's a handle
            if channel_handle.startswith('@'):
                channel_id = self.resolve_channel_id(channel_handle[1:])  # Remove @
                if not channel_id:
                    return None
            else:
                channel_id = channel_handle
            
            params = {
                'part': 'snippet,statistics',
                'id': channel_id
            }
            data = self._make_request('channels', params)
            
            if data.get('items'):
                item = data['items'][0]
                snippet = item['snippet']
                statistics = item.get('statistics', {})
                
                return {
                    'id': channel_id,
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'subscriber_count': int(statistics.get('subscriberCount', 0)),
                    'view_count': int(statistics.get('viewCount', 0)),
                    'video_count': int(statistics.get('videoCount', 0)),
                    'thumbnail_url': snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                    'url': f"https://youtube.com/channel/{channel_id}"
                }
            return None
            
        except Exception as e:
            print(f"Error getting channel info: {e}")
            return None

    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        import re
        
        # Remove PT prefix
        duration_str = duration_str[2:]
        
        # Parse components
        hours = 0
        minutes = 0
        seconds = 0
        
        # Hours
        hour_match = re.search(r'(\d+)H', duration_str)
        if hour_match:
            hours = int(hour_match.group(1))
        
        # Minutes
        minute_match = re.search(r'(\d+)M', duration_str)
        if minute_match:
            minutes = int(minute_match.group(1))
        
        # Seconds
        second_match = re.search(r'(\d+)S', duration_str)
        if second_match:
            seconds = int(second_match.group(1))
        
        return hours * 3600 + minutes * 60 + seconds
