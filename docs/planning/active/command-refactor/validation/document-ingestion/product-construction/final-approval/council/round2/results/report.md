# Final INGEST documents — final council outcome and bounded correction

2026-11-13. **CHANGES_REQUESTED; council stopped after round2/2.** All three
fresh seats complete FD1–FD8 and confirm the substantive C1–C3 corrections.
They identify the same remaining defect: A4 names impact v0.7 instead of the
current, correctly pinned v0.8. This is one shared finding, not three new design
problems. The formal per-seat9.5/zero-mandatory gate is not met.

Reviewed candidate: `b4eecbe804b862f606995c4c4e5197c9b9d37150`.
Presented content at review: `115e4cecdb659d2af043c11e73964aca0a590d78`.
The final additional council is complete. No third round, replacement or new
delegation is launched. Product construction remains unapproved.

## Complete independent reports

| Seat | Verdict | Reported overall /10 | Areas | Mandatory findings |
| --- | --- | ---: | ---: | ---: |
| [GPT-6.1 Sol](sol/report.md) | CHANGES_REQUESTED | 9.5725 | 8/8 | 1 |
| [GPT-6 Astra](astra/report.md) | CHANGES_REQUESTED | 9.565 | 8/8 | 1 |
| [Claude Opus 5.5](opus/report.md) | CHANGES_REQUESTED | 9.365 | 8/8 | 1 |

Scores are reported values, not averages or post-correction estimates. Sol's
printed FD8 rating9.5 at weight0.5 implies0.475, while its contribution shows
0.4775; the displayed area ratings therefore sum9.570 rather than9.5725. Both
exceed9.5. The original report and arithmetic note are preserved; no verdict or
score is rewritten, and its mandatory finding still blocks formal readiness.

All seats find the canonical impact v0.8 and proposed execution profile ready
within this bounded review. The human README is substantively ready; its linked
exact approval manifest contains the shared defect. There are no missing-source,
vendor-quality, serving-parity or future-product-test findings.

## Substantive corrections confirmed

- **C1:** Certifi2025.11.12 is the locked baseline. Early phases record installed
  version/module/CA origin or explicit absence. The selected2026.10.23 upgrade
  and >=2026.10.19 floor arrive with Tools/Docling at I3-C1; subsequent applicable
  installs and final lanes enforce them. No unrelated early bump is required.
- **C2:** tokenizers0.22.1→0.23.3 is disclosed as a shared Chroma/LiteLLM lock
  effect at I1-C2, with unchanged-legacy positives and stop-on-conflict behavior.
- **C3:** guarded embedding prerequisites, phase activation within the started
  initiative and the noncyclic presentation receipt are substantively correct.
  At review the receipt binds a request whose A4 scalar still saysv0.7.

These are assigned future implementation obligations, not tests rerun here.

## Shared finding and exact post-review correction

The three finding identifiers (Sol SOL-FD-001, Astra FD-ASTRA-001 and Opus M1)
refer to `approval-request.json:gate_disposition.A4.requires`. Its duplicate
version text contradicts the same manifest's current_package_impact version and
correct digest. Hashes make the intended target recoverable but do not reconcile
the operative wording. I missed this scalar during the preceding update.

After all reviewers stopped and the frozen closing check passed, the controller
completed this same requested version alignment under the existing edit direction.
Only that one JSON field changed: A4 now points to **the path, version and SHA256
in current_package_impact**, plus the document commit named by presented_revision.
This removes the duplicated version literal. Every other request field is equal;
README v2, impact v0.8, execution profile, technical contracts/maps and runtime
source are unchanged.

The [one-field change record](../../../post-review-correction.json) preserves the
exact before/after wording and request hashes. The [current presentation receipt](../../../presented-revision.json)
binds corrected content commit `b357c3c4` and the new request digest. Original
[reviewed request](reviewed-approval-request.json) and
[reviewed presentation receipt](reviewed-presented-revision.json) remain byte-exact.
Current binding/preservation checks are recorded separately from the reviews.

**This post-review correction is not independently VERIFIED.** The council
reports remain CHANGES_REQUESTED for the old reviewed bytes; no score is assumed
to rise and no 9.5 gate is silently closed. The maintainer must explicitly decide
whether to accept this bounded correction without another council, and separately
approve exact construction/private effects if satisfied. No further automatic
technical edit or review is scheduled.

## Optional advice retained

Headless Certifi enforcement comes through the shared lock, not a new declaration;
phase-list ordering, an explicit I1-C1 baseline entry, Finance-row CA impact and
repeating the fresh-store binding prerequisite are optional clarity improvements.
They are not extra mandatory findings or new implementation scope. Per-phase
activation records remain explicit. No further substantive edits are applied.

The frozen outer review request also retained a v0.7 descriptive scope caption;
its explicit primary target/pins and the actual brief identify v0.8. The original
request is retained unchanged as evidence. There is no active later review request
to rewrite; any future request must derive the current version from its binding.

## Evidence, preservation and authority

[Original report hashes and outcome](index.json), the [frozen review request](request.json),
[controller closing boundary](controller-closing.json) and minimal seat evidence
retain the exact review basis. Before the post-review edit, all pins, logical
index before status, HEAD/branch/staging,16,690 protected nonplanning files,
26 symlinks and eight preserved metadata/hash records matched. No product imports,
tests, installs, provider/model/network/store operations, user-state mutations or
production configuration changes occurred. Controller closeout checks are planning
and binding evidence only, not runtime or independent verification.

The initiative remains started/local; construction, effects, human UAT/acceptance
and delivery remain unapproved. All council delegates have finished. The next
task is Chuck's explicit disposition of the corrected approval package and the
unmet formal council gate; no third council has been authorized or launched.
