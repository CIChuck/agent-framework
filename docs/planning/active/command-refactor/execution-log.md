# Shared command refactor — execution log

2026-10-24: The maintainer accepted the separate project scope, requested
activation, and directed all command-refactor planning documents to the
`docs/planning/active/command-refactor/` packet. The dedicated
`feature/command-refactor` branch was initially created from `e591f720`. The packet,
five Markdown source documents and JSON command inventory were relocated;
links and board references are being reconciled as one planning transition.

2026-10-24: The maintainer directed independent branches, command execution
first, and a TUI development hold until the command refactor is completed,
tested, and accepted. The command branch was rebuilt directly from `master`
`c3426986`. Its former stacked tip is retained at
`backup/command-refactor-stacked-20261024`; the TUI branch and its uncommitted
work were not rewritten. See the [branch isolation record](branch-isolation.md).

2026-10-24: Documentation review established a [scope decision register](scope-decisions.md)
and [phase plan](phase-plan.md), clarified the planning chain in the packet
index, marked the older seven-name recommendation as superseded and separated
the six retirement cases from retained-command parity obligations in the JSON
inventory. Technical contract, retired-name response and scored outliers remain
open; this documentation pass does not advance a construction gate.

2026-10-24: The maintainer clarified that `command_refactor.md`,
`command-inventory.md` and `command-matrix.md` are the canonical intent sources
for this feature branch and ultimate build plan. The packet index, build plan,
scope register, phase plan and tactical-plan derivation were aligned to that
source order. Candidate recommendations remain distinct from accepted
decisions.

2026-10-24: After reviewing phase-plan sufficiency, the maintainer authorized
a revision to measurable gates. P0 now requires a PAR evidence ledger; P1
must fix contract choices, unit ownership, retirement order, interaction
scenarios and supported environments; P2–P3 require cumulative unit evidence;
P4 covers cross-family installed integration; P5 requires an aggregate report,
independent review, acceptance and a TUI handoff manifest. This revision does
not close P0/P1 or authorize product source edits.

2026-10-24: The maintainer requested a concrete architectural surface for the
shared command owner. The [architecture proposal](shared-command-architecture.md)
now maps proposed package ownership, Chat-owned service seams, the separate
`friday-framework-cli` registry and installed-client reuse proof. Package/API
and service-ownership choices remain P1 decisions; no product code changed.

`execution_phase: planning`; `validation_state: not_ready`.

Next: characterize Chat and `friday-framework-cli`, settle the supported
surface and shared contract, then request exact construction-directive approval.
