# Shared command refactor — phase plan

**Status:** Planning sequence derived from the three canonical intent documents
through the approved [build-plan scope](build-plan.md) and current
[scope decisions](scope-decisions.md). Gates and construction units remain
conditional on an approved technical contract and exact directives.

The [tactical plan](tactical-plan.md) tracks the current work within these
phases. The [test strategy](test-strategy.md) supplies evidence requirements
at every migration gate; it is not a substitute for a unit-specific test list.

| Phase | Outcome | Exit evidence and decision gate |
| --- | --- | --- |
| P0 — Source characterization | Freeze Chat's 50 canonical names, three aliases, help, parsing, effects and existing test results; characterize the separate `friday-framework-cli` API, registry, completion and installed entry point. | Source-backed before-change inventory and baseline test receipts, including known failures and effectful probes on disposable stores. |
| P1 — Supported surface and contract | Reconcile the six selected retirements, scored outliers, old-name behavior, CLI role and UI-neutral owner/API. | Updated [decision register](scope-decisions.md), reviewed technical contract, matrix/compatibility exceptions and approved first exact construction directive. No source work before this gate. |
| P2 — Shared foundation | Establish approved registry, parsing, help, typed-result and adapter seams through a bounded unit. | Frozen candidate, protected Chat/CLI checks, installed import/dependency checks and independent read-only `VERIFIED` review under its directive. |
| P3 — Command-family migration | Move retained command families to one shared implementation, preserving their observed semantics and Chat presentation. | Each family has before/after positive, invalid, unavailable, error and effect evidence as applicable; no duplicate maintained handler remains at its gate. |
| P4 — Selected retirements | Apply the six approved command retirements as an explicit scope unit. | Negative former-effect checks, approved old-name behavior, unchanged other names/aliases, help/completion/guide reconciliation and compatibility evidence. Sequence relative to P3 must be pinned in the directive. |
| P5 — Aggregate verification and acceptance | Validate the whole shared command owner and both terminal clients as applicable. | Full owning suites, isolated installed-package gates, matrix reconciliation, independent aggregate `VERIFIED` review, then separate maintainer acceptance. |

**Handoff:** After P5 acceptance, the deferred Friday TUI project may resume
and integrate the accepted contract on its own branch. TUI command parity,
frontend rendering and physical terminal UAT remain TUI acceptance gates.
This handoff is not a command-refactor construction phase.
