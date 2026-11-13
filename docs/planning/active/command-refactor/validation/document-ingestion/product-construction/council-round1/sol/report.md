# Sol independent review — INGEST product directive, round 1

**CHANGES_REQUESTED. COVERAGE 9.6/10; OVERALL 9.2/10. Construction activation: NOT APPROVED.**

Reviewer: seat sol, gpt-6.1-sol, high effort; 2026-11-12. One independent read-only round, performed directly with no delegation, memory, history search, agent inventory or peer-report reads. Embedded provenance labels in supplied normative/measured documents were treated as attribution, never as a current-seat verdict. This is conditional DOCUMENT readiness and selected-source feasibility, not implementation conformance. Future contract/file/test appendices are legitimate gated outputs; their present absence is not a finding.

Workdir `/Users/chuckrussell/Dev/gendev/agent-framework`. Base `8c36d8e26c618032c1ff536004a582c07ec56a5b`; candidate `fb587e7a12f48ef0d6937e008045de1de2dd8cd2`; branch `feature/cmd-ingest-001`. Formal target `docs/planning/active/command-refactor/directives/CD-CMD-INGEST-001-product.md`, SHA256 `da911b7e6f052ab27b0e37ee939e52a0555ca177c047f84b475c9fc72b5414c1`. Paths below are repository-relative unless absolute.

## Mandatory findings

### SOL-PD-001 — I1 exit requires the I3 ingestion deliverable (HIGH)

**Authority:** PD-02; REM section F requires bounded sequential construction, with exact approved scope; REM DI-23 requires the public headless Memory factory → Core entry → smart_read text small/large/force_chunked and warm-cache storage flow. Independent-validation policy requires each work unit to have its own bounded approved scope.

**Evidence:** Target lines 60–71 require independent verification of each slice before integrating dependants. Its I1 exit explicitly includes DI-23. Its I3 deliverables explicitly include Memory's shared plan/entry and existing smart_read text storage/cache handoffs. The target gives I1 Core/LLM/Memory embedding/namespace contracts, while I2 integrates existing consumers and I3 delivers the ingestion entry and smart_read handoffs. A DI-23 public positive cannot establish those I3 behaviors before I2 may begin. This is a forward dependency in the specified proof order, not a complaint that the code is currently unbuilt.

Current source corroborates the distinction: `packages/friday-tools/src/friday_tools/filesystem/smart_read.py:233` currently handles binary skip, mtime/context cache returns and separate large/small paths; `packages/friday-chat/src/friday_chat/adapters.py:363` delegates to the existing ingestion method, and its character slicer remains at line 2793. The new shared entry is an expressly future I3 deliverable. The AST excerpts preserve these actual methods without execution.

**Risk:** An executor cannot close I1 as written without crossing its declared slice boundary, replacing a public positive with a mock/protocol-only witness, or treating an unmet DI as verified. It undermines the intended independently verified sequence.

**Bounded correction:** Produce an explicit requirement-to-phase prerequisite/exit map. Put full DI-23 public-storage proof at the phase that implements the entry and smart_read integration; retain I1's applicable neutral contract and admission proofs under precisely named sub-obligations. Audit the other grouped exit IDs, especially DI-32's actual Chat aggregate handoff, for the same owner/dependency issue. Preserve every full DI/FC positive at the proper phase and aggregate; do not delete or weaken a parent requirement. Obtain any required scope/authority amendment rather than silently changing the parent.

**Proof required:** A topologically valid phase/evidence table showing each exit's exact source owner and already-available prerequisite. No I1 exit may require an implementation first delivered in I2/I3; each full DI obligation still has a named executed future public witness and aggregate disposition.

**Documentation impact:** Target section 2 and the final phase appendix; reconcile corresponding readiness/manifest references as necessary. No source repair is requested or authorized in this round.

### SOL-PD-002 — A1 mixes preconstruction qualification with installed product completion (MEDIUM)

**Authority:** PD-02/15; target activation table; pinned readiness-decision RD-06; REM A and DI-08/15 distinguish qualification from final product installed proof. Parent safety, positive compatibility and approval requirements remain binding.

**Evidence:** Target lines 43–54 require completion of **all RD-01–07 before product generation** and otherwise allow only document review/reconciliation under this draft. Readiness-decision line 63 requires default Chat **with the document extra** and counter-enabled headless Memory/Runtime/CLI/Agent, while explicitly rejecting a private test target as an installed product closure. Actual metadata has no Tools `document-ingestion` extra, no LLM `embedding-limits` extra, Memory depends on bare LLM, and Chat depends on bare Tools. The target itself assigns creation of these product edges to future construction (sections 3.1/4/5). Thus RD-06's installed product closure cannot be produced from unchanged product metadata before the product generation that A1 prohibits. Merely installing Docling beside existing wheels is expressly insufficient under RD-06.

**Risk:** The gate has no explicit authorized evidence path: either metadata must change before activation, or qualification-only evidence must be relabelled as final product proof. This is a gating contradiction; the report does not require those profiles to exist today.

**Bounded correction:** State exactly what preconstruction package/model qualification can establish without product changes, and which actual installed-product assertions belong to named slice/aggregate exits. Alternatively define a separately approved, exact readiness metadata work unit if that is the intended prerequisite. Any change to the pinned readiness contract or parent sequencing must be explicitly reconciled and approved. Preserve all final profile positives, dependency/origin/security checks, baseline compatibility stops and the whole Gate-A threshold; no readiness waiver is implied.

**Proof required:** A gate dependency table identifying artifacts/interpreters and permitted generation authority for every RD-06 closure item, with no product artifact required before its authorizing work unit. Show final installed profile proof remains mandatory and private experiments retain their limited classification.

**Documentation impact:** Activation table, RD-06 wording/disposition and bound activation appendices. Approved impact bytes remain preserved unless a separately reviewed addendum is necessary.

## Full criterion matrix

PASS means the conditional specification is adequate for this criterion, not that runtime conformance or readiness has been demonstrated.

| ID | Outcome | Requirement and independent evidence assessment |
| --- | --- | --- |
| PD-01 | PASS | Council authorization records the explicit request, exact single-round budget and no effects. Current-controls reports started/local, in_review, construction not granted. Target section 1 preserves policies and exact impact approval; older preparation labels do not overrule current authorization. |
| PD-02 | FAIL | Sequential slices and aggregate verification are explicit, but SOL-PD-001 introduces an I1→I3 forward proof dependency; SOL-PD-002 mixes prerequisite and installed-product exits. |
| PD-03 | PASS | Target sections 2/4 match REM owners and narrow allowlist. Core contracts and injected entry avoid new Tools↔Memory imports; Commands metadata has zero dependencies. Existing Core lazy adapters and Tools/Memory edges are disclosed. No frontend-owned chunk policy is proposed. |
| PD-04 | PASS | Target 3.1 preserves four local formats, sole Docling supplier, real OCR, furniture/headings/notes, complete-success admission and non-text audit. REM B supplies exact format/order/exclusion rules. Measured defaults' failures are retained; RD-02 explicitly stops hidden-row/column claims pending proof or approved amendment. |
| PD-05 | PASS | Target 3.2 incorporates REM C raw-tail contract, default/custom-handler separation, exact options/lookalikes/terminator and unchanged API54. Current registry execute/parser and files.py support the identified whitespace/placeholder/line-limit seams. |
| PD-06 | PASS | Target 3.3 + REM D specify all-source document/512, independent precedence, strict config, final prepared-token budgets, three strategies, plain-table honesty, source versus unsplit derived records and no second splitting. Exact strategy details properly freeze in A2. |
| PD-07 | PASS | Target 3.4 + REM E/annex B01–08 preserve service/call/config/resilience semantics, qualify omitted fields and require positive baseline/replacement operations. Preparation/counting/results are LLM-owned. Actual embedding methods preserve public batch/query interfaces; serving parity remains unresolved rather than inferred. |
| PD-08 | PASS | Target 3.4 incorporates explicit fresh coherent paths, matching reopen, incarnation/dimension/preparation identity, ephemeral isolation and strict v1/v2 recovery. Annex FC-03 preserves public backup positives with distinct binding evidence; FU-014 receives no complete-recovery credit. Current Core factory/vector constructor and v1 model AST show the intended bounded extension points. |
| PD-09 | PASS | All FC-01–14 and B01–08 are incorporated, including actual active/public/absent routes, MCP pending ownership/observer reasons, no late sink writes, truthful acknowledgement/lifecycle/metadata/multi-agent results. The annex names exact future integration nodes and positive B/N plus R proof. Source's unowned assembler task is a planned adaptation, not a present implementation finding. |
| PD-10 | PASS | Target 3.3/3.5 + REM execution section bind attempts/source/profile/plan/destination, hold admission through quiescence, exclude provider/store capability from workers and invalidate late success. Resource limits and cancellation are expressly unqualified future RD-03 proof, with no hard-kill/sandbox/transaction invention. |
| PD-11 | PASS | Fresh static audit verifies all 237 module hashes and 72 fixture/conftest hashes, 3073 inventory node entries and all three seed references. Inventory decompressed digest matches summary. These are static base definitions, not collection counts or semantic coverage. Target section 5 preserves unmapped bodies/signatures, exact phase exceptions, named FC nodes and non-default selectors. |
| PD-12 | PASS | Target section 6 and REM G2/DI-36 bind canonical architecture, exact guide paths, eight READMEs/templates, all three registries, CLI placeholders, source/example matrix and independent content review. Checker success is explicitly insufficient. |
| PD-13 | PASS | Target section 5 retains source/installed normal/-O, actual registry→real disposable storage→separate-process reopen, minimal profiles, call-phase mutants and exact origins. Offline/live module classification and Finance exclusion are explicit. Actual profile execution is future work; its gate placement defect is captured separately under PD-02/15. |
| PD-14 | PASS | Measured reports/facts distinguish configured 37-case/324-matrix behavior, 81 stored chunks per mode with Nomic 768 dimensions/context 2048, usage=0 and unqualified parity. Corpus is native-validity evidence only, no large Docling/Qwen inference. RD-01–07 remain open and component verdicts/scores are not whole-Gate-A evidence. |
| PD-15 | FAIL | Exact phase file/test appendices, intersection allowlist and stops are appropriately conditional, but SOL-PD-002 leaves preconstruction installation closure without an explicit feasible authority path. SOL-PD-001 also prevents bounded phase activation/exit as written. |
| PD-16 | PASS | Separate INGEST/TOOLS-DOC routing, selected-source versus consumer adoption, human UAT/acceptance, Qwen qualification/default selection and delivery remain distinct across target, companion, proposal and current controls. No publication, construction or model selection inferred. |

## Advisories and score rationale

SOL-ADV-001 (low, nonmandatory): target header and opening prose retain planning/pending and “before any council” preparation labels; companion similarly says no council approval recorded by that document. Current pinned authorization/controls explicitly supersede that routing condition. At the next authorized document reconciliation, label these as preparation-time metadata so operators do not confuse draft provenance with current review state. This does not invalidate the authorized present review or expand effects authority.

COVERAGE 9.6: every PD row assessed against full governing contracts and measured context, with fresh boundary/admin/static inventory checks and selected source/metadata/AST inspection. Deduction 0.4 reflects bounded source feasibility rather than exhaustive whole-framework implementation tracing or execution; no claim of universal source conformance is made.

OVERALL rubric: scope/authority **1.35/1.5**; shared architecture/feasibility **1.65/2.0**; extraction/chunking **2.0/2.0**; compatibility/data/effects **2.8/3.0**; tests/documentation/evidence **1.4/1.5** = **9.2/10**. Deductions reflect the activation dependency defect, forward phase proof dependency, and consequent uncertainty about when compatibility/installed evidence can validly close. Behavioral and documentation obligations themselves are strong and preserved. These are exact scores, no averaging with peers or rounding to 9.5. Two mandatory findings prevent VERIFIED regardless of numeric score.

## Fresh checks, inspected evidence and limits

Fresh request SHA256 was verified **before reading**: `6047aec2f9a5fa117055c41617b971edf01dd926a822a59b8fea8824891b4095`. Helper SHA256 `2e20c4e5568d8501e04c6c3a8e7e3277c8f67500f2d43d30851f7d864a2c7e46` was verified and its full bytes read before execution. The supplied helper/controller directories were never written.

Fresh helper opening, admin and closing exits: **0, 0, 0**. Admin's seven actual subprocess argv/exits/stdout/stderr are in `admin-commands.json`: board 36 tasks; dashboard current; documentation 1130 Markdown files; metadata 18 pyprojects; base..candidate planning whitespace, owned planning whitespace and staged whitespace all exit 0. No product test/build/install/import was executed. Admin checkers alone internally parse repository files as expressly permitted.

Fresh static audit exit 0: 237 modules/72 fixture hashes, 3073 static node entries, three seed references, source AST and complete selected method excerpts. No test module imported or collected; static counts are not parameterized runtime coverage. Filename-only base..candidate Git range confirmed planning-only changed paths; raw authority/navigation/log histories were never opened. Read manifest binds bounded input hashes and selected source files.

Inspected only: preparation-checks receipts, named behavior/E2E/corpus reports/facts/indexes, authority and readiness claims. The 37/324, 81-per-mode, corpus native checks and historical validation results were not rerun. No archive/store/dependency/model assets were opened to reproduce them; index parsing does not prove archive-member payloads. `measured-evidence.json` retains facts and index structure separately from fresh executions.

Existing root Ruff/collection/registry-format debt remains failed/unwaived and unrerun. Full dirty-worktree whitespace exit 2 is inspected preparation evidence only; fresh whitespace was intentionally scoped to the required candidate/planning/staged lanes. No credential-bearing Finance source/test payload was displayed or used. No network, provider/model/service/store operation, third-party/product import, install/download, Git write, branch, repair, or nested delegation occurred. All writes were to new physical private `/private/tmp/ingest-sol-review-jDcr1r` (directory mode 0700). No skill workflow or earlier review result supplied this judgment.

## Opening and closing preserved boundary

Both helper boundary checks pass with zero errors: 18,715 tracked-file hashes, 26 symlinks, eight preserved metadata entries and all 37 pins. Both measure logical index **before status**: `61ca95946a69b30db60625e88ce8ed3a16c48cfd5815a89dcd8d089f4fc2cf4e`. HEAD and branch remain the candidate/feature branch above; staged paths are empty. Both statuses are exactly:

```text
 M packages/friday-chat/config.example.yaml
 M packages/friday-chat/models-config.example.yaml
?? .friday-old/
```

These protected payloads were hash/metadata-only, never opened for content. No boundary drift or host checkpoint identity discrepancy was observed. Personal state remained excluded except permitted preservation hashing/declared metadata.

Formal disposition: **CHANGES_REQUESTED**, one round complete. Construction activation **NOT APPROVED**, all unresolved activation prerequisites remain open. No remediation/reissue or additional council is initiated. See command ledger and evidence checksum manifest in this private report directory.
