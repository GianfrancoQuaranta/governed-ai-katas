# Kata 05 · Circuit breaker

**Timebox: 40 minutes**

## Scenario

> One of your two model providers starts timing out after 30 seconds on every call. Your gateway keeps sending traffic to it, threads pile up waiting, and the healthy provider's requests start timing out too. Build a circuit breaker so the gateway fails fast on a sick provider and gives it room to recover.

## Requirements

Implement `CircuitBreaker` in `circuit_breaker.py`, a state machine with three states:

| State | Behavior |
|-------|----------|
| `"closed"` | Calls go through. Count **consecutive** failures; a success resets the count. Reaching `failure_threshold` opens the circuit. |
| `"open"` | Calls raise `CircuitOpenError` immediately, **without** calling `fn`. After `recovery_timeout` seconds, the circuit becomes half-open. |
| `"half_open"` | The next call is a trial. Success closes the circuit and resets counts. Failure opens it again and restarts the timeout. |

- `call(fn)` runs `fn()`, returns its result, and re-raises its exception after recording it.
- The `state` property must reflect time: reading it after the timeout returns `"half_open"` even if no call happened.
- Only exceptions in `failure_types` (default: `Exception`) count as failures. Others propagate and count as neither success nor failure.
- The clock is injected.

## Run

```bash
uv run pytest katas/05_circuit_breaker -m "not stretch"
```

## Stretch

- **One trial at a time:** in `"half_open"`, while a trial call is in flight, any other call raises `CircuitOpenError`. Test it with a `fn` that calls the breaker again from inside itself.

## Discussion questions

1. Consecutive failures vs failure rate over a window: when does each one misfire?
2. A 400 Bad Request from the provider: should it count as a failure? What about a timeout? A 429?
3. Your breaker is open for provider A. What should the gateway do with the request: fail, fall back to provider B, or degrade? Who decides?
4. How do you alert on breakers without paging someone every time one flaps?
