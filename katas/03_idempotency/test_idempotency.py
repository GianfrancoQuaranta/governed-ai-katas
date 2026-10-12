import threading
import time

import pytest

from idempotency import IdempotencyConflict, IdempotentExecutor


class CountingAction:
    def __init__(self, result="sent", fail_times=0, delay=0.0):
        self.calls = 0
        self.result = result
        self.fail_times = fail_times
        self.delay = delay
        self.lock = threading.Lock()

    def __call__(self, payload):
        with self.lock:
            self.calls += 1
            n = self.calls
        if self.delay:
            time.sleep(self.delay)
        if n <= self.fail_times:
            raise ConnectionError("provider down")
        return {"status": self.result, "to": payload.get("to")}


PAYLOAD = {"to": "+5493510000000", "template": "reminder", "amount": 15230.5}


def test_first_call_runs_the_action():
    action = CountingAction()
    result = IdempotentExecutor().execute("c1-cust42-step3", PAYLOAD, action)
    assert result == {"status": "sent", "to": PAYLOAD["to"]}
    assert action.calls == 1


def test_replay_returns_stored_result_without_running_again():
    ex, action = IdempotentExecutor(), CountingAction()
    first = ex.execute("k", PAYLOAD, action)
    second = ex.execute("k", dict(PAYLOAD), action)
    assert second == first
    assert action.calls == 1


def test_key_order_does_not_matter():
    ex, action = IdempotentExecutor(), CountingAction()
    ex.execute("k", {"a": 1, "b": {"x": 1, "y": 2}}, action)
    ex.execute("k", {"b": {"y": 2, "x": 1}, "a": 1}, action)
    assert action.calls == 1


def test_same_key_different_payload_conflicts():
    ex, action = IdempotentExecutor(), CountingAction()
    ex.execute("k", PAYLOAD, action)
    with pytest.raises(IdempotencyConflict):
        ex.execute("k", {**PAYLOAD, "amount": 99.0}, action)
    assert action.calls == 1


def test_different_keys_are_independent():
    ex, action = IdempotentExecutor(), CountingAction()
    ex.execute("k1", PAYLOAD, action)
    ex.execute("k2", PAYLOAD, action)
    assert action.calls == 2


def test_failures_are_not_stored():
    ex, action = IdempotentExecutor(), CountingAction(fail_times=1)
    with pytest.raises(ConnectionError):
        ex.execute("k", PAYLOAD, action)
    assert ex.execute("k", PAYLOAD, action)["status"] == "sent"
    assert action.calls == 2


def test_injected_store_is_used():
    store = {}
    IdempotentExecutor(store=store).execute("k", PAYLOAD, CountingAction())
    action = CountingAction()
    IdempotentExecutor(store=store).execute("k", PAYLOAD, action)
    assert action.calls == 0


@pytest.mark.stretch
def test_concurrent_calls_run_action_once():
    ex, action = IdempotentExecutor(), CountingAction(delay=0.05)
    results = []

    def worker():
        results.append(ex.execute("k", PAYLOAD, action))

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert action.calls == 1
    assert len(results) == 20 and all(r == results[0] for r in results)


@pytest.mark.stretch
def test_ttl_expires_keys():
    now = [0.0]
    ex = IdempotentExecutor(ttl_seconds=60, clock=lambda: now[0])
    action = CountingAction()
    ex.execute("k", PAYLOAD, action)
    now[0] = 59.0
    ex.execute("k", PAYLOAD, action)
    assert action.calls == 1
    now[0] = 61.0
    ex.execute("k", PAYLOAD, action)
    assert action.calls == 2
