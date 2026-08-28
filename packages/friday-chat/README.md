# Friday Chat

Terminal chat application for the Friday Framework.

Friday Chat provides the user-facing command-line chat experience built on the
Friday runtime, memory, agent, LLM, transcript, and tools packages.

## Install

```bash
pip install friday-chat==0.1.0a1
```

## Run

```bash
friday-chat --help
```

## Import Package

```python
import friday_chat
```

## Primary LLM Configuration

Friday Chat `0.1.0a1` uses Friday LLM's typed, provider-independent generation
configuration on the primary chat path. Target identity is explicit so Friday
does not infer provider capabilities from a model name or endpoint URL.

```yaml
llm:
  model: openai/qwen3.8-27b-mlx
  api_base: http://127.0.0.1:1234/v1
  api_key: ${FRIDAY_LLM_API_KEY}
  max_retries: 3
  timeout_seconds: 120.0
  generation:
    reasoning:
      mode: enabled
      effort: medium
      preserve: false
    sampling:
      temperature: 0.2
      top_p: 0.95
      top_k: 40
      min_p: 0.0
      presence_penalty: 0.0
      frequency_penalty: 0.0
      repetition_penalty: 1.0
    max_tokens: 8000
  transport_target:
    provider: openai_compatible
    dialect: openai_chat_completions
    serving_engine: lm_studio
  model_target:
    model_id: qwen3.8-27b-mlx
    family: qwen3_8
    revision: lmstudio-community/Qwen3.8-27B-MLX-8bit
```

Replace the revision with the exact artifact served by your local endpoint.
Friday LLM `0.1.0a1` provides the built-in normalized reasoning profile for
LM Studio, OpenAI-compatible Chat Completions, and Qwen3.8. Other transports
continue to work through the legacy path but are not automatically assigned
this capability profile.

Provider-specific controls, when needed, use a bounded `provider_options`
object with an explicit namespace. Arbitrary provider keyword dictionaries are
not accepted. Prefer normalized `generation` fields when they express the same
intent.

### Legacy Compatibility

The former flat fields remain accepted through the `0.1.x` compatibility
window:

| Legacy field | Canonical field |
| --- | --- |
| `llm.temperature` | `llm.generation.sampling.temperature` |
| `llm.top_p` | `llm.generation.sampling.top_p` |
| `llm.top_k` | `llm.generation.sampling.top_k` |
| `llm.max_tokens` | `llm.generation.max_tokens` |
| `llm.thinking` | `llm.generation.reasoning.mode` |

Legacy configurations without explicit targets retain their previous behavior
and produce startup migration diagnostics. With explicit targets, flat fields
are converted to typed generation controls. Equal flat and nested values are
accepted with a diagnostic; contradictory values fail before provider I/O.

`top_p` and `top_k` were present in earlier Friday Chat YAML but were not
forwarded by its legacy adapter. They become effective on the typed path. Wire
emission proves forwarding, not that every endpoint behaviorally honors the
setting.

## License

MIT
