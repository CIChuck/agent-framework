# INGEST-001 — approved impact and readiness harness handoff

Chuck [approved exact package impact v0.6](../../approval/ingest-package-impact.md).
[Round6](package-impact/current-verified-report.md) remains VERIFIED only for its
unchanged pinned documents/source feasibility.

Prepared for one explicitly authorized read-only [directive council](gate-a/council-round1/authorization.md),
not construction/effects activation:

- [Gate-A plan v0.3](gate-a/readiness-plan.md) and [effects envelope](gate-a/effects-envelope.json).
- [Manual harness and isolation requirements](gate-a/isolation-requirements.md).
- [Draft CD-CMD-INGEST-GATE-A-001](../../directives/CD-CMD-INGEST-GATE-A-001-readiness-harness.md).
- [Exact public candidate observations](gate-a/source-observations.json) and [consumer worklist](gate-a/consumer-readiness-matrix.md).

All versioned harness code, probes, fixture generators, test configuration and
harness tests belong under `tests/readiness/ingest/`. Generated installations,
document copies/assets, caches/logs and results belong under `.friday_test/`.
No harness source/test directory or runtime environment has been created yet.
The directive supplies explicit test selectors; root pytest excludes `tests/`.

Chuck permits the existing local LM Studio endpoint to be reused after production
is shut down, the server restarted and test logs separated. A separate server
and copied served weights are no longer required. The operator owns shutdown,
restart and later production resumption. No model call is permitted until the
run-specific window, endpoint/model/counter facts, manifests, budgets and actual
log-separation mechanism are bound. Reachability is not shutdown/restart evidence.
No such window is currently confirmed; A3 remains unactivated.

The next gate is reconciliation of all three fresh council reports against
[HRC-01–16](gate-a/council-round1/criteria.md), with both scores at least 9.5 and
no mandatory findings from every seat. The single authorized round grants no
automatic remediation/replacement loop. Later comes exact directive approval, then
separately recorded stage activation and manifest promotion before dependencies,
conversion or model effects. Public metadata/source research is the only completed
upstream work. This council authorizes no production mutation, store operation or delivery. The operator's server-restart permission does not grant the harness
service-management rights.

Preserve the [test migration](../../test-migration-plan.md), [canonical architecture](../../command-architecture-update-plan.md)
and [guide](../../guide-update-handoff.md) requirements for later product work.
The [round6 carry-forward](package-impact/round6/readiness-carry-forward.md)
remains a readiness input. Measured readiness will finalize the impact appendix
and exact product construction directive. Unchanged assessment bytes need no
repeat approval; material changed impact returns for exact-version review.
