# Friday Agent Framework

Friday is a Python framework for building AI agents that can remember, retrieve,
act, and collaborate across sessions. The project is organized as a `uv`
workspace of independently useful packages covering memory, LLM access, agent
orchestration, tools, transcripts, telemetry, sandboxing, MCP integration, and
runtime assembly.

The core idea is simple: an agent should not start from zero every time it is
called. Friday gives agents a memory loop that records what happened, extracts
what was learned, retrieves relevant context, and feeds that context back into
future turns.

Status: `v0.1.0`, alpha. The memory, agent, runtime, and tool packages contain
substantial implementation, but the repository is still under active
architectural cleanup. Some documentation describes the target system as well as
the current system.

## What Friday Provides

- Three-tier memory:
  - Episodic memory for conversation history and transcripts.
  - Semantic memory for embedding-backed recall.
  - Associative memory for entity and relationship graphs.
- Context engineering:
  - Retrieval from memory stores.
  - Token-budget-aware prompt assembly.
  - Session priming and lifecycle-aware memory inclusion.
- Agent orchestration:
  - Interactive ReAct-style agents.
  - Multi-agent routing and delegation.
  - Workflow/task graph execution with human-in-the-loop support.
- Tooling:
  - Filesystem, shell, web, git, data, text, code, system, finance, and memory
    tools.
  - Tool schemas for LLM function/tool calling.
  - Prompt-injection-aware output handling.
- Runtime infrastructure:
  - Headless runtime kernel.
  - Dependency injection for memory, LLM, telemetry, transcripts, and tools.
  - CLI-facing presentation components.
- Observability:
  - Structured logging.
  - Telemetry interfaces and providers.
  - Persistent transcripts and export formats.
- Extensibility:
  - Protocol-oriented interfaces for memory stores, LLM clients, tools,
    transcripts, telemetry, and runtime services.
  - MCP client/server integration.
  - Optional local/cloud/hybrid model routing through LiteLLM-compatible
    services.

## Python requirement

Friday requires **Python 3.13.4 or newer**. Python 3.10, 3.11, 3.12 and
3.13.0–3.13.3 are unsupported. The workspace selects the Python 3.13 series
through `.python-version`; package metadata enforces the patch minimum.

For an existing checkout using an older interpreter, select Python 3.13.4 or
newer and recreate the environment with `uv sync --python 3.13`. Dependency
constraints are unchanged, including LiteLLM 1.100.1.

## Repository Layout

```text
.
├── docs/
│   ├── guides/                 # Product and usage documentation
│   ├── policies/               # Repository engineering policy
│   └── design/                 # Design notes and implementation plans
├── experiments/                # Labs and exploratory work
├── packages/                   # Python workspace packages
├── tests/                      # Top-level integration/lab/unit suites
├── main.py                     # Minimal smoke entry point
├── pyproject.toml              # Root workspace project
└── uv.lock                     # Locked dependency graph
```

The root project is a convenience workspace package named `friday`. Most code
lives under `packages/`.

## Package Map

| Package | Purpose | Notes |
| --- | --- | --- |
| `friday-core` | Shared interfaces, config, logging, security primitives, exceptions | Intended foundation layer. Some current factory/bridge code still reaches into concrete packages. |
| `friday-telemetry` | Telemetry records, interfaces, providers, helper models | Includes debug and OpenTelemetry-style provider support. |
| `friday-llm` | LiteLLM-backed chat and embedding services | Includes resilience, pricing, telemetry helpers, and provider config. |
| `friday-transcript` | Persistent transcript models, stores, and exporters | SQLite and JSONL-oriented transcript storage/export support. |
| `friday-memory` | Memory controller, adapters, lifecycle, retrieval, context assembly, ingestion, multi-agent memory | The largest and most central package. |
| `friday-agent` | Agent base classes, interactive/Copilot agents, registries, orchestration, workflows, built-in agent tools | `CopilotAgent` currently aliases the interactive runtime agent for compatibility. |
| `friday-runtime` | Headless runtime kernel and dependency injection | Preferred assembly layer for creating full framework services. |
| `friday-cli` | Terminal display/input/session components and server hooks | The declared `friday` console entry point is still under development in this checkout. |
| `friday-tools` | General and integration tool catalog | Includes filesystem, shell, web, git, data, document, code, memory, finance, and integration tools. |
| `friday-sandbox` | Workspace and subprocess/Docker sandbox support | Used by execution-related tools and runtime isolation work. |
| `friday-mcp` | Model Context Protocol client/server integration | Supports stdio/SSE-oriented MCP components. |
| `friday-speech` | Speech service interfaces, selection, chunking, playback, adapters | Optional Picovoice and ElevenLabs extras are defined. |
| `friday-finance` | Financial data provider integration | Includes a `friday-finance-demo` script. |
| `friday-moltbook` | Moltbook API client and Pydantic models | Used by Moltbook integration tools. |
| `friday-optimization` | DSPy/lab optimization package | Currently a playground package rather than a core runtime dependency. |

## Architecture Overview

Friday separates agent work into two broad areas:

```text
User input
   |
   v
RuntimeKernel / DI container
   |
   +--> LLM service
   +--> Tool registry
   +--> Transcript store
   +--> MemoryController
          |
          +--> Episodic store      conversation turns
          +--> Vector store        semantic memories
          +--> Graph store         entities and relationships
          +--> Collection manager  lifecycle-aware memory collections
   |
   v
Agent / Orchestrator / Workflow engine
   |
   +--> Context assembly
   +--> LLM inference
   +--> Tool execution
   +--> Transcript and memory archival
```

The memory loop is the central design:

1. A user asks a question or gives a task.
2. Friday retrieves relevant prior context from memory.
3. The agent sends an assembled prompt to an LLM.
4. The LLM responds directly or requests tool calls.
5. Tool results are sanitized, wrapped, and returned to the model.
6. The turn is archived to transcript/episodic memory.
7. Extracted insights, entities, and relationships are stored for future turns.
8. Lifecycle jobs can promote, decay, compact, or reorganize memories over time.

## Installation

Friday uses `uv` for workspace development.

```bash
uv sync --all-extras
```

For a lighter development install, the default sync is usually enough:

```bash
uv sync
```

Then verify imports:

```bash
uv run python -c "from friday_runtime import RuntimeKernel; from friday_agent import InteractiveAgent; print('Friday imports OK')"
```

## Configuration

Start from the example environment file:

```bash
cp .env.example .env
```

Minimum useful environment:

```bash
APP_ENV=development
LOG_LEVEL=INFO
OPENAI_API_KEY=sk-proj-...
```

Common runtime variables include:

```bash
FRIDAY_LLM_MODEL=gpt-4o-mini
FRIDAY_CHROMA_PATH=.friday/chroma
FRIDAY_CHROMA_COLLECTION=friday_memory
FRIDAY_TELEMETRY_ENABLED=false
```

Local or enterprise model gateways can be configured through the runtime and LLM
configuration objects. See [docs/guides/10-configuration.md](docs/guides/10-configuration.md)
for the full configuration guide.

## Programmatic Usage

The headless runtime is the main composition API for applications that want to
embed Friday without a CLI.

```python
import asyncio

from friday_core.profiles import MemoryProfile
from friday_runtime import RuntimeConfig, RuntimeKernel


async def main() -> None:
    config = RuntimeConfig.from_env()
    kernel = RuntimeKernel(config=config, memory_profile=MemoryProfile.FULL)

    await kernel.start()
    try:
        # Agent spawning requires configured agent profiles.
        # See docs/guides/06-agents.md for profile structure.
        agent = kernel.spawn_agent("assistant")
        response = await agent.run("What do you remember about this project?")
        print(response)
    finally:
        await kernel.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

For lower-level use, individual packages can be imported directly:

```python
from friday_llm import LiteLLMService
from friday_memory import ContextAssembler, MemoryController
from friday_agent import AgentProfile, InteractiveAgent
from friday_tools import get_default_registry
```

## Development Commands

Install dependencies:

```bash
uv sync --all-extras
```

Run tests:

```bash
uv run pytest
```

Run a focused package test suite:

```bash
uv run pytest packages/friday-memory/tests_memory
uv run pytest packages/friday-agent/tests_agent
uv run pytest packages/friday-runtime/tests_runtime
```

Run linting:

```bash
uv run ruff check .
```

Run type checking:

```bash
uv run mypy packages tests main.py
```

Run the minimal smoke entry point:

```bash
uv run python main.py
```

## Testing Notes

The repository uses:

- `pytest`
- `pytest-asyncio`
- `ruff`
- `mypy`

Tests are distributed by package, usually under `packages/<package>/tests_*`.
Top-level integration and lab tests live under `tests/` and `experiments/`.

Some tests and integrations require provider credentials, local model services,
network access, Docker, or pre-existing local state. Prefer focused package tests
while developing a narrow change.

## Security Model

Friday treats tool outputs and external content as untrusted. The security
subsystem is designed around:

- Normalizing tool output before scanning.
- Detecting prompt-injection patterns.
- Wrapping tool output with provenance markers.
- Quarantining, redacting, warning, or blocking risky content.
- Avoiding persistence of raw malicious tool output into memory stores.

See [docs/guides/security-configuration-guidelines.md](docs/guides/security-configuration-guidelines.md)
for configuration details and the tool onboarding checklist.

## Documentation

Primary product guides:

- [Executive summary](docs/guides/01-executive-summary.md)
- [Getting started](docs/guides/02-getting-started.md)
- [Core concepts and architecture](docs/guides/03-core-concepts.md)
- [Adaptive memory](docs/guides/04-adaptive-memory.md)
- [Tools](docs/guides/05-tools.md)
- [Agents](docs/guides/06-agents.md)
- [Multi-agent orchestration](docs/guides/07-multi-agent.md)
- [Workflows](docs/guides/08-workflows.md)
- [CLI reference](docs/guides/09-cli-reference.md)
- [Configuration](docs/guides/10-configuration.md)
- [Advanced topics](docs/guides/11-advanced-topics.md)
- [Use cases](docs/guides/12-use-cases.md)
- [Troubleshooting](docs/guides/13-troubleshooting.md)
- [Appendices](docs/guides/14-appendices.md)
- [Contributing](docs/guides/15-contributing.md)

Repository policy:

- [Repository engineering policy](docs/reference/policies/repository-engineering-policy.md)

Important note: the guides are extensive and useful, but some package-layout and
CLI details are ahead of or behind the current code. When making code changes,
prefer the repository policy and current package metadata as the source of truth.

## Engineering Policy

The canonical engineering policy is
[docs/reference/policies/repository-engineering-policy.md](docs/reference/policies/repository-engineering-policy.md).
Key rules:

- Do not add file-level `# mypy: ignore-errors` under `packages/*/src` without
  an explicit waiver.
- Do not rely on `assert` as the sole enforcement for essential runtime
  invariants.
- Prefer typed models, declared interfaces, and explicit contracts at package
  boundaries.
- Prefer interface fixes over repeated `cast(...)`.
- Keep runtime credentials and local state out of the repository.

## Local State and Secrets

Do not commit:

- `.env`
- `.friday/`
- `chroma_db/`
- provider API keys
- local transcript/vector/graph stores
- generated caches such as `__pycache__`, `.pytest_cache`, and `.ruff_cache`

## Current Development Caveats

This repository is actively evolving. A few areas are especially worth knowing
before building on it:

- The package architecture has grown beyond older documentation that describes
  an eight-package workspace.
- The root `main.py` is only a minimal smoke script.
- The `friday-cli` package contains useful terminal components, but the declared
  console application entry point is not yet a complete CLI in this checkout.
- `friday-optimization` is currently lab-oriented.
- Some integration and backup code under `tests/` is legacy or experimental and
  may not represent stable public API usage.

## Contributing

Before changing code:

1. Read [docs/reference/policies/repository-engineering-policy.md](docs/reference/policies/repository-engineering-policy.md).
2. Identify the package boundary affected by the change.
3. Prefer narrow, typed contracts over incidental cross-package imports.
4. Add focused regression tests for behavior changes.
5. Run the narrowest meaningful tests, then broader validation when practical.

Pull requests should include:

- What changed.
- Why it changed.
- How to validate it.
- Package or configuration implications.
- Any migration notes for public contracts or persisted data.

## License

The root project metadata declares the project as MIT licensed.
