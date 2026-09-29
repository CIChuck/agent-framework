# Friday Chat Client Lifecycle Build Plan

Status: approved

## Objective

Make provider HTTP-client ownership explicit at the Friday LLM/Friday Chat
boundary, prevent known LiteLLM aiohttp eviction leaks during long sessions,
and ensure message-only asyncio diagnostics never become blocking
`Exception None` terminal dialogs.

## Requirements

- **AC-01:** Friday LLM pins an upstream LiteLLM release containing owned-client
  eviction cleanup and lifecycle-aware aiohttp finalization.
- **AC-02:** Friday LLM exposes one documented, asynchronous, process-scoped
  cleanup function through its public package API.
- **AC-03:** Friday Chat represents provider-client cleanup through a typed
  runtime lifecycle contract rather than importing LiteLLM directly.
- **AC-04:** Real runtime construction binds the Friday LLM cleanup adapter;
  fake runtime construction binds a deterministic no-op implementation.
- **AC-05:** Shutdown cancels and drains background work, completes configured
  LLM-dependent maintenance, then closes provider clients before the asyncio
  event loop closes.
- **AC-06:** Cleanup failures are captured as bounded maintenance diagnostics
  and participate in existing shutdown failure accounting.
- **AC-07:** Friday's prompt reader disables prompt-toolkit's blocking event-loop
  exception handler so message-only contexts retain asyncio's meaningful
  diagnostic behavior.
- **AC-08:** Timeout, cancellation, tool-loop, generation-control, and provider
  translation behavior remain unchanged except for deterministic cleanup.
- **AC-09:** Regression coverage proves prompt handler configuration, cleanup
  ordering, idempotent/no-op behavior, cleanup failure containment, and the
  upstream owned-client eviction behavior.
- **AC-10:** Focused Friday LLM and Friday Chat tests, Ruff, and affected-scope
  mypy pass; broader failures must be separated from regressions.
- **AC-11:** No secret, local provider state, `.friday/` state, protected guide,
  or unrelated dirty file is modified.
- **AC-12:** A fresh-context validator returns `VERIFIED` against a stable
  candidate before completion is proposed.

## Design

Friday LLM owns the LiteLLM implementation dependency and exposes a narrow
async cleanup function. Friday Chat owns application orchestration and carries
an `AsyncClientLifecycle` protocol in `FridayRuntime`. The real adapter delegates
to Friday LLM; the fake adapter is deterministic and provider-free.

The application invokes cleanup only after all supervised and configured
maintenance work has quiesced. This avoids closing shared provider clients
while a foreground or background request is still running.

Prompt-toolkit remains the asynchronous input implementation, but Friday opts
out of its replacement exception handler. This is an observability safeguard,
not a substitute for closing clients.

## Dependency Decision

Upgrade the exact LiteLLM pin from 1.94.1 to the current stable 1.100.1. Upstream
1.100.1 marks LiteLLM-owned cached clients, defers their close through an
evicted-client closer, retains finalizer close tasks strongly, and handles
sessions bound to another or closed loop. These changes directly address the
observed one-hour-cache and `Unclosed client session` failure mode.

Primary upstream evidence:

- <https://github.com/BerriAI/litellm/releases/tag/v1.100.1>
- <https://github.com/BerriAI/litellm/issues/12443>
- <https://github.com/BerriAI/litellm/blob/litellm_internal_staging/litellm/caching/llm_caching_handler.py>

## Non-Goals

- Provider- or model-specific tool-loop behavior.
- Changing generation, reasoning, sampling, retry, or timeout semantics.
- Suppressing `ResourceWarning` or asyncio diagnostics globally.
- Patching vendored or installed LiteLLM source.
- General background-failure UX redesign.
- Package version cohort bumps, PyPI publication, push, merge, or release.
- Paid or credentialed live-provider validation without a separate maintainer
  authorization.

## Acceptance Boundary

Deterministic verification and independent validation may support a proposal to
mark this initiative `completed`. Only the maintainer may accept it, and release
versioning remains a separate authorized unit of work.
