---
title: Friday Chat CLI reference
description: Current process options, slash-command syntax, side effects and implementation limits.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: reference
---

# Friday Chat CLI reference

The maintained executable is **`friday-chat`**, from `friday-chat==0.1.0a3`.
Retired scripts under `tests/integration/memory` are not application entry points.
The historical `friday` entry point in the CLI component package is a placeholder.

## Process options

```bash
friday-chat --help
friday-chat --version
friday-chat --config demo.yaml --runtime fake
```

| Option | Behavior |
| --- | --- |
| `--config PATH` | Explicit Chat YAML; starts interactive chat |
| `--runtime fake\|real` | Defaults to fake; `FRIDAY_CHAT_RUNTIME`, when set, takes precedence |
| `--cli-config PATH` | Explicit terminal display YAML |
| `--version` | Print installed Chat version and exit |
| `--replay CSV_PATH` | Reprocess exported user turns in a new fake runtime and exit; this branch takes precedence over `--config` |
| `--replay-delay SECONDS` | Replay delay; validate syntax with CLI help |
| `--help` | Show installed option help |

No `init`, `doctor`, `mcp connect` or automatic first-run configuration command
is implemented. With no arguments the CLI shows help. Use [getting started](02-getting-started.md)
for a complete offline config and [desktop deployment](16-desktop-deployment.md)
for stable launch paths.

## Slash commands

`/help` renders help from the current registry. `/help <command>` shows focused
arguments; `/help` and `/exit` are registered directly, with `/quit` and `/q`
as exit aliases. `/cls` also has `/clearscreen` as an alias. Other commands below
come from alpha3's command metadata. Registered commands may require configured
services; appearance in help is not proof that a backend is real or available.

| Command | Category | Purpose |
| --- | --- | --- |
| `/ingest <path> [description] [--lines=N]` | files | Ingest file content into vector memory. |
| `/read <path> [--lines=N]` | files | Read a file with smart detection. |
| `/lifecycle [--execute] [--stats\|--flush\|--optimize]` | maintenance | Run or inspect memory lifecycle processing. |
| `/migrate [--force\|--execute\|--stats]` | maintenance | Migrate existing memories to lifecycle metadata. |
| `/reorganize [--execute] [mode/options]; /reorganize --recover <run-id> [--execute]` | maintenance | Preview or explicitly execute coordinated memory reorganization. |
| `/compact` | memory | Manually trigger context compaction. |
| `/context [--debug] [--file]` | memory | Show the assembled context payload. |
| `/debug` | memory | Show context assembly debug information. |
| `/debug-budget` | memory | Show token budget diagnostics. |
| `/debug-retrieval <query>` | memory | Show retrieval diagnostics for a query. |
| `/entities [nodes\|name]` | memory | List graph entities and relationships. |
| `/insights` | memory | List durable insights. |
| `/list-ingested` | memory | List ingested document memory records. |
| `/memory` | memory | Show typed memory, transcript, session, and context statistics. |
| `/meta` | memory | List active meta insights with lifecycle and provenance metadata. |
| `/prime` | memory | Load and show primed context. |
| `/prompt [--file]` | memory | Show the full formatted prompt sent to the LLM. |
| `/reset [graph\|vector\|episodic]` | memory | Reset one or more memory stores. |
| `/summaries` | memory | List turn summaries. |
| `/timing` | memory | Show timing breakdown for the last turn. |
| `/agent [name]` | orchestration | Show detailed agent information. |
| `/agents` | orchestration | List available agents. |
| `/delegate <agent> <task>` | orchestration | Delegate a task to another agent. |
| `/status` | orchestration | Show orchestrator status. |
| `/switch [agent]` | orchestration | Switch active agent or show current agent status. |
| `/inject-payload <payload>` | security | Inject a test payload for security validation. |
| `/security` | security | Show security status. |
| `/security-config <sensitivity\|action\|wrapping> <value>` | security | Update security configuration. |
| `/security-test [instruction\|delimiter\|jailbreak\|exfil\|all]` | security | Run local security sanitization tests. |
| `/clear` | session | Clear conversation history. |
| `/cls` | session | Clear the terminal through the display boundary. |
| `/history` | session | Show conversation history. |
| `/set <key> <value>` | session | Set a scoped variable. |
| `/vars` | session | Show scoped variables. |
| `/speech [on\|off\|config\|mode <live\|file>\|voice <name>\|provider <elevenlabs\|picovoice>]` | speech | Configure speech settings. |
| `/speech-test [once\|loop]` | speech | Run the speech validation harness. |
| `/clear-tools` | tools | Clear the pending manual set and restore automatic tool selection. |
| `/inject-tools <name> [name ...]` | tools | Set the exact manual tool schema set for subsequent turns. |
| `/recommend-tools <query>` | tools | Recommend tools for a query. |
| `/run-tool <name> [json]` | tools | Execute a named tool. |
| `/tool-budget` | tools | Inspect authoritative tool selection and schema-budget state. |
| `/tools [category]` | tools | List registered runtime tools and optionally filter by category. |
| `/export [csv\|jsonl\|markdown\|md\|training]` | transcript | Export persisted entries from the current session. |
| `/export-prompts [session_id]` | transcript | Export persisted captured prompts and responses for one session. |
| `/replay <csv_path> [delay_seconds]` | transcript | Replay a transcript CSV. |
| `/sessions` | transcript | List persisted transcript sessions with current and primed markers. |
| `/transcript [session_id\|export]` | transcript | Show a persisted current or selected transcript, or export all sessions. |
| `/workflow <list\|run\|status\|approve\|skip> [name] [key=value ...]` | workflow | List, run, or control workflows. |


## Session and inspection behavior

`/clear` clears current conversation history/session memory through the runtime;
it is not a wipe of every durable store. `/cls` only requests a terminal clear.
`/history` shows the current in-process history. `/vars` and `/set` operate on
command-context variables, not arbitrary persistent application configuration.

`/context` shows the last assembled payload and `/prompt` shows the formatted
model prompt when available. `--file` writes an export. These can contain
private text even when telemetry is disabled. `/debug` and `/timing` include
local execution summaries; `/debug-budget` currently reports configured context
window/output buffer rather than a full per-section accounting. `/tool-budget`
provides the authoritative tool-selection snapshot.

`/entities` supports `nodes` or a name, not the old `--limit` reference syntax.
There is no current `/facts` command. `/insights`, `/summaries`, `/meta` and
`/list-ingested` query their respective memory views; zero results may reflect
configuration, filtering or pending extraction, not lost persistence.

## Transcripts, exports and replay

`/sessions` lists persisted sessions with current/primed markers. `/transcript`
shows the current session; a session ID selects another persisted session.
`/transcript export` exports across sessions. `/export` supports CSV, JSONL,
Markdown (`md` alias) and training views; `/export-prompts` includes captured
raw prompts/responses when capture was enabled.

`/replay` is an **active, potentially destructive operation**. For a nonempty
CSV, it first dispatches `/reset` on the current runtime, then sends the saved
user messages through the normal turn processor. In real mode this can reset
stores/archive transcripts, call models/tools and write new memory. It does
not simply display saved assistant responses. Use only a disposable isolated
runtime and state copy. Process-level `--replay` instead creates its own fake
runtime. Neither path proves original external effects were reproduced, and
neither is a safe retry mechanism for uncertain mutations.

## Tool commands

`/tools` inspects registered tools; `/recommend-tools` recommends candidates.
`/inject-tools` sets the exact manual schema set for subsequent turns and
`/clear-tools` restores automatic selection. Inspect `/tool-budget` after changing
that set. A required/manual set can fail when names or budgets are invalid.

`/run-tool <name> [json]` **executes** the tool. The JSON is an object of arguments;
use a harmless tool and synthetic data for diagnostics. Filesystem, shell,
finance, web and integration tools can read/write data, use network services
or incur charges. The manual native path and model-driven MCP path do not
share every output-sanitization guarantee; see [security](security-configuration-guidelines.md).

## Commands that change memory

| Command | Important effect |
| --- | --- |
| `/reset [graph\|vector\|episodic]` | Resets selected storage through maintenance; with no selector it requests all stores, clears session/history/extraction and archives transcripts |
| `/compact` | Requests in-session compaction; can summarize/write memory and call configured models |
| `/lifecycle` | Default dry-run; requires configured lifecycle service; `--execute` requests mutation |
| `/migrate` | Default dry-run; `--execute` or legacy `--force` requests metadata migration |
| `/reorganize` | Preview coordinated maintenance; exact `--execute` requests mutation subject to capabilities/preflight |
| `/ingest` | Reads source content and writes vector memory; may invoke configured processing services |
| `/replay` | Resets the active runtime for a nonempty CSV and reprocesses user turns, including real calls when configured |

These are not read-only troubleshooting shortcuts. Preserve a verified backup
and use the specific operation contract before modifying existing data.

Reorganization accepts at most one mode flag: `--backup`, `--dedupe`,
`--analyze`, `--prune`, `--synthesize` or `--verify`. Full-mode flags include
`--skip-synthesis`, `--skip-verify`, `--skip-lifecycle` and `--force-reembed`.
`--recover <run-id>` selects a recorded recovery bundle, not arbitrary file
paths. The parser rejects incompatible combinations; `/help reorganize` and
the command's usage output control. Current adapter capability checks may
refuse execution, and `--analyze --execute` is rejected.

## Orchestration and workflow limits

In alpha3, Chat uses a deterministic `FakeOrchestrator` **even with `--runtime
real`**. Its `friday`, `researcher` and `coder` roles are routing fixtures.
`/delegate`, `/switch` and `@agent message` do not construct independent
specialist model agents. Framework-level real orchestration is described in
[multi-agent operation](07-multi-agent.md).

Fake Chat uses a fake workflow engine. Real Chat uses the framework's flat
workflow engine with the same deterministic agent adapter; it does not execute
canonical bundles through `/workflow run`. `/workflow approve` and `skip` act
on the active execution's task gate. See [workflows](08-workflows.md).

## Speech and security commands

Chat currently uses a deterministic speech adapter even in real mode. Both
`/speech-test once` and `loop` perform one adapter call, not a continuous audio
harness. Use the standalone Speech service/harness for provider-backed audio
with explicitly provisioned credentials/devices; see [speech](speech.md).

The Chat `/security-test` command exercises deterministic sample handling,
not a comprehensive attack test. Its runtime update vocabulary differs from
Core `SanitizationConfig`; an accepted `/security-config` update does not
prove every tool path adopted it. `/inject-payload` stages a synthetic payload
for tool-result testing and should be used only in a disposable session.
See [security configuration](security-configuration-guidelines.md).

## Implementation references

- [Process CLI](../../packages/friday-chat/src/friday_chat/cli.py)
- [Command metadata and handlers](../../packages/friday-chat/src/friday_chat/commands/registry.py)
- [Transcript handlers](../../packages/friday-chat/src/friday_chat/commands/transcript.py)
- [Tool command selection](../../packages/friday-chat/src/friday_chat/commands/tools.py)

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
