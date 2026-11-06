# Local command-refactor continuation

Date: 2026-11-06
Status: Local baseline refreshed; foundation design review and approval pending
Execution phase: planning
Validation state: not_ready

The maintainer requested continuing the command refactor. This continuation
refreshes evidence and corrects active navigation in `agent-framework` on
`feature/command-refactor`; it does not record design or construction approval.
HEAD is `f6f018150391dcf0ffa870258250f254eb22d899`. The planning transfer remains
uncommitted, so this is working-tree evidence, not a frozen review candidate.

## Scope and preservation

Documentation-only continuation is authorized by the maintainer's request.
The lightweight scope is this receipt, local evidence, active packet navigation,
the next-phase checkpoint and execution log. No runtime behavior is changed.
Product source, tests, configuration, package metadata and lockfiles are unchanged.
The local Chat example edits and backlog draft are preserved by before/after
hashes in [baseline identity](baseline-identity.json).

Historical receipts and manifests remain intact. The earlier TUI reconciliation
describes a different destination; its differing/missing source classifications
do not describe this Agent Framework checkout.

## Local evidence

- All 84 source/test files in the historical P0 inventory match locally, with no
  missing or changed files. This comparison establishes identity only for that
  inventory, not all transitive dependencies or installed distributions.
- Generic CLI: `uv run pytest -q -ra packages/friday-cli/tests_cli` passed
  **155 tests**, zero skips, in 0.23 seconds.
- Controlled Chat: **826 passed**, zero skips, one existing deprecation warning,
  in 45.12 seconds. See [log](head-examples-xterm-full-chat.log) and
  [command/environment receipt](full-control.json).
- The Chat control reuses the historical isolation helper through `runpy`, with
  `ROOT` set to this repository, `OUT` set to this new evidence directory and
  `sys.argv` set to the helper's `--full` mode. A temporary collection plugin
  redirects only the two example-sensitive modules to temporary HEAD example
  blobs. `TERM=xterm-256color`; the explicit live-LMStudio module is excluded.
  The historical helper and output paths are unchanged.

Board validation passed for 36 tasks and `git diff --check` passed. All protected
file hashes remained unchanged. [Check results](checks.json) also record the
documentation-lifecycle failure: four broken links in pre-existing imported TUI
evidence reference product files absent in this checkout. Those files and links
were not changed here. No new continuation-document link failure was reported;
the repository-wide documentation gate remains red.

This rerun confirms the controlled baseline in this working home. It does not
establish case-level PAR signoff, isolated-wheel operation, live-provider proof,
P0/P1 completion or independent verification. The unmodified dirty-example suite
was not rerun; its historical failure disposition remains separate.

## Next bounded gate

1. Freeze the current reconciled planning candidate with current authority pins;
   preserve unrelated configuration, backlog and TUI draft work separately.
2. Obtain fresh scoped design-readiness review for AP-01–AP-06, including the
   residual R2-SOL1-ARCH-001 wording correction and current working-home authority.
   The earlier council reports cover older bytes and remain historical.
3. Present [CMD-DESIGN-001](../../approval/foundation-design.md) for the maintainer's
   limited API-01–API-06 design decision after the required review.
4. Continue remaining characterization, family contracts and installed-client
   obligations. Separately approve the exact foundation directive and execution
   base, with explicit applicable P0/P1 disposition, before product construction.

The board's broad `granted` value does not approve the draft foundation directive.
No automatic council, product generation, phase closure or external delivery
follows from this continuation.
