"""
Enhanced Logging and Monitoring Service
Implements structured logging and monitoring following modern best practices
"""
import sys
import os
import json
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import traceback
import threading
from contextlib import contextmanager

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@dataclass
class LogContext:
    """Context information for logging."""
    service: str
    operation: str
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring."""
    operation: str
    duration: float
    memory_usage: float
    cpu_usage: float
    api_calls: int
    cache_hits: int
    cache_misses: int
    errors: int
    timestamp: datetime

class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for logs."""
    
    def format(self, record):
        """Format log record as structured JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in log_entry and not key.startswith('_'):
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)

class EnhancedLogger:
    """Enhanced logger with structured logging and monitoring."""
    
    def __init__(self, name: str, log_level: str = "INFO", log_file: Optional[str] = None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler with structured formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(file_handler)
        
        # Performance metrics storage
        self._metrics: List[PerformanceMetrics] = []
        self._metrics_lock = threading.Lock()
        
        # Request tracking
        self._request_context = threading.local()
    
    def set_context(self, context: LogContext):
        """Set logging context for current thread."""
        self._request_context.context = context
    
    def get_context(self) -> Optional[LogContext]:
        """Get current logging context."""
        return getattr(self._request_context, 'context', None)
    
    def _log_with_context(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log message with context information."""
        context = self.get_context()
        log_extra = extra or {}
        
        if context:
            log_extra.update({
                "service": context.service,
                "operation": context.operation,
                "user_id": context.user_id,
                "request_id": context.request_id,
                "session_id": context.session_id
            })
            
            if context.additional_data:
                log_extra.update(context.additional_data)
        
        getattr(self.logger, level.lower())(message, extra=log_extra)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self._log_with_context("INFO", message, extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self._log_with_context("WARNING", message, extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message."""
        self._log_with_context("ERROR", message, extra)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self._log_with_context("DEBUG", message, extra)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        self._log_with_context("CRITICAL", message, extra)
    
    def log_performance(self, metrics: PerformanceMetrics):
        """Log performance metrics."""
        with self._metrics_lock:
            self._metrics.append(metrics)
        
        self.info(
            f"Performance metrics for {metrics.operation}",
            extra={
                "performance_metrics": asdict(metrics),
                "metric_type": "performance"
            }
        )
    
    def log_api_call(self, service: str, operation: str, duration: float, success: bool, 
                    status_code: Optional[int] = None, error: Optional[str] = None):
        """Log API call information."""
        extra = {
            "api_call": True,
            "service": service,
            "operation": operation,
            "duration": duration,
            "success": success,
            "status_code": status_code
        }
        
        if error:
            extra["error"] = error
        
        if success:
            self.info(f"API call completed: {service}.{operation}", extra)
        else:
            self.error(f"API call failed: {service}.{operation}", extra)
    
    def log_user_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """Log user action."""
        extra = {
            "user_action": True,
            "action": action
        }
        
        if details:
            extra.update(details)
        
        self.info(f"User action: {action}", extra)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event."""
        extra = {
            "security_event": True,
            "event_type": event_type
        }
        extra.update(details)
        
        self.warning(f"Security event: {event_type}", extra)
    
    def get_metrics(self, operation: Optional[str] = None) -> List[PerformanceMetrics]:
        """Get performance metrics."""
        with self._metrics_lock:
            if operation:
                return [m for m in self._metrics if m.operation == operation]
            return self._metrics.copy()
    
    def clear_metrics(self):
        """Clear performance metrics."""
        with self._metrics_lock:
            self._metrics.clear()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        with self._metrics_lock:
            if not self._metrics:
                return {"total_operations": 0}
            
            total_operations = len(self._metrics)
            total_duration = sum(m.duration for m in self._metrics)
            avg_duration = total_duration / total_operations if total_operations > 0 else 0
            
            total_api_calls = sum(m.api_calls for m in self._metrics)
            total_cache_hits = sum(m.cache_hits for m in self._metrics)
            total_cache_misses = sum(m.cache_misses for m in self._metrics)
            total_errors = sum(m.errors for m in self._metrics)
            
            cache_hit_rate = total_cache_hits / (total_cache_hits + total_cache_misses) if (total_cache_hits + total_cache_misses) > 0 else 0
            
            return {
                "total_operations": total_operations,
                "total_duration": total_duration,
                "avg_duration": avg_duration,
                "total_api_calls": total_api_calls,
                "cache_hit_rate": cache_hit_rate,
                "total_errors": total_errors,
                "error_rate": total_errors / total_operations if total_operations > 0 else 0
            }

@contextmanager
def log_context(logger: EnhancedLogger, context: LogContext):
    """Context manager for logging context."""
    old_context = logger.get_context()
    logger.set_context(context)
    try:
        yield
    finally:
        logger.set_context(old_context)

@contextmanager
def performance_monitoring(logger: EnhancedLogger, operation: str):
    """Context manager for performance monitoring."""
    start_time = datetime.now()
    start_memory = _get_memory_usage()
    start_cpu = _get_cpu_usage()
    
    api_calls = 0
    cache_hits = 0
    cache_misses = 0
    errors = 0
    
    try:
        yield {
            "increment_api_calls": lambda: setattr(performance_monitoring, 'api_calls', api_calls + 1),
            "increment_cache_hits": lambda: setattr(performance_monitoring, 'cache_hits', cache_hits + 1),
            "increment_cache_misses": lambda: setattr(performance_monitoring, 'cache_misses', cache_misses + 1),
            "increment_errors": lambda: setattr(performance_monitoring, 'errors', errors + 1)
        }
    finally:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        end_memory = _get_memory_usage()
        end_cpu = _get_cpu_usage()
        
        metrics = PerformanceMetrics(
            operation=operation,
            duration=duration,
            memory_usage=end_memory - start_memory,
            cpu_usage=end_cpu - start_cpu,
            api_calls=api_calls,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            errors=errors,
            timestamp=end_time
        )
        
        logger.log_performance(metrics)

def _get_memory_usage() -> float:
    """Get current memory usage in MB."""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return 0.0

def _get_cpu_usage() -> float:
    """Get current CPU usage percentage."""
    try:
        import psutil
        process = psutil.Process()
        return process.cpu_percent()
    except ImportError:
        return 0.0

# Global logger instance
def get_logger(name: str = "youtube2sheets", log_level: str = "INFO") -> EnhancedLogger:
    """Get enhanced logger instance."""
    return EnhancedLogger(name, log_level)

# Example usage
if __name__ == "__main__":
    logger = get_logger("example", "DEBUG")
    
    # Set context
    context = LogContext(
        service="ExampleService",
        operation="test_operation",
        user_id="test_user",
        request_id="req_123"
    )
    
    with log_context(logger, context):
        logger.info("This is a test message")
        
        with performance_monitoring(logger, "test_operation") as monitor:
            # Simulate some work
            import time
            time.sleep(0.1)
            monitor["increment_api_calls"]()
        
        # Log metrics summary
        summary = logger.get_metrics_summary()
        logger.info(f"Metrics summary: {summary}")
