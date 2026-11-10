# MAINT-001 round2 reconciliation — CHANGES_REQUESTED

Candidate `80e214b2859f14e24bc716a989a69cd20962cf07`; document readiness only.
Sol8.2 and Astra8.6 both returned CHANGES_REQUESTED. Both read-only reviews
passed integrity/isolation, with17,437 protected files unchanged; neither ran
product tests/builds/provider/store operations. [Raw reports and boundary evidence](evidence.json)
retain independent wording. No majority vote or advisory score closes a finding.

Two merged mandatory issues:

1. R2-SOL-M01: direct-await default does not protect a multi-write headless stage
   from caller cancellation. Correct with a shared shield-and-drain default and
   explicit default/injected cancellation tests, keeping outer rollback separate.
2. R2-SOL-M02 and MAINT-R2-ASTRA-01: observer/results cannot carry the shared
   scope evidence required for durable receipts. Correct with a Memory-produced
   typed operation/stage/plan/selection receipt and before/planned/after events;
   require meaningful completed verification digests and reject substitution.

The correction edits only planning documents and named future test requirements.
It also clarifies the existing strict decoder relocation, error-category mapping,
static path coverage and current administrative phase. These advisory edits do
not broaden runtime behavior or the construction allowlist.

Fresh round3 must inspect the correction delta first, then both full documents.
The changes are proposed closure, not independent verification. Implementation,
acceptance, providers/stores and delivery remain unauthorized. This is correction
cycle1 after the ownership review; do not loop beyond the declared two-cycle limit.
