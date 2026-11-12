# INGEST isolated readiness harness — council closeout handoff

Current: bounded test-only Docling behavior and actual Nomic end-to-end flow are
independently verified, including the reporting-source correction. Original live
receipts remain attributed to c977; corrected reporting proof is offline-only.
The branch is started/local. Production source/configuration/stores are unchanged.
Whole Gate-A9.5 and product construction/acceptance remain open.
[Measured results](gate-a/end-to-end-evaluation/results.md) and
[independent report](gate-a/end-to-end-evaluation/validation/round2/report.md).

**Next gate:** Fresh independent review of the isolated long-document corpus:20 genuine documents plus5 references, native complete-text validation and87 tests per mode. Qwen token counts/serving and larger-context inference remain pending; no production or model/default change.

## Historical branch/design preparation (superseded for current evaluation routing)

[Pass2 reconciliation](gate-a/verified-directive-report.md) is **VERIFIED** for
construction-document readiness/source feasibility at candidate `474479df`.
Sol10.0/9.6, Astra10.0/9.6, Opus9.6/9.5 (coverage/overall), no mandatory findings.
The [authorized loop](gate-a/correction-loop/authorization.md) stops early after
two of four corrective passes; no pass3/pass4 or replacement is launched.

The [directive v0.3](../../directives/CD-CMD-INGEST-GATE-A-001-readiness-harness.md),
[execution contract](gate-a/execution-contract.md), [plan v0.5](gate-a/readiness-plan.md),
envelope/isolation rules, nine business inputs and numeric ceilings keep their
reviewed bytes. [Advisories](gate-a/correction-loop/pass2/results/advisory-disposition.md)
remain visible as future implementation/activation considerations; they do not
silently alter those rules or grant effects authority.


All executable harness work remains future under `tests/readiness/ingest/`, with
runtime state under `.friday_test/`. No code, environment, dependency, conversion,
model/service/store effect or production change was made. Separate exact approval
precedes test-only C0 construction; real A0–A4 stages and the actual shared-LM-Studio
production-offline/restart/log-separated window need separate activation/receipts.
No runtime qualification, human acceptance, production resumption or delivery is
inferred from these document reviews.


Current construction authority: [exact C0 approval](gate-a/construction-approval.md).
It supersedes earlier pending-construction routing only. Real A0–A4 effects and
production/model/store operations remain unactivated.
