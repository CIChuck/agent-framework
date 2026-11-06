# TUI-CI01 second-candidate independent preflight

**Outcome:** `CHANGES_REQUESTED` on 2026-10-18. This is historical evidence
for candidate `3086f7d73efd48533c69d329305cb27c4c03dfcc`; a later
candidate requires fresh review.

**Reviewer:** fresh-context, read-only agent
`/root/tui_ci01_mcp_sync_review` (model/version not exposed to the
controller). This file transcribes the reviewer's final verdict; the reviewer
made no repository edits or external calls.

**Authority and revision:** TUI-CI01 construction base `d69c1d72`;
remediation delta `e3e2e974..3086f7d7`; full CI01 diff
`d69c1d72..3086f7d7`. At the reviewed revision, SHA-256 hashes were:

- `docs/planning/board.yaml`: `051d3461309c0966f23401d96c594975bea52edd043d14ef8871ae4efbf62229`
- `authority.json`: `0a518646149102403e903557c9d075154b30b3a50a78d37dda65d0626c629e12`
- `CD-TUI-CI01-linux-actions.md`: `a1927f738d64757a2cf2b97a6c9202c1e7fc1c1897a1553afbf1040d29ad63fa`
- TUI packet `README.md`: `afe2b4c69722b4873bcf7414cde38019a3e0596b29492af8644a6926bfeab0ba`

**Passed preflight checks:** The ten changed CI01 paths were in scope. uv
0.11.3 locked/offline export and dry run selected `mcp==2.3.0`,
`cryptography==50.0.2`, and `pytest-mock==3.15.1`. Workflow YAML, nine Bash
scripts, four embedded Python blocks, action pins, expression contexts and
source/checkout SHA logging passed. Board validation reported 34 tasks;
dashboard check, lock check and diff checks passed. The documentation
lifecycle checker retained only six unrelated broken absolute links in
telemetry `VAL-001`.

**CI01-03 — Medium, current packet-state mismatch.** The reviewed
`execution-log.md` header still named TUI-N01A as the active candidate
awaiting validation, although N01A is closed and the packet index and latest
log entry identify TUI-CI01 as awaiting an Ubuntu rerun. The reviewed board
next gate still called for correcting locked MCP selection, already present
in the candidate. The current packet process fields and board next gate must
agree under the [development task lifecycle policy](../../../../reference/policies/development-task-lifecycle.md)
and [independent validation policy](../../../../reference/policies/independent-validation-policy.md).
Correct the log header and board gate, regenerate the dashboard and recheck
them. No workflow or package configuration change is required.

**Exit gate:** `RD-TUI-CI01-03` in the construction directive assigns this
correction. Freeze a new candidate, obtain fresh-context read-only review,
then rerun Actions for its exact SHA. The failed first Ubuntu run does not
establish Linux verification; all suites and installed-wheel checks remain
required. Linux terminal UAT remains a later final-candidate gate.
