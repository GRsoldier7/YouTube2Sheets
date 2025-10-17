"""
API Optimizer Service
Advanced API optimization with smart caching and quota management
"""
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import time
import json
from datetime import datetime, timedelta
from src.services.enhanced_logging import get_logger, log_context, performance_monitoring

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.youtube_service import YouTubeService, YouTubeConfig
from services.sheets_service import SheetsService, SheetsConfig
from src.domain.models import Video
from src.utils.validation import validate_youtube_channel_id, ValidationError

@dataclass
class APIQuotaStatus:
    """API quota status tracking."""
    service: str
    quota_used: int
    quota_limit: int
    reset_time: datetime
    efficiency_score: float

@dataclass
class OptimizationMetrics:
    """Optimization performance metrics."""
    total_api_calls: int
    cache_hits: int
    cache_misses: int
    duplicates_filtered: int
    quota_saved: int
    time_saved: float

class APIOptimizer:
    """Advanced API optimizer with smart caching and quota management."""
    
    def __init__(self, youtube_service: YouTubeService, sheets_service: SheetsService):
        self.logger = get_logger("api_optimizer")
        self.youtube_service = youtube_service
        self.sheets_service = sheets_service
        self._quota_tracker: Dict[str, APIQuotaStatus] = {}
        self._optimization_metrics = OptimizationMetrics(0, 0, 0, 0, 0, 0.0)
        self._video_existence_cache: Dict[str, Set[str]] = {}  # tab_name -> set of video_ids
        self._cache_timestamp: Dict[str, float] = {}
        self._cache_ttl = 600  # 10 minutes
        
    def _load_existing_video_ids(self, tab_name: str) -> Set[str]:
        """Load existing video IDs from the sheet tab."""
        current_time = time.time()
        
        # Check cache first
        if (tab_name in self._video_existence_cache and 
            tab_name in self._cache_timestamp and
            current_time - self._cache_timestamp[tab_name] < self._cache_ttl):
            return self._video_existence_cache[tab_name]
        
        try:
            # Read existing data from the sheet
            existing_data = self.sheets_service.read_sheet_data(tab_name)
            
            video_ids = set()
            if existing_data:
                for row in existing_data[1:]:  # Skip header row
                    if row and len(row) > 0 and row[0]:
                        video_ids.add(row[0])
            
            # Update cache
            self._video_existence_cache[tab_name] = video_ids
            self._cache_timestamp[tab_name] = current_time
            
            return video_ids
            
        except Exception as e:
            print(f"Warning: Could not load existing video IDs for {tab_name}: {e}")
            return set()
    
    def optimize_video_fetch(self, channel_id: str, tab_name: str, max_results: int = 50) -> List[Video]:
        """Optimize video fetching by filtering out existing videos before API calls."""
        try:
            validate_youtube_channel_id(channel_id)
            
            start_time = time.time()
            
            # Load existing video IDs
            existing_video_ids = self._load_existing_video_ids(tab_name)
            
            # If we have many existing videos, we might want to limit the API call
            if len(existing_video_ids) > max_results * 2:
                print(f"Tab {tab_name} has {len(existing_video_ids)} existing videos, limiting API call")
                max_results = min(max_results, 20)  # Reduce API call size
            
            # Fetch videos from YouTube API
            print(f"Fetching up to {max_results} videos from channel {channel_id}")
            all_videos = self.youtube_service.get_channel_videos(channel_id, max_results)
            
            # Filter out existing videos
            new_videos = []
            duplicates_filtered = 0
            
            for video in all_videos:
                if video.video_id not in existing_video_ids:
                    new_videos.append(video)
                else:
                    duplicates_filtered += 1
                    print(f"Filtered existing video: {video.title}")
            
            # Update metrics
            self._optimization_metrics.total_api_calls += 1
            self._optimization_metrics.duplicates_filtered += duplicates_filtered
            self._optimization_metrics.time_saved += time.time() - start_time
            
            print(f"API Optimization: {len(new_videos)} new videos, {duplicates_filtered} duplicates filtered")
            return new_videos
            
        except ValidationError as e:
            print(f"Validation error in video fetch optimization: {e}")
            return []
        except Exception as e:
            print(f"Error optimizing video fetch: {e}")
            return []
    
    def batch_optimize_videos(self, channel_ids: List[str], tab_name: str, max_results_per_channel: int = 25) -> List[Video]:
        """Optimize video fetching for multiple channels."""
        try:
            all_new_videos = []
            total_duplicates = 0
            
            for channel_id in channel_ids:
                try:
                    validate_youtube_channel_id(channel_id)
                    
                    # Optimize each channel
                    channel_videos = self.optimize_video_fetch(channel_id, tab_name, max_results_per_channel)
                    all_new_videos.extend(channel_videos)
                    
                    # Add a small delay between channels to respect rate limits
                    time.sleep(0.5)
                    
                except ValidationError as e:
                    print(f"Invalid channel ID {channel_id}: {e}")
                    continue
                except Exception as e:
                    print(f"Error processing channel {channel_id}: {e}")
                    continue
            
            print(f"Batch optimization complete: {len(all_new_videos)} total new videos from {len(channel_ids)} channels")
            return all_new_videos
            
        except Exception as e:
            print(f"Error in batch optimization: {e}")
            return []
    
    def track_api_quota(self, service: str, quota_used: int, quota_limit: int = 10000):
        """Track API quota usage for a service."""
        try:
            reset_time = datetime.now() + timedelta(days=1)  # Assume daily reset
            
            self._quota_tracker[service] = APIQuotaStatus(
                service=service,
                quota_used=quota_used,
                quota_limit=quota_limit,
                reset_time=reset_time,
                efficiency_score=self._calculate_efficiency_score(quota_used, quota_limit)
            )
            
            quota_used_safe = quota_used or 0
            quota_limit_safe = quota_limit or 1
            percentage = (quota_used_safe / quota_limit_safe * 100) if quota_limit_safe > 0 else 0
            print(f"Quota tracking for {service}: {quota_used_safe}/{quota_limit_safe} ({percentage:.1f}%)")
            
        except Exception as e:
            print(f"Error tracking API quota: {e}")
    
    def _calculate_efficiency_score(self, quota_used: int, quota_limit: int) -> float:
        """Calculate API efficiency score."""
        if quota_limit == 0:
            return 0.0
        
        usage_ratio = quota_used / quota_limit
        
        # Efficiency score based on usage ratio
        if usage_ratio < 0.1:
            return 1.0  # Excellent
        elif usage_ratio < 0.3:
            return 0.8  # Good
        elif usage_ratio < 0.5:
            return 0.6  # Fair
        elif usage_ratio < 0.8:
            return 0.4  # Poor
        else:
            return 0.2  # Critical
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report."""
        try:
            cache_hit_rate = 0.0
            if self._optimization_metrics.total_api_calls > 0:
                cache_hit_rate = self._optimization_metrics.cache_hits / self._optimization_metrics.total_api_calls
            
            return {
                "optimization_metrics": {
                    "total_api_calls": self._optimization_metrics.total_api_calls,
                    "cache_hits": self._optimization_metrics.cache_hits,
                    "cache_misses": self._optimization_metrics.cache_misses,
                    "duplicates_filtered": self._optimization_metrics.duplicates_filtered,
                    "quota_saved": self._optimization_metrics.quota_saved,
                    "time_saved": self._optimization_metrics.time_saved,
                    "cache_hit_rate": cache_hit_rate
                },
                "quota_status": {
                    service: {
                        "quota_used": status.quota_used,
                        "quota_limit": status.quota_limit,
                        "usage_percentage": status.quota_used / status.quota_limit * 100,
                        "efficiency_score": status.efficiency_score,
                        "reset_time": status.reset_time.isoformat()
                    }
                    for service, status in self._quota_tracker.items()
                },
                "cache_status": {
                    tab_name: {
                        "video_count": len(video_ids),
                        "last_updated": self._cache_timestamp.get(tab_name, 0),
                        "cache_age": time.time() - self._cache_timestamp.get(tab_name, 0) if tab_name in self._cache_timestamp else 0
                    }
                    for tab_name, video_ids in self._video_existence_cache.items()
                }
            }
            
        except Exception as e:
            print(f"Error generating optimization report: {e}")
            return {"error": str(e)}
    
    def clear_optimization_cache(self, tab_name: Optional[str] = None):
        """Clear optimization caches."""
        if tab_name:
            self._video_existence_cache.pop(tab_name, None)
            self._cache_timestamp.pop(tab_name, None)
            print(f"Cleared optimization cache for {tab_name}")
        else:
            self._video_existence_cache.clear()
            self._cache_timestamp.clear()
            print("Cleared all optimization caches")
    
    def reset_metrics(self):
        """Reset optimization metrics."""
        self._optimization_metrics = OptimizationMetrics(0, 0, 0, 0, 0, 0.0)
        print("Reset optimization metrics")
    
    def get_quota_status(self) -> Dict[str, Any]:
        """Get current quota status for all services."""
        status = {}
        for service, quota in self._quota_tracker.items():
            status[service] = {
                'quota_used': quota.quota_used,
                'quota_limit': quota.quota_limit,
                'quota_remaining': quota.quota_limit - quota.quota_used,
                'efficiency_score': quota.efficiency_score,
                'reset_time': quota.reset_time.isoformat()
            }
        return status
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limiting status."""
        return {
            'youtube_rate_limit': 'Active',
            'sheets_rate_limit': 'Active',
            'cache_efficiency': f"{self._optimization_metrics.cache_hits}/{self._optimization_metrics.total_api_calls}",
            'optimization_active': True
        }

