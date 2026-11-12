# C3 bounded offline dependency solving

Continue the unchanged approved [harness directive](../../../../../directives/CD-CMD-INGEST-GATE-A-001-readiness-harness.md)
and [continuation](../c1/continuation.json), using the exact private engine
[approval](private-resolver-engine-approval.json). The engine transfer is complete;
there are no further downloads or real stage effects in this component.

Only the existing harness `manifests.py`, its test module and README may change
source behavior. Shared declaration parsing may be factored without altering C2
refusals or signatures. Add an explicit offline catalogue-solving API backed by
qualified resolvelib1.2.1 and packaging24.2, with lazy optional imports. Minimal
loading remains stdlib-only. Inputs are synthetic or explicitly supplied complete
candidate declarations, never live index lookups. No tool may fetch a missing
candidate, execute a build or borrow ambient packages.

Respect the exact profile ceilings: 512 candidate wheels, 8192 graph edges,
500 solver rounds, 300 seconds per synthetic qualification invocation. Preserve
stricter existing shape/requirement/selected-byte limits and external cumulative
stage ceilings. Check an optional caller stop/budget callback before work and
between solver operations. A solver result is a declaration plan, not verification
of actual artifact bytes, licenses, target machine, installed package or execution
permission. Actual A0–A4 remain open and unactivated.

| Criterion | Required evidence |
| --- | --- |
| CS-01 | Exact authority/profile/tool/source pins, allowed source delta only; protected state and C0–C2 evidence retained. |
| CS-02 | Explicit bounded catalogue/roots/target and strict parser controls; malformed outer controls refuse before optional import. |
| CS-03 | Real guarded engine backtracks from a newest conflicting version to a compatible older version; impossible graphs refuse. |
| CS-04 | Canonical names, base/extras, late extra requests, markers, finite cycles and retained C2 consistency agree; unknown extras/references refuse. |
| CS-05 | Known incompatible Python/platform/yanked candidates are excluded, malformed/unknown metadata is not hidden; deterministic chosen plan respects declared limits. |
| CS-06 | Round/time/count/edge/selected-byte and caller stop controls refuse without outside effects; no automatic retry/budget reset. |
| CS-07 | No resolver-driven network/build/install; actual library origins and target inventories private; returned plans withhold all actual qualification/execution flags. |
| CS-08 | All prior 56 test bodies retained; explicit minimal, parser and engine selectors run normal/-O with actual call assertions, no setup-failure rejection credit. |
| CS-09 | Root-rule lint/format and mypy on the exact source selection with only declared private typed dependencies, no suppressions/upstream/root edits; administration/whitespace pass. |
| CS-10 | Stable candidate and fresh read-only delta then full bounded C0–C3 aggregate, exact evidence/limits and closing preservation; no full9.5/HR, UAT, acceptance or delivery claim. |
