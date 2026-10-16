# Friday Memory

Conversation memory, semantic retrieval, entity graphs, context assembly, ingestion, and lifecycle maintenance. Choose individual adapters or let Friday Runtime compose the memory controller.

**Distribution:** [friday-framework-memory](https://pypi.org/project/friday-framework-memory/) · **Import:** `friday_memory`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-memory==0.1.0a4"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: store and retrieve a conversation turn

This example is ephemeral and requires no model, credentials, or database.

```python
import asyncio

from friday_memory import InMemoryEpisodicStore, InteractionTurn

async def main() -> None:
    store = InMemoryEpisodicStore()
    await store.add_turn(
        "demo",
        InteractionTurn(
            id="turn-1", session_id="demo",
            user_message="Remember the project name.",
            assistant_message="The project is Friday.",
        ),
    )
    turns = await store.get_turns("demo")
    print(turns[0].assistant_message)

asyncio.run(main())
```

Expected output: `The project is Friday.` This does not perform semantic retrieval or durable persistence.

## Choosing a memory surface

| Need | Public API |
| --- | --- |
| Short-term turn history | `InMemoryEpisodicStore` |
| Semantic search | `SimpleVectorStore` or `ChromaVectorStore`, plus an embedding service |
| Entity relationships | `ElementXGraphStore` or `NullGraphStore` |
| Coordinated recall and writes | `MemoryController` |
| Budgeted prompt context | `ContextAssembler`, `PromptArchitect` |
| Extraction and consolidation | `MemoryExtractor`, `MemoryConsolidator` |
| Namespace-aware shared memory | `MultiAgentMemoryController`, namespace/promotion contracts |

`MemoryController` requires explicit vector, graph, episodic and collection-management dependencies. For a full application, prefer Runtime composition over assembling those dependencies by hand. Extraction, semantic recall and maintenance can invoke configured model services; the offline example above does not.

## Storage and configuration

Persistent adapters need application-owned paths and, where applicable, a compatible embedding model/dimension. Use disposable directories for experiments. Stored transcripts, memory and diagnostic content can be sensitive; do not commit them. Lifecycle operations and snapshot/restore APIs have explicit ownership and quiescence requirements; they are not interchangeable with deleting store files.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
Run the focused suite:

```bash
uv run --no-sync pytest packages/friday-memory/tests_memory -q
```

## Documentation and support

[Runtime setup](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-runtime/README.md) · [Memory guide](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/04-adaptive-memory.md) · [Memory management](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/memory-management-guidelines.md) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-memory/src/friday_memory) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).
