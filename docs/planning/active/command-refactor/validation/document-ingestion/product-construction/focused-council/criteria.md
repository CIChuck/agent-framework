# Focused INGEST directive council

Review **CD-CMD-INGEST-001 — shared document ingestion implementation** as a
proposed construction directive. Judge whether it comprehensively tells a builder
what to change, who owns it, how integration remains compatible, how failures are
handled, and how completion will be demonstrated. This is not a repeat Docling
qualification, a product-code conformance verdict or a whole-framework audit.

## Required assessment

| ID | Focus | Weight in overall score |
| --- | --- | ---: |
| F1 | Complete extraction→planning→embedding→storage flow; neutral typed contracts; shared ownership and headless reuse; caller/consumer boundaries. | 2.0 |
| F2 | Actual default file-command integration, quoted paths/options/descriptions, retained handlers and format/line semantics; real source handoff. | 1.0 |
| F3 | All-source document/512 defaults and overrides; strategy ownership; model configuration, prepared-input limits, query/document roles and no second chunking. | 1.5 |
| F4 | Existing embedding consumers, store/model identity and upgrade policy; source/derived records, profiles, recovery and explicit supported/unchanged/absent route dispositions. | 2.0 |
| F5 | Truthful errors/partial effects; cancellation/admission/worker quiescence; source/provenance/cache/destination binding and no false success. | 1.0 |
| F6 | Complete per-package/dependency/configuration/install responsibilities and separate INGEST versus TOOLS-DOC adoption boundary. | 0.75 |
| F7 | Meaningful integration/regression/installed acceptance tests, traceable affected-test migration and substantive architecture/guide updates; proof matches requirements. | 1.0 |
| F8 | Feasible I1/I2/I3 sequencing, bounded intermediate compatibility, exact future appendices, activation/stop criteria and final aggregate/UAT handoff. | 0.75 |

For each area identify omissions, contradictions, infeasible assumptions or
unclear ownership that could materially misdirect implementation. Use exact
section references and targeted source when a concrete integration claim needs
checking. Verify that each relevant compatibility obligation has an owner and
acceptance path. Do not require a body-by-body audit of every framework method.

Future exact A2/A3 artifacts and product tests are legitimate staged deliverables.
They are not defects simply because unapproved code is not written. A future gate
must still specify an actionable owner, required decision/evidence and timing;
it cannot conceal a known contradiction or impossible dependency.

## Established inputs and explicit exclusions

- Completed Docling evaluation and measured configured profile are accepted
  baseline inputs for this review. Assess how Friday integrates those capabilities.
  Flag a specifically new/uncovered integration assumption; do not restart
  standalone converter, OCR, tokenizer or model efficacy testing.
- Do not rebuild AST/test/fixture inventories, recompute all DI/FC digests,
  stream old evidence archives, inspect wheel internals or repeat provenance
  audits. Existing inventories/captures are inputs; judge the planned test
  coverage and acceptance duties. No live calls, imports/tests, builds or installs.
- Never open/parse/execute Finance's test_integration_massive.py or access its
  credential. It is wholly outside this review, including AST parsing. There is
  no conflicting requirement to inventory it. Finance's indirect dependency/import
  impact can be assessed from ordinary package declarations or safe APIs.
- Preserve dirty YAML, .friday*, exports, .venv and every repository file. No
  user-state or secret reads. Read-only source/metadata is allowed where relevant;
  no broad scans of local state, prior/peer reports, memory or private transcripts.
- Prior readiness/construction/effects/acceptance gates are not waived by this
  focused review. Judge the construction plan, not that those gates have run.

## Completion, scoring and report

Complete F1–F8 before reporting a design score. If an actual blocker prevents
completion, report INCOMPLETE/BLOCKED, the precise missing area and reason, with
**overall=null**. Do not turn unread work into a low design-quality score. Record
completion as areas assessed out of8. For completed assessments, coverage scores
completeness of this declared focused assessment, not exhaustive-source or runtime
confidence.
For a completed assessment return honest coverage and overall scores out of10.
The requested gate is each seat VERIFIED, zero mandatory findings and both>=9.5;
no inflation, averaging or rounding up.

Use a compact F1–F8 table, numbered mandatory findings (requirement, gap/evidence,
bounded fix, acceptance implication), separate advisories, completion flag,
scores/rubric and precise limitations. Do not reproduce all original requirement
texts or inventories. Approximately1000–2000 words normally suffice; evidence and
necessary findings take priority. Keep source reads bounded and recover truncated
output. Finish the eight-area assessment rather than an unrelated audit checklist.

This seat is fresh, read-only and independent. No delegation, repair, replacement
or extra round. Write only to your own external scratch. Verify request/target
hashes, HEAD/branch and logical index before status at entry/exit, with
GIT_OPTIONAL_LOCKS=0 and bytecode off. Do not run administrative suites: controller
records structural checks once; your work is the design assessment. A document
VERIFIED grants no construction, effects, UAT, acceptance or delivery authority.
