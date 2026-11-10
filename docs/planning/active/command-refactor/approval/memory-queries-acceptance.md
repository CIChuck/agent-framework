# MEMQ-001 — maintainer acceptance and UAT closure

Maintainer: Chuck Russell. Acceptance date: 2026-11-10. Recorded: 2026-11-10T13:27:29.974635+00:00.

> The memq combined repair retest UAT was successful. It can be closed.
> The memq UAT test has been deemed successful. That can be closed.

**ACCEPTED / CLOSED:** MEMQ-001's six queries (`/memory`, `/insights`, `/summaries`,
`/meta`, `/entities`, `/list-ingested`), approved option R persisted listing, shared
entity quote and optional-description ingestion repairs, and combined diagnostic
retest. Both [MEMQ UAT](../uat/memq-user-acceptance-plan.md) and
[combined retest](../uat/memq-repair-retest.md) are PASS, maintainer-reported.
This later acceptance supersedes all earlier pending/NOT RUN/blocked labels for
these units; historical reports and technical pins retain their original bytes.

The maintainer reports full reorganization is configured on exit and produces
positive `/meta` results. No agent observed or reran that production session;
per-case traces/timings, exact launched binary hash, run IDs and model details
were not supplied in this acceptance report. The original dirty UAT plan is
preserved [byte-exact before closure](../validation/memory-queries/acceptance/uat-plan-before-acceptance.txt),
SHA256 `e6b11b076af42d32e5278d77c102cf47011ebae19ea1227234af3420f5ef85d7`. No individual measurements or
unreported cases are invented.

## Recorded code and verification identities

Checkout before acceptance: `39a631a92190bc2a8dc54b0d20fb0fecf7e8c535`, branch `feature/command-retirement`.
Shared repair source: `47134ad6404cb37916efac45e09d5378a286d387`;
corrected packet: `ead29d01c423be0bbc49e80247ff753521884e20`.
[Shared repair verification](../validation/memory-queries/uat-shared-repair/verified-report.md)
and [fresh OpenAI correction report](../validation/memory-queries/uat-shared-repair/review-round2/report.md)
remain independently VERIFIED. Diagnostic source `3969e4d4` and
[verification](../validation/memory-queries/uat-diagnostics/verified-report.md) remain
separate reviewed evidence. Original D3 candidate `bab16757` and installed source
`e4c0b9a2` retain their [bounded D3 verification](../validation/memory-queries/implementation/d3/verified-report.md).
Acceptance records the maintainer's latest result; it does not attest an
unreported launch identity or rerun any historical test/build/probe.

## Separate open issue — FU-011

`/reorganize --full --execute` is rejected because the Chat parser's mode allowlist
omits `--full`. Full is already the default: `/reorganize --execute` parses as
full execution. `/meta` currently recommends the unsupported explicit spelling.
Exit maintenance constructs a typed FULL request directly, bypassing this parser;
that explains why it can work on exit. The maintainer accepts MEMQ while keeping
this separate [command-syntax defect](../../../backlog/friday-chat-framework-followups/upgrade-log.md#fu-011-reorganize-rejects-the-explicit-full-mode-flag)
open. No syntax repair is implemented or authorized by this documentation closeout.

[Exact pure-parser evidence](../validation/memory-queries/acceptance/reorganize-argument-evidence.json)
was reproduced without app/provider/store imports or maintenance execution.
Validation/verification behavior is summarized in the
[flow note](../validation/memory-queries/acceptance/verification-flow.md).

The parent friday-command-refactor initiative remains started/local; other
families, P0/P1, TUI, whole-refactor acceptance and delivery are not inferred.
Known root/format/dirty-config debt and historical isolation disclosures remain
unwaived. Both dirty YAML files, personal state including `.friday-old/`, exports
and prior evidence are preserved. No push, merge, release, runtime or provider change.
