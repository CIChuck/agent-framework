# REM-TUI-N01B-01-01: first-candidate documentation reconciliation

**Status:** Bounded remediation of historical
[CHANGES_REQUESTED review](../validation/VAL-N01B-01-preflight-7e5241c8.md).

**Candidate under review:** `7e5241c8611c41475b7730ff84005c4bb7561dd6`.

**Controlling authority:** Maintainer-approved
[CD-TUI-N01B-01](../directives/CD-TUI-N01B-01-neutral-transcript-query-contracts.md)
permits scoped TUI packet/evidence and board/dashboard updates. The repository
[independent-validation policy](../../../../reference/policies/independent-validation-policy.md)
requires a bounded remediation directive and a fresh review of any revised
candidate. Both findings are mechanical documentation/evidence corrections
within that preauthorized scope. No new product-code authority is claimed.

| Finding | Exact correction | Verification and acceptance |
| --- | --- | --- |
| N01B01-01 | Edit only `replacement-plan.md` status/authority header and §5 current construction gate. Record N01A's independently VERIFIED closeout, approved N01B-01 and its first-candidate review/remediation, while keeping later product units design-only. | Compare header and §5 with the approved directive, authority manifest and board; board validation, dashboard check, changed-document links and `git diff --check` pass. |
| N01B01-02 | Edit only `validation/N01B-01-local-checks.md` to include exact before/after test, static, wheel-build and isolated-install command lines and environment/loopback conditions. | Every directive item 4 local command and result can be reproduced or traced to a stated runner limit; command/result counts agree with recorded evidence. |

Permitted supporting evidence/state updates are this directive, the historical
review report, TUI packet index/execution log/authority manifest, scoped TUI
board event/validation entry and generated dashboard. No source, tests,
package metadata, lock, workflow, CLI, TUI implementation, external service
or existing user state may change in remediation. Do not opportunistically
revise other design sections or soften the findings.

After the corrections, freeze a new commit and request a **fresh-context,
read-only** delta review of both findings plus the complete revised candidate
against the approved construction directive. Keep the first review as
historical evidence; it is not a pass. If a required change crosses this
document-only scope or the second candidate fails, stop and reassess the
remediation authority before editing further.
