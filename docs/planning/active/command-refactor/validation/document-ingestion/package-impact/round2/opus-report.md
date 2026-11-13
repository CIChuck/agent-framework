# INGEST-PACKAGE-IMPACT-001 — Round 2/4 — Seat opus (claude-opus-5-5)

**Outcome: VERIFIED** — no mandatory findings. Coverage **9.65/10**, overall **9.60/10**.

This is a fresh, independent, read-only review. It does not use builder reasoning or historical or peer reports and verdicts; the round-1 report files were not opened. It grants no maintainer satisfaction, Gate-A activation, construction, acceptance or delivery authority.

## Identity and integrity

- **Request:** `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/round2/inputs/review-request.json`. Its SHA256 `979d4f20…f26af6a9a` matched before the file was read.
- **Helpers:** `read_only_command.py` `3acff26f…c037d`, `verify_identity.py` `c4d9bf96…78452`, `current-controls.json` `09e53c85…5222` and `protected-manifest.json` `2c34dad1…f948` all matched. Both scripts were read in full before they were run.
- **Opening identity:** `python3 -B verify_identity.py <request> OWN_SCRATCH opening.json` gave exit 0 and PASS. The logical index (`e451bc50…d4ee`) was hashed before status. HEAD was `1a040de3`. 17704 protected files and 6 preserved-metadata entries were checked, with 0 errors.
- **Closing identity:** the same command with `closing.json` gave exit 0 and PASS, and the output was byte-identical to the opening run (sha `6c9363ce…1db3`).
- **Own scratch:** `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/c9e1408d-25a1-40fb-b900-4b692d1307fa/scratchpad/pi-r2-opus-1794405207`. It is outside the checkout and outside both supplied roots.

## Commands and exits

All Git and admin commands ran through `python3 -B read_only_command.py OWN_SCRATCH -- ARGV`.

| Command | Exit | Result |
| --- | --- | --- |
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` | 0 | passed, 36 tasks. Ran twice because of a duplicated shell invocation; both runs had identical allowed argv. |
| `… friday-dev-board.py render --check` | 0 | Planning dashboard is current |
| `… scripts/check-documentation-lifecycle.py` | 0 | 1024 Markdown files passed |
| `… scripts/check-package-metadata.py` | 0 | 18 pyproject files OK (17 packages plus root) |
| `git diff --check 8390f368..1a040de3 -- docs/planning` | 0 | no whitespace errors |
| `git diff --numstat 72ef265a 1a040de3` | 0 | correction delta inventory |
| `git diff [--word-diff] 72ef265a 1a040de3 -- <review_diff_paths>` | 0 | delta read. Criteria and iteration authorization are unchanged. |
| `git diff --numstat f43368c5 1a040de3 -- REM annex companion` | 0 | empty: the technical bytes are frozen |
| `git diff --numstat 8390f368 1a040de3 -- packages uv.lock pyproject.toml` | 0 | empty: no product or metadata change |
| `git diff --numstat 8390f368 1a040de3` | 0 | aggregate. Execution log is +57/−0; deletions appear only in current-state routing files. |
| `git show {8390f368,72ef265a,1a040de3}:execution-log.md` | 0 each | byte-prefix chain is True/True. Worktree equals the candidate; sha `e705f69c…e48e` equals the pin. |
| `git log --oneline 8390f368..1a040de3` | 0 | `72ef265a`, `1a040de3` |
| `git ls-files packages/friday-tui` and `git ls-files 'packages/*/pyproject.toml'` | 0 | friday-tui has no tracked files (ignored caches only). There are 17 tracked package pyprojects. |

**Reproduced vs inspected:**
- Reproduced: the hashes, identity checks, admin checks, diffs, numstats, the byte-prefix check and the relative-link existence check.
- Inspected statically, without importing or executing application code: package `pyproject` declarations via `tomllib`, AST counting of the Commands `__all__`, and greps or reads of selected source.

Nothing was installed, tested, built, resolved, fetched from the network, sent to a provider or model, or read from a store. The dirty Chat example YAML contents, `.friday-old/`, exports, raw authority history and peer reports were not read. The pinned authority files were checked only by hash.

## Correction delta (72ef265a → 1a040de3) — PC-01–04 closure on own evidence

| Group | Disposition | Own evidence |
| --- | --- | --- |
| **PC-01** multi-agent | **Closed** | `friday_memory/multi_agent/{controller,coordinator,journal}.py` define `MultiAgentMemoryController`, `PromotionCoordinator` and `PromotionJournal`. `friday_runtime/di.py:310-335` builds them only when `memory_mode == "multi_agent"`, wrapping the same `self.memory`. That matches the assessment's "shared physical space; visibility = authorization partitions" and annex lines 38-39 and 156. The P-04, P-07 and P-09 rows and the cross-package bullet state Memory ownership, Runtime assembly, unchanged source under the allowlist, honest partial reporting, no new transaction, and FC-13 proof. |
| **PC-02** chunk config and worker | **Closed** | `friday_chat/adapters.py:382-386` slices `/ingest` with `smart_file.chunk_size or 2048` and `chunk_overlap or 0`. `:2459-2464` feeds the legacy `LargeFileProcessorConfig`. The assessment's `ingestion.chunking.strategy/max_tokens`, command → YAML → built-in precedence (resolved per option), non-alias rule and no new overlap all match REM D (lines 544-559 and 626-629). The worker bullet matches REM "Execution, cancellation and admission" (lines 1059-1078) and DI-11/26: no provider or store capability, whole-request admission, quiescence before release, late results discarded, no hard-kill or OS-sandbox claim, and kept distinct from FC-06. |
| **PC-03** upgrade and first run | **Closed** | The bullet matches the REM existing-store policy (lines 1085-1154), the operation matrix (1166-1180), the operator note (1199-1207) and handoff items A02/A05/A06. Checks: Chat `config.py:477` has `persist_directory: str|None=None`; Chat `reorganization/layout.py:86-88` defines the vector directory, graph and optional access WAL; Runtime `config.py:763/797` defines `chroma_path` and `runtime_data_root` with containment. The packaged `config_templates/config.example.yaml:236` holds the literal `.friday/vector`. Templates are package data only, with no code loader, so a copied template counts as explicit origin, as the assessment says. The ephemeral FC-09 distinction is kept. Nothing performs a reset, migration or store operation. |
| **PC-04** DI-01–34 | **Closed** | DI-34 is bound inclusively in the source references (line 236), in P-06, and in the compatibility-table preamble (lines 74-75). The Tools row now cites DI-25, DI-30 and DI-34. No proof is fabricated or presented as executed. |

**Advisory dispositions, checked against existing contracts** (all hold):
- Graph scoring: maintained recall stays unscored; the injected sync/async scorer and async fallback match FC-08.
- Analyzer: admission happens before read-only Chroma or transcript SQLite access, with no inference, per FC-04.
- Wrappers: confirmed reset first admits the whole layout and keeps the sidecar, per FC-13.
- Retained lazy edges were verified in `core/profiles.py:75-113`, `core/interfaces/transcript.py:249-320`, `memory/ingestion/large_file_processor.py:525` and `tools/memory/{maintenance,inspection,lifecycle}.py`.
- `VectorCollectionDimension` `le=8192` is at `memory/maintenance/mutation.py:200`.
- `friday_tools.sandbox.FilesystemSandbox` is at `tools/sandbox.py:36`. `friday-sandbox` is Docker-based and currently Python-only (`protocols.py:43`).
- Declarations confirm Optimization → Memory and MCP `full` → Agent → Memory.
- `RuntimeMCPProvider` is in `runtime/mcp_loading.py`, and `_friday_tools_catalog` uses `pkgutil.walk_packages` in `tool_loading.py:60-72`.
- FU-013/014 get no positive credit.
- Exact-version satisfaction rebinding is a change-control rule inside PI-14 bounds, not a new gate.

None of these grants new scope.

## Full PI-01–16 matrix

| ID | Result | Evidence summary |
| --- | --- | --- |
| PI-01 | PASS | All 17 tracked packages appear exactly once: P-01–P-08 are implementation (CLI conditional) and P-09–P-17 are source-unchanged. The preamble (lines 69-75) explicitly says tests, inheritance or unchanged source do not mean no impact. `friday-tui` is only an untracked cache directory. |
| PI-02 | PASS | Rows trace to the REM ownership table (110-121) and the allowlist (1225-1266). Agent, Telemetry, Transcript, MCP, Optimization, Finance, Speech, Sandbox and Moltbook have no allowlist source path, which matches their dispositions. The multi-agent and Runtime `tool_loading`/`mcp_loading` witnesses are stated as source-unchanged. No unnamed owner is introduced. |
| PI-03 | PASS | Core neutral contracts, Tools conversion, Commands stdlib/API54 (AST count 54; imports are stdlib-only), Memory policy, LLM execution and Chat/Runtime composition all match. The dependency direction (no new Tools → Memory edge; injected entry) and headless injection are stated, and the retained legacy edges are inventoried accurately. |
| PI-04 | PASS | INGEST vs TOOLS-DOC appears at lines 29-38, in P-02 and in the details row. The shared extra does not complete adoption, and combining the two needs an explicit scope revision. |
| PI-05 | PASS | Chat already depends on Tools, and the change to `tools[document-ingestion]` is stated. Also stated: the Tools optional profile and legacy extras (`documents`, `spreadsheets`, `all-formats` all exist), the Certifi floor, the LLM `embedding-limits` extra requested by Memory and inherited by Runtime/CLI/Agent/Chat/Optimization/MCP-full, lazy Core/Commands/plain Tools/LLM imports, and unresolved exact versions and assets. |
| PI-06 | PASS | Covered: pool/non-pool preservation, Chat pool-default precedence, separate extraction and maintenance services, missing-field readiness, the hosted-baseline risk reported to Chuck, no swap, truncation or Qwen, and positives required separately from refusals. |
| PI-07 | PASS | Covered: identity sidecar, refusal for same-dimension changes, explicit fresh namespaces, preserved legacy files, `/read` availability, narrow graph and recovery identity, strict v1/v2 handoff, no reset, migration or backfill, and the Nomic preparation effect. |
| PI-08 | PASS | Covered: document/512 defaults and the three overrides, supplied text/web/tool payloads, unsplit MCP, conversation, maintenance and derived records, no URL ingestion, no generic automatic wiring, and no second split. Cache and receipt handling is referenced through DI-30. |
| PI-09 | PASS | Agent (`builtins.py`, `base.py`, `repl_base.py`; the inner task is not the wrapper), MEMQ metadata inspection, Telemetry (all 6 mapped literals exist in `MCPEventReason`) and Transcript FC-02/04 are covered. MCP stays source-unchanged with no new transport or schema. |
| PI-10 | PASS | Memory is labelled broadest. Covered: admission before clients and resources, owned logging and tasks drained at shutdown, two-kernel and ephemeral isolation, truthful partial counts, explicit path origin, and conditional CLI changes with no launcher (CLI `container.py` delegates to RuntimeKernel). |
| PI-11 | PASS | MCP and backups are causal compatibility consumers. Covered: live-marker protection, preserved defaults, pending IDs and receipts, no backup engine or MCP cleanup, and FU-013/014 unwaived with no positive credit. |
| PI-12 | PASS | DI, FC, B and TD references resolve, and all relative links exist. Everything is framed as planned or future proof. The prior verdict is called "design readiness only", with no claim of implementation conformance. |
| PI-13 | PASS | The details table covers versions, backends, OCR, counters, licenses, assets, numeric limits, signatures, receipts, the 8192 ceiling and final path coverage. Missing qualification stops readiness (lines 100, 148-149; P-05). |
| PI-14 | PASS | Lines 12-16 and 206-233 cover: satisfaction is an explicit prerequisite; the exact post-Gate-A version, commit and SHA256 are bound as a single referenced appendix; edited bytes need reconfirmation; material changes return for review; conditional REM approval and this council do not activate anything. |
| PI-15 | PASS (with readability advisory) | Each row gives concrete purpose, change types, retained behavior and evidence. There are no invented effort metrics, and the magnitude is described qualitatively. The rows are dense. |
| PI-16 | PASS | Opening and closing identity both PASS. The technical pins are unchanged since `f43368c5`, and product bytes are unchanged since `8390f368`. The execution log is append-only by byte prefix. README, next-phase, tactical plan, branch handoff, Gate-A handoff and the board snapshot consistently say round 2/4 with v0.2 in review. The assessment council status is kept separate from the technical verdict. The dirty YAML and `.friday-old` metadata are preserved. |

## New mandatory findings

None (PI-R2-OPUS: 0).

## Advisories (non-blocking, optional)

- **PI-R2-OPUS-A01 — row-level references.** The P-02 range "DI-01–25" includes obligations Tools does not own (DI-05/12/18/20–22). P-07 and P-08 do not cite DI-29. P-01 omits FC-09 and DI-21, which the annex row "Runtime profiles, Core factories, CLI container: FC-09/10/12" implies. P-04 lists FCs but no DIs. The inclusive DI-01–34 binding prevents these from being gaps. Optionally, narrow each row's references.
- **PI-R2-OPUS-A02 — user-visible upgrade effect.** "Refuse guarded Memory use" could name the concrete effects from REM lines 1156-1164: memory-dependent chat turns, recall, compaction, and background/exit maintenance return a readiness failure until a fresh destination is configured, while help, `/read` and exit keep working.
- **PI-R2-OPUS-A03 — preparation base.** Line 27 cites `8390f368`, but v0.2 was revised at `72ef265a`. Package and declaration bytes are identical across `8390f368..1a040de3` (verified), so the line is accurate in substance.
- **PI-R2-OPUS-A04 — Optimization.** Its `src` has no `friday_memory` import; the Memory edge exists only as a declared dependency. Stating this would sharpen the P-13 disposition.
- **PI-R2-OPUS-A05 — README state labels.** The unchanged design paragraph reads "Execution phase: planning; validation state: verified", while the package paragraph that follows reads "validation/in_review". Consider labelling the first as the design status at `f43368c5`. The board and controls are consistent.
- **PI-R2-OPUS-A06 — two satisfaction steps.** Approval steps 1 and 3 both say "record satisfaction". Optionally clarify that step 1 is initial review plus remaining conditions, and step 3 is the binding exact-version satisfaction record.

## Rubrics (independent, not target-seeking)

**Coverage: 9.65 / 10**

| Criterion | Score |
| --- | --- |
| Inventory and classification | 2.90 / 3.0 |
| Behavior, configuration and data effects | 1.95 / 2.0 |
| Ownership and dependency/deployment | 1.95 / 2.0 |
| Traceable boundaries and proofs | 1.85 / 2.0 (A01) |
| Readiness and approval completeness | 1.00 / 1.0 |

**Overall: 9.60 / 10**

| Criterion | Score |
| --- | --- |
| Accuracy | 2.90 / 3.0 (A01, A03) |
| Architecture and bounded delivery | 1.95 / 2.0 |
| Data, configuration and dependency safety | 1.95 / 2.0 |
| Evidence, future-work distinctions and reproducibility | 1.45 / 1.5 |
| Readability and change control | 1.35 / 1.5 (dense rows, A06) |

## Limits

- This is a static document and source-feasibility review. Future source, integration, normal/optimized installed evidence, Gate-A model, format and counter qualification, and B/N/R proofs are intentionally not evaluated as executed.
- The source search was targeted, not a whole-checkout audit.
- No repairs, delegation, staging or writes to the checkout or supplied inputs were made.
