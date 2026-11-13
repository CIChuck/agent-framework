# OPUS seat — focused INGEST directive council, round 2/3

- Target: `docs/planning/active/command-refactor/directives/CD-CMD-INGEST-001-product.md` SHA256 `3b998de0…cadce4db1` (verified)
- Candidate `0144c53908afb6f8288425c58c7a3bbff651faef`, branch `feature/cmd-ingest-001`
- Request SHA256 `eb0d8814…df09fe` verified before reading; all 9 required inputs, 6 optional refs, controller checks and current-controls hashes match.
- **assessment_complete: true — 8/8 areas assessed**
- **Verdict: VERIFIED** — zero mandatory findings
- **Coverage 9.6 / Overall 9.57** (weighted per rubric, not rounded up)

## C1–C5 correction check (current bytes)

| ID | Status | Evidence |
|---|---|---|
| C1 | Addressed | §3.2 ¶3 (Chat-owned awaitable adapter over Tools worker, legacy sync text/table kept, no Memory admission/profile/entry/planner just to display); §3.5 ¶2 (cancel before start = no launch; during/after-completion-before-render invalidates; exit/shutdown drains; join even if caller cancelled; no native-kill claim); §5 ¶"Document /read acceptance"; phase map read witnesses (responsive, cancel ×3, shutdown drain; DI-11/26/29; zero Memory/embedding/storage incl. absent/unready Memory). A2 owns concrete hooks. |
| C2 | Addressed | §3.3 ¶3 (Memory invokes injected Tools planner; Core counting/prep protocol injected by composition root; vendor objects stay in Tools; no default Tools→LLM edge); §5 headless document composition; phase map I3-C2 `test_headless_document_ingestion_uses_injected_tools_planner` (no Chat import, one plan, receipt). |
| C3 | Addressed | §3.2 ¶2 names `CommandRegistry.execute`/`_parse_command_input`, resolved handler identity, alias→target, custom overrides unchanged. Source-feasible: defaults come from `BASIC_COMMAND_HANDLERS` (registry.py:1147/1153), so identity matching is implementable. |
| C4 | Addressed | §3.3 ¶2: explicit/YAML/built-in above effective prepared capacity refused, never clamped; capacity checked before conversion; whole final batch preflight; N-CAP < 512 named. Exception table gives operator remedy. |
| C5 | Addressed | §3.1 ¶1 (LLM owns counter/profile schema; A2 assigns shipping/install or provisioned-root identity/hash/license/headless availability; no global cache/first-use); §3.3 ¶2a (no RuntimeConfig document YAML; Memory built-ins + per-call options; MCP ingestion settings preserved; processor char settings cannot re-split). Source confirms `MCPRuntimeClientConfig.ingestion` already exists (runtime config.py:288), so the no-new-subtree rule avoids a real collision. |

## F1–F8

| Area | Wt | Score | Assessment |
|---|---:|---:|---|
| F1 flow/contracts/ownership | 2.0 | 9.6 | Extraction→plan→embed→store has one owner per stage (§2 owners ¶, §3.5 Owners). Neutral Core values/protocols; no new Tools↔Memory imports; injected planner and counter directions explicit; headless reuse proven by a dedicated non-Chat witness. Advisory A5 on handing the converted document to the planner. |
| F2 file-command integration | 1.0 | 9.6 | Raw tail captured before `_parse_command_input` (which currently uses `split()`), default-handler identity, aliases, custom paths, exact options, `--` terminator, `/read` refusing ingest options, document `--lines` refusal, retained text/table semantics. Source shows Chat `SmartFileReader` lacks `.pptx` and returns placeholders, both explicitly replaced. Real `/ingest` currently calls the Chat `_chunk_text` slicer (adapters.py:363-401); its removal is named. |
| F3 defaults/strategies/limits | 1.5 | 9.6 | document/512 with independent precedence; strategy ownership split (Tools Docling vs Memory text); final-input token counting including headers/prep/special tokens; once-only role preparation; no second chunking; refuse-not-clamp incl. default; no overlap option. |
| F4 consumers/identity/upgrade | 2.0 | 9.5 | B01–08/FC-01–14 retained; six exceptions each with remedy; namespace identity beyond name/dimension; unbound stores preserved/refused; explicit-origin rules incl. known CLI `to_runtime_config()` gap with an A2 owner before I1; packaged `.friday/vector` disposition; recovery v2 strictness; supported/unchanged/absent route dispositions via DI-19/34. |
| F5 errors/cancellation/binding | 1.0 | 9.5 | Zero-handoff typed failures, truthful partial counts, lease held through quiescence for `/ingest` (consistent with `_SHARED_ADMISSION_COMMANDS` containing `ingest`, not `read`), late-output discard, destination-bound cache receipts and revalidation on hit. Advisories A1/A2 on drain seam and post-ceiling join behaviour. |
| F6 packages/deps/config | 0.75 | 9.6 | 8 owners + 9 indirect rows with dispositions; Tools extra, Chat default edge, LLM narrow extra via Memory, headless without Docling; I1 vs I3 lock deltas; Certifi floor/origin and Finance offline witness; INGEST/TOOLS-DOC boundary symmetric with the companion's activation precondition and path table. |
| F7 tests/docs | 1.0 | 9.6 | Genuine five-format registry→disposable Chroma with separate-process reopen; zero-ingestion negatives; headless document witness; separate `/read` lifecycle witnesses; installed normal/-O probes; A3 case-level migration before rewrite; DI-36 authored architecture/guides with requirement→section→source→example matrix. |
| F8 sequencing/gates/handoff | 0.75 | 9.6 | Q→I1→I2→I3→AG→UAT with scoped exits that make no forward claims; additive I1 staging with stop-for-exception; per-slice A2/A3/A4 binding; unchanged-scope regressions block every exit; DI-12 post-freeze council then UAT; final matrices and separate INGEST/TOOLS-DOC status. |

Weighted overall = 95.7/10 = **9.57**. Coverage **9.6**: all required inputs read at their declared scope and targeted source checks made for each material integration question. This is not a source-wide or runtime-confidence measure.

## Mandatory findings

None.

## Advisories (non-blocking; suggested A2/A4 bindings)

1. **The Chat exit/shutdown seam is outside the named Chat paths.** The real REPL render (`output_sink.write` after `command_registry.execute`) and shutdown (`_run_lifecycle` finally → `_shutdown_through_coordinator`) live in `friday_chat/app.py`. That file is not in the REM Chat path rows, and §3.5/C1 place the hooks in registry/files/runtime. The design is still feasible there: the REPL is serial, so cancellation unwinds through the handler, whose shielded join completes before app shutdown runs. A registry-owned handle set can back this up. A2 should state that mechanism, define "render" as the registry's return of `CommandResult`, and cover a repeated cancel while the join is in progress so a shield cannot orphan the worker. Alternatively, A2 can obtain an explicit path amendment for `app.py`. The shutdown witness should cancel the real `FridayChatApp.run` and not only the registry.
2. **Join bound past the conversion ceiling.** Drain-before-return paired with "no immediate kill" leaves open what happens if native conversion overruns 300 s. RD-03 (Q) already owns worst-case cancellation feasibility. A2 should freeze the worker form (thread or process) and the reported outcome, for example the existing `shutdown_failed` reason, so shutdown cannot hang without a bound.
3. **Impact v0.6 wording.** The cross-package "Document worker" bullet speaks generally of Chat holding shared command admission through conversion. The required post-Q refinement (A4) should state that the `/read` handle takes no Memory lease, and should describe the injected-planner direction.
4. **Sync `SmartFileReader.read` for document extensions.** Its behaviour is unspecified: refuse, or convert synchronously only off the event loop. Only the two default handlers call it today. A2 should freeze it.
5. **Converted-document handoff to the planner.** REM §extraction says `ExtractedDocument` keeps access to the chunking capability. The directive says Memory invokes an injected Tools planner. A2 should freeze how the planner obtains the same converted document (bound handle plus source/profile identity, with no reconversion) and how `/ingest` conversion and planning share one cancellation/quiescence scope.

## Limits

Did not read in full: the REM (only the extraction/strategy and proposed-path sections), the embedding contract, test-migration, architecture/guide plans, or the phase-map JSON. Did not run admin suites, inventories, imports, tests or network. Docling evaluation is accepted as established input. Product feasibility rests on targeted reads of Chat registry.py, files.py, app.py, adapters.py, config.py and runtime.py, Runtime config.py, package pyprojects and the Memory ingestion listing. No runtime confidence is implied. This verdict grants no construction, effects, UAT, acceptance or delivery.

## Boundary evidence

Entry and exit match exactly (GIT_OPTIONAL_LOCKS=0, bytecode off; logical index taken before status):
- index `5dca109f…33dab4f5b` matches the expected value
- HEAD `0144c539…`, branch `feature/cmd-ingest-001`
- status: the 2 dirty YAML files plus `.friday-old/` untracked; nothing staged
- all 8 preserved metadata records match, with hash/metadata only
- no repository or supplied-input writes; scratch only

Finance massive test, user YAML contents, `.friday*`, exports and `.venv` were not read.
