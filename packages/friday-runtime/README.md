# Friday Runtime

Headless composition and lifecycle for Friday services. `RuntimeConfig` describes the application; `RuntimeKernel` assembles LLM, embeddings, memory, tools, transcripts, agents and telemetry.

**Distribution:** [friday-framework-runtime](https://pypi.org/project/friday-framework-runtime/) · **Import:** `friday_runtime`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-runtime==0.1.0a4"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: inspect configuration without starting services

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from friday_core import MemoryProfile
from friday_runtime import RuntimeConfig, RuntimeKernel

with TemporaryDirectory() as directory:
    root = Path(directory)
    (root / "install").mkdir()
    (root / "workspace").mkdir()
    config = RuntimeConfig.from_sources(
        env={},
        overrides={
            "install_root": str(root / "install"),
            "workspace_root": str(root / "workspace"),
            "runtime_data_root": str(root / "state"),
            "cache_root": str(root / "cache"),
            "telemetry_enabled": False,
        },
    )
    kernel = RuntimeKernel(config=config, memory_profile=MemoryProfile.EPHEMERAL)
    print(kernel.memory_profile.value)
```

Expected output: `ephemeral`. Construction is not startup: this example does not connect to providers or open persistent stores. An ephemeral memory profile does not make a subsequently started runtime network-free; configured chat and embedding services can still call providers.

## Start a real application

Prepare a Runtime YAML file, model/embedding bindings, credential environment variables, writable state paths and any agent profiles. This complete lifecycle example reads **your** configuration and starts the configured services:

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

It does not create a default agent profile. `spawn_agent(name)` requires a registered profile and valid model/tool bindings; use a name returned by `list_agents()`. Runtime YAML and Friday Chat YAML have distinct application parsers; share only documented canonical sections.

## Configuration and ownership

- Canonical `model_library.path`, `llm_pool` and `embedding_pool` bindings resolve through Friday LLM. Relative model-library paths are resolved from the Runtime YAML file.
- Source precedence is defaults, YAML, allowed environment overrides, then explicit overrides. YAML environment override behavior is controlled by `config_policy`.
- Persistent memory/transcript/artifact locations are application-owned. Workspace and runtime-data roots must not overlap; install/workspace roots and writable state parents must exist. Configure isolated paths for experiments; shutdown is awaited.
- `MemoryProfile.FULL`, `VECTOR_ONLY`, `EPHEMERAL` and `TESTING` choose storage combinations; they do not disable every model-dependent operation.

## MCP client tools

`tools.providers.mcp` is disabled by default. Integrated clients admit explicitly configured stdio or opted-in HTTPS Streamable HTTP peers. Stdio defaults to legacy compatibility; modern/auto is explicit. HTTP requires a dated protocol version, global remote opt-ins and per-peer remote trust. Bearer authentication resolves a credential environment-variable **name**, not a token embedded in YAML.

Discovery, filters, schema/token budgets and startup registration are Runtime-owned. A pinned missing `include_tools` name can stop registration even when the server itself is optional. `kernel.mcp_provider.operational_diagnostics` exposes typed outcomes. Integrated rediscovery uses public stop/start; no in-place YAML refresh switch exists. External MCP `config_file` includes are rejected. See the client guide for complete valid configurations and limits.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
Run the focused suite:

```bash
uv run --no-sync pytest packages/friday-runtime/tests_runtime -q
```

## Documentation and support

[Model library](https://github.com/CIChuck/agent-framework/blob/master/docs/reference/llm/model-library-technical-spec.md) · [MCP setup](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/17-mcp-client.md) · [Runtime schema](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-runtime/src/friday_runtime/config.py) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-runtime/src/friday_runtime) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).
