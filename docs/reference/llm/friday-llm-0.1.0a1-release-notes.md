# Friday LLM 0.1.0a1 Release Notes And Migration

## Summary

This component alpha adds model-independent reasoning and sampling intent with
registered provider/engine/model translation. It keeps existing Friday callers
on the legacy API and does not change Friday Core, Runtime, Agent, Memory, Chat,
or the root meta-package.

## Added

- Frozen, extra-forbid `ReasoningConfig`, `SamplingConfig`,
  `GenerationConfig`, and field-set-aware `GenerationOverrides`.
- Separate `TransportTarget` and `ModelTarget` identity; family and revision are
  never inferred from a model-name substring.
- Supported/unsupported/unknown capability records with constraints,
  provenance, conservative composition, and optional bounded operator
  declarations.
- A private adapter contract and a built-in OpenAI Chat + LM Studio + Qwen3.8
  translation composition.
- Typed `ChatCompletionRequest`, enriched response/usage/assurance models, and
  named function tool choice.
- Typed stream events for text, reasoning, tool deltas, complete tool calls,
  usage, finish, and safe errors.
- Canonical immutable retry call specs, strict preflight, stream cleanup on
  timeout/cancellation, and final real-HTTP wire tests.

## Changed

- Package version: `0.1.0a0` to `0.1.0a1`.
- LiteLLM: unbounded `>=1.81.0` to exact `==1.94.1`. The initial `1.98.0`
  candidate was rejected because it cannot import on Python 3.10.
- Importing `friday_llm` no longer changes process-global LiteLLM
  `drop_params`, `modify_params`, or debug policy. Legacy compatibility options
  are now per call; typed calls are strict.
- `thinking_enabled` is deprecated when explicitly supplied. Omission retains
  the legacy disabled default for this deprecation window.
- Reasoning text may be returned to the caller but is excluded from logs,
  telemetry, assurance metadata, and diagnostics.

## Migration

1. Keep current callers unchanged if they need the legacy return type or
   text-only stream.
2. New callers should declare `TransportTarget`, `ModelTarget`, and optionally
   service-level `GenerationConfig` defaults.
3. Move per-request controls into `GenerationOverrides` and call
   `chat_completion_request()` or `chat_completion_events()`.
4. Treat an omitted override as inheritance and explicit `None` as clearing a
   service default.
5. Replace explicit `thinking_enabled` with `ReasoningConfig.mode` before the
   planned `0.2.0` removal window.
6. Do not treat emitted controls as effective without server acknowledgement or
   bounded behavioral evidence.

Semantically equal legacy/new reasoning values are accepted with a deprecation
warning. Contradictory values fail at construction before retry, circuit
breaker, or external I/O.

## Supported And Deferred

Release-one typed reasoning is limited to LiteLLM OpenAI-compatible Chat
Completions, LM Studio, Qwen3.8, and an explicitly identified model revision.
Reasoning budgets are unsupported for that profile. OpenAI Responses, LM
Studio native REST, and other provider-native normalized profiles are deferred.
The provider-neutral models do not need to change when a future private adapter
is added.

`friday-framework==0.1.0a0` continues to select its exact
`friday-framework-llm==0.1.0a0` dependency until a coordinated meta-package
release. Consumers that want this component alpha must request
`friday-framework-llm==0.1.0a1` directly and resolve its published Core and
Telemetry `0.1.0a0` dependencies.

## Known Evidence Limits

- Deterministic translation, final HTTP wire shape, response normalization, and
  streaming invariants are tested.
- The local live LM Studio/Qwen target was unavailable during implementation;
  acceptance and behavioral-effect claims remain pending.
- LiteLLM warnings, if observed in deterministic wire tests, are recorded and
  are not hidden by Friday global settings.
- TestPyPI/PyPI upload and tagging require separate authorization and are not
  part of implementation approval.
