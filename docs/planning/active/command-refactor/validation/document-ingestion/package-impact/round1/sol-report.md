# INGEST-PACKAGE-IMPACT-001 — round 1, Sol independent document review

Outcome: **CHANGES_REQUESTED**. One mandatory medium finding, PI-R1-SOL-001. COVERAGE **9.40/10**; OVERALL **9.40/10**. Neither the no-findings gate nor the independent 9.5 thresholds pass.

Reviewer: Sol, gpt-6.1-sol, high reasoning effort; 2026-11-11. Fresh review seat; no builder reasoning, peer reports/verdicts, nested delegation or repairs used. This is a full package-impact document assessment, not implementation validation or a repeat technical-design council. No memory/history lookup was used.

Workdir: `/Users/chuckrussell/Dev/gendev/agent-framework`.
Branch: `feature/cmd-ingest-001`.
Base: `8390f3688d00985b1cac0443da8105f33fb1a6b7`.
Candidate: `72ef265a981ef968a773172661bb512ddfd7da5e`.
Deliverable: `docs/planning/active/command-refactor/package-impact-assessment.md` (assessment below).
Assessment SHA256: `df73594bd39c64190552b7e7e1d3deced9c73d49e09a24405711051492affb60`.
Reviewer scratch: `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-sol-j1mv5jna`.

## Integrity and authority

The request was hashed BEFORE its contents were read: SHA256 `ff7c61995d8964b7f88e549d56debc1fb670b1cfed6ce6a5d2622ad583de3c76`, exit 0. Verified helper hashes before execution: read_only_command.py `3acff26f4fdfff2351faec29115a1c13a076ccdf2a72756c3ce7f333712c037d`; verify_identity.py `c4d9bf96ac6abc85ac7acd84ace0ed7966fcc0f3db921ed67d0e4477d9c78452`. Current-controls `46511406110780981c7e454c4ee6a22ea7081e0fd9038a8ea62deac000faf9bb` and protected manifest `4274fd36222f495dc917554a43796241fe2773f1a81acbf88a55eebd7d5c10d4` also matched. These hash checks exited 0.

Opening and closing verify_identity.py both returned PASS, exit 0, with no errors: logical index BEFORE status `db380f0067ad7338d28a7976cae3a734bb48f385c9cf9d6db4c7e8f2246a9f4d`; candidate/branch/status/staging and all request pins matched; 17,694 protected files and six preserved metadata entries checked. Receipts: `opening.json`, `closing.json` in reviewer scratch. Expected status retained the two dirty Chat YAMLs and untracked `.friday-old/`; staged set empty. No restoration performed or needed.

Read AGENTS, the council/development-board skills and engineering/lifecycle/independent-validation policies. The explicit seat scope overrides the council skill's controller delegation workflow. Current authority fields came only from the pinned current-controls snapshot. Raw authority was hash-checked by the identity helper without displaying historical fields. No peer reports or raw historical authority were read. Prior technical readiness is routing history only and supplies no correctness evidence here.

The snapshot records design_only authority, implementation approval not granted, document council round 1/4 in review, assessment approval not granted, and no Gate-A or construction activation. Its exact condition is: “I won't approve the construction directive unless I'm satisfied with the overall per-package impact of our planned approach.” Assessment lines 12–16 and 141–154 preserve this condition and require the approved version/commit/SHA256 as a single referenced appendix. Other maintainer conditions are explicitly unresolved.

## Mandatory finding

### PI-R1-SOL-001 — Medium — multi-agent compatibility disappears from the package assessment

Affected text: assessment P-04/P-07/P-09 (lines 56, 59, 72) and readiness/proof summary (lines 118–128).

Requirement: PI-09 expressly requires Agent/**multi-agent**, metadata, telemetry/transcript and active MCP consumers with correct ownership and error/receipt obligations. The normative embedding-compatibility-contract.md lines 38–39 distinguish visibility namespaces from physical embedding spaces; line 156 explicitly inventories the multi-agent controller/coordinator/journal with shared underlying Memory space, preserved authorization visibility and honest failed/partial-commit reporting. FC-13, lines 496 onward, and its proof node at line 565 require actual multi-agent coverage. REM E's consumer inventory and DI-34 retain this obligation.

Observed: none of the 17 package rows or surrounding assessment text names multi-agent use, its shared-space constraint, visibility policy, coordinator/journal or partial promotion behavior. General references to all FC proofs do not expose this existing package impact to the maintainer. P-09 specifically lists ordinary Agent archive/tools/context behavior but does not account for this distinct consumer. P-07 omits Runtime's assembly responsibility for it.

Independent source evidence: Runtime `packages/friday-runtime/src/friday_runtime/di.py:309` defines `_create_multi_agent_stack`, constructs PromotionJournal/PromotionCoordinator and injects its existing MemoryController into MultiAgentMemoryController. These are Memory-owned classes, not new Agent-package source features. `packages/friday-memory/src/friday_memory/multi_agent/controller.py:55` delegates recall and filters visibility; private/shared writes use policy checks. `multi_agent/coordinator.py:103` exposes partial-commit forensics; `execute_promotion` writes graph then insight/vector state and records intermediate journal states before commit, returning failure on exceptions. New shared admission/embedding refusals can therefore affect observable multi-agent operations despite no planned edits to those algorithms.

Risk: the maintainer can approve a table that appears comprehensive while missing an explicitly required existing consumer and its compatibility/partial-result obligations. This is a document coverage omission, not a finding that the proposed implementation is defective.

Exact bounded correction: amend P-04 to name Memory's existing multi-agent controller/coordinator/journal as source-unchanged compatibility consumers of the shared guarded Memory space; amend P-07 to name Runtime's existing assembly of that stack, and optionally cross-reference from P-09. State that visibility namespaces remain authorization partitions, preserve visibility and honest failed/partial promotion reporting, require FC-13 B/N/R public-consumer evidence, and promise no new transaction, algorithm, coordinator/journal source edits or activation. Do not add an eighteenth package or expand the REM allowlist.

Recheck: freeze the revised document, verify current identity and pins, review the correction against the cited source and FC-13, then repeat the full bounded assessment/matrix and administrative checks. Actual multi-agent tests remain future implementation proofs; no test execution or product fix is requested now.

## PI-01–16 matrix

PASS below means document readiness for that criterion, not completed implementation or model qualification.

| Criterion | Result | Independent basis |
| --- | --- | --- |
| PI-01 | PASS | P-01–17 each occur once; 17 package directories/declarations match. Eight proposed source packages include conditional CLI; nine source-unchanged rows retain test/dependency obligations. Automated inventory receipt confirms uniqueness. |
| PI-02 | PASS | Rows map to REM ownership/proposed-path table and companion future allowlist. No unauthorized owner or source expansion asserted. Exact final files remain a readiness binding at line 128; CLI remains conditional. Multi-agent presentation omission is charged once under PI-09. |
| PI-03 | PASS | P-01–07 retain Core neutral contracts, Tools adapter, Commands parsing, Memory policy, LLM guards and composition roots. Existing Core lazy Memory imports and Memory lazy Tools chunker are source facts, so “no new dependency” is read narrowly. |
| PI-04 | PASS | Lines 29–38 and P-02 explicitly separate shared INGEST capability/text storage from ReaderFactory/smart_read document adoption. Companion TD proofs and explicit combined-scope revision retained. Factory and smart_read are independent source paths. |
| PI-05 | PASS | P-02/05/06, lines 84–94 distinguish new default Chat document closure, optional Tools profile, fixed Certifi floor and inherited narrow LLM counter extra. All 17 pyprojects inspected; present dependencies do not already declare those new extras. Versions/assets correctly pending. |
| PI-06 | PASS | P-05 and lines 101–106 preserve pool/non-pool roles, missing-field readiness and hosted-baseline uncertainty. Chat adapters.py:1735 selects pool default; packaged templates select separate named maintenance service. No Qwen activation; B/N success distinguished from refusal. |
| PI-07 | PASS | P-04/06/11 and lines 107–112, 125–126 cover identity, same-dimension mismatch, fresh selection, preserved old files, /read, graph/recovery and strict v1/v2 handoff. Recovery source still uses strict v1 models: proposed v2 is future work. No migration/backup redesign claimed. |
| PI-08 | PASS | P-03/04/06 and lines 95–100 distinguish document/512 policy, three strategies, source/derived/cache and unsplit structured records. Existing Chat character slicer and Tools cache/storage paths independently inspected. No absent URL/automatic route claimed or double split proposed. |
| PI-09 | FAIL | PI-R1-SOL-001: multi-agent consumer/ownership/visibility/partial-result obligation omitted. Agent, metadata inspection, telemetry/transcript and active MCP obligations are otherwise present in P-06/09–12 and dependency/readiness text. |
| PI-10 | PASS | P-04 explicitly identifies broadest impact; P-06–08 address admission-before-effects, task/log ownership, profile isolation, truthful counts and origin. Source assembler.py:420 drops an inner task today; assessment correctly describes ownership as a planned change. CLI constructor/re-exports delegate Runtime and no launcher is added. |
| PI-11 | PASS | P-04/06/12 and line 126 retain causal backup/MCP adaptation, exact snapshots/receipts/pending IDs, live-marker protection and unchanged defaults. FU-013/014 explicitly unwaived. No new backup engine or cleanup activation. |
| PI-12 | PASS | All assertions framed as planned; source/installed normal/optimized, B/N/R and real-format proofs remain future. Baseline debt retained; no prior council score used as conformance proof. Small reference-range advisory below. |
| PI-13 | PASS | Lines 118–128 expose versions/backends, hashes/licenses/assets, resource limits, signatures/backend limits, origin/recovery details and final allowlist. Qualification failure stops; absent future proofs are not current document defects. |
| PI-14 | PASS | Lines 12–16 and 130–154 preserve exact satisfaction prerequisite, remaining conditions, one canonical version/commit/hash directive binding and renewed review for material impact. Snapshot current controls agree. |
| PI-15 | PASS | Concrete row columns distinguish purpose, source/dependency/test type and retained behavior without invented effort or completed upgrades. Memory scope magnitude is candid. Source-unchanged packages have actual compatibility dispositions. |
| PI-16 | PASS | Opening/closing identities pass; all seven local assessment link targets exist (contents of linked peer reports deliberately unread). Scoped diff shows execution log +35/-0. Current routing agrees with pinned snapshot; technical contract pins unchanged. Protected state unchanged. |

## All-package disposition cross-check

All package pyproject.toml files were read as text; no resolution/import occurred. Direct declarations here are current source; new extras are proposed.

| Row | Package | Source/dependency/test conclusion |
| --- | --- | --- |
| P-01 | Core | Neutral source/interfaces/factory changes; existing Telemetry dependency, lazy Memory adapters; no new converter/counter dependency. |
| P-02 | Tools | Shared conversion and existing text-storage/cache changes, new optional document extra; separate companion routing. Current direct Finance dependency confirmed; Memory storage injection introduces no new declared Memory edge. |
| P-03 | Commands | Pure parsing source/tests; current dependencies empty. |
| P-04 | Memory | Broad policy/admission/role/recovery/task changes; existing pinned LLM dependency will request counter extra; current tiktoken retained pending overlap proof. Multi-agent omission requires correction. |
| P-05 | LLM | Capability/schema/guard source and narrow optional counter extra; plain imports lazy. |
| P-06 | Chat | Composition, commands, templates, recovery, errors/tests/docs; existing Tools pin will request document extra by default. Packaged templates were read; dirty root examples were not. |
| P-07 | Runtime | Assembly/config changes; inherits counters through Memory, no direct Tools/document dependency. Actual import-discovery witness correctly required. Multi-agent assembly needs explicit assessment mention. |
| P-08 | CLI | Conditional forwarding/source tests, existing Runtime/Memory dependencies inherit counters; no project.scripts launcher. |
| P-09 | Agent | Source unchanged, focused consumers/tests; direct Memory/LLM dependencies inherit support. Ordinary extraction/tools are correctly listed. |
| P-10 | Telemetry | Source/schema unchanged; Chat maps existing MCP reason vocabulary. |
| P-11 | Transcript | Source/v1 unchanged, no model counter dependency; receipt/persistence compatibility and aggregate handoff tests. |
| P-12 | MCP | Transport unchanged; full optional profile can inherit Agent/Tools dependencies. Snapshot adaptation owners remain Chat/Memory. |
| P-13 | Optimization | Existing direct Memory dependency inherits counters; source/algorithms unchanged. |
| P-14 | Finance | Core dependency; Tools already depends on Finance; no new ordinary Docling requirement. |
| P-15 | Speech | Core/config dependencies, no Memory/LLM dependency introduced; unchanged configured import/registration checks. |
| P-16 | Sandbox | Docker/Pydantic package unchanged; Tools filesystem sandbox remains conversion admission owner. |
| P-17 | Moltbook | HTTP/Pydantic package unchanged; configured tool/import compatibility, no embedding feature assigned. |

## Separate advisories

A-01 (low, optional): assessment lines 58/157 cite DI-01–33 although the current REM also has DI-34. The assessment already binds all FC-01–14, so this is a traceability cleanup, not an additional missing proof or mandatory finding. Prefer DI-01–34 in the summary references.

A-02 (low, optional): a short clarification near P-04 could distinguish maintained unscored graph recall from public-injectable graph scoring, as FC-08 does. The current summary does not actually claim new scoring wiring, so no violated requirement is assigned.

## Independent scores

| COVERAGE rubric | Earned / maximum | Reason |
| --- | --- | --- |
| Inventory/source/dependency/test classification | 2.85 / 3.0 | Complete package count; one important consumer presentation gap. |
| Material behavior/config/data | 1.80 / 2.0 | Strong namespace/recovery/config coverage; missing multi-agent visibility/partial outcomes. |
| Ownership/deployment | 1.95 / 2.0 | Accurate central ownership and inherited extras; multi-agent assembly not exposed. |
| Boundaries/compatibility/proofs | 1.85 / 2.0 | Correct deferred proof model; missing named consumer and small reference imprecision. |
| Readiness/approval completeness | 0.95 / 1.0 | Honest pending qualification and exact satisfaction/change control. |
| **Total** | **9.40 / 10** | Independent document coverage score. |

| OVERALL rubric | Earned / maximum | Reason |
| --- | --- | --- |
| Accuracy against scope/source | 2.80 / 3.0 | Predominantly source-accurate, required multi-agent obligation missing. |
| Architecture/bounded delivery | 1.90 / 2.0 | INGEST/companion and neutral shared ownership preserved. |
| Data/config/dependency safety | 1.90 / 2.0 | Strong fresh-store and dependency distinctions; incomplete visibility/partial-state presentation. |
| Evidence/future work/reproducibility | 1.40 / 1.5 | Static readiness vs future proofs explicit; precise source mapping can improve. |
| Readability/approval/change control | 1.40 / 1.5 | Useful concise table and exact approval boundary; one consumer omitted from decision input. |
| **Total** | **9.40 / 10** | Independent quality score, no threshold inflation. |

## Reproduced evidence, commands and limits

All Git/admin invocations used the supplied wrapper, except opening/closing identity whose verified helper owns its read-only Git. Environment uses GIT_OPTIONAL_LOCKS=0 and PYTHONDONTWRITEBYTECODE=1. Wrapper caches/tmp paths point only into this reviewer's scratch. No product tests/imports/builds, installs/resolution/downloads, network/providers/models/store operations occurred.

The protected-manifest helper hashes protected content without presenting forbidden contents. No dirty YAML contents, actual stores, exports contents, .friday-old contents, peer report archives or builder transcripts were inspected. Static source inspection is not proof that proposed APIs/conversion/guards work.

Reproduced: five required administrative checks below, opening/closing identities, all-package metadata text examination, package-row/local-link inventory and static AST examination of 106 relevant existing source files. `source-ast-inventory.json` records hashes/imports/definitions/call targets; `assessment-inventory-links.json` records 17 unique rows and seven existing local targets. Source AST parsing executes no product code. Selected function bodies were also read for Chat/Runtime assembly, file placeholders/chunking, smart_read caches, Core/CLI factories, MCP/recovery/backup/analyzer, LLM embeddings and multi-agent operations. A source inventory is not dynamic exhaustive-route proof.

Inspected only: complete current REM/annex/companion and criteria/iteration authorization, assessment, packaged templates, declarations and safe current controls. Future DI/TD/FC/B/N/R, installed normal/optimized, real-model and genuine-format proofs were not reproduced or credited as completed. Earlier technical verdicts were not used. Root Ruff534, test_display collision and legacy formatting/MAINT baseline failures remain unwaived and were not rerun. No whole-repository-green claim.

Exact reproducible command prefixes:

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/verify_identity.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/round1/inputs/review-request.json /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-sol-j1mv5jna opening.json
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/verify_identity.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/round1/inputs/review-request.json /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-sol-j1mv5jna closing.json
```

Both exits 0. Request SHA command was `shasum -a 256` followed by the absolute request path above, exit 0. Plain cat/sed/rg/nl/wc reads and Python stdlib hash/AST/inventory scripts were used for static inspection; no source execution. Agent archive mechanics were not dynamically established and receive no implementation credit. Static AST enumeration skips nonexistent paths rather than treating them as inspected source.

No maintainer satisfaction, construction approval, Gate-A activation, acceptance, push, publication or delivery authority is granted by this report. Bounded document correction and a fresh frozen review are the next review actions; this seat performed no repair.

## Exact wrapped command receipts

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-sol-j1mv5jna -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate
```

Exit 0; receipt `command-1794404246169685000.json`.

```text
Development board validation passed: 36 tasks
```

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-sol-j1mv5jna -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check
```

Exit 0; receipt `command-1794404246331776000.json`.

```text
Planning dashboard is current
```

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-sol-j1mv5jna -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py
```

Exit 0; receipt `command-1794404246962708000.json`.

```text
Documentation lifecycle validation passed: 1020 Markdown files checked
```

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-sol-j1mv5jna -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py
```

Exit 0; receipt `command-1794404247019491000.json`.

```text
Validated 18 pyproject.toml files: version, license, authors, README, URLs, wheel package selection, and internal pins OK
```

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-sol-j1mv5jna -- git diff --check 8390f3688d00985b1cac0443da8105f33fb1a6b7..72ef265a981ef968a773172661bb512ddfd7da5e -- docs/planning
```

Exit 0; receipt `command-1794404247049410000.json`.

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-sol-j1mv5jna -- git diff --stat 8390f3688d00985b1cac0443da8105f33fb1a6b7..72ef265a981ef968a773172661bb512ddfd7da5e -- docs/planning
```

Exit 0; receipt `command-1794404286146584000.json`.

```text
 docs/planning/README.md                            |   2 +-
 docs/planning/active/command-refactor/README.md    |  13 ++
 .../active/command-refactor/authority.json         |  55 ++++++-
 .../active/command-refactor/execution-log.md       |  35 +++++
 .../planning/active/command-refactor/next-phase.md |   5 +-
 .../command-refactor/package-impact-assessment.md  | 159 +++++++++++++++++++++
 .../active/command-refactor/tactical-plan.md       |   5 +-
 .../document-ingestion/branch-handoff.md           |   2 +-
 .../document-ingestion/gate-a-handoff.md           |  21 ++-
 .../package-impact/iteration-authorization.json    |  55 +++++++
 .../package-impact/review-criteria.md              |  60 ++++++++
 docs/planning/board.yaml                           |  18 ++-
 12 files changed, 415 insertions(+), 15 deletions(-)
```

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/pi-r1-sol-j1mv5jna -- git diff --numstat 8390f3688d00985b1cac0443da8105f33fb1a6b7..72ef265a981ef968a773172661bb512ddfd7da5e -- docs/planning/active/command-refactor/execution-log.md
```

Exit 0; receipt `command-1794404333358085000.json`.

```text
35	0	docs/planning/active/command-refactor/execution-log.md
```
