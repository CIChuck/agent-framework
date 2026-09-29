# VAL-002 Independent Validation Report

Outcome: `CHANGES_REQUESTED`

## Candidate Identity

- Initiative: `development-kanban-governance`
- Work unit: `independent-validation-governance-remediation`
- Review mode: aggregate
- Repository base: `63cb579e37d65cce7f2a6186ee0dc05092ee1ac5`
- Amendment base: `3553901849362137a7c1d1e14bfcd51915d1567d`
- Prior candidate: `12c1e9e577409bf25f7fdc18fb7bb75a24f5ec07`
- Candidate: `7eea978b598025b9920c34c5b80a4d543e0dfb42`
- Aggregate diff: 32 files, 3,092 insertions, 108 deletions
- Documentation amendment: 27 files, 1,225 insertions, 183 deletions
- Request SHA-256:
  `0a8b2a2140f25a64111d704d506c32bdef32fb2eabbf0c2c38a5ee538fe8fb25`

The reviewer confirmed the revision ancestry, candidate HEAD, all eleven
authority hashes, both prior-review hashes, and final candidate stability.

## Independence And Provenance

- Reviewer: `/root/independent_validation_val_002`
- Model: Codex/GPT-5; exact build unavailable
- Completed: `2026-09-03T21:44:17Z`
- Context: fresh subagent without builder transcript, private reasoning, or
  conclusions
- Prior review use: only to re-evaluate the two named VAL-001 findings
- Access: read-only shared checkout; not a detached worktree
- Repository or external mutations: none

## Finding

### VAL-002-F01 — Medium: reopening can silently downgrade delivery history

Affected files:

- `scripts/friday-dev-board.py`
- `tests/integration/test_development_board.py`

Violated authority:

- Delivery is an independent, monotonic record of observable facts under the
  development task lifecycle policy.
- `TP-04` requires correct state-transition and delivery commands.
- The packet and `AGENTS.md` require delivery to remain separate from work
  state.

Evidence:

- `completed -> started` is an allowed work-state transition.
- Every transition into `started` unconditionally sets `delivery_state` to
  `local`.
- The dedicated delivery command correctly rejects backward delivery movement.
- Reopening completed work previously marked `pushed`, `merged`, or `released`
  can therefore erase the recorded delivery fact.
- Existing tests do not cover reopening a completed task with an advanced
  delivery state.

Risk:

The canonical board and rendered dashboard can misstate whether work was
pushed, merged, or released, weakening the audit trail.

Required mitigation:

1. Preserve the existing delivery state during `completed -> started`.
2. Promote only an initial `not_started` state to `local`.
3. Do not downgrade `local`, `pushed`, `merged`, `released`, or `unknown`.
4. Add regression coverage for reopened completed work with advanced delivery
   states while retaining initial-start coverage.
5. Re-run focused Ruff and mypy, integration tests, board and documentation
   validation, and aggregate diff checks.

This remediation requires Python and test changes. The current
documentation-only exemption and `REM-001` forbid those changes, so fresh
maintainer authority and an approved construction directive are required.

## Prior Finding Dispositions

- `VAL-001-B01`: **resolved**. `AC-01` through `AC-13` and `TP-01` through
  `TP-15` each occur exactly once and exactly match the VAL-002 request.
- `VAL-001-F02`: **resolved**. The reported trailing blank line was removed and
  aggregate `git diff --check` exits `0` with no output.

## Acceptance-Criterion Matrix

| ID | Result | Evidence summary |
| --- | --- | --- |
| AC-01 | PASS | Board validation and packet enumeration cover all 22 tasks. |
| AC-02 | PASS | Deterministic rendering and board/dashboard comparison pass. |
| AC-03 | PASS | Agent roles are rejected for approval and acceptance; negative tests pass. |
| AC-04 | PASS | Branch and completion-evidence gates are implemented and tested. |
| AC-05 | PASS | Packet placement follows state and condition; board validation passes. |
| AC-06 | PASS with finding | Acceptance evidence is enforced; delivery reopening defect is VAL-002-F01. |
| AC-07 | PASS | Documentation lifecycle and local-link validation pass for 293 files. |
| AC-08 | PASS | Amendment changes no guide, package source, entrypoint, or workspace metadata. |
| AC-09 | PASS | Work remains `started` pending validation. |
| AC-10 | PASS | Validator role and external-effect prohibitions are explicit and observed. |
| AC-11 | PASS | Revisions and hashes are pinned; stale-review behavior is explicit. |
| AC-12 | PASS | REM-001 maps both findings and preserves the two-cycle limit. |
| AC-13 | PASS | Fresh aggregate review occurred before completion or acceptance. |

## Tactical-Task Matrix

All tactical tasks pass except `TP-04`. `TP-04` fails because work-state
reopening can violate the independent delivery-state contract described in
`VAL-002-F01`. `TP-15` correctly preserves the gate: this result cannot move the
initiative to `completed`.

## Commands

- Board validation: pass; 22 tasks
- Documentation lifecycle: pass; 293 Markdown files
- Integration tests: pass; 18 tests in 3.69 seconds
- Aggregate diff check: pass; empty output
- Documentation-amendment protected-path query: pass; empty output
- Authority hashes: pass; 11 of 11
- Prior-review hashes: pass; 2 of 2
- AC/TP uniqueness and request matching: pass; 13 of 13 and 15 of 15
- Focused Ruff: pass
- Focused mypy: pass
- Final candidate stability: pass

No required check was skipped. Network, credentials, paid services, persistent
runtime state, push, merge, release, and deployment were forbidden and not used.
One auxiliary `uv` invocation encountered sandbox cache denial; equivalent
direct-environment commands passed and no required check was affected.

## Baseline And Residual Risk

The modified `.DS_Store`, untracked Friday Chat backup, and controller-owned
VAL-002 request were excluded from the candidate. No package source, guide,
entrypoint, workspace metadata, or lockfile changed in the documentation
amendment. The review used a shared checkout rather than a detached worktree;
HEAD, authority hashes, request hash, and status were rechecked.

## Disposition

Keep the initiative `started` and mark its condition `blocked`. Store proposed
construction directive `REM-002`, but do not execute it without explicit
maintainer authority to modify the board script and its tests. After authorized
remediation, commit a new stable candidate and dispatch a fresh aggregate
validator.
