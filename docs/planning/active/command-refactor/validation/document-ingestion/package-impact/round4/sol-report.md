# Independent read-only review — round 4 of 4

**CHANGES_REQUESTED** — candidate `56a495b76e7b7f8a967633bf523dfa9c30f9ed73`, branch `feature/cmd-ingest-001`.

Reviewer: GPT-6.1 Sol, high reasoning effort, 2026-11-11. Workdir: `/Users/chuckrussell/Dev/gendev/agent-framework`. This is this seat's independent current-document readiness/source-feasibility review. No builder reasoning, raw peer reports, current peer verdicts, memory lookup, nested delegation or repairs were used. Historical labels in the expressly permitted technical inputs supplied no correctness credit. No accidental prohibited report/verdict exposure occurred. The pinned safe controls were used instead of raw authority/navigation/history contents. No extra round, reissue or replacement was started.

The technical corrections PC-05/06/07 are present and materially sound. One mandatory current-state inconsistency remains. Both scores are independently computed below; the overall score is below 9.5 and the mandatory finding independently prevents VERIFIED. The four-round cap is exhausted. Return to Chuck for guidance, without another automatic review or repair cycle.

## Mandatory finding

### 1. R4-SOL-001 — medium — current closing directive still sends the reader to v0.3 / round 3

Requirement: PI-16 requires current-state consistency; the request and correction-cycle2.json require v0.4, final round 4 of the same four-total-round budget, with three rounds consumed and no replacement/fifth round. This is an operative next-step instruction, not an allowed historical provenance label.

Affected text: `docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:1401–1408`, headed “Next decision”, instructs review of “assessment v0.3” and “Fresh round 3”. The same current REM at lines 21–28 specifies v0.4/final round 4. Independently, the hash-verified safe `current-controls.json` has a `current_scope` referring to v0.3/round3 and two rounds already used, whereas its `next_gate` and `package_impact_assessment.council` correctly specify v0.4/round4 and three consumed. No raw authority content was read to establish this discrepancy.

Risk: a maintainer or controller following the closing instruction or current-scope field can select the wrong reviewed bytes or miscount the remaining review allowance. Correct opening prose and structural validation do not reconcile contradictory operative instructions.

Exact bounded correction: align the REM's closing next decision with v0.4, the present fourth/final round, three prior rounds consumed, and the stop-for-Chuck outcome if requirements are unmet. Reconcile the canonical current-scope field represented in the safe snapshot and regenerate its safe view/pins through the authorized controller. Retain historical records and the existing four-total-round cap; add no source owner, product feature, readiness effect or construction authority.

Recheck: text-check the corrected current REM closing instruction against its opening, the exact request/correction-cycle2 requirements and a freshly hash-bound safe controls snapshot. Reproduce applicable board/dashboard/lifecycle/whitespace checks and integrity verification only under subsequent explicit maintainer disposition. This report does not authorize another full council round. This finding requires documentation/control consistency only, with no product/test/configuration implementation.

## Correction delta first

The raw delta reviewed was exactly `c96ecbea685a2627e033d3a9cb62a2f05b72afb7..56a495b76e7b7f8a967633bf523dfa9c30f9ed73` over the request's five paths, with no routing, report, board, authority or log diff displayed.

| Correction | Independent result |
| --- | --- |
| PC-05 | Satisfied in assessment opening and approval/change-control section: old conditional approval binds `e1c90753a3e2876df0f9f6f0ca82b1893455266cee1f252276f460b48a9f2a16`; final directive must bind amended REM and final assessment bytes. Stale frozen-REM claim removed. Current REM hash is `b7ded08d9166da2173399c2b178c33b7176846959d2e08c3e5f3292993393187`. Annex and companion were independently byte/hash compared to delta base and are unchanged. |
| PC-06 | Satisfied in REM G1 and test plan reconciliation: explicitly incorporated case-level final-directive entries are named exceptions; general permission is insufficient; unmapped bodies, public signatures/classes and named FC nodes remain protected except exact approved equivalent mapping. Every valid requirement retains executed coverage. Annex final preservation paragraph remains unchanged. |
| PC-07 | Satisfied in architecture plan item 2, REM G2 and guide handoff: three qualified registries, CLI arg, actual Chat registry use and placeholder CLI REPL/main/server modules are explicit acceptance obligations. Current source confirms distinct registry classes, public CLI export, docstring-only placeholder modules and actual Chat registry. |
| Scoped ancillary corrections | Present: conditional test-only consumer suites/root cohort test; actual Runtime test_di and focused Memory anchors; eight README obligations; narrow executive/feature-catalogue coverage; membership-derived 17 count. No additional production owner introduced. |

## Complete PI-01–18 matrix

PASS here means sufficient current planning requirement/evidence, not completed implementation, model qualification, installed proof or maintainer approval. Source evidence is text/AST only.

| Criterion | Result | Independent evidence and assessment |
| --- | --- | --- |
| PI-01 | PASS | Assessment P-01–17 lists exactly 17 unique member packages, eight proposed implementation rows including conditional CLI, nine source-unchanged consumer rows. Root workspace `members=['packages/*']` and 17 actual member pyprojects reproduce the inventory; 18 metadata files includes the root. |
| PI-02 | PASS | REM ownership/proposed exact paths and assessment rows preserve named scope. Test-only consumer scope does not create production ownership. Final path/signature resolution and stop-on-expansion are explicit. |
| PI-03 | PASS | REM ownership/active-route tables, assessment Core/Tools/Commands/Memory/LLM/Chat/Runtime rows and architecture items 1–6 retain neutral contracts, injection and headless reuse. Existing Core lazy Memory imports and legacy Tools/Memory edges are disclosed. Core profiles source confirms lazy adapter factories. |
| PI-04 | PASS | P-02 and basis distinguish INGEST converter/text-storage corrections from companion ReaderFactory/smart_read document routing. Companion delivery sequence and TD-01–10 require separate public-consumer proofs. No shared dependency implies adoption completion. |
| PI-05 | PASS | Assessment dependency consequences, REM A, FC-12 and member metadata support default Chat extra, optional Tools profile, Certifi floor and inherited Memory/LLM counting without headless Docling. Commands declares no dependencies; extras and exact assets remain future work. |
| PI-06 | PASS | Assessment model/upgrade/readiness sections and REM E/annex B01–B08 require preserved pool/non-pool selection and positive B/N operations. Chat adapters:1735–1760 confirms pool default and non-pool hosted fallback. Runtime DI extraction service selection is separate. Unqualified hosted baseline stops Gate A; Qwen is illustrative. |
| PI-07 | PASS | Assessment data consequences and REM identity/recovery/upgrade sections distinguish same-dimension identity, explicit absent destinations, associated graph/WAL, preserved legacy state, /read and strict versions. Current MemorySnapshotManifest and Chat RecoveryBundleManifest are Literal[1], making separately named v2 handoff planning concrete. No reset/migration or broad recovery redesign. |
| PI-08 | PASS | Assessment defaults, REM D and active routes specify document/512 with independent overrides, source/derived boundaries and unsplit structured MCP/maintenance records. Current Chat character slicer and Tools smart_read cache/storage seams confirm affected behavior. No maintained URL-ingest claim or second split. |
| PI-09 | PASS | P-09–12 and cross-package section identify Memory multi-agent ownership/Runtime assembly, Agent/background consumers, metadata errors and MCP receipt/telemetry/transcript obligations. Runtime DI creates the multi-agent stack; FC-02/06/13 demand actual public-path witnesses without transport/schema expansion. |
| PI-10 | PASS | P-04/06/07/08, worker effects, REM admission and FC-01/06/09/10 require zero pre-admission side effects, owned tasks/logging, profile isolation and truthful partial errors. Core profile factory, Runtime DI:245–307 and CLI container demonstrate the current wiring seams. CLI edits stay conditional; metadata declares no CLI launcher. |
| PI-11 | PASS | P-12/readiness, REM backup paths and FC-03/13 keep backups/MCP causal, protect the live marker, retain old public/default semantics and separate FU-013/014 failures from positive proof. Tools inspection source:134 corroborates the legacy search defect; no repair is inferred. |
| PI-12 | PASS | Assessment future-evidence table, REM DI-01–36, annex proof matrix and plans consistently require future source/installed/normal/optimized/B/N/R evidence. Checks reproduced here establish administrative validity only; no prior score or fake document fixture is credited. |
| PI-13 | PASS | Assessment details-to-settle table and REM A freeze concrete versions, backends, counters, model identity, assets/licenses, numeric resource budgets, APIs and final paths before construction. Unsupported qualification is a stop, not inferred compatibility. |
| PI-14 | PASS | Assessment opening and approval steps require explicit Chuck satisfaction with exact post-Gate-A version/commit/hash, required referenced appendix and separate exact directive approval. Safe controls record impact satisfaction/Gate A/construction as not granted. The stale instruction is separately captured by PI-16. |
| PI-15 | PASS | All package rows give purpose, concrete change classification, retained behavior and proof references, with broadest Memory impact stated without invented effort estimates or completed-upgrade claims. README work is scoped across all eight implementation owners. |
| PI-16 | FAIL | Opening/closing identity, pins, unchanged normative bytes, append-only log and preserved state pass. Current REM closing decision and safe current_scope contradict the current round/version; mandatory R4-SOL-001. Current council status otherwise remains in_review and prior labels are not credited. |
| PI-17 | PASS | Test plan dispositions, per-package matrix, required baseline inventory and incorporated case-level exception mapping; REM G1/DI-35 preserve executed valid requirements, immutable accepted evidence, FC gate witnesses, public contracts and no silent skip/assertion loss. Focused Memory/Runtime anchors exist. Full inventory/rewritten tests are intentionally future directive/construction outputs. |
| PI-18 | PASS | Architecture plan/guide handoff/REM G2 and DI-36 require canonical command-execution document, actual Chat/CLI/Runtime/shared flows, diagrams, all eight READMEs, narrow guide changes, source/schema/metadata map, verified examples and fresh independent content review. Structural checks alone explicitly insufficient; live authored outputs are future work. |

## All-package disposition audit

All 17 member pyprojects were read as TOML; proposed extras are absent today and are properly described as future changes. No package-level feature upgrade is inferred from transitive dependencies.

| Package row | Disposition checked against current declarations/source and governing plan |
| --- | --- |
| P-01 Core | Neutral contracts/factory propagation + scoped tests/README; current Core depends on Telemetry and retains lazy Memory adapters. |
| P-02 Tools | Converter/extra/text-storage/cache + tests/README; current Finance dependency and legacy documents/spreadsheets extras retained; companion routing separate. |
| P-03 Commands | Pure new file_inputs + tests/README; current zero dependencies/API54 preservation remains. |
| P-04 Memory | Broad shared policy/admission/vector/graph/recovery/task seams + LLM extra/tests/README; current Chroma/NetworkX/tiktoken graph disclosed. |
| P-05 LLM | Capability/preparation/counting/result schema + narrow extra/tests/README; existing LiteLLM/resilience dependency stays. |
| P-06 Chat | Four-format delegation/config/extra/receipts/recovery + tests/README/templates; only maintained chat launcher remains. |
| P-07 Runtime | Same factories/config origin/profile/task wiring + tests/README; current DI owns assembly, extraction and multi-agent construction. |
| P-08 CLI | Conditional compatibility forwarding + tests/README; current container delegates RuntimeKernel; no launcher or independent client. |
| P-09 Agent | Production unchanged; declared Memory dependency inherits counter support; actual archive/tools/task proof retained. |
| P-10 Telemetry | Production/schema unchanged; existing reason mapping at Chat boundary; conditional test-only adaptation. |
| P-11 Transcript | Production/v1 unchanged; current persistence/receipt contracts and independent settings retained; aggregate v2 owned elsewhere. |
| P-12 MCP | Production transports unchanged; full extra inherits Agent/Memory; transport-only metadata has no Memory/Docling edge. |
| P-13 Optimization | Production unchanged; declared Memory dependency inherits counters; no new algorithm or claimed active route. |
| P-14 Finance | Production unchanged; ordinary Finance independent of document execution; Tools already declares Finance. |
| P-15 Speech | Production unchanged; Core/Pydantic/PyYAML dependencies support no new document prerequisite. |
| P-16 Sandbox | Production unchanged; Docker execution package distinct from Tools-owned FilesystemSandbox conversion checks. |
| P-17 Moltbook | Production unchanged; HTTPX/Pydantic declarations; conditional import/tool compatibility only. |

The migration plan permits conditional test-only consumer changes in P-10–17; exact nodes freeze before any rewrite. Root cohort metadata coverage remains explicit. The guide plan enumerates eight package READMEs and limits executive/feature-catalogue changes to affected claims. Current executive summary's in-place collection-rebuild wording is an appropriate future rewrite target, not a required live edit in this planning review.

## Separate rubrics

| Coverage component | Earned / maximum | Basis |
| --- | --- | --- |
| All-package inventory/classification | 3.0 / 3.0 | Complete metadata-backed inventory with conditional source/test distinctions. |
| Behavior/configuration/data effects | 2.0 / 2.0 | Material defaults, compatibility and legacy-state consequences explicit. |
| Ownership/dependency/deployment | 2.0 / 2.0 | Neutral/shared ownership and profile inheritance accurately scoped. |
| Boundaries/compatibility/proofs | 1.9 / 2.0 | Strong full proof plan; closing current-round instruction remains inconsistent. |
| Readiness/approval completeness | 0.8 / 1.0 | Pending gates explicit; stale current_scope/next decision detracts from completeness. |
| **Coverage total** | **9.7 / 10** | Independent component sum; mandatory finding still controls. |

| Overall component | Earned / maximum | Basis |
| --- | --- | --- |
| Scope/source accuracy | 2.8 / 3.0 | Technically sound planning; present-round/version contradictions remain. |
| Architecture/bounded delivery | 2.0 / 2.0 | Authored canonical architecture, narrow ownership and companion boundaries. |
| Data/configuration/dependency safety | 2.0 / 2.0 | Preserved-state and explicit readiness/identity controls. |
| Evidence/future distinctions/reproducibility | 1.4 / 1.5 | Appropriate reproducible checks and deferred proofs; stale decision wording. |
| Maintainer readability/approval/change control | 1.2 / 1.5 | Operative closing instruction/current_scope cannot be followed consistently. |
| **Overall total** | **9.4 / 10** | Independent sum; no averaging with coverage or other seats. |

## Advisories

None additional. Exact Gate-A qualification, model quality evaluation when selected, case inventory, authored guides and installed proofs remain planned future obligations, not newly discovered current-plan deficiencies. Baseline Ruff534, root test_display collision, formatting/MAINT oracle debt and FU-013/014 remain unwaived and were not rerun or repaired.

## Reproduced commands and evidence

Request SHA256 was computed before reading and matched `b9b11c7c95c7fe0f6c30c66e665597aa54456b04d6cd81675ce5d9877d085601` (exit 0). Every request pin, helper pin and protected-manifest hash matched before helper execution. Helpers were read first. Plain reads/TOML/AST operations used Python standard library and shell text readers only; no product/test import or execution.

Opening and closing verify_identity.py calls both exited 0/PASS: candidate and branch exact, logical index hashed before status `2b13729afb8065137e0f9e7fc5c1079be3249313b8a406c5d649ccab5a093d0f`, 17,730 protected files, six preserved metadata records, zero errors. This covers dirty examples without displaying contents, raw authority hash-only, unchanged index/staging/status and preserved unrelated state. Expected status remained the two modified Chat YAML files and untracked .friday-old directory. No user-state content was inspected.

All Git/admin commands below ran through the pinned wrapper with this reviewer's fresh external scratch, never supplied caches. Receipt JSON files alongside this report retain exact argv, cwd, stdout/stderr and exit codes. Historical log content was compared as bytes privately, never displayed or semantically inspected. Annex and companion old/current hashes match their request pins; execution-log old bytes are a prefix of current bytes (append-only), with old SHA256 `89023bbeae1e559c2f73c1e16431806556d9ad5a96ed36ff120814bd5800f146` and current `d39abf03d630299ea6cfb3cd4c4d41fef0fcf0a8015b2f16b005cc9da9773dc6`.

Administrative results reproduced: board validation passed 36 tasks; dashboard current; lifecycle checked 1,037 Markdown files; metadata validated 18 pyprojects; scoped whitespace check clean. These results do not establish semantic current-round consistency. Source evidence was independently inspected as text; thirteen selected modules were additionally parsed with AST and recorded in source-ast-inventory.json. No inherited test receipt was treated as reproduced runtime proof.

### Exact check commands / exits

```text
shasum -a 256 /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/round4/inputs/review-request.json
exit 0
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/verify_identity.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/round4/inputs/review-request.json /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/independent-ingest-r4-kywxszs7 opening.json
exit 0 / PASS
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/verify_identity.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/round4/inputs/review-request.json /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/independent-ingest-r4-kywxszs7 closing.json
exit 0 / PASS
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/independent-ingest-r4-kywxszs7 -- git diff c96ecbea685a2627e033d3a9cb62a2f05b72afb7..56a495b76e7b7f8a967633bf523dfa9c30f9ed73 -- docs/planning/active/command-refactor/package-impact-assessment.md docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md docs/planning/active/command-refactor/test-migration-plan.md docs/planning/active/command-refactor/command-architecture-update-plan.md docs/planning/active/command-refactor/guide-update-handoff.md
exit 0
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/independent-ingest-r4-kywxszs7 -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate
exit 0
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/independent-ingest-r4-kywxszs7 -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check
exit 0
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/independent-ingest-r4-kywxszs7 -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py
exit 0
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/independent-ingest-r4-kywxszs7 -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py
exit 0
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/independent-ingest-r4-kywxszs7 -- git diff --check 8390f3688d00985b1cac0443da8105f33fb1a6b7..56a495b76e7b7f8a967633bf523dfa9c30f9ed73 -- docs/planning
exit 0
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/independent-ingest-r4-kywxszs7 -- git show c96ecbea685a2627e033d3a9cb62a2f05b72afb7:docs/planning/active/command-refactor/embedding-compatibility-contract.md
exit 0
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/independent-ingest-r4-kywxszs7 -- git show c96ecbea685a2627e033d3a9cb62a2f05b72afb7:docs/planning/active/command-refactor/proposals/tools-document-adoption.md
exit 0
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/independent-ingest-r4-kywxszs7 -- git show c96ecbea685a2627e033d3a9cb62a2f05b72afb7:docs/planning/active/command-refactor/execution-log.md
exit 0
```

## Limits and authority

This review establishes document readiness and source feasibility only. It does not prove that the future Docling release/counter/model/assets/backend can satisfy the contract; those remain exact Gate-A stop points. No product/tests, builds, installs, dependency resolution/downloads, network/provider/model/store operations, user documents, dirty YAML contents or live guides were executed/read as prohibited. No checkout, Git metadata, board, authority, supplied scratch or shared file was written. All generated outputs/caches reside in this fresh reviewer scratch outside the checkout and supplied roots.

The stale current instructions are sufficiently localized to support CHANGES_REQUESTED rather than BLOCKED: candidate stability and governing round-4 authority are established and the defect is directly observable. Independence remains qualified. This outcome grants no maintainer package-impact satisfaction, Gate-A activation, construction, acceptance, publication or delivery authority. No further review round is authorized by this report.
