# SESSION-001 D1 — neutral models and handlers

Execution phase: `validation`. Validation state: `in_review` (D1 only).
The [exact approval](../../../../approval/session-views.md) covers the frozen
contract/directive despite their preserved draft labels. D2 Chat integration,
D3 installed candidate proof and SESSION acceptance remain pending.

Product source is committed at `4065a150`. The shared package adds exactly six
exports: HistoryTurn, HistoryData, SessionClearedData, SESSION_SPECS, SessionPort
and build_session_handlers. The two new closed outcome variants extend the
approved union; every original model/invariant remains intact. History returns
one immutable ordered snapshot. Clear performs one synchronous history clear,
then awaits one memory clear. Errors/cancellation propagate without retries or
rollback. Neither handler reads args/spec/execution fields or formats output.

[Current evidence](evidence.json) preserves raw, role-labeled receipts:

- S0 reproduced 1,228 Chat, 217 Commands/cohort and 155 CLI tests, all 25 session
  cases/all 196 pilot observations, guard controls and the unchanged baseline's
  clean offline 13-workspace/125-locked-artifact build and two installations.
- D1 passes 278 Commands/cohort tests, including 61 new cases. Source-only
  standalone normal/-O/-OO tests enforce the stdlib boundary, model/invocation
  checks, ordered calls and explicit registration with pinned guard loading.
- After-change compatibility reruns pass 1,228 Chat/155 CLI,25 session cases
  and 196 pilot observations. They do not claim Chat uses the new handlers yet.
- Four private mutants are rejected by test-call assertions with start/end
  canonical-origin checks; an unmodified copy passes. No setup failure credit.
- Scoped Ruff, four-file format, eight-source-file mypy, metadata and lock pass.

[Preservation](preservation.json) and [before inventory](before-inventory.json)
show 785 original files unchanged; only the allowed neutral README, __init__ and
contracts change among existing files. All 277 original test files, their 2,999
test definitions/9,072 assertions and all Chat/CLI/package metadata/lock bytes
remain unchanged. Two new package files add the implementation and 61 tests.

Root Ruff 534 and the sole root Chat/CLI test_display collection conflict remain
failed/unwaived. Collection increases from 6,538 to 6,599 by exactly the new 61
cases. The existing registry-format failure remains unchanged. Initial new-test
import ordering/format checks failed and were corrected; those receipts remain
historical, distinct from final passing checks.

The S0 artifact trial proves baseline machinery only; no D1 candidate wheel,
default-installed SESSION behavior or whole-family completion is claimed.
Fresh three-provider D1 council must be reconciled before D2 under the approved
directive. No maintainer acceptance or external delivery is inferred.
