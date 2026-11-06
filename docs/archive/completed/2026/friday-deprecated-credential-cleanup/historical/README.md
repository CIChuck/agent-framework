# Deprecated credential-bearing artifact removal

Status: started. Implementation authority: granted for authorized bounded units.
execution_phase: closeout; validation_state: verified.

Delivery branch: security/remove-deprecated-credentials (remote deleted).
Delivery: merged into master through [PR #9](https://github.com/CIChuck/agent-framework/pull/9)
at 2026-10-15T01:55:15Z, merge a2dd82be951aaa1bb15dc4cc1f5753f14727f8ad.
[GitHub delivery evidence](delivery-evidence.json) records the merge and branch check.

- SEC-001: two credential-bearing artifacts retired and config compatibility
  reference migrated. [Review](validation/VAL-SEC-001/report.md). Original review
  bytes preserved alongside the corrected link presentation.
- SEC-002: command parity uses an independent frozen 52-name fixture.
  [Review](validation/sec002-review/report.md).
- SEC-003: all 287 deprecated integration memory files untracked; the whole folder
  is ignored and every local file retained. [Review](validation/sec003-review/report.md).

Credential rotation and old-key retirement are [maintainer-confirmed](credential-rotation-confirmation.json).
No issuer-side checks were performed. Historical credential copies and additional
tracked artifacts outside the deprecated subtree were not rewritten or sanitized.

The current user instructions selected these bounded security units without
changing other tasks' priorities or granting Langfuse implementation authority.
Original authorities/directives and prior evidence remain retained in this packet.

Next gate: maintainer lifecycle closeout/acceptance for the bounded cleanup.
Delivery is evidenced separately; no maintainer acceptance or history rewrite is inferred.

SEC-004: maintainer requested publication of all intentional pending workspace
changes. Aggregate independently VERIFIED at 526688e3; see [full review](validation/sec004-aggregate/report.md).
PR #9 delivery and remote branch deletion are now independently confirmed in
[delivery evidence](delivery-evidence.json). The prior aggregate review's known
baseline failures and evidence-only Ruff style debt remain disclosed; this
recording step does not change its frozen source or verification limits.
