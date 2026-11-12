"""
In-memory login rate limiter / throttling service for MSME Credit Coach.

Prevents brute-force credential stuffing by enforcing lockout windows
on repeated failed login attempts per client identifier and IP address.
"""

import time
import threading
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, status


class LoginRateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._lock = threading.Lock()
        self.failed_attempts: Dict[str, List[float]] = defaultdict(list)

    def _clean(self, key: str, now: float) -> None:
        cutoff = now - self.window_seconds
        self.failed_attempts[key] = [t for t in self.failed_attempts[key] if t > cutoff]
        if not self.failed_attempts[key]:
            del self.failed_attempts[key]

    def check(self, key: str) -> None:
        """Raises 429 Too Many Requests if the key has exceeded max failed attempts."""
        now = time.time()
        with self._lock:
            self._clean(key, now)
            attempts = len(self.failed_attempts.get(key, []))
            if attempts >= self.max_attempts:
                oldest = self.failed_attempts[key][0]
                retry_after = max(1, int(self.window_seconds - (now - oldest)))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many failed login attempts. Please wait {retry_after} seconds before trying again.",
                    headers={"Retry-After": str(retry_after)},
                )

    def record_failure(self, key: str) -> None:
        """Records a failed login attempt for the key."""
        now = time.time()
        with self._lock:
            self._clean(key, now)
            self.failed_attempts[key].append(now)

    def record_success(self, key: str) -> None:
        """Resets failed login attempts upon successful authentication."""
        with self._lock:
            if key in self.failed_attempts:
                del self.failed_attempts[key]


# Global rate limiter instance: 5 attempts per 5 minutes
login_limiter = LoginRateLimiter(max_attempts=5, window_seconds=300)
