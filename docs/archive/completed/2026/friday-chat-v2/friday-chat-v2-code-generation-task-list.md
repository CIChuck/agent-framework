# FridayV2 Code Generation Task List

This task list is the execution checklist for building `packages/friday-chat`.
Use it after the FridayV2 planning packet has been committed and a FridayV2
implementation branch has been created.

Do not start a task until its prerequisites are satisfied. If implementation
reveals a planning gap, update the relevant planning document before writing or
changing code for that behavior.

## Operating Rules

- Follow this task list in order unless the user explicitly approves a change in
  sequence.
- Keep the first parity pass inside the allowed FridayV2 implementation targets:
  `packages/friday-chat/`, `packages/friday-chat/tests_chat/`, minimal workspace
  metadata, and FridayV2 planning docs.
- Do not edit existing framework package source or tests during the parity pass.
  Log needed framework changes in
  `docs/planning/backlog/friday-chat-framework-followups/upgrade-log.md`.
- For every non-trivial feature, confirm or update
  `docs/archive/completed/2026/friday-chat-v2/friday-chat-v2-behavioral-contracts.md` before
  implementation.
- For every implemented parity row, add or update tests before marking the row
  `tested`.
- Prefer fake services for initial implementation. No generated code should
  require a real LLM, embedding, speech, web, finance, telemetry, or external
  tool provider to pass the package tests.

## Pre-Code Gate

- [ ] Confirm the planning packet is committed and pushed.
- [ ] Confirm the implementation branch exists and is based on the committed
  planning packet.
- [ ] Confirm the worktree is clean except for intentionally ignored local
  runtime state.
- [x] Run `git diff --check` on the committed planning packet if any planning
  docs changed after the commit.
- [x] Confirm `README.md` has no trailing whitespace.
- [x] Confirm the FridayV2 framework freeze still appears in `AGENTS.md`, the
  build plan, and the framework upgrade log.

## Task 1: Create Package Skeleton

Prerequisites:

- Pre-code gate is complete.

Work:

- [x] Create `packages/friday-chat/pyproject.toml`.
- [x] Register the package in workspace metadata.
- [x] Add `src/friday_chat/__init__.py`.
- [x] Add module placeholders from the build plan:
  `app.py`, `cli.py`, `config.py`, `runtime.py`, `session.py`,
  `background.py`, `shell.py`, `replay.py`, `exports.py`, `security.py`,
  `speech.py`.
- [x] Add package subdirectories:
  `commands/`, `turns/`, and `tools/`.
- [x] Add `tests_chat/` with smoke tests.
- [x] Add a `friday-chat` console script that exposes help without building real
  runtime services.

Validation:

- [x] `uv sync --all-extras`
- [x] `uv run friday-chat --help`
- [x] `uv run pytest packages/friday-chat/tests_chat`
- [x] Confirm no production code imports from `tests/integration/memory`.
- [x] Confirm no existing framework package source or test files changed.

## Task 2: Add Compatibility Test Scaffolding

Prerequisites:

- Task 1 is complete.

Work:

- [x] Create `packages/friday-chat/tests_chat/compat/`.
- [x] Add `fixtures/parity_overrides.yaml`.
- [x] Add `fixtures/friday_py_config_sanitized.yaml`.
- [x] Add `fixtures/replay_basic.csv`.
- [x] Add `test_command_surface_parity.py`.
- [x] Add `test_config_compatibility.py`.
- [x] Add `test_contract_coverage.py`.
- [x] Add `test_turn_contract_parity.py`.
- [x] Add `test_tool_loop_parity.py`.
- [x] Add `test_replay_parity.py`.
- [x] Add `test_safety_defaults.py`.

Validation:

- [x] Compatibility tests run and fail only for not-yet-implemented FridayV2
  behavior, not because of missing fixtures or broken imports.
- [x] `test_command_surface_parity.py` parses retained commands and aliases from
  `tests/integration/memory/friday.py`, including fallback-only
  `/debug-retrieval` and `/list-ingested`.
- [x] `test_contract_coverage.py` maps retained parity rows to behavioral
  contract sections or explicit simple-command exemptions.

## Task 3: Implement Typed Config Compatibility

Prerequisites:

- Task 2 is complete.
- Config contract is reviewed in the behavioral contracts document.

Work:

- [x] Implement typed config models for all Friday-py top-level sections:
  `logging`, `llm`, `extraction`, `embedding`, `memory`, `transcript`, `chat`,
  `maintenance`, `lifecycle`, `smart_file`, `tools`, `web`, `langfuse`,
  `finance`, `security`, `session`, and `speech`.
- [x] Implement Friday-py-style YAML loading.
- [x] Implement environment interpolation.
- [x] Implement unknown/deprecated/renamed key diagnostics.
- [x] Add `config.example.yaml` without secrets.
- [x] Add config traceability mapping for every supported key.

Validation:

- [x] Sanitized Friday-py config fixture loads.
- [x] Minimal config loads.
- [x] Missing required LLM config fails before runtime construction.
- [x] Env interpolation tests pass.
- [x] Traceability tests fail for unmapped supported config keys.

## Task 4: Implement Runtime Factory With Fakes

Prerequisites:

- Task 3 is complete.

Work:

- [x] Define runtime service interfaces or narrow protocols needed by the app.
- [x] Implement config-to-runtime construction using existing framework
  packages where possible.
- [x] Implement fake LLM, fake embedding, fake memory controller, fake transcript
  store, fake tool registry, fake speech adapter, fake orchestrator, and fake
  workflow engine for tests.
- [x] Implement maintenance LLM fallback reporting.
- [x] Implement tool auto-injection when `tools.context.include_in_context` is
  enabled.
- [x] Implement real-runtime adapters for LLM, embeddings, memory, transcripts,
  configured tools, passage routing, and workflow loading.

Validation:

- [x] Runtime factory tests pass without provider keys or network calls.
- [x] Tool auto-injection config test passes.
- [x] Maintenance fallback diagnostics are testable.
- [x] Framework upgrade needs, if any, are logged instead of patched.
- [x] `--config --runtime real` can start and exit through the package console
  script without requiring `uv`.

## Task 5: Implement App Lifecycle

Prerequisites:

- Task 4 is complete.

Work:

- [x] Implement `FridayChatApp`.
- [x] Implement interactive loop input abstraction.
- [x] Implement EOF and keyboard interrupt handling.
- [x] Implement transcript session creation/finalization hooks.
- [x] Implement configured exit maintenance orchestration.
- [x] Implement supervised shutdown.

Validation:

- [x] App exits cleanly on EOF.
- [x] App exits cleanly on keyboard interrupt.
- [x] Transcript finalization runs on normal and error exit.
- [x] No unmanaged background tasks remain in tests.

## Task 6: Implement Command Registry Foundation

Prerequisites:

- Task 5 is complete.

Work:

- [x] Implement one registry for command metadata, help, parsing, and dispatch.
- [x] Register session commands.
- [x] Register fallback-only prototype commands as first-class FridayV2
  commands or document an accepted difference.
- [x] Implement unknown-command behavior.
- [x] Implement `/help` and `/help <command>` from registry metadata.

Validation:

- [x] Command surface parity test passes for registered commands and aliases that
  are in scope for the current slice.
- [x] Duplicate command registration fails.
- [x] `/help` includes every registered command.
- [x] No legacy fallback router exists.

## Task 7: Implement Session And Basic Memory Commands

Prerequisites:

- Task 6 is complete.

Work:

- [x] Implement `/exit`, `/quit`, `/q`.
- [x] Implement `/clear`.
- [x] Implement `/cls`, `/clearscreen`.
- [x] Implement `/history`.
- [x] Implement `/memory`.
- [x] Implement `/context`.
- [x] Implement `/prompt`.
- [x] Implement `/debug`.
- [x] Implement `/debug-budget`.
- [x] Implement `/timing`.
- [x] Implement `/prime`.
- [x] Implement `/vars` and `/set`.
- [x] Implement fallback-only memory diagnostics from the prototype:
  `/debug-retrieval`, `/entities`, `/insights`, `/summaries`, and `/meta`.

Validation:

- [x] Session command tests pass.
- [x] Basic memory command tests pass with fake stores.
- [x] File export behavior is safe and tested for context/prompt exports.
- [x] Diagnostic memory commands have empty-state and dispatch coverage.

## Task 8: Implement No-Tool Turn Processing

Prerequisites:

- Task 7 is complete.

Work:

- [x] Implement `turns.processor`.
- [x] Implement streaming path with fake LLM support.
- [x] Implement timing metrics.
- [x] Implement prompt/message capture for debug commands.
- [x] Persist `InteractionTurn`.
- [x] Store context-log entries when raw prompt capture is enabled.
- [x] Implement error handling for timeout, retry exhaustion, circuit breaker,
  and cancellation.

Validation:

- [x] No-tool turn compatibility tests pass.
- [x] Raw prompt capture tests pass.
- [x] Persistence failure path is tested.
- [x] Error-path tests leave state consistent.

## Task 9: Implement Transcript And Export Commands

Prerequisites:

- Task 8 is complete.

Work:

- [x] Implement `/sessions`.
- [x] Implement `/transcript`.
- [x] Implement `/transcript <session_id>`.
- [x] Implement `/transcript export`.
- [x] Implement `/export csv|jsonl|markdown|md|training`.
- [x] Implement `/export-prompts [session_id]`.

Validation:

- [x] Transcript command tests pass with fake transcript store.
- [x] Export format tests call expected exporters.
- [x] Missing context-log export path is tested.

## Task 10: Implement Tool Commands And Tool Loop

Prerequisites:

- Task 9 is complete.

Work:

- [x] Implement tool registry loading without mutable module globals.
- [x] Implement `/tools`.
- [x] Implement `/run-tool`.
- [x] Implement `/inject-tools`.
- [x] Implement `/clear-tools`.
- [x] Implement `/recommend-tools`.
- [x] Implement `/tool-budget`.
- [x] Implement function-calling tool loop.
- [x] Decide and document whether text-parsed tool calls remain supported.
- [x] Implement separate sanitization for LLM context and memory storage.
- [x] Implement tool output lifecycle tracking and ingestion hooks.
- [x] Implement pair-preserving tool message pruning.

Validation:

- [x] Tool command tests pass.
- [x] Tool loop compatibility tests pass.
- [x] Security stats update tests pass.
- [x] Truncation and circuit-breaker tests pass.

## Task 11: Implement Maintenance Commands

Prerequisites:

- Task 10 is complete.

Work:

- [x] Implement `/reset`.
- [x] Implement `/reorganize`.
- [x] Implement `/lifecycle`.
- [x] Implement `/migrate`.
- [x] Implement `/compact`.

Validation:

- [x] Dry-run defaults are tested.
- [x] Single-step mode precedence is tested.
- [x] Migration flag compatibility is tested.
- [x] Compaction flush-before-run behavior is tested.
- [x] Error classification is tested.

## Task 12: Implement Background Work And Exit Maintenance

Prerequisites:

- Task 11 is complete.

Work:

- [x] Implement `BackgroundTaskManager`.
- [x] Route extraction scheduling through the manager.
- [x] Route tool decay through the manager.
- [x] Route incremental graph maintenance through the manager.
- [x] Route budget-aware compaction through the manager.
- [x] Implement exit maintenance order.

Validation:

- [x] Extraction interval matrix tests pass.
- [x] Background task failure reporting is tested.
- [x] Shutdown await/cancel behavior is tested.
- [x] Exit maintenance order tests pass.

## Task 13: Implement Files, Replay, And Shell

Prerequisites:

- Task 12 is complete.

Work:

- [x] Implement `/read`.
- [x] Implement `/ingest`.
- [x] Implement `/list-ingested`.
- [x] Implement `/replay <csv_path> [delay_seconds]`.
- [x] Implement CLI `--replay` and `--replay-delay`.
- [x] Implement shell service with disabled default and explicit opt-in.

Validation:

- [x] File reader dispatch tests pass.
- [x] Ingestion metadata tests pass.
- [x] Replay compatibility tests pass.
- [x] Shell safety-default tests pass.

## Task 14: Implement Security And Speech

Prerequisites:

- Task 13 is complete.

Work:

- [x] Implement `/security`.
- [x] Implement `/security-test`.
- [x] Implement `/security-config`.
- [x] Implement `/inject-payload`.
- [x] Implement speech config refresh.
- [x] Implement prompt snippet injection.
- [x] Implement speech tag stripping and speakable snippet selection.
- [x] Implement `/speech`.
- [x] Implement `/speech-test`.
- [x] Implement speech cancellation.

Validation:

- [x] Security command tests pass.
- [x] Runtime security rollback tests pass.
- [x] Speech command tests pass with fake adapters.
- [x] Speech cancellation tests pass.

## Task 15: Implement Orchestration And Workflows

Prerequisites:

- Task 14 is complete.

Work:

- [x] Implement `@agent_name <message>` routing.
- [x] Implement `/switch`.
- [x] Implement `/agents`.
- [x] Implement `/agent`.
- [x] Implement `/delegate`.
- [x] Implement `/status`.
- [x] Implement `/workflow list|run|status|approve|skip`.
- [x] Load real workflow definitions from a configurable workflow directory in
  real runtime mode.

Validation:

- [x] Orchestration tests pass with fake orchestrator.
- [x] Delegate restores prior active agent on success and failure.
- [x] Workflow tests pass with fake workflow engine.
- [x] Real runtime workflow-loader discovery is tested with a fixture directory.

## Task 16: Parity Audit And Release Gate

Prerequisites:

- Tasks 1 through 15 are complete.

Work:

- [x] Walk every parity matrix row.
- [x] Update row status to `tested`, `verified`, `intentionally changed`,
  `deprecated`, or `deferred`.
- [x] Confirm every implemented row has a behavioral contract or
  `parity_overrides.yaml` simple-command exemption.
- [x] Confirm every accepted difference is listed in `parity_overrides.yaml`.
- [x] Review framework upgrade log and confirm no frozen framework packages were
  edited during the parity pass.

Validation:

- [x] `uv run pytest packages/friday-chat/tests_chat/compat`
- [x] `uv run pytest packages/friday-chat/tests_chat`
- [x] `uv run ruff check packages/friday-chat`
- [x] `uv run mypy packages/friday-chat`
- [x] `git diff --check`
- [x] FridayV2 local smoke session with fake or local-model config.

## Compatibility Remediation Tasks

These tasks capture compatibility gaps discovered after the first FridayV2 parity
pass. They are not optional polish; each item must be implemented and tested
before FridayV2 can be considered functionally compatible with `friday.py`.

### Task 17: Restore Startup Presentation And System Prompt Parity

Plan:

- `docs/archive/completed/2026/friday-chat-v2/friday-chat-v2-startup-config-remediation-plan.md`

Prerequisites:

- Task 16 is complete.
- The remediation scope remains inside `packages/friday-chat/`,
  `packages/friday-chat/tests_chat/`, FridayV2 example configs, launcher scripts,
  and FridayV2 planning docs.

Work:

- [x] Load Friday CLI display configuration from `cli-config.yaml` next to the
  selected `config.yaml`, matching `friday.py:7102`.
- [x] Add an explicit `--cli-config` override for FridayV2 startup while
  preserving sibling-file auto-discovery for Friday-py migration.
- [x] Implement typed CLI display config models for `theme`, `icons`, `prompt`,
  and `spinner` from `tests/integration/memory/cli-config.yaml`.
- [x] Restore configured greeting/banner startup behavior equivalent to
  `friday.py:7355`.
- [x] Restore the thinking heartbeat after prompt submission for no-tool
  conversation turns, matching `friday.py:6325`.
- [x] Restore tool-turn heartbeat behavior where the first model call uses a
  thinking indicator and later model calls use tool-processing messages, matching
  `friday.py:6630`.
- [x] Ensure all heartbeat indicators stop on normal completion, cancellation,
  timeout, retry exhaustion, circuit-breaker failure, and unexpected errors.
- [x] Stop heartbeat on the first streamed chunk after Task 18 integrates the
  normal chat path with streaming output instead of complete-then-print output.
- [x] Ensure command-line startup initializes the effective system prompt from
  `chat.system_prompt`, matching `friday.py:7542`, and passes that same prompt
  into transcript/session creation, turn processing, context budget calculation,
  `/prompt`, and `/debug`.
- [x] Preserve Friday's speech behavior where speech mode augments the base
  system prompt only when enabled, matching `friday.py:4400`.
- [x] Update `packages/friday-chat/config.example.yaml` and add a
  `cli-config.example.yaml` without secrets.
- [x] Update `scripts/run-friday-chat-example.sh` to exercise the display config
  path.

Validation:

- [x] Compatibility tests prove `cli-config.yaml` is auto-loaded from the
  `--config` sibling directory when present.
- [x] Compatibility tests prove `--cli-config` overrides sibling auto-discovery.
- [x] Compatibility tests prove defaults are used when no CLI display config is
  present.
- [x] Conversation-turn tests prove the heartbeat starts while waiting for model
  output and stops on completion or failure.
- [x] Tool-turn tests prove first-iteration thinking heartbeat and later-iteration
  tool-processing heartbeat selection.
- [x] Heartbeat config tests prove spinner type, styles, randomization, thinking
  messages, and tool messages come from the effective `cli-config.yaml`.
- [x] Startup tests prove the effective system prompt equals
  `chat.system_prompt` before speech augmentation.
- [x] Speech tests prove the effective prompt is augmented only while speech is
  enabled and returns to the base configured prompt when disabled.
- [x] Transcript/session tests prove the configured system prompt is persisted in
  session metadata.
- [x] Turn-processing tests prove prompt formatting and context-budget
  calculation use the configured effective system prompt, not a hard-coded
  default.
- [x] CLI smoke tests exercise `friday-chat --runtime fake --config
  packages/friday-chat/config.example.yaml` without `uv`.

### Task 18: Restore End-To-End Turn, Tool, Context, And Background Parity

Plan:

- `docs/archive/completed/2026/friday-chat-v2/friday-chat-v2-turn-integration-remediation-plan.md`

Prerequisites:

- Task 17 is complete, or the implementation explicitly coordinates display
  heartbeat changes with turn-processing changes.
- The remediation scope remains inside `packages/friday-chat/`,
  `packages/friday-chat/tests_chat/`, launcher/config examples, and FridayV2
  planning docs.

Work:

- [x] Add regression tests that reproduce the reported date/tool request returning
  nothing and multi-turn summary losing prior context.
- [x] Add regression tests that reproduce background summaries not appearing.
- [x] Replace the `str`-only internal chat model contract with a structured
  response that preserves content, tool calls, usage, reasoning content, and raw
  provider metadata.
- [x] Update fake and framework chat adapters so tool-call-only responses are
  preserved for execution rather than collapsed into text or empty output.
- [x] Ensure the actual LLM message payload includes effective system prompt,
  assembled supporting context, current-session history, prior-session history
  when configured, active tools, current user query, and current turn count.
- [x] Integrate the tool loop into normal conversation turn processing whenever
  active tools are available.
- [x] Execute returned tool calls through the configured tool registry and feed
  sanitized tool results back into the model until final content or max
  iterations.
- [x] Buffer every successfully persisted turn for extraction; interval-based
  extraction must process all buffered turns, not only the trigger turn.
- [x] Wire real extraction and compaction services in real runtime mode where
  existing framework packages support them.
- [x] Wire real summarization and lifecycle services in real runtime mode where
  existing framework packages support them.
- [x] Restore budget-aware in-session compaction in real runtime mode:
  initialize `ContextBudgetMonitor` and `InSessionCompactor` from
  `memory.compaction`, record the actual prompt budget status after each
  successful persisted turn, schedule background compaction when the monitor
  threshold is crossed, flush pending extraction before compaction, pass budget
  context/time-budget values into the compactor, mark compaction complete on
  success or failure, and gate the next chat prompt until any in-flight
  compaction task completes.
- [x] Restore real exit reorganization cleanup in real runtime mode when
  `session.reorganize_on_exit` is true, including `session.reorganize_mode`,
  maintenance LLM role selection, backup behavior, fast/full mode skip rules,
  and `MemoryReorganizer` report handling.
- [x] Ensure exit maintenance reports warnings for reorganization failures but
  still finalizes transcript/session resources.
- [x] Confirm this pass required no new framework-package edits or upgrade-log
  entries.

Validation:

- [x] Date/time tool UAT proves a normal conversation turn executes the configured
  date/time tool and returns a non-empty answer.
- [x] Tool-call-only model responses never produce an empty assistant response.
- [x] Multi-turn summary test proves previous turns are present in the model
  prompt/context by the fourth or fifth turn.
- [x] `/context` and `/prompt` tests show the same effective prompt/context sent
  to the model.
- [x] Raw prompt capture stores the actual model response payload.
- [x] Background extraction interval tests prove all buffered turns are extracted.
- [x] Exit-flush tests prove interval `-1` buffers turns and flushes on exit when
  configured.
- [x] Budget-aware compaction tests prove monitor initialization, budget-status
  recording, threshold-triggered background scheduling, flush-before-compaction,
  budget context propagation, completion marking, and next-prompt gating.
- [x] `/summaries` tests prove generated summaries are visible after background or
  manual summarization runs.
- [x] Real runtime tests fail if required maintenance behavior silently uses fake
  services without a framework-upgrade log entry.
- [x] Exit-maintenance tests prove real reorganization cleanup runs before
  transcript finalization when `session.reorganize_on_exit` is enabled.
- [x] Exit-maintenance tests prove reorganization errors are surfaced as warnings
  and do not block transcript finalization.

## Stop Conditions

Stop and ask the user before continuing if:

- A required behavior conflicts with repository policy.
- A required behavior cannot be implemented without editing a frozen framework
  package.
- A parity decision requires product judgment rather than implementation
  judgment.
- A test requires real external provider credentials to pass.
- The task order should change for reasons not already documented here.
