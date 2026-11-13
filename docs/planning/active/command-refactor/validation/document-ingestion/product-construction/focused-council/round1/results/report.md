# Focused INGEST directive council — round1 reconciliation

**CHANGES_REQUESTED.** All three seats completed the focused F1–F8 assessment;
the all-seat9.5 gate is not yet met. Candidate `92e356d1`, directive v0.6.

| Seat | Outcome | Coverage | Overall | Mandatory findings |
| --- | --- | ---: | ---: | --- |
| [Sol](sol/report.md) | VERIFIED | 10.0 | 9.6 | None |
| [Astra](astra/report.md) | VERIFIED | 10.0 | 9.70 | None |
| [Opus](opus/report.md) | CHANGES_REQUESTED | 9.5 | 9.34 | M1 document /read lifecycle and acceptance |

M1 is retained: current Chat calls a synchronous document reader, while /read
has no Memory shared admission. The directive's generic worker clause names an
admission lease and its only cancellation witness is ingestion-specific. Document
/read needs explicit off-event-loop Tools work, Chat-owned non-Memory request
lifecycle, cancellation/exit output discard and join/drain, with response/shutdown
acceptance. Other seats' VERIFIED results do not waive this independently
supported gap.

Related advisories clarify headless document composition, injected planning/
counting ownership, the raw-tail dispatch seam, no-clamp capacity behavior, asset
deployment ownership and headless defaults. These are bounded integration-plan
clarifications, not a restart of Docling testing or framework algorithm work.

Original completed reports and [machine reconciliation](reconciliation.json)
retain rubric scores and source limits. Every reviewer preserved entry/exit
identity and protected metadata. Controller preservation and structural checks
pass. No product/Docling test, AST inventory rebuild, archive/wheel audit, model/
network/store operation or repository write by reviewers occurred.

The controller proceeds with bounded document correction and a fresh full
focused round2 under the existing at-most3 authorization. No construction,
effects, UAT, acceptance or delivery authority follows.
