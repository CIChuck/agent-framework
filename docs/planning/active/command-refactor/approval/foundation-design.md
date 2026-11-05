# Foundation design approval request

Date: 2026-11-04
Revision: 2026-11-05 — council remediation; fresh review pending
Decision ID: CMD-DESIGN-001
Status: REVISED — awaiting fresh review before maintainer design decision
Maintainer: Chuck Russell
Prior council candidate: `fa94f180e95ba75022e81bb269b18543e6360e38`

## Decision requested

Approve the foundation design and verification criteria in the
[shared API draft](../shared-command-api.md), limited to API-01–API-06 and the
foundation types/registry semantics. This is the first design approval, not
approval of the complete shared-command implementation contract.

The earlier [independent review](../validation/VAL-CMD-ARCH-001-report.md)
covered the prior design. The later [Sol-only council round](../validation/COUNCIL-CMD-DESIGN-001-round1.md)
returned CHANGES_REQUESTED. On 2026-11-05 the maintainer authorized resolving its
three findings. Runtime validation, canonical metadata storage and retirement
instructions are now revised; the prior positive verdicts do not verify these
new bytes. A fresh review is required before requesting design approval again.
See the [bounded remediation record](../remediation/REM-CMD-DESIGN-001.md).

## What this approves

- A standard-library-only `friday_commands` foundation with no frontend imports.
- Immutable typed command metadata, requests, semantic data/errors, UI intents
  and dispatch outcomes with explicit runtime invariants.
- Atomic canonical/alias registration and current Chat whitespace/name parsing,
  including its existing behavior rather than new shell-style quoting.
- One awaited handler execution; no automatic retry, hidden I/O, UI execution
  or host exit mutation by the registry.
- Independent positive/negative fixtures, import boundaries and disposable
  installed-wheel verification specified by API-01–API-06.
- Generic CLI preservation as a separate registry/API; no speculative adapter.

The [foundation directive](../directives/CD-CMD-FND-001-neutral-foundation.md)
shows the eventual bounded implementation scope and checks. It remains **DRAFT**
and is included as review context; this design decision does not approve it for
execution. No default handlers, client wiring or command removals are included
in the foundation unit. The nine planned removals and `/tools` retention remain
as previously decided.

## What happens after this decision

If approved, record this foundation design baseline and continue remaining
P0/P1 case, capability, scenario, environment and unit-map work. Family method/
payload schemas, service relocation, installed-client baselines and progress/
cancellation semantics still need their own review. Freeze the exact execution
base and separately obtain construction-directive approval before product code.

If changes are requested, revise only the specified design decisions and obtain
fresh review of the changed candidate. No approval is inferred from silence.

## Revised artifact identity — fresh review pending

- `shared-command-api.md` SHA-256: `66b47b0e566dfb0e54db559a4e79077075e2430908aeef7cedbffe7ea4605f79`
- `directives/CD-CMD-FND-001-neutral-foundation.md` SHA-256: `648d3ce07cb338cf22ded7fd22229e03bba2551cc294457f3e9d753493ca358d`

These pins identify the corrected draft; they are not covered by the prior
review verdicts. The historical reports and manifest remain unchanged.

## Approval record

2026-11-05: Chuck Russell said “approved resolve them,” authorizing bounded
resolution of council findings. This is correction authority, not approval of
the revised design, a phase gate or product construction. No design approval is
recorded. After fresh review, the maintainer may approve CMD-DESIGN-001 or request
specific changes; the controller then records that separate decision and date.
