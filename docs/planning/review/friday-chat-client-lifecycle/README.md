# Friday Chat Client Lifecycle Remediation

---
title: Friday Chat Client Lifecycle Remediation
initiative: friday-chat-client-lifecycle
document_type: initiative-index
status: completed
created: 2026-09-03
updated: 2026-09-14
execution_phase: closeout
validation_state: verified
next_gate: maintainer acceptance review
implementation_authority: closed
---

## Current State

A long-running live Friday Chat session produced an extraction timeout, one
literal `Unclosed client session` report, and repeated blocking
`Unhandled exception in event loop: Exception None` prompts. Read-only tracing
confirmed that the modal text is prompt-toolkit's rendering of an aiohttp
message-only event-loop context, not an exception escaping Friday's tool loop.

The installed LiteLLM 1.94.1 caches asynchronous clients for one hour and
intentionally dereferences expired clients without closing them. Upstream
LiteLLM 1.100.1 adds owned-client eviction cleanup and lifecycle-aware finalizer
handling for this exact class of unclosed aiohttp session.

The maintainer's 2026-09-14 `proceed` direction approves the bounded remediation
described by [CD-001](directives/CD-001-client-lifecycle.md). It does not
authorize a push, merge, release, publication, or paid live-provider test.

## Authority

- [Repository engineering policy](../../../reference/policies/repository-engineering-policy.md)
- [Development task lifecycle](../../../reference/policies/development-task-lifecycle.md)
- [Independent validation policy](../../../reference/policies/independent-validation-policy.md)
- [Friday Chat behavioral contract](../../../archive/completed/2026/friday-chat-v2/friday-chat-v2-behavioral-contracts.md)
- [Build plan](build-plan.md)
- [Tactical plan](tactical-plan.md)
- [CD-001 construction directive](directives/CD-001-client-lifecycle.md)
- [Execution log](execution-log.md)

## Package Boundary

This is a post-release defect remediation, not a FridayV2 parity implementation
pass. The approved boundary is limited to:

- `friday-framework-llm`: LiteLLM dependency and a public process-client cleanup
  boundary;
- `friday-chat`: typed runtime ownership, shutdown integration, and nonblocking
  prompt error reporting;
- focused tests, lock metadata, and this initiative packet.

No provider- or model-specific workflow behavior is authorized.

## Next Gate

Review the [verified closeout](closeout.md) and decide whether to accept the
completed initiative. No delivery action is implied by completion.
