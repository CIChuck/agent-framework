# Construction Directive: Friday Chat Command Remediation 1

Status: Executed through Gate F; Gates A-F PASS
Date: 2026-08-08
Expected branch: `feature/friday-chat-command-remediation-1`
Required baseline ancestor: `baed8f2`
Planning checkpoint: `31bbcf1`
Controlling plan: [Friday Chat Command Remediation Plan](plan.md)
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
2. [Repository engineering policy](../../../../reference/policies/repository-engineering-policy.md)
3. Active repository `AGENTS.md` instructions
4. [Friday Chat Command Remediation Plan](plan.md)
5. This construction directive
6. [FridayV2 behavioral contracts](../friday-chat-v2/friday-chat-v2-behavioral-contracts.md)
7. [FridayV2 parity matrix](../friday-chat-v2/friday-chat-v2-parity-matrix.md)
8. [FridayV2 framework upgrade log](../../../../planning/backlog/friday-chat-framework-followups/upgrade-log.md)
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
- [Friday Chat Command Remediation Plan](plan.md)
- [FridayV2 behavioral contracts](../friday-chat-v2/friday-chat-v2-behavioral-contracts.md)
- [FridayV2 parity matrix](../friday-chat-v2/friday-chat-v2-parity-matrix.md)
- [FridayV2 framework upgrade log](../../../../planning/backlog/friday-chat-framework-followups/upgrade-log.md)
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

### Gate A: PASS — 2026-08-08

The implementer supplied the candidate evidence below. The supervising agent
independently inspected the complete test module, required one resolved-path
containment correction, reran the required evidence, and approved this gate.

Branch and baseline:

- branch: `feature/friday-chat-command-remediation-1`;
- HEAD: `4f313e9fb5dfb6e83a34d0f5a106b351317bcf75`;
- `git merge-base --is-ancestor baed8f2 HEAD`: exit `0`;
- merge base: `baed8f27ec55519e872ab8ff627fd5022a2fa0c4`;
- commits above `baed8f2`: `31bbcf1 Plan Friday Chat command remediation`,
  `2b559dc Prepare Friday Chat command remediation directive`, and
  `4f313e9 Approve Friday Chat command remediation directive`;
- committed files above `baed8f2`:
  `docs/archive/completed/2026/friday-chat-command-remediation/plan.md` and this directive;
- unrelated worktree state:
  `?? docs/dev-skills/subagent-directives-template.md`;
- the unrelated template was observed staged by concurrent/external activity
  before Gate A edits. The implementer had not run a Git mutation. Per the
  supervisor's direction, only its index entry was restored with
  `git restore --staged -- docs/dev-skills/subagent-directives-template.md`.
  It then and finally reports `??`; its contents were not read, modified, or
  deleted.

Changed files:

- added
  `packages/friday-chat/tests_chat/test_command_production_adapters.py`;
- appended this candidate evidence to this directive;
- no Friday Chat production source, frozen framework source/test, dependency,
  configuration schema, workspace metadata, or persisted schema was changed.

Criteria evidence:

- retained five intentionally failing production-shaped command-area tests
  reproduce persisted-session omission, current and selected persisted-entry
  invisibility, fake-only memory counts, absent display clear effects for both
  aliases, and missing last-turn selected schemas in `/tool-budget`;
- the transcript reproduction dispatches both current and explicitly selected
  session queries and reports all four seeded user/assistant visibility checks
  false on the baseline;
- a real `FrameworkMemoryAdapter` plus disposable Chroma collection seeded by a
  deterministic in-process embedding backend proves `/meta` is registered,
  dispatched, and reads a `meta_insight` with scalar-safe synthesis metadata;
- the selected-schema reproduction builds real framework adapters, replaces
  only chat and retrieval execution with deterministic in-process doubles,
  selects the inert `echo` schema, records nonzero turn schema tokens, and does
  not execute the tool;
- every declared vector, graph, transcript, recovery, and log path is asserted
  beneath the per-test `tmp_path` and outside the repository and user active
  `.friday` roots before and after runtime construction;
- an autouse tripwire replaces provider chat/embedding methods and low-level
  synchronous/asynchronous connection APIs with fail-closed assertions. A
  positive tripwire test proves both provider and socket interception occurs
  before transport I/O.

Expected failing test IDs and baseline reasons:

- `test_sessions_lists_seeded_persisted_session`: `/sessions` returned only
  fabricated `current-session (0 turns)` and omitted `persisted-session`;
- `test_transcript_reads_seeded_current_and_selected_sessions`: neither the
  seeded current nor selected persisted user/assistant markers were visible;
- `test_memory_reports_seeded_real_episodic_count`: `/memory` returned
  fake-only `stored_turns: 0` and `retrievals: 0` after one real episodic turn;
- `test_clear_aliases_request_display_effect_without_false_output`: `/cls` and
  `/clearscreen` produced zero display clear calls instead of two (the retained
  assertion also requires no replacement output after the effect exists);
- `test_tool_budget_reports_schemas_selected_for_real_turn`: the turn recorded
  nonzero selected schema tokens, but `/tool-budget` returned
  `No active tools injected.` and omitted `echo` and the recorded token count.

Validation commands and results:

- pre-edit baseline:
  `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_session_memory_commands.py packages/friday-chat/tests_chat/test_tool_commands.py`
  — exit `0`, `23 passed in 0.48s`;
- final production reproduction:
  `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q packages/friday-chat/tests_chat/test_command_production_adapters.py`
  — expected exit `1`, `5 failed, 3 passed in 1.59s`; only the five IDs above
  failed;
- isolated positive controls:
  `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q packages/friday-chat/tests_chat/test_command_production_adapters.py::test_production_fixture_paths_are_disposable packages/friday-chat/tests_chat/test_command_production_adapters.py::test_provider_and_network_tripwires_fail_closed packages/friday-chat/tests_chat/test_command_production_adapters.py::test_meta_dispatches_seeded_real_adapter_record`
  — exit `0`, `3 passed in 1.12s`;
- post-addition fake baseline:
  `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_session_memory_commands.py packages/friday-chat/tests_chat/test_tool_commands.py`
  — exit `0`, `23 passed in 0.44s`;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/ruff check packages/friday-chat/tests_chat/test_command_production_adapters.py`
  — exit `0`, `All checks passed!`;
- initial narrow mypy authoring check exited `1` with one
  `no-any-return` error at the test command-output helper. The helper was
  tightened with an explicit runtime `str` invariant; final
  `PATH="$PWD/.venv/bin:$PATH" .venv/bin/mypy packages/friday-chat/tests_chat/test_command_production_adapters.py`
  exited `0`, `Success: no issues found in 1 source file`;
- `git diff --check` — exit `0`, no output.
- final `git status --short --branch --untracked-files=all` reports only the
  modified directive, the new untracked production-adapter test module, and the
  preserved unrelated untracked template; `git diff --cached --name-status`
  is empty;
- final `git diff --name-only baed8f2...HEAD` reports only the two committed
  planning/directive files already identified above, and final
  `git merge-base --is-ancestor baed8f2 HEAD` exits `0`.

Supervisor-independent validation:

- full production reproduction — expected exit `1`, exactly
  `5 failed, 3 passed in 1.33s`, with only the five documented command-area
  targets failing;
- isolated containment, transport-tripwire, and seeded `/meta` controls — exit
  `0`, `3 passed in 1.23s`;
- focused fake compatibility baseline — exit `0`, `23 passed in 0.49s`;
- Ruff and narrow mypy for the new module — exit `0` with no findings;
- complete test-module inspection confirmed real Friday Chat framework adapters,
  deterministic provider doubles, public store seeding, resolved disposable
  paths, retained target assertions, and no production behavior change;
- `git diff --check`, empty staging, exact worktree scope, and `baed8f2`
  ancestry were independently reconfirmed.

Provider and active-state isolation:

- no provider credential, model endpoint, external service, or configured
  script was used;
- no active `.friday` file or directory was read, copied, mutated, cleaned, or
  migrated;
- all SQLite, Chroma, graph, recovery, log, and export state was disposable
  under pytest `tmp_path`;
- no network, shell, browser, filesystem-mutation tool, or external tool was
  executed; the `echo` definition was schema-only evidence.

Security and privacy review:

- seeded transcript and memory values are synthetic markers;
- provider/network calls fail closed through retained tripwires;
- active-state containment is asserted from non-strict resolved candidate,
  disposable-root, and active-root paths for every declared runtime path;
- no database was copied, no untrusted identifier entered a path, and no
  persisted data was rewritten.

Unrelated state preserved:

- `docs/dev-skills/subagent-directives-template.md` remains untracked and its
  content remains uninspected and unchanged by this work;
- no cache or generated state was cleaned, inspected for data, or intentionally
  manipulated; test runners may update ignored cache metadata;
- visible tracked and untracked scope is reported from final Git status rather
  than treating ignored cache state as unchanged;
- no file was staged, committed, pushed, merged, or included in a PR.

Stop-condition assessment:

- authorized branch and baseline ancestry are satisfied;
- all required Gate A reproductions and controls produced their expected
  results without a frozen-package change, private framework access, provider,
  active state, path escape, external tool, schema/dependency change, waiver,
  suppression, or behavior fix;
- no unexpected test failure or active implementation stop condition was found;
- no stop condition is active. Gate B had not begun when this disposition was
  recorded.

Supervisor disposition: `PASS`. The evidence demonstrates the five diagnosed
baseline failures and the positive `/meta` and isolation controls without a
behavior fix, provider, active state, external tool, or scope violation.

Next-gate direction: Gate B is authorized. Implement typed foundations and
session identity only, then stop for independent Gate B review.

### Gate B: PASS — 2026-08-08

The implementer completed the typed-foundation and session-identity scope and
stopped before Gate C behavior. The supervising agent independently reviewed
the complete source and test diff, required one category-ownership correction,
reran the required evidence, and approved this gate.
The supervisor's preliminary inspection identified that `/inject-tools` and
`/clear-tools` still lived in the registry module. The implementer corrected
that category-ownership omission, extended the ownership assertion, refreshed
all evidence below, and again stopped before Gate C.

Branch and baseline:

- branch: `feature/friday-chat-command-remediation-1`;
- HEAD: `4f313e9fb5dfb6e83a34d0f5a106b351317bcf75`;
- merge base: `baed8f27ec55519e872ab8ff627fd5022a2fa0c4`;
- `git merge-base --is-ancestor baed8f2 HEAD`: exit `0`;
- the working tree still includes the Gate A directive record and untracked
  production-adapter reproduction. The unrelated untracked
  `docs/dev-skills/subagent-directives-template.md` remains uninspected,
  unmodified, unstaged, and otherwise untouched.

Changed files during Gate B:

- added `packages/friday-chat/src/friday_chat/commands/contracts.py`;
- modified `packages/friday-chat/src/friday_chat/commands/registry.py`,
  `commands/session.py`, `commands/memory.py`, `commands/transcript.py`, and
  `commands/tools.py`;
- modified `packages/friday-chat/src/friday_chat/session.py`, `runtime.py`,
  `app.py`, and `replay.py`;
- added `packages/friday-chat/tests_chat/test_command_foundations.py` and
  `packages/friday-chat/tests_chat/test_session_identity.py`;
- appended this candidate evidence to the directive;
- no frozen framework package, dependency, configuration schema, workspace
  metadata, or persisted schema was changed.

Criteria evidence:

- `commands/contracts.py` is cycle-free at runtime and owns the shared typed
  command arguments, context, metadata, handler, result, and immutable UI-effect
  contract. `commands/registry.py` re-exports the compatibility names;
- only the affected clear-screen, memory, transcript/export, and tool-selection
  handlers and their formatting helpers moved into the four category modules.
  `/inject-tools`, `/clear-tools`, and `/tool-budget` now share
  `commands/tools.py`; the smallest shared runtime-tool list/exact-name lookup
  helpers moved with them and remain reused by the registry-owned neighboring
  tool handlers. `CommandRegistry` remains the sole metadata, alias,
  generated-help, and dispatch registry;
- `SessionIdentity` is a frozen value object. `build_runtime()` resolves or
  generates it once, retains injectable `session_id` compatibility, and accepts
  typed deterministic injection for tests and replay;
- the same identity object reaches runtime, normal app session state, app
  command context, and replay. Its value is propagated to framework memory,
  transcript, and maintenance adapters, and a disposable SQLite write proves
  lazy session creation under that identity;
- typed/string runtime injection mismatch, app-session/runtime mismatch, and
  replay/runtime mismatch raise `SessionIdentityMismatchError`. A same-value app
  session is canonicalized to the runtime-owned identity object;
- the affected production source contains no `friday-v2` identity literal;
- Gate C persisted transcript query/display-effect behavior and Gate D/E memory
  and tool-budget behavior remain intentionally disabled. The Gate A retained
  reproduction remains exactly five expected failures and three passing
  controls.

Validation commands and results:

- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q packages/friday-chat/tests_chat/test_command_foundations.py packages/friday-chat/tests_chat/test_session_identity.py`
  — exit `0`, `7 passed in 1.47s`; the ownership assertion includes
  `/inject-tools` and `/clear-tools` in `friday_chat.commands.tools`;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q packages/friday-chat/tests_chat/test_command_foundations.py packages/friday-chat/tests_chat/test_session_identity.py packages/friday-chat/tests_chat/test_command_registry.py packages/friday-chat/tests_chat/test_session_memory_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_tool_commands.py packages/friday-chat/tests_chat/test_app_lifecycle.py packages/friday-chat/tests_chat/test_runtime.py packages/friday-chat/tests_chat/test_display.py packages/friday-chat/tests_chat/test_turn_processing.py`
  — exit `0`, `110 passed in 1.42s`;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q packages/friday-chat/tests_chat/test_command_production_adapters.py`
  — expected exit `1`, exactly `5 failed, 3 passed in 1.37s`; failures remain
  `/sessions`, current/selected `/transcript`, real `/memory`, clear-screen UI
  effects, and last-turn `/tool-budget`, with no new failure;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/ruff check packages/friday-chat`
  — exit `0`, `All checks passed!`;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/mypy packages/friday-chat/src/friday_chat packages/friday-chat/tests_chat`
  — exit `0`, `Success: no issues found in 80 source files`;
- `git diff --check` — exit `0`, no output;
- `rg -n "friday-v2" packages/friday-chat/src/friday_chat` — exit `1`, no
  matches;
- final scope audit before this append confirmed the expected Friday Chat and
  directive files only, empty staging, unchanged `baed8f2` ancestry, and no
  frozen-framework diff.

Supervisor-independent validation and review:

- the complete Gate B focused suite passed: `110 passed in 1.82s`;
- the Gate A production-path module retained exactly its intended shape:
  expected exit `1`, `5 failed, 3 passed in 1.71s`, with no new failure;
- full Friday Chat Ruff passed and mypy reported no issues in 80 source files;
- source inspection confirmed a runtime-cycle-free command contract module,
  registry-owned metadata/aliases/help/dispatch, and behavior-preserving moves
  of only the affected category handlers and helpers;
- the first review found `/inject-tools` and `/clear-tools` still owned by the
  registry. The implementer moved them and the smallest reused lookup seam into
  `commands/tools.py`, expanded the ownership regression, and reran all evidence;
- identity inspection confirmed one generated or injected immutable value is
  retained by `FridayRuntime`, propagated by value to framework participants,
  reused by app/command/replay state, and guarded by explicit mismatch errors;
- no `friday-v2` production identity literal, Gate C behavior, frozen-package
  change, staged file, provider call, or active-state path was found;
- `git diff --check`, exact scope, empty staging, unrelated-template
  preservation, and `baed8f2` ancestry were independently reconfirmed.

Provider and active-state isolation:

- the production identity test configures vector, graph, transcript, recovery,
  and log paths under its `tmp_path` and asserts every resolved maintenance
  layout path is contained there;
- the test installs fail-closed provider chat/embedding and synchronous/asynchronous
  socket tripwires before real-adapter construction. It performs only a local
  SQLite transcript write and reaches no provider, network, external tool, or
  active `.friday` state;
- no configured example script or real runtime turn was executed.

Security and privacy review:

- no secrets, provider responses, external content, active user data, or
  persisted application state were read or written;
- generated session identities contain only a fixed prefix and random UUID4
  hex value; deterministic injections are validated as non-empty and trimmed;
- no transcript rows are rewritten or migrated.

Unrelated state preserved:

- `docs/dev-skills/subagent-directives-template.md` remains `??` and was not
  inspected, staged, modified, or removed;
- the Gate A production reproduction remains untracked and unchanged;
- staging remains empty, and no commit, push, PR, merge, branch, cleanup, or
  destructive Git operation was performed.

Stop-condition assessment:

- no public API, import-cycle, provider-isolation, disposable-path, package
  boundary, or validation blocker was found;
- no stop condition is active. Gate C has not begun.

Supervisor disposition:

- `PASS`. Typed foundations, handler ownership, identity propagation, runtime
  invariants, compatibility, isolation, and static gates satisfy every Gate B
  criterion. No stop condition is active.

Next-gate direction:

- Gate C is authorized. Implement persisted transcript/query/export behavior
  and terminal clear effects only, then stop for independent Gate C review.

### Gate C: PASS — 2026-08-08

The implementer completed both Gate C workstreams and stopped before Gate D.
The supervising agent independently inspected the implementation and reproduced
the required evidence before closing this gate.

Branch and baseline:

- branch: `feature/friday-chat-command-remediation-1`;
- HEAD: `4f313e9fb5dfb6e83a34d0f5a106b351317bcf75`;
- merge base: `baed8f27ec55519e872ab8ff627fd5022a2fa0c4`;
- final `git merge-base --is-ancestor baed8f2 HEAD`: exit `0`;
- staging remains empty. The inherited Gate A/B source, tests, and execution
  records remain present, and the unrelated untracked
  `docs/dev-skills/subagent-directives-template.md` remains uninspected,
  unmodified, unstaged, and otherwise untouched.

Changed files during Gate C:

- added `packages/friday-chat/src/friday_chat/transcripts.py` with immutable
  session, entry, context-log, and export views plus the narrow asynchronous
  Friday Chat query protocol;
- modified `packages/friday-chat/src/friday_chat/runtime.py` and
  `adapters.py` so fake and framework transcript adapters implement that same
  query protocol using public Friday Transcript APIs;
- modified `packages/friday-chat/src/friday_chat/commands/transcript.py` and
  command metadata in `commands/registry.py` for persisted session,
  transcript, all-session export, current-session export, and context-log
  export behavior;
- modified `commands/session.py`, `app.py`, and `display.py` for the typed
  clear-screen effect, app dispatch, display protocol, and Rich delegation;
- added
  `packages/friday-chat/tests_chat/test_transcript_production_commands.py` and
  updated the affected command-foundation, registry, transcript/export, and
  display tests;
- added proposed framework gap `FU-004` to
  `docs/planning/backlog/friday-chat-framework-followups/upgrade-log.md`;
- appended this candidate evidence to the directive;
- no frozen framework source/test, dependency, configuration schema, workspace
  metadata, persisted schema, Gate D memory behavior, or Gate E tool-selection
  behavior was changed.

Transcript criteria evidence:

- fake and framework adapters return the same Friday Chat-owned typed views.
  The framework mapping uses public `list_sessions()`, `get_session()`,
  paginated `get_entries()`, and `get_context_log_for_session()` calls;
- `/sessions` requests at most 1000 persisted non-archived sessions, normalizes
  newest-first ordering, marks the runtime identity, marks exactly the
  configured prior primed-session count when priming is enabled, and reports a
  lazy current identity as `not persisted` instead of fabricating a row;
- current and selected `/transcript` queries use the exact bound session ID,
  include sanitized session metadata, sort entries chronologically, normalize
  and truncate messages at a deterministic 500-character display bound, and
  cap displayed entries with an explicit omitted count;
- selected IDs containing path separators, Unicode, quotes, semicolons, and
  SQL-like text remain public store query values. They never become path
  components and cannot alter later queries;
- missing current, missing selected, empty, active, ended, archived, and
  unpersisted states have distinct output. Archived sessions remain excluded
  from normal listings/all-session exports but are explicitly readable by ID;
- `/transcript export` queries up to 1000 non-archived sessions before creating
  output, then writes one safely contained timestamped directory containing
  deterministic, all-quoted `sessions.csv` and `entries.csv` files. It reports
  exact session and entry counts and never copies SQLite or exports config
  snapshots;
- `/export` defaults to Markdown and uses the same persisted current-session
  entry views for CSV, JSONL, Markdown/`md`, and training JSONL. CSV is
  all-quoted, output reports exact entry counts, and Markdown uses configured
  user/assistant display names;
- `/export-prompts [session_id]` uses the typed context-log query for current or
  selected sessions, writes a static safely contained JSON filename, reports
  exact counts, and gives capture configuration guidance for an empty log;
- all export queries finish before timestamped directory creation, so a partial
  entry-query failure leaves no partial all-session directory. Query and write
  failures return fixed sanitized errors with no raw SQL, database path,
  transcript content, exception text, or config snapshot;
- two app invocations with generated distinct identities record turns through
  separate framework adapters against one disposable WAL-mode SQLite database.
  The second invocation lists both and reads the first invocation's committed
  transcript while marking it primed;
- production adapter testing exposed a frozen Friday Transcript row-mapping bug:
  `archive_session()` succeeds and normal filtering works, but exact session
  mapping loses `archived=True`. Per the freeze policy, `FU-004` records the
  framework repair. The Friday Chat adapter derives the typed archived flag
  only from public paginated non-archived listings, without private fields or
  SQL.

Display criteria evidence:

- `/cls` and `/clearscreen` resolve to the same category-owned handler and
  return `CommandUiEffect.CLEAR_SCREEN` with an empty normal output;
- app dispatch invokes exactly one `DisplayController.clear_screen()` call per
  command and emits no replacement `Screen cleared.` text on success;
- an absent display produces
  `Unable to clear the terminal: display is unavailable.`; a raised display
  exception produces `Unable to clear the terminal.` with no raw exception
  detail;
- production `FridayCliDisplay.clear_screen()` delegates to the shared Rich
  console's public `clear()` operation;
- platform-neutral recording tests observe the boundary, and the provider-free
  POSIX PTY smoke passed after observing Rich's clear/home control sequences.

Validation commands and results:

- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_display.py packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_command_registry.py`
  — exit `0`, `45 passed in 1.09s`;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q packages/friday-chat/tests_chat/test_display.py::test_production_clear_emits_control_sequence_through_pty`
  — exit `0`, `1 passed in 0.41s`; the POSIX PTY observed both Rich clear and
  cursor-home control sequences with no provider or external tool;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_command_foundations.py packages/friday-chat/tests_chat/test_session_identity.py packages/friday-chat/tests_chat/test_command_registry.py packages/friday-chat/tests_chat/test_session_memory_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_tool_commands.py packages/friday-chat/tests_chat/test_app_lifecycle.py packages/friday-chat/tests_chat/test_runtime.py packages/friday-chat/tests_chat/test_display.py packages/friday-chat/tests_chat/test_turn_processing.py`
  — exit `0`, `122 passed in 1.48s`;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q packages/friday-chat/tests_chat/test_command_production_adapters.py`
  — expected exit `1`, exactly `2 failed, 6 passed in 1.23s`. The sessions,
  current/selected transcript, and clear-screen targets now pass; only the
  intentionally deferred Gate D real-memory and Gate E last-turn tool-budget
  targets remain red;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q packages/friday-chat/tests_chat`
  — expected interim exit `1`, `2 failed, 325 passed in 9.07s`, consisting only
  of those same retained Gate D/E production targets;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q packages/friday-chat/tests_chat --ignore=packages/friday-chat/tests_chat/test_command_production_adapters.py`
  — exit `0`, `319 passed in 8.24s`;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/ruff check packages/friday-chat`
  — exit `0`, `All checks passed!`;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/mypy packages/friday-chat/src/friday_chat packages/friday-chat/tests_chat`
  — exit `0`, `Success: no issues found in 82 source files`;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/python -c "from friday_runtime import RuntimeKernel; from friday_agent import InteractiveAgent; print('Friday imports OK')"`
  — exit `0`, `Friday imports OK`;
- `git diff --check` — exit `0`, no output;
- final scope audit before this append confirmed empty staging, unchanged
  `baed8f2` ancestry, no frozen-package diff, and no obsolete production
  `Screen cleared.`, `current-session`, or `friday_transcripts.csv` literals.

Provider and active-state isolation:

- Gate C production transcript tests pair deterministic fake chat/memory/tool
  services with the real `FrameworkTranscriptAdapter` and public
  `SQLiteTranscriptStore`; no provider-backed chat or embedding service is
  constructed or called;
- an autouse fail-closed tripwire intercepts synchronous and asynchronous socket
  connection attempts before I/O;
- every SQLite and export path used by Gate C resolves under its test
  `tmp_path`. The tests perform only local SQLite and export writes and a local
  PTY clear sequence;
- no active `.friday` state, configured example script, provider, network,
  external service, browser, shell command tool, or external Friday tool was
  used.

Security and privacy review:

- test sessions, messages, prompts, responses, and configuration values are
  synthetic markers;
- selected identifiers remain bound public API values and are never joined to
  export paths;
- exported session views omit system prompts and configuration snapshots, CSV
  quoting is deterministic, and no live database file is copied;
- fixed failure responses suppress raw SQL, filesystem paths, transcript
  content, exception messages, and configuration details;
- successful clear produces no false acknowledgment, and failure output does
  not expose terminal exception details.

Unrelated state preserved:

- `docs/dev-skills/subagent-directives-template.md` remains `??` and was not
  inspected, staged, modified, or removed;
- the retained Gate A module remains untracked and its assertions were not
  weakened; its expected shape advanced only for the three Gate C targets;
- no cache, generated state, active state, unrelated source, or frozen package
  was cleaned or intentionally modified;
- no file was staged, committed, pushed, merged, or included in a PR.

Stop-condition assessment:

- no private framework access, schema migration, database copy, provider,
  active-state path, export escape, package-boundary violation, waiver, broad
  suppression, or unexpected Gate C failure remains;
- `FU-004` is a documented framework correctness improvement, not a missing
  Gate C capability: the existing public filtered and exact-ID APIs support the
  typed app workaround and its production tests;
- no stop condition is active. Gate D has not begun, and the two later-gate
  production assertions remain intentionally red.

Supervisor disposition:

- `PASS`. The supervising agent independently reviewed the typed transcript
  boundary, public framework-adapter calls, path containment, deterministic
  export behavior, failure sanitization, display effect dispatch, production
  tests, and `FU-004`. The public-only archived-session workaround is adequate
  for Friday Chat while the frozen framework mapping defect remains recorded
  for later repair.
- Independent validation reproduced `45 passed`, `122 passed`, `319 passed`
  with the retained later-gate module excluded, and `1 passed` for the PTY
  smoke. The retained production-adapter module failed only the two expected
  Gate D/E assertions (`2 failed, 6 passed`). Ruff, mypy over 82 files, the
  import smoke, `git diff --check`, baseline ancestry, frozen-package scope,
  obsolete-literal search, and empty staging all passed.
- No directive stop condition is active. The implementer did not approve its
  own work.

Next-gate direction:

- Gate D is authorized. Implement the memory statistics and typed memory-query
  workstream only, preserve the Gate E retained failure, then stop for
  independent Gate D review.

### Gate D: PASS — 2026-08-08

The implementer completed only `CCR-04` and stopped before Gate E. The
supervising agent independently inspected the implementation, required and
reviewed two boundedness corrections, and reproduced the required evidence
before closing this gate. The implementer did not approve its own work.

Branch and baseline:

- branch: `feature/friday-chat-command-remediation-1`;
- HEAD remains `4f313e9fb5dfb6e83a34d0f5a106b351317bcf75` because no commit was
  authorized;
- `git merge-base --is-ancestor baed8f2 HEAD`: exit `0`;
- the inherited Gate A through C worktree remains present and unstaged;
- staging is empty;
- the unrelated untracked
  `docs/dev-skills/subagent-directives-template.md` remains uninspected,
  unmodified, unstaged, and otherwise untouched.

Changed files during Gate D:

- added `packages/friday-chat/src/friday_chat/memory_views.py` with immutable
  availability-aware metrics, complete/store statistics snapshots, closed
  record kinds, bounded record views, and typed query warnings/results;
- modified `packages/friday-chat/src/friday_chat/runtime.py` and `adapters.py`
  so fake and framework memory implementations expose the same typed
  statistics and record-query methods, plus a typed current-session clear
  operation replacing the remaining command-side fake `stored_turns` reads;
- modified `packages/friday-chat/src/friday_chat/commands/memory.py` to render
  session, episodic, vector, graph, transcript, lifecycle/access-buffer,
  priming, and last-context sections without magic zeros, and to render typed
  insight, summary, and meta results;
- modified `packages/friday-chat/src/friday_chat/commands/contracts.py` and
  `app.py` so command state retains the active `FridaySession` and the most
  recent typed `BudgetStatus`;
- modified `packages/friday-chat/src/friday_chat/commands/registry.py` to use
  the public typed current-session clear operation and clear retained budget
  diagnostics during reset without changing Gate E tool-selection behavior;
- added
  `packages/friday-chat/tests_chat/test_memory_diagnostics_commands.py` and
  updated `test_session_memory_commands.py` for the honest diagnostic and
  actionable meta contracts;
- appended this candidate record only. No frozen framework source/test,
  dependency, workspace metadata, configuration schema, persisted schema,
  migration, Gate E tool-selection logic, or unrelated file was changed.

Criteria evidence:

- `MemoryMetric[T]` explicitly distinguishes `available`, `unavailable`, and
  `not_configured`; construction invariants reject an available metric without
  a value. Tests prove a returned zero remains an available zero while absent
  components carry no fabricated value;
- `FrameworkMemoryAdapter.query_memory_statistics()` reads only public typed
  component APIs: `InMemoryEpisodicStore.get_turn_count()`, public
  `CollectionManager` collection properties and `count()`, public
  `ElementXGraphStore`/`NullGraphStore` node and edge reads,
  `AccessBuffer.get_stats()`, and `MemoryController.get_priming_info()`.
  Command assembly adds public `TranscriptQueryStore.query_entries()`, typed
  `FridaySession` state, validated Friday Chat config, and retained
  `BudgetStatus`; no private framework attribute or boundary cast was added;
- the seeded disposable production test reports episodic `1`, vector
  short-term `1`, long-term `1`, decayed `1`, active total `2`, total `3`,
  graph nodes `2`, relationships `1`, transcript entries `1`, access-buffer
  entries `1` and accesses `2`, priming enabled with two previous sessions,
  one in-process turn, two tracked IDs, one scoped variable, and the exact
  retained context budget values;
- lifecycle-disabled production coverage reports graph and access-buffer values
  as `not configured`; pre-turn context values report `unavailable (no
  completed turn)`; configured empty stores report actual `0`;
- `MemoryRecordKind`, `MemoryRecordView`, and `MemoryRecordQueryResult` replace
  the three dynamic `list_insights`, `list_summaries`, and
  `list_meta_insights` paths. A focused source search confirms those methods,
  the memory-command `hasattr` fallback, and private component access are
  absent from the affected implementation;
- `/meta` still queries both short- and long-term collections, deliberately
  excludes decayed records, and says so in every meta response. It renders
  bounded record ID/text and at most eight bounded source IDs, collection,
  lifecycle stage, creation time, confidence, scalar-safe source count,
  provenance source type, verification state, and verification confidence;
- the provider-free visibility test constructs the inherited public
  `MemoryVectorAddition` synthesis contract and persists its scalar-safe
  mutation metadata. Both short- and long-term records are visible, the
  decayed control is absent, and source count `2`, synthesis provenance,
  verified state, and confidence are rendered without synthesis,
  reorganization, or provider execution;
- a fully empty meta query returns the required reorganization/help guidance
  and leaves public collection statistics unchanged. A one-store query failure
  retains the available store's record and a typed warning. A one-store count
  failure retains the other exact counts while dependent totals become
  unavailable; raw exception text and database paths are absent;
- untrusted record/session strings have terminal controls removed and bounded
  output. Store errors are reduced to fixed reason categories; record queries
  use the closed enum as the metadata filter; cancellation is propagated
  rather than recategorized as a successful partial read;
- `FridayChatApp._record_turn_state()` retains the exact typed `BudgetStatus`
  on command state. The app-level regression proves `/memory` can report the
  completed turn's total, message, tool-schema, available-budget, utilization,
  and severity values. `/tool-budget` remains unchanged for Gate E.

Independent-review correction:

- the supervisor held Gate D open after finding two boundedness omissions in
  the candidate. The command now applies its own 100-record slice before
  rendering either ordinary or meta records; the production adapter's existing
  100-record slice remains defense in depth. A fake returns
  105 valid typed insights and the regression proves exactly records `000`
  through `099` render while record `100` does not;
- scalar source lineage is rejected before `json.loads()` when it exceeds
  either 32,000 characters or 32,000 UTF-8 bytes. Decoded lists use only a
  nine-element slice: eight bounded visible IDs plus one truncation probe. The
  original list is never iterated, oversized/malformed scalar lineage is safely
  omitted, and the independently validated scalar `source_count` remains
  visible;
- regressions prove both the character and multibyte byte pre-parse bounds,
  verify `json.loads()` is not called for either oversized scalar, and use a
  1,000-element list probe that raises if the original collection is iterated.
  Output retains source count `1000`, renders only IDs `000` through `007`,
  adds truncation evidence, and excludes ID `008`;
- no other Gate D behavior changed, Gate E remains untouched, and the
  correction required no framework API or frozen-package modification.

Validation commands and results:

- `uv run pytest -q packages/friday-chat/tests_chat/test_memory_diagnostics_commands.py`:
  exit `0`, `12 passed in 1.21s` after the independent-review correction;
- the directive's eight focused modules plus the Gate D module: exit `0`,
  `120 passed in 1.58s`;
- `uv run pytest -q packages/friday-chat/tests_chat/test_command_production_adapters.py`:
  expected exit `1`, exactly `1 failed, 7 passed in 1.20s`; the sole failure is
  `test_tool_budget_reports_schemas_selected_for_real_turn`, retained for Gate
  E. The Gate D episodic and meta targets pass;
- package tests excluding that retained later-gate module: exit `0`,
  `331 passed in 8.07s`;
- full `packages/friday-chat/tests_chat`: expected exit `1`, exactly `1 failed,
  338 passed in 8.31s`, with the same sole Gate E failure;
- `uv run ruff check packages/friday-chat`: exit `0`, all checks passed;
- `uv run mypy packages/friday-chat`: exit `0`, no issues in `84` source
  files;
- import smoke for `RuntimeKernel`, `InteractiveAgent`,
  `MemoryStatisticsSnapshot`, and `MemoryRecordView`: exit `0`, `Friday imports
  OK`;
- `git diff --check`, frozen-package `git diff --quiet`, empty-index
  `git diff --cached --quiet`, baseline ancestry, and the obsolete/private
  access search all exit `0`;
- root `uv run pytest`: expected baseline exit `2`. The implementer observed
  the documented Friday Chat/Friday CLI `test_display.py` import-file mismatch
  as the sole collection error. The supervisor reran this after the three
  boundedness regressions were added and observed `1992` collected items with
  the same sole error. No cache was deleted or renamed to hide it.

Provider and active-state isolation:

- all Gate D production persistence, transcript, graph, access-WAL, recovery,
  export, and log paths are resolved below each test's `tmp_path` and asserted
  outside both repository and user `.friday` roots;
- the Gate D autouse tripwire replaces provider chat/embedding methods and
  synchronous/asynchronous socket connection boundaries with fail-closed test
  assertions. The retained production module's positive tripwire test also
  passes;
- all embeddings are deterministic in-process values. No provider, network,
  external service, external tool, active `.friday` state, or ordinary
  provider-backed chat turn was used.

Security and privacy review:

- no raw exception, database path, prompt, transcript content, config snapshot,
  credential, or provider response is included in a diagnostic warning;
- queried memory text is intentionally user-visible but normalized to remove
  terminal controls and bounded before rendering. Record IDs, lifecycle and
  provenance labels, source IDs, and session identity are also bounded and
  control-sanitized;
- scalar-safe synthesis provenance is decoded with bounded JSON handling;
  malformed records are omitted with a typed warning rather than dynamically
  dumped. Decayed records remain excluded from active record queries;
- no provider/tool execution, mutation, synthesis, reorganization, database
  copy, path derivation from untrusted data, private framework access, policy
  waiver, broad type suppression, or essential `assert`-only runtime invariant
  was introduced.

Package, config, persistence, and migration impact:

- package impact is confined to `packages/friday-chat` source/tests and this
  execution record; Friday Chat continues to compose existing public Friday
  Memory and Friday Transcript APIs;
- no dependency, config model/default, environment variable, workspace
  metadata, persistence layout/schema, default data root, reorganization
  artifact/recovery format, or migration changed;
- no framework upgrade entry was needed because every Gate D operation exists
  on a public typed API in the configured concrete framework components.

Unrelated state preserved:

- `docs/dev-skills/subagent-directives-template.md` remains `??` and was not
  inspected, staged, modified, or removed;
- all inherited Gate A through C source, tests, planning records, and `FU-004`
  remain present;
- no active state, cache, generated state, frozen package, or unrelated source
  was cleaned or intentionally modified;
- no file was staged, committed, pushed, merged, or included in a PR.

Stop-condition assessment:

- the authorized branch and baseline remain valid;
- required public typed operations were sufficient. No frozen-package change,
  private access, schema/migration/dependency change, active-state/provider
  requirement, recovery behavior change, policy waiver, unexpected test
  failure, or missing Gate D evidence remains;
- no stop condition is active. Gate E has not begun, and its one retained
  production assertion remains intentionally red.

Supervisor disposition:

- `PASS`. The supervising agent independently reviewed the typed snapshot and
  record contracts, public framework-adapter calls, status aggregation,
  current-session and retained-budget composition, meta formatting, failure
  sanitization, provider isolation, and the corrected output/lineage bounds.
- Independent validation reproduced `12 passed` for the Gate D module, `120
  passed` for the required focused set, and `331 passed` for the package with
  the retained later-gate module excluded. The retained module failed only its
  Gate E `/tool-budget` assertion (`1 failed, 7 passed`), and the full package
  had the same sole failure (`1 failed, 338 passed`). Ruff, mypy over 84 files,
  imports, whitespace, ancestry, empty staging, frozen-package scope, and the
  obsolete/private-access search passed.
- The root gate continues to reproduce only the documented collection-name
  collision. No directive stop condition is active.

Next-gate direction:

- Gate E is authorized. Implement unified tool selection and budget enforcement
  only, then stop for independent Gate E review.

### Gate E: PASS — 2026-08-08

The implementer completed only `CCR-05` and stopped before Gate F. The
supervising agent independently inspected the implementation, required and
reviewed the automatic-state reporting correction, and reproduced the required
evidence before closing this gate. The implementer did not approve its own
work.

Changed files during Gate E:

- `packages/friday-chat/src/friday_chat/tools/selection.py` (new);
- `packages/friday-chat/src/friday_chat/runtime.py`;
- `packages/friday-chat/src/friday_chat/turns/processor.py`;
- `packages/friday-chat/src/friday_chat/commands/tools.py`;
- `packages/friday-chat/src/friday_chat/commands/contracts.py`;
- `packages/friday-chat/src/friday_chat/app.py`;
- `packages/friday-chat/src/friday_chat/adapters.py`;
- `packages/friday-chat/tests_chat/test_tool_selection_budget.py` (new);
- `packages/friday-chat/tests_chat/test_tool_commands.py`;
- this construction directive.

Implemented behavior:

- `FridayRuntime` now owns one `ToolSelectionState`. The prior
  command-local `injected_tools` set is removed. The state owns automatic,
  manual, and disabled modes; the accepted manual names; the synchronized
  registered definitions; the most recent completed-turn snapshot; the most
  recent completed automatic-turn snapshot; and the most recent executed
  names;
- immutable `ToolBudgetSnapshot` evidence records mode, registered/manual/
  selected names, selected categories, categorical rejections, schema tokens,
  the exact schema-token ceiling, maximum tool count, configured ratio,
  available input context, utilization, and canonical schema bytes;
- `ToolBudgetCalculator` is the sole schema serializer and estimator. It
  serializes the exact model-bound OpenAI-shaped definitions as deterministic
  UTF-8 JSON and estimates `ceil(byte_length / 4)`. Its exact ceiling is
  `floor((memory.context_window - memory.output_buffer) *
  tools.context.max_budget_ratio)` and count enforcement uses
  `tools.context.max_tools`;
- automatic selection preserves deterministic relevance-score and registry
  ordering, then excludes count- or token-overflow candidates with categorical
  reasons. `/inject-tools` validates the entire deduplicated request before one
  authoritative mutation. Unknown, count-overflow, token-overflow, and
  disabled requests leave the accepted manual set unchanged;
- an accepted manual set is exactly the schema set bound to every following
  model turn and tool context hint until `/clear-tools` restores automatic
  selection. Runtime registry replacement is synchronized through the same
  state with explicit duplicate-name and invalid-active-manual invariants;
- turn preparation obtains definitions and budget evidence once from the
  runtime state. Those exact definitions are passed to the deterministic model,
  used to build the optional context hint, and represented in `TurnResult` as
  `selected_tool_names` plus the immutable snapshot;
- snapshot schema tokens drive dynamic retrieval budgeting,
  `BudgetStatus.tool_tokens`, `TurnResult.tool_schema_tokens`, and command
  reporting. Dynamic retrieval and `BudgetStatus.available_budget` use the
  snapshot's canonical available input context, preserve a configured
  `output_buffer: 0`, and never expand a small available context to the old
  512-token floor;
- `FrameworkMemoryAdapter.retrieve()` now distinguishes an explicit zero
  `token_limit` from `None`, and its no-limit/debug fallback derives available
  input context from `ToolBudgetCalculator`. An exact zero therefore reaches
  recall instead of expanding to a default;
- completed turns retain the immutable selection evidence and unique executed
  names in runtime state. `FridayChatApp` retains the same snapshot in command
  state. Provider response size and tool-result payloads are not calculator
  inputs and cannot mutate the frozen snapshot;
- `/tool-budget` now distinguishes current mode, registered tools, pending
  manual set, the current estimate source, most recent automatic selection,
  last completed-turn mode and selection, most recent executed tools, no-turn
  state, schema tokens, exact limit, maximum count, ratio, utilization, and
  categorical automatic rejections. Disabled and empty registries report a
  clear zero state;
- `/inject-tools` and `/tool-budget` normalize terminal-facing tool metadata,
  remove Unicode control/format characters, bound each value, and cap rendered
  name/category/rejection collections. Authoritative names, categories, and
  canonical schema bytes remain exact for lookup and model identity;
- the undocumented `max_schema_budget_percent` lookup and its command-local
  name-based estimate are removed. No compatibility alias, migration, or
  second estimator was introduced.

Independent-review correction:

- the supervisor held Gate E open because the initial candidate used
  `manual or last_completed_turn` as the displayed estimate. After a manual
  turn followed by `/clear-tools`, that made automatic mode display stale
  manual schema tokens and utilization;
- `ToolSelectionState` now retains the most recent completed automatic
  snapshot separately from the overall last completed-turn snapshot and its
  executed names. Recording a manual or disabled turn cannot overwrite the
  automatic snapshot;
- command output explicitly labels `pending_manual`, `estimate_source`,
  `automatic_selected`, `automatic_schema_tokens`, `last_completed_mode`,
  `last_selected`, `last_schema_tokens`, and `executed`. Pending manual mode
  uses its validated preview; automatic mode uses the most recent completed
  automatic snapshot; automatic mode with no prior automatic turn reports
  `automatic_pre_turn`, zero estimated schema tokens, and no automatic
  selection. The actual last manual turn remains visible separately;
- one regression runs an automatic turn, a differently sized manual turn, and
  `/clear-tools`, then proves the estimate returns to the earlier automatic
  snapshot while the last completed mode/selection/schema remain manual. A
  second starts with a manual turn, clears it without any automatic history,
  and proves the command reports an honest automatic pre-turn state instead of
  reusing the manual estimate;
- no other selection, calculation, execution, provider, context, config, or
  persistence behavior changed.

Gate E regression evidence:

- the new deterministic module covers automatic/manual transitions, exact
  manual persistence, clear-to-automatic restoration, atomic unknown/count/
  token rejection, exact-token acceptance, one-token overflow, count overflow,
  deterministic automatic and manual ordering, count/token rejection reasons,
  disabled and empty registries, manual and automatic no-turn displays,
  selected-versus-executed display, and app snapshot retention;
- a recording chat model proves the snapshot's canonical bytes and selected
  names exactly match the definitions passed on the model call. The same
  snapshot value drives `TurnResult`, dynamic retrieval, and
  `BudgetStatus.tool_tokens`;
- provider responses of materially different sizes produce identical schema
  bytes and token estimates. Synthetic short and 10,000-character
  `ToolCallRecord` result payloads share the same precomputed immutable
  snapshot; the Gate E module invokes no tool implementation;
- a one-token available context with `output_buffer: 0` produces canonical
  available budget `1`, dynamic retrieval budget `0`, and an exact recorded
  retrieval limit of `0`. A framework-adapter regression proves explicit zero
  is forwarded to recall unchanged;
- hostile names/categories and a 10,000-character unknown name retain exact
  authoritative/model schema identity while command output contains no
  terminal escape controls and remains bounded.

Validation commands and results:

- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q
  packages/friday-chat/tests_chat/test_tool_selection_budget.py`: exit `0`,
  `15 passed in 1.00s` after the independent-review correction;
- the directive's eight focused modules plus the Gate E module: exit `0`,
  `123 passed in 1.39s`;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q
  packages/friday-chat/tests_chat/test_command_production_adapters.py`: exit
  `0`, `8 passed in 1.19s`; the retained Gate E `/tool-budget` production
  assertion is now green;
- full `packages/friday-chat/tests_chat`: exit `0`, `354 passed in 8.59s`;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/ruff check
  packages/friday-chat`: exit `0`, all checks passed;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/mypy packages/friday-chat`: exit
  `0`, no issues in `86` source files;
- the required `RuntimeKernel`/`InteractiveAgent` import smoke: exit `0`,
  `Friday imports OK`;
- `git diff --check`, empty-index inspection, baseline ancestry, frozen-package
  scope inspection, and searches for `max_schema_budget_percent` and
  `injected_tools` and the rejected `current = manual or last` expression in
  Friday Chat source/tests all pass;
- root `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest`: expected baseline exit
  `2`, `2007` items collected with the documented Friday Chat/Friday CLI
  `test_display.py` import-file mismatch as the sole collection error. No cache
  was deleted or renamed to hide it.

Provider, tool, active-state, and security isolation:

- Gate E tests use only deterministic in-process models, inert definitions,
  synthetic result records, fake memory, or the retained disposable
  production-shaped adapter fixture. The new Gate E module does not invoke a
  tool implementation;
- the retained production module's provider/network fail-closed tripwires and
  disposable path-containment assertions pass. No provider, network, external
  service, external tool, shell/filesystem tool, active `.friday` state, or
  ordinary provider-backed turn was used;
- terminal-facing metadata and rejected names are control-sanitized and
  bounded without modifying authoritative lookup strings or model schema
  bytes. No raw provider response or tool-result content enters budget command
  output;
- no broad type suppression, policy waiver, essential `assert`-only runtime
  invariant, private cross-package API, or frozen framework change was used.

Package, config, persistence, and migration impact:

- package impact is confined to `packages/friday-chat` source/tests and this
  execution record. Existing Friday Chat protocols and public framework
  adapters were sufficient; no framework upgrade entry was needed;
- the existing `tools.context.max_tools`, `tools.context.max_budget_ratio`,
  `memory.context_window`, and `memory.output_buffer` values now have enforced
  runtime behavior. No config schema/default, environment variable,
  dependency, workspace metadata, persisted schema/layout, default data root,
  reorganization artifact/recovery format, or migration changed;
- no dual-key support exists for the removed undocumented percentage lookup.

Unrelated state preserved:

- `docs/dev-skills/subagent-directives-template.md` remains `??` and was not
  inspected, staged, modified, or removed;
- all inherited Gate A through D work and `FU-004` remain present;
- no active state, cache, generated state, frozen package, or unrelated source
  was cleaned or intentionally modified;
- no file was staged, committed, pushed, merged, or included in a PR.

Stop-condition assessment:

- the authorized branch and `baed8f2` ancestry remain valid;
- required public/config/runtime contracts were sufficient. No frozen-package
  change, absent public capability, migration/dependency change,
  active-state/provider/external-tool requirement, recovery behavior change,
  policy waiver, unexpected test failure, or missing Gate E evidence remains;
- no stop condition is active. Gate F has not begun.

Supervisor disposition:

- `PASS`. The supervising agent independently reviewed the runtime-owned state,
  immutable snapshot, canonical schema serialization/estimation, automatic and
  manual selection, atomic rejection, exact-boundary arithmetic, context and
  `BudgetStatus` consumers, model-bound schema identity, app retention,
  `/tool-budget` state distinctions, explicit-zero propagation, and bounded
  terminal output.
- Independent validation reproduced `15 passed` for the Gate E module, `123
  passed` for the required focused set, `8 passed` for the retained production
  module, and `354 passed` for the full Friday Chat package. Ruff, mypy over 86
  files, imports, whitespace, ancestry, empty staging, frozen-package scope,
  and obsolete-state/config searches passed.
- Root pytest continues to reproduce only the documented Friday Chat/Friday
  CLI `test_display.py` collection-name collision (`2007` items, exit `2`). No
  directive stop condition is active.

Next-gate direction:

- Gate F is authorized for documentation, complete validation, and disposable
  UAT only. Do not remove containment or enable any new execution path; if
  either becomes necessary, stop for explicit user approval.

### Gate F: PASS — 2026-08-08

Execution date: 2026-08-08

Builder disposition was `CANDIDATE`; the independent supervising agent reviewed
the implementation, required corrections, reran the gates, and records `PASS`
below. This is not a publication or integration decision.

Implemented close-out:

- canonical registry metadata now describes the final production behavior for
  `/cls`/`/clearscreen`, `/memory`, `/meta`, `/sessions`, `/transcript`,
  `/export`, `/export-prompts`, `/tools`, `/inject-tools`, `/clear-tools`, and
  `/tool-budget`; retained registry assertions prevent help-text drift;
- the behavioral contract now records immutable per-invocation identity,
  persisted public transcript query/export, typed honest memory availability,
  active/provenance-bearing non-mutating meta queries, authoritative automatic
  and manual tool snapshots, and typed display-clear semantics;
- parity rows advance to `verified` only where disposable production adapters
  or the real app/CLI UAT provide evidence. Unaffected rows remain `tested`;
- no Gate F public-API/frozen-package gap was discovered, so the framework
  upgrade log was not changed during this gate.

Six reported command areas:

1. `/sessions`: lists persisted transcript sessions through the public typed
   query API, with current and primed identity markers.
2. `/transcript` plus transcript exports: queries persisted current, selected,
   and all-session data; current/all/prompt exports are safely contained and do
   not copy SQLite.
3. `/tool-budget` plus `/inject-tools` and `/clear-tools` support: query-aware
   automatic and persistent validated manual selection share count/token
   limits, the canonical estimator, immutable turn snapshot, context budget,
   model schema payload, and reported state. Clear restores automatic mode and
   selected/executed tools remain distinct.
4. `/cls` and `/clearscreen`: both aliases return one typed clear effect, the
   app invokes the display boundary exactly once, successful clear emits no
   normal output, and supported-platform PTY evidence observes two clear/home
   sequence pairs.
5. `/memory`: reports exact available episodic, lifecycle-vector, graph,
   transcript, access-buffer, priming, app-session, and context values; missing
   sources remain typed unavailable/not-configured rather than fake zeroes.
6. `/meta`: queries existing short- and long-term `meta_insight` records,
   renders source lineage and verification provenance, excludes decayed
   records, provides actionable empty guidance, and never synthesizes or runs
   reorganization.

Cross-cutting session-identity evidence is separate from those six reported
command areas: one immutable `session_<unique-id>` is generated per production
invocation and propagated through runtime, memory, transcript, maintenance,
app, commands, and replay. Explicit mismatches fail.

Disposable real app/CLI UAT:

- retained module:
  `packages/friday-chat/tests_chat/test_command_disposable_uat.py`;
- configuration is loaded from the repository example at
  `packages/friday-chat/config.example.yaml`, then provider endpoints are made
  inert and every declared persistence, export, log, recovery, vector,
  transcript, graph, lifecycle WAL, and quarantine path is resolved under one
  fresh temporary root. Assertions exclude repository and home `.friday`;
- public operations seed current and selected transcript sessions/entries, one
  explicit episodic turn, active short- and long-term lifecycle records, two
  graph nodes and one edge, access-buffer state, and one
  reorganization-compatible synthesized meta insight with source and
  verification provenance;
- deterministic in-process chat and embedding doubles are installed behind the
  production runtime boundaries. Fail-closed provider and socket tripwires
  remain armed;
- a deterministic pre-sequence turn produces automatic `echo` selection and
  proves the immutable snapshot bytes equal the exact model tool-schema bytes;
  the real registry records no execution;
- production CLI input, output, display, and a real POSIX PTY exercise exactly:
  `/sessions`, `/transcript`, `/transcript uat-seeded-session`, `/memory`,
  `/meta`, `/tools`, `/tool-budget`, `/inject-tools echo`, `/tool-budget`,
  `/clear-tools`, `/cls`, `/clearscreen`, `/q`;
- output proves current/selected identity, persisted transcript contents, exact
  seeded memory/graph counts, meta provenance and decayed exclusion, registered
  tools, last-automatic then pending-manual budget state, restored automatic
  state after clear, two PTY clear effects, clean command exit, and zero app
  chat turns. Provider/network tripwires do not fire and tool calls remain
  empty.

Validation commands and results:

- directive eight-module focused command: exit `0`, `109 passed in 1.54s`;
- repository-example disposable UAT alone: exit `0`, `1 passed in 1.23s`;
- retained production adapters plus disposable UAT: exit `0`, `9 passed in
  1.38s`;
- registry plus UAT metadata check: exit `0`, `17 passed in 1.14s`;
- full `packages/friday-chat/tests_chat`: exit `0`, `356 passed in 8.80s`;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/ruff check
  packages/friday-chat`: exit `0`, all checks passed;
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/mypy packages/friday-chat`: exit `0`,
  no issues in `87` source files;
- required `RuntimeKernel`/`InteractiveAgent` import smoke: exit `0`, `Friday
  imports OK`;
- `git diff --check`, `baed8f2` ancestry, and authorized-scope inspection pass;
- root `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest`: expected baseline exit
  `2`, `2009` items collected, with the documented Friday Chat/Friday CLI
  `test_display.py` import-file mismatch as the sole collection error. No cache
  was deleted or renamed to hide it.

Deferred and blocked items:

- no Gate F implementation or validation item is blocked;
- the optional `scripts/run-friday-chat-example.sh` smoke remains deferred
  because it reads real example configuration and active local stores and
  requires separate explicit authority. It is not needed for candidate
  evidence and was not run;
- no new framework gap exists. Existing `FU-004` remains the Gate C Friday
  Transcript archived-session row-mapping/public-API limitation and is not a
  Gate F blocker.

Isolation, policy, and scope:

- no provider, network service, configured Kimi endpoint, external tool,
  active `.friday` state, or direct `/reorganize --execute` path was used;
- no config schema/default/example, dependency, workspace metadata, database
  schema/layout, migration, recovery artifact format, or default data root
  changed;
- no frozen framework package, private cross-package API, broad type
  suppression, policy waiver, or essential `assert`-only production invariant
  was added;
- unrelated `docs/dev-skills/subagent-directives-template.md` remains untracked
  and untouched. No file was staged, committed, pushed, merged, or placed in a
  PR.

Final changed-file and package-boundary report:

- planning records: `docs/archive/completed/2026/friday-chat-command-remediation/plan.md`, this
  directive, `friday-chat-v2-behavioral-contracts.md`,
  `friday-chat-v2-framework-upgrade-log.md`, and
  `friday-chat-v2-parity-matrix.md`;
- Friday Chat source: `adapters.py`, `app.py`, `display.py`, `replay.py`,
  `runtime.py`, `session.py`, `transcripts.py`, `memory_views.py`,
  `commands/contracts.py`, `commands/memory.py`, `commands/registry.py`,
  `commands/session.py`, `commands/tools.py`, `commands/transcript.py`,
  `tools/selection.py`, and `turns/processor.py`;
- Friday Chat tests: `test_command_disposable_uat.py`,
  `test_command_foundations.py`, `test_command_production_adapters.py`,
  `test_command_registry.py`, `test_display.py`,
  `test_memory_diagnostics_commands.py`, `test_session_identity.py`,
  `test_session_memory_commands.py`, `test_tool_commands.py`,
  `test_tool_selection_budget.py`, `test_transcript_export_commands.py`, and
  `test_transcript_production_commands.py`;
- package impact is limited to `packages/friday-chat`; no frozen framework
  source/test, configuration example, schema, dependency, or workspace metadata
  changed. `FU-004` is documentation only.

Stop-condition assessment:

- branch ancestry remains valid and all required public/config/runtime
  contracts were sufficient;
- there is no missing authority, migration requirement, provider/active-state
  dependency, unexpected package failure, recovery divergence, or frozen
  package requirement. No stop condition is active.

Recommended merge order after independent approval:

1. merge `feature/reorg-remediation-1` first;
2. merge `feature/friday-chat-command-remediation-1` second;
3. run the same focused/package/static/root checks in the integration target;
4. keep the configured active-state smoke optional and separately authorized.

Supervisor disposition:

- `PASS`. The supervising agent independently reviewed the registry-generated
  help metadata, behavioral contracts, parity claims, repository-example
  disposable UAT, final scope, package boundaries, and stop conditions.
- Independent validation reproduced `109 passed` for the prescribed focused
  modules, `1 passed` for the UAT, `9 passed` for production adapters plus UAT,
  `17 passed` for registry metadata plus UAT, and `356 passed` for the full
  Friday Chat package. Ruff, mypy over 87 source files, framework import smoke,
  whitespace, ancestry, empty staging, and authorized-scope checks passed.
- Root pytest remains a documented baseline failure only: exit `2`, `2009`
  items collected, with the Friday Chat/Friday CLI `test_display.py` import-file
  mismatch as the sole collection error. No stop condition remains active.
- All directive gates are closed. No containment was removed and no execution
  path was enabled at Gate F. The authorized pre-implementation checkpoint is
  the only implementation-session commit/push; no later staging, commit, push,
  PR, or merge occurred.
