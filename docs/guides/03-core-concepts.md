---
title: Core concepts and architecture
description: Package boundaries, contracts, turn processing and ownership in Friday applications.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Core concepts and architecture

Friday separates contracts, service implementations, application composition and
user interfaces. Understanding those layers helps you choose the smallest useful
integration and assign ownership of providers, stores and background tasks.

## Architecture layers

```text
Application: Friday Chat / your service
  -> configuration + lifecycle + consent + paths
  -> agents / orchestration / workflow execution
     -> context assembly and memory coordination
     -> LLM and embedding interfaces
     -> tool registry, admission and execution
     -> transcript and telemetry interfaces
        -> concrete model, storage, transport and exporter adapters
```

“Intelligence plane” and “control plane” are architectural descriptions. They
do not imply separately deployed services. A single process can compose all
of these layers; distributed deployments require additional application design.

| Layer | Packages | Responsibility |
| --- | --- | --- |
| Contracts | `friday-core` | Typed LLM, memory, tool, telemetry and agent contracts; shared primitives |
| Models | `friday-llm` | LiteLLM transport, normalized generation controls and model-library resolution |
| Memory | `friday-memory`, `friday-transcript` | Recall/extraction/context/lifecycle and durable conversation records |
| Execution | `friday-agent`, `friday-tools`, `friday-sandbox` | Profiles, orchestration, workflows, tool implementations and execution backends |
| Integration | `friday-mcp`, `friday-speech`, `friday-finance`, `friday-moltbook` | Explicit external capabilities |
| Observation | `friday-telemetry` | Provider-neutral observers, factory ownership and optional OpenTelemetry |
| Composition/UI | `friday-runtime`, `friday-chat`, `friday-cli` | Headless assembly, maintained terminal application and terminal components |
| Placeholder | `friday-optimization` | Package skeleton imported as `friday_opt`; no implemented optimization pipeline |

These are 16 workspace packages plus the root metadata distribution. See the
[distribution/import map](14-appendices.md#package-map); package-directory names
are not always valid PyPI names. The historical `friday` console entry point
declared by `friday-framework-cli` is not a functioning application in this
release. Use `friday-chat` for the maintained terminal app.

## Protocols and concrete implementations

Core interfaces describe operations required at a boundary. Concrete adapters
provide those operations; a protocol declaration does not ship every backend
that could implement it.

| Contract | Current examples | Integration consequence |
| --- | --- | --- |
| `LLMClient`, `EmbeddingModel` | LiteLLM chat/embedding services | Provider capability, credentials and failure behavior remain route-dependent |
| `EpisodicStoreAdapter` | In-memory history; transcript-backed history | Decide ephemeral versus durable storage explicitly |
| `VectorStoreAdapter` | `SimpleVectorStore`, `ChromaVectorStore` | Match embeddings, dimensions, collection identity and persistence |
| `GraphStoreAdapter` | `ElementXGraphStore`, `NullGraphStore` | Choose a real graph or explicitly omit graph operations |
| `ToolDefinition`, `ToolRegistry` | `FunctionTool`, `DefaultToolRegistry` | Registration is separate from per-turn selection and permissions |
| `TelemetryInterface` | Debug, composite and optional OpenTelemetry providers | Borrowers emit; owners flush and close |

Implement a new backend against the actual [Core interfaces](../../packages/friday-core/src/friday_core/interfaces),
including result shapes and lifecycle behavior. Friday does not currently ship
the `PineconeAdapter`, `Neo4jAdapter` or `OllamaClient` classes shown in older
guides. LiteLLM can route supported local/cloud services; check the selected
route rather than assuming every generation option is portable.

## Runtime composition and ownership

`RuntimeConfig` describes a headless application. `RuntimeKernel` composes
model/embedding pools, memory, agents, tools, transcripts and other services.
Constructing a kernel is separate from starting it.

This **offline Python example** validates isolated paths and constructs a
kernel without opening stores or calling models:

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from friday_core import MemoryProfile
from friday_runtime import RuntimeConfig, RuntimeKernel

with TemporaryDirectory() as directory:
    root = Path(directory)
    (root / "install").mkdir()
    (root / "workspace").mkdir()
    config = RuntimeConfig.from_sources(env={}, overrides={
        "install_root": str(root / "install"),
        "workspace_root": str(root / "workspace"),
        "runtime_data_root": str(root / "state"),
        "cache_root": str(root / "cache"),
        "telemetry_enabled": False,
    })
    kernel = RuntimeKernel(config=config, memory_profile=MemoryProfile.EPHEMERAL)
    print(kernel.memory_profile.value)
```

Expected output: `ephemeral`. Install/workspace roots exist, runtime state is
separate from the workspace and writable parents are available. Storage profile
selection does not make a **started** application network-free: ephemeral
memory can still call an embedding or extraction provider.

The **live lifecycle example** below loads your prepared headless configuration:

```python
import asyncio
from friday_runtime import RuntimeConfig, RuntimeKernel

async def main() -> None:
    kernel = RuntimeKernel(config=RuntimeConfig.from_yaml("runtime.yaml"))
    await kernel.start()
    try:
        print(kernel.list_agents())
    finally:
        await kernel.stop()

asyncio.run(main())
```

No default agent profile is created by this example. `spawn_agent(name)` needs
a registered profile and valid factory/service bindings. Chat has a distinct
configuration parser and assembly path; it is not a universal `RuntimeConfig`
YAML loader. See [configuration](10-configuration.md).

## A turn is a sequence of distinct operations

1. Resolve the active profile and session. Application identity is separate
   from untrusted model text or tool output.
2. Select tool schemas, account for their token cost and reserve result space
   where the integration supports it.
3. Recall memory, filter relevance/lifecycle state and apply context budgets.
4. Format model messages. Historical tool activity is represented differently
   from the native call/result pairs in a currently executing tool loop.
5. Receive text, reasoning, tool, usage and finish events through the appropriate
   LLM API. Reasoning events are distinct from user-facing text.
6. Validate and execute admitted tool calls. An error or timeout does not prove
   an external mutation had no effect; avoid automatic replay of uncertain work.
7. Persist the turn and settle configured secondary/background operations.
   Intermediate persistence and terminal success are different outcomes.

Chat's local telemetry tracks categorical outcomes and opaque correlation IDs.
Transcripts can retain raw conversational content. Neither the presence of a
span nor a successful SQLite write establishes atomic rollback across memory,
tools and external systems.

## Memory, orchestration and workflow state

Memory supplies retrieved context. An agent profile supplies identity and tool
selection preferences. An orchestrator routes to instantiated agents. A workflow
defines dependencies and execution state. Sharing one of these objects does not
automatically share all other state.

For example, two agent instances may share a memory controller while using
different session identifiers or namespace policies. A completed research task
should pass an explicit result/artifact to a reviewer rather than relying on
similarity search to recover the exact handoff. See [multi-agent operation](07-multi-agent.md)
and [workflows](08-workflows.md).

## Observation and resource ownership

Construct providers once at the owning application boundary. Inject
`TelemetryInterface` into consumers; consumers must not close borrowed providers.
The owned telemetry handle reports flush/shutdown outcomes and incomplete work.
The low-level debug recorder is unbounded and retains caller-supplied values.

LiteLLM client cleanup can affect process-shared clients. Quiesce all users
before process-level cleanup; do not close shared clients after each service
call. Similarly, stop agents/tools/background work before snapshotting or
restoring stores. Explicit ownership is a practical requirement for reliable
restarts, backups and tests.

## Implementation references

- [Core contracts](../../packages/friday-core/src/friday_core/interfaces)
- [Runtime configuration](../../packages/friday-runtime/src/friday_runtime/config.py)
- [Runtime kernel](../../packages/friday-runtime/src/friday_runtime/kernel.py)
- [Chat turn processing](../../packages/friday-chat/src/friday_chat/turns/processor.py)
- [Memory context assembly](../../packages/friday-memory/src/friday_memory/context/assembler.py)
- [LLM model-library contract](../reference/llm/model-library-technical-spec.md)

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
