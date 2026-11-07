# Command refactor — next-phase checkpoint

Branch: `feature/command-retirement`
Status: RET-001 accepted; amended pilot contract/directive and harness in council review
Execution phase: planning
Validation state: in_review (PILOT-001 design/harness); product implementation not started; RET-001 verified and accepted

The [board](../../board.yaml) owns initiative state. The entire refactor remains
started; this bounded retirement unit is implemented, verified and accepted locally.
Chuck Russell directly accepted it on 2026-11-07; the
[acceptance record](approval/command-retirement.md) preserves that decision.

## Current result

The [fresh independent report](validation/retirement/verified-report.md) VERIFIED
candidate `f896ef536efcc45d569f4231edfc39baab09bbc8` against merged source base
`6f291ca5755a616d9185c86dff104b660a1fba8c`, with no mandatory findings.
All nine default slash names are removed; Chat now has exactly 41 canonical
commands and three aliases. Former effects are unreachable through these names.
Retained metadata, handlers, parser and runtime behavior are preserved. Generic
custom registries remain extensible. Current guides match the supported surface.

The independent review reproduced 1,038 Chat, 145 foundation/cohort and 155 CLI
tests; source/assertion preservation, focused lint/types, metadata/lock/docs and
clean installed-package proof pass. It independently verified all 519 original
functions/2,260 assertions, 390 wheel members/668 sdist files, exact 129-package
profile and additional context-tripwire probes. Root Ruff, root collection and
older formatting failures remain explicitly failing baseline debt; no broad
success or implicit waiver is claimed.

[Exact approval](approval/command-retirement.md),
[builder report](validation/retirement/README.md),
[assertion ledger](validation/retirement/assertion-disposition.json),
[frozen request](validation/retirement/request.json) and
[independent receipts](validation/retirement/independent-evidence.json) retain
candidate-specific evidence. The controller rechecked all frozen hashes before
recording evidence/status-only closeout. No product, test, dependency, lock,
API or directive change follows the reviewed candidate.

## Next steps

1. Read and approve the [PILOT-001 contract](pilot-command-contract.md): three
   shared definitions/handlers, catalog ownership, Chat routing/rendering,
   lifecycle effects, custom-registry compatibility and required dependency.
2. Read and approve [CD-CMD-PILOT-001](directives/CD-CMD-PILOT-001-help-exit-clear.md):
   exact paths, baseline capture, assertion preservation, regression cases,
   installed artifacts, independent review and stop conditions. Explicitly
   approving both exact documents together is sufficient. Neither is approved
   yet; the instruction to prepare this packet grants no construction authority.
3. After both approvals, record their hashes and execute only that pilot. Stop
   after fresh independent verification for bounded maintainer acceptance.
4. Proceed through the remaining family/P0/P1 gates and bounded directives;
   final integration/aggregate review precedes full refactor acceptance and TUI
   resumption.

No push, PR, merge, pilot/family/TUI construction or release is authorized for
this unit. The prior foundation checkpoint was delivered in PR #13; its delivery
authority is consumed. Both original uncommitted example configurations remain
byte-identical and excluded. Historical directive draft/pending labels describe
pre-approval/review states; current approval/report/board/checkpoint govern this
handoff. RET-001 acceptance is recorded separately from independent verification; it does
not accept the entire refactor or supply future construction/delivery approval.

The planning-only preparation was authorized by Chuck Russell's 2026-11-07
“proceed”. Its scope is the two proposed documents and current board/packet
navigation/authority/log records; no product, test, configuration, dependency,
lock or frozen evidence byte changes. This is the documentation-only lightweight
exemption under repository policy, not an exemption for the future pilot.
Controller validation comprises source/protected-file hashes, proposal pins,
embedded-code syntax, board/dashboard, documentation links and whitespace.
No implementation tests or independent product review are claimed for this draft.

The 2026-11-07 harness amendment now supplies runnable diagnostic scripts,
a frozen baseline with 193 observations and explicit G0–G5 incremental gates.
[Harness receipts](validation/pilot/harness-evidence.json) record fresh/offline
startup, seven guard refusals, comparator controls, clean-Git reproduction and
source-tamper rejection; the revised runner passes 1,038 Chat,145 foundation/
cohort and155 CLI baseline tests. No pilot API/adapter is implemented. Council
review and bounded feedback are authorized separately; scores do not grant
construction approval. Historical documentation-only limits above describe the
initial draft; the later exact diagnostic exemption is in current authority.
