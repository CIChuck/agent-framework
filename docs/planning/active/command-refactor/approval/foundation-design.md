# Foundation design approval — CMD-DESIGN-001

Date: 2026-11-04
Revision: 2026-11-06 — approval recorded; Step 3 subsequently resumed
Decision ID: CMD-DESIGN-001
Status: APPROVED — foundation design only; Step 3 readiness review resumed
Maintainer: Chuck Russell
Historical source council candidate: `fa94f180e95ba75022e81bb269b18543e6360e38`

## Approved decision

Chuck Russell approved the foundation design and verification criteria in the
[shared API draft](../shared-command-api.md), limited to API-01–API-06 and the
foundation types/registry semantics. This is the first design approval, not
approval of the complete shared-command implementation contract.

The earlier [independent review](../validation/VAL-CMD-ARCH-001-report.md)
covered the prior design. The later [Sol-only council round](../validation/COUNCIL-CMD-DESIGN-001-round1.md)
returned CHANGES_REQUESTED. On 2026-11-05 the maintainer authorized resolving its
three findings. Runtime validation, canonical metadata storage and retirement
instructions are now revised; the prior positive verdicts do not verify these
new bytes. The packet previously requested fresh review before presenting this
decision again. On 2026-11-06 the maintainer directly approved CMD-DESIGN-001.
That human decision is recorded below; no fresh independent review of the current
design is claimed, and no independent-review requirement is silently waived.
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

The foundation design baseline is now recorded, but the maintainer explicitly
paused before Step 3 of the approval sequence: resolving prerequisites for the
first implementation unit. The later explicit Step 3 resumption below lifts
that pause for readiness work only.
The remaining P0/P1 case, capability, scenario, environment and unit-map work
remains open. Family method/
payload schemas, service relocation, installed-client baselines and progress/
cancellation semantics still need their own review. Freeze the exact execution
base and separately obtain construction-directive approval before product code.

If changes are requested, revise only the specified design decisions and obtain
fresh review of the changed candidate. No approval is inferred from silence.

## Approved input identity

- `shared-command-api.md` SHA-256: `e5ba883fb246967320243e1dbc9c2a70fcf6189c05540a45961388f2b6466b74`
- `directives/CD-CMD-FND-001-neutral-foundation.md` SHA-256: `46a8027d416c39390563d8cd13f852f4cc7b29783fb04c39cbf38e71eb9db400`

The API pin identifies the exact document read for this approval; approval is
limited to API-01–API-06 and foundation types/registry semantics. It does not
approve the deferred portions of the file. The directive pin identifies draft
review context only; CD-CMD-FND-001 is not approved. These bytes are not covered
by prior independent verdicts. Historical reports and manifests remain unchanged.

## Approval record

2026-11-05: Chuck Russell said “approved resolve them,” authorizing bounded
resolution of council findings. This is correction authority, not approval of
the revised design, a phase gate or product construction. No design approval is
recorded by that earlier instruction.

2026-11-06: Chuck Russell stated:

> proceed. I have read and approved CMD-design-001. pause before, starting step 3 for review

Recorded decision: CMD-DESIGN-001 approved for the limited scope above. Stop before
Step 3 (prerequisite engineering/readiness work), pending maintainer review and
explicit resumption. This is not construction-directive approval, P0/P1 closure,
independent VERIFIED, feature acceptance or permission to push/merge.

Later on 2026-11-06, Chuck Russell instructed “Proceed to step three” and
requested a Claude Opus / OpenAI Sol / Google Gemini council to evaluate the
readiness review. Step 3 is resumed; Step 4 and construction remain unapproved.

## Current planning folder

The maintainer changed direction on 2026-11-05: current planning is consolidated
in `agent-framework` on `feature/command-refactor`. Only planning documents were
transferred. No source code was inspected, evaluated or changed. No design
approval or construction grant was recorded by that transfer. The later design
approval above is separate. Earlier folder/review statements are historical and
do not verify the changed planning authority.
