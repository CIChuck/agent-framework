# Deprecated credential-bearing artifact removal

Status: started. Implementation authority: granted for the bounded repository-removal unit.
execution_phase: closeout; validation_state: verified.

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
provider-management sessions or account identifiers are available. Issuer-side
rotation remains pending and must not be reported complete from file deletion or
a passing scanner. History rewriting and public delivery are outside this unit.

Bounded removal independently VERIFIED at a65f1366.
Next gate: provider rotation and old-key invalidation confirmation, then maintainer
acceptance. Local commit only; no publication. See [review](validation/VAL-SEC-001/report.md).
