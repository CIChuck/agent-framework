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

Chat now delegates all six diagnostics through its typed port. Chat retains
legacy field projection, English output, telemetry/runtime reads and fixed UTF-8
exports; shared handlers own flags, capability order and awaited retrieval.
For exact `--debug`, `/context` calls the port's `context_debug_snapshot()`
once instead of `context_text()`; it must return exact `ContextData` with a
count and no export path, and shared code never re-measures or reformats it.
Candidate installed-artifact proof remains the separate DIAG D3 gate.

The DIAG standalone tests explicitly preload the pinned audit guard. Run the
Commands suite through a freshly prepared `validation/pilot/harness/prepare.py`
lane and its `pilot_run.py`, as specified in CD-CMD-DIAG-001. A plain pytest run
does not supply the guard required by those three standalone cases.

The opt-in memory-query API adds `MEMORY_QUERY_SPECS`, `MemoryQueryPort` and
`build_memory_query_handlers`, with thirteen frozen display-fact models. Its
six specs are memory, insights, summaries, meta, entities and list-ingested.
Register them explicitly; importing the package leaves registries empty.
The sixteen new exports follow the original 38 in order. Exactly six new
payload alternatives extend the closed outcome union; nested values cannot be
returned as outcomes, and subclass payloads are rejected.

Each handler validates the request, execution and canonical name, then checks
runtime availability once before awaiting one capability. Shared code selects
record kinds and graph mode, joins entity arguments and checks exact results.
Only exact first-argument `nodes` selects nodes-only mode. Non-string request
arguments and mismatched record kinds fail explicitly, including optimized
Python. Exceptions and cancellation propagate without retries or effects.

Hosts supply detached typed display facts and retain service reads, projection
and rendering. Memory queries perform no writes, synthesis, exports or session
changes. The neutral package imports no memory/runtime/frontend services.
This is the neutral D1 surface; Chat integration and option R's persisted
document listing follow at D2 under the approved contract. That listing uses
existing public reads owned by Chat; no domain capability moves into this
package. Source validation and command consolidation remain deferred.
