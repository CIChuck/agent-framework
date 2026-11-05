# Shared Friday command refactor

**Maintainer decision update — 2026-11-04:** Apply the resolved
[O-01–O-05 decisions](scope-decisions.md#maintainer-decisions--2026-11-04):
nine complete removals, `/tools` retained, a 41/3 target, shared
`friday-commands` ownership, preserved generic CLI behavior and retained-command
quirks. Earlier proposals below are superseded where they conflict. Exact API,
capability mapping, baseline evidence and construction approval remain pending.

**Status:** started; approved scope; contract characterization underway

**Board ID:** `friday-command-refactor`

**Branch:** `feature/command-refactor` (independent baseline `c3426986`,
the current `master` at branch reconstruction)

**Implementation authority:** task scope granted for design and
characterization; product code still requires an exact approved construction
directive.

`execution_phase: planning`; `validation_state: not_ready`.

**Date:** 2026-10-25

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
| Command baseline | [Command matrix](command-matrix.md) and [JSON snapshot](validation/command-matrix.json) | The 50-name, three-alias before-change Chat surface and PAR case IDs, including the nine retirement cases; not a post-refactor target or parity result. |
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
The approved [MCP client compatibility exception](directives/CD-CMD-MCP-001-compatibility-exception.md)
records the maintainer-requested Draft-07 and query-URL fixes as a separate,
bounded unit on this branch; it does not advance the command P0–P5 gates.
Two further MCP issues are documented:
[tool continuity across conversation turns](proposals/mcp-tool-turn-continuity.md)
and [server-neutral input-schema compatibility](proposals/mcp-schema-compatibility.md).
The schema issue has an [approved exact construction directive](directives/CD-CMD-MCP-003-server-neutral-schema.md)
for its bounded implementation unit and an
[engineering matrix](mcp-schema-engineering-matrix.md) for the supported profile.
They are separate from the shared-command contract and from each other:
registration determines which tools exist in Chat, while per-turn selection
determines which registered schemas the model receives. Both proposals remain
planning only.
There is no approved technical contract yet; the architecture proposal must
be reviewed at P1. Package ownership and CLI preservation are decided; exact
API, capability mapping and compatible primitive reuse evidence remain pending.

**Current decision boundary:** Retain the current behavior of every maintained
command that survives the nine selected retirements. The exact API and compatible CLI primitive reuse must be reconciled in an
approved contract and bounded directives; removal behavior and preservation
policy are settled by O-01–O-05. Consolidation remains backlog work.

**Next gate:** Characterize current Chat and separate CLI behavior, settle
the exact shared contract under the recorded maintainer decisions, then
review the exact command contract and first bounded construction directive.
No command source change is authorized by activation alone.

The [next-phase checkpoint](next-phase.md) identifies the bounded P0/P1
continuation and the review stop before product construction.

Initial P0 observations are in the [source ledger](validation/par-coverage-ledger.md)
and [baseline receipt](validation/p0-baseline.md). The initial dirty-worktree Chat baseline was red. The
[controlled baseline](validation/p0-failure-disposition.md) passes all 826 Chat
tests using committed examples and xterm. Case-level behavior and installed-package
proof remain open.

Review inputs now include the [production/effect audit](validation/production-effects-audit.md),
[foundation API draft](shared-command-api.md) and
[draft first directive](directives/CD-CMD-FND-001-neutral-foundation.md).
Family port signatures, installed proof and gate approval remain open.

## Foundation design remediation — fresh review pending

[CMD-DESIGN-001](approval/foundation-design.md) is revised under the maintainer's
2026-11-05 authorization to resolve the three [council findings](validation/COUNCIL-CMD-DESIGN-001-round1.md).
The [remediation record](remediation/REM-CMD-DESIGN-001.md) maps each correction
and validation. Earlier VERIFIED reports cover older bytes only. A fresh review
of the corrected candidate is pending. Overall execution remains planning, with
P0/P1 incomplete and product construction unauthorized. No design approval is recorded.
