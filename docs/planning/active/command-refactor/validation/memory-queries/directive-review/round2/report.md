# MEMQ directive council round 2 — CHANGES_REQUESTED

Candidate `0001357262bd86d17ce4f9a43c7bf98cc9115534`; correction cycle1.
All original reports are exact preserved bytes with hashes in [evidence](evidence.json).

| Seat | Result | Score | Exact report |
| --- | --- | --- | --- |
| GPT-6.1 Sol/high | CHANGES_REQUESTED | 8.8/10 | [Sol](sol.txt) |
| GPT-6 Astra/high | CHANGES_REQUESTED | 9.1/10 | [Astra](astra.txt) |
| Claude Opus 5.5/high | CHANGES_REQUESTED | 8.6/10 | [Claude](claude.txt) |

Two mandatory issues remain:

1. MEMQ-DIR-R2-SOL-001 / MEMQ-DIR-R2-CLAUDE-001: required six-member union
   expansion conflicts with the preserved exact-union helper in test_diagnostics.py.
   Permit only six expected members through the existing contracts import;
   preserve equality, old members, acceptance/refusal loops and node invocation.
2. MEMQ-DIR-R2-ASTRA-001: current README line123 still says implement D0/D1,
   contradicting the readiness stop above it. Phase wording also remains stale.

All original technical corrections are independently closed. Astra identifies
current-state reconciliation as incomplete; Sol/Claude did not report that
stale lower gate. The concrete unqualified lower README instruction confirms
Astra's finding; no majority vote overrides it.

Private synthetic union controls reject the expanded union at the canonical
call-phase assertion while the unchanged control passes. Claude's broader
synthetic D1 run has three shared setup/environment failures, excluded from
correctness credit; the additional union assertion is the differential finding.
No future product implementation is validated by these stubs.

Bounded source/correction/documentation checks and all frozen identity audits
passed. Full original commands, provenance, limits and criteria matrices remain
in the raw reports. Prior results and scores are historical, not carried forward.
Known root and formatting debt stay failed/unwaived.

Chuck Russell's “lets apply the corrections and iterate” authorizes the next
bounded correction, [REM-CMD-MEMQ-DIR-002](../../../../remediation/REM-CMD-MEMQ-DIR-002-union-and-gates.md).
This is correction cycle2; unresolved mandatory findings after the fresh review
return to the maintainer. Product D0/D1 remains stopped. No acceptance or delivery.
