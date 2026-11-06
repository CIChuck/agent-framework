# CD-CMD-CHK-001 — bounded checkpoint reconciliation

Date: 2026-11-06
Status: **PROPOSED — explicit maintainer decision required before execution**
Initiative: `friday-command-refactor`
Findings: AGG-001 and AGG-002 in the [aggregate report](../validation/checkpoint/aggregate-report.md)
Product/source base: `dea496075de55060ad477820e04b71c78239cca0`

## One requested decision

Approve this exact directive, including the one-time historical exception below
and the five-file mechanical formatting correction. After approval, record the
actual date, maintainer, directive hash and source base before editing. Complete
fresh independent validation, then use the existing authorized push/PR/merge/
new-branch sequence. No additional feature or retirement approval is requested.

## AGG-001 — exact historical exception

The branch already contains archival validation behavior in
`scripts/friday-dev-board.py` and `tests/integration/test_development_board.py`.
It entered through `40f9ed6f8e510fcaf9da08c6638ba1338e2bb8e8`, carrying changes
from `78126dcd9a5a3cb1c9ce6078855f25578e9e97b3` and
`c3bfff8bea2cd87fcdfc0ec2684de8262a4ffb3c`. The historical direction authorized
archival, but an exact construction directive for the automation was not found.
The September adoption exception does not cover these later changes.

Requested exception: explicitly permit retaining this existing archival behavior
for the checkpoint, limited to the exact [two-file base-to-candidate delta](../validation/checkpoint/historical-archival-board.patch),
SHA-256 `1001e73202db0670f9e1f267876dfea3fc68650b91780bbe2f7bc46af0a3fe22`.
This is a current, one-time exception to the construction-directive chronology,
not backdated approval or a claim that archival permission originally covered
code generation. Existing checkpoint delivery permission alone does not supply
this exception.

The retained requirements are: accepted historical evidence belongs in its
archive-local `historical/` directory; declared authority manifests and evidence
paths must validate; accepted tasks cannot leave their old active packet behind;
completion/acceptance and delivery remain distinct. The aggregate reviewer
independently passed all 57 board integration tests and archive integrity checks.
Fresh review must inspect this exact behavior and its positive/negative tests.
No new archival feature or source behavior is permitted under this directive.

Exception owner: Chuck Russell. Reason: reconcile an inherited, independently
tested automation change before publishing the checkpoint. Tracking: AGG-001.
Closure: record explicit current approval, preserve the original chronology and
exact patch, obtain fresh independent verification and retain the ordinary
directive requirement for all future code work. The exception ends at this
checkpoint; it creates no ongoing waiver.

## AGG-002 — mechanical formatting only

Run the installed Ruff formatter only on:

- `packages/friday-chat/tests_chat/test_mcp_http_integration.py`
- `packages/friday-mcp/src/friday_mcp/client/protocol.py`
- `packages/friday-mcp/tests_mcp/client/test_http_lifecycle.py`
- `packages/friday-runtime/tests_runtime/test_mcp_runtime_config.py`
- `scripts/friday-dev-board.py`

These five files were format-clean at the aggregate base and now fail. Preserve
all runtime behavior, type/API/dependency/configuration contracts, test assertions
and historical evidence. Verify each before/after Python AST is identical with
location attributes excluded; save source/AST hashes and actual formatter argv.
Do not reformat the five separately proven pre-existing failures or other files.
Do not modify the historical board test logic while recording AGG-001.

## Required verification, reports and limits

Use the frozen/no-sync offline editable overlay from the aggregate request,
with no root environment sync, downloads or lock regeneration. Disable bytecode,
pytest/Ruff caches; put mypy/build output in scratch. Record approval-only
administrative descendants and verify product equality to the source base before
formatting. Preserve both unrelated working Chat example configurations exactly.

Require AST equality, focused lint/format/type checks, the board tests and
affected MCP/Runtime/Chat tests, board/docs/metadata/offline-lock/whitespace
checks, and no product/path/metadata drift beyond the five formatting files.
The ordinary root Ruff/pytest and five older formatting failures remain explicit
baseline debt under the existing policy; this directive supplies no new waiver.
Full optional-cohort cache limits remain accurately disclosed.

Commit a stable changed candidate and provide a fresh-context read-only
validator the complete base-to-candidate aggregate diff, original two findings,
this exact approval/exception, original report/receipts, before/after AST proof
and actual verification. Require an evidence-backed VERIFIED result for both
findings and cumulative checkpoint readiness. The validator must independently
assess complete relevant source/contracts and may reuse old receipts only with
explicit current-input equivalence evidence. No stale verdict carries forward.

Allowed process records: this directive and its approval, aggregate requests/
reports/receipts, packet index/checkpoint/execution log, and command-only board/
dashboard entries. No source/test changes beyond five-file formatter output;
no new runtime features, dependencies, configuration edits, retirement, TUI
construction, real provider/tool/store execution or credential disclosure.

Stop for missing explicit exception approval, source/authority drift, AST
inequality, a new functional failure, outside-path need or unresolved independent
findings. No unattended remediation loop. Existing delivery authority remains
valid once fresh aggregate verification and actual PR requirements are satisfied.
