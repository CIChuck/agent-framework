# REM-GUIDE-002 — Retained validation-log representation

Status: authorized evidence correction within the maintainer's documentation
upgrade and CD-GUIDE-001/REM-GUIDE-001 governance/evidence scope.
Controlling authority and all guide content remain unchanged.
Frozen reviewed candidate: 6fb53e00877214d813656b204f950c8a0b725d05.
Independent report: validation/second-review/report.md, CHANGES_REQUESTED.

GUIDE-003: remove trailing spaces from the readable historical replay log,
preserve original bytes losslessly as base64 JSON, and reconcile the retention
manifest with both original and display hashes. Retain both independent reports
unchanged. The initial report remains historical, superseded for decision
purposes by subsequent validation. No whitespace waiver applies.

Allowed changes: this packet's evidence/directive/process records and board
state only. No changes to any of the 25 guides, product files, tests, metadata,
configuration, dependencies or controlling authority. No external effects.

Required checks: decode originals and verify their hashes; verify every retained
manifest and both historical reports; compare all 25 guides and fenced examples
byte-for-byte with the second reviewed candidate; run board/render/docs and
working, staged and aggregate committed-range whitespace checks. Freeze a new
candidate and obtain fresh-context read-only delta and aggregate validation.
Stop on guide/product drift, provenance loss or any further unsuccessful
remediation cycle; return unresolved findings to the maintainer.
