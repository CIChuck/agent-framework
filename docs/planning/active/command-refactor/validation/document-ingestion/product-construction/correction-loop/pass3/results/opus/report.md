# INGEST product directive — final additional pass 3/3 (global round 5) — Opus seat report

Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), fresh read-only seat, 2026-11-12. No memory/history lookup, no prior peer reports, no delegation, no repository writes.
Candidate `b6a62742e89951679f338e46f34c4650a5e0dbc7`; correction base `8c847e72`; source/test baseline `8c36d8e2`.
Target `directives/CD-CMD-INGEST-001-product.md` SHA256 `9856c29a…0ced` (verified via pin set).

## Verdict

**VERIFIED (document scope), zero mandatory findings — but this seat does NOT meet the council gate:** coverage **8.8/10**, overall **9.4/10** (< 9.5 each).
Construction activation prerequisites (Q, A1–A5, RD-01–07) remain **OPEN**. This verdict grants no Gate-A closure, construction, effects, UAT, acceptance or delivery.

## Integrity and commands (fresh)

| Step | Command (summary) | Exit / result |
| --- | --- | --- |
| Request hash before read | `shasum -a 256 request.json` | `c69ccd89…f67a` = required |
| Helper source read | `review_tools.py`, `source_reader.py` read in full before use (read-only git/stat/hash + 7 fixed admin argv) | — |
| Opening boundary | `python3.13 -I -S -B review_tools.py boundary … --label opening` | 0; passed; 18,854 tracked, 26 symlinks, 8 preserved, 52 pins; logical index `20c06871…2b19` before status |
| Admin: board | `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` | 0 (36 tasks) |
| Admin: dashboard | `… friday-dev-board.py render --check` | 0 |
| Admin: docs | `… scripts/check-documentation-lifecycle.py` | 0 (1156 files) |
| Admin: metadata | `… scripts/check-package-metadata.py` | 0 (18 pyproject) |
| Admin: range whitespace | `git diff --check 8c847e72..b6a62742 -- docs/planning` | 0 |
| Admin: owned whitespace | `git diff --check -- docs/planning` | 0 |
| Admin: staged whitespace | `git diff --cached --check` | 0 |
| Closing boundary | same helper, `--label closing` | 0; identical head/index/status/pins |
| Request rehash | `shasum -a 256 request.json` | unchanged `c69ccd89…f67a` |

All scratch (caches, tmp, outputs) under `/private/tmp/claude-501/…/scratchpad/r5opus/`. Audit artifacts there: `audit_map.json`, `audit_inv.json`, `audit_ast.json`, `audit_arch.json`, `trees.json`, `admin-commands.json`, `opening-/closing-integrity.json`, `ledger.txt`.

## Fresh versus inspected facts

Fresh (executed by this seat): all hashes/boundaries/admin above; stdlib JSON/AST/tar audits of phase map, inventory, seed, helpers, fixtures, role map and three measured archives; `git show` of base blobs for AST/hash comparison; read-only source/text reads.
Inspected only (not re-executed): measured Docling/Nomic/corpus results and facts (behavior, E2E, large-docs) — their numbers were checked for consistency with the readiness doc and archive integrity, not replayed. No product import, test, install, network, model, converter or store access.

## Correction delta T01–T06 (assessed first)

| ID | Outcome | Evidence |
| --- | --- | --- |
| PD-T01 | **Closed** | Directive §2 L120–125 adds I1 staging for preparation/role/cache identity with paired I1-C2 witnesses and I2 joint switch; JSON I1-C2 exit and `intermediate_I1_compatibility`; map MD L55–59. Consistent with REM L893–899 ("enable only with the new bound fresh-store path…never mix"). Source feasibility: `embeddings.py` has no preparation and an `md5(text)`-only query LRU (L184–214, L287–324) — an additive guarded path leaves legacy keys/inputs untouched. No final legacy mode introduced. |
| PD-T02 | **Closed (one stale sentence → A-01)** | `replacement-qualification-plan.json` N-DIM/SPACE/CAP stages now I2/I3/AG with bounded `I3_scope`; readiness L104/L120 updated; matches I3-C5. Q still precedes I1. Residual: `phase-evidence-map.md:17` still reads "candidate N public operations remain I2/AG". |
| PD-T03 | **Closed** | JSON I2-C1 exit: "exact narrow adaptation, prove an existing origin-preserving mechanism, or stop and reconcile; forwarding the resolved string alone is insufficient". Directive §2 L105–113 and annex FC-10 carry the same rule in prose. Source confirms the gap: `container.py` L70–71 resolves env/default in `default_factory`; `to_runtime_config()` L109–135 forwards the resolved `chroma_path`. MD row wording is shorter (A-02). |
| PD-T04 | **Closed** | `baseline-support-role-map.json`: 6 paths. Independently: the 37 tracked Python support files in test trees = 30 helpers + 7 conftests; helper∩fixture set = exactly these 6; fixture/helper/role-map SHA256 identical per path; base and current bytes equal; zero node credit. Original gzip unchanged. |
| PD-T05 | **Closed** | Seed v3 TM-03 requirements `TD-02/03/04` only, with `migration_acceptance_owner` assigning closure to TOOLS-DOC; old file/definition hashes unchanged and match the frozen inventory; `%PDF-1.4` literal is 8 bytes. |
| PD-T06 | **Closed** | Directive L369–371 spacing fixed; I3-C5 MD row text equals JSON `exit_assertion`. No scope change. |

## Retained S / Q / R

| ID | Outcome | Evidence |
| --- | --- | --- |
| PD-S01 | Pass | DI-22 refs I1-C2, I2-C2, I3-C2, I3-C3; earliest I3; reciprocal traces present (audit 0 bidirectional errors); directive L84–86. |
| PD-S02 | Pass | 63 non-Python test-tree files at base: 62 in the 75-identity union, `.DS_Store` excluded; 72 primary + 3 supplement, disjoint (overlap 0); union 75 = 62 non-Py + 13 Py (7 conftest + 6 dual-role). |
| PD-S03 | Pass | Directive, criteria, current-controls, authorization (`maximum_additional_passes: 3`, rounds 3–5), roster and board next_gate all say final pass 3/3, global round 5. |
| PD-S04 | Pass | Branch handoff only "Next gate" line changed; historical provenance retained. |
| PD-S05 | Pass | I2-C1 primary seams include CLI `container.py`/`profiles.py`; four origins named; A2 must settle before I1. |
| PD-S06 | Pass | Directive L115–127 + JSON rule: additive I1 or named approved exception; unwaived regressions block exits. |
| PD-S07 | Pass | I1-C2 paths include LLM/Memory pyproject + `uv.lock`; I3 document-stack delta separate. Lock baseline Certifi 2025.11.12 confirmed. |
| PD-Q01 | Pass | A1 requires B + N-DIM/SPACE/CAP qualified and asset-bound before I1; deterministic vectors explicitly not serving proof (readiness L85–104, RD-01/05). |
| PD-Q02 | Pass | `preparation-checks-metadata.json` keys contain only argv/exit/digests/byte counts; its `source_sha256` = raw receipt hash `36682354…`; raw receipt only hashed. No peer material read. |
| PD-Q03 | Pass | `path_list_semantics` + directive §4: primary seams, A2/A3 assign every path; pruner/synthesizer/fact-checker admission named at I2-C2. |
| PD-Q04 | Pass (A-04) | DI-24/33 bidirectional; 19 witnesses individually mapped, equal to annex L548–566 in order/ID; I2/I3 FC dispositions 14 distinct each. Q/I1/AG columns are a shared template. |
| PD-Q05 | Pass | Directive §7 L462–468; map L24–31; JSON `intermediate_regression_rule`. |
| PD-Q06 | Pass | 30 helpers hashed (base = current), 0 node credit, classification pending A3. |
| PD-Q07 | Pass | See T03; public call shapes preserved; I2 tests distinguish four origins. |
| PD-R01 | Pass | DAG Q→I1→I2→I3→AG→UAT acyclic; 12 exits all bidirectionally joined to DI traces; no reference stage later than earliest-complete stage; no exit text requires a later slice's implementation (I2-C1 counter installs depend on I1 metadata; I3-C2 on I1-C1; I2-C3 on I1-C4). DI-17/23/28/29/32/33 traces as stated in map L141–154; DI-35 per-slice at I1-C1..C4/I2-C1..C3/I3-C5, whole-suite at AG; DI-12 UAT after AG with two sub-stages. |
| PD-R02 | Pass | RD-01–07 Q columns use upstream/deployment/unchanged-code/inert proposals; post-build columns hold actual installs/guards; A2 is design binding; B02-first stop; Gate-A 9.5 retained (RD-07). |
| PD-R03 | Pass | All 36 `parent_definition` strings equal REM table cells and SHA256 of each cell matches (`audit_map.json`); 12 proof groups cover 36 DIs exactly once. Seed tags plausible against REM DI text. DI-12 post-code three-seat review before UAT retained (directive L398, L470–477). AD01–09: six-exception table (directive L276–283 = annex list); B02-first (RD-01); conditional CLI; worker/headless owners (§3.5); inventory root/excluded scope and totals (17 pkgs, 237/3,073 sum exactly); current routing; 8 owners + 9 indirect = 17; canonical assessment/materiality (readiness L106–123); eight-byte seed. |

## PD-01–16 matrix

| PD | Outcome | Principal evidence / note |
| --- | --- | --- |
| 01 | Pass | Maintainer authorization (`authorization.json`), policy precedence (§1), pending approval/effects (current-controls `product_implementation_approval: not_granted`), three-pass cap and stop. Board's umbrella `implementation_authority: granted` is not INGEST product authority (A-03). |
| 02 | Pass | DAG/exit audit above; AG aggregate and per-slice scoped verification; no circular activation trap (Q needs only upstream/unchanged-code facts). |
| 03 | Pass | Directive §2 ownership = REM table. Metadata: Commands 0 deps; Core→Telemetry only; Memory→Core/LLM (existing pinned edge for FC-12 extra); Tools declares no Memory; Chat→Tools for default extra; no new backend cycle. Existing lazy edges disclosed (smart_read→Memory, large_file_processor→Tools code_chunker, Core profiles→Memory). |
| 04 | Pass | §3.1 + REM B/format rules; measured corrections (furniture, headings, notes, formula/hidden refusal) carried; RD-02 hidden-unit exclusion honestly open. Source: Chat `files.py` placeholders L61/L122–129, no `.pptx`. |
| 05 | Pass | §3.2 = REM C; registry `execute` L165–196 has raw `user_input` before `_parse_command_input` (L1196–1201 whitespace split) → raw-tail delegation feasible in allowlisted `registry.py`; Commands `__all__` = 54. |
| 06 | Pass | §3.3 = REM D; Chat slicer `smart_file.chunk_size or 2048` (adapters ~L383) removed from `/ingest`; strategies/budgets/precedence/no second split. |
| 07 | Pass | §3.4 pool/non-pool, once-only preparation, counter, smaller-limit, index/cardinality/finite checks. Source: `embeddings.py` returns `response.data` order with no checks — gap is in scope. Runtime builds pool and non-pool services (`di.py` L196–233). |
| 08 | Pass | Fresh-store/open-intent/sidecar/v1-v2 per REM/annex; source: `vector.py` L80–92 constructs Persistent/EphemeralClient + get_or_create; `CollectionManager` opens three clients per path; v1 `MemorySnapshotManifest` `Literal[1]`; Chat bundle binds `participant_layout_fingerprint` to Memory manifest; coordinator reads typed via `read_model` — v2 envelope design fits allowlisted files. FU-013/014 unwaived. |
| 09 | Pass | FC-01–14 + B01–08 incorporated; source confirms each named seam: global rejection logger + FileHandler in extractor ctor (FC-01); MCP outcomes `oversized`/`storage_failed` and every mapped observer literal already in `MCPEventReason` (FC-02); fall-through `[memory_dir, memory_dir/"vector"]` in backup/analyzer/pruner/synthesizer/fact_checker and `sqlite3.connect` non-RO in analyzer (FC-03/04, DI-28); synthesizer three callable shapes (FC-05); unreferenced `asyncio.create_task` in `extract_context` + Agent outer task (FC-06); vectorless edge on swallowed exception (FC-06); `get_all` swallows exceptions (FC-08); scorer unwired, async fallback via caller `embedding_fn` (FC-08); Runtime eager Chroma/mkdir and no context-engine drain on shutdown (FC-06/09, DI-29); 8192 ceiling in `mutation.py` (FC-11); `tool_loading.py` `pkgutil.walk_packages` (FC-12). |
| 10 | Pass | §3.5 owners/handles; admission held via existing `/ingest` shared admission (registry L77–83, L186–192); cancellation/stale-success/quiescence; no OS-sandbox claim. |
| 11 | Pass | Inventory: 237 modules/3,073 nodes; names, lines and `ast.dump` digests reproduced for all 3,073 at base; module and fixture hashes equal at base and current; universe of tracked `test_*.py` = inventory (0 missing/extra); seed digests match; default retain; FC nodes retained. |
| 12 | Pass | §6 + DI-36 + architecture/guide plans: three registries named; CLI `main.py`/`repl.py`/`server/api.py` confirmed placeholders; `friday_cli.commands.CommandRegistry`/`arg` exist. |
| 13 | Pass | §5 selectors/profiles/negative controls; Transcript/Finance explicit selectors; Finance live module excluded; installed -O explicit checks; protected state preserved. |
| 14 | Pass | Readiness numbers match pinned facts (37 cases/mode, 21 docs, 324-case matrix, 18 assets; 41+40 = 81 chunks/mode, 162 doc + 10 query vectors, usage 0 ⇒ parity unqualified; corpus 20+5, max 31,544 words/46 pages/6 sheets/96 slides, no Docling conversion). Archives intact: behavior 8,148 members/67,376,725 bytes, E2E 367, large v2 194 — all member hashes/sizes match, regular files only, no links/traversal. Component scores (9.3/9.2) not substituted for 9.5. |
| 15 | Pass | A1–A5 table, §4 allowlist intersection, unassigned path blocks slice, stop conditions §7; future appendices cannot add authority. |
| 16 | Pass | Separate INGEST/TOOLS-DOC directives and completion; companion requires own activation; seed TM-03 assigned to companion; human acceptance/Qwen/UAT/delivery separately authorized; both directives at v0.5/pass 3/3. |

## Findings

**Mandatory findings: none.**

Advisories (non-blocking; bounded fixes for a future authorized edit only — no further pass is authorized now):

- **A-01 (low, T02 residue).** `phase-evidence-map.md:17` says candidate N operations "remain I2/AG"; plan JSON/readiness/I3-C5 say I2/I3/AG. Not contradictory in effect (I3-C5 binds N evidence), but inconsistent wording. Fix: "remain I2/I3/AG". Proof: grep for `I2/AG`. Docs impact: map only.
- **A-02 (low, T03/Q07 detail).** The MD I2-C1 row omits the JSON's "stop and reconcile / forwarding alone insufficient" clause. Also `to_runtime_config()` forwards default-derived `runtime_data_root`, `workspace_root`, `install_root` as constructor values. A2's origin design should state those forwarded defaults are not explicit-origin signals for Runtime-root reuse/creation. Proof: I2-C1 test cases for CLI default root. Docs: map MD/A2 appendix.
- **A-03 (info, PD-01).** Board shows umbrella `implementation_authority: granted`. Each INGEST slice activation record should cite directive-specific A4 authority so AGENTS.md step 3 can't be satisfied by the umbrella flag alone.
- **A-04 (low, Q04).** FC Q/I1/AG dispositions are one shared template across all 14 contracts; I2/I3 are specific. Acceptable for inventory/foundation/re-verification stages. A3 should still bind per-FC Q inventory rows.
- **A-05 (medium-low, policy/typing).** Several allowlisted edit targets carry pre-existing `# mypy: ignore-errors` (`friday_cli/profiles.py`, `friday_memory/lifecycle/promotion.py`, `friday_tools/memory/maintenance.py`, `lifecycle.py`; also CLI placeholders). Directive §5 requires "strict typing for changed public boundaries" but doesn't say how that applies inside these files. Fix: A2 should state per-file how changed code gets type-checked (narrow removal, or a separate strict check of the changed boundary) without adding suppressions. Proof: focused mypy on changed modules.
- **A-06 (info, feasibility load).** Runtime boot eagerly constructs the vector store and three `CollectionManager` clients on one path, mkdirs the graph parent, and shuts down without draining the context engine. Ephemeral Chroma uses the shared EphemeralClient system. This makes I2-C1/FC-09/DI-29 the heaviest seam. A2 should assign `di.py`, `collection_manager.py` and `vector.py` edits explicitly per slice.

## Scores

**Coverage 8.8/10.** Read in full: target, companion, REM (1–1420), annex (1–583), impact v0.6, test-migration, architecture and guide plans, Tools proposal, readiness, phase-map MD, the three pinned policies plus AGENTS.md, approvals, branch handoff, assessment, measured results/facts, all pass-3 control inputs. Phase-map JSON, inventory, seed, helpers, fixtures, role map and archives audited exhaustively by script.
Deductions:
- (−0.6) Source review was targeted, not complete method bodies, for: recovery restore/rollback bodies, `mutation.py` participant, `pipeline.py`/`reorganizer.py` role sites, `promotion.py`/`consolidator.py` bodies, Memory graph envelope models/adapters, `simple_vector.py` beyond the call site, Chat `config.py`/`runtime.py` wiring, `analyzer`/`backup` bodies, multi-agent journal.
- (−0.3) Phase-map JSON exit texts were read in full for 3 of 12 (the rest via the equal MD rows); replacement-plan and authority manifest were read via diff/grep, not end to end.
- (−0.2) The two pinned SKILL.md files were hash-verified only.
- (−0.1) Rounding is not applied.

**Overall 9.4/10** (rubric):

| Area | Weight | Score | Deduction rationale |
| --- | --- | --- | --- |
| Scope/authority | 1.5 | 1.48 | A-03 |
| Shared architecture/feasibility | 2.0 | 1.85 | CLI/Runtime origin needs a real design (A-02); typing inside ignore-errors files unspecified (A-05) |
| Extraction/chunking | 2.0 | 1.92 | Complete and evidence-based; RD-02 honestly open (not a deduction); minor reliance on future A2 split-or-refuse freeze |
| Compatibility/data/effects | 3.0 | 2.80 | T01 staging sound; A-01 wording; heavy I2 seam (A-06) |
| Tests/docs/evidence | 1.5 | 1.40 | Inventories exact; FC Q/I1/AG template (A-04) |
| **Total** | 10.0 | **9.45 → reported 9.4** | No rounding up |

## Precise limits / unassessed contract questions

1. Whether `MutationParticipant` and `recovery.py` restore can take the sidecar and incarnation check before every `PersistentClient` construction without reordering quiescence-token flows. Admission-before-open looks feasible from the single open sites (`recovery.py:412`, `mutation.py:594`), but the bodies were not traced.
2. Exact role correction sites in `pipeline.py` L951/L1031–1034 and `reorganizer.py` L775 were located, not read in context.
3. The exact FC-07 lifecycle false-return accounting in `promotion.py` was not traced line by line.
4. Graph envelope fields in `models/graph.py` and the adapters were not read.

None of these is a found contradiction. They are the remaining depth behind the coverage score.

This is the final authorized seat. No replacement or fourth pass is requested or implied. Activation prerequisites remain open.
