# INGEST design council — round3 reconciliation

**Gate not met.** Technical design needs changes; the Opus seat is procedurally
BLOCKED under the round3 request. No earlier outcome is changed or waived.

| Reviewer | Reported outcome | Independent score |
| --- | --- | ---: |
| [GPT-6.1 Sol](sol-report.md) | VERIFIED | 9.6/10 |
| [GPT-6 Astra](astra-report.md) | CHANGES_REQUESTED | 9.2/10 |
| [Claude Opus5.5](opus-report.md) | BLOCKED; separate technical CHANGES_REQUESTED | 9.15/10 technical |

Candidate `36362be514ef387183a27d930cd41a8799e3d714`; correction base
`2956b861de75fcf7ebf463c82f5f470cf6fa7b40`; branch `feature/cmd-ingest-001`.
All28 criteria were assessed independently. Raw reports and boundary receipts
are byte-identical copies, pinned in [reconciliation.json](reconciliation.json).
The request, helper, environment wrapper, metadata and compressed protected
manifest are archived unchanged; original absolute paths are not rebound.

## Remaining mandatory findings

1. **INGEST-R3-ASTRA-001:** Memory v2 snapshots need an explicit typed handoff
   through Chat aggregate contracts, writer/readers and rollback. Retain strict
   legacy v1 types and define closed version dispatch, compatible nested versions,
   public exports and separate Memory versus Chat layout fingerprints. Add the
   exact known consumer paths and aggregate round-trip/tamper proof obligations.
2. **Opus M-1:** explicitly distinguish an unset fallback path from an explicitly
   configured destination, and pass/refuse rules for an existing graph/WAL or
   reused Runtime data-root container. These implement the already settled
   fresh-store policy; no new maintainer preference is required.

Useful advisories cover one Gate-A trace table, existing Core lazy imports,
direct-client fallback probes, Runtime transcript/artifact-root effects, inert
embedding-service objects versus resource initialization, disjoint marker-state
rows and pre-upgrade legacy backup guidance. None requires a new feature family.

## Procedure and evidence limits

Opus correctly reports BLOCKED under the literal round3 rule: a cat of its own
start-integrity output and wc over its own scratch bypassed the all-command
wrapper. Those were scratch reads, not repository or store operations. Matching
later integrity does not erase that contract deviation. Its technical finding
and9.15 score remain separate evidence, not a clean VERIFIED seat.

The controller's round3 wrapper requirement was broader than needed for Git
optional locks. For **future round4 only**, Git/repository/admin subprocesses
and any process invoking them must still use the verified wrapper/private env;
plain source/scratch reads and own-report writes/hashes are explicitly permitted
without it. Repository read-only rules, private outputs, exact pins and strict
Git environment remain mandatory. This future precision correction neither
rescues the old verdict nor licenses repository mutations.

Start/end and [controller frozen integrity](controller-frozen-integrity.json)
pass for all17,583 protected entries, six metadata records, HEAD/branch/index/
staging/status. Logical index: `43738da1ed6e59de584e729e570b1bbeb4b5ab54b7813c66660f684951b5f9fc`.
Source findings are design feasibility inspection, not executed runtime failures.
Admin checks pass; no product tests/builds/installs, live stores or inference
were run. Historical baseline debt remains failed/unwaived.

## Next gate

Use the final authorized correction/review round4, with a new frozen candidate
and fresh Sol/Astra/Opus contexts. All seats must independently be VERIFIED,
score>=9.5 and have no mandatory findings. Otherwise return remaining issues;
no fifth pass, construction, Gate-A execution, acceptance or delivery follows.
