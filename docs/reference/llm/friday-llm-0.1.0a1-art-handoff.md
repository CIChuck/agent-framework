# Friday LLM 0.1.0a1 ART Handoff Checklist

ART integration remains separately authorized work. This document is an input,
not evidence that ART has been changed or validated.

## Package And Target

- Install only the published `friday-framework-llm==0.1.0a1` artifact; a local
  Friday checkout is not integration evidence.
- Retain published `friday-framework-core==0.1.0a0` and
  `friday-framework-telemetry==0.1.0a0`.
- Set transport provider `openai_compatible`, dialect
  `openai_chat_completions`, serving engine `lm_studio`.
- Set model ID/alias `qwen3.8-27b-mlx`, family `qwen3_8`, and the exact captured
  model revision. Do not infer family or revision from the alias.
- Use `http://127.0.0.1:1234/v1` only when ART and LM Studio share that network
  namespace; otherwise supply the actual reachable base URL outside source.

## API Mapping

- ART reasoning default/provider default -> `ReasoningMode.AUTO`.
- ART reasoning enabled/disabled -> matching `ReasoningMode`.
- ART effort -> `xhigh`, `medium`, or `low` only.
- ART top-k/min-p/repetition penalty -> normalized `SamplingConfig` fields, not
  provider wire names.
- ART must not pass arbitrary LiteLLM/provider kwargs, `extra_body`, credentials,
  URLs, retries, telemetry, messages, or tools through provider options.

Use `chat_completion_request()` for non-streaming and
`chat_completion_events()` when reasoning, tools, usage, and finish state must
remain separate. Legacy methods remain compatible but do not provide the new
typed assurance/event surface.

## Required ART Evidence

- Exact installed distribution/version and wheel SHA-256.
- LiteLLM version and dependency resolution.
- LM Studio version, architecture, model revision/fingerprint, quantization,
  alias, chat template, context length, and server settings.
- Requested, resolved, emitted, acknowledged, and behaviorally observed fields
  kept as separate assurance levels.
- Tool ID/name/argument correlation, finish reason, usage, retries, and bounded
  timing under disabled and at least one enabled effort profile.
- No raw prompt, credentials, tool arguments, response body, or reasoning text
  in ART evidence or telemetry.

## Stop Conditions

Stop ART integration if the PyPI artifact is unavailable, hashes differ, the
target identity is incomplete, an advertised control is unknown/unsupported,
tools cannot be reconstructed without corruption, or behavioral evidence is
being inferred solely from visible/absent reasoning text.
