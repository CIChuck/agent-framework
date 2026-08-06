# Reorganization Remediation Plan 1

## Status

Revised on 2026-08-06 after a second safety review. Diagnosis is complete;
implementation has not started.

The current manual and automatic execute paths must be treated as unsafe until
the storage-layout, snapshot-consistency, concurrency, and recovery defects in
this plan are resolved. Do not run either path against normal `.friday` state
during remediation development.

The project maintainer has authorized a narrow FridayV2 freeze exception for
the minimum required changes in `packages/friday-memory` and
`packages/friday-transcript`. This authorization does not permit unrelated
framework refactoring, transcript-content changes, schema migrations, broad
typing suppressions, or edits to other frozen packages.

## Resolved Product and Safety Decisions

These decisions are no longer open:

1. Automatic exit reorganization remains supported and configurable.
2. Automatic exit reorganization defaults to disabled. Enabling it is an
   explicit configuration decision.
3. Manual reorganization remains dry-run by default regardless of
   `maintenance.defaults.dry_run`.
4. Only the exact `--execute` flag authorizes a mutating command. Plain
   `/reorganize execute` is rejected with corrective usage.
5. Execute mode always requires a complete verified recovery bundle.
   `--no-backup` is removed.
6. Transcripts are recovery-only assets. Reorganization may analyze or mutate
   graph/vector memory, but it must not reorganize transcript content.
7. Failures after mutation trigger automatic rollback. A durable recovery
   journal is the fallback when rollback cannot complete.
8. Execute-mode and rollback tests use synthetic disposable stores only. No
   test or smoke operation may mutate the user's active `.friday` state.

## Problem Statement

The `/reorganize` command is registered and reaches the real
`FrameworkMaintenanceAdapter`; it is not wholly unwired. The production bridge
and the independent shutdown bridge are nevertheless unsafe and functionally
broken:

1. Only the exact `--execute` token currently disables dry-run mode, while
   unknown positional tokens are silently ignored.
2. Friday Chat passes `memory.persist_directory` (`.friday/vector` in the
   example configuration) to `MemoryReorganizer` as if it were the aggregate
   memory root.
3. Friday Memory maintenance infers graph and transcript paths relative to that
   single root, while Friday Chat stores live data at `.friday/graph.json`,
   `.friday/vector/`, and `.friday/exports/friday_transcripts.sqlite`.
4. Current execute-mode backups therefore omit graph and transcript state. The
   inspected manifest reported `graph.exists=false`, `episodic.exists=false`,
   and backed up only `chroma.sqlite3`.
5. Copying individually selected live files is not a consistent snapshot of
   SQLite WAL databases, Chroma database/index state, and graph state.
6. Relative reorganization logging is re-parented beneath the vector directory,
   producing `.friday/vector/.friday/reorganization_logs`.
7. The real adapter reads nonexistent `total_items_scanned` and
   `total_items_changed` fields, so the command always reports zero.
8. Framework substep and terminal errors are returned in reports, but command
   output ignores them and can render partial mutation as success.
9. Single-step mode flags are parsed and echoed but never dispatched. The real
   adapter always invokes the full pipeline.
10. Friday Chat has a separate `reorganize_memory()` shutdown path that always
    requests a real full reorganization and does not share manual-command
    parsing, preflight, results, or recovery handling.
11. Shutdown reorganization currently runs before transcript finalization and
    before supervised background work is closed. Manual execution can likewise
    overlap extraction, lifecycle, graph maintenance, tool decay, or compaction.
12. The full pipeline mutates in multiple steps without a transaction or
    durable recovery state. Cancellation or a late failure can leave stores
    partially changed.
13. The CLI provides no immediate acknowledgement, bounded progress, completed
    step list, warning summary, or recovery artifact path.
14. Existing command and shutdown tests primarily use fake maintenance services;
    they do not prove real adapter dispatch, consistent snapshots, rollback, or
    restart recovery.

## Evidence Baseline

Preserve these diagnosis facts as synthetic regression fixtures or assertions:

- `/reorganize execute` currently reports `Dry run: True` instead of rejecting
  the unsupported positional token.
- `/reorganize --execute` currently reaches execute mode.
- The example configuration resolves vector, graph, and transcript persistence
  to three distinct paths.
- `ReorganizationReport` exposes typed subreports, `success`, and `errors`; it
  does not expose aggregate `total_items_scanned` or
  `total_items_changed` fields.
- Friday Transcript uses SQLite WAL mode.
- Friday Memory's current backup implementation copies files individually.
- The app performs exit reorganization before transcript finalization and
  background-task shutdown.
- Manual and automatic reorganization use separate maintenance methods.
- The focused fake-service suite can pass while all production defects remain.

Do not read real memory or transcript content into diagnostics or test output.
Fixtures must contain synthetic data, and output assertions must use store
categories, paths, counts, statuses, synthetic IDs, and sanitized errors.

## Safety Invariants

1. Fail closed before mutation when layout, snapshot, provider, capacity,
   permissions, integrity, or recovery preflight fails.
2. One exclusive maintenance gate and layout-scoped inter-process lease must
   cover manual reorganization, automatic exit reorganization, lifecycle,
   extraction flush, graph maintenance, compaction, migration, reset, snapshot,
   and restore operations that can conflict.
3. Stop new writers and drain or safely cancel in-flight writers before
   snapshotting or mutating stores.
4. A backup is complete only when every configured persistent participant is
   captured or explicitly recorded as configured-but-absent.
5. A checksum-valid collection of copied files is not sufficient evidence of a
   consistent snapshot.
6. Do not begin mutation until the recovery bundle is atomically marked
   complete and passes store-specific verification.
7. Do not infer paths that the owning runtime or store already knows.
8. Do not use symlinks, copied live-layout mirrors, or path tricks to imitate a
   missing cross-package contract.
9. Never use `assert` as the sole enforcement of a persistence or destructive
   runtime invariant.
10. Cancellation is honored only at safe boundaries. Atomic snapshot, commit,
    and rollback sections must be shielded from interruption.
11. A run with errors cannot return a success status. A rollback failure must
    return `recovery_required` and preserve its journal.
12. Existing backups, nested logs, graph/vector state, transcripts, and runtime
    data are preserved. This plan does not authorize cleanup or migration of
    existing user state.
13. Providers, credentials, memory content, and transcript content must not
    appear in terminal progress, diagnostics, or test logs.
14. Recovery artifacts and reorganization logs must use restrictive
    permissions and documented retention behavior.

## Target Architecture

Friday Chat is the sole orchestration owner. Friday Memory and Friday
Transcript expose narrow typed capabilities for the stores they own; neither
framework package imports the other.

```text
FridayChatMaintenanceCoordinator
  -> exclusive maintenance gate + inter-process lease
  -> FridayMemoryMaintenanceParticipant (graph + vector + access-buffer state)
  -> FridayTranscriptSnapshotParticipant (recovery only)
  -> RecoveryJournal
  -> progress/result adapter
```

The coordinator performs this execute sequence:

1. stop new conflicting work;
2. drain or safely cancel in-flight work;
3. flush pending extraction and access-buffer state;
4. finalize the transcript session when triggered during shutdown, or obtain a
   consistent online transcript snapshot during an active manual session;
5. run layout, integrity, provider, permissions, and capacity preflight;
6. create and verify a complete recovery bundle;
7. atomically record `snapshot_verified` in the recovery journal;
8. run the selected graph/vector operation;
9. verify postconditions;
10. mark the journal complete and release the maintenance gate; or
11. on failure, restore and verify the pre-run bundle; if restoration cannot be
    completed, retain the journal and return `recovery_required`.

Dry-run performs discovery, analysis, and capability preflight without
snapshot creation, store mutation, access-buffer flushing, or transcript
changes. It may create a sanitized operation log only when that side effect is
documented and tested.

## Target Contracts

### Command syntax

```text
/reorganize [--execute]
  [--backup|--dedupe|--analyze|--prune|--synthesize|--verify]
  [--skip-synthesis] [--skip-verify] [--skip-lifecycle]
  [--force-reembed]

/reorganize --recover <run-id> [--execute]
```

Parser rules:

- reject every unknown flag and positional token;
- reject plain `execute` with usage showing `--execute`;
- reject multiple mode flags;
- reject flags that are not valid for the selected mode;
- never consult `maintenance.defaults.dry_run` to authorize a manual mutation;
- display the trigger, mode, and dry-run/execute state before long-running work;
- do not expose a backup-bypass flag;
- reject `--recover` when combined with an ordinary reorganization mode; and
- require exact `--execute` before recovery may restore a prior bundle.

Without `--execute`, `--recover <run-id>` validates the named journal and bundle
and reports the recovery steps without changing live stores. With `--execute`,
it resumes the recorded rollback from that already verified bundle; it must not
create a new backup of partially mutated state and treat that as the recovery
source.

Mode semantics must be captured in one tested capability matrix:

| Mode | Dry-run behavior | Execute behavior | Recovery bundle |
|---|---|---|---|
| `full` | Analyze and report planned steps | Run selected full pipeline | Required |
| `backup` | Report stores and estimated snapshot scope | Create and verify bundle only | Operation result |
| `analyze` | Analyze only | `--execute` rejected as meaningless | Not created |
| `dedupe` | Report candidates | Deduplicate insights | Required |
| `prune` | Report candidates | Prune graph/vector memory | Required |
| `synthesize` | Report synthesis plan | Create synthesized memory | Required |
| `verify` | Report verification plan | Update verification metadata | Required |

### Friday Chat request

```text
ReorganizationRequest
  trigger: manual | exit
  mode
  dry_run
  skip_synthesis
  skip_verify
  skip_lifecycle
  force_reembed
```

`mode` and `trigger` are closed enums. `backup_first` is not caller-controlled;
the coordinator enforces recovery-bundle creation for every mutating request.
Recovery uses a distinct typed request containing the validated run ID rather
than overloading the ordinary mode fields.

### Friday Memory contract

Add a stable public typed contract, provisionally:

```text
MemoryMaintenanceLayout
  vector_directory
  graph_path
  access_buffer_wal_path
  backup_directory
  log_directory

MemoryMaintenanceParticipant
  preflight(layout)
  create_snapshot(destination)
  verify_snapshot(manifest)
  restore_snapshot(manifest)
  verify_live_state()
  run(request, progress_callback)
```

Friday Memory owns graph/vector and access-buffer consistency. Its maintenance
components consume explicit paths and must not reconstruct Friday Chat layout
from a single overloaded root. Snapshot and restore must use supported
store-specific mechanisms and cover all Chroma database, collection, index,
graph, and enabled WAL state needed for recovery.

### Friday Transcript contract

Add a stable public recovery-only contract, provisionally:

```text
TranscriptSnapshotParticipant
  create_snapshot(destination)
  verify_snapshot(manifest)
  restore_snapshot(manifest)
  verify_live_state()
```

For SQLite, snapshot creation must use an online-backup/checkpoint strategy that
is valid for WAL mode. Verification includes an SQLite integrity check and
schema compatibility check. Restore is permitted only while transcript writes
are quiesced. This work does not alter transcript content, schema, retention, or
normal query behavior.

### Recovery bundle and journal

Friday Chat owns a versioned aggregate manifest and journal:

```text
RecoveryBundleManifest
  schema_version
  run_id
  created_at
  layout_fingerprint
  application_version
  participants
  checksums
  verification_results
  complete

RecoveryJournal
  schema_version
  run_id
  trigger
  mode
  state
  current_safe_boundary
  bundle_manifest_path
  steps_completed
  rollback_state
  sanitized_errors
```

Manifest and journal updates use atomic replacement and appropriate durability
mechanisms. Valid journal states include `preflight`, `snapshotting`,
`snapshot_verified`, `mutating`, `verifying`, `rolling_back`, `completed`, and
`recovery_required`. Startup must detect unfinished journals before permitting
another mutating maintenance run.

### Typed result

Replace `dict[str, Any]` at the Friday Chat maintenance boundary with typed
records. Use one status enum rather than conflicting success booleans:

```text
ReorganizationResult
  schema_version
  run_id
  trigger
  mode
  dry_run
  status
  steps_attempted
  steps_completed
  steps_skipped
  store_results
  warnings
  errors
  recovery_bundle_manifest_path
  recovery_journal_path
  reorganization_log_path
```

Status values include `dry_run_complete`, `completed`,
`completed_with_warnings`, `preflight_failed`, `failed_rolled_back`,
`cancelled`, and `recovery_required`. Store results, step results, counts,
warnings, and errors are typed models. Missing metrics remain unavailable rather
than becoming implicit zeroes.

## Scope and Package Boundary

### Authorized implementation targets

- `packages/friday-chat/src/friday_chat/`
- `packages/friday-chat/tests_chat/`
- `packages/friday-memory/src/friday_memory/maintenance/`
- minimal Friday Memory public exports and adapter capabilities required for
  graph/vector snapshot, restore, and integrity verification
- `packages/friday-memory/tests_memory/`
- `packages/friday-transcript/src/friday_transcript/stores/sqlite.py`
- minimal Friday Transcript public exports required for the snapshot contract
- `packages/friday-transcript/tests/`
- FridayV2 planning and behavioral documentation
- minimal example/template configuration changes

### Boundary rules

- Friday Memory must not import Friday Chat or Friday Transcript.
- Friday Transcript must not import Friday Chat or Friday Memory.
- Friday Chat composes the public typed participants.
- No new `dict[str, Any]` persistence boundary is permitted.
- Existing source typing debt must not be expanded or hidden with new broad
  suppressions.
- Record the scoped freeze exception and its validation evidence in the
  FridayV2 framework upgrade log.

### Out of scope

- Deleting, relocating, or silently migrating existing `.friday` state
- Transcript analysis, transcript reorganization, or transcript schema changes
- Chroma collection-format migration or wholesale collection rebuild
- Changing model, embedding, provider, retry, or timeout configuration
- Broad maintenance refactoring unrelated to explicit layout, store snapshots,
  restore, dispatch, typed reports, safe progress, or recovery
- Publication/versioning work
- Editing other frozen framework packages

## Work Package 0: Contain Risk and Capture a Baseline

1. Record focused Friday Chat, Friday Memory, and Friday Transcript baselines.
2. Temporarily fail closed for both manual and automatic execute paths until
   every required participant advertises and passes snapshot/restore capability.
3. Set `session.reorganize_on_exit: false` in example and packaged template
   configuration while retaining the typed configurable option.
4. Reject plain `execute`, unknown tokens, incompatible modes, and any
   `--no-backup` token.
5. Build a synthetic split layout with graph, Chroma collections, transcript
   SQLite WAL state, optional access-buffer WAL state, external recovery root,
   and external log directory.
6. Reproduce the wrong-root, incomplete-backup, fake-only test, and shutdown
   concurrency defects using synthetic state only.
7. Record baseline failures without reading or changing repository `.friday`
   state.

## Work Package 1: Add Store-Owned Snapshot Contracts

### Friday Memory

1. Add the public typed memory layout and participant models.
2. Change maintenance construction to accept explicit graph/vector/WAL paths.
3. Replace inferred graph, vector, backup, and log paths throughout the affected
   analyzer, pruner, synthesizer, verifier, logger, and reorganizer paths.
4. Implement a consistent graph/vector snapshot using supported Chroma and graph
   persistence operations rather than unsynchronized file selection.
5. Implement snapshot verification, live-store verification, and restore.
6. Cover all configured Chroma collections and required index/database files.
7. Flush or capture enabled access-buffer WAL state deterministically.
8. Prevent recovery destinations from overlapping or recursively containing
   source stores.
9. Preserve legacy single-root compatibility only through an explicit adapter,
   not implicit guessing.

### Friday Transcript

1. Add a public typed SQLite snapshot manifest/result.
2. Implement WAL-safe online snapshot creation.
3. Implement snapshot and live-database integrity verification.
4. Implement quiesced restore with post-restore verification.
5. Keep transcript content, schema, normal persistence, and query behavior
   unchanged.
6. Do not expose private database internals to Friday Chat.

## Work Package 2: Build the Friday Chat Maintenance Coordinator

1. Replace separate manual `reorganize()` and automatic
   `reorganize_memory()` behavior with one coordinator request path.
2. Add an exclusive maintenance gate shared by every conflicting Friday Chat
   maintenance entry point.
3. Add a layout-scoped inter-process lease with run ID, process/host metadata,
   and journal linkage. Never silently steal an apparently stale lease; reconcile
   it with the recovery journal first.
4. Stop scheduling new background writers while the gate is held.
5. Drain or safely cancel extraction, tool decay, graph maintenance, compaction,
   lifecycle, and transcript writes before snapshot or restore.
6. Define distinct manual-session and shutdown quiescence sequences.
7. During shutdown, finalize the transcript before its recovery snapshot.
8. Resolve relative paths from one documented configuration base and pass
   normalized explicit paths to participants.
9. Preflight presence, integrity, provider availability, permissions, disk
   capacity, path overlap, symlink behavior, layout support, and unfinished
   recovery journals.
10. Create and verify the aggregate recovery bundle before mutation.
11. Implement automatic rollback and post-rollback verification.
12. Retain an actionable journal and block new mutation if rollback fails.
13. Release active in-process and inter-process locks on every terminal path so
    read-only diagnostics and explicit recovery remain available. When state is
    `recovery_required`, the durable unfinished journal—not an orphaned process
    lock—blocks ordinary mutation until recovery is verified.

## Work Package 3: Correct Mode Dispatch and Pipeline Semantics

1. Implement the tested mode capability matrix.
2. Route each advertised mode to its corresponding Friday Memory operation.
3. Keep transcripts outside analysis and mutation dispatch.
4. Require the coordinator-created recovery bundle for every mutating mode.
5. Reject full-only flags for incompatible single-step modes.
6. Preflight required LLM and embedding providers before the first mutation.
7. Define safe cancellation boundaries between steps.
8. Prevent substep errors from being overwritten by a final success state.
9. Verify live graph/vector postconditions before declaring completion.
10. Return mode-specific typed step/store results without fabricating a full
    report shape.

## Work Package 4: Add Durable Recovery

1. Write a versioned journal before snapshot creation.
2. Atomically record each safe boundary and bundle-verification result.
3. On normal exceptions, substep failure, or cancellation after mutation,
   attempt automatic rollback.
4. Verify graph, vector, access-buffer, and transcript state after rollback.
5. Mark the result `failed_rolled_back` only after verified restoration.
6. Mark `recovery_required` if automatic rollback cannot complete or cannot be
   verified.
7. Detect unfinished journals on startup and before every mutating request.
8. Provide a narrowly scoped, explicit recovery workflow that resumes rollback
   from the recorded bundle; never silently continue reorganization. The
   workflow is `/reorganize --recover <run-id>` for inspection and
   `/reorganize --recover <run-id> --execute` for restoration.
9. Preserve failed-run bundles and journals until recovery is verified and the
   retention policy permits cleanup.

## Work Package 5: Produce Honest Results and Safe Progress

1. Add explicit aggregation for every framework report type.
2. Preserve errors, warnings, completed steps, skipped steps, and unavailable
   counts.
3. Use the single status enum for all outcomes.
4. Return real recovery-bundle, journal, and reorganization-log paths.
5. Add a narrow progress callback protocol; do not pass Rich objects into
   framework packages.
6. Wire progress through command execution so the user sees acknowledgement
   before the command handler returns.
7. Emit bounded events for quiescence, preflight, snapshot, verification,
   maintenance steps, rollback, and final state.
8. Do not promise immediate cancellation while an atomic section is active;
   report `cancellation pending` and stop at the next safe boundary.
9. Stop heartbeat/progress output on every terminal path.
10. Audit reorganization logging so normal output contains no memory content;
    require explicit policy and restrictive permissions for any content-bearing
    diagnostic artifact.

## Work Package 6: Regression, Fault-Injection, and Recovery Tests

### Parser and configuration

- Exact `--execute` authorizes mutation.
- Plain `execute`, `--no-backup`, unknown tokens, and conflicting modes fail.
- Recovery requires a valid run ID and exact `--execute` before restoration.
- Manual mode remains dry-run regardless of maintenance defaults.
- Exit reorganization remains configurable and defaults to disabled.
- Manual and exit triggers reach the same typed coordinator.

### Store contracts

- Split and legacy memory layouts resolve explicitly.
- Graph/vector snapshot covers every configured collection and required file.
- Transcript snapshot is valid while the source database is in WAL mode.
- Access-buffer WAL is flushed or captured according to its contract.
- Manifests distinguish present, configured-but-absent, and unsupported stores.
- Snapshot verification detects missing, corrupt, incomplete, or mismatched
  artifacts.
- Restore followed by store-specific integrity checks succeeds.

### Concurrency and shutdown

- A manual command cannot overlap background extraction, lifecycle, graph
  maintenance, compaction, reset, migration, or another reorganization.
- Exit reorganization drains background work and snapshots the finalized
  transcript.
- New conflicting tasks are blocked while the maintenance gate is held.
- A second process using the same layout cannot acquire the maintenance lease.
- A stale lease is reconciled with its journal rather than silently stolen.
- The gate is released on success, failure, cancellation, and rollback.
- An abandoned journal blocks another mutation and surfaces recovery guidance.

### Fault injection

- Permission denial and insufficient disk space fail before mutation.
- Provider preflight failure fails before mutation.
- Snapshot failure leaves live stores untouched.
- Corrupt graph, SQLite database, Chroma state, manifest, or journal is detected.
- Failure after every mutating safe boundary triggers rollback.
- Rollback failure produces `recovery_required` and retains the journal.
- Restart detects and successfully recovers an interrupted run.
- Repeated dry-runs are side-effect free except documented sanitized logging.
- Repeated successful execution is idempotent where the selected operation
  promises idempotence.
- Symlink, path alias, and recursive-destination cases fail closed.

### Real integration and terminal behavior

- Production Friday Chat adapter uses real Friday Memory and Friday Transcript
  participant models against disposable stores.
- Every mode invokes the correct operation.
- Counts come from actual typed subreports.
- Immediate acknowledgement and bounded progress render in a provider-free PTY.
- Cancellation waits for a safe boundary and leaves a verified consistent
  fixture or completes verified rollback.
- A full execute, deliberate failure, automatic rollback, restart, and recovery
  drill passes without touching active user state.

## Work Package 7: Documentation and Migration Notes

1. Update `/help reorganize` for exact `--execute`, mandatory recovery bundles,
   mode semantics, explicit recovery syntax, and rejected legacy syntax.
2. Document automatic exit reorganization as configurable and disabled by
   default.
3. Document that transcripts are included for recovery but are not reorganized.
4. Document the package contracts and Friday Chat coordination ownership.
5. Record the scoped FridayV2 freeze exception, affected packages, validation,
   and cleanup point in the framework upgrade log.
6. Label existing vector-only backups as incomplete recovery artifacts without
   modifying or deleting them.
7. Document recovery bundle, journal, rollback, and operator recovery behavior.
8. Document path-resolution base, permissions, retention, and sanitized logging
   rules.
9. Clarify that `maintenance.defaults.dry_run` cannot authorize manual command
   execution.

## Validation Sequence

Run in this order:

1. Focused parser, configuration, and fail-closed tests.
2. Friday Memory snapshot/restore and explicit-layout tests.
3. Friday Transcript WAL snapshot/restore and integrity tests.
4. Friday Chat coordinator, maintenance-gate, and journal tests.
5. Cross-package disposable split-layout integration and fault-injection tests.
6. Provider-free PTY progress and safe-cancellation tests.
7. Package gates:
   - `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest packages/friday-chat -q`
   - `PATH="$PWD/.venv/bin:$PATH" .venv/bin/ruff check packages/friday-chat`
   - `PATH="$PWD/.venv/bin:$PATH" .venv/bin/mypy packages/friday-chat`
   - `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest packages/friday-memory/tests_memory -q`
   - `PATH="$PWD/.venv/bin:$PATH" .venv/bin/ruff check packages/friday-memory`
   - the narrowest meaningful Friday Memory mypy gate;
   - `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest packages/friday-transcript/tests -q`
   - `PATH="$PWD/.venv/bin:$PATH" .venv/bin/ruff check packages/friday-transcript`
   - the narrowest meaningful Friday Transcript mypy gate.
8. Dry-run integration smoke against a freshly constructed disposable fixture.
9. Execute, fault, automatic rollback, restore, and restart recovery drill
   against that fixture.
10. `git diff --check` on changed paths, followed by the broadest practical
    repository checks with unrelated baseline debt reported separately.

Do not validate by copying an active `.friday` directory while the application
is running. A test snapshot must be created by the new quiesced participant
contracts or constructed from synthetic data.

## Review and Delivery Units

Use separately reviewable changes:

1. Friday Chat containment: strict parser, mandatory backup policy, automatic
   path fail-closed behavior, default configuration, and focused tests.
2. Friday Memory explicit layout plus graph/vector snapshot, restore,
   verification, and framework tests.
3. Friday Transcript WAL-safe snapshot, restore, verification, and framework
   tests.
4. Friday Chat coordinator, maintenance gate, aggregate recovery bundle,
   journal, rollback, and shutdown integration.
5. Correct mode dispatch, typed results, progress UX, fault injection, recovery
   drills, and documentation closeout.

Do not combine package publication, provider configuration changes, generated
state cleanup, or unrelated framework debt with these units.

## Acceptance Criteria

Remediation is complete only when all of the following are true:

- Manual and automatic reorganization use one Friday Chat coordinator.
- Automatic exit reorganization remains configurable and defaults to disabled.
- Unknown or legacy command syntax cannot silently change execution semantics.
- Exact `--execute` is required and no backup-bypass option exists.
- Every configured persistent participant is explicitly discovered.
- Transcripts are snapshot/restored for recovery but never reorganized.
- Execute mode cannot mutate before a complete verified recovery bundle exists.
- Graph/vector, transcript, and enabled WAL state use consistent store-owned
  snapshot mechanisms.
- Recovery destinations cannot overlap or recursively contain source stores.
- The exclusive maintenance gate prevents concurrent writers.
- The layout-scoped lease prevents concurrent maintenance from another process.
- Every advertised mode invokes the corresponding operation.
- Required providers are preflighted before mutation.
- Counts and outcomes come from typed report fields; unavailable is never
  rendered as zero.
- Substep errors cannot be overwritten by success.
- Cancellation occurs at safe boundaries.
- A post-mutation failure automatically rolls back and verifies restoration.
- A failed rollback returns `recovery_required`, retains its journal, and blocks
  further mutation until recovery.
- Startup detects unfinished journals.
- The recovery command validates a journal in dry-run and restores only its
  recorded verified bundle when explicitly executed.
- Progress and diagnostics expose no memory, transcript, or credential content.
- Recovery and log artifacts use restrictive permissions.
- Real cross-package tests cover manual, exit, execute, rollback, restart, and
  recovery paths using disposable storage.
- Friday Chat, Friday Memory, and Friday Transcript focused tests, Ruff, and
  meaningful mypy gates pass, with unrelated legacy debt reported separately.
- Existing user runtime state remains untouched.

## Implementation Discovery Gates

These are engineering gates, not unresolved product decisions:

1. Confirm the supported Chroma snapshot/restore mechanism before implementing
   the Friday Memory participant. If no safe mechanism is available through the
   current adapter, add the smallest typed adapter capability inside the
   authorized Friday Memory scope.
2. Confirm the durability operations required for atomic journal and manifest
   updates on supported platforms.
3. Inventory all configured persistent participants, including optional
   access-buffer WAL state, before freezing the manifest schema.
4. Prove rollback and restart recovery in disposable integration tests before
   re-enabling execute mode or automatic exit reorganization.
