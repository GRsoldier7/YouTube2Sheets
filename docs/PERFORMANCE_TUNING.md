# Performance Tuning Guide

This document provides comprehensive guidance on tuning YouTube2Sheets performance parameters for optimal operation.

## Overview

YouTube2Sheets uses a centralized performance configuration system located in `src/config/performance_config.py`. All performance-related parameters can be tuned to optimize for different use cases and system capabilities.

## Configuration Parameters

### Thread Pool Configuration

#### `max_workers` (Default: 10)
- **Purpose**: Maximum number of worker threads for parallel processing
- **Range**: 1-50
- **Impact**: Higher values = more parallel processing, but more memory usage
- **When to adjust**: 
  - Increase for systems with more CPU cores
  - Decrease if experiencing memory issues
  - Optimal range: 5-20 for most systems

#### `concurrent_api_limit` (Default: 20)
- **Purpose**: Maximum concurrent API requests to YouTube
- **Range**: 1-50
- **Impact**: Higher values = faster processing, but may hit API rate limits
- **When to adjust**:
  - Increase if you have high API quota
  - Decrease if hitting rate limits
  - YouTube API allows up to 50 concurrent requests

### Batch Processing Configuration

#### `batch_size_limit` (Default: 1000)
- **Purpose**: Default batch size for writing videos to Google Sheets
- **Range**: 100-5000
- **Impact**: Larger batches = fewer API calls, but more memory usage
- **When to adjust**:
  - Increase for better performance with large datasets
  - Decrease if experiencing memory issues

#### `max_batch_size` (Default: 2000)
- **Purpose**: Maximum allowed batch size
- **Range**: 500-10000
- **Impact**: Safety limit to prevent memory exhaustion
- **When to adjust**: Only increase if you have sufficient memory

#### `min_batch_size` (Default: 500)
- **Purpose**: Minimum batch size for efficient processing
- **Range**: 100-1000
- **Impact**: Ensures reasonable batch sizes even for small datasets
- **When to adjust**: Decrease for very small datasets

#### `batch_percentage` (Default: 0.2)
- **Purpose**: Percentage of total videos to include in each batch
- **Range**: 0.1-0.5
- **Impact**: Higher values = larger batches, fewer API calls
- **When to adjust**: Increase for better performance, decrease for more frequent updates

### API Configuration

#### `api_retry_attempts` (Default: 3)
- **Purpose**: Number of retry attempts for failed API calls
- **Range**: 1-10
- **Impact**: More retries = better reliability, but slower on failures
- **When to adjust**: Increase for unreliable network connections

#### `api_timeout_seconds` (Default: 15)
- **Purpose**: Timeout for API requests
- **Range**: 5-60
- **Impact**: Higher values = more tolerance for slow responses
- **When to adjust**: Increase for slow network connections

#### `rate_limit_delay` (Default: 0.1)
- **Purpose**: Delay between API requests to avoid rate limiting
- **Range**: 0.0-1.0
- **Impact**: Higher values = slower but more reliable
- **When to adjust**: Increase if hitting rate limits

### Cache Configuration

#### `cache_ttl_seconds` (Default: 3600)
- **Purpose**: Time-to-live for simple cache entries
- **Range**: 300-86400
- **Impact**: Longer TTL = better performance, but potentially stale data
- **When to adjust**: Increase for better performance, decrease for fresher data

#### `etag_cache_enabled` (Default: True)
- **Purpose**: Enable ETag-based caching for API responses
- **Impact**: Significantly reduces API calls for unchanged content
- **When to adjust**: Disable only if experiencing cache-related issues

#### `simple_cache_enabled` (Default: True)
- **Purpose**: Enable simple time-based caching
- **Impact**: Provides fallback caching when ETags are not available
- **When to adjust**: Disable only if experiencing memory issues

### Video Processing Configuration

#### `max_videos_per_channel` (Default: 50)
- **Purpose**: Maximum videos to fetch per channel
- **Range**: 10-200
- **Impact**: Higher values = more data, but more API calls
- **When to adjust**: Increase for channels with many videos

#### `video_batch_size` (Default: 50)
- **Purpose**: Number of video IDs to process in each API batch
- **Range**: 1-50
- **Impact**: YouTube API limit - do not exceed 50
- **When to adjust**: Only decrease if experiencing API errors

### Memory Management

#### `max_memory_usage_mb` (Default: 500)
- **Purpose**: Maximum memory usage before cleanup
- **Range**: 100-2000
- **Impact**: Higher values = better performance, but more memory usage
- **When to adjust**: Increase for systems with more RAM

#### `cleanup_interval_seconds` (Default: 300)
- **Purpose**: Interval for automatic memory cleanup
- **Range**: 60-1800
- **Impact**: More frequent cleanup = less memory usage, but more CPU
- **When to adjust**: Decrease if experiencing memory issues

### GUI Configuration

#### `gui_update_interval_ms` (Default: 100)
- **Purpose**: Interval for GUI updates during processing
- **Range**: 50-1000
- **Impact**: Lower values = more responsive GUI, but more CPU usage
- **When to adjust**: Increase if GUI is too slow

#### `progress_update_threshold` (Default: 0.01)
- **Purpose**: Minimum progress change to trigger GUI update
- **Range**: 0.001-0.1
- **Impact**: Lower values = more frequent updates, but more CPU
- **When to adjust**: Increase if GUI updates are too frequent

## Performance Profiles

### High Performance Profile
For systems with abundant resources:
```python
from src.config.performance_config import update_performance_config

update_performance_config(
    max_workers=20,
    concurrent_api_limit=30,
    batch_size_limit=2000,
    max_batch_size=5000,
    cache_ttl_seconds=7200,
    max_memory_usage_mb=1000
)
```

### Conservative Profile
For systems with limited resources:
```python
update_performance_config(
    max_workers=5,
    concurrent_api_limit=10,
    batch_size_limit=500,
    max_batch_size=1000,
    cache_ttl_seconds=1800,
    max_memory_usage_mb=250
)
```

### Balanced Profile (Default)
Optimized for most systems:
```python
# Uses default values - no changes needed
```

## Monitoring Performance

### Key Metrics to Monitor

1. **API Quota Usage**: Monitor daily API consumption
2. **Cache Hit Rate**: Should be >70% for optimal performance
3. **Memory Usage**: Should stay below configured limits
4. **Processing Time**: 32 channels should complete in <5 minutes
5. **Error Rate**: Should be <1% for reliable operation

### Performance Logs

The system logs performance metrics with prefixes:
- `[OPTIMIZATION]`: Performance optimization decisions
- `[CACHE]`: Cache hit/miss information
- `[BATCH]`: Batch processing information
- `[CLEANUP]`: Resource cleanup information

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Decrease `max_batch_size` and `batch_size_limit`
   - Increase `cleanup_interval_seconds`
   - Decrease `max_memory_usage_mb`

2. **API Rate Limiting**
   - Increase `rate_limit_delay`
   - Decrease `concurrent_api_limit`
   - Enable more aggressive caching

3. **Slow Processing**
   - Increase `max_workers` and `concurrent_api_limit`
   - Increase `batch_size_limit`
   - Enable ETag caching

4. **GUI Responsiveness**
   - Increase `gui_update_interval_ms`
   - Increase `progress_update_threshold`

### Performance Testing

Use the built-in performance tests:
```bash
python test_optimization_performance.py
python test_ultimate_optimization.py
```

## Best Practices

1. **Start with defaults** and adjust based on observed performance
2. **Monitor metrics** during operation to identify bottlenecks
3. **Test changes** with small datasets before scaling up
4. **Document custom configurations** for team consistency
5. **Regular cleanup** of cache files to prevent disk space issues

## Advanced Tuning

### Custom Configuration

For advanced users, you can create custom configuration profiles:

```python
from src.config.performance_config import PerformanceConfig, update_performance_config

# Create custom config
custom_config = PerformanceConfig(
    max_workers=15,
    concurrent_api_limit=25,
    batch_size_limit=1500,
    # ... other parameters
)

# Apply custom config
update_performance_config(**custom_config.__dict__)
```

### Environment-Specific Tuning

Different environments may require different configurations:

- **Development**: Conservative settings for stability
- **Testing**: Balanced settings for reliable testing
- **Production**: Optimized settings for performance

## Support

For performance tuning assistance:
1. Check the logs for performance-related messages
2. Run the performance test suite
3. Monitor system resources during operation
4. Adjust parameters incrementally and test

Remember: Performance tuning is an iterative process. Start with small changes and measure the impact before making larger adjustments.
