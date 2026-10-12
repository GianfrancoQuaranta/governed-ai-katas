# Kata 01 · Wilson release gate

**Timebox: 30 minutes**

## Scenario

> An agent generates 50,000 collection reminders for tomorrow's campaign. Compliance says the campaign can only go out if the error rate is at most 1%, with 95% confidence. Reviewers can read a few hundred messages, not 50,000. Build the math that decides whether the campaign ships.

## Requirements

Implement three functions in `wilson_gate.py`:

1. `wilson_interval(errors, n, confidence=0.95)` returns `(lower, upper)`, the Wilson score interval for the error rate.
   - Raise `ValueError` if `n <= 0`, `errors < 0` or `errors > n`.
   - Bounds must stay within `[0, 1]`.
2. `zero_error_sample_size(max_error_rate, confidence=0.95)` returns the minimum number of reviewed items, all error-free, needed to claim the error rate is at most `max_error_rate`. Use the exact formula, not the rule of three.
3. `release_decision(errors, n, threshold, confidence=0.95)` returns:
   - `"approve"` if the upper bound is at or below the threshold,
   - `"reject"` if the lower bound is above the threshold,
   - `"need_more_samples"` otherwise.

Use only the standard library. `statistics.NormalDist` gives you z for a confidence level.

## Formulas

Wilson interval, with p̂ = errors / n and z the two-sided critical value:

```
center = (p̂ + z² / 2n) / (1 + z² / n)
margin = z · sqrt(p̂(1 − p̂)/n + z² / 4n²) / (1 + z² / n)
```

Zero-error sample size: the smallest n such that (1 − p)ⁿ ≤ 1 − confidence.

## Run

```bash
uv run pytest katas/01_wilson_gate -m "not stretch"
```

## Stretch

- `required_sample_size(expected_error_rate, threshold, confidence=0.95)`: the smallest n such that, if you observe errors at exactly the expected rate (rounded down), the Wilson upper bound is at or below the threshold. Return `None` if it is impossible (expected rate ≥ threshold).

## Discussion questions

1. Your sample shows 2 errors in 300 and the threshold is 1%. Product says "0.67% is below 1%, ship it". What do you answer?
2. Why does the sample size barely depend on the campaign size (50k vs 5M)? When does campaign size start to matter?
3. When would you prefer Clopper-Pearson over Wilson?
4. Reviewers disagree with each other 5% of the time. How does that change your gate?
