"""Kata 02 · Retry with backoff and budget. See README.md."""

import random
import time
from typing import Callable, TypeVar

T = TypeVar("T")


class RetryableError(Exception):
    """Transient failure: 429, 503, timeouts."""


class RetryBudget:
    def __init__(self, max_tokens: float = 10.0, ratio: float = 0.1) -> None:
        raise NotImplementedError

    def try_acquire(self) -> bool:
        raise NotImplementedError

    def on_success(self) -> None:
        raise NotImplementedError


def retry_call(
    fn: Callable[[], T],
    *,
    max_attempts: int = 4,
    base_delay: float = 0.1,
    max_delay: float = 2.0,
    retryable: tuple[type[BaseException], ...] = (RetryableError,),
    budget: RetryBudget | None = None,
    sleep: Callable[[float], None] = time.sleep,
    rng: Callable[[], float] = random.random,
) -> T:
    raise NotImplementedError
