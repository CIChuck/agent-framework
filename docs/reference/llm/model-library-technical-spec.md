# Friday Model Library Technical Specification

- Status: Approved for implementation with parent plan
- Date: 2026-08-28
- Parent plan: [Friday Framework typed LLM adoption plan](../../archive/completed/2026/typed-llm-0.1.0a2/framework/adoption-plan.md)
- Proposed schema: `friday.model-library/v1`
- Canonical filename: `models-config.yaml`
- Proposed release cohort: `0.1.0a2`

## Purpose

Define one reusable, provider-independent model catalog for Friday Framework.
The catalog removes repeated endpoint URLs, credential environment-variable
names, transport identity, model identity, and generation defaults from Runtime,
Friday Chat, and subsystem configuration.

Runtime configuration binds operational roles to catalog profiles. Runtime and
applications continue to own behavioral settings such as passage confidence,
memory thresholds, prompts, persistence, and lifecycle policy.

Implementation authority and the FridayV2 framework-package freeze lift were
approved with the parent plan on 2026-08-28.

## Design Summary

The solution has four typed contracts:

1. `CredentialDefinition` names an environment variable but contains no secret.
2. `EndpointDefinition` describes one reusable provider connection and default
   credential reference.
3. `ChatModelProfile` or `EmbeddingModelProfile` binds a model and operation
   dialect to an endpoint.
4. `ServiceBinding` selects a profile for a runtime role and supplies only
   allowed role-specific overrides.

Friday LLM owns these public models, their validation, profile resolution,
capability preflight, and conversion to a service specification. Runtime owns
local path resolution, YAML loading, selected-role discovery, environment
lookup, and service lifecycle.

## File Reference

Runtime configuration references the library explicitly:

```yaml
model_library:
  path: ./models-config.yaml
```

Rules:

- `path` is required for canonical profile-based configuration.
- a relative path resolves against the directory containing the referencing
  Runtime or application YAML file;
- a path never resolves relative to the process working directory;
- only a local regular file is accepted in version 1; a symlink is allowed only
  when its resolved target is a regular file, and the resolved path is retained
  for diagnostics and sibling-path resolution;
- HTTP URLs, package-resource URLs, recursive includes, and chained catalogs are
  rejected;
- `FRIDAY_MODELS_CONFIG` may replace the configured path only when Runtime's
  existing `config_policy.allow_env_override` is true;
- credential environment variables are read regardless of
  `allow_env_override`, because secret resolution is not configuration override;
- the resolved catalog is immutable for the process lifetime.

## Canonical Schema

```yaml
schema: friday.model-library/v1

credentials:
  lmstudio_default:
    env: FRIDAY_LLM_API_KEY
  openrouter_maintenance_synthesizer:
    env: FRIDAY_MAINTENANCE_SYNTHESIZER_API_KEY

endpoints:
  local_lmstudio:
    api_base: http://127.0.0.1:1234/v1
    provider: openai_compatible
    serving_engine: lm_studio
    default_credential: lmstudio_default
    resilience:
      max_retries: 2
      timeout_seconds: 90

  openrouter:
    api_base: https://openrouter.ai/api/v1
    provider: openrouter
    serving_engine: openrouter
    resilience:
      max_retries: 2
      timeout_seconds: 90

profiles:
  qwen38_chat_local:
    kind: chat
    endpoint: local_lmstudio
    dialect: openai_chat_completions
    model: openai/qwen3.8-27b-mlx
    model_target:
      model_id: qwen3.8-27b-mlx
      family: qwen3_8
      revision: exact-server-revision
    generation:
      reasoning:
        mode: enabled
        effort: medium
        preserve: false
      sampling:
        temperature: 0.2
        top_p: 0.95
        top_k: 40
      max_tokens: 8000

  nomic_embedding_local:
    kind: embedding
    endpoint: local_lmstudio
    dialect: openai_embeddings
    model: openai/nomic-embed-text-v1.5
    model_target:
      model_id: nomic-embed-text-v1.5
      family: nomic_embed
      revision: exact-server-revision
```

The names and revisions above illustrate the contract. They are not approved
capability claims until verified against the configured server and Friday LLM
profiles.

## Contract Models

### Catalog Names

Credential, endpoint, profile, and service-binding names must:

- match `^[a-z][a-z0-9_-]{0,63}$`;
- be unique within their namespace;
- remain stable across configuration revisions when identity is unchanged;
- describe deployment identity rather than a transient role where practical.

Names are case-sensitive. Aliases and implicit normalization are not supported.

### CredentialDefinition

Version 1 fields:

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `env` | string | yes | Must match `^[A-Z_][A-Z0-9_]{0,127}$`. |

No `api_key`, literal value, command, file, keyring, shell expression, template,
or remote secret provider is accepted in version 1. Those sources require a
future bounded credential-resolver contract.

### EndpointDefinition

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `api_base` | HTTP(S) URL | yes | Must not contain userinfo, query, fragment, or credential material. Loopback HTTP is allowed. |
| `provider` | bounded string | yes | Explicit provider identity; never inferred from URL. |
| `serving_engine` | bounded string or null | no | Explicit engine identity; never inferred from URL or model. |
| `default_credential` | credential name or null | no | Must reference `credentials`; omission means unauthenticated. |
| `resilience` | `ResilienceConfig` | no | Endpoint defaults only. |

An endpoint contains no operation dialect because the same API base can serve
chat completions and embeddings. The selected profile contributes the dialect;
Friday LLM alone composes the final `TransportTarget`.

### ChatModelProfile

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `kind` | literal `chat` | yes | Discriminator. |
| `endpoint` | endpoint name | yes | Must resolve. |
| `dialect` | bounded string | yes | Chat operation dialect. |
| `model` | bounded string | yes | LiteLLM route string. |
| `model_target` | `ModelTarget` | yes | Exact identity with family and revision. |
| `generation` | `GenerationConfig` | no | Provider-independent defaults. |
| `provider_options` | closed union | no | Must match the composed target. |

The route model and `model_target.model_id` must satisfy Friday LLM's explicit
identity validation. A profile cannot contain credentials or resilience.

### EmbeddingModelProfile

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `kind` | literal `embedding` | yes | Discriminator. |
| `endpoint` | endpoint name | yes | Must resolve. |
| `dialect` | bounded string | yes | Embedding operation dialect. |
| `model` | bounded string | yes | LiteLLM embedding route. |
| `model_target` | `ModelTarget` | yes | Exact model identity. |
| `embedding_options` | closed model or null | no | Only public Friday LLM embedding options. |

Embedding profiles reject `generation`, reasoning, sampling, maximum generation
tokens, chat tools, and chat provider options.

### ServiceBinding

Chat pool entry:

```yaml
llm_pool:
  default_service: chat
  services:
    chat:
      profile: qwen38_chat_local
    extraction:
      profile: qwen38_chat_local
      credential: lmstudio_default
      resilience_overrides:
        timeout_seconds: 300
      generation_overrides:
        reasoning:
          mode: disabled
        sampling:
          temperature: 0.0
        max_tokens: 8000
```

Embedding pool entry:

```yaml
embedding_pool:
  default_service: memory_embedding
  services:
    memory_embedding:
      profile: nomic_embedding_local
      resilience_overrides:
        timeout_seconds: 60
```

Allowed service-binding fields:

| Field | Chat | Embedding | Rule |
| --- | --- | --- | --- |
| `profile` | yes | yes | Required; kind must match the pool. |
| `credential` | yes | yes | Optional explicit credential reference. |
| `resilience_overrides` | yes | yes | Bounded public resilience fields only. |
| `generation_overrides` | yes | no | Typed `GenerationOverrides`; explicit fields only. |

Bindings reject `model`, `api_base`, provider, engine, dialect, targets,
provider options, and literal API keys. Changing any deployment identity
requires a different catalog profile.

## Credential Resolution

Credential selection order is:

1. `ServiceBinding.credential` when explicitly set;
2. `EndpointDefinition.default_credential`;
3. unauthenticated service when neither exists.

There is no fallback to the primary chat credential, another role, a similarly
named environment variable, or LiteLLM provider conventions.

Runtime resolves only the credentials for services reachable from the active
configuration:

- the default chat and embedding services;
- explicitly bound agents;
- enabled extraction, router, maintenance, reorganization, compaction, and
  smart-file roles;
- other explicitly enabled consumers.

The entire catalog is schema-validated, but an unused credential may be absent
from the environment. A selected credential with an unset or empty environment
variable produces a bounded startup diagnostic before service construction.

Resolved secret values use a redacted type and must not appear in:

- `repr` or `str` output;
- Pydantic/dataclass dumps;
- exception messages or validation inputs;
- configuration diagnostics;
- telemetry, logs, transcripts, or release evidence;
- hashes intended to identify non-secret catalog structure.

## Resolution Algorithm

Runtime performs these steps in order:

1. Resolve and open the local catalog path.
2. Enforce byte, YAML-depth, collection-size, and string-length bounds.
3. Parse with a strict safe YAML loader that rejects duplicate mapping keys,
   custom tags, anchors, aliases, and YAML merge keys.
4. Validate the schema identifier and all catalog objects through Friday LLM's
   public model.
5. Discover reachable service bindings from enabled Runtime/application roles.
6. Resolve each binding's profile, endpoint, and credential reference.
7. Compose provider and serving engine from the endpoint with dialect and model
   identity from the profile.
8. Merge explicitly set generation and resilience overrides.
9. Run target identity, provider-options, capability, range, and conflict
   preflight without provider I/O.
10. Resolve selected credential environment variables into redacted secrets.
11. Produce immutable `LLMServiceSpec` or `EmbeddingServiceSpec` instances.
12. Construct services through Friday LLM's public factories.

Implementations should aggregate independent startup diagnostics when safe, but
must preserve deterministic ordering by configuration path. No diagnostic may
echo the raw YAML value for a credential-related path.

## Resolution Precedence

Chat generation:

1. operation-owned typed request overrides;
2. named-service `generation_overrides`;
3. chat-profile `generation` defaults;
4. Friday LLM defaults.

Resilience:

1. named-service `resilience_overrides`;
2. endpoint `resilience` defaults;
3. Friday LLM defaults.

Credentials use the separate explicit resolution order above. Identity and
provider options do not merge and cannot be overridden by a service binding.

Only explicitly supplied fields participate. Populated model defaults do not
silently override an earlier layer.

## Bounds And Resource Safety

Initial recommended bounds:

- catalog file: at most 1 MiB;
- credentials: at most 128;
- endpoints: at most 128;
- profiles: at most 512;
- YAML nesting depth: at most 12;
- mapping/list nodes: at most 10,000;
- ordinary strings: at most 4,096 characters;
- URL: at most 2,048 characters;
- route model and revision: use Friday LLM's existing public bounds.

These are validation limits, not targets. Final constants must be centralized
and tested against oversized and alias-heavy YAML inputs.

## Current Friday Chat Migration Map

The table maps current duplicated configuration to proposed catalog and service
bindings. Names are candidates until the provider/target gate is approved.

| Current consumer | Candidate profile | Endpoint | Credential reference | Binding overrides | Required decision |
| --- | --- | --- | --- | --- | --- |
| Primary chat | `qwen38_chat_local` | `local_lmstudio` | endpoint default using current `FRIDAY_LLM_API_KEY` | none | Confirm exact served revision. |
| Extraction | `qwen36_chat_local` | `local_lmstudio` | endpoint default | temperature `0.0` or approved configured value; max tokens `8000`; timeout `300` | Reconcile current YAML temperature `0.2` with extractor's hard-coded deterministic `0.0`; verify Qwen3.6 capability profile. |
| Memory embedding | `nomic_embedding_local` | `local_lmstudio` | endpoint default | timeout `60` | Add/verify typed embedding target and dialect. |
| Passage router | `qwen36_chat_local` | `local_lmstudio` | endpoint default | reasoning policy; temperature `0.1`; max tokens `1024`; timeout `90` | Service is currently disabled; preserve no-I/O heuristic path. |
| Maintenance synthesizer | `gemini25_flash_openrouter` | `openrouter` | `openrouter_maintenance_synthesizer` | temperature `0.3`; role token/timeout policy | Verify OpenRouter/Gemini capability and structured JSON behavior. |
| Maintenance classifier | `gemini25_flash_openrouter` | `openrouter` | `openrouter_maintenance_classifier` | temperature `0.1`; role token/timeout policy | Verify structured JSON behavior. |
| Maintenance researcher | `gemini25_flash_openrouter` | `openrouter` | `openrouter_maintenance_researcher` | temperature `0.2`; role token/timeout policy | Verify structured JSON behavior. |
| Maintenance judge | unresolved pending target verification | `openrouter` | `openrouter_maintenance_judge` | temperature `0.1`; role token/timeout policy | Current `openrouter/google/gemini-3.6-flash` must be verified or corrected before becoming a profile. |
| Maintenance embedding | `nomic_embedding_local` | `local_lmstudio` | endpoint default | timeout `60` | Reuse memory embedding service if lifecycle/isolation policy permits. |
| Smart-file summarizer | `gemini25_flash_openrouter` | `openrouter` | `openrouter_smart_file_summarizer` | temperature `0.1`; max tokens `500`; timeout `30` | Preserve chunk fallback behavior. |
| Smart-file synthesizer | `gemini25_flash_openrouter` | `openrouter` | `openrouter_smart_file_synthesizer` | temperature `0.3`; max tokens `1000`; timeout `60` | Preserve synthesis fallback behavior. |

The mapping does not consolidate existing OpenRouter credentials automatically.
It centralizes their environment-variable names while preserving role isolation.
Operators may intentionally point multiple credential definitions to the same
environment variable, but Friday must not assume they are interchangeable.

## Canonical Application Shape

After migration, Friday Chat's provider-related configuration becomes reference
oriented:

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
        reasoning:
          mode: disabled
        sampling:
          temperature: 0.0
        max_tokens: 8000
      resilience_overrides:
        timeout_seconds: 300
    passage_router:
      profile: qwen36_chat_local
      generation_overrides:
        reasoning:
          mode: disabled
        sampling:
          temperature: 0.1
        max_tokens: 1024

embedding_pool:
  default_service: memory_embedding
  services:
    memory_embedding:
      profile: nomic_embedding_local

extraction:
  llm_service: extraction
  interval: 3
  rejection_log: .friday/vector/extraction_rejections.log
  ontology: {}

memory:
  passage_router:
    enabled: false
    llm_service: passage_router
    min_confidence: 0.6
    fallback_mode: heuristic
```

Maintenance and smart-file role sections follow the same `llm_service`
reference pattern. Prompts and behavioral policy remain in their owning
sections.

## Legacy Compatibility

During `0.1.x`:

- existing inline Runtime and Friday Chat provider blocks remain accepted;
- each legacy path produces one actionable startup diagnostic;
- a canonical profile binding cannot mix with inline model, endpoint,
  credential, target, generation, or provider-options fields;
- mixed reference/inline identity is rejected as ambiguous rather than merged;
- legacy inline secrets are supported only for compatibility and remain
  redacted;
- canonical examples use only the model library;
- compatibility fixtures remain explicitly labeled non-canonical;
- removal is not earlier than `0.2.0` and requires a separate plan.

## Diagnostics

Required stable diagnostic categories include:

- `model_library.not_found`;
- `model_library.not_regular_file`;
- `model_library.too_large`;
- `model_library.invalid_yaml`;
- `model_library.unsupported_schema`;
- `model_library.unknown_credential`;
- `model_library.unknown_endpoint`;
- `model_library.unknown_profile`;
- `model_library.profile_kind_mismatch`;
- `model_library.target_identity_mismatch`;
- `model_library.unsupported_control`;
- `model_library.incompatible_provider_options`;
- `model_library.missing_selected_credential`;
- `model_library.legacy_inline_config`.

Messages identify the catalog and runtime paths, not secret values, messages,
tool arguments, provider payloads, or reasoning content.

## Required Tests

### Model And Resolver Tests

- valid minimal authenticated and unauthenticated catalogs;
- chat and embedding discriminated profiles;
- duplicate and invalid names;
- unknown credential, endpoint, and profile references;
- route/target identity mismatch;
- chat profile in embedding pool and embedding profile in chat pool;
- embedding profile containing generation controls;
- provider-options mismatch;
- explicit versus endpoint-default credential;
- unused missing credential accepted;
- selected missing/empty credential rejected;
- explicit-field-only generation and resilience merges;
- unsupported and conflicting controls fail before service construction;
- immutable resolved snapshot and redacted dumps/reprs.

### Loader Tests

- path relative to referencing config rather than current working directory;
- missing, directory, dangling/non-file symlink, unreadable, oversized,
  malformed, and unsupported-schema files;
- accepted regular-file symlink resolves once to a stable diagnostic base;
- remote URL and include rejection;
- duplicate-key, custom-tag, anchor, alias, merge-key, depth, and node rejection;
- `FRIDAY_MODELS_CONFIG` obeys `allow_env_override`;
- secret lookup remains available when configuration override is disabled;
- deterministic path-ordered diagnostics.

### Runtime And Consumer Tests

- one endpoint reused by chat and embedding profiles;
- one model profile reused by multiple roles with isolated overrides;
- one endpoint/profile reused with distinct role credentials;
- disabled passage routing does not require its unselected credential or create
  a service;
- maintenance mutation keeps explicit no-primary-credential-fallback behavior;
- typed final-wire kwargs match every resolved role;
- no role receives another role's generation, resilience, credential, or
  provider options;
- startup preflight performs no provider I/O;
- canonical Friday Chat startup emits zero migration warnings.

### Packaging Tests

- repository and packaged `models-config.example.yaml` stay synchronized;
- package data contains the example catalog;
- copied Runtime/Friday Chat examples resolve sibling catalog paths from an
  installed wheel or generated configuration directory;
- wheels and sdists contain no secret values or local endpoint state;
- clean installs resolve all exact candidate dependencies.

## Decisions Required Before Implementation

The parent plan recommends these defaults:

1. approve `models-config.yaml` and `friday.model-library/v1` as the canonical
   names;
2. keep credential definitions separate from endpoints so roles can share an
   endpoint/profile while retaining least-privilege keys;
3. support chat and embedding profiles in one catalog but separate service
   specifications and factories;
4. use explicit sibling-file references with no implicit search path;
5. preserve legacy inline configuration through `0.1.x`;
6. require authoritative verification of every maintained provider/model target
   before it enters a canonical example;
7. resolve the extraction temperature conflict and maintenance judge model
   identity before configuration conversion.

Approval of this specification should be bundled with approval of the parent
framework plan, feature branch, FridayV2 freeze lift, and provisional
`0.1.0a2` cohort.
