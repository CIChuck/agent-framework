# INGEST-001 — Package Impact Assessment

Version: **0.5 — draft for Chuck Russell's review**, 2026-11-11.

This assessment describes **planned changes**, not completed upgrades. It covers
all 17 current workspace packages: eight with proposed implementation changes
(CLI changes are conditional on need), and nine with compatibility obligations
whose production source is expected to remain unchanged; affected tests may
still need restructuring. Dependency effects are identified
separately from source edits. Repository-wide lock, test and provisioning work
is described below the package tables.

Chuck's conditional approval referred to the earlier REM bytes, SHA256
`e1c90753a3e2876df0f9f6f0ca82b1893455266cee1f252276f460b48a9f2a16`.
The REM has since been amended at his direction to require traceable test
restructuring and substantive architecture/guide updates. That earlier approval
does not approve the amended bytes or a construction directive. He requires
satisfaction with the overall per-package impact before approving that directive.
This draft supplies that review input; it does not record satisfaction with the
table, completion of his remaining conditions, Gate-A activation or construction
approval.

## Basis and delivery boundaries

The source of planned scope is the current
[REM](remediation/REM-CMD-INGEST-001-pdf-docx.md), normative
[embedding compatibility contract](embedding-compatibility-contract.md) and
[Tools companion](proposals/tools-document-adoption.md), together with the
[test migration](test-migration-plan.md), [architecture](command-architecture-update-plan.md)
and [guide](guide-update-handoff.md) requirements now explicitly directed by Chuck.

The old technical-design verdict at `f43368c5` and assessment-v0.2 verdict at
`1a040de3` remain historical for their pinned bytes. This v0.5 and the amended
REM require fresh review; those scores are not carried forward. Production source
and package declarations remain unchanged from `f591989e`; no tests, live guides
or architecture implementation has been rewritten during this planning revision.

The work has two distinct delivery obligations:

- **INGEST:** shared conversion capability; Chat's four-format extraction;
  common ingestion/chunking; embedding limits and identity; and the minimum
  adaptations needed to keep existing consumers compatible.
- **TOOLS-DOC companion:** route the existing Tools reader factory and
  `smart_read` document readers through that shared capability, preserving their
  selection/pagination contracts. This needs its own exact directive and
  verification. It is not automatically implemented by installing Docling or
  completing INGEST. Combining the units requires an explicit scope revision.

Revision 0.3 introduced affected-test restructuring and substantive architecture/guide
rewrites as first-class scoped deliverables. Legacy test names/files may change
with a behavioral coverage map and justified retirement; documentation requires
authored technical content and verified examples, not only a checker run.
[Maintainer clarification](validation/document-ingestion/test-doc-revision-authorization.json)
records both decisions and continuation within the original four-review cap.
Revision 0.4 reconciles that test permission with the unchanged normative annex,
clarifies approval provenance and the CLI architecture, and aligns the scoped
test/documentation paths. Revision 0.5 corrects actual test paths and discovery
commands and reconciles current routing under Chuck's one-round extension.
These corrections add no product feature or production-source owner.

The 17-package inventory is derived from root `pyproject.toml` workspace member
patterns and each member's `packages/*/pyproject.toml`, not a directory count.
Ignored cache-only folders without package metadata are not members. The package
names below are workspace directory names. `friday-cli` is the
compatibility library; it gains no standalone launcher. No TUI package or TUI
implementation is added by this plan.

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
| P-02 `friday-tools` | Source, dependency extra, tests, setup documentation | **INGEST:** implement one shared Docling conversion/chunker adapter for PDF/DOCX/XLSX/PPTX, local assets/OCR and non-text Office structural audit, provenance and truthful extraction errors. Add the `document-ingestion` extra with the selected Docling stack and `certifi>=2026.10.19`. Route explicitly injected existing text-storage/cache paths through the common ingestion entry; expose truthful errors from the affected Memory wrappers. Confirmed reset first admits the whole target layout without inference and retains its binding sidecar. **Companion:** subsequently adopt the converter in ReaderFactory and document `smart_read`, including selections and caches. | Bare Tools text operations remain usable without Docling. No new Tools-to-Memory dependency; consume the injected Core interface. No automatic storage activation, general tool rewrite or migration of every direct legacy reader. Test genuine formats, missing dependencies/assets, sandbox denial, cache/storage behavior and minimal imports. INGEST DI-01–25/30/34 and FC-01/07/12/13; companion TD-01–10 is a separate completion claim. |
| P-03 `friday-commands` | Source, tests, README | Add pure raw-tail file-argument parsing so quoted paths and descriptions survive; validate scoped `--chunking=document\|recursive\|fixed` and `--chunk-tokens=N` overrides. Supply reusable argument semantics rather than a Chat-only parser. | Keep the package standard-library-only, its root API54 unchanged, and unrelated command parsing unchanged. No filesystem access, converter, Memory or embedding execution here. Prove quoting, descriptions, exact flag handling and malformed-input refusal headlessly; REM C and DI-05/08/09/16. |
| P-04 `friday-memory` | Source, dependency extra request, tests, README | Own the common ingestion entry and `document`/512-token defaults, deterministic non-Docling segmentation, recursive/fixed strategies, validated plans and storage receipts. Add durable/ephemeral embedding-space admission and correct query/document roles. Propagate identity through vector/graph storage, recall and versioned recovery. Adapt extraction acknowledgement, owned background tasks, logging, lifecycle counts and the existing MCP/maintenance/backup consumers only where the new guard requires it. Retain the existing Memory-owned multi-agent controller/coordinator/journal as source-unchanged consumers of that space, with visibility and partial-failure proof. Request LLM's qualified counter extra through the existing pinned dependency. | The broadest source impact. Preserve record types, protection/description rules and existing maintenance order, prompts, quarantine, rollback and public receipt semantics. No second split of accepted plans; structured/derived records remain unsplit. No Docling/Tools imports in the new policy, storage-engine replacement, user reset/migration or backup repair project. Require ingestion-to-store positives, same-dimension mismatch refusals, matching reopen, graph/recall, extraction, lifecycle, recovery and all FC-01–14 B/N/R proofs. |
| P-05 `friday-llm` | Source, model-profile schema, dependency extra, tests, README | Resolve typed embedding capabilities and model-specific query/document preparation; perform exact local token counting and effective input-limit checks; validate batch correspondence, vector shape and dimensions. Add a narrow `embedding-limits` extra for qualified local counters. These protections apply to existing embedding callers as well as document ingestion. | Keep existing pool/non-pool configuration families and selection/resilience rules. Missing new profile fields use a verified readiness record, not invented limits; unqualified deployments stop affected execution. No silent truncation, model swap or Qwen activation. Plain LLM-only imports remain usable without the extra. Prove B01–B08, limit boundaries, batch order, malformed results and normal/optimized minimal installs; REM E, DI-17/18/21–24/33, FC-10/12/14. |
| P-06 `friday-chat` | Source, packaged configuration templates, dependency declaration, tests, user documentation | Delegate `/read` and `/ingest` four-format extraction and file arguments; wire common ingestion and render actual options, counts, provenance and errors. Remove Chat's ingestion character slicer. Default Chat requests Tools' new document-ingestion extra. Wire qualified embedding capabilities and typed errors through extraction, metadata inspection, MCP publication and maintenance adapters. Add `ingestion.chunking.strategy/max_tokens`; honor command → YAML → built-in precedence. Existing `smart_file.chunk_size/chunk_overlap` stop governing ingestion. Forward explicit `memory.persist_directory` origin and own conversion admission/cancellation as detailed below. Add strict aggregate recovery-v2 handoff/readers for Memory's identity-bearing snapshots. Update packaged configuration examples and setup instructions. | Chat remains a consumer of shared policy. Preserve unrelated commands, model-pool selection, MCP's exact single-record/receipt lifecycle and reorganization sequencing. Keep `/read` available when Memory admission fails; no URL-ingest route or automatic tool storage is added. Preserve the two dirty repository example YAML files. Require real registry-to-fresh-store tests, existing command regressions, metadata/MCP/error projection and strict v1/v2 recovery proof; REM C/E, DI-01–36, FC-01/02/06/10/13. |
| P-07 `friday-runtime` | Source/configuration wiring, tests, README; inherited counter dependencies | Assemble the same public Memory factory and resolved embedding capabilities for pool/non-pool configurations. Preserve explicit `chroma_path`/`runtime_data_root` origin and assemble existing Memory-owned multi-agent consumers under `memory_mode: multi_agent`; preserve visibility and honest partial progress. Defer resourceful startup as required, keep namespace admission before clients/resources, isolate ephemeral kernels and drain owned extraction tasks/sinks during existing shutdown. Expose readiness without an independent legacy-client fallback. | No Runtime-owned chunker, model-selection redesign, new tool activation or runtime engine. Keep independent transcript persistence and existing profile semantics. No Docling dependency for a headless Memory/Runtime installation. Test persistent/ephemeral profiles, two-kernel isolation, failed admission before side effects, shutdown and the actual optional Tools import-discovery path and RuntimeMCPProvider observer witness; FC-01/02/06/09/10/12/13. |
| P-08 `friday-cli` | Conditional source/type wiring, tests, README; inherited counter dependencies | Make only the compatibility-container/profile adaptations needed to forward explicit configuration origin and Runtime/Memory readiness while preserving existing constructor and re-export behavior. If the existing delegation already satisfies the contract, the directive records source unchanged with the required tests. | No new executable, independent client, chunking policy or Docling requirement. Keep environment/default/explicit-setting distinctions and Runtime delegation. Prove B06, explicit fresh-store selection with unset/first-run refusal and Runtime-root consequences, TESTING profile origin and minimal installed compatibility; FC-09/10/12 and the round-8 carry-forward. |

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
| P-13 `friday-optimization` | Source/declarations unchanged; Memory-consumer compatibility disposition | Its declared Memory dependency will inherit the qualified counting stack. Check maintained consumers/imports against the new public Memory/embedding contracts; introduce no optimization algorithm or model-quality change. REM framework inventory and FC-12/13/14. |
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

- **Document worker — Tools/LLM capability, Chat request ownership:** conversion,
  OCR, structural audit and repeated chunk counting run off Chat's event loop in
  an owned bounded worker. Final LLM preflight is offloaded when needed. The
  worker has no embedding/provider/store capability. Chat retains shared command
  admission through conversion and until worker quiescence; competing maintenance
  may report busy. Cancellation makes the request ineligible for storage,
  discards late results and waits for quiescence before releasing resources.
  Progress/finishing remains observable; no instantaneous native-thread kill,
  OS-sandbox or new transaction guarantee is made. Gate A measures limits and
  worst-case cancellation; unsupported behavior stops readiness. This is distinct
  from FC-06's existing conversation-extraction task. REM Execution/cancellation/
  admission and DI-11/26 govern the worker; no general scheduler is introduced.
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

- **Document installation:** the intended default Chat dependency graph grows
  through Tools' `document-ingestion` extra. Its final versions, wheel/platform
  support, licenses, size and resource costs are unmeasured. Keep legacy Tools
  extras explicit; installing them alone must not be described as Docling support.
- **Headless counting:** Memory requests LLM's narrow counter extra; its existing
  Runtime/CLI/Agent consumers inherit it. That does not pull the Docling/OCR stack
  into those profiles. Exact counter requirements and asset packaging are Gate-A
  outputs, not already selected packages.
- **Certifi:** enforce `certifi>=2026.10.19` in the new document profile and verify
  the effective post-install version. The `uv.lock` delta is deliberate and must
  inventory all transitive changes; unrelated upgrades require reconciliation.
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
- **Existing embedding configuration:** retain current service selection and
  resilience semantics, including Chat's pool-default precedence and separate
  qualified extraction/maintenance services. Missing capability fields do not
  force a YAML rewrite, but execution still needs verified identity, counting,
  capacity and dimensions. The hosted baseline may not qualify; report that
  incompatibility to Chuck instead of changing the default or weakening safety.
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
  documented coherent destinations without deleting old evidence. The packaged
  template's explicit `.friday/vector` origin remains a directive decision below.
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

## Details to settle before construction approval

| Decision/detail | Required readiness result or final-directive binding |
| --- | --- |
| Exact installation | One qualified Docling release, transitive graph, required Office backends/chunking dependencies, Certifi floor and reproducible package/asset hashes on the target profile. |
| Assets and resource effects | One local CPU OCR choice and qualified tokenizer/layout/table assets, licenses, manifest-owned locations and numeric download/disk/time/memory limits. No implicit first-use downloads. |
| Baseline and replacement behavior | Complete B01–B08 and per-consumer trace table; baseline and replacement-model positives as well as refusals. Operational correctness is distinct from later relevance/duplicate-quality evaluation. |
| Contracts and recovery | Exact public signatures/receipts, collection-name/backend limits, fresh-root origin rules, query-vector identity/empty-vector behavior, v2 artifact combinations and participant-fingerprint timing. |
| Backup/MCP compatibility | Paired public baseline/candidate proofs; preserve defaults, pending snapshot IDs and receipt ownership. Prevent live binding-marker overwrite and colliding evidence names. FU-013/014 remain separate unwaived defects and receive no positive-test credit; no backup repair engine or MCP cleanup project. |
| Tools completion boundary | Keep INGEST and TOOLS-DOC directives/proofs distinct. Obtain an explicit revised combined scope if Chuck wants both delivered as one construction unit. |
| Packaged-template origin | Resolve handoff OPUS-R4-A05 explicitly: the current packaged `.friday/vector` literal counts as supplied origin if retained in a copied configuration and its layout is absent. A changed template requires an exact approved delta. Neither choice stamps existing roots or rewrites the user's examples. |
| Replacement dimensions | Retain FC-11's `VectorCollectionDimension8192` ceiling. Qualify the actual selected model/dimension against it; this unit does not remove that ceiling or make Qwen a selection. |
| Test migration inventory | Freeze the per-package baseline test/fixture inventory, exact old/new node/path and oracle mapping, justified retirements and independent coverage review before test rewrites. Changed test source is scoped implementation work; DI-35 binds acceptance. |
| Architecture and documentation | Freeze the canonical architecture path and affected guide/README/configuration sections, required authored rewrites, source/example verification matrix and substantive independent review. Structural checks alone do not meet DI-36. |
| Exact package/path coverage | Resolve P-08's conditional edits; map every final file to the package rows and approved allowlist. A newly affected package or material expansion comes back for review. |

## Approval and change control

This is the **single canonical package impact assessment**. The packet links it
alongside the current amended REM. The annex and Tools companion retain their
reviewed bytes; the REM was amended at Chuck's direction and is included in the
fresh review. The final directive must bind the amended REM and exact final
assessment, rather than reuse approval of the earlier REM hash. This document
summarizes scope and unresolved details; it grants no broader edit authority.
The assessment has its own [review criteria](validation/document-ingestion/package-impact/review-criteria.md)
and [original four-round council authorization](validation/document-ingestion/package-impact/iteration-authorization.json),
now extended by [exactly one additional round](validation/document-ingestion/package-impact/round5-authorization.json).
The current review includes the amended REM and explicit test/documentation
requirements. Chuck reviews the linked draft in parallel. Earlier council
verdicts do not cover these changed bytes or presume his satisfaction.

1. Chuck reviews this draft and supplies any remaining conditions on his REM
   approval. Record satisfaction with the package impact explicitly; drafting it
   is not that approval.
2. Prepare and separately activate the bounded Gate-A plan. Refine this
   assessment with its measured dependency/model/format findings. A material
   impact change requires renewed review before construction.
3. Record Chuck's satisfaction against the exact final post-Gate-A version,
   commit and SHA256. The construction directive includes that assessment as a
   **required referenced appendix** with its exact path list and tests. An edit
   after satisfaction creates new bytes: reconfirm the version bound into the
   directive rather than reuse approval of the old hash. Material scope changes
   additionally return for renewed impact review. Keep one authoritative copy.
4. Do not approve or begin construction until Chuck is satisfied with the exact
   package impact and separately approves the directive. The original four rounds
   are complete; Chuck now authorizes exactly one additional full council, round
   5 of 5. This is no reset or further loop; stop for guidance if its gate is unmet.
   No installs, product code, model/store operation, push or delivery is
   authorized by the assessment or its review.

Source references: REM ownership, active-route and proposed-path tables;
REM A–G and DI-01–36; compatibility contract B01–B08/FC-01–14; companion
TD-01–10; current package `pyproject.toml` declarations; and
[round-8 carry-forward](validation/document-ingestion/council-round8/readiness-carry-forward.md).
