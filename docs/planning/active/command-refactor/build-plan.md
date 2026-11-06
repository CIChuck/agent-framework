# Shared Friday command refactor — build plan

**Working-folder update — 2026-11-05:** The maintainer changed direction:
current command-first and Friday TUI planning is consolidated in the
`agent-framework` folder. Earlier TUI-folder directions are superseded for
current work. This transfer changes documents only; imported implementation
claims, reviews and test receipts retain their original provenance. No design
approval, construction authority or code validation is inferred.


**Maintainer decision update — 2026-11-04:** Apply the resolved
[O-01–O-05 decisions](scope-decisions.md#maintainer-decisions--2026-11-04):
nine complete removals, `/tools` retained, a 41/3 target, shared
`friday-commands` ownership, preserved generic CLI behavior and retained-command
quirks. Earlier proposals below are superseded where they conflict. Exact API,
capability mapping, baseline evidence and construction approval remain pending.

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
| [Command matrix](command-matrix.md) | Use the 50 canonical names, three aliases and PAR IDs as the before-change case inventory. Reconcile the nine retirement cases separately from retained-command equivalence. |

## Objective and ownership

Extract the maintained Friday Chat slash-command definitions and execution
into one UI-neutral owner. Friday Chat continues to present command results in
its terminal interface; Friday TUI consumes the same semantic implementation
and renders it in its own interface. The proposed home is
`packages/friday-commands/`, distributed as `friday-framework-commands` and
imported as `friday_commands`. P1 reviews that
[proposed location and API](shared-command-architecture.md#proposed-relocation-and-package-surface)
before construction. Assess whether the separate `friday-framework-cli`
package can reuse a concrete primitive through a compatible adapter while
preserving its generic registry, entry point and established behavior.

This work has its own board lifecycle, branch, architecture decision, bounded
construction directives, candidate commits and independent reviews. The TUI
project owns its frontend adapter, command discovery, rendering, interaction
and physical terminal UAT after the shared command owner is accepted. Under
the current maintainer decision, TUI development is deferred until this
refactor is completed, tested and accepted.

The maintainer has requested a one-off MCP compatibility exception on this
branch. Its [approved exact directive](directives/CD-CMD-MCP-001-compatibility-exception.md)
covers the 2025 Draft-07 discovery fix and query-bearing endpoint URLs. It has
its own candidate and validation receipts, does not alter the command scope,
and was approved for implementation on 2026-10-25.

## Source baseline and decisions

- The current Chat registry contains 50 canonical slash commands and three
  aliases in the [TUI matrix](command-matrix.md).
  Capture a fresh source snapshot before code changes. Keep the matrix as the
  frozen before-change inventory; record the approved retained/retired target
  and compatibility exceptions separately. Reconcile the
  [refactor intent](command_refactor.md), TUI decisions, release criteria,
  help, guides and tests before claiming parity against the target.
- The maintainer's [scored inventory](command-inventory.md)
  selects `/clear-tools`, `/inject-tools`, `/recommend-tools`, `/run-tool`,
  `/tool-budget`, `/inject-payload`, `/prime`, `/set` and `/vars` for retirement.
  Remove them completely under O-01/O-04; no legacy compatibility. Keep
  `/tools`, `/security`, `/security-config`, `/security-test`, `/workflow`,
  `/speech-test` and `/migrate` with their current behavior for this version.
  The [scope decision register](scope-decisions.md) distinguishes these
  decisions from scored recommendations and lists contract choices still open.
- [Consolidation and behavior enhancements](../../backlog/friday-tui-command-followups/README.md)
  are later decisions. They are not bundled into behavior-preserving migration.
- The separate `friday_cli.commands` registry is not the Friday Chat slash
  registry. Friday Chat currently imports `friday_cli` display utilities, but
  dispatches slash commands through its own registry. Inventory the generic
  CLI's public entry point, registration/completion API and consumers before
  deciding its reuse role. The shared package must not import Friday Chat,
  Friday TUI or `friday_cli`; this does not require removing Chat's existing
  display dependency during extraction. Identify a concrete reusable primitive
  and compatible adapter, or document with source and test evidence why one
  would damage the generic CLI contract. Merely rerunning its tests does not
  close the requested CLI-benefit assessment.

The [phase plan](phase-plan.md) defines the derived sequence and exit gates;
the [tactical plan](tactical-plan.md) tracks current characterization tasks.

## Proposed work units

1. **Characterize and decide (P0–P1).** Freeze Chat and `friday-framework-cli`
   command/API baselines. Reconcile retained/retired names, aliases, syntax,
   help, effects and old-name behavior. Review the security and workflow
   commands' actual current paths without changing behavior.
2. **Approve the neutral contract (P1).** Define command metadata, argument
   normalization, capability/context boundaries, typed semantic result and
   UI-effect intents. Map Chat-owned service implementations to public
   Runtime/domain operations or narrow injected capabilities; keep domain
   behavior in its owning package rather than duplicating it in adapters.
   Set the package name, public API, dependency direction and CLI adapter role
   explicitly.
   Review inventory architecture opportunities A-01 through A-10: record which
   support this behavior-preserving refactor and which remain later work.
3. **Migrate bounded command families (P2–P3).** Establish the shared
   foundation and pilot semantics selected in the approved P1 unit map, then migrate retained
   families in dependency order. Each command has one active implementation;
   Chat delegates while its current presentation and public behavior are
   preserved. Retire the nine selected names as a separately tested scope unit
   at the position approved in P1, not as accidental extraction fallout.
4. **Prove the shared owner before TUI integration (P4–P5).** Complete the
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
evidence, the nine intentional retirements have ordinary unknown-command handling, no former effects
and updated documentation, Friday Chat and `friday-framework-cli` pass their
applicable regression and installed-client gates, dependency direction is
verified, and an independent reviewer returns `VERIFIED` on a frozen aggregate
candidate. TUI parity and physical terminal acceptance remain in the TUI
project. No implementation begins from this plan alone.
