# Friday Chat

Terminal chat application for the Friday Framework.

Friday Chat provides the user-facing command-line chat experience built on the
Friday runtime, memory, agent, LLM, transcript, and tools packages.

## MCP client tools

The distributed `config.example.yaml` and packaged
`src/friday_chat/config_templates/config.example.yaml` include the same
default-disabled MCP stanza. Copy the runtime example to an editable config
outside the package, then configure a trusted local stdio server under
`tools.providers.mcp`. Run
`friday-chat --config /path/to/config.yaml --runtime real` to use real
providers; the CLI's default fake runtime does not connect
to MCP peers. The [MCP client guide](../../docs/guides/17-mcp-client.md) has a
checkout-local peer example and the exact selected-mode tool-name filter.

Friday Chat selects registered tools per turn. MCP schema tokens and result
reservation reduce the remaining memory retrieval budget while preserving its
configured floor. Checked, bounded tool results can appear in transcript
records; direct MCP long-term memory ingestion remains disabled until an
explicit sanitized server/tool opt-in. Diagnostics are available through the
MCP provider owner; no Chat MCP health command is present. Keep secrets in
process environment variables, not the editable YAML or runtime state
directory. External `config_file` includes and integrated remote transports
are deferred.

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

### Local telemetry

Chat telemetry defaults to disabled. Enable the local diagnostic provider with:

```yaml
telemetry:
  enabled: true
  provider: debug
```

The CLI reports telemetry state at startup. Embedded applications can inspect
`runtime.telemetry.snapshot()` for immutable runtime/application lifecycle and
validated MCP and LLM event records. The observer retains the newest 256 records and
cumulative drop, rejection, and delivery-failure counts; these records remain in
process memory. A failed injected sink remains visible as `failed`, while Chat
continues operating and local inspection remains available.

`build_runtime(config, telemetry=provider)` accepts any existing
`TelemetryInterface` implementation as a caller-owned override, including when
YAML telemetry is disabled. Chat wraps it with the same typed content boundary
and never closes it. Only allowlisted lifecycle, MCP and closed version-one LLM attributes are
forwarded. Prompts, responses, reasoning, memory, schemas, arguments, results,
paths, exception messages, and raw session identifiers are excluded.

The real framework runtime passes the same enabled observer to primary chat,
embedding, extraction, passage routing, compaction, SmartFileRead and explicit
maintenance services, through canonical pools and legacy configuration. Disabled
assembly passes `None`. Construction creates no LLM request or exporter. Roles
identify constructed services: legacy extraction can alias `maintenance_default`,
and compaction can alias `maintenance_researcher` or the default. Shared instances
keep their role rather than being relabelled by concurrent consumers.

LLM events contain generated request/attempt/batch identities, truthful reported
usage and bounded timing/cost estimates; no LLM span remains open across stream
yields. Built-in pricing is historical early-2025 data, not current billing, and
failed attempts may have unknown charges. Turn correlation and local execution
metrics are described below. Remote exporter assembly and optional Langfuse
compatibility remain later work. The `langfuse`
section is not activated by local telemetry. Unsupported telemetry providers and
fields fail config validation; the shared framework telemetry defaults and
raw transcript capture settings are unchanged.

## Execution diagnostics

Enabled Chat telemetry links one opaque turn reference across model requests,
native/MCP dispatch, memory retrieval, and the existing persistence path. Tool
failure records retain their failed/blocked meaning. Intermediate persistence
completion is distinct from full-turn success; these observations do not promise
atomic rollback or durable commit acknowledgements absent from the underlying API.
The accepted MCP receipt/publication events preserve pending versus published truth.

`TurnResult.correlation_context` and `PendingExtractionTurn.correlation_context`
are optional, immutable, process-local origin metadata. Background extraction
rebinds each item's origin independently and preserves retry/requeue behavior,
including committed extraction followed by cancellation. Old/custom results and
work items default to uncorrelated behavior. Borrowed sinks remain caller-owned.

Existing `/debug` and `/timing` now include safe last-turn outcome/persistence and
bounded execution counters, even for failed turns without a result. Snapshots
retain at most256 event records,32 terminal summaries,128 active spans and fixed
operation/outcome histogram labels. They contain no prompt, reasoning, tool
arguments/results/names, memory/document contents, paths, raw IDs or exception text.
Diagnostics remain available with remote exporters off or failing. Disabled
telemetry preserves prior invocation behavior and produces no execution events.


Execution spans deliver synchronous sink calls in private per-frame contexts.
Active owned children retain explicit parents; independent background items,
including explicit absent origins, cannot inherit a foreground sink stack. None
origins emit session-only facts and do not contribute to foreground accounting.
Known rejected MCP calls use trusted membership for their closed rejection counts.
Execution schema versions require actual integer1, including forged-instance entry.
Acquired close-capable model iterators are explicitly awaited before terminal return
through direct, legacy and typed stream paths. Cleanup preserves an active callback,
model or cancellation exception; chunk ordering, heartbeat and buffering stay intact.
