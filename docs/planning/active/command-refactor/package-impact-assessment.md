# INGEST-001 — Package Impact Assessment

Version: **0.8 — corrected final construction approval proposal**, 2026-11-13.

This assessment describes planned implementation, not completed product upgrades.
It covers all **17 workspace packages**: eight implementation owners and nine
packages whose production source stays unchanged with compatibility obligations.
Tests may change only under the exact case map. Dependency, configuration,
installation, upgrade and documentation consequences are included below.

Chuck approved v0.6 on 2026-11-11, SHA256
`f570318f704fe3c5ba29b62860148b45eb31d15243fcf0eb6acd76bc9d218176`,
as recorded in the [exact-version approval](approval/ingest-package-impact.md).
That approval remains valid for those historical bytes. This revision reconciles
the completed evaluation and subsequent maintainer decisions and requires his
review of the changed impact before construction. No approval is inferred here.

## Basis and delivery boundaries

The [final approval package](validation/document-ingestion/product-construction/final-approval/README.md)
combines this assessment with the unchanged
[product directive](directives/CD-CMD-INGEST-001-product.md),
[shared contracts](validation/document-ingestion/product-construction/activation/shared-contracts.md),
[exact file map](validation/document-ingestion/product-construction/activation/slice-file-map.json),
[case map](validation/document-ingestion/product-construction/activation/test-case-map.json)
and [current requirement dispositions](validation/document-ingestion/product-construction/activation/requirement-reconciliation.md).
Those dispositions apply the maintainer's model, Office and shared-process
decisions over the specifically superseded REM/directive wording. They do not
replace the remaining [REM](remediation/REM-CMD-INGEST-001-pdf-docx.md),
[compatibility contract](embedding-compatibility-contract.md),
[test migration](test-migration-plan.md), [architecture](command-architecture-update-plan.md)
or [guide](guide-update-handoff.md) requirements.

The activation design at `9ddaf6f8` passed its
[three-seat council](validation/document-ingestion/product-construction/activation/council/round7/results/report.md).
That result belongs to the reviewed design and its pinned historical references;
it is not an independent review or approval of the new assessment/wrapper bytes.
The technical contracts, file/case maps and original reports remain unchanged.
No product source, tests, dependencies, live guides or production state are
modified by preparing this assessment.

Two delivery obligations remain distinct:

- **INGEST:** shared document conversion/process service; Chat's PDF/DOCX/XLSX/PPTX
  extraction; common chunking and ingestion; embedding guards and store identity;
  and bounded adaptations of existing consumers.
- **TOOLS-DOC:** subsequent ReaderFactory and document smart_read adoption,
  preserving selection/pagination. It retains its own
  [directive](directives/CD-CMD-TOOLS-DOC-001-adoption.md) and verification.
  The shared converter and existing text-storage handoff do not complete it.

Compared with approved v0.6, this revision records the selected measured stack,
configured capability resolution without a serving/parity campaign, the affected-
workbook refusal, shared process ownership across frontends, independent document
settings, required counter-factory/same-entry late attachment, exact phase timing
and the completed review stop. It adds no runtime package or feature owner.
Traceable test restructuring and substantive architecture/guide authorship remain
first-class implementation deliverables, as Chuck previously directed.
The v0.8 correction specifies the actual Certifi baseline and I3-C1 enforcement
start, plus tokenizers' shared-lock effect at I1-C2. It adds no file, package,
behavioral feature or test-map exception beyond the reviewed implementation scope.

The 17 rows derive from root workspace membership and package metadata rather
than a directory count. Friday CLI remains a compatibility library without a
standalone executable. No new TUI package or frontend is included.

## Packages with proposed implementation changes

“Source” includes narrowly scoped interfaces, configuration models or wiring.
Every affected package includes explicit test migration and documentation work;
the eight implementation rows also name their scoped package README updates.
Affected test cases/helpers/fixtures may be renamed, split, rewritten, replaced
or justifiably retired with retained/replacement coverage for every valid
requirement. This is implementation scope, not permission to edit tests now.
Exact cases, paths, versions and interfaces bind the final approved directive.

| ID / package | Change types | Planned upgrade and purpose | Compatibility boundary and required evidence |
| --- | --- | --- | --- |
| P-01 `friday-core` | Source, public contracts, tests, README | Add immutable source/block/chunk/options and ingestion-receipt contracts; an injected ingestion-entry interface; and typed embedding-space, prepared-vector/query and explicit-origin/admission contracts. Existing store factories forward that information. This gives Chat, Tools and headless consumers a common interface without making Core own conversion or ingestion policy. | No Docling, tokenizer or new Memory/backend dependency in the neutral contracts. Retain existing lazy adapter imports and unrelated public interfaces. Prove Core factory propagation and headless injection; REM ownership/path table, DI-18/19/29/33, FC-10/12. |
| P-02 `friday-tools` | Source, dependency extra, tests, setup documentation | **INGEST:** implement one shared process-based Docling conversion/chunker service for PDF/DOCX/XLSX/PPTX, independently bound local assets/OCR, cooperative read-only Office structural admission and owned process lifecycle, provenance and truthful extraction errors. Add the `document-ingestion` extra with the selected Docling stack and `certifi>=2026.10.19`. Route explicitly injected existing text-storage/cache paths through the common ingestion entry; expose truthful errors from the affected Memory wrappers. Confirmed reset first admits the whole target layout without inference and retains its binding sidecar. **Companion:** subsequently adopt the converter in ReaderFactory and document `smart_read`, including selections and caches. | Bare Tools text operations remain usable without Docling. No new Tools-to-Memory dependency; consume the injected Core interface. No automatic storage activation, general tool rewrite or migration of every direct legacy reader. Included XLSX sheets with hidden rows/columns refuse the whole workbook before conversion; hidden-sheet exclusion remains. Headless progress/cancel/drain uses the same service. Test genuine formats, missing dependencies/assets, sandbox denial, cache/storage behavior and minimal imports. INGEST DI-01–25/30/34 and FC-01/07/12/13; companion TD-01–10 is a separate completion claim. |
| P-03 `friday-commands` | Source, tests, README | Add pure raw-tail file-argument parsing so quoted paths and descriptions survive; validate scoped `--chunking=document\|recursive\|fixed` and `--chunk-tokens=N` overrides. Supply reusable argument semantics rather than a Chat-only parser. | Keep the package standard-library-only, its root API54 unchanged, and unrelated command parsing unchanged. No filesystem access, converter, Memory or embedding execution here. Prove quoting, descriptions, exact flag handling and malformed-input refusal headlessly; REM C and DI-05/08/09/16. |
| P-04 `friday-memory` | Source, dependency extra request, tests, README | Own the common ingestion entry with required counter, counter factory and embedding broker from one resolved capability record, and `document`/512-token defaults, deterministic non-Docling segmentation, recursive/fixed strategies, validated plans and storage receipts. Add durable/ephemeral embedding-space admission and correct query/document roles. Propagate identity through vector/graph storage, recall and versioned recovery. Adapt extraction acknowledgement, owned background tasks, logging, lifecycle counts and the existing MCP/maintenance/backup consumers only where the new guard requires it. Retain the existing Memory-owned multi-agent controller/coordinator/journal as source-unchanged consumers of that space, with visibility and partial-failure proof. Request LLM's local counter extra through the existing pinned dependency. | The broadest source impact. Preserve record types, protection/description rules and existing maintenance order, prompts, quarantine, rollback and public receipt semantics. No second split of accepted plans; structured/derived records remain unsplit. No Docling/Tools imports in the new policy, storage-engine replacement, user reset/migration or backup repair project. Require ingestion-to-store positives, same-dimension mismatch refusals, matching reopen, graph/recall, extraction, lifecycle, recovery and all FC-01–14 B/N/R proofs. |
| P-05 `friday-llm` | Source, model-profile schema, dependency extra, tests, README | Resolve typed embedding capabilities and model-specific query/document preparation; perform exact local token counting and effective input-limit checks; validate batch correspondence, vector shape and dimensions. Add a narrow `embedding-limits` extra for qualified local counters. These protections apply to existing embedding callers as well as document ingestion. | Keep existing pool/non-pool configuration families and selection/resilience rules. Missing optional model fields use a configured local capability record with validated assets, capacity and dimensions. Explicit API manifest path takes precedence over FRIDAY_EMBEDDING_MANIFEST. No serving identity/tokenizer parity campaign or immutable-hosted-identity gate remains; configured identity cannot detect an undeclared server alias swap. No silent truncation, model swap or Qwen activation. Plain LLM-only imports remain usable without the extra. Prove B01–B08, limit boundaries, batch order, malformed results and normal/optimized minimal installs; REM E, DI-17/18/21–24/33, FC-10/12/14. |
| P-06 `friday-chat` | Source, packaged configuration templates, dependency declaration, tests, user documentation | Delegate `/read` and `/ingest` four-format extraction and file arguments; wire common ingestion and render actual options, counts, provenance and errors. Remove Chat's ingestion character slicer. Default Chat requests Tools' new document-ingestion extra. Wire configured embedding capabilities and typed errors through extraction, metadata inspection, MCP publication and maintenance adapters. Add `ingestion.chunking.strategy/max_tokens`; honor command → YAML → built-in precedence. Existing `smart_file.chunk_size/chunk_overlap` stop governing ingestion. Forward explicit `memory.persist_directory` origin and own request handles/cancellation as detailed below. Document /read has no Memory lease. Lazy entry reuse and a later converter attachment must support text followed by a real document in one lifecycle. Add strict aggregate recovery-v2 handoff/readers for Memory's identity-bearing snapshots. Update packaged configuration examples and setup instructions. | Chat remains a consumer of shared policy. Preserve unrelated commands, model-pool selection, MCP's exact single-record/receipt lifecycle and reorganization sequencing. Keep `/read` available when Memory admission fails; no URL-ingest route or automatic tool storage is added. Preserve the two dirty repository example YAML files. Require real registry-to-fresh-store tests, existing command regressions, metadata/MCP/error projection and strict v1/v2 recovery proof; REM C/E, DI-01–36, FC-01/02/06/10/13. |
| P-07 `friday-runtime` | Source/configuration wiring, tests, README; inherited counter dependencies | Assemble the same public Memory factory and resolved embedding capabilities for pool/non-pool configurations. Preserve explicit `chroma_path`/`runtime_data_root` origin and assemble existing Memory-owned multi-agent consumers under `memory_mode: multi_agent`; preserve visibility and honest partial progress. Defer resourceful startup as required, keep namespace admission before clients/resources, isolate ephemeral kernels and drain owned extraction tasks/sinks during existing shutdown. Expose readiness without an independent legacy-client fallback. Add public entry/converter registration and ordered shutdown; an entry can be registered without a converter and attached later. Supply the required factory from the same capability snapshot in every composition root. | No Runtime-owned chunker, model-selection redesign, new tool activation or runtime engine. Keep independent transcript persistence and existing profile semantics. No Docling dependency for text-only headless Memory/Runtime use. Optional headless document users install the Tools extra and use its public document binding, with no frontend import or new Runtime ingestion YAML section. Test persistent/ephemeral profiles, two-kernel isolation, failed admission before side effects, shutdown and the actual optional Tools import-discovery path and RuntimeMCPProvider observer witness; FC-01/02/06/09/10/12/13. |
| P-08 `friday-cli` | Minimal source/type wiring, tests, README; inherited counter dependencies | Preserve explicit path origin through the compatibility container into Runtime; forwarding a resolved default string alone is insufficient. The selected I2 files carry this narrow adaptation unless an existing mechanism is positively proved. Preserve constructor/re-export behavior and Runtime/Memory readiness. | No new executable, independent client, chunking policy or Docling requirement. Keep environment/default/explicit-setting distinctions and Runtime delegation. Prove B06, explicit fresh-store selection with unset/first-run refusal and Runtime-root consequences, TESTING profile origin and minimal installed compatibility; FC-09/10/12 and the round-8 carry-forward. |

## Packages with indirect impact or compatibility verification only

These packages remain in the assessment because they consume shared services,
protocols or installed dependencies. **No production-source feature upgrade or edit is
currently proposed for them.** Focused consumer tests/fixtures may nevertheless
need restructuring or replacement under the migration map. Source-unchanged does
not mean test-unchanged; production changes beyond the approved paths still
require scope reconciliation before construction.
DI-34 binds the whole-framework consumer audit and all FC-01–14/B01–B08
proofs to these rows; no source-unchanged row is exempt from that disposition.

| ID / package | Planned disposition | Effect to check and preserve |
| --- | --- | --- |
| P-09 `friday-agent` | Source unchanged; explicit integration tests; counter support inherited through Memory | Actual archive/background extraction, `recall_memory`/`store_fact` tools and context consumers must retain input/output and observable failure behavior. Prove the owned inner task finishes; do not treat the Agent wrapper's return as extraction completion. No new scheduler, model selector, Docling dependency or Agent protocol. The existing multi-agent stack is Memory-owned/Runtime-assembled, not a new Agent source feature; its visibility/partial-outcome obligations are detailed below. FC-06/12/13. |
| P-10 `friday-telemetry` | Source and schema unchanged; compatibility checks | Map affected MCP outcomes to existing reason literals at Chat's boundary. Preserve existing event/counter contracts and telemetry-disabled behavior. No new telemetry protocol; record the exact approved byte/token overflow mapping in the final oracle. FC-02 and round-8 carry-forward CF-05. |
| P-11 `friday-transcript` | Source and v1 contracts unchanged; integration checks | Preserve transcript persistence, MCP receipt ownership/readback and existing public interfaces. New aggregate/Memory recovery-v2 models live in their named owners, not in Transcript's v1 schema. Memory's analyzer performs admission before transcript-SQLite reads without changing Transcript; Runtime root-selection consequences are disclosed below. FC-02/04/09/13 and REM recovery handoff. |
| P-12 `friday-mcp` | Transport source unchanged; transitive compatibility checks | Existing transports and server opt-in behavior remain. The affected snapshot-to-Memory integration lives in Memory and Chat; it does not authorize transport edits, new automatic ingestion or document chunking of snapshots. Its optional `full` profile can inherit counters through Agent → Memory; transport-only installation gains no direct Docling/Memory requirement. FC-02/13. |
| P-13 `friday-optimization` | Source/declarations unchanged; Memory-consumer compatibility disposition | Its declared Memory dependency inherits the local counting stack, although current source does not import Memory. Check maintained consumers/imports against the new public Memory/embedding contracts; introduce no optimization algorithm or model-quality change. REM framework inventory and FC-12/13/14. |
| P-14 `friday-finance` | Source/declarations unchanged; import/tool-registration checks | Tools already depends on Finance. The new document extra must not make ordinary Finance imports or existing registered tools require Docling/OCR. No finance calculations or features change. REM framework inventory and FC-12. |
| P-15 `friday-speech` | Source/declarations unchanged; import/registration disposition | Preserve existing Core interfaces and configured speech behavior. No document conversion, tokenizer or embedding requirement is introduced for ordinary speech use. REM framework inventory. |
| P-16 `friday-sandbox` | Source/declarations unchanged; boundary/import disposition | Preserve this package's existing public/import contracts; no sandbox policy or execution engine redesign. Converter access retains the existing Tools-owned `friday_tools.sandbox.FilesystemSandbox` checks. The separate `friday-sandbox` Python-execution integration receives no conversion role. REM framework inventory and companion TD-03/04. |
| P-17 `friday-moltbook` | Source/declarations unchanged; import/registration disposition | No ingestion or embedding feature is assigned here. Record the source-backed unchanged/transitive disposition and configured tool/import compatibility in the all-package inventory. REM framework inventory. |

## First-class test migration deliverable

Substantial test rewrites are expected where setup, architecture, capability
injection, snapshots or intended behavior changes. The
[per-package migration plan](test-migration-plan.md) covers all P-01–17 owners
and cross-package/installed suites. Its dispositions are retain, restructure,
rewrite/replace, retire with reason, and add. Before the first rewrite, the
directive freezes baseline case/fixture IDs and requires an old-to-new map
of requirements, nodes, oracles, replacements, retirements and executed proof.

Every still-valid behavioral requirement retains substantive coverage; obsolete
implementation-specific test bodies and names are not immutable. Update moved
selectors and preserve required gate witnesses. No silent assertion loss,
blanket skip/xfail, production guard bypass, unrelated suite overhaul or
retroactive accepted-evidence edit is permitted. Test/assertion counts alone
are not coverage equivalence. REM G1 and DI-35 make this an acceptance gate.

## Substantive architecture and guide deliverables

The [canonical architecture plan](command-architecture-update-plan.md) requires
`docs/architecture/command-execution.md` for the implemented candidate, plus
substantive rewrites/restructuring of the affected
[guide sections](guide-update-handoff.md), package READMEs and configuration
examples. Document actual Chat command flow/delegation/outcomes, CLI/Runtime
roles, shared ownership/dependencies, deployment, admission and failure behavior.
Reconcile the command/package tables and architecture diagrams with the candidate.

Acceptance requires technical content review, source/schema/metadata mapping,
representative verified command/configuration/install examples and cross-document
consistency, alongside lifecycle/link checks. A check pass does not prove that
needed rewrites were authored or technically correct. REM G2 and DI-36 bind
these deliverables; this planning step rewrites no live guide or architecture.

## Cross-package execution and consumer effects

- **Shared document process — Tools implementation, frontend-neutral ownership:**
  Tools owns conversion/OCR, document planning and the bounded subprocess/IPC
  service. Core owns neutral values/protocols; Memory invokes the injected
  session/planner and owns ingestion policy; Friday-LLM performs embeddings in
  the parent. Chat, Runtime, CLI consumers and a future TUI reuse this service.
  No frontend-owned engine, extra worker pool or new scheduler is introduced.
  Cooperative bounded snapshot/Office checks remain observable; conversion and
  repeated document counting execute in the owned process. `/ingest` holds its
  existing admission through worker quiescence. `/read` takes no Memory lease,
  works without embedding setup and owns/drains its request, including runtime-
  absent use. Cancellation invalidates output; close signals, reaps and cleans
  up before slot release. An unconfirmed reap cannot report success or release
  admission. The worker has no embedding/provider/store capability. Exact cold/
  repeat deadlines, RSS, heartbeat, queue and TERM/KILL/reap criteria are built
  and proved at I3-C4, after implementation; no pre-coding spike is required.
  Native execution is not claimed to be an OS security sandbox.
- **One entry, text first and documents later:** every entry receives its pure
  counter factory at construction independently of document settings. Chat and
  Runtime can own that entry alone, reuse it, and attach the converter later.
  Acceptance must store text then a genuine document through the identical
  entry/lifecycle, with readback and ordered shutdown; ownership spies and
  separate-lifecycle positives are insufficient. Document sessions must match
  their submitted SourceDocument exactly before planning or any write.
- **Multi-agent — Memory ownership, Runtime assembly:** the existing
  `multi_agent` controller, promotion coordinator and journal share the admitted
  underlying physical Memory space under `memory_mode: multi_agent`. Their
  visibility namespaces remain authorization partitions, not independent
  embedding spaces. Keep authorization visibility and honest failed/partial
  promotion reporting. The algorithms/source remain unchanged under the current
  allowlist; necessary wiring is not authority for coordinator/journal edits.
  Require actual FC-13 B/N/R consumer proof; no new transaction or activation.
- **Graph recall and analysis:** maintained Chat/Runtime graph recall stays
  unscored by graph embeddings. Identity-safe comparisons and asynchronous
  fallback belong to separately injected public scorer capabilities (FC-08),
  without new maintained scoring/backfill wiring. The Memory analyzer must admit
  its normalized destination before read-only Chroma or transcript SQLite access
  (FC-04); ordinary store-only inspection does not require embedding inference.

## Dependency, configuration and data consequences

- **Selected installation:** reuse the measured Docling 2.150.0, Docling Core
  2.106.0, RapidOCR 3.10.0/ONNX CPU and python-dateutil 2.9.0.post0 profile.
  The historical combined Friday stack required dateutil 2.9.0.post0; the
  incompatible standalone 4.0.0 requirement is not carried into the product.
  Tools' `document-ingestion` extra is declared/locked at I3-C1 before real
  conversion tests. Chat requests it by default at I3-C3 before command adoption.
  Final clean installed profiles are proved at I3-C5. The root distribution
  inherits Chat's stack; its legacy `documents` extra is not a Docling label.
  Measured target support does not establish every platform or the final new
  product lock. Resolve only this intended delta; inventory hashes/licenses and
  actual installed versions before use. Do not start another vendor evaluation.
- **Headless counting:** LLM's narrow `embedding-limits` extra selects
  `tokenizers==0.23.3`; Memory requests it at I1-C2, with the corresponding lock
  delta. The current shared lock has 0.22.1, already consumed by Chroma and
  LiteLLM, so 0.23.3 affects their existing consumers too. Required I1 unchanged-
  legacy positives cover that change. A resolution conflict stops I1-C2 instead
  of authorizing a different tokenizer/model or an unrelated upgrade.
  Existing tiktoken support is retained for applicable hosted profiles.
  Counter/capability assets are explicit local deployment bindings, not new
  weights shipped in Core/Commands. Text-only headless users need no Docling/OCR.
- **Certifi:** the current lock contains 2025.11.12 with no direct package floor.
  I1/I2 record the locked version, module and CA origin where installed, or
  absence in dependency-free profiles, without an unrelated early upgrade. Tools' Docling extra and lock delta at I3-C1 introduce selected
  2026.10.23 and the required `certifi>=2026.10.19` floor. From I3-C1 onward,
  verify the floor and module/CA origin after each applicable private install,
  including every final I3-C5 normal/optimized headless and Chat profile containing
  Certifi. Record absence in dependency-free profiles rather than add a dependency
  just for validation. This shared CA-bundle upgrade affects all HTTPS consumers,
  including Finance, even where source is unchanged. Keep TLS verification;
  do not install into the working production environment.
- **Two independent local bindings:** embedding operations resolve a provisioned
  manifest by explicit API path, otherwise `FRIDAY_EMBEDDING_MANIFEST` from the
  retained service environment snapshot. Document conversion separately resolves
  explicit settings, otherwise `FRIDAY_DOCUMENT_CONVERSION_MANIFEST`; it supplies
  absolute asset/scratch roots, a profile ID and asset-manifest hash. `/read`
  never resolves the embedding manifest. Text reads and text ingestion require
  no document binding. Missing bindings refuse only the affected capability;
  never search upward, use a global-cache fallback or download on first use.
  These are operator provisioning requirements even though old model YAML keys
  remain parseable. Document settings are captured per request until a converter
  is bound; owned converter settings and embedding capabilities then stay fixed.
- **Ingestion configuration and defaults:** add optional
  `ingestion.chunking.strategy` and `ingestion.chunking.max_tokens`, initially
  `document` and `512`. Resolve each option independently: explicit per-command
  override, then YAML, then built-in default; reject invalid YAML at configuration
  preflight. `smart_file.chunk_size`/`chunk_overlap` currently drive Chat's
  2,048-character slicer but cease governing `/ingest`. They may remain for scoped
  legacy reads/summarization and are not aliases or a second ingestion default.
  No new overlap option is added. Document payloads use `document` chunking and 512 final
  embedding-input tokens, with command overrides for `document`, `recursive`,
  `fixed` and a valid token budget. Supplied text/web/tool payloads share the
  capability. Existing MCP snapshots, conversation/maintenance records and
  derived summaries retain their unsplit semantics under the embedding guard.
  No maintained URL-ingest or generic automatic tool-to-Memory route is invented.
- **Existing embedding configuration:** keep pool/non-pool selection, resilience,
  cache/batch choices and separate extraction/maintenance services. New
  `max_input_tokens` and `expected_dimensions` fields are optional. Configured
  local records supply counting, effective limits, preparation and dimensions
  without requiring a YAML rewrite or external serving attestation. Supported
  defaults need positive offline operation at I2; missing records are failures,
  not compatibility evidence. An out-of-band server/model alias change remains
  undetectable unless the operator changes the declared identity. No default
  model change or actual provider call is authorized by this assessment.
- **Model replacement and existing data:** Qwen 4B remains illustrative. A real
  model/preparation change needs an explicitly selected fresh compatible
  namespace; same dimensions do not establish compatibility. Preserve old
  files; do not reset, re-embed, migrate or mix their vectors. Existing unbound
  stores refuse guarded Memory use while `/read` remains available. Interrupted
  recovery must be handled under the compatible old release before upgrade.
- **Upgrade and first-run effect — existing policy, not a new reset:** current
  persistent Chat/Runtime stores predate `embedding-space.json`; after upgrade,
  those identity-free stores refuse guarded Memory use even if the model name
  remains unchanged. Enabling Nomic task prefixes also changes preparation for
  the same model. Select a fresh absent destination rather than reuse/stamp old
  vectors. Chat uses explicit `memory.persist_directory` and its resolved sibling
  graph path; Runtime uses explicit `chroma_path` with a consistent
  `runtime_data_root`. The vector directory, resolved graph file and configured
  access-WAL path must all be absent, including empty files/directories. Do not
  discover or silently adopt another WAL. Unset/default-derived persistent paths
  never authorize creation, even on first run; an explicit raw value equal to a
  default can qualify if its associated layout is absent. `/read` remains usable
  with the required file assets. Existing matching bound defaults may open;
  ephemeral profiles instead follow their isolated FC-09 policy.
  Choosing a new Runtime data root also selects fresh transcript/artifact
  locations under its existing containment rules. Reusing a root is eligible
  only when its actual vector/graph/configured WAL targets are absent; unrelated
  transcript/artifact files are left alone and not replayed. Reused recovery/log
  roots can still contain incompatible journals and block maintenance; use the
  documented coherent destinations without deleting old evidence. The copied packaged
  template's explicit `.friday/vector` value counts as supplied origin if retained;
  its existing layout still refuses. Preserve the dirty user examples and test
  the committed template in the isolated export.
  Before upgrading, stop writers, complete interrupted recovery with the
  compatible old release, and retain a verified old-release snapshot or consistent
  cold copy of full old state/configuration. Keep the old release for legacy
  restoration: new guarded tooling refuses identity-free snapshots/restores.
  No backup, move, scan, reset or recovery is performed by this assessment.
  REM Existing-store upgrade policy/operator note and handoff A02/A05/A06 govern.
- **Retained dependency edges:** existing lazy/undeclared Core profiles/transcript
  interfaces → Memory, Memory's large-file code chunker → Tools, and Tools memory
  wrappers → Memory remain inventoried legacy edges. Do not broaden or claim to
  repair them here. New neutral contracts and storage injection add no such edge.
- **Other files:** cross-package tests, genuine synthetic fixtures, setup/upgrade
  instructions and local asset manifests are required. Preserve user examples,
  user documents/stores, historical acceptance and review artifacts. No package
  publication or version bump is implied by this assessment.

## Construction commitments and phase exits

The [final approval request](validation/document-ingestion/product-construction/final-approval/README.md)
binds the exact scope and proposed execution profile. The following are staged
implementation duties, not a new requirement to build the worker or rerun Docling
before permission to code.

| Commitment | Exact disposition and required exit |
| --- | --- |
| Interfaces and configuration | Reviewed shared contracts and 91-path map control. I1 adds neutral foundations and local counters without changing old flows; I2 coordinates existing callers, startup, origin and recovery. |
| Local assets | Build phase-local strict document/embedding manifests from provisioned local assets. Record hashes, sizes, sources, licenses and configured model facts before use. Tests never perform first-use downloads or infer production configuration. |
| Compatibility | I2/I3/AG execute positive baseline/replacement operations and separate refusal controls using real local counters, dimension-correct deterministic provider responses and disposable stores. No actual-serving model/parity qualification campaign. |
| Worker and formats | Build I3-C1; command adoption C3; process/IPC/resource/late-output/repeated-cancel/drain and same-entry functional proof C4. Hidden included rows/columns reject the whole workbook; hidden-sheet-only exclusion remains positive. |
| Data and recovery | Explicit fresh namespace, origin and identity rules; strict v1 inspection/v2 active artifact rules; preserve old files. No user reset, re-embedding, migration or backup repair. Existing MCP/backup adaptations remain solely causal compatibility work. FU-013/014 stay unwaived. |
| Dimensions | Retain the existing 8192-dimension ceiling and exact declared output checks. Qwen remains illustrative; offline replacement profiles do not select a production model. |
| Tests | The current map proposes 49 exact old-case exceptions and 51 new witnesses in 18 classified modules. No case is retired in this request. Unlisted valid assertions remain; unexpected rewrites require case-map reconciliation before edit. Existing inventory is reused, not rebuilt as a new campaign. |
| Architecture and guides | I3-C5 authors the canonical architecture and selected guide/README/template updates. DI-35/36 require substantive coverage/content review and verified examples. Link/check passes alone cannot close them. Guide16/17 references are read-only followups unless a later explicit path delta authorizes edits. |
| Dependencies and installs | Narrow counter delta I1-C2, Tools stack I3-C1, default Chat edge I3-C3, final clean normal/optimized installed proof I3-C5. Use a private environment; no root sync or production install. |
| Delivery boundary | INGEST and TOOLS-DOC retain separate completion. No new CLI/TUI executable, public package release, push/merge, production deployment or human acceptance is included. |

## Approval and change control

This remains the single canonical current assessment. The prior v0.6 approval
and council records remain historical evidence for their exact bytes; they are
not reused as approval or independent review of v0.8. The final proposal records
its own hashes and distinguishes unchanged reviewed technical artifacts from this
updated impact and approval wrapper.

Chuck's next task is to review this version and the linked final request, then
approve or request changes to the package impact, construction scope and proposed
isolated execution effects. No construction is activated by the current
"ok proceed" instruction to prepare these documents. Exact approval must be
recorded before product/test/guide implementation or dependency installation.
Future validation runs bind their stable source, lock and phase manifests before
execution. A missing asset or incompatible intended resolution stops the affected
phase without revising the production model or silently expanding scope.

A material new package, path, behavior or dependency expansion returns for
explicit scope review. No new council is launched by this assessment update.
After approved construction, fresh independent implementation validation and
human UAT/acceptance remain separate gates.

Source references: current activation contracts/dispositions/file and case maps;
REM A–G and DI-01–36; compatibility B01–B08/FC-01–14; separate companion TD-01–10;
and preserved Docling/Friday-LLM/Nomic/Chroma results. Measured stack facts do not
claim a product implementation, a current model server or broad retrieval quality.
