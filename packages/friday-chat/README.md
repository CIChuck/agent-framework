# Friday Chat

The maintained terminal chat application for Friday. It composes the framework's model, memory, agent, transcript and tool services and provides application configuration and local execution diagnostics.

**Distribution:** [friday-chat](https://pypi.org/project/friday-chat/) · **Import:** `friday_chat`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-chat==0.1.0a4"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: an offline interactive session

Create `demo.yaml` in a disposable working directory:

```yaml
llm:
  model: openai/offline-demo
chat:
  system_prompt: You are Friday.
```

Then run:

```bash
friday-chat --config demo.yaml --runtime fake
```

Type a message, then `/q` to exit. Fake mode is the CLI default and uses a test runtime; it does not contact a model, open real memory services or connect to MCP peers. Its responses are not evidence of a working provider integration. `friday-chat --help` and `friday-chat --version` inspect the installed command without starting chat.

## Configure a real session

Copy the installed examples to editable files outside the package. This script creates a **new** directory and refuses to overwrite an existing one:

```python
from importlib.resources import files
from pathlib import Path

destination = Path("friday-config")
destination.mkdir(exist_ok=False)
resources = files("friday_chat.config_templates")
for name in ("config.example.yaml", "models-config.example.yaml", "cli-config.example.yaml"):
    (destination / name).write_text(resources.joinpath(name).read_text(encoding="utf-8"), encoding="utf-8")
```

Edit `friday-config/config.example.yaml` and its companion model library to match your endpoints, models, writable state directories and enabled services. Preserve or update `model_library.path` relative to the runtime configuration file. A full example is a configuration starting point, not a universal provider setup.

Set every credential selected by an enabled service through your process environment. The supplied examples reference `FRIDAY_LLM_API_KEY`, `FRIDAY_OPENROUTER_API_KEY` and `FRIDAY_MOONSHOT_API_KEY`; remove or rebind services you do not use. Chat does not implicitly load `.env`. YAML model-library credentials store environment-variable **names**, never actual keys.

```bash
friday-chat --config friday-config/config.example.yaml --runtime real
```

Real mode can contact configured providers, consume quota and write configured state. Runtime YAML and Chat YAML have application-specific parsers; use the packaged Chat example when configuring this application.

## Features and optional integrations

- Interactive chat, configured model/embedding roles, memory retrieval/extraction, transcript persistence and selected native/MCP tools.
- Model-library bindings for primary chat, extraction, routing, compaction, maintenance, embeddings and smart-file processing. Legacy flat generation fields remain a compatibility surface; conflicting old/new fields fail validation.
- Optional `speech`, `finance`, `sandbox`, `moltbook` extras; `full` combines those integrations. For example: `python -m pip install "friday-chat[speech]==0.1.0a4"`. Installing dependencies does not enable providers.
- MCP client configuration under `tools.providers.mcp`, disabled by default. Real mode is required. Modern stdio and explicitly admitted HTTPS Streamable HTTP are supported; credentials, remote trust, filters and limits remain explicit.

See the MCP guide for complete YAML, canonical `mcp_...` tool names and the distinction between an optional peer and a pinned required tool. There is no Chat MCP health command, external MCP `config_file` include, or in-place integrated catalog-refresh switch.

## Diagnostics and telemetry

```yaml
telemetry:
  enabled: true
  provider: debug
```

Local telemetry is disabled by default. Enabled Chat telemetry supplies bounded local execution/LLM/MCP diagnostics, opaque turn correlation and safe `/debug`/`/timing` summaries. Closed telemetry events exclude raw prompts, responses, reasoning, tool data, memory contents, paths and credentials. This does **not** sanitize raw transcripts, generic caller events or legacy helpers.

Embedding applications can inject a borrowed `TelemetryInterface` through `build_runtime(config, telemetry=...)`; Chat does not close that provider. Remote exporter assembly and provider-neutral Langfuse integration remain separate work. The legacy `langfuse` section is not activated by local debug telemetry. Persistence diagnostics distinguish an intermediate write from full-turn success; they do not promise atomic rollback.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
Run the focused suite:

```bash
uv run --no-sync pytest packages/friday-chat/tests_chat -q
```

## Documentation and support

[Model configuration](https://github.com/CIChuck/agent-framework/blob/master/docs/reference/llm/model-library-technical-spec.md) · [MCP tools](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/17-mcp-client.md) · [Speech](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/speech.md) · [Chat configuration](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-chat/src/friday_chat/config.py) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-chat/src/friday_chat) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).
