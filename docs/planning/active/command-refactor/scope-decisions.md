# Shared command refactor — scope and decision register

**Status:** Maintainer decisions recorded through 2026-10-24; unresolved contract
choices below require review before construction. This record reconciles the
canonical [refactor intent](command_refactor.md), [scored inventory](command-inventory.md)
and [command matrix](command-matrix.md) for the approved [build plan](build-plan.md).
It does not replace an exact construction directive.

## Controlling decisions

| ID | Decision | Consequence for this refactor |
| --- | --- | --- |
| S-01 | Build one UI-neutral implementation for maintained Friday Chat slash commands. | Chat delegates to it; the later TUI adapter consumes the accepted contract. Keep frontend rendering separate. |
| S-02 | Retire `/clear-tools`, `/inject-tools`, `/recommend-tools`, `/run-tool`, `/tool-budget` and `/inject-payload` within this refactor. | The 50-command [source matrix](command-matrix.md) remains an as-built snapshot. The planned supported set is 44 canonical names if no further scope decision is made. The six retirement cases require explicit old-name, help, completion, documentation and compatibility checks. |
| S-03 | Preserve current behavior, names, aliases and syntax for commands that remain. | Migrate `/security`, `/security-config`, `/security-test`, `/workflow`, `/speech-test`, `/tools` and `/migrate` without behavior changes. `/migrate` stays through the first TUI version. A scored recommendation alone does not authorize a removal or repair. |
| S-04 | Defer behavior enhancements and consolidations C-01 through C-06. | Track session restore, security/workflow capability reviews, `/read` attachment, ingested-source validation, confirmation prompts, diagnostics and tool presentation in the [follow-up backlog](../../backlog/friday-tui-command-followups/README.md). Disregard the transcript model-identification comment for this scope. |
| S-05 | Execute and accept the command refactor before resuming TUI development. | TUI command integration and physical terminal parity are later TUI gates. The separate `friday-framework-cli` contract and regressions belong in this refactor. |

## Decisions required for the technical contract

| ID | Open choice | Required record before source work |
| --- | --- | --- |
| O-01 | What happens when each retired name is entered: unknown command or a bounded migration response? | Exact response, help/completion policy, release boundary and six-case compatibility exception list. The older [pruning review](command-pruning-review.md) suggests messages but is not a decision. |
| O-02 | What package, public API, typed result/effect model and capability boundaries own shared execution? | Reviewed contract with import direction, migration seams and protected Chat behavior. The [architecture document](shared-command-architecture.md) is a proposal. |
| O-03 | How does the separate `friday-framework-cli` benefit from shared primitives or an adapter while keeping its public registry and entry point? | Source-backed compatible reuse decision and concrete regression gate; if no safe seam exists, record the reason and protected baseline rather than changing its public API incidentally. |
| O-04 | How are scored `/prime`, `/set` and `/vars` retirement comments reconciled with the six-name scope? | Explicitly confirm their disposition before the supported-surface contract is frozen. Until then, no source removal of these names is authorized. |
| O-05 | Which observed Chat quirks are compatibility obligations and which are later defects? | Command-level baseline and any approved exception. No behavior correction is implied by extraction. |

## Change control

The [scored inventory](command-inventory.md) preserves the maintainer's raw
scores and commentary. The [refactor intent](command_refactor.md) preserves
the branch's architectural direction and explicit maintainer clarifications.
The [matrix and JSON snapshot](command-matrix.md) preserve the 50-name source
baseline, including names selected for retirement; they are not a
post-refactor target or passing test result. This register owns the current
scope synthesis, not the underlying feature intent. Reconcile it with the
three source documents, the [build plan](build-plan.md),
[phase plan](phase-plan.md), tests, help and guides when an open choice is
decided. Each product-code unit still needs its own approved exact directive
under the project [authority record](authority.json) and development board.
