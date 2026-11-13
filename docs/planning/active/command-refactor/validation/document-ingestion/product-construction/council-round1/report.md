# INGEST product directive — council round 1 reconciliation

**CHANGES_REQUESTED. The required 9.5 gate is unmet.** All three fresh reviewers
returned mandatory findings; there is no construction approval. The review target
remains byte-identical at SHA256 `da911b7e6f052ab27b0e37ee939e52a0555ca177c047f84b475c9fc72b5414c1`.
Frozen candidate: `fb587e7a12f48ef0d6937e008045de1de2dd8cd2`.

| Reviewer | Coverage | Overall | Outcome |
| --- | ---: | ---: | --- |
| GPT-6.1 Sol | 9.6 | 9.2 | CHANGES_REQUESTED |
| GPT-6 Astra | 9.6 | 9.1 | CHANGES_REQUESTED |
| Claude Opus 5.5 | 9.4 | 8.6 | CHANGES_REQUESTED |

The threshold applies to each seat, both scores, with VERIFIED and no mandatory
findings. Scores are retained exactly; no averaging, rounding-up or substitute
review. The result covers conditional document readiness/source feasibility,
not unbuilt implementation conformance or whole Gate A.

## Reconciled corrections

1. **INGEST-PD-R1-001 — high: phase exit dependencies.** All three reviewers
   identify I1 requirements that need I2/I3 consumer/recovery/chunking code. Opus
   also identifies whole-suite DI-35 acceptance prematurely placed at I2.
   Define exact per-phase sub-obligations and prerequisites, and keep full public
   DI/FC positives and full DI-01–36 closure at their proper exits/aggregate.
   Demonstrate a topologically valid owner/file/test/earliest-phase join.
2. **INGEST-PD-R1-002 — medium: preconstruction versus installed acceptance.**
   Sol identifies A1/RD-06 requiring actual product extras/profiles before the
   implementation authorized to create them. Astra and Opus note related A1/RD
   ambiguity. Separate qualification of dependencies/deployments and baseline
   experiments from post-build installed-product/consumer and verified-example
   acceptance. Preserve every final positive and the existing readiness gate.
3. **INGEST-PD-R1-003 — medium: requirement traceability.** Opus identifies wrong
   DI group/seed tags and ambiguous treatment of DI-12's required final three-seat
   review. Map exact REM definitions to proof groups, phases and assertions;
   explicitly retain the separately authorized post-code-freeze council before UAT.

These are corrections to the draft's sequencing and mapping. The controller
accepts the source-supported findings; the governing REM requirements are not
waived. Each original mandatory finding maps to one primary group in the
[machine-readable reconciliation](reconciliation.json), with overlaps disclosed.
No correction has been applied to the reviewed directive or seed in this round.

## Advisories to consider in a bounded revision

Consolidate intentional compatibility exceptions/remedies; surface B02 hosted
baseline qualification first; resolve CLI's conditional source disposition;
name the conversion-worker/headless owner; complete inventory scope/root totals;
refresh old preparation labels; fix indirect-package arithmetic; reconcile the
canonical post-readiness impact form; correct the corrupt PDF seed's eight-byte
description. All original advisory IDs/dispositions remain in the reconciliation
and individual reports. Advisory status does not weaken a parent requirement.

## Evidence and conduct

- [Sol report](sol/report.md), [command ledger](sol/commands.md),
  [compact evidence index](sol/evidence-index.json).
- [Astra report](astra/report.md), [command ledger](astra/command-ledger.json),
  [compact evidence index](astra/evidence-index.json).
- [Opus report](opus/report.md), [command ledger](opus/command-ledger.json),
  [compact evidence index](opus/evidence-index.json).

Reports were hash-verified before retention. Raw report bytes are preserved.
Each reviewer reran seven allowed offline administrative checks and opening/
closing boundaries. Static inventory/source inspections are fresh; earlier
Docling/model/Chroma/product results are inspected evidence, not fresh executions.
Controller closing boundary also passed before metadata closeout: 18,715 tracked
files, 26 symlinks, eight retained metadata entries and 37 pins. Dirty YAMLs,
`.friday-old`, source, working environment, stores and exports remain preserved.
Known root debt and protected user-config whitespace remain failed/unwaived.

Opus disclosed printing the first 400 bytes of controller delegates.json: seat,
status and opaque task ID, without peer findings/reasoning/scores. This was an
inventory-exclusion deviation. The request's substantive peer-reasoning BLOCKED
trigger was not met; retain the disclosed review with its unchanged scores and
CHANGES_REQUESTED outcome. The common phase finding is independently corroborated.
No replacement, concealed exception or extra round is used.

## Stop point

One authorized round is complete. No automatic remediation/reissue was authorized;
no council remains active. Recommended next work is a bounded documentation-only
correction of these three groups and applicable advisories, followed by a newly
authorized fresh council. The user retains that direction and final approval.
Product construction, whole-readiness qualification, live model/store effects,
UAT, acceptance and delivery remain ungranted by this review.
