# INGEST-001 — Package Impact Assessment

Version: **0.1 — draft for Chuck Russell's review**, 2026-11-11.

This assessment describes **planned changes**, not completed upgrades. It covers
all 17 current workspace packages: eight with proposed implementation changes
(CLI changes are conditional on need), and nine with compatibility obligations
whose source is expected to remain unchanged. Dependency effects are identified
separately from source edits. Repository-wide lock, test and provisioning work
is described below the package tables.

Chuck's approval of REM-CMD-INGEST-001 is conditional. He requires satisfaction
with the overall per-package impact before approving the construction directive.
This draft supplies that review input; it does not record satisfaction with the
table, completion of his remaining conditions, Gate-A activation or construction
approval.

## Basis and delivery boundaries

The source of planned scope is the reviewed
[REM](remediation/REM-CMD-INGEST-001-pdf-docx.md), its normative
[embedding compatibility contract](embedding-compatibility-contract.md), and the
[Tools adoption companion](proposals/tools-document-adoption.md). Their technical
bytes remain those reviewed at `f43368c503da19fd245730ee579806db95ed3748`;
the [reconciled report](validation/document-ingestion/compatibility-verified-report.md)
records design readiness only. This assessment was prepared from the packet and
package declarations at `8390f3688d00985b1cac0443da8105f33fb1a6b7`.

The work has two distinct delivery obligations:

- **INGEST:** shared conversion capability; Chat's four-format extraction;
  common ingestion/chunking; embedding limits and identity; and the minimum
  adaptations needed to keep existing consumers compatible.
- **TOOLS-DOC companion:** route the existing Tools reader factory and
  `smart_read` document readers through that shared capability, preserving their
  selection/pagination contracts. This needs its own exact directive and
  verification. It is not automatically implemented by installing Docling or
  completing INGEST. Combining the units requires an explicit scope revision.

The package names below are workspace directory names. `friday-cli` is the
compatibility library; it gains no standalone launcher. No TUI package or TUI
implementation is added by this plan.

## Packages with proposed implementation changes

“Source” includes narrowly scoped interfaces, configuration models or wiring.
Every row includes focused tests and documentation where needed. Exact versions,
signatures and conditional edits remain subject to Gate-A qualification and the
final directive's approved path list.

| ID / package | Change types | Planned upgrade and purpose | Compatibility boundary and required evidence |
| --- | --- | --- | --- |
| P-01 `friday-core` | Source, public contracts, tests | Add immutable source/block/chunk/options and ingestion-receipt contracts; an injected ingestion-entry interface; and typed embedding-space, prepared-vector/query and explicit-origin/admission contracts. Existing store factories forward that information. This gives Chat, Tools and headless consumers a common interface without making Core own conversion or ingestion policy. | No Docling, tokenizer or new Memory/backend dependency in the neutral contracts. Retain existing lazy adapter imports and unrelated public interfaces. Prove Core factory propagation and headless injection; REM ownership/path table, DI-18/19/29/33, FC-10/12. |
| P-02 `friday-tools` | Source, dependency extra, tests, setup documentation | **INGEST:** implement one shared Docling conversion/chunker adapter for PDF/DOCX/XLSX/PPTX, local assets/OCR, provenance and truthful extraction errors. Add the `document-ingestion` extra with the selected Docling stack and `certifi>=2026.10.19`. Route explicitly injected existing text-storage/cache paths through the common ingestion entry; expose truthful errors from the affected Memory wrappers. **Companion:** subsequently adopt the converter in ReaderFactory and document `smart_read`, including selections and caches. | Bare Tools text operations remain usable without Docling. No new Tools-to-Memory dependency; consume the injected Core interface. No automatic storage activation, general tool rewrite or migration of every direct legacy reader. Test genuine formats, missing dependencies/assets, sandbox denial, cache/storage behavior and minimal imports. INGEST DI-01–24 and FC-01/07/12/13; companion TD-01–10 is a separate completion claim. |
| P-03 `friday-commands` | Source, tests | Add pure raw-tail file-argument parsing so quoted paths and descriptions survive; validate scoped `--chunking=document\|recursive\|fixed` and `--chunk-tokens=N` overrides. Supply reusable argument semantics rather than a Chat-only parser. | Keep the package standard-library-only, its root API54 unchanged, and unrelated command parsing unchanged. No filesystem access, converter, Memory or embedding execution here. Prove quoting, descriptions, exact flag handling and malformed-input refusal headlessly; REM C and DI-05/08/09/16. |
| P-04 `friday-memory` | Source, dependency extra request, tests | Own the common ingestion entry and `document`/512-token defaults, deterministic non-Docling segmentation, recursive/fixed strategies, validated plans and storage receipts. Add durable/ephemeral embedding-space admission and correct query/document roles. Propagate identity through vector/graph storage, recall and versioned recovery. Adapt extraction acknowledgement, owned background tasks, logging, lifecycle counts and the existing MCP/maintenance/backup consumers only where the new guard requires it. Request LLM's qualified counter extra through the existing pinned dependency. | The broadest source impact. Preserve record types, protection/description rules and existing maintenance order, prompts, quarantine, rollback and public receipt semantics. No second split of accepted plans; structured/derived records remain unsplit. No Docling/Tools imports in the new policy, storage-engine replacement, user reset/migration or backup repair project. Require ingestion-to-store positives, same-dimension mismatch refusals, matching reopen, graph/recall, extraction, lifecycle, recovery and all FC-01–14 B/N/R proofs. |
| P-05 `friday-llm` | Source, model-profile schema, dependency extra, tests | Resolve typed embedding capabilities and model-specific query/document preparation; perform exact local token counting and effective input-limit checks; validate batch correspondence, vector shape and dimensions. Add a narrow `embedding-limits` extra for qualified local counters. These protections apply to existing embedding callers as well as document ingestion. | Keep existing pool/non-pool configuration families and selection/resilience rules. Missing new profile fields use a verified readiness record, not invented limits; unqualified deployments stop affected execution. No silent truncation, model swap or Qwen activation. Plain LLM-only imports remain usable without the extra. Prove B01–B08, limit boundaries, batch order, malformed results and normal/optimized minimal installs; REM E, DI-17/18/21–24/33, FC-10/12/14. |
| P-06 `friday-chat` | Source, packaged configuration templates, dependency declaration, tests, user documentation | Delegate `/read` and `/ingest` four-format extraction and file arguments; wire common ingestion and render actual options, counts, provenance and errors. Remove Chat's ingestion character slicer. Default Chat requests Tools' new document-ingestion extra. Wire qualified embedding capabilities and typed errors through extraction, metadata inspection, MCP publication and maintenance adapters. Add strict aggregate recovery-v2 handoff/readers for Memory's identity-bearing snapshots. Update packaged configuration examples and setup instructions. | Chat remains a consumer of shared policy. Preserve unrelated commands, model-pool selection, MCP's exact single-record/receipt lifecycle and reorganization sequencing. Keep `/read` available when Memory admission fails; no URL-ingest route or automatic tool storage is added. Preserve the two dirty repository example YAML files. Require real registry-to-fresh-store tests, existing command regressions, metadata/MCP/error projection and strict v1/v2 recovery proof; REM C/E, DI-01–33, FC-01/02/06/10/13. |
| P-07 `friday-runtime` | Source/configuration wiring, tests; inherited counter dependencies | Assemble the same public Memory factory and resolved embedding capabilities for pool/non-pool configurations. Preserve explicit path origin, defer resourceful startup until admission, isolate ephemeral kernels and drain owned extraction tasks/sinks during existing shutdown. Expose readiness without an independent legacy-client fallback. | No Runtime-owned chunker, model-selection redesign, new tool activation or runtime engine. Keep independent transcript persistence and existing profile semantics. No Docling dependency for a headless Memory/Runtime installation. Test persistent/ephemeral profiles, two-kernel isolation, failed admission before side effects, shutdown and the actual optional Tools import-discovery path; FC-01/06/09/10/12/13. |
| P-08 `friday-cli` | Conditional source/type wiring, tests; inherited counter dependencies | Make only the compatibility-container/profile adaptations needed to forward explicit configuration origin and Runtime/Memory readiness while preserving existing constructor and re-export behavior. If the existing delegation already satisfies the contract, the directive records source unchanged with the required tests. | No new executable, independent client, chunking policy or Docling requirement. Keep environment/default/explicit-setting distinctions and Runtime delegation. Prove B06, explicit fresh-store selection, TESTING profile origin and minimal installed compatibility; FC-09/10/12 and the round-8 carry-forward. |

## Packages with indirect impact or compatibility verification only

These packages remain in the assessment because they consume shared services,
protocols or installed dependencies. **No feature upgrade or source edit is
currently proposed for them.** Focused tests may be added or extended where the
REM permits them; source changes beyond the approved path list require scope
reconciliation before construction.

| ID / package | Planned disposition | Effect to check and preserve |
| --- | --- | --- |
| P-09 `friday-agent` | Source unchanged; explicit integration tests; counter support inherited through Memory | Actual archive/background extraction, `recall_memory`/`store_fact` tools and context consumers must retain input/output and observable failure behavior. Prove the owned inner task finishes; do not treat the Agent wrapper's return as extraction completion. No new scheduler, model selector, Docling dependency or Agent protocol. FC-06/12/13. |
| P-10 `friday-telemetry` | Source and schema unchanged; compatibility checks | Map affected MCP outcomes to existing reason literals at Chat's boundary. Preserve existing event/counter contracts and telemetry-disabled behavior. No new telemetry protocol; record the exact approved byte/token overflow mapping in the final oracle. FC-02 and round-8 carry-forward CF-05. |
| P-11 `friday-transcript` | Source and v1 contracts unchanged; integration checks | Preserve transcript persistence, MCP receipt ownership/readback and existing public interfaces. New aggregate/Memory recovery-v2 models live in their named owners, not in Transcript's v1 schema. FC-02/09/13 and REM recovery handoff. |
| P-12 `friday-mcp` | Transport source unchanged; transitive compatibility checks | Existing transports and server opt-in behavior remain. The affected snapshot-to-Memory integration lives in Memory and Chat; it does not authorize transport edits, new automatic ingestion or document chunking of snapshots. FC-02/13. |
| P-13 `friday-optimization` | Source/declarations unchanged; Memory-consumer compatibility disposition | Its declared Memory dependency can inherit the qualified counting stack. Check maintained consumers/imports against the new public Memory/embedding contracts; introduce no optimization algorithm or model-quality change. REM framework inventory and FC-12/13/14. |
| P-14 `friday-finance` | Source/declarations unchanged; import/tool-registration checks | Tools already depends on Finance. The new document extra must not make ordinary Finance imports or existing registered tools require Docling/OCR. No finance calculations or features change. REM framework inventory and FC-12. |
| P-15 `friday-speech` | Source/declarations unchanged; import/registration disposition | Preserve existing Core interfaces and configured speech behavior. No document conversion, tokenizer or embedding requirement is introduced for ordinary speech use. REM framework inventory. |
| P-16 `friday-sandbox` | Source/declarations unchanged; boundary/import disposition | Preserve this package's existing public/import contracts; no sandbox policy or execution engine redesign. Converter access retains the existing Tools-side filesystem sandbox checks, without assigning this package a new conversion role. REM framework inventory and companion TD-03/04. |
| P-17 `friday-moltbook` | Source/declarations unchanged; import/registration disposition | No ingestion or embedding feature is assigned here. Record the source-backed unchanged/transitive disposition and configured tool/import compatibility in the all-package inventory. REM framework inventory. |

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
- **Ingestion defaults:** document payloads use `document` chunking and 512 final
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
| Backup/MCP compatibility | Paired public baseline/candidate proofs; preserve defaults, pending snapshot IDs and receipt ownership. Prevent live binding-marker overwrite and colliding evidence names. FU-013/014 remain separate unwaived defects; no backup repair engine or MCP cleanup project. |
| Tools completion boundary | Keep INGEST and TOOLS-DOC directives/proofs distinct. Obtain an explicit revised combined scope if Chuck wants both delivered as one construction unit. |
| Exact package/path coverage | Resolve P-08's conditional edits; map every final file to the package rows and approved allowlist. A newly affected package or material expansion comes back for review. |

## Approval and change control

This is the **single canonical package impact assessment**. The current packet
links it alongside the frozen REM; the REM/annex/companion are not rewritten to
add a navigation link or alter their reviewed hashes. This document summarizes
their scope and exposes unresolved details; it grants no broader edit authority.
The assessment has its own [review criteria](validation/document-ingestion/package-impact/review-criteria.md)
and [four-round council authorization](validation/document-ingestion/package-impact/iteration-authorization.json).
Its council review and Chuck's parallel review are separate from the earlier
technical-design verdict; neither presumes his satisfaction with this table.

1. Chuck reviews this draft and supplies any remaining conditions on his REM
   approval. Record satisfaction with the package impact explicitly; drafting it
   is not that approval.
2. Prepare and separately activate the bounded Gate-A plan. Refine this
   assessment with its measured dependency/model/format findings. A material
   impact change requires renewed review before construction.
3. The final construction directive includes this assessment as a **required
   referenced appendix**, binding its approved version, commit and SHA256 along
   with the exact path list and tests. Keep one authoritative copy.
4. Do not approve or begin construction until Chuck is satisfied with the exact
   package impact and separately approves the directive. The subsequently
   authorized council may review and iterate this document up to four rounds.
   No installs, product code, model/store operation, push or delivery is
   authorized by the assessment or its review.

Source references: REM ownership, active-route and proposed-path tables;
REM A–F and DI-01–33; compatibility contract B01–B08/FC-01–14; companion
TD-01–10; current package `pyproject.toml` declarations; and
[round-8 carry-forward](validation/document-ingestion/council-round8/readiness-carry-forward.md).
