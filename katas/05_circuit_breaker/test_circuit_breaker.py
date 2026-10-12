import pytest

from circuit_breaker import CircuitBreaker, CircuitOpenError


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class Provider:
    def __init__(self):
        self.healthy = True
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if not self.healthy:
            raise TimeoutError("provider timed out")
        return "completion"


def fail_n(breaker, provider, n):
    for _ in range(n):
        with pytest.raises(TimeoutError):
            breaker.call(provider)


def make(threshold=3, timeout=30.0, **kw):
    clock = FakeClock()
    return CircuitBreaker(threshold, timeout, clock=clock, **kw), clock, Provider()


def test_starts_closed_and_passes_calls():
    breaker, _, provider = make()
    assert breaker.state == "closed"
    assert breaker.call(provider) == "completion"


def test_opens_after_consecutive_failures():
    breaker, _, provider = make(threshold=3)
    provider.healthy = False
    fail_n(breaker, provider, 2)
    assert breaker.state == "closed"
    fail_n(breaker, provider, 1)
    assert breaker.state == "open"


def test_success_resets_the_failure_count():
    breaker, _, provider = make(threshold=3)
    provider.healthy = False
    fail_n(breaker, provider, 2)
    provider.healthy = True
    breaker.call(provider)
    provider.healthy = False
    fail_n(breaker, provider, 2)
    assert breaker.state == "closed"


def test_open_circuit_fails_fast_without_calling():
    breaker, _, provider = make(threshold=1)
    provider.healthy = False
    fail_n(breaker, provider, 1)
    calls = provider.calls
    with pytest.raises(CircuitOpenError):
        breaker.call(provider)
    assert provider.calls == calls


def test_becomes_half_open_after_timeout():
    breaker, clock, provider = make(threshold=1, timeout=30)
    provider.healthy = False
    fail_n(breaker, provider, 1)
    clock.now = 29.9
    assert breaker.state == "open"
    clock.now = 30.0
    assert breaker.state == "half_open"


def test_successful_trial_closes_the_circuit():
    breaker, clock, provider = make(threshold=2, timeout=30)
    provider.healthy = False
    fail_n(breaker, provider, 2)
    clock.now = 31
    provider.healthy = True
    assert breaker.call(provider) == "completion"
    assert breaker.state == "closed"
    provider.healthy = False
    fail_n(breaker, provider, 1)
    assert breaker.state == "closed"


def test_failed_trial_reopens_and_restarts_timeout():
    breaker, clock, provider = make(threshold=2, timeout=30)
    provider.healthy = False
    fail_n(breaker, provider, 2)
    clock.now = 31
    fail_n(breaker, provider, 1)
    assert breaker.state == "open"
    clock.now = 60
    assert breaker.state == "open"
    clock.now = 61
    assert breaker.state == "half_open"


def test_non_failure_exceptions_propagate_without_counting():
    breaker, _, _ = make(threshold=1, failure_types=(TimeoutError,))

    def bad_request():
        raise ValueError("400: invalid schema")

    with pytest.raises(ValueError):
        breaker.call(bad_request)
    assert breaker.state == "closed"


@pytest.mark.stretch
def test_only_one_trial_in_flight():
    breaker, clock, provider = make(threshold=1, timeout=10)
    provider.healthy = False
    fail_n(breaker, provider, 1)
    clock.now = 10
    seen = []

    def trial():
        try:
            breaker.call(lambda: "nested")
        except CircuitOpenError:
            seen.append("rejected")
        return "trial ok"

    assert breaker.call(trial) == "trial ok"
    assert seen == ["rejected"]
    assert breaker.state == "closed"
