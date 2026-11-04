# Shared command refactor — scope and decision register

**Status:** Maintainer product and ownership decisions recorded through 2026-11-04;
exact API, capability mapping and construction directives still require review. This record reconciles the
canonical [refactor intent](command_refactor.md), [scored inventory](command-inventory.md)
and [command matrix](command-matrix.md) for the approved [build plan](build-plan.md).
It does not replace an exact construction directive.

## Controlling decisions

| ID | Decision | Consequence for this refactor |
| --- | --- | --- |
| S-01 | Build one UI-neutral implementation for maintained Friday Chat slash commands. | Chat delegates to it; the later TUI adapter consumes the accepted contract. Keep frontend rendering separate. |
| S-02 | Retire `/clear-tools`, `/inject-tools`, `/recommend-tools`, `/run-tool`, `/tool-budget`, `/inject-payload`, `/prime`, `/set` and `/vars` within this refactor. | The 50-command [source matrix](command-matrix.md) remains an as-built snapshot. The planned supported set is 41 canonical names and three aliases. All nine retired names are removed completely from registration, help and completion; no legacy notices, redirects or compatibility shims. They receive ordinary unknown-command handling and cannot execute former effects. `/tools` remains a supported read-only inventory command, including its category filter. |
| S-03 | Preserve current behavior, names, aliases and syntax for commands that remain. | Migrate `/security`, `/security-config`, `/security-test`, `/workflow`, `/speech-test`, `/tools` and `/migrate` without behavior changes. `/migrate` stays through the first TUI version. A scored recommendation alone does not authorize a removal or repair. |
| S-04 | Defer behavior enhancements and consolidations C-01 through C-06. | Track session restore, security/workflow capability reviews, `/read` attachment, ingested-source validation, confirmation prompts, diagnostics and tool presentation in the [follow-up backlog](../../backlog/friday-tui-command-followups/README.md). Disregard the transcript model-identification comment for this scope. |
| S-05 | Execute and accept the command refactor before resuming TUI development. | TUI command integration and physical terminal parity are later TUI gates. The separate `friday-framework-cli` contract and regressions belong in this refactor. |

## Maintainer decisions — 2026-11-04

Chuck Russell resolved the five questions individually in the planning discussion.
These are product/ownership decisions, not approval of exact API signatures,
a completed technical contract, or product-code construction.

| ID | Final decision | Remaining engineering obligation |
| --- | --- | --- |
| O-01 | Remove retired names completely without regard to legacy use. No migration messages, redirects or compatibility support. | Remove all nine from registration, help and completion; test ordinary unknown-command handling and absence of former effects. Update current guides during the authorized retirement unit. |
| O-02 | One UI-neutral `friday-commands` package owns definitions, parsing, validation, execution and structured results; Chat and TUI own input and presentation. | Design and review the public API, typed requests/results/effects, errors, progress/cancellation, capability ownership and one-way dependencies. Exact API approval remains pending. |
| O-03 | Preserve the separate `friday-framework-cli` public API and behavior. Reuse shared primitives only where compatibility is demonstrated; do not force the Chat command set into its registry. | Characterize its current registry, consumers and installed entry point. Record a source-backed reuse seam or reason to preserve it separately, with regression evidence. |
| O-04 | Remove `/prime`, `/set` and `/vars`; they are unused. `/tools` remains supported. | Nine retirements leave 41 canonical names and three aliases from the frozen 50/3 source baseline. Do not alter startup priming or runtime configuration merely because these slash names are removed. Identify orphaned command state/metrics in the exact retirement directive. |
| O-05 | Preserve retained-command behavior by default, including existing quirks. Record discovered bugs for a separate decision and bounded fix. The nine removals are explicit exceptions. | Characterize actual behavior before extraction. Resolve any discovered security or contract violation before the affected migration proceeds; do not silently fix or waive it. |

## Remaining technical-contract gate

Complete P0 source evidence and baseline receipts, design the exact shared API
and service/capability map, demonstrate the generic CLI preservation/reuse
boundary, and prepare the unit/scenario map and first exact construction
directive. Obtain the required independent architecture review and maintainer
approval. These decisions do not close P0/P1, grant product-code authority, or
resume deferred Friday TUI construction.

## Change control

The [scored inventory](command-inventory.md) preserves the maintainer's raw
scores and commentary. The [refactor intent](command_refactor.md) preserves
the branch's architectural direction and explicit maintainer clarifications.
The [matrix and JSON snapshot](command-matrix.md) preserve the 50-name source
baseline, including names selected for retirement; they are not a
post-refactor target or passing test result. This register owns the current
scope synthesis, not the underlying feature intent. Reconcile it with the
three source documents, the [build plan](build-plan.md),
[phase plan](phase-plan.md), tests, help and guides when these decisions or their technical details change. Each product-code unit still needs its own approved exact directive
under the project [authority record](authority.json) and development board.
