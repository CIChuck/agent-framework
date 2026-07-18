# FridayV2 Parity Matrix

This matrix tracks implementation parity between the prototype CLI and
FridayV2. The prototype source is `tests/integration/memory/friday.py`; the
target package is `packages/friday-chat`.

Status values:

- `not started`
- `in progress`
- `implemented`
- `tested`
- `verified`
- `intentionally changed`
- `deprecated`
- `deferred`

No row should be removed. If FridayV2 intentionally changes behavior, keep the
row and document the decision.

Compatibility test requirements are defined in
`docs/planning/build-plans/friday-chat-v2-compatibility-testing-protocol.md`.
Framework package change requests discovered during implementation are tracked
in `docs/planning/build-plans/friday-chat-v2-framework-upgrade-log.md`.
Command and subsystem business rules are defined in
`docs/planning/build-plans/friday-chat-v2-behavioral-contracts.md`.

## Target Module Map

| Target area | Proposed module |
| --- | --- |
| App lifecycle | `friday_chat.app`, `friday_chat.cli` |
| Runtime wiring | `friday_chat.runtime`, `friday_runtime` |
| Typed config | `friday_chat.config` |
| Session state | `friday_chat.session` |
| Turn processing | `friday_chat.turns.processor` |
| Streaming | `friday_chat.turns.streaming` |
| Tool loop | `friday_chat.tools.loop` |
| Tool registry loading | `friday_chat.tools.registry` or `friday_runtime.tool_loading` |
| Commands | `friday_chat.commands.*` |
| Background jobs | `friday_chat.background` |
| Shell service | `friday_chat.shell` |
| Replay | `friday_chat.replay` |
| Export helpers | `friday_chat.exports` |
| Speech integration | `friday_chat.speech` |
| Security controls | `friday_chat.security` |
| Tests | `packages/friday-chat/tests_chat` |
| Compatibility tests | `packages/friday-chat/tests_chat/compat` |
| Behavioral contracts | `docs/planning/build-plans/friday-chat-v2-behavioral-contracts.md` |
| Framework upgrade log | `docs/planning/build-plans/friday-chat-v2-framework-upgrade-log.md` |

## Core App And Runtime

| Feature | Prototype evidence | Target | Acceptance criteria | Status |
| --- | --- | --- | --- | --- |
| CLI entry point | `friday.py:7071` | `friday_chat.cli` | `uv run friday-chat --config ...` starts app with typed config validation | not started |
| Config loading | `friday.py:7102` | `friday_chat.config` | YAML loads into typed config; missing required sections fail before services start | not started |
| Secret handling | `config.yaml:65`, `config.yaml:101` | `friday_chat.config` | Example config has no literal provider keys; env interpolation is tested | not started |
| Friday-py config compatibility | `tests/integration/memory/config.yaml`, `friday.py:7121` | `friday_chat.config` | FridayV2 accepts the current config shape and normalizes it into typed models without requiring users to restructure config | not started |
| Friday-py config section coverage | `tests/integration/memory/config.yaml` | `friday_chat.config` | Top-level sections `logging`, `llm`, `extraction`, `embedding`, `memory`, `transcript`, `chat`, `maintenance`, `lifecycle`, `smart_file`, `tools`, `web`, `langfuse`, `finance`, `security`, `session`, and `speech` are accepted and traced | not started |
| High-value nested config compatibility | `tests/integration/memory/config.yaml` | `friday_chat.config`, `friday_chat.runtime` | Nested sections `memory.retrieval`, `memory.priming`, `memory.cache`, `memory.supporting_context`, `memory.passage_router`, `memory.query_relevance_filter`, `memory.compaction`, `maintenance.llm`, `maintenance.prompts`, `tools.registry`, `tools.context`, `smart_file.llm`, `web.reader`, `security.sanitization`, and `speech.selection` are accepted and traced | not started |
| Config traceability | `friday.py:7121`, `friday.py:7203`, `friday.py:7400`, `friday.py:7817` | `friday_chat.config`, `friday_chat.runtime` | Every supported top-level and nested config key maps to a runtime consumer, compatibility handler, or explicit deprecation record | not started |
| Runtime composition | `friday.py:7530` | `friday_chat.runtime` | LLM, embedding, stores, transcript, context assembler, extractor, tools, and maintenance services are created through factory methods | not started |
| Interactive loop | `friday.py:7968` | `friday_chat.app` | Empty input skipped, commands dispatched, chat messages processed, EOF and keyboard interrupt exit cleanly | not started |
| Shutdown | `friday.py:8003` | `friday_chat.app`, `friday_chat.background` | Exit maintenance runs as configured; transcript finalized; tracked tasks cancelled or awaited | not started |

## Turn Processing

| Feature | Prototype evidence | Target | Acceptance criteria | Status |
| --- | --- | --- | --- | --- |
| Lazy session initialization | `friday.py:6020` | `friday_chat.session` | First turn initializes session state and scoped defaults | not started |
| Dynamic context budget | `friday.py:6028` | `friday_chat.turns.processor` | Tool definitions are included in budget calculation | not started |
| Context assembly | `friday.py:6049` | `friday_chat.turns.processor` | Assembles context from memory controller using query, state, and budget limit | not started |
| Prompt formatting | `friday.py:6059` | `friday_chat.turns.processor` | Formats prompt with current user query, context format, and turn count | not started |
| Timing metrics | `friday.py:6076` | `friday_chat.turns.metrics` | Timing data supports `/timing` and tests can assert recorded keys | not started |
| Streaming response | `friday.py:6310` | `friday_chat.turns.streaming` | No-tool turns stream output, support pre-first-chunk cancellation, and return metrics | not started |
| Tool response loop | `friday.py:6567` | `friday_chat.tools.loop` | Tool-enabled turns use non-streaming loop with max iterations and failure breaker | not started |
| Turn persistence | `friday.py:6180` | `friday_chat.turns.processor` | Persisted turn includes messages, tool calls/results, timing, token data, model, temperature, raw prompt/response when enabled | not started |
| Error handling | `friday.py:6284` | `friday_chat.turns.processor` | Timeout, retry exhausted, circuit breaker, and cancellation produce user-facing responses and do not corrupt state | not started |

## Commands

| Feature | Prototype evidence | Target | Acceptance criteria | Status |
| --- | --- | --- | --- | --- |
| Single command registry | `friday.py:429`, `friday.py:1111` | `friday_chat.commands` | FridayV2 has no legacy fallback router; all commands register through one registry | not started |
| `/exit`, `/quit`, `/q` | `friday.py:437` | `commands.session` | Exit command returns app-level exit signal | not started |
| `/clear` | `friday.py:446` | `commands.session` | Clears turn IDs, pending extraction, last payload, and turn count | not started |
| `/cls`, `/clearscreen` | `friday.py:453` | `commands.session` | Clears terminal through display abstraction | not started |
| `/help`, `/help <command>` | `friday.py:1087`, `friday.py:5642` | `commands.help` | Lists grouped commands and detailed argument help | not started |
| `/history` | `friday.py:462` | `commands.memory` | Shows conversation history with timestamps and tool calls | not started |
| `/memory` | `friday.py:469` | `commands.memory` | Shows episodic, vector, graph, transcript, and lifecycle stats where available | not started |
| `/context [--debug] [--file]` | `friday.py:476` | `commands.memory` | Shows assembled context, optional token diagnostics, and optional export | not started |
| `/prompt [--file]` | `friday.py:497` | `commands.memory` | Shows full formatted prompt and optional export | not started |
| `/prime` | `friday.py:511` | `commands.memory` | Loads and displays primed context before first turn | not started |
| `/debug` | `friday.py:518` | `commands.memory` | Shows context assembly debug details | not started |
| `/debug-budget` | `friday.py:525` | `commands.memory` | Shows context/window budget diagnostics | not started |
| `/timing` | `friday.py:532` | `commands.memory` | Shows last-turn timing breakdown | not started |
| `/debug-retrieval <query>` | `friday.py:1150` | `commands.memory` | Shows retrieval diagnostics for query | not started |
| `/list-ingested` | `friday.py:1154` | `commands.files` | Lists ingested file/source records | not started |
| `/entities`, `/entities nodes`, `/entities <name>` | `friday.py:539` | `commands.memory` | Supports entity list, node details, and lookup views | not started |
| `/insights` | `friday.py:564` | `commands.memory` | Lists insight records with structured metadata | not started |
| `/summaries` | `friday.py:571` | `commands.memory` | Lists summary records | not started |
| `/meta` | `friday.py:578` | `commands.memory` | Lists meta insights | not started |
| `/vars` | `friday.py:585` | `commands.memory` | Shows scoped variables | not started |
| `/set <key> <value>` | `friday.py:1087` | `commands.memory` | Sets scoped variable with validation | not started |
| `/sessions` | `friday.py:593` | `commands.transcript` | Lists transcript sessions | not started |
| `/transcript [session_id]` | `friday.py:600` | `commands.transcript` | Shows current or selected transcript; supports export subcommand behavior | not started |
| `/export [format]` | `friday.py:616` | `commands.transcript` | Supports csv, jsonl, markdown, and training exports | not started |
| `/export-prompts [session_id]` | `friday.py:634` | `commands.transcript` | Exports raw context log prompts/responses to JSON | not started |
| `/reset [store]` | `friday.py:651` | `commands.maintenance` | Resets all memory or graph/vector/episodic store only | not started |
| `/reorganize ...` | `friday.py:671`, `friday.py:3361` | `commands.maintenance` | Supports all prototype flags, including `--force-reembed`, and dry-run default | not started |
| `/lifecycle ...` | `friday.py:734` | `commands.maintenance` | Supports execute, stats, optimize, and flush modes | not started |
| `/migrate ...` | `friday.py:767`, `friday.py:3855` | `commands.maintenance` | Resolves prototype mismatch: registry advertises `--execute`/`--stats`, handler implements `--force`; FridayV2 supports compatibility aliases or documents an intentional change | not started |
| `/compact` | `friday.py:794` | `commands.maintenance` | Runs manual compaction and reports result | not started |
| `/replay <csv> [delay]` | `friday.py:803`, `friday.py:3124` | `friday_chat.replay`, `commands.testing` | Resets memory, loads CSV turns in order, processes through normal pipeline | not started |
| `/tools [category]` | `friday.py:827` | `commands.tools` | Lists tools and filters by category | not started |
| `/run-tool <name> [json]` | `friday.py:841`, `friday.py:4117` | `commands.tools` | Validates JSON params and plain-text param mapping, executes tool, sanitizes output, records security stats | not started |
| `/inject-tools <names>` | `friday.py:854`, `friday.py:4231` | `commands.tools` | Sets active tool schemas for chat context and resolves whitespace-vs-comma argument mismatch | not started |
| `/clear-tools` | `friday.py:868` | `commands.tools` | Clears active tool schemas | not started |
| `/recommend-tools <query>` | `friday.py:875` | `commands.tools` | Shows recommended tools for query | not started |
| `/tool-budget` | `friday.py:889` | `commands.tools` | Shows tool token budget impact | not started |
| `/security` | `friday.py:897` | `commands.security` | Shows security config and scan/detection stats | not started |
| `/security-test [type]` | `friday.py:904` | `commands.security` | Runs injection detection probes | not started |
| `/security-config <setting> <value>` | `friday.py:921` | `commands.security` | Updates security config with rollback on invalid values | not started |
| `/inject-payload <payload>` | `friday.py:936` | `commands.security` | Appends payload to next tool result for local testing | not started |
| `/speech ...` | `friday.py:951` | `commands.speech` | Supports on/off/mode/voice/provider/config | not started |
| `/speech-test [once or loop]` | `friday.py:966` | `commands.speech` | Runs cancellable speech harness | not started |
| `/switch [agent]` | `friday.py:979` | `commands.orchestration` | Shows or switches active agent | not started |
| `/agents` | `friday.py:993` | `commands.orchestration` | Lists agents, capabilities, active marker, and cached state | not started |
| `/agent [name]` | `friday.py:1000` | `commands.orchestration` | Shows selected or active agent details | not started |
| `/delegate <agent> <task>` | `friday.py:1014` | `commands.orchestration` | Delegates task and restores previous active agent | not started |
| `/status` | `friday.py:1027` | `commands.orchestration` | Shows orchestrator status | not started |
| `@agent_name <message>` | `friday.py:1114`, `friday.py:5399` | `commands.orchestration` | Routes message through orchestrator direct routing | not started |
| `/workflow ...` | `friday.py:1034`, `friday.py:5066` | `commands.workflow` | Supports list, run, status, approve, and skip | not started |
| `/read <path> [--lines N]` | `friday.py:1057`, `friday.py:5423` | `commands.files` | Reads txt/md/yaml/json/py/csv/tsv/pdf/docx/xlsx through smart detection with optional line limit | not started |
| `/ingest <path> [description]` | `friday.py:1071` | `commands.files` | Ingests file content into vector memory with metadata | not started |
| `!<command>` | `friday.py:7000`, `friday.py:7973` | `friday_chat.shell` | Disabled by default or config-gated; tests cover disabled, enabled, timeout, stderr, nonzero exit | not started |

## Subsystems

| Feature | Prototype evidence | Target | Acceptance criteria | Status |
| --- | --- | --- | --- | --- |
| Tool registry config loading | `friday.py:7175` | `friday_chat.tools.registry` | Loads configured tools without mutable module-global lookup | not started |
| Auto tool context injection | `friday.py:7817` | `friday_chat.runtime` | Honors `tools.context.include_in_context` by activating all loaded tool schemas at startup | not started |
| Passage router setup | `friday.py:7400` | `friday_chat.runtime` | Optional passage router LLM/config is constructed with typed config and graceful fallback | not started |
| Maintenance LLM roles | `friday.py:7481` | `friday_chat.runtime` | Optional synthesizer, classifier, researcher, and judge LLMs are constructed with fallback reporting | not started |
| Session maintenance config | `config.yaml`, `friday.py:8003` | `friday_chat.config`, `friday_chat.app` | `session.flush_on_exit`, `session.lifecycle_on_exit`, `session.reorganize_on_exit`, and `session.reorganize_mode` control exit maintenance | not started |
| Text tool-call fallback | `friday.py:6674` | `friday_chat.tools.loop` | Either supported with tests or intentionally changed/deprecated | not started |
| Tool output sanitization | `friday.py:6830` | `friday_chat.security`, `friday_chat.tools.loop` | Separate sanitized content for LLM context and memory storage | not started |
| Tool output lifecycle tracking | `friday.py:6921` | `friday_chat.tools.lifecycle` | Tracks large outputs and decays them after configured inactivity | not started |
| Tool output vector ingestion | `friday.py:6935` | `friday_chat.tools.ingestion` | Ingests qualifying outputs with source path and security metadata | not started |
| Speech prompt injection | `friday.py:4400` | `friday_chat.speech` | Adds speech instructions only when enabled | not started |
| Streaming speech trigger | `friday.py:6355` | `friday_chat.speech` | Live speech starts from selected snippet and avoids double playback | not started |
| Background extraction | `friday.py:5800`, `friday.py:6250` | `friday_chat.background` | Buffers turns and extracts on configured interval; exit flush is tested | not started |
| Incremental graph maintenance | `friday.py:6230`, `friday.py:7857` | `friday_chat.background` | Runs on schedule through supervised task manager | not started |
| Budget-aware compaction | `friday.py:6237`, `friday.py:7870` | `friday_chat.background` | Triggers on monitor threshold and gates next turn when in progress | not started |
| Exit maintenance | `friday.py:5832` | `friday_chat.maintenance` | Flushes extraction, access buffer, lifecycle, and optional reorganization in order | not started |
| Workflow loader setup | `friday.py:7824` | `friday_chat.runtime` | Workflow directory is configurable, not hard-coded to prototype path | not started |
| Replay CLI mode | `friday.py:7924` | `friday_chat.cli`, `friday_chat.replay` | CLI replay exits after processing and reports summary | not started |
| Transcript session finalization | `friday.py:8026` | `friday_chat.app` | Finalizes transcript even after loop exceptions | not started |

## Required Tests

| Test area | Target tests | Status |
| --- | --- | --- |
| Config validation | Missing llm config, Friday-py config compatibility, env-secret interpolation, invalid speech/security config, unknown/deprecated key reporting | not started |
| Config traceability | Every supported config key has a mapped consumer, compatibility handler, or explicit deprecation record | not started |
| Framework freeze | No FridayV2 parity implementation test mutates existing framework packages; upgrade needs are logged instead | not started |
| Contract coverage | Every implemented parity row has a behavioral contract or explicit simple-command exemption in `parity_overrides.yaml` | not started |
| Command registry | Every command is registered exactly once and appears in help | not started |
| Command parsing | Flags, positional args, unknown commands, detailed help, `/migrate` compatibility aliases, and `/inject-tools` name separators | not started |
| Turn processor | No-tool streaming path with fake LLM and fake memory controller | not started |
| Tool loop | API tool calls, text tool calls, tool errors, circuit breaker, truncation, pruning | not started |
| Persistence | Turn saved with transcript/context-log metadata | not started |
| Background tasks | Extraction flush, task failure reporting, shutdown cancellation/await | not started |
| Shell service | Disabled default, enabled execution, timeout, nonzero, stderr | not started |
| Replay | CSV order, reset-before-replay, normal pipeline invocation, delay handling | not started |
| Security | Sanitization stats, runtime config update rollback, payload injection | not started |
| Speech | Config updates, prompt snippet, tag stripping, cancellation | not started |
| Orchestration | Switch, delegate, at-routing, status with fake orchestrator | not started |
| Workflow | List, run with inputs, pending approval, approve, skip | not started |
| File commands | Reader dispatch for all supported formats, line limit, ingest metadata | not started |
