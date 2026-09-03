# Friday Chat

Terminal chat application for the Friday Framework.

Friday Chat provides the user-facing command-line chat experience built on the
Friday runtime, memory, agent, LLM, transcript, and tools packages.

## Install

```bash
pip install friday-chat==0.1.0a2
```

## Run

```bash
friday-chat --help
```

## Import Package

```python
import friday_chat
```

## Model Library Configuration

Friday Chat `0.1.0a2` uses one provider-independent model library for primary
chat, extraction, passage routing, compaction, maintenance, embeddings, and
smart-file processing. Copy both packaged examples into the same directory,
rename the model library if desired, and keep its path relative to the runtime
configuration file.

```yaml
model_library:
  path: ./models-config.yaml
llm_pool:
  default_service: chat
  services:
    chat:
      profile: qwen38_chat_local
    extraction:
      profile: qwen36_chat_local
      generation_overrides:
        reasoning: {mode: disabled}
        sampling: {temperature: 0.0}
        max_tokens: 8000
embedding_pool:
  default_service: memory
  services:
    memory:
      profile: nomic_embedding_local
extraction:
  llm_service: extraction
embedding:
  embedding_service: memory
```

The referenced `models-config.yaml` stores reusable endpoint and model identity,
but never a secret value:

```yaml
schema: friday.model-library/v1
credentials:
  local_lmstudio:
    env: FRIDAY_LLM_API_KEY
endpoints:
  local_lmstudio:
    api_base: http://127.0.0.1:1234/v1
    provider: openai_compatible
    serving_engine: lm_studio
    default_credential: local_lmstudio
profiles:
  qwen38_chat_local:
    kind: chat
    endpoint: local_lmstudio
    dialect: openai_chat_completions
    model: openai/qwen3.8-27b-mlx
    model_target:
      model_id: qwen3.8-27b-mlx
      family: qwen3_8
      revision: replace-with-exact-served-revision
```

Export every credential selected by an enabled service before startup. The
packaged example uses `FRIDAY_LLM_API_KEY`, `FRIDAY_OPENROUTER_API_KEY`, and
`FRIDAY_MOONSHOT_API_KEY`. If you maintain a local `.env`, source it first;
Friday Chat does not load `.env` files implicitly. For hosted providers, define
a credential entry whose `env` names the provider key and select that credential
from each least-privilege service binding. Never put the key itself in either
YAML file.

Friday LLM provides the built-in normalized reasoning profile for LM Studio,
OpenAI-compatible Chat Completions, and Qwen3.8. Other transports continue to
work through compatibility behavior but are not automatically assigned that
capability profile.

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
