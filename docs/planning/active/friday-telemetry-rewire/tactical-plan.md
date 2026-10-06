# Telemetry tactical plan

Status: TELEM-01 approved with CD-001 on 2026-10-05; later units require new directives.
Branch: `feature/friday-telemetry-rewire`.
Preparation base: `2155a0fc51f5b20dea4e35c6cfc70f1d52002735`.

| Unit | Work | Gate |
| --- | --- | --- |
| TELEM-01 | Strict local configuration, safe runtime observer, CLI/app lifecycle diagnostics, correct composite spans | Approve CD-001; record start; build a frozen candidate; fresh independent review |
| TELEM-02 | OTel parent/context/events and exporter lifecycle; explicit remote configuration/factory | New directive, deterministic collector coverage, independent review before remote activation |
| TELEM-03 | Safe typed/legacy/streaming/embedding metrics and role-service injection | Inventory construction paths, approve event schema and request/attempt identity; new directive |
| TELEM-04 | Native/MCP tools, memory, persistence, turn diagnostics and operational metrics | Approve correlation/outcome contracts; preserve accepted MCP boundaries; new directive |
| TELEM-05 | Optional Langfuse compatibility | Separate bridge/callback ownership decision and directive; does not gate core telemetry |

## TELEM-01 requirement and test mapping

| Task / criterion | Required evidence |
| --- | --- |
| T01-01 / AC-01: strict default-disabled local config | Default and enabled config loads, unsupported providers/fields/malformed types fail safely; existing compatibility fixtures pass |
| T01-02 / AC-02: runtime assembly and injection | Fake and stubbed-real construction expose the observer; custom override works with disabled config; CLI uses the same path; no vendor calls |
| T01-03 / AC-03: lifecycle truth and bounded inspection | Runtime/app events match assembly and cleanup outcomes; cancellation and failed cleanup are distinguishable; 256-event bound and retained failure/drop counts |
| T01-04 / AC-04: content boundary | Planted sentinels absent from all first-slice events/diagnostics; valid MCP events retain meaning; unknown/invalid event attempts counted and rejected |
| T01-05 / AC-05: composite correctness | Both child spans end with correct parents; duplicate/unknown end, empty composite, membership changes, mutation and sink failures |
| T01-06 / AC-06: regressions and closeout | Complete Chat and telemetry suites; repository Ruff and safe deterministic root pytest; changed-file Ruff; changed-source Python 3.13 mypy plus syntax/API and Python >=3.13.4 supported-runtime evidence; board/docs checks; exact candidate manifest and independent read-only review, under the [verification profile](verification-profile.md) |

The builder performs implementation checks; it cannot grant `VERIFIED`.
The controller freezes the exact authority and candidate for a fresh-context
validator, as required by `AGENTS.md`. Work stays `started` throughout review
and any separately authorized remediation. TELEM-01 verification does not
complete or accept the whole telemetry initiative.

## Approved REM-004 verification closeout

Maintainer explicitly approved REM-004 and WVR-002 on2026-10-05. R4-01 through
R4-06/R4-06b map the remaining VAL-005-F01 once. Execute the exact directive after
fresh A05 readiness, then require a stable product delta and aggregate review.
Only the exact326 historical lint findings are waived; all live lint, typing,
security, listener and deterministic test gates remain mandatory. TELEM-02
through TELEM-05 remain separately governed.
