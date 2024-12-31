# 14. Minimalist Monitoring Strategy

Date: 2024-12-31

## Status

Proposed

## Revision History
1.0.0 (2024-12-31) @dev
- Initial version with structured logging
- Added performance metrics
- Added basic health checks

## Context

As a solo developer with AI assistance, we need monitoring that:
1. Provides essential insights
2. Requires minimal maintenance
3. Helps debug issues
4. Integrates with AI workflows

## Decision

We will implement lightweight monitoring using built-in Python tools and simple logging:

### 1. Logging Strategy
Structured logging for AI analysis:

```python
# logging_setup.py
import logging
import json
from datetime import datetime
from pathlib import Path

def setup_logging(app_name: str):
    """Setup structured logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            if hasattr(record, "extra"):
                log_data.update(record.extra)
            return json.dumps(log_data)
    
    # File handler for analysis
    file_handler = logging.FileHandler(
        log_dir / f"{app_name}.log"
    )
    file_handler.setFormatter(JSONFormatter())
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s: %(message)s')
    )
    
    # Root logger setup
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
```

### 2. Performance Metrics
Simple timing decorator:

```python
# metrics.py
import time
import functools
import logging
from typing import Callable

def track_time(func: Callable) -> Callable:
    """Track function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        
        logging.info(
            f"{func.__name__} took {duration:.2f}s",
            extra={
                "metric_type": "duration",
                "function": func.__name__,
                "duration": duration
            }
        )
        return result
    return wrapper

# Usage
@track_time
def process_data():
    pass
```

### 3. Error Tracking
Centralized error handling:

```python
# error_tracking.py
import logging
import traceback
from typing import Type

def track_error(
    error: Exception,
    error_type: Type[Exception] = Exception
) -> None:
    """Track an error with context."""
    logging.error(
        str(error),
        extra={
            "error_type": error_type.__name__,
            "traceback": traceback.format_exc(),
            "metric_type": "error"
        }
    )

# Usage
try:
    process_data()
except Exception as e:
    track_error(e)
```

### 4. Health Checks
Basic health endpoint:

```python
# health.py
import psutil
from fastapi import FastAPI
from pydantic import BaseModel

class HealthStatus(BaseModel):
    """Health check response."""
    status: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float

@app.get("/health")
async def health_check() -> HealthStatus:
    """Check system health."""
    return HealthStatus(
        status="healthy",
        cpu_percent=psutil.cpu_percent(),
        memory_percent=psutil.virtual_memory().percent,
        disk_percent=psutil.disk_usage("/").percent
    )
```

## Consequences

### Positive
1. Easy to implement and maintain
2. Structured logs for AI analysis
3. Basic performance tracking
4. Simple error tracking

### Negative
1. No distributed tracing
2. Limited metrics
3. Basic alerting only

### Mitigation
1. Use AI to analyze logs
2. Add metrics as needed
3. Implement custom alerts

## References
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [FastAPI Monitoring](https://fastapi.tiangolo.com/advanced/monitoring/)
