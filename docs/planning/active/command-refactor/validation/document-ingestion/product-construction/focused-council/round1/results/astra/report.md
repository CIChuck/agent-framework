# ASTRA — focused INGEST directive review, round 1/3

**VERIFIED. assessment_complete=true; areas_assessed=8/8; mandatory_findings=0; coverage=10.0/10; overall=9.70/10.**

Candidate: `92e356d17bc3a97be18d3d7cc4fed740b06795d1`, branch `feature/cmd-ingest-001`, repository `/Users/chuckrussell/Dev/gendev/agent-framework`. This is a fresh independent read-only assessment of the conditional implementation directive, not product conformance, completed readiness, or permission to construct. No prior reports, transcripts or memory were consulted. No delegation, repairs or additional round was performed.

The directive comprehensively specifies the Friday integration and provides a coherent conditional build sequence. Its known unresolved qualification questions are explicitly blocking decisions with owners, required evidence and timing. I found no known contradiction hidden behind a future appendix. Exact A2/A3 artifacts and candidate execution remain legitimate staged obligations. Completed Docling evaluation was treated as established input.

References below use repository-relative files and line numbers. `D` denotes `docs/planning/active/command-refactor/directives/CD-CMD-INGEST-001-product.md`; `PM` denotes `validation/document-ingestion/product-construction/phase-evidence-map.md` under the same command-refactor directory; `PI` is its `package-impact-assessment.md`; `RD` is its `validation/document-ingestion/product-construction/readiness-decision.md`.

| Area | Assessment and exact evidence | Earned / weight |
| --- | --- | ---: |
| F1 — flow and ownership | Complete extraction → common planning → full embedding/vector validation → persistence/receipt flow. Core owns immutable neutral contracts; Tools converts and adapts document chunking; Memory owns policy, entry and persistence; LLM owns preparation/counting. Chat and headless roots own request/lease composition. New dependency cycles are prohibited. D42–46, 97–104, 228–249, 328–334; REM136–198 resolves public entry and source/derived semantics. | 1.95 / 2.0 |
| F2 — actual file commands | Default-handler resolution precedes raw-tail parsing; custom handlers/aliases, literal descriptions, option terminator, exact override syntax and retained text-line behavior are specified. Real extracted content reaches the common entry once, with positive stored counts required. D188–210; REM457–507. Registry and adapter source confirm real integration seams. | 0.98 / 1.0 |
| F3 — chunking/configuration/model guards | All supported supplied sources share document/512 defaults and independent override precedence. Final prepared input determines budget, with model-specific offline counters and response validation. Document/recursive/fixed responsibilities, structure/Unicode preservation, no second splitting and unsplit derived records are explicit. D212–266; PI189–207. | 1.47 / 1.5 |
| F4 — existing consumers and identity | The six compatibility exceptions have remedies. Existing interfaces/selection remain; B/N positive operations are required alongside refusals. Fresh coherent namespace admission, incarnation, graph/WAL implications, recovery versions, MCP receipts, background tasks, unscored recall and multi-agent visibility all have owners and exits. Public-unwired/absent routes receive distinct dispositions. D251–316; PM163–195; PI104–112, 208–244; REM136–153 and compatibility annex129–166. | 1.94 / 2.0 |
| F5 — failures and lifecycle | Complete conversion admission, zero handoff on extraction failure, whole-batch validation before writes, truthful partial storage and no transactional overclaim. Owned bounded work has no provider/store capability; cancellation invalidates storage eligibility and holds admission until quiescence. Cache eligibility binds source/options/model and actual destination records. D155–186, 237–249, 318–334; PM95–99. | 0.96 / 1.0 |
| F6 — packages and companion | All P01–P17 dispositions reviewed. Eight bounded implementation owners and nine indirect packages have differentiated responsibilities. Narrow counters remain separate from Docling; default Chat gets the document extra, bare Tools retains text use, and legacy extras remain distinct. Certifi/dateutil/lock duties are explicit. INGEST text-storage work and TOOLS-DOC document routing have separate activation and proof. D92–104, 137–153, 336–363; PI82–112; companion19–79. | 0.73 / 0.75 |
| F7 — tests and documentation | Acceptance exercises genuine registry → plan → disposable Chroma, stored source/provenance/counts, query and separate-process reopen, failure controls, headless injection and installed profiles. Case-level migration protects valid behavioral coverage. Architecture/guides require authored content, source/schema mapping and verified examples. D365–475; PI114–145; PM95–99. | 0.96 / 1.0 |
| F8 — sequence and acceptance | Q → I1 → I2 → I3 → AG → UAT is coherent. I1 is additive and preserves old preparation until I2 binds callers; narrow-counter and document dependency changes occur in separate slices. Exact appendices precede generation/test rewrites, unchanged-scope regressions block intermediate exits, and final code council precedes human UAT. D48–90, 106–133, 477–507; PM12–71, 197–208; RD50–104. | 0.71 / 0.75 |

The overall score is the sum of earned points under the supplied rubric: F1 2.0, F2 1.0, F3 1.5, F4 2.0, F5 1.0, F6 0.75, F7 1.0, F8 0.75. It is not an average of other seats or a rounded-up gate result. Coverage measures completion of this eight-area directive assessment, not exhaustive source inspection or runtime assurance. Minor deductions reflect cross-document navigation and presentation complexity, especially at phase/consumer boundaries; they do not treat unimplemented staged deliverables as defects. This completed seat meets its requested document gate.

## Mandatory gaps

None. No numbered mandatory finding or required corrective change is issued.

## Advisories

1. When freezing A2, make the central contract appendix easy to navigate from D3.3 and D3.5. It should colocate the source/plan/attempt identities, injected planner capability, receipt fields, and cancel/join state transitions. These obligations already exist at D53, 234–249 and 320–334; this is a usability recommendation, not an additional activation condition.
2. Keep the distinction between the single shared ingestion policy and existing unsplit structured records prominent in operator and architecture examples. MCP snapshots, derived summaries and maintenance records deliberately do not become document/512 chunks. D239–242, 298–300 and PI196–201 already specify this distinction.
3. Use the required per-slice maps to make I1's temporary dual preparation paths conspicuous to implementers. D118–133 and PM49–60 already prohibit accidental legacy-vector changes and mixed-space writes. The staged design is plausible, but deserves explicit paired old/current witnesses when built; this review supplies no such runtime proof.

## Evidence, selective source checks and limits

Read the full 507-line directive, criteria, compact review context, authorization, full phase map and full companion. Read all P01–P17 rows and relevant test, documentation, dependency, configuration, worker and upgrade duties in PI. Read RD's established results, limits and qualification/post-build gate distinction. A truncated combined output was recovered with a smaller PI131–270 read; it did not leave a focused area unread. Historical provenance labels in permitted documents were not used as verdict evidence.

Selective parent reads resolved two questions: REM136–198 and 457–510 establish the injected entry/source-derived/cache boundary and exact parser contract; compatibility annex11–79 and 129–166 establish positive B/N/R compatibility and supported/public/absent consumer dispositions. Heading/reference searches located these passages. I did not reconstruct inventories or audit all consumers.

Product reads were bounded to these seams:

- `packages/friday-chat/src/friday_chat/commands/registry.py:165–198,669–715,1196–1205`: the original input remains available at dispatch, handler identity is resolved, shared admission surrounds execution, and current handlers use SmartFileReader and the runtime adapter. This makes the proposed default-only raw-tail integration concrete.
- `packages/friday-chat/src/friday_chat/adapters.py:363–426`: actual character chunking and direct single/batch storage identify the implementation to replace. D207 and 225–235 directly address it.
- `packages/friday-tools/src/friday_tools/filesystem/smart_read.py:270–350,582–622`: existing session/Memory cache returns and small-file direct storage substantiate the need for INGEST's destination-bound receipts and common entry. These are not deferred document-routing duties.
- `packages/friday-cli/src/friday_cli/container.py:70–141`: constructor/environment defaults collapse into resolved fields forwarded to Runtime. D106–116 explicitly recognizes this gap and requires resolution before I1, with four-origin tests at I2.
- `packages/friday-chat/src/friday_chat/runtime.py:530–595` was a preliminary runtime implementation read, not used as real-storage evidence. A nonexistent `runtime/memory.py` lookup was corrected by a bounded filename/symbol search to the actual adapter; it was not a blocker.

No product imports, tests, builds, installs, network/provider/store calls, standalone Docling/OCR/model evaluation, administrative suite, archive/wheel audit or AST inventory was performed. Finance's excluded integration module was not read, parsed or executed. No user YAML, state, secrets or venv contents were inspected; only permitted metadata/hash checks touched protected entries. Safe-current-controls and controller-checks files were hash-verified, not read or adopted as fresh behavioral proof.

Buildability remains conditional on the existing gates: RD02 hidden-unit exclusion versus whole-workbook refusal, RD03 resource/cancellation qualification, RD01/05 exact baseline and replacement serving/counter identities, and RD06 dependency/assets feasibility. The directive names these honestly and stops dependent construction; this review neither closes them nor repeats the established converter evaluation. Actual exact signatures and candidate integration remain to be demonstrated under A2/I1–I3/AG.

## Entry and exit integrity

The request was SHA256-verified **before reading**: `32ab367aa4f9ffefcc8fe3b7deff3e761ed5e20e17d59b55bb286112dcd599fe`. Target SHA256 at both boundaries: `8abad750e6346b7118c6c23ea0fd2f2550f19a880179d23e134487c4d32495f2`. All eight required inputs, five optional references, supplied safe-current-controls and controller-checks matched their declared hashes at entry and exit.

HEAD and branch matched the candidate above at both boundaries. With `GIT_OPTIONAL_LOCKS=0`, `git ls-files -s -z` was obtained **before status** at each boundary; its SHA256 was `610562634bfd1122e9bdf85414be29b202a7608f97626fe5a0c61c1a2a31cf26`. Staging was empty. Status retained exactly the two modified Chat example YAMLs and untracked `.friday-old/`. All eight declared protected entries retained their expected mode, size, mtime, ctime, birthtime and declared content hashes. Python metadata scripts used bytecode suppression and imported only standard-library modules.

Machine-readable `entry.json` and `exit.json` in this report directory compare equal. All writes were confined to the new physical external reviewer scratch directory containing this report. No repository or supplied-input writes occurred.

This document VERIFIED grants no construction, effects, UAT, acceptance or delivery authority. This seat stops here.
