# REM-MCP-UP-004: Refresh admission and nested input-request validation

Status: Proposed; exact maintainer approval required before remediation.
Work unit: MCP-UP-04. Prepared 2026-10-13.

## Objective and controlling authority

Repair the independently reproduced refresh-admission and nested InputRequests
classification findings while keeping the original CD-MCP-UP-004 scope and
optional-feature boundary. This is a separate security remediation gate under
AGENTS.md and the independent-validation policy. A separate remediator must
perform the source edits; the original builder must not perform the security fix.
The original independently reviewed candidate, controls, captures, original
review, failed probes and preconstruction evidence remain immutable.
[Original independent report](../validation/VAL-UP04-01/report.md),
[original safe evidence](../validation/VAL-UP04-01/stored-manifest.json),
[bound verification profile](../verification-profile-REM-MCP-UP-004.json) and
[exact proposal manifest](../proposals/REM-MCP-UP-004-authority-manifest.json)
control this packet together with [approved UP-04 authority](../authority-UP-04.json).

Baseline: independently reviewed candidate
`138fb68e33b94d20c17bbaff79ec6be3c8bfc3fb`, product
`8170c26b541433dcd5b9107d44a1c7a4a92fdd83`.
The bound MCP targets remain2026-07-28, explicit2025-11-25 HTTP and preserved2024
legacy defaults. No dependency, checker, capability or publication change.

## Exact three-file product scope

- `packages/friday-mcp/src/friday_mcp/client/base.py`
- `packages/friday-mcp/src/friday_mcp/client/protocol.py`
- `packages/friday-mcp/tests_mcp/client/test_result_refresh.py`

Authority receipts, this directive, proposal/profile, requirement/test mapping,
execution/review evidence, log/current state and board/dashboard are process paths.
No other product/source/test/doc file changes are authorized. Any additional
product path requires an exact scope amendment before editing.

## Finding mapping and required fixes

### VAL-UP04-001: Failed admission-limit refresh leaves old wrappers usable

The reviewer reproduced a lower concurrent_requests=1 configuration in which
an explicit second refresh raises limit_exceeded before invalidating the prior
usable catalog, and an old public wrapper subsequently issues one mutating call.
This violates RES-AC-01/02/03/08 and the failed/limited-refresh contract.

Retire usable catalog/admission state before an explicit refresh can fail at
its admission/limit gate, including the interval before an owned discovery task
begins execution. Retire2025 raw-call recovery compatibility data when an explicit
refresh fails. Preserve serialized overlapping refresh, the original absolute
operation deadline, bounded owner/concurrency counts and retryable cleanup.
Do not let an older operation overwrite or clear newer successful publication;
do not gratuitously cancel already-issued calls or replay tools/call.

Use the original independent public-API reproducer as a regression. Exercise
constructor concurrent_requests=1 through4, immediately rejected refresh,
failed/cancelled/partial refresh, public adapter reads and retained wrappers,
with modern stdio-like and both dated HTTP profile parity.
Assert current usable snapshot/admission is unavailable and zero post-failure
mutating calls are issued. Prove later explicit successful refresh/reconnect
and already-issued output-schema/header binding remain correct.

### VAL-UP04-002: Nested input-request subtype and form grammar classification

Use the complete pinned modern schema and MRTR capture to validate the declared
sampling message content union separately from ordinary tool-result content.
Valid sampling tool_use and tool_result must receive the fixed
input_required_unsupported disposition. Sampling content outside its declared
union, including resource_link, must be invalid rather than mislabelled valid.
Validate the restricted elicitation form-property union and its mandatory fields
before unsupported disposition; malformed property schemas must be invalid.
Preserve date-specific ordinary ToolResult content, error and structured-output
rules, bounded JSON/depth/result/schema budgets and metadata grammar.

Produce a precise variant/field matrix from the pinned schemas, with valid,
malformed and omitted/explicit-null cases and actual source/test/command evidence.
Exercise the actual public modern stdio-like request loop and modern HTTP path
with exact fixed codes, sentinel privacy, zero follow-up I/O and cleanup.
No sampling, roots, elicitation callback, input-response fabrication, opaque-state
forwarding, URL/resource/media fetch or continuation is enabled. Tests must prove
zero continuation/callback/public I/O as well as exact failure-code classification.

## Acceptance and mandatory verification

Both original findings must resolve with reproducible positive/negative public-API
proof. Preserve all ten original RES-AC criteria and repeat the entire original
20-command verification profile against a single stable corrected commit with
per-command argv/environment/source/guard freezes and fresh private caches.
Compare all327 complete Ruff diagnostic/fix objects and four inherited Mypy
path/line/column/code/message objects to the accepted baseline. Preserve complete
skip locations/reasons and normalized warning sections; report observed new test
counts. No waiver, suppression, checker weakening or dependency change.

Only named private SDK stdio/literal127.0.0.1 TLS and accepted cross/root fixtures
under the existing pinned guard are permitted. Preserve unrelated user files,
root overlay, original reports and all failed attempts. No credentials, live
providers, public peers, real user stores or remote publication.

Commit a stable corrected candidate. Retain the original CHANGES_REQUESTED
report, superseding it only for decision on the corrected candidate. A fresh
read-only validator must perform the remediation delta followed by full UP-04
work-unit validation; VERIFIED precedes a completion proposal, and maintainer
acceptance remains separate. Stop on scope/control drift, a new semantic finding
or a necessary product path outside these three files.
