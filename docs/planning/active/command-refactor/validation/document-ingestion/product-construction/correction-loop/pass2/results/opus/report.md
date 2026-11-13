# INGEST product directive — Opus seat, additional pass 2/3 (global round 4)

Seat: Claude Opus 5.5 (`claude-opus-5-5`), fresh context, read-only, no delegation.
Date: 2026-11-12. Repository `/Users/chuckrussell/Dev/gendev/agent-framework`.
Candidate `8c847e72b6ab260a2fc618f74390f39d599cb6e7`; correction base
`af4e12bd66e19303b6b32dbd7a66c70eae6d3330`; source/test baseline `8c36d8e2…`.
Target `directives/CD-CMD-INGEST-001-product.md` SHA256 `19f0a7e9…7bb7dfa` (pinned, matched).

## Verdict

**VERIFIED** (document readiness and bounded selected-source feasibility of the conditional draft).

- Mandatory findings: **0**. Advisories: **7** (ADV-01 … ADV-07).
- Coverage **9.1/10**; overall **9.4/10**. Both are **below the 9.5 seat threshold**, so this seat does **not** satisfy the all-seat gate. Explanation below. No averaging and no rounding up.
- This VERIFIED result is not construction readiness. Activation prerequisites remain **open**: Q/A1 (RD-01–07, B and N-DIM/N-SPACE/N-CAP real qualification, Gate-A aggregate 9.5 review), A2, A3, A4 and A5, plus every actual B/N qualification. The result grants no Gate-A closure, construction, effects, UAT, acceptance or delivery.

## Integrity (matched opening/closing)

| Check | Opening | Closing |
| --- | --- | --- |
| Request SHA256 before reading | `92c0a020…d241c` = pinned | rehash identical |
| Helper `review_tools.py` read in full before use | `2e20c4e5…7e46` = pin | identical |
| boundary.json / current-controls.json | `00b988d7…` / `fd6fe8d1…` = pins | identical |
| Helper boundary (exit) | **0**, passed, errors [] | **0**, passed, errors [] |
| HEAD / branch | `8c847e72…` / `feature/cmd-ingest-001` | same |
| Logical index digest (before status) | `86b8c63e…d1bb` | same |
| Status / staged | 2 dirty Chat YAML, `?? .friday-old/` / empty | same |
| Tracked / symlinks / preserved / pins | 18,824 / 26 / 8 / 49 | same |

Scratch (physical, reviewer-owned): `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/ef0abf0a-5e19-4ead-907e-0a1be34af5a6/scratchpad/opus-r4p2-seat/`.
No repository or supplied-input writes were made. I did not import or test the product, install anything, use the network or a model, or open a store.

## Commands and exits (fresh)

All Git/admin subprocesses ran with `GIT_OPTIONAL_LOCKS=0` and with bytecode writing off. Python used `-I -B` with the qualified CPython 3.13.10.

| # | Command | Exit | Output |
| --- | --- | --- | --- |
| 0 | `shasum -a 256 request.json` (before reading) | 0 | matches pin |
| 1 | `review_tools.py boundary --label opening` | 0 | passed |
| A1 | admin `board` (`uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate`) | 0 | 36 tasks |
| A2 | admin `dashboard` (`… render --check`) | 0 | current |
| A3 | admin `docs` (`scripts/check-documentation-lifecycle.py`) | 0 | 1150 Markdown files |
| A4 | admin `metadata` (`scripts/check-package-metadata.py`) | 0 | 18 pyproject.toml OK |
| A5 | `git diff --check af4e12bd..8c847e72 -- docs/planning` | 0 | clean |
| A6 | `git diff --check -- docs/planning` | 0 | clean |
| A7 | `git diff --cached --check` | 0 | clean |
| — | admin helper aggregate | 0 | `admin-commands.json` in scratch |
| 2 | stdlib DI/FC/exit/proof-group audit (phase map vs REM/annex) | 0 | see matrices |
| 3 | stdlib inventory/seed/fixture/helper re-derivation from `git show 8c36d8e2:<path>` + `ast` | 0 | see matrices |
| 4 | stdlib `tarfile` stream/hash of 3 archives vs indexes | 0 | `archive-audit.txt` |
| 5 | `review_tools.py boundary --label closing` | 0 | passed |

Known baseline debt was not rerun and is not waived: root Ruff, root collection `test_display` collision, registry-format debt, FU-013/FU-014, and protected user whitespace in `models-config.example.yaml`.

## Fresh versus inspected facts

**Fresh (re-derived by this seat):**
- All 36 DI `parent_definition` strings are byte-identical to the REM table rows, and their SHA256 digests recompute. The 12 proof groups are disjoint and cover exactly DI-01–36.
- Every exit↔DI reference is reciprocal. No DI claims earliest completion before its latest referenced exit. The DAG is Q→I1→I2→I3→AG→UAT and is acyclic.
- The 19 FC named witnesses equal the annex proof-matrix nodes, with the same FC mapping. Each first executes at I2 at a valid exit and is reviewed at AG.
- Inventory: 237 modules and 3,073 static base nodes, re-derived from the baseline blobs. Every module hash matches, and every node's `sha256(ast.dump(node))` and line matches. The per-package and root-integration (11/61) counts equal the summary. The gzip is `dd37f3d5…`, and its JSON decompresses to `3c513e8f…`.
- Fixtures: 72 originals (59 non-Python, 7 conftest, 6 MCP fixture `.py`), all hash-matched. The supplement adds 3 disjoint identities, for an effective 75. There are 63 non-Python test-tree files: 62 included and 1 `.DS_Store` excluded. Supplement and exclusion hashes match baseline and worktree.
- Helpers: 30 entries, equal to all non-test, non-conftest `.py` files in the trees, with hashes matched. 6 overlap the fixture list (see ADV-04).
- Seed TM-01/02/03: file hashes match the baseline. Definition digest equals `sha256(ast.dump(node))`. The TM-03 fixture is exactly 8 bytes (`%PDF-1.4`).
- The gzip was created once (c3018370) and never modified. The helper inventory is unchanged since creation. The seed is unchanged in this correction range.
- No `packages/`, `tests/`, `uv.lock` or root `pyproject.toml` change exists from `8c36d8e2` to the candidate.
- Archives (integrity only, not behavioral proof):
  - behavior: 8,148/8,148 members match.
  - E2E: 367/367 match.
  - large-docs v2: 194/194 match.
  - Archive SHA256s equal their index records; there are no unsafe or non-regular members.
- Directive numeric limits trace to archived harness source:
  - 32 MiB, 50 pages, 2,048 members, 128 MiB, 4 MiB/part;
  - 32 sheets/100 slides (`fixtures.py:918`), 20,000 rows, 16,384 columns;
  - 250,000 cells/merged, 5,000 shapes;
  - `document_timeout=300`.
  - ONNX Runtime 1.31.1 appears in the archived package/lock records.
- Seven admin checks pass, as listed above.

**Inspected only (permitted historical/measurement claims, not verdict evidence):**
- Docling 2.150.0/Core 2.106.0/RapidOCR 3.10.0/Certifi 2026.10.23; 37 cases per mode; the 324-case matrix; 41+40 stored chunks per mode; 162 document plus 10 query vectors; Nomic `usage=0`; corpus maxima.
- Prior component verdicts named inside the results files.
- Controller `static-correction-checks.json` and `preparation-validation.json`. I did not adopt them; my checks above were independent.

## Correction delta first — PD-S01–07

| ID | Result | Evidence |
| --- | --- | --- |
| PD-S01 DI22 | **Closed** | Directive §2 (lines 86–87); MD join DI-22 = I3 with I1-C2/I2-C2/I3-C2/I3-C3; JSON DI-22 `earliest=I3`. I3-C2/C3 `traces_requirements` include DI-22 (reciprocity verified fresh). The I2-C2 assertion is limited to existing callers. |
| PD-S02 fixtures | **Closed** | Fresh re-derivation: 72+3=75 disjoint; 63 non-Python files = 62 included + 1 OS artifact; gzip/AST/seed bytes unchanged; no count inflation (helpers credit 0). See ADV-04 for the separate helper/fixture dual-listing. |
| PD-S03 pass/round | **Closed** | Target, companion, readiness, manifest, branch-handoff and current-controls all say pass 2/3 / round 4. A grep of the current drafts/maps finds no stale round2/no-third-round text. Historical criteria are preserved. |
| PD-S04 handoff | **Closed** | Only the "Next gate" line changed; the historical branch/merge provenance block is intact. |
| PD-S05 CLI seams | **Closed** (ADV-03) | `container.py` and `profiles.py` are added to the I2-C1 JSON paths. The MD/JSON assertion requires all four origins. Source confirms the gap (`chroma_path` default_factory env/default at `container.py:70–71`; `to_runtime_config` forwards at `:126`; `for_testing` literal at `:106`). |
| PD-S06 I1 additive | **Closed** (ADV-01) | Directive §2 (lines 115–124), phase-map MD (lines 48–55) and JSON `intermediate_I1_compatibility`. No released unguarded mode or broad waiver; stop for a named exception otherwise. Consistent with the intermediate regression rule. |
| PD-S07 uv.lock | **Closed** | I1-C2 JSON paths include `uv.lock` plus an assertion. MD row and RD-06 paragraph: I1 owns the counter lock delta, while I3-C5 owns the document-stack delta separately. |

## Retained corrections — PD-Q01–07

| ID | Result | Evidence |
| --- | --- | --- |
| Q01 | Retained | A1 row; RD-01/RD-05 Q; the qualification plan has 4 unqualified slots, null identities and `real_serving_required`; the activation rule stops on missing evidence. Deterministic vectors are labelled operational only. Candidate N stays post-build (see ADV-02). |
| Q02 | Retained | The metadata projection has no stdout/stderr payload, and the raw receipt is hash-only. My readable inputs contained no peer material or protected payload. |
| Q03 | Retained | Directive §4 and the MD/JSON `path_list_semantics` say primary seams are not an allowlist and that unassigned paths block. Pruner/synthesizer/fact-checker are in I2-C2. |
| Q04 | Retained | DI-24 (I1-C2/I3-C2/I3-C5) and DI-33 (I2-C1/I2-C2/I3-C5) are reciprocal. All 19 witnesses are individually mapped, with per-contract I2/I3 dispositions. |
| Q05 | Retained | Directive §7, MD lines 26–30 and JSON `intermediate_regression_rule`. |
| Q06 | Retained | The helper inventory has 30 modules, including the fake MCP server, the LLM helpers and the Moltbook test apps, with no node credit. |
| Q07 | Retained | A2 settles the gap before I1; I2-C1 exercises default/env/constructor/testing origins. Public shapes are preserved. |

## Required correction evidence — PD-R01–03

| ID | Result | Evidence |
| --- | --- | --- |
| R01 | **Pass** | DAG verified. All 12 exits have an owner, primary paths, a phase prerequisite (via `phases.requires`) and a planned witness. DI-17 (I1-C2→I3-C2), DI-23 (I1-C1→I3-C2), DI-28 (I2 ×3), DI-29 (I1-C3/I2-C1/I3-C3), DI-32 (I1-C4→I2-C3) and DI-33 (I2-C1/C2→I3-C5) are traced. DI-35 is per-slice, with whole-suite review at AG. No earlier exit asserts later implementation (assertions reviewed individually). The aggregate keeps all 36 DI and 14 FC; DI-12 human UAT is a separate later stage. |
| R02 | **Pass** | Every RD-01–07 Q column uses upstream/deployment facts, unchanged baseline code, or design/metadata proposals. None needs new extras/guards/candidate installs/authored final docs. A2 is a design binding. Post-build columns, all baseline-qualification stops, the Gate-A 9.5 review (RD-07) and final installed positives are retained. |
| R03 | **Pass** | DI digests, disjoint groups and seed tags were recomputed (TM-01 → DI-01/02/04/13/14/35, TM-02 → DI-07/35, TM-03 → TOOLS-DOC TD-02/03/04 + DI-35; see ADV-05). DI-12's separately authorized post-code three-seat review before UAT is retained (directive §7, JSON substages). AD01–09 check: (1) six-exception table with remedies (§3.4); (2) B02 risk checked first (RD-01); (3) conditional CLI; (4) worker/headless owner (§3.5); (5) inventory scope/root totals 11/61 match; (6) current routing; (7) package arithmetic 8 + Agent + 8 = 17; (8) canonical v0.6 assessment and materiality table; (9) eight-byte seed. |

## PD-01–16 matrix

| Criterion | Result | Key evidence / notes |
| --- | --- | --- |
| PD-01 authority/cap | Pass | Explicit statement in `correction-loop/authorization.json`; directive lines 8–13 and 17–19; engineering policy order. Product approval is `not_granted`; three-pass cap; no fourth pass. |
| PD-02 I1/I2/I3 sequencing | Pass (ADV-01) | Acyclic DAG; per-slice scoped exits plus AG aggregate; additive I1 staging avoids a forced regression. No circular activation (Q depends on no I-stage). |
| PD-03 ownership/injection | Pass | §2 ownership matches REM ownership table, impact P-01–08 and annex. The Core entry protocol avoids Tools↔Memory edges. Legacy edges are disclosed and source-confirmed: smart_read lazy Memory import (lines 37/218), large-file → Tools `code_chunker` (line 525), Tools memory wrappers → Memory, Core `profiles` lazy Memory imports. |
| PD-04 extraction | Pass | §3.1 matches REM B, the format rules and the measured configured profile (furniture/headings/notes). Limits trace to source. RD-02 hidden-row/column handling is honestly open, with "per document vs per unit" left to the final contract. |
| PD-05 raw tail/API54 | Pass | §3.2 matches REM C. Feasibility: `CommandRegistry.execute` holds the raw `user_input` and resolves `self._handlers[canonical]` before calling (registry.py:175–195). `_parse_command_input` split is at :1200. Commands `__all__` = 54 with no dependencies. |
| PD-06 chunking/budgets | Pass | §3.3 matches REM D: independent precedence; final-input budget; source/derived/unsplit; no second split. Source has the Chat `_chunk_text` 2,048-char seam and large-file raw_chunk/chunk_summary/file_synthesis seams. |
| PD-07 pool/model/counter | Pass (ADV-01) | §3.4 matches REM E and annex B01–08. Source: `_embed_batch_with_retry` has no index/cardinality/dimension checks; Chat `embed_text` → `embed_query`; `ChromaVectorStore.query` uses `embed_documents`; the pool default is ignored in favour of `embedding_service`; B02 defaults to `text-embedding-3-small`. These are single, feasible seams. |
| PD-08 stores/recovery/backup | Pass | Fresh-store policy, matrix, v1/v2 and FC-03 bounded selector are incorporated. Source: eager `PersistentClient` (`vector.py:84`); `recovery._open_client` single seam; `[memory_dir, memory_dir/"vector"]` probing in pruner/synthesizer/fact-checker/analyzer/backup; `_collection_dimension` returns None when empty; `MemorySnapshotManifest`, `RecoveryBundleManifest`, `_SnapshotEvidence` and Chat `AtomicJsonStore.read_model` exist. |
| PD-09 FC/B consumers | Pass | All 14 FC and 19 witnesses mapped. MCP observer: `MCPIngestionOutcome` has 4 literals; `processor.py:704` forwards the reason unchanged to strict `MCPEventReason`, which contains every annex-mapped literal. The assembler's untracked `create_task` (:420), the global rejection `FileHandler`, the `pending_extraction` owner (`adapters.py` flush → `_extract_turns`), the multi-agent stack, RetrievalFactorComputer/AccessBuffer/IncrementalGraphMaintainer and FU-013 `vector.search` were all source-located. |
| PD-10 worker/admission | Pass | §3.5 owner split matches REM and impact. Chat's `gate.shared(...)` already wraps the whole handler. The headless owner has an equivalent lease. A2 freezes the handles. No OS-sandbox claim. |
| PD-11 inventory/seed | Pass (ADV-04/05) | Fully re-derived (see the fresh facts above). §5 binds A3 case maps, the retain default, named FC nodes and exact selectors, with no broad skip/xfail. |
| PD-12 DI-36 docs | Pass | §6 plus architecture/guide plans. The three `CommandRegistry` classes and CLI `arg`, `repl.py`, `main.py` and `server/api.py` exist as described. The plan requires a matrix and independent content review. |
| PD-13 tests/profiles | Pass | §5 covers source/installed normal/-O lanes, minimal profiles, negative-control rules, offline/live classification, Finance live exclusion with an offline witness, and Transcript/Finance explicit selectors. `tool_loading` uses `pkgutil.walk_packages`. |
| PD-14 measured claims | Pass | Readiness claims reconcile with the results/facts files and archive integrity. Open items are honestly open: Nomic parity `usage=0`, RD-02, RD-03, Qwen serving, and the Gate-A 9.5 review. |
| PD-15 activation/scope | Pass | A1–A5; §4 intersection rule; unexpanded rows grant nothing; per-slice A2/A3/A4; stop list in §7. |
| PD-16 cross-document | Pass | INGEST/TOOLS-DOC separation agrees across the directive, companion, proposal, impact and guide handoff; Qwen is illustrative; UAT/acceptance/delivery are separate. The companion's allowlist matches the proposal. |

## Static audit matrices

**Exits (12):**
- I1: C1 Core, C2 LLM + Memory metadata + lock, C3 Memory admission, C4 Memory-v2.
- I2: C1 config/origin/profiles, C2 consumers/maintenance, C3 Chat-v2 recovery.
- I3: C1 converter, C2 headless plan/receipts, C3 command, C4 worker, C5 installed/docs.
- Each exit has `phase`, owners, primary paths, the generic phase-candidate `source_input`, a planned witness with `witness_status: planned`, an assertion and traces. Prerequisites are carried by `phases.requires`.

**FC dispositions (14):** each record has per-stage Q/I1/I2/I3/AG text.
- First exits: FC-01/09/10/12 at I2-C1; FC-02–08, 11, 13 and 14 at I2-C2.
- I3 interactions recheck at I3-C2/C3/C4/C5 as stated.

**Proof groups (12)**, identical to directive §5:
- file_arguments {05,06}
- native_ocr_office {01–04,13,14,25}
- command_storage {07}
- chunk_policy_content {16,17,31}
- embedding_capabilities_roles {18,22,24}
- routes_namespaces_recovery_caches {19,20,21,23,27,28,29,30,32,33}
- worker_resources {11,26}
- installed_regressions_rejections {08,09,10,15}
- framework_integration {34}
- review_human_sequence {12}
- test_migration {35}
- documentation {36}

## Source-review ledger (checklist groups)

| Group | Files/sections actually read | Depth |
| --- | --- | --- |
| Selection and roles | LLM `embeddings.py` 75–130 and 249–410 (full embed path); Chat `adapters.py` 250–275, 370–420, 1735–1810; CLI `container.py` 43–200, `profiles.py` full; Core `profiles.py` 56–88; Runtime `di.py` assembly greps 83–372 and `config.py` origin greps | Method bodies for the primary seams; `model_library.py` was not read in body |
| Stores and graph | `vector.py` 54–109 and 195–232; `collection_manager.py` 113–200 plus embed sites; `simple_vector.py` greps; `graph_scorer.py` 125–145 plus sync APIs | Partial; graph adapters/models/null_graph not read |
| Extraction/tasks/effects | `assembler.py` 398–427; `extraction_filter.py`/`extractor.py` logging greps; Chat flush/`_extract_turns` owner | Seam-level; consolidator/promotion bodies not read |
| MCP and indirect | Chat `memory_mcp.py` 20–200; `processor.py` 695–720; telemetry `MCPEventReason` full | Read; Memory `ingestion/mcp.py`, multi-agent bodies and MEMQ adapters were existence-only |
| Maintenance/recovery | `recovery.py` 398–414; `mutation.py` `_collection_dimension`; probing loops in 5 openers; `analyzer` sqlite opens | Seam-level; pipeline/reorganizer/provider_contracts/`__main__`/backup body not read |
| Files/common ingestion | Chat `registry.py` 165–200, 665–720, 1196–1206; `files.py` greps; `smart_read.py` 30–45 and 210–232 plus cache greps; `large_file_processor` storage greps; `tool_ingester` greps; Tools `inspection.py` | Seam-level |
| Profiles/imports/docs | Tools/Memory/Chat/Commands `pyproject.toml` (deps/extras); `tool_loading.py` greps; 3 registries; CLI placeholders; packaged template (clean tracked file) lines | 4 of 17 package metadata files inspected, plus the admin metadata check |
| Static evidence | Full gzip, summary, supplement, helper inventory, seed, phase-map JSON/MD and 3 archives | Complete, re-derived |

Parents read in full: REM (1–1420), annex, impact v0.6, approval record, existing-store policy, test-migration plan, architecture plan, guide handoff, Tools proposal, TOOLS-DOC directive, 3 policies, `AGENTS.md`, council/dev-board skills, readiness, phase map MD/JSON, qualification plan, authority manifest, correction-loop authorization/roster, preparation authorization, metadata projection, branch handoff, assessment, and the 3 Gate-A results plus facts and indexes.

## Mandatory findings

None.

## Advisories (stable IDs, bounded fixes)

- **ADV-01 (medium-low) — I1 preparation-activation timing is implicit.**
  - Requirement: REM lines 799 and 894–899 enable the verified Nomic preparation/role convention only on the bound fresh-store path after role handoffs; no mixed legacy vectors.
  - Evidence: directive §2 (lines 115–124) and phase-map `intermediate_I1_compatibility` constrain only the *identity requirement* for existing callers. They do not state that I1-C2's preparation must not change vectors that existing unbound flows write or compare before their I2 wiring.
  - Risk: low to moderate. An A2 author could enable preparation globally at I1. The intermediate regression rule and parent incorporation would catch it, but only indirectly.
  - Bounded fix: add one sentence to the additive-staging paragraph and the JSON key. New preparation/role correction is reachable only through new guarded/bound APIs in I1; existing unbound flows keep baseline preparation until their I2 bound wiring.
  - Proof: an I1-C2 negative witness showing existing-caller vectors are unchanged.
  - Docs impact: I1 notes.
- **ADV-02 (low) — N stage list omits I3.**
  - Evidence: the qualification plan's `candidate_positive_refusal_stages: ["I2","AG"]` and readiness line 104 ("I2/AG still execute candidate N"). The phase map, however, repeats B/N/R at I3-C5, adds document flows to FC-14 at I3, and REM overflow rule 2 (chunk budget vs effective capacity, N-CAP) is an I3 concern.
  - Bounded fix: add I3 to the stage list, or say "I2/I3/AG".
  - Proof: none needed beyond the edit. Docs impact: none.
- **ADV-03 (low) — CLI wording drift.**
  - Evidence: the JSON I2-C1 assertion still says "CLI is source-unchanged if forwarding suffices", while the MD row dropped it. Source shows origin is lost inside the dataclass `default_factory`, so forwarding alone cannot suffice.
  - Bounded fix: align the JSON to FC-10's three branches: bind a narrow adaptation, prove an existing mechanism, or stop and reconcile.
- **ADV-04 (low) — 6 dual-listed files.**
  - The 6 MCP fixture-server `.py` files (`tests_mcp/fixtures/*_server.py` ×5 and `tests_chat/fixtures/mcp_execution_peer.py`) appear in both the 72 fixture identities and the 30-helper inventory. There is no count inflation, since helpers carry 0 credit.
  - Bounded fix: A3 assigns a single classification per path, or the summary notes the overlap.
- **ADV-05 (low) — cross-unit tag.** Seed TM-03 is a TOOLS-DOC entry tagged DI-35 (INGEST migration acceptance). Bounded fix: keep DI-35 only if shared-inventory acceptance is intended; otherwise tag the companion's own migration gate.
- **ADV-06 (trivial) — typography and ordering.** Directive §5 lines 363–364 are missing spaces ("union:72", "plus3", "total75"). The I3-C5 assertion sentence order differs between MD and JSON.
- **ADV-07 (disclosure, no deduction) — unassigned allowlist paths.** Many REM allowlist paths have no primary exit yet. Examples: `controller/memory_controller.py`, `retrieval/collection_manager.py`, `graph_scorer.py`, `extraction_filter.py`, `consolidator.py`, `lifecycle/promotion.py`, `ingestion/mcp.py`, `maintenance/__main__.py`, `pipeline.py`/`reorganizer.py`/`provider_contracts.py`, graph models/adapters, Chat `config.py`/`reorganization/mutation.py`/templates, and Tools `memory/lifecycle.py`. The directive correctly makes A2 assignment a blocking activation gate. Listing them would speed A2.

## Scores (honest; not inflated)

**Coverage 9.1/10.** The 7 delta, 7 retained, 3 R and 16 PD criteria were all assessed. Every static join, inventory, seed and archive was independently re-derived. All permitted parents were read in full.

The deduction is for source depth. Several checklist seams were verified only at symbol or seam level, not as full method bodies:
- Memory `ingestion/mcp.py` and `collection_manager.stage_mcp_snapshot`;
- multi-agent controller/coordinator/journal and MEMQ adapters;
- consolidator/promotion;
- pipeline/reorganizer/provider_contracts/`__main__` and the backup body;
- graph adapters/models;
- Chat `reorganization/mutation.py`, `coordinator.py` and `artifacts.py` bodies;
- `model_library.py`;
- 13 of 17 package metadata files (covered only by the admin metadata check).

**Overall 9.4/10** (rubric):

| Area | Weight | Score | Deduction reason |
| --- | --- | --- | --- |
| Scope/authority | 1.5 | 1.45 | ADV-06 cosmetic |
| Shared architecture/feasibility | 2.0 | 1.85 | ADV-01 implicit staging scope; ADV-03 wording |
| Extraction/chunking | 2.0 | 1.90 | Counter granularity and RD-02/03 open (honestly disclosed; minor residual specification) |
| Compatibility/data/effects | 3.0 | 2.80 | ADV-01 preparation-activation timing; ADV-02 N stage list |
| Tests/documentation/evidence | 1.5 | 1.42 | ADV-04/05 classification/tag nits |
| **Total** | 10 | **9.42 → 9.4** | |

These are not runtime-confidence scores. There is no deduction for forbidden replay, absent unapproved code or gated future appendices.

## Precise unresolved questions

1. Will A2 restrict I1 preparation to new guarded paths (ADV-01)?
2. Are Office structural counters per document or per unit? `fixtures.py:938` initializes counters before the unit loop, but the final contract is open.
3. Which mechanism preserves CLI constructor-versus-default origin? Additive marker types are feasible without a signature change.
4. Exact incarnation-scoped ephemeral collection-name encoding against backend name-length limits (FC-09).
5. Whether the hosted B02 identity can qualify at all (Q stop).
6. Nomic local/server parity (`usage=0`).

## Limits

- Targeted source feasibility only (see the ledger); no unrelated defect hunt.
- No product execution, so no runtime confirmation.
- Archive checks are integrity, not behavior.
- Raw authority/navigation/execution-log, raw preparation receipt, pass-1 results and peer reports were not read (filename-only listing seen in the diff stat).
- `.DS_Store`: hash and classification only.

## Stop

This single seat stops here. I started no replacement, repair, or later pass. Q/A1–A5 and actual B/N qualification remain open.
