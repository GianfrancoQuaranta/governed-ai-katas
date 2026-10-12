# AI Platform Katas

Hand-written practice for AI platform engineering: timed coding katas (30–45 min) and small projects built from scratch.

Every kata is a piece of a real system: the statistics behind a release gate, retries that don't cause retry storms, idempotent actions for agents, per-tenant rate limits, circuit breakers per model provider, and an eval gate that blocks regressions. The capstone project ([Governed Agent Lab](projects/governed-agent-lab/README.md)) puts them together.

## Setup

```bash
uv sync                      # or: python -m venv .venv && pip install pytest
uv run pytest katas/01_wilson_gate -m "not stretch"
```

Python 3.11+, standard library only. No third-party packages inside the katas.

## Rules

1. **Timebox.** Set a timer for the time in the kata's README. When it rings, stop and commit whatever you have.
2. **By hand.** No Copilot, no autocomplete, no asking an AI during the kata. Official Python docs are allowed.
3. **Read the scenario first, code second.** Spend the first 5 minutes writing the plan as comments.
4. **Core first.** Run `pytest <kata dir> -m "not stretch"` until green. Then try the stretch tests.
5. **Talk out loud in English.** Explain what you're doing as if an interviewer were watching. Record yourself once a week.
6. **Debrief.** After the timer, answer the discussion questions in the kata's README in [PRACTICE_LOG.md](PRACTICE_LOG.md). Then (and only then) ask for a code review using [REVIEW_PROMPT.md](REVIEW_PROMPT.md).
7. **Redo.** A kata isn't done until you can solve it again, from an empty file, within the timebox. Redo each one 1–2 weeks later.

## Katas

| # | Kata | Time | Concepts | Roadmap tier |
|---|------|------|----------|--------------|
| 01 | [Wilson release gate](katas/01_wilson_gate/README.md) | 30 min | Confidence intervals, sample sizing, release decisions | 9 |
| 02 | [Retry with backoff and budget](katas/02_retry_backoff/README.md) | 35 min | Exponential backoff, full jitter, retry budgets | 1 |
| 03 | [Idempotent action executor](katas/03_idempotency/README.md) | 30 min | Idempotency keys, payload conflicts, failure semantics | 1, 7 |
| 04 | [Per-tenant token bucket](katas/04_token_bucket/README.md) | 30 min | Rate limiting, refill math, tenant isolation | 6 |
| 05 | [Circuit breaker](katas/05_circuit_breaker/README.md) | 40 min | Closed/open/half-open state machine, fail fast | 1, 6 |
| 06 | [Eval gate](katas/06_eval_gate/README.md) | 45 min | Golden sets per capability, thresholds, regression detection | 9 |

Suggested cadence: 3 sessions a week. Do them in order the first time; after that, mix redos and new katas.

## Projects

Small, complete systems built by hand. Each one reuses kata code.

- [Governed Agent Lab](projects/governed-agent-lab/README.md): an agent that drafts and sends collection messages, with an eval gate, sampled approvals, automatic suspension, provenance logging and provider independence.
