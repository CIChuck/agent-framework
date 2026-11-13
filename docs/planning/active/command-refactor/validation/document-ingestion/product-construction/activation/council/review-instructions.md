# Proposed council instructions — INGEST construction activation package

**Draft for Chuck's review. No reviewer has been launched.**
Date: 2026-11-13. The controller waits for Chuck's direction before dispatch.
The following is the common brief proposed for all three fresh independent seats.
Before dispatch, the controller fills the frozen candidate SHA, target/input
hashes and lightweight entry/exit identity record; those are identity fields,
not changes to the review scope below.

## Council and stopping rule

- GPT-6.1 Sol, GPT-6 Astra and Claude Opus 5.5, each at high reasoning effort.
- At most **three full council rounds**, counting the initial review as round 1.
- Between rounds the controller may make bounded planning-document corrections
  directly addressing findings, then freeze a new candidate and use fresh seats.
- Stop early if every seat completes the assessment, returns VERIFIED with zero
  mandatory findings and scores **at least 9.5/10 overall**. No averaging across
  seats or rounding up. Otherwise stop after round 3 and await Chuck's feedback.
- No fourth round, replacement seat, expanded work unit, code generation or live
  effects follow automatically. Reviewers never remediate or delegate.

## Exact review assignment

Review **INGEST — proposed construction activation package**, rooted at
`docs/planning/active/command-refactor/validation/document-ingestion/product-construction/activation/README.md`.
Assess whether its linked contracts and implementation/test assignments provide
a coherent, comprehensive, buildable basis for bounded construction approval.
This is a document/design review, not product-code conformance or an assertion
that every future activation/acceptance gate has already run.

Read the overview, shared-contracts.md, readiness-disposition.md,
validation-plan.md, approval-binding.json and the three current decision records:
model-qualification-decision.md, office-visibility-decision.md and
shared-worker-decision.md. Inspect slice-file-map.json, test-case-map.json and
digest-vectors.json for their actual contract/mapping meaning. Use focused JSON
views where repeated generated rows add no new meaning. Do not rebuild the old
AST inventory, rehash every historical artifact or substitute count arithmetic
for coverage assessment.

Use referenced directive/REM/compatibility/impact requirements only as needed to
resolve a concrete question. Current explicit maintainer decisions below override
their superseded clauses. Source reads are permitted to check actual interfaces,
composition/shutdown seams or test assumptions; no exhaustive source audit is
assigned. Prior council reports, scores, private transcripts and memory are not
review inputs. Provenance labels in permitted current documents are context,
not inherited correctness evidence or automatic grounds to stop.

## Decisions to preserve

1. **Docling is the established selected converter.** Completed format/OCR and
   source-to-store evaluations are inputs. Do not reopen vendor selection or
   require another general Docling evaluation.
2. **The separate pre-coding model identity/tokenizer-parity qualification is
   removed.** Do not reintroduce that campaign under a different gate or move a
   new mandatory parity campaign after coding. Runtime input-limit/vector/store
   safeguards and ordinary positive compatibility/implementation tests remain.
3. **Reject affected XLSX workbooks clearly.** Hidden rows/columns in an included
   worksheet cause whole-workbook refusal before conversion/embedding/storage,
   with an actionable explanation. Do not require hidden-row/column filtering.
   Existing hidden-sheet exclusion and other format behavior remain.
4. **Use a shared worker process.** Tools owns conversion/worker lifecycle;
   Memory owns ingestion policy/orchestration; Core owns neutral progress/results/
   lifecycle protocols; LLM brokers embeddings outside the conversion worker.
   Chat, CLI/Runtime and a future TUI consume the same headless capabilities.
   No Chat-owned ingestion engine, frontend import in shared code, new CLI
   executable or TUI implementation is authorized.
5. **Preserve bounded execution and truthful outcomes.** Concurrency/resource
   limits, cancellation/timeout/drain and no late output/storage require meaningful
   implementation acceptance. Check that their timing is feasible and noncircular;
   do not require completed product worker code before authorizing its creation.
   Any proposed additional pre-coding experiment must identify a specific
   unresolved risk and why established evidence or normal implementation tests
   cannot address it; do not invent a general readiness project.

## Eight assessment areas

| ID | Assess | Overall weight |
| --- | --- | ---: |
| A1 | Current maintainer decisions, scope, honest readiness/approval state and removal of stale or contradictory prerequisites. | 1.50 |
| A2 | Exact neutral values/protocols, validation, data flow, injected dependencies and source/plan/vector/receipt identity. | 1.75 |
| A3 | Shared process ownership, bounded concurrency, progress/cancel/timeout/shutdown, and headless CLI/TUI reuse. | 1.75 |
| A4 | Existing consumer compatibility, configuration/call shapes, model/store safeguards, fresh-store and strict recovery boundaries. | 1.50 |
| A5 | Exact slice/file/test/helper assignments, traceable valid coverage, meaningful public/installed acceptance and authored architecture/guides. | 1.25 |
| A6 | Format refusal/content/provenance, chunk policy/capacity, errors, partial effects, cache/destination binding and no false success. | 0.75 |
| A7 | Package/dependency/asset responsibilities, optional/default/headless profiles and separate TOOLS-DOC boundary. | 0.75 |
| A8 | Buildable I1/I2/I3 sequencing, intermediate compatibility, concrete approvals/effects and final review/UAT handoff. | 0.75 |

Identify material omissions, contradictions, unsafe assumptions or unclear owners
that would misdirect a builder. Future code/tests and final exact approval are
legitimate staged work; absence alone is not a document defect. A gate must
still state an actionable decision/artifact, owner and feasible timing. Flag
known contradictions instead of hiding them in a future appendix.

## Review boundaries and preservation

Use a fresh read-only context and a new physical external scratch directory.
Verify the frozen request/target and required input identities. At entry/exit
use GIT_OPTIONAL_LOCKS=0 and bytecode off; obtain logical index before status,
then compare HEAD/branch/status/staging and declared preserved metadata.
The controller performs structural/preservation/admin checks once per round;
reviewers focus on the substantive assessment and do not rerun that checklist.

No product imports, tests, builds, installs, network/model/provider/store calls,
source edits, user-state reads, dependency/provenance audit or old harness replay.
Do not open, parse or execute Finance's test_integration_massive.py or inspect
credentials, dirty YAML, .friday* contents, exports or .venv. Only declared
metadata/hash checks of preserved entries are allowed. Never write the checkout,
supplied evidence or another reviewer's scratch. No nested agents or repairs.

## Required report

Complete **all eight areas** before assigning an overall design score. Return:

- assessment_complete=true/false and areas_assessed out of 8;
- VERIFIED, CHANGES_REQUESTED or BLOCKED;
- an A1–A8 table with concise evidence and weighted score contributions;
- mandatory findings with exact section/evidence, violated requirement, bounded
  fix and required future acceptance; keep optional advisories separate;
- one honest **overall score out of 10**, no inflation, averaging or rounding up;
- source/input checks, actual limits and what was inspected versus executed;
- a durable report path and SHA256.

If genuinely unable to complete, report the exact reason and overall=null;
unread work is not a low design-quality score. Recover ordinary output
truncation with bounded reads. Roughly 1,000–2,000 words normally suffice.
No separate numerical coverage grade is requested: the eight-area completion
record makes the assessment scope explicit. A high score never waives a
mandatory finding. A document verdict grants no construction, effects, human
acceptance, push or delivery authority. Stop after this single seat.
