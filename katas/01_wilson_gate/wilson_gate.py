"""Kata 01 · Wilson release gate. See README.md."""

from statistics import NormalDist  # noqa: F401  (you will need it)


def wilson_interval(errors: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson score interval for the error rate errors / n."""
    raise NotImplementedError


def zero_error_sample_size(max_error_rate: float, confidence: float = 0.95) -> int:
    """Minimum clean reviews needed to claim error rate <= max_error_rate."""
    raise NotImplementedError


def release_decision(errors: int, n: int, threshold: float, confidence: float = 0.95) -> str:
    """Return "approve", "reject" or "need_more_samples"."""
    raise NotImplementedError


def required_sample_size(expected_error_rate: float, threshold: float, confidence: float = 0.95) -> int | None:
    """Stretch. See README.md."""
    raise NotImplementedError
