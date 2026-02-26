from prometheus_client import Counter, Histogram, Gauge
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['service', 'method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['service', 'method', 'endpoint']
)

# Database metrics
db_operations_total = Counter(
    'db_operations_total',
    'Total database operations',
    ['service', 'operation', 'status']
)

db_connection_errors_total = Counter(
    'db_connection_errors_total',
    'Database connection errors',
    ['service']
)

# Error budget metrics
error_budget_remaining = Gauge(
    'error_budget_remaining_ratio',
    'Remaining error budget as ratio',
    ['service']
)

def track_request(service: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            status = "success"
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                logger.error(f"Request failed in {func.__name__}: {e}")
                raise
            finally:
                duration = time.time() - start
                http_request_duration_seconds.labels(
                    service=service,
                    method="POST",
                    endpoint=func.__name__
                ).observe(duration)
                http_requests_total.labels(
                    service=service,
                    method="POST",
                    endpoint=func.__name__,
                    status=status
                ).inc()
        return wrapper
    return decorator
