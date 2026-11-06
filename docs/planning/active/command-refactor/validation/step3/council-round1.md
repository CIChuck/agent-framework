# Step 3 readiness council — round 1

Date: 2026-11-06
Outcome: **CHANGES_REQUESTED**
Execution phase: planning
Validation state: changes_requested
Scope: planning/readiness and foundation API consistency; no implementation validation

This is the consolidated result of the requested single three-provider pass.
All three reviewers returned CHANGES_REQUESTED. The foundation-only approach is
technically defensible, but the reviewed directive is not ready for Step 4
approval. The findings below remain open; this report records results and a
proposed correction plan, rather than repairing or approving the frozen draft.

## Frozen identity and original reports

- Candidate: `95fdeadc0a0e4b9720cdb553e5b26756a438ab70`.
- Base: `bbbd90e05143137c5a1d49eacedb4125d254b8fb`.
- Diff: base..candidate, 22 files under `docs/planning/`; no product changes.
- [Dispatch request](council-request.json) SHA-256:
  `fc15a9d5f7439b96e3bd761bb2b16ae8cf404aa2748fbad98c622a6fd082765a`.
- Approved API SHA-256:
  `e5ba883fb246967320243e1dbc9c2a70fcf6189c05540a45961388f2b6466b74`.

Original report text is preserved as received, including reviewer-specific
line references and qualifications. The request remains unchanged as historical
dispatch evidence; its inaccurate finance/sandbox premise is itself covered by
CMD-RDY-002 below. [Collection receipt](council-round1/receipt.json) pins the reports.

- Claude Opus 5.5, high: [full report](council-round1/claude-report.txt).
  <t3-thread://v2/6ee9d258-4414-45b2-ad28-6fe30f4adb05/thread:delegated-task:command%3Amcp%3Ad51d3c36-7628-4e11-bad1-5d855750ae16%3Adelegate-task%3Acmd-readiness-95fdeadc-claude-r1>
- GPT-6.1 Sol, high: [full report](council-round1/sol-report.txt).
  <t3-thread://v2/6ee9d258-4414-45b2-ad28-6fe30f4adb05/thread:delegated-task:command%3Amcp%3Ad51d3c36-7628-4e11-bad1-5d855750ae16%3Adelegate-task%3Acmd-readiness-95fdeadc-sol-r1>
- Gemini 4 Argon High: [full report](council-round1/gemini-report.txt).
  <t3-thread://v2/6ee9d258-4414-45b2-ad28-6fe30f4adb05/thread:delegated-task:command%3Amcp%3Ad51d3c36-7628-4e11-bad1-5d855750ae16%3Adelegate-task%3Acmd-readiness-95fdeadc-gemini-r1>

No numerical scores were requested for this planning review or supplied.
All reviewers used fresh contexts and the shared checkout read-only. Each
reported matching request, authority, deliverable, protected-file and source
pins at start/end. Full owning-suite counts remain historical receipts.

## Consolidated mandatory findings and proposed correction plan

Findings are retained on their evidence, rather than decided by majority vote.
Sol and Gemini's favorable R-03/R-06 assessments do not negate Claude's
specific reproductions of directive and ordering gaps.

1. **CMD-RDY-001 — High — package-cohort scope and verification.**
   Maps to Claude VAL-001 (R-03).
   Adding the proposed package makes the exact 17-project cohort assertion fail.
   The directive prohibits the existing-test/root-metadata edits needed to
   integrate it. Decide cohort membership before approval; the recommended
   proposal is to add the dependency-free package to the existing lock-step
   cohort. Bound any required changes to root `pyproject.toml`, its workspace
   source/`all` extra, `tests/integration/test_package_cohort_metadata.py`,
   `scripts/check-package-artifacts.py`, and `uv.lock`, plus package lists
   where needed. Add cohort/metadata checks and a root-test import procedure
   that proves the new package is actually installed. Acceptance: the draft's
   allowed paths and verification cover cohort count/name/version, root
   inclusion and wheel inventory without introducing a client dependency.
2. **CMD-RDY-002 — Medium — default-install evidence and provenance.**
   Maps to Claude VAL-002, Sol STEP3-SOL-001 and Gemini VAL-STEP3-001 (R-05;
   supporting RD-02/R-04 text).
   Default Chat/registry/CLI imports and Chat help pass; the explicit
   `friday_tools` import fails on missing `friday_finance`. The relative
   `friday_tools.sandbox` module uses the standard library; it is distinct
   from the lazily imported optional `friday_sandbox` distribution. The first
   default log came from an earlier, unpinned probe revision. Correct the
   readiness summary, draft RD-02 text, unit-map environment entry, receipt
   and execution-log record with an appended correction. Preserve raw logs
   and the original request. Rerun the default profile with an exact pinned
   script and save separate import/help/entry-point outcomes and network
   attempt counts. Acceptance: reproducible default evidence makes no runtime
   health claim; finance+sandbox remains diagnostic, not a demonstrated
   minimum. Generic CLI app failure and future client packaging gates remain.
3. **CMD-RDY-003 — Medium — ingest admission dependency.**
   Maps to Claude VAL-003 (R-06).
   `ingest` uses shared admission in existing dispatch, but FILE-001 precedes
   MAINT-001 and lists only MEMQ-001 as prerequisite. Make admission an explicit
   prerequisite, either through MAINT-001 or a separately reviewed capability,
   and preserve ingest admission in the owning-unit description. Acceptance:
   the map remains acyclic, dependency order is valid, all 50 cases/three
   aliases remain assigned exactly once, and the summary/ledger agree.
4. **CMD-RDY-004 — Medium — lock procedure and permitted registry access.**
   Maps to Claude VAL-004 (R-03).
   The first plain `uv run --with-editable` may relock; a disposable stub
   exposed missing offline registry artifacts. Specify permitted package
   registry access or a reproducible offline alternative and an explicit
   lock-generation step. Require a semantic `uv.lock` diff proving no
   unrelated dependency/version/source change, followed by frozen commands.
   Acceptance: the builder can execute the documented checks without an
   unstated external-service permission or uncontrolled resolution change.
5. **CMD-RDY-005 — Low — CLI scenario boundary.**
   Maps to Claude VAL-005 (R-06/R-04).
   SC-08 assigns FND-001 installed-entry-point proof that RD-02 explicitly
   defers. Limit FND-001 to the required source-level CLI regression and
   foundation wheel proof; retain installed-client entry-point proof at its
   later owning delivery gate. Acceptance: scenario and directive obligations
   agree, with no client repair or healthy-client claim in FND-001.

These corrections affect planning, draft scope and evidence only. Product
package integration remains future construction under a separately approved
directive. No source/test/configuration repair, API redesign, handler migration,
new dependency, command removal, or external delivery is authorized here.

## Controller reconciliation and evidence limits

Direct inspection confirms the 17-project/name assertions and root coverage
test, the directive's prohibitions and unqualified uv commands, the ingest
admission wrapper, FILE-001's missing dependency, and the conflicting SC-08
text. Source also confirms the local sandbox/lazy optional sandbox distinction.
All three reviewers independently reproduced the default tools/finance defect.
Claude's disposable cohort/lock probes are reviewer evidence; the controller
did not repeat those experiments.

The controller independently verified the frozen candidate, all 16 authority
and 22 deliverable pins, request hash and all 16,882 protected hashes before
recording these results. Collection changes only navigation/process records
and adds reports; it does not correct the reviewed packet. Original draft,
unit map, probe and raw receipts remain byte-identical to the reviewed inputs.
The accompanying receipt records collection checks and preservation results.

The four unrelated TUI broken links remain the documentation baseline.
Offline full-cohort dependency resolution, runtime construction, live tools/
providers, terminal/audio UAT, and Linux/Windows acceptance remain unproven.
API-01–API-06 consistency is supported by this pass, but the overall readiness
verdict is CHANGES_REQUESTED. No prior verdict is promoted into approval.

## Next decision and order

Read this report first, then the [readiness summary](../../readiness-review.md)
and [draft directive](../../directives/CD-CMD-FND-001-neutral-foundation.md)
with the findings above in view. Decide bounded planning/evidence correction
and package-cohort disposition before Step 4. No automatic remediation or
second council pass follows this one-round request.

After authorized corrections, freeze a new candidate; the old council applies
only to the original bytes and does not verify the correction. Determine the
required fresh validation scope explicitly. Step 4 then records the exact
directive/base, RD-01/RD-02 dispositions and how independent architecture
readiness is satisfied. Construction, feature acceptance and delivery remain
separate and unapproved.
