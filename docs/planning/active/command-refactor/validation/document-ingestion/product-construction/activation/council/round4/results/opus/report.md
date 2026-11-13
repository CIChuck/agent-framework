# INGEST activation package — Opus seat, global round 4/6 (additional pass 1/3)

Seat: opus (claude-opus-5-5), fresh read-only. Candidate `a4b18fe5743ea8543bd000f6f85d8225d4dbb676`, branch `feature/cmd-ingest-001`.

- **Verdict: CHANGES_REQUESTED**
- **assessment_complete: true**, areas_assessed 8/8, E1–E5 assessed
- **Overall: 9.41 / 10**, the exact weighted sum, truncated and not rounded up
- Mandatory findings: 1. Advisories: 6.

## Input and boundary checks

- Request SHA256 `d8bc163d…2ded` matched before reading (Python stdlib).
- All 16 required inputs, the 10 optional references, controller-checks, the approved instructions and current-controls matched their pins.
- All 22 approval-binding input/appendix/adjustment hashes match the current files.
- Entry and exit: logical index (`git ls-files -s -z`) = `2f3eb131…c934`, HEAD and branch as expected, status equal to the declared three lines, nothing staged. All eight preserved entries matched exactly (metadata, plus hashes where declared).
- Entry deviation, disclosed: the first logical-index command failed because of shell word-splitting. One `git status` (GIT_OPTIONAL_LOCKS=0) ran before the index hash was taken correctly. No index write was possible, and the hash matched.
- The five digest vectors were recomputed in private scratch from the stated canonicalization: canonical text, hex and SHA256 all match. The raw UTF-8 vector also matches. This is a design-consistency check only.
- Targeted source reads only:
  - `friday_tools` package initializers (the parent-import closure)
  - Chat `FrameworkAsyncClientLifecycle` (frozen, no fields), `FridayRuntime.async_clients`, `CommandContext.runtime: FridayRuntime | None`, `_read_handler` / `_ingest_handler`
  - Runtime `DIContainer.shutdown` (MCP stop only)
  - `friday-commands/tests_commands` listing
- Not done: no product import, test, build, install, network, provider or store operation, AST or inventory rebuild, or harness replay. No Finance `test_integration_massive.py`, user YAML, `.friday*`, exports or `.venv` contents were opened. No checkout or input writes. Controller-checks were treated as identity metadata only.

## Neutral E1–E5 assessment

**E1 — satisfied.**
- Tools exposes `resolve_document_conversion_settings` / `create_document_converter`.
- Precedence: explicit absolute path, else `FRIDAY_DOCUMENT_CONVERSION_MANIFEST`. No fallback, and no lookup of the embedding manifest.
- The schema, the 1 MiB cap and the asset-manifest/profile containment are strict.
- `/read` resolves only the document binding. Plain text never resolves it.
- Covered by I3-C1 and I3-C3 witnesses and the installed-candidate witness (positive case, plus refusal before the worker starts), with guide/README assignments at I3-C5.
- See advisories 1 and 2.

**E2 — satisfied.**
- The parent-initializer limitation is stated honestly. Source confirms `friday_tools/__init__` eagerly imports finance (`friday_finance`), sandbox, smart_read and the readers.
- Initializer time and RSS count against the cold/RSS limits. No bootstrap shim or init edit is allowed, and a stop-for-reconciliation condition exists.
- fd 1 is duplicated and redirected before vendor imports.
- The versioned IPC envelope and state table, with explicit invalid-transition refusal, are present and tested by the I3-C4 headless worker witness in normal and -O installed lanes.

**E3 — satisfied.**
- The retained `capability_record_sha256` is re-read and compared on every `create`, including in the child.
- Named I1-C2 witnesses exist: `…manifest_resolution_is_strict_and_contained`, `…counter_factory_binds_exact_capability_record_bytes`.
- `test_simple_vector.py` is kept as an unchanged I1 selector.
- Cross-process drift is tested at I3-C4.

**E4 — satisfied.**
- A private `_OwnedIngestionState` lives in `adapters.py` under the frozen wrapper. The lock is synchronous, with no awaits held under it.
- `bind_document_converter` and `bind_ingestion` are both specified. Neither resolves settings at boot or initializes Memory for `/read`.
- Close order: entry → converter → LLM clients. A shielded retained task handles repeated cancellation.
- See advisory 3.

**E5 — satisfied.**
- Optional-only YAML and keys: `max_input_tokens` / `expected_dimensions`, `ingestion.chunking`. No required key or constructor parameter.
- Parent and appendix bindings are current.
- The extension controls only the council budget (README tail, request).
- See advisory 4 for one stale phrase.

## Review A1–A8

| Area | Evidence (concise) | Score | Weight | Contribution |
| --- | --- | ---: | ---: | ---: |
| A1 | Maintainer decisions applied without reviving the parity campaign. Gates A1–A5 are honestly incomplete. Construction is not activated. Impact v0.6 is still canonical, and its revision is required at A4. One stale round-count phrase. | 9.6 | 1.50 | 14.400 |
| A2 | Complete typed fields and invariants. Exact protocols. Space-equality preflight. Plan/receipt digests reproducible. Two independent bindings. Minor: settings "tamper" wording. | 9.5 | 1.75 | 16.625 |
| A3 | One active plus one queued, busy before I/O. Profile deadlines owned by the parent monotonic clock. TERM/KILL/reap, unhealthy state on failed reap. Ordered DI/Chat close, headless recipe. Minor: placement of the parent-side XLSX audit and post-plan IPC state. | 9.4 | 1.75 | 16.450 |
| A4 | `embed_*` shapes unchanged. Only an optional constructor kwarg is added. I1 legacy preserved, I2 switches over in a coordinated way. Exact route matching. Fresh-store, pending/raced marker and v1/v2 recovery combinations are strict. | 9.5 | 1.50 | 14.250 |
| A5 | 91 exact paths, 49 mapped cases, 46 planned witnesses, retain default, helper classes, fixture oracles. The I3 required selectors contradict the module classification (M1). | 8.9 | 1.25 | 11.125 |
| A6 | Full workbook refusal before conversion with actionable text. Full coverage/order with no overlap. Refusal when a minimal unit cannot fit. Partial results never yield a receipt. Readback-confirmed IDs. | 9.4 | 0.75 | 7.050 |
| A7 | Tools/Memory/Core/LLM ownership as decided. Tools never imports LLM by name. Narrow extras/lock, Certifi floor. TOOLS-DOC stays separate. Headless profiles tested. | 9.5 | 0.75 | 7.125 |
| A8 | I1 additive, I2 coordinated switch, I3 adoption. Worker proof at I3-C4 (non-circular). Per-slice approval/validation, then aggregate review, then UAT. | 9.5 | 0.75 | 7.125 |
| **Total** | | | 10.00 | **94.150 → 9.41** |

## Mandatory finding

**M1 — the I3 required selectors name an unclassified module with no witness and leave out a classified witness module (A5).**

Evidence:
- `validation-plan.md` §Exact selectors, I3 row, requires `packages/friday-commands/tests_commands/test_file_inputs.py`.
- That module:
  - is absent from `test-case-map.json` `modules` (13 entries, so it is unclassified)
  - has no `planned_new_witnesses` node
  - does not exist at baseline (the tests_commands listing confirms this)
- The map's own rule says "Unclassified modules/helpers cannot execute under this map". The plan says an unclassified module "stop[s] execution".
- So I3 as written cannot run its own required selector. Separately, the new public Commands API `parse_file_input` / `FileCommandInput` (`file_inputs.py`, new at I3-C3) has no direct named witness for:
  - REM C quote, opaque-description and terminator semantics
  - refusing document line options before conversion
  - no filesystem/environment access
  - stdlib-only imports with API54 unchanged

  It is covered only indirectly through Chat registry integration.
- The same I3 row also omits `packages/friday-runtime/tests_runtime/test_di.py`. That file is classified and holds the I3-C4 witness `test_shutdown_drains_shared_document_worker`.

Violated requirement: A5 exact assignments and traceable valid coverage, plus the plan's own classification-before-execution rule.

Bounded fix (planning documents only):
1. Add `test_file_inputs.py` to the `modules` list (`exists_at_baseline: false`, offline class).
2. Add an I3-C3 planned witness, for example `test_parse_file_input_rem_c_semantics_and_document_option_refusal`, with requirements and assertions. It should also assert that no Core/Memory/filesystem/environment imports occur.
3. Name the existing `tests_commands/test_import_boundary.py` as a retained API54/stdlib regression selector.
4. Add `test_di.py` to the I3 selector row.

Future acceptance: the I3 phase expansion shows every selector classified and every witness bound before execution.

## Advisories (non-blocking)

1. **Settings tamper wording.** "Tampered settings … bytes are `identity`", but the resolver receives no expected hash for the settings file itself. Clarify:
   - settings content errors are `readiness`
   - manifest/profile mismatches against the declared hashes are `identity`
   - the settings-file hash is recorded at Gate A2/A5
2. **`/read` without a runtime.** `CommandContext.runtime` may be `None`, and the lazy converter owner is reached through runtime/`async_clients`. State that document `/read` refuses, or owns a converter locally under try/finally, when there is no runtime.
3. **Lifecycle constructor kwargs.** State that the new `FrameworkAsyncClientLifecycle` keyword arguments seed `_OwnedIngestionState` (created via `field(init=False, default_factory=…)`), and that accessors read the holder, so there is a single source of truth.
4. **Stale round count.** `requirement-reconciliation.md` still says "these three review rounds". Align it with global rounds 1–6.
5. **XLSX audit placement and IPC state.** Say where the parent-side XLSX structural audit runs: off the event loop (thread or bounded preflight), and inside the heartbeat window. Consider a terminal `planned` state rather than returning to `converted` when a second plan is invalid anyway.
6. **RSS sampling dependency.** Name the mechanism and dependency used for process-tree RSS sampling (test-only or product) in the A5 profile.

## Limits

This is a design review only; no product behavior was executed. The comparison with the earlier round is limited to the neutral E1–E5 questions, with no peer or previous reports used. Source reads were targeted, not exhaustive. Scores reflect a judgment about the document as a basis for building, not product conformance. This verdict grants no construction, effects, acceptance or delivery authority.
