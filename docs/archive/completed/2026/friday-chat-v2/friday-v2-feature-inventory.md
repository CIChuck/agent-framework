# FridayV2 Feature Inventory

This inventory enumerates the behavior that FridayV2 must preserve from the
current reference prototype at `tests/integration/memory/friday.py`. Detailed
business rules live in the behavioral contracts document.

The goal is feature parity without carrying forward the prototype's critical
structure problems: production behavior under `tests/`, an 8k-line god object,
dual command routing, unmanaged background tasks, unrestricted shell execution
by default, raw YAML plumbing throughout the app, and checked-in provider
secrets.

## Source Of Truth

- Reference CLI: `tests/integration/memory/friday.py`
- Local prototype helper package: `tests/integration/memory/friday_chat/`
- Target package: `packages/friday-chat`
- Runtime wiring should reuse `friday-runtime` wherever possible.

## Completion Rule

FridayV2 is not complete until every feature below is one of:

- `implemented`: available in FridayV2 with tests.
- `intentionally changed`: behavior changed with a documented reason and tests.
- `deprecated`: explicitly removed with a documented reason.
- `deferred`: consciously postponed with a documented reason and owner.

Unreviewed omissions are not allowed.

Compatibility must be proven using the protocol in
`docs/archive/completed/2026/friday-chat-v2/friday-chat-v2-compatibility-testing-protocol.md`.
Existing framework packages are frozen during the FridayV2 parity pass. Any
needed framework package changes must be recorded in
`docs/planning/backlog/friday-chat-framework-followups/upgrade-log.md`.
Business rules and implementation semantics are defined in
`docs/archive/completed/2026/friday-chat-v2/friday-chat-v2-behavioral-contracts.md`. If a feature
is listed here but lacks enough behavioral detail there, update the behavioral
contracts before implementing it.

## App Lifecycle

Source evidence:

- CLI argument parsing and config loading: `tests/integration/memory/friday.py:7071`
- Component composition: `tests/integration/memory/friday.py:7530`
- Session construction: `tests/integration/memory/friday.py:7782`
- Main interactive loop: `tests/integration/memory/friday.py:7968`
- Exit maintenance and transcript finalization: `tests/integration/memory/friday.py:8003`

Required behavior:

- Load app configuration from an explicit config path.
- Validate required configuration before constructing runtime services.
- Configure logging, Rich console styling, input history, and command completion.
- Start an interactive single-line prompt loop.
- Support replay mode from CLI arguments.
- Finalize transcript sessions on exit.
- Run configured exit maintenance before shutdown.
- Shut down background tasks deterministically.

FridayV2 constraints:

- The runnable app must live in package code, not under `tests/`.
- Config must use typed models at the app boundary.
- Provider keys must come from environment variables, secret managers, or local
  ignored files, never from committed config.
- Startup composition must be behind a factory or runtime builder instead of a
  long script-level `main()`.

## Turn Processing

Source evidence:

- Full turn pipeline: `tests/integration/memory/friday.py:6009`
- Streaming LLM path: `tests/integration/memory/friday.py:6310`
- Tool-calling LLM path: `tests/integration/memory/friday.py:6567`
- Prompt/tool-pair pruning: `tests/integration/memory/friday.py:6478`

Required behavior:

- Initialize session state lazily if needed.
- Calculate dynamic context budget including active tool definitions.
- Assemble memory context with `ContextAssembler`.
- Format the prompt with current user input and configured context format.
- Record timing metrics for initialization, budget calculation, context
  assembly, prompt formatting, LLM call, and total turn time.
- Store the final prompt for debug commands.
- Use streaming mode when no tools are active.
- Use function-calling mode when tools are active.
- Persist `InteractionTurn` with user/assistant messages, tool calls, tool
  results, timing, token metrics, model, temperature, and optional raw
  prompt/response.
- Update session turn count after successful processing.
- Handle LLM timeout, retry exhaustion, circuit breaker, and cancellation with
  user-facing output.

FridayV2 constraints:

- Turn processing must be isolated in a testable service.
- UI output must be injectable or abstracted so turn tests do not require an
  interactive terminal.
- Background work triggered by a turn must be scheduled through a supervised
  task manager.

## Command Surface

Source evidence:

- Registry command definitions: `tests/integration/memory/friday.py:429`
- Legacy fallback command router: `tests/integration/memory/friday.py:1111`
- Help command: `tests/integration/memory/friday.py:5642`

FridayV2 must support a single registry-based command system. The legacy
fallback router must not be recreated.

### Session Commands

Source evidence: `tests/integration/memory/friday.py:437`

Commands:

- `/exit`, `/quit`, `/q`
- `/clear`
- `/cls`, `/clearscreen`
- `/help`
- `/help <command>`

Required behavior:

- Exit commands return a loop-level exit signal.
- Clear resets current conversation history, pending extraction buffer, last
  context payload, and session turn count.
- Clear-screen uses the terminal display layer.
- Help shows grouped commands and detailed per-command argument help.

### Memory And Context Commands

Source evidence: `tests/integration/memory/friday.py:461`

Commands:

- `/history`
- `/memory`
- `/context`
- `/context --debug`
- `/context --file`
- `/prompt`
- `/prompt --file`
- `/prime`
- `/debug`
- `/debug-budget`
- `/debug-retrieval <query>`
- `/timing`
- `/entities`
- `/entities nodes`
- `/entities <name>`
- `/insights`
- `/summaries`
- `/meta`
- `/vars`
- `/set <key> <value>`
- `/list-ingested`

Required behavior:

- Inspect conversation history with timestamps and tool calls.
- Show memory statistics across episodic, vector, and graph stores.
- Show the assembled context payload and optional token diagnostics.
- Export context and prompt views to file when requested.
- Prime memory before the first turn and expose primed context.
- Show debugging data for context assembly, budget calculations, retrieval,
  timing, graph entities, insights, summaries, meta insights, scoped variables,
  and ingested sources.

### Transcript And Export Commands

Source evidence: `tests/integration/memory/friday.py:592`

Commands:

- `/sessions`
- `/transcript`
- `/transcript <session_id>`
- `/transcript export`
- `/export [csv|jsonl|markdown|training]`
- `/export-prompts [session_id]`

Required behavior:

- List transcript sessions.
- Display current or selected session transcript.
- Export all transcript data to CSV.
- Export the current session to supported formats.
- Export raw prompts/responses from context logs to JSON.

### Maintenance Commands

Source evidence: `tests/integration/memory/friday.py:650`

Commands:

- `/reset [graph|vector|episodic]`
- `/reorganize`
- `/reorganize --execute`
- `/reorganize --no-backup`
- `/reorganize --skip-synthesis`
- `/reorganize --skip-verify`
- `/reorganize --skip-lifecycle`
- `/reorganize --force-reembed`
- `/reorganize --analyze`
- `/reorganize --prune`
- `/reorganize --synthesize`
- `/reorganize --verify`
- `/reorganize --backup`
- `/reorganize --dedupe`
- `/lifecycle`
- `/lifecycle --execute`
- `/lifecycle --stats`
- `/lifecycle --optimize`
- `/lifecycle --flush`
- `/migrate`
- `/migrate --force`
- `/migrate --execute`
- `/migrate --stats`
- `/compact`

Required behavior:

- Reset all memory or individual stores.
- Preserve appropriate archival behavior for transcript state during full reset.
- Run memory reorganization in dry-run by default.
- Support targeted reorganization steps and backup controls.
- Support forced graph-edge re-embedding during reorganization.
- Run lifecycle promotion, decay, reactivation, access-buffer flushing, and
  retrieval-factor optimization.
- Migrate existing memories to lifecycle metadata.
- Resolve the prototype's migration flag mismatch: the registry advertises
  `--execute` and `--stats`, while the handler implements `--force`. FridayV2
  should support compatibility aliases or explicitly document a changed command
  contract.
- Trigger manual context compaction.

### Replay Commands And Modes

Source evidence:

- Registry command: `tests/integration/memory/friday.py:803`
- CSV loading and replay processing: `tests/integration/memory/friday.py:3124`
- CLI replay mode: `tests/integration/memory/friday.py:7924`

Commands and modes:

- `/replay <csv_path> [delay_seconds]`
- CLI `--replay CSV_FILE`
- CLI `--replay-delay SECONDS`

Required behavior:

- Load exported CSV transcripts.
- Extract user messages in turn order.
- Reset memory before replay.
- Process each replay prompt through the normal turn pipeline.
- Support optional delay between replay turns.
- Exit after CLI replay mode completes.

### Tool Commands And Tool Loop

Source evidence:

- Tool commands: `tests/integration/memory/friday.py:826`
- Tool loop: `tests/integration/memory/friday.py:6567`
- Tool execution and sanitization: `tests/integration/memory/friday.py:6819`

Commands:

- `/tools [category]`
- `/run-tool <name> [json]`
- `/inject-tools <names>`
- `/clear-tools`
- `/recommend-tools <query>`
- `/tool-budget`

Required behavior:

- Load tools from configured registry.
- Auto-inject all configured tool schemas into chat context when
  `tools.context.include_in_context` is enabled.
- List tools and filter by category.
- Validate tool parameters.
- Execute individual tools from the command line.
- Support `/run-tool` JSON parameters and the prototype's plain-text mapping for
  tools with a `message`, single required, or single available parameter.
- Inject selected tool schemas into the chat context.
- Resolve the prototype's `/inject-tools` argument mismatch: registry text says
  comma-separated names, while the handler splits whitespace-separated names.
- Clear injected tools.
- Recommend tools for a query.
- Show token budget cost of active tools.
- Run ReAct-style function calling when active tools are present.
- Preserve provider-specific reasoning content where required.
- Support text-parsed tool calls for models that do not use function calling,
  if this behavior remains intentionally supported.
- Enforce max iterations, consecutive failure circuit breaker, max tool
  messages, and max tool result size.
- Preserve tool-call/tool-result message pairs when pruning.
- Track tool calls and results in transcripts.
- Sanitize tool output before LLM context and before memory storage.
- Track large tool outputs for lifecycle management.
- Ingest qualifying tool output for cross-session retrieval.

FridayV2 constraints:

- The tool loop must be a package-level service with direct tests.
- Tool registry state must not depend on mutable module globals.

### Security Commands

Source evidence: `tests/integration/memory/friday.py:896`

Commands:

- `/security`
- `/security-test [instruction|delimiter|jailbreak|exfil|all]`
- `/security-config <sensitivity|action|wrapping> <value>`
- `/inject-payload <payload>`

Required behavior:

- Show sanitization settings and detection statistics.
- Run sample prompt-injection detection probes.
- Update security sensitivity/action/wrapping at runtime.
- Inject a test payload into the next tool result for validation.
- Maintain scan, detection, blocked, and pattern-count stats.

FridayV2 constraints:

- Security test hooks must be clearly labeled as local validation features.
- Runtime security configuration updates must be typed and rollback-safe.

### Speech Commands And Playback

Source evidence:

- Speech commands: `tests/integration/memory/friday.py:950`
- Speech service wiring and prompt snippet: `tests/integration/memory/friday.py:4381`
- Streaming speech behavior: `tests/integration/memory/friday.py:6355`
- Speech cancellation binding: `tests/integration/memory/friday.py:7912`

Commands:

- `/speech`
- `/speech config`
- `/speech on`
- `/speech off`
- `/speech mode live|file`
- `/speech voice <voice_id>`
- `/speech provider elevenlabs|picovoice`
- `/speech-test [once|loop]`

Required behavior:

- Load speech config and instantiate `friday-speech` services when enabled.
- Add speech-tagging instructions to the system prompt when speech is enabled.
- Strip speech tags from terminal output where appropriate.
- Support live streaming speech trigger and post-response playback.
- Support blocking and background playback modes.
- Cancel speech playback with `Ctrl+Q`.
- Run speech harness tests with cancellation.
- Roll back runtime config updates when validation fails.

### Orchestration Commands

Source evidence:

- Command definitions: `tests/integration/memory/friday.py:978`
- At-routing: `tests/integration/memory/friday.py:5399`

Commands and routing:

- `/switch [agent]`
- `/agents`
- `/agent [name]`
- `/delegate <agent> <task>`
- `/status`
- `@agent_name <message>`

Required behavior:

- Show or switch active agent.
- List configured agents, capabilities, active agent, and cached agents.
- Show agent details.
- Delegate a task to another agent and return to the previous active agent.
- Show orchestrator status.
- Route `@agent_name` messages through the orchestrator.

### Workflow Commands

Source evidence:

- Command definitions: `tests/integration/memory/friday.py:1034`
- Workflow handlers: `tests/integration/memory/friday.py:5066`
- Workflow loader setup: `tests/integration/memory/friday.py:7824`

Commands:

- `/workflow`
- `/workflow list`
- `/workflow run <name> [key=value ...]`
- `/workflow status`
- `/workflow approve`
- `/workflow skip`

Required behavior:

- Load workflow definitions from configured workflow directories.
- List available workflows with description, task count, and version.
- Run workflows with parsed key/value inputs.
- Track active workflow and execution state.
- Report workflow status.
- Continue pending approval gates through approve or skip.

### File Commands

Source evidence: `tests/integration/memory/friday.py:1056`

Commands:

- `/read <path>`
- `/read <path> --lines N`
- `/ingest <path> [description]`

Required behavior:

- Read `txt`, `md`, `yaml`, `json`, `py`, `csv`, `tsv`, `pdf`, `docx`, and
  `xlsx` through smart detection.
- Display file metadata and excerpts.
- Respect optional max-line limits where supported.
- Ingest files into vector memory with semantic chunking.
- Attach path/description metadata to ingested content.

### Shell Access

Source evidence:

- Shell execution implementation: `tests/integration/memory/friday.py:7000`
- Main loop dispatch: `tests/integration/memory/friday.py:7973`

Behavior in prototype:

- `!<command>` executes an arbitrary shell command in the user's shell.
- Stdout is printed normally, stderr is printed red, nonzero exit codes are
  shown, and commands time out after 60 seconds.

FridayV2 constraints:

- Shell access must be disabled by default or explicitly gated by config.
- Shell execution must go through a service boundary.
- Any sandbox or working-directory policy must be visible in config and help.
- Tests must cover disabled mode, enabled mode, timeout, stderr, and nonzero
  exit code behavior.

## Background Work And Maintenance

Source evidence:

- Background task helpers: `tests/integration/memory/friday.py:5779`
- Task scheduling during turn processing: `tests/integration/memory/friday.py:6224`
- Exit maintenance: `tests/integration/memory/friday.py:5832`

Required behavior:

- Buffer extraction turns and flush them on configured intervals.
- Flush pending extraction on exit.
- Run tool content decay after turns.
- Run incremental graph maintenance on schedule.
- Run budget-aware compaction when thresholds are crossed.
- Gate the next turn on in-flight compaction when needed.
- Flush access buffer on exit when configured.
- Run lifecycle promotion/decay/reactivation on exit when configured.
- Run optional reorganization on exit.

FridayV2 constraints:

- All background tasks must be created through `BackgroundTaskManager`.
- Task failures must be captured, logged, and visible in diagnostics.
- Shutdown must await or cancel tracked tasks intentionally.

## Persistence And Runtime State

Source evidence:

- Persistence directory and transcript DB: `tests/integration/memory/friday.py:7530`
- Graph store and vector store: `tests/integration/memory/friday.py:7549`
- Transcript session creation: `tests/integration/memory/friday.py:7761`

Required behavior:

- Use persistent transcript, graph, vector, and lifecycle collections.
- Support configurable persistence directory.
- Maintain transcript sessions with model/system prompt/config snapshot.
- Support context log persistence for raw prompt/response capture.
- Respect transcript export directory and raw prompt capture settings.
- Keep Chroma/vector data, graph JSON, transcript DB, history, rejection logs,
  exports, and maintenance logs out of committed package source by default.

## Configuration Surface

Configuration compatibility is a critical FridayV2 feature. The existing
`tests/integration/memory/config.yaml` format configures every major Friday
capability and should be preserved as the primary migration format for users.

Required behavior:

- Preserve configuration coverage for LLM, extraction LLM, embeddings, memory,
  retrieval, priming, passage routing, cache, supporting context, transcript,
  maintenance LLM roles, lifecycle, tools, web, smart file reading, finance,
  security, speech, Langfuse, logging, and CLI display.
- Preserve the current top-level config section names used by the prototype:
  `logging`, `llm`, `extraction`, `embedding`, `memory`, `transcript`, `chat`,
  `maintenance`, `lifecycle`, `smart_file`, `tools`, `web`, `langfuse`,
  `finance`, `security`, `session`, and `speech`.
- Preserve nested configuration capability for:
  `memory.retrieval`, `memory.token_estimator`, `memory.compaction`,
  `memory.supporting_context`, `memory.passage_router`,
  `memory.query_relevance_filter`, `memory.cache`, `memory.priming`,
  `maintenance.pruning`, `maintenance.synthesis`,
  `maintenance.fact_checking`, `maintenance.llm`, `maintenance.embedding`,
  `maintenance.defaults`, `maintenance.logging`, `maintenance.prompts`,
  `lifecycle.access_buffer`, `lifecycle.factor_computer`, `tools.loop`,
  `tools.registry`, `tools.context`, `smart_file.code`, `smart_file.llm`,
  `smart_file.prompts`, `web.client`, `web.ssl`, `web.proxy`,
  `web.security`, `web.reader`, `finance.massive`,
  `security.sanitization`, `speech.tts`, `speech.wakeword`,
  `speech.elevenlabs`, `speech.picovoice`, `speech.streaming`,
  `speech.playback`, `speech.selection`, and `speech.chunking`.
- Provide a migration-compatible loader that accepts a Friday-py-style
  `config.yaml`, normalizes it into typed FridayV2 config models, and reports
  unknown, deprecated, renamed, missing, or incompatible fields with actionable
  diagnostics.
- Keep defaults semantically compatible with `friday.py` unless a deviation is
  documented in the parity matrix.
- Make each top-level and nested config section traceable to at least one
  runtime builder, command, subsystem, or explicit "accepted but unused"
  compatibility field.

FridayV2 constraints:

- Provide `config.example.yaml` without secrets.
- Support environment interpolation for keys and endpoints.
- Parse to typed config models before runtime construction.
- Validate incompatible settings before starting the app.
- Add config parity tests that load the current prototype config shape with
  secrets replaced by environment placeholders.
- Add traceability tests or checks that fail when a supported config key has no
  mapped consumer, compatibility handler, or explicit deprecation record.
- Do not force users to relearn the configuration structure for the first
  FridayV2 migration; format changes should be additive or compatibility-backed.

Testing details are defined in
`docs/archive/completed/2026/friday-chat-v2/friday-chat-v2-compatibility-testing-protocol.md`.

## Framework Freeze

FridayV2 must be implemented as the app layer over the existing Friday framework
packages. The first parity pass should not modify existing framework package
internals, because the goal is to compare FridayV2 against
`tests/integration/memory/friday.py` while the framework baseline remains
stable.

Allowed implementation targets:

- `packages/friday-chat/`
- `packages/friday-chat/tests_chat/`
- Workspace metadata required to register and run `packages/friday-chat`.
- FridayV2 planning documents under `docs/planning/`.

Frozen implementation targets:

- Existing `packages/friday-*` framework package source and tests, except for
  the new `packages/friday-chat` package.

If missing framework capability blocks or complicates FridayV2, record it in
`docs/planning/backlog/friday-chat-framework-followups/upgrade-log.md` with source
evidence, impact, the FridayV2 workaround, compatibility risk, and suggested
follow-up tests. Do not patch the frozen package during the parity pass.

## Existing Prototype Code That May Be Reused

- `tests/integration/memory/friday_chat/config.py`
- `tests/integration/memory/friday_chat/models.py`
- `tests/integration/memory/friday_chat/tools.py`
- `tests/integration/memory/friday_chat/processing.py`
- `tests/integration/memory/friday_chat/commands/*.py`
- `packages/friday-cli/src/friday_cli/*`
- `packages/friday-runtime/src/friday_runtime/*`

Reuse means porting behind clean package interfaces, not importing production
FridayV2 behavior from `tests/integration/memory`.
