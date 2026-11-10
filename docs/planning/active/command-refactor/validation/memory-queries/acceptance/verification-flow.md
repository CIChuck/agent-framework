# Current verification and meta-insight flow

Read against the accepted checkout39a631a9 on2026-11-10. This note describes
existing code; it changes no verification, synthesis, ordering or model policy.

A verification stage selects active, non-empty memory records whose stored
verification_status is neither verified nor rejected. Three sequential LLM
reviews run: classifier, researcher, judge. Each sees collection/ID/document text;
later roles also receive earlier verdicts. Each must return exactly one decision
per requested collection/ID, without omissions/duplicates/extra IDs. The judge's
final status (verified/rejected/uncertain) and confidence are persisted. This is
not a majority vote. It is model assessment of supplied text: the current request
contains no browser/search/retrieval tools or required external citations. The
role names alone do not establish independent external fact checking.

Separate mechanical checks require complete enclosing JSON, bounded fields,
allowed statuses and confidence0..1, exact record coverage and valid storage
postconditions. Length-limited output, malformed JSON, schema/coverage failure,
provider timeout or store failure can fail the stage without finding a fact false.
Readiness probes and the three sequential calls add latency. The current model
requests return decisions for the selected batch, not one provider call per record.

Synthesis sources must already be active, non-meta insight/long_term records with
a topic and verification_status=verified. They are grouped by collection/topic,
subject to configured minimum group size and run/source limits. Unverified or
uncertain sources are quarantined from synthesis. Existing fingerprints, low
confidence, empty drafts or duplicate documents can also suppress output.

Full mode currently orders dedupe -> prune -> synthesize -> verify -> lifecycle
(with optional reembedding first). Synthesis therefore cannot use sources first
verified later in that same run. A successful run may verify sources, with meta
insights appearing on a later synthesis/full run. Newly generated meta records
start unverified and can themselves be considered by the following verify stage.
A failed execute operation rolls back its mutations; this can undo synthesis and
verification updates from that operation.

To inspect a targeted run, `/reorganize --verify --execute` executes verification
with normal recovery snapshots and potential metadata changes. Operational failure
is visible as `Step verify: failed`, errors and terminal status such as
failed_rolled_back, preflight_failed or recovery_required. Preserve the reported
run ID, journal and log paths and safe role/model/schema/finish/issue details.
`Step verify: completed` means the review completed; records may still be rejected
or uncertain and ineligible for synthesis. The console currently lacks a verdict
count breakdown, and `/meta` is a query, not a verification trigger. A later
synthesis preview can still warn about quarantined sources. This visibility
limitation is described here, not declared repaired by MEMQ acceptance.

Source: `friday_chat/reorganization/mutation.py` provider completion/verification
chain/coverage and `coordinator.py` planned steps; `friday_memory/maintenance/mutation.py`
source eligibility, stored verdicts and generated-record metadata. The acceptance
is maintainer-reported, not a new production run by the agent.
