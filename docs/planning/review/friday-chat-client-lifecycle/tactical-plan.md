# Friday Chat Client Lifecycle Tactical Plan

Status: approved

1. **TP-01:** Freeze baseline `fe15552` and create
   `feature/friday-chat-client-lifecycle` without altering unrelated worktree
   files.
2. **TP-02:** Record the reproduced causal chain and upstream dependency
   evidence in the initiative packet.
3. **TP-03:** Transition the board from `queued` through `approved` to `started`
   with CD-001 as the implementation authority.
4. **TP-04:** Upgrade the exact LiteLLM dependency and refresh only resolver
   output required by that change.
5. **TP-05:** Add the public Friday LLM asynchronous cleanup boundary and
   focused contract tests.
6. **TP-06:** Add the typed Friday Chat runtime lifecycle dependency with real
   and fake implementations.
7. **TP-07:** Invoke cleanup at the final quiescent shutdown boundary and cover
   success, ordering, and failure containment.
8. **TP-08:** Disable prompt-toolkit's blocking replacement exception handler
   and cover the call contract.
9. **TP-09:** Add a deterministic dependency integration regression for
   LiteLLM-owned client eviction; do not make a provider call.
10. **TP-10:** Run focused tests, package tests, affected Ruff and mypy, board
    and documentation validation, and aggregate diff checks.
11. **TP-11:** Freeze a stable candidate commit and prepare a hash-pinned
    independent validation request.
12. **TP-12:** Dispatch a fresh-context, read-only validator. Remediate only
    numbered findings under separately recorded authority.
13. **TP-13:** Propose `completed` only after `VERIFIED`; do not push, merge,
    accept, release, publish, or run paid live tests without explicit authority.
