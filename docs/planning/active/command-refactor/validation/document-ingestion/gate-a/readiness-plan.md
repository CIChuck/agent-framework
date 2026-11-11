# INGEST-001 — Gate-A dependency and capability readiness plan

Version: **0.1 — prepared for maintainer review**, 2026-11-11.
Execution status: **NOT ACTIVATED**. Public metadata/source research has been
performed; dependency resolution, artifact installation, model transfer,
conversion, inference and store operations have not.

## Approval and purpose

Chuck approved the exact [Package Impact Assessment v0.6](../../../package-impact-assessment.md),
SHA256 `f570318f704fe3c5ba29b62860148b45eb31d15243fcf0eb6acd76bc9d218176`.
[The approval record](../../../approval/ingest-package-impact.md) binds the reviewed
`ae813002` bytes presented at `fd33d5f5`. It authorizes preparing this plan;
construction remains separately gated. The assessment, amended
[REM](../../../remediation/REM-CMD-INGEST-001-pdf-docx.md), normative
[compatibility annex](../../../embedding-compatibility-contract.md) and reviewed
[test](../../../test-migration-plan.md)/[architecture](../../../command-architecture-update-plan.md)/
[guide](../../../guide-update-handoff.md) plans retain their reviewed bytes.

Gate A answers whether the selected dependencies, real formats, local assets and
embedding capabilities can satisfy the existing contract on the target profile.
It supplies measured inputs for the exact construction directive; it does not
implement shared handlers, claim installed `/ingest` correctness or redesign the
framework. INGEST and the separately directed TOOLS-DOC adoption stay distinct.

The machine-readable [effects envelope](effects-envelope.json) binds proposed
paths, budgets, hosts, stages and activation prerequisites. [Source observations](source-observations.json)
contain exact candidate wheel URLs/digests and commit-bound asset URLs. They are
metadata observations, not downloaded-artifact or compatibility evidence.
[The consumer matrix](consumer-readiness-matrix.md) binds the final inventory work.

## Selected candidates to investigate

| Candidate | Qualification choice and consequence |
| --- | --- |
| `docling[rapidocr]==2.150.0` | Investigate this exact release, commit `6852c27fb87dafaaa1a564545a8ce78d4565b186`. Its metadata requests matching `docling-slim[standard]`; standard includes Office backends and `docling-core[chunking]`. The `rapidocr` extra supplies the ONNX dependency path. This selects a distribution graph, not additional accepted file formats. |
| `rapidocr==3.10.0` | One CPU OCR engine, ONNX Runtime backend, English fixture scope. No EasyOCR, Tesseract executable, native-mac OCR or automatic engine fallback. Explicit custom detection/recognition/classifier assets and recognition keys must qualify together before use. |
| `certifi==2026.10.23` | Exact qualification candidate, above the settled `>=2026.10.19` floor. The future Tools extra declares the floor; the resolved lock/manifest and target interpreter bind the exact version. No unlocked post-install upgrade substitutes for this. |
| Local counting | Investigate existing lock versions `tokenizers==0.22.1` and `tiktoken==0.12.0` as starting counter candidates. Neither is qualified merely by being locked. Select the smallest exact extra that proves model-bound synchronous counting; record any required delta. No Docling dependency in the headless counter profile. |

These facts come from official release metadata, not an installation. Exact
transitive versions and compatible macOS wheels remain A0 outputs. Keep existing
Tools `documents`/`spreadsheets` extras intact. A smaller `docling-slim` profile is
an unselected alternative: if the chosen graph exceeds limits, report a proposed
impact change rather than silently substitute it. Audio/VLM/remote-serving
extras, additional format admission and remote conversion are excluded.

Current metadata shows the target is **Darwin arm64 / CPython 3.13.10**. Record
actual macOS version, CPU/RAM, interpreter/tool paths and hashes at activation;
no other platform is qualified by inference. An unsupported native wheel is a
stop, not permission to build arbitrary third-party source or change Python.

## Private layout and effects boundaries

At activation, create one new absent directory:
`/private/tmp/friday-ingest-gate-a-001/<activation-id>/`. Resolve its real path,
record ownership, and refuse an existing/nonempty or aliased destination. The
root contains `source-export/`, `target/`, `wheelhouse/`, `cache/`, `fixtures/`
and `reports/`. Nothing is written to the working checkout or `.venv`.

All UV/XDG/Hugging Face/Transformers/Torch/temp caches point into this root.
Do not repurpose HOME or rely on a global cache. Publish verified assets under
`target/share/friday/ingestion-assets/<manifest-sha256>/`, then make them read-only.
The manifest records normalized paths, revisions, licenses and per-file SHA256.
Reject path escapes, symlinks, duplicate members and missing/different bytes.

Only synthetic documents/text and explicitly bound local model evidence are
inputs. Preserve dirty YAMLs, `.friday-old`, exports, user documents/stores and
accepted historical bundles. No persistent Memory namespace, backup/restore,
maintenance run, provider Finance test, model swap/load/unload or credential use
is authorized by this plan. A3 remains locked until its operator facts are bound.

### Proposed hard budgets

| Resource | Limit / stop condition |
| --- | --- |
| Metadata | 64 MiB, 500 requests, 15 minutes; public allowlisted hosts only. |
| Package payload / asset payload | 4 GiB / 1 GiB downloaded, counted across retries. No unbounded snapshot download. |
| Private retained disk | 16 GiB total; require at least 20 GiB free before starting. |
| Conversion process tree | 8 GiB peak RSS, one conversion, four CPU threads. No GPU profile is qualified. |
| Time | Two hours overall; 20 minutes installation; 300 seconds single conversion, 180 seconds warm conversion, 30 seconds cleanup/quiescence grace. |
| Synthetic document admission | 32 MiB compressed; 128 MiB expanded; 2048 archive members; 50 PDF pages; 32 sheets; 20,000 rows/sheet; 250,000 total cells; 100 slides; 5,000 total shapes. |
| Optional local embedding stage | At most 64 requests, 256 vectors, 131,072 aggregate input tokens; synthetic inputs only. |

These are proposed qualification/workload ceilings, not measured performance or
final product limits. Record cold/warm timing, peak memory, installed/download
sizes and actual units. Enforce limits outside the converter as well as through
its API; stop before overruns, never silently raise a budget. Terminating a private
qualification child after a hard limit is not proof of production thread
cancellation: the final directive still needs its own admission/quiescence tests.

## Stage promotion and artifact manifests

Plan approval must name the activated stages, exact run root, budgets and manifest
reviewer. A bounded activation may cover conditional stages; each transition still
requires a recorded, complete manifest before its effects. The **Codex controller**
reviews ordinary data-only manifests against the approved envelope. Unlisted
hosts, unknown licenses, source builds, custom model code, material package changes
or unresolved model facts stop for Chuck; they are not delegated approvals.
No council is launched automatically. The prior package-impact council loop ended.

### A0 — metadata resolution and final-directive inventory

1. Freeze a clean export of the current source and approved document pins.
   Rehearse only proposed package metadata in the private export: Tools' new
   extra, default Chat's extra request and the narrow LLM counter extra. Record
   exact before/after metadata and proposed lock diff; production source is unchanged.
2. Resolve against current Chat/Core/Memory/LLM constraints for the target, with
   no ambient extras or project-environment sync. Use binary-only third-party
   requirements, no executable installers/source builds/custom model code.
   Metadata may come only from the envelope's exact public hosts. If the resolver
   needs a wheel archive to obtain missing metadata, stop before that payload;
   first record the exact URL/hash/size and an explicit archive-inspection allowance.
3. Emit every exact package/version/platform/file/URL/hash/size/license and reason
   for change. Separate required new dependencies, existing upgrades, removals
   and unrelated churn. An unexplained unrelated upgrade stops the profile.
4. Read source/test metadata for the entire consumer matrix and B01–B08/FC-01–14.
   Freeze each active, public-unwired and absent route, open intent/raw path origin,
   vector role, storage/cache semantics and proposed test/oracle mapping. An
   absent route earns no integration credit. This is not a new implementation route.

A0 does not pass because a resolver exits zero. The manifest must be complete,
within budgets, source-linked and reviewed. Exact transitive wheel URLs are
unavailable before resolution; therefore A1 cannot activate from seed URLs alone.

### A1 — pinned wheels and isolated installation

Only after A0 manifest promotion, transfer exact approved wheels from
`files.pythonhosted.org`, verify bytes before use and retain the wheelhouse.
Third-party sdists/builds are excluded. Workspace wheel builds may use only the
exact private source export and separately pinned existing build tools; no source
edits or build-time network access. Inventory any build-tool requirement too.

Install separate disposable profiles for default Chat plus the document stack,
Tools-only text, neutral Commands, headless Memory/Runtime/CLI/Agent and direct
LLM-counter use. Requested extras may exist only in the private metadata rehearsal;
report them as proposed, not shipped. Compare package maps with the actual baseline.
The changed default Chat closure is deliberate; the old 138-distribution map is
not its new oracle. Commands must remain a one-distribution neutral closure.

Run target-interpreter dependency checks and module/distribution origins. Verify
Certifi only **after all installation steps**, using parsed versions, target
metadata and `certifi.where()` within the prefix. Repeat normal and `-O` modes.
The below-floor negative control uses a private verifier/report substitution;
never downgrade the working environment. Rejection must be an explicit validation
failure, not an import/setup failure. The shared lock's CA-bundle change affects
Finance/provider SDKs, LLM and MCP HTTPS clients too; no live API call is needed
to inspect their dependency/import/TLS-context construction.

### A2 — assets, genuine formats and offline local chunking

The asset candidates select Heron layout, TableFormer accurate (the selected
release references the v2.3.0 table model lineage), a bounded English RapidOCR
custom-model set, and Nomic tokenizer data. All URLs in source-observations are
commit-bound; only selected files may transfer. Model repository default-branch
names are not activation pins. Prefer safetensors/ONNX/data formats; no executable
model Python or remote-code trust flag is enabled.

The OCR candidate uses publicly listed English PP-OCRv3 detection/recognition
and a classification model. **It is not qualified yet.** After inspecting the
pinned Docling/RapidOCR routes, prove exact custom-path/architecture compatibility
and recognition-key provenance. A dictionary may come only from the verified model
metadata or an explicitly inventoried licensed sidecar; never the engine's guessed
language default. If this cannot be proved, stop before OCR use and return a revised
candidate manifest. Do not fall back to another host, ModelScope, engine or model.
The earlier RapidAI HF metadata request returned 401; no authentication was attempted.

For large LFS files, verify the upstream SHA256 from metadata and transferred
bytes. For regular repository data files, bind the commit/git-blob identity,
verify it on transfer and record observed SHA256 before publication. Freeze exact
per-file license obligations before transfer/use; repository tags alone are not
an unresolved multi-license decision. Extra redirect hosts stop the transfer.

Use explicit local paths and a CPU pipeline with remote services/plugins/enrichment
disabled. Conversion runs with offline settings and a network-deny guard; prove
a deliberate network attempt is refused. Record the guard's containment limits—
Python audit containment is not an OS sandbox. No asset auto-fetch or global-cache
fallback is accepted. Test missing/hash-tampered/readonly assets, plus Office
conversion without PDF assets where its pipeline does not require them.

Prepare at least 30 genuine synthetic documents: six PDF, six DOCX, ten XLSX,
eight PPTX, plus shared malformed/limit controls. Bind fixture hashes and distinctive
source text. Exercise:

- PDF real page counts, native reading order/tables, English scanned text, blank
  image-only content, encryption, corruption and known partial conversion.
- DOCX interleaved paragraphs/tables/headings; characterize omitted headers,
  footers/comments/textboxes rather than claim exhaustive extraction.
- XLSX workbook order, hidden sheets/rows/columns, merged cells, Unicode, zero,
  booleans/dates/leading-zero text, and valid/missing/error formula caches. The
  structural audit supplies facts/refusals only; Docling alone supplies text.
- PPTX slide order/indices, hidden units, native text/tables, separately labelled
  notes and excluded comments/media/layout content. No rendering or linked fetch.
- Renamed binary/ZIP, format mismatch, empty meaningful content, clipping,
  unclassified warnings and all resource limits. Capture diagnostics separately.

Acceptance is the REM B contract, including fail-closed gaps. A Markdown string
alone is not evidence of content, ordering, coverage or formulas/notes correctness.
If the pinned release cannot meet a rule, record the conflict and stop; do not
quietly narrow the contract or add a second text extractor.

Freeze the real conversion/status/serialization/provenance API and warning map.
For document/recursive/fixed, use one local synchronous counter and final prepared
embedding input, including contextual headings, model prefixes and special tokens.
Test 512 default and overrides at exact boundaries; never rely on Docling's default
MiniLM tokenizer, a network counter per split, character estimates or truncation.
No implemented Memory handler is claimed: these are upstream/scratch feasibility
probes, followed later by source/installed command-to-store construction tests.
Converter-only A2 checks can precede A3. Final model-bound chunk acceptance stays
pending until A3 qualifies the counter; preliminary counts cannot qualify it.
Cover supplied plain text, Markdown, code/JSON, CSV/TSV and web/tool payloads too,
using the planned non-Docling segmentation boundary. This does not add a URL route
or rechunk unsplit structured/conversation/maintenance records.

### A3 — exact embedding capabilities, separately bound

The packaged pool points memory/maintenance at `nomic_embedding_local`, but its
revision is a placeholder. This is a baseline configuration shape, **not** proof
of the user's selected service or served weights. The existing Nomic tokenizer
repository snapshot is merely a candidate; it must match the actual deployment.
Read no dirty YAML, global model cache or personal model file by inference.

Before any inference, activation must bind: dedicated local endpoint and service
selection; served artifact/revision and digest; tokenizer data/digest; supported
capacity and returned dimensions; query/document/special-token preparation;
normalization; and an explicit synthetic-call allowance. The plan currently leaves
those operator facts unbound, so A3 is blocked. No model load/unload, existing-store
access or background maintenance is permitted. Qwen 4B remains illustrative.

Qualify omitted-new-field baseline fixtures B01–B08, preserving actual pool/default/
non-pool/resilience/batch/cache selection. Check query/document roles, local/server
count parity, effective input limits, batch index/input ordering, finite/complete
vectors and exact dimensions. Counter parity may use an explicitly bound server
facility as a cross-check; it never replaces offline counting for chunking.
Report an unattested hosted alias such as legacy text-embedding-3-small as a
compatibility gap until immutable provider identity/counting is established;
do not silently replace or disable a selected baseline service to call it compatible.

No replacement model is selected by this approval. Real N qualification requires
an explicitly selected independent deployment/artifact, different dimensions and
same-dimension foreign identity cases, smaller capacity without Memory writes. Later consumer proofs use a fresh disposable
layout. Synthetic vectors may test the probe protocol but cannot qualify real
model behavior. Full baseline/replacement consumer round trips and stored-state
admission remain construction obligations after the interfaces exist. Gate A is
not globally complete while a required selected baseline or replacement is unqualified.

### A4 — report and construction-directive handoff

Emit a reproducible readiness report/manifest: exact inputs, package/assets/license
and lock diffs, platform/tool versions, API/coverage findings, timing/memory/storage,
normal/optimized origin checks, model readiness records, refusal controls and
source-linked consumer/test/oracle trace. Distinguish observed upstream capability,
synthetic protocol checks and future product behavior. Unsupported coverage or
baseline qualification is a stop requiring explicit disposition, not a pass.

The final directive must bind the approved impact appendix (version/commit/hash),
exact source and test paths, case-level migration exceptions, default/offline/live
selectors, at least one offline Finance import/tool-registration witness, canonical
architecture and substantive guide rewrites, and source/installed review gates.
Assess proposed guide 16/17 cross-references before adding their exact paths;
no current scope addition is implied. Preserve all known failed baseline debt.
If readiness materially changes package impact, return the new version to Chuck.
Unchanged approved bytes do not need another identical approval request.

Return measured results for review under separately authorized validation. Neither
plan approval nor a successful package install approves product construction,
TOOLS-DOC adoption, provider/store effects, acceptance, push or publication.

## Activation checklist and present stop point

This plan is ready for Chuck's document review, **not executed qualification**.
Activation records its exact version/hash, permitted stages, fresh run root,
manifest reviewer and limits. A0 must precede any artifact-stage promotion;
A1/A2 require exact promoted artifact/license manifests. A3 additionally needs
operator deployment facts and an explicit call allowance. Unknown facts stop only
the dependent stage; they do not become invented defaults or an overall pass.

No council, package installation, source/test/guide implementation or model call
has been started. The completed package-impact council supplied planning readiness,
not evidence for the unexecuted stages above.

## Primary research sources

- [Exact Docling release](https://pypi.org/project/docling/2.150.0/) and
  [matching modular distribution](https://pypi.org/project/docling-slim/2.150.0/).
- [RapidOCR 3.10.0](https://pypi.org/project/rapidocr/3.10.0/) and
  [Certifi 2026.10.23](https://pypi.org/project/certifi/2026.10.23/).
- [Pinned OCR adapter](https://github.com/docling-project/docling/blob/v2.150.0/docling/models/stages/ocr/rapid_ocr_model.py),
  [tokenizer-aware chunking](https://docling-project.github.io/docling/_generated/examples/hybrid_chunking/)
  and [explicit offline artifacts](https://docling-project.github.io/docling/usage/advanced_options/).
- [Nomic model-owner card](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5).

Public metadata/source reading produced the observations JSON. No search-result
summary, current upstream default or model card is substituted for pinned-target
execution. Exact source URLs/metadata digests and asset revisions are recorded.
