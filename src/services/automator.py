"""
YouTube2Sheets Automator Service
Orchestrates the YouTube to Google Sheets sync process.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)

from src.domain.models import Video, Channel, Filters, Destination, RunConfig, RunResult, RunStatus
from .youtube_service import YouTubeService, YouTubeConfig
from .sheets_service import SheetsService, SheetsConfig
from .async_service_layer import AsyncYouTubeService, AsyncServiceConfig
from src.utils.parsing import parse_channels, parse_keywords, is_youtube_short
from src.backend.api_optimizer import ResponseCache, VideoDeduplicator, APICreditTracker
from src.config.performance_config import get_performance_config


@dataclass
class AutomatorConfig:
    """Automator configuration."""
    youtube_api_key: str
    service_account_file: str
    spreadsheet_url: str
    max_videos_per_channel: int = 50
    batch_size: int = 100
    use_etag_cache: bool = True
    deduplicate: bool = True


class YouTubeToSheetsAutomator:
    """Main orchestrator for YouTube to Google Sheets sync."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = AutomatorConfig(
            youtube_api_key=config.get('youtube_api_key', ''),
            service_account_file=config.get('google_sheets_service_account_json', ''),
            spreadsheet_url=config.get('default_spreadsheet_url', '')
        )
        
        # Initialize performance optimizations first
        self.response_cache = ResponseCache("youtube_response_cache.json")
        self.video_deduplicator = VideoDeduplicator()
        self.api_credit_tracker = APICreditTracker(daily_quota=10000)
        
        # Background task tracking for proper cleanup
        self.background_tasks = set()
        
        # Performance metrics
        self.cache_hits = 0
        self.cache_misses = 0
        self.duplicates_prevented = 0
        
        # Initialize services
        youtube_config = YouTubeConfig(api_key=self.config.youtube_api_key)
        self.youtube_service = YouTubeService(youtube_config, shared_cache=self.response_cache, cache_tracker=self)
        
        # Initialize sheets service if credentials available
        if self.config.service_account_file:
            spreadsheet_id = self._extract_spreadsheet_id(self.config.spreadsheet_url)
            sheets_config = SheetsConfig(
                service_account_file=self.config.service_account_file,
                spreadsheet_id=spreadsheet_id
            )
            self.sheets_service = SheetsService(sheets_config)
        else:
            self.sheets_service = None
        
        # State tracking
        self.is_running = False
        self.current_progress = 0.0
        self.current_channel = ""
        self.processed_channels = 0
        self.total_channels = 0
        self.videos_processed = 0
        self.videos_written = 0
        self.errors = []
        
        # Thread pool for parallel operations
        self.perf_config = get_performance_config()
        self.thread_pool = ThreadPoolExecutor(max_workers=self.perf_config.max_workers)
    
    def __del__(self):
        """Cleanup resources on destruction."""
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources and shutdown thread pool."""
        try:
            if hasattr(self, 'thread_pool') and self.thread_pool:
                print("[CLEANUP] Shutting down thread pool...")
                self.thread_pool.shutdown(wait=True, cancel_futures=False)
                print("[CLEANUP] Thread pool shutdown complete")
        except Exception as e:
            print(f"[CLEANUP] Error during thread pool shutdown: {e}")
        
        # Cancel all background tasks
        try:
            if hasattr(self, 'background_tasks') and self.background_tasks:
                print("[CLEANUP] Cancelling background tasks...")
                for task in self.background_tasks:
                    if not task.done():
                        task.cancel()
                print(f"[CLEANUP] Cancelled {len(self.background_tasks)} background tasks")
        except Exception as e:
            print(f"[CLEANUP] Error cancelling background tasks: {e}")
        
        try:
            if hasattr(self, 'response_cache') and self.response_cache:
                print("[CLEANUP] Saving response cache...")
                self.response_cache._save_to_disk()
                print("[CLEANUP] Response cache saved")
        except Exception as e:
            print(f"[CLEANUP] Error saving response cache: {e}")
    
    def _extract_spreadsheet_id(self, url: str) -> str:
        """Extract spreadsheet ID from Google Sheets URL."""
        if not url:
            return ""
        
        if '/spreadsheets/d/' in url:
            start = url.find('/spreadsheets/d/') + len('/spreadsheets/d/')
            end = url.find('/', start)
            if end == -1:
                end = url.find('?', start)
            if end == -1:
                end = len(url)
            return url[start:end]
        
        return ""
    
    def sync_channels_optimized(self, run_config: RunConfig, use_parallel: bool = True) -> RunResult:
        """
        Optimized sync with automatic parallel/sequential selection.
        
        Args:
            run_config: Run configuration
            use_parallel: If True, use parallel processing for multiple channels
            
        Returns:
            RunResult with metrics
        """
        # For single channel or if parallel disabled, use sequential
        if len(run_config.channels) == 1 or not use_parallel:
            return self.sync_channels_to_sheets(run_config)
        
        # For multiple channels, use async parallel processing
        try:
            # Run async method in new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self.sync_channels_async_optimized(run_config))
                return result
            finally:
                loop.close()
        except Exception as e:
            print(f"[WARN] Async processing failed, falling back to sequential: {e}")
            return self.sync_channels_to_sheets(run_config)
    
    def sync_channel_to_sheet(self, channel_input: str, spreadsheet_url: str, tab_name: str, config: 'SyncConfig') -> bool:
        """
        Sync a single channel to Google Sheets.
        
        Args:
            channel_input: Channel ID, URL, or handle
            spreadsheet_url: Google Sheets URL
            tab_name: Target sheet tab name
            config: Sync configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a RunConfig for a single channel
            from src.domain.models import RunConfig, Filters, Destination
            run_config = RunConfig(
                channels=[channel_input],
                filters=Filters(
                    min_duration=config.min_duration_seconds or 0,  # FIXED: correct attribute name
                    keywords=config.keyword_filter.split(',') if config.keyword_filter else [],
                    keyword_mode=config.keyword_mode,
                    exclude_shorts=(config.min_duration_seconds or 0) < 60,  # FIXED: infer from min_duration
                    max_results=config.max_videos
                ),
                destination=Destination(
                    spreadsheet_id=self._extract_spreadsheet_id(spreadsheet_url),
                    tab_name=tab_name
                ),
                batch_size=100,  # FIXED: use default value
                rate_limit_delay=1.0  # FIXED: use default value
            )
            
            # Use the existing sync_channels_to_sheets method
            result = self.sync_channels_to_sheets(run_config)
            
            return result.status.value == "completed"
            
        except Exception as e:
            print(f"Error syncing channel {channel_input}: {e}")
            import traceback
            traceback.print_exc()  # Print full stack trace for debugging
            return False

    def sync_channels_to_sheets(self, run_config: RunConfig) -> RunResult:
        """
        Sync YouTube channels to Google Sheets with parallel processing.
        
        Args:
            run_config: Configuration for the sync run
            
        Returns:
            RunResult with success status and metrics
        """
        start_time = time.time()
        self.is_running = True
        self.errors = []
        self.videos_processed = 0
        self.videos_written = 0
        
        try:
            # Validate configuration
            if not self.youtube_service:
                raise Exception("YouTube service not initialized")
            
            if not self.sheets_service:
                raise Exception("Google Sheets service not initialized")
            
            # Setup phase: Ensure tab exists (defer table/formatting until we have data)
            tab_name = run_config.destination.tab_name
            table_created = False
            formatting_applied = False
            first_write_done = False
            
            # Ensure tab exists
            try:
                self.sheets_service.create_sheet_tab(tab_name)
                print(f"[OK] Tab '{tab_name}' ready")
            except Exception as e:
                print(f"[WARN] Tab setup warning: {e}")
                # Continue anyway - might be appending to existing tab
            
            # Load existing videos for deduplication
            try:
                existing_videos = self.sheets_service.read_data(tab_name, "A:A")
                if existing_videos:
                    # Mark existing video IDs as seen
                    video_ids = [row[0] for row in existing_videos[1:] if row]  # Skip header
                    self.video_deduplicator.mark_as_seen(video_ids, tab_name=tab_name)
                    print(f"[INFO] Loaded {len(video_ids)} existing videos for deduplication")
            except Exception as e:
                print(f"[WARN] Could not load existing videos: {e}")
            
            # PARALLEL PROCESSING: Process all channels concurrently
            self.total_channels = len(run_config.channels)
            self.processed_channels = 0
            
            print(f"[PARALLEL] Processing {len(run_config.channels)} channels concurrently...")
            
            # DYNAMIC WORKER CALCULATION: Optimize based on API quota and channel count
            optimal_workers = min(
                self.perf_config.concurrent_api_limit,  # API concurrent request limit
                len(run_config.channels),
                max(5, len(run_config.channels) // 2)  # At least 5, up to half of channels
            )
            print(f"[OPTIMIZATION] Using {optimal_workers} workers for {len(run_config.channels)} channels")
            
            # Use ThreadPoolExecutor for parallel channel processing
            with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
                # Create tasks for all channels
                future_to_channel = {
                    executor.submit(self._process_single_channel, channel_id, run_config.filters, tab_name): channel_id
                    for channel_id in run_config.channels
                }
                
                # ADAPTIVE BATCH SIZING: Dynamic based on total estimated videos
                video_batch = []
                total_estimated_videos = len(run_config.channels) * run_config.filters.max_results
                batch_size_limit = min(
                    self.perf_config.max_batch_size,  # Max batch size
                    max(self.perf_config.min_batch_size, int(total_estimated_videos * self.perf_config.batch_percentage))  # Configurable percentage, min batch size
                )
                print(f"[OPTIMIZATION] Using adaptive batch size: {batch_size_limit} (estimated {total_estimated_videos} total videos)")
                
                # Process completed channels as they finish
                for future in as_completed(future_to_channel):
                    channel_id = future_to_channel[future]
                    try:
                        channel_videos = future.result()
                        if channel_videos:
                            video_batch.extend(channel_videos)
                            self.videos_processed += len(channel_videos)
                        
                        self.processed_channels += 1
                        self.current_channel = channel_id
                        self._update_progress()
                        
                        # ADAPTIVE BATCHING: Write when batch is full or at end
                        should_write = (
                            len(video_batch) >= batch_size_limit or  # Batch full
                            self.processed_channels == len(run_config.channels)  # All channels done
                        )
                        
                        if should_write and video_batch:
                            # Write batch to sheets
                            success = self._write_video_batch(video_batch, tab_name, table_created, first_write_done)
                            if success:
                                self.videos_written += len(video_batch)
                                first_write_done = True
                                if not table_created:
                                    table_created = True
                                video_batch = []  # Clear batch
                        
                    except Exception as e:
                        error_msg = f"Channel {channel_id} failed: {e}"
                        print(f"[ERROR] {error_msg}")
                        self.errors.append(error_msg)
                        self.processed_channels += 1
                        self._update_progress()
            
            # Apply formatting once at the end if we wrote any data
            if first_write_done and not formatting_applied:
                try:
                    self.sheets_service.apply_conditional_formatting(tab_name)
                    formatting_applied = True
                    print(f"[OK] Conditional formatting applied to '{tab_name}'")
                except Exception as e:
                    print(f"[WARN] Could not apply formatting: {e}")
            
            # Calculate final metrics
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate cache efficiency
            total_cache_operations = self.cache_hits + self.cache_misses
            cache_hit_rate = (self.cache_hits / total_cache_operations * 100) if total_cache_operations > 0 else 0
            
            print(f"[SUMMARY] {self.processed_channels}/{self.total_channels} channels, {self.videos_processed} after filters, {self.duplicates_prevented} dupes, {self.videos_written} new")
            print(f"[PERFORMANCE] Cache hit rate: {(cache_hit_rate or 0):.1f}%, Duplicates prevented: {self.duplicates_prevented}")
            
            # Determine success status
            success_rate = self.processed_channels / self.total_channels if self.total_channels > 0 else 0
            status = RunStatus.COMPLETED if success_rate >= 0.8 else RunStatus.FAILED
            
            return RunResult(
                run_id=f"run_{int(time.time())}",
                status=status,
                start_time=datetime.fromtimestamp(start_time),
                end_time=datetime.now(),
                videos_processed=self.videos_processed,
                videos_written=self.videos_written,
                duration_seconds=duration,
                errors=self.errors,
                api_quota_used=self.youtube_service.get_quota_usage() if self.youtube_service else 0
            )
            
        except Exception as e:
            import traceback
            error_msg = f"Sync failed: {e}"
            full_trace = traceback.format_exc()
            print(f"[ERROR] {error_msg}")
            print(f"[TRACEBACK]\n{full_trace}")
            self.errors.append(f"{error_msg}\n{full_trace}")
            
            return RunResult(
                run_id=f"run_{int(time.time())}",
                status=RunStatus.FAILED,
                start_time=datetime.fromtimestamp(start_time),
                end_time=datetime.now(),
                videos_processed=self.videos_processed,
                videos_written=self.videos_written,
                duration_seconds=time.time() - start_time,
                errors=self.errors,
                api_quota_used=self.youtube_service.get_quota_usage() if self.youtube_service else 0
            )
        
        finally:
            self.is_running = False
            self.current_progress = 0.0
            self.current_channel = ""
    
    async def _process_channels_with_prefetching(self, async_yt, channels: List[str], filters: Filters, tab_name: str) -> List[List[Dict[str, Any]]]:
        """
        Process channels with predictive prefetching for maximum efficiency.
        
        Args:
            async_yt: Async YouTube service instance
            channels: List of channel IDs to process
            filters: Video filters to apply
            tab_name: Target sheet tab name
            
        Returns:
            List of results for each channel
        """
        results = []
        
        # Process channels in batches with prefetching
        batch_size = min(5, len(channels))  # Process 5 channels at a time
        
        for i in range(0, len(channels), batch_size):
            batch = channels[i:i + batch_size]
            
            # Create tasks for current batch
            tasks = []
            for channel_id in batch:
                task = self._process_single_channel_async(async_yt, channel_id, filters, tab_name)
                tasks.append(task)
            
            # Process batch concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)
            
            # Prefetch next batch if there are more channels
            if i + batch_size < len(channels):
                next_batch = channels[i + batch_size:i + 2 * batch_size]
                # Start prefetching next batch in background
                prefetch_tasks = []
                for channel_id in next_batch:
                    # Prefetch channel data without processing
                    prefetch_task = async_yt.get_channel_videos_async(channel_id, filters.max_results)
                    prefetch_tasks.append(prefetch_task)
                
                # Create background task and track for cleanup
                if prefetch_tasks:
                    task = asyncio.create_task(asyncio.gather(*prefetch_tasks, return_exceptions=True))
                    self.background_tasks.add(task)
                    task.add_done_callback(self.background_tasks.discard)
        
        return results

    async def _process_single_channel_async(self, async_yt, channel_id: str, filters: Filters, tab_name: str) -> List[Dict[str, Any]]:
        """
        Process a single channel asynchronously with connection pooling.
        
        Args:
            async_yt: Async YouTube service instance
            channel_id: YouTube channel ID or handle
            filters: Video filters to apply
            tab_name: Target sheet tab name
            
        Returns:
            List of video dictionaries ready for writing
        """
        try:
            # Get videos from channel using async service
            videos = await async_yt.get_channel_videos_async(channel_id, filters.max_results)
            
            # Apply filters
            filtered_videos = self._apply_filters(videos, filters)
            
            # Convert to dict format for sheets
            video_dicts = [video.to_dict() for video in filtered_videos]
            
            # DEDUPLICATION: Filter out duplicates
            video_ids = [v.get('id') or v.get('video_id', '') for v in video_dicts]
            new_video_ids = self.video_deduplicator.filter_new_videos(
                video_ids, 
                channel_id=channel_id, 
                tab_name=tab_name
            )
            
            # Keep only new videos
            new_videos = [v for v in video_dicts if (v.get('id') or v.get('video_id', '')) in new_video_ids]
            duplicates_count = len(video_dicts) - len(new_videos)
            
            if duplicates_count > 0:
                self.duplicates_prevented += duplicates_count
                print(f"[REFRESH] Skipped {duplicates_count} duplicates for {channel_id}")
            
            return new_videos
            
        except Exception as e:
            print(f"[ERROR] Channel {channel_id} async processing failed: {e}")
            return []

    def _process_single_channel(self, channel_id: str, filters: Filters, tab_name: str) -> List[Dict[str, Any]]:
        """
        Process a single channel and return its videos.
        
        Args:
            channel_id: YouTube channel ID or handle
            filters: Video filters to apply
            tab_name: Target sheet tab name
            
        Returns:
            List of video dictionaries ready for writing
        """
        try:
            # Get videos from channel
            videos = self.youtube_service.get_channel_videos(channel_id, filters.max_results)
            
            # Apply filters
            filtered_videos = self._apply_filters(videos, filters)
            
            # Convert to dict format for sheets
            video_dicts = [video.to_dict() for video in filtered_videos]
            
            # DEDUPLICATION: Filter out duplicates
            video_ids = [v.get('id') or v.get('video_id', '') for v in video_dicts]
            new_video_ids = self.video_deduplicator.filter_new_videos(
                video_ids, 
                channel_id=channel_id, 
                tab_name=tab_name
            )
            
            # Keep only new videos
            new_videos = [v for v in video_dicts if (v.get('id') or v.get('video_id', '')) in new_video_ids]
            duplicates_count = len(video_dicts) - len(new_videos)
            
            if duplicates_count > 0:
                self.duplicates_prevented += duplicates_count
                print(f"[REFRESH] Skipped {duplicates_count} duplicates for {channel_id}")
            
            return new_videos
            
        except Exception as e:
            print(f"[ERROR] Channel {channel_id} processing failed: {e}")
            return []
    
    def _write_video_batch(self, video_batch: List[Dict[str, Any]], tab_name: str, table_created: bool, first_write_done: bool) -> bool:
        """
        Write a batch of videos to Google Sheets.
        
        Args:
            video_batch: List of video dictionaries to write
            tab_name: Target sheet tab name
            table_created: Whether table structure has been created
            first_write_done: Whether this is the first write operation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not video_batch:
                return True
            
            # Create table structure on first write
            if not table_created and first_write_done:
                try:
                    self.sheets_service.create_table_structure(tab_name)
                    print(f"[OK] Table structure created for '{tab_name}'")
                except Exception as e:
                    print(f"[WARN] Could not create table structure: {e}")
            
            # Write videos to sheet
            success = self.sheets_service.write_videos_to_sheet(tab_name, video_batch)
            if success:
                print(f"[WRITE] Wrote {len(video_batch)} videos to '{tab_name}'")
            else:
                print(f"[WARN] Failed to write batch to '{tab_name}'")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] Batch write failed: {e}")
            return False
    
    async def _fetch_channel_videos_async(self, channel_id: str, max_results: int, filters: Filters) -> tuple[str, List[Dict[str, Any]]]:
        """Async wrapper to fetch and filter videos from a single channel."""
        loop = asyncio.get_event_loop()
        try:
            # Run sync operation in thread pool
            videos = await loop.run_in_executor(
                self.thread_pool,
                self.youtube_service.get_channel_videos,
                channel_id,
                max_results
            )
            
            # Log fetched count
            print(f"[DEBUG] {channel_id}: Fetched {len(videos)} raw videos from YouTube")
            logger.info(f"[DEBUG] {channel_id}: Fetched {len(videos)} raw videos from YouTube")
            # Log to GUI for visibility
            logger.info(f"[CHANNEL] {channel_id}: Fetched {len(videos)} videos from YouTube")
            
            # Apply filters
            filtered_videos = self._apply_filters(videos, filters)
            
            # Log filtered count
            if len(filtered_videos) == 0 and len(videos) > 0:
                # All videos filtered out - log warning
                logger.warning(f"[FILTER] {channel_id}: ALL {len(videos)} videos filtered out!")
                logger.warning(f"[FILTER] Active filters: keywords={filters.keywords}, keyword_mode={filters.keyword_mode}, min_duration={filters.min_duration}")
            elif len(filtered_videos) < len(videos):
                # Some videos filtered
                logger.info(f"[FILTER] {channel_id}: {len(filtered_videos)}/{len(videos)} videos passed filters")
                print(f"[DEBUG] {channel_id}: {len(filtered_videos)} videos after filters (removed {len(videos) - len(filtered_videos)})")
            elif len(videos) > 0:
                # All videos passed
                logger.info(f"[FILTER] {channel_id}: All {len(videos)} videos passed filters")
            
            # Convert to dict
            video_dicts = [video.to_dict() for video in filtered_videos]
            
            return (channel_id, video_dicts)
        except Exception as e:
            logger.error(f"[ERROR] Failed to fetch {channel_id}: {e}")
            logger.error(f"[ERROR] Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
            return (channel_id, [])
    
    async def sync_channels_async_optimized(self, run_config: RunConfig) -> RunResult:
        """
        Ultra-optimized async sync with connection pooling and predictive prefetching.
        
        Args:
            run_config: Run configuration
            
        Returns:
            RunResult with metrics
        """
        start_time = time.time()
        self.is_running = True
        self.errors = []
        self.videos_processed = 0
        self.videos_written = 0
        
        try:
            # Validate configuration
            if not self.youtube_service:
                raise Exception("YouTube service not initialized")
            
            if not self.sheets_service:
                raise Exception("Google Sheets service not initialized")
            
            # Setup phase: Ensure tab exists
            tab_name = run_config.destination.tab_name
            table_created = False
            formatting_applied = False
            first_write_done = False
            
            # Ensure tab exists
            try:
                self.sheets_service.create_sheet_tab(tab_name)
                print(f"[OK] Tab '{tab_name}' ready")
            except Exception as e:
                print(f"[WARN] Tab setup warning: {e}")
            
            # Load existing videos for deduplication
            try:
                existing_videos = self.sheets_service.read_data(tab_name, "A:A")
                if existing_videos:
                    video_ids = [row[0] for row in existing_videos[1:] if row]
                    self.video_deduplicator.mark_as_seen(video_ids, tab_name=tab_name)
                    print(f"[INFO] Loaded {len(video_ids)} existing videos for deduplication")
            except Exception as e:
                print(f"[WARN] Could not load existing videos: {e}")
            
            # ASYNC PARALLEL PROCESSING with connection pooling
            self.total_channels = len(run_config.channels)
            self.processed_channels = 0
            
            print(f"[ASYNC] Processing {len(run_config.channels)} channels with connection pooling...")
            
            # Create async service with optimized config
            async_config = AsyncServiceConfig(
                max_concurrent_requests=min(10, len(run_config.channels)),
                enable_connection_pooling=True,
                connection_pool_size=100
            )
            
            async with AsyncYouTubeService(YouTubeConfig(api_key=self.config.youtube_api_key), async_config) as async_yt:
                # PREDICTIVE PREFETCHING: Process channels with prefetching
                all_results = await self._process_channels_with_prefetching(async_yt, run_config.channels, run_config.filters, tab_name)
                
                # Accumulate results and write in batches
                video_batch = []
                batch_size_limit = 1000
                
                for i, result in enumerate(all_results):
                    channel_id = run_config.channels[i]
                    
                    if isinstance(result, Exception):
                        error_msg = f"Channel {channel_id} failed: {result}"
                        print(f"[ERROR] {error_msg}")
                        self.errors.append(error_msg)
                    else:
                        channel_videos = result
                        if channel_videos:
                            video_batch.extend(channel_videos)
                            self.videos_processed += len(channel_videos)
                    
                    self.processed_channels += 1
                    self.current_channel = channel_id
                    self._update_progress()
                    
                    # Write batch when full or at end
                    should_write = (
                        len(video_batch) >= batch_size_limit or
                        self.processed_channels == len(run_config.channels)
                    )
                    
                    if should_write and video_batch:
                        success = self._write_video_batch(video_batch, tab_name, table_created, first_write_done)
                        if success:
                            self.videos_written += len(video_batch)
                            first_write_done = True
                            if not table_created:
                                table_created = True
                            video_batch = []
            
            # Apply formatting once at the end
            if first_write_done and not formatting_applied:
                try:
                    self.sheets_service.apply_conditional_formatting(tab_name)
                    formatting_applied = True
                    print(f"[OK] Conditional formatting applied to '{tab_name}'")
                except Exception as e:
                    print(f"[WARN] Could not apply formatting: {e}")
            
            # Calculate final metrics
            end_time = time.time()
            duration = end_time - start_time
            
            total_cache_operations = self.cache_hits + self.cache_misses
            cache_hit_rate = (self.cache_hits / total_cache_operations * 100) if total_cache_operations > 0 else 0
            
            print(f"[SUMMARY] {self.processed_channels}/{self.total_channels} channels, {self.videos_processed} after filters, {self.duplicates_prevented} dupes, {self.videos_written} new")
            print(f"[PERFORMANCE] Cache hit rate: {(cache_hit_rate or 0):.1f}%, Duplicates prevented: {self.duplicates_prevented}")
            
            success_rate = self.processed_channels / self.total_channels if self.total_channels > 0 else 0
            status = RunStatus.COMPLETED if success_rate >= 0.8 else RunStatus.FAILED
            
            return RunResult(
                run_id=f"async_run_{int(time.time())}",
                status=status,
                start_time=datetime.fromtimestamp(start_time),
                end_time=datetime.now(),
                videos_processed=self.videos_processed,
                videos_written=self.videos_written,
                duration_seconds=duration,
                errors=self.errors,
                api_quota_used=self.youtube_service.get_quota_usage() if self.youtube_service else 0
            )
            
        except Exception as e:
            error_msg = f"Async sync failed: {e}"
            print(f"[ERROR] {error_msg}")
            self.errors.append(error_msg)
            
            return RunResult(
                run_id=f"async_run_{int(time.time())}",
                status=RunStatus.FAILED,
                start_time=datetime.fromtimestamp(start_time),
                end_time=datetime.now(),
                videos_processed=self.videos_processed,
                videos_written=self.videos_written,
                errors=self.errors
            )
        finally:
            self.is_running = False

    async def sync_channels_parallel(self, run_config: RunConfig) -> RunResult:
        """
        PARALLEL sync implementation for maximum speed.
        Fetches all channels concurrently, then writes in optimized batches.
        """
        start_time = time.time()
        self.is_running = True
        self.errors = []
        self.videos_processed = 0
        self.videos_written = 0
        
        try:
            # Validate
            if not self.youtube_service or not self.sheets_service:
                raise Exception("Services not initialized")
            
            tab_name = run_config.destination.tab_name
            table_created = False
            first_write_done = False
            
            # Ensure tab exists
            try:
                self.sheets_service.create_sheet_tab(tab_name)
                print(f"[OK] Tab '{tab_name}' ready")
            except Exception as e:
                print(f"[WARN] Tab setup: {e}")
            
            # Load existing videos for deduplication
            try:
                existing_videos = self.sheets_service.read_data(tab_name, "A:A")
                if existing_videos:
                    video_ids = [row[0] for row in existing_videos[1:] if row]
                    self.video_deduplicator.mark_as_seen(video_ids, tab_name=tab_name)
                    print(f"[INFO] Loaded {len(video_ids)} existing videos for deduplication")
            except Exception as e:
                print(f"[WARN] Could not load existing videos: {e}")
            
            # PARALLEL FETCH: Create tasks for all channels
            print(f"[LAUNCH] Fetching {len(run_config.channels)} channels in parallel...")
            tasks = [
                self._fetch_channel_videos_async(
                    channel_id,
                    run_config.filters.max_results,
                    run_config.filters
                )
                for channel_id in run_config.channels
            ]
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and apply deduplication
            all_new_videos = []
            total_fetched = 0
            total_after_filters = 0
            total_duplicates = 0
            failed_channels = 0
            
            for result in results:
                if isinstance(result, Exception):
                    self.errors.append(str(result))
                    failed_channels += 1
                    print(f"[ERROR] Channel task failed: {result}")
                    continue
                
                channel_id, video_dicts = result
                total_after_filters += len(video_dicts)
                
                if not video_dicts:
                    print(f"[DEBUG] {channel_id}: 0 videos after filtering")
                    continue
                
                # Deduplication
                video_ids = [v.get('id') or v.get('video_id', '') for v in video_dicts]
                new_video_ids = self.video_deduplicator.filter_new_videos(
                    video_ids,
                    channel_id=channel_id,
                    tab_name=tab_name
                )
                
                new_videos = [v for v in video_dicts if (v.get('id') or v.get('video_id', '')) in new_video_ids]
                duplicates_count = len(video_dicts) - len(new_videos)
                total_duplicates += duplicates_count
                
                if duplicates_count > 0:
                    self.duplicates_prevented += duplicates_count
                    print(f"[DEBUG] {channel_id}: Skipped {duplicates_count} duplicates, keeping {len(new_videos)}")
                
                all_new_videos.extend(new_videos)
                self.videos_processed += len(video_dicts)
            
            # Comprehensive summary logging
            logger.info(f"")
            logger.info(f"=" * 60)
            logger.info(f"[SUMMARY] Parallel Fetch Complete")
            logger.info(f"=" * 60)
            logger.info(f"Channels processed: {len(results) - failed_channels}/{len(results)}")
            logger.info(f"Failed channels: {failed_channels}")
            logger.info(f"Videos after filters: {total_after_filters}")
            logger.info(f"Duplicates removed: {total_duplicates}")
            logger.info(f"New videos to write: {len(all_new_videos)}")
            logger.info(f"=" * 60)
            logger.info(f"")
            
            # Also print for console
            print(f"[SUMMARY] {len(results) - failed_channels}/{len(results)} channels, {total_after_filters} after filters, {total_duplicates} dupes, {len(all_new_videos)} new")
            
            # BATCH WRITE: Write all videos in optimized batches
            if all_new_videos:
                # Create table on first write
                if not first_write_done:
                    try:
                        self.sheets_service.create_table_structure(tab_name)
                        print(f"[OK] Table structure created")
                        table_created = True
                        first_write_done = True
                    except Exception as e:
                        print(f"[WARN] Table creation: {e}")
                
                # Smart batching based on total size
                batch_size = 1000 if len(all_new_videos) > 1000 else len(all_new_videos)
                
                for i in range(0, len(all_new_videos), batch_size):
                    batch = all_new_videos[i:i + batch_size]
                    success = self.sheets_service.write_videos_to_sheet(tab_name, batch)
                    
                    if success:
                        self.videos_written += len(batch)
                        print(f"[OK] Batch {i//batch_size + 1}: {len(batch)} videos written")
                    else:
                        print(f"[WARN] Failed to write batch {i//batch_size + 1}")
                
                # Apply formatting once at end
                if table_created:
                    try:
                        self.sheets_service.apply_conditional_formatting(tab_name)
                        print(f"[OK] Conditional formatting applied")
                    except Exception as e:
                        print(f"[WARN] Formatting: {e}")
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Create result
            from src.domain.models import RunStatus
            status = RunStatus.COMPLETED if len(self.errors) == 0 else RunStatus.FAILED
            print(f"[DEBUG] Returning RunResult with status: {status}, videos_written: {self.videos_written}")
            logger.info(f"[DEBUG] Returning RunResult with status: {status}, videos_written: {self.videos_written}")
            
            return RunResult(
                run_id=f"run_parallel_{int(time.time())}",
                status=status,
                start_time=datetime.fromtimestamp(start_time),
                end_time=datetime.now(),
                videos_processed=self.videos_processed,
                videos_written=self.videos_written,
                errors=self.errors,
                duration_seconds=duration,
                api_quota_used=self.youtube_service.get_quota_usage()
            )
            
        except Exception as e:
            duration = time.time() - start_time
            from src.domain.models import RunStatus
            return RunResult(
                run_id=f"run_parallel_{int(time.time())}",
                status=RunStatus.FAILED,
                start_time=datetime.fromtimestamp(start_time),
                end_time=datetime.now(),
                videos_processed=self.videos_processed,
                videos_written=self.videos_written,
                errors=self.errors + [str(e)],
                duration_seconds=duration,
                api_quota_used=self.youtube_service.get_quota_usage() if self.youtube_service else 0
            )
        finally:
            self.is_running = False
    
    def _apply_filters(self, videos: List[Video], filters: Filters) -> List[Video]:
        """Apply filters to video list."""
        filtered_videos = []
        
        for video in videos:
            # Duration filter - skip if video is SHORTER than minimum
            if filters.min_duration and video.duration < filters.min_duration:
                continue
            
            # Exclude shorts filter
            if filters.exclude_shorts and is_youtube_short(video.video_id, video.duration):
                continue
            
            # Keywords filter (if keyword_mode is "include", require at least one keyword match)
            if filters.keywords and filters.keyword_mode == "include":
                title_desc = f"{video.title} {video.description}".lower()
                if not any(keyword.lower() in title_desc for keyword in filters.keywords):
                    continue
            
            # Keywords filter (if keyword_mode is "exclude", skip if any keyword matches)
            if filters.keywords and filters.keyword_mode == "exclude":
                title_desc = f"{video.title} {video.description}".lower()
                if any(keyword.lower() in title_desc for keyword in filters.keywords):
                    continue
            
            # If we made it here, video passes all filters
            filtered_videos.append(video)
        
        return filtered_videos
    
    def _update_progress(self):
        """Update progress tracking."""
        if self.total_channels > 0:
            self.current_progress = (self.processed_channels / self.total_channels) * 100
        else:
            self.current_progress = 0.0
    
    def cancel_sync(self):
        """Cancel the current sync operation."""
        self.is_running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the automator."""
        return {
            'is_running': self.is_running,
            'progress': self.current_progress,
            'current_channel': self.current_channel,
            'processed_channels': self.processed_channels,
            'total_channels': self.total_channels,
            'videos_processed': self.videos_processed,
            'videos_written': self.videos_written,
            'errors': self.errors
        }
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration status."""
        return {
            'youtube_api_configured': bool(self.config.youtube_api_key),
            'sheets_configured': bool(self.config.service_account_file),
            'spreadsheet_configured': bool(self.config.spreadsheet_url),
            'optimization_enabled': self.config.use_etag_cache and self.config.deduplicate
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            'youtube_service': 'Active' if self.youtube_service else 'Inactive',
            'sheets_service': 'Active' if self.sheets_service else 'Inactive',
            'optimization_active': True
        }
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get optimization status with live metrics."""
        # Get cache statistics with defensive programming
        try:
            cache_stats = self.response_cache.get_statistics()
            if not isinstance(cache_stats, dict):
                cache_stats = {}
        except Exception:
            cache_stats = {}
        
        # Get deduplication statistics with defensive programming
        try:
            dedup_stats = self.video_deduplicator.get_statistics()
            if not isinstance(dedup_stats, dict):
                dedup_stats = {}
        except Exception:
            dedup_stats = {}
        
        # Safely extract values with proper defaults
        cache_hit_rate = cache_stats.get('hit_rate', 0)
        if cache_hit_rate is None:
            cache_hit_rate = 0
        
        return {
            'etag_caching': self.config.use_etag_cache,
            'deduplication': self.config.deduplicate,
            'batch_processing': self.config.batch_size,
            'max_videos_per_channel': self.config.max_videos_per_channel,
            'optimization_active': True,
            # Live performance metrics with safe formatting
            'cache_hit_rate': f"{float(cache_hit_rate):.1f}%",
            'cache_entries': cache_stats.get('entries', 0),
            'duplicates_prevented': dedup_stats.get('duplicates_prevented', 0),
            'seen_videos': dedup_stats.get('seen_videos', 0),
            'api_quota_status': self.api_credit_tracker.get_status()
        }
