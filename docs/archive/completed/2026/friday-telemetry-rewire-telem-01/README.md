# TELEM-01 accepted: local telemetry assembly

Status: accepted work unit. Initiative: `friday-telemetry-rewire`.
Accepted by: repository maintainer Chuck Russell.
Accepted at: 2026-10-06.
Acceptance evidence: explicit conversation response **"accepted"**, following
TELEM-01 VERIFIED closeout and the stated next gate of TELEM-01 acceptance.

## Accepted scope and evidence

Accepted work unit: CD-001 / TELEM-01, including bounded REM-001 through REM-004
under approved A01–A06 and WVR-002/WVR-003. AC-01 through AC-06 are satisfied by
fresh independent delta and aggregate review of product candidate
`8aedd87c8def5a6c514bdfea7505205e8db78bb6` from aggregate base
`2155a0fc51f5b20dea4e35c6cfc70f1d52002735`.
Evidence-only closeout commit: `00238817eeb76e971766651a552bfae685ac8c04`.

- [Independent VERIFIED report](../../../../planning/active/friday-telemetry-rewire/validation/VAL-006/report.md), SHA-256 `b67d8271acfdd7f6b6f4d49d58220ce354423eaa5c8ebde9993694d26009e421`.
- [Independent evidence](../../../../planning/active/friday-telemetry-rewire/validation/VAL-006/evidence.json), SHA-256 `a063afd3549bc842292368306cf160a6e8f19b290589e604fe47e6a9233b0733`.
- [Execution closeout](../../../../planning/active/friday-telemetry-rewire/execution/REM-004-final/report.md).
- [Continuing initiative packet](../../../../planning/active/friday-telemetry-rewire/README.md).

Accepted behavior is strict default-disabled provider-neutral local Chat
telemetry assembly, caller-owned injection, safe bounded runtime/application
lifecycle inspection and correct Composite span fan-out. Full deterministic root
checks passed with2,804 tests and one optional SciPy skip; complete Chat and
telemetry passed741 with five existing live-gated skips. Changed-source typing
and changed-file lint passed. Root Ruff remained raw nonzero with exactly326
immutable archival findings plus one unchanged invariant CommandRegistry UP046,
covered by the separately approved exact waivers at this acceptance decision.
The unchanged optional OTel console-exporter shutdown diagnostic remains a
recorded residual issue.

## Acceptance boundary and follow-ups

This archive records acceptance of TELEM-01 only. The broader initiative remains
started in its active packet; TELEM-02 through TELEM-05 are unfinished and require
their own directives. The existing authority and validation artifacts remain
unchanged in that continuing packet, preserving their frozen paths and hashes.
Delivery remains local.

WVR-002 and WVR-003 expire after this TELEM-01 acceptance decision under their
existing terms. They retain historical validity for the accepted candidate and
are not renewed or extended to later work. Maintainer-owned REM-004-HIST-01 and
REM-004-GENERIC-01 policy decisions remain follow-ups before acceptance beyond
TELEM-01. This acceptance does not change source, suppress lint, activate remote
exporters, or authorize push, merge, release or deployment.
