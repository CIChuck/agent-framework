# ASTRA round 3 independent design review

Outcome: **CHANGES_REQUESTED**. Independent technical rubric: **9.20/10**. One mandatory medium-severity design finding; no separate advisory findings. Procedural conformance is assessed separately below. This is proposed-design review, not implementation validation.

Reviewer: ASTRA, gpt-6-astra, high effort; 2026-11-10. Fresh reviewer context; I did not author/remediate this candidate. No builder transcript/private reasoning, current peer verdict, raw previous review, or nested delegation was used. A lightweight memory-registry lookup supplied only general authority-boundary context, not correctness evidence. The explicitly authorized shared-checkout read-only exception applies.

Workdir: /Users/chuckrussell/Dev/gendev/agent-framework. Branch: feature/cmd-ingest-001. Candidate: 36362be514ef387183a27d930cd41a8799e3d714. Correction base: 2956b861de75fcf7ebf463c82f5f470cf6fa7b40. Aggregate base: c36e7ee51a9328918b9bb97712aa7f1d4a850d19.

Request SHA256: faa4e9570318004b6e1bf00db15e60925a006f5484a47a5c399b640279379af4. Helper SHA256: 080be4f9b781c5624492ab83071dcd6301f5d30f8c65a33eb636ab0a90a9d368. Wrapper SHA256: cb0669f81efd0098c104d7b96342fcd614255021ea2bfa49cbbb6af7c2fea248. All three matched before execution; helper/wrapper source was inspected. The request was read by fields, and the full current REM and companion by numbered pages. Some tool output was truncated; focused follow-up reads recovered the material used in the assessment.

Authority: explicit task and pinned request, AGENTS.md, repository-engineering-policy.md, development-task-lifecycle.md, independent-validation-policy.md, council/independent-code-validator/friday-dev-board skills, pinned maintainer scope/discussion/format/security/iteration/roster and fresh-store policy records. Current authority fields were projected without dumping historical authority. The correction brief supplied requirements only. Correction delta was inspected first, followed by full current design, filtered aggregate comparison and source feasibility. No product changes appear in the aggregate comparison of the pinned source paths.

## 1. Mandatory finding INGEST-R3-ASTRA-001 — complete the Chat aggregate recovery schema handoff

Severity: medium, mandatory. Requirements: IR-S02 identity-preserving snapshot/schema/layout binding and same-namespace rollback; IR-08 typed cross-package contracts; IR-16 coherent bounded final-directive prerequisites. This is a present design/allowlist inconsistency, not a demand for implementation now.

REM `docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:851-885` requires new version2 snapshots and exact schema dispatch while retaining strict old validators. Its exact implementation-path table at 989-1019 adds Memory recovery/models and Runtime/Core/CLI but lists only Chat config/runtime/adapters, file handlers and reorganization/mutation.py. Lines 1021-1029 require stopping if integration cannot fit those paths.

Maintained source shows the additional boundary already exists:

- `packages/friday-memory/src/friday_memory/maintenance/recovery_models.py:289-301`: MemorySnapshotManifest is a strict schema_version Literal[1] model.
- `packages/friday-chat/src/friday_chat/reorganization/coordinator.py:1459-1462`: the maintained snapshot path parses that exact model; 1470-1494 embeds it in the aggregate recovery bundle.
- `packages/friday-chat/src/friday_chat/reorganization/contracts.py:417-430`: RecoveryBundleManifest is version1 and statically embeds MemorySnapshotManifest; 435-461 ties participant identity to it.
- `packages/friday-chat/src/friday_chat/reorganization/artifacts.py:177-225`: aggregate bundle verification reparses both the bundle and exact MemorySnapshotManifest and compares their payloads.

Consequently a separately added v2 Memory manifest does not automatically traverse the maintained Chat snapshot/bundle/rollback path. Leaving the current strict consumers unchanged rejects v2; simply broadening the old model would contradict the requirement to retain strict version1 validators and historical artifact interpretation. The proposal does not say which versioned public loader/model Chat consumes or include these known consumers in its bounded paths. The general instruction to freeze signatures later is insufficient to reconcile this already visible cross-package seam.

Narrow correction: document the Memory v1/v2 public dispatch and Chat aggregate schema compatibility; explicitly account for coordinator.py, contracts.py and artifacts.py, plus required public Memory exports, as schema/admission integration only. State whether REM's versioned fingerprint is the Memory participant fingerprint (recovery.py:218-231) or also changes Chat's distinct layout fingerprint (layout.py:199-213); amend layout/assembly paths only if the latter is intended. Preserve maintenance ordering, quiescence, journal scheduling, approval and rollback triggers. No recovery-engine redesign is requested.

Narrow future evidence: extend DI-27/28 to exercise actual Chat snapshot -> aggregate bundle write/read -> same-namespace restore/automatic rollback with a bound v2 Memory manifest. Preserve identity-free v1 fixtures for offline inspection; reject their bound-store restore without writes. Assert schema/binding/incarnation tamper rejection through the aggregate reader, not only the Memory helper. Freeze exact changed fixtures/oracles in the final directive. No runtime tests were executed in this review.

## 2. All 28 criteria

References below use REM for the remediation document above and TD for `docs/planning/active/command-refactor/proposals/tools-document-adoption.md`. PASS means adequate proposed contract at this gate, not implemented or experimentally proven behavior.

| Criterion | Outcome | Evidence and assessment |
|---|---|---|
| IR-01 | PASS | REM 3-40, 1095-1112; current authority projection and pinned fresh-store policy distinguish proposal, gate A, construction, MAINT acceptance and delivery. Frozen identity checks pass at start. |
| IR-02 | PASS | REM 302-352: local four-format admission, detected-format equality, full conversion, meaningful content and partial/error refusal before Memory. Current files.py:44-62,122-132 confirms placeholder gap is real and intentionally future work. |
| IR-03 | PASS | REM 333-367, DI-01..04: native/OCR PDF, real counts, interleaved DOCX, declared omissions and genuine scanned fixtures; no fallback extractor. |
| IR-04 | PASS | REM 366-380,400-416, DI-13/25: visible sheet/row/column scope, independently audited saved formula cache/error handling, merged/types semantics and late content; no calculation or silent preview. TD 73-87 distinguishes factory selections. |
| IR-05 | PASS | REM 367,382-416, DI-14/25: native tables/notes/numbering, hidden content, visual omissions and no media fetch. Selected-release mapping remains a stop gate. |
| IR-06 | PASS | REM 427-462,531-539, DI-05/06: original raw tail, handler ownership, exact options/lookalikes, literal terminator and API54 preservation. registry.py:175,1196 and files.py:135-151 identify existing parsing seams. |
| IR-07 | PASS | REM 496-595: shared document/512, independent override precedence, all three strategies, overhead/overlap and structure boundaries. Existing adapters.py:383-385 character splitter must be replaced. |
| IR-08 | CHANGES_REQUESTED | Core/Memory/Tools/LLM ownership and injection are otherwise sound (REM 94-177,578-586); missing versioned Chat aggregate recovery contract/path integration is finding 001. |
| IR-09 | PASS | REM 599-683,709-718: optional schema parsing versus required verified identity/counter/dimensions, effective deployed cap, Qwen illustrative only. No current model/provider inference claimed. |
| IR-10 | PASS | REM 685-790: once-only roles, batch/cardinality/index/dimension/finite checks, split-at-planning versus reject-at-LLM, identity envelopes and full-plan validation. embeddings.py:272-285,311-323,382-394 demonstrates current guard/cache gap. |
| IR-11 | PASS | REM 179-300,619-640: exact dependency/extras, Certifi floor after all installs, offline assets and hosted unsupported-route refusal. Gate A is explicitly pending; no install proof claimed. |
| IR-12 | PASS | REM 321-352,400-416,887-906: format/ZIP/resource bounds, untrusted content, cancellation/quiescence, no thread-as-sandbox claim. Numeric limits are appropriately frozen by the selected-release gate. |
| IR-13 | PASS | REM 121-177; TD 25-35,88-118: actual/public-unwired/absent routes, extraction versus storage caches, opt-in/provenance retained. smart_read.py:283-318,402-446 confirms early cache handoffs requiring repair; adapters.py:2364-2380 supplies LLM/config but no Memory. |
| IR-14 | PASS | REM DI-01..31,1069-1078 and TD TD-01..10 require real fixtures, installed normal/optimized proof, Chroma, call-phase mutations and precise oracle exceptions. Existing failed baselines are not waived. Finding 001 specifies one necessary refinement to DI-27/28 under IR-S02. |
| IR-15 | PASS | Pinned policy record; REM 913-983 and current authority/status: explicit absent destination, no hidden reset/migration/stateless fallback; master future base, MAINT UAT separate. |
| IR-16 | CHANGES_REQUESTED | REM 179-260 defines bounded gate-A effects and stops correctly; exact-path/final-directive coherence needs finding 001 before declaring this design complete. |
| IR-R01 | PASS | REM 105-177, DI-23/30: injected Core entry, Memory factory, raw plan versus derived records, full preflight and cache sequencing. Existing reverse imports acknowledged rather than denied. |
| IR-R02 | PASS | REM 740-814,913-983: single authoritative sidecar, exclusive pending/ready creation, immutable incarnation, same-dimension mismatch, graph/precomputed provenance and no hidden migration. Recovery-specific handoff assessed separately under S02. |
| IR-R03 | PASS | REM 217-229,695-705, DI-22/28: role inventory covers retrieval, graph, synthesis, lifecycle, pools and direct clients; unclassified callers prevent asymmetric enable. Source search confirms named direct clients and embedding seams. |
| IR-R04 | PASS | REM 607-640,818-841: parse compatibility, operation-time verified capability, non-pool refusal, read-only availability and lazy assembly. Runtime di.py:196-260 and Core profiles.py:56-86 establish actual required change sites. |
| IR-R05 | PASS | REM 543-576: Memory-owned deterministic text blocks, no Docling requirement for text, no hidden conversion fallback; structure-less CSV has an explicit coverage limitation. |
| IR-R06 | PASS | REM 244-260,619-640,709-728,887-906: synchronous offline counting, manifest assets, server cross-check/effective ceiling and quiescent cancellation. |
| IR-R07 | PASS | REM 400-416, DI-25: bounded non-text Office audit, provenance mapping and unknown-warning refusal; Docling remains sole text supplier. |
| IR-R08 | PASS | REM 121-136,171-177,1103-1105; TD 25-59: truthful route inventory, no new fetcher/automatic storage, inactive migration classification. |
| IR-S01 | PASS | Policy record lines 3-18 and REM 913-983 settle policy and exact path/open-intent matrix, pre-created empty refusal, graph/WAL selection, lazy /read and no stateless fallback. assembly.py:26-47 corroborates sibling graph and independently configured other paths. |
| IR-S02 | CHANGES_REQUESTED | REM 843-885 substantially repairs Memory binding/snapshot/restore/raw-client obligations, but maintained Chat aggregate schema readers and bounded paths remain unaccounted for: finding 001. |
| IR-S03 | PASS | REM 818-849,630-640,777-790, DI-29/31: Runtime pool/non-pool, Core factory and CLI delegation, lazy gates, hosted immutable identity/offline assets and whole-recall provenance failure. CLI container.py:175,231 delegates kernel. |
| IR-S04 | PASS | REM 162-177,126-130,537-538,569-576, TD 106-111: destination/incarnation/collection/record receipts, honest smart_read/import/CSV/migration/flags and current governance. |

Totals: 25 PASS; 3 CHANGES_REQUESTED, all attributable to the single finding. No criterion is presented as implementation proof.

## 3. Disposition of round2 requirements

- Opus M-1 / IR-S01: closed at design level by explicit policy record and REM open-intent/state matrix; no remaining policy question inferred.
- INGEST-R2-ASTRA-001 and Opus M-2 / IR-S02: substantially addressed for Memory, direct client admission and restore restrictions; not fully closed because finding 001 identifies the maintained aggregate consumer seam.
- INGEST-R2-SOL-A01: addressed by lazy capability/read-only startup, DI-29.
- INGEST-R2-ASTRA-002: addressed by destination/incarnation/collection/record/provenance receipts, DI-30.
- Opus A-1..A-8: respectively addressed by honest smart_read wiring; existing import-edge acknowledgment; plain-delimited coverage; immutable hosted/offline BPE rule; current roster and future web-route boundary; exact sidecar root/whole graph refusal; inactive migration classification; and exact option-name handling. These are independent dispositions of the supplied requirements, not adoption of earlier verdicts.

## 4. Rubric

| Dimension | Score | Rationale |
|---|---:|---|
| Scope, authority, boundedness | 1.45/1.50 | Settled policy and clear gate boundaries; one path reconciliation remains. |
| Shared architecture/integration | 1.65/2.00 | Strong injected ownership and runtime classification; aggregate recovery seam incomplete. |
| Extraction/coverage | 1.95/2.00 | Thorough format/coverage refusal contract with explicit feasibility stops. |
| Chunking, embedding, data safety | 2.75/3.00 | Strong identity, input and cache safety; complete recovery compatibility not yet specified. |
| Verification/reporting | 1.40/1.50 | Meaningful future oracles and green planning checks; aggregate schema proof needs explicit refinement. |
| Total | 9.20/10 | Independent advisory score; mandatory finding controls outcome regardless of threshold. |

## 5. Reproduced checks versus inspected evidence

Reproduced locally under the verified wrapper, all exit 0: start integrity; board validate (36 tasks); dashboard render --check (current); documentation lifecycle (987 Markdown files); package metadata (18 pyproject files); whitespace diff check. Also reproduced filtered correction/aggregate/source comparisons and read-only source searches. Raw outputs are in this private directory. Exact wrapped child argv, cwd, environment guard values and exits are in command-audit.jsonl; an appendix is finalized after closing integrity.

The five requested argv are:

```
uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate
uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check
uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py
uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py
git diff --check 2956b861de75fcf7ebf463c82f5f470cf6fa7b40..36362be514ef387183a27d930cd41a8799e3d714
```

Each command was prefixed with `python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-design-r3-gywt4bca/inputs/read_only_command.py /tmp/astra-ingest-r3-20261110-9c62 --`. Nested Git children used that prefix too. No historical receipt command was replayed.

Inspected evidence: maintained source, current proposal/authority/status and requirement records. Historical planning-check receipts were inspected only as status, not passing correctness evidence. Source defects are the pre-remediation baseline, not new runtime regressions from this document candidate.

Public primary references were freshly opened with official web tools: [Docling formats](https://docling-project.github.io/docling/usage/supported_formats/) and [chunking](https://docling-project.github.io/docling/concepts/chunking/) support broad format/hybrid-tokenizer feasibility; [offline options](https://docling-project.github.io/docling/usage/advanced_options/) describe model provisioning. These do not prove selected-release Office coverage. [Qwen model card](https://huggingface.co/Qwen/Qwen3-Embedding-4B) supports the illustrative 32K/up-to-2560 values; [Nomic model card](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) supports distinct query/document conventions. [LM Studio tokenization](https://lmstudio.ai/docs/python/tokenization) and [model listing](https://lmstudio.ai/docs/developer/rest/list) were inspected as API references only. [Certifi release](https://pypi.org/project/certifi/2026.10.19/) and [advisory](https://github.com/certifi/python-certifi/security/advisories/GHSA-6q48-6c7w-9gw2) corroborate the release and earlier patched version; the maintainer's higher floor still governs. No artifacts downloaded or installed and no provider contacted for inference.

Not run: runtime tests, builds, dependency resolution, Gate-A experiments, model operations, user-store operations, UAT. These are excluded or future gates, not missing proof required today. Root Ruff 534, test_display collection conflict7196, seven legacy format failures and MAINT Chat1413/15 remain request-supplied unwaived baseline limits, not reproduced current results.

## 6. Isolation and limits

Bootstrap exported GIT_OPTIONAL_LOCKS=0 and PYTHONDONTWRITEBYTECODE=1; hashes used hashlib/pathlib without Git. A static pathlib bootstrap created fresh external owner-only scratch. All subsequent Git/admin/child commands used the immutable wrapper. It established UV_OFFLINE=1, UV_NO_SYNC=1, UV_FROZEN=1, UV_PYTHON_DOWNLOADS=never and private UV_CACHE_DIR/XDG_CACHE_HOME/TMPDIR. environment.json independently records those values (macOS canonical /private/tmp alias). No environment secret was collected.

Generated outputs, cache, temporary paths and reports are inside this scratch. The wrapper is environment/audit machinery, not an OS sandbox. No repository/supplied-input/old-scratch write, checkout, install, test/build, model inference, network mutation or personal-store content inspection occurred. The helper alone performed authorized protected hashing/stat and Git status. The supplied status field was read as request metadata, not used to inspect personal files. Additional contracts.py/artifacts.py source pins were recorded privately and rechecked before closing. Start integrity matched 17,583 protected records and the pinned logical index 43738da1ed6e59de584e729e570b1bbeb4b5ab54b7813c66660f684951b5f9fc; helper also checked the supplied six metadata records and all named pins.

Recommended next action is only the narrow document/schema-boundary correction described in finding 001, followed by the controller's authorized review handling. This report grants no construction, Gate-A execution, acceptance, merge, publication or delivery authority.

## 7. Closing integrity and exact command audit

Closing helper exit 0, PASS; candidate, branch, logical index, status, staged state, authority/document/source pins, all 17,583 protected records and the supplied metadata preservation checks match. No failures. No exploration followed closing integrity. Procedural conformance: PASS; no detected conduct/isolation/all-command violation. Technical outcome remains CHANGES_REQUESTED, 9.20/10.

Audit through closing integrity: 32 starts and 32 matching ends; all exits 0; both mandatory environment guards present in every entry. This final report-only writer is the sole currently open wrapper record and will be closed by the wrapper on exit. All earlier command records are paired, including nested wrapped comparisons. Full private environment values are recorded in environment.json.

Every child argv below was executed with the wrapper prefix documented above; cwd is the exact repository workdir. The wrapper itself and Python stdin script bodies are available in the tool transcript; argv `python3 -B -` denotes static reads/report bookkeeping, with the one orchestration script using separately wrapped children. Bootstrap static hash/read/scratch setup precedes this log as explicitly permitted.

```json
[
  {
    "argv": [
      "python3",
      "-B",
      "/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-design-r3-gywt4bca/inputs/check_integrity.py",
      "/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-design-r3-gywt4bca/inputs/review-request.json"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "git",
      "diff",
      "2956b861de75fcf7ebf463c82f5f470cf6fa7b40..36362be514ef387183a27d930cd41a8799e3d714",
      "--",
      "docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md",
      "docs/planning/active/command-refactor/proposals/tools-document-adoption.md",
      "docs/planning/active/command-refactor/approval/ingest-existing-store-policy.md"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "rg",
      "-n",
      "PersistentClient|create_vector_store|SmartFileReadTool\\(|embed_query\\(|embed_documents\\(|embed_text\\(",
      "packages/friday-runtime/src",
      "packages/friday-core/src/friday_core/profiles.py",
      "packages/friday-cli/src/friday_cli/container.py",
      "packages/friday-memory/src",
      "packages/friday-chat/src/friday_chat/runtime.py",
      "packages/friday-chat/src/friday_chat/adapters.py"
    ],
    "exit": 0
  },
  {
    "argv": [
      "rg",
      "-n",
      "fingerprint|mkdir|PersistentClient|layout|snapshot|restore|memory",
      "packages/friday-chat/src/friday_chat/reorganization/layout.py",
      "packages/friday-chat/src/friday_chat/reorganization/assembly.py",
      "packages/friday-cli/src/friday_cli/container.py",
      "packages/friday-core/src/friday_core/profiles.py"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "rg",
      "-n",
      "layout_fingerprint|MemoryStorageLayout|snapshot|create_snapshot|verify_snapshot",
      "packages/friday-chat/src/friday_chat/reorganization/coordinator.py",
      "packages/friday-chat/src/friday_chat/reorganization/assembly.py",
      "packages/friday-memory/src/friday_memory/maintenance/recovery_models.py",
      "packages/friday-memory/src/friday_memory/maintenance/recovery.py"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "git",
      "diff",
      "--check",
      "2956b861de75fcf7ebf463c82f5f470cf6fa7b40..36362be514ef387183a27d930cd41a8799e3d714"
    ],
    "exit": 0
  },
  {
    "argv": [
      "uv",
      "run",
      "--offline",
      "--frozen",
      "--no-sync",
      "--no-python-downloads",
      "python",
      "-B",
      "scripts/check-package-metadata.py"
    ],
    "exit": 0
  },
  {
    "argv": [
      "uv",
      "run",
      "--offline",
      "--frozen",
      "--no-sync",
      "--no-python-downloads",
      "python",
      "-B",
      "scripts/friday-dev-board.py",
      "render",
      "--check"
    ],
    "exit": 0
  },
  {
    "argv": [
      "uv",
      "run",
      "--offline",
      "--frozen",
      "--no-sync",
      "--no-python-downloads",
      "python",
      "-B",
      "scripts/friday-dev-board.py",
      "validate"
    ],
    "exit": 0
  },
  {
    "argv": [
      "uv",
      "run",
      "--offline",
      "--frozen",
      "--no-sync",
      "--no-python-downloads",
      "python",
      "-B",
      "scripts/check-documentation-lifecycle.py"
    ],
    "exit": 0
  },
  {
    "argv": [
      "rg",
      "-n",
      "SmartFileReadTool|chunk_size|chunk_text|_read_document|placeholder|_parse_command_input|file_synthesis|store_to_memory|_memory|embedding|cache|BinaryReader|XlsxReader",
      "packages/friday-chat/src/friday_chat/commands/files.py",
      "packages/friday-chat/src/friday_chat/adapters.py",
      "packages/friday-chat/src/friday_chat/commands/registry.py",
      "packages/friday-tools/src/friday_tools/filesystem/smart_read.py",
      "packages/friday-tools/src/friday_tools/filesystem/readers/factory.py",
      "packages/friday-llm/src/friday_llm/embeddings.py"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "git",
      "diff",
      "c36e7ee51a9328918b9bb97712aa7f1d4a850d19..36362be514ef387183a27d930cd41a8799e3d714",
      "--",
      "docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md",
      "docs/planning/active/command-refactor/proposals/tools-document-adoption.md",
      "docs/planning/active/command-refactor/approval/ingest-existing-store-policy.md",
      "docs/planning/active/command-refactor/validation/document-ingestion/council-round3/correction-brief.json",
      "docs/planning/active/command-refactor/validation/document-ingestion/council-round3/roster.json",
      "docs/planning/active/command-refactor/validation/document-ingestion/council-iteration-authorization.json"
    ],
    "exit": 0
  },
  {
    "argv": [
      "git",
      "diff",
      "2956b861de75fcf7ebf463c82f5f470cf6fa7b40..36362be514ef387183a27d930cd41a8799e3d714",
      "--",
      "docs/planning/active/command-refactor/README.md",
      "docs/planning/active/command-refactor/next-phase.md",
      "docs/planning/active/command-refactor/tactical-plan.md",
      "docs/planning/active/command-refactor/execution-log.md",
      "docs/planning/active/command-refactor/validation/document-ingestion/planning-checks.json",
      "docs/planning/active/command-refactor/validation/document-ingestion/branch-handoff.md",
      "docs/planning/board.yaml",
      "docs/planning/README.md",
      "docs/planning/backlog/friday-chat-framework-followups/upgrade-log.md"
    ],
    "exit": 0
  },
  {
    "argv": [
      "git",
      "diff",
      "--stat",
      "c36e7ee51a9328918b9bb97712aa7f1d4a850d19..36362be514ef387183a27d930cd41a8799e3d714",
      "--",
      "packages/friday-chat/src/friday_chat/commands/files.py",
      "packages/friday-chat/src/friday_chat/commands/registry.py",
      "packages/friday-chat/src/friday_chat/adapters.py",
      "packages/friday-chat/src/friday_chat/runtime.py",
      "packages/friday-chat/src/friday_chat/config.py",
      "packages/friday-chat/src/friday_chat/config_templates/config.example.yaml",
      "packages/friday-chat/src/friday_chat/config_templates/models-config.example.yaml",
      "packages/friday-chat/tests_chat/test_files_replay_shell.py",
      "packages/friday-tools/src/friday_tools/filesystem/readers/base.py",
      "packages/friday-tools/src/friday_tools/filesystem/readers/factory.py",
      "packages/friday-tools/src/friday_tools/filesystem/readers/pdf_reader.py",
      "packages/friday-tools/src/friday_tools/filesystem/readers/docx_reader.py",
      "packages/friday-tools/src/friday_tools/filesystem/readers/xlsx_reader.py",
      "packages/friday-tools/src/friday_tools/filesystem/smart_read.py",
      "packages/friday-tools/src/friday_tools/web/reader.py",
      "packages/friday-tools/src/friday_tools/web/fetch.py",
      "packages/friday-memory/src/friday_memory/ingestion/metadata.py",
      "packages/friday-memory/src/friday_memory/ingestion/chunker.py",
      "packages/friday-memory/src/friday_memory/ingestion/tool_ingester.py",
      "packages/friday-memory/src/friday_memory/ingestion/large_file_processor.py",
      "packages/friday-llm/src/friday_llm/model_library.py",
      "packages/friday-llm/src/friday_llm/embeddings.py",
      "packages/friday-core/src/friday_core/interfaces/memory.py",
      "packages/friday-core/pyproject.toml",
      "packages/friday-commands/pyproject.toml",
      "packages/friday-tools/pyproject.toml",
      "packages/friday-memory/pyproject.toml",
      "packages/friday-llm/pyproject.toml",
      "packages/friday-chat/pyproject.toml",
      "pyproject.toml",
      "uv.lock",
      "packages/friday-memory/src/friday_memory/adapters/vector.py",
      "packages/friday-memory/src/friday_memory/adapters/simple_vector.py",
      "packages/friday-memory/src/friday_memory/adapters/graph.py",
      "packages/friday-memory/src/friday_memory/adapters/null_graph.py",
      "packages/friday-memory/src/friday_memory/models/graph.py",
      "packages/friday-memory/src/friday_memory/controller/memory_controller.py",
      "packages/friday-memory/src/friday_memory/context/extractor.py",
      "packages/friday-memory/src/friday_memory/retrieval/collection_manager.py",
      "packages/friday-memory/src/friday_memory/retrieval/graph_scorer.py",
      "packages/friday-memory/src/friday_memory/maintenance/synthesizer.py",
      "packages/friday-memory/src/friday_memory/maintenance/pipeline.py",
      "packages/friday-memory/src/friday_memory/maintenance/reorganizer.py",
      "packages/friday-memory/src/friday_memory/maintenance/provider_contracts.py",
      "packages/friday-chat/src/friday_chat/reorganization/mutation.py",
      "packages/friday-memory/src/friday_memory/maintenance/recovery.py",
      "packages/friday-memory/src/friday_memory/maintenance/recovery_models.py",
      "packages/friday-memory/src/friday_memory/maintenance/mutation.py",
      "packages/friday-memory/src/friday_memory/maintenance/pruner.py",
      "packages/friday-memory/src/friday_memory/maintenance/fact_checker.py",
      "packages/friday-memory/src/friday_memory/lifecycle/migration.py",
      "packages/friday-runtime/src/friday_runtime/di.py",
      "packages/friday-runtime/src/friday_runtime/config.py",
      "packages/friday-core/src/friday_core/profiles.py",
      "packages/friday-cli/src/friday_cli/container.py",
      "packages/friday-cli/src/friday_cli/profiles.py",
      "packages/friday-chat/src/friday_chat/reorganization/assembly.py",
      "packages/friday-chat/src/friday_chat/reorganization/layout.py",
      "packages/friday-chat/src/friday_chat/reorganization/coordinator.py"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "rg",
      "-n",
      "class RecoveryBundleManifest|memory:|MemorySnapshotManifest|read_model|schema_version",
      "packages/friday-chat/src/friday_chat/reorganization/artifacts.py",
      "packages/friday-chat/src/friday_chat/reorganization/contracts.py"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "-"
    ],
    "exit": 0
  },
  {
    "argv": [
      "python3",
      "-B",
      "/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-design-r3-gywt4bca/inputs/check_integrity.py",
      "/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-design-r3-gywt4bca/inputs/review-request.json"
    ],
    "exit": 0
  }
]
```

Private evidence hashes (before final report completion):

- `start-integrity.json`: `b23551fd210a938f53fe1e6ac1310f07edb87460b29710ee5478f66c13b979ba`
- `end-integrity.json`: `b23551fd210a938f53fe1e6ac1310f07edb87460b29710ee5478f66c13b979ba`
- `environment.json`: `ad5e8e30c150042d6bf377db912aef0487d3da969c4fe5930db249b7924537b4`
- `additional-source-pins.json`: `6a1f55a880255ada27e814bc2bfc906655b3177b2f0cf6037faf6213d1bfba7c`
- `board.txt`: `c4d2aec671b8fd5d5a978b1c191b186f6d151f7ace4785fbd74b06c3c5f3fdae`
- `dashboard.txt`: `a28df31135633728c76b88ed1a836e90f2c8046e1d72663c8881937c7693ba33`
- `docs.txt`: `d5552bad1a314d23ed2b897a244170000542cba18d12ddec6aa420ae3ea62dbd`
- `metadata.txt`: `b755228d64e991cad2a40d1ea238ea00e97d8d2fd420a5141fffa00476ed690f`
- `whitespace.txt`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `aggregate-technical.txt`: `feb31cd71d03a8fd3209f1697ffb09addc60b9e0373e1b2eb7a5c2136e570fb3`
- `delta-status.txt`: `4473ab6d135c7be9ac1ee80f995dae67e91c19a4323109c551a867b84cac9f84`
- `source-diff.txt`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
