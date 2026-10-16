# Friday Agent Framework

Friday is a modular Python framework for building agents with conversation memory, model services, tools and workflows. Use **Friday Chat** for a terminal application, **Friday Runtime** to compose an embedded application, or individual packages for smaller integrations.

**Current release:** [0.1.0a4](https://pypi.org/project/friday-framework/0.1.0a4/) (alpha) · **Python:** 3.13.4+ · **License:** MIT

Public APIs and configuration are still evolving. The implemented packages and their limits are described below; the Optimization namespace is scaffolding. Keep all Friday distributions on the same release version.

## Install and choose a starting point

Create a virtual environment, then install the published application or framework:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install "friday-chat==0.1.0a4"
friday-chat --help
```

On Windows, use `.venv\Scripts\Activate.ps1` in PowerShell instead of the `source` command. The examples assume a compatible Python is already installed.

For framework development in your own application:

```bash
python -m pip install "friday-framework==0.1.0a4"
```

`friday-framework` is a metadata-only convenience distribution: import the member packages, not `friday` or `friday_framework`. Its default dependencies include the core framework and Chat. Install an individual distribution from the table below when you need only that surface.

Optional extras include `mcp`, `speech`, `finance`, `sandbox`, `moltbook`, `optimization`, `documents`, `spreadsheets`, `langfuse` and `all`. Select only what your application needs, for example `python -m pip install "friday-framework[mcp]==0.1.0a4"`. Extras install dependencies; they do not configure credentials, start services, implement placeholder functionality, or complete the separately queued Langfuse backend.

## Quick start: define and invoke a local tool

This complete example needs no model, credentials, network or persistent stores:

```python
import asyncio
from friday_tools import FunctionTool

def greet(name: str) -> str:
    """Return a greeting."""
    return f"Hello, {name}!"

async def main() -> None:
    print(await FunctionTool(greet).execute(name="Friday"))

asyncio.run(main())
```

Expected output: `Hello, Friday!`.

For an interactive offline session, follow the [Friday Chat quick start](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-chat/README.md). To call actual models, configure the application's model/embedding services and environment credentials before selecting real mode. Chat defaults to a fake runtime for testing; a successful fake session does not verify a provider.

## How the packages fit together

```text
Application: Friday Chat or your own Python application
    RuntimeKernel: configuration, service ownership and lifecycle
        Agent / workflow -> LLM service and admitted tools
        Memory / context -> episodic, vector and graph adapters
        Transcript store -> conversation records and exports
        Telemetry sink -> configured events, spans and diagnostics
```

Packages expose public interfaces and typed models so applications can choose providers. The main integration layers are distinct:

- **Runtime** composes services; **Agent** defines behavior and workflows.
- **Memory** retrieves and assembles context; **Transcript** stores conversation records.
- **Tools** supplies executable tools; **MCP** connects external tool peers or exposes explicitly registered tools.
- **CLI Components** supplies terminal UI building blocks; **Chat** is the maintained terminal application.

## Package map

The workspace contains the root `friday-framework` distribution and these 16 members:

| Directory / README | PyPI distribution | Python import | Purpose |
| --- | --- | --- | --- |
| [friday-agent](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-agent/README.md) | `friday-framework-agent` | `friday_agent` | Agent profiles, orchestration and workflows |
| [friday-chat](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-chat/README.md) | `friday-chat` | `friday_chat` | Terminal chat application |
| [friday-cli](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-cli/README.md) | `friday-framework-cli` | `friday_cli` | Reusable terminal components; historical executable is a placeholder |
| [friday-core](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-core/README.md) | `friday-framework-core` | `friday_core` | Shared contracts, logging and security primitives |
| [friday-finance](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-finance/README.md) | `friday-framework-finance` | `friday_finance` | Massive financial-data client |
| [friday-llm](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-llm/README.md) | `friday-framework-llm` | `friday_llm` | Chat, embeddings and typed model requests |
| [friday-mcp](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-mcp/README.md) | `friday-framework-mcp` | `friday_mcp` | MCP tools clients and programmatic servers |
| [friday-memory](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-memory/README.md) | `friday-framework-memory` | `friday_memory` | Memory, retrieval, context assembly and lifecycle |
| [friday-moltbook](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-moltbook/README.md) | `friday-framework-moltbook` | `friday_moltbook` | Typed Moltbook client |
| [friday-optimization](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-optimization/README.md) | `friday-framework-optimization` | `friday_opt` | Experimental namespace; optimizer modules are placeholders |
| [friday-runtime](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-runtime/README.md) | `friday-framework-runtime` | `friday_runtime` | Headless service composition and lifecycle |
| [friday-sandbox](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-sandbox/README.md) | `friday-framework-sandbox` | `friday_sandbox` | Execution backends and workspace ownership |
| [friday-speech](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-speech/README.md) | `friday-framework-speech` | `friday_speech` | Speech contracts, adapters and playback |
| [friday-telemetry](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-telemetry/README.md) | `friday-framework-telemetry` | `friday_telemetry` | Provider-neutral events, spans and optional exporters |
| [friday-tools](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-tools/README.md) | `friday-framework-tools` | `friday_tools` | Tool definitions, registries and integrations |
| [friday-transcript](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-transcript/README.md) | `friday-framework-transcript` | `friday_transcript` | Conversation records, persistence and exports |

## Configuration and operational limits

Start from the examples packaged with the application you actually use. Friday Chat and headless Runtime have their own parsers; do not assume every YAML section or environment variable applies to every entry point. The [model-library reference](https://github.com/CIChuck/agent-framework/blob/master/docs/reference/llm/model-library-technical-spec.md) explains endpoint/model identity and credential references.

Keep provider keys in process environments or your secret-management system, never committed YAML. Chat does not implicitly load `.env`. Select writable application-owned state paths; memory stores and transcripts can contain private content. Examples that call providers or start execution backends must be explicitly provisioned and can consume quota or mutate state.

MCP is disabled by default. Its integrated clients support configured local stdio and explicitly admitted HTTPS Streamable HTTP peers; supported roles/revisions and limits are documented in the [MCP README](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-mcp/README.md). Tools-profile support is not a claim of complete MCP conformance.

Telemetry is provider-neutral and application-selected. Closed LLM/MCP/execution event schemas exclude raw content, while generic events, legacy helpers and transcripts have different guarantees. OpenTelemetry export needs explicit assembly and configuration. The provider-neutral Langfuse implementation remains queued; installing the legacy optional integration is not its implementation.

## Development

Clone the monorepo and install the shared workspace, optional integrations and development tools with [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/CIChuck/agent-framework.git
cd agent-framework
uv sync --all-packages --all-extras --group dev --python 3.13
uv run --no-sync python -c "from friday_runtime import RuntimeKernel; print('Friday imports OK')"
```

The checkout's `.python-version` selects Python 3.13; metadata enforces the 3.13.4 minimum. Each member has its own `pyproject.toml`, and the workspace shares `uv.lock`. Use a narrower package/extras selection when working without optional SDKs or integrations. Do not commit generated `.venv`, credentials or application data.

Run checks from the repository root:

```bash
uv run --no-sync pytest packages/friday-runtime/tests_runtime -q
uv run --no-sync ruff check .
uv run --no-sync mypy packages tests main.py
```

Package READMEs give their focused test path. `uv run --no-sync pytest` runs configured package/lab discovery; top-level integration suites are separate. Some integration/live suites need credentials, Docker, model services or existing fixtures: select them deliberately. Broad lint/type/test runs may expose existing debt; report it separately from new failures rather than weakening checks.

Before implementation, read [AGENTS.md](https://github.com/CIChuck/agent-framework/blob/master/AGENTS.md), the [engineering policy](https://github.com/CIChuck/agent-framework/blob/master/docs/reference/policies/repository-engineering-policy.md) and the [development board](https://github.com/CIChuck/agent-framework/blob/master/docs/planning/README.md). Changes follow the task/directive, independent validation and maintainer-acceptance workflow. A documentation page or queued task is not implementation authority.

## Documentation, support and contributions

- [Documentation index](https://gendevx.com/friday/): guides and deeper topics; consult current package READMEs and metadata for entry points.
- [Model library](https://github.com/CIChuck/agent-framework/blob/master/docs/reference/llm/model-library-technical-spec.md), [MCP client](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/17-mcp-client.md), [MCP server](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/18-mcp-server.md), [MCP migration](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/19-mcp-migration.md), [speech](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/speech.md).
- [Report issues or request features](https://github.com/CIChuck/agent-framework/issues): include the Friday/Python versions, affected package, minimal reproduction and sanitized diagnostics.
- [Contributing guide](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md): read alongside current repository policy. Keep pull requests scoped and include validation and migration implications.

Older guides and design documents may describe historical or proposed behavior. The package metadata, public implementation and current task authority determine what is available now. The historical `friday` console entry point is a placeholder; use `friday-chat` for the terminal app. Root `main.py` is a smoke entry point.

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).
