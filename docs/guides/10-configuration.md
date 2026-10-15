---
title: Configuration reference
description: Separate Chat, headless Runtime, model-library and display configuration with current schemas and ownership.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: reference
---

# Configuration reference

Friday configuration belongs to the application that loads it. Friday Chat YAML,
headless Runtime YAML, agent profiles, workflows and display settings are
different schemas. Do not merge an old example into a new application merely
because both files are called `config.yaml`.

## Files and loaders

| File/type | Loader/owner | Purpose |
| --- | --- | --- |
| Chat runtime YAML | `friday_chat.config.load_friday_py_config()` | Models, memory, tools, sessions and optional integrations for Chat |
| Headless Runtime YAML | `RuntimeConfig.from_yaml()` / `from_sources()` | Service pools, runtime paths, profiles, workflows and headless policies |
| `models.yaml` | Application loader plus `friday_llm.ModelLibrary` | Reusable endpoint/model identity and credential references |
| `cli-config.yaml` | Chat display resolver | Terminal prompt, banners, responses, icons and spinners |
| `agents/*.yaml` | `AgentLoader` | Validated profiles; see [agents](06-agents.md) |
| Workflow files/bundles | `WorkflowLoader` | Flat or canonical workflow definitions; see [workflows](08-workflows.md) |

All examples below target **0.1.0a3**. Fragments identify their owning schema.
Unknown Chat top-level sections are diagnosed and omitted by its loader;
some nested sections deliberately accept flexible mappings. Headless Runtime
has stricter allowed-key validation. A successful YAML parse alone is not a
runtime capability check.

## Canonical model library

Use the strict `friday.model-library/v1` schema for new multi-role applications.
It separates credential references, endpoints, model profiles and application
service bindings. Profiles have kind `chat` or `embedding`; bind a role to a
profile of the matching kind.

The following is a **complete loadable example model library**, `models.yaml`.
It describes a local LM Studio setup; replace the model aliases/revisions with
those actually served before making a live call. The identifiers are examples,
not a promise that your server has those models loaded.

```yaml
schema: friday.model-library/v1
credentials:
  local:
    env: FRIDAY_LOCAL_MODEL_KEY
endpoints:
  local:
    api_base: http://127.0.0.1:1234/v1
    provider: openai_compatible
    serving_engine: lm_studio
    default_credential: local
    resilience:
      max_retries: 2
      timeout_seconds: 60
profiles:
  chat_local:
    kind: chat
    endpoint: local
    dialect: openai_chat_completions
    model: openai/qwen3.8-27b-mlx
    model_target:
      model_id: qwen3.8-27b-mlx
      family: qwen3_8
      revision: replace-with-served-model-revision
    generation:
      reasoning:
        mode: disabled
      sampling:
        temperature: 0.2
      max_tokens: 2000
  embedding_local:
    kind: embedding
    endpoint: local
    dialect: openai_embeddings
    model: openai/nomic-embed-text-v1.5
    model_target:
      model_id: nomic-embed-text-v1.5
      family: nomic_embed
      revision: replace-with-served-embedding-revision
```

`env` contains the **name** of a process environment variable. Supply a value
appropriate for the server, including a deliberate non-secret placeholder if
your explicitly local server requires one. Never copy a hosted secret into
this file. Resolved service specs protect credential representation, but other
application config snapshots/logs can still be sensitive.

Friday LLM resolves profiles without owning file lookup. Chat and Runtime read
the model-library file and resolve relative paths against the owning YAML file.
Unused credential declarations do not require a value merely by existing;
every actually resolved service with a selected credential does.

## Bind models to Chat roles

Save this **complete canonical Chat configuration** next to `models.yaml` as
`config.yaml`. All chat roles deliberately reuse one profile to keep the
example small. This is valid assembly configuration, not recommended tuning
for every role or evidence that the live model is available.

```yaml
model_library:
  path: ./models.yaml
llm_pool:
  default_service: chat
  services:
    chat: {profile: chat_local}
    extraction: {profile: chat_local}
    passage_router: {profile: chat_local}
    compaction: {profile: chat_local}
    synthesizer: {profile: chat_local}
    classifier: {profile: chat_local}
    researcher: {profile: chat_local}
    judge: {profile: chat_local}
    smart_file_summarizer: {profile: chat_local}
    smart_file_synthesizer: {profile: chat_local}
embedding_pool:
  default_service: memory
  services:
    memory: {profile: embedding_local}
    maintenance: {profile: embedding_local}
embedding:
  embedding_service: memory
extraction:
  llm_service: extraction
  interval: 3
chat:
  user_name: User
  assistant_name: Friday
  system_prompt: You are Friday. Use source evidence and disclose uncertainty.
memory:
  persist_directory: ./state/vector
  collection_name: memories_long_term
  context_window: 32000
  output_buffer: 2500
  max_history_turns: 15
  context_format: markdown
  compaction:
    enabled: false
  priming:
    enabled: true
    previous_sessions: 1
    previous_session_turns: 3
    token_budget: 4000
transcript:
  export_directory: ./state/exports
  capture_raw_prompts: false
tools:
  enabled: false
  registry: []
  providers:
    mcp:
      enabled: false
      config:
        servers: []
telemetry:
  enabled: false
langfuse:
  enabled: false
speech:
  enabled: false
lifecycle:
  enabled: false
session:
  flush_on_exit: true
  lifecycle_on_exit: false
  reorganize_on_exit: false
```

Keep the process working directory stable: Chat's relative data, export and
workflow paths are not all rebased against the config directory. The
`model_library.path` rule above is specifically implemented for that reference.
Use explicit absolute state paths for desktop launchers. See [desktop deployment](16-desktop-deployment.md).

This **offline Python example** resolves both files with a synthetic environment
and prints only non-secret identifiers. It constructs no runtime:

```python
from friday_chat.config import load_friday_py_config

config = load_friday_py_config("config.yaml", env={
    "FRIDAY_LOCAL_MODEL_KEY": "local-example-placeholder",
})
print(config.llm_pool.default_service)
print(sorted(config.embedding_service_specs))
```

Expected output: `chat` and `['maintenance', 'memory']`. This validates loading
and resolution, not connectivity. Start a **live session** only after provisioning
the endpoints and exporting the selected credential:

```bash
friday-chat --config config.yaml --runtime real
```

## Role-specific overrides and generation controls

Service bindings can add `resilience_overrides` and `generation_overrides`.
This is a **Chat `llm_pool.services` fragment**, replacing a binding above:

```yaml
extraction:
  profile: chat_local
  resilience_overrides:
    timeout_seconds: 90
  generation_overrides:
    reasoning: {mode: disabled}
    sampling: {temperature: 0.0}
    max_tokens: 1500
```

Separate transport identity (`provider`, dialect, serving engine) from model
identity (`model_id`, family, revision). Built-in normalized reasoning/sampling
capability support is specifically LM Studio + OpenAI-compatible Chat Completions
+ Qwen3.8. Other LiteLLM routes remain compatibility paths; transport support
does not establish that every normalized option works on each provider/model.
Unsupported controls fail preflight rather than silently disappearing.

On typed requests, omitted fields inherit service defaults; explicit `None`
clears a default and delegates to the provider. Typed calls do not inject the
legacy temperature 0.7 default. Preserve reasoning as separate events/content
when using the typed streaming API; it is not user-facing response text.

Legacy `llm.model`, `api_base`, `temperature`, `thinking` and related flat
provider sections remain compatibility configuration in 0.1.x. Mixed old/new
controls can be rejected when contradictory and diagnosed when redundant.
Use [the model-library migration contract](../reference/llm/model-library-technical-spec.md)
instead of adding global LiteLLM `drop_params` or `modify_params` mutations.
The installed Friday LLM dependency is pinned to LiteLLM 1.100.1.

## Chat sections and responsibilities

| Section | Relevant fields | Notes |
| --- | --- | --- |
| `logging` | `level`, extraction/tool debug and rejection logging | Content-bearing logs need retention/access policy |
| `extraction` | `llm_service`, `interval`, `ontology`, `prompt`, `rejection_log` | Interval 0 schedules each turn, positiveN everyNth turn, -1 disables interval scheduling; explicit flushes are separate |
| `embedding` | `embedding_service` | Selects a configured embedding role |
| `memory` | Persistence, retrieval, context window, output buffer, history, priming, supporting context, compaction | [Memory guide](04-adaptive-memory.md) and [budget guide](memory-management-guidelines.md) |
| `transcript` | `export_directory`, `capture_raw_prompts` | Capture defaults false in the model; broad template sets true |
| `tools` | `enabled`, `registry`, `providers`, `context`, `loop` | Registry membership, per-turn selection and execution limits differ |
| `web` | Client, SSL, proxy, security, reader and search credentials | Generic web policy is separate from strict MCP HTTPS policy |
| `maintenance` | Backup location, pruning/synthesis/verification roles, defaults/logging | Can call models and mutate stores; coordinated preflight applies |
| `lifecycle` | Enablement, decay/promotion settings, access buffer, factor computer | Template values are not identical to library defaults |
| `session` | `flush_on_exit`, `lifecycle_on_exit`, `reorganize_on_exit`, `reorganize_mode` | Exit may perform configured processing; allow shutdown to settle |
| `security` | `sanitization` | Core scanner vocabulary and Chat command vocabulary differ; see [security](security-configuration-guidelines.md) |
| `telemetry` | `enabled`, `provider: debug` | Bounded local Chat diagnostics; default disabled |
| `langfuse` | Legacy enablement/public key/secret key/host | Separate callback compatibility; new provider-neutral integration queued |
| `speech` | Enablement/providers/mode/selection/chunking/playback | See [speech](speech.md); hardware/provider calls require explicit setup |
| `finance` | `massive` credentials/tier | Provider entitlement and runtime exceptions need inspection |
| `smart_file` | Chunking, source handling, LLM roles/prompts | Reading and persisting are distinct choices |
| `chat` | User/assistant identity, system prompt, workflow directory compatibility fields | Identity is application configuration, not authentication |

## Secrets and environment precedence

Chat ordinary `${NAME}` strings are interpolated from the provided/process
environment **before** validation, including ordinary disabled sections.
Missing references fail loading. Unknown top-level sections can still contain
strings traversed during interpolation. Removing an unused integration's key
without removing its placeholder is insufficient.

MCP HTTP `credential_env: FRIDAY_REMOTE_MCP_TOKEN` is a literal identifier,
validated before interpolation and resolved only by enabled connection assembly.
It must never be `${...}`, a token or an inline credential. Stdio peer `env`
values have the ordinary Chat interpolation behavior. Headless Runtime callers
must supply secret values through their own documented loading/assembly path;
do not assume Chat's interpolation applies to all libraries.

`FRIDAY_CHAT_RUNTIME` overrides the CLI runtime-mode argument. `--config` is the
explicit Chat file selector; do not assume `FRIDAY_CONFIG` or an OS config
directory is automatically searched. Display resolution has its own
`--cli-config` handling. `.env` is not loaded implicitly by Chat.

## Headless Runtime configuration

`RuntimeConfig.from_sources(yaml_path=..., env=..., overrides=...)` merges
defaults, YAML, allowed environment overrides and explicit overrides. YAML
environment override policy is controlled by `config_policy.allow_env_override`;
the library default is false. Do not apply that precedence rule to Chat's
separate parser.

Headless sections include `runtime_paths`, `config_policy`, `model_library`,
`llm_pool`, `embedding_pool`, `agents`, `workflows`, `memory`, `transcript`,
`scratch`, `artifacts`, `tools` and telemetry. For example, this **headless
configuration fragment** names explicit application paths:

```yaml
runtime_paths:
  install_root: /opt/friday/install
  workspace_root: /srv/friday/workspace
  runtime_data_root: /srv/friday/state
  cache_root: /srv/friday/cache
config_policy:
  allow_env_override: false
  strict_agent_llm_binding: true
  workflow_mode: canonical
agents:
  dir: /srv/friday/profiles
  role_bindings:
    researcher: researcher
workflows:
  dir: /srv/friday/workflows
```

Create existing install/workspace roots and writable state/cache parents before
validation. Runtime state must not overlap the workspace; transcript, persistent
scratch and artifact paths have containment rules under runtime data. The
[offline construction example](03-core-concepts.md#runtime-composition-and-ownership)
shows a valid temporary layout without starting services.

Common headless environment mappings include `FRIDAY_LLM_MODEL`,
`FRIDAY_CHROMA_PATH`, `FRIDAY_CHROMA_COLLECTION`, `FRIDAY_TELEMETRY_ENABLED`,
`FRIDAY_INSTALL_ROOT`, `FRIDAY_RUNTIME_DATA_ROOT`, `FRIDAY_WORKSPACE_ROOT` and
`FRIDAY_CACHE_ROOT`. The [Runtime schema](../../packages/friday-runtime/src/friday_runtime/config.py)
is authoritative for the allowlist and override behavior.

## MCP configuration

Use `tools.providers.mcp`, default disabled, in the application YAML. Configure
stdio `protocol_profile: legacy|modern|auto` explicitly when needed. HTTPS
Streamable HTTP requires a dated version, global remote security opt-ins,
per-peer remote trust and its own credential/network policy. HTTP+SSE is the
retained legacy API, not the newest integrated transport.

The [MCP client guide](17-mcp-client.md) owns complete valid stanzas and limits;
[migration](19-mcp-migration.md) owns the protocol matrix. An external
`config_file` include is rejected. This client stanza does not expose Friday
as an MCP server.

## Telemetry configuration and Langfuse

This **Chat fragment** enables local categorical diagnostics:

```yaml
telemetry:
  enabled: true
  provider: debug
```

Chat retains a bounded local execution view and accepts borrowed
`TelemetryInterface` injection through `build_runtime`. It does not close the
borrowed provider. Closed LLM/MCP/execution events exclude raw content; generic
caller events, transcripts, logs and legacy helpers have different guarantees.

For library-owned providers, `create_telemetry(TelemetryFactoryConfig(...))`
returns an owned handle. Optional OpenTelemetry supports console and explicitly
configured OTLP/gRPC, verified TLS and bounded lifecycle reporting. That is not
an automatic Chat exporter selector or ambient global-tracer integration.

The telemetry rewire and queued Langfuse implementation are separate board
items. The legacy `langfuse` YAML/extra is not the new provider-neutral backend.
See [telemetry ownership and limits](11-advanced-topics.md#telemetry-ownership-and-exporters).

## Validate configuration changes

Load/resolve configuration without constructing services first. Inspect
diagnostics without printing credentials or entire resolved objects. Next,
test a disposable real session for each enabled service and restart persistence.
Finally exercise the required tools and shutdown path. Schema validity,
provider connectivity and correct application behavior are three distinct checks.

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
