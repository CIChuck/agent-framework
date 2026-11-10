# INGEST-001 final design council — round4 reconciliation

**VERIFIED — the maintainer's all-seat score gate is met.** No mandatory finding.

| Reviewer | Final outcome | Independent score | Advisory findings |
| --- | --- | ---: | ---: |
| [GPT-6.1 Sol](sol-report.md) | VERIFIED | 9.6/10 | 0 |
| [GPT-6 Astra](astra-report.md) | VERIFIED | 9.6/10 | 0 |
| [Claude Opus5.5](opus-report.md) | VERIFIED | 9.5/10 | 6 nonblocking |

All three independently pass all30 criteria on candidate
`728cba77e816e5618a06262dd4aa1cbc6e50a376`, branch `feature/cmd-ingest-001`.
Correction base: `36362be514ef387183a27d930cd41a8799e3d714`.
The corrected delta was reviewed first, then the full bounded REM and Tools
companion, retained decisions and current source feasibility. This is design
readiness only, not implementation or selected-release readiness.

## Disposition and boundaries

Both last mandatory requirements are independently closed at design level:
typed Memory-v2/Chat aggregate-v2 model/loader/consumer handoff and distinct
fingerprints; exact explicit-origin/default/graph/WAL fresh-creation eligibility.
All retained IR-01..16, IR-R01..08, IR-S01..04 and IR-F01/F02 pass.
Raw per-criterion outcomes and report/receipt hashes are in
[reconciliation.json](reconciliation.json). Scores are not averaged or rounded.

Opus's six advisories concern fingerprint timing, recovery/log-root reuse,
nested artifact versions, actual Runtime path effects, template origin and
pre-upgrade interrupted recovery guidance. They are nonblocking and carried to
the [Gate-A/directive handoff](../gate-a-handoff.md). They are not asserted closed.
The reviewed REM and companion remain byte-identical to this candidate; this
controller bookkeeping does not silently revise their technical contract.

## Identity, conduct and evidence

The [request](review-request.json) hash is
`0601d7c1f2db634e6efe20fd96aa38ea80539e129fdb0e1ecab3d5afe18c7c1c`.
Original absolute input paths are preserved; compressed manifest decompression
restores the exact original bytes. A later replay needs a newly bound request.
Raw reports are exact copies. All three start/end reports and the
[controller's last frozen audit](controller-frozen-integrity.json) pass for
17,606 protected entries, six metadata records, HEAD/branch, staging and status.
Logical index, measured before status:
`35a40c37ddfd7753db30f03eefd097ccee9c6f9ecbd5095f635f185e919dc280`.

The copied command logs have paired starts/ends (Sol10, Astra10, Opus9), with
required Git optional-lock and bytecode guards on every logged call. Reviewers
report no round4 Git/admin/isolation deviations. Plain source/scratch reads were
permitted by this round's precise rule; this is not an OS-wide process audit.
Prior procedural limitations and BLOCKED outcomes remain historical facts.

Administrative/integrity checks were executed independently; technical runtime
claims were assessed from source, not product execution. No runtime suites,
builds, installs, model/provider inference or stores ran in this design council.
Historical root Ruff534, collection conflict7196, seven legacy formatting
failures and MAINT oracle failures remain failed/unwaived background, not freshly
reproduced or fixed. No whole-repository-green claim follows.

## Review history and stop

| Seat | Round1 | Round2 | Round3 | Round4 |
| --- | --- | --- | --- | --- |
| Sol | CHANGES_REQUESTED8.1 | VERIFIED9.5 | VERIFIED9.6 | VERIFIED9.6 |
| Astra | CHANGES_REQUESTED8.5 | CHANGES_REQUESTED9.0 | CHANGES_REQUESTED9.2 | VERIFIED9.6 |
| Opus | CHANGES_REQUESTED7.3, conduct qualified | CHANGES_REQUESTED8.4, conduct qualified | BLOCKED; separate technical CHANGES_REQUESTED9.15 | VERIFIED9.5 |

Each historical result binds only to its own frozen candidate. The initial
round plus the three authorized additional rounds are complete. All current
council tasks are terminal; no fifth pass or replacement is launched.

**Next gate:** Review the VERIFIED INGEST design handoff and separately activate a bounded Gate-A effects envelope for isolated dependency/model/counter/format readiness. Freeze and approve the exact construction directive before product code. Six nonblocking advisories carry forward; MAINT human UAT/acceptance and delivery remain separate.

Gate A, construction approval, human acceptance and delivery remain ungranted.
