# TELEM-02 accepted: owned OTel adapter and factory lifecycle

Status: accepted work unit. Initiative: friday-telemetry-rewire.
Accepted by: repository maintainer Chuck Russell.
Accepted at: 2026-10-06, America/New_York.
Acceptance evidence: explicit conversation response **"accepted"**, following
TELEM-02 independent VERIFIED and the stated acceptance gate.

The accepted product is `45f3114173a7e9ada128c7950fe1f7e63cb2ff28`, under CD-002
and approved A02. Evidence-only closeout is `10857936715f82049490e2f0e52671df3075e680`.
Independent VAL-007 reviews the full unit and complete aggregate from
`2155a0fc51f5b20dea4e35c6cfc70f1d52002735`, with no numbered findings.

- [Independent VERIFIED report](../../../../planning/active/friday-telemetry-rewire/validation/VAL-007/report.md).
- [Independent evidence](../../../../planning/active/friday-telemetry-rewire/validation/VAL-007/evidence.json).
- [Builder evidence](../../../../planning/active/friday-telemetry-rewire/execution/TELEM-02-final/report.md).
- [Exact acceptance and evidence hashes](acceptance-evidence.json).
- [Continuing initiative](../../../../planning/active/friday-telemetry-rewire/README.md).

Accepted behavior includes provider-neutral programmatic disabled/debug/OTel
construction, provider-owned SDK context/parent/event semantics, bounded scalar
validation, owned processor/exporter lifecycle and fixed native retry disablement.
Caller-owned Chat injection remains unchanged. Actual SDK/protobuf/console,
concurrency/privacy/cleanup and both exact synthetic loopback collector tests passed.
Root2,891, Chat+Telemetry828 and owning-tree2,873 tests passed, with only unchanged
optional/live skips. Changed-file lint and typing passed. Root Ruff remained raw
exit1 with exactly327 findings under the separately approved WVR-004 disposition.

WVR-004 expires after this acceptance under its existing terms. Its exact historical
scope and reviewed authority remain immutable; it is not renewed for later units.
REM-004-HIST-01 and REM-004-GENERIC-01 remain maintainer-owned policy follow-ups.

This archive records TELEM-02 acceptance only. The continuing initiative remains
started/local for TELEM-03 through TELEM-05. Its frozen authority, reports and raw
receipts remain at their existing paths and hashes. Next is preparation of the
TELEM-03 safe LLM metrics/role-service injection construction directive; that unit's
implementation requires its own approval. Remote/TLS/vendor activation and delivery
remain separate gates. No product source, dependency, configuration, push, merge,
release or deployment change is made by this acceptance record.
