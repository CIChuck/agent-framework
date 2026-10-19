# TUI-N01B-09 first local candidate independent review

**Verdict:** `CHANGES_REQUESTED` for candidate
`36028fbf704c0ebb6a63ef09ab5a582af3f0184f` against authority base
`ee9d667c1db4f4239d0b4fece2f26d6d25934680`.
**Reviewer:** fresh-context read-only Codex validation subagent, 2026-10-19;
model/version unavailable. The reviewer used the shared clean checkout and
made no edits. This is historical first-candidate evidence; it is not a pass
and a revised candidate needs fresh review.

The reviewer checked the pinned [directive](../directives/CD-TUI-N01B-09-neutral-transcript-session-ensure.md),
[authority manifest](../authority.json),
[board](../../../board.yaml), [policy](../../../../reference/policies/independent-validation-policy.md),
[before-code characterization](N01B-09-before-code-session-ensure-characterization.md),
[builder checks](N01B-09-local-checks.md), and exact
`ee9d667c..36028fbf` diff. The branch was clean. Only the four approved
Runtime/Chat source/test paths and scoped TUI planning/evidence changed.
The implementation preserved the lazy factory, existing and ended session
handling, ignored false create, exception and cancellation propagation,
Chat's snapshot expression and preflight/write ordering, and the Runtime
Chat/CLI boundary.

Independent checks passed: 22 new tests, 414 full Runtime, 890 full Chat
with five skips, 155 unchanged CLI, and 35 Transcript; scoped Ruff lint,
targeted Mypy, offline lock, board/dashboard, changed-document links,
diff check, and installed Runtime-only and Chat wheel probes. Ruff format
flags the pre-existing large Chat adapter at both authority base and
candidate; the other three changed Python files pass format. Full suites
used synthetic local loopback fixtures, not a live provider or remote
service.

## Finding N01B09-01 — current validation state conflicts with board gate

**Severity:** medium. The packet [index](../README.md) current header,
[authority manifest](../authority.json) top-level `validation_state`, and
[execution-log](../execution-log.md) summary say `verified`, while the
latest execution-log entry says N01B-09 is `pending` and the board's
`next_gate` calls for independent validation. The
[independent-validation policy](../../../../reference/policies/independent-validation-policy.md)
requires `execution_phase` and `validation_state` in the packet index and
execution log to agree with the board gate. These inconsistent current fields
could make the N01B-09 candidate appear independently approved before it is.

Correct only the current N01B-09 packet fields to `pending` or `in_review`,
and keep N01B-08's `VERIFIED` result as historical evidence. Recheck board
validation and dashboard, duplicate-key authority JSON, changed-document
links, and `git diff --check`; freeze a new candidate and request a fresh
independent delta review plus complete candidate reconciliation. No product,
test, runtime configuration or dependency change is requested.

Exact-source Ubuntu verification, installed TUI terminal UAT, maintainer
acceptance and additional delivery remain outside this local review.
