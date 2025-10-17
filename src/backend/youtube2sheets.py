"""Refactored core automation engine for YouTube2Sheets."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .api_optimizer import APICreditTracker, ResponseCache, VideoDeduplicator
from .data_processor import VideoRecord, build_video_record
from .exceptions import APIError, ProcessingError, ValidationError
from .filters import apply_filters
from .scheduler_sheet_manager import SchedulerSheetManager
from .security_manager import default_spreadsheet_url, get_env_var, validate_service_account_path
from .sheet_formatter import SheetFormatter

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
DEFAULT_HEADERS = [
    "ChannelID",
    "YT Channel",
    "Date of Video",
    "Short_Long",
    "Video Length",
    "Video Title",
    "Video Link",
    "Views",
    "Likes",
    "Comments",
    "NotebookLM",
    "Date Added",
]


@dataclass(slots=True)
class SyncConfig:
    """Filtering and sync options supplied by the GUI or CLI."""

    min_duration_seconds: Optional[int] = None
    max_duration_seconds: Optional[int] = None
    keyword_filter: Optional[str] = None
    keyword_mode: str = "include"  # include or exclude
    max_videos: int = 50

    def keywords(self) -> List[str]:
        if not self.keyword_filter:
            return []
        return [kw.strip() for kw in self.keyword_filter.split(",") if kw.strip()]


class YouTubeToSheetsAutomator:
    """High-level orchestrator to fetch data from YouTube and write to Google Sheets."""

    def __init__(
        self,
        youtube_api_key: Optional[str] = None,
        service_account_file: Optional[str] = None,
        *,
        spreadsheet_url: Optional[str] = None,
        quota_tracker: Optional[APICreditTracker] = None,
        response_cache: Optional[ResponseCache] = None,
    ) -> None:
        youtube_key = youtube_api_key or get_env_var("YOUTUBE_API_KEY")
        credentials_file = validate_service_account_path(
            service_account_file or get_env_var("GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON")
        )

        self._spreadsheet_url = spreadsheet_url or default_spreadsheet_url()

        # Instantiate Google APIs
        self.youtube_service = build("youtube", "v3", developerKey=youtube_key)
        self.sheets_service = build("sheets", "v4", credentials=self._build_credentials(credentials_file))

        self.quota_tracker = quota_tracker or APICreditTracker()
        self.response_cache = response_cache or ResponseCache()
        self.video_deduplicator = VideoDeduplicator()
        self.scheduler: Optional[SchedulerSheetManager] = None
        
        # Sheet formatter for automatic Table creation
        sheet_id = self.extract_sheet_id(self._spreadsheet_url) if self._spreadsheet_url else None
        self.sheet_formatter = SheetFormatter(self.sheets_service, sheet_id) if sheet_id else None
    
    def _normalize_channel_input(self, channel_input: str) -> Optional[str]:
        """
        Normalize various YouTube channel input formats to channel ID.
        
        Args:
            channel_input: Channel input in various formats (@handle, URL, UC...)
            
        Returns:
            Normalized channel ID or None if invalid
        """
        import re
        
        channel_input = channel_input.strip()
        
        # Already a channel ID (UC...)
        if channel_input.startswith('UC') and len(channel_input) == 24:
            return channel_input
        
        # @handle format
        if channel_input.startswith('@'):
            # For now, return as-is since we'd need to resolve to channel ID
            return channel_input
        
        # URL formats
        url_patterns = [
            r'youtube\.com/@([^/?]+)',
            r'youtube\.com/channel/([^/?]+)',
            r'youtube\.com/c/([^/?]+)',
            r'youtube\.com/user/([^/?]+)'
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, channel_input)
            if match:
                return match.group(1)
        
        # If no pattern matches, return as-is
        return channel_input

        logger.info("YouTubeToSheetsAutomator initialized with enhanced API optimization")

    @staticmethod
    def _build_credentials(service_account_file: str):
        from google.oauth2.service_account import Credentials

        return Credentials.from_service_account_file(service_account_file, scopes=SCOPES)

    # ------------------------------------------------------------------
    # Channel helpers
    # ------------------------------------------------------------------

    def extract_channel_id(self, channel_input: str) -> str:
        if channel_input.startswith("UC") and len(channel_input) == 24:
            return channel_input

        if channel_input.startswith("@"):  # handle handles directly
            channel_id = self._lookup_channel_by_query(channel_input[1:])
            if channel_id:
                return channel_id

        if "youtube.com" in channel_input:
            channel_id = self._extract_from_url(channel_input)
            if channel_id:
                return channel_id

        # Fallback: assume caller provided the ID
        return channel_input

    def _lookup_channel_by_query(self, query: str) -> Optional[str]:
        try:
            self.quota_tracker.consume(100)
            response = (
                self.youtube_service.search()
                .list(part="snippet", q=query, type="channel", maxResults=1)
                .execute()
            )
        except HttpError as exc:  # pragma: no cover - API errors not easily unit tested
            raise APIError("YouTube search failed", api_name="youtube", status_code=exc.resp.status) from exc

        items = response.get("items", [])
        if items:
            return items[0]["snippet"].get("channelId")
        return None

    def _extract_from_url(self, url: str) -> Optional[str]:
        import re

        patterns = [
            r"youtube\.com/channel/([a-zA-Z0-9_-]+)",
            r"youtube\.com/c/([a-zA-Z0-9_-]+)",
            r"youtube\.com/user/([a-zA-Z0-9_-]+)",
            r"youtube\.com/@([a-zA-Z0-9_-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if not match:
                continue
            identifier = match.group(1)
            if "channel/" in pattern:
                return identifier
            return self._lookup_channel_by_query(identifier)
        return None

    # ------------------------------------------------------------------
    # Video fetching / processing
    # ------------------------------------------------------------------

    def get_channel_videos(
        self, 
        channel_id: str, 
        *, 
        max_results: int, 
        config: SyncConfig,
        existing_video_ids: Optional[List[str]] = None,
        tab_name: str = ""
    ) -> List[VideoRecord]:
        """
        Fetch videos from a YouTube channel with intelligent deduplication.
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to fetch
            config: Sync configuration for filtering
            existing_video_ids: List of video IDs already in the sheet (for deduplication)
            tab_name: Tab name for composite deduplication keys
            
        Returns:
            List of VideoRecord objects (only new videos if existing_video_ids provided)
        """
        # Pre-populate deduplicator with existing videos to avoid API calls
        if existing_video_ids:
            marked_count = self.video_deduplicator.mark_as_seen(existing_video_ids, channel_id, tab_name)
            logger.info(
                "Marked %d existing videos as seen for channel %s (tab: %s)",
                marked_count, channel_id, tab_name or "default"
            )
        
        videos: List[VideoRecord] = []
        next_page_token: Optional[str] = None
        total_duplicates_skipped = 0

        while len(videos) < max_results:
            request_params: Dict[str, object] = {
                "part": "snippet",
                "channelId": channel_id,
                "maxResults": min(50, max_results - len(videos)),
                "order": "date",
                "type": "video",
            }

            if next_page_token:
                request_params["pageToken"] = next_page_token

            try:
                self.quota_tracker.consume(100)
                response = self.youtube_service.search().list(**request_params).execute()
            except HttpError as exc:
                raise APIError("YouTube search failed", api_name="youtube", status_code=exc.resp.status) from exc

            channel_name = self._resolve_channel_title(response)

            # Collect video IDs from search results
            video_ids = []
            for item in response.get("items", []):
                if item.get("id", {}).get("kind") == "youtube#video":
                    video_id = item["id"].get("videoId")
                    if video_id:
                        video_ids.append(video_id)

            # 🚀 CRITICAL OPTIMIZATION: Filter out duplicates BEFORE API call
            new_video_ids = self.video_deduplicator.filter_new_videos(video_ids, channel_id, tab_name)
            duplicates_in_batch = len(video_ids) - len(new_video_ids)
            total_duplicates_skipped += duplicates_in_batch
            
            if duplicates_in_batch > 0:
                logger.info(
                    "🎯 Deduplication: Skipped %d duplicate videos (saving ~%d quota units)",
                    duplicates_in_batch,
                    duplicates_in_batch  # Each video costs ~1 quota unit in batch call
                )

            # Fetch full video details ONLY for new videos
            if new_video_ids:
                try:
                    self.quota_tracker.consume(1)  # videos().list costs 1 quota unit
                    details_response = self.youtube_service.videos().list(
                        part="snippet,statistics,contentDetails",
                        id=",".join(new_video_ids)
                    ).execute()
                    
                    for item in details_response.get("items", []):
                        try:
                            record = build_video_record(item, channel_name)
                            videos.append(record)
                        except ProcessingError as exc:
                            logger.warning("Skipping video due to processing error: %s", exc)
                except HttpError as exc:
                    logger.error("Failed to fetch video details: %s", exc)
                    raise APIError("YouTube video details fetch failed", api_name="youtube", status_code=exc.resp.status) from exc

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        logger.info(
            "✅ Fetched %d NEW videos from channel %s (skipped %d duplicates)",
            len(videos), channel_id, total_duplicates_skipped
        )

        keywords = config.keywords()
        filtered = apply_filters(
            videos,
            min_seconds=config.min_duration_seconds,
            max_seconds=config.max_duration_seconds,
            keywords=keywords,
            keyword_mode=config.keyword_mode,
        )

        logger.info("%s videos remain after filtering", len(filtered))
        return filtered

    def _resolve_channel_title(self, response: Dict) -> str:
        items = response.get("items", [])
        if not items:
            return "Unknown"
        snippet = items[0].get("snippet", {})
        return snippet.get("channelTitle", "Unknown")

    # ------------------------------------------------------------------
    # Sheets helpers
    # ------------------------------------------------------------------

    def read_existing_video_ids(self, spreadsheet_url: str, tab_name: str) -> List[str]:
        """
        Read existing video IDs from a Google Sheet tab for deduplication.
        
        Args:
            spreadsheet_url: Google Sheets URL
            tab_name: Tab name to read from
            
        Returns:
            List of video IDs (extracted from Video Link column)
        """
        sheet_id = self.extract_sheet_id(spreadsheet_url)
        
        try:
            # Read all rows from the sheet
            range_name = f"{tab_name}!A:L"  # Read all 12 columns
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            rows = result.get("values", [])
            
            if not rows or len(rows) <= 1:
                logger.info("No existing videos found in sheet tab '%s'", tab_name)
                return []
            
            # Extract video IDs from Video Link column (column G, index 6)
            video_ids = []
            for row in rows[1:]:  # Skip header row
                if len(row) > 6:  # Ensure row has Video Link column
                    video_link = row[6]
                    # Extract video ID from URL (format: https://www.youtube.com/watch?v=VIDEO_ID)
                    if "youtube.com/watch?v=" in video_link:
                        video_id = video_link.split("v=")[1].split("&")[0]
                        video_ids.append(video_id)
            
            logger.info(
                "📊 Read %d existing videos from sheet tab '%s'",
                len(video_ids), tab_name
            )
            return video_ids
            
        except HttpError as exc:
            # Tab might not exist yet - that's OK
            if exc.resp.status == 400:
                logger.info("Tab '%s' does not exist yet - no existing videos", tab_name)
                return []
            logger.error("Failed to read existing videos: %s", exc)
            return []  # Return empty list on error - better to have duplicates than crash
        except Exception as exc:
            logger.error("Unexpected error reading existing videos: %s", exc)
            return []

    def write_to_sheets(
        self, 
        spreadsheet_url: str, 
        tab_name: str, 
        records: Iterable[VideoRecord], 
        append_mode: bool = True,
        format_as_table: bool = True,
        defer_formatting: bool = False
    ) -> bool:
        """
        Write video records to Google Sheets with optional deferred formatting.
        
        Args:
            spreadsheet_url: Google Sheets URL
            tab_name: Tab name to write to
            records: Video records to write
            append_mode: If True, append to existing data. If False, overwrite entire tab.
            format_as_table: If True, apply professional Table formatting
            defer_formatting: If True, skip formatting (for batch operations - format at end)
            
        Returns:
            True if successful
            
        Note:
            Use defer_formatting=True during batch processing to avoid O(N²) formatting overhead.
            Call format_table_after_batch() once at the end to apply formatting.
        """
        sheet_id = self.extract_sheet_id(spreadsheet_url)
        
        if append_mode:
            # Append mode: Add new rows below existing data
            record_rows = [record.as_row() for record in records]
            
            try:
                # First, check if sheet is empty and needs headers
                range_name = f"{tab_name}!A1"
                result = self.sheets_service.spreadsheets().values().get(
                    spreadsheetId=sheet_id,
                    range=range_name
                ).execute()
                
                existing_values = result.get("values", [])
                
                if not existing_values:
                    # Sheet is empty - write headers first
                    values_to_write = [DEFAULT_HEADERS] + record_rows
                else:
                    # Sheet has data - append only records
                    values_to_write = record_rows
                
                body = {"values": values_to_write}
                self.sheets_service.spreadsheets().values().append(
                    spreadsheetId=sheet_id,
                    range=f"{tab_name}!A:L",
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body=body,
                ).execute()
                
                logger.info("✅ Appended %d rows to sheet tab '%s'", len(record_rows), tab_name)
                
                # 🎨 Apply Table formatting if requested (unless deferred for batch processing)
                if format_as_table and not defer_formatting and self.sheet_formatter:
                    total_rows = len(existing_values) + len(record_rows) if existing_values else len(record_rows) + 1
                    self.sheet_formatter.format_as_table(
                        tab_name=tab_name,
                        num_rows=total_rows,
                        num_columns=12,
                        apply_conditional_formatting=True,
                        create_named_range=True
                    )
                    self.sheet_formatter.auto_resize_columns(tab_name)
                    logger.info("🎨 Applied professional Table formatting to '%s'", tab_name)
                elif defer_formatting:
                    logger.debug("⏸️ Deferred formatting for '%s' (batch mode)", tab_name)
                
                return True
                
            except HttpError as exc:
                raise APIError("Failed to append to Google Sheets", api_name="google_sheets", status_code=exc.resp.status) from exc
        else:
            # Overwrite mode: Replace entire tab
            values = [DEFAULT_HEADERS]
            values.extend(record.as_row() for record in records)

            try:
                body = {"values": values}
                range_name = f"{tab_name}!A1"
                self.sheets_service.spreadsheets().values().update(
                    spreadsheetId=sheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    body=body,
                ).execute()
                logger.info("✅ Overwrote sheet tab '%s' with %d rows", tab_name, len(values))
                
                # 🎨 Apply Table formatting if requested (unless deferred for batch processing)
                if format_as_table and not defer_formatting and self.sheet_formatter:
                    self.sheet_formatter.format_as_table(
                        tab_name=tab_name,
                        num_rows=len(values),
                        num_columns=12,
                        apply_conditional_formatting=True,
                        create_named_range=True
                    )
                    self.sheet_formatter.auto_resize_columns(tab_name)
                    logger.info("🎨 Applied professional Table formatting to '%s'", tab_name)
                elif defer_formatting:
                    logger.debug("⏸️ Deferred formatting for '%s' (batch mode)", tab_name)
                
                return True
            except HttpError as exc:
                raise APIError("Failed to write to Google Sheets", api_name="google_sheets", status_code=exc.resp.status) from exc

    def format_table_after_batch(self, spreadsheet_url: str, tab_name: str) -> bool:
        """
        Apply professional Table formatting after batch processing complete.
        
        Use this after writing multiple channels with defer_formatting=True to apply
        formatting once at the end (avoiding O(N²) overhead).
        
        Args:
            spreadsheet_url: Google Sheets URL
            tab_name: Tab name to format
            
        Returns:
            True if successful
        """
        if not self.sheet_formatter:
            logger.warning("Sheet formatter not initialized")
            return False
        
        try:
            sheet_id = self.extract_sheet_id(spreadsheet_url)
            
            # Get current row count
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f"{tab_name}!A:L"
            ).execute()
            
            total_rows = len(result.get("values", []))
            
            if total_rows > 0:
                self.sheet_formatter.format_as_table(
                    tab_name=tab_name,
                    num_rows=total_rows,
                    num_columns=12,
                    apply_conditional_formatting=True,
                    create_named_range=True
                )
                self.sheet_formatter.auto_resize_columns(tab_name)
                logger.info("🎨 Applied deferred Table formatting to '%s' (%d rows)", tab_name, total_rows)
                return True
            
            return False
            
        except HttpError as exc:
            logger.error("Failed to format table after batch: %s", exc)
            return False

    def _get_sheet_tabs(self, sheet_id: str) -> List[str]:
        """
        Get list of tab names from a Google Sheet, excluding tabs with 'ranked' in the name.
        
        Args:
            sheet_id: Google Sheets ID
            
        Returns:
            List of tab names (excluding those with 'ranked' in the name)
        """
        try:
            # Get spreadsheet metadata
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            # Extract sheet names
            sheets = spreadsheet.get('sheets', [])
            all_tab_names = [sheet['properties']['title'] for sheet in sheets]
            
            # Filter out tabs with 'ranked' in the name (case-insensitive)
            tab_names = [name for name in all_tab_names if 'ranked' not in name.lower()]
            
            logger.info("📊 Retrieved %d tabs from spreadsheet (filtered %d with 'ranked'): %s", 
                       len(tab_names), len(all_tab_names) - len(tab_names), ', '.join(tab_names))
            return tab_names
            
        except HttpError as exc:
            logger.error("Failed to get sheet tabs: %s", exc)
            raise APIError("Failed to get sheet tabs", api_name="google_sheets", status_code=exc.resp.status) from exc
        except Exception as exc:
            logger.error("Unexpected error getting sheet tabs: %s", exc)
            return []

    @staticmethod
    def extract_sheet_id(spreadsheet_url: str) -> str:
        import re

        patterns = [
            r"/spreadsheets/d/([a-zA-Z0-9-_]+)",
            r"id=([a-zA-Z0-9-_]+)",
            r"([a-zA-Z0-9-_]{44})",
        ]

        for pattern in patterns:
            match = re.search(pattern, spreadsheet_url)
            if match:
                return match.group(1)
        return spreadsheet_url

    # ------------------------------------------------------------------
    # Public workflows
    # ------------------------------------------------------------------

    def sync_channel_to_sheet(
        self, 
        *, 
        channel_input: str, 
        spreadsheet_url: str, 
        tab_name: str, 
        config: Optional[SyncConfig] = None,
        defer_formatting: bool = False
    ) -> bool:
        """
        Sync YouTube channel videos to Google Sheets with intelligent deduplication.
        
        This method:
        1. Reads existing videos from the sheet
        2. Marks them in the deduplicator
        3. Fetches ONLY new videos from YouTube
        4. Appends new videos to the sheet
        
        This approach saves significant API quota by avoiding processing of existing videos.
        
        Args:
            channel_input: YouTube channel (@handle, username, or channel ID)
            spreadsheet_url: Google Sheets URL
            tab_name: Tab name to write to
            config: Optional sync configuration (filters, max videos)
            defer_formatting: If True, skip formatting (for batch jobs - format at end)
            
        Returns:
            True if successful
        """
        config = config or SyncConfig()
        channel_id = self.extract_channel_id(channel_input)
        
        # 🚀 STEP 1: Read existing videos from sheet for deduplication
        existing_video_ids = self.read_existing_video_ids(spreadsheet_url, tab_name)
        logger.info(
            "📊 Found %d existing videos in sheet - will fetch only new videos",
            len(existing_video_ids)
        )
        
        # 🚀 STEP 2: Fetch videos with deduplication (API calls saved automatically!)
        records = self.get_channel_videos(
            channel_id, 
            max_results=config.max_videos, 
            config=config,
            existing_video_ids=existing_video_ids,  # ← KEY: Pre-filter duplicates
            tab_name=tab_name
        )
        
        if not records:
            logger.warning("No NEW records to add for %s", channel_input)
            return True  # Success - just nothing new to add
        
        logger.info("✅ Writing %d new videos to sheet", len(records))
        return self.write_to_sheets(
            spreadsheet_url, 
            tab_name, 
            records,
            defer_formatting=defer_formatting
        )
    
    def sync_multiple_channels(
        self,
        *,
        channel_inputs: List[str],
        spreadsheet_url: str,
        tab_name: str,
        config: Optional[SyncConfig] = None
    ) -> Dict[str, bool]:
        """
        Sync multiple YouTube channels to a single Google Sheets tab with optimal efficiency.
        
        This method implements the HYBRID APPROACH:
        - Writes after each channel (incremental safety, progress visibility)
        - Defers formatting until all channels complete (O(N) efficiency, not O(N²))
        - Single formatting operation at the end
        
        Benefits:
        - Partial results preserved if job fails mid-way
        - User sees incremental progress
        - Optimal performance (no redundant formatting)
        - Memory efficient (process and release per channel)
        
        Args:
            channel_inputs: List of YouTube channels to sync
            spreadsheet_url: Google Sheets URL  
            tab_name: Tab name to write all channels to
            config: Optional sync configuration
            
        Returns:
            Dictionary mapping channel_input to success status
        """
        results: Dict[str, bool] = {}
        config = config or SyncConfig()
        
        logger.info(
            "🚀 Starting batch sync: %d channels → '%s' (incremental writes, deferred formatting)",
            len(channel_inputs), tab_name
        )
        
        try:
            # Process each channel with deferred formatting
            for idx, channel_input in enumerate(channel_inputs, 1):
                logger.info(
                    "📺 Processing channel %d/%d: %s",
                    idx, len(channel_inputs), channel_input
                )
                
                try:
                    success = self.sync_channel_to_sheet(
                        channel_input=channel_input,
                        spreadsheet_url=spreadsheet_url,
                        tab_name=tab_name,
                        config=config,
                        defer_formatting=True  # ← KEY: Defer formatting for efficiency
                    )
                    results[channel_input] = success
                    
                    if success:
                        logger.info("✅ Channel %d/%d complete: %s", idx, len(channel_inputs), channel_input)
                    else:
                        logger.warning("⚠️ Channel %d/%d failed: %s", idx, len(channel_inputs), channel_input)
                        
                except Exception as exc:
                    logger.error("❌ Channel %d/%d error: %s - %s", idx, len(channel_inputs), channel_input, exc)
                    results[channel_input] = False
            
        finally:
            # 🎨 CRITICAL: Always format at the end, even if some channels failed
            logger.info("🎨 Applying deferred formatting to '%s' (all channels processed)", tab_name)
            self.format_table_after_batch(spreadsheet_url, tab_name)
        
        successful = sum(1 for success in results.values() if success)
        logger.info(
            "✅ Batch sync complete: %d/%d channels successful",
            successful, len(channel_inputs)
        )
        
        return results

    # ------------------------------------------------------------------
    # Scheduler support
    # ------------------------------------------------------------------

    def enable_scheduler(self, sheet_id: str, tab_name: str = "Scheduler") -> None:
        self.scheduler = SchedulerSheetManager(self.sheets_service, sheet_id, tab_name)
        logger.info("Scheduler enabled for sheet %s", sheet_id)

    def run_scheduler_once(self) -> Dict[str, str]:
        if not self.scheduler:
            raise ValidationError("Scheduler not enabled. Call enable_scheduler first.")

        results = self.scheduler.run_due_jobs(self)
        logger.info("Scheduler run complete: %s", results)
        return {job_id: status.value for job_id, status in results.items()}

    # ------------------------------------------------------------------
    # API Optimization & Performance Monitoring
    # ------------------------------------------------------------------

    def get_api_optimization_report(self) -> Dict:
        """
        Get comprehensive API optimization report with all metrics.
        
        Returns:
            Dictionary with quota status, cache stats, deduplication stats, and recommendations
        """
        quota_status = self.quota_tracker.get_status()
        cache_stats = self.response_cache.get_statistics()
        dedup_stats = self.video_deduplicator.get_statistics()
        
        # Calculate efficiency metrics
        total_api_efficiency = 100.0
        if cache_stats["total_requests"] > 0:
            cache_efficiency = cache_stats["hit_rate"]
        else:
            cache_efficiency = 0.0
        
        # Calculate API calls saved
        api_calls_saved_by_cache = cache_stats["hits"]
        api_calls_saved_by_dedup = dedup_stats["duplicates_prevented"]
        total_api_calls_saved = api_calls_saved_by_cache + api_calls_saved_by_dedup
        
        # Generate recommendations
        recommendations = []
        if quota_status["usage_percent"] > 85:
            recommendations.append("CRITICAL: Approaching daily quota limit - reduce processing frequency")
        elif quota_status["usage_percent"] > 70:
            recommendations.append("WARNING: Over 70% of daily quota used - monitor closely")
        
        if cache_stats["hit_rate"] < 20 and cache_stats["total_requests"] > 10:
            recommendations.append("Low cache hit rate - consider processing fewer unique channels")
        elif cache_stats["hit_rate"] > 50:
            recommendations.append("Excellent cache performance - ETag optimization working well")
        
        if dedup_stats["duplicates_prevented"] > 0:
            recommendations.append(f"Deduplication prevented {dedup_stats['duplicates_prevented']} redundant API calls")
        
        if not recommendations:
            recommendations.append("All systems optimal - no action needed")
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "quota": quota_status,
            "cache": {
                **cache_stats,
                "efficiency_score": cache_efficiency,
            },
            "deduplication": dedup_stats,
            "efficiency": {
                "cache_hit_rate": cache_efficiency,
                "api_calls_saved": total_api_calls_saved,
                "breakdown": {
                    "saved_by_cache": api_calls_saved_by_cache,
                    "saved_by_deduplication": api_calls_saved_by_dedup,
                },
            },
            "recommendations": recommendations,
        }

