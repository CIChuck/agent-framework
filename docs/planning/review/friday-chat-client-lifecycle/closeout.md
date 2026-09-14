# Friday Chat Client Lifecycle Closeout

## Completion Proposal

CD-001 and REM-001 are implemented on
`feature/friday-chat-client-lifecycle`. The stable product candidate is
`a5ed1bce59470cc599ee971d29642b4bb91ef576`, based on
`fe15552cc83caa2590be2e73158091dd15826d1e`.

Fresh VAL-002 delta and aggregate review returned `VERIFIED` after VAL-001-F01
was remediated. Every AC-01 through AC-12 and TP-01 through TP-13 passed.

## Delivered Behavior

- LiteLLM is pinned to 1.100.1 with upstream owned-client eviction repairs.
- Friday LLM exposes a documented process-client cleanup function.
- Friday Chat owns cleanup through typed real/fake runtime lifecycle services.
- Cleanup runs exactly once after all coordinator-owned exit maintenance and
  before event-loop teardown, with bounded failure accounting.
- prompt-toolkit no longer replaces the app event-loop exception handler.
- Deterministic regression coverage exercises eviction, delegation, runtime
  binding, cleanup ordering, termination failures, and content-safe errors.

## Validation Summary

- Focused tests: `55 passed`.
- Friday LLM: `186 passed, 8 skipped`.
- Friday Chat: `434 passed, 5 skipped`, plus the same three documented PTY
  baseline failures.
- Ruff, focused mypy, board validation, documentation lifecycle, scope review,
  and diff checks passed.
- Independent outcome: `VERIFIED`.

## Remaining Gates

The initiative is proposed as `completed`, not `accepted`. Maintainer acceptance
is still required. Push, pull request, merge, package-version changes, release,
PyPI publication, and live-provider validation remain separately unauthorized.
