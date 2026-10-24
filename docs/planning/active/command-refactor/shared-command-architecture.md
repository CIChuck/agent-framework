# Shared Friday slash-command architecture

**Status:** Proposed technical contract informed by accepted TUI decision D-123
(`01cbaa0b:docs/planning/active/friday-tui/decisions.md`). Package/API signatures and construction units still
require review and their own directives. This document grants no code, release,
or publication authority.

This document belongs to the [active shared-command initiative](README.md).
Its proposed contract remains linked to the
[command coverage matrix](command-matrix.md), which supplies the current TUI
parity baseline.

## Why this boundary exists

The maintained `/` commands currently live in
`friday_chat.commands.registry` and its neighboring handler modules.
`friday_cli.commands` supplies a generic registry for the separate
`friday-framework-cli` package; it is not the Friday Chat command implementation.
Current Chat command handlers and `CommandContext` reference Chat-owned runtime,
session, and service objects, so copying or importing the registry into the TUI
would either duplicate behavior or make the TUI depend on a CLI package.

Friday Chat and Friday TUI must execute a maintained command through **one
shared, UI-neutral implementation**. For a given command and session state,
both frontends must use the same command name/alias and argument metadata,
parsing and validation, handler/policy, service effects, error meaning, and
typed result. Each frontend may render that result and perform declared UI
effects in its own interface. A TUI-only extension must not appear in either
CLI's default command set.

## Invocation, execution, and presentation boundary

```text
CLI text or TUI control
  -> shared command name/alias, parameters, parsing, and validation
  -> shared execution and Friday service effects
  -> shared semantic outcome, progress, and UI-effect intent
  -> frontend-owned rendering and interaction
```

The CLI may accept typed `/` text while the TUI may also offer completion or
a palette. Those are input affordances: once a maintained command is invoked,
both clients must resolve the same canonical command and parameters with the
same defaults, validation, policy, and execution. A TUI control must not call
a different implementation or quietly change a parameter's meaning.

The shared engine returns the **same semantic outcome** for equivalent
requests and state: command data, success or error meaning, any ordered
progress, and declared effects on Friday services or the UI. It does not
choose terminal colors, line wrapping, table layout, scrolling, focus, or
where messages appear. The CLI and TUI own those presentation choices and
apply UI-effect intents in their own environments. For example, `/cls`
requests a display clear; the CLI clears its terminal view and the TUI clears
its conversation view. Neither renderer executes the command again or
reinterprets a failed operation as success.

The current Chat `CommandResult` includes display-ready `output: str` and
`ui_effects`. That is a compatibility starting point, not a requirement for
the TUI to parse CLI-formatted text to recover command data. The technical
contract must define typed results or events where structured data and rich
TUI presentation need them, while preserving existing Chat text and behavior
for retained commands. Exact result types, progress transport, and adapter
APIs remain construction decisions; this boundary does not specify them by
implication.

Parity evidence must compare the normalized request, semantic outcome,
service and session effects, errors, and effect intents across both clients.
Presentation is verified separately: preserve Chat's established text and
terminal behavior, and test the TUI's own view and interaction requirements.
Identical screen text is not the definition of command parity.

## Proposed dependency direction and ownership

```text
friday-chat ──┐
              ├──> UI-neutral command engine ──> Friday runtime/services
friday-tui ──┘

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

The proposed home is a separately installable `friday-framework-commands`
package. Its final package name and public API are technical-contract decisions;
they must not be inferred as already implemented. The command engine owns the
maintained registry, metadata, parser, dispatch, handlers, validation, and
command-level policy. It depends on typed, UI-neutral runtime capabilities and
session/turn state, never on `friday_chat`, `friday_cli`, Textual, Rich, or a
frontend's private objects. The existing Chat command implementation is the
source for migration, not a runtime dependency of the TUI.

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
without changing the shared default or either CLI. New maintained commands
and changes to existing commands are made once in the shared engine.

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

1. Characterize the existing Chat behavior for each bounded command family:
   accepted and invalid syntax, aliases, unavailable services, progress,
   error/result text and meaning, session changes, files, and other effects.
   Keep the [50-command matrix](command-matrix.md) as the frozen migration and
   acceptance inventory until each case is reconciled with the shared registry.
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
4. Connect the TUI to that **same** shared engine. Test each PAR case through
   both frontends on equivalent disposable fixtures, including state/file
   effects and failures, then complete rolling terminal UAT. Test metadata
   driven help/completion and a TUI-only extension without CLI leakage.

The matrix detects missing coverage, version skew, unintended frontend
differences, and migration regressions. It is not a specification for a second
set of TUI handlers. Preview alphas may expose a tested subset, but any
maintained command they expose must use the shared implementation. Neither
this design nor its migration changes Friday Chat or `friday-framework-cli`
public behavior by intent; before/after checks must demonstrate that boundary.
