"""Kata 05 · Circuit breaker. See README.md."""

import time
from typing import Callable, TypeVar

T = TypeVar("T")


class CircuitOpenError(Exception):
    """Raised instead of calling a provider while the circuit is open."""


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        failure_types: tuple[type[BaseException], ...] = (Exception,),
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        raise NotImplementedError

    @property
    def state(self) -> str:
        raise NotImplementedError

    def call(self, fn: Callable[[], T]) -> T:
        raise NotImplementedError
