# ASTRA — final authorized ROUND4 independent design review

Outcome: **VERIFIED**. Advisory rubric: **9.60/10**. Mandatory findings: **none**. Advisory findings requiring changes: **none**.

Candidate `728cba77e816e5618a06262dd4aa1cbc6e50a376`, branch `feature/cmd-ingest-001`, workdir `/Users/chuckrussell/Dev/gendev/agent-framework`. Correction base `36362be514ef387183a27d930cd41a8799e3d714`; aggregate base `c36e7ee51a9328918b9bb97712aa7f1d4a850d19`. Date: 2026-11-10. Seat ASTRA, gpt-6-astra, high effort.

## Scope, authority and independence

This is document/design readiness for REM-CMD-INGEST-001 plus TOOLS-DOC-001, not implementation conformance. I did not author or remediate the candidate. No parent transcript, private reasoning, current peer verdict, prior raw council report or unfiltered aggregate history was used. Historical score/status text encountered in permitted current status documents was excluded from correctness evidence. The correction brief was used only to identify requirements. No nested agents.

Read AGENTS.md, repository engineering/lifecycle/independent-validation policies, council, independent-code-validator and friday-dev-board skills, scope decisions, recorded discussion/format/Certifi/store-policy/iteration/roster authority, and current projected authority.json fields. Explicit user instructions govern the shared-checkout exception, no delegation, and final-round limit. A preliminary memory-registry lookup supplied procedural context only; no memory-derived product claim or prior verdict supports this result.

The correction technical diff was inspected FIRST. Then the entire current REM and companion, maintained-source seams, a path-filtered aggregate comparison and current status were assessed. The aggregate contains planning changes in the admitted technical paths and no changes in the pinned source paths. Old implementation gaps therefore remain baseline, not evidence that this proposal has already been built.

## Rubric

| Dimension | Score | Reason |
| --- | ---: | --- |
| Scope, authority, boundedness | 1.50/1.50 | Explicit settled choices, effects boundary, exact stop conditions and separate companion. |
| Shared architecture and integration | 1.90/2.00 | Concrete public contracts and enumerated consumers; substantial cross-package coordination remains. |
| Extraction and coverage | 1.85/2.00 | Clear fail-closed coverage; Office mapping and selected-version behavior remain material feasibility risks explicitly assigned to Gate A. |
| Chunking, embedding, data safety | 2.90/3.00 | End-to-end roles, exact counts, namespace identity and recovery are coherent; atomic creation and lazy composition are delicate future work. |
| Verification, reproducibility, reporting | 1.45/1.50 | Strong genuine-fixture, installed, negative and mutation obligations; exact future trace/test manifest must still be frozen. |
| Total | **9.60/10** | Score is independent of the controller threshold. |

These deductions express residual implementation/readiness complexity, not violated design requirements. No finding is invented to fill a score gap. There are no new mandatory/advisory finding IDs to assign.

## Correction-first disposition

**IR-F01 / supplied requirement INGEST-R3-ASTRA-001: closed at the design gate.** REM lines 903–948 and DI-32 now require separately named strict Memory-v2 and Chat-v2 aggregate models, closed 1/2 dispatch, unchanged old exports/bindings, typed active consumers, independent participant reparse and exact equality. Compatible combinations are only aggregate1/Memory1/Transcript1 for offline inspection and aggregate2/Memory2/Transcript1 for bound active recovery. Mixed versions, malformed discriminants, v1 active restore and v2 parse fallback refuse.

This addresses actual source coupling: Memory `maintenance/recovery_models.py:289` has a strict v1 manifest; Chat `reorganization/contracts.py:417` embeds it; `artifacts.py:167` writes, reads and reparses participants; `coordinator.py:365` types `_SnapshotEvidence`, and lines 1439–1558 carry snapshot through aggregate verification and rollback. `durability.py:314` accepts a typed Pydantic model, so a typed closed envelope can preserve the generic store. Memory/Chat root and maintenance/reorganization exports are included in the proposed allowlist. The unchanged Chat path digest at `layout.py:198` is distinct from the new identity-bearing Memory participant digest. No journal or Transcript schema expansion is needed by this design.

**IR-F02 / supplied fresh-creation requirement: closed at the design gate.** REM lines 1003–1095 plus DI-21/28/29 distinguish unset fallback from explicit raw origin, including an explicit value equal to the default. Runtime raw configuration is merged at several entry points (`config.py:1365`, 1486, 1970, 2120); recording origin before those defaults is necessary and explicitly required. Default RuntimeConfig is not CREATE_FRESH. Existing bound fallback can OPEN_BOUND. Absent vector plus any existing resolved graph/configured WAL refuses, including empty files. Reused Runtime container with only unrelated artifacts is eligible; its actual graph path is `resolve_runtime_state_path("memory/graph.json")` (`di.py:248`), not Chat's sibling graph. Pending/invalid-marker and marker-absent cases are disjoint. No history inference or cleanup is introduced.

The direct-client probes observed in pruner:105, synthesizer:174 and fact_checker:131 currently try two paths and swallow failures. The proposal explicitly removes that fall-through, requires exact normalized admission, and names a bypass mutant. Existing inert embedding objects can survive assembly; actual model/tokenizer/provider/store initialization remains gated. Backup guidance explains that legacy restoration needs the compatible old release.

All correction-brief advisory dispositions were independently considered: consolidated trace table, existing Core lazy Memory edges, direct-client no-fallback, Runtime transcript/artifact effects, inert service distinction, disjoint marker rows and pre-upgrade backup guidance. They are addressed in the current text, without claiming runtime proof. Earlier procedural outcomes are neither reconsidered nor retroactively waived.

## All 30 criterion outcomes

`PASS` below means coherent bounded proposed design with identified source seams and future proof requirements. It does not mean product tests passed. REM references identify sections or numbered DI obligations; TD refers to the companion.

| Criterion | Outcome | Evidence and assessment |
| --- | --- | --- |
| IR-01 | PASS | REM opening/ownership/next decision, current authority projection and explicit store decision preserve proposal-only scope. Start/end identity checks pass. |
| IR-02 | PASS | REM B requires actual meaningful source content, exact local four-format admission and zero ingestion for partial/empty/diagnostic output. `commands/files.py:61,122` confirms the placeholder seam being replaced. DI-01–04/07. |
| IR-03 | PASS | B requires page/order/OCR coverage and DOCX interleaving; declared Word omissions remain separate from failed required content. DI-01–03/09 specify genuine oracles. |
| IR-04 | PASS | B inventories visibility, cached formula/error status, merges and types through a non-text audit, reconciles Docling output, refuses unknown mapping and preview clipping. DI-13/25; legacy XlsxReader:152–306 demonstrates the separate selected-sheet/row API that TD retains. |
| IR-05 | PASS | B requires slide order/native text/tables/notes, truthful hidden and visual exclusions, no media fetch or fabricated content. DI-14/25 and TD-09. |
| IR-06 | PASS | C/D define original raw tail, exact reserved overrides, quoted option paths and literal suffix. `registry.py:175,1196` confirms irreversible splitting today. Default-handler identity is checked before altered parsing; API54 retained. DI-05/06. |
| IR-07 | PASS | D supplies document/512, independent override precedence, all three strategies, final contextualized budget and split/refuse limits. Existing adapter character slicer at adapters.py:385 is explicitly removed from storage. DI-16/17. |
| IR-08 | PASS | Ownership and exact paths allocate neutral Core contracts, Memory policy and injected Tools adapter; immutable structure is retained and accepted plans are not recut. Existing lazy imports are inventoried rather than falsely denied. DI-08/23. |
| IR-09 | PASS | E binds exact artifact/qualified hosted identity, dimensions, tokenizer and effective loaded capacity. Model-card maxima cannot substitute for served limits; Qwen is illustrative. DI-18/24. |
| IR-10 | PASS | E preflights final inputs, counts headers/special/role formatting once, validates entire result cardinality/dimensions/finite values/index mapping before storage. LLM does not split a single request. embeddings.py:249–325 confirms the shared boundary requiring changes. |
| IR-11 | PASS | A specifies isolated selected-version graph/extra/OCR/counter proof, manifest assets and declared/locked Certifi floor plus post-install origin/negative checks. No current install success inferred. DI-08/10/20/24. |
| IR-12 | PASS | B and execution section bound archives/resources, reject malformed/encrypted input, retain sandbox and untrusted-source controls, keep worker without storage capability and hold admission until quiescence. DI-04/11/25/26. |
| IR-13 | PASS | Route table and companion distinguish reads from storage and public unwired routes. smart_read.py:283–321,402,588 shows cache/small storage seams; adapters.py:2364 supplies LLMs but no maintained Memory injection. TD-01–10 and DI-19/23/30. |
| IR-14 | PASS | DI-01–32 and TD-01–10 require actual public paths, independent genuine-fixture validity, fresh Chroma, installed normal/-O origins, negative call-phase witnesses and explicit oracle deltas. Baseline debt is not waived. |
| IR-15 | PASS | Store-policy record, E identity section and next decision require fresh disposable tests, no legacy scan/reset/migration and separate master PR/MAINT acceptance. |
| IR-16 | PASS | A has explicit selected-release/API/resource/counter/effects stops before construction. Deferring empirical results to separately authorized Gate A is appropriate; no unsupported feature may silently fall back. |
| IR-R01 | PASS | Core injected entry/Memory public factory covers small/large/cache paths; shared source chunks differ explicitly from unsplit derived summaries. large_file_processor.py:841–960 confirms those record classes and current storage ordering. DI-23. |
| IR-R02 | PASS | Single root sidecar, exclusive pending/ready creation, incarnation, same-dimension refusal and runtime vector envelopes cover persistence, cache and graph. DI-21/22/30; vector.py:84/86 shows both direct constructor seams. |
| IR-R03 | PASS | Role inventory covers query adapter, graph fallback, synthesis, promotion/decay/reactivation and maintenance. vector.py:195–229 presently embeds query via document helper; synthesizer.py:712 uses query for stored text. Both are explicitly corrected. Source locator scan records other callers. DI-22. |
| IR-R04 | PASS | E separates optional catalog parsing from mandatory operation capabilities; pool/non-pool paths resolve or refuse. `/read` remains independently available. model_library.py:105/237 shows schema and resolved-spec seams. DI-18/29. |
| IR-R05 | PASS | D specifies deterministic Memory-owned non-Docling segmentation and source coverage with no extra dependency; missing Docling does not force text fallback or break text document strategy. DI-16/17/31. |
| IR-R06 | PASS | A/E/execution require offline synchronous exact counting, manifest root, server cross-check and worker quiescence; no unsafe thread-kill claim. DI-24/26. |
| IR-R07 | PASS | B limits audit to structural facts and refuses missing caches, clipping, unknown warnings or unprovable mapping. Docling remains sole text supplier; Gate A must demonstrate genuine Office behavior. DI-25. |
| IR-R08 | PASS | Route table accurately qualifies active/public-unwired/absent functionality; lifecycle migration remains inactive and guarded without functional repair. No automatic fetch/store activation. Prior advisory dispositions retained. |
| IR-S01 | PASS | Explicit policy record and root-state × operation matrix preserve old files, read-only availability and typed intent without legacy/stateless fallback. DI-29. |
| IR-S02 | PASS | E recovery adds identity/schema/layout binding narrowly; same-namespace restore does not overwrite sidecar, and old v1 artifacts are offline-only. Direct-client admission precedes live client creation. DI-27/28/32. |
| IR-S03 | PASS | Runtime/Core/CLI classification matches `di.py:250`, Core profiles:56 and CLI profiles reexports. Lazy operation readiness, hosted immutable identity/local BPE and unknown graph-vector whole-operation refusal are explicit. |
| IR-S04 | PASS | Destination/incarnation/collection/record receipts prevent false same-model cache completion. CSV lacks inferred table schema; inactive migration receives no integration credit. Existing imports and exact flags are documented. DI-30/31. |
| IR-F01 | PASS | Strict separate v1/v2 models, closed dispatch and actual aggregate consumers/exports are covered, with distinct fingerprints and DI-32. Detailed independent correction trace above. |
| IR-F02 | PASS | Exact raw-origin and associated-path absence rules, Runtime-container reuse, no direct-client fall-through and operator backup guidance are explicit. Detailed independent correction trace above. |

## Reproduced checks versus inspected evidence

All required administrative checks were executed through the verified command wrapper with private cache/TMPDIR settings. No product tests, builds, imports, installs, dependency resolution or application/model calls were run.

| Executed check | Exit | Result / own evidence |
| --- | ---: | --- |
| hashlib/pathlib verification of request and both helpers | 0 | All three exact SHA256 values matched before helper inspection/execution. |
| Immutable integrity helper, start | 0 | PASS; start-integrity.json. |
| Technical-path correction Git diff | 0 | Inspected inline before full design. |
| Board validate | 0 | 36 tasks; board.txt. |
| Dashboard render --check | 0 | Current; dashboard.txt. |
| Documentation lifecycle | 0 | 991 Markdown files; docs.txt. |
| Package metadata | 0 | 18 pyproject files; metadata.txt. |
| Correction git diff --check | 0 | No whitespace errors; whitespace.txt. |
| Technical/source-filtered aggregate Git diff | 0 | aggregate.diff, 106538 characters; current additions assessed against full documents, no prior raw review paths. |
| Static AST parsing | 0 | 57 pinned Python files, no imports; static-symbols.json. This is syntax/symbol inspection, not a product test. |
| Consumer locator search | 0 | 84 matched lines; consumer-locators.txt. Search hits were classified as code or examples; no dynamic coverage claim. |
| Immutable integrity helper, end | 0 | PASS; end-integrity.json. |

The exact wrapper argv, guards and exits are preserved in command-audit.jsonl. Administrative argv use `uv run --offline --frozen --no-sync --no-python-downloads python -B` with the requested scripts. The outer orchestration Python was itself wrapped, and every Git/admin child additionally used the wrapper. Static `sed`, `rg`, `cat`, `wc`, pathlib/hash/ast and own-report operations were exempt, unwrapped commands and are not misrepresented as wrapper executions. Shell/read invocations returned exit0. No prohibited personal-state listing/reading was performed; protected hashing/stat was done only by the immutable helper. The large status string was not dumped; exact equality was checked by that helper.

Public-source inspection, not installed proof: [Docling formats](https://docling-project.github.io/docling/usage/supported_formats/) lists the four intended formats; [native chunking](https://docling-project.github.io/docling/concepts/chunking/) exposes document-based/tokenizer-aware chunking and contextualization; [advanced options](https://docling-project.github.io/docling/usage/advanced_options/) documents offline provisioning and limits. These support architectural plausibility, not selected-version Office coverage. [Qwen's official card](https://huggingface.co/Qwen/Qwen3-Embedding-4B) confirms illustrative 32K/up-to-2560 specs, not deployed capacity. [PyPI metadata](https://pypi.org/pypi/certifi/2026.10.19/json) was read; no artifact was downloaded or installed. Historical assessment/planning receipts were not credited as reproduced runtime evidence.

## Integrity, isolation and limits

Start and end both match candidate/branch and logical index SHA256 `35a40c37ddfd7753db30f03eefd097ccee9c6f9ecbd5095f635f185e919dc280`, with all 17606 protected entries and the six preserved metadata records checked by the immutable helper; zero failures. Logical index is measured before status by the verified helper. Request SHA256 remains `0601d7c1f2db634e6efe20fd96aa38ea80539e129fdb0e1ecab3d5afe18c7c1c`.

Fresh reviewer-owned scratch is this report's parent directory. Every generated locator, symbol inventory, administrative output, audit, cache/temp directory, aggregate diff and report went there. No supplied/prior scratch writes, repository mutations, cleanup, checkouts, staging, commits or store operations. No known isolation or required Git/admin-environment deviation. Closing integrity followed the last shared source/input inspection; only own-scratch reporting/audit/hashing followed.

Baseline limits: selected Docling/dependency/OCR/counter/model experiments are pending. Current placeholders, character slicing, unguarded embedding shape/length paths and eager storage construction remain unbuilt remediation targets. Recorded historical Ruff534, collection conflict7196, seven formatting failures and MAINT Chat1413/15 were neither rerun nor waived. The 57-file AST pass does not establish type correctness or runtime safety. Public documentation does not prove the candidate's selected release.

Next gate: return this final authorized seat report for controller reconciliation. Any Gate-A activation must separately bind hosts, budgets, private target/asset root and final directive. No fifth review, construction, Gate-A execution, human acceptance, merge or delivery is authorized by this VERIFIED result.
