# Kata 04 · Per-tenant token bucket

**Timebox: 30 minutes**

## Scenario

> Your inference gateway serves several internal teams. One of them launched a batch job that burned the whole provider quota in 10 minutes, and every other team got 429s. Build per-tenant rate limiting so one noisy neighbor can't take everyone down. Limits are in LLM tokens, not requests: one request can cost 200 tokens and the next 20,000.

## Requirements

Implement in `token_bucket.py`:

1. `TokenBucket(capacity, refill_per_sec, clock=time.monotonic)`
   - Starts full.
   - Refills continuously at `refill_per_sec`, never above `capacity`.
   - `try_consume(tokens=1)` returns `True` and subtracts if enough tokens are available, otherwise returns `False` and subtracts nothing.
   - A request larger than `capacity` can never succeed: return `False`.
   - Raise `ValueError` for non-positive `capacity` or negative `refill_per_sec`.
2. `TenantRateLimiter(limits, default, clock=time.monotonic)`
   - `limits` maps tenant id to `(capacity, refill_per_sec)`; `default` is the pair for unknown tenants.
   - `allow(tenant, tokens=1)` uses that tenant's own bucket. Tenants never share tokens.
   - Buckets are created lazily the first time a tenant shows up.

The clock is injected. Never call `time.monotonic()` directly in your logic.

## Run

```bash
uv run pytest katas/04_token_bucket -m "not stretch"
```

## Stretch

- `retry_after(tenant, tokens)`: seconds until `allow(tenant, tokens)` would succeed, `0.0` if it would succeed now, or `None` if it never can. This feeds the `Retry-After` header.

## Discussion questions

1. You only know the real token count after the model answers. How do you rate-limit before the call?
2. Your gateway runs in 8 replicas. Where does the bucket live, and what do you lose if each replica keeps its own?
3. Token bucket vs fixed window vs sliding window: which one lets a tenant burst, and when is that what you want?
4. A tenant is legitimately huge (40% of all traffic). How do you protect the others without starving it?
