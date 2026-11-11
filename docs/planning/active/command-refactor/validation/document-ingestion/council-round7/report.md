# INGEST compatibility cycle — pass2/4, global round7

Outcome: **CHANGES_REQUESTED**, candidate `f1916747`; threshold not met.

| Seat | Outcome | Coverage | Overall |
| --- | --- | --- | --- |
| Sol | CHANGES_REQUESTED | 9.4 | 9.3 |
| Astra | CHANGES_REQUESTED | 9.1 | 9.0 |
| Opus | CHANGES_REQUESTED | 8.8 | 8.5 |

Five source-confirmed correction themes: async absent-vector fallback versus
sync zero contribution; existing pending-record retention/retry; the real closed
telemetry reason boundary; 35 overwritten historical gate lines; and public
backup layout/member completeness. Nine advisories are mapped to narrow proof
and scope clarifications. Proposed document corrections receive a fresh pass3;
no source-only finding becomes implementation closure.

Readable [Sol](sol-report.md), [Astra](astra-report.md) and [Opus](opus-report.md)
reports normalize whitespace only; adjacent `.md.gz` files preserve exact raw
bytes. [Reconciliation](reconciliation.json) records both hashes, scores and
remaining budget. All opening/closing protected checks and five admin checks
passed per seat; no product/runtime/model/store proof was executed. The later
maintainer scope question limits MCP/backups to causal compatibility adaptations;
new physical layouts/defaults and cleanup/consistency repairs are excluded.

Pass3/4 is next, then at most ONE further correction/review pass. Each seat must
independently VERIFIED with zero mandatory findings and coverage/overall >=9.5.
After pass4 stop for maintainer guidance if the gate is unmet. No Gate-A,
construction, MAINT acceptance, personal-store operation or delivery follows.
