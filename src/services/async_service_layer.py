"""
Async Service Layer
Implements async/await patterns for I/O operations following modern best practices
"""
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
import logging
import aiohttp
import aiofiles
from concurrent.futures import ThreadPoolExecutor

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.models import Video, Channel, RunConfig
from src.services.enhanced_error_handler import EnhancedErrorHandler, ErrorContext
from src.services.youtube_service import YouTubeService, YouTubeConfig
from src.services.sheets_service import SheetsService, SheetsConfig

@dataclass
class AsyncServiceConfig:
    """Configuration for async services."""
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 1
    enable_connection_pooling: bool = True
    connection_pool_size: int = 100

class AsyncYouTubeService:
    """Async YouTube service with modern patterns."""
    
    def __init__(self, config: YouTubeConfig, async_config: AsyncServiceConfig):
        self.config = config
        self.async_config = async_config
        self.error_handler = EnhancedErrorHandler()
        self.logger = logging.getLogger(__name__)
        
        # Thread pool for sync operations
        self.thread_pool = ThreadPoolExecutor(max_workers=async_config.max_concurrent_requests)
        
        # Session for HTTP requests
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_session()
    
    async def _initialize_session(self):
        """Initialize aiohttp session."""
        connector = aiohttp.TCPConnector(
            limit=self.async_config.connection_pool_size,
            limit_per_host=self.async_config.max_concurrent_requests,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=self.async_config.request_timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'YouTube2Sheets/1.0',
                'Accept': 'application/json'
            }
        )
    
    async def _close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
    
    async def fetch_videos_async(self, channel_ids: List[str], max_results: int = 50) -> AsyncGenerator[Video, None]:
        """Fetch videos asynchronously from multiple channels."""
        if not self.session:
            await self._initialize_session()
        
        # Create tasks for all channels
        tasks = [
            self._fetch_channel_videos_async(channel_id, max_results)
            for channel_id in channel_ids
        ]
        
        # Process channels concurrently
        async for videos in self._process_tasks_concurrently(tasks):
            for video in videos:
                yield video
    
    async def get_channel_videos_async(self, channel_id: str, max_results: int = 50) -> List[Video]:
        """Get videos from a channel asynchronously."""
        return await self._fetch_channel_videos_async(channel_id, max_results)
    
    async def _fetch_channel_videos_async(self, channel_id: str, max_results: int) -> List[Video]:
        """Fetch videos from a single channel asynchronously."""
        context = ErrorContext(
            service="YouTube",
            operation="fetch_channel_videos",
            timestamp=datetime.now(),
            additional_data={"channel_id": channel_id, "max_results": max_results}
        )
        
        try:
            # Run sync YouTube service in thread pool
            loop = asyncio.get_event_loop()
            youtube_service = YouTubeService(self.config)
            
            videos = await loop.run_in_executor(
                self.thread_pool,
                youtube_service.get_channel_videos,
                channel_id,
                max_results
            )
            
            return videos
            
        except Exception as error:
            error_response = self.error_handler.handle_generic_error(error, context)
            self.error_handler.log_error(error_response)
            return []
    
    async def _process_tasks_concurrently(self, tasks: List[asyncio.Task]) -> AsyncGenerator[List[Video], None]:
        """Process tasks concurrently with proper error handling."""
        semaphore = asyncio.Semaphore(self.async_config.max_concurrent_requests)
        
        async def process_with_semaphore(task):
            async with semaphore:
                try:
                    return await task
                except Exception as e:
                    self.logger.error(f"Task failed: {e}")
                    return []
        
        # Execute all tasks concurrently
        results = await asyncio.gather(
            *[process_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )
        
        # Yield results
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Task exception: {result}")
                yield []
            else:
                yield result
    
    async def search_videos_async(self, query: str, max_results: int = 50) -> List[Video]:
        """Search for videos asynchronously."""
        context = ErrorContext(
            service="YouTube",
            operation="search_videos",
            timestamp=datetime.now(),
            additional_data={"query": query, "max_results": max_results}
        )
        
        try:
            loop = asyncio.get_event_loop()
            youtube_service = YouTubeService(self.config)
            
            videos = await loop.run_in_executor(
                self.thread_pool,
                youtube_service.search_videos,
                query,
                max_results
            )
            
            return videos
            
        except Exception as error:
            error_response = self.error_handler.handle_generic_error(error, context)
            self.error_handler.log_error(error_response)
            return []

class AsyncSheetsService:
    """Async Google Sheets service with modern patterns."""
    
    def __init__(self, config: SheetsConfig, async_config: AsyncServiceConfig):
        self.config = config
        self.async_config = async_config
        self.error_handler = EnhancedErrorHandler()
        self.logger = logging.getLogger(__name__)
        
        # Thread pool for sync operations
        self.thread_pool = ThreadPoolExecutor(max_workers=async_config.max_concurrent_requests)
    
    async def write_videos_async(self, videos: List[Video], tab_name: str) -> bool:
        """Write videos to Google Sheets asynchronously."""
        context = ErrorContext(
            service="GoogleSheets",
            operation="write_videos",
            timestamp=datetime.now(),
            additional_data={"tab_name": tab_name, "video_count": len(videos)}
        )
        
        try:
            loop = asyncio.get_event_loop()
            sheets_service = SheetsService(self.config)
            
            success = await loop.run_in_executor(
                self.thread_pool,
                sheets_service.write_videos_to_sheet,
                videos,
                tab_name
            )
            
            return success
            
        except Exception as error:
            error_response = self.error_handler.handle_generic_error(error, context)
            self.error_handler.log_error(error_response)
            return False
    
    async def get_tabs_async(self) -> List[str]:
        """Get sheet tabs asynchronously."""
        context = ErrorContext(
            service="GoogleSheets",
            operation="get_tabs",
            timestamp=datetime.now()
        )
        
        try:
            loop = asyncio.get_event_loop()
            sheets_service = SheetsService(self.config)
            
            tabs = await loop.run_in_executor(
                self.thread_pool,
                sheets_service.get_sheet_tabs
            )
            
            return tabs
            
        except Exception as error:
            error_response = self.error_handler.handle_generic_error(error, context)
            self.error_handler.log_error(error_response)
            return []
    
    async def create_tab_async(self, tab_name: str) -> bool:
        """Create a new tab asynchronously."""
        context = ErrorContext(
            service="GoogleSheets",
            operation="create_tab",
            timestamp=datetime.now(),
            additional_data={"tab_name": tab_name}
        )
        
        try:
            loop = asyncio.get_event_loop()
            sheets_service = SheetsService(self.config)
            
            success = await loop.run_in_executor(
                self.thread_pool,
                sheets_service.create_sheet_tab,
                tab_name
            )
            
            return success
            
        except Exception as error:
            error_response = self.error_handler.handle_generic_error(error, context)
            self.error_handler.log_error(error_response)
            return False

class AsyncAutomator:
    """Async automator orchestrating all services."""
    
    def __init__(self, youtube_config: YouTubeConfig, sheets_config: SheetsConfig, async_config: AsyncServiceConfig):
        self.youtube_config = youtube_config
        self.sheets_config = sheets_config
        self.async_config = async_config
        self.logger = logging.getLogger(__name__)
    
    async def run_async_sync(self, channel_ids: List[str], tab_name: str, max_videos: int = 50) -> Dict[str, Any]:
        """Run async sync operation."""
        start_time = datetime.now()
        results = {
            "success": False,
            "videos_processed": 0,
            "videos_written": 0,
            "errors": [],
            "duration": 0.0
        }
        
        try:
            async with AsyncYouTubeService(self.youtube_config, self.async_config) as youtube_service:
                async_sheets_service = AsyncSheetsService(self.sheets_config, self.async_config)
                
                # Fetch videos asynchronously
                videos = []
                async for channel_videos in youtube_service.fetch_videos_async(channel_ids, max_videos):
                    videos.extend(channel_videos)
                
                results["videos_processed"] = len(videos)
                
                if videos:
                    # Write to sheets asynchronously
                    success = await async_sheets_service.write_videos_async(videos, tab_name)
                    results["success"] = success
                    results["videos_written"] = len(videos) if success else 0
                else:
                    results["success"] = True  # No videos to process
                
        except Exception as e:
            self.logger.error(f"Async sync failed: {e}")
            results["errors"].append(str(e))
        
        finally:
            end_time = datetime.now()
            results["duration"] = (end_time - start_time).total_seconds()
        
        return results

# Utility functions for async operations
async def run_async_operation(coro):
    """Run an async operation with proper error handling."""
    try:
        return await coro
    except Exception as e:
        logging.error(f"Async operation failed: {e}")
        raise

def create_async_config(**kwargs) -> AsyncServiceConfig:
    """Create async service configuration with defaults."""
    return AsyncServiceConfig(**kwargs)

# Example usage
async def example_async_usage():
    """Example of async service usage."""
    youtube_config = YouTubeConfig(api_key="your_api_key")
    sheets_config = SheetsConfig(
        service_account_file="path/to/service_account.json",
        spreadsheet_id="your_spreadsheet_id"
    )
    async_config = AsyncServiceConfig(
        max_concurrent_requests=5,
        request_timeout=30
    )
    
    automator = AsyncAutomator(youtube_config, sheets_config, async_config)
    
    results = await automator.run_async_sync(
        channel_ids=["UC_x5XG1OV2P6uZZ5FSM9Ttw"],
        tab_name="Test_Tab",
        max_videos=10
    )
    
    print(f"Sync results: {results}")

if __name__ == "__main__":
    # Example usage
    asyncio.run(example_async_usage())
