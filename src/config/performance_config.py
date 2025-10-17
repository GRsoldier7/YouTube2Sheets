"""
Performance Configuration for YouTube2Sheets
Centralized configuration for all performance-related parameters.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class PerformanceConfig:
    """Centralized performance configuration for YouTube2Sheets."""
    
    # Thread Pool Configuration
    max_workers: int = 10
    concurrent_api_limit: int = 20
    
    # Batch Processing Configuration
    batch_size_limit: int = 1000
    max_batch_size: int = 2000
    min_batch_size: int = 500
    batch_percentage: float = 0.2  # 20% of total videos per batch
    
    # API Configuration
    api_retry_attempts: int = 3
    api_timeout_seconds: int = 15
    rate_limit_delay: float = 0.1
    
    # Cache Configuration
    cache_ttl_seconds: int = 3600  # 1 hour
    etag_cache_enabled: bool = True
    simple_cache_enabled: bool = True
    
    # Video Processing Configuration
    max_videos_per_channel: int = 50
    video_batch_size: int = 50  # YouTube API limit
    
    # Memory Management
    max_memory_usage_mb: int = 500
    cleanup_interval_seconds: int = 300  # 5 minutes
    
    # Performance Monitoring
    enable_performance_monitoring: bool = True
    metrics_collection_interval: int = 30  # seconds
    
    # GUI Configuration
    gui_update_interval_ms: int = 100
    progress_update_threshold: float = 0.01  # 1%
    
    # Error Handling
    max_consecutive_errors: int = 5
    error_retry_delay: float = 1.0
    
    # Resource Cleanup
    thread_cleanup_timeout: int = 2  # seconds
    cache_save_timeout: int = 5  # seconds


# Default configuration instance
DEFAULT_CONFIG = PerformanceConfig()


def get_performance_config() -> PerformanceConfig:
    """Get the current performance configuration."""
    return DEFAULT_CONFIG


def update_performance_config(**kwargs) -> None:
    """Update performance configuration parameters."""
    for key, value in kwargs.items():
        if hasattr(DEFAULT_CONFIG, key):
            setattr(DEFAULT_CONFIG, key, value)
        else:
            raise ValueError(f"Unknown configuration parameter: {key}")


def reset_to_defaults() -> None:
    """Reset configuration to default values."""
    global DEFAULT_CONFIG
    DEFAULT_CONFIG = PerformanceConfig()
