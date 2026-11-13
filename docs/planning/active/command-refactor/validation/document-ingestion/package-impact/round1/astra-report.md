# Astra independent package-impact document review — round 1/4

**CHANGES_REQUESTED** — two medium-severity mandatory documentation findings.
Coverage **9.0/10**; overall **9.1/10**. Neither satisfies the 9.5 gate.

Reviewer: Astra, GPT-6 Astra, high reasoning effort, 2026-11-11. Fresh single-seat read-only review; no builder reasoning, peer verdicts, nested delegation, repairs or shared writes. No memory files consulted. Shared-checkout exception explicitly authorized by the request. All generated artifacts are in this report's private external directory.

Workdir: `/Users/chuckrussell/Dev/gendev/agent-framework`.
Branch: `feature/cmd-ingest-001`.
Base: `8390f3688d00985b1cac0443da8105f33fb1a6b7`.
Candidate: `72ef265a981ef968a773172661bb512ddfd7da5e`.
Assessment: `docs/planning/active/command-refactor/package-impact-assessment.md`, SHA256 `df73594bd39c64190552b7e7e1d3deced9c73d49e09a24405711051492affb60`.

## Scope and conclusion

The complete 159-line assessment was reviewed against the frozen REM, normative embedding-compatibility contract, Tools companion, PI criteria, current-controls snapshot, package declarations and selected relevant implementation seams. All 17 package rows occur exactly once; the eight proposed implementation packages (CLI conditional) and nine source-unchanged packages are correctly classified. The basic architecture, dependencies, approval boundary and division between INGEST and TOOLS-DOC are sound.

The document does not yet expose two material existing obligations for the maintainer's package-impact decision: multi-agent consumer compatibility and the document conversion/counting worker's execution/cancellation boundary. Generic FC/DI references do not replace their inclusion in the package-impact summary. The findings require only bounded additions to this assessment; the technical contracts already specify both behaviors. No technical redesign or new construction authority is requested.

Future Gate-A qualification, installed normal/optimized execution, genuine-format/model proofs, precise signatures and exact final allowlists remain intentionally pending. Their absence is not scored as missing implementation evidence in this document review.

Reference shorthand below: **A** = assessment; **REM** = `docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md`; **EC** = `docs/planning/active/command-refactor/embedding-compatibility-contract.md`; **TD** = `docs/planning/active/command-refactor/proposals/tools-document-adoption.md`. Source paths are relative to the workdir.

## Mandatory findings

### PI-R1-ASTRA-001 — Medium — multi-agent impact is omitted

**Requirement:** PI-09 explicitly requires Agent/multi-agent consumers with correct ownership and error obligations; PI-02 requires material planned effects to be included. EC:38–39 distinguishes authorization visibility namespaces from physical embedding spaces. EC:156 and FC-13 (497 onward) require the multi-agent controller/coordinator/journal to retain visibility and truthful failed/partial-commit reporting. EC:565 names the integration proof.

**Affected text:** A:56,59,72 and the rest of the package tables. The Agent row describes archive/extraction and tools, but neither it nor the actual Memory/Runtime owner rows names the multi-agent consumer, its shared physical embedding space or visibility/partial-commit contract.

**Independent source evidence:** `packages/friday-runtime/src/friday_runtime/di.py:310–336` constructs `MultiAgentMemoryController`, `PromotionCoordinator` and `PromotionJournal` on the existing Memory controller. `packages/friday-memory/src/friday_memory/multi_agent/controller.py:54–63` delegates recall then filters visibility; its private/shared writes delegate to Memory. `multi_agent/coordinator.py:123–193` performs graph then insight writes, journals intermediate progress and records failure. These are concrete consumers of the planned shared guard; they are not an absent future route or a new Agent-package feature.

**Risk:** A maintainer can approve the displayed package impact without seeing the operational effect on multi-agent visibility and partially completed promotions, or incorrectly infer that separate visibility namespaces allow different physical embedding spaces.

**Bounded correction:** Add an explicit compatibility disposition to P-04/P-07 or a short linked cross-package paragraph: multi-agent controller/coordinator/journal are Memory-owned and assembled by Runtime, share the admitted physical space, preserve authorization visibility and observable failure/partial progress, and require FC-13 B/N/R integration proof. Their algorithms/source remain unchanged unless an exact separately reconciled allowlist permits a necessary adaptation. Do not put them under an invented Agent source edit or promise transactionality.

**Recheck:** Read the revised assessment against EC:38–39,156,497–525,565 and the cited source; verify ownership, physical-space/visibility distinction, positive and refusal evidence, and no expanded source authorization. Then repeat full PI coverage on the new frozen candidate. No product test is required for this document correction.

### PI-R1-ASTRA-002 — Medium — conversion-worker and cancellation impact is omitted

**Requirement:** PI-02 requires material planned effects; PI-10 requires wiring/task impacts to be exposed. REM:1059–1080 requires off-event-loop conversion/OCR/audit/repeated counting, an owned bounded worker without provider/store capability, admission held through worker quiescence, cancellation preventing late ingestion, and no hard-kill/OS-sandbox claim. DI-11 and DI-26 require the corresponding future responsiveness/cancellation proofs.

**Affected text:** A:54,57–59,123. The tables mention extraction ownership, background extraction shutdown and resource limits, but never the distinct document worker, command admission lifetime, cancellation behavior or late-result disposal. Existing conversation extraction task ownership is a different obligation.

**Independent source evidence:** `packages/friday-chat/src/friday_chat/commands/registry.py:669–704` calls synchronous `SmartFileReader.read` directly inside the async handlers before awaiting ingestion. `commands/files.py:44–61,122–131` currently supplies binary placeholders. Replacing that with real conversion creates the execution impact already specified by REM. `packages/friday-chat/src/friday_chat/adapters.py:363–407` shows the separate ingestion/storage handoff. `packages/friday-memory/src/friday_memory/context/assembler.py:398–428` shows that conversation extraction is a separate inner-task path; the report does not confuse those two obligations.

**Risk:** The table understates Chat's orchestration change and the observable cancellation/busy behavior of the proposed heavier document stack, including the requirement that a cancelled conversion cannot later store data.

**Bounded correction:** Add a concise statement in the Chat row or a cross-package execution paragraph: owned conversion/audit/counting work runs off the event loop, the worker has no provider/store capability, command admission remains held until quiescence, cancelled results cannot be ingested, and responsiveness/cancellation/resource limits require DI-11/26 proof. Tie the shared converter and counting roles to Tools/LLM without assigning a new scheduler/runtime engine. Keep numeric limits and final file allocation as Gate-A/directive outputs.

**Recheck:** Compare the revised summary with REM:1059–1080 and DI-11/26; verify it is distinct from FC-06 extraction task shutdown, retains the no-hard-kill/no-transaction promises, and adds no source permission. Repeat full PI review on a new frozen candidate.

## PI-01–16 matrix

| Criterion | Result | Evidence and assessment |
|---|---|---|
| PI-01 | PASS | A:5–10,53–80; static comparison of all `packages/*/pyproject.toml` directory names with P-01–17 returned 17 unique exact matches. Direct source changes, inherited extras and test obligations are distinguished. |
| PI-02 | FAIL | Ownership/path categories generally match REM's proposed paths and TD's companion allowlist; the material effects in findings 001/002 are absent. No unauthorized new source package was found. |
| PI-03 | PASS | A:53–60 preserves neutral Core, Tools conversion, pure Commands arguments, Memory policy, LLM execution and Chat/Runtime composition. Core profiles' current lazy imports and Tools smart_read's injected controller confirm why the proposed interface direction matters. |
| PI-04 | PASS | A:29–38,54,127 explicitly separates shared capability/text storage from ReaderFactory/smart_read document routing. TD delivery sequence and source factory/smart_read paths support the distinction. |
| PI-05 | PASS | A:54,57–60,76–94,122–123 accurately describes Chat's extra, bare Tools, Certifi floor, counter extra and inherited headless effects. All 17 pyprojects inspected; Commands has no dependencies, Memory already pins LLM and tiktoken, Tools already pins Finance. No installed proof claimed. |
| PI-06 | PASS | A:57,101–106,124; EC B01–08 and FC-10/14. Packaged templates select memory/maintenance Nomic profiles with placeholder revision; LLM schema currently has batch/cache options only. Baseline qualification and replacement positives remain required; Qwen is illustrative. |
| PI-07 | PASS | A:56,58,107–112,125–126 summarizes binding, same-dimension refusal, old-data preservation, /read, graph propagation and recovery versions without migration/redesign. Current strict Memory/Chat v1 models substantiate separate v2 additions. See advisory on making graph route distinctions easier to find. |
| PI-08 | PASS | A:54–58,95–100; REM active routes and D. Source character slicer and smart_read cache/storage paths confirm actual changes. Shared document/512 and strategy overrides are distinct from unsplit structured/derived records; no invented URL/automatic route. |
| PI-09 | FAIL | Agent, MCP, Transcript, telemetry and metadata owners are represented at A:58,72–75; multi-agent is missing (001). Existing telemetry reason literals and Chat memory_mcp callback support the stated no-schema-change boundary. |
| PI-10 | FAIL | A:56,58–60 adequately covers startup admission, origin, extraction logging/tasks and profile isolation, supported by Core profiles, Runtime di, CLI container and packaged rejection-log path. Distinct document-worker task/wiring effects are omitted (002). |
| PI-11 | PASS | A:56,58,74–75,126; EC causal boundary/FC-02/03. Backup public signatures/defaults and current copy behavior were inspected, not exercised. Pending snapshots, marker protection and FU-013/014 remain bounded and unwaived. |
| PI-12 | PASS | A consistently labels future changes/evidence and separates technical-design history from assessment approval. EC proof nodes and REM DI obligations remain future. Minor reference-range advisory below does not defeat explicit FC-01–14 coverage. |
| PI-13 | PASS | A:46–49,84–94,118–128 exposes exact versions/assets/licenses/resource limits, model/counter qualification, signatures and final paths as unresolved readiness outputs. No qualification success inferred. |
| PI-14 | PASS | A:12–16,130–154 agrees with pinned current-controls exact maintainer condition: “I won't approve the construction directive unless I'm satisfied with the overall per-package impact of our planned approach.” Single approved version/commit/hash binding and renewed review for material changes are explicit; remaining conditions are not presumed complete. |
| PI-15 | PASS | A tables provide concrete purpose, change type, retained behavior and future evidence. Memory's relative breadth is clear, no invented effort estimate/version-upgrade claim. Completeness defects are counted under PI-02/09/10. |
| PI-16 | PASS | Opening/closing identities PASS; request/helper/input/document hashes match. All required admin checks pass; navigation targets exist; execution-log comparison is append-only. Current fields came only from the pinned safe snapshot. Technical reports were not used as correctness evidence. |

## All-package source/dependency disposition audit

| Packages | Independent evidence used |
|---|---|
| Core / Commands | Both pyprojects; Core `profiles.py` factory implementation; REM neutral contracts and file_inputs allowlist. Commands remains dependency-free; no root API expansion proposed. |
| Tools | Pyproject legacy documents/spreadsheets/all-formats extras and required Finance; `filesystem/readers/factory.py` legacy reader registrations; `filesystem/smart_read.py` small/large/cache and injected storage; TD exact companion boundary. |
| Memory | Pyproject LLM/tiktoken/Chroma dependencies; vector adapter, CollectionManager, synthesizer query-role/callable paths; assembler task; multi_agent controller/coordinator; backup/analyzer; strict recovery models. Planned ingestion, admission, graph, extraction, lifecycle, recovery and public-wrapper categories checked against every REM allowlist row. |
| LLM | Pyproject; model_library EmbeddingOptions/profile declarations and embeddings query/document/cache/batching implementation. Counter/guard additions remain prospective. |
| Chat | Pyproject; packaged config/model templates (not dirty top-level YAML); registry/files/adapters; memory_mcp; aggregate recovery contracts. Confirms placeholder/character-split replacement, current pool defaults, log location and separate recovery ownership. |
| Runtime / CLI | Both pyprojects; Runtime di storage/controller/extractor/multi-agent assembly and real tool_loading discovery; Core profile branch; CLI default/env/for_testing forwarding and Runtime delegation. |
| Agent | Pyproject Memory dependency; `base.py:500–520` outer extraction scheduling confirms inner task completion is separate. |
| Telemetry / Transcript | Pyprojects, actual telemetry MCP reason declaration, Chat strict aggregate's TranscriptSnapshotManifest reference; unchanged schemas and independent persistence match EC. |
| MCP | Pyproject optional full profile and `server/tools_mode.py:75` lazy Tools import; transport unchanged, affected Memory/Chat ownership correct. |
| Optimization | Pyproject direct Memory dependency; targeted source import search. Its inherited counting dependency is a declaration effect, not a newly asserted active algorithm. |
| Finance / Speech / Sandbox / Moltbook | All pyprojects plus scoped source dependency searches. Finance's tool wrappers live in Tools; Speech depends on Core; Sandbox/Moltbook have no new Memory/Docling edge. No feature edits inferred. |

The permitted-path table also includes tests/fixtures, READMEs, lock changes and planning records. These are represented as future cross-package work at A:113–128. New files cannot be source-inspected before construction; their intended purposes were checked against REM/TD. This is a document review with selected source tracing, not an exhaustive dynamic consumer discovery or execution audit.

## Separate advisories

1. Replace stale inclusive-looking `DI-01–33` references at A:58,157 with `DI-01–34` where intended. REM includes DI-34's framework-wide requirement. The explicit all-FC references and inventory obligations already preserve that requirement, so this is a reference precision improvement, not an additional mandatory finding.
2. A short sentence under Memory would improve graph readability: maintained Chat/Runtime recall stays unscored; identity-safe graph comparison/fallback is a public injected capability. EC FC-08 already supplies the binding rule; the assessment does not assert new scoring.
3. Explicitly naming admission-before-SQLite-read behavior for the legacy analyzer would make Memory's broad row more informative. The generic direct-consumer/admission/FC obligations currently incorporate it; this suggestion does not authorize algorithm repairs.

## Independent scores

| Coverage category | Award / maximum | Rationale |
|---|---:|---|
| Inventory and source/dependency/test classification | 2.8 / 3.0 | Exact package inventory; missing explicit multi-agent consumer disposition. |
| Material behavior/configuration/data effects | 1.5 / 2.0 | Strong store/config/recovery coverage; omitted worker/cancellation impact. |
| Shared ownership and deployment consequences | 1.9 / 2.0 | Correct dependency direction and extras; incomplete multi-agent ownership visibility. |
| Boundaries, compatibility, proofs | 1.8 / 2.0 | Clear B/N/R and unit separation; omitted concrete consumer/execution obligations. |
| Readiness and approval completeness | 1.0 / 1.0 | Exact approval condition and future gate separation. |
| **Coverage total** | **9.0 / 10** | No upward adjustment to meet the target. |

| Overall category | Award / maximum | Rationale |
|---|---:|---|
| Accuracy against current scope/source | 2.6 / 3.0 | Accurate represented effects; two material omissions. |
| Architecture and bounded delivery | 1.8 / 2.0 | Good separation; execution boundary absent from summary. |
| Data/configuration/dependency safety | 1.8 / 2.0 | Good identity/qualification safeguards; cancellation consequence not exposed. |
| Evidence/future distinctions/reproducibility | 1.5 / 1.5 | Frozen request, repeatable admin checks and no false runtime claims. |
| Readability and approval/change control | 1.4 / 1.5 | Useful compact tables; minor precision opportunities. |
| **Overall total** | **9.1 / 10** | Mandatory findings independently prevent VERIFIED. |

## Integrity and evidence limits

The request's SHA256 was verified before reading: `ff7c61995d8964b7f88e549d56debc1fb670b1cfed6ce6a5d2622ad583de3c76`. Helpers were hashed before execution: read_only_command `3acff26f4fdfff2351faec29115a1c13a076ccdf2a72756c3ce7f333712c037d`; verify_identity `c4d9bf96ac6abc85ac7acd84ace0ed7966fcc0f3db921ed67d0e4477d9c78452`; current-controls `46511406110780981c7e454c4ee6a22ea7081e0fd9038a8ea62deac000faf9bb`.

Opening and closing helper runs both exited 0/PASS: candidate and branch matched, logical index before status was `db380f0067ad7338d28a7976cae3a734bb48f385c9cf9d6db4c7e8f2246a9f4d`, 17,694 protected files and six preserved metadata entries checked, no errors. Staging stayed empty. Status remained exactly the two modified Chat example YAML files and untracked `.friday-old/`. The helper performed required hashes of protected content; their contents were not displayed or used as review evidence. No supplied scratch was written.

Reproduced: hashes/identity, administrative checks, exact package inventory, local link-target existence and append-only execution-log comparison. Inspected: frozen technical requirements and selected source/metadata, not runtime behavior. No product tests/imports/builds, installs, dependency resolution, network/model/provider/store operations or live state inspection were performed. Existing root Ruff534, root test_display collection collision and legacy formatting/MAINT oracle failures remain unwaived and were not rerun. No whole-repository-green claim. Prior technical council verdicts are historical routing metadata only; no peer reports were read.

Two exploratory source probes used incorrect guessed paths/globs and were corrected using scoped file discovery: nonexistent Chat file_reader.py/command_registry.py produced rg diagnostics; nonexistent Agent agents/*.py and Core telemetry/*.py globs produced zsh diagnostics. Actual files were subsequently inspected. These are search errors, not product/admin failures and receive no test credit.

## Required command receipts

All Git/admin commands below ran via the verified wrapper with this private scratch. Full argv, cwd, stdout, stderr and exit codes are retained in adjacent `command-*.json`. Opening/closing JSON files are adjacent. Wrapper redirects UV/XDG/TMP/MYPY caches to private scratch and disables bytecode/Git optional locks.

`python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-astra-gasso2ge -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate`

Exit: 0. Receipt: `command-1794404227345983000.json`.

`python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-astra-gasso2ge -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check`

Exit: 0. Receipt: `command-1794404227506977000.json`.

`python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-astra-gasso2ge -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py`

Exit: 0. Receipt: `command-1794404228248484000.json`.

`python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-astra-gasso2ge -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py`

Exit: 0. Receipt: `command-1794404228311725000.json`.

`python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-astra-gasso2ge -- git diff --check 8390f3688d00985b1cac0443da8105f33fb1a6b7..72ef265a981ef968a773172661bb512ddfd7da5e -- docs/planning`

Exit: 0. Receipt: `command-1794404228353551000.json`.

`python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-astra-gasso2ge -- git diff --stat 8390f3688d00985b1cac0443da8105f33fb1a6b7..72ef265a981ef968a773172661bb512ddfd7da5e`

Exit: 0. Receipt: `command-1794404273009328000.json`.

`python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-astra-gasso2ge -- git show 8390f3688d00985b1cac0443da8105f33fb1a6b7:docs/planning/active/command-refactor/execution-log.md`

Exit: 0. Receipt: `command-1794404273038413000.json`.

`python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/verify_identity.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/round1/inputs/review-request.json /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-astra-gasso2ge opening.json` — exit 0, PASS.

`python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/verify_identity.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/round1/inputs/review-request.json /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-astra-gasso2ge closing.json` — exit 0, PASS.

Administrative results: board validation passed (36 tasks); dashboard current; documentation lifecycle passed (1020 Markdown files); package metadata passed (18 pyprojects including root); scoped whitespace check passed. All required command exits are 0.

This report grants no maintainer satisfaction, Gate-A activation, construction, acceptance or delivery authority. Recheck the bounded document corrections on a newly frozen candidate; do not repair product code or amend technical scope under these findings.
