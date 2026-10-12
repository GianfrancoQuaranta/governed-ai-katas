# Governed Agent Lab

A small agent platform built by hand: an agent drafts collection reminders and sends them through a simulated messaging tool, and nothing reaches a customer unless it passes evals, sampled approval and runtime checks.

It is the job description of a Senior AI Engineer (evaluation and governance) in miniature, and it is meant to become the project you walk through in a deep-dive interview round.

## Rules

- Write the design note (milestone 0) **before** any code.
- Same rules as the katas: by hand, no AI while coding. Use [REVIEW_PROMPT.md](../../REVIEW_PROMPT.md) after each milestone.
- Each milestone is 1–3 sessions of 45 minutes. Commit at the end of every session, even if it's broken.
- Reuse your kata code. Copy it in and improve it; don't import from `katas/`.
- Fake data only. Never use real customer data or anything from your employer.

## Milestones

### 0 · Design note (2 pages)

Context, goals and **non-goals**, the actions the agent can take and which ones are irreversible, failure modes, and how you'll know it works. Write it in English.

### 1 · The agent

- A workflow with three steps: load the customer (fake data), draft the message with a model, call `send_message`.
- `send_message` is a fake tool that appends to a JSON file and fails randomly 10% of the time.
- Model calls go through a `LLMProvider` interface with two implementations: a real provider and a deterministic fake for tests.

### 2 · Golden set and eval gate

- 30 cases for `collection_msg`: normal, edge cases (zero debt, payment plan in progress, customer marked deceased) and two prompt-injection attempts hidden in customer notes.
- Checks: correct amount and due date, no forbidden phrases, tone rules.
- The gate from kata 06 runs in CI and blocks merges below threshold or with regressions.

### 3 · Runtime governance

- Deterministic checks before `send_message`: amount matches the ledger, quiet hours, opt-out list.
- Campaign approval: a statistically sized review sample (kata 01), approve / reject / need more samples.
- Automatic suspension: sample 1% of sent messages, and pause the campaign when the Wilson upper bound crosses the threshold.

### 4 · Reliability

- Idempotency keys on every action (kata 03), and a test that kills the process right after `send_message` and replays.
- Retries with budget (kata 02) and a circuit breaker per provider (kata 05) with fallback to the second provider.
- Per-campaign token budget (kata 04) with a kill switch.

### 5 · Provenance and observability

- Every model call logs: model, prompt version, input data sources, checks passed or failed, cost.
- A script that answers "why did customer X get this message on day Y?" from the logs alone.

### 6 · Write-up

- Update the design note with what changed and why.
- A blog post or LinkedIn article: one thing that broke and what you learned.
