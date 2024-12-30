"""API monitoring utilities."""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from threading import Lock

import requests
from googleapiclient.errors import HttpError

@dataclass
class APIMetrics:
    """API call metrics."""
    calls: int = 0
    errors: int = 0
    total_time: float = 0.0
    last_error: Optional[str] = None
    last_call: Optional[datetime] = None
    min_time: float = float('inf')
    max_time: float = 0.0

class APIMonitor:
    """Monitor API usage and performance.
    
    Features:
    - Rate limit tracking
    - Response time monitoring
    - Error tracking
    - Quota management
    """
    
    def __init__(self):
        self._metrics: Dict[str, APIMetrics] = {}
        self._lock = Lock()
        
    def track_call(self, api_name: str, duration: float, error: Optional[Exception] = None):
        """Track an API call.
        
        Args:
            api_name: Name of the API
            duration: Call duration in seconds
            error: Exception if call failed
        """
        with self._lock:
            if api_name not in self._metrics:
                self._metrics[api_name] = APIMetrics()
                
            metrics = self._metrics[api_name]
            metrics.calls += 1
            metrics.total_time += duration
            metrics.last_call = datetime.now()
            
            if duration < metrics.min_time:
                metrics.min_time = duration
            if duration > metrics.max_time:
                metrics.max_time = duration
                
            if error:
                metrics.errors += 1
                metrics.last_error = str(error)
                
    def get_metrics(self, api_name: str) -> Optional[APIMetrics]:
        """Get metrics for an API.
        
        Args:
            api_name: Name of the API
            
        Returns:
            API metrics or None if not found
        """
        return self._metrics.get(api_name)
        
    def get_error_rate(self, api_name: str) -> float:
        """Get error rate for an API.
        
        Args:
            api_name: Name of the API
            
        Returns:
            Error rate as percentage
        """
        metrics = self.get_metrics(api_name)
        if not metrics or not metrics.calls:
            return 0.0
        return (metrics.errors / metrics.calls) * 100
        
    def get_average_time(self, api_name: str) -> float:
        """Get average call time for an API.
        
        Args:
            api_name: Name of the API
            
        Returns:
            Average time in seconds
        """
        metrics = self.get_metrics(api_name)
        if not metrics or not metrics.calls:
            return 0.0
        return metrics.total_time / metrics.calls

# Global monitor instance
monitor = APIMonitor()

def track_api_call(api_name: str):
    """Decorator to track API calls.
    
    Example:
        ```python
        @track_api_call('gmail')
        def make_api_call():
            ...
        ```
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            error = None
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error = e
                raise
            finally:
                duration = time.time() - start
                monitor.track_call(api_name, duration, error)
        return wrapper
    return decorator
