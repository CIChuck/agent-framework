# CHANGES_REQUESTED — CD-MCP-UP-003 / MCP-UP-03

Controller navigation cover. [Original independent report](artifacts/report.md.gz)
and [all original evidence hashes](stored-manifest.json) are immutable.

Candidate: `a897b3deaa9e007223c8ecbe7cfbfb4750ef10b7`; original report SHA256: `12fffb5c48bb0e1529cad29be47146d52004bd9c7e8aead381565a4aed6195ff`.

Sole finding **VAL-UP03-001 (Medium)**: new configuration guidance incorrectly
claims exact address permissions narrow default eligible public-address access.
The accepted policy adds exact address exceptions; configured ports constrain
ports separately. INT-AC-01..09 and the required checks pass; INT-AC-10 requires
accurate documentation before VERIFIED. Runtime behavior requires no change.

[Bounded explanation correction](../../remediation/REM-MCP-UP-003-guide-accuracy.md)
implements already-approved INT-AC-10 documentation accuracy in one original
product path, without new runtime/configuration/transport scope. New frozen
candidate and fresh independent review are required. Whole MCP stays started/local.
