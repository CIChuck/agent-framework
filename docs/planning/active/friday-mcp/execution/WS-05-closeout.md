# MCP-WS-05 Review Checkpoint

Date: 2026-09-28
Status: Independent review complete; correction required; not VERIFIED or accepted
Initiative: `friday-mcp`
Work unit: `MCP-WS-05`
Branch: `feature/friday-mcp-ws05-execution`
Candidate: `2388e747ba1bf8157881230ad36ae3ef3272b807`
Original work-unit base: `a609f948fe2d869ac29d0cce29d22d9334cd7d08`
Approval/start: `5e86df832a311a62509fb0838f6c45b6ecd6fdfa`
Delivery: Local

Fresh `/root/mcp_ws05_val011`, created with `fork_turns: none`, returned complete
work-unit aggregate **CHANGES_REQUESTED**. The [complete independent report](../validation/VAL-011-report.md)
is preserved byte-for-byte with all 182 original evidence members and 149
verified portable links in [lossless evidence](../validation/VAL-011-evidence.yaml).
Its original report, member manifest, delivery manifest and archive are unchanged.

Two High findings prevent WS-05 completion or acceptance:

- **VAL-011-F-001:** inherited raw MCP session config snapshots persist configured
  environment values in SQLite and expose them in JSONL session headers, including
  metadata-disabled exports, and CSV `export_all_sessions` session metadata.
  Ordinary single-session CSV entries/Markdown did not expose the sentinel in
  these probes. This violates the approved aggregate runtime-only capture policy.
- **VAL-011-F-002:** a later native call reusing an earlier MCP ID leaves ambiguous
  continuation/record IDs. That ambiguity is inherited; WS-05's new strict pairing
  guard additionally causes `TurnPersistenceError` and zero stored entries for
  a completed mixed turn that the base persisted. Keep the pairing guard and
  native IDs intact while correcting upstream MCP correlations.

All 17 required commands ran independently. Focused tests: 201 passed. Transcript:
34 passed. Agent: 209 passed. Core/MCP/Runtime: 416 passed. Memory: 680 passed/one
skip. Ruff, all twelve affected-source Python-3.13 typing, lock, board/dashboard,
documentation and frozen aggregate/preservation checks pass. Full Chat and
integration retain the independently reproduced PTY/three localhost fixture and
board-count failures; default mypy retains NumPy's target syntax failure. Commands
remain explicitly nonzero; no filters, silent skips, debt fixes or invented waiver.
Counts overlap and are not additive.

Independent public probes: 22 passed/five failed, corresponding to the two findings.
The reviewer built three offline wheels, inspected actual dependency metadata and
completed isolated extracted-wheel imports/typed round-trips without editable
hooks. A clean offline resolver lacked cached pydantic-settings; this limitation
and the declared-dependency-byte fallback are explicitly recorded. Public cleanup
assertions and defensive finally settlement are distinguished. No live providers,
real credentials, network UAT, dedicated MCP ingestion, telemetry or delivery.

Report SHA256: `0e79c26a3cb90557228c06db7b7d8cc2de68410b19843c789a8b9f18cf9f3266`.
Archive SHA256: `e7c457abf84ba8de84ca87b04ee8a50fa906101157b8682bad980986b69d62c4`.
At review start/closeout, all 978 tracked product/test/config files, 30 authorities,
four reports, request and five unrelated fingerprints match. No governed edits
or fixes were made by the reviewer; controller changes are process metadata only.

Next gate: explicit approval of the concrete [REM-006 proposal](../remediation/REM-006-directive.md)
and a separate remediator. Eight allowed implementation paths, both findings,
regressions, six remediation criteria and full delta/original-aggregate VAL-012
requirements are reviewable. The original WS-05 directive forbids automatic
security/package remediation; this draft does not supply approval or dispatch.
Phase remediation/state changes_requested describes that gate, not executed fixes.

Accepted WS-00 through WS-04 remain intact. The wider initiative stays
started/granted/normal/local; it is not completed/accepted. After approved fixes,
freeze a new candidate and obtain a new fresh read-only delta plus complete
WS-05 aggregate review. Explicit WS-05 acceptance and all later-phase/initiative
aggregate/delivery approvals remain separate. No historical database cleanup
or wider security redesign is authorized by this checkpoint.

## REM-006 Approval And Execution Gate

The maintainer subsequently said "fix them - proceed", explicitly approving
the complete bounded REM-006 directive and separate remediator. Execution starts
from `dd6a337eb2928ab4050ea70fb41dc77072210e34` on the existing WS-05 branch.
Next implement the approved corrections/regressions, freeze a new candidate and
obtain fresh read-only VAL-012 delta plus complete original WS-05 aggregate.
No new verdict or acceptance exists; the original VAL-011 report remains unchanged.
