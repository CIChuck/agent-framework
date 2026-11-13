# INGEST activation — readiness dispositions and remaining evidence

**Current maintainer adjustment — 2026-11-13:** [The separate model identity/
tokenizer-parity pre-coding qualification is removed](model-qualification-decision.md).
Earlier RD-01/RD-05 prerequisite descriptions below are retained as superseded
background for that item only. Runtime guards and ordinary implementation
compatibility tests remain; no later parity campaign is substituted. Office
coverage and worker/resource decisions remain open.

Version 0.1, 2026-11-13. This is an evidence disposition for the existing
[RD-01–07 requirements](../readiness-decision.md), not a new Docling evaluation.
No live request, import, install, conversion, model switch or store operation is
performed by this preparation. The [focused directive verdict](../focused-council/round2/results/report.md)
remains valid for its unchanged reviewed document, not for product conformance.

## Decisions the implementation appendix now makes

- Shared immutable values/protocols, exact field rules, full-batch validation,
  identity encoding and versioned recovery surfaces are specified in
  [A2](shared-contracts.md), with deterministic [hash vectors](digest-vectors.json).
- Source/metadata/document paths have exact slice/owner/purpose/exit assignments
  in [the file map](slice-file-map.json); new helpers cannot appear implicitly.
  Registry/files/runtime/adapters supply read ownership and existing shutdown
  hooks; app.py remains a source-unchanged real application witness.
- The proposed document session uses one spawned process, retaining one converted
  vendor document through planning. A pure injected local-counter factory avoids
  a Tools→LLM dependency. Read-only conversion needs no factory. This implementation
  choice still requires resource/spawn/timeout qualification in RD-03; it is not
  advertised as an already measured product feature.
- Existing synchronous text/table reads remain; synchronous document reads refuse
  and direct callers to the async API. The default async command uses that API.
- Text chunk coverage has no content overlap; contextual headings/table headers
  may repeat explicitly. An indivisible unit that cannot fit is refused without
  provider/storage effects. All resolved budgets, including default 512, refuse
  rather than clamp when too large. Memory never splits accepted chunks again.
- LLM owns capability/counter schemas and provisioned-root resolution. Tokenizers
  0.23.3 is the measured proposed local JSON-tokenizer backend; no weight/tokenizer
  download, global cache or production model change is requested. Hosted counter
  support remains unqualified rather than invented.
- Legacy public signatures/v1 models remain. Same-dimension changed preparation
  is still a new embedding space. Full v2 binding covers nested vector artifacts,
  while existing Transcript-v1/journal and Chat path fingerprint stay unchanged.

These proposed decisions implement existing delegated A2 duties. They require
exact approval; they do not supply absent empirical evidence or amend the REM.

## Evidence reuse and the remaining Q gate

| ID | Reused evidence / prepared artifact | Current disposition | Exact evidence or decision still required |
| --- | --- | --- | --- |
| RD-01 | Approved compatibility annex inventories B01–08/FC01–14; earlier Nomic source-to-store evidence; exact slice/test assignments. | **Open: actual identities and B/N qualification.** | Actual baseline and N-DIM/N-SPACE/N-CAP identities, immutable serving evidence, real counter assets and old-convention baseline positives in disposable stores. Check B02 hosted immutable identity first. No test double or model-name echo qualifies it. |
| RD-02 | Completed configured four-format/OCR behavior and genuine Office fixtures; sole-Docling-text and non-text audit contract retained. | **Open: narrow Office coverage mapping.** | Prove hidden sheet/row/column/slide exclusion, notes-versus-comments and formula-cache mapping to the selected output through public APIs. Current hidden-row/column whole-workbook refusal is not exclusion support. If not feasible, present a precise narrower REM/impact amendment for approval; no silent change. |
| RD-03 | Existing document/input ceilings and measured bounded conversion results; proposed process/session and cancellation design. | **Open: product envelope and worker feasibility.** | Qualify the proposed worker, full representative boundaries, cold/warm resource limits, spawn/IPC/local-counter operation, cancellation, 300-second deadline and two-second terminate grace. The old corpus's native validity does not establish these results. No claim of OS sandboxing/immediate native kill. |
| RD-04 | A2 signatures/fields, plan/receipt/namespace identities, strict v2 versions and five canonical design vectors; exact path map. | **Prepared design, not approved/runtime-qualified.** | Review and freeze this appendix; bind actual qualified asset/capability records and finalize measured RD-02/03-specific profile values. Exact product invariants are validated after generation, at the assigned exits. |
| RD-05 | Friday-LLM/Nomic/Chroma E2E: 768 dimensions, observed context 2048, real persisted/reopened chunks. Model ID and old evidence remain exact. | **Open: immutable serving identity and boundary parity.** | The recorded server usage=0 cannot prove token parity. Bind served artifact/counter/preparation, effective per-input/batch limits and positive/overflow boundary evidence for B and every N scenario. No use of the consumed old request ledger for new calls. |
| RD-06 | Existing compatible private stack: Docling 2.150.0/Core 2.106.0/RapidOCR 3.10.0, Certifi 2026.10.23, dateutil 2.9.0.post0; proposed narrow counter and dependency split. | **Partly evidenced; exact proposed graph/profile binding open.** | Bind the reusable measured artifacts and complete intended dependency/profile/asset/license graph, including hosted counter if retained. Retain Certifi>=2026.10.19 after all installs, shared TLS verification and no unrelated upgrades. Actual new product extras/lock/clean candidate installs belong to I1/I3/AG, not pre-creation proof. |
| RD-07 | Unchanged frozen inventory, explicit case exceptions/new witnesses, offline/live exclusions, guide/source duties and closed focused directive council. | **Preparation drafted; readiness approval open.** | Complete any additional phase-specific exceptions/helper classifications before their edits/execution, finalize qualification and impact materiality, then obtain the separately required whole-readiness review. The successful focused council is not this different gate. |

The last Nomic endpoint state is historical test evidence. This document does not
assert that production is still stopped, the server is reserved/restarted or a
particular artifact is loaded now. Qwen remains illustrative. There is no new
service window, model selection or installation authority.

## Proposed numeric interpretation to bind with RD-03

Use the directive's values; qualify this exact interpretation before activation:
32 MiB compressed input per file; 50 PDF pages per file; 2,048 OOXML members and
128 MiB expanded bytes per file; 4 MiB per XML member; 32 sheets per workbook;
row coordinate <=20,000 and column coordinate <=16,384 per sheet; 250,000 actual
cell/merged-expansion units per workbook; 100 slides and 5,000 shapes per deck.
Count all inventory units before visibility filtering. Scope warnings retain
original unit identities. Neither ZIP bombs nor hidden units bypass admission.
The 300-second conversion deadline discards output and drains/reaps the owned
process as A2 specifies; measured memory/startup/IPC ceilings remain an explicit
RD-03 evidence field, not an invented value.

## What can proceed now

Finish/review the planning artifacts and reuse already preserved results.
No new model/provider call, install or personal-store inspection is implied.
Once concrete Q gaps have a disposition, update the same canonical package-impact
assessment, retain approved v0.6 in Git and bind the new hash to maintainer
satisfaction. Its revision must make the no-Memory /read lifecycle, injected
planner direction, worker/asset choices and their actual per-package consequences
plain. Do not claim this preparation already qualifies every deployment.

The first independent readiness checkpoint is B02's immutable hosted identity,
followed by the actual B/N identity/counter binding. If the supported provider
cannot supply it, the maintainer must choose a specific contract/compatibility
amendment or retain the gate. A local model is not silently substituted. The
remaining format/worker questions are narrow integration qualification, not a
repeat evaluation of whether Docling is generally suitable.
