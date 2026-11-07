# PILOT-001 — help, exit and clear-screen contract

Status: **proposed; design approval not granted**. Prepared 2026-11-07 at
`7b80ca01489a52608aafb54b626b74fbb36efbe3`, branch `feature/command-retirement`.
This supplements the approved [foundation API](shared-command-api.md); it does
not change API-01–API-06. Read this first, then the
[construction directive](directives/CD-CMD-PILOT-001-help-exit-clear.md).
The maintainer must approve both exact documents before implementation.

## Purpose and boundary

Prove one real Chat consumer of the neutral package by extracting only `help`,
`exit` and `cls`. Exit retains aliases `quit` and `q`; cls retains `clearscreen`.
There remain exactly 41 default canonical commands and three aliases. All nine
RET-001 removals remain removed. `/clear` is conversation-history clearing and
is outside this pilot; `/cls` requests terminal clearing.

The neutral package owns the three definitions and their typed behavior. Chat
owns its public compatibility registry, its existing text parser, English
rendering, application shutdown and terminal effects. The other 38 definitions
and handlers remain Chat-owned. This is a staged extraction, not a second
complete default registry or a migration of other command families.

## Proposed additive public API

Add these four exports to `friday_commands`; preserve every existing export,
constructor, exception rule, empty-registry default and dispatch behavior.
The implementation module is `friday_commands.pilot`.

```python
PILOT_SPECS: tuple[CommandSpec, ...]  # ordered help, exit, cls

class HelpCatalog(Protocol):
    def specs(self) -> tuple[CommandSpec, ...]: ...
    def lookup_key(self, key: str) -> CommandSpec | None: ...

def describe_help(
    catalog: HelpCatalog, focused_name: str | None = None
) -> CommandOutcome: ...

def build_pilot_handlers(catalog: HelpCatalog) -> Mapping[str, CommandHandler]: ...
```

Use the existing `CommandSpec`, `CommandHandler`, `CommandRequest`,
`CommandExecution`, `CommandOutcome`, `HelpData`, `ExitData`, `NoData`,
`CommandError` and `UiEffect` types. Add no outcome variant or runtime capability
to the foundation models. `HelpCatalog` is a structural, synchronous read port;
the factory returns a read-only mapping with exactly `help`, `exit`, `cls`.
Factory construction neither reads the catalog nor registers commands globally.
Each returned handler implements the existing async handler protocol. It accepts
the canonical request for its own command; a different request name raises
`ValueError` before reading the catalog. Arguments retain the rules below.
`CommandExecution` is accepted but unused; these commands require no session ID.
The new shared handlers require exact `CommandRequest` and `CommandExecution`
instances, raising `TypeError` before inspecting request fields; wrong canonical
names then raise `ValueError`. `describe_help` accepts only `None` or a string
focus, including subclasses; other values (even falsy values) raise `TypeError`
before reading the catalog. This defines new shared boundaries without changing
legacy Chat registration or its existing falsy-focus handling. Truthy non-string
focuses are outside the declared legacy `str | None` API; their old exception
type (for example `AttributeError` for `5`) is not a compatibility guarantee.

`PILOT_SPECS` contains exact baseline metadata, including ordered aliases,
argument fields, punctuation and the `cls` detail paragraph. Move these values
from Chat; do not independently retype or revise them. Its order is not a new
display-order rule. A consumer opts in by registering these specs and handlers
in its own registry; importing the package still creates no default registry.
For a standalone neutral consumer, implement `HelpCatalog.specs()` from the
neutral registry's `specs()` snapshot and `lookup_key` with an exact map built
from each snapshot's canonical names and aliases. Do not use `resolve()` for
already normalized keys; it normalizes again. Refresh the map from the current
snapshot for each lookup if registration remains mutable.

## PC-01 — catalog and help selection

`specs()` returns a snapshot of canonical entries, with no separate alias rows.
It may represent all 41 Chat commands or a smaller custom consumer catalog.
No shared singleton or built-in catalog is consulted during help selection.
For general help, `describe_help` calls `specs()` once, sorts entries by canonical
name and returns `CommandOutcome(data=HelpData(commands=..., focused_name=None))`.
It does not call `lookup_key`.

For a truthy focus, apply `N(s) = s.removeprefix('/').strip().lower()` exactly
once and call `lookup_key(N(s))` once. The provider resolves an exact canonical
or alias key without trimming, lowercasing or removing another slash. A known
focus returns one spec with `focused_name=spec.name`; an unknown focus returns
`CommandError(code='unknown_command', command_name=N(s), usage=None)`.
Neither focused path calls `specs()` or projects unrelated argument metadata.
`None` and `''` mean general help; whitespace is truthy before normalization
and therefore performs an exact empty-key lookup. Empty catalogs are valid.
No help outcome requests a UI effect.

The async `help` handler calls `describe_help` once with the first argument,
or `None` for no arguments. Extra arguments are ignored. It returns that typed
outcome unchanged. Port exceptions and cancellation propagate without retries,
fallback catalogs, fabricated output or silent omission of an entry.

## PC-02 — exit and terminal-clear behavior

`exit` ignores arguments and returns `CommandOutcome(data=ExitData(True))`.
`cls` ignores arguments and returns
`CommandOutcome(data=NoData(), ui_effects=(UiEffect.CLEAR_SCREEN,))`.
Neither handler reads the catalog, runtime, stores, history, session, terminal
or network. Neither exits the process, mutates context, prints text or applies
an effect. Their lifecycle requests belong to the host.
Chat's exit and cls wrappers pass a private immutable empty catalog adapter
(`specs()` returns `()`, `lookup_key(...)` returns `None`) to the factory; no
default registry or context access is needed. This is not a fifth shared export.

## PC-03 — Chat dispatch and public compatibility

Preserve `CommandRegistry.register`, `execute`, `render_help`, `commands`,
`canonical_names`, `command_names`, all legacy dataclasses/re-exports, the
39-entry `DEFAULT_COMMAND_SPECS` tuple and `BASIC_COMMAND_HANDLERS` interface.
Replace only the three metadata owners with projections from `PILOT_SPECS`, at
the existing builder/tuple positions and using the existing public Chat types.
All seven metadata fields and nested argument fields of every retained command
must match the baseline exactly. No other definition moves in this unit.

Keep `_help_handler`, `_exit_handler` and `session.cls_handler` as compatibility
wrappers. They delegate to shared behavior; they contain no second help
selection, exit policy or clear-screen policy implementation. Chat parses and
resolves the input once as today. A wrapper builds a typed canonical request
from those already parsed arguments and calls/awaits the selected shared handler
once. Use the corresponding `PILOT_SPECS` entry for that request, not unrelated
legacy metadata passed to the wrapper; the old wrappers ignore that metadata.
It must not reconstruct text, call `execute_text`, re-normalize the command
name, redispatch through Chat or route all 41 commands through a second registry.

Help keeps the existing context selection: a `RegistryCommandContext` uses
`context.registry`, even when different from the dispatching registry; a plain
`CommandContext` uses a newly built default catalog. Direct synchronous
`registry.render_help(...)` uses that registry and calls `describe_help` plus
the Chat renderer synchronously. It must not run an event loop or invoke a
coroutine. The catalog adapter must not call `render_help` or create a recursion.
Before calling the strict shared helper, Chat maps a legacy falsy focus to
`None`, preserving existing general-help behavior for direct legacy callers.

Custom registries stay empty until explicit registration. Explicit custom
handlers, including handlers named `help`, `exit`, `cls` or a retired spelling,
remain authoritative. There is no hard-coded dispatch interception or blacklist.
Legacy duplicate/registration behavior and malformed-input handling do not
acquire stricter neutral-registry validation as a side effect.

## PC-04 — metadata projection and rendering

The Chat catalog adapter performs exact key lookup using Chat's existing
canonical/alias maps. It projects only the selected spec for focused help, or
the full catalog for general help. It snapshots collections into neutral models
without registering them in a neutral registry: a legacy empty alias or
slash-retaining canonical name must not undergo a second normalization or
registration validation. Keep argument names/descriptions verbatim.

Do not replace public Chat argument constructors with stricter neutral types.
Characterize and preserve the currently permissive rendering cases: truthy or
falsy `required`, a non-None numeric default formatted as by the existing
f-string, and choices supplied as ordered lists, strings or mappings of string
keys. Project their displayed meaning (`bool(required)`, formatted default and
ordered choice strings), without changing registration acceptance. An invalid
choice member that previously raised must still raise; do not stringify it.
Do not eagerly validate an unrelated bad entry during focused/unknown help.
If another legacy value cannot cross the typed boundary without an observable
change, stop for a contract decision; do not add `Any`, a fallback legacy help
engine or silent data repair to force the migration through.

Chat alone formats general and focused help using the existing grouping,
category/name sorting, alias order, arguments, defaults, choices, detail text,
blank lines and trailing-newline behavior. There is no new formatting standard.
Exact output is compared with independently captured before-change results.

Map shared outcomes to the existing Chat `CommandResult`:

| Shared result | Chat result and owner |
| --- | --- |
| General `HelpData` (`focused_name=None`, no effects) | Existing generated help text; no exit/effect. Empty command tuples are valid. |
| Focused `HelpData` (exactly one spec, `focused_name=spec.name`, no effects) | Existing focused text; no exit/effect. Other focus/command cardinalities are invalid. |
| Unknown-help error (`unknown_command`, `usage=None`, no effects) | `Unknown command: /{normalized}. Type /help for available commands.` |
| `ExitData(True)` with no effects | `output='Goodbye.'`, `exit_requested=True`, no effect. Existing `execute` sets the context flag. |
| `NoData` plus one clear effect | `output=''`, one Chat `CLEAR_SCREEN`, no exit. |

These successful results retain `handled=True`. Adapter helpers accept only
the listed shapes and explicitly reject unsupported data/error/effect shapes
with `ValueError`; no `assert`-only invariant or silent generic message. They
must not read context/runtime for exit or clear, including session identity.

## PC-05 — application lifecycle and preserved boundaries

Leave `FridayChatApp` production source unchanged. It applies a clear effect once at
the display boundary, before nonempty command output. Preserve the missing
display message `Unable to clear the terminal: display is unavailable.` and
the caught-failure message `Unable to clear the terminal.`. An empty successful
clear result writes no substitute text. Exceptions do not leak terminal details.

Exit output, context exit flag, `command_exit` reason, run-loop break and existing
finally cleanup keep their current order and counts. Shared handlers never
construct or own that lifecycle. Cancellation and unexpected exceptions propagate
once; no double invocation, exception swallowing, extra terminal clear or retry.

Generic `friday_cli.commands` remains a separate API with its quote/decorator/
kwargs/sync/async/string-result semantics. Reuse the existing Chat result and
display boundary; do not adapt or merge the generic CLI registry. TUI and all
other family/capability contracts remain deferred.

## PC-06 — packaging and acceptance evidence

Add a required exact-version Chat dependency on
`friday-framework-commands==0.1.0a4` and its workspace source declaration. Update
only the resulting Chat lock edges/requires-dist; preserve all existing resolved
versions. The neutral package remains standard-library-only with no executable.
The existing 18-project cohort, root extras and artifact inventory do not grow.

Required proof covers: neutral standalone handler dispatch and immutable help
snapshots; exact 41/3 metadata; before/after help outputs and parser quirks;
custom registries; typed projection and error boundaries; app lifecycle/effects;
all nine retirement negatives; full Chat/foundation/CLI regression suites;
clean Git-export builds and default installed Chat dependency closure outside
the checkout. Tests must prove shared delegation, not merely matching output
from an accidentally retained Chat implementation. No live provider or real
user-store access is necessary. The directive specifies cases and verification.

## PC-07 — runnable harness and incremental gates

The preparation assets in `validation/pilot/harness/` are diagnostic tooling,
not the pilot implementation. They prepare a fresh scratch runner using eight
exact hash-pinned public build wheels, including Hatchling's `editables` hook
dependency and pinned setuptools/wheel for the source-only PyPika build.
After bootstrap, the runner uses only that wheelhouse with indexes
disabled and offline execution. An existing verified wheelhouse can bootstrap
another empty scratch directory without network access. Unprepared empty caches
must not be assumed to contain build dependencies.

Before any product edit, `capture.py` verifies Python source bytes against the
specified Git revision (all files under package `src/`, including data) and captures metadata, help, parsed dispatch outcomes,
custom registry cases and fake-app lifecycle traces. The frozen
`validation/pilot/baseline.json` is the expected result; do not regenerate it
from new behavior. Capture-program and baseline hashes are frozen for the unit.
`compare.py` requires the expected baseline hash and compares all observation
groups exactly, including list order and boolean versus integer types. Source
provenance may differ; the capture-program identity must remain identical.
Its self-test must reject deliberately damaged observations;
the injected guard must pass its own refusal and allowed-loopback controls.
The pilot guard retains the historical Python-open checks and adds
`sqlite3.connect` path checks, including SQLite file URIs, for the actual user's
and repository's `.friday` trees. Test real SQLite refusal only against a fake
repository inside scratch; use audit-only probes for real protected roots.
This is Python audit containment, not an OS sandbox for arbitrary native I/O.
On Darwin, protected paths use case folding. Connections also receive a SQLite
authorizer: protected ATTACH/VACUUM INTO destinations and unresolved
parameterized attachment destinations are denied. Fixtures must not remove
that authorizer to bypass a refusal.
All fixtures must still explicitly use scratch. Capture rejects any loaded
`friday*` module whose file or namespace origin escapes the verified export.
The runner checks positional and `--option=value` argument paths against every
existing top-level scratch JSON/log file and current receipt names, preserving
earlier receipts by assigning a new suffix to repeated run names. Invoke the
read-only comparator directly as documented when reading scratch JSON inputs.

The materialized `bundle.py` provides the lock-derived artifact recipe and a
baseline end-to-end trial at exact Python 3.13.10. It fetches target artifacts
only by lock URL/hash, builds workspace wheels from Git, records PyPika's locked
sdist-to-wheel lineage, compiles hash-pinned profiles and checks isolated installs.
It can replay entirely offline from retained raw artifacts. G5 must repeat
against the implementation and additionally prove installed pilot behavior.

Build with successive gates: harness/baseline readiness; shared-handler tests;
Chat adapter/compatibility tests; app lifecycle/effect tests; full regression
suites; then clean installed-package proof. Run the focused tests repeatedly
within each implementation stage, and advance only when its cases pass. Product
tests for new APIs are added under the approved directive; they are not claimed
to exist or pass during this preparation. There is no permission to skip an
earlier gate, replace a failing baseline, weaken assertions or relax isolation.
The directive supplies commands, exact test locations and required handoffs.

Approval covers this pilot profile only. It does not approve remaining family
contracts, close full P0/P1 gates, accept the entire refactor, authorize TUI work
or supply push/PR/merge/release authority.
