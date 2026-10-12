"""Kata 03 · Idempotent action executor. See README.md."""

import time
from typing import Any, Callable


class IdempotencyConflict(Exception):
    """Same key, different payload."""


class IdempotentExecutor:
    def __init__(
        self,
        store: dict | None = None,
        ttl_seconds: float | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        raise NotImplementedError

    def execute(self, key: str, payload: dict, action: Callable[[dict], Any]) -> Any:
        raise NotImplementedError
