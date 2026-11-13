# REM-CMD-INGEST-C0-001 — bounded C0 control corrections

Status: correction cycle1 under exact approved C0 construction, not an amendment
to the frozen harness directive or activation of any upstream stage.
Base candidate: `ecfa38bb71854bb3174ceb9ee82cbb87ef110e69`.
The [fresh C0 report](../validation/document-ingestion/gate-a/construction/c0/review1/report.md)
returns CHANGES_REQUESTED. Its result remains historical until a new frozen candidate
receives fresh delta-first and full bounded CC-01–10 validation. This is the first
remediation cycle; the repository's two-unsuccessful-cycle stop rule applies.

Authority: approved CD-CMD-INGEST-GATE-A-001 v0.3, exact construction-approval.json
and private static-tool approval. Fixing the existing four violated CC obligations
is necessary within that approved scope. No new effect/profile or feature is granted.
Under the independent validation policy a separate remediator handles these security
controls; the controller freezes/records evidence and a new context validates.

| Finding | Required correction and positive/negative evidence |
| --- | --- |
| C0-F01, high | Refuse supported unpropagated standard and qualified low-level Python thread startup before launch, including import-before-guard aliases. Test `threading.Thread` and low-level shapes normal/-O; no outside marker may appear. Keep any supported worker non-escalating and document the exact boundary. |
| C0-F02, high | Reject unsupported dir_fd forms for every controlled mutation API, including chmod/utime. Audit the remaining admitted forms. Normal/-O rejection must preserve fake target mode/time/content, with ordinary owned-path positives. |
| C0-F03, medium | Instrument/refuse os.access and inventory equivalent supported Python-visible discovery APIs. Outside-present and outside-absent probes refuse identically in both modes; keep declared-root positives and dir_fd negatives. Canonical ancestor metadata never grants arbitrary outside probing. |
| C0-F04, medium | Recheck revocation and expiry after counting/reservations immediately before fake transport handoff. Changes in those callbacks yield zero calls/actual attempts; conservative prior budget charges remain. Preserve valid flow and describe the bounded accepted-in-flight boundary. |

Allowed source edits: `tests/readiness/ingest/startup.py`, `window.py`,
`tests/test_protection.py`, `tests/test_window.py`, `tests/test_startup.py` only
if needed for alias/startup coverage, and README.md for precise supported boundaries.
Parent technical/authority/business inputs, bootstrap.py, run.py, dependencies,
all production packages/tests/configuration and stores are unchanged. Planning
status, this directive and correction evidence may be recorded by the controller.
No opportunistic generic sandbox expansion, live HTTP, actual stores, cleanup,
working-venv use for harness/static tests, downloads or A0–A4 effect activation.

Run normal/-O selftests from private exact-byte snapshots during remediation;
new regressions must reach their intended call assertions. Setup/import failures
earn no rejection credit. Run root-rule private Ruff/format/mypy, then controller
commits source and repeats formal checks from the committed export. No supplied
scratch/cache may be used as an output target. Document all failed/setup attempts
separately and preserve full production/dirty/generated metadata boundaries.

Completion requires all four IDs independently closed and full bounded CC01–10
conformance on the changed candidate. No whole-harness readiness, user acceptance,
new council loop or delivery authority follows. Full A0–A4 obligations remain open.
