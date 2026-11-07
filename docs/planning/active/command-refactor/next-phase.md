# Command refactor — next-phase checkpoint

Branch: `feature/command-retirement`
Status: RET-001 independently VERIFIED; ready for maintainer acceptance
Execution phase: closeout
Validation state: verified (RET-001 only)

The [board](../../board.yaml) owns initiative state. The entire refactor remains
started; this bounded retirement unit is implemented and verified locally.

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

1. Maintainer acceptance of RET-001.
2. Prepare/review PILOT-001: catalog ownership, help/exit/clear routing, rendering
   and lifecycle boundaries, aliases and verification. Obtain its exact design/
   construction approval before implementing any migration.
3. Proceed through the remaining family/P0/P1 gates and bounded directives;
   final integration/aggregate review precedes full refactor acceptance and TUI
   resumption.

No push, PR, merge, pilot/family/TUI construction or release is authorized for
this unit. The prior foundation checkpoint was delivered in PR #13; its delivery
authority is consumed. Both original uncommitted example configurations remain
byte-identical and excluded. Historical directive draft/pending labels describe
pre-approval/review states; current approval/report/board/checkpoint govern this
handoff. Independent verification is not maintainer acceptance.
