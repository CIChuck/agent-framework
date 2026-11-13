# REM-CMD-INGEST-001 — compatibility cycle pass 2/4 (global round 7) — Opus seat review

## 1. Outcome

**CHANGES_REQUESTED**

| Score | Value | Rubric |
| --- | --- | --- |
| Coverage | **8.8 / 10** | all-framework direct/transitive consumers 3.5/4.0; baseline+replacement positive proof 2.6/3.0; negative/identity/overflow/failure-effect 1.75/2.0; headless/minimal-install/non-embedding 0.95/1.0 |
| Overall | **8.5 / 10** | framework consumer inventory 1.75/2.0; operational configuration & API compatibility 2.5/3.0; model replacement & namespace data safety 2.2/2.5; bounded proof & reporting 1.75/2.0; scope & authority 0.3/0.5 |

There are three mandatory findings (M1–M3) and nine advisories (A1–A9). Neither score reaches the 9.5 gate. I did not adjust the scores toward that target. Most of the pass-1 corrections are source-accurate and well bounded; see §6. M1 and M3 are source-feasibility contradictions inside two of the corrected contracts (FC-02 and FC-03). M2 is a status-record integrity defect introduced by this candidate.

## 2. Candidate, diff and authority

- Repository `/Users/chuckrussell/Dev/gendev/agent-framework`, branch `feature/cmd-ingest-001`, HEAD `f1916747ad7d03e451f2b57dc00542faa6095d7c`.
- Aggregate base `91ac63ba…`. Amendment base `8d25d53a…`. I read the amendment delta first, using only the six technical paths and then the eight status paths in the request.
- Request `review-request.json` SHA256 `d7e045a1…6f9e` was verified before reading. Helper hashes verified: `check_integrity.py` `6ef84653…`, `read_only_command.py` `cb0669f8…`, `extract_current_controls.py` `a9fd727a…`, `current-controls.json` `6d63c006…`.
- Current controls: I ran the static extractor without the wrapper (it is a plain static read) into OWN `controls-copy.json`. That file is byte-identical to the frozen controls (`cmp` identical; SHA256 `6d63c006…`). I did not open or grep the raw `authority.json`. Controls record: REM `proposed`/`planning`/`in_review`, implementation `not_granted`, pass 2 of 4, `product_changes_authorized: false`, and no Gate-A or construction authority.
- Authority read: `AGENTS.md`, the independent-validation policy (and the engineering/lifecycle policies through AGENTS), council and independent-validator skills, `scope-decisions.md`, `ingest-existing-store-policy.md` and `compatibility-iteration-authorization.json`.
- Documents read in full at the current pins: REM (`069ff23f…`), normative annex (`bbafc992…`), Tools companion (`8220e195…`) and correction map (`42307859…`).
- Review mode: fresh, read-only design and source-feasibility review. No product execution.

## 3. Independence and conduct

- Fresh context. I received no parent reasoning or transcript. I opened no raw historical or peer reports (council-round6 report files were neither opened nor grepped), started no nested agents and made no repairs.
- Pass-1 scores appear in the status diff (execution-log/board event text). I treated them as context only.
- Private scratch: `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/86392a73-9eb6-4485-91dd-39acbe67a9c7/scratchpad/opus-r7p2-1794365215`. It is outside the repository and all supplied inputs.
- **Wrapper discipline:** every Git and admin invocation went through `read_only_command.py`. The audit log records 12 wrapped completions, all exit 0. My first attempt at the five admin checks failed in zsh before any process started: the shell treated the whole unsplit wrapper string as a command name and returned "no such file or directory", exit 127. No Git, uv or helper process ran in that attempt, so no unwrapped command executed. I then reissued all five through the wrapper.
- Static reads only: package `src` trees, which I searched broadly, but only under `packages/*/src`. By explicit path I also read the committed packaged template `friday_chat/config_templates/config.example.yaml`, three `pyproject.toml` files, `uv.lock` and the installed pinned `chromadb` 1.4.0 source in `.venv` (backend-behavior read only). I never read either dirty example YAML or anything under `.friday-old`, exports or other personal state. The only `.friday-old` paths I cite come from the frozen request's own `status_porcelain_all` string.
- No product imports, tests, builds, installs, downloads, provider calls, store operations or writes to the repository or inputs.
- The harness auto-persisted two large tool outputs to its own `~/.claude/projects/.../tool-results/` directory: the request JSON and the status diff text. That location is outside the repository and supplied inputs. It was harness behavior, not a write by me, and I disclose it here.
- `uv run` caches went to OWN through the wrapper's `UV_CACHE_DIR` and `XDG_CACHE_HOME` settings.

## 4. Mandatory findings

### M1 — FC-02's public observer and cleanup contract cannot be built from the current source as written (high)

**Files:**
- annex FC-02, lines 163–192
- REM allowlist row for `ingestion/mcp.py` and `memory_mcp.py` (REM:1235)
- `friday_chat/memory_mcp.py:29-31,126-232`
- `friday_chat/turns/processor.py:688-708`
- `friday_telemetry/models/mcp.py:26-80,80-95`
- `friday_telemetry/helpers/mcp.py:34-52`
- `friday_runtime/mcp_loading.py:171-195`

**Evidence:**

1. The only maintained sink for the observer is the turn processor's lambda. It forwards `reason` into `RuntimeMCPProvider.emit_event(..., reason: MCPEventReason)`. `MCPEventReason` is a closed `Literal` in friday-telemetry, and `MCPEvent` is `strict=True, extra="forbid"`. `MCPTelemetryHelper.emit` swallows validation errors with `except Exception: return`.
   - FC-02 asks for "additional bounded safe reason literals" such as an explicit oversized decision or a refusal/ownership category. If those literals are new, they fail mypy at `processor.py:706`. That file is not on the allowlist.
   - At runtime they are silently dropped from exported telemetry. They survive only in `_ingestion_counts`.
   - Making them work requires changing the friday-telemetry contract. The annex explicitly holds telemetry "compatible unchanged" and gives it no opportunistic rewrite.
   - The annex never says whether the new outcomes must reuse existing `MCPEventReason` members (for example `token_limit` or `capped`, `rejected` or `unavailable`, `execution_error`) or need a scoped telemetry and processor change.
2. FC-02 requires construction to "Retain current cancellation, readback and **cleanup of newly owned, uncommitted snapshots**".
   - Current maintained source has no such cleanup. `persist_mcp_interaction` ends with `except asyncio.CancelledError: raise`, and `discard_mcp_memory` (`adapters.py:342`) has no maintained caller.
   - Today a pending snapshot staged by an earlier call in the same turn is left as a non-retrievable pending record when a later call fails or the receipt append fails (`retrieval/mcp.py:66-70`).
   - FC-02 turns typed refusals and `storage_failed` from "skipped receipt" into a whole-persistence error. That makes the orphaned-pending case more frequent.
   - An implementer cannot "retain" behavior that does not exist. They would either add an unspecified discard path or leave a behavior the design says is absent.

**Risk:** the real observer and turn-outcome witnesses demanded by `test_mcp_snapshot_embedding_compatibility` are either infeasible within scope or silently non-observable, and pending-record handling is undefined.

**Required narrow fix (document only):**
- (a) Freeze an exact mapping from each new FC-02 outcome to an **existing** `MCPEventReason` member, so no telemetry or processor change is needed. Alternatively, add an explicit allowlist row for the `friday_telemetry/models/mcp.py` reason extension and `turns/processor.py` typing, with telemetry-contract tests, and remove the conflicting "telemetry unchanged" claim for this one boundary.
- (b) Replace "retain current cleanup" with the actual current behavior. Then choose one of:
  - accept and disclose that pending records left after a failed persist remain unpublished and unretrievable, with no new cleanup; or
  - authorize a narrow discard of records newly staged by this call before any receipt append, which preserves pending records whose receipt is already durable. Name it in the exception list.

**Future witnesses:**
- Real `TurnProcessor._persist_turn` with a live `RuntimeMCPProvider`, telemetry disabled and enabled. Assert the `ingestion_decisions` counts and the exported `MCPEvent` reason for each of: oversized, typed refusal, storage_failed, ownership conflict.
- A mixed turn where call 1 is prepared and call 2 is refused. Assert the transcript receipt, the persistence error, call 1's record state (pending or discarded, per the chosen rule) and that it is not retrievable.
- Run in normal and `-O` installed lanes.

### M2 — 35 historical "Next gate" lines in status records were overwritten (medium)

**Files:**
- `next-phase.md` and `tactical-plan.md`, lines 27, 38, 49, 58, 79, 97, 116, 139, 162, 183, 205, 228, 247, 276, 299, 333 and 359 in each (17 per file)
- `command-refactor/README.md:183`

**Evidence:** the wrapped amendment status diff, `git diff 8d25d53a..f1916747`, shows 35 `-**Next gate:**` lines that are not the pass-1 current gate. They sit under headings such as "Historical implementation checkpoints", "Historical round3 handoff" and "DIAG-001 — verified completion and human acceptance checkpoint". Each was replaced with the current pass-2 INGEST gate. The original texts were MAINT UAT, MEMQ D0/D1/D2 and DIAG acceptance gates. Four lines legitimately changed from pass 1 to pass 2.

**Violated:** EC-18 (coherent current state; historical records preserved and not misrepresented), plus the lifecycle and validation policies' durable-evidence expectations. The 35 checkpoints now falsely state the current INGEST gate. The board, dashboard and documentation checks do not catch this.

**Fix:** restore those 35 historical lines byte-for-byte from `8d25d53a`, and change only the current-gate lines. No other scope.

**Witness:** a wrapped diff limited to these three files shows only current-gate deltas.

### M3 — FC-03 positive physical backup has no defined layout, contradicting REM and the exception list (high)

**Files:**
- annex FC-03 (lines 194–227); REM:951–966 ("Legacy callers without an explicit resolved directory/admission fail actionably instead of guessing")
- `maintenance/backup.py:39-70,137-156,273-326`
- `chat/adapters.py:790-830,1080-1110`
- `maintenance/__main__.py:346-363`
- `runtime/di.py:248-256`

**Evidence:**

1. `BackupManager(memory_dir, backup_root)` has no layout parameter. File selection is fixed: root-level `MEMORY_FILES` plus a recursive copy of `memory_dir/vector/**`.
2. The only maintained constructor of `MemoryReorganizer`, and therefore of `BackupManager`, is in Chat (`adapters.py:804` and `:1081`). It passes `memory_dir=Path(config.memory.persist_directory)`, which is the **vector directory itself**. In that form:
   - the default `backup_root` is `<vector>/backups`, inside the namespace;
   - selection copies only a root-level `chroma.sqlite3` and misses the Chroma 1.4 per-segment `<uuid>/{data_level0,header,length,link_lists}.bin` directories. The request's frozen porcelain shows that layout under `.friday-old/vector/<uuid>/`;
   - the `embedding-space.json` sidecar is not copied, because `memory_dir/vector` does not exist in this form.

   A restore in this form would report success while writing an incoherent index into the same incarnation. The existing non-dry-run Chat route is disabled, but FC-03 requires positive results for Reorganizer `backup`/`backup_first` and the injectable Tools wrapper, which accepts any constructed Reorganizer.
3. Runtime's layout cannot be expressed through `memory_dir`: `chroma_path` and `resolve_runtime_state_path("memory/graph.json")` are independent paths.
4. FC-03 says "use … the resolved layout" and "freeze exact source/artifact member mapping at Gate A". REM requires callers without an explicit resolved directory to fail rather than guess. It does not say how the unchanged public signature yields a resolved layout, which `memory_dir` forms are admitted, or that the member inventory must be complete before create or restore reports success. Refusing the vector-dir form would itself be a new compatibility exception, and the exception list is closed ("Any additional exception stops readiness").

**Required narrow fix (document only):**
- State the deterministic `memory_dir` → layout derivation for the unchanged signature: memory parent, `vector/` child, `graph.json`.
- Classify the vector-dir form and the Runtime split layout explicitly. Either refuse before mkdir as a named exception added to the exception list, or require the frozen member mapping to cover every Chroma segment directory.
- Require a member-completeness check against the admitted live layout at create, at verify, and before any restore write. An incomplete set refuses; it never yields a partial "success".
- Keep the sidecar as receipt evidence and never restore it as a file.

**Future witnesses:** run each of the following on B and N disposable stores, normal and `-O`:
- public create/verify/same-incarnation restore with the memory-parent layout, asserting restored rows are queryable and the live sidecar bytes are unchanged;
- vector-dir `memory_dir`, which must refuse (or complete, if that option is chosen) before mkdir;
- a Tools `MemoryMaintenanceTool(backup_first=True)` built over each form;
- a segment-file deletion mutant, which must make create and restore refuse.

## 5. Advisory findings

- **A1 (FC-08):** the named catch seams omit `MemoryController._retrieve_graph_with_scoring`'s `except Exception` (`memory_controller.py:1639`) and the explicit `recall` `asyncio.gather(..., return_exceptions=True)` unpacking (`:522-527`). FC-08 already requires injected-scorer foreign-vector failures and actual recall errors to propagate. Name both seams so the injected B/N/R node is not defeated by those swallows.
- **A2 (FC-06):** the Agent's outer `asyncio.create_task(_safe_extract_context)` (`friday_agent/base.py:500`) can run after Runtime shutdown has drained the assembler. Specify that `extract_context` called on a closed or drained assembler records `skipped-unavailable` and opens no closed sink. Agent stays source-unchanged. Add a late-arrival witness.
- **A3 (FC-01):** say how an extractor without `rejection_log_path`, and the standalone `configure_rejection_logging()`, interact with owned sinks. The current default emits to the module-global logger (`extraction_filter.py:25-67,127,178`). Also list Chat's `logging.extraction_rejections` boolean (`config.py:273`) as inert, alongside the `_file` field.
- **A4 (FC-11 scope):** the empty-collection admitted-dimension substitution and graph-only REEMBED fixes are in `maintenance/mutation.py` (`_collection_dimension`, `:628-640`; `:1309-1327`). The REM row for `mutation.py` allows only admission, v2 binding, fingerprint and restore. Add the FC-11 purpose to that row explicitly.
- **A5 (inventory, EC-02):** `RetrievalFactorComputer` (`factor_computer.py:184-254`), `AccessBuffer.flush_all` and `IncrementalGraphMaintainer` are store-only metadata consumers wired in Chat. They have `except Exception` swallows and appear in no annex row. Give them a source-unchanged disposition (admission at construction; no embedding I/O) or name their typed-refusal behavior.
- **A6 (FC-13):** the `VectorInspectionTool` query branch calls `controller.vector.search(...)`, but neither `ChromaVectorStore` nor `SimpleVectorStore` defines `search`, so the branch is pre-existing broken. Classify it as no-credit pre-existing behavior, recorded in the upgrade log under O-05. Positive coverage applies only to the `get_all` branch. Otherwise the mandated actual-call wrapper tests contradict unchanged behavior.
- **A7 (FC-09):** consider per-kernel `tenant`/`database` on `EphemeralClient`, which chromadb 1.4.0 supports. It is a lighter isolation alternative to collection-name suffixing. Either way, freeze one approach and its name-length constraints at Gate A.
- **A8 (FC-02):** the token-overflow pre-check needs a counter injected into `MCPMemoryIngester`. It is constructed with only `collection_manager` in `FrameworkMemoryAdapter.prepare_mcp_memory` and `verify_mcp_memory` (`adapters.py`, approximately lines 309–336). Name that constructor seam.
- **A9 (status):** REM lines 17–27 still describe the superseded "rounds2–4" authority without a superseded marker. This is minor and historical.

## 6. Pass-1 correction dispositions (my own judgment)

| ID | Disposition | Source check |
| --- | --- | --- |
| IC-01 / FC-03 | **Not closed** (M3) | Public create/verify/restore are retained, receipt/sidecar/unsafe-root rules are sound and the separate v2 family is correct. Layout and member completeness are undefined. |
| IC-02 / FC-06 task | **Closed** (A2) | Unowned inner `create_task` at `assembler.py:420` and no-op `di.shutdown` (`di.py:135-147`) confirmed. Status/wait, drain and telemetry-off rules are appropriate. |
| IC-03 / FC-02 | **Not closed** (M1) | Disposition table and receipt rules are sound; observer contract and cleanup premise are not. |
| IC-04 / FC-01 | **Closed** (A3) | Global `rejection_logger`, eager `mkdir`/`FileHandler` (`extraction_filter.py:43-67`) and eager Chat/Runtime construction (`adapters.py:2063-2091`, `di.py:360-373`) confirmed. Per-owner lease design fits. |
| IC-05 / FC-08 | **Closed** (A1) | Verified independently: neither `adapters.py:1810-1817` nor `di.py:299-306` passes `graph_scorer`; `memory_controller.py:1590` returns unscored. Both scorer APIs (`graph_scorer.py:221,288,330,382`) are injectable only. |
| IC-06 / FC-06 extraction | **Closed** | Per-item swallows at `extractor.py:544,583,602,665,678,698` and the vectorless-edge path at 583→592 confirmed. Outer `extract()` returns `result.error`; Chat `_extract_turns` re-queues on `error` (`adapters.py:1168-1185`). `ExtractionCommitCompletedUnderCancellation` is a `CancelledError` subclass, so cancellation is preserved. Stable IDs at `:708-715`. |
| OPUS-R6-A1 / FC-09 | **Closed** (A7) | chromadb 1.4.0 `SharedSystemClient._identifier_to_system` and settings-keyed `EphemeralClient` confirmed. |
| A2 / FC-08 seams | **Closed** (A1 omissions) | `get_all` (`collection_manager.py:421-431`), `get_insights_by_author` (`:319-328`), priming/fetch catches present. |
| A3 / FC-13 | **Closed** (A6) | Tools `maintenance.py` and inspection confirmed injectable only; Chat legacy execute disabled (`adapters.py:780-782`). |
| A4 / FC-12 | **Closed** | `tool_loading.py:60-96` `walk_packages`; any import failure raises `ToolProviderLoadError`. |
| A5 / FC-05 | **Closed** | `synthesizer.py:697-742` covers the three shapes and the `None` → Chroma-default path (`:785-795`). |
| A6 / FC-11 | **Closed** (A4) | Synthesizer probe at `pipeline.py:523-526` precedes the embedding probe at `:551-553`. |
| A7 status | **Partially closed** | Current gate is coherent, but M2 corrupts history. |
| A8 / FC-01 | **Closed** (A3) | Only `config.py:274` references the setting. |
| A9 / B02 | **Closed** | Default `text-embedding-3-small` (`adapters.py:1749`). Early-stop disclosure is appropriate. |
| A10 / FC-04 | **Closed** | `analyzer.py:103,146,206` use plain `sqlite3.connect`; read-only URI requirement is explicit. |
| Round-5 themes EC-01..09 and 10 high/medium | **Retained and coherent** | FC-01..14 map one-to-one. |

## 7. Independent consumer inventory and dispositions

Sweep: an embedding/vector token grep over every `packages/*/src`. Files with direct hits: Memory 18, Core 5, Chat 4, LLM 3, CLI 1, Runtime 1; zero in Agent, Commands, Finance, MCP, Moltbook, Optimization, Sandbox, Speech, Telemetry, Tools and Transcript. A second store-consumer grep found the indirect users. `friday-tui` has 0 tracked files (stray `__pycache__` only), so it gets no disposition.

| Consumer (source) | Route class | Disposition / proof | Status |
| --- | --- | --- | --- |
| LLM `embeddings.py`, `model_library.py`, resolver | maintained | shared guard, FC-10/12, DI-18 | covered |
| Core `profiles.py`, `interfaces/memory.py`, `llm.py` | maintained | admission/envelope, FC-09/10 | covered |
| Memory `adapters/vector.py`, `simple_vector.py`, `collection_manager.py` | maintained | admission on every read/write; FC-08 `get_all` seam | covered |
| `memory_controller.recall` / `prime` / fetch / author | maintained | FC-08 | covered; seams per A1 |
| `_retrieve_graph_with_scoring` + `graph_scorer` sync/async | public-injectable (unwired) | FC-08 capability B/N/R, zero-comparison spies | covered; seam per A1 |
| `context/extractor.py` (edge embed, insights, summary) | maintained (Chat always; Runtime when enabled) | FC-06 | covered |
| `extraction_filter.py` rejection logging | maintained | FC-01 | covered; A3 |
| `context/assembler.extract_context` + Agent `_archive_turn` | maintained (Runtime/Agent) | FC-06 | covered; A2 |
| `context/consolidator.py` | public-unwired (no construction found) | FC-06 | covered |
| `maintenance/compactor.py` (`InSessionCompactor`) | maintained (Chat) | compaction row | covered |
| `lifecycle/promotion.py`, Tools `memory/lifecycle.py` | maintained / public | FC-07 | covered |
| `retrieval/factor_computer.py`, `access_buffer.py`, `maintenance/incremental.py` | maintained (Chat) | store-only metadata; **unlisted** | A5 |
| pipeline / synthesizer / pruner / fact_checker / mutation / recovery | maintained (MAINT) + public | FC-05/11, DI-27/28 | covered; A4 |
| `backup.py` / `reorganizer.backup` / module backup / Tools wrapper | public | FC-03 | **M3** |
| `analyzer.py` | public | FC-04 | covered |
| `ingestion/mcp.py` + Chat `memory_mcp.py` + `turns/processor.py` observer + telemetry `MCPEventReason` | maintained opt-in | FC-02 | **M1** |
| `ingestion/tool_ingester.py`, `large_file_processor.py`, Tools `smart_read` | public / injected | DI-19/23/30 | covered |
| `lifecycle/migration.py`, Chat migrate stub | inactive | no credit | covered |
| `multi_agent/controller.py`, `coordinator.py` | maintained when `memory_mode=multi_agent` | FC-13 | covered |
| Agent `tools/builtins.py` `recall_memory` / `store_fact` | maintained (Runtime registration) | FC-13; no catch, so errors propagate | covered |
| Tools `memory/inspection.py` (Stats / Graph / Vector) | public-injectable | FC-13 | covered; A6 |
| Runtime `di.py` (profiles, eager graph-parent `mkdir`, extractor, shutdown) | maintained | FC-06/09/10 | covered |
| Runtime `tool_loading._friday_tools_catalog` | maintained | FC-12 | covered |
| CLI `container.FridayConfig` → `RuntimeConfig` | public compat | FC-10 / B06 | covered |
| Chat `adapters.build_framework_embedding_service` | maintained | B01/B02, FC-10 | covered |
| Chat `reorganization/mutation.py` | maintained | REM row | covered |
| Telemetry (non-MCP), Transcript, Commands, MCP transports, Speech, Sandbox, Finance, Moltbook, Optimization | no embedding refs | unchanged; import / minimal-install witnesses | covered (except telemetry MCP reasons per M1) |

## 8. B / N / R matrix (design sufficiency)

| Flow | B positive | N positive (dimension change, same-dimension different space, smaller cap) | R refusal | Judgment |
| --- | --- | --- | --- | --- |
| Extraction → graph / insight / summary → recall | FC-06/14, DI-33 | FC-14 | FC-06 typed, no vectorless edge | sufficient |
| Background Agent / assembler | FC-06 node | same | delayed failure, telemetry off | sufficient (A2) |
| Chat pending extraction | FC-06 node | same | re-queue | sufficient |
| MCP snapshot | FC-02 node | same | oversized / refusal / ownership | **insufficient (M1)** |
| Physical backup / restore | FC-03 node | same | receipt / sidecar / clone / unsafe root | **insufficient (M3)** |
| Logical v2 snapshot / rollback | DI-27/32 | same | v1 / tamper | sufficient |
| Lifecycle promote / decay / reactivate | FC-07 | same | false-return counts | sufficient |
| Maintenance synth / REEMBED / prune / verify | FC-11, DI-28 | empty-store dimension, graph-only | probe order, 8192 | sufficient (A4) |
| Legacy synthesis shapes | FC-05 three shapes | same | no Chroma default | sufficient |
| Analyzer | FC-04 provider-offline | same | no open on refusal | sufficient |
| Injected scorer | FC-08 injected B/N | same | same-dimension foreign | sufficient (A1) |
| Profiles ×4, two ephemeral kernels | FC-09 | same | no PersistentClient | sufficient |
| Tools wrappers / inspection | FC-13 | same | typed failure / partial | sufficient (A6) |
| Headless installs | FC-12 | — | missing counter / assets | sufficient |

## 9. B01–B08

All eight families are source-backed:

| ID | Source | Notes |
| --- | --- | --- |
| B01 | `adapters.py:1740-1746` | pool default |
| B02 | `:1748-1760` | — |
| B03 | sanitized fixture | Gate-A |
| B04 / B05 | `di.py:166-246` | — |
| B06 | `container.py:63-126` | — |
| B07 / B08 | maintenance config / `EmbeddingModel` | — |

The ignored Chat `embedding.embedding_service` hint is verified (`config.py:470`, unused in selection). Unknown qualification is a hard stop, not a silent exclusion (annex:68-89). This is adequate.

## 10. Criterion rows

| ID | Result | Evidence |
| --- | --- | --- |
| EC-01 | PASS | Controls identical; authority JSON; four-pass budget; design only. |
| EC-02 | PARTIAL | §7; unlisted store-only users (A5); telemetry boundary (M1). |
| EC-03 | PASS | §9; annex:91-98; REM E. |
| EC-04 | PARTIAL | Envelope consumers classified; MCP observer contract (M1). |
| EC-05 | PASS | REM:644-664; annex:68-89. |
| EC-06 | PASS | REM:689-691, 783-803. |
| EC-07 | PASS | §6 IC-05 verified. |
| EC-08 | PASS | IC-06 / IC-02; A2 advisory. |
| EC-09 | **FAIL** | M3. |
| EC-10 | PASS | FC-07; REM:692-694. |
| EC-11 | PASS | §7; FC-12 catalog; A5 advisory. |
| EC-12 | PASS | annex:21-36; REM:1086-1147. |
| EC-13 | PASS | annex:37-39; REM:684-688. |
| EC-14 | PARTIAL | REM:805-836; swallow seams per A1/A5. |
| EC-15 | PASS | DI-18..34 sufficient apart from the M1/M3 nodes. |
| EC-16 | PARTIAL | Allowlist gaps: processor / telemetry (M1), mutation.py purpose (A4). |
| EC-17 | PASS | Companion coherent; Certifi floor; FC-12 lazy imports. |
| EC-18 | **FAIL** | M2. |
| FC-01 | PASS (A3) | §6. |
| FC-02 | **FAIL** | M1. |
| FC-03 | **FAIL** | M3. |
| FC-04 | PASS | §6. |
| FC-05 | PASS | §6. |
| FC-06 | PASS (A2) | §6. |
| FC-07 | PASS | `promotion.py` / Tools lifecycle; annex:294-299. |
| FC-08 | PASS (A1) | §6. |
| FC-09 | PASS (A7) | §6; `profiles.py:74-87`; `vector.py:83-86`. |
| FC-10 | PASS | §9. |
| FC-11 | PASS (A4) | §6. |
| FC-12 | PASS | `tool_loading.py:60-96`; Memory pins LLM + tiktoken. |
| FC-13 | PASS (A6) | §7. |
| FC-14 | PASS | annex:402-409. |

## 11. Checks

| Check | Command (via wrapper) | Exit | Output SHA256 |
| --- | --- | --- | --- |
| integrity-start | `check_integrity.py` request | 0 PASS (17681 protected, 0 failures) | `f62cb573…` |
| current-controls | extractor → `cmp` | identical | `6d63c006…` |
| board | `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` | 0 ("36 tasks") | `c4d2aec6…` |
| dashboard | `… render --check` | 0 | `a28df311…` |
| docs | `… check-documentation-lifecycle.py` | 0 (1008 files) | `abd78a24…` |
| metadata | `… check-package-metadata.py` | 0 (18 pyproject) | `b755228d…` |
| whitespace | `git diff --check 91ac63ba..f1916747` | 0, empty | `e3b0c442…` |
| integrity-end | same helper, after final shared inspection | 0 PASS, identical to start | `f62cb573…` |

**Limits:**
- Fresh results: the five admin checks and the two integrity runs.
- Statically inspected only: product source and the installed chromadb source.
- Future obligations: all Gate-A model, counter and dependency work, all B/N/R tests, installed normal and `-O` lanes.
- Baseline debt from earlier runs (Ruff 534, `test_display` collection conflict 7196, formatting, MAINT oracle) remains failed and unwaived. I make no whole-repository-green claim and grant no runtime, acceptance, construction, Gate-A or delivery assurance.

## 12. Next gate

The controller should apply the narrow M1–M3 document corrections, plus advisories at its discretion, and dispatch fresh pass 3 of 4. Two passes remain, including that one.
