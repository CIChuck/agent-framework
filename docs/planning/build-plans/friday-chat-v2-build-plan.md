# Friday Chat V2 Build Plan

This plan creates a new `packages/friday-chat` package that provides the
canonical Friday CLI app while preserving the feature surface of
`tests/integration/memory/friday.py`.

Related planning docs:

- `docs/planning/features/friday-v2-feature-inventory.md`
- `docs/planning/build-plans/friday-chat-v2-parity-matrix.md`
- `docs/planning/build-plans/friday-chat-v2-behavioral-contracts.md`
- `docs/planning/build-plans/friday-chat-v2-compatibility-testing-protocol.md`
- `docs/planning/build-plans/friday-chat-v2-framework-upgrade-log.md`

## Goal

Build FridayV2 as a clean package-level app over the existing Friday framework
packages. The app must preserve Friday prototype behavior without copying its
critical structural problems.

## Non-Goals

- Do not refactor `tests/integration/memory/friday.py` in place.
- Do not import production FridayV2 code from `tests/integration/memory`.
- Do not copy committed provider keys or local-machine config into package
  source.
- Do not reimplement memory, LLM, transcript, agent, workflow, speech, sandbox,
  telemetry, or tool primitives that already exist in framework packages.
- Do not recreate the dual command router from the prototype.
- Do not modify existing Friday framework packages during the FridayV2 parity
  implementation pass.

## Architecture

Create `packages/friday-chat` with this intended structure:

```text
packages/friday-chat/
  pyproject.toml
  src/friday_chat/
    __init__.py
    app.py
    cli.py
    config.py
    runtime.py
    session.py
    background.py
    shell.py
    replay.py
    exports.py
    security.py
    speech.py
    commands/
      __init__.py
      registry.py
      session.py
      memory.py
      transcript.py
      maintenance.py
      tools.py
      security.py
      speech.py
      orchestration.py
      workflow.py
      files.py
    turns/
      __init__.py
      processor.py
      streaming.py
      metrics.py
    tools/
      __init__.py
      loop.py
      registry.py
      schemas.py
  tests_chat/
    ...
```

Package responsibilities:

- `friday_chat.cli`: command-line entry point and argument parsing.
- `friday_chat.app`: app lifecycle, interactive loop, replay mode, shutdown.
- `friday_chat.config`: typed app config and env interpolation.
- `friday_chat.runtime`: config-to-runtime service construction, leaning on
  `friday-runtime`.
- `friday_chat.session`: lightweight session state holder, not a god object.
- `friday_chat.turns.processor`: normal chat turn pipeline.
- `friday_chat.tools.loop`: ReAct/function-calling loop.
- `friday_chat.commands`: single registry-based command system.
- `friday_chat.background`: supervised background tasks and shutdown.
- `friday_chat.shell`: optional shell access service.

## Package Dependencies

`friday-chat` may depend on:

- `friday-core`
- `friday-runtime`
- `friday-memory`
- `friday-llm`
- `friday-agent`
- `friday-tools`
- `friday-transcript`
- `friday-cli`
- `friday-speech`
- `friday-finance`

Use existing packages for core behavior. FridayV2 should orchestrate these
packages, not duplicate them.

## Framework Freeze

During the first FridayV2 parity implementation pass, existing framework
packages are frozen. FridayV2 may depend on them and adapt to their public
interfaces, but it must not change their source or tests while parity with
`tests/integration/memory/friday.py` is still being established.

Allowed implementation targets:

- `packages/friday-chat/`
- `packages/friday-chat/tests_chat/`
- Workspace metadata required to register and run `packages/friday-chat`.
- FridayV2 planning documents under `docs/planning/`.

Disallowed during the parity pass:

- Source or test edits under existing `packages/friday-*` packages other than
  `packages/friday-chat`.
- Contract changes in shared framework packages to make FridayV2 easier.
- Opportunistic cleanup of framework internals found while implementing
  FridayV2.

If a framework package lacks a needed capability, exposes a bug, has an awkward
interface, or needs a clearer type contract, record the request in
`docs/planning/build-plans/friday-chat-v2-framework-upgrade-log.md`. Each entry
must include source evidence, impact, the FridayV2 workaround, compatibility
risk, and suggested follow-up tests. Those changes belong to a secondary
framework-upgrade pass after FridayV2 parity is measurable.

## Design Rules

- Every command is registered once through one registry.
- Every async background task is created through `BackgroundTaskManager`.
- Shell execution is disabled by default or explicitly config-gated.
- Config enters the app as typed models.
- All runtime data defaults to ignored paths under a configurable data root.
- User-facing IO is abstracted enough for tests.
- The parity matrix is the implementation checklist.
- The behavioral contracts are the implementation rule source for command and
  subsystem semantics.
- `friday.py` is a behavioral reference, not a source file to copy wholesale.
- Existing framework packages are frozen during the parity pass; discovered
  framework changes go into the framework upgrade log.

## Implementation Phases

### Phase 0: Planning Gate

Deliverables:

- Complete feature inventory.
- Complete parity matrix.
- Complete behavioral contracts for all retained FridayV2 features and
  commands.
- This build plan.
- Framework upgrade log.

Acceptance:

- The feature inventory covers commands, turn processing, background tasks,
  persistence, config, shell, speech, security, orchestration, workflow, replay,
  file IO, and exports.
- The parity matrix has a row for every feature that could otherwise be lost.
- High-risk parity rows link to or are covered by behavioral contracts.
- The compatibility testing protocol defines automated proof for config,
  command, behavioral, replay, and safety parity.
- The framework upgrade log exists and is the required destination for any
  framework package change request discovered during FridayV2 implementation.

### Phase 1: Package Skeleton

Work:

- Add `packages/friday-chat`.
- Add package metadata and workspace dependency wiring.
- Add `friday-chat` console script.
- Add empty module layout.
- Add smoke tests for import and CLI help.

Acceptance:

- `uv sync --all-extras` recognizes `friday-chat`.
- `uv run friday-chat --help` works.
- `uv run pytest packages/friday-chat/tests_chat` passes.
- No production code imports from `tests/integration/memory`.
- No existing framework package source or test files are modified for FridayV2
  implementation.

### Phase 2: Typed Config And Runtime Factory

Work:

- Treat configuration compatibility with `tests/integration/memory/config.yaml`
  as a product requirement, not a convenience.
- Define typed config models for app, LLM, extraction, embedding, memory,
  passage routing, transcript, maintenance LLM roles, lifecycle, tools, web,
  smart file, finance, security, speech, logging, CLI, and Langfuse.
- Preserve the current Friday-py top-level config shape:
  `logging`, `llm`, `extraction`, `embedding`, `memory`, `transcript`, `chat`,
  `maintenance`, `lifecycle`, `smart_file`, `tools`, `web`, `langfuse`,
  `finance`, `security`, `session`, and `speech`.
- Implement a compatibility loader that accepts Friday-py-style YAML and
  normalizes it into FridayV2 typed models.
- Implement YAML loading and environment interpolation.
- Add `config.example.yaml` without secrets.
- Add a generated or maintained config traceability table that maps every
  supported top-level and nested key to a runtime consumer, compatibility
  handler, explicit deprecation record, or accepted-unused rationale.
- Implement runtime factory using existing framework packages and
  `friday-runtime` where possible.

Acceptance:

- Missing required config fails before service construction.
- Literal provider keys are absent from committed example config.
- Runtime factory can be tested with fake services.
- Secret/env interpolation has unit tests.
- A sanitized copy of the current prototype config shape loads successfully.
- Tests cover all top-level Friday-py config sections:
  `logging`, `llm`, `extraction`, `embedding`, `memory`, `transcript`, `chat`,
  `maintenance`, `lifecycle`, `smart_file`, `tools`, `web`, `langfuse`,
  `finance`, `security`, `session`, and `speech`.
- Tests cover key nested sections that drive behavior:
  `memory.retrieval`, `memory.priming`, `memory.cache`,
  `memory.supporting_context`, `memory.passage_router`,
  `memory.query_relevance_filter`, `memory.compaction`, `maintenance.llm`,
  `maintenance.prompts`, `tools.loop`, `tools.registry`, `tools.context`,
  `smart_file.llm`, `web.reader`, `security.sanitization`, and
  `speech.selection`.
- Traceability tests fail if a supported config key is not mapped to a consumer,
  compatibility handler, explicit deprecation record, or accepted-unused
  rationale.

### Phase 3: App Lifecycle And Session Shell

Work:

- Implement `FridayChatApp`.
- Implement `FridaySession` as a narrow state holder.
- Implement interactive loop with input abstraction.
- Implement transcript session creation/finalization.
- Implement supervised shutdown.

Acceptance:

- App can start with fake runtime and process EOF cleanly.
- Keyboard interrupt exits cleanly.
- Transcript finalization runs on normal exit and error exit.
- No unmanaged background tasks are left running in tests.

### Phase 4: Command Registry Foundation

Work:

- Build command registration modules.
- Port session/help commands first.
- Remove any fallback router concept from the design.

Acceptance:

- Every registered command appears in `/help`.
- `/help <command>` shows argument details.
- Unknown command behavior is tested.
- Registry tests prevent duplicate command registration.

### Phase 5: Basic Turn Processing

Work:

- Implement no-tool turn processor.
- Assemble context with `ContextAssembler`.
- Format prompts.
- Stream LLM responses.
- Persist `InteractionTurn`.
- Record timing and context metrics.

Acceptance:

- Fake LLM/fake memory tests cover a complete no-tool turn.
- Timeout, retry exhaustion, circuit breaker, and cancellation paths are tested.
- `/history`, `/memory`, `/context`, `/prompt`, `/debug`, `/debug-budget`, and
  `/timing` can run against fake or local stores.

### Phase 6: Transcript And Export Commands

Work:

- Port sessions, transcript, export, and prompt export commands.
- Extract export helpers.

Acceptance:

- Current and selected transcript display works.
- CSV, JSONL, Markdown, and training export formats are tested.
- Raw prompt export handles missing context logs gracefully.

### Phase 7: Tool Registry And Tool Loop

Work:

- Port tool loading without module-global registry state.
- Port startup auto-injection for `tools.context.include_in_context`.
- Implement tool commands.
- Implement tool loop service.
- Preserve or explicitly replace text tool-call fallback.
- Implement sanitization for LLM context and memory storage.
- Implement tool result tracking, truncation, pruning, lifecycle tracking, and
  vector ingestion.

Acceptance:

- Tool loop tests cover API tool calls, text tool calls if retained, missing
  tools, invalid categories, tool errors, consecutive failure breaker,
  max-iteration stop, truncation, and pair-preserving pruning.
- `/run-tool` tests cover both JSON parameters and plain-text parameter mapping.
- `/inject-tools` tests cover the chosen separator contract and any compatibility
  behavior for the prototype's whitespace/comma mismatch.
- Tool output sanitization stats are asserted.
- Tool command tests do not require real external services.

### Phase 8: Memory Inspection And Maintenance

Work:

- Port entities, insights, summaries, meta, vars, set, list-ingested.
- Port reset, reorganize, lifecycle, migrate, and compact.
- Implement maintenance service boundaries.

Acceptance:

- Dry-run is the default for destructive maintenance.
- Reset supports all stores and full reset.
- Lifecycle stats, optimize, flush, and execute paths are tested with fakes.
- Reorganize flags map exactly to prototype behavior, including
  `--force-reembed`, or documented changes.
- Migration resolves the prototype's flag mismatch: the registry advertises
  `--execute` and `--stats`, while the handler implements `--force`.

### Phase 9: Background Task Manager

Work:

- Implement `BackgroundTaskManager`.
- Route extraction, tool decay, graph maintenance, and compaction through it.
- Implement exit flush ordering.

Acceptance:

- Task failure is captured and visible in diagnostics.
- Shutdown can await or cancel tasks deterministically.
- Pending extraction flushes on exit.
- In-flight compaction gates the next turn when required.

### Phase 10: Files, Replay, And Shell

Work:

- Port `/read` and `/ingest`.
- Implement replay service and CLI replay mode.
- Implement config-gated shell service.

Acceptance:

- File reader dispatch supports txt/md/yaml/json/py/csv/tsv/pdf/docx/xlsx.
- Ingestion stores expected metadata.
- Replay resets memory and invokes the normal turn processor in CSV turn order.
- Shell is disabled by default.
- Shell tests cover enabled execution, timeout, stderr, and nonzero exit.

### Phase 11: Security And Speech

Work:

- Port security commands and runtime update behavior.
- Port speech configuration, prompt snippet, tag stripping, playback, streaming
  trigger, cancellation, and harness command.

Acceptance:

- Security config updates are rollback-safe and tested.
- Injection payload testing is local-validation only.
- Speech can be tested with fake adapters.
- Prompt snippet appears only when speech is enabled.
- Speech tags do not leak into terminal output when stripping is enabled.

### Phase 12: Orchestration And Workflows

Work:

- Port agent switching, listing, info, delegate, status, and `@agent` routing.
- Port workflow list/run/status/approve/skip.
- Make workflow directories configurable.

Acceptance:

- Orchestration commands pass against a fake `AgentOrchestrator`.
- Workflow commands pass against fake or fixture workflow definitions.
- Workflow approval/skip state transitions are tested.

### Phase 13: Parity Audit

Work:

- Walk the parity matrix row by row.
- Confirm every implemented row has a behavioral contract or an explicit
  simple-command exemption in `parity_overrides.yaml`.
- Mark each row `tested`, `verified`, `intentionally changed`, `deprecated`, or
  `deferred`.
- Add missing tests or implementation until no row remains `not started` or
  `in progress`.
- Run the full compatibility protocol.

Acceptance:

- Parity matrix is updated.
- `uv run pytest packages/friday-chat/tests_chat` passes.
- `uv run pytest packages/friday-chat/tests_chat/compat` passes.
- Targeted package tests for reused framework packages pass where touched.
- FridayV2 can run a local smoke session with fake or local-model config.

## Migration Strategy

Use vertical slices. Do not spend weeks building infrastructure before one
complete path works.

Recommended first working slice:

1. Package skeleton.
2. Typed config.
3. Fake runtime app lifecycle.
4. No-tool turn processing with fake LLM.
5. Transcript persistence.
6. `/help`, `/clear`, `/history`, `/memory`, `/context`, `/prompt`.

Then add the tool loop, maintenance, files, replay, speech, orchestration, and
workflow slices.

## Quality Gates

Each phase should satisfy:

- Tests for new behavior.
- Config changes update the config traceability table and compatibility tests.
- New or changed command behavior updates the behavioral contracts first.
- No production imports from `tests/integration/memory`.
- No checked-in secrets.
- No edits to existing framework package source or tests during the parity pass.
- Framework improvements discovered during implementation are logged in the
  framework upgrade log.
- No new `# mypy: ignore-errors` in `packages/*/src`.
- No reliance on `assert` for runtime invariants.
- Explicit exceptions for invalid config and invalid runtime state.
- Typed config/model boundaries instead of raw dicts spreading through the app.

## Open Decisions

- Whether text-parsed tool calls should remain supported or become an explicit
  compatibility mode.
- Whether shell access should be hidden, disabled by default, or moved behind a
  separate `--enable-shell` CLI flag.
- Whether `/migrate` should standardize on `--execute`, keep `--force`, or
  support both as compatibility aliases.
- Whether `/inject-tools` should standardize on whitespace-separated names,
  comma-separated names, or support both.
- Whether FridayV2 should accept every prototype config key indefinitely or
  define a documented compatibility window with warnings for deprecated keys.
- Whether FridayV2 should own its own console script name (`friday-chat`) before
  replacing the existing `friday` command.
- How much of `friday-runtime` should be extended before app-specific wiring
  lives in `friday-chat.runtime`.
- Whether `tests/integration/memory/friday_chat` should be deleted after useful
  code is ported.
