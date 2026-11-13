# CD-CMD-INGEST-001 — shared document ingestion implementation

Version: **0.1, conditional construction draft**, 2026-11-12.
Initiative: `friday-command-refactor`; branch: `feature/cmd-ingest-001`.
Source and test baseline: `8c36d8e26c618032c1ff536004a582c07ec56a5b`.
Execution phase: **planning**; validation state: **pending**.

Chuck's latest “proceed” authorizes preparation of this directive from the
measured evaluation. It does not approve these new bytes, close whole Gate A,
or activate production implementation. No product code, tests, dependencies,
configuration or stores change during preparation. This draft is for his review
before any council is invoked. Previous review-loop budgets are not renewed.

## 1. Authority, objective and activation

The [authority manifest](../validation/document-ingestion/product-construction/authority-manifest.json)
pins the following inputs. Explicit maintainer direction and repository policies
control; this directive cannot silently relax a parent requirement.

- [REM-CMD-INGEST-001](../remediation/REM-CMD-INGEST-001-pdf-docx.md), including
  DI-01–36, and its [framework compatibility contract](../embedding-compatibility-contract.md),
  including B01–08 and FC-01–14.
- **Required impact appendix:** the exact approved
  [Package Impact Assessment v0.6](../package-impact-assessment.md), SHA256
  `f570318f704fe3c5ba29b62860148b45eb31d15243fcf0eb6acd76bc9d218176`,
  together with the measured differences and open decisions in the
  [readiness decision](../validation/document-ingestion/product-construction/readiness-decision.md).
  The approved assessment is preserved. Material changes require a separately
  bound addendum and Chuck's satisfaction, rather than extending his old approval.
- [Test migration](../test-migration-plan.md),
  [canonical architecture](../command-architecture-update-plan.md), and
  [Friday guide requirements](../guide-update-handoff.md).
- [Repository engineering](../../../../reference/policies/repository-engineering-policy.md)
  and [independent validation](../../../../reference/policies/independent-validation-policy.md)
  policies. Work remains started/local through implementation and review.

The outcome is one reusable extraction → chunk planning → embedding → storage
path for the maintained local-file `/ingest` command and the explicitly named
public ingestion capabilities. Chat delegates; another frontend can consume
the shared implementation without importing Chat. `/read` uses the same extracted
source without initializing embeddings or writing Memory.

Activation requires **all** of the following, recorded against exact bytes:

| Gate | Required record before product generation |
| --- | --- |
| A1 — measured readiness | Complete the open items RD-01–07 in the readiness decision. Whole Gate A and the existing 9.5 threshold remain unmet until the applicable aggregate review establishes them; component scores are not substituted. No unqualified baseline profile is labelled compatible. |
| A2 — exact contracts | Freeze the signatures, runtime-validated models, serialization/digest vectors, capability/asset manifests and resource limits required below. Review the actual contract appendix against the parent REM, including Tools selection/provenance needs. An API-name sketch or an unimplemented protocol is insufficient. |
| A3 — test exceptions | Complete and incorporate the phase's case-level migration map from the frozen inventory before its first test rewrite. Identify exact old/new nodes, oracles and exceptions; default disposition is retain. |
| A4 — maintainer approval | Record Chuck's approval of this directive's SHA256, its frozen appendices and any explicit readiness/impact amendments. A draft review or approval of the old assessment does not satisfy this gate. |
| A5 — bounded execution | Confirm board/branch, phase scope and validation environment; freeze allowed effects, private outputs and any separately authorized live window. No implicit model installation, store reset, network validation or production deployment. |

Until those gates are met, permitted work under this draft is document review
and reconciliation only. Missing readiness is not an implementation waiver.
Qwen is a separate candidate qualification: it does not become the production
default or a new requirement for existing Nomic configurations.

## 2. Build order and ownership

Implement in three bounded slices, as required by the REM. Freeze and independently
verify each slice before integrating its dependants; then review the complete
bounded aggregate. Each slice's activation record pins its exact contract/map
appendices and the source candidate it builds on. Earlier verdicts do not cover
changed bytes. This order does not defer compatibility obligations until after
acceptance.

| Slice | Owners and deliverable | Required proof before the next slice |
| --- | --- | --- |
| I1 — shared embedding and namespace contracts | Core neutral contracts; LLM capabilities/preparation/counting/result checks; Memory admission, identity-bearing vectors and versioned recovery contracts. | DI-17/18/21–24/27–29/32/33 and FC contract tests, preserving old call shapes. Fresh, matching reopen, foreign/same-dimension refusal, read-only availability and strict v1/v2 handoff. |
| I2 — narrow existing-consumer integration | Memory/Chat/Runtime/CLI and listed Tools wrappers use those contracts. Complete actual active/public/absent call-site trace and B/N/R evidence. | FC-01–14, DI-22/27–29/32–35, direct-opener/observer/background-task/multi-agent and minimal-installed-profile checks. No successful consumer replaced by blanket refusal. |
| I3 — extraction, chunking and command delivery | Tools shared converter; Memory shared plan and entry; Commands scoped file arguments; Chat `/read`/`/ingest`; existing smart_read **text** storage/cache handoffs. | DI-01–36, source and installed actual command/store tests, aggregate regressions, test-map review and substantive architecture/guide acceptance. |

The separately drafted [TOOLS-DOC directive](CD-CMD-TOOLS-DOC-001-adoption.md)
owns ReaderFactory and smart_read **document routing**. It builds on the frozen
shared API and needs its own activation, implementation and verification. Neither
unit claims the other's consumer adoption from a converter-helper test.

Core owns neutral immutable data and protocols, not policy or backend imports.
LLM owns exact model preparation, synchronous local counting, effective limits
and response validation. Memory owns namespace admission, policy/default
resolution, complete-plan validation and persistence. Tools owns conversion,
structural audit and Docling document-chunker adaptation. Commands stays standard
library only. Chat and Runtime compose capabilities and present results. New
Tools→Memory or Memory→Tools imports are prohibited; use the neutral injected
entry. Existing legacy edges remain disclosed, not broadened.

## 3. Frozen behavior to implement

### 3.1 Dependency and extraction profile

Use the measured **Docling 2.150.0 / Docling Core 2.106.0 / RapidOCR 3.10.0
ONNX Runtime CPU** profile as the qualification candidate. Certifi **2026.10.23**
passed the isolated installed check. Declare **`certifi>=2026.10.19`** in Tools'
new `document-ingestion` extra and bind exact compatible artifacts in the lock.
Default Chat requests that extra. Retain the legacy Tools `documents`,
`spreadsheets` and `all-formats` extras; they are not aliases for Docling support.
Memory requests LLM's narrow counter extra, without pulling Docling into
headless Memory/Runtime/CLI/Agent installations.

The combined test used python-dateutil **2.9.0.post0**, compatible with the current
Friday-LLM dependency constraints. Do not copy the standalone experiment's 4.0.0
constraint. Inventory and justify the actual workspace lock delta; do not reuse
a test target as a supported product installation or upgrade unrelated packages.
The shared lock's Certifi change affects all HTTPS consumers, including Finance;
preserve TLS verification and run the relevant offline dependency/import checks.

Docling is the sole document text supplier. Allow only local regular PDF, DOCX,
XLSX and PPTX with matching detected format. Preserve existing text/table reads.
No remote converter, format auto-expansion, fallback reader, placeholder or
diagnostic-as-content success. Use provisioned, hashed local assets; no first-use
download. Missing PDF/OCR assets must not unnecessarily disable asset-independent
Office pipelines or ordinary text ingestion.

Carry the measured settings into the production adapter, through public APIs:

- Export body **and furniture** where required to retain source markers.
- Preserve OCR-only isolated headings with `always_emit_headings=True`.
- Preserve unambiguous speaker notes, distinguish comments, and enforce the
  required native paragraph/table/sheet/slide order and complete admitted scope.
- Use read-only structural inspection for format, hidden units, formula cache,
  external relationships and resource limits. It supplies facts/refusals, never
  replacement document text, recalculation or repair.
- Accept only complete successful conversion and meaningful source text.
  Corrupt, encrypted, partial, empty/image-only-without-usable-OCR, unclassified
  clipping, missing assets and admission failures yield safe typed errors and
  zero embedding/storage handoff. Sideband metadata reports real units/warnings.
- Resolve RD-02 before claiming the required hidden-row/column exclusions.
  Current measured whole-workbook refusal is not falsely labelled exclusion
  support or silently made a new product compatibility exception.

The measured starting limits are 32 MiB compressed input, 50 PDF pages,
2,048 OOXML members, 128 MiB expanded OOXML, 4 MiB per XML part, 32 sheets,
20,000 worksheet row coordinates, 16,384 column coordinates, 250,000 counted
cells/merged expansion and 100 slides/5,000 counted shapes. The final contract
must state whether counters are per document or per unit exactly as implemented.
Use a 300-second conversion ceiling and measured worker resource envelope;
these test values require RD-03 qualification for production coverage/performance.
Never invent an unmeasured guarantee of OS-level isolation or immediate kill.

### 3.2 File argument and UI behavior

The new `friday_commands.file_inputs` submodule consumes the original raw tail
only after resolving a **default** file handler. Preserve custom handlers,
aliases' actual targets and the parser for all unrelated commands. Root API54
and its literal tests stay unchanged.

Implement REM C's exact quoted-path/opaque-description contract, including
repeated spaces, Unicode and no shell interpolation. Recognize exactly
`--chunking=<document|recursive|fixed>` and `--chunk-tokens=<positive integer>`
before or after the path; refuse duplicate/empty/malformed exact options before
I/O. Preserve prefix lookalikes as description and the post-path literal `--`
terminator. `/read` refuses ingestion options. Document `--lines*` refuses before
conversion; retain the legacy text/table malformed-line behavior and disclose
effective limit/truncation. Do not replace the global parser with shlex.

`SmartFileReader` delegates the four formats to the shared converter. `/read`
renders actual content and sideband metadata, without chunking/embedding solely
to display it. `/ingest` passes the successful source into the common entry once.
Remove its Chat-owned character slicing. Success requires the exact positive
stored-chunk count returned by Memory. Render effective strategy/budget and
truthful coverage/partial-failure details; do not infer success from a source
path in `/list-ingested`.

### 3.3 Shared chunking and storage

```yaml
ingestion:
  chunking:
    strategy: document
    max_tokens: 512
```

Resolve each option independently: per-ingestion override → YAML → built-in.
Both YAML keys are optional; strict invalid values refuse configuration preflight.
The budget counts the **final embedding input**, including contextual headers,
model preparation and special tokens; it is neither characters nor an exact
requested length. `smart_file.chunk_size/chunk_overlap` cease governing `/ingest`
and are not token aliases. No new overlap option.

Tools' injected Docling adapter implements document-aware chunking for converted
documents. Memory implements deterministic document-block segmentation for
supplied text/Markdown/code/JSON/YAML/CSV/TSV/web text, plus shared recursive and
fixed strategies. Preserve Unicode, source spans/order and provenance; preserve
structured table headers and sheet/slide boundaries. Plain delimited text has
no inferred header and reports absent supplied table structure. Freeze exact
overlap/context and split-or-refuse rules in A2; prototype tests alone do not
establish a production implementation. No dropped tail or second chunking pass.

The injected Memory entry owns planning, full embedding-input/vector validation
and storage. Retain source metadata, protection, quarantine/opt-in and the shared
absent-description repair. For source/derived smart_read records, preflight the
whole embedding batch before the first write. Source records equal the common
plan; summaries/synthesis remain derived **unsplit** guarded records. Preserve
truthful partial failures without adding a cross-record transaction guarantee.

Cache eligibility binds source, conversion, policy/options, prepared model/counter
identity and actual completed destination storage: normalized root, namespace
incarnation, exact collections, record IDs and provenance. Revalidate current
admission and opt-in on a hit. A model match, mtime or boolean alone cannot skip
storage into a fresh destination. Ignore old unqualified entries without purging
them. Existing Chat/Runtime do not acquire automatic smart_read storage wiring.

### 3.4 Embedding and existing-consumer compatibility

Retain embedding_pool/non-pool configuration shapes, actual service selection,
default precedence, endpoints/credentials, cache/batch/resilience behavior and
existing `embed_query`/`embed_documents` call interfaces. Optional profile fields
`max_input_tokens` and `expected_dimensions` may be supplied by exact qualified
readiness when omitted in YAML. Explicit contradictions refuse; unused unresolved
profiles do not disable a qualified service or `/read`.

Prepare query/document inputs exactly once at LLM's boundary. Count with the
matching offline synchronous tokenizer; no character estimate, remote per-count
loop or silent truncation. The smaller qualified model/loaded/batch/config limit
wins. Validate response cardinality, indices/order, finite dimensions and all
vectors before storage. Valid shuffled indices reorder exactly; duplicates,
missing/out-of-range indices or invalid components refuse. Preserve batching/
retry interfaces and include retries in any separately approved live budget.

Namespace identity includes artifact, preparation/normalization and dimensions;
service name or dimension equality does not establish the same space. Existing
unbound stores are preserved and refused. Create fresh persistent state only
under the explicitly supplied coherent vector/graph/configured-WAL policy.
Unset/default-derived first-run paths do not authorize creation. Keep the
packaged template's existing explicit `.friday/vector` literal for this draft;
document that copying it supplies origin, never permission to adopt old data.
Matching bound reopen and isolated ephemeral profiles follow FC-09/10. Runtime
root changes also affect transcript/artifact locations; do not replay old state.

Apply **all FC-01–14**, including the following narrow safeguards:

- Admission precedes resourceful rejection logging, direct Chroma/SQLite opens,
  recovery or provider readiness probes; owned sinks/tasks cannot fan out or
  write late after cancellation/close.
- Preserve MCP's exact unsplit pending snapshot, same-ID retry and transcript
  ownership. Use existing observer reasons through the actual Chat/Runtime path;
  no new telemetry schema, pending-record cleanup or automatic activation.
- Acknowledge extraction/consolidation only for stored outputs. Expose the actual
  inner task's terminal state; keep stable-ID retry and truthful partial counts.
- Maintain unscored Chat/Runtime graph recall. Guard public injected sync/async
  scorers without newly wiring them or removing their specified absent-vector
  fallback. Typed failures cannot become empty successful recall/inspection.
- Preserve public backup create/verify/restore shapes and working baselines.
  Never restore the live identity marker. Use noncolliding binding-evidence
  filenames. FU-013/014 remain separate failed/unwaived defects, not a backup
  repair project or positive complete-recovery evidence.
- Use strict Memory-v2/Chat-aggregate-v2 loaders and same-namespace restore,
  leaving Transcript-v1 and old public models strict and unchanged. Reject mixed
  nested versions. Compute the participant fingerprint only after binding and
  incarnation are available, or refresh deterministically before capture.
- Preserve multi-agent authorization visibility over the shared physical space
  and truthful partial promotion. Keep the existing 8,192-dimension ceiling.
  Do not change maintenance order, verification prompts or recovery engines.

### 3.5 Worker and admission lifecycle

Conversion/OCR/audit/repeated chunk counting run off the event loop in owned
bounded work. That worker has no model-provider or storage capability. Hold the
request's shared admission through quiescence. Cancellation invalidates storage
eligibility, discards late output and waits for owned work before releasing
admission. A timeout cannot leave an earlier success eligible. Freeze the
attempt/source/profile/plan identities and failure cases; do not copy test-only
audit hooks into product code as a claim of OS sandboxing.

## 4. Exact file boundaries

The REM's **Proposed exact implementation paths** table is incorporated in full,
at its manifest-pinned hash. The implementation allowlist is its intersection
with the slice/owner scope above, not whole-package write permission. Before
activation, its shorthand rows must be expanded into a machine-readable exact
file list in A2/A3, including selected optional/new modules and test nodes.
An unexpanded row does not authorize a newly chosen helper path.

Core/Commands/LLM/Memory/Tools/Chat/Runtime/CLI are the eight implementation owners.
Agent and the other nine indirect package rows receive only the specifically
mapped test/import dispositions. No speculative production edit to Agent,
Telemetry, Transcript, MCP, Optimization, Finance, Speech, Sandbox or Moltbook.
Runtime tool discovery is a real source-unchanged optional-import witness.

Only named package metadata, deliberate `uv.lock` delta, packaged Chat templates,
eight package READMEs, synthetic scoped fixtures, named integration/probe tests
and the architecture/guide paths below are in scope. Preserve both dirty Chat
example YAML files, `.friday-old`, `.friday`, exports, working `.venv`, existing
private evaluation targets and accepted historical evidence. No package version
bump, root executable, user-store cleanup, legacy migration/reset, new URL-ingest
route, TUI feature or complete FILE-001 extraction.

## 5. Tests, migration and evidence

The [baseline inventory](../validation/document-ingestion/product-construction/baseline-test-inventory.json.gz)
and [readable summary](../validation/document-ingestion/product-construction/baseline-test-summary.json)
freeze tracked test/fixture bytes and static base-node IDs without importing or
running them. They are an inventory, not collected parameter counts, an offline
classification, or executed coverage. The [migration seed](../validation/document-ingestion/product-construction/test-migration-seed.json)
identifies known cases; it is not an approved blanket test-body exception.

For each phase, bind exact old/new nodes, fixtures/oracles, requirement IDs,
disposition/reason, expected assertions, public call path and executed selectors.
Only case entries incorporated into the approved phase appendix are named
exceptions under the annex; retain unmapped bodies and old public signatures/
classes. Named FC nodes remain unless an approved equivalent is mapped.
Retirement needs an obsolete-requirement reason or replacement; count arithmetic
alone is insufficient. No broad skip/xfail, assertion weakening or test-only
guard bypass. New discovered cases are mapped before old coverage is removed.

| Proof group | Required concrete evidence |
| --- | --- |
| Parsing/configuration | DI-03/04/10/13/15/18/19: raw-tail quotes/description/options, independently resolved defaults, custom handlers, API54 and unchanged families. |
| Extraction/chunking | DI-01/02/05–12/14/16/25/26/30/31: genuine native/OCR documents; every required source marker/late unit/table/note; all strategies/budgets; meaningful refusal before ingestion; exact limits and coverage. |
| Embeddings/namespaces/recovery | DI-17/18/20–24/27–29/32/33 and FC-01–14: actual baseline and qualified replacement positives plus targeted refusals, exact models/roles/dimensions, public consumers and typed propagation. |
| Whole-framework integration | DI-34: complete per-call source/role/destination/open-intent/capability/B-N-R/node/installed-lane trace, including source-unchanged and active/public/absent dispositions. |
| Test migration | DI-35: independent old-to-new coverage review and executed retained/replacement obligations. |
| Documentation | DI-36: authored architecture/guides, source/schema mapping, verified examples and independent technical content review. |

Actual command acceptance must invoke the registry on genuine small PDF, scanned
PDF, DOCX, XLSX and PPTX, including a path with repeated spaces. Inspect the
disposable Chroma records: distinctive source content, exact plan/count/provenance,
no placeholder/diagnostic text, retained missing-description behavior. Query
and reopen the store in a separate process. Run zero-ingestion checks for corrupt,
empty/OCR-no-text, missing dependency/assets, known partial conversion, unsafe
Office structure, source change, limits, cancellation and model/vector refusal.
Use deterministic vectors for offline integration and real model-matched counting;
reserve actual Friday-LLM inference for a separately bounded approved window.

Run focused new contracts, then affected package regressions and named integration
nodes, then clean installed profiles/probes. Commands-only remains one distribution;
bare Tools retains text use; headless Memory/Runtime/CLI/Agent has counters without
Docling; default Chat includes the document stack. Normal and optimized installed
probes must enforce invariants with explicit checks, not removable assertions.
Check post-install Certifi version **and module/CA origin** after all installs.

All future commands use an explicitly prepared private candidate environment,
run-owned cache/basetemp/home/output paths and synthetic inputs. Examples:

```text
<candidate-python> -B -m pytest <exact-phase-selectors> -p no:cacheprovider --basetemp <run>/pytest/<unique-id>
<candidate-python> -B -m pytest packages/friday-transcript/tests -p no:cacheprovider --basetemp <run>/pytest/transcript
<candidate-python> -B -m pytest packages/friday-finance/tests/test_basics.py -p no:cacheprovider --basetemp <run>/pytest/finance-offline
<candidate-python> -B -m pytest tests/integration/test_document_ingestion.py tests/integration/test_embedding_compatibility.py -p no:cacheprovider --basetemp <run>/pytest/ingest-integration
```

These are future selector forms, not permission to execute unclassified suites.
Every module is classified offline/live before selection. Root discovery does
not cover Transcript/Finance `tests/` or root integration. Finance's
`test_integration_massive.py` remains live/excluded; no use or reproduction of its
credential and no retained offline-coverage credit. Require an offline Finance
tool-registration witness. Bind any new Optimization dependency-only witness to
an exact path; do not invent a maintained source consumer.

Use focused root-rule Ruff/format, strict typing for changed public boundaries,
package/cohort metadata, artifact/install/lock/origin checks and the approved
behavior captures with exact named oracle exceptions. Keep root Ruff debt,
root collection's test_display collision and baseline registry formatting
explicitly failed/unwaived; re-establish actual counts at the frozen candidate.
Setup/import/collection errors earn no mutant-rejection credit. Required negative
controls must reach the named call assertion with canonical before/finish/after
source and test hashes, plus an unchanged passing control.

## 6. Documentation is an implementation deliverable

Create `docs/architecture/command-execution.md` only when it can describe the
implemented candidate accurately. Distinguish Chat's maintained registry,
CLI's retained component registry/arg helper, and neutral Commands' registry;
classify CLI's placeholder main/REPL/server modules honestly. Show actual shared
owners, dependencies, request/worker/admission flow and headless reuse.

Substantively rewrite affected sections of the exact guides in the handoff,
eight package READMEs and packaged templates. Cover installation/extras/assets,
defaults/overrides, legacy character-key change, format limits, shared model
configuration, fresh-store upgrade/first-run behavior, partial/cancelled work,
troubleshooting and separate Tools adoption. Root framework users inherit the
default Chat stack; its legacy documents extra is not a Docling-support label.

Require a changed requirement → authored section → source/schema/metadata →
verified example/test matrix, exact candidate/release labels, actual content/
diagram review and source/installed example evidence. Documentation lifecycle,
links and generated tables are necessary structural checks, not acceptance of
technical content. No unrelated guide rewrite or automatic publication.

## 7. Freeze, review, stop and handoff

Each slice and the aggregate have a stable commit, exact authority/contract/map
pins, source/installed profile, commands/exits and fresh-versus-inspected evidence.
Use a fresh read-only validator under repository policy; a council is a separate
maintainer-requested workflow. Any later council uses the then-authorized roster,
honest scores and the existing minimum 9.5/no-mandatory-finding gate; no automatic
loop or provider/model substitution is inferred from this preparation.

Stop on changed/missing authority, unclassified caller, unavailable qualified
baseline, unsupported format exclusion/provenance, incompatible dependency,
scope/path expansion, guard bypass, unexpected test loss, stale evidence,
budget/service-window failure or altered protected state. Keep the successful
and failed attempts; obtain a bounded disposition rather than hiding a gap.

The final handoff includes implementation/compatibility/test-map/documentation
matrices, exact installed artifacts and profile limits, preserved-state proof,
separate INGEST/TOOLS-DOC completion status, and a disposable real `/ingest` UAT
checklist. Human acceptance, production rollout/model selection, push, PR,
merge and release remain separately authorized.
