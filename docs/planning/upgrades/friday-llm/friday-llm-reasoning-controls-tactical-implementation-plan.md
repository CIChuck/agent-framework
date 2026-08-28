# Friday LLM Reasoning Controls Tactical Implementation And Release Plan

- Status: Implementation and live-provider gate complete; prior package-only
  artifact superseded by lock-step cohort; publication not authorized
- Date: 2026-08-27
- Approval date: 2026-08-27
- Implementation completion date: 2026-08-27
- Target distribution: `friday-framework-llm==0.1.0a1`
- Release unit: package-scoped component upgrade

## Source Authority And Precedence

1. Active maintainer instructions and `AGENTS.md` define repository scope and
   implementation boundaries.
2. [Repository engineering policy](../../../reference/policies/repository-engineering-policy.md)
   is the code-quality and package-contract authority.
3. [Friday LLM reasoning and sampling controls requirement](friday-llm-reasoning-and-sampling-controls-requirement.md)
   is the capability and downstream ART handoff authority.
4. [Friday Framework PyPI preparation plan](../../build-plans/friday-framework-pypi-preparation.md)
   is the packaging and publication authority.
5. [Tactical implementation planner](../../../dev-skills/tactical-implementation-planner.md)
   is the plan-structure authority.
6. Current source, tests, metadata, and lock state are the implementation-reality
   authority when older documentation differs.

The tactical planner references `docs/methodology/constitution/gendev.md`, but
that file is not present in this checkout. If it is restored before
implementation, review this plan against it and record any required changes.

## Implementation Authority Gate

Maintainer approval was recorded on 2026-08-27 for this tactical plan. The
FridayV2 parity freeze is released only for the authorized implementation scope
listed in this document. This satisfies `LLM-RC-00-01` and authorizes the Friday
LLM source, tests, metadata, lockfile, release-helper, and documentation work
required by this plan.

The freeze remains in force for every validation-only consumer and unrelated
Friday framework package. If implementation requires a consumer or other
framework-package change, stop and obtain a coordinated scope amendment before
editing it.

Publication is a separate irreversible action. Completing implementation and
tests does not authorize TestPyPI or PyPI upload.

Implementation, deterministic validation, live-provider validation, packaging,
and clean-install smoke testing are complete. The exact results and artifact identities are recorded in
[Friday LLM 0.1.0a1 release evidence](../../../reference/llm/friday-llm-0.1.0a1-release-evidence.md).
The package-only artifact recorded there is now diagnostic evidence rather than
an upload candidate: the approved
[lock-step cohort](../friday-packages/friday-package-cohort-0.1.0a1-plan.md)
changes Friday LLM's Core and Telemetry pins to `0.1.0a1`. Friday LLM must be
rebuilt and revalidated as part of that cohort. The release also remains stopped
because neither TestPyPI nor PyPI upload has been authorized. No tag has been
created.

## Implementation Objective

Publish a backward-compatible Friday LLM alpha that represents reasoning and
sampling intent with immutable provider- and model-independent typed models,
resolves service defaults and request overrides deterministically, composes
target capabilities and translation layers for the approved LM Studio/Qwen
OpenAI-compatible Chat Completions profile, fails before external I/O for
unsupported or conflicting new controls, preserves the legacy Friday API for
one deprecation window, and provides reproducible wire and release evidence.

The release must not claim that a control was behaviorally effective merely
because Friday configured or emitted a field.

## Release-One Decisions

### Version And Release Unit

- Target `friday-framework-llm==0.1.0a1`.
- Keep `friday-framework-core==0.1.0a0` and
  `friday-framework-telemetry==0.1.0a0` unless implementation demonstrates a
  required contract change.
- Do not bump the root meta-package or unrelated component packages in this
  release.
- Record that `friday-framework==0.1.0a0` will continue selecting its exact
  `friday-framework-llm==0.1.0a0` dependency until a later coordinated release.
- Do not reuse or overwrite the immutable PyPI `0.1.0a0` artifacts.

These package-only dependency decisions are historical. The 2026-08-28
coordinated release supersedes them with `0.1.0a1` for every current Friday
distribution and internal exact pin. The typed Friday LLM implementation and
live evidence remain valid; only the package graph and artifacts require new
cohort evidence.

### LiteLLM Baseline

- Investigate the initial `litellm==1.98.0` candidate. It was rejected because
  it imports `typing.NotRequired` on Python 3.10 and fails before Friday can be
  imported.
- Use `litellm==1.94.1`, the current stable release that imports on the declared
  Python 3.10 floor and preserves the deterministic release-one wire contract.
- Use an exact dependency for this alpha because provider translation is part
  of the tested contract.
- The replacement decision and evidence must stay synchronized across this
  plan, package metadata, lockfile, wire fixtures, and release notes.
- Do not retain the current unbounded `litellm>=1.81.0` dependency.
- A future release may widen the range only after lower- and upper-bound
  compatibility testing exists.

### Supported Target Composition

Release-one normalized reasoning support is limited to:

- endpoint dialect: OpenAI-compatible Chat Completions;
- transport path: `litellm.acompletion`;
- serving engine: LM Studio;
- model family: Qwen3.8;
- live integration target: the exact artifact served locally as
  `qwen3.8-27b-mlx`.

The implementation may continue transporting legacy calls to existing LiteLLM
providers, but it must not advertise normalized reasoning-control support
unless the composed dialect, provider/engine, and model capability records are
registered, compatible, and tested. The Qwen/LM Studio target is the first
built-in composition, not the shape of the public generation API.

### Public API Strategy

- Preserve existing `chat_completion()` and `chat_completion_stream()` methods
  for one deprecation window.
- Add a typed request method for new configuration rather than overloading the
  legacy `temperature=0.7` signature with ambiguous `None` or sentinel values.
- Add a typed event-stream method. Keep the legacy stream as a text-only
  projection over text events.
- Keep new public contracts owned and exported by `friday-llm`; do not require a
  `friday-core` release for `0.1.0a1`.
- Preserve the legacy `ChatCompletionResponse` return type for the legacy
  non-streaming method.

Proposed public shapes:

```python
service = LiteLLMService(
    model_name="openai/qwen3.8-27b-mlx",
    transport_target=TransportTarget(
        provider="openai_compatible",
        dialect="openai_chat_completions",
        serving_engine="lm_studio",
    ),
    model_target=ModelTarget(
        model_id="qwen3.8-27b-mlx",
        family="qwen3_8",
        revision="documented-or-captured-revision",
    ),
    generation_defaults=GenerationConfig(...),
)

result = await service.chat_completion_request(
    ChatCompletionRequest(
        messages=...,
        tools=...,
        tool_choice="auto",
        overrides=GenerationOverrides(...),
    )
)

async for event in service.chat_completion_events(request):
    ...
```

Final names may change during `LLM-RC-01`, but the separation between legacy
methods, typed request execution, typed events, transport identity, model
identity, and provider-neutral generation intent is fixed for release one.

## Assumptions

- Distribution names and import names remain distinct:
  `friday-framework-llm` installs `friday_llm`.
- Qwen model recommendations are documentation inputs, not Friday defaults.
- Provider and model specificity is required inside capability and translation
  adapters but forbidden from leaking into normalized generation models.
- The endpoint may ignore a syntactically accepted field; only captured and
  classified evidence can raise the assurance level beyond emitted.
- Existing provider response objects are an untrusted dynamic boundary and may
  require narrow local validation before conversion to typed Friday models.
- `reasoning_content` is sensitive untrusted model output. It may be returned to
  the caller when required by the public contract but must not be logged,
  included in diagnostics, or copied to telemetry.
- Live LM Studio tests are opt-in and unavailable in ordinary CI unless an
  explicitly provisioned runner exists.
- Existing unrelated worktree changes and generated runtime state are preserved.

## Non-Goals

- Do not implement OpenAI Responses support in `0.1.0a1`.
- Do not implement LM Studio native `/api/v1/chat` support.
- Do not implement an Anthropic-native transport or a general Anthropic
  reasoning translator.
- Do not implement Ollama, Gemini, DeepSeek, Moonshot, Bedrock, vLLM, or SGLang
  normalized reasoning profiles in this release.
- Do not expose unrestricted provider `**kwargs`.
- Do not create a public adapter class for every provider/model tuple.
- Do not publish a public provider-extension registration API in this release.
- Do not change Friday Chat, Runtime, Agent, Memory, or Core public APIs.
- Do not make ART source or configuration changes.
- Do not claim full provider capability discovery from model-name heuristics.
- Do not persist raw reasoning content or wire payloads.
- Do not clean caches, `.friday/`, Chroma state, transcripts, local config, or
  unrelated dirty files.

## Global Stop Conditions

Stop implementation and request direction if any of these occurs:

- The FridayV2 framework-package freeze has not been explicitly released for
  this work.
- A required change to `friday-core` or another component package would make
  `0.1.0a1` no longer package-scoped.
- The selected LiteLLM version cannot produce deterministic, inspectable wire
  behavior for the supported profile.
- LM Studio does not honor the selected Qwen control on the OpenAI-compatible
  Chat Completions endpoint and no documented supported representation exists.
- A public contract would require an unbounded `dict[str, Any]`, repeated casts,
  a new broad mypy suppression, or an unapproved policy waiver.
- Streaming tool calls cannot be represented without silently corrupting IDs,
  names, argument fragments, ordering, or finish state.
- Release validation requires a secret in source, committed config, a command
  argument, a captured payload, or an artifact.
- Package-only versioning produces an unsatisfied published dependency.
- A requested change conflicts with repository engineering policy.

## Workstream Dependency Map

1. `LLM-RC-00` establishes authority, baseline evidence, and final release
   decisions.
2. `LLM-RC-01` defines immutable public contracts and compatibility rules.
3. `LLM-RC-02` implements capability registration, merging, and translation.
4. `LLM-RC-03` integrates the resolver into non-streaming and legacy service
   paths.
5. `LLM-RC-04` adds typed streaming events and tool-call assembly.
6. `LLM-RC-05` adds bounded observability and security controls.
7. `LLM-RC-06` completes deterministic and downstream validation.
8. `LLM-RC-07` runs the opt-in live LM Studio/Qwen evidence lane.
9. `LLM-RC-08` builds, rehearses, publishes, and verifies the distribution.
10. `LLM-RC-09` prepares the downstream ART handoff without modifying ART.

## LLM-RC-00: Authority, Inventory, Dependency Baseline, And Wire Investigation

### Purpose

Resolve governance and empirical wire questions before public types or
translator behavior are frozen.

### Implementation Tasks

- `LLM-RC-00-01`: Record maintainer approval for the framework-upgrade pass and
  confirm the FridayV2 freeze no longer blocks the scoped files.
- `LLM-RC-00-02`: Record the working-tree baseline, current commit, Python and uv
  versions, package versions, LiteLLM version, and focused validation results.
- `LLM-RC-00-03`: Inventory every `LiteLLMService` constructor and completion
  caller across Friday packages. Classify each as legacy-only, potential typed
  API adopter, or validation-only consumer.
- `LLM-RC-00-04`: Inspect the rejected LiteLLM `1.98.0` candidate and selected
  `1.94.1` source paths used for OpenAI-compatible Chat Completions.
- `LLM-RC-00-05`: Capture sanitized final HTTP JSON for no override, current
  `thinking={"type": "disabled"}`, Qwen
  `chat_template_kwargs.enable_thinking`, each documented Qwen effort tier, and
  `preserve_thinking`.
- `LLM-RC-00-06`: Capture common and Qwen/LM Studio sampling fields, including
  the observed wire names for `top_k`, `min_p`, and repeat/repetition penalty.
- `LLM-RC-00-07`: Record which fields LiteLLM translates, passes through,
  drops, rejects, or rewrites.
- `LLM-RC-00-08`: Freeze release-one capability records separately for endpoint
  dialect, provider/serving engine, model family, and exact model revision, plus
  their composition rules and the exact LiteLLM dependency, after the wire
  findings.
- `LLM-RC-00-09`: Confirm that core and telemetry `0.1.0a0` artifacts remain
  available and satisfy the proposed wheel metadata.

### Affected Areas

- `packages/friday-llm/pyproject.toml`
- `uv.lock`
- `packages/friday-llm/src/friday_llm/service.py`
- `packages/friday-llm/src/friday_llm/__init__.py`
- `packages/friday-llm/tests_llm/`
- `docs/planning/upgrades/`
- `docs/planning/build-plans/`
- a new sanitized wire-investigation report under `docs/reference/llm/`

### Required Tests And Evidence

- A fake local HTTP transport captures final JSON without external network I/O.
- Captured fixtures contain no API key, prompt body beyond fixed synthetic test
  text, local user path, raw reasoning, or unrestricted headers.
- Both streaming and non-streaming setup are captured.
- The report distinguishes Friday input, LiteLLM kwargs, final HTTP fields,
  response fields, and behavioral observations.

### Acceptance Criteria

- Framework-upgrade authority is explicit.
- The exact LiteLLM version is selected from evidence.
- The release-one capability records have no inferred or unknown entries
  presented as supported, and each resolved control retains source provenance.
- Final wire field names are known before translator implementation starts.
- No source implementation begins if the target endpoint cannot support the
  required control.

### Dependencies

None.

### Non-Goals

- Do not finalize public API names before the wire findings.
- Do not use a real prompt, credential, or private conversation in captures.

## LLM-RC-01: Typed Public Contracts And Compatibility Foundation

### Purpose

Define immutable public models, merge semantics, error contracts, and the exact
legacy transition without changing transport behavior.

### Implementation Tasks

- `LLM-RC-01-01`: Add a dedicated public configuration module containing
  provider-neutral `ReasoningConfig`, `SamplingConfig`, `GenerationConfig`, and
  `GenerationOverrides`; separate `TransportTarget` and `ModelTarget` identity
  models; and capability-state and provenance contracts.
- `LLM-RC-01-02`: Configure public Pydantic models as frozen and
  `extra="forbid"` with explicit field descriptions and serialization tests.
- `LLM-RC-01-03`: Define `ReasoningMode` values `auto`, `enabled`, and
  `disabled`.
- `LLM-RC-01-04`: Define omission versus explicit-null override behavior:
  omitted inherits the service field, explicit null clears it to provider
  default, and a concrete value overrides it. Use Pydantic field-set tracking,
  not truthiness, to implement the distinction.
- `LLM-RC-01-05`: Define `ChatCompletionRequest` and an enriched typed result
  carrying content, tool calls, model, normalized usage, finish reason,
  reasoning content, and assurance metadata.
- `LLM-RC-01-06`: Define `ToolChoice` for `auto`, `none`, `required`, and a
  named function where supported.
- `LLM-RC-01-07`: Add typed exceptions for configuration conflict,
  unsupported control, unknown capability, protected extension, and translation
  failure. Errors must identify the field and supported alternatives without
  including payload values or secrets.
- `LLM-RC-01-08`: Export the new public types through `friday_llm.__init__` and
  document their stability as alpha APIs.
- `LLM-RC-01-09`: Remove `# mypy: ignore-errors` from every new module and from
  materially changed public contract modules. Remove it from `service.py`,
  `config.py`, and `__init__.py` as part of this upgrade or stop for an explicit
  policy-compliant waiver.
- `LLM-RC-01-10`: Define a typed, namespaced provider-options envelope whose
  variants are adapter-owned Pydantic models. Do not expose `dict[str, Any]`,
  arbitrary `extra_body`, or unrestricted keyword arguments at the public
  boundary. Release one registers only options proven for its supported target.
- `LLM-RC-01-11`: Define `CapabilityState` as `supported`, `unsupported`, or
  `unknown`, and require capability constraints and provenance to survive
  composition and appear in bounded diagnostics. Define absence of a source
  record as no opinion, distinct from an applicable `unknown` record.
- `LLM-RC-01-12`: Prohibit provider-, endpoint-, serving-engine-, and
  model-specific control fields or value names in the normalized generation
  models. Target identity types may describe those axes but must not contain
  generation controls.

### Compatibility Truth Table

| Legacy constructor input | New reasoning input | Release-one result |
| --- | --- | --- |
| omitted | omitted | Preserve old default: resolve disabled through legacy compatibility policy |
| `False` | omitted | Resolve disabled and emit `DeprecationWarning` |
| `True` | omitted | Resolve enabled intent and emit `DeprecationWarning`; unknown legacy dialects preserve the old no-disable wire behavior |
| omitted | `auto` | Emit no reasoning override |
| omitted | `enabled` | Validate and translate using composed target capabilities |
| omitted | `disabled` | Validate and translate using composed target capabilities |
| legacy plus semantically equal new value | present | Accept for one release with deprecation warning and use the new value |
| legacy plus contradictory new value | present | Raise configuration conflict before external I/O |

The legacy methods retain `temperature=0.7`. The new typed request method emits
no sampling field unless supplied by service defaults or request overrides.

### Reasoning Validation Rules

- `mode=disabled` rejects effort, budget, or preserve values that request active
  reasoning.
- Effort, budget, and preserve require `mode=enabled` in release one.
- `budget_tokens` must be a positive integer and is rejected for the Qwen3.8
  release-one target unless the wire investigation proves support.
- Effort values are capability-defined rather than globally fixed.
- Supplying effort and budget together is rejected unless the selected
  capability explicitly supports the combination.

### Sampling Validation Rules

- Provider-neutral models perform broad type and finite-number validation.
- Provider/model range checks occur during capability preflight.
- `top_p` and `min_p` are within `[0, 1]` where supported.
- `top_k` is a positive integer where supported.
- Temperature and penalty ranges come from the frozen capability table.
- `repetition_penalty` remains a normalized Friday field; a translator may map
  it to `repeat_penalty`, but the two names are never treated as interchangeable
  without a registered mapping.
- Friday does not inject model-card recommended sampling values.

### Affected Areas

- `packages/friday-llm/src/friday_llm/generation.py` (new)
- `packages/friday-llm/src/friday_llm/requests.py` (new)
- `packages/friday-llm/src/friday_llm/exceptions.py`
- `packages/friday-llm/src/friday_llm/config.py`
- `packages/friday-llm/src/friday_llm/__init__.py`
- `packages/friday-llm/tests_llm/test_generation.py` (new)
- `packages/friday-llm/tests_llm/test_requests.py` (new)

### Required Tests

- Validation and serialization for every public field.
- Frozen-model and deep-copy/materialization tests.
- Omitted, explicit-null, and concrete-value merge tests.
- Every compatibility truth-table row.
- Negative tests for every invalid reasoning combination and non-finite number.
- Public import and `__all__` tests.
- Contract tests proving normalized generation serialization contains no
  provider, dialect, engine, or model-family fields.
- Typed provider-option discriminator and wrong-namespace rejection tests.
- Focused mypy tests proving public signatures without broad suppressions.

### Acceptance Criteria

- No implementation workstream must invent a config, merge, error, or legacy
  rule.
- Normalized generation intent is usable unchanged by multiple adapters; target
  metadata and adapter-owned options remain separate contracts.
- New typed requests can represent provider-default behavior without silently
  injecting `temperature=0.7`.
- Legacy call signatures and return types remain source compatible.
- Public contract modules pass meaningful mypy checking.

### Dependencies

- Depends on `LLM-RC-00`.

### Non-Goals

- Do not add provider translation in this workstream.
- Do not modify `friday-core` contracts.

## LLM-RC-02: Capability Registry, Resolution, And Translation

### Purpose

Resolve normalized intent and independently described target identity into a
deterministic, inspectable LiteLLM call specification without external I/O.

### Implementation Tasks

- `LLM-RC-02-01`: Add private capability-source and translator protocols that
  accept frozen normalized contracts and target descriptors and return frozen,
  typed records or a `LiteLLMCallSpec`.
- `LLM-RC-02-02`: Add separately versioned built-in capability records for the
  OpenAI Chat dialect, LM Studio serving-engine overlay, Qwen3.8 family overlay,
  and exact tested model revision proven in `LLM-RC-00`.
- `LLM-RC-02-03`: Require explicit transport provider, endpoint dialect,
  serving engine when relevant, model ID, model family, and tested revision for
  new normalized reasoning controls. Do not infer support from a loose model
  substring.
- `LLM-RC-02-04`: Permit `auto` against an unknown target composition by
  emitting no reasoning override. Reject any explicit new reasoning control
  against an unknown target composition before I/O.
- `LLM-RC-02-05`: Implement a pure default/override resolver that materializes
  one immutable resolved config per request.
- `LLM-RC-02-06`: Compose capabilities per normalized control in the order
  dialect baseline, provider overlay, serving-engine overlay, model-family
  overlay, exact-revision overlay, and optional operator declaration. Preserve
  provenance and apply the fixed lattice: authoritative `unsupported` wins;
  required `unknown` remains unknown; support requires at least one
  authoritative supporting record; constraints are intersected; an empty
  intersection is a conflict. Operator declarations may refine `unknown` but
  may not override `unsupported`, widen constraints, or contradict built-ins.
- `LLM-RC-02-07`: Implement layered translation in the order endpoint dialect,
  provider/serving engine, then model family/revision quirks. Retain owner and
  provenance for every wire field. Allow additive writes; replacement or
  removal requires a registered named overlay rule that identifies the expected
  prior owner. Reject every undeclared collision.
- `LLM-RC-02-08`: Translate the release-one Qwen reasoning mode, supported
  effort and preserved-thinking fields, and common sampling fields to the wire
  representation proven by investigation, including the exact mapping of
  repetition penalty when applicable.
- `LLM-RC-02-09`: Protect Friday-owned fields: model, messages, tools,
  tool-choice, credentials, base URL, metadata, telemetry, timeouts, retries,
  streaming, and resilience cannot be supplied through typed provider options.
- `LLM-RC-02-10`: Keep provider-specific adapter registration private in
  release one. Only registered typed option models and fixed translator-owned
  JSON fields may be emitted.
- `LLM-RC-02-11`: Add an inspectable resolution summary containing field names,
  capability sources, conflicts, and assurance states but no prompt, tool
  arguments, reasoning content, or provider-option values.
- `LLM-RC-02-12`: Add two deterministic synthetic adapters used only by
  architecture tests. They must translate the same normalized intent into
  different valid call specs without changing or specializing the normalized
  request types.

### Assurance States

Use these terms consistently:

- `requested`: supplied by the caller;
- `resolved`: accepted after service/request merge and capability validation;
- `emitted`: present in the captured outbound HTTP payload;
- `acknowledged`: confirmed by explicit provider/server response metadata;
- `behaviorally_observed`: supported by a bounded controlled comparison.

Never label `requested`, `resolved`, or `emitted` settings as effective.

### Affected Areas

- `packages/friday-llm/src/friday_llm/capabilities.py` (new)
- `packages/friday-llm/src/friday_llm/targets.py` (new)
- `packages/friday-llm/src/friday_llm/provider_options.py` (new)
- `packages/friday-llm/src/friday_llm/translation.py` (new)
- `packages/friday-llm/src/friday_llm/generation.py`
- `packages/friday-llm/tests_llm/test_capabilities.py` (new)
- `packages/friday-llm/tests_llm/test_translation.py` (new)
- sanitized golden fixtures under `packages/friday-llm/tests_llm/fixtures/`

### Required Tests

- Golden call-spec tests for every supported mode and field.
- Unknown-target auto behavior and explicit-control rejection.
- Capability composition, source provenance, and contradiction tests.
- Tests distinguishing absent source records from applicable `unknown` records,
  unsupported precedence, constraint intersections, and empty intersections.
- Unsupported field rejection before transport invocation.
- Deterministic serialization and ordering for diagnostics.
- No translator mutation of input models or nested mappings.
- Protected-field collision tests.
- Two synthetic-adapter tests proving one normalized request can produce
  different target-specific call specs without provider fields in core models.
- Layer-collision tests proving translators cannot silently overwrite a wire
  field, plus positive tests for an explicitly registered replacement overlay.
- Translation parity between streaming and non-streaming setup.
- Tests proving model-name heuristics cannot grant capabilities.

### Acceptance Criteria

- Resolution and translation are pure, deterministic, and free of network I/O.
- The supported target composition emits only fields proven in the wire
  investigation.
- Unknown support is never reported as supported or effective.
- Capability, translation, and model recommendations are distinct records with
  no implicit conversion between them.
- Adding a future provider, engine, or model quirk requires an adapter/overlay,
  not a change to normalized generation models.
- Both service execution paths consume the same call-spec builder.

### Dependencies

- Depends on `LLM-RC-00` and `LLM-RC-01`.

### Non-Goals

- Do not implement runtime capability probing as an authority source.
- Do not add a public extension plugin system.
- Do not create a monolithic class for each provider/dialect/engine/model tuple.

## LLM-RC-03: Service Integration And Legacy Isolation

### Purpose

Integrate typed requests and translation into `LiteLLMService` while preserving
legacy behavior and eliminating package-import global policy changes.

### Implementation Tasks

- `LLM-RC-03-01`: Add optional `transport_target`, `model_target`, and
  `generation_defaults` constructor parameters using the public typed
  contracts.
- `LLM-RC-03-02`: Change legacy `thinking_enabled` handling so omission and
  explicit values follow the compatibility truth table.
- `LLM-RC-03-03`: Add `chat_completion_request()` using the single resolver and
  call-spec builder.
- `LLM-RC-03-04`: Refactor non-streaming setup so retry attempts reuse one
  frozen call spec and cannot re-resolve mutable caller input.
- `LLM-RC-03-05`: Adapt `chat_completion()` to the shared internal execution
  path while preserving its signature, `temperature=0.7`, return type, and
  structured-output behavior.
- `LLM-RC-03-06`: Remove process-global `litellm.drop_params` and
  `litellm.modify_params` assignments from package import.
- `LLM-RC-03-07`: Set any required LiteLLM compatibility behavior explicitly on
  the individual legacy call. New typed calls use strict unsupported-parameter
  behavior.
- `LLM-RC-03-08`: Pass explicit LiteLLM provider identity only from the
  transport target and only using the mechanism proven in `LLM-RC-00`. Keep the
  model target independent from transport routing.
- `LLM-RC-03-09`: Normalize response content, tool calls, reasoning aliases,
  usage details, and finish reason into the enriched typed result.
- `LLM-RC-03-10`: Preserve the legacy response adapter, including malformed
  tool-argument behavior, without exposing newly captured private reasoning in
  logs.
- `LLM-RC-03-11`: Define and test the relationship between legacy LiteLLM
  `model_name` routing and `ModelTarget.model_id`. Do not infer family or
  revision from either string, and reject contradictory explicit identities
  before transport.

### Affected Areas

- `packages/friday-llm/src/friday_llm/service.py`
- `packages/friday-llm/src/friday_llm/__init__.py`
- `packages/friday-llm/src/friday_llm/telemetry_helper.py`
- `packages/friday-llm/tests_llm/test_service.py`
- new focused service-contract test modules where needed

### Required Tests

- Existing service tests remain green.
- Importing `friday_llm` does not change LiteLLM global `drop_params` or
  `modify_params` values.
- Legacy calls preserve the prior kwargs and result shape for every current
  tested behavior.
- New strict calls reject unsupported controls before mocked transport use.
- Concurrent calls with conflicting configs do not leak state.
- Retries use byte-equivalent call specs.
- Response tests cover `reasoning_content`, `reasoning`, absent reasoning,
  reasoning-token details, finish reason, empty content, and tools.
- Configuration errors do not increment the circuit breaker or enter retry.

### Acceptance Criteria

- The package no longer changes unsupported-parameter policy globally at import.
- Legacy callers remain source compatible.
- New callers receive strict, inspectable behavior.
- The same resolver and translator are used for every attempt and execution
  mode.

### Dependencies

- Depends on `LLM-RC-01` and `LLM-RC-02`.

### Non-Goals

- Do not migrate downstream Friday callers in this release.
- Do not redesign resilience or structured-output parsing beyond what the new
  contract requires.

## LLM-RC-04: Typed Streaming Events And Tool-Call Invariants

### Purpose

Represent streaming text, reasoning, tools, usage, and completion state without
breaking the legacy text-only stream.

### Implementation Tasks

- `LLM-RC-04-01`: Define a discriminated stream-event union with text delta,
  reasoning delta, tool-call delta, usage, finish, and diagnostic-safe error
  events.
- `LLM-RC-04-02`: Add `chat_completion_events()` using the same frozen call spec
  as non-streaming execution plus `stream=True`.
- `LLM-RC-04-03`: Assemble tool calls by provider index and call ID without
  concatenating reasoning or final text into arguments.
- `LLM-RC-04-04`: Preserve multiple tool-call ordering and handle name and
  argument fragments arriving separately.
- `LLM-RC-04-05`: Capture usage-only chunks whose choices list is empty.
- `LLM-RC-04-06`: Preserve finish reason and completion state.
- `LLM-RC-04-07`: Implement the legacy `chat_completion_stream()` as a
  projection that yields only text deltas and retains its current signature.
- `LLM-RC-04-08`: Ensure cancellation and timeout close the upstream iterator
  and finalize telemetry without yielding a false success event.

### Affected Areas

- `packages/friday-llm/src/friday_llm/streaming.py` (new)
- `packages/friday-llm/src/friday_llm/service.py`
- `packages/friday-llm/src/friday_llm/__init__.py`
- `packages/friday-llm/tests_llm/test_streaming.py` (new or expanded)

### Required Tests

- Text-only stream compatibility.
- Interleaved reasoning and text.
- One and multiple tool calls.
- Tool arguments split across arbitrary chunk boundaries.
- Name, ID, and index fragments in different chunks.
- Malformed final arguments represented as a typed failure without
  reasoning-text contamination.
- Empty-choice usage chunk.
- Finish reason propagation.
- Timeout, cancellation, connection failure, and cleanup.
- Byte-equivalent translated request fields between streaming and
  non-streaming modes except streaming-specific fields.

### Acceptance Criteria

- New streaming callers can reconstruct complete tool calls deterministically.
- The old stream still yields only strings.
- Reasoning, final text, and tool arguments remain separate.
- No success or finish event is fabricated after cancellation or failure.

### Dependencies

- Depends on `LLM-RC-02` and `LLM-RC-03`.

### Non-Goals

- Do not migrate Friday Chat to typed events in this component release.

## LLM-RC-05: Observability, Privacy, And Extension Safety

### Purpose

Expose enough bounded metadata to diagnose translation without leaking prompts,
reasoning, tools, credentials, or provider payloads.

### Implementation Tasks

- `LLM-RC-05-01`: Add requested, resolved, emitted, acknowledged, and
  behaviorally observed assurance fields to bounded diagnostics.
- `LLM-RC-05-02`: Record only normalized field names and safe enum values for
  sampling and reasoning; never record raw extension values.
- `LLM-RC-05-03`: Record bounded transport provider, endpoint dialect,
  serving-engine profile, model-family/revision profile, capability-source
  versions and provenance, and LiteLLM version with length and cardinality
  bounds.
- `LLM-RC-05-04`: Record whether reasoning was returned and provider-supplied
  reasoning-token counts without recording reasoning text.
- `LLM-RC-05-05`: Define maximum key count, nesting depth, string length, and
  serialized bytes for translator-owned provider JSON.
- `LLM-RC-05-06`: Reject protected or secret-like keys in any future extension
  input even though public extension registration is deferred.
- `LLM-RC-05-07`: Ensure API base query strings, credentials, prompt bodies,
  tool schemas, tool arguments, raw reasoning, and response bodies never enter
  telemetry or debug logs.
- `LLM-RC-05-08`: Document that Qwen `preserve_thinking` is a provider chat
  template control, not permission for Friday to persist or log reasoning.

### Affected Areas

- `packages/friday-llm/src/friday_llm/telemetry_helper.py`
- `packages/friday-llm/src/friday_llm/telemetry_models.py`
- `packages/friday-llm/src/friday_llm/translation.py`
- `packages/friday-llm/tests_llm/test_telemetry_helper.py`
- `packages/friday-llm/tests_llm/test_telemetry_models.py`
- `packages/friday-llm/tests_llm/test_translation_security.py` (new)

### Required Tests

- Redaction tests with canary API keys, query-string secrets, prompts, tool
  arguments, and reasoning text.
- Boundary tests for every size and depth limit.
- High-cardinality model and endpoint strings are bounded or normalized.
- No payload or extension value appears in captured logs or telemetry events.
- Emitted controls cannot be labeled acknowledged or behaviorally observed
  without the corresponding evidence.

### Acceptance Criteria

- Diagnostics identify translation decisions without sensitive content.
- Provider control fields are bounded before serialization.
- Preserve/replay behavior does not imply persistence permission.

### Dependencies

- Depends on `LLM-RC-01`, `LLM-RC-02`, and `LLM-RC-03`.

### Non-Goals

- Do not persist wire captures in routine telemetry.
- Do not expose raw chain-of-thought through diagnostics.

## LLM-RC-06: Deterministic Validation And Downstream Compatibility

### Purpose

Prove package behavior and detect regressions in Friday packages that consume
the legacy API without modifying their public contracts.

### Implementation Tasks

- `LLM-RC-06-01`: Complete unit and contract coverage for all release-one
  public fields, translations, errors, legacy paths, events, and security rules.
- `LLM-RC-06-02`: Enforce a no-network fixture for the default package suite.
- `LLM-RC-06-03`: Add final HTTP capture tests against a local fake endpoint;
  do not accept `litellm.acompletion` mocks as wire evidence.
- `LLM-RC-06-04`: Run existing Friday Chat, Runtime, Agent, Memory, and
  integration tests that exercise the legacy service contract.
- `LLM-RC-06-05`: Run focused Ruff and meaningful mypy gates on the changed
  package.
- `LLM-RC-06-06`: Run repo-wide gates and separate pre-existing failures from
  upgrade regressions.
- `LLM-RC-06-07`: Verify lockfile consistency and inspect the exact LiteLLM
  resolution.
- `LLM-RC-06-08`: Record validation commands, environment, results, skipped
  tests, and any unrelated baseline debt in a release evidence document.
- `LLM-RC-06-09`: Add an architecture contract test that rejects
  provider/model fields in normalized generation schemas and runs the same
  normalized request through at least two synthetic adapter compositions.

### Required Commands

```bash
uv lock --check
uv run pytest -q packages/friday-llm/tests_llm
uv run ruff check packages/friday-llm
uv run mypy packages/friday-llm/src/friday_llm packages/friday-llm/tests_llm
uv run pytest -q packages/friday-chat/tests_chat
uv run pytest -q packages/friday-runtime/tests_runtime
uv run pytest -q packages/friday-agent/tests_agent
uv run pytest -q packages/friday-memory/tests_memory
uv run pytest -q tests/integration
uv run ruff check .
uv run mypy packages tests main.py
uv run pytest
```

Run focused gates first. If a broad gate fails because of documented unrelated
debt, preserve its exact output and prove that the focused affected scope
passes.

### Required Tests

- No network in the default package suite.
- Translation fixtures pinned to the selected LiteLLM version.
- Provider-independence and synthetic-adapter architecture contracts.
- Concurrency, retry, timeout, cancellation, and circuit-breaker boundaries.
- Downstream legacy constructor and method compatibility.
- Python 3.10, 3.11, 3.12, and 3.13 package test coverage in clean
  environments before publication. Add 3.14 only if package classifiers and
  the selected LiteLLM release intentionally support it.

### Acceptance Criteria

- Every release-one requirement maps to at least one deterministic test.
- Package Ruff, package mypy, package tests, and no-network enforcement pass.
- No affected downstream test failure remains unexplained.
- Broad baseline failures, if any, are demonstrably unrelated and separately
  reported.

### Dependencies

- Depends on `LLM-RC-01` through `LLM-RC-05`.

### Non-Goals

- Do not repair unrelated repository debt in this workstream.

## LLM-RC-07: Opt-In Live LM Studio/Qwen Evidence Lane

### Purpose

Determine whether the exact local target accepts and honors the translated
controls while preserving bounded tool behavior.

### Implementation Tasks

- `LLM-RC-07-01`: Require an explicit environment flag or pytest marker; the
  default package command must never run the live lane.
- `LLM-RC-07-02`: Capture LM Studio version, host architecture, served model
  artifact/revision, quantization, alias, chat template, loaded context length,
  and server settings.
- `LLM-RC-07-03`: Use `http://127.0.0.1:1234/v1`, a placeholder local API-key
  value, fixed synthetic prompts, and the exact selected LiteLLM version.
- `LLM-RC-07-04`: Test explicit disabled mode, enabled mode with every supported
  effort tier, and explicit provider-default mode.
- `LLM-RC-07-05`: Test supported sampling fields separately before testing a
  combined operator profile.
- `LLM-RC-07-06`: Test non-streaming and streaming tool calls, multiple tool
  calls where deterministic enough, and a tool-result follow-up turn.
- `LLM-RC-07-07`: Record emitted fields, response reasoning shape, finish
  reason, token usage, reasoning-token usage if supplied, latency, retry count,
  and assurance level.
- `LLM-RC-07-08`: Bound request count, output tokens, retries, per-request
  duration, total duration, and artifact size.
- `LLM-RC-07-09`: Compare controls using the strongest available server
  metadata and controlled behavior. Absence of visible reasoning text alone is
  not proof of disabled reasoning.

### Required Test Matrix

| Case | Stream | Tools | Required evidence |
| --- | --- | --- | --- |
| provider default | no | no | no contradictory override emitted |
| disabled | no | no | disabled wire field emitted plus strongest available observation |
| enabled plus effort | no | no | effort accepted and response classified |
| disabled | no | one | call ID, name, JSON arguments, finish reason |
| enabled plus effort | no | one | separated reasoning and tool arguments; follow-up correlation |
| disabled | yes | one | streamed tool fragments assemble correctly |
| enabled plus effort | yes | one | reasoning, tools, text, usage, and finish remain separated |

### Evidence Artifact Requirements

- Sanitize all headers and payload content.
- Store normalized field names and fixed synthetic prompt identifiers rather
  than raw request bodies.
- Hash the model/config fingerprint and evidence file.
- Record unsupported or inconclusive cases explicitly.
- Do not commit local LM Studio state, logs containing prompts, or model files.

### Acceptance Criteria

- Every advertised profile is emitted and accepted.
- Tool invariants pass under disabled and at least one enabled effort profile.
- Evidence language matches its actual assurance level.
- Inconclusive behavioral evidence is not upgraded to behaviorally observed or
  verified.

### Dependencies

- Depends on `LLM-RC-06`.

### Non-Goals

- Do not require this lane in ordinary CI.
- Do not run ART host or Docker regressions here.

## LLM-RC-08: Package Build, Rehearsal, Publication, And Verification

### Purpose

Produce immutable, inspectable artifacts, prove clean installation, and publish
only after separate upload authorization.

### Implementation Tasks

- `LLM-RC-08-01`: Update package version to `0.1.0a1`, preserve exact internal
  `0.1.0a0` pins, set the selected exact LiteLLM dependency, and regenerate
  `uv.lock`.
- `LLM-RC-08-02`: Parameterize metadata and artifact validators with target
  version and package subset. Preserve reservation-build defaults only when
  explicitly selected.
- `LLM-RC-08-03`: Update the package README with typed and legacy examples,
  supported profile matrix, migration table, assurance terminology, telemetry
  privacy, and live-test instructions.
- `LLM-RC-08-04`: Add release notes and a migration note covering the
  deprecation window, global LiteLLM side-effect removal, dependency pin, new
  methods, and deferred dialects.
- `LLM-RC-08-05`: Build only `friday-framework-llm` into a new version-specific
  artifact directory; never mix it with reservation artifacts.
- `LLM-RC-08-06`: Run Twine metadata checks, artifact-content checks, secret and
  local-state scans, and SHA-256 hashing.
- `LLM-RC-08-07`: Install the wheel in a fresh environment using published
  `core==0.1.0a0` and `telemetry==0.1.0a0`; run `pip check`, public imports,
  legacy smoke, and typed fake-transport smoke.
- `LLM-RC-08-08`: Build a wheel from the sdist and repeat the clean-install
  smoke so the sdist is independently usable.
- `LLM-RC-08-09`: Rehearse on TestPyPI using an explicit first-index strategy or
  preinstalled production dependencies. Do not use an ambiguous best-match
  multi-index resolution.
- `LLM-RC-08-10`: Prefer PyPI Trusted Publishing and automatic attestations.
  If unavailable, require separate approval for a token-based upload and never
  place the token in source, config, command arguments, logs, or evidence.
- `LLM-RC-08-11`: After explicit publication approval, upload the exact tested
  artifacts without rebuilding them.
- `LLM-RC-08-12`: Install the exact PyPI version in a clean environment and
  verify version, dependencies, README, project URLs, hashes, imports, legacy
  smoke, typed fake-transport smoke, and attestation/provenance.
- `LLM-RC-08-13`: Tag the exact artifact-producing commit only after
  post-publication verification passes.

### Build And Artifact Commands

Use a version-specific directory chosen before execution, for example:

```bash
uv build --package friday-framework-llm \
  --out-dir dist/friday-framework-llm-0.1.0a1
uv run --with twine twine check dist/friday-framework-llm-0.1.0a1/*
python3 scripts/check-package-metadata.py \
  --version 0.1.0a1 \
  --package friday-framework-llm
python3 scripts/check-package-artifacts.py \
  dist/friday-framework-llm-0.1.0a1 \
  --version 0.1.0a1 \
  --package friday_framework_llm
```

The validator options above are required deliverables and do not exist at
intake.

### Required Artifact Checks

- Exactly one sdist and one universal wheel for the target version.
- Wheel contains the intended `friday_llm` modules and `dist-info` metadata.
- Sdist contains the build metadata, license, README, source, and intended tests
  without local state.
- Metadata dependencies match the approved exact versions.
- README renders correctly on TestPyPI/PyPI.
- No `.env`, `.friday`, Chroma, transcript database, cache, recovery code, API
  key, private prompt, raw reasoning, local absolute path, or wire capture with
  sensitive content is present.
- Wheel and sdist hashes are recorded before upload and unchanged afterward.

### Acceptance Criteria

- The exact built wheel and sdist pass metadata, content, install, dependency,
  import, and behavior smoke tests.
- TestPyPI rehearsal passes before production upload.
- Production upload uses the already tested artifacts.
- Clean post-publication installation resolves only published dependencies.
- PyPI metadata, files, hashes, and provenance match the evidence record.

### Dependencies

- Build preparation depends on `LLM-RC-06` and `LLM-RC-07`.
- TestPyPI and PyPI upload each require separate explicit authorization.

### Non-Goals

- Do not publish the root meta-package or unrelated components.
- Do not upload from the old reservation artifact directory.

## LLM-RC-09: Friday Release Closeout And ART Handoff

### Purpose

Close the Friday work with reproducible evidence and provide ART everything
needed for a separately authorized published-package integration.

### Implementation Tasks

- `LLM-RC-09-01`: Publish the final supported capability matrix, API reference,
  migration table, and assurance terminology.
- `LLM-RC-09-02`: Record exact validation commands and results, Python versions,
  selected LiteLLM version, live environment fingerprint, artifact hashes,
  PyPI URL, and release tag.
- `LLM-RC-09-03`: Document every deferred dialect, unsupported control, known
  limitation, and inconclusive live observation.
- `LLM-RC-09-04`: Provide ART with the exact package constraint, typed API
  example, transport-target and model-target values, config mapping,
  compatibility notes, and required evidence fields.
- `LLM-RC-09-05`: Confirm that ART must resolve the published distribution and
  must not use a local Friday checkout as integration evidence.
- `LLM-RC-09-06`: Open or update the ART follow-on only under separate ART
  authority; do not modify ART during Friday closeout.

### Required Evidence

- Friday release evidence document.
- Sanitized wire-investigation report.
- Capability and translation matrix.
- Migration and deprecation note.
- PyPI artifact identities and hashes.
- ART handoff checklist.

### Acceptance Criteria

- Friday release completion is independently decidable without ART changes.
- ART can implement its adapter without guessing Friday types, defaults,
  provider identity, or evidence semantics.
- Deferred work is not represented as delivered.

### Dependencies

- Depends on `LLM-RC-08` post-publication verification.

### Non-Goals

- Do not authorize or implement ART changes.

## File And Module Ownership Expectations

### Authorized Implementation Scope After Freeze Release

- `packages/friday-llm/src/friday_llm/`
- `packages/friday-llm/tests_llm/`
- `packages/friday-llm/pyproject.toml`
- `packages/friday-llm/README.md`
- `uv.lock`
- package-aware changes to:
  - `scripts/check-package-metadata.py`
  - `scripts/check-package-artifacts.py`
  - `scripts/smoke-install-artifacts.sh`
- Friday LLM planning, reference, migration, release, and evidence documents

### Validation-Only Consumer Scope

- `packages/friday-chat/`
- `packages/friday-runtime/`
- `packages/friday-agent/`
- `packages/friday-memory/`
- `packages/friday-core/`
- `tests/integration/`

Do not edit validation-only consumer source or tests in this release. If a
required consumer change is discovered, stop and reclassify the release as a
coordinated package change with an updated plan and version decision.

## Requirement Traceability

| Requirement area | Owning workstreams |
| --- | --- |
| Typed reasoning config | `LLM-RC-01`, `LLM-RC-02` |
| Typed sampling config | `LLM-RC-01`, `LLM-RC-02` |
| Model-independent normalized contracts | `LLM-RC-01`, `LLM-RC-02`, `LLM-RC-06` |
| Independent transport and model identity | `LLM-RC-01`, `LLM-RC-02`, `LLM-RC-03` |
| Composed capability state and provenance | `LLM-RC-00`, `LLM-RC-01`, `LLM-RC-02`, `LLM-RC-05` |
| Service defaults and request overrides | `LLM-RC-01`, `LLM-RC-02`, `LLM-RC-03` |
| Layered provider-aware translation | `LLM-RC-00`, `LLM-RC-02`, `LLM-RC-03` |
| Typed bounded provider options | `LLM-RC-01`, `LLM-RC-02`, `LLM-RC-05`; public registration deferred |
| Tool-call invariants | `LLM-RC-03`, `LLM-RC-04`, `LLM-RC-07` |
| Observability and privacy | `LLM-RC-02`, `LLM-RC-05` |
| Backward compatibility | `LLM-RC-01`, `LLM-RC-03`, `LLM-RC-06` |
| Wire investigation | `LLM-RC-00`, `LLM-RC-06`, `LLM-RC-07` |
| PyPI release | `LLM-RC-08`, `LLM-RC-09` |
| ART follow-on | `LLM-RC-09`; implementation remains external |

## Documentation Closeout

Before publication, update or add:

- package README and examples;
- generated or hand-written API reference for public models, methods, events,
  errors, and compatibility behavior;
- capability/translation matrix;
- target-identity, capability-source, and adapter composition reference;
- sanitized wire-investigation report;
- migration and deprecation guide;
- release notes;
- live-test operator instructions;
- package-specific release checklist and evidence record;
- PyPI preparation plan status for the component exception.

Documentation must clearly separate:

- Friday defaults from model-card recommendations;
- normalized generation intent from target identity and provider options;
- capability support from wire translation and model recommendations;
- configured, resolved, emitted, acknowledged, and behaviorally observed state;
- legacy compatibility from new strict behavior;
- release-one support from deferred dialects;
- Friday package completion from ART integration completion.

## Deferred Items

- OpenAI Responses API.
- LM Studio native REST API.
- Anthropic-native, Gemini, Ollama, DeepSeek, Moonshot, Bedrock, vLLM, and
  SGLang normalized profiles.
- Public provider-extension registration.
- Runtime capability probing as an authority source.
- Downstream Friday package migration to typed requests or typed streaming.
- Change of the default legacy reasoning behavior from disabled to auto.
- Removal of `thinking_enabled`; target no earlier than `0.2.0` after migration
  evidence.
- Wider LiteLLM dependency ranges.
- Root meta-package and coordinated framework version update.
- ART configuration and runtime integration.

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| LiteLLM changes provider translation | Exact alpha dependency, captured wire fixtures, version recorded in diagnostics |
| LM Studio accepts but ignores a field | Assurance-state model and controlled live comparison |
| First Qwen/LM Studio profile shapes the generic API | Contract tests forbid provider/model fields in normalized generation models; synthetic adapters prove substitution |
| Capability overlays disagree | Tri-state per-control composition with provenance and typed preflight conflicts |
| Translation layers overwrite one another | Typed call-spec builder rejects semantic field collisions before transport |
| Legacy default changes unintentionally | Explicit compatibility truth table and regression tests |
| New config leaks across concurrent requests | Frozen resolved call spec materialized before I/O and concurrency tests |
| Streaming tools corrupt arguments | Typed events, index/ID assembly, fragmented-delta tests |
| Global LiteLLM flags affect host applications | Remove import mutation and use per-call compatibility settings |
| Reasoning content leaks | Never log or telemetry raw reasoning; canary redaction tests |
| Package-only release violates dependency expectations | Document component exception, verify published internal dependencies, do not update root meta-package implicitly |
| Broad typing debt hides new errors | Remove suppressions from touched public modules; stop for policy-compliant waiver if necessary |
| TestPyPI resolves an unintended dependency | Explicit first-index strategy or preinstalled exact production dependencies |
| PyPI artifact differs from tested artifact | Hash before upload, do not rebuild, verify post-upload hash and provenance |

## Final Acceptance Criteria

This tactical plan is complete when all of the following are true:

- Framework-upgrade implementation authority was explicitly recorded.
- `friday-framework-llm==0.1.0a1` contains the approved immutable typed API.
- Normalized generation models contain no provider-, engine-, or model-specific
  controls; transport identity, model identity, capabilities, and typed
  provider options remain separate.
- Legacy methods remain source compatible for one documented deprecation
  window.
- The exact supported LM Studio/Qwen/OpenAI Chat profile is validated from
  Friday input through captured wire payload.
- New unsupported controls fail before external I/O with typed actionable
  errors.
- Conflicting capability sources and translator field collisions fail before
  external I/O, while unknown `auto` emits no override.
- Streaming text, reasoning, tools, usage, and finish events remain separated.
- Importing the package does not change LiteLLM unsupported-parameter policy
  globally.
- Package tests, Ruff, meaningful mypy, no-network enforcement, and affected
  downstream validation pass.
- The bounded live lane passes or the release stops without weakening claims.
- README, API, migration, capability, release, and evidence documents are
  complete.
- Wheel and sdist pass clean build, metadata, content, secret, install,
  dependency, import, and fake-transport behavior checks.
- TestPyPI rehearsal passes.
- Production upload was separately authorized and used the exact tested
  artifacts.
- Clean post-publication verification confirms version, dependency resolution,
  hashes, metadata, imports, behavior smoke, and provenance.
- ART receives a published-package handoff without Friday modifying ART.
