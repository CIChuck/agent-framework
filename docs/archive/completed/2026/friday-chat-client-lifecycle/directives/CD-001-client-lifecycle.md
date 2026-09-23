# CD-001 Client Lifecycle Construction Directive

Status: approved by maintainer direction on 2026-09-14

## Authority

The repository maintainer directed the agent to proceed after receiving the
read-only causal diagnosis and the proposed four-part remediation. This
directive narrows that authority to the files and behaviors below.

Authority order:

1. active maintainer direction;
2. repository engineering, development lifecycle, and independent validation
   policies;
3. accepted Friday Chat behavioral contract;
4. this initiative's build plan;
5. this tactical plan and directive.

## Objective

Eliminate known unclosed LiteLLM aiohttp client sessions in long-running Friday
Chat processes, close remaining process-scoped clients before loop teardown,
and prevent message-only event-loop diagnostics from becoming blocking
`Exception None` prompts.

## Allowed Product And Test Files

- `packages/friday-llm/pyproject.toml`
- `packages/friday-llm/src/friday_llm/lifecycle.py`
- `packages/friday-llm/src/friday_llm/__init__.py`
- `packages/friday-llm/tests_llm/test_lifecycle.py`
- `packages/friday-chat/src/friday_chat/runtime.py`
- `packages/friday-chat/src/friday_chat/adapters.py`
- `packages/friday-chat/src/friday_chat/app.py`
- `packages/friday-chat/src/friday_chat/input_sources.py`
- `packages/friday-chat/tests_chat/test_runtime.py`
- `packages/friday-chat/tests_chat/test_app_lifecycle.py`
- `packages/friday-chat/tests_chat/test_input_sources.py`
- `uv.lock`
- this initiative's planning, execution, and validation artifacts

## Required Implementation

1. Pin LiteLLM to stable 1.100.1; do not use a floating or prerelease range.
2. Add a public Friday LLM async cleanup function that delegates to LiteLLM's
   public cleanup boundary and documents its process-scoped semantics.
3. Add a narrow typed Friday Chat lifecycle protocol with deterministic real
   and fake implementations.
4. Bind the real implementation only in real runtime construction.
5. Close provider clients after background and LLM-dependent maintenance work
   is finished and before the application event loop terminates.
6. Route cleanup errors through the existing bounded maintenance-warning and
   shutdown-failure path; do not expose credentials or full provider payloads.
7. Call `PromptSession.prompt_async(..., set_exception_handler=False)`.
8. Preserve all provider, model, tool-loop, timeout, retry, and generation
   configuration behavior.

## Required Tests

- Public Friday LLM cleanup delegates once and propagates cleanup failure.
- Fake lifecycle cleanup is deterministic and provider-free.
- Real runtime binds the framework lifecycle adapter.
- Application shutdown calls provider cleanup exactly once after maintenance
  work and background cancellation.
- Cleanup failure records a bounded diagnostic and follows existing shutdown
  containment behavior.
- Prompt reader passes `set_exception_handler=False`.
- LiteLLM-owned client eviction schedules or completes cleanup without an
  unclosed aiohttp event-loop report.
- Existing timeout, streaming, input, app lifecycle, and runtime suites remain
  green.

## Verification

- `uv run pytest packages/friday-llm/tests_llm/test_lifecycle.py`
- `uv run pytest packages/friday-chat/tests_chat/test_input_sources.py`
- `uv run pytest packages/friday-chat/tests_chat/test_app_lifecycle.py`
- `uv run pytest packages/friday-chat/tests_chat/test_runtime.py`
- `uv run pytest packages/friday-llm/tests_llm`
- `uv run pytest packages/friday-chat/tests_chat`
- focused Ruff for changed Python files
- focused mypy for both changed packages
- board and documentation lifecycle validation
- `git diff --check` and explicit changed-file scope review

No live provider, credential, network target, PyPI, GitHub, push, merge, tag, or
release action is authorized by these commands.

## Stop Conditions

Stop and return to the maintainer if:

- LiteLLM 1.100.1 breaks an existing typed provider or generation contract;
- cleanup requires closing clients while requests may still be active;
- the change requires provider- or model-specific behavior;
- package-cohort version changes become necessary for deterministic validation;
- a secret or local state file would need to be read or modified; or
- implementation must leave the allowed file list.
