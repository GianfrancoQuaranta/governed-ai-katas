# Kata 02 · Retry with backoff and budget

**Timebox: 35 minutes**

## Scenario

> Your inference gateway calls a model provider that sometimes returns 429 or 503. Last week a provider blip turned into an outage: every client retried immediately, three times, and the provider never recovered. Build a retry helper that can't cause a retry storm.

## Requirements

Implement in `retry_backoff.py`:

1. `RetryBudget(max_tokens=10.0, ratio=0.1)`
   - Starts full (`max_tokens` tokens).
   - `try_acquire()` takes 1 token for a retry and returns `True`, or returns `False` if fewer than 1 token is left.
   - `on_success()` adds `ratio` tokens, capped at `max_tokens`. With `ratio=0.1`, retries are limited to roughly 10% of successful traffic.
2. `retry_call(fn, *, max_attempts=4, base_delay=0.1, max_delay=2.0, retryable=(RetryableError,), budget=None, sleep=time.sleep, rng=random.random)`
   - Calls `fn()` and returns its result.
   - On an exception listed in `retryable`, waits and tries again, up to `max_attempts` total calls. Any other exception propagates immediately.
   - Delay before retry number k (k = 1, 2, …) uses **full jitter**: `rng() * min(max_delay, base_delay * 2 ** (k - 1))`.
   - If a `budget` is given, every retry must `try_acquire()` first; if it can't, re-raise the last error without sleeping. Every success calls `budget.on_success()`.
   - When attempts run out, re-raise the last exception.
   - `sleep` and `rng` are injected so tests are deterministic. Never call `time.sleep` directly.

## Run

```bash
uv run pytest katas/02_retry_backoff -m "not stretch"
```

## Stretch

- Honor `Retry-After`: if the exception has a numeric attribute `retry_after` (seconds), sleep `max(retry_after, jittered_delay)` instead. `max_delay` does not cap it: an explicit request from the server wins.

## Discussion questions

1. Why full jitter instead of plain exponential backoff? Draw what happens to 1,000 clients that failed at the same instant.
2. Retries happen at three layers: SDK, gateway and agent. What's the worst-case number of calls to the provider for one user request, and how do you prevent it?
3. Which errors from an LLM provider should never be retried? Name three.
4. Why is a retry budget better than a fixed `max_attempts` during an outage?
