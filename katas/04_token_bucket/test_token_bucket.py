import pytest

from token_bucket import TenantRateLimiter, TokenBucket


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def test_starts_full_and_drains():
    clock = FakeClock()
    bucket = TokenBucket(10, 1, clock)
    assert all(bucket.try_consume() for _ in range(10))
    assert not bucket.try_consume()


def test_refills_over_time():
    clock = FakeClock()
    bucket = TokenBucket(10, 2, clock)
    assert bucket.try_consume(10)
    clock.advance(2.5)
    assert bucket.try_consume(5)
    assert not bucket.try_consume(1)


def test_refill_is_capped_at_capacity():
    clock = FakeClock()
    bucket = TokenBucket(10, 1, clock)
    bucket.try_consume(10)
    clock.advance(1000)
    assert bucket.try_consume(10)
    assert not bucket.try_consume(1)


def test_failed_consume_takes_nothing():
    clock = FakeClock()
    bucket = TokenBucket(10, 1, clock)
    assert bucket.try_consume(7)
    assert not bucket.try_consume(5)
    assert bucket.try_consume(3)


def test_request_larger_than_capacity_never_succeeds():
    clock = FakeClock()
    bucket = TokenBucket(100, 10, clock)
    clock.advance(1000)
    assert not bucket.try_consume(101)


@pytest.mark.parametrize("capacity,rate", [(0, 1), (-5, 1), (10, -1)])
def test_invalid_config(capacity, rate):
    with pytest.raises(ValueError):
        TokenBucket(capacity, rate, FakeClock())


def test_tenants_are_isolated():
    clock = FakeClock()
    limiter = TenantRateLimiter({"batch-team": (1000, 10), "chat-team": (1000, 10)}, (100, 1), clock)
    assert limiter.allow("batch-team", 1000)
    assert not limiter.allow("batch-team", 1)
    assert limiter.allow("chat-team", 1000)


def test_unknown_tenant_gets_default_limits():
    clock = FakeClock()
    limiter = TenantRateLimiter({"vip": (1000, 10)}, (100, 1), clock)
    assert limiter.allow("new-team", 100)
    assert not limiter.allow("new-team", 1)
    assert limiter.allow("other-new-team", 100)


def test_each_tenant_refills_independently():
    clock = FakeClock()
    limiter = TenantRateLimiter({"a": (10, 1), "b": (10, 5)}, (1, 1), clock)
    limiter.allow("a", 10)
    limiter.allow("b", 10)
    clock.advance(2)
    assert limiter.allow("b", 10)
    assert not limiter.allow("a", 3)
    assert limiter.allow("a", 2)


@pytest.mark.stretch
def test_retry_after():
    clock = FakeClock()
    limiter = TenantRateLimiter({"a": (10, 2)}, (1, 1), clock)
    assert limiter.retry_after("a", 5) == pytest.approx(0.0)
    limiter.allow("a", 10)
    assert limiter.retry_after("a", 5) == pytest.approx(2.5)
    assert limiter.retry_after("a", 11) is None
    clock.advance(2.5)
    assert limiter.allow("a", 5)
