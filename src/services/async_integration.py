"""
Async Integration Layer
Integrates async services with the main application
"""
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.async_service_layer import AsyncAutomator, AsyncServiceConfig
from src.services.youtube_service import YouTubeService, YouTubeConfig
from src.services.sheets_service import SheetsService, SheetsConfig
from src.services.enhanced_logging import get_logger, log_context, LogContext

class AsyncIntegration:
    """Integration layer for async operations."""
    
    def __init__(self, youtube_config: YouTubeConfig, sheets_config: SheetsConfig):
        self.youtube_config = youtube_config
        self.sheets_config = sheets_config
        self.async_config = AsyncServiceConfig(
            max_concurrent_requests=10,
            request_timeout=30,
            retry_attempts=3
        )
        self.logger = get_logger("async_integration")
    
    async def run_async_sync(self, channel_ids: List[str], tab_name: str, max_videos: int = 50) -> Dict[str, Any]:
        """Run async sync operation with enhanced logging."""
        context = LogContext(
            service="AsyncIntegration",
            operation="run_async_sync",
            additional_data={
                "channel_ids": channel_ids,
                "tab_name": tab_name,
                "max_videos": max_videos
            }
        )
        
        with log_context(self.logger, context):
            self.logger.info(f"Starting async sync for {len(channel_ids)} channels")
            
            try:
                automator = AsyncAutomator(
                    self.youtube_config,
                    self.sheets_config,
                    self.async_config
                )
                
                results = await automator.run_async_sync(channel_ids, tab_name, max_videos)
                
                self.logger.info(
                    f"Async sync completed",
                    extra={
                        "videos_processed": results["videos_processed"],
                        "videos_written": results["videos_written"],
                        "success": results["success"],
                        "duration": results["duration"]
                    }
                )
                
                return results
                
            except Exception as e:
                self.logger.error(f"Async sync failed: {e}")
                return {
                    "success": False,
                    "videos_processed": 0,
                    "videos_written": 0,
                    "errors": [str(e)],
                    "duration": 0.0
                }
    
    def run_sync_with_async(self, channel_ids: List[str], tab_name: str, max_videos: int = 50) -> Dict[str, Any]:
        """Run sync operation using async integration."""
        return asyncio.run(self.run_async_sync(channel_ids, tab_name, max_videos))

# Utility function for easy integration
def create_async_integration(youtube_config: YouTubeConfig, sheets_config: SheetsConfig) -> AsyncIntegration:
    """Create async integration instance."""
    return AsyncIntegration(youtube_config, sheets_config)
