# TUI-CI01 finance-candidate independent preflight

**Outcome:** `CHANGES_REQUESTED` on 2026-10-18 for candidate
`89a875acb14c02007cf6a1873428960210598a45`. This is historical
evidence; any later candidate needs fresh review.

**Reviewer:** fresh-context, read-only agent
`/root/tui_ci01_finance_review_89a875ac` (model/version not exposed to the
controller). The reviewer made no repository edits or external calls.

**Authority and revision:** TUI-CI01 construction base `d69c1d72`;
full diff `d69c1d72..89a875ac`; finance remediation delta
`7a41004a..89a875ac`. At the reviewed revision, SHA-256 hashes were:

- `docs/planning/board.yaml`: `0df106b76cb74e0553a34e7eeed456fd45592fca7b9707ab93ea8e547ac27d72`
- `authority.json`: `aa8126c45f98596bcd3a1bbde1c21be75d8e79c313080f0b13eac73ef485501a`
- `CD-TUI-CI01-linux-actions.md`: `5d07416a8e57af73c5d3725bfdad71b5de9c9dd56d5a057c64f40ecd88ffdef0`
- TUI packet `README.md`: `499accc5f97e335cf13f0734e28af14921ff5220dbb29e07ca8bdc8d5c50a888`

**Passed checks:** The clean worktree's full and remediation diffs were in
CI01 scope, with no protected product, test or lockfile edits. Board
validation and dashboard checks passed, as did diff whitespace checks,
workflow YAML, nine Bash scripts, four Python blocks, pinned actions and
read-only permissions. Locked/offline selection included the finance
package, its `massive` dependency, MCP, `cryptography` and `pytest-mock`.
The finance wheel was included only in the later Chat-side installation,
not the initial isolated Runtime environment. The second Ubuntu run tested
the older `7a41004a` candidate and failed; the MCP stdio outcome remained
open.

**CI01-04 — Medium, current packet-state mismatch.** The reviewed packet
index said validation was pending an Ubuntu rerun while the execution-log
header said `changes_requested`. The board next gate still called for the
finance correction already present in the workflow. Under the
[independent validation policy](../../../../reference/policies/independent-validation-policy.md),
current packet process fields and the board next gate must agree. Reconcile
the header and board gate, regenerate the dashboard and obtain a fresh review.
No workflow or package change is needed for this finding.

**Exit gate:** `RD-TUI-CI01-05` assigns the packet correction. A complete
green Ubuntu run for the new exact candidate and fresh final work-unit
review are still required before TUI-CI01 can be verified. Linux terminal
UAT remains a later final-candidate gate.
