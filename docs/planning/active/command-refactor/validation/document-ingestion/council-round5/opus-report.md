# REM-CMD-INGEST-001 — round5 framework-wide embedding compatibility review (Opus seat)

**Verdict: CHANGES_REQUESTED**
**Advisory score: 7.2 / 10** (design readiness only; not implementation conformance or runtime assurance)

Seat: opus · model `claude-opus-5-5` · effort high · fresh context, single pass, read-only, no subagents/delegation, no peer verdicts or prior raw council reports consulted.

## 1. Candidate, authority and independence

| Item | Value |
| --- | --- |
| Request | `.../inputs/review-request.json`, SHA256 `e463c4e849957eb920e4260c10d408217498f6afb787da474c301a546e33c35c` (verified before review) |
| Integrity helper | SHA256 `2d383c058aec2af50f4b0c6d6b27909b7b57995755a89f3af6bcb2857eceb38a` (verified, inspected: read-only hashing/stat/git queries) |
| Command wrapper | SHA256 `cb0669f81efd0098c104d7b96342fcd614255021ea2bfa49cbbb6af7c2fea248` (verified, inspected: git allowlist, locks off, bytecode off, private caches) |
| Candidate / branch | `06f294d779c5bc9ea3016eaffdf8efb349979ce4` on `feature/cmd-ingest-001` |
| REM | `docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md`, SHA256 `2bbf54c8…6dea` (pinned; integrity PASS) |
| Amendment record | `validation/document-ingestion/embedding-pool-compatibility.json` (`3f17db1c…`) |
| Round authority | `council-round5/scope.md`, `roster.json` (opus seat listed); `authority.json` read only for `branch`, `current_scope`, `product_code_authority`, `active_council_roster`, `document_ingestion_remediation.current_revision` |
| Current revision controls | `prior_review_applies: false`, `new_council_active: true`, `gate_a_or_construction_authority: false` |
| Scratch | `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/b009693c-10b7-4a28-84c2-970a0e25d393/scratchpad/opus-r5-1794359781` (outside repo and input root) |

The amendment REM delta (`c28e6f8b..06f294d7`, technical paths only) was read first: it replaces the old "absent fields refuse" rule with "omitted YAML fields may resolve from qualified artifact-bound readiness; missing baseline qualification is a gate-A stop", adds §E "Existing pool and subsystem compatibility" (REM:645-691), extends gate-A item 6 to conversation extraction/compaction/graph scoring (REM:227-230), rewrites DI-18 and adds DI-33. The 82c3a05a..06f294d7 range does not touch the REM.

## 2. Commands and exits (all Git/admin through the wrapper)

| # | Command (argv, abbreviated) | Exit |
| --- | --- | --- |
| 0 | First batch of required checks: zsh did not word-split a scalar variable, so the shell reported "no such file or directory: python3 -B …" | 127 (nothing executed; no wrapper, uv or git process started) |
| 1 | wrapper → `python3 -B check_integrity.py review-request.json` (start) → `start-integrity.json` | 0, PASS, 17643 protected, 0 failures |
| 2 | wrapper → `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` | 0 ("36 tasks") |
| 3 | wrapper → same `… friday-dev-board.py render --check` | 0 ("dashboard is current") |
| 4 | wrapper → same `… check-documentation-lifecycle.py` | 0 (998 Markdown files) |
| 5 | wrapper → same `… check-package-metadata.py` | 0 (18 pyproject files) |
| 6 | wrapper → `git diff --check c28e6f8b..06f294d7` | 0 (no output) |
| 7 | wrapper → `git diff --stat` (technical paths, two ranges); `git log --oneline -6 -- REM` | 0, 0, 0 |
| 8 | wrapper → `git diff -U1 c28e6f8b..06f294d7 -- REM` → scratch | 0 |
| 9 | wrapper → `git ls-files packages/friday-tui` | 0 (no tracked files) |
| 10 | wrapper → `git show 06f294d7:…/config_templates/config.example.yaml` and `models-config.example.yaml` → scratch | 0, 0 |
| 11 | wrapper → `check_integrity.py` (end, after final shared inspection) → `end-integrity.json` | 0, PASS, 17643, 0 failures |

Exempt plain reads: `cat`/`sed`/`rg`/`awk`/Read of committed source, docs, test files and the committed compat fixture `packages/friday-chat/tests_chat/compat/fixtures/friday_py_config_sanitized.yaml`; `find packages/friday-tui -type f` (it listed only untracked `.pytest_cache` files). Nothing under `.friday-old/`, `exports/` or the two dirty example YAMLs was listed or read. No product import, test, build, install, model or provider call took place. No write was made to the shared checkout or the input directory. Audit log: `command-audit.jsonl` in scratch.

## 3. Independent framework-wide consumer inventory and dispositions

Legend for the route column: **A** = actively wired by maintained Chat/Runtime; **P** = public but unwired; **I** = inactive/stub/example; **—** = no embedding coupling. A **NEW** tag in the REM column means the consumer is not named, or is wrongly characterised, in the REM.

| # | Consumer (source) | Route | Embedding / vector coupling | REM coverage | Disposition |
| --- | --- | --- | --- | --- | --- |
| 1 | `friday_llm/embeddings.py` LiteLLMEmbeddingService (49-410) | A | Provider call, untyped LRU query cache keyed by md5(text) (184-214), no result validation (383) | Named (REM:1182, §E) | Covered by a narrow contract |
| 2 | `friday_llm/model_library.py` EmbeddingOptions/Spec/resolver (105-127, 237-312) | A | Strict schema; resolves every pool binding | Named | Covered |
| 3 | Core `interfaces/llm.py` EmbeddingModel; `interfaces/memory.py` query_embedding (174-185); `profiles.py` factories (56-117) | A | Protocol; bare-float precomputed vector | Named (REM:862-864, 1166) | Covered |
| 4 | Memory `adapters/vector.py` (84-91 clients; 99-109, 226 query→embed_documents; 146, 183 add/upsert) | A | Store and query role | Named | Covered |
| 5 | Memory `adapters/simple_vector.py` (109, 154) | A (Runtime EPHEMERAL/TESTING) | In-memory store | Named | Covered, but see M5 for profile composition |
| 6 | `retrieval/collection_manager.py` (115-175 three PersistentClients; 559/617/667 promotion/decay/reactivation re-embed; 481-503 MCP staging) | A | Document role on writes | Named, but MCP staging not | Partial; see M2 |
| 7 | `controller/memory_controller.py` recall (497-526 shared embed_query; gather `return_exceptions=True`), graph scoring (1586-1645, broad except), priming/fetch handlers (777, 811, 1038, 1193, 1318) | A | Query role; swallows exceptions into empty results | Named for role/admission; the swallow sites are not | **Gap, M4** |
| 8 | `retrieval/graph_scorer.py` cosine returns 0.0 on mismatch (36-37); sync path is the only one used by maintained recall (330-415, called at controller 1625); async on-demand fallback (221-325) | Sync A; async P | Silent zero; fallback has no maintained caller | Named, but REM:858-859, 1177 and DI-22 treat the fallback as live | **Gap, M4** |
| 9 | `context/extractor.py` edge embeddings (574-580); Chat wiring passes the default embedding (adapters 2065-2086); Runtime uses the optional `memory_extraction.embedding_service` (di.py 349-367) | A | Document role edge vectors into the graph | Named (REM:683) | Covered |
| 10 | `context/extraction_filter.py` `configure_rejection_logging` (32-55: `mkdir(parents)` plus eager `FileHandler`), called from the extractor constructor (211-212) at Chat startup (runtime.py 1457, adapters 1876/2065) and at Runtime boot | A | No embedding, but **creates files and directories inside the vector directory** for the packaged template (`config.example.yaml:71` vs `:236`) and the compat fixture (`friday_py_config_sanitized.yaml:29` vs `:197`) | **NEW** | **Gap, M1** |
| 11 | `context/assembler.py` recall → controller (500); `extract_context` fire-and-forget (413-418); consolidator `vector.query` (consolidator.py:460) | A | Indirect | Assembler pinned only | Through the controller/adapter: compatible if M4 holds |
| 12 | `maintenance/compactor.py` (510, 624 via CollectionManager) | A | Indirect write/promote | Named ("compaction") | Covered |
| 13 | `maintenance/pipeline.py` SYNTHESIZE/REEMBED (951, 1031-1036), preflight `probe()` (551-553) | A (MAINT coordinator) | Document role; real provider probe during preflight | Pipeline named; probe ordering not | Covered, **A4** |
| 14 | Chat `reorganization/mutation.py` maintenance embedding registry, pool and non-pool (157-160 probe, 263-303) | A | Separate maintenance binding | Named (REM:1188) | Covered, A4 |
| 15 | `maintenance/mutation.py` participant: stored-dimension inference (627-641), add/update checks (1278, 1308-1326), client writes (1442-1486) | A | Stored-vector comparison | Named | Covered, **A8** |
| 16 | `maintenance/recovery.py`, `recovery_models.py` (511-563 probes, 1333-1378 rebuild) | A | Vector snapshot/restore | Named (§ recovery) | Covered |
| 17 | `maintenance/pruner.py` (114 client; 150-196 stored-vector duplicate search; 621, 687 import ConsistencyAnalyzer) | Legacy, reached from reorganizer and `__main__` | Stored-vector comparison | Named as a direct opener | Covered for the client; see M3 for the analyzer it pulls in |
| 18 | `maintenance/synthesizer.py` (183 client with `[memory_dir, memory_dir/vector]` probe at 179; 714 embed_query; **697-740 swallows errors and returns None, then 780-795 `collection.add` without embeddings, so Chroma's built-in default EF does the embedding**) | Legacy | Hidden **third embedding model** (Chroma default) | Opener named; default-EF fallback not | **Gap, M3** |
| 19 | `maintenance/fact_checker.py` (140 client; 359 metadata update) | Legacy | Opener only | Named | Covered |
| 20 | `maintenance/reorganizer.py` (741-775 edge re-embed; 24/248/1179 analyzer; 148 BackupManager) | Legacy; Chat `adapters.reorganize`/`reorganize_memory` (784-835, 1037-1110) have no maintained caller, execute is disabled | Default (memory) binding | Pinned/allowed | Should be classified inactive (A-note in M3) |
| 21 | `maintenance/analyzer.py` ConsistencyAnalyzer (94-97, 124-186: raw `sqlite3.connect(chroma.sqlite3)` with `[memory_dir, memory_dir/vector]` probing; also opens transcript.db) | Legacy/public; module CLI `analyze` | Raw store open with fallback probing; bypasses admission | **NEW** (not in REM:241-244 or 920-929 lists) | **Gap, M3** |
| 22 | `maintenance/backup.py` BackupManager (53, 105-125, 137-156 copies `vector/**`; 273-325 restore copies everything back, including any future `embedding-space.json`) | Public; reorganizer backup_first; module CLI `backup`/`restore` | File-level restore bypasses admission and can overwrite a live sidecar | **NEW** | **Gap, M3** |
| 23 | `friday_memory/maintenance/__main__.py` (`python -m` CLI: backup/restore/list/analyze/prune/synthesize/verify; 348-509; synthesizer built **without** an embedding function at 445) | Public module entrypoint | Drives 17-22 directly | **NEW** | **Gap, M3** |
| 24 | `lifecycle/migration.py` (423 fixed 768-d dummy, 443) | I | — | Named (REM:136); accurate | Inactive, no credit |
| 25 | `ingestion/mcp.py` MCPMemoryIngester (34-190; broad except → `storage_failed` at 187), Chat `memory_mcp.py` (114, 162, 217), adapters 309-345, Core `mcp.py:121` `max_ingested_bytes=65536` | **A** (opt-in per server) | Auto tool-output → short-term memory → embed_documents | **NEW**; REM:32-33 says no maintained automatic tool ingestion exists | **Gap, M2** |
| 26 | `ingestion/tool_ingester.py`, `large_file_processor.py`; Tools `smart_read.py` (`store_to_memory` default False, 161-164; Chat constructs it without Memory, adapters 2364-2381) | P | Storage handoffs | Named; accurate | Covered |
| 27 | `ingestion/pipeline.py` DocumentIngestionPipeline / `chunker.py` SemanticChunker (root export at `friday_memory/__init__.py:47`) | P (tests only) | Legacy second chunker | Not named | **A11** |
| 28 | `multi_agent/controller.py` (57 recall, 95/145 store_fact) and `coordinator.py` (159-167), wired by Runtime `memory_mode=multi_agent` (di.py 303-333) | A (opt-in) | Indirect via controller | Not named; "namespace" term collides | Compatible through controller admission; **A6** |
| 29 | friday-agent built-ins `recall_memory`/`store_fact` (builtins.py 90-205), bound by Runtime di.py:385-397; agents consume `memory`/`context_engine` (base.py 494-520, kernel.py 405-440, 600-630) | A (Runtime) | Indirect recall/graph writes; extraction errors swallowed by `_safe_extract_context` | Not named; friday-agent not an allowed path | Compatible only if Runtime supplies a deferred capability; **A6** |
| 30 | Runtime `di.py` pool construction (195-243), storage (245-280, eager mkdir 248, 265), controller (282-300), extraction (343-372) | A | All | Named | Partial; **M5** for profiles |
| 31 | Runtime `kernel.py` `embeddings` property (291-294) | A | Re-export | Named indirectly | Covered if the type is preserved |
| 32 | CLI `container.py` (63-71 env defaults; 110-135 to RuntimeConfig; 220-224 embeddings) | A (compat) | Default model plus path-origin collapse | Named | Covered, **A5** |
| 33 | Chat `build_framework_embedding_service` (1735-1761) **ignores `embedding.embedding_service`** (config.py:467-470; template :233) and always uses `default_service` | A | Binding selection | Not named | **A1** |
| 34 | Chat MEMQ `/memory` stats/records/list-ingested (memory_queries.py 278-284, 556-560 unavailable projection) | A | Store-only reads | Not in the operation matrix | Compatible; **A7** |
| 35 | Chat `/reset` (adapters.reset_store 930-934 records only) | A (stub) | None | — | Unaffected |
| 36 | Telemetry: `llm_events.py` Outcome/ServiceRole (28-34, 173-176), `safe_llm.py` finish (187-225) | A | A pre-dispatch refusal is a valid `error` with 0 attempts | — | Compatible unchanged (A9) |
| 37 | `friday_llm/langfuse_integration.py`, `telemetry.py`, `pricing.py` | A (opt-in) | Callbacks see the prepared text | — | Compatible unchanged |
| 38 | Retrieval/consolidation thresholds: collection_manager 66-75 and 255-271, graph_scorer 70-75, template 241-242/274/312-313/394, `factor_computer` 89-101, pruner duplicate threshold | A | Model-calibrated constants | Not named | **A2** |
| 39 | `models/vector_metadata.py` (TypedDict total=False) | A | Metadata keys | — | Compatible unchanged |
| 40 | friday-mcp, speech, optimization, moltbook, finance, sandbox, transcript, commands | — | No memory/LLM/embedding imports (rg) | — | Unaffected (Commands remains stdlib-only per REM) |
| 41 | friday-tui | — | No tracked files at the candidate | — | Not maintained |
| 42 | `scripts/*`, `main.py` | — | No embedding consumers | — | Unaffected |

Test and fixture blast radius (static count): 12 test files construct `CollectionManager`, 11 construct `PersistentClient`, 4 construct `ChromaVectorStore`, 11 construct `RuntimeKernel`, plus MCP memory tests (`friday-chat/tests_chat/test_mcp_memory.py`, `friday-memory/tests_memory/test_mcp_memory.py`, `tests/integration/test_mcp_memory_ingestion.py`) and the compat config fixture. The REM's "guarded-store setup/admission" exception class (REM:1249-1258) plausibly covers the store and kernel setup changes. It does not name the MCP tests or the compat-fixture rejection-log behaviour.

## 4. Two-scenario compatibility matrix

S1 = unchanged existing pool/catalog and maintained non-pool configuration (new YAML fields omitted, qualified readiness assumed). S2 = explicit replacement model (changed dimension, or the same dimension with a different space or preparation) bound to an explicitly provisioned fresh vector/graph/WAL namespace.

| Consumer | S1 expectation per REM | S1 source-backed risk | S2 expectation per REM | S2 source-backed risk |
| --- | --- | --- | --- | --- |
| Pool resolution and service selection | Names, default, profile and resilience preserved; omitted fields come from the readiness record | Packaged revision is the placeholder `replace-with-exact-lm-studio-revision` (models template 88-96); the non-pool compat fixture has no revision. "Exact identity" keying is undefined (A3) | New profile plus explicit fields | Chat ignores `embedding.embedding_service` (A1); an operator may believe the switch happened while `default_service` still binds |
| Chat startup / `/read` | No Chroma, model or store I/O | **The extractor constructor creates `.friday/vector/extraction_rejections.log`** (M1), turning the explicit-absent default into "existing unbound", so CREATE_FRESH is refused permanently | New absent vector dir | A rejection log left at the old path keeps writing into the old legacy vector dir (mtime mutation, M1); a log placed under the new dir blocks CREATE_FRESH |
| Recall (Chat, Runtime, agents, multi-agent) | Typed refusal, never silent empty | `gather(return_exceptions=True)` and the graph `except` convert typed errors to empty payloads (M4) | Identity-enveloped graph vectors | Sync scorer gives missing vectors 0 silently; unknown-provenance refusal is swallowed (M4); model-calibrated thresholds unchanged (A2) |
| Extraction → graph/insight/summary | Existing bindings | Runtime extraction service may differ from the default; REM requires qualification (covered) | Same namespace identity | Covered by namespace admission |
| MCP snapshot memory | Not classified | A 64 KiB default bound can exceed the token capacity; the new guard refusal becomes `storage_failed` (M2); a role-prefix change is forbidden while the caller is unclassified | Same | Same, plus a dimension change is covered by admission |
| MAINT coordinator synthesis/reembed/verify | Maintenance binding kept | Preflight probe is a provider call; its ordering against admission is not specified (A4) | Fresh namespace | Empty collections plus a graph-only REEMBED is refused by the stored-dimension inference (A8) |
| Legacy maintenance (reorganizer, `python -m`, analyzer, backup, synthesizer) | Openers "use admission" | Analyzer raw sqlite and BackupManager file copies bypass admission; the synthesizer silently embeds with Chroma's default EF (M3) | Fresh namespace | BackupManager.restore can copy an old or foreign `embedding-space.json` over the live sidecar (M3) |
| Recovery v2 snapshot/restore | Same namespace only | Covered (DI-27, DI-32) | Same | Covered |
| Runtime profiles | Same factory | EPHEMERAL/TESTING use an in-memory vector store **plus a persistent CollectionManager** at `chroma_path` (M5) | Fresh or ephemeral identity | Contradicts REM:1140-1141 ("without touching a persistent namespace") (M5) |
| CLI container | Delegates | `chroma_path` origin is collapsed by the dataclass default (A5) | Same | Same |
| Telemetry / Langfuse / non-memory packages | Unchanged | None found | Unchanged | None found |

## 5. Acceptance criteria EC-01..18

| EC | Result | Basis |
| --- | --- | --- |
| EC-01 | PASS | Pins, integrity start/end PASS, read-only boundary, the fresh-namespace boundary is explicit (REM:1041-1110); the round5 authorization exists |
| EC-02 | **PARTIAL** | Strong named inventory, but MCP route, rejection-log side effect, analyzer/backup/`__main__`, Runtime profile composition and agent/multi-agent consumers are absent (M1-M3, M5, A6) |
| EC-03 | PARTIAL | Pool, default and resilience preservation is specified (REM:652-660); the existing Chat `embedding.embedding_service` silent default is not recorded (A1) |
| EC-04 | **PARTIAL** | Query-envelope extension and its call sites are declared (REM:860-864); the MCP consumer and the recall swallow sites are unclassified (M2, M4) |
| EC-05 | PARTIAL | Readiness-record rule and stop are correct (REM:623-643); identity keying for placeholder/absent revisions and the runtime source of "current identity" are undefined (A3) |
| EC-06 | PARTIAL | LLM/Memory ownership is correct (REM:666-668); the MCP caller is unclassified, so by REM:233-234/777 asymmetric enablement stays blocked (M2) |
| EC-07 | **PARTIAL** | Envelope rule is right; the maintained sync scorer, the dead async fallback and the swallow sites are not addressed (M4) |
| EC-08 | PASS | Extraction LLM is separated from embedding; Runtime optional extraction service qualified separately (REM:683); Chat re-queues on failure (adapters 1150-1185) |
| EC-09 | **PARTIAL** | Maintained MAINT path is covered; legacy synthesizer default EF, BackupManager restore and analyzer are uncovered (M3) |
| EC-10 | PARTIAL | Lifecycle and compaction are covered and 512 is limited to ingestion (REM:669-671); MCP tool storage is unclassified (M2) |
| EC-11 | **PARTIAL** | Lazy startup design is good (REM:908-919); the extractor rejection-log startup side effect and Runtime profile/agent wiring are unclassified (M1, M5, A6) |
| EC-12 | PARTIAL | Vector/graph/WAL freshness is explicit (REM:1087-1096); an extra state file inside the vector dir, sidecar-overwriting legacy restore and threshold disclosure are missing (M1, M3, A2) |
| EC-13 | PASS | Separate names and timeouts may share a space; unused-service isolation (REM:640-641); independent namespaces allowed (REM:663-665) |
| EC-14 | **PARTIAL** | Boundary guard and index validation are excellent (REM:781-812); recall, MCP and legacy-synthesizer swallowing loopholes remain (M2-M4) |
| EC-15 | PARTIAL | DI-18 and DI-21-33 are thorough; witnesses for the new findings are missing (listed per finding) |
| EC-16 | **PARTIAL** | Newly found consumers lack an explicit narrow allowed purpose or a declared exception (M1-M5) |
| EC-17 | PASS (advisory A10) | Certifi floor, extras and Docling isolation are coherent with framework compatibility; counter-dependency placement is correctly deferred to gate A |
| EC-18 | PASS | Current state and pins are coherent; historical round scores are present only as status context and are not used as evidence |

## 6. Findings

### Mandatory

**OPUS-M1 — Extraction rejection logging creates state inside the vector directory at startup (unlisted consumer; breaks CREATE_FRESH and legacy-root preservation).**
Source: `friday_memory/context/extraction_filter.py:32-55` (`log_path.parent.mkdir(parents=True)` plus an eager `logging.FileHandler`), called from `MemoryExtractor.__init__` (`context/extractor.py:211-212`). Chat constructs the extractor during application assembly (`friday_chat/runtime.py:1457` → `adapters.py:1876, 2065-2086`, `rejection_log_path=config.extraction.rejection_log`); Runtime does the same in `di.py:358-370`. The packaged template sets `extraction.rejection_log: .friday/vector/extraction_rejections.log` (`config_templates/config.example.yaml:71`) inside `memory.persist_directory: .friday/vector` (`:236`). The compat fixture does the same (`tests_chat/compat/fixtures/friday_py_config_sanitized.yaml:29, 197`).
Failure scenario: on a first run with the explicit `.friday/vector` (absent), startup creates the directory plus a log file before any memory operation, so the REM matrix row "existing directory without marker" (REM:1130) refuses forever. With a new `persist_directory`, the old configured log path keeps mutating the legacy vector directory, contrary to REM:1145-1149.
REM gap: the lazy boundary (REM:908-912), fresh preconditions (REM:1087-1092) and DI-29 name only vector, graph and WAL.
Mitigation: classify extractor construction and rejection logging as a Memory-dependent component deferred behind the capability (Chat `adapters.py` and Runtime `di.py` are already allowed paths), or make the handler lazy with an explicit allowed purpose for `extraction_filter.py`. Add "configured rejection log resolving inside the selected vector directory" to the readiness diagnostics, with no user YAML rewrite. The template's own value may change only under the existing template allowance.
Required proof: DI-29 witnesses for the packaged template and the compat fixture. Startup and `/read` must create no `vector/` entry. CREATE_FRESH must succeed on first memory use. A legacy-unbound root's bytes and mtime/ctime, including its parent directory, must stay unchanged with the log configured inside it.

**OPUS-M2 — The active MCP tool-output → Memory route is unclassified.**
Source: `friday_chat/memory_mcp.py:114, 162, 217` → `adapters.py:56, 309-345` → `friday_memory/ingestion/mcp.py:34-190` → `retrieval/collection_manager.py:481-503` (`add_to_short_term` → `embed_documents`). Default `max_ingested_bytes=65536` (`friday_core/mcp.py:121`); a broad `except Exception` maps failures to `storage_failed` (`ingestion/mcp.py:187`).
REM gap: REM:32-33 states that no maintained automatic tool ingestion exists. The route table (REM:127-136), §D all-source scope (REM:514-520), the §E consumer table (REM:681-688) and DI-19/22/33 omit MCP snapshots. By the REM's own rule (REM:233-234, 777), asymmetric Nomic preparation cannot be enabled while this caller is unclassified. A 64 KiB snapshot can exceed the effective token limit, so the new guard turns a currently "prepared" outcome into `storage_failed` under S1. That is a new failure mode in an unlisted subsystem. Applying document/512 chunking would break the exact single-record receipt, publish and discard protocol.
Mitigation: add a route-table and trace row: "MCP snapshot memory, active, opt-in per server; a single exact record; document role; **not** document-chunked; unsplit guard; over-capacity maps to the existing `oversized` (or a typed) outcome, never success". Either add a narrow allowed purpose for `ingestion/mcp.py` (outcome mapping only) or declare it unchanged with the observed oracle delta.
Required proof: role-spy (DI-22), S1/S2 positive (DI-33), an over-capacity negative with zero provider I/O, and the existing MCP memory test oracles kept unchanged or listed as exact exceptions.

**OPUS-M3 — Legacy and public raw-store surfaces omitted from the "all direct openers" inventory: identity-overwrite and hidden-model paths.**
Source:
- `maintenance/analyzer.py:94-97, 124-186`: raw `sqlite3.connect` on `chroma.sqlite3` with `[memory_dir, memory_dir/vector]` probing. Pulled in by the pruner (621, 687) and reorganizer (24, 1179).
- `maintenance/backup.py:53, 105-156, 273-325`: copies `vector/**` and restores every file, which would include `embedding-space.json`.
- `maintenance/synthesizer.py:697-740, 780-795`: embedding errors become None, then `collection.add` without embeddings, so Chroma's default embedding function does the work.
- `maintenance/__main__.py:348-509`: `python -m friday_memory.maintenance`; the synthesizer is built with no embedding function at 445.
- Chat `adapters.reorganize`/`reorganize_memory` (784-835, 1037-1110): no maintained caller.
REM gap: REM:241-244 and REM:920-929 enumerate the direct openers as recovery, mutation, pruner, synthesizer and fact checker, which misses the analyzer and BackupManager. REM:949 ("restore must never copy a snapshot identity over an unrelated live sidecar") can be bypassed by `BackupManager.restore_backup`. Chroma's built-in embedding function is an unnamed embedding model writing into a bound namespace.
Mitigation:
- Classify each surface (public-unwired legacy, module entrypoint, inactive Chat hooks).
- Require that, when an `embedding-space.json` or pending marker is present, the analyzer, BackupManager create/restore, legacy synthesizer/pruner/fact checker and `__main__` subcommands refuse or route through the admission helper. A narrow refusal is enough; no redesign.
- Require that the synthesizer refuse instead of omitting embeddings.
- Add these paths to the allowed-path table with "refusal only" purpose, or record an explicit maintainer-approved exclusion.
Required proof: DI-28 additions. The analyzer opens no SQLite file and creates no `-wal`/`-shm` under an unbound or mismatched root. BackupManager restore refuses to write over a live sidecar. A no-embedding-function synthesize run writes nothing. A `python -m` mutant is caught.

**OPUS-M4 — Recall error swallowing and graph-path reality contradict the typed-refusal guarantee.**
Source:
- `controller/memory_controller.py:497-526`: `asyncio.gather(..., return_exceptions=True)` maps vector and graph exceptions to `[]`/`{}`.
- `memory_controller.py:1594-1645`: broad `except` around graph scoring.
- `memory_controller.py:777, 811, 1038, 1193, 1318`: priming and fetch handlers.
- Maintained scoring uses only `graph_scorer.filter_paths_sync` (`memory_controller.py:1625`; `graph_scorer.py:330-415`), where missing or mismatched vectors score 0.0 (`graph_scorer.py:36-37`). The async on-demand fallback (`graph_scorer.py:221-325`) has no maintained caller.
- friday-agent `base.py:513-520` and the assembler (413-418) swallow extraction failures in the background.
REM gap: REM:684 and REM:853-859 promise that the whole recall fails with a typed error and that "missing vectors may use the existing on-demand document-role computation". REM:1177 and DI-22 treat "graph fallback" as a live route. The `memory_controller.py` allowed purpose (REM:1176) does not authorise narrowing these handlers, and no DI row requires an end-to-end recall witness.
Mitigation:
- Add trace rows for these handlers, with an allowed purpose of letting typed embedding-space, provenance and readiness errors propagate through recall's gather and except sites while every other existing degradation policy is preserved.
- Classify the async fallback as public-unwired.
- Disclose the sync missing-vector-equals-zero behaviour as existing and unchanged, and stop calling it on-demand computation.
Required proof: DI-22/DI-33 end-to-end negative witnesses (Chat recall, Runtime agent recall and the `recall_memory` tool) asserting a typed error rather than an empty `ContextPayload` for an unknown-provenance graph vector and for a mid-session identity mismatch.

**OPUS-M5 — Runtime MemoryProfile composition is unclassified and contradicts the ephemeral statement.**
Source: `friday_core/profiles.py:56-117` (EPHEMERAL/TESTING → `SimpleVectorStore`; VECTOR_ONLY/EPHEMERAL/TESTING → `NullGraphStore`), while Runtime `di.py:282-300` always builds `CollectionManager(path=self._config.chroma_path)` with three PersistentClients. Recall uses CollectionManager embeddings and collections (`memory_controller.py:499-516`). Graph and transcript parents are created eagerly (`di.py:248, 265`). Eleven test files construct RuntimeKernel.
REM gap: REM:1140-1141 says fresh ephemeral stores do not touch a persistent namespace, and DI-29 covers only "Core direct StoreOpenRequest/ephemeral". Under the unset-origin rule, EPHEMERAL/TESTING Runtime would either refuse lifecycle memory or touch a persistent root, and either outcome changes existing behaviour without a disposition.
Mitigation: freeze a per-profile (FULL, VECTOR_ONLY, EPHEMERAL, TESTING) open-intent and identity matrix inside the existing `di.py`/`profiles.py` allowance, with no profile redesign: either ephemeral lifecycle collections or explicitly persistent ones with an explicit request. Disclose the chosen delta.
Required proof: DI-29 rows per profile, with zero persistent-root effects for the ephemeral choice, a refusal for an unset persistent choice, and kernel test setup listed as exact exceptions.

### Advisory

- **OPUS-A1** Chat `build_framework_embedding_service` (`adapters.py:1735-1745`) ignores `embedding.embedding_service` (`config.py:467-470`; template :233). Record this as existing behaviour and either validate the field against `default_service` or disclose it. DI-33 should assert the S2 case where the two differ.
- **OPUS-A2** Similarity thresholds are calibrated per model space (template 241-242, 274, 312-313, 394; `graph_scorer.py:70-75`; pruner 0.95; `factor_computer.py:89-101`). Disclose that S2 compatibility is operational, not retrieval-quality. Deterministic test vectors cannot prove it.
- **OPUS-A3** Enumerate the "maintained baseline configurations" for gate A:
  - the Chat pool template with its placeholder revision (models template 88-96);
  - the Chat non-pool default `text-embedding-3-small` (`adapters.py:1749`);
  - the compat non-pool alias with no revision;
  - the Runtime default (`config.py:637, 745`) and its legacy `embedding:` mapping;
  - the CLI env default (`container.py:63-66`);
  - the Chat inline `maintenance.embedding`;
  - Memory `MaintenanceConfig.embedding` (`maintenance/models.py:350-374`).

  State how readiness binds to exact identity when the YAML revision is a placeholder or absent, and where "current identity" comes from at runtime (config plus readiness record, or a live served-artifact attestation). Then either add a server-side alias-swap control to DI-21 or disclose the limitation.
- **OPUS-A4** The MAINT preflight probe makes a real embedding call (`pipeline.py:551-553`; Chat `reorganization/mutation.py:157-160`). Order it after namespace admission and through the guard, and witness zero provider I/O for unbound or mismatched roots.
- **OPUS-A5** CLI `FridayConfig.chroma_path` default factory (`container.py:69-71`) passes the default value explicitly into `RuntimeConfig` (110-135), so the unset/explicit origin bit is lost. Name it in DI-29.
- **OPUS-A6** Add the friday-agent built-ins and agents (`di.py:385-397`; `kernel.py:405-440, 600-630`) and the multi-agent controller and coordinator to the trace table as controller-mediated consumers needing no friday-agent change. Disambiguate the multi-agent `namespace` term (`di.py:303-330`) from the vector namespace.
- **OPUS-A7** Add the MEMQ store-only inspection commands (`memory_queries.py:556-560`) to the operation matrix (unavailable projection, no Chroma initialisation).
- **OPUS-A8** The MAINT participant infers dimension from stored rows (`mutation.py:627-641`; graph REEMBED requires exactly one known dimension at 1308-1326). In a fresh namespace with empty collections, a graph-only REEMBED refuses. Cross-check against the identity dimension or disclose, and add the case to DI-33.
- **OPUS-A9** Telemetry is compatible unchanged: a pre-dispatch refusal is a valid `error` outcome with zero attempts (`llm_events.py:173-176`). New refusals will map to the generic error category; state this.
- **OPUS-A10** Specify the counter-dependency install profiles for Runtime/CLI/Agent-only installs (friday-llm declares no tokenizer dependency), with the expected readiness behaviour (REM:1183 defers placement).
- **OPUS-A11** Classify the public `DocumentIngestionPipeline`/`SemanticChunker` (root export at `friday_memory/__init__.py:47`; test-only callers) as public-unwired legacy that must not become a second chunking authority.

## 7. Scope effects of newly found consumers

M1-M5 need either narrow additions to the allowed-path table (`context/extraction_filter.py` or deferral within Chat `adapters.py`/Runtime `di.py`; `ingestion/mcp.py` outcome mapping; `maintenance/analyzer.py`, `backup.py`, `__main__.py` and the synthesizer no-embedding refusal; `memory_controller.py` typed-error propagation; `profiles.py`/`di.py` profile open intent) or explicit maintainer-approved exclusions with disclosure. None needs a subsystem redesign, an automatic routing change, a migration, TUI work or a maintenance-order change. Existing MCP and Runtime-kernel test oracles become exact-exception candidates under the REM's existing freeze rule (REM:1249-1258).

## 8. Rubric

| Area | Weight | Score | Rationale |
| --- | --- | --- | --- |
| Framework consumer inventory | 2.0 | 1.2 | Thorough named seams, but one active ingestion route, a startup side effect, three legacy raw-store surfaces and the Runtime profile composition are missing |
| Operational configuration and API compatibility | 3.0 | 2.2 | The pool-preservation, readiness-record and stop rules are sound. The packaged-baseline CREATE_FRESH blockage (M1), the MCP behaviour delta and the identity keying for placeholders are open |
| Model replacement and namespace data safety | 2.5 | 1.8 | Strong sidecar, envelope and v2 recovery design; bypasses through legacy restore and the Chroma default EF, recall swallowing, and threshold disclosure remain |
| Bounded proof and reporting | 2.0 | 1.55 | DI-18 and DI-21-33 are detailed and call-phase oriented; witnesses for the new seams are missing |
| Scope and authority | 0.5 | 0.45 | Coherent and non-authorizing; the newly found consumers lack allowed-path entries |
| **Total** | 10 | **7.2** | |

## 9. Reproduced versus inspected versus future

- **Reproduced here:** integrity start/end PASS; board, dashboard, docs, metadata and whitespace checks (exit 0); hashes of the request, helper and wrapper.
- **Inspected statically (not executed):** every source and line citation above; committed templates read via wrapped `git show`; the committed compat fixture and test file names.
- **Future obligations (not requested here):** gate-A model, counter and dependency qualification; installed normal/optimized lanes; all DI rows, including the additions requested above. Nothing in this report is runtime evidence.

## 10. Isolation and limits

Private scratch only; wrapper audit is complete (`command-audit.jsonl`). The single failed zsh invocation (exit 127) executed nothing. No shared or input write, no unwrapped Git or admin command, no personal-state access, no peer or prior raw reports. Static analysis cannot prove the absence of dynamic consumers (for example config-driven `importlib` tool modules), so the inventory is source-grep-bounded, like the REM's own lower bound.

Report path: `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/b009693c-10b7-4a28-84c2-970a0e25d393/scratchpad/opus-r5-1794359781/review-report.md`
