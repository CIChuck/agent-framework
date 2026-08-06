# Construction Directive: Reorganization Remediation 1

Status: Approved construction directive
Date: 2026-08-06
Expected branch: `feature/reorg-remediation-1`
Baseline ancestor: `9d4eac0`
Approval state: Approved by maintainer for supervised execution
Controlling plan: [Reorganization Remediation Plan 1](../reorg-remediation-plan-1.md)

## AI Builder Role

You are the implementation agent for Friday Chat memory-reorganization
remediation. Your job is to make manual and configurable exit reorganization
safe, correctly wired, recoverable, observable, and testable across Friday
Chat, Friday Memory, and Friday Transcript.

This is destructive-capable persistence work. Safety and recoverability take
precedence over preserving an advertised execute path. Keep execute behavior
fail-closed until every required snapshot, restore, rollback, and restart gate
in this directive passes.

## Source Authority and Precedence

Apply these sources in order:

1. Active system, developer, and user instructions
2. [Repository engineering policy](../../../reference/policies/repository-engineering-policy.md)
3. Active repository `AGENTS.md` instructions
4. [Reorganization Remediation Plan 1](../reorg-remediation-plan-1.md)
5. This construction directive
6. [Friday Chat V2 behavioral contracts](../friday-chat-v2-aechive/friday-chat-v2-behavioral-contracts.md)
7. Current public package contracts and source code
8. Current package-local and integration tests

The controlling plan contains resolved product and safety decisions. Do not
reopen or reinterpret them during implementation. If this directive conflicts
with the plan or repository policy, stop and report the conflict before editing
source.

The construction-directive guidance references
`docs/methodology/constitution/gendev.md`; that file was not present when this
directive was created. If it appears before or during implementation, read it
and stop if reconciliation would materially change scope or architecture.

## Input Coverage and Traceability

No separate current PRD, architecture specification, governance specification,
tactical plan, migration analysis, or UAT plan exists specifically for this
remediation. The controlling plan is the accepted combined authority for those
concerns. Do not infer missing requirements from unrelated planning documents.

The archived [Memory Reorganization Utility Plan](../../../archive/build-plans/completed/friday-core-legacy/memory-reorganization-utility.md)
is historical evidence only. It is not implementation authority. In particular,
its transcript-analysis behavior, optional backup bypass, single-root layout,
file-copy backup assumptions, and on-demand-only automation decisions are
superseded by the controlling plan.

| Controlling-plan scope | Directive workstreams | Hard gate | Required evidence |
|---|---|---|---|
| WP0 containment and baseline | `REORG-00` | Gate A | parser, configuration, framework CLI, and synthetic reproduction tests |
| WP1 store-owned contracts | `REORG-01`–`REORG-03` | Gate B | snapshot, corruption, restore, and integrity tests |
| WP2 coordinator | `REORG-04` | Gate C | quiescence, gate, lease, and shutdown tests |
| WP3 dispatch | `REORG-06` | Gate D | complete mode-matrix and provider-preflight tests |
| WP4 recovery | `REORG-05` | Gate C | rollback, rollback-failure, restart, and recovery tests |
| WP5 results and progress | `REORG-07` | Gate D | typed-result, privacy, progress, and PTY tests |
| WP6–WP7 tests and close-out | `REORG-08` | Gate D | package gates, integration drill, docs, and final report |

## Implementation Objective

Deliver one typed, coordinated reorganization capability with these outcomes:

- manual and exit reorganization share a Friday Chat coordinator;
- manual commands are dry-run unless exact `--execute` is supplied;
- exit reorganization remains configurable and defaults to disabled;
- every mutation is preceded by a complete verified recovery bundle;
- Friday Memory owns graph/vector/access-buffer snapshot and restore behavior;
- Friday Transcript owns WAL-safe transcript snapshot and restore behavior;
- transcript content is recovery-only and is never reorganized;
- conflicting maintenance and cross-process execution are excluded;
- post-mutation failure automatically rolls back;
- failed rollback leaves a durable actionable journal and blocks ordinary
  mutation;
- reports and CLI output reflect real typed outcomes and safe progress;
- no test or smoke operation mutates active user `.friday` state.

## Provider Testing Boundary

The primary Friday Chat LLM, including any DGX-hosted provider used by an
operator, is an established deployment dependency and is not a subject of this
remediation. No gate depends on reaching a DGX endpoint or completing a live
chat-model inference. `packages/friday-chat/config.example.yaml` remains the
configuration contract and default surface; required tests must not contact
the external endpoints named in that file.

This boundary does not remove maintenance-provider safety requirements. Each
reorganization mode must declare the maintenance LLM and embedding capabilities
it actually needs. Before an execute request mutates state, the production
coordinator must fail closed when a capability required by that selected mode
is missing, misconfigured, or unavailable. Modes and flags that skip a provider
dependent step must not require that unused provider.

Test provider selection, capability preflight, success, timeout, and failure
with deterministic adapters or test doubles. Dispatch tests for synthesis,
verification, and embedding-dependent work must exercise the real coordinator
and store-participant contracts while substituting only the external provider
transport. A live provider smoke test is optional evidence, must use operator
supplied configuration without changing it, and cannot replace any required
provider-free test or gate criterion.

## Authorized Scope

Edit only files required for the controlling plan in these locations:

- `packages/friday-chat/src/friday_chat/`
- `packages/friday-chat/tests_chat/`
- `packages/friday-chat/config.example.yaml`
- packaged Friday Chat configuration templates
- `packages/friday-memory/src/friday_memory/maintenance/`
- `packages/friday-memory/src/friday_memory/adapters/graph.py`
- `packages/friday-memory/src/friday_memory/adapters/vector.py`
- `packages/friday-memory/src/friday_memory/adapters/__init__.py`
- `packages/friday-memory/src/friday_memory/__init__.py`
- `packages/friday-memory/tests_memory/`
- `packages/friday-transcript/src/friday_transcript/stores/sqlite.py`
- `packages/friday-transcript/src/friday_transcript/stores/protocol.py`
- `packages/friday-transcript/src/friday_transcript/stores/__init__.py`
- `packages/friday-transcript/src/friday_transcript/models/` only for a typed
  snapshot manifest/result and its export
- `packages/friday-transcript/src/friday_transcript/__init__.py`
- `packages/friday-transcript/tests/`
- `tests/integration/reorganization/`
- [Friday Chat V2 behavioral contracts](../friday-chat-v2-aechive/friday-chat-v2-behavioral-contracts.md)
- [Friday Chat V2 framework upgrade log](../friday-chat-v2-aechive/friday-chat-v2-framework-upgrade-log.md)
- the controlling plan and this directive only for accurate implementation
  close-out notes

Minimal workspace metadata may change only if required to register a test or
public export. If implementation requires another source package, a transcript
schema change, or broader adapter redesign, stop and request authority.

## Explicit Non-Goals

- Do not reorganize, classify, prune, synthesize, verify, migrate, or otherwise
  alter transcript content.
- Do not move, delete, normalize, or silently migrate existing `.friday` state.
- Do not delete or rewrite existing backups or nested reorganization logs.
- Do not perform Chroma collection-format migration or wholesale collection
  rebuild.
- Do not change model, embedding, provider, retry, timeout, or credential
  configuration.
- Do not make live DGX, primary chat-model, or external maintenance-provider
  inference a required test or gate dependency.
- Do not change unrelated lifecycle, retrieval, compaction, extraction, graph,
  or transcript semantics.
- Do not add a backup-bypass option.
- Do not accept plain `/reorganize execute` as an alias.
- Do not add dependencies unless the current stack cannot satisfy an approved
  safety invariant; stop before adding one.
- Do not weaken typing, runtime checks, security, logging, or test coverage to
  make an implementation pass.
- Do not clean caches, `.friday/`, Chroma state, transcript state, or unrelated
  dirty files.
- Do not commit, push, merge, publish, or create a pull request unless the user
  separately authorizes that action.

## Anti-Drift Requirements

- Do not implement deferred or adjacent memory-maintenance features.
- Do not broaden package, file, command, platform, migration, or deployment
  scope without explicit authority.
- Do not silently change the coordinator, participant, recovery, or package
  ownership architecture.
- Do not weaken security, recovery, typing, logging, or governance behavior.
- Do not remove or rewrite unrelated code, tests, documentation, or generated
  state.
- Do not describe planned behavior as implemented, enabled, or validated before
  its gate evidence exists.
- Report every skipped or failed verification command honestly.
- If a compatibility requirement conflicts with a safety invariant, preserve
  the safety invariant and stop for direction.

## Mandatory Execution Order and Gates

Implement the workstreams in order. A later workstream may introduce types or
tests early when needed for compilation, but behavior may not cross a hard gate
until its prerequisites pass.

For each gate, issue a `PASS`, `FAIL`, or `BLOCKED` disposition with evidence
for every criterion. Gates A through C may proceed after a documented `PASS` if
no stop condition is active. Gate D requires explicit maintainer approval before
the capability guard is removed or any execute path is made available.

### Gate A: Baseline and containment

Required before implementing mutating behavior:

- branch and baseline ancestor are verified;
- `9d4eac0` is verified as an ancestor of the implementation branch; directive
  and other approved planning-only commits may exist above it;
- unrelated worktree changes are identified and preserved;
- currently supported platforms and filesystem semantics are inventoried;
- focused package baselines are recorded;
- synthetic split-layout fixtures reproduce the diagnosed failures;
- both manual and exit execute paths fail closed;
- example and packaged configuration default exit reorganization to disabled;
- strict parsing rejects plain `execute`, `--no-backup`, unknown tokens, and
  incompatible mode flags.

### Gate B: Store recovery capability

Required before Friday Chat may create an execute request:

- Friday Memory creates and verifies a consistent graph/vector/access-buffer
  snapshot;
- Friday Memory restores that snapshot and verifies live state;
- Friday Transcript creates a WAL-safe online snapshot;
- Friday Transcript restores only while quiesced and passes post-restore SQLite
  integrity checks;
- aggregate manifests distinguish present, configured-but-absent, unsupported,
  incomplete, and corrupt participants;
- recovery destinations cannot alias, overlap, or recursively contain sources;
- package-local snapshot, corruption, and restore tests pass.

### Gate C: Coordinated mutation and rollback

Required before any execute path is enabled:

- the Friday Chat maintenance gate blocks conflicting in-process writers;
- a layout-scoped inter-process lease blocks a second process;
- manual and shutdown quiescence sequences are implemented and tested;
- a versioned bundle and journal are durable before mutation;
- every mutating safe boundary has fault-injection coverage;
- failure and cancellation after mutation trigger verified rollback;
- failed rollback produces `recovery_required` and an unfinished journal;
- restart detection and explicit recovery complete successfully in disposable
  integration tests.

### Gate D: User-facing enablement

Required before removing containment:

- every advertised mode dispatches correctly;
- maintenance capabilities required by each selected mode are preflighted
  before mutation, unused providers are not required, and provider readiness
  behavior is proven without a live DGX dependency;
- typed result states cannot represent contradictory success/failure outcomes;
- immediate acknowledgement and bounded progress work in a provider-free PTY;
- CLI help and behavioral documentation describe exact syntax and recovery;
- the full execute, deliberate-failure, rollback, restart, and recovery drill
  passes against disposable stores;
- all required validation commands have been run and reported.

Do not enable automatic exit reorganization by default after Gate D. The
feature remains configurable, with the default set to disabled.

## Required Workstreams

### `REORG-00`: Baseline and fail-closed containment

1. Verify `feature/reorg-remediation-1` and confirm `9d4eac0` is an ancestor. If
   the branch history has unrelated drift, inspect the delta before continuing.
2. Record focused test baselines for Friday Chat, Friday Memory, and Friday
   Transcript.
3. Construct disposable synthetic fixtures for:
   - split graph/vector/transcript paths;
   - multiple configured Chroma collections and index state;
   - transcript SQLite WAL state;
   - optional access-buffer WAL state;
   - external recovery and log directories.
4. Reproduce wrong-root, incomplete-backup, fake-only reporting, mode-dispatch,
   and shutdown-concurrency failures without reading repository `.friday` data.
5. Inventory every public maintenance entry point, including
   `python -m friday_memory.maintenance`.
6. Fail closed for the standalone Friday Memory `restore` command and for every
   `--no-dry-run` prune, synthesize, verify, or reorganize path. Reject its
   `--no-backup` path. Read-only list, analyze, and dry-run behavior may remain;
   memory-only backup output must be labeled as not being a complete Friday
   Chat recovery bundle.
7. Add strict Friday Chat parsing and actionable usage errors.
8. Add a runtime capability guard derived from participant preflight—not a
   hidden build or test flag—that prevents manual and automatic mutation until
   Gate B and Gate C capabilities are available.
9. Set `session.reorganize_on_exit: false` in user-facing example and packaged
   template configuration while preserving the configurable field.

### `REORG-01`: Typed cross-package contracts

1. Define closed enums and typed models for:
   - operation trigger and mode;
   - store discovery and capability state;
   - snapshot, restore, and integrity results;
   - progress steps;
   - result status and typed errors;
   - recovery bundle and journal schema.
2. Use Pydantic models for persisted or externally validated records and typed
   dataclasses/protocols for simple in-process contracts where appropriate.
3. Add schema versions to persisted manifests and journals.
4. Keep `ReorganizationRequest` and `RecoveryRequest` distinct.
5. Use one result-status enum containing at least `dry_run_complete`,
   `completed`, `completed_with_warnings`, `preflight_failed`,
   `failed_rolled_back`, `cancelled`, and `recovery_required`.
6. Do not add `dict[str, Any]` as a cross-package or persisted contract.
7. Preserve compatibility through explicit adapters where required; do not
   preserve compatibility through path guessing.

### `REORG-02`: Friday Memory explicit layout and recovery participant

1. Add a public typed layout with explicit vector directory, graph path,
   optional access-buffer WAL path, recovery directory, and log directory.
2. Update only affected maintenance components to consume explicit paths.
3. Keep Friday Memory independent of Friday Chat and Friday Transcript.
4. Inventory every file and store component required to recover all configured
   Chroma collections, database state, index state, graph state, and enabled
   access-buffer WAL state.
5. Select and document a supported Chroma snapshot/restore strategy before
   implementing it. Unsynchronized recursive copying is not acceptable.
6. Add create, verify, restore, and live-integrity operations.
7. Make restore fail closed on schema, layout, checksum, collection, or index
   incompatibility.
8. Keep recovery and log destinations outside source stores and reject symlink
   or path-alias bypasses.
9. Correct reorganization log path handling without moving old logs.

### `REORG-03`: Friday Transcript WAL-safe recovery participant

1. Add a narrow public snapshot protocol and typed manifest/result.
2. Use an SQLite online-backup or verified checkpoint mechanism valid for WAL
   mode.
3. Verify the snapshot with SQLite integrity and schema-compatibility checks.
4. Restore only under the coordinator's quiesced-write contract.
5. Verify the live database after restore.
6. Keep transcript content, schema, retention, append semantics, and query
   behavior unchanged.
7. Do not expose private SQLite implementation details to Friday Chat.

### `REORG-04`: Friday Chat coordinator and maintenance exclusion

1. Replace divergent manual `reorganize()` and shutdown
   `reorganize_memory()` behavior with one typed coordinator.
2. Add an in-process maintenance gate covering every conflicting maintenance
   and recovery operation.
3. Add a layout-scoped inter-process lease containing run ID, process/host
   metadata, and journal linkage.
4. Never silently steal a stale lease. Reconcile it with the associated journal
   and expose recovery guidance.
5. Block new background writers before snapshot or restore.
6. Drain or safely cancel extraction, tool decay, graph maintenance,
   compaction, lifecycle, and transcript writes.
7. For shutdown, finalize the transcript before its recovery snapshot.
8. For manual operation, use the online transcript snapshot without finalizing
   the active session.
9. Resolve configured paths once from one documented base and pass explicit
   normalized paths to participants. Preserve the current process-working-
   directory base for relative paths; changing that behavior requires separate
   migration authority.
10. Preflight layout, store integrity, participant capability, providers,
    permissions, capacity, path overlap, symlinks, leases, and unfinished
    journals.
11. Inventory the repository's supported platforms before selecting lease and
    durability mechanisms. Unverified platforms must fail closed rather than
    silently using weaker coordination.
12. Release active locks on terminal paths. Use the durable unfinished journal,
    not an orphaned lock, to block ordinary mutation after recovery failure.

### `REORG-05`: Recovery bundle, journal, rollback, and restart recovery

1. Create an aggregate versioned recovery manifest with run ID, layout
   fingerprint, application version, participant manifests, checksums,
   verification results, and a completion marker.
2. Write the journal before snapshot creation and update it atomically at every
   safe boundary.
3. Do not mutate until the aggregate bundle is complete and verified.
4. On a post-mutation exception, substep failure, or cancellation, attempt
   automatic rollback.
5. Verify every participant after rollback before returning
   `failed_rolled_back`.
6. If rollback cannot complete or verify, preserve the bundle and journal,
   return `recovery_required`, and block ordinary mutation.
7. Detect unfinished journals during startup and before every mutation.
8. Implement:

   ```text
   /reorganize --recover <run-id>
   /reorganize --recover <run-id> --execute
   ```

   The first form validates and reports only. The second resumes restoration
   from the recorded verified bundle. It must not replace the recovery source
   with a new backup of partially mutated state.
9. Use owner-only recovery directories and files on POSIX (`0700` directories,
   `0600` files) and the closest enforceable owner-only equivalent on other
   verified platforms. Test the effective permissions.
10. Do not automatically delete bundles, journals, or failed-run evidence in
    this remediation. Retention automation is deferred and requires separate
    authority.

### `REORG-06`: Mode dispatch and pipeline correctness

1. Implement and test the controlling plan's mode capability matrix.
2. Route `full`, `backup`, `analyze`, `dedupe`, `prune`, `synthesize`, and
   `verify` to the intended operation.
3. Keep the standalone Friday Memory CLI mutation and restore paths fail-closed;
   they cannot assemble Friday Chat's transcript-inclusive recovery bundle and
   must not bypass the coordinator.
4. Reject `--execute` for analyze-only mode and reject incompatible full-only
   flags for single-step modes.
5. Keep transcripts outside all analysis and mutation dispatch.
6. Require a verified recovery bundle for each graph/vector mutation.
7. Define required maintenance LLM and embedding capabilities per mode and
   flag combination. Preflight only those capabilities before mutation, fail
   closed when any required capability is unavailable, and do not treat the
   primary Friday Chat LLM or DGX as an implicit maintenance provider.
8. Preserve every substep error and warning.
9. Do not mark the run successful merely because a coroutine returned.
10. Verify graph/vector postconditions before completion.
11. Honor cancellation only at safe boundaries; shield atomic snapshot,
    journal, mutation-commit, and rollback sections.

### `REORG-07`: Honest results, progress, and privacy

1. Aggregate counts from actual typed subreport fields.
2. Represent unavailable metrics explicitly rather than as zero.
3. Return attempted, completed, and skipped steps plus per-store results.
4. Return real recovery manifest, journal, and reorganization log paths.
5. Add a framework-neutral progress callback; do not pass Rich objects into
   Friday Memory or Friday Transcript.
6. Wire command execution so acknowledgement appears before long-running work
   completes.
7. Emit bounded events for quiescence, preflight, snapshot, verification,
   mutation steps, rollback, recovery, and final state.
8. During a shielded atomic section, report cancellation as pending and stop at
   the next safe boundary.
9. Remove progress/heartbeat state on every terminal path.
10. Keep terminal output, diagnostics, and normal reorganization logs free of
    memory content, transcript content, credentials, prompts, and raw provider
    responses.

### `REORG-08`: Tests, documentation, and close-out

1. Implement every test category in the controlling plan, including negative
   and fault-injection cases.
2. Exercise the production participant and coordinator contracts, not only fake
   services.
3. Test two processes contending for the same layout lease.
4. Test every standalone Friday Memory CLI mutation and restore bypass.
5. Inject failure after every mutating safe boundary.
6. Prove rollback, rollback failure, restart detection, and explicit recovery.
7. Prove dry-run side-effect behavior and idempotence where promised.
8. Prove provider preflight and provider-dependent dispatch with deterministic
   external-provider adapters; no required test may contact DGX or another live
   inference endpoint.
9. Update `/help reorganize`, example configuration, behavioral contracts, and
   framework upgrade log.
10. Label existing vector-only backups as incomplete recovery artifacts in
   documentation without changing those artifacts.
11. Record the scoped FridayV2 freeze exception, affected contracts, validation
   evidence, and cleanup point.
12. Do not declare completion until Gate D and all acceptance criteria in the
    controlling plan pass.

## Migration and Compatibility Instructions

- Preserve current on-disk paths and data. This remediation adds explicit
  layout contracts; it does not relocate user stores.
- Preserve legacy single-root callers through an explicit compatibility adapter
  only when doing so is safe and testable.
- Do not reinterpret a legacy vector-only manifest as a complete recovery
  bundle.
- Do not mutate old manifests or logs to make them appear compatible.
- Reject unsupported layouts with typed, actionable preflight results.
- Manual command execution is never inherited from
  `maintenance.defaults.dry_run`.
- Plain `execute` and `--no-backup` are rejected rather than deprecated into
  destructive behavior.
- Existing standalone Friday Memory mutation and restore syntax is retained only
  as actionable fail-closed output; it is not a recovery-policy bypass.
- Existing configurations may keep `reorganize_on_exit`; example/template
  defaults become false, and enabled configurations use the same coordinator
  and mandatory recovery behavior as manual execution.

## Security and Governance Requirements

- Treat configured paths, manifest fields, journal fields, stored metadata,
  provider errors, and persisted content as untrusted input.
- Validate path containment using normalized resolved paths while accounting for
  non-existent destinations and symlink traversal.
- Reject recovery destinations that overlap a source by alias, symlink, parent,
  child, or equivalent resolved identity.
- Create recovery and content-bearing diagnostic artifacts with restrictive
  permissions; enforce and test owner-only access rather than relying on
  permissive process defaults.
- Never log memory or transcript content in terminal progress, exceptions,
  diagnostics, or tests.
- Sanitize provider errors and never emit API keys, headers, environment values,
  prompts, or raw responses.
- Use explicit exceptions for external input, persistence, lifecycle, and
  destructive invariants.
- Do not rely on `assert` for essential runtime enforcement.
- Do not add `# mypy: ignore-errors` under `packages/*/src`.
- Do not broaden existing suppressions or weaken mypy configuration.
- Prefer public typed models and protocols over private implementation access,
  repeated `cast(...)`, or incidental attributes.
- Keep Friday Memory and Friday Transcript independent; Friday Chat owns
  composition.

## Testing Requirements

At minimum, cover:

- strict parser and mode matrix behavior;
- fail-closed standalone Friday Memory mutation and restore commands;
- default-disabled but configurable exit reorganization;
- unified manual and exit coordinator dispatch;
- split and legacy memory layouts;
- Chroma multi-collection snapshot, verification, corruption, and restore;
- graph snapshot, corruption, and restore;
- transcript WAL snapshot, integrity, schema mismatch, and restore;
- enabled access-buffer WAL handling;
- missing, absent-by-configuration, unsupported, and corrupt participants;
- permission denial, insufficient capacity, symlink, alias, and recursive paths;
- mode-specific maintenance-provider capability success, omission when unused,
  missing configuration, timeout, and failure before mutation;
- proof that primary chat-provider and DGX availability are not prerequisites
  for provider-free reorganization modes or mandatory test execution;
- snapshot failure before mutation;
- conflicting in-process work;
- inter-process lease contention and stale-lease reconciliation;
- cancellation before mutation, between safe boundaries, and during a shielded
  section;
- fault injection after every mutating safe boundary;
- verified automatic rollback;
- rollback failure and `recovery_required` behavior;
- startup detection of unfinished journals;
- recovery inspection and explicit recovery execution;
- typed aggregation of success, warning, failure, unavailable, and no-change
  outcomes;
- immediate acknowledgement and bounded PTY progress;
- disposable full execute, deliberate failure, rollback, restart, and recovery;
- preservation of active user state by construction.

Use synthetic IDs and synthetic memory/transcript content. Never use repository
`.friday` state as a fixture. Replace only external LLM and embedding transport
with deterministic adapters where a mode requires those capabilities; continue
to exercise the production coordinator and persistence participants.

## Verification Commands

Create or extend these focused test modules so the directive has stable
verification targets:

- `packages/friday-chat/tests_chat/test_maintenance_commands.py`
- `packages/friday-chat/tests_chat/test_reorganization_coordinator.py`
- `packages/friday-chat/tests_chat/test_reorganization_terminal.py`
- `packages/friday-memory/tests_memory/test_maintenance/test_recovery_participant.py`
- `packages/friday-memory/tests_memory/test_maintenance/test_framework_cli_safety.py`
- `packages/friday-transcript/tests/test_sqlite_snapshot.py`
- `tests/integration/reorganization/test_reorganization_recovery.py`

Run focused tests first:

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest \
  packages/friday-chat/tests_chat/test_maintenance_commands.py \
  packages/friday-chat/tests_chat/test_reorganization_coordinator.py \
  packages/friday-chat/tests_chat/test_reorganization_terminal.py -q
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest \
  packages/friday-memory/tests_memory/test_maintenance/test_recovery_participant.py \
  packages/friday-memory/tests_memory/test_maintenance/test_framework_cli_safety.py -q
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest \
  packages/friday-transcript/tests/test_sqlite_snapshot.py -q
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest \
  tests/integration/reorganization/test_reorganization_recovery.py -q
```

Then run the affected package gates:

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest packages/friday-chat -q
PATH="$PWD/.venv/bin:$PATH" .venv/bin/ruff check packages/friday-chat
PATH="$PWD/.venv/bin:$PATH" .venv/bin/mypy packages/friday-chat

PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest packages/friday-memory/tests_memory -q
PATH="$PWD/.venv/bin:$PATH" .venv/bin/ruff check packages/friday-memory
PATH="$PWD/.venv/bin:$PATH" .venv/bin/mypy \
  packages/friday-memory/src/friday_memory/maintenance \
  packages/friday-memory/src/friday_memory/adapters/graph.py \
  packages/friday-memory/src/friday_memory/adapters/vector.py

PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest packages/friday-transcript/tests -q
PATH="$PWD/.venv/bin:$PATH" .venv/bin/ruff check packages/friday-transcript
PATH="$PWD/.venv/bin:$PATH" .venv/bin/mypy \
  packages/friday-transcript/src/friday_transcript/stores \
  packages/friday-transcript/src/friday_transcript/models
```

Do not hide legacy debt with broad ignores. If an exact mypy command exposes
pre-existing debt, preserve its output and run the narrowest changed-file gate
as supplemental evidence; do not silently replace the required command.

When cross-package contracts are integrated, also run:

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/python -c "from friday_runtime import RuntimeKernel; from friday_agent import InteractiveAgent; print('Friday imports OK')"
```

Run the cross-package disposable recovery drill, deterministic
maintenance-provider preflight cases, and provider-free PTY tests through the
exact focused modules above. Do not require or contact the primary chat LLM,
DGX, or external endpoints from `config.example.yaml`. Then run the root gate
and whitespace check:

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest
git diff --check
```

If the root gate fails from unrelated legacy debt, report the exact failure and
the narrower passing evidence. Do not omit the root attempt.

## CLI, API, and UAT Requirements

CLI requirements:

- `/reorganize` is dry-run by default;
- exact `--execute` is required for mutation;
- plain `execute`, `--no-backup`, unknown tokens, and incompatible flags show
  actionable usage;
- analyze-only mode rejects meaningless execute authorization;
- recovery inspection and execution use the exact syntax in `REORG-05`;
- standalone Friday Memory mutation and restore commands fail closed with
  migration guidance rather than bypassing the aggregate coordinator;
- start state, progress, final status, warnings, errors, and recovery paths are
  visible without exposing persisted content.

API requirements:

- contracts are exported from stable public modules;
- Friday Chat does not access private Friday Memory or Friday Transcript
  attributes;
- Friday Memory and Friday Transcript do not import each other;
- persisted manifests and journals are schema-versioned and validated;
- the coordinator exposes one typed path for manual and exit requests.

UAT requirements:

- use newly constructed disposable storage or snapshots produced through the
  new quiesced participant contracts;
- never copy a running `.friday` directory as UAT input;
- prove dry-run, full execute, injected post-mutation failure, verified rollback,
  process restart, and explicit recovery;
- use deterministic maintenance-provider adapters for provider-dependent modes;
  a running primary chat client or live DGX call is not required;
- if an optional live-provider smoke is run, report it separately and do not
  treat it as a substitute for the disposable provider-free drill;
- do not run execute-mode UAT against active user state.

## Documentation Close-Out

Update:

- `/help reorganize` usage and argument descriptions;
- Friday Chat behavioral contracts;
- example and packaged configuration defaults;
- the FridayV2 framework upgrade log;
- recovery bundle, journal, rollback, retention, permissions, and operator
  recovery documentation;
- standalone Friday Memory CLI containment and its future migration path;
- the controlling plan only when implementation evidence requires accurate
  status or discovery-gate close-out.

Documentation must distinguish planned, implemented, enabled, and validated
behavior. Do not describe execute mode as available until Gate D passes.

## Reporting Requirements

At each gate and final close-out, report:

- workstream IDs completed;
- files changed, grouped by package;
- public contract additions or compatibility changes;
- Chroma snapshot/restore strategy and evidence;
- SQLite WAL snapshot/restore strategy and evidence;
- maintenance gate and inter-process lease behavior;
- recovery journal states and durability approach;
- fault-injection points exercised;
- rollback and restart-recovery evidence;
- CLI and progress behavior;
- mode-specific maintenance-provider preflight evidence and whether any
  optional live-provider smoke was run;
- documentation updated;
- exact verification commands and results;
- skipped verification and why;
- unrelated baseline failures;
- remaining stop conditions or risks;
- gate disposition and criterion-by-criterion evidence;
- confirmation that active `.friday` state was untouched.

Do not report a failed-and-rolled-back run as ordinary success. Distinguish
`failed_rolled_back` from `recovery_required` explicitly.

## Stop Conditions

Stop and ask for direction if:

- a safe Chroma snapshot/restore strategy cannot be proven;
- snapshot consistency would require copying live files without a supported
  quiescence or store-owned mechanism;
- the implementation requires transcript content or schema changes;
- another source package must change outside authorized scope;
- Friday Memory would need to import Friday Transcript or vice versa;
- an essential contract would require an untyped dictionary or private
  cross-package access;
- atomic journal or manifest durability cannot be provided on supported
  platforms;
- the supported platform set cannot be established from current package and
  deployment authority;
- the inter-process lease cannot distinguish active work from recoverable stale
  state safely;
- rollback cannot be verified after a mutating step;
- a test or smoke procedure would require active user `.friday` state;
- provider configuration changes appear necessary;
- implementing a mode would require unplanned collection migration or broad
  maintenance refactoring;
- repository policy would require a waiver;
- unrelated worktree changes overlap required files and cannot be preserved;
- implementation would change the current process-working-directory base for
  relative configuration paths;
- a required validation failure indicates new behavior is unsafe rather than
  unrelated baseline debt.

When stopped, leave execute mode fail-closed, preserve recovery artifacts and
unrelated state, and report the smallest decision or authority needed to
continue.
