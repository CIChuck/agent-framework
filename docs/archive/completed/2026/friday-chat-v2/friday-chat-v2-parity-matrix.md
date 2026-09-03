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
`docs/archive/completed/2026/friday-chat-v2/friday-chat-v2-compatibility-testing-protocol.md`.
Framework package change requests discovered during implementation are tracked
in `docs/planning/backlog/friday-chat-framework-followups/upgrade-log.md`.
Command and subsystem business rules are defined in
`docs/archive/completed/2026/friday-chat-v2/friday-chat-v2-behavioral-contracts.md`.

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
| Behavioral contracts | `docs/archive/completed/2026/friday-chat-v2/friday-chat-v2-behavioral-contracts.md` |
| Framework upgrade log | `docs/planning/backlog/friday-chat-framework-followups/upgrade-log.md` |

## Core App And Runtime

| Feature | Prototype evidence | Target | Acceptance criteria | Status |
| --- | --- | --- | --- | --- |
| CLI entry point | `friday.py:7071` | `friday_chat.cli`, package console script | Installed `friday-chat --config ...` starts app with typed config validation; `uv run friday-chat ...` remains only a development convenience | tested |
| Config loading | `friday.py:7102` | `friday_chat.config` | YAML loads into typed config; missing required sections fail before services start | tested |
| Secret handling | `config.yaml:65`, `config.yaml:101` | `friday_chat.config` | Example config has no literal provider keys; env interpolation is tested | tested |
| Friday-py config compatibility | `tests/integration/memory/config.yaml`, `friday.py:7121` | `friday_chat.config`, `config.example.yaml` | FridayV2 accepts the current config shape and normalizes it into typed models without requiring users to restructure config; example and fixture preserve all 406 active YAML option paths from the Friday-py reference config | tested |
| Friday-py config section coverage | `tests/integration/memory/config.yaml` | `friday_chat.config` | Top-level sections `logging`, `llm`, `extraction`, `embedding`, `memory`, `transcript`, `chat`, `maintenance`, `lifecycle`, `smart_file`, `tools`, `web`, `langfuse`, `finance`, `security`, `session`, and `speech` are accepted and traced | tested |
| CLI display config compatibility | `tests/integration/memory/cli-config.yaml`, `friday.py:7102` | `friday_chat.display`, `friday_chat.cli`, `cli-config.example.yaml` | FridayV2 auto-loads `cli-config.yaml` next to the selected `config.yaml`, supports an explicit override, and applies configured theme, icons, prompt styles, spinner settings, and defaults | tested |
| Startup banner and greeting | `friday.py:7355` | `friday_chat.display`, `friday_chat.app` | FridayV2 startup renders the configured greeting/banner behavior before entering the interactive loop | tested |
| Heartbeat boundary and configured messages | `friday.py:6325`, `friday.py:6630`, `tests/integration/memory/cli-config.yaml` | `friday_chat.display`, `friday_chat.turns.processor`, `friday_chat.tools.loop` | FridayV2 has a display-owned heartbeat boundary, starts thinking feedback while waiting for model output, stops on completion/failure cleanup, and selects tool-processing feedback for later tool-loop iterations | tested |
| Streaming first-chunk heartbeat parity | `friday.py:6376`, `friday.py:6413`, `friday.py:6440` | `friday_chat.display`, `friday_chat.turns.processor`, `friday_chat.app` | FridayV2 stops heartbeat before emitting the first streamed no-tool response chunk, keeps tool turns on the non-streaming tool loop, and streams app output through chunk-aware sinks | tested |
| Startup system prompt initialization | `friday.py:7542`, `friday.py:7762`, `friday.py:7782`, `friday.py:4400` | `friday_chat.config`, `friday_chat.runtime`, `friday_chat.app`, `friday_chat.turns.processor` | Command-line startup initializes the effective prompt from `chat.system_prompt`, uses it for session metadata, turn processing, context-budget calculation, `/prompt`, and `/debug`, and applies speech prompt augmentation only while speech is enabled | tested |
| High-value nested config compatibility | `tests/integration/memory/config.yaml` | `friday_chat.config`, `friday_chat.runtime` | Nested sections `memory.retrieval`, `memory.priming`, `memory.cache`, `memory.supporting_context`, `memory.passage_router`, `memory.query_relevance_filter`, `memory.compaction`, `maintenance.llm`, `maintenance.prompts`, `tools.registry`, `tools.context`, `smart_file.llm`, `web.reader`, `security.sanitization`, and `speech.selection` are accepted and traced | tested |
| Config traceability | `friday.py:7121`, `friday.py:7203`, `friday.py:7400`, `friday.py:7817` | `friday_chat.config`, `friday_chat.runtime` | Every supported top-level and nested config key maps to a runtime consumer, compatibility handler, or explicit deprecation record | tested |
| Runtime composition | `friday.py:7530` | `friday_chat.runtime` | LLM, embedding, stores, transcript, context assembler, extractor, tools, and maintenance services are created through factory methods | tested |
| Per-invocation session identity | `friday.py:6020`, `friday.py:7530` | `friday_chat.session`, `friday_chat.runtime`, `friday_chat.app`, `friday_chat.replay` | One immutable `session_<unique-id>` identity is generated per production invocation and propagated through runtime, persistence, app, command, maintenance, and replay boundaries; injected identity mismatch fails explicitly | verified |
| Interactive loop | `friday.py:7968` | `friday_chat.app` | Empty input skipped, commands dispatched, chat messages processed, EOF and keyboard interrupt exit cleanly | tested |
| Shutdown | `friday.py:8003` | `friday_chat.app`, `friday_chat.background` | Exit maintenance runs as configured; transcript finalized; tracked tasks cancelled or awaited | tested |

## Turn Processing

| Feature | Prototype evidence | Target | Acceptance criteria | Status |
| --- | --- | --- | --- | --- |
| Lazy session initialization | `friday.py:6020` | `friday_chat.session` | First turn initializes session state and scoped defaults | tested |
| Dynamic context budget | `friday.py:6028` | `friday_chat.turns.processor` | Tool definitions are included in budget calculation | tested |
| Context assembly | `friday.py:6049` | `friday_chat.turns.processor` | Assembles context from memory controller using query, state, and budget limit | tested |
| Prompt formatting | `friday.py:6059` | `friday_chat.turns.processor` | Formats prompt with current user query, context format, and turn count | tested |
| Actual prompt delivery | `friday.py:6062` | `friday_chat.turns.processor` | The exact message payload sent to the LLM includes effective system prompt, assembled supporting context, history, tools, current query, and turn count; raw prompt capture records the same payload | tested |
| Current-session history continuity | `friday.py:6050`, `friday.py:6062`, `friday.py:6278` | `friday_chat.turns.processor`, `friday_chat.app`, `friday_chat.runtime` | After multiple turns, later prompts include prior current-session turns and the model cannot incorrectly see the fourth or fifth turn as the first turn | tested |
| Timing metrics | `friday.py:6076` | `friday_chat.turns.metrics` | Timing data supports `/timing` and tests can assert recorded keys | tested |
| Streaming response | `friday.py:6310` | `friday_chat.turns.streaming` | No-tool turns stream output, support pre-first-chunk cancellation, and return metrics | tested |
| Tool response loop | `friday.py:6567` | `friday_chat.tools.loop` | Tool-enabled turns use non-streaming loop with max iterations and failure breaker | tested |
| End-to-end conversation tool execution | `friday.py:6567`, `friday.py:6674`, `friday.py:6763`, `friday.py:6830` | `friday_chat.turns.processor`, `friday_chat.tools.loop`, `friday_chat.runtime` | Normal conversation turns preserve provider tool calls, execute configured tools, feed sanitized tool results back to the model, and never collapse tool-call-only responses into empty output | tested |
| Turn persistence | `friday.py:6180` | `friday_chat.turns.processor` | Persisted turn includes messages, tool calls/results, timing, token data, model, temperature, raw prompt/response when enabled | tested |
| Error handling | `friday.py:6284` | `friday_chat.turns.processor` | Timeout, retry exhausted, circuit breaker, and cancellation produce user-facing responses and do not corrupt state | tested |

## Commands

| Feature | Prototype evidence | Target | Acceptance criteria | Status |
| --- | --- | --- | --- | --- |
| Single command registry | `friday.py:429`, `friday.py:1111` | `friday_chat.commands` | FridayV2 has no legacy fallback router; all commands register through one registry | tested |
| `/exit`, `/quit`, `/q` | `friday.py:437` | `commands.session` | Exit command returns app-level exit signal | tested |
| `/clear` | `friday.py:446` | `commands.session` | Clears turn IDs, pending extraction, last payload, and turn count | tested |
| `/cls`, `/clearscreen` | `friday.py:453` | `commands.session` | Returns one typed clear effect; the app invokes the production display boundary exactly once with no false replacement output, and supported-platform PTY coverage observes terminal clear/home sequences | verified |
| `/help`, `/help <command>` | `friday.py:1087`, `friday.py:5642` | `commands.help` | Lists grouped commands and detailed argument help | tested |
| `/history` | `friday.py:462` | `commands.memory` | Shows conversation history with timestamps and tool calls | tested |
| `/memory` | `friday.py:469` | `commands.memory` | Shows typed episodic, vector, graph, transcript, lifecycle, priming, session, and context statistics; unavailable/unconfigured sources are not rendered as fabricated zeroes | verified |
| `/context [--debug] [--file]` | `friday.py:476` | `commands.memory` | Shows assembled context, optional token diagnostics, and optional export | tested |
| `/prompt [--file]` | `friday.py:497` | `commands.memory` | Shows full formatted prompt and optional export | tested |
| `/prime` | `friday.py:511` | `commands.memory` | Loads and displays primed context before first turn | tested |
| `/debug` | `friday.py:518` | `commands.memory` | Shows context assembly debug details | tested |
| `/debug-budget` | `friday.py:525` | `commands.memory` | Shows context/window budget diagnostics | tested |
| `/timing` | `friday.py:532` | `commands.memory` | Shows last-turn timing breakdown | tested |
| `/debug-retrieval <query>` | `friday.py:1150` | `commands.memory` | Shows retrieval diagnostics for query | tested |
| `/list-ingested` | `friday.py:1154` | `commands.files` | Lists ingested file/source records | tested |
| `/entities`, `/entities nodes`, `/entities <name>` | `friday.py:539` | `commands.memory` | Supports entity list, node details, and lookup views | tested |
| `/insights` | `friday.py:564` | `commands.memory` | Lists insight records with structured metadata | tested |
| `/summaries` | `friday.py:571` | `commands.memory` | Lists summary records | tested |
| `/meta` | `friday.py:578` | `commands.memory` | Lists active short- and long-term meta insights through public memory APIs with provenance and partial-failure warnings; excludes decayed records and performs no synthesis or reorganization | verified |
| `/vars` | `friday.py:585` | `commands.memory` | Shows scoped variables | tested |
| `/set <key> <value>` | `friday.py:1087` | `commands.memory` | Sets scoped variable with validation | tested |
| `/sessions` | `friday.py:593` | `commands.transcript` | Lists persisted sessions through the public transcript query API with current and primed markers | verified |
| `/transcript [session_id]` | `friday.py:600` | `commands.transcript` | Queries persisted current or safely bound selected-session entries; all-session export uses deterministic public queries beneath the configured export root | verified |
| `/export [format]` | `friday.py:616` | `commands.transcript` | Exports persisted current-session entries as csv, jsonl, markdown, or training data beneath the configured export root | verified |
| `/export-prompts [session_id]` | `friday.py:634` | `commands.transcript` | Exports persisted raw context-log records for the current or safely bound selected session, with honest capture-disabled guidance | verified |
| `/reset [store]` | `friday.py:651` | `commands.maintenance` | Resets all memory or graph/vector/episodic store only | tested |
| `/reorganize ...` | `friday.py:671`, `friday.py:3361` | `commands.maintenance` | Supports all prototype flags, including `--force-reembed`, and dry-run default | tested |
| `/lifecycle ...` | `friday.py:734` | `commands.maintenance` | Supports execute, stats, optimize, and flush modes | tested |
| `/migrate ...` | `friday.py:767`, `friday.py:3855` | `commands.maintenance` | Resolves prototype mismatch: registry advertises `--execute`/`--stats`, handler implements `--force`; FridayV2 supports compatibility aliases or documents an intentional change | tested |
| `/compact` | `friday.py:794` | `commands.maintenance` | Runs manual compaction and reports result | tested |
| `/replay <csv> [delay]` | `friday.py:803`, `friday.py:3124` | `friday_chat.replay`, `commands.testing` | Resets memory, loads CSV turns in order, processes through normal pipeline | tested |
| `/tools [category]` | `friday.py:827` | `commands.tools` | Lists registered runtime tool definitions and filters by category | verified |
| `/run-tool <name> [json]` | `friday.py:841`, `friday.py:4117` | `commands.tools` | Validates JSON params and plain-text param mapping, executes tool, sanitizes output, records security stats | tested |
| `/inject-tools <names>` | `friday.py:854`, `friday.py:4231` | `commands.tools` | Atomically sets an exact persistent manual schema selection after canonical name, count, and token-budget validation; supports tested whitespace/comma separators | verified |
| `/clear-tools` | `friday.py:868` | `commands.tools` | Clears pending manual selection and restores automatic per-turn selection without disabling the registry | verified |
| `/recommend-tools <query>` | `friday.py:875` | `commands.tools` | Shows recommended tools for query | tested |
| `/tool-budget` | `friday.py:889` | `commands.tools` | Reports authoritative automatic/manual/last-completed/executed selection state and the same canonical schema-token snapshot consumed by turn budgeting and the model payload | verified |
| `/security` | `friday.py:897` | `commands.security` | Shows security config and scan/detection stats | tested |
| `/security-test [type]` | `friday.py:904` | `commands.security` | Runs injection detection probes | tested |
| `/security-config <setting> <value>` | `friday.py:921` | `commands.security` | Updates security config with rollback on invalid values | tested |
| `/inject-payload <payload>` | `friday.py:936` | `commands.security` | Appends payload to next tool result for local testing | tested |
| `/speech ...` | `friday.py:951` | `commands.speech` | Supports on/off/mode/voice/provider/config | tested |
| `/speech-test [once or loop]` | `friday.py:966` | `commands.speech` | Runs cancellable speech harness | tested |
| `/switch [agent]` | `friday.py:979` | `commands.orchestration` | Shows or switches active agent | tested |
| `/agents` | `friday.py:993` | `commands.orchestration` | Lists agents, capabilities, active marker, and cached state | tested |
| `/agent [name]` | `friday.py:1000` | `commands.orchestration` | Shows selected or active agent details | tested |
| `/delegate <agent> <task>` | `friday.py:1014` | `commands.orchestration` | Delegates task and restores previous active agent | tested |
| `/status` | `friday.py:1027` | `commands.orchestration` | Shows orchestrator status | tested |
| `@agent_name <message>` | `friday.py:1114`, `friday.py:5399` | `commands.orchestration` | Routes message through orchestrator direct routing | tested |
| `/workflow ...` | `friday.py:1034`, `friday.py:5066` | `commands.workflow` | Supports list, run, status, approve, and skip | tested |
| `/read <path> [--lines N]` | `friday.py:1057`, `friday.py:5423` | `commands.files` | Reads txt/md/yaml/json/py/csv/tsv/pdf/docx/xlsx through smart detection with optional line limit | tested |
| `/ingest <path> [description]` | `friday.py:1071` | `commands.files` | Ingests file content into vector memory with metadata | tested |
| `!<command>` | `friday.py:7000`, `friday.py:7973` | `friday_chat.shell` | Disabled by default or config-gated; tests cover disabled, enabled, timeout, stderr, nonzero exit | tested |

## Subsystems

| Feature | Prototype evidence | Target | Acceptance criteria | Status |
| --- | --- | --- | --- | --- |
| Tool registry config loading | `friday.py:7175` | `friday_chat.tools.registry` | Loads configured tools without mutable module-global lookup | tested |
| Auto tool context injection | `friday.py:7817` | `friday_chat.runtime`, `friday_chat.tools.selection`, `friday_chat.turns.processor` | Intentionally changes startup-wide activation into bounded query-aware automatic selection or persistent validated manual selection when `tools.context.include_in_context` is enabled; one immutable canonical schema snapshot feeds context, budget telemetry, and the model call | verified |
| Passage router setup | `friday.py:7400` | `friday_chat.runtime` | Optional passage router LLM/config is constructed from `memory.passage_router` and applied to recalled passages with graceful fallback | tested |
| Maintenance LLM roles | `friday.py:7481` | `friday_chat.runtime` | Optional synthesizer, classifier, researcher, and judge LLMs are constructed with fallback reporting | tested |
| Session maintenance config | `config.yaml`, `friday.py:8003` | `friday_chat.config`, `friday_chat.app` | `session.flush_on_exit`, `session.lifecycle_on_exit`, `session.reorganize_on_exit`, and `session.reorganize_mode` control exit maintenance | tested |
| Text tool-call fallback | `friday.py:6674` | `friday_chat.tools.loop` | Either supported with tests or intentionally changed/deprecated | intentionally changed |
| Tool output sanitization | `friday.py:6830` | `friday_chat.security`, `friday_chat.tools.loop` | Separate sanitized content for LLM context and memory storage | tested |
| Tool output lifecycle tracking | `friday.py:6921` | `friday_chat.tools.lifecycle` | Tracks large outputs and decays them after configured inactivity | tested |
| Tool output vector ingestion | `friday.py:6935` | `friday_chat.tools.ingestion` | Ingests qualifying outputs with source path and security metadata | tested |
| Speech prompt injection | `friday.py:4400` | `friday_chat.speech` | Adds speech instructions only when enabled | tested |
| Streaming speech trigger | `friday.py:6355` | `friday_chat.speech` | Live speech starts from selected snippet and avoids double playback | tested |
| Background extraction | `friday.py:5800`, `friday.py:6250` | `friday_chat.background` | Buffers turns and extracts on configured interval; exit flush is tested | tested |
| Background extraction buffering completeness | `friday.py:6250`, `friday.py:6253`, `friday.py:5866` | `friday_chat.background`, `friday_chat.runtime.maintenance` | Every persisted turn is buffered; interval `N` extracts the full buffered batch; interval `-1` flushes buffered turns on exit | tested |
| Real summarization and summary visibility | `friday.py:7840`, `friday.py:3957`, `friday.py:2615` | `friday_chat.runtime.maintenance`, `commands.maintenance`, `commands.memory` | Real runtime mode wires extraction, compaction-backed summarization, lifecycle promotion, access-buffer, factor-computer, and incremental-maintenance services where available; generated summaries are visible through `/summaries` | tested |
| Real exit reorganization cleanup | `friday.py:5832`, `friday.py:5923`, `friday.py:5938`, `friday.py:5974`, `friday.py:8003` | `friday_chat.app`, `friday_chat.runtime.maintenance` | When `session.reorganize_on_exit` is enabled, FridayV2 runs real reorganization before transcript finalization with reference ordering, mode skip rules, maintenance LLM roles, lifecycle collaborators, and warning-only failure handling | tested |
| Incremental graph maintenance | `friday.py:6230`, `friday.py:7857` | `friday_chat.background` | Runs on schedule through supervised task manager | tested |
| Budget-aware compaction initialization | `friday.py:7870` | `friday_chat.runtime.maintenance`, `friday_chat.config` | `memory.compaction.enabled` initializes the real `ContextBudgetMonitor` and `InSessionCompactor` with framework collection manager and LLM dependencies, or logs an explicit framework-upgrade gap | tested |
| Budget-aware compaction turn scheduling | `friday.py:1441`, `friday.py:6237`, `friday.py:7989` | `friday_chat.background`, `friday_chat.turns.processor`, `friday_chat.app` | After a successful persisted turn, FridayV2 records actual prompt budget status, schedules real background compaction when the monitor threshold is crossed, flushes extraction first, passes budget context/time budget, marks completion on success or failure, and awaits in-flight compaction before the next chat prompt | tested |
| Exit maintenance | `friday.py:5832` | `friday_chat.maintenance` | Flushes extraction, access buffer, lifecycle, and optional reorganization in order | tested |
| Workflow loader setup | `friday.py:7824` | `friday_chat.runtime` | Workflow directory is configurable via `chat.workflows_dir`/`FRIDAY_WORKFLOWS_DIR` with root `workflows/` fallback | tested |
| Replay CLI mode | `friday.py:7924` | `friday_chat.cli`, `friday_chat.replay` | CLI replay exits after processing and reports summary | tested |
| Transcript session finalization | `friday.py:8026` | `friday_chat.app` | Finalizes transcript even after loop exceptions | tested |

## Required Tests

| Test area | Target tests | Status |
| --- | --- | --- |
| Config validation | Missing llm config, Friday-py config compatibility, 406-path active option parity, env-secret interpolation, invalid speech/security config, unknown/deprecated key reporting | tested |
| Config traceability | Every supported config key has a mapped consumer, compatibility handler, or explicit deprecation record | tested |
| Framework freeze | No FridayV2 parity implementation test mutates existing framework packages; upgrade needs are logged instead | tested |
| Contract coverage | Every implemented parity row has a behavioral contract or explicit simple-command exemption in `parity_overrides.yaml` | tested |
| Disposable command UAT | Example-derived one-root real runtime, public seeded stores, deterministic chat/embedding doubles, transport tripwires, production CLI input/output/display, supported-platform PTY, exact Gate F slash-command sequence | verified |
| Command registry | Every command is registered exactly once and appears in help | tested |
| Command parsing | Flags, positional args, unknown commands, detailed help, `/migrate` compatibility aliases, and `/inject-tools` name separators | tested |
| Turn processor | No-tool streaming path with fake LLM and fake memory controller | tested |
| Tool loop | API tool calls, text tool calls, tool errors, circuit breaker, truncation, pruning | intentionally changed |
| Persistence | Turn saved with transcript/context-log metadata | tested |
| Background tasks | Extraction flush, task failure reporting, shutdown cancellation/await | tested |
| Shell service | Disabled default, enabled execution, timeout, nonzero, stderr | tested |
| Replay | CSV order, reset-before-replay, normal pipeline invocation, delay handling | tested |
| Security | Sanitization stats, runtime config update rollback, payload injection | tested |
| Speech | Config updates, prompt snippet, tag stripping, cancellation | tested |
| Orchestration | Switch, delegate, at-routing, status with fake orchestrator | tested |
| Workflow | List, run with inputs, pending approval, approve, skip | tested |
| File commands | Reader dispatch for all supported formats, line limit, ingest metadata | tested |
