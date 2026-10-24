# Shared command refactor — tactical plan

**Status:** active design and baseline characterization; no product code unit
is authorized without an approved exact construction directive.

**Branch and baseline:** `feature/command-refactor` based directly on
`c3426986` (`master`), independent of `feature/friday-tui`. The separate [development board](../../board.yaml)
controls current task state. The [build plan](build-plan.md),
[test strategy](test-strategy.md), [scored inventory](command-inventory.md),
[command matrix](command-matrix.md) and [architecture proposal](shared-command-architecture.md)
bound this planning phase.

## Ordered work and gates

1. **Baseline characterization.** Recheck the live Friday Chat registry,
   aliases, parser, help, handler dependencies and effects against the 50/3
   inventory. Inventory the separate `friday-framework-cli` registry, public
   API, completion and installed entry point. Capture baseline test commands,
   counts, skips and known failures. Use disposable stores for effectful probes.
2. **Decide the exact supported surface.** Reconcile the six selected
   retirements, retained-name behavior and old-name response with the scored
   inventory. Record any user-visible exception to the before-change matrix;
   do not fold deferred consolidation or behavior enhancements into extraction.
3. **Review the cross-client contract.** Decide the neutral package/API,
   command context and capability boundary, typed results and UI-effect
   intents. Determine how `friday-framework-cli` can reuse a concrete seam
   while preserving its different registry and behavior. Obtain independent
   architecture review and maintainer approval of the exact contract.
4. **Prepare bounded construction directives.** Start with registry metadata,
   name/alias resolution, argument parsing/help and a small effect family.
   Each directive pins allowed files, baseline, negative/effect cases,
   compatibility exceptions, installed checks and stop conditions. Do not
   generate product code until its directive is approved.
5. **Implement and verify by family.** After each authorized code unit,
   freeze a candidate, run the focused and protected Chat/CLI gates, and
   obtain a fresh-context read-only `VERIFIED` result. Run broad owning
   suites and installed isolation checks before an aggregate review.
6. **Handoff to TUI.** Propose completion only after the shared owner and
   both terminal-client gates are verified. Maintainer acceptance is separate.
   TUI development remains deferred until completion, testing, and maintainer
   acceptance. Its independent branch then integrates the accepted public
   contract and runs its own parity and terminal UAT.

The current gate is steps 1–3: characterization and contract review. No
handler migration, six-name retirement, help change or package source edit
is authorized by this tactical plan alone.
