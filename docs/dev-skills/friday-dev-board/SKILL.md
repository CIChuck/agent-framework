---
name: friday-dev-board
description: Operate Friday repository development work from the canonical planning board, including task selection, authorization checks, lifecycle transitions, validation evidence, and acceptance handoff. Use for starting, resuming, completing, or reviewing Friday engineering initiatives; do not use it to infer approval or perform GitHub mutations without explicit authorization.
---

# Friday Development Board

Read these authorities before changing task state:

1. `docs/reference/policies/development-task-lifecycle.md`
2. `docs/planning/board.yaml`
3. the selected initiative packet
4. `docs/reference/policies/repository-engineering-policy.md` for code work

Use `uv run python scripts/friday-dev-board.py validate` before selecting work.
Use `next`, `list`, or `show <initiative>` to report current state and next gate.

Do not implement a queued task. Only explicit maintainer authorization permits
the `approved` transition, and only explicit maintainer acceptance permits the
`accepted` transition. A push, merge, plan label, historical approval, or user
silence is not a substitute.

For an authorized task:

1. Confirm dependencies and package boundaries.
2. Create the named feature branch and record the baseline.
3. Move the packet to the lane required by the target state and repair links.
4. Record the transition with the board command and update the execution log.
5. Confirm code-generating work has an approved construction directive or a
   maintainer-recorded lightweight-change exemption.
6. Implement only the approved scope and preserve unrelated worktree state.
7. Keep the task `started` while a stable candidate receives fresh-context,
   read-only validation under the independent validation policy.
8. Dispatch bounded remediation for `CHANGES_REQUESTED` only within recorded
   authority, then require a fresh review of the new candidate.
9. Move work to `completed` only after applicable validation is `VERIFIED`, and
   stop there for maintainer review unless acceptance is explicit.

Track `local`, `pushed`, `merged`, and `released` as delivery facts separate from
work state. Never push, merge, release, delete a branch, or change an external
system merely because a board transition is authorized.

Run both board validation and documentation lifecycle validation before handoff.
If the board, packet, dashboard, Git state, or execution log disagree, stop task
execution and reconcile the evidence before declaring the current stop point.
