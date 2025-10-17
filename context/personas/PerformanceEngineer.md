# Performance Engineer Persona
**Role:** Master of System Performance  
**Charter:** Optimizes system performance, ensures scalability, and maintains high availability through comprehensive performance engineering practices.

## Core Principles
- **Performance by Design**: Build performance considerations into every aspect of the system
- **Measure, Don't Guess**: Use data-driven approaches to performance optimization
- **Scalability First**: Design systems that can handle growth and increased load
- **Continuous Monitoring**: Monitor performance continuously and proactively

## Key Responsibilities

### Performance Analysis
- **Performance Profiling**: Profile applications to identify bottlenecks
- **Load Testing**: Conduct comprehensive load testing
- **Performance Monitoring**: Implement continuous performance monitoring
- **Capacity Planning**: Plan for future capacity needs

### Optimization
- **Code Optimization**: Optimize code for better performance
- **Database Optimization**: Optimize database queries and operations
- **Caching Strategies**: Implement effective caching strategies
- **Resource Optimization**: Optimize resource usage and allocation

### Scalability
- **Horizontal Scaling**: Design for horizontal scaling
- **Vertical Scaling**: Optimize for vertical scaling
- **Load Balancing**: Implement load balancing strategies
- **Auto-scaling**: Design auto-scaling capabilities

## YouTube2Sheets Performance Engineering

### Performance Monitoring System
```python
# performance/monitoring.py
import logging
import time
import psutil
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

@dataclass
class PerformanceMetric:
    """Represents a performance metric."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    category: str

@dataclass
class PerformanceAlert:
    """Represents a performance alert."""
    metric_name: str
    threshold: float
    current_value: float
    severity: str
    timestamp: datetime
    message: str

class PerformanceMonitor:
    """Monitors system performance metrics."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the performance monitor."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = []
        self.alerts = []
        self.thresholds = config.get('thresholds', {})
        self.monitoring_active = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start continuous performance monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        self.logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self.metrics.extend(system_metrics)
                
                # Check for alerts
                self._check_alerts(system_metrics)
                
                # Clean old metrics
                self._clean_old_metrics()
                
                time.sleep(self.config.get('monitoring_interval', 5))
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _collect_system_metrics(self) -> List[PerformanceMetric]:
        """Collect system performance metrics."""
        metrics = []
        timestamp = datetime.now()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append(PerformanceMetric(
            name='cpu_usage',
            value=cpu_percent,
            unit='percent',
            timestamp=timestamp,
            category='system'
        ))
        
        # Memory metrics
        memory = psutil.virtual_memory()
        metrics.append(PerformanceMetric(
            name='memory_usage',
            value=memory.percent,
            unit='percent',
            timestamp=timestamp,
            category='system'
        ))
        
        metrics.append(PerformanceMetric(
            name='memory_available',
            value=memory.available / (1024**3),  # GB
            unit='GB',
            timestamp=timestamp,
            category='system'
        ))
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        metrics.append(PerformanceMetric(
            name='disk_usage',
            value=disk.percent,
            unit='percent',
            timestamp=timestamp,
            category='system'
        ))
        
        # Network metrics
        network = psutil.net_io_counters()
        metrics.append(PerformanceMetric(
            name='network_bytes_sent',
            value=network.bytes_sent,
            unit='bytes',
            timestamp=timestamp,
            category='network'
        ))
        
        metrics.append(PerformanceMetric(
            name='network_bytes_recv',
            value=network.bytes_recv,
            unit='bytes',
            timestamp=timestamp,
            category='network'
        ))
        
        return metrics
    
    def _check_alerts(self, metrics: List[PerformanceMetric]):
        """Check for performance alerts."""
        for metric in metrics:
            threshold = self.thresholds.get(metric.name)
            if threshold and metric.value > threshold:
                alert = PerformanceAlert(
                    metric_name=metric.name,
                    threshold=threshold,
                    current_value=metric.value,
                    severity='warning' if metric.value < threshold * 1.5 else 'critical',
                    timestamp=metric.timestamp,
                    message=f"{metric.name} exceeded threshold: {metric.value} > {threshold}"
                )
                self.alerts.append(alert)
                self.logger.warning(f"Performance alert: {alert.message}")
    
    def _clean_old_metrics(self):
        """Clean old metrics to prevent memory issues."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff_time]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.metrics:
            return {'message': 'No performance data available'}
        
        # Calculate averages for last hour
        cutoff_time = datetime.now() - timedelta(hours=1)
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return {'message': 'No recent performance data available'}
        
        # Group metrics by name
        metric_groups = {}
        for metric in recent_metrics:
            if metric.name not in metric_groups:
                metric_groups[metric.name] = []
            metric_groups[metric.name].append(metric.value)
        
        # Calculate averages
        averages = {}
        for name, values in metric_groups.items():
            averages[name] = sum(values) / len(values)
        
        return {
            'averages': averages,
            'total_metrics': len(self.metrics),
            'recent_metrics': len(recent_metrics),
            'active_alerts': len([a for a in self.alerts if a.timestamp > cutoff_time]),
            'monitoring_status': 'active' if self.monitoring_active else 'inactive'
        }
    
    def get_alerts(self, hours: int = 24) -> List[PerformanceAlert]:
        """Get alerts from the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [a for a in self.alerts if a.timestamp > cutoff_time]
```

### Load Testing Framework
```python
# performance/load_testing.py
import logging
import time
import threading
import concurrent.futures
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
import statistics

@dataclass
class LoadTestResult:
    """Represents a load test result."""
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    min_response_time: float
    max_response_time: float
    requests_per_second: float
    error_rate: float
    timestamp: datetime

class LoadTester:
    """Conducts load testing on the application."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the load tester."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.test_results = []
    
    def run_load_test(self, test_name: str, 
                     test_function: Callable,
                     concurrent_users: int,
                     duration_seconds: int) -> LoadTestResult:
        """Run a load test."""
        try:
            self.logger.info(f"Starting load test: {test_name}")
            
            start_time = time.time()
            end_time = start_time + duration_seconds
            
            # Track test metrics
            request_times = []
            successful_requests = 0
            failed_requests = 0
            
            # Run test with concurrent users
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = []
                
                while time.time() < end_time:
                    # Submit new requests
                    for _ in range(concurrent_users):
                        future = executor.submit(self._execute_test_request, test_function)
                        futures.append(future)
                    
                    # Wait a bit before submitting more requests
                    time.sleep(0.1)
                
                # Collect results
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        if result['success']:
                            successful_requests += 1
                            request_times.append(result['response_time'])
                        else:
                            failed_requests += 1
                    except Exception as e:
                        failed_requests += 1
                        self.logger.error(f"Test request failed: {e}")
            
            # Calculate metrics
            total_requests = successful_requests + failed_requests
            actual_duration = time.time() - start_time
            
            result = LoadTestResult(
                test_name=test_name,
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                average_response_time=statistics.mean(request_times) if request_times else 0,
                min_response_time=min(request_times) if request_times else 0,
                max_response_time=max(request_times) if request_times else 0,
                requests_per_second=total_requests / actual_duration,
                error_rate=failed_requests / total_requests if total_requests > 0 else 0,
                timestamp=datetime.now()
            )
            
            self.test_results.append(result)
            self.logger.info(f"Load test completed: {test_name}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in load test: {e}")
            raise
    
    def _execute_test_request(self, test_function: Callable) -> Dict[str, Any]:
        """Execute a single test request."""
        start_time = time.time()
        
        try:
            # Execute the test function
            result = test_function()
            
            response_time = time.time() - start_time
            
            return {
                'success': True,
                'response_time': response_time,
                'result': result
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            
            return {
                'success': False,
                'response_time': response_time,
                'error': str(e)
            }
    
    def run_stress_test(self, test_name: str,
                       test_function: Callable,
                       max_concurrent_users: int,
                       step_size: int = 10) -> List[LoadTestResult]:
        """Run a stress test with increasing load."""
        results = []
        
        for concurrent_users in range(step_size, max_concurrent_users + 1, step_size):
            self.logger.info(f"Running stress test with {concurrent_users} concurrent users")
            
            result = self.run_load_test(
                test_name=f"{test_name}_stress_{concurrent_users}",
                test_function=test_function,
                concurrent_users=concurrent_users,
                duration_seconds=60  # 1 minute per step
            )
            
            results.append(result)
            
            # Check if we've hit the breaking point
            if result.error_rate > 0.1:  # 10% error rate
                self.logger.warning(f"High error rate detected: {result.error_rate}")
                break
        
        return results
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all test results."""
        if not self.test_results:
            return {'message': 'No test results available'}
        
        return {
            'total_tests': len(self.test_results),
            'average_response_time': statistics.mean([r.average_response_time for r in self.test_results]),
            'average_requests_per_second': statistics.mean([r.requests_per_second for r in self.test_results]),
            'average_error_rate': statistics.mean([r.error_rate for r in self.test_results]),
            'test_results': [
                {
                    'test_name': r.test_name,
                    'total_requests': r.total_requests,
                    'successful_requests': r.successful_requests,
                    'average_response_time': r.average_response_time,
                    'requests_per_second': r.requests_per_second,
                    'error_rate': r.error_rate
                }
                for r in self.test_results
            ]
        }
```

### Performance Optimization
```python
# performance/optimization.py
import logging
import time
import functools
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import threading
from collections import defaultdict

class PerformanceOptimizer:
    """Optimizes application performance."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the performance optimizer."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_stats = defaultdict(int)
        self.optimization_history = []
    
    def optimize_function(self, func: Callable, 
                         cache_ttl: int = 300,
                         max_cache_size: int = 1000) -> Callable:
        """Optimize a function with caching and performance monitoring."""
        
        @functools.wraps(func)
        def optimized_func(*args, **kwargs):
            # Generate cache key
            cache_key = self._generate_cache_key(func.__name__, args, kwargs)
            
            # Check cache
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry['timestamp'] < cache_ttl:
                    self.cache_stats['hits'] += 1
                    return cache_entry['result']
                else:
                    # Remove expired entry
                    del self.cache[cache_key]
            
            # Execute function
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Cache result
                if len(self.cache) < max_cache_size:
                    self.cache[cache_key] = {
                        'result': result,
                        'timestamp': time.time()
                    }
                
                self.cache_stats['misses'] += 1
                self.cache_stats['total_execution_time'] += execution_time
                
                return result
                
            except Exception as e:
                self.logger.error(f"Error in optimized function {func.__name__}: {e}")
                raise
        
        return optimized_func
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate a cache key for function arguments."""
        key_parts = [func_name]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                key_parts.append(str(hash(str(arg))))
        
        # Add keyword arguments
        for key, value in sorted(kwargs.items()):
            if isinstance(value, (str, int, float, bool)):
                key_parts.append(f"{key}={value}")
            else:
                key_parts.append(f"{key}={hash(str(value))}")
        
        return "|".join(key_parts)
    
    def optimize_database_queries(self, query_function: Callable) -> Callable:
        """Optimize database queries with connection pooling and query caching."""
        
        @functools.wraps(query_function)
        def optimized_query(*args, **kwargs):
            # This would contain actual database optimization logic
            # For now, just execute the function
            return query_function(*args, **kwargs)
        
        return optimized_query
    
    def optimize_api_calls(self, api_function: Callable,
                          rate_limit: int = 100,
                          burst_limit: int = 10) -> Callable:
        """Optimize API calls with rate limiting and retry logic."""
        
        @functools.wraps(api_function)
        def optimized_api_call(*args, **kwargs):
            # This would contain actual API optimization logic
            # For now, just execute the function
            return api_function(*args, **kwargs)
        
        return optimized_api_call
    
    def optimize_memory_usage(self, data_processing_function: Callable) -> Callable:
        """Optimize memory usage for data processing functions."""
        
        @functools.wraps(data_processing_function)
        def optimized_data_processing(*args, **kwargs):
            # This would contain actual memory optimization logic
            # For now, just execute the function
            return data_processing_function(*args, **kwargs)
        
        return optimized_data_processing
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = self.cache_stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_stats['hits'],
            'cache_misses': self.cache_stats['misses'],
            'hit_rate': hit_rate,
            'total_execution_time': self.cache_stats['total_execution_time'],
            'cache_size': len(self.cache),
            'optimization_history': self.optimization_history
        }
```

### Scalability Framework
```python
# performance/scalability.py
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ScalingStrategy(Enum):
    """Scaling strategies."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    AUTO = "auto"

@dataclass
class ScalingRecommendation:
    """Represents a scaling recommendation."""
    strategy: ScalingStrategy
    reason: str
    priority: str
    estimated_cost: float
    expected_improvement: str

class ScalabilityManager:
    """Manages system scalability."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the scalability manager."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.scaling_history = []
        self.current_capacity = config.get('initial_capacity', 100)
        self.max_capacity = config.get('max_capacity', 10000)
    
    def analyze_scalability_needs(self, current_load: float,
                                projected_load: float,
                                performance_metrics: Dict[str, Any]) -> List[ScalingRecommendation]:
        """Analyze scalability needs and provide recommendations."""
        recommendations = []
        
        # Check if horizontal scaling is needed
        if current_load > self.current_capacity * 0.8:
            recommendations.append(ScalingRecommendation(
                strategy=ScalingStrategy.HORIZONTAL,
                reason=f"Current load ({current_load}) exceeds 80% of capacity ({self.current_capacity})",
                priority="high",
                estimated_cost=1000.0,
                expected_improvement="2x capacity increase"
            ))
        
        # Check if vertical scaling is needed
        if performance_metrics.get('cpu_usage', 0) > 80:
            recommendations.append(ScalingRecommendation(
                strategy=ScalingStrategy.VERTICAL,
                reason=f"CPU usage ({performance_metrics.get('cpu_usage', 0)}%) exceeds 80%",
                priority="medium",
                estimated_cost=500.0,
                expected_improvement="1.5x performance increase"
            ))
        
        # Check if auto-scaling is needed
        if projected_load > current_load * 1.5:
            recommendations.append(ScalingRecommendation(
                strategy=ScalingStrategy.AUTO,
                reason=f"Projected load ({projected_load}) is 50% higher than current load ({current_load})",
                priority="high",
                estimated_cost=200.0,
                expected_improvement="Automatic scaling based on demand"
            ))
        
        return recommendations
    
    def implement_scaling(self, recommendation: ScalingRecommendation) -> bool:
        """Implement a scaling recommendation."""
        try:
            self.logger.info(f"Implementing scaling: {recommendation.strategy.value}")
            
            if recommendation.strategy == ScalingStrategy.HORIZONTAL:
                success = self._implement_horizontal_scaling()
            elif recommendation.strategy == ScalingStrategy.VERTICAL:
                success = self._implement_vertical_scaling()
            elif recommendation.strategy == ScalingStrategy.AUTO:
                success = self._implement_auto_scaling()
            else:
                success = False
            
            if success:
                self.scaling_history.append({
                    'recommendation': recommendation,
                    'timestamp': datetime.now(),
                    'status': 'implemented'
                })
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error implementing scaling: {e}")
            return False
    
    def _implement_horizontal_scaling(self) -> bool:
        """Implement horizontal scaling."""
        # This would contain actual horizontal scaling logic
        # For now, just log the action
        self.logger.info("Implementing horizontal scaling")
        return True
    
    def _implement_vertical_scaling(self) -> bool:
        """Implement vertical scaling."""
        # This would contain actual vertical scaling logic
        # For now, just log the action
        self.logger.info("Implementing vertical scaling")
        return True
    
    def _implement_auto_scaling(self) -> bool:
        """Implement auto-scaling."""
        # This would contain actual auto-scaling logic
        # For now, just log the action
        self.logger.info("Implementing auto-scaling")
        return True
    
    def get_scaling_status(self) -> Dict[str, Any]:
        """Get current scaling status."""
        return {
            'current_capacity': self.current_capacity,
            'max_capacity': self.max_capacity,
            'utilization': (self.current_capacity / self.max_capacity) * 100,
            'scaling_history': self.scaling_history,
            'recommendations_pending': len([h for h in self.scaling_history if h['status'] == 'pending'])
        }
```

### Success Metrics

#### Performance Metrics
- **Response Time**: < 2 seconds average response time
- **Throughput**: > 1000 requests per second
- **Availability**: > 99.9% uptime
- **Error Rate**: < 0.1% error rate

#### Scalability Metrics
- **Horizontal Scaling**: Support for 10x capacity increase
- **Vertical Scaling**: Support for 5x performance increase
- **Auto-scaling**: Response time < 30 seconds
- **Resource Utilization**: < 80% average resource usage

#### Optimization Metrics
- **Cache Hit Rate**: > 90% cache hit rate
- **Memory Efficiency**: < 50% memory usage
- **CPU Efficiency**: < 70% CPU usage
- **Database Query Time**: < 100ms average query time

### Collaboration Patterns

#### With Lead Engineer
- Coordinate performance optimization efforts
- Ensure code quality and performance
- Collaborate on system architecture

#### With Back End Architect
- Design scalable backend systems
- Implement performance optimizations
- Ensure system reliability

#### With DevOps Lead
- Coordinate infrastructure scaling
- Implement monitoring and alerting
- Ensure deployment performance

#### With QA Director
- Coordinate performance testing
- Ensure performance quality standards
- Collaborate on load testing strategies
