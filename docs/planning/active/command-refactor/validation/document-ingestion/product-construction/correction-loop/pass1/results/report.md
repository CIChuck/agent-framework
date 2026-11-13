# INGEST product directive — additional pass1/3 reconciliation

**CHANGES_REQUESTED; all-seat9.5 gate unmet.** Frozen candidate `af4e12bd`.

| Seat | Outcome | Coverage | Overall |
| --- | --- | ---: | ---: |
| Sol | VERIFIED, bounded document only | 9.3 | 9.3 |
| Astra | CHANGES_REQUESTED | 9.1 | 9.2 |
| Opus | CHANGES_REQUESTED | 8.6 | 8.9 |

[Sol](sol/report.md), [Astra](astra/report.md) and [Opus](opus/report.md) retain
their original reports, scores, limits and evidence attribution. Opus's on-disk
file was a short summary; its full terminal report is captured verbatim as the
formal report here, with its original summary preserved separately. No missing
reviewer scripts or executions are invented.

Four bounded correction groups remain: DI22's complete role/storage matrix must
join I3; the fixture inventory must cover omitted retained oracle files; current
criteria must drop stale round2 restrictions; branch-handoff current routing must
match the new cap. The independent source-backed findings remain even where
other seats did not identify them or used advisory severity. Existing mandatory
Q01–07 corrections are supported, with the DI22 residual explicitly retained.

Related advisories clarify CLI origin tests, I1 intermediate compatibility and
the I1 lock delta. All reviewers reported source-depth limits; partial parent
reading is not a complete bounded document assessment. Original scores are not
raised or averaged. [Machine reconciliation](reconciliation.json) records scope,
disagreements, corrections and remaining budget.

All seven admin checks and all reviewer/controller boundaries pass. Historical
experiments were inspected/hash-verified, not rerun. Product, dependencies, user
configuration and state remain unchanged. Known debt stays failed/unwaived.

One additional pass is complete; two remain under the current authorization.
The controller proceeds with bounded document corrections and a fresh full pass2.
No Q/Gate-A closure, construction, UAT, acceptance or delivery authority follows.
