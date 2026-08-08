# Construction Directive: Friday Chat Command Remediation 1

Status: Approved for supervised execution
Date: 2026-08-08
Expected branch: `feature/friday-chat-command-remediation-1`
Required baseline ancestor: `baed8f2`
Planning checkpoint: `31bbcf1`
Controlling plan: [Friday Chat Command Remediation Plan](../chat-command-remediation)
Approval state: Approved by the maintainer for supervised execution; the
primary supervising agent may approve Gates A through F under this directive

## AI Builder Role

You are the primary implementation agent for the Friday Chat command
remediation. Repair the production paths for `/sessions`, `/transcript`,
transcript exports, `/cls`, `/clearscreen`, `/memory`, `/meta`, and
`/tool-budget` without changing the established command names or crossing the
FridayV2 package freeze.

This is production-path and persisted-state integration work. Make the command
behavior correct through typed Friday Chat contracts and disposable real-store
tests. Do not substitute display-string fixes, fake-only state, private
framework access, or live-provider testing for the required runtime behavior.

## Source Authority and Precedence

Apply these sources in order:

1. Active system, developer, and user instructions
2. [Repository engineering policy](../../../reference/policies/repository-engineering-policy.md)
3. Active repository `AGENTS.md` instructions
4. [Friday Chat Command Remediation Plan](../chat-command-remediation)
5. This construction directive
6. [FridayV2 behavioral contracts](../friday-chat-v2-aechive/friday-chat-v2-behavioral-contracts.md)
7. [FridayV2 parity matrix](../friday-chat-v2-aechive/friday-chat-v2-parity-matrix.md)
8. [FridayV2 framework upgrade log](../friday-chat-v2-aechive/friday-chat-v2-framework-upgrade-log.md)
9. Current public package contracts and source code
10. Current package-local and integration tests

The controlling plan contains the accepted product, architecture, safety, and
test decisions. Do not reopen or reinterpret them during implementation. If
this directive conflicts with the plan, repository policy, or active
instructions, stop before editing source and report the exact conflict.

The construction-directive guidance references
`docs/methodology/constitution/gendev.md`; that file was not present when this
directive was prepared. If it appears before or during implementation, read it
and stop if reconciling it would materially change scope, architecture, or gate
criteria.

## Input Coverage and Traceability

No separate current PRD, architecture specification, governance specification,
migration plan, or UAT plan exists specifically for this remediation. The
controlling plan is the accepted combined authority for those concerns. Do not
infer requirements from unrelated plans or archived prototype proposals.

| Controlling-plan work | Directive workstream | Hard gate | Required evidence |
|---|---|---|---|
| `CCR-00` baseline, isolation, reproductions | `CCR-00` | Gate A | ancestry, state-safety proof, focused baseline, failing production-path reproductions, positive `/meta` proof |
| `CCR-01` shared contracts and identity | `CCR-01` | Gate B | typed-contract tests, identity invariants, category ownership, legacy command tests |
| `CCR-02` transcript queries and exports | `CCR-02` | Gate C | disposable SQLite session, entry, export, error, and input-safety tests |
| `CCR-03` terminal clear behavior | `CCR-03` | Gate C | recording-display tests and supported-platform provider-free PTY proof |
| `CCR-04` memory and meta diagnostics | `CCR-04` | Gate D | disposable real-store counts, unavailable states, synthesized meta visibility, partial-failure tests |
| `CCR-05` tool selection and budget | `CCR-05` | Gate E | shared-state, enforcement, estimator, turn-snapshot, and exact-schema tests |
| `CCR-06` documentation, validation, UAT | `CCR-06` | Gate F | package/static/root evidence, disposable CLI UAT, updated contracts and parity status |

## Implementation Objective

Deliver these outcomes:

- each production command reads or changes the same typed state used by the
  running Friday Chat application;
- one generated and injectable session identity reaches runtime, adapters, app
  state, persistence, and commands;
- transcript listing, reading, and export use persisted SQLite queries rather
  than fake-only lists;
- clear-screen aliases request one real display effect and emit no false
  acknowledgment;
- memory diagnostics report real counts and distinguish zero from unavailable
  or unconfigured values;
- `/meta` preserves the working record query, exposes useful typed provenance,
  and provides an actionable empty state without triggering synthesis;
- manual and automatic tool selection share one runtime-owned state and one
  schema-budget calculator with the model turn;
- all mandatory validation is provider-free and uses disposable persistence
  roots;
- documentation claims only the behavior proved by the final evidence.

## Branch and Integration Invariants

- Work only on `feature/friday-chat-command-remediation-1` unless the
  supervising agent records an explicitly authorized replacement branch.
- Verify `baed8f2` is an ancestor before source edits.
- Treat `feature/reorg-remediation-1` and commit `baed8f2` as inherited,
  separately reviewable history. Do not amend, squash, revert, or rewrite that
  implementation as part of command remediation.
- Record all commits and changes above `baed8f2` at Gate A.
- Preserve unrelated tracked and untracked state, including any existing
  `docs/dev-skills/subagent-directives-template.md` working-tree file.
- Integration order is fixed: merge `feature/reorg-remediation-1` first, then
  update the command-remediation branch base if necessary and merge
  `feature/friday-chat-command-remediation-1` second.
- Do not create commits, push, merge, publish, or open a pull request during
  construction unless the user separately authorizes that action.

## Authorized Scope

Edit only files required by the controlling plan in these locations:

- `packages/friday-chat/src/friday_chat/`
- `packages/friday-chat/tests_chat/`
- one narrowly named disposable integration test under `tests/integration/`
  only if package-local tests cannot prove the production adapters together
- [Friday Chat Command Remediation Plan](../chat-command-remediation)
- [FridayV2 behavioral contracts](../friday-chat-v2-aechive/friday-chat-v2-behavioral-contracts.md)
- [FridayV2 parity matrix](../friday-chat-v2-aechive/friday-chat-v2-parity-matrix.md)
- [FridayV2 framework upgrade log](../friday-chat-v2-aechive/friday-chat-v2-framework-upgrade-log.md)
- this construction directive for execution evidence and close-out notes

No Friday Memory, Friday Transcript, Friday CLI, or other framework package
source or test change is authorized. No configuration schema, example
configuration, dependency, workspace metadata, database schema, or persisted
data migration is authorized. If a required behavior cannot be implemented
through an existing public typed framework API, log the gap and stop that
workstream.

## Explicit Non-Goals

- Do not change unrelated Friday Chat commands or broad registry behavior.
- Do not redesign the whole command system or split every handler out of
  `commands/registry.py`; move only the affected handlers and their required
  typed helpers.
- Do not add a second command registry, fallback router, or command-local state
  that competes with runtime state.
- Do not modify Friday Memory, Friday Transcript, Friday CLI, or another frozen
  framework package.
- Do not rewrite, migrate, merge, archive, or delete existing transcript rows
  or sessions to adopt the new session identity.
- Do not make `/meta` synthesize records, run reorganization, invoke a provider,
  or create a duplicate generation path.
- Do not change reorganization mutation, rollback, recovery, journal, lease, or
  containment behavior delivered by `baed8f2`.
- Do not copy a live SQLite database for export; query public transcript APIs.
- Do not place untrusted session IDs in filesystem paths.
- Do not silently support both `max_budget_ratio` and the dead
  `max_schema_budget_percent` key with different units.
- Do not change model, embedding, provider, retry, timeout, endpoint, or
  credential configuration.
- Do not contact Kimi, DGX, OpenAI, an embedding endpoint, or any external
  service in a mandatory test or UAT path.
- Do not add dependencies.
- Do not weaken typing, invariants, security, sanitization, or validation to
  obtain a passing result.
- Do not clean caches, `.friday/`, Chroma state, transcript state, or unrelated
  dirty files.
- Do not describe planned or fake-only behavior as implemented or tested.

## Anti-Drift Requirements

- Implement every `CCR-00` through `CCR-06` requirement and no adjacent feature.
- Keep command names, aliases, and established compatibility behavior unless
  the controlling plan explicitly changes them.
- Keep metadata and canonical dispatch registration in `CommandRegistry`.
- Use typed models, dataclasses, or protocols for new boundaries. Do not add
  long-lived `dict[str, Any]`, repeated `cast(...)`, or `getattr`/`hasattr`
  probes as substitute interfaces.
- Enforce essential runtime invariants with explicit exceptions, not `assert`
  alone.
- Do not add `# mypy: ignore-errors` or broad suppressions.
- Do not access private framework attributes to avoid a stop condition.
- Do not weaken security, governance, package ownership, or error sanitization.
- Do not remove unrelated code, tests, documentation, or generated state.
- Report every skipped, failed, or blocked validation command honestly.
- Do not advance past a failed or blocked gate.

## Provider, Persistence, and Runtime-State Boundary

All required automated tests and UAT must be provider-free. Use deterministic
in-process chat, embedding, selector, and tool doubles wherever a transport
would otherwise be constructed. A test must fail before any network attempt.

Every SQLite, Chroma, graph, export, log, recovery, and other persistence path
used by this remediation must resolve beneath that test's `tmp_path` or one
new disposable UAT root. Add explicit containment assertions. Never read,
copy, mutate, clean, migrate, or inspect active `.friday` data.

The configured `scripts/run-friday-chat-example.sh` path is optional operator
evidence only. Do not run it without explicit user authority to read active
local configuration and state. If separately authorized, enter slash commands
only; do not submit a normal chat turn, execute a tool, run reorganization, or
contact the configured model.

Tool tests must not execute network, shell, filesystem-mutation, browser, or
external tool implementations. Prove schema selection and model dispatch using
safe registered schemas and deterministic model doubles.

## Supervised Execution Protocol

Use one fresh-context implementation sub-agent when execution is authorized.
Before editing, it must read completely:

- repository `AGENTS.md`;
- the repository engineering policy;
- the controlling plan;
- this directive;
- the FridayV2 behavioral contracts;
- the FridayV2 parity matrix;
- the FridayV2 framework upgrade log;
- every additional document referenced as authority by those sources and
  required for the selected workstream.

The implementation sub-agent may not approve its own work. The supervising
agent independently inspects the diff, test evidence, scope, and stop
conditions at every gate. After that review, the supervising agent may record
`PASS`, close the gate, and direct work to continue without waiting for the
user. Consult the user when a gate is `FAIL` or `BLOCKED`, a stop condition is
active, or additional scope or authority is required.

This delegation applies through Gate F. At Gate F, pause for explicit maintainer
approval before any action that would remove containment or enable an execution
path. This remediation does not plan either action; if neither is required, the
supervising agent may review and close Gate F under the delegated authority.

For every gate, append a durable execution record to this directive containing:

- date and disposition: `PASS`, `FAIL`, or `BLOCKED`;
- branch, baseline ancestor, and worktree status;
- files changed during the gate;
- exact validation commands and exit status;
- test counts and relevant expected-failure evidence;
- supervisor's independent inspection findings;
- active stop-condition assessment;
- explicit authorization or direction for the next gate.

No verbal summary alone closes a gate. Missing evidence is `BLOCKED`; a failed
criterion is `FAIL`, not partial `PASS`.

## Mandatory Execution Order and Gates

Execute Gates A through F in order. `CCR-02` and `CCR-03` may be implemented in
either order within Gate C, but Gate C closes only when both pass. A later
workstream may introduce a type needed for compilation, but its behavior may
not be enabled before its prerequisite gate closes.

### Gate A: Branch Isolation and Executable Reproductions

Do not implement behavior changes before Gate A passes.

Required evidence:

- current branch is `feature/friday-chat-command-remediation-1`;
- `git merge-base --is-ancestor baed8f2 HEAD` succeeds;
- every change above `baed8f2` and every unrelated worktree item is recorded;
- the existing 23-test focused fake baseline is rerun and its current result is
  recorded rather than assumed;
- production-shaped disposable regressions prove the diagnosed failures for
  `/sessions`, current and selected `/transcript`, `/memory`, clear-screen, and
  `/tool-budget` before their fixes;
- a seeded real-adapter `meta_insight` proves `/meta` is already registered and
  dispatched before its formatting changes;
- every fixture path is asserted beneath `tmp_path` and outside repository or
  user `.friday` roots;
- no provider transport, active data, external tool, or destructive operation
  is reached;
- regression tests retain the failures after baseline capture and are not
  weakened to match existing broken output.

Gate A `PASS` means the reproductions accurately fail on the baseline and the
positive `/meta` control succeeds. It does not mean the new regression suite is
already green. Record each expected failure by test ID and failure reason.

### Gate B: Typed Foundations and Session Identity

Required evidence:

- shared command arguments, results, and UI effects live in one cycle-free
  typed Friday Chat module;
- only affected handlers and formatting helpers move to
  `commands/session.py`, `commands/memory.py`, `commands/transcript.py`, and
  `commands/tools.py`;
- `CommandRegistry` remains the only metadata, alias, help, and dispatch
  registry;
- one immutable generated production session identity is created per CLI
  invocation and is injectable for deterministic tests and replay;
- the same identity reaches runtime, Framework adapters, app session state,
  maintenance, persistence, and command queries;
- explicit runtime checks reject app/runtime identity disagreement;
- hard-coded production `friday-v2` identity creation is removed from affected
  composition paths;
- unchanged command/help and focused legacy tests remain green;
- no frozen framework package is modified.

### Gate C: Persisted Transcript and Terminal Display

Both transcript and display criteria must pass.

Transcript evidence:

- fake and framework transcript adapters implement the same Friday Chat-owned
  typed query contract;
- `/sessions` queries up to 1000 persisted sessions, newest first, with correct
  current and configured primed-session markers;
- `/transcript` reads the current persisted identity and
  `/transcript <session_id>` safely reads the requested persisted session;
- display truncation and chronological entry order are deterministic;
- `/transcript export`, `/export`, and `/export-prompts` use the same typed
  persisted query path and safe export root;
- all-session export writes deterministic `sessions.csv` and `entries.csv`
  without copying SQLite;
- selected IDs containing separators, Unicode, and SQL-like text remain bound
  query values and never become path components;
- missing, empty, archived, WAL-backed, partial, and failure cases have
  explicit sanitized behavior;
- two disposable app invocations against one SQLite store persist distinct
  session identities and can query each other as specified.

Display evidence:

- a typed command effect requests clear-screen with empty normal output;
- app dispatch invokes one display clear boundary;
- production terminal delegation reaches Rich console clear;
- recording test doubles observe one request without a terminal;
- `/cls` and `/clearscreen` resolve to the same handler and effect;
- successful clear emits no `Screen cleared.` replacement message;
- unavailable or failed clear returns a sanitized honest error;
- a supported-platform provider-free PTY smoke observes clear behavior, while
  the recording boundary remains the required platform-neutral test.

### Gate D: Honest Memory Statistics and Meta Visibility

Required evidence:

- `MemoryStatisticsSnapshot` or equivalent uses optional typed values instead
  of fabricated zeros;
- the production adapter aggregates only through public episodic, collection,
  graph, transcript, lifecycle, priming, session, and context APIs;
- output consistently distinguishes actual zero, unavailable, and not
  configured;
- current-session, vector, graph, transcript, lifecycle/access-buffer, priming,
  and last-context metrics match seeded disposable data where configured;
- typed `MemoryRecordView` queries replace dynamic record-method lookup for the
  affected insight, summary, and meta paths;
- `/meta` preserves the existing short- and long-term query, renders bounded
  provenance, lifecycle stage, confidence, source count, creation, and
  verification fields, and documents decayed-record treatment;
- a reorganization-compatible synthesized `meta_insight` from the inherited
  mutation contract is visible without provider execution;
- empty and partial-store-failure states are actionable and do not fabricate
  success;
- the most recent typed budget status needed for diagnostics is retained in
  app command state rather than reduced to untyped debug strings;
- no private framework access or framework package change is introduced.

### Gate E: Unified Tool Selection and Budget Enforcement

Required evidence:

- one runtime-owned `ToolSelectionState` and immutable `ToolBudgetSnapshot`, or
  equivalent typed contracts, govern commands and turns;
- no manual injection means automatic relevance selection for each turn;
- `/inject-tools` atomically switches to manual mode and exactly that accepted
  schema set is offered until `/clear-tools` restores automatic mode;
- unknown names and changes exceeding count or token limits are rejected before
  authoritative state changes;
- `tools.context.max_tools`, `tools.context.max_budget_ratio`,
  `memory.context_window`, and `memory.output_buffer` are enforced;
- one canonical estimator drives selection, dynamic context budgeting,
  `BudgetStatus.tool_tokens`, `TurnResult`, and `/tool-budget`;
- `TurnResult` exposes the selected tool names and immutable budget snapshot,
  and app command state retains the most recent snapshot;
- `/tool-budget` accurately distinguishes registered, manual, last-selected,
  and executed tools and shows useful manual, automatic, and no-turn states;
- exact-boundary acceptance and one-token/count overflow behavior are
  deterministic;
- the schema definitions reported for the recorded turn are byte-for-byte the
  definitions passed to the deterministic chat model;
- provider responses and tool execution results do not affect schema-budget
  calculation;
- the undocumented `max_schema_budget_percent` lookup is removed without an
  unapproved dual-key compatibility path.

### Gate F: Documentation, Full Validation, and Disposable UAT

Required evidence:

- all Gate A reproductions now pass through production-shaped disposable paths;
- affected command usage, aliases, descriptions, and argument metadata are
  complete and generated from the registry;
- behavioral contracts document final session identity, transcript/export,
  memory unavailable, meta provenance, tool selection/budget, and clear-screen
  behavior;
- parity rows no longer claim `tested` without production-path or app-level
  evidence and are advanced only to the status justified by results;
- every framework gap is recorded in the framework upgrade log and its
  workstream stopped rather than bypassed;
- focused, production-adapter, package, Ruff, mypy, import, whitespace, and
  disposable UAT gates pass;
- repository pytest is attempted without cache cleanup and its exact outcome
  is reported, including any still-present baseline collection collision;
- no active `.friday` data, provider, external tool, unrelated file, or
  unauthorized package was touched;
- no stop condition remains active.

## Required Workstreams

### `CCR-00`: Baseline, Isolation, and Reproductions

1. Capture branch, ancestry, status, inherited commits, and unrelated state.
2. Rerun the focused fake baseline.
3. Convert the disposable real-adapter probe into retained regressions for all
   five demonstrated production failures.
4. Add the positive seeded `/meta` control.
5. Add path-containment and network/provider prohibition checks.
6. Record Gate A without implementing a behavior fix.

### `CCR-01`: Shared Contracts and Session Identity

1. Introduce the smallest cycle-free typed command contract module.
2. Move only affected handlers and their helpers to the intended category
   modules while preserving registry ownership.
3. Introduce one generated/injectable session identity and propagate it through
   every affected composition layer.
4. Preserve lazy session persistence while honestly representing the current
   in-process identity.
5. Add deterministic replay/test injection and mismatch invariants.
6. Preserve help, aliases, parsing, and safe existing command behavior.

### `CCR-02`: Persistent Transcript Commands

1. Define Friday Chat-owned typed session, entry, context-log, and export views.
2. Extend the Friday Chat transcript protocol and both fake/framework adapters
   through existing public Friday Transcript APIs.
3. Rebuild `/sessions`, current/selected `/transcript`, and deterministic
   terminal formatting on persisted queries.
4. Update usage to `/transcript [session_id|export]`.
5. Rebuild `/transcript export`, `/export`, and `/export-prompts` on the common
   query path and safe export root.
6. Preserve ordering and exact counts; sanitize every persistence error.
7. Test malicious-looking IDs, WAL visibility, archived/empty/missing state,
   every export format, and failure privacy.

### `CCR-03`: Terminal Clear Behavior

1. Add the typed clear-screen effect to command results.
2. Dispatch effects in the app and add a clear-capable display protocol.
3. Delegate the production implementation to Rich console clear.
4. Add recording and failure test doubles.
5. Prove alias equivalence, no replacement output, and provider-free PTY
   behavior.

### `CCR-04`: Honest Memory and Meta Diagnostics

1. Add typed memory-statistics and memory-record query results.
2. Aggregate only public real-store APIs and categorize unavailable components.
3. Render all required statistics consistently without magic zeros.
4. Replace affected dynamic record lookup with typed queries.
5. Preserve `/meta` retrieval while adding provenance and lifecycle fields.
6. Prove inherited reorganization synthesis visibility without a provider.
7. Cover empty, zero, unavailable, not-configured, and partial-failure states.

### `CCR-05`: Unified Tool Selection and Budget

1. Add runtime-owned selection state and the canonical budget calculator.
2. Route manual injection, clearing, automatic selection, model schemas,
   context hints, turn results, and command inspection through that state.
3. Enforce count and token ratio atomically before model dispatch.
4. Retain immutable selected-schema budget evidence on the turn and app.
5. Remove the dead configuration lookup.
6. Cover manual/automatic transitions, errors, bounds, ordering, disabled/no
   tool state, and schema identity with deterministic doubles.

### `CCR-06`: Documentation, Validation, and Close-Out

1. Complete affected command metadata and help descriptions.
2. Update behavioral contracts and parity evidence from actual results.
3. Record but do not implement any newly discovered frozen-framework gap.
4. Run the full validation sequence and mandatory disposable UAT.
5. Append Gate F evidence and a final changed-file/package-boundary report.
6. Offer the configured-script smoke only as a separately authorized optional
   check.

## Migration, Removal, and Compatibility Instructions

- Do not migrate existing transcript identities or rewrite persisted rows.
  Existing sessions remain queryable by their stored IDs.
- New production invocations use a unique `session_<unique-id>` identity;
  deterministic identities remain injectable for tests and replay.
- Remove hard-coded `friday-v2` identity creation only from affected production
  composition paths after identity propagation tests exist.
- Replace fake-only command reads such as `.turns`, `.context_logs`,
  `stored_turns`, and `retrievals` with the typed Friday Chat contract. Fakes
  must implement the same contract; do not keep a production fallback to their
  incidental attributes.
- Preserve every existing command name and alias. `/transcript` argument
  metadata changes from a literal current-session restriction to
  `[session_id|export]`.
- Preserve transcript export formats and safely improve their production data
  source; do not rename formats or silently change quoting/order contracts.
- Remove `max_schema_budget_percent` command lookup after canonical
  `max_budget_ratio` enforcement is wired. Do not introduce a config migration
  or alias without separate authority.
- Move only affected handlers. Delete obsolete private helpers only after all
  references are removed and focused tests prove no compatibility regression.
- Do not change persisted schemas, default data roots, reorganization artifacts,
  or recovery formats.

## Security and Governance Requirements

- Treat session IDs, record text, transcript content, provider output, tool
  metadata, and store errors as untrusted.
- Use bound store queries for session IDs. Never concatenate them into SQL or
  filesystem paths.
- Constrain every export below the approved export root after resolution and
  reject traversal, alias, or containment failure.
- Export queried records only. Never copy an active SQLite database.
- Sanitize errors so terminal output and logs contain no raw SQL, database
  paths, transcript content, config snapshots, prompts, credentials, provider
  responses, or memory content.
- Preserve tool-output sanitization, provenance, quarantine, and ingestion
  safety. This remediation changes schema selection, not tool trust policy.
- Do not execute external tools in tests.
- Preserve reorganization recovery and mutation containment from the inherited
  base.
- Keep all new contracts explicitly typed and all runtime invariants explicit.
- A policy waiver, broad type suppression, or private cross-package access is a
  stop condition, not an implementation technique.

## Testing Requirements

### Baseline and production-path regressions

- Retain the existing focused fake tests as compatibility coverage.
- Add `packages/friday-chat/tests_chat/test_command_production_adapters.py` for
  disposable production-shaped paths.
- Capture pre-fix failure evidence before changing behavior.
- Use public store seeding operations and per-test paths beneath `tmp_path`.
- Add a provider/network tripwire so accidental transport construction fails.

### Transcript and identity

- Prove fake and framework adapter conformance.
- Prove two invocations, current/selected/missing/empty/archived sessions,
  primed markers, WAL visibility, safe untrusted IDs, deterministic ordering,
  exact export counts, every format, and sanitized errors.

### Display

- Prove effect dispatch, alias equivalence, one clear call, empty success output,
  honest failure, recording-adapter behavior, and supported-platform PTY output.

### Memory and meta

- Seed real disposable episodic, lifecycle, vector, graph, transcript, and
  reorganization-compatible meta records through public APIs.
- Prove exact counts, zero/unavailable/not-configured distinctions, decayed
  policy, provenance fields, empty guidance, and partial failure.

### Tool selection and budget

- Prove manual and automatic modes, clearing, unknown names, count overflow,
  token overflow, exact boundary, deterministic order, disabled/no tools,
  schema identity, selected-versus-executed output, and provider-independent
  budget calculation.
- Use an in-process deterministic chat-model double and inert schemas; do not
  execute tools.

### Negative and safety tests

- No test path may resolve into repository or user `.friday` state.
- No test may contact a provider or external service.
- Malicious-looking session IDs cannot alter queries or escape export roots.
- Persistence exceptions do not leak sensitive data.
- Identity mismatch fails explicitly.
- Budget rejection leaves authoritative selection state unchanged.
- Clear failure never reports success.
- Missing public framework capability stops the workstream.

## Verification Commands

Record command, exit status, test count, duration, and relevant failure details.
Use focused tests first:

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q \
  packages/friday-chat/tests_chat/test_command_registry.py \
  packages/friday-chat/tests_chat/test_session_memory_commands.py \
  packages/friday-chat/tests_chat/test_transcript_export_commands.py \
  packages/friday-chat/tests_chat/test_tool_commands.py \
  packages/friday-chat/tests_chat/test_app_lifecycle.py \
  packages/friday-chat/tests_chat/test_runtime.py \
  packages/friday-chat/tests_chat/test_display.py \
  packages/friday-chat/tests_chat/test_turn_processing.py
```

Run the production-path module explicitly:

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q \
  packages/friday-chat/tests_chat/test_command_production_adapters.py
```

Run package and static gates:

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q \
  packages/friday-chat/tests_chat
PATH="$PWD/.venv/bin:$PATH" .venv/bin/ruff check packages/friday-chat
PATH="$PWD/.venv/bin:$PATH" .venv/bin/mypy packages/friday-chat
PATH="$PWD/.venv/bin:$PATH" .venv/bin/python -c \
  "from friday_runtime import RuntimeKernel; from friday_agent import InteractiveAgent; print('Friday imports OK')"
git diff --check
```

Attempt the root pytest gate without deleting caches or generated state:

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest
```

The plan records a known root collection collision between Friday Chat and
Friday CLI files named `test_display.py`. Recheck it; do not assume it remains.
If root pytest fails for baseline debt, report the exact current failure and the
narrower passing evidence. Do not clean state or alter unrelated tests to make
the root command pass.

Run these read-only scope and safety checks before every gate closes:

```bash
git status --short --branch
git diff --check
git diff --name-only baed8f2...HEAD
git merge-base --is-ancestor baed8f2 HEAD
```

Inspect both committed and uncommitted changes. A clean `git diff` does not
prove scope when prior implementation commits exist.

## CLI, API, and UAT Requirements

Mandatory UAT uses one new disposable root. Derive a configuration from the
example but redirect every persistence, export, log, and recovery path beneath
that root and replace provider transports with deterministic in-process
doubles. Seed through public APIs:

- two distinct transcript sessions and entries;
- current and selected session state;
- graph nodes and relationships;
- episodic and lifecycle/vector records;
- one reorganization-compatible `meta_insight`;
- inert registered tool schemas and deterministic selection state.

Run the real Friday Chat app/CLI boundary in a PTY and exercise:

```text
/sessions
/transcript
/transcript <seeded-session-id>
/memory
/meta
/tools
/tool-budget
/inject-tools echo
/tool-budget
/clear-tools
/cls
/clearscreen
/q
```

Required observations:

- sessions and entries come from the disposable SQLite store;
- current and selected session identity are distinguishable;
- memory and meta output matches seeded data and provenance;
- tool budget reflects automatic, manual, and cleared state using the same
  schemas as the deterministic turn path;
- both clear aliases produce an observable clear effect with no false text;
- the process exits cleanly;
- no network connection or active-state path is opened.

No ordinary provider-backed chat turn is required. If a turn is needed to
prove automatic tool selection, run it only against the deterministic in-process
model double. The recording display boundary is required on every platform; PTY
clear observation is additional required evidence on supported platforms.

## Documentation Close-Out

At Gate F:

- update the controlling plan status and evidence without rewriting its
  original findings;
- update behavioral contracts for the final implemented semantics;
- update affected parity rows only to the status supported by production-path
  evidence;
- add any missing public-framework capability to the framework upgrade log and
  stop that workstream;
- update command metadata so generated general and detailed help remains
  accurate;
- append the supervised execution record to this directive;
- do not mark deferred, blocked, failed, or untested behavior complete;
- do not edit unrelated planning or archive documents.

## Reporting Requirements

Every gate report must include:

- disposition and criterion-by-criterion evidence;
- exact files changed;
- package-boundary impact;
- config, environment, persistence, and migration impact;
- tests added or changed and why they prove production behavior;
- exact commands, exit statuses, counts, and durations;
- expected versus unexpected failures;
- provider/network and active-state isolation evidence;
- security and privacy checks;
- unrelated state preserved;
- stop-condition assessment;
- supervisor approval and next-gate direction.

The final report must also state:

- which six reported command areas were remediated;
- which paths remain deferred or blocked;
- whether any framework upgrade was logged;
- whether root validation passed or failed for baseline debt;
- whether mandatory disposable UAT passed;
- that no live provider or active `.friday` state was used;
- the required branch merge order;
- that no commit, push, PR, or merge occurred unless separately authorized.

## Stop Conditions

Stop and request direction if:

- the active branch is not the authorized implementation branch;
- `baed8f2` is not an ancestor, or inherited reorganization divergence cannot
  be isolated;
- a required fix needs Friday Memory, Friday Transcript, Friday CLI, or another
  frozen framework package source or test change;
- a required operation is absent from a public typed framework API;
- session identity adoption would require rewriting existing transcript rows;
- real memory statistics require private cross-package access;
- transcript export would require copying an active SQLite database;
- required injected-versus-automatic tool precedence conflicts with the plan;
- a mandatory test or UAT would require active `.friday` data, a live provider,
  an external service, or actual external tool execution;
- implementation changes reorganization mutation or recovery behavior;
- any persistence path escapes its disposable root;
- a dependency, config schema, database schema, workspace metadata, or
  migration change appears necessary;
- a policy waiver, broad typing suppression, repeated boundary cast, or
  essential `assert`-only invariant appears necessary;
- unrelated state cannot be preserved;
- a gate criterion fails or lacks evidence.

When stopped, do not improvise a workaround, weaken the criterion, or continue
another dependent workstream. Record `FAIL` or `BLOCKED`, preserve the exact
evidence, and ask for the smallest additional decision or authority required.

## Supervised Execution Record

No implementation gates have been executed in this directive.

Use this template for each gate:

```text
### Gate X: PASS | FAIL | BLOCKED — YYYY-MM-DD

Branch and baseline:
Changed files:
Criteria evidence:
Validation commands and results:
Provider and active-state isolation:
Security and privacy review:
Unrelated state preserved:
Stop-condition assessment:
Supervisor disposition:
Next-gate direction:
```
