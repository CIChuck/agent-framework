# Friday LLM

LiteLLM-backed chat and embedding services with typed requests, streaming events, reusable model profiles, resilience and optional provider-neutral request metrics.

**Distribution:** [friday-framework-llm](https://pypi.org/project/friday-framework-llm/) · **Import:** `friday_llm`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-llm==0.1.0a3"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: validate a request locally

```python
from friday_llm import ChatCompletionRequest, GenerationOverrides, SamplingConfig

request = ChatCompletionRequest(
    messages=({"role": "user", "content": "Hello"},),
    overrides=GenerationOverrides(sampling=SamplingConfig(temperature=0.3)),
)
print(request.overrides.sampling.temperature)
```

Expected output: `0.3`. Constructing a request makes no provider call. The current distribution pins `litellm==1.100.1`; use the declared dependency rather than substituting a different LiteLLM version.

## Complete a request against a local model server

This example performs a **live** call. Start LM Studio's OpenAI-compatible server at `http://127.0.0.1:1234/v1`, load the model under the alias shown, and replace the captured revision with the one actually served.

```python
import asyncio
from friday_llm import (
    ChatCompletionRequest, LiteLLMService, ModelTarget, TransportTarget,
    close_litellm_async_clients,
)

async def main() -> None:
    service = LiteLLMService(
        model_name="openai/qwen3.8-27b-mlx",
        api_key="lm-studio",  # Local server placeholder, not a hosted credential.
        api_base="http://127.0.0.1:1234/v1",
        transport_target=TransportTarget(
            provider="openai_compatible", dialect="openai_chat_completions",
            serving_engine="lm_studio",
        ),
        model_target=ModelTarget(
            model_id="qwen3.8-27b-mlx", family="qwen3_8",
            revision="replace-with-served-model-revision",
        ),
    )
    try:
        response = await service.chat_completion_request(
            ChatCompletionRequest(messages=({"role": "user", "content": "Hello"},))
        )
        print(response.content)
    finally:
        await close_litellm_async_clients()

asyncio.run(main())
```

Transport clients are process-shared by LiteLLM. In a long-running application, call `close_litellm_async_clients()` once at process shutdown after all model work is quiescent, not after each borrowed service call. Hosted endpoints require their real credential supplied by the application.

## Public surfaces and capabilities

| Need | API |
| --- | --- |
| Typed completion | `ChatCompletionRequest`, `chat_completion_request()` |
| Typed streaming | `chat_completion_events()`; distinct text/reasoning/tool/usage/finish events |
| Embeddings | `LiteLLMEmbeddingService` |
| Reusable model configuration | `ModelLibrary`, service bindings, `resolve_chat_service`, `resolve_embedding_service`, `from_spec()` |
| Request controls | `GenerationConfig`, `GenerationOverrides`, `ReasoningConfig`, `SamplingConfig` |
| Resilience and estimates | `ResilienceConfig`, `CircuitBreakerConfig`, `PricingConfig`, `CostCalculator` |

Built-in normalized reasoning/sampling capability support is specifically LM Studio + OpenAI-compatible Chat Completions + Qwen3.8. Other LiteLLM routes remain compatibility paths; routing support is not a promise that every normalized control works on every endpoint. Unsupported controls fail preflight. Model-library credential entries name environment variables; resolved specs use redacted secret values. Runtime/Chat own file loading.

Omitted typed request fields inherit service defaults; explicit `None` clears a default and delegates to the provider. Typed calls do not inject legacy `temperature=0.7`. Legacy `chat_completion()` and text-only streaming remain compatibility APIs; explicit `thinking_enabled` has deprecation/migration behavior. Prefer the typed surface for new callers. Importing Friday LLM does not change LiteLLM's global `drop_params` or `modify_params` policy.

## Telemetry and privacy

Borrowed `TelemetryInterface` sinks receive closed version-one request/attempt/batch/finish events. They exclude prompt/response/reasoning text, tool payloads, vectors and raw model/context identifiers. USD amounts are estimates from reported usage and configured/historical rates, not billing; the built-in rates are historical early-2025 data. Missing usage is distinct from zero, and failed attempts can have unknown charges.

The standalone legacy telemetry helper retains raw-content behavior and is outside that safety guarantee. Optional legacy Langfuse callback support is available through the `langfuse` extra; the provider-neutral Langfuse implementation is separate queued work. Do not enable callback logging assuming it inherits the closed event schema.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
Run the focused suite:

```bash
uv run --no-sync pytest packages/friday-llm/tests_llm -q
```

The default suite is deterministic. The separately gated `test_live_lmstudio.py` lane requires an explicitly provisioned model, captured revision and live-test opt-in; it is not the quick-start validation above.
## Documentation and support

[Model library and migration](https://github.com/CIChuck/agent-framework/blob/master/docs/reference/llm/model-library-technical-spec.md) · [Telemetry contracts](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-telemetry/README.md) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-llm/src/friday_llm) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).
