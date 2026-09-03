# Requirement: Friday LLM Reasoning and Sampling Controls

## Status

- State: accepted as the originating requirement; Friday tactical plan approved
- Implementation authority: granted on 2026-08-27 for the scope defined by the
  tactical plan; TestPyPI, PyPI, and ART implementation remain separately gated
- Priority: high for reasoning-model interoperability
- Discovered during: `TU-WP-07P` local LM Studio CLI regression preparation
- Implementation owner: Friday development team
- ART integration owner: ART team, after a compatible Friday release is
  published and validated
- ART runtime implementation authority: not granted by this issue
- Friday tactical plan:
  [tactical-implementation-plan.md](tactical-implementation-plan.md)

## Executive Summary

Friday's current LLM service exposes a single `thinking_enabled` boolean and
maps a disabled value to one provider-shaped request field. That contract is
too narrow for current reasoning models and does not prove that the configured
control reaches or is honored by an OpenAI-compatible endpoint.

Friday should add typed, per-service reasoning and sampling configuration whose
semantics do not depend on a model or provider. Provider, endpoint, serving
engine, and model-specific behavior belongs behind capability and translation
contracts, with bounded typed provider options for controls that cannot yet be
normalized. The same translation must be used for streaming and non-streaming
requests and must preserve tool-call behavior.

After Friday publishes this capability, ART will replace its global thinking
toggle with per-service configuration, pass the new settings through its sole
Friday adapter, update its schema and documentation, and rerun mandatory live
CLI tool-use regressions against LM Studio in host and Docker modes.

## Relationship To TU-WP-07P

This requirement was identified in ART while preparing the mandatory local LM
Studio and Docker CLI regression lane associated with `TU-WP-07P`. It has been
ported into the Friday repository as the source requirement for a separately
governed Friday package upgrade.

This issue does not expand the MCP producer scope or authorize ART runtime
implementation. Friday implementation authority is controlled by the linked
tactical plan and repository policy. Until the Friday work and ART integration
are complete,
`thinking_enabled: false` must be described as configured intent rather than a
verified effective LM Studio/Qwen wire behavior.

If `TU-WP-07P` closes before this issue, its live evidence must not claim that
reasoning was disabled solely because the ART configuration contained the
boolean. Tool-use results and reasoning-control effectiveness are separate
claims and require separate evidence.

## Problem Statement

Reasoning-capable models expose more than an on/off switch. Depending on the
model and serving framework, useful controls can include:

- whether reasoning is enabled;
- reasoning effort or depth;
- a reasoning-token budget;
- whether prior reasoning is retained across turns;
- temperature and nucleus/top-k/minimum-probability sampling;
- presence, frequency, or repetition penalties.

The exact request field and accepted value set vary by provider, endpoint
family, model, and inference framework. Passing one provider's request shape to
another endpoint can be ignored, rejected, or produce behavior different from
the operator's intent.

Friday currently lacks a typed contract that can represent these controls and
translate them deliberately. ART consequently cannot configure them without
either provider-specific leakage into runtime core or an unverified generic
payload escape hatch. A single profile keyed by provider, endpoint, server, and
model would avoid the escape hatch but would still hard-code the first tested
combination into the architecture and create a combinatorial profile matrix.

## Verified Current State

### ART configuration

`src/art/runtime_config/models.py` currently defines:

- global `llm.thinking_enabled: bool`;
- per-service `temperature`;
- per-service `max_tokens`;
- no reasoning effort, reasoning budget, preserved-thinking, `top_p`, `top_k`,
  `min_p`, presence-penalty, frequency-penalty, or repetition-penalty fields.

The global location is problematic because an ART pool can contain models with
different reasoning capabilities and provider dialects.

### ART-to-Friday mapping

`src/art/providers/friday_llm.py` constructs `LiteLLMService` with:

- model name;
- API key;
- API base;
- resilience settings;
- the global ART `thinking_enabled` value.

Although ART's service configuration has a `provider` field, the current
constructor call does not pass an explicit provider/dialect identity to
Friday. A provider-aware implementation must not rely only on a loose model
name heuristic when choosing request semantics.

### Friday behavior

The repository Friday LLM implementation at intake is
`friday-framework-llm==0.1.0a0`. It stores `thinking_enabled` on
`LiteLLMService`. For both ordinary and streaming completion calls, a false
value adds this LiteLLM argument:

```python
thinking={"type": "disabled"}
```

This proves the Friday-to-LiteLLM argument, but it does not prove the final
HTTP JSON emitted by LiteLLM or the behavior selected by LM Studio's Qwen chat
template.

At intake, the package also:

- declares `litellm>=1.81.0` and resolves `1.81.3` in `uv.lock`;
- sets process-global `litellm.modify_params = True` and
  `litellm.drop_params = True` during package import;
- defaults ordinary and streaming requests to `temperature=0.7`;
- returns text-only `AsyncIterator[str]` values from its public streaming
  method, without exposing streamed reasoning, tool-call, usage, or finish
  events;
- returns only prompt, completion, and total token counts from non-streaming
  requests;
- has no deterministic package tests for the existing `thinking_enabled`
  request mapping.

These are implementation-reality constraints for the Friday tactical plan, not
desired end-state behavior.

### Model and server behavior

The official
[Qwen3.8-27B model card](https://huggingface.co/Qwen/Qwen3.8-27B/blob/main/README.md)
states that thinking is enabled by default, documents `reasoning_effort`,
documents `preserve_thinking`, and shows an OpenAI-compatible example using
`chat_template_kwargs.enable_thinking` to disable thinking. It also publishes
different recommended sampling profiles for thinking and non-thinking modes
while warning that inference-framework support varies.

LM Studio's
[native chat API](https://lmstudio.ai/docs/developer/rest/chat) exposes a
`reasoning` setting with `off`, `on`, `low`, `medium`, and `high` values and
also exposes several sampling controls. LM Studio separately supports
OpenAI-compatible endpoints, so the native API contract alone does not prove
which representation Friday/LiteLLM emits or which controls the compatibility
endpoint honors.

### Tool-use evidence

The current local ART regression exercised representative tool-capable CLI
flows against `qwen3.8-27b-mlx` in both host and Docker modes successfully.
That is positive evidence for the tested tool-schema and tool-result path. It
does not prove that `thinking_enabled: false` took effect, and it does not cover
tool behavior under multiple reasoning or sampling profiles.

## Required Friday Capability

### 1. Typed reasoning configuration

Friday must introduce a typed reasoning configuration rather than adding a
collection of unrelated constructor booleans. The contract must be capable of
representing at least:

```yaml
reasoning:
  mode: disabled       # auto | enabled | disabled
  effort: low          # optional; supported values are capability-dependent
  budget_tokens: null  # optional positive integer
  preserve: false      # optional
```

Requirements:

- `auto` leaves model/provider defaults in control and emits no contradictory
  override.
- `enabled` and `disabled` express operator intent without assuming one wire
  representation.
- Effort and budget are optional because some providers expose only one of
  them.
- Preserved reasoning is independently configurable where supported.
- Invalid combinations fail during configuration or request preflight.
- Resolved configuration is immutable for an in-flight request.

Friday may choose different public type or field names, but it must preserve
these semantics.

### 2. Typed sampling configuration

Friday must provide typed optional fields for at least:

```yaml
sampling:
  temperature: 0.3
  top_p: null
  top_k: null
  min_p: null
  presence_penalty: null
  frequency_penalty: null
  repetition_penalty: null
```

Requirements:

- An unset field means no Friday override; it must not be replaced silently by
  an arbitrary Friday default.
- Ranges must be validated using the selected provider/model capability where
  ranges differ.
- Friday must distinguish similarly named but non-equivalent fields, such as
  `repetition_penalty` and an endpoint's `repeat_penalty`.
- Friday must not hard-code Qwen's recommended values as universal defaults.
- ART's desired local `temperature: 0.3` is an explicit operator profile, not a
  proposed package-wide default.

### 3. Defaults and per-request overrides

The service must support:

- service-level default reasoning and sampling configuration;
- explicitly bounded per-request overrides where the Friday protocol permits
  them;
- deterministic merge rules;
- no mutation of defaults by an individual request.

The ordinary and streaming completion methods must resolve configuration by
the same code path.

### 4. Model-independent intent and provider-aware translation

The normalized public generation contract must remain independent of any
provider, endpoint dialect, serving engine, or model family. In particular,
`ReasoningConfig`, `SamplingConfig`, `GenerationConfig`, and request overrides
must not acquire Qwen-, Anthropic-, OpenAI-, or LM Studio-specific fields or
value names.

Operational target identity is separate from generation intent. Friday must
represent at least these independent axes:

- transport provider and endpoint dialect;
- serving engine, when it changes compatible-endpoint behavior;
- model ID, model family, and optional model revision;
- an optional explicit operator capability declaration with provenance.

Capabilities must be composed per control from those sources rather than
encoded only as a provider/dialect/engine/model tuple. Each applicable record
must resolve to `supported`, `unsupported`, or `unknown`, with its constraints
and provenance. No record means that a source has no opinion; it is distinct
from an applicable record whose state is `unknown`.

Composition must follow an explicit lattice:

- any applicable authoritative `unsupported` record resolves unsupported;
- an applicable required source that remains `unknown` keeps the result unknown;
- at least one authoritative source must claim support before a control can
  resolve supported;
- numeric ranges and value sets are intersected, and an empty intersection is a
  typed configuration conflict;
- an operator declaration may refine `unknown`, but may not silently override
  `unsupported`, widen built-in constraints, or contradict a built-in record.

Friday must keep three concerns distinct:

- capability: whether a target can accept a normalized control and its range;
- translation: how accepted normalized intent becomes a wire representation;
- recommendation: optional model guidance that never becomes a Friday default.

Translation must be composable in this order:

```text
provider-neutral intent
  -> target and capability resolution
  -> endpoint-dialect translator
  -> provider/serving-engine overlay
  -> model-family or revision quirk overlay
  -> immutable LiteLLM call specification
```

Friday must select these layers using explicit target information. It must not
create a public class for every provider/model combination or infer support from
a loose model-name substring. The translation system must distinguish, where
applicable:

- OpenAI-compatible Chat Completions;
- OpenAI-compatible Responses;
- Anthropic-style reasoning/thinking controls;
- LM Studio's native API;
- Qwen chat-template controls passed through a compatible endpoint;
- providers that support no reasoning controls.

Required behavior:

- A requested supported control is emitted in the provider's documented form.
- A requested unsupported control is rejected with a typed, actionable error
  before the external request unless an explicit compatibility policy says
  otherwise.
- An explicit control whose composed capability is `unknown` is rejected before
  external I/O; `auto` may emit no override against an unknown capability.
- Friday must never silently report a dropped control as emitted,
  acknowledged, or behaviorally effective.
- Provider defaults remain distinguishable from an explicit operator request.
- Capability detection must be deterministic and inspectable.
- Every emitted wire field must retain its owning translator and provenance.
  Additive writes are allowed; replacement or removal requires a registered,
  named overlay rule with an expected prior owner and focused tests. Any other
  collision fails before transport.

### 5. Bounded provider extensions

Friday must provide a constrained extension mechanism for newly introduced
provider parameters that do not yet have normalized fields. Provider-specific
options must use typed, namespaced models owned by the applicable adapter. The
normalized generation models must not expose unrestricted mappings or absorb
provider-specific fields.

The mechanism must:

- be namespaced by provider or endpoint family;
- use a typed adapter-owned option model or discriminated union at the public
  boundary, not `dict[str, Any]`;
- accept only JSON-compatible non-secret values;
- use an allowlist or registered translator rather than unrestricted `**kwargs`;
- reject attempts to override Friday-owned message, tool, credential,
  telemetry, timeout, or resilience fields;
- be redacted and bounded in logs and telemetry;
- never become a bypass around capability validation.

### 6. Tool-call invariants

Reasoning and sampling work must not change the semantic tool contract.

For every supported reasoning mode, Friday must preserve:

- input tool schemas and explicit tool-choice behavior;
- tool-call IDs;
- tool names;
- JSON arguments without reasoning-text contamination;
- multiple tool calls and their ordering semantics;
- finish reasons;
- streaming tool-call fragment assembly;
- final response content separately from reasoning content;
- tool-result correlation on the following model request.

Reasoning content must not be mistaken for final content or parsed as tool
arguments.

### 7. Observability

Friday telemetry and debug diagnostics must expose bounded metadata sufficient
to troubleshoot translation:

- requested reasoning configuration;
- selected transport provider, endpoint dialect, serving engine, and model
  family/revision identifiers;
- composed capability state, source versions, and provenance;
- resolved normalized reasoning configuration;
- requested, resolved, and emitted sampling field names;
- unsupported or dropped-field decisions;
- whether reasoning content was returned;
- reasoning-token usage when the provider supplies it.

Diagnostics must not expose API keys, prompt bodies, raw private reasoning,
tool arguments, or unrestricted provider payloads.

## Backward Compatibility

The Friday release must preserve existing callers during a documented
transition.

Minimum requirements:

- Continue accepting `thinking_enabled` for one deprecation window.
- Map the legacy boolean deterministically to the new reasoning mode.
- Reject simultaneous contradictory legacy and new configuration.
- Preserve existing completion method defaults unless a versioned change is
  explicitly documented.
- Preserve current tool-call response types and parsing behavior.
- Document whether the change fits the current Friday `0.1.x` compatibility
  line or requires a coordinated ART dependency-bound update.

ART currently constrains `friday-framework-llm` to
`>=0.1.0a0,<0.2.0`; a `0.2.x` delivery therefore requires an explicit ART
dependency change and lockfile update.

## Required Investigation Before Implementation

The Friday team must first capture the actual outbound JSON after LiteLLM
translation. The investigation must compare at least:

1. no reasoning override;
2. the current `thinking={"type": "disabled"}` argument;
3. Qwen's documented `chat_template_kwargs.enable_thinking` form;
4. supported reasoning-effort settings;
5. supported preserved-thinking settings;
6. LM Studio's documented native reasoning control, if the native adapter is
   in scope.

For each case, record:

- Friday input configuration;
- LiteLLM call arguments;
- sanitized final HTTP request fields;
- endpoint and model identity;
- response content/reasoning field shape;
- available token usage and finish reason;
- whether the endpoint rejected, ignored, or honored the control;
- latency and retry count within bounded test limits.

Absence of visible reasoning text alone is not sufficient proof that reasoning
was disabled. The finding must use the strongest response metadata and
controlled behavioral comparison the endpoint provides.

## Acceptance Test Matrix

### Deterministic package tests

Friday must test:

- validation and serialization of every normalized field;
- absence of provider-, engine-, and model-specific fields from the normalized
  generation models;
- deterministic default/override merging;
- legacy `thinking_enabled` compatibility and conflicts;
- each registered provider translation;
- capability composition, provenance, `unknown` handling, and source-conflict
  rejection;
- at least two synthetic adapter targets that map the same normalized intent to
  different call specifications without changing the normalized request;
- unsupported-control failure before external I/O;
- typed provider-option namespace, allowlist, and protected-field rejection;
- identical translation logic for streaming and non-streaming setup;
- telemetry redaction and boundedness;
- no real network access in the default unit suite.

### Tool-call tests

At minimum, test these combinations with deterministic fake transports:

- reasoning `auto`, `enabled`, and `disabled` with one tool call;
- each supported effort tier with one tool call;
- multiple tool calls;
- malformed tool arguments;
- streamed tool arguments split across chunks;
- reasoning content plus tool calls in one provider response;
- a tool result followed by another reasoning-enabled model request;
- provider rejection of an unsupported combination.

### Live LM Studio tests

Provide an explicit opt-in, bounded test against an exact served model. For the
current ART integration target, use:

- endpoint: `http://127.0.0.1:1234/v1`;
- model: `qwen3.8-27b-mlx`;
- OpenAI-compatible transport;
- placeholder local API-key value only;
- no committed credential or local-secret value.

The live test must cover:

- direct non-thinking response;
- at least one supported reasoning-effort setting;
- non-streaming tool call;
- streaming tool call;
- sanitized wire-field evidence;
- bounded token, request, retry, duration, and artifact limits.

The package's default test command must never activate this live lane.

## Friday Deliverables

The Friday team should return:

1. the typed public reasoning and sampling API;
2. the capability and translation matrix separated by dialect, provider,
   serving engine, model family, and model revision;
3. deterministic unit and tool-call tests;
4. the sanitized LM Studio/Qwen wire-investigation report;
5. API reference and migration documentation;
6. release notes identifying compatibility and deprecations;
7. a published package version and integrity metadata;
8. exact validation commands and results.

The API reference must show normalized generation models separately from
transport targets, model targets, capability records, and typed provider-option
models. A release-one Qwen or LM Studio example must not be presented as the
generic contract.

The Friday deliverables are complete when the Friday package release and its
post-publication verification pass. ART adoption is a downstream integration
gate and does not block closing the Friday implementation plan.

## ART Follow-On Integration

After Friday delivers a compatible release, ART will perform a separately
authorized integration that:

1. updates the controlled Friday dependency and `uv.lock`;
2. adds nested per-service reasoning and sampling configuration;
3. migrates/deprecates global `llm.thinking_enabled` without silently changing
   existing configurations;
4. passes explicit transport and model target information through the sole
   Friday adapter as required by the Friday API;
5. carries supported per-request overrides through ART's provider-neutral
   request contract;
6. updates `config/example.yaml`, the runtime config schema, compatibility
   fixtures, operator documentation, and inspection output;
7. preserves the rule that only `src/art/providers/friday_llm.py` imports
   Friday packages directly;
8. reruns strict configuration, adapter-mapping, tool-call, CLI, and restore
   tests;
9. reruns the mandatory real LM Studio host and Docker CLI regression matrix;
10. records requested, resolved, emitted, acknowledged, and behaviorally
    observed reasoning states in bounded evidence.

The ART integration must not use a local Friday checkout as its release
evidence. The normal repository configuration must resolve the published,
controlled Friday distribution.

## Friday Completion Criteria

The Friday delivery is complete only when:

- Friday has published the validated capability and handoff artifacts;
- legacy Friday configuration behavior has migration coverage;
- deterministic Friday package and downstream contract tests pass;
- the bounded Friday live LM Studio lane passes;
- captured evidence supports the claimed assurance level without treating
  configured or emitted intent as behaviorally effective;
- architecture tests prove that provider-specific behavior is isolated behind
  capability, translation, and typed option contracts;
- documentation distinguishes model recommendations from Friday defaults; and
- a clean environment resolves and imports the exact published distribution.

## ART Integration Closure Criteria

The originating ART follow-on is complete only when:

- ART has approved a separate integration scope;
- ART configuration and adapter mapping consume the published API;
- ART legacy configuration behavior has migration coverage;
- ART deterministic tool-call invariants pass;
- ART host and Docker LM Studio CLI regressions pass; and
- ART evidence records the published Friday version and requested, emitted,
  acknowledged, and behaviorally observed control states without conflating
  them.

Until the applicable Friday or ART gate passes, the existing boolean must not
be treated as a portable, verified reasoning-control contract.
