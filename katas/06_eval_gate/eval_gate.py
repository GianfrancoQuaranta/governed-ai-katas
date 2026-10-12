"""Kata 06 · Eval gate. See README.md."""

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class Case:
    id: str
    capability: str
    input: dict
    check: Callable[[Any], bool]


@dataclass
class CapabilityResult:
    capability: str
    total: int
    passed: int
    pass_rate: float
    failed_ids: list[str] = field(default_factory=list)


@dataclass
class GateDecision:
    approved: bool
    reasons: list[str]


def run_eval(cases: list[Case], model_fn: Callable[[dict], Any]) -> dict[str, CapabilityResult]:
    raise NotImplementedError


def gate(
    results: dict[str, CapabilityResult],
    thresholds: dict[str, float],
    baseline: dict[str, float] | None = None,
    max_regression: float = 0.02,
) -> GateDecision:
    raise NotImplementedError
