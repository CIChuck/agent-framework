# Shared Friday command refactor — TUI effort, first phase

**Status:** started/pushed. Ingestion extraction/chunking and embedding-limit
planning is corrected for final council round4; MAINT-001 human UAT/acceptance remains pending.

**Delivery:** [PR #15](https://github.com/CIChuck/agent-framework/pull/15)
is merged into `master` at `c36e7ee5`; its remote retirement branch is deleted.
The current scoped branch `feature/cmd-ingest-001` incorporates that merge while
retaining its separate planning commit. Merge does not complete MAINT human UAT
or acceptance or authorize INGEST construction; see the
[branch handoff](validation/document-ingestion/branch-handoff.md).

**Working-folder update — 2026-11-05:** The maintainer changed direction:
current command-first and Friday TUI planning is consolidated in the
`agent-framework` folder. Earlier TUI-folder directions are superseded for
current work. This transfer changes documents only; imported implementation
claims, reviews and test receipts retain their original provenance. No design
approval, construction authority or code validation is inferred.

**MEMQ accepted — 2026-11-10:** Chuck Russell reports both the main MEMQ UAT
and combined repair retest successful and directs closure. [Acceptance](approval/memory-queries-acceptance.md)
records the accepted query family, shared quote/ingestion repairs and diagnostics.
Full reorganization on exit yields positive `/meta` results, maintainer-reported.
The explicit `/reorganize --full --execute` syntax defect is separately open as
[FU-011](../../backlog/friday-chat-framework-followups/upgrade-log.md#fu-011-reorganize-rejects-the-explicit-full-mode-flag).
`execution_phase: closeout`; `validation_state: verified`; MEMQ acceptance: accepted.
Earlier implementation/review/pending-UAT statements describe their historical
freezes and are superseded by this acceptance. The wider initiative stays started/local.

**Separate MAINT-001 closeout:** [Implementation verification](validation/maintenance/implementation/verified-report.md)
reconciles Astra9.5 and Sol9.6, both VERIFIED, no mandatory findings. Reviewed
candidate `b15ee091`; product/artifact source `ae15a537`. Execution phase:
closeout; validation state: verified. [Targeted human UAT](uat/maintenance-reorganization-uat.md)
is ready, all cases NOT RUN. Acceptance and delivery remain ungranted.

**Additional requested planning — document ingestion:**
The [REM](remediation/REM-CMD-INGEST-001-pdf-docx.md) and
[Tools companion](proposals/tools-document-adoption.md) are corrected for final
round4. Execution phase: planning; validation state: in_review.
The maintainer's [fresh-store upgrade policy](approval/ingest-existing-store-policy.md)
is unchanged: preserve old state and `/read`, no legacy mode/reset/migration.

[Round3](validation/document-ingestion/council-round3/report.md) returned Sol
VERIFIED9.6, Astra CHANGES_REQUESTED9.2 and Opus procedurally BLOCKED with
separate technical CHANGES_REQUESTED9.15. The remaining typed aggregate handoff
and fresh-creation qualification are corrected, with bounded useful advisories.
The [round4 correction scope](validation/document-ingestion/council-round4/correction-brief.json)
binds the last authorized pass. Every seat must be VERIFIED >=9.5 with no
mandatory findings; otherwise return remaining issues, with no fifth pass.
No product code, gate-A execution, installation, store action, acceptance or
delivery follows automatically. MAINT human UAT/acceptance remain separate.

**Working home:** `agent-framework`, branch `feature/cmd-ingest-001`.
**Board ID:** `friday-command-refactor`.
**Status:** CMD-FND-001 implemented, independently VERIFIED at `b4fc199e` and
accepted by Chuck Russell. Exact strengthened RET-001 is now approved and implemented locally; independently VERIFIED at `f896ef53` and accepted by Chuck Russell on 2026-11-07.
Exact foundation approvals and source base
`d003c4db` remain in the [approval record](approval/foundation-readiness.md).
See [independent result](validation/VAL-CMD-FND-001-report.md) and
[builder evidence](validation/CMD-FND-001-report.md). That foundation evidence
predates the separately approved pilot wiring work.
`execution_phase: closeout`; `validation_state: verified` for completed DIAG-001
D1–D3 and its bounded aggregate at `be72a1e8`. [Final verification](validation/diagnostics/implementation/d3/verified-report.md)
records Sol/Astra/Claude VERIFIED9.7 each, no open mandatory findings,1,991 source
passes and exact corrected artifact/probe source `28c544fa`. [Acceptance handoff](validation/diagnostics/implementation/d3/acceptance-handoff.md)
was answered: Chuck Russell reported successful manual UAT and [accepted DIAG-001](approval/diagnostics-acceptance.md);
the [roadmap](uat/friday-chat-user-acceptance-roadmap.md) records maintainer-reported results. MEMQ-001 has completed guarded D0 and generated the bounded neutral D1 implementation under the existing technical approval: the revised
[contract](memory-query-command-contract.md) and [directive](directives/CD-CMD-MEMQ-001-memory-queries.md)
retain the original [approval](approval/memory-queries.md) and the current
[cycle2 correction amendment](approval/memory-queries-directive-correction2.md).
Council rounds 1 and 2 returned CHANGES_REQUESTED. The original four corrections are
recorded in [REM-CMD-MEMQ-DIR-001](remediation/REM-CMD-MEMQ-DIR-001-readiness.md).
MEMQ `execution_phase: closeout`; `validation_state: verified` for D3 and the bounded aggregate at `bab16757`. D2 is independently VERIFIED at `ccf5471b`.
D1 is independently VERIFIED at `9ce71581` ([reconciliation](validation/memory-queries/implementation/d1/verified-report.md)). Directive/design
readiness remains VERIFIED only for its reviewed candidate `be15dca1`. The [fresh round4 council](validation/memory-queries/directive-review/round4/report.md)
is unanimously VERIFIED: Sol9.6, Astra9.5, Claude9.6; no mandatory findings remain.
Chuck Russell's [additional-pass authorization](approval/memory-queries-directive-additional-pass.md)
and [REM-CMD-MEMQ-DIR-003](remediation/REM-CMD-MEMQ-DIR-003-historical-qualifier.md)
covered the historical qualification and this fresh council. The old Sol BLOCKED
receipt remains preserved and invalid; all current seats complied independently.
Neutral product code and the [MEMQ UAT plan](uat/memq-user-acceptance-plan.md) are committed at `0f809207`.
The [D1 builder record](validation/memory-queries/implementation/d1/README.md) reports 599 Commands/cohort,
1,338 Chat and 155 CLI passes, exact retained observations and private mutation controls.
The three fresh D1 seats are VERIFIED (Sol9.7, Astra9.6, Claude9.6), with no mandatory findings.
D2 Chat integration and option R persisted listing are implemented at `3ed1d58a`;
[builder evidence](validation/memory-queries/implementation/d2/README.md) records
1,390 Chat,599 Commands/cohort and155 CLI passes plus20 current assertion-witnessed
mutation refusals. [Round1 council](validation/memory-queries/implementation/d2/council-round1/report.md) reproduced the runtime checks; Sol9.6 and Claude9.4 VERIFIED, Astra9.3 CHANGES_REQUESTED for stale authority prose. [Round2](validation/memory-queries/implementation/d2/council-round2/report.md) resolves that finding; Claude identifies an overbroad frozen backlog edit. The [exact restoration](remediation/REM-CMD-MEMQ-D2-002-restore-frozen-backlog.md) is independently VERIFIED by [round3 reconciliation](validation/memory-queries/implementation/d2/verified-report.md): Sol/Astra/Claude9.5 each, no mandatory findings. [D3 builder evidence](validation/memory-queries/implementation/d3/README.md) records 2,144 owning-suite passes,154 matching artifacts,8 actual installed probes,50 member/origin+10 archive+10 semantic refusals and8 restored clean-copy probes. [Final D3/aggregate reconciliation](validation/memory-queries/implementation/d3/verified-report.md) is unanimously VERIFIED: Sol9.5, Astra9.4, Claude9.5; no mandatory findings. Installed proof uses committed source `e4c0b9a2`. The historical [manual handoff](validation/memory-queries/implementation/d3/acceptance-handoff.md)
has been answered by [MEMQ acceptance](approval/memory-queries-acceptance.md). Existing technical approval
governs construction; council results do not grant acceptance or delivery.
[Correction controls and preservation](validation/memory-queries/directive-review/correction1/report.md)
are historical controller evidence; current union and complete-index gate controls
are in [cycle2 evidence](validation/memory-queries/directive-review/correction2/report.md).
The [additional prose correction evidence](validation/memory-queries/directive-review/correction3/report.md)
records the current patch and preservation checks, not an independent verdict.

**Next gate:** Reconcile the final authorized Sol/Astra/Opus round4 of corrected INGEST documents. Pass only if every seat is independently VERIFIED >=9.5 with no mandatory findings; otherwise return remaining issues without a fifth pass. Gate A/construction and MAINT human acceptance remain separate.

 The wider initiative stays started/local. Ignored exports
and dirty examples remain preserved. SESSION-001 remains accepted and verified.
SESSION D1–D3 and the complete bounded aggregate are independently VERIFIED at
`112e657f`: Sol 9.7, Astra 9.7, Claude 9.6; no mandatory findings remain.
[Bounded SESSION acceptance](approval/session-acceptance.md) is recorded from Chuck Russell's
“accepted” instruction. The broader initiative remains started/local.
PILOT-001 D1 is independently VERIFIED at `eacef5b0` by the reconciled three-provider
council. D2 remains VERIFIED. D3 and the complete bounded pilot are independently
VERIFIED at `eb216421` by Claude and Sol, both 9.6/10, and now
[accepted by Chuck Russell](approval/pilot-acceptance.md).
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

**Next gate:** Reconcile fresh MAINT-001 round4 Astra/Sol document review. Proceed with bounded implementation only if BOTH return VERIFIED at least9.5/10 with no mandatory findings and exact conditional pins match; otherwise stop and report.
See the [main checkpoint](next-phase.md).

The [Friday Chat user acceptance roadmap](uat/friday-chat-user-acceptance-roadmap.md)
provides 17 individually runnable interface, diagnostics, export, usability and
performance cases, with a results register for the completed candidate. All
cases started as NOT RUN; the maintainer reported a successful run on 2026-11-09. This documentation does not change construction or acceptance authority.

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

Current additional readiness correction: [round-three findings and dispositions](validation/pilot/council-remediation-round3.json),
[round-four diagnostic evidence](validation/pilot/harness-evidence-round4.json).
Round-four council is complete: all scores meet 9, but all verdicts request
changes at that reviewed candidate. See the [consolidated result](validation/pilot/council-round4.json) and
[proposed correction plan](validation/pilot/round4-reconciliation.md). Await
the next approval gate: [pilot contract](pilot-command-contract.md) followed by
[CD-CMD-PILOT-001](directives/CD-CMD-PILOT-001-help-exit-clear.md), or both together.
The two fixes and aggregate readiness are now [independently VERIFIED](validation/pilot/final-readiness-validation.md).
Pilot construction remains unapproved.

Current pilot construction is [approved](approval/pilot.md). D1 covers neutral
handlers/tests, D2 Chat integration/lifecycle, D3 regression/artifact/installed
proof. A fresh council follows each deliverable; no later family or delivery
is approved. Historical pending-approval paragraphs above are superseded by
this exact maintainer record.

D1 neutral handlers, D2 Chat integration and D3 regression/installed proof are
independently verified. [Reconciled pilot verification](validation/pilot/implementation/d3/verified-report.md)
records the current result; [exact council reports](validation/pilot/implementation/d3/council-round2.json)
and [current evidence](validation/pilot/implementation/d3/remediation-evidence.json)
preserve the reviewed candidate and limits. Both D3 findings are closed.
Chuck Russell has [accepted PILOT-001](approval/pilot-acceptance.md).
Approved SESSION-001 inputs:

1. [Session contract](session-command-contract.md): typed history/clear port,
   payload union amendment, exact legacy behavior and failure order.
2. [CD-CMD-SESSION-001](directives/CD-CMD-SESSION-001-session-views.md): bounded
   paths, incremental tests, frozen baseline and installed proof. Both documents
   are approved together in the subsequent exact approval record. S0 precedes
   neutral D1 construction and fresh council before D2.

[Preparation evidence](validation/session/preparation.json) records 25 source
observations, exact replay and 434 related Chat/217 Commands-cohort passing
tests. It is reference evidence, not another approval document. Later families,
P0/P1 and TUI remain open; delivery is local only.

SESSION-001 construction was [approved](approval/session-views.md), independently
VERIFIED and [accepted by Chuck Russell](approval/session-acceptance.md).
The [remaining council roster](approval/council-roster.md) is Sol/Astra/Claude.
The post-SESSION instruction “Await separate maintainer direction and approved scope for a next unit” is historical and superseded by the current MEMQ next gate above.
