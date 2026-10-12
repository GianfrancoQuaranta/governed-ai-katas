# Kata 06 · Eval gate

**Timebox: 45 minutes**

## Scenario

> Your agent platform has several capabilities: drafting collection messages, classifying complaints, summarizing calls. Product wants to ship a new prompt version tomorrow. Nothing goes live unless every capability passes its golden set, meets its agreed threshold, and hasn't regressed against the current production version. Build the gate.

## Requirements

Implement in `eval_gate.py`:

1. `run_eval(cases, model_fn)` returns `dict[str, CapabilityResult]`, one entry per capability.
   - Each `Case` has `id`, `capability`, `input` (a dict) and `check` (a function that takes the model output and returns `True` if it's acceptable).
   - Call `model_fn(case.input)` for every case. If `model_fn` or `check` raises, the case **fails**: one broken case must not crash the whole run.
   - `CapabilityResult` holds `capability`, `total`, `passed`, `pass_rate` and `failed_ids` (in the order the cases were given).
2. `gate(results, thresholds, baseline=None, max_regression=0.02)` returns a `GateDecision(approved, reasons)`.
   - A capability with **no threshold** blocks the release: no agreed bar, no go-live.
   - A capability whose `pass_rate` is below its threshold blocks the release.
   - If a `baseline` (capability → previous pass rate) is given, a drop of **more than** `max_regression` blocks the release, even when the threshold is still met.
   - A capability with a threshold but **no results** blocks the release: you can't approve what you didn't test.
   - `reasons` has one human-readable string per problem, each one naming the capability. `approved` is `True` only if `reasons` is empty.

## Run

```bash
uv run pytest katas/06_eval_gate -m "not stretch"
```

## Stretch

- `CapabilityResult.upper_error_bound`: the Wilson upper bound of the error rate at 95% (reuse your kata 01). Add a `gate(..., use_confidence=True)` mode that compares `1 - upper_error_bound` against the threshold instead of the raw pass rate, so a capability with only 20 cases can't pass by luck.

## Discussion questions

1. Your golden set has 40 cases for one capability. What's the smallest pass-rate difference you can trust between two prompt versions?
2. A check uses an LLM as judge. What breaks in this design, and how do you keep the judge honest?
3. The provider updates the model silently. How does this gate catch it if nobody changes the prompt?
4. Product wants to ship with one capability below threshold because "it's still better than before". What do you say, and what would you need to agree?
