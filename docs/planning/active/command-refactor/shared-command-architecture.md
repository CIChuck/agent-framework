# Shared Friday slash-command architecture

**Maintainer decision update — 2026-11-04:** Apply the resolved
[O-01–O-05 decisions](scope-decisions.md#maintainer-decisions--2026-11-04):
nine complete removals, `/tools` retained, a 41/3 target, shared
`friday-commands` ownership, preserved generic CLI behavior and retained-command
quirks. Earlier proposals below are superseded where they conflict. Exact API,
capability mapping, baseline evidence and construction approval remain pending.

**Status:** Proposed technical contract informed by accepted TUI decision D-123
(`01cbaa0b:docs/planning/active/friday-tui/decisions.md`). Shared `friday-commands` ownership is confirmed by O-02. The detailed
relocation map and proof obligations below remain inputs to P1 review;
the package/API signatures, service ownership and construction units remain
open. This document grants no code, release, or publication authority.

This document belongs to the [active shared-command initiative](README.md).
It refines the canonical [feature intent](command_refactor.md),
[scored command inventory](command-inventory.md) and
[command coverage matrix](command-matrix.md). The matrix supplies the current
TUI parity planning baseline; the [scope decision register](scope-decisions.md)
controls the nine selected retirements and unresolved contract choices. The
[phase plan](phase-plan.md) requires an approved package, service-ownership
and CLI-role decision before construction.

## Why this boundary exists

The maintained `/` commands currently live in
`friday_chat.commands.registry` and its neighboring handler modules.
`friday_cli.commands` supplies a generic registry for the separate
`friday-framework-cli` package; it is not the Friday Chat command implementation.
Friday Chat currently depends on that package for display utilities through
`friday_chat.display`, not for its slash-command dispatch. Its own
`friday_chat.commands.registry` and `friday_chat.commands.contracts` own the
maintained Chat surface today. The generic CLI registry has a different
registration API and `str | None` result contract; merging the registries
would be a separate public-API decision.
Current Chat command handlers and `CommandContext` reference Chat-owned runtime,
session, and service objects, so copying or importing the registry into the TUI
would either duplicate behavior or make the TUI depend on `friday-chat`.

Friday Chat and Friday TUI must execute a maintained command through **one
shared, UI-neutral implementation**. For a given command and session state,
both frontends must use the same command name/alias and argument metadata,
parsing and validation, handler/policy, service effects, error meaning, and
typed result. Each frontend may render that result and perform declared UI
effects in its own interface. A TUI-only extension must not appear in the
default registry of Friday Chat or `friday-framework-cli`.

## Invocation, execution, and presentation boundary

```text
Friday Chat text or TUI control
  -> shared command name/alias, parameters, parsing, and validation
  -> shared execution and Friday service effects
  -> shared semantic outcome, progress, and UI-effect intent
  -> frontend-owned rendering and interaction
```

Friday Chat may accept typed `/` text while the TUI may also offer completion or
a palette. Those are input affordances: once a maintained command is invoked,
both clients must resolve the same canonical command and parameters with the
same defaults, validation, policy, and execution. A TUI control must not call
a different implementation or quietly change a parameter's meaning.

The shared engine returns the **same semantic outcome** for equivalent
requests and state: command data, success or error meaning, any ordered
progress, and declared effects on Friday services or the UI. It does not
choose terminal colors, line wrapping, table layout, scrolling, focus, or
where messages appear. Friday Chat and the TUI own those presentation choices
and apply UI-effect intents in their own environments. For example, `/cls`
requests a display clear; Friday Chat clears its terminal view and the TUI
clears its conversation view. Neither renderer executes the command again or
reinterprets a failed operation as success.

The current Chat `CommandResult` includes display-ready `output: str` and
`ui_effects`. That is a compatibility starting point, not a requirement for
the TUI to parse Friday Chat's formatted text to recover command data. The
technical contract must define typed results or events where structured data
and rich TUI presentation need them, while preserving existing Chat text and behavior
for retained commands. The shared result must contain enough semantic data for
both adapters; Chat may format that data into its established text, while TUI
renders it without parsing that text. Exact result variants, compatibility
formatting, progress transport, cancellation and adapter APIs remain P1
decisions; this boundary does not specify them by implication.

Parity evidence must compare the normalized request, semantic outcome,
service and session effects, errors, and effect intents across both clients.
Presentation is verified separately: preserve Chat's established text and
terminal behavior, and test the TUI's own view and interaction requirements.
Identical screen text is not the definition of command parity.

## Proposed dependency direction and ownership

```text
friday-chat adapter ──┐
                      ├──> friday_commands ──> public Runtime/domain capabilities
friday-tui adapter ───┘

friday-framework-cli: separate registry; shared-primitives/adapter role pending
```

The arrows show command execution ownership, not every existing package
dependency. Friday Chat's current presentation dependencies remain protected.
The separate `friday-framework-cli` may benefit from neutral registry,
invocation or result primitives through an explicit adapter if its source and
public API support that boundary. The
[separate refactor](build-plan.md)
must inventory that package and approve its role before code changes; it must
preserve the package's established command names, registration/completion,
entry point and behavior. The maintained 50-command Chat registry is not
silently assigned to this different CLI.

The proposed home is `packages/friday-commands/`, distributed as the separately
installable `friday-framework-commands` package and imported as
`friday_commands`. Its public API and distribution details remain P1 technical-contract
decisions; the package does not exist on this branch yet. The command engine
owns the maintained registry, metadata, parser, dispatch, handlers, validation,
command-level policy and typed semantic outcomes. It depends on typed,
UI-neutral runtime capabilities and session/turn state, never on `friday_chat`,
`friday_cli`, `friday_tui`, Textual, Rich or a frontend's private objects. The
existing Chat command implementation is the migration source, not a runtime
dependency of the TUI.

## Proposed relocation and package surface

| Proposed owner | Move or retain | Boundary |
| --- | --- | --- |
| `packages/friday-commands/src/friday_commands/` | Move maintained command metadata, name/alias resolution, parsing, validation, dispatch, command policy and handler semantics from `friday_chat.commands`. Define typed requests, outcomes, errors, progress and UI-effect intents plus small capability contracts. | One implementation for each retained command; no frontend formatting or concrete Chat session/runtime types. The nine selected retirements use complete removal under O-01/O-04. |
| `packages/friday-chat/src/friday_chat/` | Keep the executable, input loop, Chat presentation, output/progress delivery, and capability wiring. Preserve necessary public `friday_chat.commands` imports as delegating compatibility entry points. | Existing Chat text and interaction remain protected; compatibility shims do not own a second registry definition or handler. Its current `friday-framework-cli` display dependency is separate from command ownership. |
| `packages/friday-tui/src/friday_tui/` (later project) | Build the TUI editor, discovery, adapter, renderer, view state and lifecycle after shared-owner acceptance. | Consume the shared registry and semantic results. TUI-only commands compose through an isolated extension point; no imports from `friday_chat` or `friday_cli`. No TUI source is constructed by this refactor. |
| Runtime and domain packages | Keep or expose public memory, transcript, tool, agent, security, speech and maintenance operations. | Own domain behavior and durable state. Frontend adapters may supply capabilities, but must not each reimplement command policy or stateful service logic. |
| `packages/friday-cli/src/friday_cli/` | Keep the separate generic registry, decorator API, entry point and established behavior. | P1 decides whether an adapter can reuse neutral metadata, invocation or result primitives without changing that public contract; the Chat slash surface is not assigned to this registry. |

The current `CommandContext` and its `RegistryCommandContext` extension carry
`FridayRuntime`, `FridaySession`, command-local state and Chat-owned maintenance
objects; the current registry also imports Chat reorganization, replay,
security, speech and tool helpers.
These imports cannot move wholesale into `friday_commands`. P0 must map each
handler to its actual service and effect path. P1 then assigns every required
service to a public Runtime/domain operation or a narrow injected capability.
If a service implementation currently lives only in Chat, move its reusable
operation to an appropriate neutral owner or expose it through an approved
public service boundary before the TUI consumes it. The adapters wire these
capabilities; they do not duplicate the underlying operation. Keep the shared
context small and typed by capability family rather than transplanting the
broad Chat `CommandContext`.

The workspace already discovers `packages/*`. The approved construction unit
must add the new package manifest, explicit client dependencies and lockfile
changes. Chat and, later, TUI must install a compatible tested command-package
version. Do not infer reuse from workspace imports alone: build and install
the wheels outside the checkout and inspect the resolved dependency graph.

Friday Chat keeps its executable, input loop, terminal presentation, existing
public behavior, and any necessary compatibility entry points; those entry
points delegate to the shared engine rather than retain a second command
implementation. Friday TUI keeps its editor, command suggestions/palette,
view state, rendering, and lifecycle. Its frontend adapter provides the shared
engine's typed capabilities and handles declared UI effects; it does not
reimplement command parsing or command policy. For example, the shared
`/cls` result requests a display clear; each frontend clears its own view.
The shared `/exit` result requests exit; the TUI still follows its accepted
safe-quit admission and cleanup rules. Shared session state must distinguish
the command's intended effects from frontend-only state such as editor recall.

Both frontends derive maintained-command help, aliases, usage, and discovery
from the same registry metadata. An explicit extension point may compose
TUI-only commands into the TUI's effective registry with collision checks and
without changing the shared default, Friday Chat or the generic CLI. New
maintained commands and changes to existing commands are made once in the
shared engine.

## Framework evolution rule

The Friday harness must remain free to add or improve runtime, memory,
transcript, tool, and agent capabilities without embedding those capabilities
in a frontend or turning the command package into a second harness. The owning
domain package or Runtime exposes a coherent public operation and typed data;
the shared command engine translates a `/` request into that operation and a
semantic result. Friday Chat and TUI render the result. A framework capability
does not automatically become a slash command; a new maintained command is an
intentional addition to the shared registry.

Keep dependencies one-way: domain packages and Runtime must not import the
command engine, and the command engine must not reach into their private
implementation or either frontend. Prefer direct public service calls where
they fit over a large collection of pass-through adapters. If a proposed
command adapter has to mirror most of the Chat runtime, stop and define a
smaller neutral domain operation instead. Cross-domain work belongs to a
neutral coordinator with clear ownership, not arbitrarily to one domain.

Ordinary changes behind a stable public service contract should leave command
syntax and both frontends untouched. Adding a maintained command should
require one shared definition/implementation plus tests; frontend work is
needed only for a genuinely new presentation or interaction. Tests must prove
existing command compatibility and both clients' handling of any new semantic
result. This is an evolvability criterion, not a promise that all future
features can be added with zero client changes.

## Migration and proof

The [phase plan](phase-plan.md) places source characterization in P0, package,
service and CLI-role decisions in P1, foundation and family/retirement units
in P2–P3, installed cross-family integration in P4 and aggregate acceptance
in P5. TUI integration begins only after P5 acceptance.

1. Characterize the existing Chat behavior for each bounded command family:
   accepted and invalid syntax, aliases, unavailable services, progress,
   error/result text and meaning, session changes, files, and other effects.
   Keep the [50-command matrix](command-matrix.md) as the frozen source inventory
   until each retained or retirement case is reconciled with the shared registry.
2. Identify Chat-owned context and service dependencies. Move only the needed
   typed contracts and implementation into the neutral owner, replacing
   frontend-specific references without changing observable Chat behavior.
   Already verified neutral runtime effects remain reusable; they do not by
   themselves constitute a shared command handler. For each command, retire
   the old active handler as Chat delegates to the migrated one; do not keep
   two live implementations that must be updated together.
3. Switch Chat to the shared command implementation behind its existing
   application boundary. Prove unchanged installed Chat behavior and the
   separate `friday-framework-cli` baseline. If the approved contract gives
   that CLI a shared-primitives adapter, prove its unchanged public behavior
   and installed operation before TUI command integration.
4. After command-refactor acceptance, connect the TUI to that **same** shared
   engine. Test each retained PAR case through both frontends on equivalent
   disposable fixtures, including state/file effects and failures; verify the
   nine retirement cases against their approved old-name and discovery policy.
   Complete rolling terminal UAT, metadata-driven help/completion checks and a
   TUI-only extension check without leakage into Friday Chat or the generic CLI.

## Reuse proof and acceptance boundary

- **Import and packaging checks:** Reject imports by `friday_commands` of
  `friday_chat`, `friday_cli`, `friday_tui`, renderer code or private
  Runtime/domain modules; reject imports of `friday_commands` by Runtime/domain
  packages.
  Build the shared package and clients as wheels, install them outside the
  workspace, and verify dependency closure and entry points. Chat's existing
  use of `friday_cli` display utilities does not make the shared package depend
  on `friday_cli`.
- **Single-owner checks:** For every retained PAR case, the effective Chat
  registry must resolve to the one shared metadata/handler owner. Any legacy
  `friday_chat.commands` API delegates to it. A later TUI adapter must use the
  same owner and must not maintain a parallel handler or parser. Check aliases,
  help, completion metadata and TUI-only extension isolation from that registry.
- **Behavior checks:** Before/after Chat fixtures compare normalized request,
  result meaning, errors, ordered progress, session/runtime and file/tool
  effects, plus Chat's protected text and UI effects. The nine retired names
  follow their approved retirement contract instead of retained-command
  equivalence. When TUI integration begins, run the retained PAR cases through
  both installed clients on equivalent disposable fixtures; verify TUI
  rendering separately. Identical screen text is not the parity criterion.
- **Release identity:** Record the exact shared-package version and wheel used
  by Chat and the later TUI release. Test that installed clients resolve a
  compatible version rather than relying on editable-workspace behavior.
  Keep the separate `friday-framework-cli` registry/API regression gate until
  its P1 reuse role is decided and tested.

The command-refactor branch can verify the package boundary, single owner,
Chat compatibility and protected `friday-framework-cli` behavior. It cannot
claim Chat/TUI parity before the deferred TUI project installs the accepted
package and completes its own command, presentation and physical terminal UAT.

The matrix detects missing coverage, version skew, unintended frontend
differences, and migration regressions. It is not a specification for a second
set of TUI handlers. Preview alphas may expose a tested subset, but any
maintained command they expose must use the shared implementation. Neither
this design nor its retained-command migration changes Friday Chat or
`friday-framework-cli` public behavior by intent. The nine selected Chat
retirements are explicit exceptions; before/after checks must demonstrate
both boundaries.
