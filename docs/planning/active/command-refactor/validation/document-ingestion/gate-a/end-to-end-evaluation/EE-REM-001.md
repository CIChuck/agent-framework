# EE-REM-001 — conversion-source reporting binding

Controller-directed bounded remediation of **E2E-IV-001**, Medium / EE-07,
under the approved isolated harness and maintainer's complete end-to-end request.
This corrects test reporting integrity only; no production or live-model effect.

The independent review of `cae6aa4c` found that the canonical report CLI still
returns PASS after only the copied conversion helper changes. The original
experiment remains attributable to its committed `c9777736` source.

Use a separate remediator as required by independent-validation policy for data
integrity. Allowed code: `tests/readiness/ingest/e2e.py`, its `tests/test_e2e.py`
and a necessary local README clarification. Limit runtime changes to reporting
source binding. Preserve all conversion/chunking/inference/storage functions and
the verified `behavior.py` bytes. No production source, dependency, lock,
configuration, model/service, supplied runtime, store, live receipt or cleanup.

Before report PASS, require a nonempty immutable per-run behavior binding and
compare it to the current physical conversion source. Reuse the runner digests
already carried by corpus conversion attempts. Missing, malformed, conflicting,
changed or aliased behavior source/binding must refuse explicitly. Retain own-
runner checks and all existing evidence hashes/failure controls. A historical
normal result need not match the later optimized conversion attempt pointer;
compare the source digest, not a newer attempt's identity.

Add positive and source-tamper controls, including canonical normal/-O report
CLI proof in new private fixtures. Demonstrate missing/mismatched source binding
and preserve existing failure/artifact/current-e2e checks. Use synthetic report
fixtures solely for reporting-control credit; never claim new inference or new
live execution of corrected code. Focused static checks and complete offline
regressions remain required.

Freeze a new candidate and obtain fresh delta-first, full bounded EE-01–08 review.
The unchanged live functions may be AST-compared to `c9777736`, with the original
actual experiment inspected and clearly attributed. No additional model request
or replay budget is authorized or needed for this reporting-only correction.
The original stores, archive and live result receipts remain byte-identical;
corrected reporting tests do not rewrite/relabel them as current-code execution.
Whole Gate-A 9.5, product construction, acceptance and delivery remain open.
