# INGEST activation council — Opus seat, global round 5/6 (additional pass 2/3)

- Seat: opus (claude-opus-5-5, high effort), fresh read-only context.
- Candidate: `34981199842ef73891605a20f3b4275eeb37e943`, branch `feature/cmd-ingest-001`.
- Request SHA256, computed before reading: `77b3acddf8f650621bff4bd0917496a3f7cf2602eda52a7134f1fe0cbea2f96f` (match).
- **assessment_complete: true; areas_assessed: 8/8**
- **Verdict: CHANGES_REQUESTED**. There is one mandatory finding.
- **Overall design score: 9.32 / 10.** This is the weighted sum below, not rounded up, so it is below the 9.5 gate.

## Neutral corrections F1–F4

| ID | Assessment |
| --- | --- |
| F1 | **Satisfied.** `test_file_inputs.py` is classified in test-case-map `modules` (new, offline, pure). It has the I3-C3 witness `test_parse_file_input_rem_c_semantics_and_document_option_refusal`. `retained_regression_selectors` keeps `test_import_boundary.py` and the API54 node `test_memory_queries.py::test_memory_query_specs_exports_and_factory` at I3-C3 with bodies unchanged. I confirmed that the node exists at HEAD line 499. `tests_runtime/test_di.py` is classified and included in the validation-plan I3 selector, and has the I3-C4 witness `test_shutdown_drains_shared_document_worker`. I checked every I1 and I3 selector module, and each one has a module classification. |
| F2 | **Satisfied.** In shared-contracts §3, settings content/schema errors produce `readiness`, and manifest/profile hash mismatches produce `identity`. The settings hash is recorded for traceability, not attestation. In §4, runtime=None `/read` owns and drains its converter locally. The Chat lifecycle uses a single `_OwnedIngestionState` holder seeded by constructor kwargs, with accessors and no stale frozen copies. This is feasible against the actual `@dataclass(frozen=True) FrameworkAsyncClientLifecycle` at adapters.py:144, which has no fields. |
| F3 | **Satisfied.** The XLSX preflight belongs to Tools and runs as an async streaming scan in batches of at most 64 KiB or 64 records. It runs inside the request admission, cancellation and cold-deadline scope and before any converter process. DTDs are refused, there is no extraction fallback, and the heartbeat witness covers the preflight. The IPC table now includes the `planned` state. RSS sampling uses `psutil` `children(recursive=True)` with PID/create-time identity. I confirmed `psutil>=7.2.1` is already declared in Tools `dependencies`. No new path, thread engine or experiment is added. |
| F4 | **Satisfied.** approval-binding status is `proposed_extension_round5_…`. The README limits the extension to rounds 4–6 and says it changes only the cap, with scope, weights and gate unchanged and earlier stops historical. Stopping after round 6 rules out a seventh round. There is one residual wording issue, recorded as advisory V4. |

## Review A1–A8

| Area | Weight | Score | Contribution | Evidence |
| --- | ---: | ---: | ---: | --- |
| A1 Decisions/scope/honest state | 1.50 | 9.6 | 1.440 | Three decision records are applied precisely by requirement-reconciliation: the parity campaign is removed both before and after coding, whole-workbook refusal applies, and the worker is shared. Gates A1–A5 are all `complete:false` and `product_generation_allowed:false`. The model decision's earlier "no new council follows" is explicitly reconciled. Docling selection is not reopened. |
| A2 Neutral values/protocols/identity | 1.75 | 9.5 | 1.663 | The value table is exhaustive (frozen, slotted, strict, `-O`-safe), with exact protocol signatures, separate document and embedding resolvers, an IPC envelope, and strict loaders. I recomputed all five canonical vectors and the raw UTF-8 vector with stdlib `json`/`hashlib`, and all match. The plan, receipt and space digests chain correctly, and the space→plan→receipt linkage is consistent. Minor gap: advisory V2. |
| A3 Shared process/concurrency/lifecycle/headless reuse | 1.75 | 8.8 | 1.540 | The process launch, fd-1 redirect, framing, the trusted-only pickle frame, one active plus one queued request, TERM/KILL/reap, `worker_not_quiescent` and profile deadlines are all concrete. The DIContainer shutdown order is defined. The seams match the current `DIContainer.shutdown` (di.py:135), which is MCP-only today. **Mandatory M1:** the registration API cannot own an entry without a converter. |
| A4 Consumer compatibility/safeguards/stores | 1.50 | 9.2 | 1.380 | Old constructor and `from_spec` shapes are kept, with keyword-only additions. Route selection is exact, the store marker is fsync-ordered, and ephemeral tenant isolation and v1/v2 recovery dispatch are covered. The sync `read` refusal is mapped through TM-A048, and both actual callers (registry.py:678/697) are in scope. Because of M1, plain-text `/ingest` in a deployment with no document binding is either refused or left undrained. That is a compatibility regression against today's working text ingest. |
| A5 Slice/file/test assignments, acceptance, guides | 1.25 | 9.5 | 1.188 | There are 91 exact rows with per-exit purposes. The map has 49 cases, matching gate A3, and 47 named witnesses. Helper and fixture rules are opt-in, non-default selectors are explicit, Finance live tests are excluded, and the installed normal/`-O` probe is specified. Guides are authored at I3-C5 with a requirement→source→document→example map. |
| A6 Format refusal/content/chunking/errors/partial effects | 0.75 | 9.5 | 0.713 | Error codes are closed. Workbook refusal happens before conversion with an actionable message. Coverage is exact, there is no overlap or lost tail, and an over-capacity budget refuses the whole request. Partial and unconfirmed IDs are never receipted. Metadata is flat with a reserved prefix. |
| A7 Packages/dependencies/profiles/TOOLS-DOC | 0.75 | 9.3 | 0.698 | Ownership by package is clean: Tools has no LLM import, Memory has no Tools import, and Commands stays stdlib. The `tokenizers` extra is in LLM at I1, and TOOLS-DOC routing and TM-03 stay separate. Timing concern: advisory V1. |
| A8 Sequencing/intermediate compatibility/approvals/handoff | 0.75 | 9.4 | 0.705 | I1 is additive while legacy behaviour is unchanged, and I2 switches over with the unguarded branch removed. I3 runs C1→C5 with worker proof at I3-C4, after the build and not circularly. Then AG, aggregate review and UAT. The A4/A5 owners and impact revision are named, and the A-labels used for gates and review areas are kept distinct. |
| **Total** | 10.00 | | **9.325** | Reported as 9.32. |

## Mandatory finding

**M1 — An ingestion entry cannot be registered without a document converter, which contradicts the rule that non-document ingestion does not need the document binding (A3/A4).**

- **Evidence.**
  - shared-contracts §3 (around line 200) says: "Disabled Memory, plain text/JSON/table reads and **non-document ingestion do not resolve this binding**. The four document formats alone require it."
  - §4 defines the only entry registration as `bind_ingestion(self, *, entry: IngestionEntry, document_converter: DocumentConverter)`, with a non-optional converter, for both `DIContainer` and `FrameworkAsyncClientLifecycle`. It also says "a later entry must use the already bound converter".
  - The headless recipe also says to "register the pair".
  - A `DocumentConverter` can only be obtained through `create_document_converter`, which resolves the document settings, or through the Docling constructor, which needs the four bound settings.
  - TM-A049 states that the shared entry replaces Chat slicing for `/ingest`, so plain-text ingest goes through `IngestionEntry`.
- **Violated requirement.** The signatures are declared exact, so a builder has three choices:
  - resolve the document binding for text ingest, which contradicts §3 and breaks text `/ingest` in deployments without document assets;
  - leave the entry unregistered, which violates the close/drain ownership required by brief decision 5 and §4 ("close drains the entry");
  - invent an unspecified API.
- **Bounded fix** (planning documents only):
  - Make `document_converter: DocumentConverter | None = None` in both `bind_ingestion` signatures.
  - State that a binding with only an entry is valid for non-document ingestion.
  - A later `bind_document_converter` may then attach the converter.
  - A later `bind_ingestion` that supplies a converter must use the identical object, or the same pair if both are already bound.
  - Shutdown or close drains the entry, then the converter if one is present, then MCP or the clients.
  - Converted-document ingest refuses with `readiness` if no converter is bound.
  - Update the README/headless recipe wording and the slice-map purposes for di.py and adapters.py (I3-C3/C4) to match.
- **Required future acceptance:**
  - An I3-C3 witness shows plain-text Chat `/ingest` storing a common plan with the document binding absent and no settings resolution.
  - The I3-C4 `test_di.py` and Chat lifecycle witnesses cover entry-only registration, a later converter attach, rejection of a mismatched converter, and drain order with and without a converter.
  - TM-A049's fixture must not need a document binding.

## Advisories (not mandatory)

- **V1.** The Tools `pyproject.toml` and the document-stack delta in `uv.lock` are assigned only at I3-C5, but I3-C1 already exercises real Docling and RapidOCR. Today Tools declares only pypdf, python-docx and openpyxl extras. The doc should say that I3-C1–C4 run in an A5-bound interpreter whose document-stack pins come from the phase dependency manifest. Alternatively, move the extra declaration to I3-C1 so that intermediate commits declare what they lazily import.
- **V2.** The settings resolver checks asset "existence and sizes" but does not name the error code for a size mismatch. Specify `identity`, consistent with hash mismatch, or `missing_asset`.
- **V3.** Copying the 32 MiB input snapshot into `request_root` happens inside the heartbeat window. Say explicitly that it is chunked or offloaded, so it is covered like the preflight.
- **V4.** In `council/authorization.json`, `bounded_corrections` still says "No … fourth/replacement round", next to `maximum_rounds: 6`. The extension controls this, but the stale clause should be marked historical or reworded.
- **V5.** `files.py` `SUPPORTED_EXTENSIONS` currently lacks `.pptx`. TM-A048 covers PPTX, but the files.py purpose could name the added extension.

## Boundaries, evidence and limits

- **Entry and exit checks.** Both were run with `GIT_OPTIONAL_LOCKS=0` and bytecode off, taking the logical index (SHA256 of `git ls-files --stage -z`) before status. Both times:
  - index `f3deff5e…cd849`
  - HEAD `34981199…`
  - branch `feature/cmd-ingest-001`
  - status with the 2 modified example YAMLs plus `?? .friday-old/`
  - empty staging
  - All 16 required pins, all 10 optional pins, the controller-checks pin, and the 8 preserved metadata records (mode, size, mtime, ctime, birthtime, plus SHA256 where declared) matched.
- **Read in full:** the request and current-controls (hash verified), extension-authorization, authorization, review-instructions, correction-requirements, README, shared-contracts, requirement-reconciliation, readiness-disposition, validation-plan, approval-binding and the three decision records.
- **Read as focused views:** all 91 slice-file-map rows (paths, exits, and full purposes for key rows) and the test-case-map modules, selectors, helpers, witnesses, 49 mapped-case identities and TM-A048/A049 in full. For the digest vectors I recomputed all of them.
- **Targeted source reads at HEAD, via `git show`/`git grep` only:**
  - Tools pyproject dependencies and extras
  - Chat `adapters.py` lifecycle class
  - Runtime `di.py` container and shutdown
  - Chat `commands/files.py` reader and `parse_line_limit`
  - `SmartFileReader` callers in registry.py
  - existence of the API54 test node
- **Not executed or not read:** no product imports, tests, builds, installs, network, model, provider or store calls. I did not read Finance `test_integration_massive.py`, user YAML, `.friday*`, `exports` or `.venv`, the optional parent references, `state.json`, or prior/peer reports and memory.
- **No writes, delegates or repairs.** Nothing was written to the checkout or input directories. The only writes were to this seat's private scratch directory outside both.
- **Limits.** This is a design review only, with no product conformance claims. The verdict grants no construction, effects, acceptance, push or delivery authority. This seat stops here.
