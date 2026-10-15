# Deprecated credential-bearing artifact removal

Status: started. Implementation authority: granted for authorized bounded units.
execution_phase: closeout; validation_state: verified.

Current branch: security/remove-deprecated-credentials; delivery: local only.

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

Next gate: maintainer acceptance and delivery decision for the bounded cleanup.
No local data deletion, push, merge or publication is inferred.
