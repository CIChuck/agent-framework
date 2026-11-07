# Shared Friday command refactor — TUI effort, first phase

**Working-folder update — 2026-11-05:** The maintainer changed direction:
current command-first and Friday TUI planning is consolidated in the
`agent-framework` folder. Earlier TUI-folder directions are superseded for
current work. This transfer changes documents only; imported implementation
claims, reviews and test receipts retain their original provenance. No design
approval, construction authority or code validation is inferred.

**Working home:** `agent-framework`, branch `feature/command-retirement`.
**Board ID:** `friday-command-refactor`.
**Status:** CMD-FND-001 implemented, independently VERIFIED at `b4fc199e` and
accepted by Chuck Russell. Exact strengthened RET-001 is now approved and implemented locally; independently VERIFIED at `f896ef53` and accepted by Chuck Russell on 2026-11-07.
Exact foundation approvals and source base
`d003c4db` remain in the [approval record](approval/foundation-readiness.md).
See [independent result](validation/VAL-CMD-FND-001-report.md) and
[builder evidence](validation/CMD-FND-001-report.md). No command migration/wiring.
`execution_phase: planning`; `validation_state: not_ready` for PILOT-001.
RET-001 remains independently VERIFIED and accepted.
The corrected checkpoint is VERIFIED and merged through PR #13.
The foundation's VERIFIED result and acceptance remain separate completed evidence.

The maintainer changed the working home on 2026-11-05 to this Agent Framework
checkout; the shared command refactor remains the first phase. The full
packet is now local. Its separate logical contract, regression and acceptance
gates remain; TUI construction stays deferred until command-refactor acceptance.

[Reconciliation record](reconciliation/README.md) and [import manifest](reconciliation/import-manifest.json)
identify the source commit, preserved snapshots, protected drafts and baseline
differences. The old separate-checkout direction is superseded for current work.
Imported source-test results and review verdicts describe their original commit.
The later [direct foundation design approval](approval/foundation-design.md) is
recorded separately; the later exact foundation construction approval is in
[foundation readiness decisions](approval/foundation-readiness.md).

The recorded product decisions remain: nine complete removals, `/tools` retained,
41 canonical names/three aliases, shared neutral command ownership, preserved
generic CLI and retained-command quirks. Foundation API-01–API-06 is approved;
the complete contract and remaining P0/P1 work are still open. The approved
foundation is implemented and verified; later construction needs separate
authority. Current authority comes from this checkout's
AGENTS, policies, board and the maintainer's reconciliation instruction.

## Canonical planning chain

The three command documents below are the canonical product-intent sources for
this branch. Read them together when deriving or revising the build, phase or
tactical plans. A later plan may detail an accepted decision, but cannot
silently replace the intent, maintainer commentary or source baseline.

| Role | Canonical file | What it controls |
| --- | --- | --- |
| Authority | [Board](../../board.yaml) and [authority record](authority.json) | Task state, branch, current scope and the requirement for an exact approved construction directive before product code. |
| Feature intent | [Refactor discussion](command_refactor.md) | Why this branch exists, shared-owner and harness-evolution direction, migration sequence, protected behavior and maintainer clarifications. Candidate pruning and construction ideas remain proposals where labeled. |
| Maintainer priorities | [Command inventory](command-inventory.md) | Focus areas, command scores and comments, recorded command decisions, architecture opportunities and deferred consolidation ideas. Assistant recommendations remain advisory. |
| Command baseline | [Command matrix](command-matrix.md) and [JSON snapshot](validation/command-matrix.json) | The 50-name, three-alias before-change Chat surface and PAR case IDs, including the nine retirement cases; not a post-refactor target or parity result. |
| Reconciled scope | [Build plan](build-plan.md) and [scope decisions](scope-decisions.md) | The approved objective and current decisions derived from the three intent sources; open choices and deferred work stay explicit. |
| Contract input | [Shared-command architecture](shared-command-architecture.md) | Proposed ownership and dependency direction; package, API and CLI role still need explicit review and approval. |
| Evidence standard | [Test strategy](test-strategy.md) | Required regression classes for phases and bounded units. |
| Sequence | [Phase plan](phase-plan.md) | Phase outcomes and exit gates derived from scope, baseline and evidence standard. |
| Execution | [Tactical plan](tactical-plan.md) and [execution log](execution-log.md) | Current characterization tasks and actual work receipts; future code units need their own directives. |

The [scope decision register](scope-decisions.md) reconciles the recorded
decisions across the three intent sources; it does not demote the scored
inventory or refactor discussion to historical input. Keep the matrix and
refactor discussion reciprocally linked as command scope changes. The
[pruning review](command-pruning-review.md) preserves an obsolete seven-name
proposal as historical reasoning. The
[branch isolation record](branch-isolation.md) explains the independent
history and eventual TUI reconciliation. The
[command follow-up backlog](../../backlog/friday-tui-command-followups/README.md)
holds behavior changes and consolidation proposals outside this extraction.
The approved [MCP client compatibility exception](directives/CD-CMD-MCP-001-compatibility-exception.md)
records the maintainer-requested Draft-07 and query-URL fixes as a separate,
bounded unit on this branch; it does not advance the command P0–P5 gates.
Two further MCP issues are documented:
[tool continuity across conversation turns](proposals/mcp-tool-turn-continuity.md)
and [server-neutral input-schema compatibility](proposals/mcp-schema-compatibility.md).
The schema issue has an [approved exact construction directive](directives/CD-CMD-MCP-003-server-neutral-schema.md)
for its bounded implementation unit and an
[engineering matrix](mcp-schema-engineering-matrix.md) for the supported profile.
They are separate from the shared-command contract and from each other:
registration determines which tools exist in Chat, while per-turn selection
determines which registered schemas the model receives. Both proposals remain
planning only.
The complete technical contract is not approved; the foundation design approval
covers only API-01–API-06. Remaining family contracts, capability mapping and
compatible primitive reuse evidence remain P1 obligations after resumption.

**Current decision boundary:** Retain the current behavior of every maintained
command that survives the nine selected retirements. The exact API and compatible CLI primitive reuse must be reconciled in an
approved contract and bounded directives; removal behavior and preservation
policy are settled by O-01–O-05. Consolidation remains backlog work.

**Next gate:** Read/approve the proposed [PILOT-001 contract](pilot-command-contract.md),
then [CD-CMD-PILOT-001](directives/CD-CMD-PILOT-001-help-exit-clear.md).
They define catalog ownership, Chat routing, help/exit/clear rendering/lifecycle
and exact construction/verification scope. Both remain unapproved.
RET-001 is accepted. No pilot/family/TUI construction or publication is approved.
See the [main checkpoint](next-phase.md).

The [2026-11-06 local continuation](validation/local-2026-11-06/README.md)
refreshes baseline identity in this working home and records the current
planning/review boundary. Historical evidence remains preserved separately.

The [next-phase checkpoint](next-phase.md) identifies the current unit's
acceptance boundary and remaining P0/P1 gates.

Initial P0 observations are in the [source ledger](validation/par-coverage-ledger.md)
and [baseline receipt](validation/p0-baseline.md). The initial dirty-worktree Chat baseline was red. The
[controlled baseline](validation/p0-failure-disposition.md) passes all 826 Chat
tests using committed examples and xterm. Case-level behavior and installed-package
proof remain open.

Review inputs now include the [production/effect audit](validation/production-effects-audit.md),
[approved foundation API](shared-command-api.md) and
[approved first directive](directives/CD-CMD-FND-001-neutral-foundation.md).
Their frozen historical labels are superseded by the exact human approval record.
Family port signatures, installed proof and gate approval remain open.

## Foundation design approved; corrected readiness verified

[CMD-DESIGN-001](approval/foundation-design.md) is revised under the maintainer's
2026-11-05 authorization to resolve the three [council findings](validation/COUNCIL-CMD-DESIGN-001-round1.md).
The [remediation record](remediation/REM-CMD-DESIGN-001.md) maps each correction
and validation. Earlier VERIFIED reports cover their own frozen bytes only.
On 2026-11-06 Chuck Russell directly
approved CMD-DESIGN-001, paused, then explicitly resumed Step 3 and requested
a three-provider readiness council. That council supported current foundation
API consistency but requested five readiness corrections. Chuck Russell then
authorized REM-CMD-STEP3-001; its corrected packet is now independently VERIFIED
at `fcea84b8`. Construction approval remains separate.
At that earlier checkpoint execution remained planning with P0/P1 incomplete
and construction unauthorized. The later explicit CD-CMD-FND-001 approval
permits only the foundation unit. That unit now has its own fresh independent
[VERIFIED implementation result](validation/VAL-CMD-FND-001-report.md).
Chuck Russell subsequently accepted the verified foundation by direct instruction
“approved, proceed what's next steps?”; see the execution log. The complete
refactor remains started/local and later construction is separately gated.

Round 2 results and the narrow residual pruning-review correction are recorded
in [the council report](validation/COUNCIL-CMD-DESIGN-001-round2.md). The correction
had controller checks only at that historical checkpoint; those verdicts do
not verify the current corrected readiness candidate.
