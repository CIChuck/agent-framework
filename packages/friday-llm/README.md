# Friday Framework LLM

`friday-framework-llm` is Friday's LiteLLM-backed chat and embedding package.
Version `0.1.0a2` adds provider-neutral reasoning and sampling contracts while
keeping the `0.1.0a0` completion APIs compatible for one deprecation window.

## Install

```bash
pip install friday-framework-llm==0.1.0a2
```

The import package is `friday_llm`. This alpha pins `litellm==1.94.1` because
the observed provider translation is part of the tested contract.

## Reusable Model Library

`ModelLibrary` separates credential environment-variable names, reusable
endpoints, and deployable chat or embedding profiles. Applications bind roles
with `ChatServiceBinding` or `EmbeddingServiceBinding`, resolve them with an
explicit environment mapping, and construct services through
`LiteLLMService.from_spec(...)` or `LiteLLMEmbeddingService.from_spec(...)`.
Friday LLM owns the strict schema and pure resolution; Runtime and applications
own local-file loading and decide which role bindings are active.

Credentials are represented with `SecretStr` in resolved service specs and are
redacted from representations and serialized model dumps. Unknown references,
kind mismatches, incomplete targets, unsupported controls, and missing selected
credential variables fail before provider I/O.

## Typed Completion

New integrations should declare transport identity, model identity, and
generation intent separately:

```python
from friday_llm import (
    ChatCompletionRequest,
    GenerationOverrides,
    LiteLLMService,
    ModelTarget,
    ReasoningConfig,
    ReasoningMode,
    SamplingConfig,
    TransportTarget,
)

service = LiteLLMService(
    model_name="openai/qwen3.8-27b-mlx",
    api_key="lm-studio",
    api_base="http://127.0.0.1:1234/v1",
    transport_target=TransportTarget(
        provider="openai_compatible",
        dialect="openai_chat_completions",
        serving_engine="lm_studio",
    ),
    model_target=ModelTarget(
        model_id="qwen3.8-27b-mlx",
        family="qwen3_8",
        revision="your-captured-model-revision",
    ),
)

response = await service.chat_completion_request(
    ChatCompletionRequest(
        messages=({"role": "user", "content": "Use a synthetic prompt."},),
        overrides=GenerationOverrides(
            reasoning=ReasoningConfig(
                mode=ReasoningMode.ENABLED,
                effort="medium",
            ),
            sampling=SamplingConfig(temperature=0.3, top_k=20),
            max_tokens=256,
        ),
    )
)
```

Omitted request fields inherit service defaults. An explicit `None` clears a
service default and delegates that field to the provider. The typed API does
not inject the legacy `temperature=0.7` default.

## Typed Streaming

`chat_completion_events()` separates text, reasoning, tool fragments, complete
tool calls, usage, finish state, and diagnostic-safe errors. It never mixes
reasoning text into final text or tool arguments.

```python
async for event in service.chat_completion_events(request):
    if event.type == "text_delta":
        print(event.text, end="")
    elif event.type == "tool_call_complete":
        dispatch(event.name, event.arguments)
```

## Release-One Support Matrix

| Axis | Built-in normalized profile |
| --- | --- |
| Endpoint dialect | OpenAI-compatible Chat Completions |
| Transport | `litellm.acompletion` |
| Serving engine | LM Studio |
| Model family | Qwen3.8 |
| Evidence target | local alias `qwen3.8-27b-mlx` |
| Reasoning | provider default, enabled, disabled; effort `xhigh`, `medium`, `low`; preserve |
| Sampling | temperature, top-p, top-k, min-p, presence/frequency penalty, repetition penalty |
| Unsupported | Qwen3.8 reasoning token budget |

OpenAI Responses, LM Studio native REST, Anthropic-native, Gemini, Ollama,
DeepSeek, Moonshot, Bedrock, vLLM, and SGLang normalized profiles are deferred.
Legacy LiteLLM routing remains available, but Friday does not advertise typed
reasoning controls for an unregistered target composition.

Model-card sampling recommendations are not Friday defaults. Typed,
namespaced `LMStudioQwenOptions` exist only for the registered profile and
cannot set credentials, URLs, messages, tools, telemetry, retries, timeouts, or
arbitrary `extra_body` fields.

## Assurance And Privacy

Friday uses these evidence terms precisely:

- `requested`: supplied by the caller;
- `resolved`: accepted after merge and capability validation;
- `emitted`: present in captured outbound HTTP JSON;
- `acknowledged`: confirmed by provider or server metadata;
- `behaviorally_observed`: supported by a bounded controlled comparison.

Emitted does not mean effective. Assurance metadata contains bounded field and
profile names, capability provenance, and the LiteLLM version. It does not
contain prompts, tool arguments, credentials, response bodies, or reasoning
text. `preserve_thinking` controls provider chat-template replay; it does not
grant Friday permission to persist or log reasoning.

## Legacy Migration

`chat_completion()` and text-only `chat_completion_stream()` retain their
current signatures and return shapes. The legacy default still disables
thinking and still supplies `temperature=0.7`.

| Old input | `0.1.0a2` behavior | Migration |
| --- | --- | --- |
| `thinking_enabled` omitted | legacy disabled behavior | move new callers to `ReasoningMode.AUTO` or an explicit mode |
| `thinking_enabled=False` | disabled plus `DeprecationWarning` | use `ReasoningConfig(mode="disabled")` |
| `thinking_enabled=True` | enabled intent plus `DeprecationWarning` | declare an execution target and use typed reasoning |
| contradictory old/new values | configuration error before I/O | keep one source of truth |

Importing `friday_llm` no longer changes LiteLLM's process-global
`drop_params` or `modify_params` policy. Compatibility settings are scoped to
individual legacy calls; typed calls use strict preflight validation.

LM Studio 0.4.x accepts only string-form tool-choice values. For a normalized
named function choice, the private LM Studio adapter exposes only the selected
function schema and emits `required`, preserving exact-function semantics
without adding an LM Studio field to the public request model. A missing or
ambiguous selected schema fails before external I/O.

## Live LM Studio Evidence Lane

The default tests never contact LM Studio. To opt in, load the exact model,
record its revision/fingerprint, then run:

```bash
FRIDAY_LLM_LIVE=1 \
FRIDAY_LLM_LIVE_REVISION='<captured revision>' \
FRIDAY_LLM_LIVE_MODEL='qwen3.8-27b-mlx' \
uv run pytest -q packages/friday-llm/tests_llm/test_live_lmstudio.py
```

The live lane is a release gate, not ordinary CI. Record LM Studio version,
architecture, quantization, alias, chat template, context length, and server
settings alongside its results.

## License

MIT

## Provider-neutral request metrics

An optional borrowed `TelemetryInterface` sink now receives closed version-one
`llm.request_start`, `llm.attempt_finish`, `llm.batch_finish` and
`llm.request_finish` events. Consumers of the services' previous
`llm_completion_success/error` or `embeddings_generated/error` payloads must
migrate to these events; the services do not emit both schemas. Completion, stream
and vector return shapes, retries, circuit policy and Langfuse metadata remain
compatible. Constructors and `from_spec` accept optional keyword-only
`service_role`, defaulting to `unspecified`.

Metrics exclude prompts, response/reasoning text, tool data, vectors, raw model or
context identifiers and exception messages. Request IDs are generated per call,
attempt IDs count actual dispatches, and embedding batch IDs correlate their
attempts. Cache hits, empty input and preflight rejection have no dispatch or
fabricated usage. Reported zero differs from unavailable usage. Streams count raw
chunks and retain the final cumulative usage snapshot once, including usage after
finish; `first_text_ms` measures elapsed time to first text, including setup retries.
Cancellation and explicit early close produce `cancelled` and `incomplete` outcomes.

USD values are estimates from reported usage and local rates, never actual billing.
`price_source`, `price_match` and an opaque `pricing_ref` describe the effective
rates without exposing model/config strings. Built-in rates are the historical
early-2025 table, not verified current prices; custom and supplied rates are caller
inputs. Partial/missing required usage, disabled pricing or an unpriced model means
no estimate. Failed attempts may incur unknown provider charges. The additive
`CostCalculator.estimate_with_provenance` leaves legacy numeric `calculate` and
lookup behavior intact; invalid rates have an explicit telemetry disposition.

The public standalone legacy telemetry helper retains historical unsafe payloads
for compatibility and is outside this guarantee. Full turn/parent-span correlation
and Langfuse adoption remain separate work.
