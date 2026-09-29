# REM-008 — Reuse Owned MCP Memory Records And Immutable Receipts On Retry

Status: Approved for bounded execution; separate remediator authorized
Date: 2026-09-29
Approved by: repository maintainer
Approval evidence: "Fix the retry behavior. i will Validate afterwards." after the exact nine-path REM-008 proposal and separate-remediator request
Remediation base: `486f3cf585799cc46bc8a6c4f6cf4925734f7188`
Execution start: 2026-09-29 on the named current branch; controller records before remediator dispatch
Initiative: `friday-mcp`
Work unit: `MCP-WS-06`
Branch: `feature/friday-mcp-ws06-memory`
Reviewed candidate: `910508cd40c49c30ddfbd6a779aec5fda3ac2a67`
Original work-unit base: `99bde5148ee21f47d4734d2a026fb198a3d19cbd`
Finding: `VAL014-F01`, complete independent [VAL-014 report](../validation/VAL-014-report.md)
Approval: Granted for this nine-path correction and separate remediator; maintainer reserves validation of the resulting candidate

## Authority And Approval Boundary

Explicit maintainer direction, repository engineering/lifecycle/independent-validation
policies, accepted WS-00 through WS-05, the approved
[WS-06 directive](../directives/ws-06-memory-compatibility-ingestion.md), and the
complete frozen VAL-014 review control this bounded correction. The original
request, report, archives, authority and reviewed candidate remain unchanged.
The original WS-06 approval authorized its construction scope and independent
review; the separate maintainer message above now authorizes this numbered
correction and separate remediator. It does not accept the resulting candidate.

The [independent-validation policy](../../../../../reference/policies/independent-validation-policy.md)
requires: "Use a separate remediator for security, architecture, data integrity,
package boundaries, or a repeated failure." It also states: "Automated remediation
may proceed only for bounded, non-destructive findings that the maintainer
preauthorized." This finding concerns persistent record identity and append-only
receipt integrity. This directive records the maintainer's explicit approval.
The builder and validator must not silently repair the frozen candidate. Record
the execution start before dispatch. The maintainer reserved validation; no
validation result is inferred from remediation checks.

This is the first WS-06 remediation cycle. After two unsuccessful remediation
cycles, return unresolved findings to the maintainer. No later workstream, delivery,
historical migration or unrelated repair is authorized by this approval.

## Exact Allowed Implementation Manifest

Exactly nine paths are approved: four existing source files, four existing tests
and one new remediation implementation report.

- `packages/friday-memory/src/friday_memory/ingestion/mcp.py`
- `packages/friday-memory/src/friday_memory/retrieval/collection_manager.py`
- `packages/friday-chat/src/friday_chat/adapters.py`
- `packages/friday-chat/src/friday_chat/memory_mcp.py`
- `packages/friday-memory/tests_memory/test_mcp_memory.py`
- `packages/friday-memory/tests_memory/test_retrieval/test_collection_manager.py`
- `packages/friday-chat/tests_chat/test_mcp_memory.py`
- `tests/integration/test_mcp_memory_ingestion.py`
- `docs/planning/active/friday-mcp/execution/REM-008-implementation-report.md`

Controller approval/start, directive, request/report/evidence/status, packet
index/queue/log and board/dashboard are separate process artifacts. Other product
files, Core contracts/sanitizer, Memory snapshot models, retrieval and maintenance
helpers, Chat mandatory/optional protocols and turn processor, Transcript source,
models/stores/exporters, MCP/Runtime/Agent packages, configuration, dependencies and
lock remain frozen. Stop for an exact amendment if another implementation path is
needed. Preserve all historical authority/review/builder evidence and the five
unrelated paths/fingerprints: .DS_Store, deleted family-tree.md, docker-bench-security,
Chat config backup and Sandbox audit Dockerfile. Do not clean user/runtime state.

## VAL014-F01 — Medium: Owned Public Interaction Retry

The production Memory adapter omits the ingester's optional owned record ID.
Persisting the same checked completed interaction again creates another pending
UUID, then SQLite rejects the duplicate entry. The first committed snapshot and
single immutable transcript remain truthful, but the retry embeds/writes another
record and reports failure. Independent checkout and isolated-distribution
reproducers both exit 1. Lower-level explicit-ID tests do not cover this public
path. This violates MCP-06-04's "Reuse owned IDs on retries" and WS06-AC05.

Required correction:

- Establish and reuse the owned record identity for the same actual entry/call
  through the production public preparation/coordinator path. Repeated successful
  retries must return the original correlated facts without additional embedding,
  semantic records or fabricated capture/freshness. Do not hash raw arguments or
  results, reconstruct discarded data, or add configuration/schema/dependencies.
- Verify and reuse a matching immutable transcript receipt through public store
  readback. Compare the complete relevant safe interaction and paired call/result
  content, ownership and correlations. Reject a conflicting same-entry/call retry
  with fixed safe diagnostics; do not overwrite the original entry or provenance,
  mistake an unrelated/native record for owned memory, or weaken pairing guards.
- Cover false append with no committed entry, ambiguous failure after a successful
  append, readback/receipt failure, publication failure, cancellation and concurrent
  retries. Keep pending records excluded until a matching actual durable receipt
  is verified. Preserve a record named by an immutable receipt even if publication
  fails. Do not let a failed competing retry delete another operation's owned
  pending or committed record. Own and await all operations; cancellation propagates.
- Handle mixed native/MCP calls and repeated tool names using actual per-call IDs;
  no tool re-execution or new native identifiers. Preserve default zero semantic
  writes, exact grants, separate sanitation/caps, labels, freshness, maintenance,
  WS-04 budgets, legacy/custom adapters and native-only persistence behavior.

Do not add automatic crash recovery, cleanup of historical orphan records,
transcript rewrites, global taint tracking, a new registry/database, live refresh,
revocation or neighboring refactors. Any schema, public contract or source-path
expansion is a stop condition requiring reconciliation.

## Acceptance Criteria

| ID | Required independent evidence |
| --- | --- |
| REM008-AC01 | Public real-Chroma/SQLite retries after success reuse the exact owned record/receipt and returned paired facts, with one entry/record and no extra embeddings, including mixed/repeated-name calls. |
| REM008-AC02 | False append, ambiguous post-append/readback failure, publication failure and cancellation retries remain truthful, preserve owned IDs and immutable data, and cannot publish unreceipted records or delete another retry's ownership. |
| REM008-AC03 | Conflicting same-entry/call payload/provenance/policy and unrelated/native-ID collisions fail closed without overwrite, new retrievable data or unsafe diagnostics; concurrent matching retries settle safely. |
| REM008-AC04 | Original WS-06 ten criteria, accepted predecessors/defaults/native behavior and exact nine-path scope remain intact; meaningful typing, full checks, distribution proof, cleanup and frozen/unrelated preservation are complete. |
| REM008-AC05 | A newly frozen candidate is handed to the maintainer with reproducible remediation-delta and original WS-06 aggregate evidence; only subsequent validation can close the finding. |

## Verification And Reporting

Run focused retry regressions first using public production adapters, temporary
Chroma and SQLite, deterministic embeddings and synthetic local stdio peers. Include
the two original VAL-014 reproducers as reproducible regression evidence and extend
them for every failure/concurrency/ownership boundary above. Count embeddings and
records directly and inspect complete immutable receipts and all returned facts.

Run all 16 commands in the original [VAL-014 request](../validation/VAL-014-request.yaml)
against the new candidate. Replace only its old aggregate whitespace endpoints
with original base `99bde5148ee21f47d4734d2a026fb198a3d19cbd` and the new candidate;
add an exact remediation-base-to-candidate delta whitespace/scope check. Meaningful
unfiltered Python-3.13 typing must cover all nine original affected sources, including
all four remediated sources. Preserve nonzero baseline outcomes without filtering
new errors. Required focused/full/compatibility/Ruff/typing/lock/board/docs checks
remain distinct from independent public and packaging evidence.

Independently rebuild current declared framework distributions offline and repeat
the original checkout and fresh isolated declared-distribution retry proofs, plus
production Chroma/SQLite/provenance/export and public safety/budget/cleanup probes.
No editable source or source-PYTHONPATH masking in the isolated proof. Retain clean
resolver/cache limitations separately. The maintainer-reserved validation gate
later establishes its own independent base/freeze conclusions.
No providers, paid calls, external MCP endpoints, real credentials or delivery.

Do not dispatch a formal independent validator in this execution turn: the
maintainer explicitly reserved validation. The implementation report and handoff
must distinguish remediator checks from a validation verdict. A fresh VAL-015
remains a separate potential review gate if the maintainer directs it later.

The new remediation report records the exact source/test candidate/base, finding
and five remediation/ten original criterion mappings, all commands/outputs/exits,
retry/partial-publication semantics, isolated proof, cleanup and preservation.
Reconcile the old implementation report's public retry limitation by reference;
leave that reviewed historical report byte-exact. Archive original new evidence
losslessly as separate controller metadata. Do not describe helper-only reuse as
production idempotency or silently omit failed harness/build attempts.

After a stable candidate, mark VAL-014 superseded only for decisions on that
changed candidate and retain its complete historical bytes. Hand the exact
remediation delta and original WS-06 aggregate, full checks and freeze evidence
to the maintainer for validation. The remediator does not validate its own work.
A VERIFIED outcome permits a WS-06 closeout proposal, followed by explicit
maintainer acceptance. The wider initiative remains started and local.

Stop for missing bounded approval/start/separate assignment, authority conflict,
outside-path requirements, lost ownership, unsafe publication, changed-source
failures, unclassified regressions, incomplete evidence or any external-effect need.
