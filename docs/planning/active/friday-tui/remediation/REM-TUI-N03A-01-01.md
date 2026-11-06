# REM-TUI-N03A-01-01: current packet-state reconciliation

**Status:** Bounded documentation remediation of
[N03A01-VAL-01](../validation/VAL-N03A-01-first-f921eb4c.md). The original
candidate `f921eb4c380822879363f8331d54438ce7048640` and its independent
`CHANGES_REQUESTED` verdict remain historical evidence.

Chuck Russell approved exact [CD-TUI-N03A-01](../directives/CD-TUI-N03A-01-installable-shell.md)
with scoped TUI planning/evidence. The [independent-validation
policy](../../../../reference/policies/independent-validation-policy.md)
requires a bounded remediation directive and fresh review. This current-state
correction is within the approved documentation scope; it authorizes no new
product or test code and no external delivery.

| Finding | Exact correction | Verification |
| --- | --- | --- |
| N03A01-VAL-01 | Replace current claims in the packet `README.md`, `replacement-plan.md` and `screen-layout.md` that N03A-01 is proposed/unapproved or no TUI shell exists. Point to the approved directive and local check report. Align `execution_phase: validation` and `validation_state: pending` in the packet index, authority and execution log while a corrected candidate awaits fresh review. Set the board next gate to fresh review plus still-open physical UAT; retain the first verdict as historical evidence. | Board validation/dashboard, duplicate-key authority JSON parse, changed-document local links, exact changed paths and whitespace pass. A fresh independent reviewer checks the corrected delta and original full candidate. |

Allowed correction paths are this remediation record, the first-review
report, the TUI packet `README.md`, `replacement-plan.md`, `screen-layout.md`,
`authority.json`, `execution-log.md`, the scoped TUI board task/events and
generated dashboard. Existing package source, tests, metadata, lock, CLI,
runtime, workflows and user guides remain frozen. If any correction requires
another path or behavioral change, stop and reassess authority first.

N03A01-VAL-02 remains open. Do not call the shell milestone complete without
hands-on macOS terminal evidence for physical keys, pointer, resize, visual
layout and restoration. After the status correction, commit a new stable
candidate and request fresh-context read-only review; do not treat the first
verdict as `VERIFIED`.
