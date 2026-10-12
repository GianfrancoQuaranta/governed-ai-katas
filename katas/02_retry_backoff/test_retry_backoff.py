import pytest

from retry_backoff import RetryableError, RetryBudget, retry_call


class Flaky:
    """Fails with the given exceptions in order, then returns "ok"."""

    def __init__(self, *errors):
        self.errors = list(errors)
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return "ok"


class Sleeps(list):
    def __call__(self, seconds):
        self.append(seconds)


def test_success_first_try_does_not_sleep():
    fn, sleeps = Flaky(), Sleeps()
    assert retry_call(fn, sleep=sleeps) == "ok"
    assert fn.calls == 1 and sleeps == []


def test_retries_transient_errors_with_exponential_delays():
    fn, sleeps = Flaky(RetryableError(), RetryableError()), Sleeps()
    assert retry_call(fn, sleep=sleeps, rng=lambda: 1.0) == "ok"
    assert fn.calls == 3
    assert sleeps == [pytest.approx(0.1), pytest.approx(0.2)]


def test_delay_is_capped_by_max_delay():
    fn, sleeps = Flaky(*[RetryableError()] * 3), Sleeps()
    retry_call(fn, base_delay=1.0, max_delay=2.0, sleep=sleeps, rng=lambda: 1.0)
    assert sleeps == [pytest.approx(1.0), pytest.approx(2.0), pytest.approx(2.0)]


def test_full_jitter_scales_the_delay():
    fn, sleeps = Flaky(RetryableError()), Sleeps()
    retry_call(fn, base_delay=1.0, sleep=sleeps, rng=lambda: 0.25)
    assert sleeps == [pytest.approx(0.25)]


def test_non_retryable_error_propagates_immediately():
    fn, sleeps = Flaky(ValueError("bad request")), Sleeps()
    with pytest.raises(ValueError):
        retry_call(fn, sleep=sleeps)
    assert fn.calls == 1 and sleeps == []


def test_gives_up_after_max_attempts():
    fn, sleeps = Flaky(*[RetryableError()] * 10), Sleeps()
    with pytest.raises(RetryableError):
        retry_call(fn, max_attempts=4, sleep=sleeps, rng=lambda: 0.0)
    assert fn.calls == 4 and len(sleeps) == 3


def test_custom_retryable_types():
    fn, sleeps = Flaky(TimeoutError()), Sleeps()
    assert retry_call(fn, retryable=(TimeoutError,), sleep=sleeps, rng=lambda: 0.0) == "ok"
    assert fn.calls == 2


def test_budget_starts_full_and_drains():
    budget = RetryBudget(max_tokens=2, ratio=0.1)
    assert budget.try_acquire() and budget.try_acquire()
    assert not budget.try_acquire()


def test_budget_refills_on_success_and_is_capped():
    budget = RetryBudget(max_tokens=1, ratio=0.5)
    assert budget.try_acquire()
    budget.on_success()
    assert not budget.try_acquire()
    budget.on_success()
    assert budget.try_acquire()
    for _ in range(10):
        budget.on_success()
    assert budget.try_acquire()
    assert not budget.try_acquire()


def test_empty_budget_prevents_retries():
    budget = RetryBudget(max_tokens=0)
    fn, sleeps = Flaky(RetryableError()), Sleeps()
    with pytest.raises(RetryableError):
        retry_call(fn, budget=budget, sleep=sleeps)
    assert fn.calls == 1 and sleeps == []


def test_success_feeds_the_budget():
    budget = RetryBudget(max_tokens=1, ratio=1.0)
    assert budget.try_acquire()
    retry_call(Flaky(), budget=budget, sleep=Sleeps())
    assert budget.try_acquire()


class SlowDown(RetryableError):
    def __init__(self, retry_after):
        super().__init__("429")
        self.retry_after = retry_after


@pytest.mark.stretch
def test_retry_after_wins_over_shorter_backoff():
    fn, sleeps = Flaky(SlowDown(5)), Sleeps()
    retry_call(fn, base_delay=0.1, max_delay=2.0, sleep=sleeps, rng=lambda: 1.0)
    assert sleeps == [pytest.approx(5.0)]


@pytest.mark.stretch
def test_backoff_wins_when_longer_than_retry_after():
    fn, sleeps = Flaky(RetryableError(), SlowDown(0.1)), Sleeps()
    retry_call(fn, base_delay=1.0, max_delay=4.0, sleep=sleeps, rng=lambda: 1.0)
    assert sleeps == [pytest.approx(1.0), pytest.approx(2.0)]
