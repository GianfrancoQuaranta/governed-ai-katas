"""Kata 04 · Per-tenant token bucket. See README.md."""

import time
from typing import Callable


class TokenBucket:
    def __init__(
        self,
        capacity: float,
        refill_per_sec: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        raise NotImplementedError

    def try_consume(self, tokens: float = 1) -> bool:
        raise NotImplementedError


class TenantRateLimiter:
    def __init__(
        self,
        limits: dict[str, tuple[float, float]],
        default: tuple[float, float],
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        raise NotImplementedError

    def allow(self, tenant: str, tokens: float = 1) -> bool:
        raise NotImplementedError

    def retry_after(self, tenant: str, tokens: float = 1) -> float | None:
        """Stretch. See README.md."""
        raise NotImplementedError
