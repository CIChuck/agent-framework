# Shared command refactor — tactical plan

**Status:** active P0–P1 design and baseline characterization; no product code unit
is authorized without an approved exact construction directive.

**Branch and baseline:** `feature/command-refactor` based directly on
`c3426986` (`master`), independent of `feature/friday-tui`. The separate [development board](../../board.yaml)
controls current task state. The [phase plan](phase-plan.md) defines the
sequence; the [scope decisions](scope-decisions.md), [build plan](build-plan.md),
[test strategy](test-strategy.md), [command matrix](command-matrix.md) and
[architecture proposal](shared-command-architecture.md) bound this planning phase.

## Ordered work and gates

1. **P0 — Baseline characterization.** Recheck the live Friday Chat registry,
   aliases, parser, help, handler dependencies and effects against the 50/3
   inventory. Inventory the separate `friday-framework-cli` registry, public
   API, completion and installed entry point. Open the PAR coverage ledger;
   capture baseline test commands, fixtures, counts, skips and known failures.
   Use disposable stores for effectful probes.
2. **P1 — Decide the exact supported surface.** Reconcile the six selected
   retirements, `/prime`, `/set` and `/vars` scored comments, retained-name
   behavior and old-name response with the scored inventory. Record any
   user-visible exception to the before-change matrix. Map all cases to
   retained families or the retirement unit, choose that unit's order, and
   identify cross-family scenarios and supported test environments. Do not
   fold deferred consolidation or behavior enhancements into extraction.
3. **P1 — Review the cross-client contract.** Decide the neutral package/API,
   command context and capability boundary, typed results and UI-effect
   intents. Determine how `friday-framework-cli` can reuse a concrete seam
   while preserving its different registry and behavior. Obtain independent
   architecture review and maintainer approval of the exact contract.
4. **P1 to P2 — Prepare bounded construction directives.** Start with registry metadata,
   name/alias resolution, argument parsing/help and a small effect family.
   Each directive pins allowed files, baseline, negative/effect cases,
   compatibility exceptions, installed checks and stop conditions. Do not
   generate product code until its directive is approved.
5. **P2 to P3 — Implement and verify by unit.** After each authorized foundation,
   retained-family or retirement unit, freeze a candidate, update the PAR
   ledger, run focused and cumulative Chat/CLI gates, and obtain a fresh-context
   read-only `VERIFIED` result.
6. **P4 — Cross-family integration.** Run the scenario map and installed
   package/client checks against a frozen candidate; reconcile every result
   with the P0 baseline and approved exceptions.
7. **P5 and later handoff to TUI.** Propose completion only after the shared
   owner and both current terminal-client gates are verified. Maintainer
   acceptance is separate.
   TUI development remains deferred until completion, testing, and maintainer
   acceptance. Deliver the accepted contract and evidence manifest to the
   independent TUI branch for its own parity and terminal UAT.

The current gate is steps 1–3: characterization and contract review. The
later steps are conditional on that gate and exact directives. No
handler migration, six-name retirement, help change or package source edit
is authorized by this tactical plan alone.

## Deriving a construction unit

For each proposed P2–P3 unit, the tactical implementation plan must cite its
phase gate, applicable [scope decisions](scope-decisions.md), exact PAR cases
from the [source matrix](command-matrix.md), and the approved technical
contract revision. Check the unit against the [refactor intent](command_refactor.md)
and maintainer [command inventory](command-inventory.md); record any apparent
conflict before proposing the directive. Pin allowed source/test/doc paths,
protected Chat and CLI
behavior, fixtures, exact commands and expected results from the
[test strategy](test-strategy.md). Record the candidate commit, independent
review and stop conditions in the exact construction directive before any
product source edit. A later unit cannot use this general tactical plan as
its construction authority.
