# Foundation design approval request

Date: 2026-11-04
Decision ID: CMD-DESIGN-001
Status: AWAITING MAINTAINER DECISION — approval not recorded
Maintainer: Chuck Russell
Reviewed candidate: `0124d14bb8e91091d35eb73c09f6640e6f558289`

## Decision requested

Approve the foundation design and verification criteria in the
[shared API draft](../shared-command-api.md), limited to API-01–API-06 and the
foundation types/registry semantics. This is the first design approval, not
approval of the complete shared-command implementation contract.

The [independent review](../validation/VAL-CMD-ARCH-001-report.md) returned
**VERIFIED for design approval readiness**, with no mandatory findings. Its
optional multi-slash parser-fixture advice is retained for future test planning.

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

## Reviewed artifact identity

- `shared-command-api.md` SHA-256: `ffa20519db96115fe3e5c169dd09dc2e684fa43ec3c944c0b4112264100c7fcc`
- `directives/CD-CMD-FND-001-neutral-foundation.md` SHA-256: `96119a2a4872b4b98d1ad52d3c7b81b8a534841c6682aa239b2604e7634a898c`

These reviewed artifact bytes remain unchanged. The report and this request are
post-review closeout metadata, not a modification of the reviewed design.

## Approval record

No approval has been recorded. A maintainer answer should identify
`CMD-DESIGN-001` and either approve this limited foundation design or state the
requested changes. The controller records the answer and date afterward.
