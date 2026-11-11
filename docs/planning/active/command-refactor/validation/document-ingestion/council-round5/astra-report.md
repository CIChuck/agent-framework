# Astra round5 — REM-CMD-INGEST-001

BLOCKED. Advisory design score: 8.4/10. Two mandatory technical design findings retained below.

Candidate 06f294d779c5bc9ea3016eaffdf8efb349979ce4; feature/cmd-ingest-001.
Base 82c3a05a271c321c18a3967624281a5272c579b9; amendment base c28e6f8bba959f10137b8d772a667ec4e59389f5.
Reviewer Astra, gpt-6-astra, high effort. One read-only pass; no delegation or repair.
Design/source feasibility only: no implementation conformance, runtime assurance, acceptance, construction, Gate-A, reset or delivery authority.

## Authority, integrity and independence

Request SHA256 verified before substantive review:
e463c4e849957eb920e4260c10d408217498f6afb787da474c301a546e33c35c.
REM: 2bbf54c8c987eba9b2b823c9efb6f218c4cd7058d8e0f72694ae8ed04dd12dea.
Helper: 2d383c058aec2af50f4b0c6d6b27909b7b57995755a89f3af6bcb2857eceb38a.
Wrapper: cb0669f81efd0098c104d7b96342fcd614255021ea2bfa49cbbb6af7c2fea248.
Both scripts inspected before execution. Complete request read in bounded sections.

Start and end integrity PASS, exit 0: all 17,643 protected entries and six preserved metadata records matched. Logical index digest 948187c7cb810e1721eaf094454ff68b44e4e6b35f65fad0290c6e98437a0ffe. HEAD, branch, status, staging and all pins matched. Closing integrity followed the last shared inspection.

Applied AGENTS.md, engineering/lifecycle/independent-validation policies, council and independent-validator skills, scope decisions, explicit fresh-store policy, current REM/companion, compatibility amendment and round5 scope/roster. Current revision marks in_review, prior_review_applies=false, new_council_active=true and gate_a_or_construction_authority=false.

ASTRA-R5-B01 — procedural BLOCKER: authority extraction exceeded the current-fields-only restriction.
An initial JSON selection extracted current controls correctly. A later command:
rg -n 'current_scope|new_council_active|current_revision' docs/planning/active/command-refactor/authority.json
also returned historical fields at lines 512, 716, 945, 1555, 1914, 2036, 2060 and 2091, including historical status text. The request forbids that broader authority inspection. Although no historical correctness conclusion was used, this seat cannot claim clean isolation and returns BLOCKED. No raw council report, current peer verdict, parent reasoning or aggregate history diff was consulted. General memory guidance also exposed historical summaries of other work units; none supplied correctness evidence. No cleanup or repair concealed this exception. Any replacement review requires separate authorization and fresh context; none is started here.

## Mandatory technical findings

### ASTRA-R5-001 — High: public consolidation can acknowledge turns after guarded summary storage refuses

Evidence:
- packages/friday-memory/src/friday_memory/context/consolidator.py:358 stores the summary through store_insight; :367 catches every batch exception and only logs it; :370 returns normal stats.
- Same file :189 calls summarization; :196-198 marks all input turns consolidated regardless of failed batches; :201 emits consolidation_completed. The returned errors list can remain empty.
- packages/friday-memory/src/friday_memory/adapters/episodic.py:105-119 excludes consolidated turns from subsequent consolidation selection.
- packages/friday-memory/src/friday_memory/context/assembler.py:432-454 exposes delegation; Memory root __init__.py:209 exports MemoryConsolidator. No maintained composition root setting it was found: public-unwired, not absent.
- REM:789-814 requires all-caller guards; :915-929 prohibits readiness failures becoming successful no-ops; exact implementation paths at :1162-1201 omit context/consolidator.py. DI-33 at :1246 lacks this acknowledgement witness.

A smaller replacement-model capacity, invalid vector batch or typed admission refusal can now take this prescribed refusal path. The existing caller can report completion and remove turns from retry eligibility without storing their summary. This is an existing weakness exposed by new mandatory guard semantics, not a claim that this docs candidate introduced the bug. Shared guard changes cannot fix this catch-and-acknowledge caller.

Narrow mitigation: explicitly classify the public consumer and permit only guard-failure propagation and successful-batch acknowledgement changes in context/consolidator.py and focused tests. Preserve scheduling, prompts, deduplication and record semantics; no automatic wiring, document splitting or transaction redesign.

Required proofs: qualified baseline plus changed-dimension and same-dimension changed-preparation replacement; success stores once before acknowledgement; overflow, mismatch and malformed vectors leave affected turns eligible, expose actionable failure and do not emit successful completion for refused work. Include mixed batches and retry. Existing tests_memory/test_context/test_consolidator.py:67 onward does not establish these guard scenarios. Require source and representative installed normal/-O call-phase proof. Affects EC-02/10/11/14/15/16.

### ASTRA-R5-002 — Medium: lifecycle refusal can render as successful promotion/decay counts

Evidence:
- packages/friday-memory/src/friday_memory/lifecycle/promotion.py:372 increments decayed_from_long_term before demote_to_decayed, then :380 catches failures into errors.
- Same file :462 increments promoted_to_long_term before promote_memory, then :470 catches failures into errors.
- packages/friday-tools/src/friday_tools/memory/lifecycle.py:34-54 renders those counts in content while putting errors only in data; ToolResult.error is unset.
- packages/friday-tools/src/friday_tools/base.py:29-33 stringifies error or content; :136-138 execute returns that string, hiding data.errors.
- Promotion service is active in Chat adapters.py:1926 and maintenance pipeline.py:317. Tools wrapper is public/injected, with no maintained factory wiring found.
- REM:677-691 and DI-33 require lifecycle compatibility/typed refusal, but :1175-1185 omits lifecycle/promotion.py and Tools memory/lifecycle.py from exact scope.

Narrow mitigation: explicitly define lifecycle refusal disposition, permit only truthful non-dry-run success accounting and public error rendering at those paths, with focused tests. Preserve dry-run prospective counts, thresholds and stage ordering. No generic tool redesign.

Required proofs: compatible service-name success; smaller-capacity replacement refusal; same-dimension identity drift and malformed-vector refusal. Assert refused mutations are not counted as successes and ordinary tool execute text exposes failure. Preserve existing partial-results policy. tests_memory/test_lifecycle/test_promotion.py:23-30 uses fixed 768-dimensional mocks; add model-parameterized tests and public Tools execute assertions in tests_tools/test_memory_tools.py. Affects EC-10/11/14/15/16.

## Advisories

ASTRA-R5-A01: authority.json:9 still says “Review the VERIFIED INGEST design handoff”; current_revision:2046 correctly records in-review status. Reconcile top-level wording during authorized document updates. No Gate-A authority inferred.

ASTRA-R5-A02: maintenance/mutation.py:200 caps VectorCollectionDimension at 8192. Freeze selected-model compatibility with this existing ceiling at Gate-A; do not remove it speculatively. runtime.py:479 has a three-dimensional fake, not production proof. lifecycle/migration.py:423 has a 768-dimensional dummy, explicitly inactive under REM:150 and excluded from replacement proof.

## Full consumer/disposition inventory

Paths here are under packages unless prefixed docs. Covered means proposed contract/path exists, not implemented or tested. Unchanged means compatibility through the shared boundary appears feasible, subject to regression proof. All package src trees were searched and all 442 Python files parsed successfully. package-audit.json retains package counts, framework import edges and call hits; consumer-files.txt/calls.txt retain discovery. Static search cannot prove every dynamic external injection.

| Consumer/status | Source evidence | Disposition/proof |
|---|---|---|
| LLM catalog/pool, active | friday-llm/model_library.py; embeddings.py:249,287,309,383 | Covered REM E/DI-18/33. Preserve list APIs, timeout/batch/cache/resilience; guard before cache/provider and validate indices. |
| Core protocols/factory, public | friday-core/interfaces/llm.py:113,125; interfaces/memory.py:174; profiles.py:58-84 | Covered narrow store envelope extension; embed methods remain unchanged. |
| Runtime pool/non-pool, active | friday-runtime/di.py:196-242,250,293,349-367; config.py:637,745-769,870-930 | Covered DI-29/33. Preserve extraction LLM and optional embedding selection, lazy readiness and unrelated services. |
| CLI compatibility | friday-cli/container.py:125,175,220-231; profiles.py; session.py:46,87,116 | Delegates Runtime; metadata merely carries config. Narrow forwarding covered. |
| Chat assembly/embedding | friday-chat/adapters.py:263-270,1926,2050; runtime.py:1421-1461; config.py:754 | Covered selection, deferred startup, query/document role, background/exit readiness. |
| Conversation extraction | friday-memory/context/extractor.py:578-606 | Covered narrow role/refusal changes. Existing catches must not swallow new guard failures; full extraction→graph/insights→recall proof. |
| Recall/provided query | controller/memory_controller.py:499-529,1460,1568,1639 | Covered identity envelope propagation; existing gather-to-empty must change for typed guard failures. |
| Persistent/ephemeral stores | adapters/vector.py; simple_vector.py:109-168 | Covered admission, dynamic dimensions, document/query roles; same-dimension identity cannot rely on shape. |
| Lifecycle collections | retrieval/collection_manager.py:179-262,559-673 | Covered promotion/demotion/reactivation guard before destination write/source deletion. |
| Graph stored/on-demand vectors | retrieval/graph_scorer.py:226-264; models/graph.py; adapters/graph.py/null_graph.py | Covered reserved provenance, query envelopes and document fallback; unknown provenance refuses whole semantic recall. |
| Synthesis/reorganization | maintenance/synthesizer.py:183,712-735; reorganizer.py:775; pipeline.py:951-1054 | Covered maintenance binding, role correction and direct-client refusal; no prompt/stage changes. |
| Pruning/clustering/fact checks | maintenance/pruner.py:114,172; fact_checker.py:140; analyzer.py | Covered stored-vector comparisons even without inference. Analyzer/reporting has no independent embedding space. |
| Snapshot/mutation/recovery | maintenance/mutation.py:594,1278,1467; recovery.py:412,536,563,1378; Chat reorganization artifacts/coordinator/contracts | Covered v2 identity/incarnation, strict legacy inspection and same-namespace rollback; DI-27/28/32. |
| Session compactor, active | maintenance/compactor.py:435-462,624-637; Chat adapters.py:889-930 | Guard through store; errors retained in result and Chat payload, acknowledgement after storage. Require explicit typed failure/later-phase trace; no unsupported silent-success claim. |
| MemoryConsolidator, public-unwired | context/consolidator.py:189-219,358-370; assembler.py:432-454 | Gap ASTRA-R5-001. |
| Promotion/lifecycle tool | lifecycle/promotion.py:372-392,462-471; friday-tools/memory/lifecycle.py:34-54 | Gap ASTRA-R5-002. |
| Agent recall/store tools, injected | friday-agent/tools/builtins.py:107-139,190-218; Runtime kernel.py:644-652 | Compatible unchanged through controller text/payload APIs; test real binding/refusal. Scratchpad uses session variables. |
| Multi-agent facade, optional maintained | multi_agent/controller.py:55-65,95,145 | Compatible via controller. Authorization namespaces share the underlying embedding root; not independent model spaces. Test visibility after replacement. |
| Multi-agent coordinator/journal | multi_agent/coordinator.py:124-192; journal.py:80-145 | Graph→vector partial failure recorded FAILED/partial_commit, no atomic claim; no cached vectors. Test refusal never commits and preserve partial reporting. |
| Context/passage/tool recommendation | context/assembler.py:501,665; passage_router.py:90; tool_manager.py:214 | Recall delegates; keyword/LLM selection does not compare vectors. Preserve nonsemantic paths. |
| smart_read text storage/cache, public injected | friday-tools/filesystem/smart_read.py; ingestion/large_file_processor.py | Covered raw/derived split, opt-in, receipts and cache identity. Chat storage remains unwired. Document routing belongs to companion. |
| ToolOutputIngester, public-unwired | ingestion/tool_ingester.py | Covered callable entry; no automatic route activated. |
| Legacy preparation pipeline/chunker | ingestion/pipeline.py:38-100,284 | Text/metadata preparation only; no provider/client. Guard final storage; do not claim old character chunks implement new document/512 entry. |
| Tools inspection/maintenance | friday-tools/memory/inspection.py:54-100,125-150; memory/maintenance.py | Store-only admission without tokenizer; semantic query delegates search. Preserve ordinary error adaptation; baseline API issues are not new integration proof. |
| Commands/MEMQ projections | friday-commands/memory_queries.py:75-79,113-144; Chat commands/memory_queries.py:74-88,150-169,507-533 | No vector creation; typed read failures reusable. Test bound inspection with embedding provider unavailable. |
| Transcript | friday-transcript/models/transcript.py:255; stores/sqlite.py:1119; Core interfaces/transcript.py:392 | No embedding consumer; acknowledgement upstream, transcript-v1 unchanged. |
| Telemetry | friday-telemetry/helpers/llm.py:358-393,669-723; models/llm.py:309 | Dynamic optional dimension metric; no inference/store ownership. Preserve error telemetry. |
| Finance/Moltbook/Speech/Sandbox | respective src trees; package-audit.json | No embedding/store calls found; own network/audio/process behavior unchanged. DI-10/29 import/composition regressions still required. |
| MCP | friday-mcp/client/server trees | Transport can call Runtime-bound tools but has no independent vector model. Registration/startup must not force Memory readiness. |
| Optimization | friday-optimization/src/friday_opt/signatures/query_gen.py:1; pyproject.toml:10 | Scaffold, no active embedding call; declared Memory dependency still affects installation closure. |
| TUI | friday-tui/src has no Python files | Inactive; no implementation authority. |
| Entrypoints/scripts | main.py:1-6; scripts static search | Smoke print/admin artifact checks; no alternate embedding lane found. |
| Legacy migration | lifecycle/migration.py:423,596 | Explicitly inactive, no repair/activation or integration credit; guarded-store admission must still prevent bypass. |

## Two-scenario matrix

Future proof obligations only. U: unchanged pool/catalog AND maintained non-pool configuration, new YAML fields omitted. R: explicit replacement with fresh coherent namespace, testing both changed dimension and same-dimension different space/preparation.

| Surface | U | R |
|---|---|---|
| Configuration | Same defaults/names/endpoints/credentials/batch/cache/resilience; qualified readiness supplies omissions | Explicit model choice, no redirect/resizing/ingestion-only service; independent roots may differ |
| Readiness | Missing baseline qualification is STOP, never parse-only success | Exact artifact/counter/preparation qualification; unsupported deployment STOP |
| API/roles | Existing embed query/documents interfaces; narrow identity-bearing store extension | Once-only query/document preparation across graph, storage, maintenance and lifecycle |
| Namespace | Fresh store also required for changed current-model preparation | Explicit absent vector+graph+configured WAL; sidecar/incarnation checked; no old-vector reuse |
| Extraction/recall | Retain extraction LLM and embedding bindings; graph/insight/summary roundtrip | Same full roundtrip under each replacement axis; unknown cached vector refuses before query inference |
| Lifecycle/consolidation | Success and actionable refusal; findings 001/002 unresolved | Lower-capacity unsplit refusal cannot acknowledge lost work or announce successful mutation |
| Maintenance/recovery | Compatible distinct service names pass; unused bad service isolated | Mixed space refuses; same-root/incarnation v2 rollback only |
| Caches/provided vectors | Validate identity/role/capacity before cache success; valid envelope passes | Reject old-space same-dimension vector; fresh destination needs actual record receipt |
| Non-embedding operations | Help/read/exit, graph text, admitted store inspection avoid embedding initialization | Same; unavailable namespace touched only for bounded admission, no automatic stateless fallback |
| Public indirect consumers | Agent/multi-agent delegate shared semantics; lifecycle wrapper gap remains | Preserve visibility and honest partial failure; no new transaction promise |
| Installed lanes | Qualified baseline fixture plus omitted fields in normal/-O | Representative cross-subsystem proof with exact new dimensions/counters; Docling only where needed |

## EC assessment

Technical assessments retained under procedural BLOCKED, not formal passing verdicts.

| EC | Assessment | Basis |
|---|---|---|
| 01 | Blocked procedurally | Exact pins/integrity pass; B01 |
| 02 | Gap | Unnamed public consumers found; findings 001/002 |
| 03 | Design adequate | REM:623-691, DI-33 preserve operational selection |
| 04 | Design adequate pending signatures | Core/store envelope scope and actual controller/store/scorer consumers covered |
| 05 | Design adequate | REM:623-641 qualification/STOP |
| 06 | Design adequate | Shared LLM preparation/count/result; Memory admission |
| 07 | Design adequate | REM:847-865, DI-22 graph roles/provenance and typed recall refusal |
| 08 | Design adequate | Separate extraction binding and DI-33 complete flow |
| 09 | Design adequate | Direct-client identity, comparisons, recovery REM:921-1005 |
| 10 | Gap | Findings 001/002 despite correct unsplit policy |
| 11 | Gap | Public consolidation/lifecycle effects; other package dispositions above |
| 12 | Design adequate | Fresh graph/vector/WAL REM:1058-1138; DI-21/27/29/33 |
| 13 | Design adequate | Compatible names and independent namespaces REM:640,660-671 |
| 14 | Gap | Shared checks sound; downstream catch/rendering holes |
| 15 | Gap | DI inventory needs exact public refusal witnesses |
| 16 | Gap | Necessary narrow files omitted; no broad rewrite requested |
| 17 | Design adequate; Gate-A pending | Companion TD-01..10, Certifi/offline/optional dependency rules |
| 18 | Blocked | Report retained but authority isolation violated; historical scores unused |

## Rubric and limitations

Inventory 1.5/2; configuration/API 2.5/3; replacement/namespace safety 2.4/2.5; bounded proof design 1.5/2; scope/authority design 0.5/0.5. Total 8.4/10, advisory proposal quality only. B01 independently overrides the technical assessment.

Fresh checks: board exit 0 (36 tasks); dashboard exit 0/current; documentation lifecycle exit 0 (998 Markdown files); metadata exit 0 (18 pyproject files); amendment whitespace exit 0. Start/end integrity exit 0. No product tests/imports/builds, installs/resolution, models/providers, personal store/dirty YAML reads, reset or migration. Static source/tests are not runtime evidence. Gate-A and actual normal/-O proofs remain future work.

All Git/admin executions used the verified wrapper and private caches/temp/output. A static zsh glob for empty TUI source produced no-matches; pathlib inventory confirmed zero Python files. Some large tool displays truncated; targeted reads resolved the REM and findings. No product failure inferred from absent proposed implementation; baseline lint/collection/formatting debt neither rerun nor waived.

Evidence: command-audit.jsonl (exact argv/cwd/exit and guard environment), start-integrity.json, end-integrity.json, board.txt, dashboard.txt, docs.txt, metadata.txt, whitespace.txt, amendment.diff, package-audit.json, consumer-files.txt, calls.txt, all alongside report.

Return BLOCKED to controller with useful findings. No automatic replacement review, remediation, acceptance or broader authority.


## Exact wrapped administrative commands and exits

Prefix for every command: python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/astra-round5-independent-ax58i_i1 --

    python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/check_integrity.py /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/review-request.json
    exit 0

    uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate
    exit 0

    uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check
    exit 0

    uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py
    exit 0

    uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py
    exit 0

    git diff --check c28e6f8bba959f10137b8d772a667ec4e59389f5..06f294d779c5bc9ea3016eaffdf8efb349979ce4
    exit 0

    git diff c28e6f8bba959f10137b8d772a667ec4e59389f5..06f294d779c5bc9ea3016eaffdf8efb349979ce4 -- docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md docs/planning/active/command-refactor/proposals/tools-document-adoption.md docs/planning/active/command-refactor/validation/document-ingestion/embedding-pool-compatibility.json docs/planning/active/command-refactor/validation/document-ingestion/council-round5/scope.md
    exit 0

    python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/check_integrity.py /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/review-request.json
    exit 0
