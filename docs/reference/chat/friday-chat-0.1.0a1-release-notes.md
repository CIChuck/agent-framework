# Friday Chat 0.1.0a1 Release Notes

- Candidate: `friday-chat==0.1.0a1`
- Required LLM: `friday-framework-llm==0.1.0a1`
- Status: Implemented candidate; publication not authorized
- Date: 2026-08-28

## What Changed

Friday Chat's primary interactive model now consumes Friday LLM's typed request,
generation, target, response, and stream-event APIs. The application keeps its
own `ChatModelResponse` and text-only streaming boundaries while Friday LLM owns
capability preflight, translation, retries, and transport.

The canonical `llm:` YAML now contains:

- provider-independent `generation.reasoning` and `generation.sampling`;
- explicit `transport_target` and `model_target` identity;
- optional bounded, namespaced provider options;
- existing connection and resilience fields.

Friday Chat does not infer provider, dialect, serving engine, model family, or
revision from the route model or URL.

## Sampling Behavior

`top_p` and `top_k` existed in earlier Friday Chat configuration but the primary
legacy adapter did not forward them. They now reach Friday LLM and the final
supported LM Studio/OpenAI-compatible wire payload on the typed path.

The typed path also supports the upstream normalized fields `temperature`,
`min_p`, `presence_penalty`, `frequency_penalty`, `repetition_penalty`, and
`max_tokens`. Captured wire emission proves forwarding; it does not by itself
prove that every endpoint behaviorally honored a value.

## Reasoning Behavior

The canonical modes are `auto`, `enabled`, and `disabled`. The built-in Friday
LLM `0.1.0a1` target profile supports LM Studio's OpenAI-compatible Chat
Completions endpoint with Qwen3.8, bounded effort values `xhigh`, `medium`, and
`low`, and optional preservation. Reasoning budgets remain unsupported for this
profile and fail before provider I/O.

Reasoning events are never merged into Friday Chat's visible text stream.
Reasoning content remains sensitive and is not added to configuration
diagnostics, logs, telemetry, transcripts, release evidence, or artifact smokes.

## Legacy Configuration Window

These flat fields remain accepted through `0.1.x` and are scheduled for removal
no earlier than `0.2.0`:

| Legacy | Canonical |
| --- | --- |
| `llm.temperature` | `llm.generation.sampling.temperature` |
| `llm.top_p` | `llm.generation.sampling.top_p` |
| `llm.top_k` | `llm.generation.sampling.top_k` |
| `llm.max_tokens` | `llm.generation.max_tokens` |
| `llm.thinking` | `llm.generation.reasoning.mode` |

Configurations without explicit targets keep the legacy method path and produce
an actionable startup diagnostic. With explicit targets, legacy fields are
resolved into typed generation intent. Equal flat and nested values are
accepted with a deprecation diagnostic; conflicting values fail before service
construction. Unknown nested LLM keys now fail instead of being ignored.

## Consumer Boundary

This release migrates only the primary interactive Chat model. Extraction,
maintenance roles, compaction, passage routing, smart-file summarization, and
reorganization providers remain legacy consumers. A separate legacy fallback
service prevents primary typed targets or defaults from changing those
consumers accidentally. Their migration sequence is recorded in the
[deferred consumer handoff](../../planning/upgrades/friday-chat/friday-chat-typed-llm-deferred-consumer-handoff.md).

## Packaging

- Friday Chat metadata and runtime version are `0.1.0a1`.
- Friday LLM is pinned exactly to `0.1.0a1`.
- Every other direct and optional Friday package remains pinned to `0.1.0a0`.
- The `full` self-extra points to `friday-chat==0.1.0a1`.
- The root `friday-framework==0.1.0a0` meta-package is unchanged and is not part
  of this component release.

TestPyPI, PyPI, and release-tag operations require separate authorization. PyPI
artifacts are immutable; corrections must use a new version rather than
overwriting `0.1.0a1`.
