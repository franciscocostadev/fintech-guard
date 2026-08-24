"""Contador de tentativas de login em memória.

Com mais de um worker isso precisa virar Redis, senão cada processo tem o
próprio contador.
"""

import threading
import time
from collections import defaultdict, deque

_lock = threading.Lock()
_attempts: dict[str, deque[float]] = defaultdict(deque)


def _prune(bucket: deque[float], window: int, now: float) -> None:
    while bucket and now - bucket[0] > window:
        bucket.popleft()


def is_blocked(key: str, max_attempts: int, window_seconds: int) -> bool:
    now = time.monotonic()
    with _lock:
        bucket = _attempts[key]
        _prune(bucket, window_seconds, now)
        return len(bucket) >= max_attempts


def register_failure(key: str, window_seconds: int) -> None:
    now = time.monotonic()
    with _lock:
        bucket = _attempts[key]
        _prune(bucket, window_seconds, now)
        bucket.append(now)


def reset(key: str) -> None:
    with _lock:
        _attempts.pop(key, None)
