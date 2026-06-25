import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request, status

_buckets: dict[str, list[float]] = defaultdict(list)
_lock = Lock()


def rate_limiter(max_requests: int, window_seconds: float):
    """Per-process sliding-window rate limiter keyed by client IP and route.

    In-memory only: resets on restart and does not coordinate across multiple
    server instances. Sufficient for a single-instance Render deployment.
    """

    def dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"{request.url.path}:{client_ip}"
        now = time.monotonic()
        cutoff = now - window_seconds

        with _lock:
            timestamps = _buckets[key]
            while timestamps and timestamps[0] < cutoff:
                timestamps.pop(0)
            if len(timestamps) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="リクエストが多すぎます。しばらく待ってから再試行してください",
                )
            timestamps.append(now)

    return dependency
