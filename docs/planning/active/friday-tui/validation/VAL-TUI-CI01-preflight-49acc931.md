# TUI-CI01 Moltbook-candidate independent preflight

**Outcome:** `CHANGES_REQUESTED` on 2026-10-18 for candidate
`49acc931ac1fe5a610b94f0005d67f8c1ef6c7ad`. This is historical
evidence; a later candidate needs fresh review.

**Reviewer:** fresh-context, read-only agent
`/root/tui_ci01_moltbook_review_49acc931` (model/version not exposed to the
controller). The reviewer made no repository edits or external calls.

**Authority and revision:** TUI-CI01 construction base `d69c1d72`;
full diff `d69c1d72..49acc931`; Moltbook/diagnostic remediation delta
`505c4c1d..49acc931`. At the reviewed revision, SHA-256 hashes were:

- `docs/planning/board.yaml`: `793d22a42dd74a5048964c3d617358a024355143d97b3a368366c35a734e5417`
- `authority.json`: `2cb36c87c5c2316668a276777baf1bac77c50c5301bb547f831bd1fbd00e43da`
- `CD-TUI-CI01-linux-actions.md`: `12b026f6723f12fa4a17c3676bc631aaec3ddee162554f9e8de57d9610c3a568`
- TUI packet `README.md`: `53bc6e25dd3daf441227a3f78c0badd5197ae4167ec86c70e717878753be6134`

**Passed checks:** The candidate was clean and the hashes matched. Full and
remediation diffs stayed in CI01 scope. Locked/offline export and dry run
selected Moltbook, finance, MCP, `cryptography` and `pytest-mock`. Workflow
YAML, ten Bash scripts and four embedded Python blocks parsed. Its
cancellation-aware guards let independent suites and wheel checks run after
an earlier test failure without suppressing that failure, and Moltbook
remained outside initial installed Runtime isolation. Board validation,
dashboard and diff checks passed.

**CI01-05 — Medium, conflicting current authority.** The active packet
README said the board had `design_only` authority after N01A closeout, but
its header, authority manifest and board showed `granted` authority for
TUI-CI01. It also said to resume automated Linux checks when a runner
became available, although CI01 was running on GitHub-hosted Ubuntu.

**CI01-06 — Medium, stale next gate.** The board and generated dashboard
still called for a run of the finance-corrected candidate `505c4c1d`.
That candidate had already failed, and the reviewed candidate added
Moltbook selection and diagnostics. The current gate must refer to the
next complete CI01 run and independent review.

**Exit gate:** `RD-TUI-CI01-07` assigns the current-state corrections. The
first three Ubuntu runs failed, including the MCP stdio case twice; no
Linux verification is claimed. A new frozen candidate, fresh preflight,
complete Ubuntu run and final work-unit review remain required.
