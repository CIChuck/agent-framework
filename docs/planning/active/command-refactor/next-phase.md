# Command refactor — next-phase checkpoint

Date: 2026-11-06
Branch: `feature/command-refactor`
Status: Legacy launcher retirement VERIFIED; required-finance default proof passes; dependency validation pending
Execution phase: validation
Validation state: in_review

This is the main next-step document. The [packet index](README.md) maps the
supporting files. Current planning lives in Agent Framework; earlier TUI-folder
directions and imported receipts retain their historical provenance.

## Recorded decision and Step 3 resumption

Chuck Russell approved [CMD-DESIGN-001](approval/foundation-design.md) on
2026-11-06 and instructed: “pause before, starting step 3 for review.”

Step 3 refers to the approval sequence below: **resolving prerequisites for the
first implementation unit**. It does not mean tactical task 3 or phase P3.
On 2026-11-06 the maintainer resumed it with “Proceed to step three” and
requested a read-only council using Claude Opus, OpenAI Sol and Google Gemini.
The prior pause is lifted for prerequisite work only; construction stays gated.

The foundation approval covers API-01–API-06 and neutral types/registry semantics
in the exact [API document](shared-command-api.md) pinned by the approval record.
It does not approve the whole contract, the construction directive or P0/P1 exit.

## Approval sequence

| Step | Action | Current state |
| --- | --- | --- |
| 1 | Reconcile navigation and freeze the design inputs; obtain required independent design-readiness evidence. | Approved API pinned; foundation consistency supported. Corrected packet VERIFIED at `fcea84b8`; subsequent packaging units need their own validation. No construction approval inferred. |
| 2 | Maintainer decides CMD-DESIGN-001. | APPROVED on 2026-11-06 by direct instruction. This decision does not fabricate independent review evidence. |
| 3 | Resolve applicable P0/P1 prerequisites for the first implementation unit. | Prior readiness VERIFIED at `fcea84b8`; legacy retirement VERIFIED at `06285ae4`. Required finance default imports pass; fresh dependency validation pending. RD-01 remains proposed; RD-02 records separate packaging resolutions. Full P0/P1 remains open. |
| 4 | Maintainer approves the exact CD-CMD-FND-001 directive, execution base and readiness disposition. | Draft; not approved. |
| 5 | Execute separately approved units, verify frozen candidates, then obtain feature acceptance. | Future work; product construction unauthorized. |

## Existing work and remaining obligations

Read the [fresh validation result](validation/step3/correction-report.md), then
[readiness-review.md](readiness-review.md) for the corrected Step 3
assessment, pinned default-profile evidence, proposed case/unit map and Step 4
decisions. The [original council result](validation/step3/council-round1.md)
remains historical for `95fdeadc`; the authorized
[correction record](remediation/REM-CMD-STEP3-001.md) defines the five changes.
The maintainer has since identified the framework CLI launcher declaration as a
legacy error and approved [its removal](directives/CD-CMD-CLI-001-retire-legacy-launcher.md).
The [CLI removal](validation/legacy-cli-removal/report.md) is now VERIFIED.
The maintainer then requested finance mandatory for tools. The
[current default proof](validation/required-finance/receipt.json) installs
finance/SDK without extras and imports tools successfully. RD-02 now records
these two separate resolutions rather than a pending defect waiver; fresh
dependency validation must bind the updated candidate before Step 4. Historical
reports/probes retain their exact prior observations.
The table below remains the broader roadmap; full P0/P1 closure is not claimed.

| Item | Existing record | Outstanding beyond this readiness assessment |
| --- | --- | --- |
| Product scope and ownership | [Scope decisions](scope-decisions.md), O-01–O-05: nine complete removals, tools retained, 41 names/three aliases, neutral shared owner, preserved separate CLI and retained quirks. | Apply these decisions to the detailed unit map; do not reopen them implicitly. |
| Source map | [PAR ledger](validation/par-coverage-ledger.md) and frozen 50-name/three-alias matrix exist. | Complete per-case positive/invalid/unavailable/error/effect evidence and owning-unit assignments. A source map is not behavioral signoff. |
| Baseline receipts | [Local continuation](validation/local-2026-11-06/README.md) records matching inventoried hashes, 826 controlled Chat tests and 155 CLI tests. | Close applicable installed-client, environment and case-level evidence gaps. These stored results were not rerun for this approval recording. |
| Foundation contract | [CMD-DESIGN-001](approval/foundation-design.md) approves the limited foundation input. | Resolve applicable independent-review/readiness obligations; family capabilities, service ownership, progress/cancellation and the complete contract remain open. |
| Unit/scenario/environment map | [Phase plan](phase-plan.md) and [tactical plan](tactical-plan.md) describe required outputs. | All cases/aliases now have proposed owners and eight scenario obligations in the readiness map. Final family contracts, order/platform approval and per-case evidence remain before affected construction. |
| First construction unit | [CD-CMD-FND-001](directives/CD-CMD-FND-001-neutral-foundation.md) exists as a draft. | Pin the execution base, approved API and applicable readiness evidence; obtain separate construction approval. Any foundation-only deferral requires explicit disposition. |

## Reading order for the next decision

1. [Fresh validation result](validation/step3/correction-report.md): exact
   candidate, closure of the five findings, supporting checks and limits.
2. [Readiness review](readiness-review.md): current evidence, RD-01 proposal and
   RD-02 resolution record; fresh dependency delta validation is pending.
3. [Draft foundation directive](directives/CD-CMD-FND-001-neutral-foundation.md):
   exact paths, package integration, tests, lock procedure and stop conditions.

The [phase plan](phase-plan.md), [tactical plan](tactical-plan.md) and
[test strategy](test-strategy.md) remain reference material for broader gates;
they are not additional approval documents for this Step 4 decision.

The single requested council pass completed against candidate `95fdeadc`.
Chuck Russell accepted bounded corrections and fresh validation. The corrected
draft selects the existing package cohort, an explicit controlled lock procedure
and MAINT-001 before FILE-001. Fresh review VERIFIED candidate
`fcea84b879995735308e5be18cfed6cbb82a0b17`. Step 4 must approve the exact
directive/base, explicitly approve RD-01, record validated RD-02 resolution and whether this
review satisfies the architecture-readiness gate for the pinned API. The
proposed execution base must now be the updated required-finance validation
candidate, because its product metadata and readiness disposition changed after
`fcea84b8`. The old verdict cannot verify this delta. No replacement CLI launcher
is authorized by foundation approval. Finance repair is separately authorized
under CD-CMD-DEP-001; its current default import proof needs fresh validation.
No automatic additional council/remediation loop or product build follows.

The initiative remains started/local; completion, acceptance and delivery
are separate decisions. TUI construction remains gated on command-refactor
acceptance and separate authorization.
