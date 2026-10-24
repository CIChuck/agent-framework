# Shared Friday command refactor — draft build plan

**Status:** maintainer-approved initiative scope; technical contract and
construction directives remain open

## Objective and ownership

Extract the maintained Friday Chat slash-command definitions and execution
into one UI-neutral owner. Friday Chat continues to present command results in
its terminal interface; Friday TUI consumes the same semantic implementation
and renders it in its own interface. Establish the separate
`friday-framework-cli` package's direct-consumer or protected-adapter role in
the approved technical contract so that it can benefit where its current API
supports sharing without changing its established behavior accidentally.

This work has its own board lifecycle, branch, architecture decision, bounded
construction directives, candidate commits and independent reviews. The TUI
project owns its frontend adapter, command discovery, rendering, interaction
and physical terminal UAT after the shared command owner is accepted. TUI
shell, conversation, Activity and file-context work may proceed independently
under their own gates; the TUI command-integration phase and full command
parity wait for this initiative's accepted result.

## Source baseline and decisions

- The current Chat registry contains 50 canonical slash commands and three
  aliases in the [TUI matrix](command-matrix.md).
  Capture a fresh source snapshot before code changes. The matrix remains the
  before-change inventory and TUI parity baseline until a supported-surface
  decision updates it, the [refactor discussion](command_refactor.md),
  TUI decisions, release criteria, help, guides and tests together.
- The maintainer's [scored inventory](command-inventory.md)
  selects `/clear-tools`, `/inject-tools`, `/recommend-tools`, `/run-tool`,
  `/tool-budget` and `/inject-payload` for retirement in this refactor.
  Determine the retired-name response and release boundary explicitly. Keep
  `/tools`, `/security`, `/security-config`, `/security-test`, `/workflow`,
  `/speech-test` and `/migrate` with their current behavior for this version.
- [Consolidation and behavior enhancements](../../backlog/friday-tui-command-followups/README.md)
  are later decisions. They are not bundled into behavior-preserving migration.
- The separate `friday-cli.commands` registry is not the Friday Chat slash
  registry. Inventory its public entry point, command registration/completion
  and consumers before deciding whether it can use a shared contract directly.
  A shared package must not depend on Friday Chat, Friday TUI or `friday-cli`.
  The CLI workstream must identify a concrete reusable seam or document with
  source and test evidence why a direct adapter would damage its contract;
  merely rerunning its tests does not close the requested CLI benefit.

## Proposed work units

1. **Characterize and decide.** Freeze Chat and `friday-framework-cli`
   command/API baselines. Reconcile retained/retired names, aliases, syntax,
   help, effects and old-name behavior. Review the security and workflow
   commands' actual current paths without changing behavior.
2. **Approve the neutral contract.** Define command metadata, argument
   normalization, capability/context boundaries, typed semantic result and
   UI-effect intents. Keep domain operations in their owning Friday packages.
   Set the package name, public API and CLI adapter participation explicitly.
3. **Migrate bounded command families.** Move registry mechanics and small
   display commands first, then service-owning families. Each command has one
   active implementation; Chat delegates while its current presentation and
   public behavior are preserved. Retire the six selected names as a separately
   tested scope unit, not as accidental extraction fallout.
4. **Prove the shared owner before TUI integration.** Complete the
   [test strategy](test-strategy.md), including installed package/client
   isolation, exact changed-name checks, cross-family regressions and a fresh
   independent aggregate review. Record known deviations and obtain explicit
   maintainer acceptance before the TUI command phase consumes the result.

## Boundaries and exit criteria

The shared owner resolves maintained names, aliases, parameters, defaults,
validation and command-level policy, invokes Friday services, and returns
typed outcomes and effect intents. Frontends own layout, colors, focus,
scrolling and confirmation interactions. Equivalent normalized requests and
state must produce equivalent meaning, errors and service effects; identical
screen text is not the cross-frontend contract. Friday Chat's retained output
and public behavior remain compatibility obligations in its own interface.

The refactor exits only when every retained command family has before/after
evidence, the six intentional retirements have approved replacement/old-name
behavior and documentation, Friday Chat and `friday-framework-cli` pass their
applicable regression and installed-client gates, dependency direction is
verified, and an independent reviewer returns `VERIFIED` on a frozen aggregate
candidate. TUI parity and physical terminal acceptance remain in the TUI
project. No implementation begins from this draft alone.
