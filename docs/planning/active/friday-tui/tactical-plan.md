# Friday TUI tactical plan

**Status:** Superseded implementation sequence; planning redesign required

**Branch:** `feature/friday-tui`

execution_phase: planning; validation_state: not_ready

The [architecture reset](architecture-reset.md) withdraws the Chat-dependent
sequence and CD-TUI-001. The historical steps below are not implementation
instructions; replace them with independent-package units and revised UAT gates
before requesting product-code authority.

## Current authorized slice

1. Preserve the previously revised README while moving its packet from queued to
   active; keep historical archive/evidence paths unchanged.
2. Record the maintainer's request as approval to start design/planning only.
   Set the board to `started`, authority `design_only`, delivery `local`, and the
   dedicated branch. Do not approve the newly authored build plan on the user's
   behalf or grant product-code authority.
3. Construct the build plan, record product questions and source observations,
   and define phases, acceptance mapping, validation and stop conditions.
4. Incorporate accepted Q-01/Q-02/Q-03 into the requirements: macOS/Linux,
   multiline editing with an explicit submit shortcut, and safe-point quit with
   non-interruptible work and cleanup completed before exit.
5. Draft the [integration contract](integration-contract.md), explain the
   technical tradeoffs in [decisions.md](decisions.md), and prepare the exact
   first [construction directive](directives/CD-TUI-001-shared-presentation-contracts.md).
   Reconcile the registry's argument metadata and capture a limited unchanged
   CLI/Chat baseline plus a metadata-only Textual dependency resolution.
6. Validate the planning transaction and record the exact stop point. Product
   code, dependency installation and publication are outside this slice.
7. Incorporate the maintainer's continuous-testing/UAT requirement: break phases
   into bounded testable units, split the first directive's check boundaries and
   schedule real-user UAT from the first shell through the installed candidate.
8. Preserve the shared Friday runtime/configuration surface: record D-06,
   AC-14/FR-11, shared startup precedence and CFG-01..06 checks; keep profile
   discovery/setup proposals separate from current explicit-path behavior.
9. Inventory extra UX options and propose an additive `tui` namespace in the
   existing CLI presentation file (D-07, FR-12/AC-15). Keep settings unimplemented,
   preserve current root fields and first-directive scope, and bind future
   UXCFG-01..08 plus user preference UAT to the appropriate construction units.
10. Record the maintainer's agreement with that UX design and align the README,
    contract, build/test plans and authority. Distinguish accepted design from
    pending implementation, deferred features and unexecuted UAT.

## Proposed implementation ordering

| Order | Work package | Main evidence before next package |
| --- | --- | --- |
| 1 | TUI-00 / G0 | Review concrete decisions, baseline command/dependency evidence, typed integration contract and CD-TUI-001. |
| 2 | CD-TUI-001 / 00A then 00B | After approval, implement/check the pure display reader first, independently verify it, then implement/check the shutdown report; combined scope remains five Chat source/new-test paths. |
| 3 | TUI-01A..C | Bootstrap/package checks, worker bridges, then usable shell; each has passing tests/review before dependent work; user-approved UAT-01 before G1. |
| 4 | TUI-02A..J (F1..F3) | Test each command group and its fixture effects as built; demonstrate family UAT as it becomes usable; complete parity and combined UAT-02 approval for G2. |
| 5 | TUI-03A..C | Check streaming, active Quit and failure/cleanup units separately; user-approved UAT-03 before G3. |
| 6 | TUI-04A..B | Check extension/discovery, then terminal interaction; user-approved UAT-04 before G4. |
| 7 | TUI-05A..B | Clean installed matrix, then aggregate validation and final installed UAT-05 on both targets; completion proposal remains separate from maintainer acceptance. |

Each product-code unit requires a separately approved construction directive
with exact paths, candidate baseline, checks and stop conditions. Begin by
rechecking board, branch, authority and current source. If the baseline changes,
reconcile it before using historical counts or results.

The [incremental test and UAT plan](test-and-uat-plan.md) is the canonical unit
breakdown, dependency map, UAT scenario schedule and evidence/signoff format.
All 24 proposed units and five UAT checkpoints remain unexecuted. Start with
behavior and failure cases, implement a small path, test immediately, then
freeze/review before dependent work. User UAT is required at the scheduled
gates; a missing target or unanswered signoff remains blocked/pending, not passed.

## Required test groups for future directives

- Unchanged `packages/friday-cli/tests_cli` and relevant
  `packages/friday-chat/tests_chat` command, display, config and lifecycle suites.
- Registry-derived inherited-command/alias/argument cases with equivalent CLI and
  TUI fixtures; include invalid input and unavailable backend cases.
- TUI headless keyboard/input, clear-view, multiline paste, help/completion,
  chunk/progress ordering, slow operations and cleanup tests.
- Disposable real-store export, reset and maintenance integration tests with fake
  model/provider transports; preserve exact execution-intent flags.
- Extension addition, duplicate name/alias rejection, typed effects and
  per-frontend registry isolation; repeat baseline cases after an extension.
- With/without-TUI installed CLI compatibility, pure display-config loading,
  dependency compatibility and source/entry-point invariance checks.
- Supported terminal-size/resize/Unicode/key/restoration matrix, package resource
  and installed-executable checks outside the checkout.

CD-TUI-001 selects concrete commands/test files for the first shared-interface
unit; later directives must do the same for their slices. Do not claim these
groups have passed merely because the plan lists them. The existing 241-test
source profile passed; this is not TUI or installed-distribution evidence.
Record known baseline failures separately and keep existing tests intact.

## Planning verification

Run the existing board validator and dashboard consistency check; validate local
links, active packet status and retained-history references; reconcile the
README's command inventory with the current source; check whitespace and the
exact diff allowlist. Confirm `packages/`, tests, scripts, workspace metadata,
lockfile and governance policy files are unchanged from the source baseline.

The full documentation checker has six previously recorded temporary-checkout
links in an unchanged historical telemetry report. Recheck and report that
baseline separately; do not rewrite frozen validation evidence to clear it.

## Stop point

After planning checks, leave the active packet ready for review of the concrete
technical contract, build plan and CD-TUI-001. Q-01 through Q-03 are accepted;
T-01 through T-08 have concrete proposals and rationale in
[decisions.md](decisions.md), but are not approved on the maintainer's behalf.
No application implementation, commit/push, PR, merge, release or publication is
part of this request.
