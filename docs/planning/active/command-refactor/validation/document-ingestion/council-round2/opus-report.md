# REM-CMD-INGEST-001 + TOOLS-DOC-001 — design council round 2, Opus seat

- **Seat:** opus · Anthropic `claude-opus-5-5` · high effort · fresh context, read-only
- **Outcome:** **CHANGES_REQUESTED**
- **Independent advisory score:** **8.4 / 10**. The controller's ≥9.5 target did not influence this score.
- **Candidate:** `2956b861de75fcf7ebf463c82f5f470cf6fa7b40` on `feature/cmd-ingest-001`
- **Correction base:** `4f9cb13a7a868ec28305a6fe6445007cd3727532` (15 changed paths, all documents/planning)
- **Request:** `review-request.json` SHA256 `3a113826…865455` (verified before reading); helper `check_integrity.py` SHA256 `6e1ec704…278c3` (verified before execution)
- **Authority:** none for construction, gate A, acceptance or delivery. A VERIFIED result would still not count as maintainer acceptance.

## 1. Summary

The correction is substantial and mostly sound. Every round-1 theme (CR-01..08) gets real design text, and most of that text matches current source. Specifically:
- The Chat character slicer is described correctly.
- Query/document role defects are described correctly: `ChromaVectorStore.query` falls back to `embed_documents`, the synthesizer uses `embed_query`, and the graph-scorer fallback uses `embed_query`.
- The strict `EmbeddingOptions(extra="forbid")` schema is described correctly.
- Smart_read's direct `ingested_file` storage and its `file_synthesis` memory cache are described correctly.
- ToolOutputIngester has no maintained caller, and the web tools have no Memory handoff. Both claims are accurate.

The four-format extraction contract, the Office structural audit, the parser contract, the local counting design, the cancellation/admission design and the gate-A effects envelope are coherent and safely bounded.

Two design gaps remain, and both can be seen in source today:

1. **The fresh-store-only identity admission has no defined behavior for existing installations, and no maintainer decision covers that.** The maintainer decided on fresh stores for *testing*. The REM extends this to production: all vector reads/writes on a `legacy-unbound` root are refused. Every current Chat install uses `.friday/vector`, which will be unbound. The REM does not say what Chat/Runtime do at startup on such a root. It also does not say how a fresh root is "explicitly requested". It even partly contradicts itself, because "enable [the new preparation] only with the new bound fresh-store path" implies a legacy mode still exists.
2. **The "complete" inventory of vector openers and embedding constructors misses real composition roots and a raw-vector writer.** The REM rules require a sidecar check before any Chroma client is constructed, admission on every vector read/write, and a capability-guarded embedding boundary for *all callers*. Several existing paths fall under those rules but are neither in the allowlist nor classified:
   - Memory `maintenance/recovery.py` opens `chromadb.PersistentClient` directly and deletes/repopulates raw vectors on restore.
   - `friday-runtime/di.py` (RuntimeKernel) builds pool and non-pool `LiteLLMEmbeddingService` instances plus a `CollectionManager`.
   - `friday-core/profiles.create_vector_store` and `friday-cli/container.py` construct stores and embedding services.

   The REM also explicitly excludes "recovery" changes.

Neither gap is a demand for implementation proof. Both are boundary decisions the maintainer should make before gate A. The current stop-and-reconcile clause would hit them at gate A, but the design already claims to have closed these inventory themes.

## 2. Mandatory findings

### M-1 — Legacy-unbound runtime consequence and the fresh-root request mechanism are undecided (IR-15, IR-R02, IR-16)

**Evidence**
- REM §E "Durable store identity" (lines 701–720) has three relevant rules:
  - An existing unbound root "is `legacy-unbound` and refuses this stack's vector reads/writes".
  - "Only an explicitly requested fresh root may be created/bound."
  - Identity is validated "at create, reopen and every vector read/write, including lifecycle and maintenance operations".
- REM lines 735–740 say "Enable that verified convention only with the new bound fresh-store path". That implies a legacy path keeps running somehow. Line 576 contradicts this ("no silent unguarded mode").
- The maintainer's decision in `discussion-decisions.json` is `"test_store": "fresh/disposable; no legacy migration/re-embedding"` and "Fresh test stores". That decision is about testing. It does not decide production behavior on existing stores.
- In source, the packaged `config_templates/config.example.yaml:236` sets `persist_directory: .friday/vector`. Chat builds `CollectionManager(path=maintenance_layout.vector_directory)` (`adapters.py:1771–1799`). Every existing user store is therefore legacy-unbound.
- The Chat allowlist row says "preserve existing store paths" (REM line 803). The REM never says whether Chat, at startup on that preserved path, does any of the following:
  - fails fast,
  - runs with memory disabled,
  - refuses each recall, turn-store or maintenance operation,
  - keeps a legacy unguarded mode.

  It also never defines the request mechanism (config key, CLI, new path) for a fresh root.
- DI-21 tests only fresh/mismatch/refusal mechanics, not this behavior.

**Why mandatory:** As written, a faithful implementation would make recall, turn storage, compaction and maintenance stop working for every existing installation unless the user reconfigures manually. That is a product decision the maintainer has not made, and it is not a gate-A readiness fact. No stop condition covers it, because the text already presents it as settled design.

**Narrow mitigation (document only):**
- Record an explicit maintainer decision on legacy-root runtime behavior. Options:
  - (a) Refuse with a single actionable startup/readiness diagnostic, while non-memory chat continues.
  - (b) Keep a clearly labelled legacy mode with legacy raw preparation, no new guard claims, and no INGEST writes.
  - (c) Change the packaged default to a new path.
- Define the fresh-root request mechanism and its configuration surface.
- Remove the "only with the new bound path" ambiguity.
- State the `/read`, `/ingest`, recall and maintenance outcomes on each root state: fresh, bound-match, bound-mismatch, legacy-unbound, pending/malformed.

**Testing impact:** Extend DI-21/DI-22 with a root-state × operation matrix through actual Chat/Runtime composition, using a disposable pre-populated unbound root. Prove the decided outcome, prove that store bytes/mtime are unchanged on refusal, and prove that no implicit binding happens.

### M-2 — Exact affected paths omit real vector openers and embedding constructors that the REM's own rules govern (IR-08, IR-R02, IR-R03, IR-R04)

**Evidence**

- **Raw-vector restore bypasses admission.** In Memory `maintenance/recovery.py`:
  - `_open_client` (lines 411–412) is a bare `chromadb.PersistentClient(path=vector_directory)`.
  - `_discover_vector` (line 631) and `_export_vector_snapshot` (line 583) open the live directory.
  - `_restore_vector_snapshot` (lines 1499–1512) deletes every live collection and repopulates raw float vectors from `chroma-logical.json`. There is no embedding-space identity anywhere in the snapshot or restore path.
  - So a snapshot taken under another identity, or before INGEST, can be restored under a bound sidecar. That is exactly the vector mixing REM §E forbids.
  - The REM requires "Check it before constructing a Chroma client that might mutate its directory" and admission on "every vector read/write, including … maintenance operations".
  - Yet `recovery.py` and `recovery_models.py` are not in the allowlist, and REM line 797 explicitly excludes "recovery … redesign".
  - The user's `.friday-old/backups/*/memory/chroma-logical.json` shows this path is in real use.
  - The REM also does not say whether the sidecar belongs to the snapshot/layout fingerprint (`recovery.py:213–228`).
- **The headless composition roots are unaddressed.**
  - `friday-runtime/src/friday_runtime/di.py` builds pool (`from_spec`, 203–207) and non-pool (`LiteLLMEmbeddingService(...)`, 218–231) embedding services, `create_vector_store` (250) and `CollectionManager(path=chroma_path)` (292–297).
  - `friday-core/src/friday_core/profiles.py:56–86` (public, root-exported `create_vector_store`) lazily constructs `ChromaVectorStore` and `SimpleVectorStore`.
  - `friday-cli/src/friday_cli/container.py` constructs `LiteLLMEmbeddingService`.
  - The REM places the guard "at the shared LLM embedding boundary … for all callers" and makes capabilities "required for any embedding operation in this guarded stack". But it names only "Legacy non-catalog **Chat and maintenance** constructors" (line 578).
  - AGENTS.md names RuntimeKernel as the preferred headless assembly layer. The REM's ownership table has no `friday-runtime` row.
  - The "public Memory factory" for headless clients (lines 103–109) therefore has no stated relationship to the existing Runtime/Core factories.

**Why mandatory:** These are the same CR-03/CR-04 themes ("all callers", "explicit exact affected paths", "non-pool constructors") that the correction claims to have addressed. The REM asserts that its all-caller inventory is complete (lines 648–658), and source shows it is not. The recovery restore is a concrete bypass of the new identity invariant inside an explicitly excluded area, so the text currently contradicts itself. The generic stop-and-reconcile clause would make gate A halt on knowable facts instead of a decided boundary.

**Narrow mitigation (document only):**
- **Recovery:** choose one, and add the exact paths and the exception to the exclusion.
  - (a) Narrow identity propagation: the snapshot manifest records the canonical identity digest, restore refuses a mismatched or unbound snapshot into a bound root (and the reverse), and the sidecar is part of the layout fingerprint.
  - (b) Recovery operations refuse on bound roots until a named follow-up.
- **Runtime/Core/CLI:** classify each as in scope (add exact paths), refused-by-design (state the user-visible refusal and add regression proof), or explicitly unguarded-out-of-scope (then narrow the "all callers" claim). Name RuntimeKernel's relationship to the new Memory factory.

**Testing impact:** Add DI-21/DI-22 rows for:
- cross-identity snapshot restore refusal with zero live-store mutation;
- snapshot/restore round-trip preserving the binding;
- Runtime pool and non-pool embedding preflight under the decided classification;
- `create_vector_store` on unbound, bound and ephemeral roots.

## 3. Advisory findings

- **A-1 (IR-13, IR-R08) — smart_read storage is not wired in maintained composition, and the REM does not say so.** Chat builds `SmartFileReadTool` without `memory_controller` (`adapters.py:2364–2378`; packaged config lines 568–569), and Runtime never builds it.
  - As a result, `store_to_memory=true` is a silent no-op in Chat today, and the memory-cache lookup never runs.
  - Label the smart_read row *public, not wired in Chat/Runtime*.
  - State whether Chat will inject the new entry. Injecting it would newly activate storage, which conflicts with the companion's "do not turn on previously disabled storage".
  - List the intentional oracle change that storage requests without an entry now "fail actionably" instead of silently doing nothing.
- **A-2 (IR-08, IR-R01) — existing reverse import edges are not acknowledged.**
  - Memory `large_file_processor.py:525` lazily imports `friday_tools.filesystem.code_chunker`, and code `raw_chunk` records come from it today.
  - Tools `friday_tools/memory/{maintenance,inspection,lifecycle}.py` import `friday_memory` at module level, but `friday-tools/pyproject.toml` declares no Memory dependency.
  - REM line 99 ("no Docling/Tools imports") and the "no new" wording should say that the code chunker may drive only summarization windows. They should also say that code raw_chunk text changes to the shared plan, and record that as an oracle change.
- **A-3 (IR-07, IR-R05) — table context for CSV/TSV.** The Memory text segmenter treats CSV/TSV as opaque spans grouped by blank lines. A large CSV usually has no blank lines, so it becomes one block, recursive line splits follow, and later chunks lose the header row. That conflicts with the general rule "Large tables retain row/header context across chunks". Either specify header carry for delimited text or explicitly declare it unsupported for non-Docling tables.
- **A-4 (IR-09, IR-R04, IR-11) — hosted/non-artifact embedding models.** The non-pool Chat and Runtime default is `text-embedding-3-small` (`adapters.py:1748`).
  - Hosted models have no artifact digest or revision for the canonical identity.
  - Offline local counting would need provisioned tiktoken BPE assets, because tiktoken downloads them on first use.
  - State the hosted-provider identity rule, or mark hosted embeddings as an explicit readiness stop. Then the user-visible effect becomes a decision rather than something gate A discovers.
- **A-5 (IR-15) — governance wording.**
  - In `authority.json`, top-level `active_council_roster.record` still points to `council-round1/roster.json`, while `document_ingestion_remediation.council.roster` points to round 2.
  - The maintainer's format-expansion premise ("assume we're already capable of text and web ingestion … through our tool chain") turned out false. The REM handles this honestly by giving no route credit. "Next decision" should still ask the maintainer whether a web→Memory route is wanted as separate scope.
- **A-6 (IR-R02) — sidecar location and graph refusal semantics.**
  - Name the exact "root": the vector directory or the `.friday` memory root. `graph_path` lives outside the vector directory.
  - Define what "unknown existing vector provenance refuses use" means at recall time for legacy `graph.json` edge vectors: is the vector skipped with a warning, scored via the on-demand document role, or does the operation fail?
- **A-7 (IR-R03) — dead lifecycle paths.** Classify `lifecycle/migration.py` explicitly as public-not-wired or broken. It holds a bare `query_embedding=[0.0]*768` search fallback (line 423) and calls a non-existent `CollectionManager.add_to_long_term` (line 591). Chat `/migrate` is a stub (`adapters.py:1127–1139`). That prevents accidental integration credit or a guard-bypass oversight.
- **A-8 (IR-06) — parser precision.** Say explicitly that "missing `=`" applies only to the exact override names, so `--chunking fixed` is a usage error, while lookalikes such as `--chunkingX=…` and `--chunk=…` remain description. DI-05 already tests lookalikes.

## 4. Criterion matrix (all 24)

| ID | Result | Basis |
| --- | --- | --- |
| IR-01 | PASS | Maintainer decisions, roster, iteration authority, branch/candidate identity and the proposal-vs-construction/MAINT separation are consistent across REM, board, authority fields and handoff. |
| IR-02 | PASS | Four-format allowlist, extraction-before-storage, complete-vs-declared coverage, and refusal of partial/empty/diagnostic content are explicit (§B). |
| IR-03 | PASS | PDF native/OCR/order/page count; DOCX interleaving; trustworthy omissions with gate-A characterization. |
| IR-04 | PASS | Visible sheets, saved formula cache with missing/error refusal, merged/type rules, no recalculation, no silent caps; structural audit maps the facts. |
| IR-05 | PASS | Slides/notes/hidden/native tables, declared visual omissions, no media fetch or false success. |
| IR-06 | PASS (A-8) | Raw-tail quoting, reserved overrides, literal `--`, `/read` refusal, custom-handler scoping, API54 unchanged; legacy malformed `--lines` characterized and deferred (FU-012). |
| IR-07 | PASS (A-3) | All-source document/512, precedence, three strategies, overlap/budget semantics coherent. |
| IR-08 | PARTIAL (M-2, A-2) | The Core entry protocol avoids a *new* cycle, but existing reverse edges and the Runtime/Core-profile composition roots are not placed in the boundary. |
| IR-09 | PASS (A-4) | Catalog fields, artifact identity, effective min capacity including serving ceilings; Qwen illustrative only. |
| IR-10 | PASS | Role preparation, overhead counting, cardinality/dimension/finite/index validation, reject/no-truncate, whole-batch preflight. |
| IR-11 | PASS | Certifi floor with lock and post-install origin/version proof plus negative control; manifest-owned asset root; offline behavior; proof boundaries clear. |
| IR-12 | PASS | Resource/ZIP/member/cell limits, encryption/malformed refusal, cancellation and side-effect limits; no sandbox overclaim. |
| IR-13 | PARTIAL (A-1) | Cache identity and raw/derived split are well specified; smart_read's real wiring state is not stated. |
| IR-14 | PARTIAL (M-1, M-2) | DI-01..26 and TD-01..10 are meaningful and include call-phase witnesses. They lack root-state, recovery and Runtime-composition proofs. |
| IR-15 | PARTIAL (M-1, A-5) | No hidden migration/reset/cleanup and status is truthful, but the fresh-store decision is extended from testing to production behavior without a maintainer decision. |
| IR-16 | PARTIAL (M-1) | Gate-A envelope and stop conditions are coherent; the legacy-root behavior is a design decision wrongly left implicit, not gate-A evidence. |
| IR-R01 | PASS (A-1, A-2) | Explicit injected Core entry and Memory factory, raw plan vs derived records, sequencing between INGEST and companion. |
| IR-R02 | PARTIAL (M-1, M-2) | Strong single-authority sidecar, pending/ready markers, same-dimension refusal, graph envelope, no backfill. The recovery bypass and legacy-root consequence are undefined. |
| IR-R03 | PARTIAL (M-2, A-7) | Memory/Chat roles are accurate against source; Runtime/CLI/Core profile callers and recovery are missing. |
| IR-R04 | PARTIAL (M-2, A-4) | Parse-optional/operation-required design is sound; the non-pool constructor clause names only Chat/maintenance, while Runtime has one too. |
| IR-R05 | PASS (A-3) | Memory-owned non-Docling segmenter, no Docling extra needed, missing extras affect only the four formats, no hidden fallback. |
| IR-R06 | PASS | Synchronous local counting from the manifest root, server parity as a cross-check, effective serving limit, worker thread with held admission and late-result discard, no hard-kill claim. |
| IR-R07 | PASS | Non-text audit supplies no text, mapping/warning allowlist refuses on unknowns, Docling is the sole text supplier, release proof stays in gate A. |
| IR-R08 | PARTIAL (A-1) | Web and ToolOutputIngester classifications match source, with no activation. Smart_read's non-wired state is not labelled. |

## 5. Disposition of correction-brief requirements (independent judgment)

| Theme | Disposition |
| --- | --- |
| CR-01 shared entry, cache identity, sequencing | Addressed. Residual: A-1, A-2. |
| CR-02 durable identity, legacy admission | Mechanism addressed. Residual: M-1 (runtime consequence) and M-2 (recovery bypass). |
| CR-03 role inventory | Memory/Chat roles verified correct against source. Incomplete for Runtime/CLI/Core profile and recovery (M-2). |
| CR-04 capacity fields, legacy constructors | Parsing vs operation split addressed. Non-pool Runtime constructor omitted (M-2); hosted identity open (A-4). |
| CR-05 non-Docling strategy | Addressed. Advisory A-3. |
| CR-06 local tokenization, nonblocking | Addressed. |
| CR-07 Office structural admission | Addressed. |
| CR-08 actual routes | Web and ToolOutputIngester addressed truthfully. Smart_read wiring state unlabelled (A-1). |
| SOL-003, ASTRA-002, ASTRA-003, OPUS-A01..A07 | All reflected in text (direct adapter query role, index validation, reserved tokens and literal `--`, worker/admission/late discard, format sniffing and ZIP refusal, effective per-input limit, `--lines` characterization, effects envelope, roster disclosure). |

## 6. Rubric

| Area | Weight | Score | Note |
| --- | ---: | ---: | --- |
| Scope, authority and boundedness | 1.5 | 1.35 | Governance clean. Production use of a testing-only decision (M-1). |
| Shared architecture and integration | 2.0 | 1.50 | Entry/factory design good. Runtime/Core/CLI and recovery not placed (M-2); reverse edges (A-2). |
| Format extraction and coverage | 2.0 | 1.85 | Thorough; gate-A proofs are well bounded. |
| Chunking, embedding and data safety | 3.0 | 2.35 | Strong guard and identity design; legacy-root consequence and recovery bypass. |
| Verification, reproducibility and reporting | 1.5 | 1.35 | Rich DI/TD set; missing root-state, recovery and Runtime rows. |
| **Total** | **10.0** | **8.40** | |

## 7. Commands and exits (all through the wrapper unless noted)

The wrapper is `OWN_SCRATCH/run.sh` (SHA256 `4fab3180c3d717d8a4cfb9a9ab3c84da0eeee5b6819afe702ac102052dcaa767`). It does the following:
- exports `GIT_OPTIONAL_LOCKS=0` and `PYTHONDONTWRITEBYTECODE=1`;
- sets `PYTHONPYCACHEPREFIX`, `UV_CACHE_DIR` and `XDG_*` to directories inside my own scratch;
- sets `UV_OFFLINE=1`, `UV_FROZEN=1`, `UV_NO_SYNC=1` and `UV_PYTHON_DOWNLOADS=never`;
- sets `RUFF_CACHE_DIR` and `MYPY_CACHE_DIR` into my scratch, and `GIT_PAGER=cat`;
- changes to the workdir, then `exec "$@"`.

| Check | Command | Exit |
| --- | --- | --- |
| request/helper hash | `shasum -a 256 review-request.json check_integrity.py` (no git) | 0, both match |
| integrity-start | `run.sh python3 -B check_integrity.py review-request.json > out/start-integrity.json` | 0, PASS, 17561 protected, no failures |
| correction diff | `run.sh git diff --stat / git diff 4f9cb13a..2956b861 -- <explicit changed paths>`; REM delta saved to `out/rem-delta.diff` | 0 |
| changed names | `run.sh git diff --name-only 4f9cb13a..2956b861` | 0 (15 paths, all planning) |
| board | `run.sh uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` | 0 — "passed: 36 tasks" |
| dashboard | same prefix `… render --check` | 0 — "Planning dashboard is current" |
| docs | same prefix `scripts/check-documentation-lifecycle.py` | 0 — "982 Markdown files checked" |
| metadata | same prefix `scripts/check-package-metadata.py` | 0 — "Validated 18 pyproject.toml files" |
| whitespace | `run.sh git diff --check 4f9cb13a..2956b861` | 0, empty output |
| authority fields | `run.sh python3 -I` extracting only `branch`, `current_scope`, `product_code_authority`, `active_council_roster`, `document_ingestion_remediation` | 0 |
| integrity-end | `run.sh python3 -B check_integrity.py … > out/end-integrity.json` | 0, PASS, no failures |
| post-deviation recheck | same into `out/post-deviation-integrity.json` | 0, PASS |

Source inspection used read-only `grep`, `sed` and `cat` on the pinned source files and on extra non-pinned source: `recovery.py`, `runtime/di.py`, `core/profiles.py`, `lifecycle/migration.py`, `smart_read.py`, `large_file_processor.py` and `friday_tools/memory/*`. These ran without Git and without writes.

## 8. Reproduced vs inspected

- **Reproduced:** integrity start and end, the four admin checks, the whitespace check, and the delta file list.
- **Inspected (source, not executed):** every source claim in §1–§3, with file:line evidence.
- **Not executed, by design:** product tests, installs, Docling/model/counter readiness, provider calls, store reads.
- **Public references:** cited by the REM (Docling, Nomic, Qwen, LM Studio, certifi advisory/PyPI). I did not fetch them this session. The conclusions above do not depend on facts that would need fetching. In particular, the Nomic task-prefix convention and Docling's `allowed_formats`, `ConversionStatus` and HybridChunker tokenizer interface are consistent with my prior knowledge, which counts as background, not proof.

## 9. Baseline limits acknowledged

- Gate-A readiness (Docling/OCR/counter/model) is intentionally pending.
- Current `/ingest` character slicing (`adapters.py:2793`), missing LLM limit/dimension/index guards (`embeddings.py:353–381` ignores `index`), and placeholder document reading (`files.py:122–131`) are pre-remediation gaps, not claims of fixes.
- Historical failures I did not rerun: Ruff 534, `test_display` collision 7196, seven legacy format failures, MAINT Chat 1413/15.
- MAINT UAT/acceptance and the broader TUI work are separate.

## 10. Isolation and Git-environment audit

- Every output, cache and report is under my own new scratch: `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/d6a9e142-7bff-4a3b-a599-5bd5e27fe34d/scratchpad/opus-ingest-r2-kIJhP3/`.
- Supplied inputs: listed and hashed only. The listing is unchanged (4 files, same sizes and mtimes).
- Repository writes: none by me. `scripts/__pycache__/*.pyc` timestamps (Aug–Oct 2026) predate this session. No builder scripts or receipt argv were replayed. No nested agents. No peer reports or prior council report text were opened.
- **Disclosed deviation:** after integrity-end, one exploratory read-only command, `git -c core.fsmonitor=false check-ignore -q docker-bench-security`, ran in a plain shell **without** the wrapper, so without `GIT_OPTIONAL_LOCKS=0` / `PYTHONDONTWRITEBYTECODE=1` exported. `check-ignore` neither refreshes the index nor takes locks, and `.git/index` mtime stayed at 16:49:47 (before the session). I reran the immutable helper afterwards through the wrapper: PASS, no failures. I am disclosing this rather than certifying the run clean.
- **Observed but not attributable to me:**
  - `.git/FETCH_HEAD` was modified at 16:54:19. I ran no fetch.
  - The `.git/` and `docker-bench-security/.git` directory mtimes changed at 16:57:21. This matches the external Git metadata/T3 checkpoint activity the request permits.
  - Logical index SHA `587b8099…ebe3`, HEAD, branch, porcelain status, pins, 17561 protected entries and six preserved metadata records matched at start, at end and after the deviation.
- **Harness-owned output:** one large tool output (the pretty-printed request) was saved automatically by the harness under `~/.claude/projects/…/tool-results/`. That is outside the repository and the supplied inputs. I am noting it for completeness.

## 11. Integrity

| Run | Outcome | Logical index | Protected | Failures |
| --- | --- | --- | --- | --- |
| start | PASS | `587b8099a2c6a1be5adc8bfe021bbc9cd6c6ebdcbf54a78d543d57007125ebe3` | 17561 | [] |
| end | PASS | same | 17561 | [] |
| post-deviation | PASS | same | 17561 | [] |
