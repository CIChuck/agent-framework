# Friday Core

Shared contracts and primitives for Friday packages: LLM, memory, tool, agent and telemetry interfaces; configuration; structured logging; errors; and security types. Import contracts here when implementing an adapter.

**Distribution:** [friday-framework-core](https://pypi.org/project/friday-framework-core/) · **Import:** `friday_core`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-core==0.1.0a3"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: structured logging

```python
from friday_core import MemoryProfile, get_logger

logger = get_logger("example")
logger.info("application.configured", memory_profile=MemoryProfile.EPHEMERAL.value)
```

This creates a log record without constructing a model client or opening a memory store. Configure log destinations in your application.

## Package boundaries

| Surface | Use |
| --- | --- |
| `LLMClient`, `EmbeddingModel` | Model service contracts |
| `VectorStoreAdapter`, `GraphStoreAdapter`, `EpisodicStoreAdapter` | Memory backends |
| `ToolDefinition`, `ToolRegistry` | Tool definitions and discovery |
| `TelemetryInterface` | Provider-neutral instrumentation |
| `MemoryProfile` | Storage profile selection |
| `security` | Tool-output validation and provenance support |

Concrete services live in the corresponding Friday packages. Telemetry implementations are maintained in `friday-framework-telemetry`; Core retains compatibility re-exports. The optional `telemetry` extra installs that package's OpenTelemetry dependencies; it does not enable collection automatically. Do not treat output scanning as a complete isolation boundary for arbitrary code.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
Run the focused suite:

```bash
uv run --no-sync pytest packages/friday-core/tests_core -q
```

## Documentation and support

[Architecture](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/03-core-concepts.md) · [Security configuration](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/security-configuration-guidelines.md) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-core/src/friday_core) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).
