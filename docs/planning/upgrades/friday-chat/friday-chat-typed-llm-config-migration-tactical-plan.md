# Friday Chat Typed LLM Configuration Migration Tactical Plan

- Status: Implementation and lock-step cohort validation complete; publication not authorized
- Plan date: 2026-08-28
- Accepted design recommendations: 2026-08-28
- Implementation approval date: 2026-08-28
- Target distribution: `friday-chat==0.1.0a1`
- Required LLM distribution: `friday-framework-llm==0.1.0a1`
- Release unit: Friday Chat package-scoped component upgrade

## Source Authority And Precedence

1. Active maintainer instructions and `AGENTS.md` define repository scope and
   implementation boundaries.
2. [Repository engineering policy](../../../reference/policies/repository-engineering-policy.md)
   is the code-quality and package-contract authority.
3. [Friday LLM reasoning and sampling controls requirement](../friday-llm/friday-llm-reasoning-and-sampling-controls-requirement.md)
   and [Friday LLM tactical implementation and release plan](../friday-llm/friday-llm-reasoning-controls-tactical-implementation-plan.md)
   define the upstream typed LLM contract and supported release-one profile.
4. The installed public API and release evidence for
   `friday-framework-llm==0.1.0a1` are the implementation-reality authority for
   this migration.
5. [Friday Framework PyPI preparation plan](../../build-plans/friday-framework-pypi-preparation.md)
   is the packaging and publication authority.
6. Existing FridayV2 configuration, behavioral, parity, and compatibility
   plans define application-level compatibility expectations.
7. [Tactical implementation planner](../../../dev-skills/tactical-implementation-planner.md)
   defines the required plan structure.
8. Current Friday Chat source, tests, metadata, lock state, and packaged
   resources take precedence when older documentation differs.

The tactical planner references `docs/methodology/constitution/gendev.md`, but
that file is not present in this checkout. If it is restored before
implementation, review this plan against it and record any required changes.

## Authority Gates

The three design recommendations recorded in this plan are accepted:

- migrate only the primary `llm:` consumer in the first release;
- use canonical nested generation and explicit target identity, while keeping
  legacy flat controls for one deprecation window and rejecting conflicts;
- release Friday Chat as `0.1.0a1`, pin Friday LLM exactly to `0.1.0a1`, and
  initially leave every other Friday dependency at `0.1.0a0`.

The final recommendation was superseded after clean-install evidence proved the
mixed graph unsatisfiable. On 2026-08-28 the maintainer approved the
[lock-step Friday package cohort](../friday-packages/friday-package-cohort-0.1.0a1-plan.md),
which moves every current Friday distribution and internal pin to `0.1.0a1`.

The maintainer approved this tactical plan on 2026-08-28. The FridayV2
framework freeze is released only for the Friday Chat, test, planning, minimal
workspace metadata, and package-generic release-helper scope listed here.

Plan approval does not authorize either TestPyPI or PyPI upload, a release tag,
or a remote push. Each registry upload remains a separate explicit action.

## Objective

Migrate Friday Chat's primary model path to Friday LLM's public typed request,
generation, target, provider-option, response, and event contracts without
embedding provider-specific behavior in the application configuration model.
The migration must make supported sampling controls such as `top_p` and
`top_k` effective, preserve old Friday Chat configurations for one documented
deprecation window, fail before network I/O for ambiguous or unsupported new
configuration, preserve Friday Chat's application-owned model protocol, and
produce a reproducible `friday-chat==0.1.0a1` artifact that can be independently
validated and, after separate authorization, published to PyPI.

## Release-One Decisions

### Scope And Consumer Boundary

- Implement the migration only for `FridayChatConfig.llm` and the primary
  `FrameworkChatModel` built by `build_framework_chat_model()`.
- Preserve Friday Chat's `ChatModel` boundary: non-streaming calls return the
  application-owned response shape and streaming calls yield application-owned
  text chunks.
- Convert Friday LLM typed responses and events at the adapter boundary rather
  than leaking provider or LiteLLM objects through Friday Chat.
- Inventory and regression-test other model consumers, including extraction,
  maintenance roles, reorganization, summarization, and smart-file helpers,
  but do not migrate or silently reconfigure them in `0.1.0a1`.
- Record future consumers in a sequenced handoff. If a shared configuration
  contract is required outside `packages/friday-chat`, stop and request a scope
  amendment instead of patching a frozen framework package.

### Version And Dependency Matrix

| Distribution or reference | Required version in this release |
| --- | --- |
| `friday-chat` project metadata | `0.1.0a1` |
| `friday_chat.__version__` | `0.1.0a1` |
| Friday Chat `full` self-extra | `friday-chat[finance,moltbook,sandbox,speech]==0.1.0a1` |
| `friday-framework-llm` | exactly `0.1.0a1` |
| Other direct and optional Friday dependencies | exactly `0.1.0a1` under the approved cohort |
| Root `friday-framework` project | `0.1.0a1` |
| Root references to Friday Chat and Friday LLM | exactly `0.1.0a1` |

The mixed component matrix was the original decision and is retained below as
failure evidence. It is not the current release contract. Final release
validation must use the lock-step cohort and must test both Friday Chat and the
root meta-package without workspace sources.

### Release Blocker Discovered During Clean Installation

The accepted matrix above is not installable from the published artifacts.
Clean pip resolution found that each of these immutable PyPI releases requires
`friday-framework-llm==0.1.0a0`:

- `friday-framework-memory==0.1.0a0`;
- `friday-framework-runtime==0.1.0a0`;
- `friday-framework-cli==0.1.0a0`.

Friday Chat requires Friday LLM `0.1.0a1` for the public typed request and
generation contracts, so no environment can satisfy the direct Chat pin and
those transitive exact pins simultaneously. Workspace resolution concealed the
problem because workspace sources replace the published wheel dependency graph.
The rejected `51a112c` candidate passed source metadata, archive, secret, and
Twine checks, then failed the first clean-install gate with pip
`ResolutionImpossible`. It must not be uploaded.

The initial four-package repair was also incomplete because exact pins continue
through Agent, Optimization, MCP extras, optional packages, and the root
meta-package. The approved repair is therefore a full 17-distribution
`0.1.0a1` lock-step release. Relaxing exact pins, installing with `--no-deps`,
or publishing the rejected artifacts would hide an invalid distribution rather
than repair the contract. The cohort plan is now the authority for metadata,
artifact, clean-install, release-order, and publication readiness.

### Branch Strategy

- Implement on `feature/friday-chat-typed-llm-config`, based on the commit that
  contains the accepted Friday LLM `0.1.0a1` contract and this approved plan.
- Do not implement the Chat release on
  `feature/friday-llm-reasoning-controls`; keep the upstream component history
  and downstream application history reviewable as separate release units.
- Before creating or switching branches, preserve and classify every dirty
  path. In particular, do not overwrite or automatically stage an existing
  edit to `packages/friday-chat/config.example.yaml`.
- If the clean branch point cannot be established without moving or mixing
  user-owned changes, stop and ask for direction. Plan-only edits may remain on
  the current planning branch until their disposition is explicitly decided.

### Canonical Configuration

The canonical user-facing shape maps directly to public Friday LLM models:

```yaml
llm:
  model: openai/qwen3.8-27b-mlx
  api_base: http://127.0.0.1:1234/v1
  api_key: ${LM_STUDIO_API_KEY}
  timeout_seconds: 120
  max_retries: 3

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

The final example must include only provider-option fields actually accepted by
the installed public Friday LLM type. Do not duplicate provider capability or
translation logic in Friday Chat. Reuse `GenerationConfig`, `ReasoningConfig`,
`SamplingConfig`, `TransportTarget`, and `ModelTarget` directly or through typed
Friday Chat wrappers that contain those public models.

`provider_options` is an optional sibling of `generation`, not part of the
normalized model. Release one accepts `LMStudioQwenOptions | None`, using the
concrete type exported from the `friday_llm` package root, and passes it on the
typed request. Do not import the non-root-exported `ProviderOptions` alias and
do not replace it with `dict[str, Any]`. A future Friday LLM release can export
additional concrete namespaced types, after which Friday Chat may extend its
closed discriminated union without changing the normalized generation schema.
The canonical example intentionally omits provider options because the current
LM Studio/Qwen options overlap normalized reasoning intent. Documentation may
show a separate provider-options example, but it must not encourage redundant
settings; equal duplicates are accepted and contradictory duplicates fail in
Friday LLM preflight.

`model` remains the transport route string. `model_target.model_id` is the
explicit model identity used by the capability preflight. It must match the
route model after the provider routing prefix is removed according to Friday
LLM's public validation rules. Friday Chat must not infer family, revision,
serving engine, provider, or endpoint dialect from `model`.

### Compatibility Window

Existing flat controls remain recognized in `0.1.0a1`:

- `temperature`
- `top_p`
- `top_k`
- `max_tokens`
- `thinking`

They are deprecated for removal no earlier than `0.2.0`. The implementation
must use Pydantic field-set information, not populated defaults alone, to tell
whether a legacy key was explicitly supplied.

| Configuration state | Required behavior |
| --- | --- |
| No targets and no nested generation | Use the legacy service/method path for this window; preserve legacy defaults and emit one actionable startup deprecation diagnostic. |
| Explicit targets with legacy flat controls only | Resolve flat controls into a typed `GenerationConfig`; use the typed path; emit one diagnostic per deprecated path without duplicating warnings. |
| Explicit targets with nested controls only | Use the canonical typed path with no legacy-control deprecation warning. |
| Flat and nested values are semantically equal | Accept, use the canonical nested value, and emit a deprecation diagnostic for the flat path. |
| Flat and nested values conflict | Reject configuration before service construction or external I/O and identify both paths without disclosing secrets. |
| Nested generation but missing either target | Reject before service construction; do not infer the missing identity. |
| Either target is partially specified or malformed | Reject before service construction. |
| Provider options without both explicit targets | Reject before service construction. |
| Provider options incompatible with the explicit target profile | Delegate to Friday LLM's typed preflight and reject before external I/O; do not duplicate its provider matching in Friday Chat. |

Legacy defaults must remain stable when neither form is explicitly set:

- effective `temperature` remains `0.7`;
- effective reasoning remains disabled;
- other absent sampling controls remain unset;
- retry and timeout behavior remain unchanged.

Explicit legacy `top_p` and `top_k` become effective when a configuration uses
the typed path. This is a deliberate activation of previously declared but
inert settings and must be called out in release notes. Legacy configurations
without explicit targets remain on the legacy path for this window so the
upgrade does not invent a target or silently claim unsupported capability.

### Strictness And Diagnostics

- Make the primary `llm` section strict for unknown nested keys.
- Keep only recognized legacy keys and canonical typed fields; do not retain a
  general `extra="allow"` escape hatch for this section.
- Surface deprecations and failures at startup through the existing
  configuration diagnostics path so CLI users can act on them.
- Configuration conflicts, target mismatches, unknown capability composition,
  unsupported reasoning budgets, and incompatible provider options must fail
  before the first provider call.
- Errors and diagnostics may identify field paths and capability names but must
  redact API keys, provider secrets, messages, tool arguments, raw wire
  payloads, and reasoning content.

### Provider Independence

The application schema expresses normalized generation intent and explicit
target identity. Provider-specific options live only in a namespaced, bounded
public Friday LLM model. Friday Chat must not contain provider-name conditionals,
model-name heuristics, LiteLLM wire keys, or Qwen translation behavior.

Adding another provider later should require an upstream Friday LLM capability
and translator plus a compatible namespaced options model, not a change to the
normalized Friday Chat generation schema. This preserves model independence
while allowing providers to expose capabilities that are genuinely unique.

## Assumptions

- `friday-framework-llm==0.1.0a1` is the required upstream contract and its
  public API will not be copied into Friday Chat.
- Friday LLM publication must precede any TestPyPI or PyPI installation of the
  Friday Chat candidate.
- Every exact `0.1.0a0` Friday dependency needed by the selected Chat extras
  must already exist and install successfully on the intended registry; local
  workspace resolution is not registry readiness evidence.
- The supported live release target remains the documented LM Studio,
  OpenAI-compatible Chat Completions, Qwen3.8 profile.
- Live tests are opt-in and may run only against an explicitly configured
  loopback endpoint.
- Friday Chat owns display, transcript, memory, and application response policy;
  Friday LLM owns request validation, capability resolution, translation, and
  transport.
- Reasoning content is sensitive untrusted model output. It may be preserved in
  an in-memory application response when explicitly required, but it must not
  be displayed, logged, diagnosed, telemetered, or stored by accident.
- Existing unrelated worktree changes and generated state must be preserved.

## Non-Goals

- Do not modify source or tests in any framework package other than
  `packages/friday-chat`.
- Do not add a Friday Chat provider registry, capability registry, or provider
  translator.
- Do not infer target identity from model strings or endpoint URLs.
- Do not expose unrestricted provider `**kwargs` in YAML.
- Do not migrate extraction, memory maintenance, reorganization, smart-file,
  or summarizer model consumers in this release.
- Do not redesign Friday Chat's internal turn-processing protocol.
- Do not add OpenAI Responses, native LM Studio, Anthropic-native, Ollama,
  Gemini, DeepSeek, vLLM, SGLang, or other new transport profiles.
- Do not change root meta-package versions or dependencies.
- Do not clean `.friday/`, caches, Chroma data, transcript state, local config,
  or unrelated dirty files.
- Do not upload, tag, or push merely because implementation or tests pass.

## Global Stop Conditions

Stop and request maintainer direction if any of the following occurs:

- This tactical plan has not been explicitly approved for implementation.
- The installed Friday LLM public API differs materially from the contracts
  recorded in its release plan and evidence.
- The migration needs a change outside the approved Friday Chat, planning,
  minimal workspace metadata, or release-helper scope.
- A normalized behavior requires provider or model heuristics in Friday Chat.
- Compatibility cannot be implemented without silently choosing between
  conflicting legacy and canonical values.
- An unknown nested LLM key would be ignored instead of rejected.
- The primary non-streaming adapter cannot preserve text, tool calls, reasoning
  separation, usage, or finish state without corrupting Friday Chat's boundary,
  or the text-only streaming adapter cannot reject non-text semantics safely.
- Preflight validation performs external I/O or a deterministic request-shape
  failure is routed through retries.
- A test or release artifact exposes secrets, prompts, tool arguments,
  reasoning content, raw provider responses, or local runtime state.
- Focused failures overlap changed behavior and cannot be explained and fixed.
- An artifact resolves an unintended Friday package version.
- The required LLM artifact is unavailable on the target registry.
- The live supported target cannot pass the bounded Friday Chat end-to-end gate.
- A requested implementation conflicts with repository engineering policy.
- TestPyPI or PyPI authorization has not been separately granted for the next
  upload action.

## Workstream Dependency Map

1. `CHAT-LLM-00` establishes authority, current behavior, and baseline evidence.
2. `CHAT-LLM-01` defines the typed schema and compatibility resolver.
3. `CHAT-LLM-02` migrates primary non-streaming service construction and calls.
4. `CHAT-LLM-03` migrates streaming and protects application invariants.
5. `CHAT-LLM-04` synchronizes templates, diagnostics, and user documentation.
6. `CHAT-LLM-05` supplies deterministic, compatibility, and security validation.
7. `CHAT-LLM-06` runs the opt-in live Friday Chat evidence lane.
8. `CHAT-LLM-07` versions, builds, validates, and rehearses the distribution.
9. `CHAT-LLM-08` closes out the release evidence and downstream-consumer handoff.

`CHAT-LLM-01` depends on `CHAT-LLM-00`. `CHAT-LLM-02` depends on
`CHAT-LLM-01`. `CHAT-LLM-03` depends on `CHAT-LLM-02`. `CHAT-LLM-04` may begin
after `CHAT-LLM-01`, but its examples cannot be finalized until
`CHAT-LLM-02` and `CHAT-LLM-03` pass. `CHAT-LLM-05` develops alongside each
implementation workstream and gates `CHAT-LLM-06` and `CHAT-LLM-07`.
Publication rehearsal depends on deterministic and live validation. Actual
uploads remain independently authorized.

## CHAT-LLM-00: Authority, Inventory, And Baseline

### Purpose

Capture the exact starting point and protect package boundaries before changing
configuration or runtime behavior.

### Implementation Tasks

- `CHAT-LLM-00-01`: Record approval of this plan, the authorized file scope,
  current branch, commit, dirty paths, Python and uv versions, and current
  package versions.
- `CHAT-LLM-00-02`: Confirm the candidate is built on a dedicated feature branch
  from the intended base. Preserve unrelated changes; do not switch branches if
  doing so would overwrite or mix the existing dirty worktree.
- `CHAT-LLM-00-03`: Inventory every Friday Chat model constructor and caller.
  Classify only `FridayChatConfig.llm` plus `FrameworkChatModel` as the primary
  implementation target and classify all other consumers as validation-only.
- `CHAT-LLM-00-04`: Trace every current `LLMConfig` field from YAML through
  service construction and final method arguments. Record declared-but-inert
  fields, especially `top_p` and `top_k`.
- `CHAT-LLM-00-05`: Record current config-loader behavior for unknown top-level
  keys, unknown nested LLM keys, environment interpolation, diagnostics, and
  missing required model values.
- `CHAT-LLM-00-06`: Run focused Friday Chat tests before changes and record
  pass, skip, and failure results. Reproduce any known PTY/control-sequence
  failures without treating prior observations as current evidence.
- `CHAT-LLM-00-07`: Run the narrow import, Ruff, and mypy baselines that cover
  the target files. Record unrelated repository debt separately.
- `CHAT-LLM-00-08`: Confirm Friday LLM `0.1.0a1` public exports, exact LiteLLM
  dependency, capability profile, and sanitized release evidence.
- `CHAT-LLM-00-09`: Resolve the active framework-upgrade-log location required
  by `AGENTS.md`. The named active path is absent in the current checkout and a
  copy exists only under the archived Friday Chat V2 planning directory. Restore
  or designate an active planning-only log before recording new framework gaps;
  do not silently edit an archive as though it were active authority.

### Affected Areas

- `packages/friday-chat/src/friday_chat/config.py`
- `packages/friday-chat/src/friday_chat/adapters.py`
- `packages/friday-chat/src/friday_chat/runtime.py`
- `packages/friday-chat/src/friday_chat/turns/`
- `packages/friday-chat/tests_chat/`
- Friday LLM public exports and reference evidence, read-only

### Tests And Evidence

- `uv run pytest packages/friday-chat/tests_chat -q`
- `uv run ruff check packages/friday-chat`
- focused mypy command for Friday Chat source and tests
- current `git status --short --branch` and package metadata capture
- config-to-runtime field inventory checked into release evidence or plan notes

### Acceptance Criteria

- The baseline is reproducible and distinguishes existing failures from new
  failures.
- Every Friday Chat LLM consumer is classified.
- No implementation file outside the authorized boundary has changed.
- Each currently effective, inert, defaulted, or ignored LLM setting is known
  before compatibility behavior is written.

### Dependencies And Non-Goals

- Depends on explicit plan approval.
- Does not implement configuration or adapter changes.
- Does not clean or stage unrelated worktree paths.

## CHAT-LLM-01: Typed Schema And Compatibility Resolver

### Purpose

Create one deterministic bridge from legacy Friday Chat YAML to Friday LLM's
typed configuration without duplicating provider behavior.

### Implementation Tasks

- `CHAT-LLM-01-01`: Replace the permissive primary LLM section with a strict
  model containing connection/resilience fields, canonical typed fields, and
  only the documented legacy compatibility fields.
- `CHAT-LLM-01-02`: Use the public Friday LLM Pydantic contracts for
  `generation`, `transport_target`, and `model_target` wherever their
  serialization shape is suitable. Type release-one provider options as the
  root-exported `LMStudioQwenOptions | None`. If a wrapper is needed for YAML
  ergonomics, make it typed and convert explicitly.
- `CHAT-LLM-01-03`: Implement a pure compatibility resolver that returns one of
  two explicit results: legacy execution configuration or fully typed execution
  configuration. Do not return an unbounded dictionary.
- `CHAT-LLM-01-04`: Use field-set tracking to distinguish omitted legacy keys
  from defaults and implement the complete compatibility table in this plan.
- `CHAT-LLM-01-05`: Map `thinking: true` to reasoning mode `enabled` and
  `thinking: false` to `disabled` only when the legacy key is explicitly set.
- `CHAT-LLM-01-06`: Preserve effective temperature `0.7` and disabled reasoning
  when both forms are absent.
- `CHAT-LLM-01-07`: Require both explicit targets for the typed path. Validate
  route model identity without inferring family, revision, engine, dialect, or
  provider.
- `CHAT-LLM-01-08`: Reject flat-versus-nested conflicts with an explicit
  `FridayChatConfigError` or another typed configuration exception; do not rely
  on `assert`.
- `CHAT-LLM-01-09`: Reject unknown LLM keys, partial targets, and route/model
  identity mismatches before the service is constructed. Delegate capability and
  provider-option compatibility to Friday LLM's typed preflight before I/O.
- `CHAT-LLM-01-10`: Produce structured, deduplicated startup diagnostics for
  legacy path usage and each explicitly supplied legacy field.
- `CHAT-LLM-01-11`: Ensure serialized diagnostics and validation errors redact
  secrets and sensitive content.

### Affected Areas

- `packages/friday-chat/src/friday_chat/config.py`
- `packages/friday-chat/tests_chat/test_config.py` or the existing config test
  modules
- Existing configuration diagnostics modules and CLI-startup tests

### Required Unit And Negative Tests

- Canonical nested configuration parses to exact Friday LLM public models.
- Every sampling bound and reasoning enum is enforced.
- Unknown nested LLM keys fail with an actionable field path.
- No-target legacy configuration preserves current defaults and selects the
  legacy path.
- Targeted flat-only configuration selects the typed path.
- Nested-only configuration selects the typed path without legacy warnings.
- Equal flat and nested values are accepted with one deprecation diagnostic.
- Each conflicting flat/nested pair fails before service construction.
- Explicit `thinking: true` and `thinking: false` map correctly.
- Omitted `thinking` does not accidentally override nested reasoning.
- Nested generation without both targets fails.
- Partial transport or model identity fails.
- Route and target model mismatch fails.
- Provider options without a compatible namespace and targets fail.
- Unsupported budget and unknown capability composition fail.
- API-key and provider-option canaries never appear in exception or diagnostic
  output.
- A mocked transport proves every deterministic config failure makes zero
  external calls and schedules no retry.

### Acceptance Criteria

- One typed resolver is the sole source of effective primary LLM configuration.
- Provider-neutral fields contain no provider translation logic.
- No target value is inferred.
- Compatibility behavior exactly matches the table in this plan.
- Config errors are explicit exceptions and are visible before runtime starts.

### Dependencies And Non-Goals

- Depends on `CHAT-LLM-00`.
- Does not instantiate `LiteLLMService` or call a provider.
- Does not loosen another flexible config section.

## CHAT-LLM-02: Primary Service Construction And Non-Streaming Migration

### Purpose

Adopt the typed Friday LLM request path for the primary model while preserving
Friday Chat's response and retry contracts.

### Implementation Tasks

- `CHAT-LLM-02-01`: Make `build_framework_chat_model()` consume the resolver's
  explicit legacy or typed result.
- `CHAT-LLM-02-02`: For typed execution, construct `LiteLLMService` with
  `transport_target`, `model_target`, resolved `generation_defaults`, existing
  connection values, and existing resilience policy.
- `CHAT-LLM-02-03`: Do not pass deprecated `thinking_enabled` for canonical
  configuration or for an omitted legacy `thinking` key. If an explicitly
  supplied legacy `thinking` value requires the upstream compatibility
  parameter, contain it to the legacy path and surface only the Friday Chat
  migration diagnostic during normal startup.
- `CHAT-LLM-02-04`: Convert Friday Chat messages and tools into a public
  `ChatCompletionRequest` and call `chat_completion_request()`. Set
  `tool_choice="auto"` when tools are present because the legacy Friday LLM
  method currently does so internally; leave it unset without tools. Do not add
  named selection to the application-owned `ChatModel` protocol.
- `CHAT-LLM-02-05`: Convert the typed Friday LLM response into Friday Chat's
  `ChatModelResponse`, preserving text, reasoning content when explicitly part
  of the existing response contract, tool calls, usage, and finish reason.
- `CHAT-LLM-02-06`: Keep the old service and `chat_completion()` call only for
  the no-target legacy compatibility path.
- `CHAT-LLM-02-07`: Preserve timeout and retry behavior; deterministic preflight
  failures must not enter the retry loop or perform transport I/O.
- `CHAT-LLM-02-08`: Keep fake-runtime and dependency-injected test paths free of
  provider I/O.
- `CHAT-LLM-02-09`: Avoid global LiteLLM state changes and avoid exposing
  provider payloads in logs or telemetry.

### Affected Areas

- `packages/friday-chat/src/friday_chat/adapters.py`
- `packages/friday-chat/src/friday_chat/runtime.py`, only if the application
  boundary requires a typed local adjustment
- `packages/friday-chat/tests_chat/test_adapters.py` or existing adapter tests
- Focused turn-processing and tool-selection tests

### Required Unit, Integration, And Negative Tests

- Typed service construction receives exact target and generation models.
- Canonical config produces no `thinking_enabled` deprecation warning.
- Legacy no-target config still uses the legacy method and emits the expected
  startup diagnostic.
- `top_p` and `top_k` reach the typed request from both canonical and targeted
  legacy forms.
- `min_p`, presence penalty, frequency penalty, repetition penalty,
  `max_tokens`, reasoning mode, effort, and preserve reach the typed request.
- A real in-process loopback HTTP server captures the final JSON emitted through
  Friday Chat plus actual LiteLLM; it verifies wire names and values for the
  supported LM Studio/Qwen profile.
- No test passes merely by checking constructor arguments or a mocked
  intermediate dictionary when behavioral effectiveness is claimed.
- Text, reasoning content, tool calls, usage, and finish reason survive typed
  response conversion without provider objects leaking through.
- Tool schemas and automatic selection semantics remain stable: typed requests
  carry `tool_choice="auto"` when tools are present, matching the legacy
  method's effective wire behavior.
- Unsupported settings and target mismatches fail before loopback request
  count increments.
- Retry tests prove a stable request specification across attempts and no retry
  for deterministic configuration errors.

### Acceptance Criteria

- Primary non-streaming canonical calls use `chat_completion_request()`.
- `top_p` and `top_k` are demonstrably emitted in final supported-target wire
  JSON.
- Legacy no-target behavior remains available and explicitly deprecated.
- Friday Chat's public/application response types remain stable.
- No provider-specific branch exists in Friday Chat.

### Dependencies And Non-Goals

- Depends on `CHAT-LLM-01`.
- Does not migrate non-primary consumers.
- Does not claim that an endpoint honored a field solely because the field was
  emitted.

## CHAT-LLM-03: Typed Streaming And Application Invariants

### Purpose

Use Friday LLM's typed event stream without exposing reasoning or corrupting
streamed text and tool state in Friday Chat.

### Implementation Tasks

- `CHAT-LLM-03-01`: For typed execution, call
  `chat_completion_events()` with the same immutable request specification used
  by non-streaming execution.
- `CHAT-LLM-03-02`: Project text events into Friday Chat's existing
  `AsyncIterator[str]` interface.
- `CHAT-LLM-03-03`: Handle reasoning events according to explicit application
  policy: never merge them into displayed answer text and never log, diagnose,
  telemeter, or persist them implicitly.
- `CHAT-LLM-03-04`: Preserve the existing no-tools streaming invariant. Friday
  Chat currently routes tool-enabled turns through non-streaming completion, so
  the text-only stream must not advertise tool support. Reject an unexpected
  tool event explicitly rather than silently dropping or partially assembling
  it.
- `CHAT-LLM-03-05`: Preserve cancellation, timeout, retry, and partial-output
  semantics already owned by Friday Chat.
- `CHAT-LLM-03-06`: Retain the legacy text-stream projection only for the
  no-target compatibility path.

### Affected Areas

- `packages/friday-chat/src/friday_chat/adapters.py`
- `packages/friday-chat/src/friday_chat/turns/processor.py`
- Existing streaming, tool, transcript, display, and cancellation tests

### Required Unit, Integration, And Negative Tests

- Typed text events yield the same visible text sequence as equivalent legacy
  chunks.
- Reasoning-only and interleaved reasoning/text streams never expose reasoning
  through the visible text iterator.
- Reasoning can be retained only in an explicitly tested in-memory response
  field and never in diagnostics, telemetry, transcript, or memory side effects.
- Tool-enabled turns remain on the tested non-streaming path.
- An unexpected streamed tool event fails explicitly and is never rendered as
  text or silently discarded.
- Usage and finish events do not appear as text.
- Cancellation closes the stream and does not trigger an unintended retry.
- A preflight failure creates no stream and performs no I/O.
- Legacy streaming remains behaviorally compatible during the window.

### Acceptance Criteria

- Canonical streaming uses typed Friday LLM events.
- Friday Chat's existing text-stream interface remains stable.
- No sensitive reasoning content leaks to visible or persisted channels.
- Finish semantics are preserved, and non-text event types unsupported by the
  application boundary are rejected explicitly.

### Dependencies And Non-Goals

- Depends on `CHAT-LLM-02`.
- Does not redesign the CLI display protocol.
- Does not add a new public reasoning-display feature.
- Does not extend Friday Chat's text-only streaming protocol with tools or
  typed events.

## CHAT-LLM-04: Templates, Diagnostics, And Documentation

### Purpose

Make the canonical configuration discoverable, secure, packaged, and
consistent across repository and installed-resource entry points.

### Implementation Tasks

- `CHAT-LLM-04-01`: Update the packaged template at
  `packages/friday-chat/src/friday_chat/config_templates/config.example.yaml`
  with canonical nested examples and safe environment placeholders.
- `CHAT-LLM-04-02`: Reconcile the repository example at
  `packages/friday-chat/config.example.yaml` without overwriting unrelated local
  edits. If it is already dirty, inspect and merge only the approved scoped
  changes or stop if ownership is ambiguous.
- `CHAT-LLM-04-03`: Document the legacy-to-canonical field mapping, conflict
  behavior, target identity requirement, and removal window.
- `CHAT-LLM-04-04`: Document the distinction between normalized generation,
  transport identity, model identity, and bounded provider options.
- `CHAT-LLM-04-05`: Document that `top_p` and `top_k` become effective only on
  the typed path and that emitted is not proof the endpoint honored a value.
- `CHAT-LLM-04-06`: Add configuration examples for reasoning disabled, enabled
  with effort, and sampling-only use. Include no real keys, private endpoints,
  local user paths, prompts, or provider responses.
- `CHAT-LLM-04-07`: Surface migration diagnostics during normal CLI startup and
  make `--help`/configuration guidance identify the canonical template.
- `CHAT-LLM-04-08`: Add `0.1.0a1` release notes with compatibility, dependency,
  config, behavior-activation, and publication caveats.

### Affected Areas

- Packaged and repository Friday Chat YAML templates
- Friday Chat README/configuration documentation
- CLI diagnostics/help tests
- New Friday Chat release notes/evidence under `docs/reference/`

### Required Tests And Reviews

- Repository and packaged templates parse successfully.
- A template-parity test prevents the two examples from drifting in their
  documented LLM keys while allowing intentional comments or packaging
  differences.
- Installed-resource tests load the packaged template from the wheel.
- Secret and local-state canaries are absent from source, templates, wheel, and
  sdist.
- Startup tests show legacy diagnostics once and canonical configuration with
  no legacy warning.
- Documentation examples are exercised by the config parser.

### Acceptance Criteria

- A user can migrate without reading source code.
- The installed package contains the same supported canonical schema described
  in repository documentation.
- No documentation implies automatic target inference or unrestricted provider
  options.
- Existing dirty example changes are preserved or explicitly reconciled.

### Dependencies And Non-Goals

- May start after `CHAT-LLM-01`; finalization depends on `CHAT-LLM-03`.
- Does not include credentials or live payload captures.
- Does not advertise profiles absent from Friday LLM `0.1.0a1`.

## CHAT-LLM-05: Deterministic Validation And Compatibility Gate

### Purpose

Prove the migration across config, adapter, CLI, package boundary, and supported
Python versions without relying on live provider availability.

### Implementation Tasks

- `CHAT-LLM-05-01`: Add focused config, adapter, streaming, diagnostic, and
  release-metadata regression tests alongside each workstream.
- `CHAT-LLM-05-02`: Add a table-driven legacy/canonical compatibility suite
  covering omissions, equality, conflicts, partial targets, and unsupported
  capability.
- `CHAT-LLM-05-03`: Add final-wire loopback tests that enter through Friday
  Chat's config and adapter, not directly through Friday LLM.
- `CHAT-LLM-05-04`: Run primary TurnProcessor and CLI flows with injected fake
  transports to verify no accidental provider I/O.
- `CHAT-LLM-05-05`: Run validation-only regression coverage for extraction,
  maintenance, reorganization, summarization, and smart-file consumers.
- `CHAT-LLM-05-06`: Run Friday Chat's full package suite, focused Ruff, and
  focused mypy on every supported Python minor where the environment is
  provisioned.
- `CHAT-LLM-05-07`: Run the repository-level test, Ruff, and mypy gates after
  focused success. Classify pre-existing unrelated debt separately; do not hide
  it with broad suppressions or relaxed gates.
- `CHAT-LLM-05-08`: Run Python 3.10, 3.11, 3.12, and 3.13 clean-environment
  package tests or equivalent CI jobs.

### Affected Areas

- Friday Chat config, adapter, CLI, turn, tool, and packaging tests
- Focused release-helper tests housed in the authorized Friday Chat test tree
- CI or local version-matrix configuration, only where minimally required
- Repository-wide validation commands, read-only except for recorded evidence

### Deterministic Verification Matrix

| Layer | Minimum evidence |
| --- | --- |
| Config models | Canonical, legacy, conflict, unknown-key, bounds, and redaction tests |
| Compatibility resolver | Complete table-driven truth table with explicit path selection |
| Adapter unit | Exact public typed request/response/event conversion |
| Final wire | Loopback capture of supported reasoning and every sampling wire field |
| Turn integration | Primary complete/stream flows and tools with fake transport |
| CLI | startup diagnostics, `--version`, `--help`, explicit config, and fake runtime |
| Non-primary consumers | Regression-only evidence; no behavior migration |
| Static quality | Focused Ruff and mypy with no new suppressions |
| Package | Full Friday Chat tests on Python 3.10-3.13 |
| Repository | Broad gates with unrelated baseline debt reported separately |

### Acceptance Criteria

- Every touched behavior has positive and negative coverage.
- Final-wire tests prove `top_p`, `top_k`, and other supported controls are
  forwarded through the complete Friday Chat path.
- Deterministic failures cause zero transport calls.
- All focused tests and static checks pass.
- Broader failures are proven unrelated and do not overlap changed interfaces.
- Validation-only consumers retain their baseline behavior.

### Dependencies And Non-Goals

- Runs throughout `CHAT-LLM-01` through `CHAT-LLM-04` and gates later stages.
- Does not treat a mocked keyword assertion as final-wire evidence.
- Does not require live credentials.

## CHAT-LLM-06: Opt-In Live Friday Chat Evidence Lane

### Purpose

Prove that the supported configuration works through Friday Chat, not only
through Friday LLM or a synthetic wire server.

### Preconditions

- All `CHAT-LLM-05` focused gates pass.
- LM Studio is explicitly configured on an allowlisted loopback URL.
- The exact served Qwen3.8 model identity and revision are recorded.
- No secret, message, raw response, tool argument, or reasoning content will be
  captured in evidence.
- Live execution is separately acknowledged as an opt-in validation action.

### Implementation Tasks

- `CHAT-LLM-06-01`: Build `FridayChatConfig` from a sanitized canonical YAML
  fixture and construct the model through `build_framework_chat_model()`.
- `CHAT-LLM-06-02`: Run bounded non-streaming reasoning-disabled and
  reasoning-enabled requests.
- `CHAT-LLM-06-03`: Run bounded streaming requests and verify visible-text and
  reasoning separation.
- `CHAT-LLM-06-04`: Exercise supported `top_p`, `top_k`, and one additional
  provider-specific sampling control through Friday Chat.
- `CHAT-LLM-06-05`: Exercise one existing Friday Chat tool-enabled turn through
  the non-streaming path and verify automatic selection; named selection remains
  out of scope because Friday Chat exposes no such input.
- `CHAT-LLM-06-06`: Run one bounded TurnProcessor or CLI-level flow with safe
  disposable state.
- `CHAT-LLM-06-07`: Record sanitized command shape, environment facts, counts,
  timing, model identity, result classification, and package versions without
  raw content.

### Affected Areas

- An opt-in Friday Chat live test module under
  `packages/friday-chat/tests_chat/`
- Sanitized Friday Chat release evidence under `docs/reference/`
- Disposable temporary config and runtime state outside tracked source

### Live CLI And UAT Procedure

1. Verify the exact installed Friday Chat, Friday LLM, LiteLLM, and Python
   versions and the allowlisted loopback endpoint.
2. Load the sanitized canonical configuration through the same loader used by
   the CLI.
3. Build the real primary adapter and run the bounded complete and stream cases.
4. Run one safe tool-enabled turn through the normal non-streaming path.
5. Start Friday Chat with disposable state, confirm startup diagnostics and a
   single bounded turn, then exit cleanly.
6. Record only classified results and sanitized environment facts.

### Required Tests And Negative Tests

- Live positive cases listed in implementation tasks 02 through 06 of this
  workstream.
- A mismatched model identity fails before the endpoint receives a request.
- An unsupported reasoning budget fails before the endpoint receives a request.
- A non-loopback or missing allowlist configuration refuses to run the live
  lane.
- Evidence redaction canaries prove secrets and model content are absent.

### Live Acceptance Criteria

- Primary Friday Chat construction and complete/stream execution succeed
  against the exact supported profile.
- Reasoning and visible text remain separated.
- Tools behave consistently with deterministic coverage.
- No secrets or sensitive model content are stored in evidence.
- A skipped or unavailable live target is a release hold, not a passing gate.

### Dependencies And Non-Goals

- Depends on `CHAT-LLM-05`.
- Does not test arbitrary providers or public network endpoints.
- Does not upgrade an emitted-field claim to honored without observable,
  provider-supported evidence.

## CHAT-LLM-07: Versioning, Artifact Validation, And Publication Rehearsal

### Purpose

Produce immutable, independently installable Friday Chat artifacts with exact
mixed-version dependency evidence.

### Implementation Tasks

- `CHAT-LLM-07-01`: After functional gates pass, update
  `packages/friday-chat/pyproject.toml` to `0.1.0a1`.
- `CHAT-LLM-07-02`: Set `friday_chat.__version__` to `0.1.0a1` and add a test
  that runtime and installed metadata versions are identical.
- `CHAT-LLM-07-03`: Pin `friday-framework-llm==0.1.0a1`, keep all other Friday
  dependencies at `0.1.0a0`, and update the `full` self-extra to
  `friday-chat[finance,moltbook,sandbox,speech]==0.1.0a1`.
- `CHAT-LLM-07-04`: Update `uv.lock` intentionally and verify the expected
  resolution. Do not update root project pins or unrelated package metadata.
- `CHAT-LLM-07-05`: Verify name ownership and exact availability of every
  required `0.1.0a0` Friday dependency plus Friday LLM `0.1.0a1` on each target
  registry before attempting a Chat install or upload.
- `CHAT-LLM-07-06`: Enhance `scripts/check-package-metadata.py` to validate a
  package/self version separately from an explicit expected internal dependency
  map; a single workspace-wide `--internal-version` is insufficient for this
  mixed-version component release.
- `CHAT-LLM-07-07`: Enhance `scripts/check-package-artifacts.py` to verify Chat
  `0.1.0a1`, LLM `0.1.0a1`, every other Friday pin at `0.1.0a0`, the expanded
  `full` extra metadata, console entry point, package resources, license, and
  absence of forbidden local state. Validate the self-reference in source
  metadata because the build backend expands it in wheel metadata.
- `CHAT-LLM-07-08`: Extend `scripts/smoke-install-artifacts.sh` with a Friday
  Chat mode that checks installed metadata, import/runtime version parity,
  packaged config loading, `friday-chat --version`, `friday-chat --help`,
  canonical fake-runtime config, and `pip check`.
- `CHAT-LLM-07-09`: Build wheel and sdist with
  `uv build --package friday-chat` into an isolated candidate directory such as
  `dist/friday-chat-0.1.0a1/`.
- `CHAT-LLM-07-10`: Run Twine metadata checks, custom artifact validators,
  archive listings, secret/local-state scans, dependency inspection, and
  hashes on the exact candidate files.
- `CHAT-LLM-07-11`: Install the wheel alone in a clean environment and run the
  Chat smoke suite. Install the sdist in a separate clean environment, rebuild
  it, and compare required metadata, entry points, and resources.
- `CHAT-LLM-07-12`: Repeat clean-install smoke tests on Python 3.10-3.13.
- `CHAT-LLM-07-13`: Freeze hashes and do not rebuild, rename, or mutate
  artifacts between final validation and any authorized upload.

### Affected Areas

- `packages/friday-chat/pyproject.toml`
- `packages/friday-chat/src/friday_chat/__init__.py`
- `packages/friday-chat/tests_chat/` release and installed-resource tests
- `uv.lock`
- `scripts/check-package-metadata.py`
- `scripts/check-package-artifacts.py`
- `scripts/smoke-install-artifacts.sh`
- Candidate artifacts and sanitized release evidence

### Required Tests And Negative Tests

- Metadata validator accepts the exact mixed-version matrix.
- Fixtures with the wrong Chat version, LLM pin, other Friday pin, source
  self-extra, or expanded wheel `full` extra each fail for the expected reason.
- Wheel/sdist fixtures missing the console entry point, config resources, or
  license fail.
- Secret, local-user-path, `.friday`, Chroma, transcript, and cache canaries
  fail the artifact scan.
- Wheel and sdist clean-install smokes pass without workspace sources.
- A deliberately inconsistent runtime `__version__` fails parity validation.
- `pip check`, CLI version/help, config-resource parsing, and provider-free fake
  runtime pass in each supported Python environment.

### Artifact Commands

Exact command flags may evolve with the release helpers, but the executable
sequence must retain these gates:

```bash
uv run pytest packages/friday-chat/tests_chat -q
uv run ruff check packages/friday-chat scripts/check-package-metadata.py scripts/check-package-artifacts.py
uv build --package friday-chat
uv run twine check dist/friday-chat-0.1.0a1/*
```

The release evidence must record the exact validator and smoke-install commands
rather than relying on this abbreviated example.

### TestPyPI Strategy

- Friday LLM `0.1.0a1` must already exist on TestPyPI before the Chat candidate
  is installed from TestPyPI.
- Request explicit authorization immediately before upload.
- Use Trusted Publishing and attestations when the configured registry supports
  them.
- Upload the previously hashed candidate; do not rebuild.
- Avoid an ambiguous `--extra-index-url` resolution that could select an
  unintended dependency version. Preinstall every exact dependency from its
  intended registry, verify the installed versions, then install the TestPyPI
  Chat candidate with `--no-deps` and run `pip check`. This proves the LLM
  candidate and other fixed dependencies came from their intended sources.
- Run `pip check`, metadata/version checks, packaged-template parsing,
  `friday-chat --version`, `friday-chat --help`, and a provider-free fake-runtime
  smoke from the installed artifact.
- Record the immutable registry URLs and hashes.

### PyPI Strategy

- Friday LLM `0.1.0a1` must already be published and independently verified on
  PyPI.
- Request separate explicit PyPI authorization after TestPyPI evidence is
  accepted.
- Upload the same hashed Friday Chat files; never rebuild between registries.
- Install exactly `friday-chat==0.1.0a1` from PyPI in a clean environment and
  run `pip check`, `uvx friday-chat==0.1.0a1 --version`,
  `uvx friday-chat==0.1.0a1 --help`, packaged-template parsing, and a
  provider-free configuration smoke.
- Create and push a release tag only after PyPI verification and only with
  explicit authority for those remote mutations.

### Acceptance Criteria

- Metadata, runtime version, dependency pins, self-extra, lockfile, and
  artifacts all match the version matrix.
- Wheel and sdist contain the console entry point and canonical config template
  and contain no forbidden state or secrets.
- Clean wheel and sdist installs pass on Python 3.10-3.13.
- The validators detect intentional negative fixtures for wrong LLM,
  other-package, source self-extra, and expanded `full` extra versions.
- No root meta-package version or dependency changes are included.
- No upload, tag, or push occurs without its specific authority gate.

### Dependencies And Non-Goals

- Depends on `CHAT-LLM-05` and `CHAT-LLM-06`.
- Does not publish the root framework or unrelated components.
- Does not resolve dependencies from the local workspace during clean artifact
  proof.

## CHAT-LLM-08: Closeout And Deferred Consumer Handoff

### Purpose

Record exactly what changed, what was proved, what remains legacy, and what
authority is still required.

### Implementation Tasks

- `CHAT-LLM-08-01`: Create a Friday Chat `0.1.0a1` release-evidence document
  containing commit identity, dirty-worktree statement, package versions,
  sanitized test results, live target classification, artifact names, sizes,
  hashes, and publication status.
- `CHAT-LLM-08-02`: Create release notes covering canonical configuration,
  legacy compatibility, newly effective `top_p`/`top_k`, provider independence,
  target requirements, and removal timing.
- `CHAT-LLM-08-03`: Update this plan status only when each completed gate has
  evidence; do not conflate implementation complete, live gate complete,
  TestPyPI published, PyPI published, or tagged.
- `CHAT-LLM-08-04`: Record each validation-only Friday Chat consumer with its
  current configuration source, LLM API, required future migration, dependency,
  and risk.
- `CHAT-LLM-08-05`: Sequence the future shared-consumer migration after the
  primary path stabilizes. Prefer a shared typed application-level config model
  rather than duplicating fields across consumers.
- `CHAT-LLM-08-06`: Record any discovered framework improvement in the FridayV2
  framework upgrade log rather than patching a frozen package.
- `CHAT-LLM-08-07`: Update `docs/planning/README.md` and archival status when the
  release is genuinely complete.

### Affected Areas

- This tactical plan and `docs/planning/README.md`
- Friday Chat release notes and release evidence under `docs/reference/`
- The active FridayV2 framework upgrade log, once its authority path is resolved
- No runtime source in deferred consumer packages

### Deferred Consumer Handoff Fields

For each consumer, record:

- owner module and construction site;
- current config path and defaults;
- legacy or typed Friday LLM method used;
- whether it needs reasoning, sampling, tools, or streaming;
- response/storage sensitivity, especially reasoning content;
- proposed shared typed config dependency;
- focused regression suite;
- earliest safe release and approval boundary.

### Acceptance Criteria

- Evidence distinguishes configured, emitted, provider-accepted, and observed
  behavioral assurance levels.
- Remaining legacy consumers are explicit and sequenced.
- No source outside approved scope was modified to make the evidence green.
- Publication and tag status are factually recorded.

### Required Review

- Independently compare the release evidence with commits, test outputs,
  artifacts, hashes, registry state, and tags.
- Confirm every deferred consumer entry points to an actual current constructor
  and test surface.
- Confirm no validation-only consumer or frozen package source changed.

### Dependencies And Non-Goals

- Depends on all completed implementation and validation workstreams.
- Does not implement the deferred consumer migrations.
- Does not mark publication complete based on local artifacts alone.

## Risks, Mitigations, And Recovery

| Risk | Mitigation or recovery |
| --- | --- |
| Legacy and canonical paths drift | One pure resolver, a complete truth table, explicit path-selection tests, and a dated removal window. |
| A default becomes an apparent explicit override | Use `model_fields_set` at every compatibility boundary and test omitted values separately from explicit defaults. |
| Provider-specific behavior leaks into Chat | Depend only on public Friday LLM target, generation, request, and bounded options models; prohibit provider branches and wire keys in Chat. |
| Redundant normalized and provider options conflict | Prefer normalized intent in examples; accept equal duplicates and rely on preflight to reject contradictions before I/O. |
| Text-only streaming drops non-text events | Keep tool-enabled turns non-streaming and fail explicitly on unexpected streamed tool events. |
| Reasoning content leaks into display or storage | Separate event handling, content canaries, sanitized diagnostics, and transcript/memory/telemetry negative tests. |
| Exact mixed-version pins escape current validators | Add per-package expected-pin maps and intentional negative artifact fixtures. |
| Workspace sources conceal an uninstallable wheel | Require clean, registry-backed wheel and sdist installs with `pip check`; do not use the root meta-package as the candidate. |
| TestPyPI resolves an unintended package | Preinstall exact dependencies from intended registries, verify versions, install the Chat artifact with `--no-deps`, then run `pip check`. |
| The dirty repository example is overwritten | Capture ownership and diff first; merge only scoped hunks or stop. Never clean or restore the file automatically. |
| Other Chat LLM consumers behave inconsistently | Keep them validation-only in this release, record their configuration and API paths, and schedule a shared typed-config follow-up. |
| Live provider evidence is unavailable or flaky | Deterministic loopback proof remains mandatory, but the missing live gate is a release hold rather than a substituted pass. |
| The active framework-upgrade log is missing | Restore or designate the planning-only authority before recording gaps; do not treat an archive as active silently. |
| PyPI artifacts need correction after upload | PyPI versions are immutable. Do not overwrite `0.1.0a1`; prepare a new version such as `0.1.0a2`. A yank or other registry mutation requires separate explicit authority. |

Before any registry upload, recovery is a normal feature-branch correction and
full revalidation. After upload, never delete, replace, or reuse the candidate
version as a repair mechanism. Record the defect, decide whether a yank is
warranted, issue a new version, and repeat the relevant release gates.

## File-Scope Contract

Plan approval authorizes changes only in these areas when required by the
workstreams:

- `packages/friday-chat/src/friday_chat/`
- `packages/friday-chat/tests_chat/`
- Friday Chat package metadata and examples
- `uv.lock`
- minimal workspace metadata strictly required to build or test Friday Chat
- package-generic release helpers under `scripts/`, with regression tests
- Friday Chat planning, release notes, and release evidence under `docs/`

The following remain read-only unless the maintainer explicitly expands scope:

- every `packages/friday-*` source or test tree other than `friday-chat`;
- root meta-package version and dependency declarations;
- ART or any external consumer repository;
- local runtime state and unrelated dirty paths.

## Verification And Acceptance Checklist

Implementation is complete only when all applicable items are true:

- [ ] The tactical plan was explicitly approved and the authorized scope was
      recorded.
- [ ] Baseline branch, commit, worktree, versions, config flow, and tests were
      captured before edits.
- [ ] Primary canonical configuration uses Friday LLM public typed contracts.
- [ ] Unknown LLM keys, conflicts, partial targets, mismatches, and unsupported
      capabilities fail before I/O.
- [ ] No target identity is inferred from a model or URL.
- [ ] Legacy no-target configuration preserves behavior and emits an actionable
      deprecation diagnostic.
- [ ] Equal and conflicting flat/nested combinations match the compatibility
      table.
- [ ] Primary non-streaming and streaming canonical paths use typed Friday LLM
      APIs.
- [ ] Final-wire tests prove `top_p`, `top_k`, and all supported configured
      fields pass through Friday Chat correctly.
- [ ] Text, reasoning, tools, usage, finish state, cancellation, and retries
      preserve explicit application invariants.
- [ ] Reasoning and secrets are absent from logs, diagnostics, telemetry,
      transcripts, evidence, and artifacts except where an explicit tested
      application contract permits in-memory reasoning.
- [ ] Packaged and repository templates are synchronized and parse successfully.
- [ ] Validation-only consumers retain baseline behavior and are recorded for a
      later migration.
- [ ] Focused tests, Ruff, and mypy pass with no new broad suppression.
- [ ] Broader gates were run and unrelated debt was separated from candidate
      failures.
- [ ] The live LM Studio/Qwen Friday Chat lane passed; an unavailable target is
      recorded as a release hold.
- [ ] Friday Chat metadata, runtime version, self-extra, LLM pin, other Friday
      pins, and lockfile match the version matrix.
- [ ] Wheel and sdist validators, secret scans, Twine checks, and clean-install
      smoke tests pass on Python 3.10-3.13.
- [ ] Final candidate names, sizes, and hashes are recorded and unchanged.
- [ ] TestPyPI and PyPI actions, if any, were separately authorized and verified.
- [ ] A release tag, if any, was created only after verified PyPI publication
      and explicit remote-mutation authority.

## Approval Record

- Accepted design recommendations: primary consumer only; canonical nested
  schema plus one legacy window; `friday-chat==0.1.0a1` with only Friday LLM at
  `0.1.0a1`.
- Tactical implementation approval: granted 2026-08-28.
- Live-provider execution approval: pending when the opt-in gate is reached.
- Dependency-cohort scope amendment: granted 2026-08-28 for every current
  Friday distribution at `0.1.0a1`.
- TestPyPI upload approval: pending and separate.
- PyPI upload approval: pending and separate.
- Tag/push approval: pending and separate.
