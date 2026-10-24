# Shared Friday command refactor — build plan

**Status:** maintainer-approved initiative scope derived from the three
canonical intent documents below; technical contract and construction
directives remain open

## Intent lineage

This build plan translates three linked source documents into an execution
sequence. If a later plan appears to disagree with them, reconcile the
disagreement in the [scope decision register](scope-decisions.md) before
changing a phase gate or writing a construction directive.

| Canonical source | Build commitment |
| --- | --- |
| [Refactor intent](command_refactor.md) | One shared, UI-neutral command owner; preserved behavior for retained commands; explicit retirement unit; Chat and separate CLI regression; TUI integration only after acceptance. Friday services own domain capability as the harness evolves. |
| [Scored command inventory](command-inventory.md) | Honor maintainer command decisions and focus areas. Carry architecture opportunities into contract review; defer consolidation and behavior enhancements unless separately decided. |
| [Command matrix](command-matrix.md) | Use the 50 canonical names, three aliases and PAR IDs as the before-change case inventory. Reconcile the six retirement cases separately from retained-command equivalence. |

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
and physical terminal UAT after the shared command owner is accepted. Under
the current maintainer decision, TUI development is deferred until this
refactor is completed, tested and accepted.

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
  The [scope decision register](scope-decisions.md) distinguishes these
  decisions from scored recommendations and lists contract choices still open.
- [Consolidation and behavior enhancements](../../backlog/friday-tui-command-followups/README.md)
  are later decisions. They are not bundled into behavior-preserving migration.
- The separate `friday-cli.commands` registry is not the Friday Chat slash
  registry. Inventory its public entry point, command registration/completion
  and consumers before deciding whether it can use a shared contract directly.
  A shared package must not depend on Friday Chat, Friday TUI or `friday-cli`.
  The CLI workstream must identify a concrete reusable seam or document with
  source and test evidence why a direct adapter would damage its contract;
  merely rerunning its tests does not close the requested CLI benefit.

The [phase plan](phase-plan.md) defines the derived sequence and exit gates;
the [tactical plan](tactical-plan.md) tracks current characterization tasks.

## Proposed work units

1. **Characterize and decide.** Freeze Chat and `friday-framework-cli`
   command/API baselines. Reconcile retained/retired names, aliases, syntax,
   help, effects and old-name behavior. Review the security and workflow
   commands' actual current paths without changing behavior.
2. **Approve the neutral contract.** Define command metadata, argument
   normalization, capability/context boundaries, typed semantic result and
   UI-effect intents. Keep domain operations in their owning Friday packages.
   Set the package name, public API and CLI adapter participation explicitly.
   Review inventory architecture opportunities A-01 through A-10: record which
   support this behavior-preserving refactor and which remain later work.
3. **Migrate bounded command families.** Move registry mechanics and small
   display commands first, then service-owning families. Each command has one
   active implementation; Chat delegates while its current presentation and
   public behavior are preserved. Retire the six selected names as a separately
   tested scope unit, not as accidental extraction fallout.
4. **Prove the shared owner before TUI integration.** Complete the
   [test strategy](test-strategy.md), including installed package/client
   isolation, exact changed-name checks, cross-family state/effect scenarios
   and a fresh independent aggregate review. Record known deviations and
   obtain explicit maintainer acceptance before the TUI command phase consumes
   the result.

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
project. No implementation begins from this plan alone.
