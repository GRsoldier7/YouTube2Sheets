"""
Async Wrapper Service
Provides async wrappers for existing synchronous services
"""
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.youtube_service import YouTubeService, YouTubeConfig
from src.services.sheets_service import SheetsService, SheetsConfig
from src.services.enhanced_logging import get_logger, log_context, LogContext, performance_monitoring
from src.services.enhanced_error_handler import EnhancedErrorHandler, ErrorContext

class AsyncWrapper:
    """Async wrapper for synchronous services."""
    
    def __init__(self, youtube_config: YouTubeConfig, sheets_config: SheetsConfig):
        self.youtube_config = youtube_config
        self.sheets_config = sheets_config
        self.error_handler = EnhancedErrorHandler()
        self.logger = get_logger("async_wrapper")
        
        # Thread pool for running sync operations
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
    
    async def fetch_videos_async(self, channel_ids: List[str], max_results: int = 50) -> List[Dict[str, Any]]:
        """Fetch videos asynchronously from multiple channels."""
        context = LogContext(
            service="AsyncWrapper",
            operation="fetch_videos_async",
            additional_data={"channel_ids": channel_ids, "max_results": max_results}
        )
        
        with log_context(self.logger, context):
            self.logger.info(f"Starting async fetch for {len(channel_ids)} channels")
            
            try:
                with performance_monitoring(self.logger, "async_fetch_videos") as monitor:
                    # Create tasks for all channels
                    tasks = [
                        self._fetch_channel_videos_async(channel_id, max_results)
                        for channel_id in channel_ids
                    ]
                    
                    # Execute all tasks concurrently
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Flatten results and filter out exceptions
                    all_videos = []
                    for result in results:
                        if isinstance(result, Exception):
                            self.logger.error(f"Channel fetch failed: {result}")
                        else:
                            all_videos.extend(result)
                    
                    monitor["increment_api_calls"]()
                    self.logger.info(f"Async fetch completed: {len(all_videos)} videos")
                    
                    return all_videos
                    
            except Exception as e:
                error_context = ErrorContext(
                    service="AsyncWrapper",
                    operation="fetch_videos_async",
                    timestamp=datetime.now()
                )
                error_response = self.error_handler.handle_generic_error(e, error_context)
                self.error_handler.log_error(error_response)
                return []
    
    async def _fetch_channel_videos_async(self, channel_id: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch videos from a single channel asynchronously."""
        try:
            # Run sync operation in thread pool
            loop = asyncio.get_event_loop()
            youtube_service = YouTubeService(self.youtube_config)
            
            videos = await loop.run_in_executor(
                self.thread_pool,
                youtube_service.fetch_channel_videos,
                channel_id,
                max_results
            )
            
            return videos if videos else []
            
        except Exception as e:
            self.logger.error(f"Channel {channel_id} fetch failed: {e}")
            return []
    
    async def write_videos_async(self, videos: List[Dict[str, Any]], tab_name: str) -> bool:
        """Write videos to Google Sheets asynchronously."""
        context = LogContext(
            service="AsyncWrapper",
            operation="write_videos_async",
            additional_data={"tab_name": tab_name, "video_count": len(videos)}
        )
        
        with log_context(self.logger, context):
            self.logger.info(f"Starting async write to {tab_name}")
            
            try:
                with performance_monitoring(self.logger, "async_write_videos") as monitor:
                    # Run sync operation in thread pool
                    loop = asyncio.get_event_loop()
                    sheets_service = SheetsService(self.sheets_config)
                    
                    success = await loop.run_in_executor(
                        self.thread_pool,
                        sheets_service.write_videos_to_sheet,
                        videos,
                        tab_name
                    )
                    
                    monitor["increment_api_calls"]()
                    self.logger.info(f"Async write completed: {success}")
                    
                    return success
                    
            except Exception as e:
                error_context = ErrorContext(
                    service="AsyncWrapper",
                    operation="write_videos_async",
                    timestamp=datetime.now()
                )
                error_response = self.error_handler.handle_generic_error(e, error_context)
                self.error_handler.log_error(error_response)
                return False
    
    async def get_tabs_async(self) -> List[str]:
        """Get sheet tabs asynchronously."""
        context = LogContext(
            service="AsyncWrapper",
            operation="get_tabs_async"
        )
        
        with log_context(self.logger, context):
            try:
                with performance_monitoring(self.logger, "async_get_tabs") as monitor:
                    # Run sync operation in thread pool
                    loop = asyncio.get_event_loop()
                    sheets_service = SheetsService(self.sheets_config)
                    
                    tabs = await loop.run_in_executor(
                        self.thread_pool,
                        sheets_service.get_sheet_tabs
                    )
                    
                    monitor["increment_api_calls"]()
                    self.logger.info(f"Async get tabs completed: {len(tabs)} tabs")
                    
                    return tabs if tabs else []
                    
            except Exception as e:
                error_context = ErrorContext(
                    service="AsyncWrapper",
                    operation="get_tabs_async",
                    timestamp=datetime.now()
                )
                error_response = self.error_handler.handle_generic_error(e, error_context)
                self.error_handler.log_error(error_response)
                return []
    
    def run_async_operation(self, coro):
        """Run an async operation with proper error handling."""
        try:
            return asyncio.run(coro)
        except Exception as e:
            self.logger.error(f"Async operation failed: {e}")
            raise

# Utility function for easy integration
def create_async_wrapper(youtube_config: YouTubeConfig, sheets_config: SheetsConfig) -> AsyncWrapper:
    """Create async wrapper instance."""
    return AsyncWrapper(youtube_config, sheets_config)
