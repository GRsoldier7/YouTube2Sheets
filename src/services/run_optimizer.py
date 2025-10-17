"""
Run Optimizer Service
Comprehensive run performance optimization with progress tracking and resource management
"""
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import psutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.youtube_service import YouTubeService, YouTubeConfig
from services.sheets_service import SheetsService, SheetsConfig
from services.sheets_optimizer import SheetsOptimizer
from services.api_optimizer import APIOptimizer
from src.domain.models import Video, Channel
from src.utils.validation import validate_youtube_channel_id, ValidationError

@dataclass
class RunProgress:
    """Run progress tracking."""
    total_channels: int
    processed_channels: int
    total_videos: int
    processed_videos: int
    duplicates_filtered: int
    errors: int
    start_time: float
    current_channel: str = ""
    status: str = "initializing"

@dataclass
class RunMetrics:
    """Run performance metrics."""
    total_time: float
    videos_per_second: float
    api_calls_made: int
    cache_hit_rate: float
    memory_peak: float
    cpu_peak: float
    efficiency_score: float

class RunOptimizer:
    """Comprehensive run optimizer with performance monitoring and resource management."""
    
    def __init__(self, youtube_service: YouTubeService, sheets_service: SheetsService):
        self.youtube_service = youtube_service
        self.sheets_service = sheets_service
        self.sheets_optimizer = SheetsOptimizer(sheets_service)
        self.api_optimizer = APIOptimizer(youtube_service, sheets_service)
        
        self._progress_callbacks: List[Callable[[RunProgress], None]] = []
        self._run_metrics = RunMetrics(0.0, 0.0, 0, 0.0, 0.0, 0.0, 0.0)
        self._is_running = False
        self._should_stop = False
        
    def add_progress_callback(self, callback: Callable[[RunProgress], None]):
        """Add a progress callback function."""
        self._progress_callbacks.append(callback)
    
    def _notify_progress(self, progress: RunProgress):
        """Notify all progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                callback(progress)
            except Exception as e:
                print(f"Error in progress callback: {e}")
    
    def optimize_run(self, channels: List[str], tab_name: str, 
                    max_videos_per_channel: int = 25,
                    enable_conditional_formatting: bool = True,
                    enable_duplication_check: bool = True) -> Dict[str, Any]:
        """Optimize a complete run with all performance enhancements."""
        try:
            self._is_running = True
            self._should_stop = False
            start_time = time.time()
            
            # Initialize progress tracking
            progress = RunProgress(
                total_channels=len(channels),
                processed_channels=0,
                total_videos=0,
                processed_videos=0,
                duplicates_filtered=0,
                errors=0,
                start_time=start_time,
                status="initializing"
            )
            
            # Setup sheet optimization
            if enable_conditional_formatting:
                print("Setting up conditional formatting...")
                self.sheets_optimizer.setup_conditional_formatting(tab_name)
            
            # Optimize sheet structure
            self.sheets_optimizer.optimize_sheet_structure(tab_name)
            
            # Process channels with optimization
            all_new_videos = []
            total_duplicates = 0
            
            progress.status = "processing_channels"
            self._notify_progress(progress)
            
            for i, channel_id in enumerate(channels):
                if self._should_stop:
                    print("Run stopped by user")
                    break
                
                try:
                    validate_youtube_channel_id(channel_id)
                    progress.current_channel = channel_id
                    progress.processed_channels = i + 1
                    self._notify_progress(progress)
                    
                    print(f"Processing channel {i+1}/{len(channels)}: {channel_id}")
                    
                    # Optimize video fetching
                    if enable_duplication_check:
                        channel_videos = self.api_optimizer.optimize_video_fetch(
                            channel_id, tab_name, max_videos_per_channel
                        )
                    else:
                        channel_videos = self.youtube_service.get_channel_videos(
                            channel_id, max_videos_per_channel
                        )
                    
                    all_new_videos.extend(channel_videos)
                    progress.total_videos += len(channel_videos)
                    progress.processed_videos += len(channel_videos)
                    
                    # Add small delay to respect rate limits
                    time.sleep(0.2)
                    
                except ValidationError as e:
                    print(f"Invalid channel ID {channel_id}: {e}")
                    progress.errors += 1
                except Exception as e:
                    print(f"Error processing channel {channel_id}: {e}")
                    progress.errors += 1
            
            # Write videos to sheet with optimization
            if all_new_videos and not self._should_stop:
                progress.status = "writing_to_sheet"
                self._notify_progress(progress)
                
                print(f"Writing {len(all_new_videos)} videos to sheet...")
                
                # Use sheets optimizer for smart writing
                success = self.sheets_service.write_videos_to_sheet(tab_name, [
                    {
                        "video_id": video.video_id,
                        "title": video.title,
                        "url": video.url,
                        "published_at": video.published_at,
                        "view_count": video.view_count,
                        "duration": video.duration,
                        "like_count": video.like_count,
                        "comment_count": video.comment_count,
                        "channel_id": getattr(video, 'channel_id', ''),
                        "channel_title": getattr(video, 'channel_title', ''),
                        "description": getattr(video, 'description', ''),
                        "tags": getattr(video, 'tags', ''),
                        "added_date": datetime.now().isoformat()
                    }
                    for video in all_new_videos
                ])
                
                if success:
                    print("Videos written to sheet successfully")
                else:
                    print("Failed to write videos to sheet")
                    progress.errors += 1
            
            # Calculate final metrics
            end_time = time.time()
            total_time = end_time - start_time
            
            self._run_metrics = RunMetrics(
                total_time=total_time,
                videos_per_second=len(all_new_videos) / total_time if total_time > 0 else 0,
                api_calls_made=len(channels),
                cache_hit_rate=self.api_optimizer._optimization_metrics.cache_hits / max(1, self.api_optimizer._optimization_metrics.total_api_calls),
                memory_peak=psutil.Process().memory_info().rss / 1024 / 1024,  # MB
                cpu_peak=psutil.Process().cpu_percent(),
                efficiency_score=self._calculate_efficiency_score(progress)
            )
            
            progress.status = "completed"
            self._notify_progress(progress)
            
            return {
                "success": True,
                "videos_processed": len(all_new_videos),
                "duplicates_filtered": total_duplicates,
                "errors": progress.errors,
                "total_time": total_time,
                "metrics": self._run_metrics,
                "optimization_stats": self.sheets_optimizer.get_optimization_stats(tab_name)
            }
            
        except Exception as e:
            print(f"Error in optimized run: {e}")
            return {
                "success": False,
                "error": str(e),
                "videos_processed": 0,
                "duplicates_filtered": 0,
                "errors": 1
            }
        finally:
            self._is_running = False
    
    def _calculate_efficiency_score(self, progress: RunProgress) -> float:
        """Calculate overall efficiency score."""
        try:
            # Base score
            score = 1.0
            
            # Penalize errors
            if progress.errors > 0:
                error_penalty = min(0.5, progress.errors * 0.1)
                score -= error_penalty
            
            # Reward high processing rate
            if progress.total_videos > 0 and progress.processed_videos > 0:
                processing_rate = progress.processed_videos / progress.total_videos
                if processing_rate > 0.9:
                    score += 0.1
                elif processing_rate < 0.5:
                    score -= 0.2
            
            # Reward low duplicate rate
            if progress.total_videos > 0:
                duplicate_rate = progress.duplicates_filtered / progress.total_videos
                if duplicate_rate < 0.1:  # Less than 10% duplicates
                    score += 0.1
                elif duplicate_rate > 0.5:  # More than 50% duplicates
                    score -= 0.2
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            print(f"Error calculating efficiency score: {e}")
            return 0.5
    
    def get_progress_status(self) -> Dict[str, Any]:
        """Get current progress status."""
        return {
            'is_running': self._is_running,
            'current_progress': self._current_progress.__dict__ if hasattr(self, '_current_progress') and self._current_progress else None,
            'run_metrics': self._run_metrics,
            'optimization_active': True
        }
    
    def get_memory_status(self) -> Dict[str, Any]:
        """Get current memory usage status."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'memory_mb': memory_info.rss / 1024 / 1024,
                'memory_percent': process.memory_percent(),
                'optimization_active': True
            }
        except ImportError:
            return {
                'memory_mb': 'Unknown',
                'memory_percent': 'Unknown',
                'optimization_active': True
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            'run_metrics': self._run_metrics,
            'is_running': self._is_running,
            'optimization_active': True,
            'efficiency_score': self._calculate_efficiency_score(self._current_progress) if hasattr(self, '_current_progress') and self._current_progress else 0.0
        }
    
    def stop_run(self):
        """Stop the current run."""
        self._should_stop = True
        print("Stop signal sent")
    
    def get_run_status(self) -> Dict[str, Any]:
        """Get current run status."""
        return {
            "is_running": self._is_running,
            "should_stop": self._should_stop,
            "metrics": self._run_metrics,
            "optimization_report": self.api_optimizer.get_optimization_report()
        }
    
    def optimize_memory_usage(self):
        """Optimize memory usage by clearing caches."""
        try:
            # Clear all caches
            self.sheets_optimizer.clear_cache()
            self.api_optimizer.clear_optimization_cache()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            print("Memory optimization completed")
            
        except Exception as e:
            print(f"Error optimizing memory: {e}")
    
    def get_performance_recommendations(self) -> List[str]:
        """Get performance optimization recommendations."""
        recommendations = []
        
        try:
            # Check memory usage
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            if memory_usage > 500:  # More than 500MB
                recommendations.append("High memory usage detected. Consider reducing batch size or clearing caches.")
            
            # Check CPU usage
            cpu_usage = psutil.Process().cpu_percent()
            if cpu_usage > 80:  # More than 80% CPU
                recommendations.append("High CPU usage detected. Consider reducing concurrent operations.")
            
            # Check cache efficiency
            if self._run_metrics.cache_hit_rate < 0.5:  # Less than 50% cache hit rate
                recommendations.append("Low cache hit rate. Consider increasing cache TTL or improving cache keys.")
            
            # Check processing speed
            if self._run_metrics.videos_per_second < 1.0:  # Less than 1 video per second
                recommendations.append("Slow processing speed. Consider optimizing API calls or reducing data processing.")
            
            if not recommendations:
                recommendations.append("Performance is optimal. No recommendations at this time.")
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            recommendations.append("Unable to generate recommendations due to error.")
        
        return recommendations

# Import datetime for the run optimizer
from datetime import datetime

