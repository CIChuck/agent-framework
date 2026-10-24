# Shared Friday command refactor

**Status:** started; approved scope; contract characterization underway

**Board ID:** `friday-command-refactor`

**Branch:** `feature/command-refactor` (independent baseline `c3426986`,
the current `master` at branch reconstruction)

**Implementation authority:** task scope granted for design and
characterization; product code still requires an exact approved construction
directive.

`execution_phase: planning`; `validation_state: not_ready`.

**Date:** 2026-10-24

The maintained slash-command refactor is a framework and terminal-client work
unit with its own architecture, migration, compatibility and independent
validation gates. Friday TUI consumes its accepted result at the command
integration phase; the refactor is not a TUI construction subunit. The existing
Friday Chat command surface is the source baseline. Both Friday Chat and the
separate `friday-framework-cli` require explicit regression coverage; the
exact direct-consumer role of `friday-framework-cli` must be settled in the
command contract before implementation.

The canonical `feature/command-refactor` branch contains no Friday TUI package
source or TUI implementation history. TUI development is deferred until this
refactor is completed, tested, and accepted. The TUI branch's handoff index is
only a reference; command implementation belongs on
`feature/command-refactor`. Earlier TUI decisions and effect-map notes at
`01cbaa0b` are historical input. The reviewed command contract in this packet
will control implementation.

The [approved build-plan scope](build-plan.md) defines boundaries. The
[test strategy](test-strategy.md) defines the required characterization,
family-by-family regression and installed-client gates. The maintainer's
[scored command inventory](command-inventory.md),
[refactor discussion](command_refactor.md) and
[shared-command architecture proposal](shared-command-architecture.md)
are source inputs to this initiative; the architecture still needs a reviewed
technical contract before code work. The [command coverage matrix](command-matrix.md)
remains the 50-command before-change and TUI parity baseline. Keep it and the
refactor discussion reciprocally linked as command decisions are reconciled.
The [tactical plan](tactical-plan.md), [authority record](authority.json) and
[execution log](execution-log.md) track the active design phase.
The [branch isolation record](branch-isolation.md) explains the independent
history and eventual TUI reconciliation.

**Current decision boundary:** Retain the current behavior of every maintained
command that survives the six selected retirements. Retirements, old-name
behavior, package/API design, CLI integration, and any command consolidation
must be reconciled in an approved contract and bounded directives. The
[command follow-up backlog](../../backlog/friday-tui-command-followups/README.md)
holds behavior changes and consolidation proposals outside this extraction.

**Next gate:** Characterize current Chat and separate CLI behavior, settle
their shared-contract roles and the six retired names' old-name response, then
review the exact command contract and first bounded construction directive.
No command source change is authorized by activation alone.
