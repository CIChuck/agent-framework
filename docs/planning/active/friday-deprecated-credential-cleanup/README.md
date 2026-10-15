# Deprecated credential-bearing artifact removal

Status: started. Implementation authority: granted for the bounded repository-removal unit.
execution_phase: implementation; validation_state: not_ready.

Chuck Russell requested deletion of the deprecated credential-bearing files and
revocation/replacement of previously used keys. The exact statement and four-path
construction scope are in [authority.json](authority.json) and
[CD-SEC-001](directives/CD-SEC-001-remove-deprecated-credential-artifacts.md).

The active compatibility suite now uses its existing sanitized fixture as the
option-shape baseline. The comparison between that fixture and the retiring
original was removed. The current
Chat application and shipped examples remain unchanged. The deprecated standalone
script's default config is intentionally retired under the maintainer's direction.

The normal board next command still selects queued Langfuse. This explicit current
maintainer security instruction selects this bounded task without changing any
other task's priority or implementation authority.

Credential revocation and replacement are a separate external work unit. No
provider-management sessions or account identifiers are available. The maintainer has confirmed rotation and retirement; see
[confirmation](credential-rotation-confirmation.json). No issuer-side validation
was performed. History rewriting and public delivery are outside this unit.

Bounded removal independently VERIFIED at a65f1366.
Next gate: provider rotation and old-key invalidation confirmation, then maintainer
acceptance. Local commit only; no publication. See [review](validation/VAL-SEC-001/report.md).

SEC-002: current explicit instruction authorizes replacing the deprecated command
reference under [CD-SEC-002](directives/CD-SEC-002-retire-legacy-command-reference.md).
SEC-002 independently VERIFIED at e5a3066c. Both command parity tests use the
frozen fixture and pass with the deprecated folder unavailable in the private
checkout. See [review](validation/sec002-review/report.md).
Next gate: confirm provider rotation/revocation; maintainer acceptance and local
delivery remain separate. No deprecated directory was deleted.

SEC-003: authorized Git untracking and whole-folder ignore rule; all local files
must remain intact. Next gate: SEC-003 verification and independent review.
