# WVR-002 proposal: immutable historical MCP probe diagnostics

Status: Proposed; no maintainer approval and no operative waiver.
Date: 2026-10-05. Work unit: TELEM-01 / REM-004.
Owner: repository maintainer Chuck Russell; controller records exact evidence.
Follow-up: REM-004-HIST-01, described below. WVR-001 is separate and unapproved.

The [exact scope inventory](../remediation/REM-004-scope.json) freezes 326 Ruff
diagnostics in four accepted MCP validation probe artifacts, their normalized
path/code/location/message identities and complete SHA-256 file hashes. They
account for 326 of the 337 preexisting findings and 326 of the current 459;
the Python target change added no findings in these archive files. The current
133 live findings are excluded from this proposal and must be fixed.

The exception preserves reproducible accepted evidence. Reformatting those probes
would change their recorded review artifacts; adding a global exclude or rule
suppression would hide future problems. This proposal changes only the explicit
gate disposition for the exact historical findings, leaving files and root Ruff
invocation untouched.

If explicitly approved, the validator must independently run unchanged root Ruff,
retain its raw nonzero result, normalize paths and compare a sorted multiset of
path/code/location/end_location/message to the 326 archive entries in scope.json.
Verify all four SHA-256 file hashes, zero additional diagnostics, zero live
diagnostics, and all other mandatory checks passing. The report states
"root Ruff nonzero; exact 326 archival findings covered by approved WVR-002"
instead of claiming raw lint passed. No pytest, typing, security, localhost,
source/API, telemetry or future-phase failure is covered.

Cleanup point: REM-004-HIST-01 is a proposed archive-validation policy decision
owned by the maintainer, to be considered before aggregate acceptance beyond
TELEM-01. It must decide how archived executable evidence is validated without
rewriting prior proof. No automatic archive edits or implementation are authorized.
This exception expires after the TELEM-01 acceptance decision or immediately
if any archive content hash, covered diagnostic identity, Ruff version/target,
or lint configuration changes. Local evidence-closeout commits with unchanged
governed content do not extend its work-unit scope. Renewal requires explicit
maintainer approval and fresh independent review.

Approval of REM-004 preparation or construction alone does not approve WVR-002.
Until explicitly approved, aggregate AC-06 remains nonpassing.
