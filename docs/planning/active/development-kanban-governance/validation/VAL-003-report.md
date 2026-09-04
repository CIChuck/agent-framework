# VAL-003 Independent Validation Report

Outcome: `CHANGES_REQUESTED`

## Candidate Identity

- Initiative: `development-kanban-governance`
- Work unit: `delivery-state-preservation`
- Review mode: aggregate; remediation cycle 2
- Repository base: `63cb579e37d65cce7f2a6186ee0dc05092ee1ac5`
- Documentation amendment base: `3553901849362137a7c1d1e14bfcd51915d1567d`
- Remediation base: `67d468cc90d5e62de4050e542c8d81e79b332490`
- Prior candidate: `7eea978b598025b9920c34c5b80a4d543e0dfb42`
- Candidate: `190e39ea5b7018d4ba43facd250cfe9b5a19ec3e`
- Aggregate diff: 37 files, 3,734 insertions, 108 deletions
- Remediation diff: 17 files, 205 insertions, 18 deletions
- Request SHA-256:
  `e11d096346c604cb533e022954e75bb43e2b33ec3ebeb8a7cd29b870326b2c74`

All revisions, ancestry, diff boundaries, eleven primary authority hashes, and
three remediation hashes matched. HEAD and the governed candidate remained
stable throughout review.

## Independence And Provenance

- Reviewer: `/root/independent_validation_val_003`
- Model: Codex/GPT-5; exact build unavailable
- Completed: `2026-09-03T22:28:19Z`
- Context: fresh validator without builder history, private reasoning, or
  conclusions
- Prior review use: VAL-002 supplied only the finding input
- Access: read-only shared checkout; not a detached worktree
- Repository or external mutations: none

## Finding

### VAL-003-F01 — Medium: mandatory backward-delivery regression is absent

Affected files:

- `tests/integration/test_development_board.py`
- `execution/REM-002-implementation-report.md`

REM-002 requires backward-delivery rejection to remain covered. The command's
guard remains implemented, and the new parameterized test covers initial
promotion plus reopening preservation for `local`, `pushed`, `merged`,
`released`, and `unknown`. No test attempts a backward delivery transition,
checks its error, or confirms that state remains unchanged after rejection.

The implementation report therefore overstates evidence when it says existing
backward-delivery tests remain passing.

Required mitigation:

1. Establish an advanced delivery state in a focused negative regression.
2. Attempt backward movement and assert exit code `1`.
3. Assert the rejection message and unchanged persisted delivery state.
4. Correct the implementation report to identify the new coverage accurately.
5. Freeze a new candidate and rerun the VAL-003 validation profile.

Because this is the second unsuccessful remediation cycle, further automated
remediation requires explicit maintainer disposition under the independent
validation policy.

## VAL-002-F01 Disposition

The behavioral defect is corrected:

- initial `approved -> started` promotes `not_started` to `local`;
- `completed -> started` preserves `local`, `pushed`, `merged`, `released`, and
  `unknown`;
- the backward-movement guard remains implemented;
- maintainer-only gates remain present and tested; and
- no unauthorized behavioral scope was found.

The finding cannot be closed because REM-002's mandatory negative regression is
absent.

## Requirement Evidence

All `AC-01` through `AC-13` requirements pass. All `TP-01` through `TP-15`
requirements pass at the aggregate plan level. REM-002 passes every behavioral,
scope, and gate requirement except its explicit backward-rejection test.

Behavior-bearing remediation is confined to the authorized board script and
focused integration test. No package source, guide, runtime configuration,
schema, enumeration, entrypoint, workspace metadata, lockfile, or
independent-validation policy changed.

## Commands

- Board validation: pass; 22 tasks
- Documentation lifecycle: pass; 296 Markdown files
- Focused board tests: pass; 10 tests
- Full integration tests: pass; 23 tests
- Focused Ruff: pass
- Mypy for the board script under repository configuration: pass
- Mypy for script and test under Python 3.13: pass
- Aggregate diff check: pass; empty output
- Aggregate and documentation-amendment protected-path queries: pass; empty
- AC/TP uniqueness: pass; 13 of 13 and 15 of 15
- Authority and remediation hashes: pass; 14 of 14
- Final candidate stability: pass

No required check was skipped. Combined script/test mypy under the repository's
Python 3.10 target reproduced the declared NumPy-stub syntax baseline; both
required mypy profiles passed.

## Baseline And Residual Risk

The modified `.DS_Store`, untracked Friday Chat backup, and controller-owned
VAL-003 request were excluded from the candidate. Review used a shared checkout,
but repeated revision, hash, status, and governed-file checks confirmed
stability.

Without a negative regression, future changes could weaken monotonic delivery
history without detection. The implementation report must not claim coverage
that the suite does not contain.

## Disposition

Keep the initiative `started`, close implementation authority, and mark the
packet blocked at a maintainer-decision gate. Do not execute a third remediation
cycle without an explicit maintainer exception to the two-cycle limit.
