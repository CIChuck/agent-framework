# INGEST — final construction approval request

Version 1, 2026-11-13. **Prepared for Chuck's review; not approved or activated.**

## What is finalized

The shared ingestion design is complete. The [activation council](../activation/council/round7/results/report.md)
finished at candidate `9ddaf6f8`; all three complete reviews meet the 9.5 gate
with no mandatory findings. The reviewed contracts and exact file/test maps
remain unchanged. Docling's completed evaluation is reused.

The canonical [package impact assessment v0.7](../../../../package-impact-assessment.md)
now describes the selected dependencies, shared process, independent document
settings, text-first entry reuse, configured embedding guards, tests, substantive
documentation and upgrade consequences. Its previous v0.6 approval remains
historical; this changed version is presented for approval. This new assessment
and approval assembly have controller checks, not a new independent council verdict.

## Your next task

Read the impact assessment and the scope/effects below. Approve this request or
identify changes. A clear approval can cover **all three construction slices and
the bounded private execution profile**, with advancement conditional on each
slice's required independent verification. It does not need repeated permission
for already approved work within these bounds.

The [exact approval manifest](approval-request.json) pins the documents, maps,
selected versions, phase responsibilities and [proposed execution profile](execution-profile.json).
The recorded approval will bind its SHA256 and the presented commit before any
product/test/guide change or dependency installation. The current “ok proceed”
authorized preparation of this package, not construction.

The earlier activation `approval-binding.json` is preserved as the reviewed
proposal at `9ddaf6f8`; its v0.6 impact digest is historical. This request replaces
that approval assembly for the revised impact and proposed execution effects,
while retaining its exact technical design and case/file maps. Do not treat the
old digest as a claim that the current canonical assessment is still v0.6.

## What approval would authorize

| Stage | Concrete work | Required exit before advancing |
| --- | --- | --- |
| I1 — shared foundations | Core ingestion/vector/open-intent contracts; LLM configured capabilities, local counters, preparation and full-batch checks; Memory namespace/v2 foundations; narrow counter metadata/lock changes. | Foundation and public-boundary tests; unchanged legacy positives; normal/optimized invariant controls; independent implementation verification. No early switch of legacy preparation or cache identity. |
| I2 — existing consumers | Coordinate Chat/Runtime/CLI origin and startup wiring, existing embedding callers, tasks/errors, graph/vector identity and strict recovery compatibility. | Positive baseline/replacement consumer operations and separate refusals in disposable stores; supported configured defaults resolve; per-slice case migration and independent verification. No serving/parity campaign. |
| I3 — document ingestion | Tools shared converter/process and document extra at C1; Memory shared planning/storage and headless reuse at C2; Commands parser and Chat adoption/default document edge at C3; worker/lifecycle proof at C4; final installed profiles and authored docs at C5. | Genuine PDF/DOCX/XLSX/PPTX and text ingestion; registry-to-store readback/reopen; same-entry text then late document ingestion; real process/cancel/resource tests; installed normal/optimized lanes; migration and documentation acceptance. |
| Aggregate | Freeze the implemented candidate and review the complete affected behavior, tests and authored documentation. | Fresh independent code council before human UAT. A runtime pass cannot be inferred from the current design verdict. |

The unchanged [91-path source/metadata/document map](../activation/slice-file-map.json)
and [case map](../activation/test-case-map.json) are the exact edit boundaries.
The latter proposes 49 old-case exceptions, 51 new witnesses and 18 classified
modules; it retires no case. Unlisted valid assertions stay retained. Exact
selectors and asset/lock identities are recorded before their phase executes;
an unexpected helper, rewrite, dependency or source path is reconciled before use.
Counts identify scope and are not proof of coverage.

The selected [shared contracts](../activation/shared-contracts.md) supply exact
public signatures and lifecycle rules. The [current dispositions](../activation/requirement-reconciliation.md)
override only the specifically superseded historical obligations. Review of the
remaining normative parents is not replaced by this short approval index.

## Dependencies and deployment effects

- Reuse Docling 2.150.0, Docling Core 2.106.0 and RapidOCR 3.10.0 with ONNX CPU;
  use the compatible python-dateutil 2.9.0.post0 constraint. The new Tools extra
  is `document-ingestion`, requested by default Chat before command adoption.
- LLM's narrow `embedding-limits` extra selects tokenizers 0.23.3. Memory requests
  that extra; text-only headless use does not gain the Docling/OCR stack.
- Preserve the Certifi floor **>=2026.10.19**, using measured 2026.10.23 in the
  selected profile. Verify it after every private install. The shared lock/CA
  bundle affects all HTTPS consumers, including source-unchanged packages.
- Keep existing model YAML and pool/resilience selection compatible. Provision
  explicit local capability/counter assets. Optional input/dimension fields
  cannot silently truncate or admit incompatible vectors. No Qwen selection,
  model switch, serving-identity or tokenizer-parity experiment is included.
- Document conversion has its own local binding, independent of embeddings:
  explicit API path, otherwise `FRIDAY_DOCUMENT_CONVERSION_MANIFEST`.
  Embedding operations use their separate `FRIDAY_EMBEDDING_MANIFEST` binding.
  No new required Runtime ingestion YAML section or first-use downloads.

Product lock changes are part of the approved implementation, not already
installed facts. Before installing a phase, record the stable source/lock,
resolved artifacts, asset manifests and private interpreter in its run binding.
This is ordinary construction evidence preparation; it does not require a
finished converter or a new package-evaluation project before coding starts.

## Operator-visible behavior to approve

1. `/ingest` uses real extraction, quoted paths and the common defaults:
   `document` chunking and 512 final embedding-input tokens. Command options
   override YAML, which overrides built-ins, independently for each field.
   Supported strategies are `document`, `recursive` and `fixed`. A budget above
   effective model capacity refuses instead of clamping.
2. Included XLSX sheets with hidden rows/columns cause an actionable whole-
   workbook refusal before conversion or writes. Hidden-sheet exclusion remains
   supported. Empty, corrupt, partial or unsupported documents cannot become
   placeholder or diagnostic text in Memory.
3. `/read` takes no Memory lease and needs no embedding setup. Plain-text reads
   require no document binding. Text ingestion needs embedding capabilities but
   no converter; later document ingestion must reuse the same entry successfully.
4. Conversion uses the shared Tools process service for Chat and headless users.
   Cancellation, timeout, progress and shutdown have common ownership. Actual
   worker limits are proved at I3-C4 after building it.
5. Existing unbound stores refuse guarded Memory use. Operators explicitly
   select coherent fresh vector/graph/WAL locations; no old files are stamped,
   reset, migrated or re-embedded. A new Runtime data root also changes transcript/
   artifact locations. Old-release recovery/backup guidance is required.

## Execution and production boundary

Approval would allow source/test/documentation edits only within the exact maps,
and private dependency resolution, builds, installs, fixture conversion, counters,
deterministic embedding substitutes and disposable Chroma tests under the bound
profile. Generated environments/configuration/assets/data/output live under a
new run beneath `.friday_test/ingest-product/`. Test code stays in the selected
package suites and `tests/integration`; no new readiness harness is introduced.

The working `.venv`, user `.friday*` stores, dirty YAML examples, exports, global
caches and running model services are not install or test targets. Source edits
occur on the feature branch; they are not deployment into a running application.
No current production shutdown or reserved LM Studio window is assumed.

Tests make no external provider/model calls. Private dependency/asset preparation
may fetch only the selected, recorded public artifacts; tests run offline, with
only explicitly owned local fixture-server connections where required. No LM
Studio/OpenRouter/other model endpoint, credential-bearing Finance integration,
production reset, package publication, push, merge or release is included.
Live-model UAT requires its own later explicit window/effects authorization.

## Tests and documentation are construction deliverables

Retained/replacement coverage must preserve every still-valid behavior with the
approved old-to-new map. Do not rebuild the old AST inventory as a new review
campaign or weaken assertions to make code pass. Finance's offline selector is
`packages/friday-finance/tests/test_basics.py`; its live integration file stays
excluded from reading/parsing/execution. Root integration and Transcript selectors
are explicit because root test discovery omits them.

I3-C5 authors `docs/architecture/command-execution.md`, the selected Friday guide
chapters, eight package READMEs and allowed templates. It must distinguish the
three registries, actual Chat versus placeholder CLI entry points, package extras,
local bindings, first-run/upgrade refusal and shared process ownership. Source/
schema checks, verified examples and substantive independent content review are
required alongside link checks. No live guide is rewritten in this preparation.

## What remains separate

TOOLS-DOC ReaderFactory/document smart_read adoption has its own directive and
acceptance. INGEST includes the shared capability and existing text-storage
handoff, not every Tools document entry point. Existing MCP/backup adaptations
are bounded compatibility work, not new projects. FU-013/014 remain unwaived.

Implementation acceptance, human UAT, deployment and delivery are separate from
this requested construction approval. If a phase discovers a material scope or
effects expansion, return that specific change for review; do not silently change
models, paths, contracts or provider permissions. No additional design council is
launched by this package preparation.

The [preparation checks](preparation-checks.json) cover the exact hashes, all 17
package rows, phase/case-map consistency, links, board/documentation/metadata and
preserved production state. They establish this planning handoff, not executed
product tests or independent approval of the new wrapper.
