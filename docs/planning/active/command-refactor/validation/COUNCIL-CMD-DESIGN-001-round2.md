# CMD-DESIGN-001 — Sol-only council, round 2

Date: 2026-11-05
Reviewed candidate: `c9c159226ff74158e182ff1b28f8599db5f900b9`
Council outcome: CHANGES_REQUESTED — one remaining documentation instruction
Scope: limited foundation design approval readiness, AP-01–AP-06

| Reviewer | Verdict | Advisory score |
| --- | --- | --- |
| GPT-6.1 Sol | CHANGES_REQUESTED | 8.8/10 |
| GPT-6 Sol | VERIFIED | 9/10 |
| GPT-5.6 Sol | VERIFIED | 9.5/10 |

All three confirmed the runtime-invariant and canonicalization corrections.
GPT-6.1 Sol found R2-SOL1-ARCH-001 (low): the pruning review still described the
former six-name subset as current replacement guidance, despite superseding the
old seven-name proposal. The other reviewers considered historical labeling
sufficient. The controller accepts the concrete leftover wording as a correction;
positive votes do not override a mandatory finding.

The reviewers verified all 22 new manifest pins and supplied API/approval/directive
hashes, unchanged candidate and dirty inputs, board validation (36 tasks),
documentation lifecycle (685 files) and whitespace checks. No product tests,
builds, installs or live-provider effects were performed. Scores are advisory.
Full reports are available in their returned delegated threads in the parent
conversation. The round did not grant design approval, P0/P1 closure or source
authority.

## Bounded residual correction after all reviewers completed

Under the maintainer's existing authorization to resolve SOL3-ARCH-003, the
controller corrected only `command-pruning-review.md`: current scope now lists
all nine removals and the 41/3 target; the earlier recommendation/migration-message
sections are explicitly historical and superseded. Original candidate tables,
raw scoring and receipts were preserved. The public API, construction directive
and approval artifact bytes were not changed by this correction.

This is controller remediation, not an independently VERIFIED revised candidate.
The council verdict above remains attached to c9c15922. No new delegate/council was
automatically started for this small wording correction. A future review must
use the corrected file's new pin and exact candidate rather than inherit a prior
verdict. The optional slash-retaining-key fixture suggestion is retained as
implementation-test advice; no further API expansion was made.

## Remaining boundary

Freeze the corrected wording and review evidence. Obtain any required fresh
scoped confirmation before returning CMD-DESIGN-001 for maintainer design approval.
Construction, future family contracts, installed-client proof and remaining
P0/P1 work remain separately gated. No design approval is recorded.

[Residual correction pins](pruning-wording-correction.json) identify the changed
pruning document and unchanged core artifacts for any scoped confirmation.
