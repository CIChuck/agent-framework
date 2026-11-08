# Friday Commands

Frontend-neutral, standard-library-only command contracts and a registry for
injected asynchronous handlers, plus opt-in help, exit, clear-screen and session
view handlers. Registries start empty. The package has no runtime dependencies,
executable, provider access or frontend integration.

Distribution: `friday-framework-commands==0.1.0a4`. Import: `friday_commands`.
Python: 3.13.4 or newer. Part of the lock-step Friday package cohort.

```python
import asyncio
from friday_commands import (
    CommandExecution, CommandOutcome, CommandRegistry, CommandSpec, NoData,
)

async def handle(request, execution):
    return CommandOutcome(data=NoData())

async def main():
    registry = CommandRegistry()
    registry.register(CommandSpec("example", "Example", "demo", "/example"), handle)
    result = await registry.execute_text("/example", CommandExecution())
    print(result.handled)

asyncio.run(main())
```

Models validate their fields at runtime and snapshot collection inputs. Registry
registration is atomic and returns immutable canonical metadata. Only a literal
leading slash dispatches; arguments split on whitespace, preserving quote
fragments rather than applying shell parsing. Exceptions and cancellation from
handlers propagate; hosts own rendering, UI effects and lifecycle.

The pilot exports `PILOT_SPECS`, `HelpCatalog`, `describe_help` and
`build_pilot_handlers`. Register the specs and handlers explicitly in a consumer
registry. The injected synchronous catalog supplies help snapshots and exact-key
lookups; general help is sorted, focused help resolves one normalized key, and
unknown focus returns a typed error. Exit and clear only return typed lifecycle
or UI-effect requests. Hosts own rendering, shutdown and effect application.

Chat uses the shared help, exit and clear-screen handlers through typed adapters.
The Chat and framework CLI registries remain separate; other command families
require separately reviewed contracts. See the pilot contract and directive.

The session view exports are `HistoryTurn`, `HistoryData`, `SessionClearedData`,
`SESSION_SPECS`, `SessionPort` and `build_session_handlers`. Register the two
specs and returned handlers explicitly. The injected port supplies a history
snapshot or performs host-owned clearing; it stores no session state globally.
History returns an immutable ordered snapshot. Clear synchronously clears host
history, then awaits current-session memory clearing and returns a typed marker.
Exceptions and cancellation propagate without retries or restoring history.
The marker reports completion of that procedure, not erasure of every store.

Hosts render the data and implement the narrow port through their existing
public service boundary. `/clear` is conversation clearing; `/cls` remains the
separate display effect. Chat now delegates `/history` and `/clear` through its
typed session port, keeping English output and current-session memory ownership
in Chat and its runtime.

The opt-in diagnostics API exports `DIAGNOSTIC_SPECS`, `DiagnosticsPort` and
`build_diagnostic_handlers`, plus eleven immutable value models. Register its
six specs explicitly: context, prompt, debug, debug-budget, timing and
debug-retrieval. Shared handlers interpret exact flags, request an export only
after preparing its typed data, and check runtime availability before retrieval
usage. Retrieval is awaited once; host errors and cancellation propagate.

Ports supply detached typed debug/budget/timing facts, selected context/prompt
strings, and existing export/retrieval capabilities. The shared package renders
no terminal text, chooses no destination and imports no host/domain services.
Hosts own projection, presentation, encoding and fixed export paths. Invalid
port results fail without coercion; selected text must be a string. Direct
requests retain the existing string-only argument boundary. All 24 earlier
exports retain their order, with the fourteen diagnostics names appended.

This is the neutral diagnostics deliverable. Chat diagnostics wiring and
candidate installed-artifact proof are subsequent DIAG deliverables; the
accepted pilot and session integrations remain in place.
