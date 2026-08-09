# FridayV2 Behavioral Contracts

This document defines the behavior FridayV2 must preserve from the reference CLI
at `tests/integration/memory/friday.py`. The feature inventory says what exists;
this file says how the feature must behave.

FridayV2 implementation should not treat a parity-matrix row as ready to build
until the row is covered here or is explicitly listed as a simple command with
no additional business rules in the compatibility suite's
`parity_overrides.yaml` fixture.

## Contract Rules

- Reference behavior comes from `tests/integration/memory/friday.py`.
- FridayV2 should preserve behavior unless the parity matrix records an
  `intentionally changed`, `deprecated`, or `deferred` decision.
- Terminal styling does not need byte-for-byte parity. Runtime state changes,
  service calls, persistence artifacts, command modes, error behavior, and
  safety defaults do need parity.
- Tests should assert structured state, service calls, records, and flags before
  asserting display text.
- Existing framework packages are frozen during the parity pass. Missing
  framework support must be logged in
  `docs/planning/build-plans/friday-chat-v2-framework-upgrade-log.md`.

## Contract Template

Use this shape when adding or refining a contract:

```text
Contract:
Reference:
Inputs:
Config keys:
Preconditions:
Runtime service calls:
State changes:
Output contract:
Error behavior:
Compatibility decision:
Required tests:
```

## Runtime And Configuration

### Config Loading

Reference: `friday.py:7071`, `friday.py:7102`, `friday.py:7121`,
`tests/integration/memory/config.yaml`

Required behavior:

- Accept the current Friday-py top-level section names:
  `logging`, `llm`, `extraction`, `embedding`, `memory`, `transcript`, `chat`,
  `maintenance`, `lifecycle`, `smart_file`, `tools`, `web`, `langfuse`,
  `finance`, `security`, `session`, and `speech`.
- Preserve the full active YAML option path surface from
  `tests/integration/memory/config.yaml` for first-pass migration. The
  FridayV2 example config and sanitized compatibility fixture must remain
  path-equivalent to that reference config.
- Normalize YAML into typed FridayV2 config models before constructing runtime
  services.
- Preserve config shape for the first migration. Renames must be additive or
  handled by a compatibility adapter.
- Reject missing required LLM config before constructing services.
- Load secrets from environment or ignored local files, not committed examples.
- Produce actionable diagnostics for unknown, deprecated, renamed, missing, or
  incompatible fields.
- Maintain a machine-checkable config traceability map. Every supported key must
  map to a runtime consumer, command, compatibility handler, deprecation record,
  or accepted-unused rationale.

Required tests:

- Sanitized copy of `tests/integration/memory/config.yaml` loads successfully.
- Sanitized fixture and `packages/friday-chat/config.example.yaml` contain the
  same active YAML option paths as `tests/integration/memory/config.yaml`.
- Minimal config loads successfully.
- Missing required LLM config fails before runtime creation.
- Env placeholders resolve for API keys and base URLs.
- Unknown/deprecated key policy is tested.
- Traceability check fails for unmapped supported keys.

### CLI Display And Startup Prompt Config

Reference: `tests/integration/memory/cli-config.yaml`, `friday.py:7102`,
`friday.py:7355`, `friday.py:6325`, `friday.py:6376`, `friday.py:6413`,
`friday.py:6440`, `friday.py:6630`, `friday.py:6653`, `friday.py:7542`,
`friday.py:7762`, `friday.py:7782`, `friday.py:4400`

Required behavior:

- Treat `cli-config.yaml` as part of Friday CLI compatibility, not optional
  visual polish.
- When `--config <path>` is provided, auto-load `cli-config.yaml` from the same
  directory as `<path>` when it exists.
- Provide a FridayV2 `--cli-config <path>` override for non-sibling layouts.
- Use defaults when no CLI display config exists.
- Support typed config for `theme`, `icons`, `prompt`, and `spinner` settings
  from the reference CLI config.
- Render the startup greeting/banner before entering the interactive loop.
- Start a visible thinking heartbeat after prompt submission while waiting for a
  no-tool conversation response.
- Stop the no-tool heartbeat on the first streamed chunk, completion without
  chunks, cancellation, timeout, retry exhaustion, circuit-breaker failure, or
  unexpected error.
- During tool turns, use a thinking heartbeat for the first model call and a
  tool-processing heartbeat for later model calls.
- Stop every tool-turn heartbeat in a cleanup path before processing returned
  tool calls or surfacing errors.
- Source heartbeat spinner type, message lists, styles, and randomization from
  the effective CLI display config.
- Initialize the base system prompt from `chat.system_prompt` during
  command-line startup.
- Use the same configured base prompt for transcript/session metadata, prompt
  formatting, context-budget calculation, `/prompt`, and `/debug`.
- Apply speech prompt augmentation only when speech is enabled, and restore the
  base configured prompt when speech is disabled.
- Do not hard-code `"You are Friday."` or `"You are a helpful assistant."` in any
  command-line startup path when `chat.system_prompt` is configured.

Required tests:

- Auto-discovery loads sibling `cli-config.yaml`.
- Explicit `--cli-config` wins over sibling auto-discovery.
- Missing CLI display config falls back to defaults.
- Startup banner/greeting output is testable with a fake console sink.
- No-tool conversation heartbeat starts before the model call and stops on first
  streamed chunk.
- No-tool heartbeat cleanup is tested for cancellation and model-call failure.
- Tool-turn heartbeat tests prove first-call thinking messages and later-call
  tool-processing messages.
- Heartbeat config tests prove spinner settings come from the effective
  `cli-config.yaml`.
- Startup system prompt equals `chat.system_prompt` before speech augmentation.
- Speech enable/disable updates the effective prompt without losing the base
  configured prompt.
- Transcript/session metadata persists the configured system prompt.
- Turn prompt formatting, context-budget calculation, `/prompt`, and `/debug`
  all use the effective configured system prompt.

### Config Surface Keys

Reference: `tests/integration/memory/config.yaml`

Top-level sections that must remain migration-compatible:

- `logging`
- `llm`
- `extraction`
- `embedding`
- `memory`
- `transcript`
- `chat`
- `maintenance`
- `lifecycle`
- `smart_file`
- `tools`
- `web`
- `langfuse`
- `finance`
- `security`
- `session`
- `speech`

High-value nested sections that must be explicitly traced:

- `memory.retrieval`
- `memory.priming`
- `memory.cache`
- `memory.supporting_context`
- `memory.passage_router`
- `memory.query_relevance_filter`
- `memory.compaction`
- `maintenance.llm`
- `maintenance.prompts`
- `tools.loop`
- `tools.registry`
- `tools.context`
- `smart_file.llm`
- `web.reader`
- `security.sanitization`
- `speech.selection`

Required tests:

- Contract coverage tests verify these names remain present in the config
  traceability mapping.
- Config compatibility tests load representative values for each high-value
  nested section.

### Runtime Assembly

Reference: `friday.py:7530`, `friday.py:7782`, `friday.py:7817`

Required behavior:

- Compose LLM, embedding, memory stores, transcript store, context assembler,
  extractor, tool registry, workflow engine, speech service, maintenance LLMs,
  lifecycle services, and compaction services from typed config.
- Use existing framework packages for core behavior.
- Configure maintenance LLM roles independently when configured, falling back to
  the main chat LLM per role when omitted.
- Configure maintenance embedding independently when configured, falling back to
  the session embedding service on setup failure.
- If `tools.context.include_in_context` is enabled, activate all configured tool
  schemas at startup.
- Workflow directory must be configurable, not hard-coded to the prototype path.

Required tests:

- Runtime factory builds against fakes without provider calls.
- Tool auto-injection honors config.
- Maintenance LLM fallback roles are visible in diagnostics.
- Workflow directory override is honored.

## App Lifecycle

Reference: `friday.py:7968`, `friday.py:8003`, `friday.py:8026`

Required behavior:

- Start a single-line prompt loop after runtime construction.
- Empty input is ignored.
- Slash commands are dispatched through the command registry.
- `@agent_name ...` routes through orchestration when the orchestrator exists.
- Non-command input runs the normal turn processor.
- `/exit`, `/quit`, and `/q` return an app-level exit signal.
- On exit, run configured exit maintenance before final shutdown.
- Finalize transcript sessions on normal exit and exceptional exit.
- Shutdown must await or cancel tracked background tasks intentionally.

### Runtime Session Identity

- A production invocation owns one immutable `SessionIdentity`, generated once
  as `session_<unique-id>` unless a caller injects an explicit identity for a
  deterministic test or replay.
- The same identity is propagated through runtime construction, memory and
  transcript adapters, maintenance services, the app `FridaySession`, command
  handlers, and replay. It is not regenerated at any of those boundaries.
- Supplying both a typed identity and a string session id is allowed only when
  their values match. Identity disagreement fails explicitly instead of
  silently splitting persisted state.
- Transcript creation remains lazy, but the eventual persisted transcript id
  is the invocation identity. Existing transcript rows retain their original
  ids and remain independently queryable.

Required tests:

- EOF and keyboard interrupt exit cleanly.
- Exit maintenance flags control behavior.
- Transcript finalization runs on normal and error exits.
- No unmanaged task is left pending in app tests.

## Turn Processing

Reference: `friday.py:6009`, `friday.py:6310`, `friday.py:6567`,
`friday.py:6224`, `friday.py:6284`

Required behavior:

- Lazily initialize session state on first turn.
- Reset speech-spoken state at the start of each turn.
- Calculate dynamic context budget from system prompt and active tool
  definitions.
- Assemble context with query, session state, and dynamic budget limit.
- Format prompt using system prompt, assembled payload, configured context
  format, current user query, and current turn count.
- Send the formatted prompt/message payload to the LLM. The model call must not
  receive only the raw user message when context, system prompt, history, or
  tools are configured.
- Preserve current-session history across turns and include it in later prompt
  assembly according to `memory.max_history_turns`.
- Use the same prompt/message payload for raw prompt capture that was sent to the
  LLM.
- Record timing keys: `init`, `budget_calc`, `context_assembly`,
  `prompt_format`, `pre_llm_total`, `llm_call`, and `total`.
- Store final prompt messages for `/prompt` and `/debug`.
- Use streaming LLM path when no tools are active.
- Use non-streaming tool loop when active tools exist.
- Persist an `InteractionTurn` with user message, assistant message, tool calls,
  tool results, timing, token metrics, model, temperature, and raw
  prompt/response when configured.
- When raw prompt capture is enabled, also store a context-log entry for the
  turn.
- Add the persisted turn id to session turn tracking only after persistence
  succeeds.
- Increment session turn count after successful processing.
- Schedule tool decay, incremental graph maintenance, budget-aware compaction,
  and extraction through supervised background services in FridayV2.
- Buffer every turn for extraction. Flush the batch when the configured interval
  triggers; do not drop turns between intervals.

Error behavior:

- LLM timeout returns a user-facing timeout message and does not persist a
  partial successful turn.
- Retry exhaustion returns a service-unavailable style message.
- Circuit breaker returns a retry-later message.
- Cancellation returns no assistant turn and leaves state consistent.
- Transcript save failure reports a warning and does not add the turn id.

Required tests:

- No-tool turn with fake LLM and fake stores.
- Tool turn with fake tools.
- Multi-turn summary scenario proves prior turns are present in the fourth or
  fifth turn's model payload.
- Actual LLM call payload includes system prompt, supporting context, history,
  active tools, current query, and turn count where configured.
- Raw prompt capture on and off.
- Raw prompt capture matches the actual model message payload.
- Persistence failure path.
- Timeout, retry exhaustion, circuit breaker, and cancellation.
- Extraction interval values `0`, positive `N`, and `-1`.

## Command Registry

Reference: `friday.py:429`, `friday.py:1111`, `friday.py:5642`

Required behavior:

- FridayV2 must use one registry for help and dispatch.
- Registered commands and aliases must be the source for `/help`.
- General `/help` must group commands by category and render each command's
  aliases, short description, complete usage syntax, and structured argument
  details from registry metadata.
- Structured argument details must identify required and optional arguments and
  include declared defaults and choices.
- The legacy fallback router must not be recreated.
- Fallback-only prototype commands `/debug-retrieval` and `/list-ingested` must
  either be registered in FridayV2 or explicitly marked as changed.
- Unknown slash commands return an unknown-command response.

Required tests:

- Parse the prototype registry and compare with FridayV2 registry.
- Verify alias coverage.
- Verify `/help` and `/help <command>` are generated from registry metadata.
- Verify literal usage syntax such as `[command]` and `[json]` survives terminal
  rendering.
- Verify every registered command has non-empty category, description, and
  usage metadata, and every declared argument has a description.
- Duplicate command registration fails.

## Session Commands

Reference: `friday.py:437`, `friday.py:1237`

Contracts:

- `/exit`, `/quit`, `/q`: return app exit signal and do not run turn processing.
- `/clear`: clear `turn_ids`, pending extraction turns, `last_payload`, and
  session turn count if state exists. It does not clear persistent stores.
- `/cls`, `/clearscreen`: clear terminal through display abstraction and return
  an empty response. The app applies that typed effect exactly once. If no
  display boundary is configured, or the boundary fails, return a sanitized,
  honest unavailable/failure response instead of claiming success.
- `/help`: list commands grouped by category using the legacy verbose layout,
  including aliases, description, usage, and argument details.
- `/help <command>`: show category, usage, description, aliases, and structured
  argument details from registry metadata.

Required tests:

- Clear resets only in-session state.
- Help includes every registered command and alias.
- Clear-screen recording coverage does not require a real terminal; supported
  platform coverage also proves the production display writes terminal clear
  and home control sequences through a real PTY.

## Memory And Context Commands

Reference: `friday.py:1251`, `friday.py:1319`, `friday.py:1597`,
`friday.py:2728`, `friday.py:4052`

Contracts:

- `/history`: merge prior history from the last context payload with current
  session turns from episodic storage, prior turns first. Show counts for prior
  and current turns. Empty history returns a no-history message.
- `/memory`: report typed statistics across episodic, vector, graph,
  transcript, lifecycle, priming, session, and last-context metrics. A numeric
  zero is rendered only when the backing source returned zero. Unsupported,
  unconfigured, and failed sources retain honest typed availability or warning
  states and are never collapsed into fabricated zeroes.
- `/context`: show the last assembled context payload. If no payload exists,
  assemble or report that no context is available according to the final
  FridayV2 command design.
- `/context --debug`: include token and budget diagnostics per context section.
- `/context --file`: export context to the configured transcript export
  directory or safe default.
- `/prompt`: show complete last formatted prompt without truncation.
- `/prompt --file`: export complete prompt to file.
- `/prime`: call memory recall with empty query, current session id, and
  `include_history=True`; store the payload as `last_payload`; report counts for
  entities, known facts, insights, summaries, prior history, and current
  history.
- `/debug`: show context assembly debug data from the last payload and assembler.
- `/debug-budget`: show context window, output buffer, available budget, recent
  context token history, and budget utilization.
- `/debug-retrieval <query>`: run retrieval diagnostics for the supplied query;
  empty query should return usage.
- `/timing`: show the last-turn timing keys from the turn processor.
- `/entities`: list graph entities and relationship summaries.
- `/entities nodes`: show node-only detail.
- `/entities <name>`: show matching entity detail.
- `/insights`, `/summaries`, `/meta`: query public memory APIs and list typed
  records with structured metadata, provenance, and useful empty-state
  guidance. `/meta` merges active short-term and long-term meta insights,
  excludes decayed records, preserves source/derivation provenance, and does
  not synthesize, reorganize, or otherwise mutate memory. A partial store
  failure returns the available records plus a typed warning.
- `/vars`: show scoped variables or report none set.
- `/set <key> <value>`: require initialized session state, set the scoped var,
  and return confirmation.
- `/list-ingested`: list ingested file/source records or a useful empty state.

Required tests:

- Prior and current history merge order.
- Empty-state responses.
- File export paths are constrained to safe export roots.
- `/prime` stores payload for later `/context`.
- `/set` fails before session state exists and succeeds afterward.

## Transcript And Export Commands

Reference: `friday.py:2810`, `friday.py:2870`, `friday.py:2947`,
`friday.py:2989`, `friday.py:3049`

Contracts:

- `/sessions`: require the public transcript query boundary. List up to 1000
  persisted sessions in deterministic order, mark the current invocation
  identity, and mark sessions included in primed context based on
  `memory.priming.previous_sessions`.
- `/transcript`: query and show the persisted current-session entries.
- `/transcript <session_id>`: treat the supplied id as an untrusted bound query,
  then show the persisted selected-session entries or an honest no-entries
  message. The current and selected session identities remain distinguishable.
- `/transcript export`: export all transcript sessions to a timestamped
  subdirectory containing `sessions.csv` and `entries.csv`; archived sessions
  omitted by the public all-session query remain omitted from the export.
- `/export`: default to Markdown for persisted current-session entries.
- `/export csv`: write all-quoted CSV and report entry count.
- `/export jsonl`: write JSONL and report entry count.
- `/export markdown` or `/export md`: write Markdown using configured user and
  assistant names.
- `/export training`: write chat-format training JSONL.
- `/export-prompts [session_id]`: export context-log raw prompt/response data to
  JSON for current or selected session. If no context logs exist, tell the user
  to enable `transcript.capture_raw_prompts`.
- Transcript commands use public typed query/export APIs rather than copying or
  opening SQLite storage directly. Every export resolves beneath the configured
  export root, uses deterministic record ordering/counts, and rejects unsafe
  path escape.

Required tests:

- Missing transcript store returns configured error.
- Export formats call the expected exporter.
- Export paths are timestamped and safe.
- Prompt export handles missing context logs.

## Maintenance Commands

Reference: `friday.py:3238`, `friday.py:3361`, `friday.py:3708`,
`friday.py:3855`, `friday.py:3956`

### `/reset [store]`

Required behavior:

- Valid stores are `graph`, `vector`, and `episodic`.
- Unknown store returns valid options.
- Full reset clears graph, lifecycle/vector collections, legacy vector store,
  current episodic session, archives transcript sessions, clears all primed
  content, clears turn ids, clears pending extraction, and resets turn count.
- Selective reset clears only the requested store and current session primed
  cache. It does not reset turn ids or archive transcripts.
- Each store failure is reported independently; remaining stores still attempt
  to reset.

Required tests:

- Full reset calls every store and transcript archival.
- Selective reset calls only the selected store.
- Store failure appears in output without aborting later cleanup.

### `/reorganize ...`

Required behavior:

- Require a configured vector persistence directory; otherwise return an error.
- Default to a side-effect-free dry run. Only the exact `--execute` flag may
  authorize mutation; plain `execute`, `--no-backup`, duplicate, unknown, and
  incompatible flags are rejected.
- Route `--backup`, `--analyze`, `--dedupe`, `--prune`, `--synthesize`, and
  `--verify` to exactly that operation. With no mode flag, run the full typed
  pipeline. Full-only skip and re-embedding flags are invalid for single-step
  modes, and analyze rejects execute authorization.
- Use the app-owned coordinator for both manual and shutdown requests. Every
  mutating request must first create and verify one aggregate Friday Memory and
  Friday Transcript recovery bundle; there is no backup bypass.
- Authorize execution from one typed coordinator capability and the actual
  request. Backup and explicit recovery require Memory and Transcript recovery
  participants plus runtime quiescence hooks; mutating modes and configured
  exit full/fast/deep additionally require the mutation adapter. Explicit
  recovery remains available when mutation providers or adapters are absent.
  Legacy direct maintenance and standalone Friday Memory mutation/restore paths
  remain fail-closed.
- Include Transcript only in snapshot, rollback, and recovery. Transcript
  content is never analyzed, classified, pruned, synthesized, verified, or
  otherwise reorganized.
- Use only explicitly configured `maintenance.llm.<role>` and
  `maintenance.embedding` providers. The primary chat LLM, primary embedding,
  and DGX availability are never implicit maintenance fallbacks. Preflight only
  capabilities required by the selected mode and flags.
- Every maintenance LLM request includes the exact strict JSON Schema for its
  typed response. Parse the first valid JSON object from normal or reasoning
  content, reject schema violations with content-safe categorical errors, and
  prove synthesis sources and output counts remain bound to the fresh plan
  before embedding or mutation.
- Build synthesis candidates only from active, verified insight records. Group
  sources by vector collection and normalized topic, honor the configured
  minimum cluster size, and issue at most one bounded provider request per
  eligible group. Treat memory text in that request as untrusted data.
- Bound synthesis exposure before the provider call: no more than 128 topic
  groups and 512 source records per plan, 64 visible source records per group,
  6,000 characters per visible document, and 120,000 characters in one request
  payload. Report deferred or ineligible sources only through content-safe
  counts and warnings.
- Bind each synthesis group to a deterministic, versioned fingerprint of its
  collection, normalized topic, ordered source identifiers, and normalized
  source-document hashes. An existing fingerprint suppresses provider work;
  an unchanged second execute run must report synthesis `changed=0` and must
  not call the synthesis LLM or embedding provider.
- Permit the synthesis provider to abstain. Empty output, output below the
  configured confidence threshold, and an exact duplicate of an existing
  document are successful no-ops that do not invoke embeddings or mutation.
- Persist synthesized vector records as `meta_insight` with bounded canonical
  `source_memories` JSON, `source_count`, and
  `provenance_source_type=synthesis`, topic, confidence, reasoning, creation
  time, synthesis version, and fingerprint; verify that exact lineage and
  metadata as live-store postconditions without copying memory content into
  logs. Generate its stable record identifier from the fingerprint.
- Keep maintenance-generated synthesis out of normal retrieval until its
  verification status is `verified`; rejected, uncertain, and not-yet-verified
  synthesis remains available to explicit diagnostics and maintenance. A full
  run may synthesize and then verify in the same pipeline.
- Preserve legacy maintenance-generated `meta_insight` records. When bounded
  source lineage maps one unambiguously to a current group, backfill its topic,
  fingerprint, and synthesis version instead of creating another vector; the
  following unchanged plan must be a no-op.
- Report typed per-store and per-step outcomes. Preserve unavailable counts as
  unavailable, never as zero, and never convert nested failure evidence into a
  successful terminal state.
- Acknowledge accepted work before awaiting the coordinator and emit bounded,
  content-safe progress. Cancellation during an atomic section is reported as
  pending and takes effect at the next safe boundary.
- For active-session manual execution, register exclusive intent before
  cancelling supervised background writers. Distinguish turns that were merely
  buffered under the configured interval from unfinished turns restored by an
  actively preempted extractor. Flush committed memory state without a
  synchronous extraction-model retry. After the exclusive gate is released,
  resume an extractor preempted by that maintenance run exactly once on every
  terminal result, including verified rollback and preflight failure. Do not
  force normally buffered turns ahead of their configured trigger. Report the
  buffered, preempted, and unscheduled-resume states categorically without turn
  content.
- Show retained recovery-manifest, journal, and categorical owner-only log paths
  when they exist. Normal output and logs contain no memory or Transcript
  content, credentials, prompts, or raw provider responses.
- Support exact recovery inspection with `/reorganize --recover <run-id>` and
  exact restoration with `/reorganize --recover <run-id> --execute`. Restore the
  recorded verified bundle; never replace it with a snapshot of partially
  mutated state.

Error behavior:

- Coordinator results expose typed, content-safe error categories. Exceptions
  escaping an ordinary or recovery coordinator call render only a bounded
  exception type and generic recovery guidance; raw paths, provider responses,
  and exception messages are not printed in the REPL.

Required tests:

- Strict syntax and the complete mode/flag capability matrix.
- Dry-run idempotence and execute containment/authorization behavior.
- Mode-specific provider readiness, omission when unused, timeout, and sanitized
  failure without a live provider dependency.
- Real participant full execute, automatic rollback, rollback failure, restart
  detection, and explicit recovery against disposable stores.
- Provider-free PTY acknowledgement, bounded progress, cancellation-pending
  reporting, nullable metrics, and content-safe terminal output.
- Verified-source and collection/topic isolation, configured cluster and
  confidence thresholds, prompt guidance, bounded provider payloads, empty and
  low-confidence abstention, exact-duplicate suppression, and retrieval
  quarantine.
- Legacy-lineage metadata migration followed by an unchanged no-op plan, plus a
  disposable full execute repeated against the same stores that proves the
  second synthesis step reports `changed=0` with no additional vector, LLM, or
  embedding call.

Recovery and operator contract:

- Resolve vector, graph, optional access-buffer WAL, Transcript, recovery, and
  log paths once against the process working directory. Reject source/recovery/
  log overlap, symlink traversal, hard-link identity substitution, permission
  failure, inadequate capacity, unsupported lease semantics, and unfinished
  journals before mutation.
- Persist a schema-versioned owner-only journal before snapshot creation. Do not
  cross the mutation boundary until the checksum-bound aggregate bundle contains
  complete, verified Friday Memory and Friday Transcript participant manifests.
- Treat Chroma's recognized legacy `hnsw:*` collection metadata as configuration
  already represented by the exported schema, not as user metadata. Recovery
  canonicalizes those duplicate keys before public-API reconstruction while
  preserving every ordinary collection metadata field; newly created Friday
  collections use Chroma's modern configuration boundary.
- On post-mutation error or cancellation, restore and verify the exact retained
  bundle. Return `failed_rolled_back` only after verification. If restoration or
  verification fails, return `recovery_required`, retain the unfinished journal
  and bundle, and block ordinary mutation.
- On restart, surface unfinished run IDs. Inspection is read-only. Explicit
  recovery drains conflicting runtime state and restores only the bundle already
  bound into that journal.
- Recovery directories are owner-only (`0700`) and artifacts are owner-only
  (`0600`) on the verified POSIX platform. The reorganization log is a separate
  schema-versioned categorical envelope with the same restrictive permissions;
  operators follow its journal path for terminal details.
- Bundles, journals, and failed-run evidence are retained. This remediation does
  not automate retention or remove legacy/nested logs. Existing vector-only
  backups remain incomplete Friday Chat recovery artifacts and cannot be used as
  aggregate recovery bundles.
- Relative configuration retains its existing process-working-directory base;
  this remediation does not relocate or migrate on-disk state.

### `/lifecycle ...`

Required behavior:

- Require promotion service; otherwise return lifecycle-not-configured error.
- Default mode is dry-run promotion cycle. `--execute` mutates.
- `--stats` takes precedence and reports short-term, long-term, decayed, and
  access-buffer stats when available.
- `--flush` flushes access buffer only and requires access buffer.
- `--optimize` flushes access buffer if configured, recomputes retrieval factors
  if configured, and reports skipped steps when missing.
- Default cycle calls `run_promotion_cycle(dry_run=...)`, reports promoted,
  decayed, reactivated, errors, and current collection stats.

Required tests:

- Precedence of `--stats`, `--flush`, `--optimize`, and default cycle.
- Dry-run default.
- Missing access buffer in flush mode.
- Error classification mirrors `/reorganize`.

### `/migrate ...`

Required behavior:

- Require `persist_dir`; otherwise return an error.
- Prototype handler uses `--force` to execute even though registry advertises
  `--execute` and `--stats`.
- FridayV2 must support compatibility aliases or document an intentional
  command contract change in the parity matrix.
- Migration is non-destructive and idempotent.
- Dry-run checks if migration is needed and returns early when not needed.
- Report vector, graph node, and graph edge scanned/migrated/skipped counts and
  up to five errors.

Required tests:

- `--force` compatibility.
- Chosen handling for `--execute` and `--stats`.
- No-migration-needed dry-run path.
- Error classification.

### `/compact`

Required behavior:

- Require compactor and budget monitor.
- Refuse to start when compaction is already running.
- Flush pending extraction before compaction. If extraction flush fails, abort
  compaction and preserve pending turns.
- Run synchronously with trigger reason `manual_command`.
- Pass current tokens, available budget, target utilization, and time budget.
- Mark compaction started and complete.
- Report turns summarized, tokens saved versus target, target met, insights
  deduplicated, memories promoted, duration, time-budget exhaustion, and up to
  five errors.

Required tests:

- Disabled compaction messages.
- Already-running guard.
- Extraction flush failure preserves pending turns and skips compactor.
- Successful call passes budget context.

## Replay

Reference: `friday.py:3124`, `friday.py:3194`, `friday.py:7924`

Required behavior:

- `/replay <csv_path> [delay_seconds]` replays an exported transcript through
  the normal Friday turn pipeline.
- Load CSV with `csv.DictReader`.
- Extract rows with non-empty `user_message`.
- Preserve `assistant_message` in loaded turn records for diagnostics, but
  process only user messages.
- Convert `turn_number` to integer and sort by turn number.
- Missing CSV raises file-not-found message.
- Invalid delay returns a numeric-delay error.
- Empty transcript returns no-user-messages message.
- Before replay, run full `/reset` for clean slate and print reset output.
- Process each user message through the normal turn processor.
- Honor delay between turns except after the final turn.
- CLI replay mode exits after replay completes.

Required tests:

- CSV ordering.
- Empty rows ignored.
- Missing file, invalid delay, empty CSV.
- Reset-before-replay.
- Delay through fake sleep.
- Normal turn processor invoked for every replay message.

## Tool Commands And Tool Loop

Reference: `friday.py:4068`, `friday.py:4117`, `friday.py:4231`,
`friday.py:6567`, `friday.py:6819`

### Tool Commands

Required behavior:

- `/tools [category]`: list schemas grouped by category. Unknown category
  returns available categories.
- `/run-tool`: require registry; require known tool; parse JSON when params
  begin with `{`; otherwise map plain text to a parameter using priority:
  `message`, exactly one required parameter, then first available parameter
  when the schema has one parameter or has no required parameters. Validate
  params before execution.
- `/run-tool` must reject tools with no parameter schema for plain text input.
- `/run-tool` must reject tools with missing or `uncategorized` category.
- `/run-tool` sanitizes output, updates security stats, and returns sanitized
  result.
- `/inject-tools`: accept whitespace-separated names for prototype
  compatibility, with tested comma-separated support. Resolve every requested
  name before mutation and atomically set manual selection only when the exact
  canonical schema set fits both configured count and token-budget bounds.
  Unknown, duplicate, or over-budget requests leave the prior selection intact.
- `/clear-tools`: clear pending manual selection and restore automatic
  per-turn selection. It does not disable configured tools.
- `/recommend-tools`: require query, call assembler recommendation against all
  schemas with `top_k=5`, and show score, confidence, category, reason, and
  suggested parameters.
- `/tool-budget`: report authoritative selection state, including mode,
  configured limits, pending manual selection, latest successful automatic
  selection, last completed selection, executed-tool count, canonical schema
  token estimate, and names/categories. It distinguishes zero-budget,
  no-registered-tools, no-match, and cleared/manual states without claiming
  that a previous schema set will be sent on the next turn.
- Automatic selection is query-aware and computed for each turn from the
  registered tool definitions. The immutable resulting budget snapshot is used
  unchanged for context budgeting and the exact model tool-schema payload.
- Manual selection persists across turns until `/clear-tools`; automatic
  selection resumes immediately after clear. A zero tool budget yields an empty
  schema set without invoking or disabling the registry.

Required tests:

- JSON and plain-text mapping priorities.
- Invalid JSON and validation errors.
- Missing registry, unknown tool, uncategorized tool.
- Sanitization stats update.
- Whitespace and chosen comma compatibility for `/inject-tools`.

### Tool Loop

Required behavior:

- Tool-enabled turns use non-streaming LLM calls with active tool schemas.
- LLM adapters must preserve structured tool-call responses. A tool-call-only
  provider response must not be reduced to an empty assistant message or a
  non-executable text placeholder.
- Loop settings come from `tools.loop`: `max_iterations`,
  `max_consecutive_failures`, `max_tool_messages`, and
  `max_tool_result_chars`.
- Accumulate prompt, completion, and total token usage across loop iterations.
- If the provider returns function calls, normalize them into tool call records.
- If no API tool calls are returned and text fallback is retained, parse
  `tool_name(arg=value)` style calls only for active tool names.
- FridayV2 does not retain model-output text-parsed tool calls in the initial
  parity implementation. Tool execution is driven by explicit provider
  function-call records or direct `/run-tool` command invocation. This avoids
  ambiguous assistant-text parsing while preserving prototype command
  compatibility for plain-text `/run-tool` parameters.
- Preserve provider `reasoning_content` on assistant tool-call messages.
- Execute tool calls in order.
- Feed sanitized tool results back into the working model message list and
  continue the loop until final content or max iterations.
- A normal conversation turn that asks for date/time must execute the configured
  date/time tool and return a non-empty assistant answer.
- Append test injection payload to the next tool result when configured, then
  clear the payload.
- Require every tool to exist and declare a non-default category.
- Sanitize tool output separately for LLM context and memory storage. LLM
  context may include wrappers; memory storage must not.
- Update security stats: total scans, detections, blocked count, and patterns
  seen.
- Track tool calls and tool results for transcript persistence.
- Track large successful outputs for lifecycle management.
- Ingest successful tool outputs for cross-session retrieval with source path
  from `path` or `file_path` arguments where available.
- Truncate tool output passed back to the LLM when over configured maximum and
  report truncation.
- Preserve assistant tool-call and tool-result pairs when pruning messages.
- Consecutive tool execution failures trigger circuit breaker and return metrics
  with partial calls/results.
- Max iterations returns a user-facing apology and metrics.

Required tests:

- API tool calls and optional text-parsed calls.
- Tool-call-only provider response is preserved and executed.
- End-to-end date/time tool scenario.
- Reasoning content preservation.
- Tool error circuit breaker.
- Truncation.
- Pair-preserving pruning.
- Separate sanitization outputs.
- Tool output lifecycle and ingestion calls.

## Security Commands

Reference: `friday.py:4375`, `friday.py:4606`, `friday.py:4687`,
`friday.py:4733`

Contracts:

- `/security`: show enabled state, detection sensitivity, quarantine action,
  wrapping mode, scan counts, detections, blocked count, and patterns seen.
- `/security-test [type]`: run local sample payloads for `instruction`,
  `delimiter`, `jailbreak`, `exfil`, or `all`; report detection and sanitized
  result.
- `/security-config sensitivity <value>`: update detection sensitivity and
  refresh embedding sanitizer.
- `/security-config action <value>`: update quarantine action.
- `/security-config wrapping <style|off>`: enable wrapping with style or disable
  wrapping with `off`.
- Invalid runtime security config must roll back to the previous valid config.
- `/inject-payload <payload>`: store one payload to append to the next tool
  result, then clear it after use.

Required tests:

- Security stat counters.
- Runtime config update success and rollback.
- Payload is single-use.
- Embedding sanitizer has wrapping disabled even when LLM-context wrapping is
  enabled.

## Speech

Reference: `friday.py:4381`, `friday.py:4450`, `friday.py:4510`,
`friday.py:4745`, `friday.py:4782`, `friday.py:6355`

Required behavior:

- Speech config is parsed through `friday-speech` when refreshed.
- Speech service exists only when config is enabled.
- Enabling speech appends speech tag instructions to the base system prompt;
  disabling speech restores the base prompt.
- Terminal display strips include/exclude speech tags.
- Speakable text is cleaned by removing leading ISO timestamps, bracketed
  metadata, and assistant-name prefixes.
- Streaming speech starts once when live mode and playback are enabled.
- Snippet selection order:
  include-tag content if complete, partial include-tag content if open tag has
  appeared, `streaming_min_words`, `streaming_min_chars`, `first_sentence`,
  `first_n_words`, otherwise no streaming snippet. Strategy `all` does not
  produce a streaming snippet.
- Playback can be blocking or background based on config.
- Starting a speech task cancels any previous speech task.
- `Ctrl+Q` cancels playback.
- Runtime speech updates use rollback on validation failure.
- `/speech` defaults to config display.
- `/speech on|off` toggles enabled state.
- `/speech mode live|file`, `/speech voice <voice_id>`, and
  `/speech provider elevenlabs|picovoice` update config with validation.
- `/speech-test [once|loop]` requires enabled speech and runs the harness.

Required tests:

- Prompt snippet added and removed.
- Tag stripping and text cleaning.
- Streaming snippet selection strategies.
- Runtime update rollback.
- Cancellation and task replacement.
- Speech harness disabled/enabled paths with fake adapters.

## Orchestration

Reference: `friday.py:1114`, `friday.py:4865`, `friday.py:5399`

Contracts:

- `@agent_name <message>` routes only when the orchestrator exists.
- `/switch [agent]`: without agent shows current active agent status; with agent
  switches active agent or returns routing error.
- `/agents`: list agents, capabilities, active marker, and cached state.
- `/agent [name]`: show selected or active agent details.
- `/delegate <agent> <task>`: delegate to target agent and restore the previous
  active agent afterward.
- `/status`: show orchestrator status including active agent, cache state, and
  message count.

Required tests:

- Missing orchestrator behavior.
- Switch and restore semantics.
- At-routing success and unknown agent.
- Delegate restores prior active agent on success and failure.

## Workflows

Reference: `friday.py:5066`

Contracts:

- `/workflow` without subcommand should show usage or list behavior defined by
  the final FridayV2 registry contract.
- `/workflow list`: list available workflow definitions.
- `/workflow run <name> [inputs]`: start workflow through workflow engine.
- `/workflow status [id]`: show workflow status and pending approvals.
- `/workflow approve <id>`: approve pending step.
- `/workflow skip <id>`: skip pending step.
- Missing workflow directory or engine returns workflow-not-enabled messages.
- Workflow directory must be configurable.

Required tests:

- Disabled workflow messages.
- List/run/status/approve/skip with fake engine.
- Pending approval state transitions.

## File Commands

Reference: `friday.py:5423`, `friday.py:5507`

Contracts:

- `/read <path> [--lines=N]`: resolve relative path against current working
  directory, require existing file, reject directories, choose reader through
  `ReaderFactory`, and pass optional limit.
- Supported formats: txt, md, yaml, json, py, csv, tsv, pdf, docx, xlsx.
- Output includes file name, reader name, encoding, page count, row count,
  column count, sheet names, truncation marker, and content when available.
- Legacy parser treats malformed `--lines` as limit `100`. FridayV2 may improve
  parsing only if the compatibility decision is documented.
- `/ingest <path> [description]`: read file through smart reader, chunk if
  needed, store vector-memory records with source metadata, and report ingestion
  counts. Missing path or unsupported file should return actionable errors.

Required tests:

- Relative path resolution.
- Missing file and directory errors.
- Reader dispatch per supported extension using fakes.
- Line limit and malformed limit compatibility.
- Ingest metadata includes source path and optional description.

## Shell Access

Reference: `friday.py:7000`, `friday.py:7973`

Required behavior:

- Prototype accepts `!<command>` in the interactive loop and executes a shell
  command with timeout.
- FridayV2 must not enable shell execution by default. Shell execution must be
  disabled by default or require explicit config/CLI opt-in.
- When enabled, shell execution must run through a service boundary with
  working-directory, timeout, stdout, stderr, and nonzero-exit behavior tested.
- Disabled shell access should return an explicit user-facing error.

Required tests:

- Disabled default.
- Enabled success.
- Timeout.
- Stderr and nonzero exit.
- Working-directory policy.

## Background Work And Exit Maintenance

Reference: `friday.py:1441`, `friday.py:5752`, `friday.py:5779`,
`friday.py:5832`, `friday.py:5923`, `friday.py:5938`, `friday.py:5974`,
`friday.py:6224`, `friday.py:6237`, `friday.py:7870`, `friday.py:7989`,
`friday.py:8003`

Required behavior:

- Extraction interval rules:
  `0` means every turn, positive `N` means turns divisible by `N`, and `-1`
  means only on exit.
- Every successfully persisted turn is buffered for extraction before the
  interval rule is evaluated.
- Positive interval `N` extracts all buffered turns when the interval triggers,
  not only the trigger turn.
- A foreground chat prompt preempts in-flight background extraction before
  retrieval or chat-model inference begins. Cancellation restores unfinished
  turns to the extraction buffer, leaves unrelated background work running, and
  resumes the deferred extraction batch after the foreground turn finishes.
- Assign each buffered extraction turn one stable work identifier and retain it
  across cancellation, provider failure, and retry. LLM analysis remains
  cancellable, but after memory mutation begins the current turn must reach a
  safe commit boundary before cancellation is observed by the batch. A
  committed turn is never requeued solely because cancellation was requested.
- Store extracted insights and summaries under deterministic per-turn record
  identifiers through idempotent vector upserts. Repeating the same turn must
  not increase the vector count or inflate an existing graph node's access
  evidence.
- Extraction batches count entities, facts, and relationships and log failures
  per turn without failing the user turn.
- Real runtime mode must wire real extraction, summarization, lifecycle, and
  compaction services where existing framework packages provide them. If a real
  service cannot be wired without framework edits, the gap must be logged in the
  framework upgrade log and exposed in diagnostics.
- Pending extraction must flush before compaction to prevent knowledge loss.
  Failed flush restores pending turns.
- Background tool decay runs after successful persisted turns when tool content
  manager exists.
- Incremental graph maintenance runs when configured maintainer says it should.
- Budget-aware compaction initializes `ContextBudgetMonitor` from
  `memory.compaction` when enabled.
- Real runtime mode initializes `InSessionCompactor` with the framework memory
  controller, collection manager, configured extraction/maintenance LLM, and
  typed compaction config when dependencies are available.
- After each successfully persisted turn, budget-aware compaction records the
  actual prompt budget status produced during prompt formatting.
- When the monitor threshold is crossed, FridayV2 marks compaction started and
  schedules real compaction as background work.
- Compaction must flush pending extraction before consolidating turns. If the
  flush fails, compaction stops and pending turns remain buffered.
- Compaction must pass session id, trigger reason, time budget, current tokens,
  available budget, and target utilization into the compactor.
- Compaction completion must be marked in a cleanup path on success or failure.
- Before processing the next chat prompt, the interactive loop must await any
  in-flight compaction task and surface progress feedback.
- Exit maintenance drains buffered extraction/access state and closes conflicting
  background work before coordinated reorganization.
- Lifecycle age and decay calculations accept both timezone-aware UTC metadata
  and legacy timezone-naive local metadata. Compatibility normalization occurs
  in memory without rewriting existing records. A lifecycle result containing
  errors is a failed shutdown substep and must not be recorded as successful.
- When coordinated exit reorganization is enabled, finalize the Transcript before
  taking its recovery snapshot, then run the same typed coordinator used by the
  manual command. Final resource cleanup follows the coordinator.
- `session.flush_on_exit`, `session.lifecycle_on_exit`,
  `session.reorganize_on_exit`, and `session.reorganize_mode` control exit
  behavior.
- `session.reorganize_on_exit` remains configurable and defaults to `false`.
  Enabling it requests execute through the same coordinator and mandatory
  aggregate recovery policy as the manual command.
- `reorganize_mode: fast` maps to full mode with synthesis and verification
  skipped. `full` and `deep` map to the complete pipeline. Unknown enabled values
  fail closed.
- Exit provider selection uses only explicit maintenance roles and embedding;
  it does not inherit the primary chat or embedding provider.
- Exit reorganization errors remain visible as maintenance warnings and must not
  prevent final resource cleanup. Post-mutation failure must first complete
  verified rollback or retain `recovery_required` evidence.

Required tests:

- Extraction interval matrix.
- Extraction interval matrix proves buffered turns are not dropped between
  interval triggers.
- Manual maintenance tests distinguish an idle configured buffer from a running
  extractor, prove resume occurs only after exclusive admission is released,
  and cover success, preflight failure, cancellation/rollback, and categorical
  scheduling failure.
- Extraction cancellation tests prove analysis remains interruptible, an
  in-progress commit reaches its safe boundary, only unfinished later turns are
  requeued, and repeating one stable turn leaves vector cardinality unchanged.
- Flush-before-compaction success and failure.
- Real-runtime maintenance wiring test proves required services are not silently
  replaced with fake implementations.
- Tool decay and graph maintenance scheduling.
- Budget monitor initialization from `memory.compaction`.
- Budget status recording after persisted turns.
- Threshold-triggered background compaction scheduling.
- Flush-before-compaction success and failure.
- Budget context/time-budget propagation into the compactor.
- Completion marking on compaction success and failure.
- Next-prompt gating while compaction is in flight.
- Exit maintenance order and config flags.
- Exit closes and drains tracked work before transcript finalization, and any
  coordinated recovery snapshot or execution decision follows finalization.
- Reorganization mode tests cover fast skip behavior and full/deep maintenance
  LLM role wiring.
- Reorganization failure tests prove transcript finalization still runs.

## Persistence And Runtime State

Reference: `friday.py:7530`, `friday.py:7761`, `friday.py:8026`

Required behavior:

- Persist transcript, graph, vector, lifecycle, context logs, history, exports,
  maintenance logs, and rejection logs under configured runtime data roots.
- Runtime data defaults must be ignored by git and kept out of package source.
- Transcript session creation includes model, user id, system prompt/config
  snapshot where available.
- Transcript finalization updates ended time and aggregate stats.
- Reset/archive semantics must preserve old transcript sessions from future
  priming context after full reset.

Required tests:

- Runtime paths use configured roots.
- Transcript create/finalize lifecycle.
- Full reset archives sessions.
- Package source never receives runtime state during tests.

## Contract Coverage Gate

Before implementing a parity-matrix row:

1. Confirm the row has a behavioral contract in this document or a
   simple-command exemption in `parity_overrides.yaml`.
2. If the contract is missing or too vague, inspect `friday.py`, update this
   document, and add or update required tests before implementation.
3. If behavior is intentionally changed, update the parity matrix and
   `parity_overrides.yaml` test fixture.
4. If a framework package change would make the behavior easier, log it in the
   framework upgrade log and implement an app-layer workaround during the parity
   pass.
