import structlog
from typing import Any, Dict
from prometheus_client import Counter, Histogram, start_http_server

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
EMAIL_ANALYSIS_COUNTER = Counter(
    'email_analysis_total',
    'Total number of emails analyzed',
    ['status']  # success or failure
)

EMAIL_ANALYSIS_DURATION = Histogram(
    'email_analysis_duration_seconds',
    'Time spent analyzing emails',
    buckets=[1, 2, 5, 10, 30, 60]  # buckets in seconds
)

API_ERRORS = Counter(
    'api_errors_total',
    'Total number of API errors',
    ['error_type']
)

VALIDATION_ERRORS = Counter(
    'validation_errors_total',
    'Total number of validation errors',
    ['field']
)

def start_metrics_server(port: int = 8000) -> None:
    """Start the Prometheus metrics server."""
    start_http_server(port)
    logger.info("metrics_server_started", port=port)

def log_api_error(error_type: str, details: Dict[str, Any]) -> None:
    """Log an API error and increment the counter."""
    API_ERRORS.labels(error_type=error_type).inc()
    logger.error("api_error", error_type=error_type, **details)

def log_validation_error(field: str, details: Dict[str, Any]) -> None:
    """Log a validation error and increment the counter."""
    VALIDATION_ERRORS.labels(field=field).inc()
    logger.warning("validation_error", field=field, **details)
