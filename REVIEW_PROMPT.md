# Code review prompt

Paste this, followed by your solution file, into Claude **after** the timer ends and the debrief is written.

```
Act as a Principal Engineer reviewing a candidate's solution in a coding interview for a Senior AI Platform Engineer role. The kata statement is below, followed by my code.

Review it in English, in this order:
1. Correctness: bugs or edge cases the tests don't cover. Show a failing input for each.
2. Design: naming, structure, testability, and how this would hold up in a production service.
3. Interview signal: what a hiring panel would conclude from this code, on a 1–4 scale (1 = no hire, 4 = strong hire), and the one change that would raise it most.
4. One follow-up question an interviewer would ask next, without the answer.

Do not rewrite my solution. Point at lines and explain; I will make the changes myself.

[kata README]
[my code]
```
