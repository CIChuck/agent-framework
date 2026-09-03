# Friday Framework Typed LLM Adoption Plan

- Status: Published to production PyPI and post-publication verified
- Date: 2026-08-28
- Approval date: 2026-08-28
- Implementation completion date: 2026-08-28
- Branch: `feature/friday-framework-typed-llm-adoption`
- Proposed release cohort: `0.1.0a2`
- Upstream baseline: `friday-framework-llm==0.1.0a1`
- Registry verification: official PyPI JSON checked 2026-08-28 for all 17
  distributions; every distribution currently publishes through `0.1.0a1`, so
  `0.1.0a2` is available for the proposed cohort.
- Predecessors:
  - [Friday LLM reasoning and sampling controls requirement](../friday-llm/friday-llm-reasoning-and-sampling-controls-requirement.md)
  - [Friday Chat typed LLM migration plan](../friday-chat/friday-chat-typed-llm-config-migration-tactical-plan.md)
  - [Friday Chat deferred consumer handoff](../friday-chat/friday-chat-typed-llm-deferred-consumer-handoff.md)
  - [Friday package cohort 0.1.0a1 plan](friday-package-cohort-0.1.0a1-plan.md)
- Companion specification:
  - [Friday model library technical specification](friday-model-library-technical-spec.md)

## Objective

Extend Friday LLM's normalized generation, explicit target identity, capability
preflight, provider-options, typed request, typed response, streaming-event, and
assurance features to every appropriate Friday Framework consumer. Preserve
provider independence, eliminate scattered provider construction, and publish
one installable lock-step package cohort.

This is a framework migration, not a YAML-only rewrite. Configuration must not
advertise typed controls until the service constructed from that configuration
actually receives the corresponding `GenerationConfig`, `TransportTarget`, and
`ModelTarget` and validates them before provider I/O.

## Why A Framework-Wide Upgrade Is Required

Friday Chat's primary LLM is typed, but the remaining graph is inconsistent:

- Friday Runtime constructs every `llm_pool` service without generation
  defaults or explicit target identity.
- Friday Memory directly constructs or consumes LLM services for extraction,
  passage routing, consolidation, compaction, synthesis, fact checking,
  reorganization, lifecycle processing, and large-file ingestion.
- Friday Chat still constructs separate legacy services for extraction,
  maintenance roles, passage routing, compaction, reorganization, and smart-file
  processing.
- Friday Agent and Friday Tools call the legacy `LLMClient.chat_completion()`
  interface with flat per-call controls.
- Friday CLI exposes Runtime's composition and compatibility configuration.
- exact `0.1.0a1` pins propagate every contract change through the complete
  17-distribution package graph.

Updating example files before these construction and call paths are migrated
would produce accepted-but-ignored settings, contradictory defaults, or typed
preflight failures on the first request.

## Authority And Freeze Boundary

This document authorizes no implementation, branch creation, release, network
call, or publication by itself.

The current FridayV2 parity boundary freezes existing framework package source
outside `packages/friday-chat`. Implementing this plan requires an explicit
approval that opens a new framework-upgrade phase and permits the package paths
listed below. Until then, any discovered framework requirement belongs in the
FridayV2 framework-upgrade log rather than source.

Implementation should occur on the proposed feature branch. PyPI upload, Git
push, merge, tag creation, live-provider testing, and cleanup remain separate
authority gates.

## Governing Design Decisions

### One Owner For LLM Semantics

`friday-framework-llm` remains the sole owner of:

- `GenerationConfig`, `GenerationOverrides`, `ReasoningConfig`, and
  `SamplingConfig`;
- `TransportTarget`, `ModelTarget`, and execution-target validation;
- capability records, composition, and preflight;
- provider-specific bounded options and translation;
- typed request, response, streaming event, assurance, retry, and transport
  behavior.

No application or framework consumer may create its own provider capability
registry, infer a target from a model name or URL, or expose unrestricted
provider keyword arguments.

### One Public Service Specification

Friday LLM will add and export strict reusable chat and embedding service
specifications, provisionally named `LLMServiceSpec` and
`EmbeddingServiceSpec`. The chat specification contains:

- the LiteLLM route model;
- endpoint and credential references;
- `ResilienceConfig`;
- normalized generation defaults;
- explicit transport and model targets;
- a closed union of public provider-options models.

Friday LLM will also expose one supported construction path for each service,
such as `LiteLLMService.from_spec(...)` and
`LiteLLMEmbeddingService.from_spec(...)`. The final API names are decided in the
Friday LLM work package, but every downstream package must consume the same
public APIs.
Applications may wrap this model to add subsystem behavior, but may not copy its
LLM fields or validation rules.

Credential fields must be redacted from representations, diagnostics, model
dumps, and validation errors. Environment interpolation remains an application
or Runtime concern; unresolved placeholders fail before service construction.

### Central Model Library

The normative release-one schema and migration mapping are defined in the
[Friday model library technical specification](friday-model-library-technical-spec.md).

Runtime and application configuration will reference a versioned local model
library, canonically named `models-config.yaml`, instead of repeating endpoint,
credential, target, and model identity under every role.

Friday LLM will own and export the strict library models and pure resolver.
Runtime will own path resolution, file loading, environment access, role
binding, and startup diagnostics. This keeps provider semantics in Friday LLM
without making it responsible for application filesystem policy.

The library has three non-recursive layers:

- **credentials** contain only validated environment-variable names, never
  secret values;
- **endpoints** contain a reusable API base, optional default credential
  reference, provider, serving engine, and resilience defaults;
- **profiles** declare `kind: chat` or `kind: embedding`, bind one route model
  and model target to one endpoint, supply the operation dialect, and may add
  only options valid for that kind.

A profile is a deployable model target, not merely a model-family name. The same
weights served by LM Studio and vLLM require separate profiles because serving
engine and dialect affect capabilities and wire translation.

Canonical `models-config.yaml` structure:

```yaml
schema: friday.model-library/v1

credentials:
  local_lmstudio:
    env: FRIDAY_LMSTUDIO_API_KEY

endpoints:
  local_lmstudio:
    api_base: http://127.0.0.1:1234/v1
    default_credential: local_lmstudio
    provider: openai_compatible
    serving_engine: lm_studio
    resilience:
      max_retries: 2
      timeout_seconds: 90

profiles:
  qwen38_local:
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
```

An embedding profile can reuse `local_lmstudio` with
`kind: embedding` and its embedding dialect/model target, but it cannot contain
`generation` or chat provider options. Friday LLM's resolver composes the
endpoint provider and serving engine with the profile dialect; downstream
packages do not assemble a `TransportTarget` themselves.

Canonical Runtime `config.yaml` structure:

```yaml
model_library:
  path: ./models-config.yaml

llm_pool:
  default_service: chat
  services:
    chat:
      profile: qwen38_local
    extraction:
      profile: qwen38_local
      generation_overrides:
        reasoning:
          mode: disabled
        sampling:
          temperature: 0.0
        max_tokens: 8000

memory:
  extraction:
    enabled: true
    llm_service: extraction
```

The library is loaded once into an immutable snapshot at startup. In release
one it does not support remote URLs, recursive includes, profile inheritance,
hot reload, or arbitrary deep merges. The library path resolves relative to the
referencing runtime configuration file, never the process working directory.

Each `credentials.*.env` field stores only a validated environment-variable
name; it never stores the credential. A named-service binding may select a
different credential reference than the endpoint default, allowing multiple
least-privilege keys for one provider endpoint without duplicating the endpoint
or model profile. Missing credentials are checked only for enabled, selected
service bindings so an unused catalog entry does not prevent startup. An
endpoint that genuinely requires no authentication omits `default_credential`;
it must not use a fabricated credential to pass validation.

Credential selection is deterministic: an explicit named-service credential
reference wins, otherwise the endpoint's `default_credential` is used, otherwise
the service is unauthenticated. There is no implicit primary-service credential
fallback.

Resolving a selected credential is distinct from allowing environment values to
override configuration. Runtime reads the named secret even when
`config_policy.allow_env_override` is false, but that secret cannot change the
selected endpoint, profile, targets, or generation settings.

Resolution precedence is explicit:

1. operation-owned typed request overrides;
2. runtime named-service `generation_overrides`;
3. model-profile generation defaults;
4. endpoint resilience defaults;
5. Friday LLM defaults.

Runtime bindings may override generation and resilience within the public typed
schema for chat profiles, resilience for either profile kind, and the explicit
credential reference. They may not override endpoint identity, profile kind,
route model, model target, operation dialect, or provider options in place. A
different deployment identity requires a separate named profile. Unknown
credential/endpoint/profile references, duplicate names, kind mismatches,
partial targets, unresolved selected credentials, and unsupported merged
controls fail before service construction or provider I/O.

### Provider-Independent Protocol Boundary

`friday-core.LLMClient` remains a minimal compatibility and dependency-injection
protocol during the `0.1.x` window. Friday Core must not import Friday LLM and
must not acquire a circular dependency.

Friday LLM will export a structural typed-client protocol for consumers that
need `ChatCompletionRequest`, typed responses, or streaming events. Packages
that need those features must declare a direct Friday LLM dependency instead
of relying on a transitive import. Packages that only receive a preconfigured
client may continue to depend on the Core protocol.

The legacy `chat_completion()` API remains available through the compatibility
window, but new or migrated code uses typed requests. Removal is not earlier
than `0.2.0` and requires a separate breaking-change plan.

### Explicit Precedence

The five-level model-library precedence above governs every framework consumer.
Only explicitly set fields participate in a merge. Populated Pydantic or
dataclass defaults must not accidentally override an operator setting. Equal
legacy and canonical values are accepted during compatibility; contradictory
values fail before provider I/O and name both paths without echoing values that
may be sensitive.

### Separate Behavioral And Provider Configuration

Subsystem settings stay outside the shared LLM specification and model library.
For example, passage-router confidence, fallback mode, and similarity
thresholds are not LLM generation controls. The subsystem references a Runtime
named service rather than repeating the provider profile:

```yaml
memory:
  passage_router:
    enabled: true
    min_confidence: 0.6
    fallback_mode: heuristic
    llm_service: passage_router
```

Every named service or profile may reference a separate least-privilege
credential environment variable. Credential fallback to another role or the
primary service is allowed only when the owning subsystem documents and tests
that behavior; otherwise a missing credential fails before provider I/O.

## Adoption Levels

Each distribution receives the smallest correct level of adoption:

1. **Semantic owner**: defines public typed LLM contracts and provider support.
2. **Composer**: validates service configuration and constructs named typed
   services.
3. **Typed caller**: creates typed requests or consumes typed streaming events.
4. **Injected consumer**: receives a configured provider-independent client and
   does not own provider configuration.
5. **Compatibility-only**: has no LLM behavior; receives graph, packaging, and
   regression validation only.

Provider independence does not mean pretending every provider supports every
control. Unsupported and unknown controls fail closed.

## Package Impact Matrix

| Distribution | Adoption | Required work |
| --- | --- | --- |
| `friday-framework-llm` | Semantic owner | Add the shared service specification/factory, typed-client protocol, required provider profiles, compatibility diagnostics, and final-wire tests. |
| `friday-framework-core` | Compatibility boundary | Keep the minimal `LLMClient` acyclic, document legacy status, correct any signature drift required for compatibility, and add structural contract tests. |
| `friday-framework-runtime` | Composer | Migrate `RuntimeConfig.llm_pool` and DI construction to shared typed service specs; bind agents, extraction, and other roles to explicit named services. |
| `friday-framework-memory` | Typed caller and injected consumer | Migrate extraction, routing, consolidation, compaction, maintenance, fact checking, reorganization, lifecycle processing, and large-file LLM calls without changing persistence semantics. |
| `friday-framework-agent` | Typed caller | Add an explicit Friday LLM dependency if typed per-call overrides are required; migrate ReAct/interactive calls and preserve reasoning/tool-call replay safely. |
| `friday-framework-tools` | Typed caller or injected consumer | Migrate code generation and smart-file boundaries; keep non-LLM tools free of provider knowledge. Use an optional extra only if that preserves the existing lightweight base install. |
| `friday-chat` | Application composer | Complete every deferred consumer, centralize service construction, migrate canonical and packaged configs, and retain actionable compatibility diagnostics. |
| `friday-framework-cli` | Configuration/assembly facade | Delegate to Runtime's typed pool, update compatibility config and templates, and prevent a second LLM schema from emerging in the container. |
| `friday-framework-telemetry` | Assurance/redaction consumer | Represent normalized requested/resolved/emitted controls and target profile metadata without messages, credentials, tool arguments, or reasoning content. |
| `friday-framework-transcript` | Persistence safety boundary | Prove reasoning and provider internals are not persisted accidentally; no direct Friday LLM dependency unless a typed public transcript contract is approved. |
| `friday-framework-mcp` | Indirect Agent consumer | Validate Agent extras and MCP tool-call flows against typed responses; do not add provider configuration. |
| `friday-framework-optimization` | Indirect Memory consumer | Validate DSPy/Memory installation and behavior; isolate DSPy provider configuration from Friday LLM unless an explicit adapter is designed. |
| `friday-framework-finance` | Compatibility-only | Version/pin and integration smoke validation; no LLM source changes. |
| `friday-framework-moltbook` | Compatibility-only | Version/pin and integration smoke validation; no LLM source changes. |
| `friday-framework-sandbox` | Compatibility-only | Version/pin and tool-execution integration validation; no LLM source changes. |
| `friday-framework-speech` | Output safety boundary | Verify speech consumes only approved final answer text and never reasoning content; otherwise compatibility-only. |
| root `friday-framework` | Cohort aggregator | Update exact dependencies/extras, examples, lock state, release helpers, and clean-install smoke coverage. |

## Provider And Model Support Gate

The existing typed profile is limited to the documented LM Studio,
OpenAI-compatible Chat Completions, Qwen3.8 target. Current framework examples
and compatibility fixtures also reference local OpenAI-compatible servers,
other Qwen families, OpenRouter-hosted models, and Moonshot/Kimi routes.

Before converting any such consumer, Friday LLM must establish truthful support:

1. inventory the exact provider, dialect, serving engine, model family, and
   revision used by maintained examples and tests;
2. verify each provider's current public request contract from authoritative
   documentation;
3. add the narrow capability and translation records actually needed;
4. add sanitized final-wire fixtures and loopback tests;
5. reject unsupported combinations without network I/O.

A dialect record may establish common controls such as temperature, `top_p`,
presence/frequency penalties, and maximum tokens. It must not imply support for
reasoning, `top_k`, `min_p`, repetition penalty, structured output, or provider
options. Those require a truthful engine, provider, or model-family record.

Applications must never label an OpenRouter, Moonshot, vLLM, or other target as
LM Studio merely to unlock a capability.

## Work Packages And Sequence

### FW-LLM-00: Approval, Branch, Baseline, And Target Inventory

1. Approve the new framework-upgrade phase and lift the FridayV2 freeze only for
   the paths enumerated by this plan.
2. Create `feature/friday-framework-typed-llm-adoption` from current `master`.
3. Record dirty worktree state and preserve the local Friday Chat config backup,
   unrelated documents, runtime state, and caches.
4. Capture focused and repository validation baselines before source changes.
5. Generate a complete inventory of:
   - `LiteLLMService` constructors;
   - legacy completion and streaming calls;
   - LLM configuration schemas and environment variables;
   - duplicated provider endpoints, credentials, and target identities;
   - role fallbacks and inherited credentials;
   - reasoning display, logging, telemetry, and persistence paths;
   - maintained provider/model targets.
6. Turn the inventory into a checked allowlist so CI detects new legacy call
   sites or unapproved direct service constructors.

**Gate:** no implementation begins until the package scope, provider targets,
and baseline are recorded without cleaning unrelated state.

### FW-LLM-01: Friday LLM Shared Construction Contract

1. Add strict public `LLMServiceSpec` and `EmbeddingServiceSpec` models (final
   names subject to API review).
2. Add strict, versioned `ModelLibrary`, `EndpointProfile`, `ModelProfile`, and
   named-service binding models plus a pure resolver from profile and overrides
   to `LLMServiceSpec`.
3. Add one public service factory/classmethod for chat and one for embeddings.
4. Export every type needed by downstream packages from `friday_llm`'s public
   root, including the typed-client protocol and any execution-target type
   downstream validation legitimately requires.
5. Make credential rendering and validation failures redaction-safe.
6. Validate model route identity against explicit targets.
7. Reject partial targets, unknown fields, duplicate library names, unknown
   credential/endpoint/profile references, incompatible provider options, and
   contradictory legacy/canonical controls before transport.
8. Preserve `ResilienceConfig`, telemetry, pricing, circuit-breaker, and
   Langfuse behavior through the applicable factory.
9. Add pure library-resolution, preflight, merge, construction, and final-wire
   tests.

**Gate:** downstream packages do not copy or wrap internal Friday LLM modules;
the complete required contract is a stable public export.

### FW-LLM-02: Required Capability Profiles

1. Implement only profiles required by the approved maintained-target matrix.
2. Compose capability records independently by provider, dialect, engine, and
   model family.
3. Add bounded provider-options models only where normalized intent cannot
   express a real provider feature.
4. Prove common OpenAI-compatible controls separately from engine/model-specific
   controls.
5. Add unknown, unsupported, conflict, range, and identity tests.
6. Record capability provenance in assurance summaries and release evidence.

**Stop condition:** if a maintained config needs an unverified or unsupported
control, keep that consumer on the documented compatibility path or change the
config with explicit behavioral approval. Do not manufacture support.

### FW-LLM-03: Core And Cross-Package Protocol Boundary

1. Reconcile the Core `LLMClient` signature with the legacy method that Friday
   LLM actually implements, without importing Friday LLM into Core.
2. Mark Core's flat generation parameters as compatibility-only in API docs.
3. Add structural conformance tests proving `LiteLLMService` still satisfies the
   compatibility protocol.
4. Use Friday LLM's typed-client protocol in packages that construct typed
   requests.
5. Replace repeated `cast(...)` patterns with explicit protocols or validated
   factories where practical.

**Gate:** no dependency cycle and no untyped cross-package configuration model.

### FW-LLM-04: Runtime Named-Service Migration

1. Add the strict `model_library.path` Runtime section and resolve relative
   paths against the Runtime YAML's directory.
2. Load and validate `models-config.yaml` once, then resolve selected profile
   references through Friday LLM's public resolver.
3. Replace Runtime's local flat `LLMServiceConfig` fields with named-service
   bindings containing a profile reference plus bounded generation/resilience
   overrides.
4. Migrate `embedding_pool.services.*` to embedding-profile references plus
   bounded resilience overrides; reject chat profiles in the embedding pool and
   embedding profiles in the LLM pool.
5. Retain inline flat `provider`, `model`, `api_key`, and `api_base`
   compatibility only through an explicit migration resolver and diagnostics.
6. Validate every configured named service before DI boot; preflight only
   enabled and reachable selections where subsystem enablement matters.
7. Resolve the binding credential or endpoint default through its selected
   `credentials.*.env` entry into a redacted secret field without exposing
   values through serialization, representations, exceptions, or diagnostics.
8. Construct all chat and embedding pool entries through their shared factories.
9. Preserve explicit agent-to-service, extraction-to-service, and default
   service bindings without implicit target inheritance.
10. Correct Runtime's package metadata: `friday_runtime.config` imports
   `friday_mcp.config` at module import time, so Runtime must declare the exact
   cohort MCP dependency unless that integration is first refactored behind a
   genuinely optional boundary. The planned default is to declare it.
11. Update environment-variable, library, YAML, and explicit-override precedence
    tests.
12. Add multi-service tests proving distinct reasoning, sampling, targets,
   resilience, and credentials do not bleed between roles.

**Gate:** no direct `LiteLLMService(...)` remains in Runtime composition outside
an approved compatibility adapter.

### FW-LLM-05: Friday Memory Consumer Migration

Migrate in this order so deterministic structured-memory paths are proven before
durable mutation paths:

1. entity and fact extraction;
2. passage routing;
3. consolidation and in-session compaction;
4. synthesizer and fact-checker roles;
5. reorganizer and mutation providers;
6. lifecycle tool-content processing;
7. large-file summarizer and synthesizer stages;
8. maintenance command-line construction.

For every consumer:

- accept an injected typed client or service specification rather than
  constructing an inferred provider;
- move operation-owned flat values into explicit `GenerationOverrides`;
- preserve structured JSON parsing, retry, timeout, cancellation, abstention,
  rollback, and fallback semantics;
- decide whether reasoning is disabled, automatic, or enabled based on the
  role, not the primary chat setting;
- prevent reasoning text from entering memories, graph records, rejection logs,
  maintenance evidence, or synthesized documents;
- retain provider-free disabled and heuristic fallback modes;
- add fake-transport and final-wire regression coverage.

Friday Memory's standalone maintenance command must accept an explicit model
library path and profile references or receive already resolved service specs.
It must reuse Friday LLM's library schema rather than inventing a second file
format.

Touched source files may not gain broad mypy suppression. Existing suppression
in a touched boundary should be removed when the contract can now be typed; any
remaining exception requires a documented waiver.

**Gate:** deterministic memory outputs and transactional mutation behavior match
the pre-migration baseline except for explicitly approved generation changes.

### FW-LLM-06: Agent And Tools Typed Calls

1. Migrate Agent ReAct, interactive, Copilot, routing, orchestration, and
   workflow LLM calls that own per-call controls to typed requests.
2. Decide explicitly whether agent profile temperature becomes a service
   default or request override; do not apply both.
3. Preserve assistant reasoning only when required for provider tool-call replay
   and only in bounded in-memory history.
4. Keep reasoning out of user display, transcript, telemetry, tool arguments,
   and durable memory.
5. Migrate Friday Tools code generation and smart-read LLM boundaries.
6. If Friday Tools needs Friday LLM only for optional LLM tools, add a correctly
   tested optional dependency rather than burdening unrelated tools.
7. Add named tool-choice, malformed tool-call, cancellation, retry, and
   structured-response tests.

**Gate:** non-LLM tools and provider-independent agent injection remain usable
without application-owned provider heuristics.

### FW-LLM-07: Friday Chat Deferred Consumers

1. Replace duplicated primary and auxiliary provider wrappers with the shared
   Friday LLM service specification.
2. Add `model_library.path` and named-service references to Friday Chat's
   application config, reusing the same Friday LLM library resolver as Runtime.
   Migrate `embedding` to an embedding-profile reference as part of the same
   catalog cutover.
3. Migrate:
   - `extraction.llm`;
   - `memory.passage_router.llm`;
   - compaction role binding;
   - `maintenance.llm.{synthesizer,classifier,researcher,judge}`;
   - the explicit reorganization mutation registry;
   - `smart_file.llm.{summarizer,synthesizer}`.
4. Keep behavioral fields at their existing subsystem paths and replace
   repeated provider blocks with `llm_service` references.
5. Make connection/credential fallback explicit. Reorganization mutation keeps
   its current no-primary-fallback safety contract.
6. Add per-path deprecation diagnostics for legacy inline auxiliary fields.
7. Update both:
   - `packages/friday-chat/config.example.yaml`;
   - `packages/friday-chat/src/friday_chat/config_templates/config.example.yaml`.
8. Add a packaged, secret-free `models-config.example.yaml` and verify copied
   template paths remain valid after wheel installation.
9. Update compatibility fixtures without treating them as canonical examples.
10. Verify canonical example startup emits zero configuration warnings.

**Gate:** every enabled Chat LLM service has an explicit target and typed
generation path; disabled services do not require credentials or network I/O.

### FW-LLM-08: CLI, Telemetry, Transcript, Speech, And MCP Boundaries

1. Make Friday CLI delegate LLM pool parsing and construction to Runtime; retain
   only compatibility presentation and actionable diagnostics.
2. Remove or deprecate duplicate container configuration once all supported CLI
   paths use `RuntimeKernel`/`RuntimeConfig`.
3. Extend telemetry with bounded assurance metadata, never raw reasoning or
   credentials.
4. Add transcript and speech tests proving only approved final text crosses
   persistence and audio boundaries.
5. Validate MCP/Agent tool-call flows using typed responses and explicit target
   profiles.
6. Ensure all warning and error messages name the subsystem and config path.

**Gate:** one configuration source reaches one service factory; no CLI-specific
provider translation exists.

### FW-LLM-09: Compatibility-Only Package Audit

For Finance, Moltbook, Optimization, Sandbox, and any other distribution with no
owned LLM construction:

1. prove no direct LLM dependency or provider logic is needed;
2. run import and integration tests against the candidate cohort;
3. update exact pins and versions only where required by lock-step policy;
4. do not add placeholder configuration or artificial Friday LLM dependencies.

Optimization must additionally prove its DSPy configuration remains isolated
from Friday LLM unless a separately designed adapter is approved.

### FW-LLM-10: Compatibility Window And Documentation

1. Accept legacy flat service and generation fields through `0.1.x`.
2. Emit one deterministic startup diagnostic per deprecated path.
3. Accept semantically equal legacy/canonical duplicates and reject conflicts.
4. Publish a complete old-to-new path mapping for Runtime, Chat, and Memory
   command configuration.
5. Document `models-config.yaml`, endpoint/profile separation, relative path
   resolution, credential environment variables, and service-binding
   precedence.
6. Document model route versus capability identity, target discovery, reasoning
   sensitivity, provider options, and unsupported-control behavior.
7. Provide canonical examples for each approved target profile and role type.
8. State that removal is not earlier than `0.2.0`.

### FW-LLM-11: Deterministic Validation Gate

Run validation in increasing scope:

1. focused model, resolver, capability, translation, and service-factory tests;
2. final-wire loopback tests with captured sanitized kwargs;
3. package tests for LLM, Core, Runtime, Memory, Agent, Tools, Chat, CLI,
   Telemetry, Transcript, Speech, MCP, and Optimization;
4. cross-package tests under `tests/integration`;
5. `uv run ruff check .`;
6. `uv run mypy packages tests main.py`;
7. `uv run pytest`;
8. root import and RuntimeKernel smoke tests;
9. Python 3.10, 3.11, 3.12, and 3.13 clean environments where provisioned.

If a repository-wide gate exposes unrelated legacy debt, record it separately
and also run the narrowest complete validation for every changed package. No
broad suppression, relaxed gate, live provider, or `--no-deps` workaround may
stand in for deterministic evidence.

### FW-LLM-12: Lock-Step `0.1.0a2` Candidate And Release

Because all internal Friday requirements use exact pins, publish the change as
one `0.1.0a2` cohort unless dependency policy is separately changed.

1. bump all 17 distribution versions and every active exact internal pin;
2. update exported runtime version constants and parity tests;
3. regenerate `uv.lock` and prove no stale `0.1.0a1` active pins remain;
4. build every wheel and sdist from a clean committed candidate;
5. validate metadata, extras, package contents, credentials, and Twine checks;
6. clean-install the full graph from built artifacts without workspace sources;
7. smoke `friday-chat`, Runtime, CLI, root `friday-framework`, and supported
   extras;
8. record immutable artifact hashes and sanitized evidence;
9. request separate publication approval;
10. publish in dependency order and verify every artifact from PyPI before the
    next layer.

Recommended publication order:

1. Telemetry, Transcript, Sandbox, and Moltbook;
2. Core;
3. Finance, Friday LLM, and Speech;
4. Memory;
5. Agent, Optimization, and Tools;
6. MCP;
7. Runtime;
8. CLI;
9. Friday Chat;
10. root `friday-framework`.

No package may be uploaded until all of its exact candidate dependencies are
available and independently installable on the target registry.

## Required Test Matrix

| Concern | Required proof |
| --- | --- |
| Model library | Schema version, relative path, duplicate names, unknown credential/endpoint/profile, explicit versus default credential, chat/embedding kind mismatch, unused missing credential, selected missing credential, immutable snapshot, and prohibited remote/include/inheritance forms. |
| Configuration | Canonical reference, legacy inline form, equal duplicate, conflicting duplicate, partial target, unknown key, unresolved selected secret, and disabled service. |
| Capabilities | Supported, unsupported, unknown, conflicting records, range/enum violations, provider-option mismatch. |
| Construction | Every named/role service receives correct target, generation defaults, resilience, telemetry, endpoint, and credential without cross-role bleed. |
| Requests | Typed non-streaming, streaming events, tools, named tool choice, structured JSON, timeout, cancellation, and retry. |
| Memory | Extraction, routing fallback, compaction, synthesis, fact checking, reorganization admission/rollback, large-file processing, and no reasoning persistence. |
| Agent/Tools | Multi-turn tool replay, agent role binding, code generation, malformed tool arguments, and provider-independent injection. |
| Safety | Secret redaction, reasoning redaction, untrusted output handling, diagnostic bounds, and no provider I/O after preflight failure. |
| Packaging | version/pin parity, wheel/sdist contents, extras, clean install, import smoke, CLI/Runtime/Chat startup. |

## Acceptance Criteria

The plan is complete only when all of the following are true:

- Friday LLM exposes one stable public service specification and construction
  path used by Runtime, Memory-owned constructors, and Friday Chat.
- Friday LLM exposes one strict versioned model-library schema and pure resolver;
  Runtime and Friday Chat load one local `models-config.yaml` and reference chat
  or embedding profiles rather than repeating endpoints, credentials, and
  target identities.
- Canonical model libraries contain credential environment-variable names,
  never credential values; service bindings may select a named least-privilege
  credential, and missing credentials for unused bindings do not block startup.
- Every maintained enabled LLM role has explicit transport and model targets.
- Every normalized control is either capability-validated and emitted or fails
  before provider I/O.
- Runtime pools support distinct typed services without configuration bleed.
- Friday Memory's extraction, routing, maintenance, lifecycle, reorganization,
  and smart-file paths use typed services and preserve their safety semantics.
- Agent and LLM-enabled Tools use typed requests where they own generation
  overrides.
- Friday Chat's primary and auxiliary consumers emit no migration warnings with
  the canonical example.
- Legacy configurations remain functional with actionable diagnostics through
  the declared compatibility window.
- Reasoning content is not displayed, logged, telemetered, spoken, transcribed,
  or persisted unless a separately tested contract explicitly requires it.
- No application package owns provider translation or capability inference.
- CI detects new unauthorized direct `LiteLLMService` constructors and legacy
  completion call sites.
- all focused, package, integration, Ruff, and mypy gates pass or unrelated
  baseline debt is explicitly separated with complete focused proof.
- all 17 distributions and internal pins form one clean-installable `0.1.0a2`
  graph.
- Runtime's declared dependencies are sufficient for importing
  `friday_runtime.config` in a clean environment, including its MCP contract.
- artifacts contain no secrets or local state and pass clean-environment smoke
  tests on supported Python versions.
- publication, push, merge, live-provider execution, and tagging occur only
  after their respective approvals.

## Explicit Non-Goals

- Do not make every package depend directly on Friday LLM.
- Do not add remote model-library URLs, recursive includes, profile inheritance,
  hot reload, or arbitrary deep merge in the first model-library release.
- Do not move provider translation or capabilities into Core, Runtime, Memory,
  Agent, Tools, Chat, or CLI.
- Do not infer targets from route strings, URLs, API keys, or environment
  variable names.
- Do not expose arbitrary provider payload dictionaries.
- Do not silently enable reasoning or newly effective sampling controls.
- Do not persist or expose hidden reasoning as an application feature.
- Do not apply chat-generation configuration or provider options to embedding
  profiles; sharing a connection endpoint does not combine their typed service
  contracts.
- Do not migrate DSPy provider behavior without a separate adapter contract.
- Do not clean caches, `.friday/`, Chroma data, transcripts, local config
  backups, or unrelated worktree files.
- Do not use live-provider success as a substitute for deterministic final-wire
  tests.
- Do not upload, push, merge, tag, or delete branches merely because validation
  passes.

## Approval Gates

Approval should be explicit at these points:

1. approve this architecture, the new framework-upgrade phase, proposed branch,
   and provisional `0.1.0a2` cohort;
2. approve the maintained provider/target matrix after authoritative research;
3. approve any behavior change where a formerly inert or unsupported control
   becomes effective;
4. approve the final committed candidate and release evidence;
5. approve push/PR/merge operations;
6. approve PyPI publication;
7. approve post-merge branch cleanup.
