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

## Canonical planning chain

The three command documents below are the canonical product-intent sources for
this branch. Read them together when deriving or revising the build, phase or
tactical plans. A later plan may detail an accepted decision, but cannot
silently replace the intent, maintainer commentary or source baseline.

| Role | Canonical file | What it controls |
| --- | --- | --- |
| Authority | [Board](../../board.yaml) and [authority record](authority.json) | Task state, branch, current scope and the requirement for an exact approved construction directive before product code. |
| Feature intent | [Refactor discussion](command_refactor.md) | Why this branch exists, shared-owner and harness-evolution direction, migration sequence, protected behavior and maintainer clarifications. Candidate pruning and construction ideas remain proposals where labeled. |
| Maintainer priorities | [Command inventory](command-inventory.md) | Focus areas, command scores and comments, recorded command decisions, architecture opportunities and deferred consolidation ideas. Assistant recommendations remain advisory. |
| Command baseline | [Command matrix](command-matrix.md) and [JSON snapshot](validation/command-matrix.json) | The 50-name, three-alias before-change Chat surface and PAR case IDs, including the six retirement cases; not a post-refactor target or parity result. |
| Reconciled scope | [Build plan](build-plan.md) and [scope decisions](scope-decisions.md) | The approved objective and current decisions derived from the three intent sources; open choices and deferred work stay explicit. |
| Contract input | [Shared-command architecture](shared-command-architecture.md) | Proposed ownership and dependency direction; package, API and CLI role still need explicit review and approval. |
| Evidence standard | [Test strategy](test-strategy.md) | Required regression classes for phases and bounded units. |
| Sequence | [Phase plan](phase-plan.md) | Phase outcomes and exit gates derived from scope, baseline and evidence standard. |
| Execution | [Tactical plan](tactical-plan.md) and [execution log](execution-log.md) | Current characterization tasks and actual work receipts; future code units need their own directives. |

The [scope decision register](scope-decisions.md) reconciles the recorded
decisions across the three intent sources; it does not demote the scored
inventory or refactor discussion to historical input. Keep the matrix and
refactor discussion reciprocally linked as command scope changes. The
[pruning review](command-pruning-review.md) preserves an obsolete seven-name
proposal as historical reasoning. The
[branch isolation record](branch-isolation.md) explains the independent
history and eventual TUI reconciliation. The
[command follow-up backlog](../../backlog/friday-tui-command-followups/README.md)
holds behavior changes and consolidation proposals outside this extraction.
There is no approved technical contract yet; the architecture proposal must
be reviewed and its open package/API and CLI-role decisions recorded at P1.

**Current decision boundary:** Retain the current behavior of every maintained
command that survives the six selected retirements. Old-name behavior,
package/API design and CLI integration must be reconciled in an approved
contract and bounded directives. Consolidation remains backlog work.

**Next gate:** Characterize current Chat and separate CLI behavior, settle
their shared-contract roles and the six retired names' old-name response, then
review the exact command contract and first bounded construction directive.
No command source change is authorized by activation alone.
