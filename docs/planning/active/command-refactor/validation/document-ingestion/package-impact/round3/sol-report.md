# Round 3 Sol independent document review

**VERIFIED — current documents only.** No mandatory findings. Coverage **9.70/10**; overall **9.60/10**. These are independent rubric totals, not inherited scores. They do not waive requirements or provide approval.

Reviewer: Sol seat, GPT-6.1 Sol, high reasoning, Codex harness; 2026-11-11. Fresh read-only review, round **3 of the same maximum 4**, with two earlier rounds consumed. No delegation, repairs, repository writes, installs, product/test execution, downloads, providers, models or stores. Shared checkout exception is explicitly authorized by the request. All generated evidence is in reviewer-owned `/tmp/pi-r3-sol-tq13f4gr` (resolved `/private/tmp/pi-r3-sol-tq13f4gr`), outside the checkout and both supplied roots.

Workdir `/Users/chuckrussell/Dev/gendev/agent-framework`; branch `feature/cmd-ingest-001`; candidate `c96ecbea685a2627e033d3a9cb62a2f05b72afb7`; amendment base `f591989e5f0253be71e113df79a6a8af4e43521c`. Administrative whitespace range begins at `8390f3688d00985b1cac0443da8105f33fb1a6b7`.

## Inputs and ordering

The very first operation hashed the request before reading it. SHA256 matched `475c9d6328e975e0b4fbaf4c9fec561da71e4790ff08f158d19c63a07e9faed2`. Helper/current-controls/protected-manifest hashes were verified before running either helper. Opening verify_identity passed before substantive review. The amendment diff was then obtained with exactly request.review_diff_paths. Primary amendment content was examined before the full current assessment, REM, annex, companion, migration and architecture/guide requirements. Historical authorization/report content was not displayed; routing changes were selectively examined without score-bearing history. Raw authority and board history were hash-only; the supplied safe current-controls supplied current authority. No peer reports, builder transcripts or private reasoning were read. Linked historical carry-forward requirements were inspected only as pending constraints, with no verdict/score credit.

The amendment adds first-class test restructuring and authored documentation requirements; it changes no production source, tests, workspace pyproject or lock bytes between amendment base and candidate. The annex and companion were independently hash-compared against their amendment-base Git blobs and remain unchanged. The amended REM is a new review input; no former result was extended to its new bytes.

Repository-relative references below use packet prefix `docs/planning/active/command-refactor/`. `PIA` means `package-impact-assessment.md`; `REM` means `remediation/REM-CMD-INGEST-001-pdf-docx.md`; `TMP` means `test-migration-plan.md`; `ARCH` means `command-architecture-update-plan.md`; `GUIDE` means `guide-update-handoff.md`; `ANNEX` means `embedding-compatibility-contract.md`; `TOOLS` means `proposals/tools-document-adoption.md`. References denote inspected text, not execution receipts.

## Amendment assessment first

The authorization record `validation/document-ingestion/test-doc-revision-authorization.json` records the exact two maintainer choices, no budget reset and no implementation authority. PIA:56–130, REM:G1/G2 and DI-35/36, TMP:18–115 and ARCH:11–98 give them operative planning content.

Tests may be retained, renamed/moved/split, rewritten/replaced, retired with a governing reason, or added. The final directive freezes baseline cases/fixtures and old/new node, requirement, oracle and retirement mappings before rewriting. Valid requirements need substantive executed replacement coverage; selectors/imports must follow moved nodes; uncalled/unawaited helpers, assertion counts, broad skips/xfails and production guard bypasses cannot substitute for proof. API54 and unchanged v1/public contracts retain their expectations. Historical receipts remain immutable. ANNEX's retained-assertion wording is reconciled by explicit final-directive exceptions and REM G1's higher-priority amendment; it does not require retaining obsolete test bodies.

The future canonical architecture path is explicit. Required content covers actual Chat command lookup/delegation/effects, CLI/Runtime roles, shared ownership, dependency/installation and data consequences, request/admission/resource diagrams and reuse limits. GUIDE names affected chapters; REM:1260–1262 names architecture/navigation, guides and affected package READMEs. ARCH:81–98 and DI-36 require actual content review, source/schema/metadata mapping, representative verified examples and fresh independent review beyond links. Future case-level inventory, canonical architecture and rewritten guides are intentional construction/readiness outputs; their absence now is not a finding.

## Complete mandatory matrix

| Criterion | Outcome | Independent evidence and reasoning |
| --- | --- | --- |
| PI-01 | PASS | PIA:64–97 contains exactly P-01–17: eight proposed owners including conditional CLI, nine production-source-unchanged consumers. A text/metadata comparison found 17 unique names exactly matching all 17 package pyprojects. TMP:41–75 separately accounts for test effects in each package. |
| PI-02 | PASS | PIA package rows and readiness table trace to REM ownership/active-route/allowlist tables, DI-01–36, ANNEX FC-01–14 and TOOLS TD-01–10. New test/doc scope is explicitly bounded in REM:1259–1262; no additional production owner is authorized. CLI necessity and exact files remain final-directive outputs. |
| PI-03 | PASS | PIA P-01–08; REM:104–195; ARCH:19–49. Neutral Core contracts, Tools conversion, Commands parsing, Memory policy, LLM preparation/limits and Chat/Runtime composition remain separate. Core profiles.py:56–117 currently imports Memory lazily; Tools smart_read.py:181–218 and 588 onward show existing injected/lazy Memory seams, correctly disclosed as legacy edges rather than a new desired dependency cycle. |
| PI-04 | PASS | PIA basis/P-02 and REM active-route table distinguish shared converter/text storage from ReaderFactory/smart_read document routing. TOOLS delivery sequence and TD-01–10 require separate public-entry proofs/directive. Installing the extra or completing Chat extraction is explicitly insufficient. |
| PI-05 | PASS | PIA:161 onward, P-02/04/05/06/07/08/09/12/13; REM A and FC-12. All current pyprojects inspected: Tools has legacy document/spreadsheet extras but no proposed extra yet; Chat currently requests plain Tools; Memory requests pinned LLM; Runtime/CLI/Agent inherit Memory; Optimization declares Memory; MCP full inherits Agent. Commands dependencies are empty. Planned extras/Certifi floor/assets are future qualified outputs, with plain imports kept lazy. |
| PI-06 | PASS | PIA P-05 and existing-configuration/readiness rows; REM E; ANNEX B01–B08 and qualification rules. Existing pool default, separate extraction/maintenance bindings, omitted optional fields and hosted baseline uncertainty are retained. Chat adapters.py:1740 onward selects embedding_pool.default_service. LLM model-library test:169–185 asserts existing target/resilience behavior. Positive baseline and replacement proofs are required separately from refusals; Qwen remains illustrative. |
| PI-07 | PASS | PIA model/data/upgrade text and P-04/06; REM:833–1051 and 1079–1201. Identity includes preparation/artifact, so equal dimensions do not suffice. Explicit absent coherent destinations, matching reopen and /read availability are clear. Strict Memory-v2/Chat-v2/Transcript-v1 handoff, unchanged old v1 interpretation and same-incarnation rollback are scoped. Existing recovery_models.py and Chat reorganization/contracts.py declare strict v1 models, grounding the need for separate new types. No reset/migration/backfill is promised. |
| PI-08 | PASS | PIA ingestion configuration and P-02/03/04/06; REM D/active routes; TMP P-02/04/06. Document/512 and independent command→YAML→built-in precedence are explicit. Source plans differ from unsplit summaries/MCP/maintenance records, caches bind destination as well as model, and accepted plans are not split twice. Existing Chat adapters.py:376–405 still character-slices; the plan explicitly replaces that path. No URL-ingest or generic automatic route is invented. |
| PI-09 | PASS | PIA P-09–13 and multi-agent/graph bullets; ANNEX FC-02/06/08/13. Source Memory multi_agent/controller.py and coordinator.py owns visibility/promotion; Runtime di.py:310 onward assembles it. tests_memory/test_multi_agent.py:71–305 exercises authorization and partial-journal behavior. Transcript v1 and telemetry literals remain unchanged. Real root MCP integration test uses production Memory/Transcript and mixed calls, supporting the named affected family. |
| PI-10 | PASS | PIA P-04/06/07/08 and worker section disclose broad Memory impact, admission, owned logging/tasks, teardown and explicit origin. ContextAssembler assembler.py:398–429 currently starts an inner task without the proposed status ownership. Runtime di.py:245–281 currently constructs graph parent/storage, grounding required pre-effect admission/profile work. CLI container.py:70–126 and 173 delegates Runtime with default-derived path risks; changes remain conditional and preserve constructors. CLI pyproject has no launcher. |
| PI-11 | PASS | PIA backup/MCP and readiness rows; ANNEX FC-02/03/13; REM recovery/operator sections. Existing BackupManager signatures/default destination and copy semantics are preserved, new binding evidence cannot overwrite live markers, and no broader physical-backup repair is assigned. MCP snapshots remain one exact record with retained receipts/pending IDs and existing telemetry vocabulary. FU-013/014 and root debt are explicitly unwaived and gain no positive credit. |
| PI-12 | PASS | PIA references and future-tense obligations; REM DI-01–36; ANNEX named integration matrix/B/N/R; ARCH acceptance. Source/installed normal/optimized proofs and call-phase controls are future requirements. This review reproduced only administrative/hash/static checks. No old score or current static check is asserted to prove implemented extraction or compatibility. |
| PI-13 | PASS | PIA:235–249; REM A; ARCH verified-example row; TMP map. Versions/wheels/licenses/assets/numeric resources, exact local counters, serving identity, signatures/receipts, collection encoding, CLI necessity and exact allowlist remain concrete readiness outputs. Unsupported baseline qualification stops readiness; no guessed model/extra/API is presented as selected success. |
| PI-14 | PASS | PIA:251–282 and safe current-controls expressly retain Chuck's exact post-readiness version/commit/SHA satisfaction and separate construction-directive approval. Edits invalidate old-hash satisfaction; material changes return for review. Gate A needs separate activation. Council does not supply any of these approvals. |
| PI-15 | PASS | PIA package tables state types, concrete purpose, limits and required proofs; broadest Memory impact and indirect dependencies/test effects are visible. No invented time/cost/effort estimates or completed package-upgrade claims. Scope is dense but understandable with the companion plans. |
| PI-16 | PASS | Opening/closing identity PASS, 17,720 protected files, six preserved metadata entries, all pins and logical index exact; raw authority hash checked without history reads. Execution log is byte-prefix append-only (25 added/0 deleted lines). 46 local file links in primary inputs resolve. Board/dashboard/lifecycle/metadata/whitespace checks all exit 0. Safe controls and current routing say in_review, original round3/4, no implementation approval; prior results are not extended. |
| PI-17 | PASS | TMP dispositions/all17 families/map/acceptance; PIA:99–114; REM:1315,1321–1347. Representative test AST/text proves real anchors exist. Chat fake-extension positives, smart_read direct storage/cache doubles, LLM short-vector doubles, Core interface tests, Runtime TESTING fixtures, CLI config tests and multi-agent visibility tests justify focused rework. Root integration/installed/oracle obligations survive. Initial full case map remains required before rewriting; current plan does not pretend it exists. |
| PI-18 | PASS | ARCH:11–98; GUIDE:20–55; PIA:116–130; REM:1260–1262,1316,1349–1367. Canonical future command-execution.md, substantive chapters/package/schema examples, diagrams and actual content/source/metadata review are required. Guide README currently states alpha3 and architecture README reserves current/accepted architecture; provenance rules correctly prevent representing this unbuilt plan as current implementation. |

## Findings and advisories

**Mandatory findings: none.** There are no PI-R3-SOL-NNN mandatory corrections or rechecks required for this frozen planning candidate.

**PI-R3-SOL-001 — low, optional editorial advisory.** PIA:253–255 calls the REM “frozen” and says REM/annex/companion are not rewritten to add a navigation link. Its basis and approval paragraphs already correctly explain that the REM has been amended and requires this fresh review; this wording is not an authority defect. Risk: a skim reader could mistake “frozen” for the former technically reviewed bytes. Optional bounded document change on a future authorized revision: say “current amended REM” and retain the narrow no-navigation-only-rewrite explanation for the unchanged annex/companion. Recheck the sentence against the basis and current-controls; no product/test work is involved. This advisory is not a violated PI criterion or permission to edit the candidate now.

Readiness risks remain explicit obligations rather than hidden defects: hosted baseline immutable-identity qualification may fail; selected Docling/audit/provenance/tokenizer behavior, resources and worker cancellation remain unmeasured; exact test inventory and authored documentation must be frozen and later executed/reviewed. The current plan properly stops for these outputs rather than claiming feasibility has been demonstrated dynamically.

## Independent rubrics

| Coverage component | Award | Maximum |
| --- | ---: | ---: |
| All-package inventory/source/dependency/test classification | 2.95 | 3.00 |
| Material behavior/configuration/data effects | 1.95 | 2.00 |
| Shared ownership/dependency/deployment consequences | 1.95 | 2.00 |
| Traceable boundaries/compatibility/required proofs | 1.90 | 2.00 |
| Unresolved readiness/approval completeness | 0.95 | 1.00 |
| **Total** | **9.70** | **10.00** |

| Overall component | Award | Maximum |
| --- | ---: | ---: |
| Accuracy against current scope/source | 2.90 | 3.00 |
| Architecture/bounded delivery | 1.95 | 2.00 |
| Data/configuration/dependency safety | 1.95 | 2.00 |
| Evidence/future-work distinction/reproducibility | 1.40 | 1.50 |
| Maintainer readability/approval/change control | 1.40 | 1.50 |
| **Total** | **9.60** | **10.00** |

Near-full credit reflects unusually explicit per-package effects, positive/refusal distinctions and amendment acceptance controls. Remaining room reflects dense cross-document navigation and the qualitative/static source-feasibility nature of this assessment; it is not a demand for premature implementation. No threshold was used to erase a finding. This seat meets the specified document-review threshold; it makes no claim about other seats or the council aggregate.

## Reproduced evidence, commands and limits

Every Git/admin invocation used pinned `read_only_command.py OWN_SCRATCH -- ARGV`, apart from verify_identity's explicitly owned internal Git calls. Wrapper supplies GIT_OPTIONAL_LOCKS=0, PYTHONDONTWRITEBYTECODE=1 and reviewer-owned UV/XDG/TMP/MYPY locations. No supplied cache/output path was used. Plain file/text/AST/hash inspection executed no repository imports. File/AST analyses used system Python with `-B`; application/test code was never executed.

Initial `shasum -a 256 <request>` exited 0 with the expected request digest. Helper-pin verification exited 0. Opening and closing exact helper invocation:

`python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/verify_identity.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/round3/inputs/review-request.json /tmp/pi-r3-sol-tq13f4gr LABEL`

LABEL was opening.json and closing.json; each exited 0/PASS, no errors. Logical index was hashed before status in both:
`f358ac6cda5fc01e4dd9fabddf94825bf1121d961f8d45c03e87b40cd3a7abf2`.
Branch/candidate matched the frozen request, staging was empty, and status was exactly the two modified Chat example YAML paths and untracked `.friday-old/`. Their contents were not inspected; helper hashes/metadata checks preserved them and exports. No restoration/cleanup was attempted.

All five requested administrative checks exited 0: board validate (36 tasks), board render --check (current dashboard), documentation lifecycle (1,033 Markdown files), package metadata (18 pyprojects including workspace root), and scoped Git whitespace. This proves those administrative properties only. The exact argv and exits for every wrapped command are appended below, with receipt filenames. Historical Git blob content was consumed solely for prefix/hash comparisons and is not reproduced here.

Additional static checks: 17-package exact set equality PASS; primary local-file links 46 checked, zero missing; selected test AST parsing PASS with node/line inventory saved as test-ast-inventory.json. AST case counts are inspection aids, not executed coverage credit. Representative source/test text is cited above; no exhaustive current case-level migration inventory or whole-framework dynamic audit is claimed.

Two exploratory source lookups initially guessed obsolete file locations (`friday_chat/files.py`, `friday_chat/commands.py`, and Agent `agents/interactive.py`) and reported missing paths. Package-local rg --files resolved the Chat locations to commands/files.py and commands/registry.py and Agent location to interactive.py. These were inspection-path misses, not product failures or blocked checks.

No root Ruff/tests/formatting/MAINT checks were executed. Root Ruff534, test_display collection collision and legacy formatting/MAINT oracles remain unwaived baseline debt. No model/provider/network/store/install/provisioning/format/OCR, B/N/R runtime, clean-installed, normal/-O, cancellation or substantive live-guide implementation result was reproduced. Existing source/tests were inspected as text/AST only. Administrative checks do not establish semantic correctness of future rewrites; DI-35/36 require that later independent evidence.

This report supplies document readiness for the exact current bytes. It grants no maintainer package-impact satisfaction, Gate-A activation, construction/test/product/live-guide implementation, human acceptance, publication, delivery or model choice authority.

## Exact wrapped command ledger

Wrapper prefix: `python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /tmp/pi-r3-sol-tq13f4gr --`.

- `git diff --unified=3 f591989e5f0253be71e113df79a6a8af4e43521c..c96ecbea685a2627e033d3a9cb62a2f05b72afb7 -- docs/planning/active/command-refactor/package-impact-assessment.md docs/planning/active/command-refactor/README.md docs/planning/active/command-refactor/next-phase.md docs/planning/active/command-refactor/tactical-plan.md docs/planning/active/command-refactor/validation/document-ingestion/gate-a-handoff.md docs/planning/active/command-refactor/validation/document-ingestion/branch-handoff.md docs/planning/active/command-refactor/validation/document-ingestion/package-impact/review-criteria.md docs/planning/active/command-refactor/validation/document-ingestion/package-impact/iteration-authorization.json docs/planning/active/command-refactor/validation/document-ingestion/package-impact/correction-cycle1.json docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md docs/planning/active/command-refactor/test-migration-plan.md docs/planning/active/command-refactor/command-architecture-update-plan.md docs/planning/active/command-refactor/guide-update-handoff.md docs/planning/active/command-refactor/validation/document-ingestion/test-doc-revision-authorization.json` — exit 0; receipt `command-1794417194137280000.json`.
- `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` — exit 0; receipt `command-1794417211584152000.json`.
- `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check` — exit 0; receipt `command-1794417211740171000.json`.
- `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py` — exit 0; receipt `command-1794417212410801000.json`.
- `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py` — exit 0; receipt `command-1794417212467156000.json`.
- `git diff --check 8390f3688d00985b1cac0443da8105f33fb1a6b7..c96ecbea685a2627e033d3a9cb62a2f05b72afb7 -- docs/planning` — exit 0; receipt `command-1794417212505777000.json`.
- `git diff --name-only f591989e5f0253be71e113df79a6a8af4e43521c..c96ecbea685a2627e033d3a9cb62a2f05b72afb7 -- packages tests pyproject.toml uv.lock` — exit 0; receipt `command-1794417292123106000.json`.
- `git diff --numstat f591989e5f0253be71e113df79a6a8af4e43521c..c96ecbea685a2627e033d3a9cb62a2f05b72afb7 -- docs/planning/active/command-refactor/execution-log.md` — exit 0; receipt `command-1794417292150585000.json`.
- `git show f591989e5f0253be71e113df79a6a8af4e43521c:docs/planning/active/command-refactor/execution-log.md` — exit 0; receipt `command-1794417292177770000.json`.
- `git show f591989e5f0253be71e113df79a6a8af4e43521c:docs/planning/active/command-refactor/embedding-compatibility-contract.md` — exit 0; receipt `command-1794417337218830000.json`.
- `git show f591989e5f0253be71e113df79a6a8af4e43521c:docs/planning/active/command-refactor/proposals/tools-document-adoption.md` — exit 0; receipt `command-1794417337249168000.json`.
