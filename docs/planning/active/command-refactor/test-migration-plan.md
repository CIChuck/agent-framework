# INGEST-001 — test migration and restructuring plan

Status: **required planning contract; implementation not authorized**, 2026-11-11.

Chuck explicitly permits affected tests to be renamed, split, replaced or retired
when obsolete, provided every still-valid behavioral requirement maps to retained
or replacement coverage and each retirement has a documented reason. Substantial
test rewrites are therefore planned work, not an accidental consequence to hide
under “run the tests.” This applies to changed contracts, fixtures, mocks,
snapshots, setup/admission and package boundaries as well as assertions.

The [REM](remediation/REM-CMD-INGEST-001-pdf-docx.md) and final construction
directive must bind this plan. No tests or product files are rewritten during
this planning revision. Existing accepted evidence and old commit snapshots
remain immutable; an obsolete expected behavior can be replaced in current
tests without rewriting the historical receipt that originally tested it.

## Required disposition for every affected test

| Disposition | Required reason and evidence |
| --- | --- |
| Retain | The behavioral requirement remains valid and its current test/setup still exercises it. Preserve its meaningful assertions; a passing old test is not sufficient if it now bypasses the public path. |
| Restructure | Rename, move or split a case/helper/file to reflect the new shared owner or fixture boundary. Map old node IDs to new ones and demonstrate that valid obligations still execute; update selectors, imports and documentation references. |
| Rewrite or replace | The implementation contract, fixture, expected result or oracle deliberately changes under an identified approved requirement. Record the old expectation, intended new expectation and substantive replacement witnesses. Do not preserve obsolete architecture through a mock or weaken production guards to keep an old fixture green. |
| Retire | The tested behavior is explicitly obsolete or redundant. Record the exact reason, governing change and replacement coverage or proof that the obsolete requirement no longer applies. Retirement does not excuse any still-valid requirement. |
| Add | A new contract or previously missing failure/consumer path requires new coverage. Identify the requirement and observable public behavior, including negative and integration witnesses where applicable. |

These permissions are limited to the affected INGEST/compatibility contracts.
They do not authorize an unrelated suite rewrite, permanent skips/xfails,
assertion deletion to conceal failures, weakened expectations, source suppressions
or a smaller suite presented as equivalent solely by test/assertion counts.
Fixture updates must still exercise real admission, exact dimensions/counting,
role preparation and failure propagation. No test-only production bypass is allowed.

Required DI/FC acceptance IDs and explicitly named integration witnesses remain
stable unless the final directive explicitly maps an approved replacement and
preserves the gate obligation. Legacy case names/files are not immutable. Root
API54 and other unchanged public contracts retain their literal expectations;
reorganizing an affected fixture does not authorize an API change.

### Reconciliation with the normative compatibility contract

The unchanged compatibility contract's final preservation clause retains old
public signatures/classes and assertion bodies except named final-directive
fixture/oracle exceptions. Chuck's recorded test-restructuring decision is the
narrow governing amendment to that test-body rule. Each case-level map entry
that the final approved directive explicitly incorporates is a named exception,
including an identified rename, move, split, replacement or justified retirement
and its retained/replacement behavioral obligations. The plan alone is not an
exception for an unidentified case. Unmapped body edits remain prohibited;
existing public signatures/classes remain retained. Named FC test nodes stay
unless an incorporated entry explicitly maps their approved equivalent while
preserving the named gate's executed coverage. Accepted evidence stays immutable.

## Per-package migration scope

The P IDs align with the [Package Impact Assessment](package-impact-assessment.md).
These are expected rework families, not a claim that every listed test must change
or that final case-level inventory is complete. The final directive identifies
exact existing/new paths and case IDs after readiness. Production-source-unchanged
packages may still need focused test/fixture rewrites; unrelated cases stay intact.

| Package | Expected test work and present anchors | Contract coverage to retain or establish |
| --- | --- | --- |
| P-01 Core | Restructure/extend `tests_core/test_interfaces.py` and affected profile/factory fixtures for typed ingestion, query/vector identity and explicit open intent. New contract tests where needed. | Neutral imports/dependencies; factory forwarding; immutable shapes and refusal ordering; no backend policy in contracts. |
| P-02 Tools | Rewrite affected `tests_tools/test_filesystem_readers.py`, `test_smart_read.py`, `test_memory_tools.py` fixtures/assertions; add shared document adapter/structural-audit tests. Preserve existing web/text coverage. Separate companion-only document routing cases. | Genuine four-format extraction, sandbox-before-read, missing assets/backends, source/derived and cache receipts, whole-layout admission, truthful wrapper results. No placeholder or mocked-converter-only success. |
| P-03 Commands | Add pure file-input tests; reorganize affected shared helpers or API fixtures only when necessary. Existing SESSION/DIAG/MEMQ tests remain valid regression coverage. | Original raw-tail parsing, quotes/description/options and before-I/O validation; standard-library-only/API54 surface; no unrelated command-semantic changes. |
| P-04 Memory | Significant fixture/case rework is expected across `tests_memory/test_ingestion*.py`, `test_adapters/test_vector.py`/`test_graph.py`, `test_context/test_extractor_cancellation.py`/`test_extraction_filter.py`/`test_assembler.py`/`test_assembler_lifecycle.py`/`test_consolidator.py`, `test_retrieval/test_collection_manager.py`/`test_graph_scorer.py`, lifecycle suites, `test_maintenance/test_backup.py`/`test_analyzer.py`/`test_recovery_participant.py`/`test_mutation_participant.py` and `test_multi_agent.py`; add new ingestion/binding tests. | Admitted fresh namespaces and exact capabilities, matching reopen, role/dimension/capacity errors, no second chunking, full valid source/derived coverage, visibility and partial failures, strict v1/v2 recovery and retained maintenance safety. |
| P-05 LLM | Rewrite/extend `tests_llm/test_embeddings.py` and `test_model_library.py` plus affected capability/batch/cache doubles. Add qualified counter, input-envelope, ordering and malformed-result cases. | Existing call/selection/resilience contracts; exact query/document formatting, token limits, complete batch validation, lazy imports and omitted-field readiness. No character estimate or truncation accepted as token enforcement. |
| P-06 Chat | Replace obsolete document-placeholder and character-slice expectations in `tests_chat/test_files_replay_shell.py` and affected adapter/config/registry fixtures. Restructure relevant MCP, maintenance, diagnostics and reorganization tests; add actual document-ingestion/public-path cases. | Real command delegation/storage, typed config precedence, effective help/output, read failures cause zero ingestion, worker/admission/cancellation, exact receipt/error behavior, old valid text/replay/shell contracts and strict aggregate recovery. |
| P-07 Runtime | Rewrite affected `tests_runtime/test_di.py`, `test_kernel.py`, `test_config.py` and MCP/loading fixtures where startup, explicit origin, profile isolation or teardown changes; preserve actual tool-discovery witnesses. | Pool/non-pool assembly, no unavailable-store side effects, ephemeral isolation, observed inner-task completion, shutdown, real MCP observer mapping and minimal installs. |
| P-08 CLI | Adapt focused compatibility/config/container/profile tests only as needed, including `tests_cli/test_cli_config.py` and new targeted fixtures. Old backend-opening assumptions may need replacement even if production delegation stays unchanged. | Raw origin survives configuration merging, Runtime delegation/readiness, constructor/re-export compatibility, no launcher or separate ingestion policy. |
| P-09 Agent | Rewrite affected archive/context/background-memory integration fixtures and focused `tests_agent/test_base.py`/public-tool tests if shared contracts change their setup. No Agent production-source change is inferred. | Observe the real inner extraction task and terminal failure/status; retain authorization, actual tools and public inputs/results. Wrapper completion is not extraction success. |
| P-10 Telemetry | Retain schema/reason tests; update only affected integration expectations for the exact approved existing reason/counter mapping. | Same event union and telemetry-disabled behavior; no new reason schema or silent dropped failure. |
| P-11 Transcript | Retain strict v1/public persistence tests in `packages/friday-transcript/tests/`; adapt only affected cross-package receipt/aggregate fixtures and add strict mixed-version refusal witnesses in the owning suites. | Receipt ownership/readback, unchanged Transcript v1, Memory/Chat v2 ownership, independent path settings and no live identity overwrite. |
| P-12 MCP | Retain transport tests; adapt affected optional-profile/import/integration fixtures when inherited dependencies or guarded Memory publication changes setup. | No transport feature change; exact snapshot text/pending IDs/receipts and truthful failure categories through actual Chat/Runtime consumers. |
| P-13 Optimization | No existing package test suite is present. Add a declared-Memory dependency/import-profile witness only if the final inventory justifies it; its exact new package-local `tests_optimization/` or root integration path and selector must bind the directive. | Dependency inheritance without inventing an active source route, optimization algorithm or model-quality change. |
| P-14 Finance | Retain existing behavior tests in `packages/friday-finance/tests/`; focused import/tool-catalog regressions may be added or have installation fixtures updated. | Ordinary Finance use does not acquire a Docling execution prerequisite. No financial algorithm rewrite. |
| P-15 Speech | Retain unrelated speech tests; add/adapt only justified shared-import/registration profile witnesses. | No new document/tokenizer prerequisite for ordinary speech use; no speech feature change. |
| P-16 Sandbox | Retain Docker/Python execution tests; rewrite document filesystem-sandbox tests only in Tools, their actual owner. | Converter access remains behind Tools' FilesystemSandbox; no sandbox-engine or policy redesign. |
| P-17 Moltbook | Retain existing behavior; conditional import/tool-registration test adaptation only if the final consumer inventory identifies an affected dependency/setup. | No new embedding/ingestion feature or speculative production edit. |

Root integration work includes new shared document-ingestion and embedding
compatibility suites, plus affected `tests/integration/test_mcp_memory_ingestion.py`
and `test_package_cohort_metadata.py`. Installed-profile/replay/probe oracles also
need explicit dispositions. Genuine synthetic format/OCR fixtures replace fake
extension-only positives; deterministic exact-dimension embeddings are separated
from actual serving/tokenizer qualification. TOOLS-DOC tests remain its separate
construction obligation and cannot be claimed complete by INGEST alone.

The REM's test-only allowlist covers the existing Telemetry, Transcript, MCP,
Finance, Speech, Sandbox and Moltbook consumer suites conditionally; production
source remains excluded. Transcript and Finance use `packages/friday-transcript/tests/`
and `packages/friday-finance/tests/`, not `tests_transcript/` or `tests_finance/`.
Optimization has no baseline suite: any justified new package-local or root
integration witness must have its exact path and selector in the directive.
The final directive names exact old/new files and cases before any rewrite.
Retained/import evidence does not require a gratuitous test edit.

### Explicit execution of non-default suites

Root pytest `testpaths` matches `packages/*/tests_*`, which omits the two existing
`tests/` suites. Construction validation must therefore run them explicitly,
including retained cases as well as scoped replacements, for example:

```bash
uv run --no-sync pytest packages/friday-transcript/tests -q
uv run --no-sync pytest packages/friday-finance/tests -q
```

These are future construction checks, not commands executed during this planning
review. The approved directive binds the prepared environment, private caches/
basetemps and installed/source profiles, and records exact executed selectors,
counts and outcomes. Root collection alone supplies no credit for these suites.
Any new Optimization witness has its own explicit selector. Existing failures
remain failed/unwaived and are distinguished from candidate regressions.

## Case-level migration map — required before the first test rewrite

The final directive must include an initial inventory and require a maintained
old-to-new map. Each affected test/fixture entry records:

- Package, old file/node IDs, fixture/snapshot identity and baseline commit.
- Behavioral requirement and intended old oracle; retain/restructure/replace/
  retire/add disposition, reason and governing REM/DI/FC requirement.
- New file/node IDs and concrete assertions proving every still-valid obligation;
  distinguish baseline success, replacement-model success and refusal coverage.
- Deliberate before/after oracle changes, preserved unrelated behavior, relevant
  actual public path and source/installed normal/optimized lane.
- Meaningful negative or mutation witness where the contract requires one,
  canonical origins and actual call-phase assertion failure. Setup/import/
  collection failures receive no rejection credit.
- Retirement rationale, replacement location or obsolete-requirement disposition,
  reviewer outcome and unresolved gaps. New unexpected cases are mapped before
  their old coverage is removed; historical evidence is never edited retroactively.

Renaming a test requires updating the command selectors and proof references
that run it. Moving a check into an uncalled helper or a collected-but-unawaited
coroutine does not retain coverage. Test/assertion counts and AST inventories
are useful audits, not semantic equivalence evidence or a requirement to retain
the obsolete implementation's test bodies.

## Test migration acceptance

DI-35 requires independent review of this map against the actual changed suite:
all affected baseline cases/fixtures have dispositions, every valid requirement
has substantive executed witnesses, deliberate oracle changes are justified,
and retirements leave no hidden gap. Run new focused contracts first, then the
affected package and cross-package regressions, installed profiles/replays and
required controls. No fresh production feature is inferred from a test edit.

Report unexpected test churn outside the approved paths before proceeding.
Existing root collection, lint/formatting and known failed baseline branches
remain explicit unwaived debt. Do not turn them into false positives or repair
them opportunistically under this migration. Tests are implementation work and
start only after the exact construction directive is approved.
