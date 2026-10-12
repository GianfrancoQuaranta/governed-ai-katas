import pytest

from wilson_gate import (
    release_decision,
    required_sample_size,
    wilson_interval,
    zero_error_sample_size,
)


def test_interval_with_errors():
    lower, upper = wilson_interval(2, 300)
    assert lower == pytest.approx(0.00183, abs=2e-4)
    assert upper == pytest.approx(0.02397, abs=2e-4)


def test_interval_zero_errors_starts_at_zero():
    lower, upper = wilson_interval(0, 300)
    assert lower == pytest.approx(0.0, abs=1e-12)
    assert upper == pytest.approx(0.01264, abs=2e-4)


def test_interval_all_errors_ends_at_one():
    lower, upper = wilson_interval(10, 10)
    assert upper == pytest.approx(1.0, abs=1e-12)
    assert 0.0 < lower < 1.0


def test_higher_confidence_gives_wider_interval():
    lo95, up95 = wilson_interval(5, 200, 0.95)
    lo99, up99 = wilson_interval(5, 200, 0.99)
    assert lo99 < lo95 and up99 > up95


@pytest.mark.parametrize("errors,n", [(1, 0), (-1, 10), (11, 10)])
def test_interval_rejects_invalid_input(errors, n):
    with pytest.raises(ValueError):
        wilson_interval(errors, n)


def test_zero_error_sample_size_one_percent():
    assert zero_error_sample_size(0.01) == 299


def test_zero_error_sample_size_tenth_of_percent():
    assert zero_error_sample_size(0.001) == 2995


def test_zero_error_sample_size_is_tight():
    n = zero_error_sample_size(0.02)
    assert (1 - 0.02) ** n <= 0.05
    assert (1 - 0.02) ** (n - 1) > 0.05


def test_decision_approve():
    assert release_decision(0, 300, 0.02) == "approve"


def test_decision_point_estimate_below_threshold_is_not_enough():
    assert release_decision(2, 300, 0.01) == "need_more_samples"


def test_decision_reject():
    assert release_decision(30, 300, 0.01) == "reject"


@pytest.mark.stretch
def test_required_sample_size_is_enough():
    n = required_sample_size(0.002, 0.01)
    assert n is not None
    _, upper = wilson_interval(int(n * 0.002), n)
    assert upper <= 0.01


@pytest.mark.stretch
def test_required_sample_size_is_minimal():
    n = required_sample_size(0.002, 0.01)
    _, upper = wilson_interval(int((n - 1) * 0.002), n - 1)
    assert upper > 0.01


@pytest.mark.stretch
def test_required_sample_size_impossible():
    assert required_sample_size(0.02, 0.01) is None
