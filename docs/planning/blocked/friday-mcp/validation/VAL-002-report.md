# VAL-002 — Independent MCP-WS-00 Remediation And Aggregate Review

**Verdict:** remediation delta `VERIFIED`; aggregate WS-00 candidate `VERIFIED`;
overall WS-00 validation gate `VERIFIED`.

**Reviewer:** Fresh-context Codex validation subagent, independent of the
builder and REM-001 remediator (model/version not exposed).

**Date:** 2026-09-27

**Modes:** Read-only delta review followed by aggregate work-unit review.

**Candidate:** `b79754f23aeee69ea3618b711c78f2c3e51edb71`

**Delta:** `3ad7454954b7a415a99a914ba0197a3a7d88be23..b79754f23aeee69ea3618b711c78f2c3e51edb71`

**Aggregate:** `20c70dd70622e5f1b80029076a789fb58c748fb5..b79754f23aeee69ea3618b711c78f2c3e51edb71`

The reviewer used the pinned [VAL-002 request](VAL-002-request.yaml), read
`AGENTS.md`, repository engineering, lifecycle, and independent-validation
policies, the build and tactical plans, the approved [WS-00 directive](../directives/ws-00-contract-policy-foundation.md),
the [rebaseline](../rebaseline-2026-09-27.md), [VAL-001](VAL-001-report.md),
[REM-001](../remediation/REM-001-directive.md), and both exact diffs. All ten
authority-document hashes matched the request. The reviewer made no repairs,
commits, board edits, or live/external calls. The post-candidate request commit
`eb2fb72` changed planning metadata only; reviewed source and tests remained
at the pinned candidate.

## Delta verdict — VERIFIED

- F-001 is resolved: `friday_core.mcp` now provides typed, content-safe
  security/workspace scoping, ingestion opt-ins, metadata schema estimate and
  sanitization/filter diagnostics, call/correlation identifiers and output
  sanitization/ingestion decisions, and per-server catalog/cache/rejection
  discovery state. Focused tests cover construction, serialization, defaults,
  and invalid values. These are contracts only; no consumer behavior changed.
- F-002 is resolved: normalization collisions fail closed with a bounded
  diagnostic identifying both source pairs by safe shape/length and a
  12-character SHA-256 fingerprint of each *name*. Regression tests check
  distinct-source and oversized-input cases. These fingerprints are not
  argument hashes and do not change the default no-stored-argument-hash policy.
- The remediation diff contains only the approved contract module, its focused
  tests, and the REM-001 implementation report. No new regression or scope
  expansion was found.

## Aggregate verdict — VERIFIED

The reviewer found evidence for all `MCP-00-01` through `MCP-00-08` criteria in
the complete WS-00 diff: framework-facing DTO ownership in `friday-core`
without a reverse dependency, public typed policy/provenance/discovery
contracts, a read-only tool-metadata sidecar strategy, conservative default
limits, fail-closed names and collisions, argument redaction/hash defaults,
stdio-only first-pass integrated transport posture, and no new broad mypy
suppressions. The existing `friday-mcp` protocol-local models and native tool
registry remain unchanged. No runtime loading, connection/discovery,
registration, Friday Chat, memory, transcript, telemetry, or CLI behavior was
introduced by WS-00.

Independent deterministic checks: **232 passed** across core, MCP, and
runtime tests; Ruff passed for core and MCP; focused mypy passed for
`friday_core.mcp`; board validation, dashboard freshness, documentation
lifecycle, and both diff whitespace checks passed. The request records the
exact commands. Package-wide mypy remains blocked by the environment's NumPy
stub syntax under the repository's Python 3.10 target; using Python 3.13
reaches four existing errors in untouched `friday_core.profiles.py`. The
broader integration suite's fixed 22-task board assertion already failed at
base `20c70dd` because the board had 23 tasks. These are baseline failures,
not candidate regressions.

**Findings:** none.

**Residual risk:** Later workstreams must enforce these contracts in runtime
configuration and execution, attach the metadata sidecar to registration and
reject native-tool collisions, implement persistence redaction, and validate
live MCP interoperability under separately approved scope. This review does
not verify those unimplemented behaviors or approve WS-01 through WS-08.

`VERIFIED` closes the independent validation gate for WS-00 only. The wider
`friday-mcp` initiative remains `started`; no maintainer acceptance, merge,
delivery, or later-workstream authority is implied.
