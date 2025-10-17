"""Data transformation utilities for YouTube2Sheets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from .exceptions import ProcessingError


@dataclass(slots=True)
class VideoRecord:
    """Canonical representation of a YouTube video for spreadsheet export."""

    channel_id: str
    channel: str
    date: str
    video_type: str
    duration: str
    title: str
    url: str
    views: str
    likes: str
    comments: str
    notebooklm: str = "☐"
    date_added: str = ""

    def as_row(self) -> list[str]:
        """Return the record as a row suitable for Google Sheets APIs."""

        return [
            self.channel_id,
            self.channel,
            self.date,
            self.video_type,
            self.duration,
            self.title,
            self.url,
            self.views,
            self.likes,
            self.comments,
            self.notebooklm,
            self.date_added,
        ]


def parse_duration(duration: str) -> int:
    """Convert an ISO-8601 duration string (e.g. ``PT4M13S``) into total seconds."""

    import re

    if not duration.startswith("PT"):
        raise ProcessingError(f"Invalid ISO duration: {duration!r}")

    time_portion = duration[2:]
    hours = re.search(r"(\d+)H", time_portion)
    minutes = re.search(r"(\d+)M", time_portion)
    seconds = re.search(r"(\d+)S", time_portion)

    total_seconds = 0
    if hours:
        total_seconds += int(hours.group(1)) * 3600
    if minutes:
        total_seconds += int(minutes.group(1)) * 60
    if seconds:
        total_seconds += int(seconds.group(1))

    return total_seconds


def format_duration(seconds: int) -> str:
    """Format a number of seconds into ``H:MM:SS`` or ``M:SS``."""

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    rem_seconds = seconds % 60

    if hours:
        return f"{hours}:{minutes:02d}:{rem_seconds:02d}"
    return f"{minutes}:{rem_seconds:02d}"


def format_int(value: Optional[str], default: str = "0") -> str:
    """Format an integer string with thousands separators; fall back gracefully."""

    try:
        if value is None:
            raise ValueError
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return default


def normalize_published_date(published_at: Optional[str]) -> str:
    """Return a human-readable date string (``YYYY-MM-DD``) for a video."""

    if not published_at:
        return "Unknown"

    try:
        dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        # Fallback: use first 10 characters if valid
        return published_at[:10] if len(published_at) >= 10 else published_at


def build_video_record(video_item: Dict, channel_name: str) -> VideoRecord:
    """Transform a raw YouTube API item into a :class:`VideoRecord`."""

    snippet = video_item.get("snippet", {})
    statistics = video_item.get("statistics", {})
    content_details = video_item.get("contentDetails", {})

    # Handle both search API format (id.videoId) and videos API format (id as string)
    video_id_obj = video_item.get("id")
    if isinstance(video_id_obj, dict):
        video_id = video_id_obj.get("videoId")
    else:
        video_id = video_id_obj
    
    if not video_id:
        raise ProcessingError("Video item missing videoId")

    duration_seconds = parse_duration(content_details.get("duration", "PT0S"))
    video_type = "Short" if duration_seconds < 60 else "Long"
    
    # Get current date for Date Added column
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    return VideoRecord(
        channel_id=snippet.get("channelId", ""),
        channel=channel_name,
        date=normalize_published_date(snippet.get("publishedAt")),
        video_type=video_type,
        duration=format_duration(duration_seconds),
        title=snippet.get("title", "No Title"),
        url=f"https://www.youtube.com/watch?v={video_id}",
        views=format_int(statistics.get("viewCount"), default="0"),
        likes=format_int(statistics.get("likeCount"), default="N/A"),
        comments=format_int(statistics.get("commentCount"), default="0"),
        notebooklm="☐",
        date_added=current_date,
    )

