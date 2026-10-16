---
title: Getting started
description: Install alpha3, run an offline Chat session and prepare a real model-backed configuration.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Getting started

This guide separates installation, an offline UI check, and a real session.
Complete the offline check first. It requires no provider account, model server,
microphone, Docker daemon or existing memory store.

## Prerequisites and installation

Use **Python >=3.13.4** in an isolated environment. Keep Friday distributions
on the same **0.1.0a3** version. From a new application directory on macOS/Linux:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install "friday-chat==0.1.0a3"
friday-chat --version
friday-chat --help
```

On Windows PowerShell, create the environment with `py -3.13 -m venv .venv`
and activate `.venv\Scripts\Activate.ps1`, then use the same `python -m pip`
and `friday-chat` commands. Check the interpreter's patch version with
`python --version` before installation.

For a persistent executable managed by uv, see [desktop deployment](16-desktop-deployment.md).
For library use, install the component you need, such as
`friday-framework-runtime==0.1.0a3`. The root `friday-framework` distribution
is an aggregate metadata package, not an importable application.

## Run an offline Chat session

Save this **complete offline configuration** as `demo.yaml`:

```yaml
llm:
  model: openai/offline-demo
chat:
  system_prompt: You are Friday.
```

Run from the directory containing that file:

```bash
friday-chat --config demo.yaml --runtime fake
```

Type a short message, try `/help` and `/history`, then exit with `/q`.
The `openai/offline-demo` identifier is a configuration placeholder; fake mode
does not send it to a provider. Fake mode uses test implementations and does
not demonstrate durable memory, model quality or MCP connectivity.

Fake is the CLI default. An existing `FRIDAY_CHAT_RUNTIME` environment variable
overrides the `--runtime` value, so remove an unintended setting before relying
on either mode. There is no supported `friday-chat init` or `doctor` command in
this release. Use explicit `--config` paths.

## Prepare a real session

Real sessions can call providers and write state. Copy installed templates into
a new directory outside the installed package. This **offline Python example**
refuses to overwrite an existing directory:

```python
from importlib.resources import files
from pathlib import Path

destination = Path("friday-config")
destination.mkdir(exist_ok=False)
resources = files("friday_chat.config_templates")
for name in ("config.example.yaml", "models-config.example.yaml", "cli-config.example.yaml"):
    text = resources.joinpath(name).read_text(encoding="utf-8")
    (destination / name).write_text(text, encoding="utf-8")
print(destination)
```

The templates are broad examples with multiple model roles and optional
integrations. Before running them:

1. Select the model and embedding endpoints you actually operate. Record the
   exact served model/revision rather than assuming example identifiers exist.
2. Edit `models-config.example.yaml` and the `llm_pool`/`embedding_pool` bindings.
   Remove or rebind unused services. Keep `model_library.path` relative to the
   main configuration file, or provide an explicit absolute path.
3. Supply credentials selected by those bindings through environment-variable
   references. Chat does not automatically load `.env` files.
4. Remove unused `${...}` placeholders from the main YAML, including disabled
   optional sections: Chat interpolates ordinary strings before validation.
   HTTP MCP `credential_env` is a special literal reference, discussed in the
   [MCP client guide](17-mcp-client.md#secrets-and-paths).
5. Set memory, transcript, export and log paths to a new, writable data directory.
   Adjust the example user names/system prompt to your application.
6. Disable optional integrations you have not configured, including the example's
   legacy `langfuse` section. Review raw prompt capture and quarantine retention
   before using real user data.

[Configuration](10-configuration.md) supplies a smaller canonical model-library
example and explains how roles, generation controls and storage settings relate.
The display file controls terminal appearance; it is not the place for model,
tool, MCP or security settings.

With your endpoints running and credentials configured, this is a **live command**:

```bash
friday-chat --config friday-config/config.example.yaml --cli-config friday-config/cli-config.example.yaml --runtime real
```

A successful response verifies the selected chat route only. Test extraction,
embedding recall, tool calls and restart persistence independently.

## Check persistence without relying on model recollection

In a disposable real-session data directory, state a distinctive synthetic fact,
then inspect `/history`, `/sessions`, `/transcript` and `/memory`. Exit normally
so owned background work and configured shutdown processing can settle. Restart
with the same configuration and paths, then inspect the persisted session.

Distinguish these checks:

| Check | Evidence it provides |
| --- | --- |
| `/transcript <session_id>` shows an earlier turn | The transcript backend retained that turn |
| `/entities`, `/insights` or `/summaries` shows extracted records | The corresponding extraction/storage operation produced records |
| `/context` or `/prompt` contains the earlier fact | Current context construction selected it |
| A later model response mentions the fact | The model used available context; verify its wording against the source |

Extraction may be asynchronous or interval-based. A transcript receipt does not
prove all secondary stores are updated. Check diagnostics and enabled extraction
roles before concluding that memory is missing. Never delete a live database's
lock files to make a check pass.

## Use a component without Chat

This **offline Python example** demonstrates episodic storage only:

```python
import asyncio
from friday_memory import InMemoryEpisodicStore, InteractionTurn

async def main() -> None:
    store = InMemoryEpisodicStore()
    await store.add_turn("demo", InteractionTurn(
        id="turn-1", session_id="demo",
        user_message="What is the project?",
        assistant_message="The project is Friday.",
    ))
    turns = await store.get_turns("demo")
    print(turns[0].assistant_message)

asyncio.run(main())
```

Expected output: `The project is Friday.` The store disappears with the process.
For durable transcripts, see [the SQLite example](04-adaptive-memory.md#durable-transcripts).
For full-stack assembly, see [runtime composition](03-core-concepts.md#runtime-composition-and-ownership).

## Where to go next

- [Core concepts](03-core-concepts.md) explains package boundaries and ownership.
- [CLI reference](09-cli-reference.md) documents current commands and side effects.
- [Tools](05-tools.md) adds explicit local functions before external integrations.
- [Troubleshooting](13-troubleshooting.md) follows configuration and lifecycle
  checks without deleting or resetting existing state.

Installation guidance follows the [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).
Examples in this folder are checked against the repository's alpha3 APIs;
provider-backed examples require your own environment and are labeled live.

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
