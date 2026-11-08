# Friday Commands

Frontend-neutral, standard-library-only command contracts and a registry for
injected asynchronous handlers, plus opt-in help, exit and clear-screen pilot
handlers. Registries start empty. The package has no runtime dependencies,
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
