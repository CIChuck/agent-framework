# MCP-WS-03 Work-Unit Closeout

Date: 2026-09-28
Status: Independently verified and explicitly accepted
Initiative: `friday-mcp`
Work unit: `MCP-WS-03`
Branch: `feature/friday-mcp-ws03-registry`
Current candidate: `d395acdba9e233cb226f54e6258575f480157cf1`
Work-unit base: `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641`
WS-03 approval/start: `b54069654bb3e21a6265fbabcd23f6991e286ab0`
REM-005 authorization/bounded base: `215e54de71eda08067d22695d0062f7bed35e9d0`
Accepted WS-02 product predecessor: `a257f041d1d68f8aea2f5b9773df1b88acd82379`
Accepted by: repository maintainer
Accepted at: 2026-09-28
Acceptance evidence: Explicit maintainer message "accepted - Summarize WS-03."
after review of the independently verified closeout in the active conversation
Delivery: Local

## Scope And Result

Approved WS-03 implements executable runtime MCP registration, exact original
multi-peer routing, pre-filter collisions, typed metadata, strict filters and
includes, bounded schema sanitation, complete final-export cost caps,
transactional publication and owned public cleanup before binding validation.
REM-005 corrects only historical VAL-008 F-001: additive typed bounded first/
second collision descriptors retained after failed public startup cleanup.
It changed exactly the eight approved source/test/fixture/report paths.

Fresh-context read-only [VAL-009](../validation/VAL-009-report.md) returned
`VERIFIED` for the REM-005 delta, complete original WS-03 aggregate and overall
gate, with no findings. All six remediation and ten work-unit criteria passed.
Both F-001 public variants were independently reproduced after failed startup
cleanup: MCP/MCP retains distinct first/second safe source summaries; MCP/native
retains explicit provider identity and preserves all native registry objects.
The unchanged historical report is superseded only for current decisions.

Independent commands: 173 focused, 459 affected aggregate and 46 Chat tests
passed (overlapping suites; counts are not additive). Native tools returned
233 passes plus the same two invalid-ZIP fixture failures; broad integration
returned 69 passes plus the same board-count assertion failure. All seventeen
required commands ran. Ruff and affected 45-file Python 3.13 typing passed;
required default/core-inclusive typing failures were independently reproduced
at the accepted predecessor. Twelve required commands exited zero; the five
baseline failures retain their original exits and are not passing checks.

Twenty-six independently executed groups passed, covering both-source privacy,
full-original bounded fingerprints and immutable history, actual two-peer native
registry routing, sidecar costs, schema/filter/cap boundaries, publication before
bindings, transaction failures/cancellation, retained public owners and noisy
stdio settlement. Assertions of public cleanup precede defensive fixture
teardown. A deliberately failing scratch assertion separately verifies fixture
settlement without being counted as public cleanup success. No production
cleanup budget or network/live-provider behavior was changed or substituted.

The complete report has SHA256
`69fc9a1355e1de082396fc5259064f9c88976d25f57dd518126bac414dece05a`.
[Evidence manifest](../validation/VAL-009-evidence.yaml) records all 73 original
reviewer artifacts in a deterministic lossless archive, including exact commands,
logs, probes, complete three-range diffs, machine-readable results and freeze
snapshots. Restoring its sibling layout exposes each exact named artifact.

## Authority And Stability

[VAL-009 request](../validation/VAL-009-request.yaml) pins the candidate,
previous/full delta, bounded correction and complete original WS-03 aggregate,
twenty-two authority hashes, both implementation-report hashes, six remediation
and ten work-unit criteria, seventeen required commands and local independent
probe obligations. New reviewer `/root/mcp_ws03_val009` had no inherited
controller/builder/remediator conversation and remained read-only in the governed workspace. Formal start and
closeout match all 22 authorities, both reports, unchanged request, 968 tracked
product/config files and five unrelated paths (60 existing files plus preserved
`family-tree.md` deletion). The report records identity/model availability/date.

Historical [VAL-008](../validation/VAL-008-report.md) remains byte-exact and is
superseded for current-candidate decisions only in a separate status record.
Frozen candidate and reviewed authority/report stability are reported by the
independent validator at start and closeout. Unrelated local changes remain
preserved; delivery remains local.

## Compatibility And Residual Gates

Collision prevention, ordinary constructors/binding reasons/counters,
normalizer, native mandatory protocols, filters/caps/sanitizer and production
cleanup budgets remain compatible. New `decision.collision` is optional and
typed; strict diagnostic serialization consumers must allow the additive field.
Summaries expose bounded shape/length/fingerprints, not raw original names.
Evidence is last-attempt in-memory history, not a persistent audit log or
background refresh. Native schema exports remain mutable to trusted callers
under approved scope; hashes and sanitizer checks do not promise universal
injection protection or a hard shutdown SLA.

Declared unchanged NumPy/default-target syntax, four core profiles.py errors,
integration board-count assertion and native invalid-zip fixtures remain
explicit unresolved baseline debt; no repair or waiver is made by this closeout.
New candidate failures cannot be relabeled baseline debt.

The maintainer accepted this verified WS-03 work unit on 2026-09-28. The wider
initiative remains started/normal/local. WS-04 and later workstreams, complete
feature-branch aggregate pre-merge review, live interoperability/app UAT and
delivery actions remain separate gates. The active initiative packet remains
in place because this is work-unit acceptance, not initiative completion.

## Maintainer Acceptance

Acceptance: explicitly recorded for candidate
`d395acdba9e233cb226f54e6258575f480157cf1` and complete fresh VAL-009 verification.
The maintainer said "accepted - Summarize WS-03." after the verified closeout
and explicit acceptance gate were presented. This decision accepts WS-03 only.

Next gate: reconcile the WS-04 directive and readiness before requesting bounded
approval. WS-04 implementation remains unapproved; no later-slice or delivery
authority is inferred from this acceptance.
