# FridayV2 Compatibility Testing Protocol

This protocol defines how FridayV2 will prove compatibility with the current
prototype CLI at `tests/integration/memory/friday.py` and its configuration file
at `tests/integration/memory/config.yaml`.

Compatibility testing is a release gate for FridayV2. The goal is not to compare
terminal output byte-for-byte; the goal is to compare stable contracts:
configuration acceptance, command surface, runtime artifacts, transcript
records, tool calls, memory operations, safety defaults, and replay behavior.

## Principles

- Production FridayV2 code must not import from `tests/integration/memory`.
- Tests may parse `tests/integration/memory/friday.py` and sanitized copies of
  `tests/integration/memory/config.yaml` as reference artifacts.
- Compatibility tests should prefer structured assertions over terminal output
  snapshots.
- Every intentional incompatibility must be represented in the parity matrix as
  `intentionally changed`, `deprecated`, or `deferred`.
- The compatibility suite must run unattended in CI with fake services wherever
  possible.
- Non-trivial command and subsystem behavior must trace to
  `docs/archive/completed/2026/friday-chat-v2/friday-chat-v2-behavioral-contracts.md`.

## Test Location

Create the compatibility suite under:

```text
packages/friday-chat/tests_chat/compat/
  test_config_compatibility.py
  test_command_surface_parity.py
  test_turn_contract_parity.py
  test_tool_loop_parity.py
  test_replay_parity.py
  test_safety_defaults.py
  test_contract_coverage.py
  fixtures/
    friday_py_config_sanitized.yaml
    replay_basic.csv
    parity_overrides.yaml
```

`parity_overrides.yaml` should list explicitly accepted differences, such as
deprecated commands, renamed flags, intentionally safer defaults, and
simple-command exemptions for retained commands that need no behavioral contract
beyond command registration and dispatch.

## Layer 1: Config Compatibility

Reference artifacts:

- `tests/integration/memory/config.yaml`
- `tests/integration/memory/cli-config.yaml`
- `tests/integration/memory/friday.py:7102`
- `tests/integration/memory/friday.py:7121`
- `tests/integration/memory/friday.py:7355`
- `tests/integration/memory/friday.py:6325`
- `tests/integration/memory/friday.py:6376`
- `tests/integration/memory/friday.py:6413`
- `tests/integration/memory/friday.py:6440`
- `tests/integration/memory/friday.py:6630`
- `tests/integration/memory/friday.py:6653`
- `tests/integration/memory/friday.py:7542`
- `tests/integration/memory/friday.py:7762`
- `tests/integration/memory/friday.py:7782`

Test goals:

- FridayV2 accepts the Friday-py-style config shape without forcing users to
  restructure the file.
- FridayV2 normalizes that config into typed models.
- FridayV2 loads the companion CLI display config used by the reference CLI.
- FridayV2 shows heartbeat/progress feedback while waiting for model responses.
- FridayV2 initializes the command-line session with the configured
  `chat.system_prompt`.
- Secrets use environment placeholders in fixtures and examples.
- Every supported config key is traceable.

Required tests:

- Load sanitized Friday-py config fixture successfully.
- Load minimal config successfully.
- Fail clearly on missing required `llm` configuration.
- Resolve environment placeholders for API keys, base URLs, and provider
  secrets.
- Reject or warn on unknown keys according to the chosen compatibility policy.
- Report deprecated or renamed keys with actionable diagnostics.
- Verify every top-level section has a typed model or compatibility handler:
  `logging`, `llm`, `extraction`, `embedding`, `memory`, `transcript`, `chat`,
  `maintenance`, `lifecycle`, `smart_file`, `tools`, `web`, `langfuse`,
  `finance`, `security`, `session`, and `speech`.
- Verify high-value nested sections are mapped:
  `memory.retrieval`, `memory.priming`, `memory.cache`,
  `memory.supporting_context`, `memory.passage_router`,
  `memory.query_relevance_filter`, `memory.compaction`, `maintenance.llm`,
  `maintenance.prompts`, `tools.loop`, `tools.registry`, `tools.context`,
  `smart_file.llm`, `web.reader`, `security.sanitization`, and
  `speech.selection`.
- Auto-load `cli-config.yaml` from the same directory as `--config` when present.
- Verify an explicit `--cli-config` override wins over sibling auto-discovery.
- Verify missing CLI display config falls back to defaults.
- Verify no-tool conversation turns start a thinking heartbeat after prompt
  submission and stop it on first streamed chunk.
- Verify no-tool heartbeat cleanup on completion without chunks, cancellation,
  timeout, retry exhaustion, circuit-breaker failure, and unexpected errors.
- Verify tool turns use a thinking heartbeat for the first model call and
  tool-processing heartbeats for later model calls.
- Verify heartbeat spinner type, style, randomization, thinking messages, and
  tool messages come from the effective CLI display config.
- Verify command-line startup uses `chat.system_prompt` for the effective
  system prompt, transcript/session metadata, prompt formatting, context-budget
  calculation, `/prompt`, and `/debug`.
- Verify speech prompt augmentation starts from the configured base prompt and
  can be disabled without losing that base prompt.

Acceptance:

- Config compatibility tests pass without external LLM, embedding, speech, web,
  finance, or telemetry services.
- The sanitized fixture is committed; real secrets are not.
- A config traceability table or equivalent machine-readable mapping exists and
  is checked by tests.
- CLI display config and startup system-prompt compatibility tests run without a
  real terminal or provider credentials.
- Heartbeat compatibility tests use fake display/indicator adapters and do not
  depend on terminal animation timing.

## Layer 2: Command Surface Parity

Reference artifact:

- `tests/integration/memory/friday.py`

Test goals:

- FridayV2 exposes every retained Friday command and alias.
- FridayV2 help is generated from the same command registry used for dispatch.
- Intentional differences are explicit and machine-checkable.

Required tests:

- Parse `friday.py` registry calls to extract command names and aliases.
- Include fallback-only commands from the prototype: `/debug-retrieval` and
  `/list-ingested`.
- Compare extracted command names against FridayV2 command registry.
- Confirm all retained commands appear in `/help`.
- Confirm `/help <command>` exists for every retained command.
- Confirm categories are present for session, memory, transcript, maintenance,
  testing, tools, security, speech, orchestration, workflows, and files.
- Confirm known prototype inconsistencies are covered:
  `/migrate --force` versus advertised `--execute`/`--stats`, and
  `/inject-tools` whitespace versus comma-separated name handling.

Acceptance:

- Missing commands fail the test unless listed in `parity_overrides.yaml`.
- Added FridayV2-only commands are allowed, but must be categorized and tested.

## Layer 3: Behavioral Contract Parity

Reference artifacts:

- `tests/integration/memory/friday.py:6009`
- `docs/archive/completed/2026/friday-chat-v2/friday-chat-v2-behavioral-contracts.md`

Test goals:

- FridayV2 preserves the turn-processing contract without requiring real
  providers.
- Tests compare structured artifacts, not terminal paint.
- Behavioral contracts are test inputs. Each non-trivial command or subsystem
  contract should have at least one compatibility assertion or an explicit
  deferred status.

Use fakes for:

- LLM chat completion and streaming.
- Embeddings.
- Tool registry and tool execution.
- Transcript store.
- Vector, graph, and episodic stores.
- Speech adapters.
- Orchestrator and workflow engine.
- Background task scheduler when testing command behavior.

Required tests:

- Contract coverage test maps retained parity rows to behavioral contract
  sections or explicit simple-command exemptions in `parity_overrides.yaml`.
- A no-tool turn initializes session state, assembles context, formats a prompt,
  calls the streaming LLM, persists an `InteractionTurn`, records timing, and
  increments turn count.
- A tool turn calls the tool loop, records tool calls/results, sanitizes output,
  truncates oversized results, and preserves tool-call/tool-result pairs.
- A normal conversation turn preserves structured provider tool calls, executes
  the configured tool, feeds the result back into the model, and returns
  non-empty final content.
- A date/time tool scenario proves asking for the date executes the configured
  date/time tool.
- A tool-call-only model response never becomes an empty assistant response.
- The actual model message payload includes the effective system prompt,
  assembled supporting context, current-session history, active tools, current
  query, and turn count where configured.
- By the fourth or fifth turn, a summary request receives earlier conversation
  turns in model context and cannot be treated as the first turn.
- Raw prompt capture stores the same message payload that was sent to the model.
- Background extraction tests prove every persisted turn is buffered and positive
  interval extraction processes the full buffered batch.
- Exit-flush tests prove interval `-1` buffers turns and extracts them on exit
  when configured.
- Real-runtime maintenance tests prove extraction/summarization/lifecycle/
  compaction are wired to real services or the framework-upgrade gap is logged.
- Budget-aware compaction tests prove `memory.compaction.enabled` initializes the
  real budget monitor and compactor when framework dependencies are available.
- Budget-aware compaction tests prove actual prompt budget status is recorded
  after each successful persisted turn, threshold breach schedules background
  compaction, pending extraction flushes before compaction, budget context and
  time-budget values reach the compactor, completion is marked on success or
  failure, and the next chat prompt waits for in-flight compaction.
- Exit reorganization tests prove `session.reorganize_on_exit` runs real
  reorganization cleanup before transcript finalization when a persistence
  directory exists.
- Reorganization mode tests prove `reorganize_mode: fast` skips synthesis and
  verification, while full/deep modes wire configured maintenance LLM roles.
- Reorganization failure tests prove warning-level diagnostics are surfaced and
  transcript finalization still runs.
- LLM timeout, retry exhaustion, circuit breaker, and cancellation produce
  user-facing errors without corrupting state.
- `/context`, `/prompt`, `/debug`, `/debug-budget`, `/timing`, `/history`, and
  `/memory` read the same structured state the turn processor writes.
- `/reset` clears the requested stores and preserves/archives transcript state
  according to the command contract.
- `/lifecycle`, `/reorganize`, `/migrate`, and `/compact` call the expected
  maintenance services with dry-run defaults where applicable.
- `/read` dispatches supported file formats.
- `/ingest` chunks content and stores protected document metadata.
- `/security` and `/security-test` update and report sanitizer statistics.
- `/speech` updates config with rollback on invalid values.
- Orchestration and workflow commands operate against fake agent/workflow
  services.

Acceptance:

- Tests assert structured outputs, method calls, persisted records, and state
  transitions.
- Contract coverage is traceable from parity-matrix row to behavioral contract
  to test.
- No test requires a network call or real provider key.

## Layer 4: Replay Parity

Reference artifacts:

- `tests/integration/memory/friday.py:3124`
- `tests/integration/memory/friday.py:7924`

Test goals:

- FridayV2 replay mode processes exported transcript CSVs through the normal
  turn pipeline.

Required tests:

- Load replay CSV and sort turns by turn number.
- Ignore empty user messages.
- Reset memory before replay.
- Process each user prompt through the normal turn processor.
- Honor optional delay through a fake clock or patched sleep.
- CLI replay mode exits after completion.
- Replay output reports expected turn count and summary.

Acceptance:

- Deterministic fake LLM responses produce stable transcript artifacts.
- Replay tests are runnable in CI.

## Layer 5: Safety Defaults

Test goals:

- FridayV2 does not inherit unsafe prototype defaults accidentally.

Required tests:

- Shell access is disabled by default or requires explicit config/CLI opt-in.
- Example config contains no literal provider keys.
- Runtime data defaults to ignored paths outside package source.
- Tool output sanitization is enabled according to config and applied before
  LLM context and memory storage.
- Unknown tools, missing tool categories, invalid command args, invalid config,
  and unsafe shell settings fail with explicit errors.
- Background tasks are supervised, and shutdown awaits or cancels tracked work.

Acceptance:

- Safety-default tests are part of the normal compatibility suite.
- Any intentional relaxation must be documented in the parity matrix.

## Automation

Local command:

```bash
uv run pytest packages/friday-chat/tests_chat/compat
```

Recommended CI job:

```bash
uv sync --all-extras
uv run pytest packages/friday-chat/tests_chat/compat
uv run pytest packages/friday-chat/tests_chat
```

The CI compatibility job should become required before FridayV2 is considered
canonical.

## Traceability Workflow

1. Add or change a FridayV2 feature.
2. Update `friday-chat-v2-parity-matrix.md`.
3. Add or update the behavioral contract for that row.
4. Update config traceability if any config key changes.
5. Add or update compatibility tests.
6. Run the compatibility suite.
7. Mark the relevant parity row as `tested` or `verified` only after tests pass.

## Completion Criteria

FridayV2 compatibility is complete when:

- Every parity matrix row is `tested`, `verified`, `intentionally changed`,
  `deprecated`, or `deferred`.
- Config compatibility tests load the sanitized Friday-py config.
- Command parity tests pass with no unapproved omissions.
- Every implemented non-trivial parity row has a behavioral contract or an
  explicit simple-command exemption in `parity_overrides.yaml`.
- Behavioral contract tests cover normal turns, tool turns, maintenance,
  replay, shell safety, speech, orchestration, workflow, and file ingestion.
- The compatibility suite is automated in CI.
