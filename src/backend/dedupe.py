"""
Video deduplication module for YouTube2Sheets.
Handles O(1) duplicate detection using efficient data structures.
"""

from typing import Dict, List, Set
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class VideoHash:
    """Hash representation of a video for deduplication."""
    video_id: str
    title: str
    channel_id: str
    published_at: str


class VideoDeduplicator:
    """Efficient video deduplication using hash-based detection."""
    
    def __init__(self):
        self.seen_videos: Set[str] = set()
        self.video_hashes: Dict[str, VideoHash] = {}
    
    def is_duplicate(self, video_id: str, title: str, channel_id: str, published_at: str) -> bool:
        """
        Check if a video is a duplicate.
        
        Args:
            video_id: YouTube video ID
            title: Video title
            channel_id: YouTube channel ID
            published_at: Publication timestamp
            
        Returns:
            True if duplicate, False otherwise
        """
        # Create a unique hash for this video
        video_hash = f"{video_id}_{channel_id}_{published_at}"
        
        if video_hash in self.seen_videos:
            logger.debug(f"Duplicate video detected: {video_id} - {title}")
            return True
        
        # Add to seen videos
        self.seen_videos.add(video_hash)
        self.video_hashes[video_hash] = VideoHash(
            video_id=video_id,
            title=title,
            channel_id=channel_id,
            published_at=published_at
        )
        
        return False
    
    def clear(self) -> None:
        """Clear all seen videos."""
        self.seen_videos.clear()
        self.video_hashes.clear()
        logger.info("Video deduplicator cleared")
    
    def get_stats(self) -> Dict[str, int]:
        """Get deduplication statistics."""
        return {
            "total_videos_seen": len(self.seen_videos),
            "unique_videos": len(self.video_hashes)
        }
