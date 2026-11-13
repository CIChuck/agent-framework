# Independent document review — round 4 of 4

**CHANGES_REQUESTED** — one mandatory finding (R4-ASTRA-001). Coverage **9.8/10**; overall **9.4/10**. This seat does not satisfy the gate. No fifth round, replacement, reissue, delegation, repair or continued automatic review is authorized. Return the unresolved finding to Chuck for disposition.

Reviewer: independent GPT-6 Astra seat, high reasoning effort, Codex/T3 Code; 2026-11-11. Workdir `/Users/chuckrussell/Dev/gendev/agent-framework`; branch `feature/cmd-ingest-001`; candidate `56a495b76e7b7f8a967633bf523dfa9c30f9ed73`; correction base `c96ecbea685a2627e033d3a9cb62a2f05b72afb7`. Reviewer-owned scratch: `/tmp/independent-r4-7aekkkfq` (external to checkout and supplied roots).

This is current document readiness/source-feasibility review. It grants no maintainer package-impact satisfaction, Gate-A activation, construction, acceptance or delivery authority. The explicit final-round instruction controls despite the stale fields identified below.

## Independence and input identity

The first operation hashed the request before it was read: `b9b11c7c95c7fe0f6c30c66e665597aa54456b04d6cd81675ce5d9877d085601`, matching the supplied digest. All request pins, helper pins, safe-controls hash and protected-manifest hash matched before helper execution. Both Python helpers were read. AGENTS, council and friday-dev-board skills, engineering/lifecycle/independent-validation policies, complete PI criteria and both scoring rubrics were inspected. User restrictions superseded the council skill's delegation workflow. No memory lookup, nested delegation, builder transcript/private reasoning or raw peer report/current peer verdict was consumed. Historical labels inside expressly supplied current technical documents received no correctness credit. No accidental forbidden exposure occurred.

Correction review was initiated using only the five permitted diff paths, followed by current aggregate documents and source inspection. No raw navigation/authority/board/report diff was displayed. Authority was hash-only; current fields were read exclusively from the pinned safe controls. The log comparison inspected bytes for prefix preservation without displaying historical content.

Opening and closing identity helpers both exited 0, outcome PASS: candidate/branch/status/staging matched, logical index was hashed before status and remained `2b13729afb8065137e0f9e7fc5c1079be3249313b8a406c5d649ccab5a093d0f`; all 17,730 protected files and six preserved metadata entries matched. The two dirty YAML files and protected stores/exports were not read for content. Their permitted hash/metadata checks passed. No shared write or restoration occurred.

## Mandatory finding

### R4-ASTRA-001 — Medium — current decision instructions still identify round 3/v0.3

**Requirement:** PI-16 requires current-state consistency. The review request and correction-cycle2.json require v0.4, three consumed rounds, and final round 4 with no reset/reissue/replacement/fifth round. Repository lifecycle policy requires current packet and board state to agree.

**Affected text and independent evidence:** `docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:1403` says “Review the revised assessment v0.3”; lines 1405–1406 call for “Fresh round 3” reviewing the amendment delta. This is under **Next decision**, not a historical label. The pinned `current-controls.json` top-level `current_scope` likewise calls for assessment v0.3, round3/4 and two consumed rounds. In contrast, REM lines 23–26, safe-controls `next_gate`, `package_impact_assessment.version`, `package_impact_assessment.council`, and safe current board/navigation all identify v0.4 and final round4/4. These facts were directly read, not inherited from a report. The request and controls hashes match; this is a real inconsistency in the frozen input, not an unstable checkout.

**Risk:** A downstream controller following the REM's concluding action or current_scope may select the wrong assessment/version or miscount the remaining review budget. Higher-priority instructions prevent that action in this review but do not make the conflicting current records consistent. Administrative validators passing do not check this semantic conflict.

**Exact bounded correction/disposition:** Reconcile REM's current Next decision and the authority current_scope represented by safe controls to v0.4/final round4, three rounds consumed, no replacement/fifth round, and stop for Chuck if the final gate is unmet. After this round, record its actual disposition rather than imply a new authorized review. Preserve historical prose and append-only evidence; do not change product scope, annex, companion, approvals or test requirements. No repair was performed by this reviewer.

**Recheck:** After explicit maintainer disposition, compare those current fields with the board next gate and revised safe snapshot; verify pinned hashes and that all current instructions identify the same consumed budget and stopping rule. Re-run appropriate administrative/link checks and identity checks for any changed candidate. This recommendation does not authorize another council round or reuse this candidate's verdict.

## Correction delta results

- **PC-05 satisfied:** assessment lines 12–20 binds conditional approval to old REM hash `e1c90753a3e2876df0f9f6f0ca82b1893455266cee1f252276f460b48a9f2a16`. Approval/change-control explicitly requires final amended REM/assessment binding and renewed exact-version satisfaction. The obsolete frozen-REM assertion is removed. Current REM hash is `b7ded08d9166da2173399c2b178c33b7176846959d2e08c3e5f3292993393187`.
- **PC-06 satisfied:** REM G1 and test plan reconciliation require explicitly incorporated case-level final-directive exceptions; unmapped bodies and public signatures/classes stay retained. Named FC nodes require an approved equivalent mapping with executed gate coverage. This is consistent with the annex's final exception clause and recorded user permission, without forcing obsolete test architecture or permitting silent coverage loss.
- **PC-07 satisfied:** architecture plan item 2 names `friday_cli.commands.CommandRegistry`/`arg`, `friday_chat.commands.registry.CommandRegistry`, and `friday_commands.registry.CommandRegistry`; requires owners/callers/compatibility, actual Chat routing and placeholder CLI REPL/main/server classification in architecture and CLI README. Current source supports those distinctions.
- Conditional test-only suites P-10–17 and root `tests/integration/test_package_cohort_metadata.py` are explicit in REM paths. Runtime `test_di.py` and the named focused Memory adapter/context/retrieval/maintenance anchors exist. All eight README obligations are bound by REM, assessment and guide handoff; Tools/Chat use setup/user-documentation classification while their README paths are explicit. Executive-summary/feature-catalogue changes are narrowly limited to affected claims. Membership-derived inventory is exactly 17 unique rows matching 17 metadata-bearing members.
- Annex and companion byte comparisons against the correction base are equal, with hashes `1092a332684e3f6a5f9edc3f2355c768775b0f2c01b82bcc97242932334faabb` and `8220e195f7b9b899fb377f5550920a3d9ac0699b33293a59c366ff6d2fa6d998`. Execution-log baseline bytes remain an exact prefix of current bytes.

## Complete PI matrix

References below are to current documents under `docs/planning/active/command-refactor`; source paths are repository-relative. PASS means the present planning requirement is supported, not that future runtime proof has executed.

| Criterion | Result | Evidence and assessment |
|---|---|---|
| PI-01 | PASS | Assessment P-01–17 matches root workspace `packages/*` and all 17 member pyprojects exactly once; eight proposed owners including conditional CLI, nine production-source-unchanged consumers. |
| PI-02 | PASS | Assessment rows map to REM ownership and proposed paths; test-only consumer allowances do not add production owners. Companion paths remain separately directed. |
| PI-03 | PASS | REM ownership and assessment distinguish Core boundaries, Tools conversion, Commands parsing, Memory policy, LLM guards and composition. Core profiles/transcript lazy Memory imports, Memory large-file Tools import and Tools memory-wrapper imports independently confirm disclosed legacy edges. |
| PI-04 | PASS | Assessment delivery boundaries/P-02 and companion delivery steps separate shared INGEST capability/text storage from ReaderFactory/smart_read document routing; installation alone earns no adoption credit. |
| PI-05 | PASS | All pyprojects inspected; current Chat Tools dependency is plain, Tools document/spreadsheet extras are legacy, Commands has no dependencies. Proposed default document extra/Certifi floor and LLM-counter inheritance match REM A/FC-12; exact assets/versions remain readiness outputs. |
| PI-06 | PASS | Assessment embedding configuration/readiness rows and REM E/annex B01–08 require qualified positive B/N alongside refusals. Chat adapters selects pool default; Runtime DI separately resolves extraction service. Hosted baseline uncertainty and illustrative Qwen remain explicit stops. |
| PI-07 | PASS | Assessment upgrade/data consequences and REM identity/recovery sections preserve old files, explicit fresh coherent layout, same-dimension refusal, /read availability and strict Memory2/Chat2/Transcript1 handoff; no migration/reset authority. |
| PI-08 | PASS | REM C/D, assessment configuration/source-derived discussion and companion specify document/512 with per-option precedence, no second splitting, unsplit structured/derived records and destination-specific storage receipts; absent routes receive no product claim. |
| PI-09 | PASS | Assessment P-09–12 and cross-package sections plus annex FC-02/06/13 cover Agent, Memory-owned multi-agent, metadata inspection, actual MCP receipts and unchanged telemetry/transcript contracts. Runtime DI confirms multi-agent assembly; Chat memory_mcp confirms pending/publication path. |
| PI-10 | PASS | Memory broadest impact is visible. REM admission/cancellation/FC-01/06/09/10 and P-04/06/07/08 require pre-effect admission, owner-specific logging/tasks, profile isolation, explicit origin and truthful results. CLI container is a Runtime compatibility wrapper with default-derived paths; conditional adaptation is appropriate. |
| PI-11 | PASS | Annex causal boundary/FC-02/03 and assessment readiness table preserve public backups and pending records, protect binding markers and leave FU-013/014 unwaived. BackupManager source confirms public defaults/file-selection behavior requiring paired proofs. No new backup engine or MCP cleanup. |
| PI-12 | PASS | REM DI-01–36, annex FC matrix and test plan distinguish required future source/installed normal/optimized and B/N/R proof from this static review; no runtime conformity inferred from administrative checks. |
| PI-13 | PASS | Assessment readiness table and REM A freeze dependencies/assets/licenses/resource bounds/model counters/signatures/exact files later; unsupported qualification stops construction. No speculative installation needed now. |
| PI-14 | PASS | Assessment approval/change-control, safe conditional approval and Gate-A handoff require Chuck's exact version/commit/hash satisfaction and separate directive approval, preserve remaining conditions and material-change review. Stale round wording is separately PI-16. |
| PI-15 | PASS | Every package has purpose/change type/retained behavior/proof disposition; dependency and test effects are distinguished. No invented effort estimate or completed-upgrade claim. |
| PI-16 | FAIL | Opening/closing preservation, pins, links/admin checks and log append-only pass. Current next-decision/current_scope disagreement remains R4-ASTRA-001. Prior verdicts are not extended to changed contracts. |
| PI-17 | PASS | Test plan dispositions, per-package map, initial inventory and acceptance; REM G1/DI-35 explicitly reconcile case exceptions with annex preservation. Every valid behavior requires executed replacement/retained coverage; no assertion-count shortcut or unrelated churn. Inventory/rewrites are future outputs. |
| PI-18 | PASS | Architecture plan, guide handoff and REM G2/DI-36 require authored canonical Chat/CLI/Runtime/shared architecture, all eight READMEs, diagrams, source/schema/metadata mapping, representative verified examples and fresh content review beyond checkers. Future live documents need not exist now. |

## All-package disposition audit

All listed pyprojects were parsed as data, without package imports. The detailed dependency/extra/script evidence is in `source-evidence.json`.

| Row | Package | Independently assessed disposition |
|---|---|---|
| P-01 | Core | Neutral contracts/factory forwarding; existing lazy Memory edges disclosed; no new backend policy. |
| P-02 | Tools | Conversion/document extra plus narrow text/cache/wrapper changes; separate document-reader adoption. Existing Finance dependency confirmed. |
| P-03 | Commands | Pure parser, no dependency/launcher/root API expansion; shared registry separate from frontends. |
| P-04 | Memory | Ingestion/admission/identity/recovery/consumer impact broadest; current LLM dependency carries proposed counter extra. |
| P-05 | LLM | Shared capability/preparation/count/result guards; schema additions and optional counter support, no selector redesign. |
| P-06 | Chat | Maintained registry/file pipeline, packaged templates, wiring/outcomes/recovery; current placeholder and 2048-character slicer verified as source. |
| P-07 | Runtime | Existing Memory/Agent/Transcript/MCP composition; DI multi-agent/extraction and real tool-discovery anchors confirmed. |
| P-08 | CLI | Runtime compatibility wrapper; no console script. Conditional origin/readiness edits plus required tests/docs. |
| P-09 | Agent | Declared Memory/LLM dependency; consumer/task completion proof, no production-source allocation. |
| P-10 | Telemetry | Existing schema/reasons preserved; adaptation assigned to Chat, conditional tests only. |
| P-11 | Transcript | Existing v1/persistence retained; aggregate v2 belongs to Chat/Memory. |
| P-12 | MCP | Transport unchanged; full extra includes Agent/Tools, so transitive counter effects are accurately qualified. |
| P-13 | Optimization | Declared Memory dependency confirmed; inheritance/import proof without invented active source route. |
| P-14 | Finance | Tools dependency relation confirmed; no Docling execution prerequisite or financial feature change. |
| P-15 | Speech | Core dependency confirmed; no ordinary document/tokenizer requirement introduced. |
| P-16 | Sandbox | Separate Docker execution package; document filesystem sandbox remains Tools-owned. |
| P-17 | Moltbook | HTTP/Pydantic dependencies; conditional configured import/registration checks, no ingestion feature assignment. |

## Scores (independent sums, not averaged)

| Coverage dimension | Earned / maximum |
|---|---|
| Inventory/source/dependency/test classification | 3.0 / 3.0 |
| Behavior/configuration/data effects | 2.0 / 2.0 |
| Shared ownership/deployment consequences | 2.0 / 2.0 |
| Boundaries/compatibility/required proofs | 2.0 / 2.0 |
| Readiness/approval completeness | 0.8 / 1.0 |
| **Coverage total** | **9.8 / 10** |

| Overall dimension | Earned / maximum |
|---|---|
| Accuracy against current scope/source | 2.8 / 3.0 |
| Architecture/bounded delivery | 2.0 / 2.0 |
| Data/configuration/dependency safety | 2.0 / 2.0 |
| Evidence/future distinctions/reproducibility | 1.3 / 1.5 |
| Readability/approval/change control | 1.3 / 1.5 |
| **Overall total** | **9.4 / 10** |

Deductions reflect the stale current-state instructions and their effect on reproducible review routing/change control. Substantive technical planning coverage is strong. Scores do not waive the mandatory PI-16 failure. Optional advisories: none additional; unresolved technical qualification remains the already-required Gate-A work, not a new current-plan defect.

## Reproduced checks, inspected evidence and limits

Reproduced: request/input hashes; opening/closing identity; five-path correction diff; annex/companion equality and log-prefix comparison; package-member/row equality; selected AST parsing; all five administrative checks. Board validate passed (36 tasks); dashboard current; lifecycle passed (1,037 Markdown files); metadata passed (18 pyprojects including root); whitespace check passed. Exact wrapped argv/exits and receipt paths follow below.

Inspected only: current technical requirements and declarations/source/test anchors. Source observations include Chat files.py placeholders, adapters.py:383–385 slicing and :1740–1742 pool selection; app.py Chat registry use; selected shared command delegates; CLI commands.py registry/arg and three docstring-only placeholder modules; Runtime di.py:285–375 composition and tool_loading.py:59–85 real import discovery; Core profiles and transcript lazy imports; Memory assembler.py:398–427 unowned current background task, vector adapter clients, collection embedding calls, synthesis roles and BackupManager defaults; Tools wrapper imports; MCP preparation/publication control points. Selected test/LLM/Commands files parsed successfully as AST, with declarations recorded in source-evidence.json. One exploratory rg operand (`commands/shared_handlers.py`) did not exist; actual delegation files were subsequently located as pilot.py, session_views.py, diagnostics.py and memory_queries.py. That search limitation is not product evidence.

No tests, product imports, builds, installs, resolution, downloads, live providers/models, user stores or documents were executed/accessed. No upstream model/version/security assertion was independently network-qualified; these were assessed as pinned planning requirements with explicit future qualification. Source inspection was selected and static, not exhaustive dynamic consumer proof. No semantic-quality or installed interoperability conclusion follows. Root Ruff534, collection collision and legacy formatting/MAINT oracle failures remain unwaived and were not rerun. Full case inventory, rewritten tests, authored live architecture/guides and actual model/installed witnesses remain intentional construction/readiness outputs.

## Exact integrity and Git/administrative commands

All commands below exited 0. Plain source/file reads used cat, sed, rg and standard-library Python only; no product execution. Inline metadata/AST and byte-comparison probes also exited 0, with evidence retained in the files named above. The exploratory missing-path rg diagnostic is disclosed above (the containing read batch exited 0).

```text
shasum -a 256 /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/round4/inputs/review-request.json
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/verify_identity.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/round4/inputs/review-request.json /tmp/independent-r4-7aekkkfq opening.json
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/verify_identity.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/round4/inputs/review-request.json /tmp/independent-r4-7aekkkfq closing.json
```

Receipt: `/tmp/independent-r4-7aekkkfq/command-1794418339236330000.json`; exit 0

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /tmp/independent-r4-7aekkkfq -- git diff c96ecbea685a2627e033d3a9cb62a2f05b72afb7..56a495b76e7b7f8a967633bf523dfa9c30f9ed73 -- docs/planning/active/command-refactor/package-impact-assessment.md docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md docs/planning/active/command-refactor/test-migration-plan.md docs/planning/active/command-refactor/command-architecture-update-plan.md docs/planning/active/command-refactor/guide-update-handoff.md
```

Receipt: `/tmp/independent-r4-7aekkkfq/command-1794418360970337000.json`; exit 0

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /tmp/independent-r4-7aekkkfq -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate
```

Receipt: `/tmp/independent-r4-7aekkkfq/command-1794418361124954000.json`; exit 0

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /tmp/independent-r4-7aekkkfq -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check
```

Receipt: `/tmp/independent-r4-7aekkkfq/command-1794418361741221000.json`; exit 0

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /tmp/independent-r4-7aekkkfq -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py
```

Receipt: `/tmp/independent-r4-7aekkkfq/command-1794418361802280000.json`; exit 0

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /tmp/independent-r4-7aekkkfq -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py
```

Receipt: `/tmp/independent-r4-7aekkkfq/command-1794418361843564000.json`; exit 0

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /tmp/independent-r4-7aekkkfq -- git diff --check 8390f3688d00985b1cac0443da8105f33fb1a6b7..56a495b76e7b7f8a967633bf523dfa9c30f9ed73 -- docs/planning
```

Receipt: `/tmp/independent-r4-7aekkkfq/command-1794418452157487000.json`; exit 0

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /tmp/independent-r4-7aekkkfq -- git show c96ecbea685a2627e033d3a9cb62a2f05b72afb7:docs/planning/active/command-refactor/embedding-compatibility-contract.md
```

Receipt: `/tmp/independent-r4-7aekkkfq/command-1794418452186280000.json`; exit 0

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /tmp/independent-r4-7aekkkfq -- git show c96ecbea685a2627e033d3a9cb62a2f05b72afb7:docs/planning/active/command-refactor/proposals/tools-document-adoption.md
```

Receipt: `/tmp/independent-r4-7aekkkfq/command-1794418452213674000.json`; exit 0

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /tmp/independent-r4-7aekkkfq -- git show c96ecbea685a2627e033d3a9cb62a2f05b72afb7:docs/planning/active/command-refactor/execution-log.md
```

Formal report: `/tmp/independent-r4-7aekkkfq/formal-report.md`. Its SHA256 is delivered separately to avoid a self-referential digest. No additional review is authorized by this report.
