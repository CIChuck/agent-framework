# MAINT-001 specification council — round 1 reconciliation

**VERIFIED — specification/design readiness only.** No mandatory findings.

Reviewed candidate: `2d0957f495b2a11088388bc7e61d4ced3a3f4db4`.
[Specification](../../../../maintenance-reorganization-specification.md) SHA256:
`e085d9fbad99b8cf59887db4590e41ee6f9af2cb963dd99e4fbbc7ee7f2332ab`.
The reviewed bytes remain unchanged. This report is an administrative descendant,
not a new independent verdict for changed specification or implementation bytes.

Chuck Russell explicitly requested the OpenAI-only council after document review.
Two fresh read-only high-effort contexts completed independently, with no builder
transcript, peer verdict, nested delegation or repairs. Both terminal results
have no pending child work or questions.

| Reviewer | Outcome | Advisory score |
| --- | --- | --- |
| GPT-6.1 Sol / high | VERIFIED | 9.0/10 |
| GPT-6 Astra / high | VERIFIED | 9.2/10 |

All MS-01..08 criteria pass in both reports: bounded authority/baseline;
pending-memory verification order and retained coverage; shared run-local exact
selection; honest final-judge counts; modes/skips/preview; failure/recovery;
proposed evidence adequacy; and specification-level completeness.

## Reconciled advisories

1. **Preflight and empty-stage calls** (Sol A01 / Astra A01). The directive must
   separate readiness probes from record assessment completions. Preview must
   work with missing providers and make no probe/complete/embed call. Specify
   precisely whether and when execute readiness probes run for empty candidate
   selections. Test those paths with tripwire providers; no weakening of the
   specification's offline-preview requirement is proposed.
2. **Migration-only synthesis** (Astra A02). Add a named MT-02 fixture where
   synthesis backfills existing lineage metadata but creates no outputs. The
   generated-reference selection is empty and triggers no second assessment.
   Existing records must not be selected from changed-count totals.
3. **Legacy journal fixtures** (Sol A02 / Astra A03). Choose a concrete
   compatibility route in the directive. Preserve actual version-1 completed
   and unfinished journal/bundle fixtures; exercise installed restart recovery,
   unknown/malformed versions and interruption in new stages. Preserve historical
   single-stage `verify` records without inventing a two-stage history.

These are accepted planning inputs for the future directive, not mandatory
specification corrections or completed implementation work. There is no
reviewer disagreement requiring escalation and no new review round is started.

## Evidence and integrity

[Evidence bundle](evidence.json) embeds exact raw reports, reviewer boundary
receipts, the request and controller integrity receipt with source paths/hashes.
The controller read both full reports and rechecked request/manifest identities,
all nine pins, all 17,431 protected contents, HEAD, branch, logical index before
status, empty staging and preserved .friday-old/exports metadata before making
these administrative updates. Both reviewers independently checked the same
boundaries. User configuration edits and local state remain untouched.

**Actually executed by reviewers:** identity/integrity hashing and bounded
source/document inspection. Existing source and test bodies were inspected.
No tests, builds, live models, network, personal-store operations or UAT ran.
Thus this is not executable MT01..09 proof, a construction directive, product
validation or a claim that the repository is green. Known baseline debt remains
unwaived. Local document/admin checks are recorded in the execution log.

## Next gate

Prepare the exact construction directive using these advisory inputs and present
it to Chuck Russell for document review. Any unresolved product/API or journal
compatibility choice must be explicit. No implementation is approved by this
council. No further council or sub-agent invocation occurs without direction
following the requested human document-review opportunity. Accepted MEMQ remains
closed, and the umbrella initiative remains started/local.
