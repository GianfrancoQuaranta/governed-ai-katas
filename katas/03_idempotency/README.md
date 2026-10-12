# Kata 03 · Idempotent action executor

**Timebox: 30 minutes**

## Scenario

> Your agent sends a WhatsApp collection message, and the process dies before it records that the message went out. On restart, the workflow replays the step. Without protection, the customer gets the same message twice, and in a regulated business that's a complaint. Build the layer that makes every agent action safe to replay.

## Requirements

Implement `IdempotentExecutor` in `idempotency.py`:

- `execute(key, payload, action)` runs `action(payload)` and returns its result.
- Same `key` and an **equal** payload again: return the stored result **without** calling `action`.
- Same `key` with a **different** payload: raise `IdempotencyConflict`. A reused key with new content is a bug in the caller, and silently returning the old result would hide it.
- If `action` raises, store nothing and let the exception propagate, so a later call with the same key can try again.
- Payloads are JSON-serializable dicts. Two payloads are equal if they have the same content, regardless of key order.
- The store is injected (`store=None` means a new in-memory dict) so it can be swapped for Redis or Postgres later.

## Run

```bash
uv run pytest katas/03_idempotency -m "not stretch"
```

## Stretch

1. **Thread safety:** 20 threads calling `execute` with the same key at the same time must run `action` exactly once, and all of them must get the same result.
2. **TTL:** `IdempotentExecutor(ttl_seconds=..., clock=...)`. After the TTL expires, the key can run again.

## Discussion questions

1. Who should generate the idempotency key: the agent, the workflow engine or the downstream service? What goes into it?
2. The action succeeded but storing the result failed. What happens on replay, and how would you close that gap?
3. Your executor runs in 6 replicas. What changes in the store, and what does "exactly once" really mean here?
4. The WhatsApp provider's API has no idempotency support. What can you still guarantee?
