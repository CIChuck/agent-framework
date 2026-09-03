# Deferred Feature Upgrade: Model-Aware Reasoning Control

## Status

- State: deferred for later reconsideration
- Decision date: 2026-09-02
- Classification: future Friday LLM feature upgrade
- Implementation authority: not granted
- Active design authority: not granted
- Current action: preserve the findings and make no further source,
  configuration, API, or release changes for this feature
- Related requirement:
  [Friday LLM reasoning and sampling controls requirement](friday-llm-reasoning-and-sampling-controls-requirement.md)
- Related completed plan:
  [Friday LLM reasoning controls tactical implementation plan](friday-llm-reasoning-controls-tactical-implementation-plan.md)

## Deferral Decision

Friday will not attempt to solve model-aware reasoning disablement in the
current upgrade. The investigation established that the problem crosses model,
provider, endpoint, serving-engine, prompt-template, and dependency boundaries.
Resolving it responsibly requires a separately approved feature upgrade rather
than another tactical adjustment to the current translator or example
configuration.

This record documents the assertion, evidence, limitation, and conditions for
a future revisit. It is not an implementation plan and does not select a future
API, adapter, capability schema, or provider strategy.

## Validated Assertion

The investigation supports this assertion:

> A provider-independent reasoning intent cannot, by itself, guarantee that
> reasoning is disabled. Effective control depends on the selected model family
> and revision together with the provider, API dialect, serving engine, prompt
> template, and server version that interpret the request.

LiteLLM can normalize or transport parameters for supported integrations, but
it does not control the model's prompt template or guarantee that a downstream
server honors an accepted field. Friday must therefore distinguish normalized
intent and emitted wire fields from effective model behavior.

The strongest accurate statement for the currently tested target is:

```text
requested: disabled
resolved: disabled
emitted: chat_template_kwargs.enable_thinking=false
acknowledged: not established
behaviorally observed: reasoning remained enabled
```

## Local Evidence

### Tested target

- Model alias: `qwen3.8-27b-mlx`
- Model revision:
  `lmstudio-community/Qwen3.8-27B-MLX-8bit`
- Serving engine: LM Studio
- Endpoint dialect: OpenAI-compatible Chat Completions
- Endpoint: allowlisted loopback service at `http://127.0.0.1:1234/v1`
- Friday transport dependency: LiteLLM
- Prompt: fixed synthetic instruction requesting the single visible word
  `READY`
- Raw reasoning content was not recorded.

### Wire evidence

Friday's deterministic final-HTTP capture proves that the current
Qwen3.8/LM Studio translator emits:

```json
{
  "chat_template_kwargs": {
    "enable_thinking": false
  }
}
```

The relevant implementation is
[Friday LLM translation](../../../../packages/friday-llm/src/friday_llm/translation.py),
and its final-wire regression coverage is in
[test_wire_capture.py](../../../../packages/friday-llm/tests_llm/test_wire_capture.py).
This evidence proves transmission through LiteLLM. It does not prove that LM
Studio or the selected model template applied the field.

### Live behavioral evidence

The opt-in Friday LLM and Friday Chat live suites passed functionally against
the target: `17 passed` in 60.16 seconds. Reasoning modes, streaming, tool
calls, and the bounded Friday Chat turn path all completed without a functional
request failure.

A subsequent controlled comparison measured five warmed requests for each of
the explicit disabled and enabled modes:

| Measurement | Disabled median | Enabled median |
| --- | ---: | ---: |
| First stream event | 489.0 ms | 488.4 ms |
| First visible text | 1,637.3 ms | 1,638.6 ms |
| Complete response | 1,643.2 ms | 1,645.6 ms |

A count-only follow-up observed identical reasoning behavior in both modes:

| Observation | Disabled | Enabled |
| --- | ---: | ---: |
| Reasoning events | 18 | 18 |
| Reasoning characters | 84 | 84 |
| Provider-reported reasoning tokens | 18 | 18 |
| Visible events | 2 | 2 |
| Visible characters | 7 | 7 |

The live comparison therefore did not behaviorally verify the disabled mode.
It instead demonstrated that the currently loaded LM Studio/Qwen3.8 route did
not distinguish the two requested modes. The approximately 1.15-second interval
between the first reasoning event and first visible text remained in both
cases.

## External Findings

Web research was performed on 2026-09-02 using official model/provider
documentation and official project issue trackers.

### Qwen3.8

The official
[Qwen3.8-27B model card](https://huggingface.co/Qwen/Qwen3.8-27B-FP8)
states that thinking is enabled by default and can be disabled per request. For
self-hosted OpenAI-compatible inference it shows
`chat_template_kwargs.enable_thinking=false`; for Qwen Cloud it requires the
different top-level `enable_thinking=false` representation.

The same model card publishes different recommended generation settings for
thinking and non-thinking modes and warns that inference-framework support for
sampling controls varies. This means a mode change may require a coordinated
model-specific sampling profile rather than only a boolean field.

### LM Studio

LM Studio's
[native chat API](https://lmstudio.ai/docs/developer/rest/chat) uses a distinct
`reasoning` field with values including `off`, and reports an error when the
selected model does not support the requested setting.

LM Studio's
[model.yaml documentation](https://beta.lmstudio.ai/docs/app/modelyaml)
describes model-specific custom fields that can set the `enable_thinking` Jinja
variable. It also states that the mechanism works only when the selected prompt
template defines that variable. Therefore the loaded model artifact and prompt
template participate in whether the control is effective.

The official LM Studio tracker also contains
[a report that Qwen thinking parameters were ignored](https://github.com/lmstudio-ai/lmstudio-bug-tracker/issues/1559)
through an OpenAI-compatible route. An issue report is not a universal product
contract, but it is consistent with Friday's live observation and reinforces
the need for behavioral verification.

### Other model families and providers

The model dependence is not unique to Qwen:

- [Google's Gemini thinking documentation](https://ai.google.dev/gemini-api/docs/generate-content/thinking?hl=en)
  describes models that can disable thinking with `thinkingBudget=0`, models
  that cannot disable it, and newer modes where `minimal` does not guarantee
  that reasoning is absent.
- [Anthropic's thinking documentation](https://platform.claude.com/docs/en/about-claude/models/extended-thinking-models)
  describes model-specific differences among disabled, adaptive, and manual
  thinking, including models that reject disabled thinking and effort values
  that conflict with it.
- [OpenAI's GPT-5.1 model documentation](https://developers.openai.com/api/docs/models/gpt-5.1)
  documents `reasoning.effort=none` for that model, while other OpenAI models
  expose different allowed effort sets and defaults.

These differences show that `disabled`, `none`, `off`, a zero budget, and a
minimal effort are not portable synonyms.

### LiteLLM boundary

The current Friday wire test establishes that LiteLLM transports the selected
nested Qwen field in this integration. The failure is therefore not evidence
that LiteLLM always drops the field. It is evidence that successful transport
alone cannot establish effective model behavior.

An open
[LiteLLM issue concerning chat-template controls](https://github.com/BerriAI/litellm/issues/31092)
also reports a backend where the required template parameter cannot be conveyed
correctly. This supports retaining LiteLLM as a transport dependency while
keeping semantic capability and assurance decisions in Friday.

## Current Configuration Limitation

The current model catalog defines one Qwen3.8 profile with reasoning enabled
and one sampling bundle:

- [models-config.example.yaml](../../../../packages/friday-chat/models-config.example.yaml)

Consumers can override `reasoning.mode`, but a partial override may retain
sampling settings from the original profile. The current Qwen3.8 example uses
`temperature=0.2`, `top_p=0.95`, and `top_k=40`, which do not match Qwen's
published thinking or non-thinking recommendation as a complete set.

This is recorded as a future profile-semantics question, not authorization to
change the current catalog. Friday must not promote model-card recommendations
to universal framework defaults.

## Current Operational Meaning

Until this feature is revisited:

- `reasoning.mode=disabled` expresses operator intent.
- For the tested LM Studio/Qwen3.8 OpenAI-compatible route, Friday can prove
  that the disabling field was emitted but cannot claim that reasoning was
  disabled.
- Operators requiring guaranteed zero reasoning tokens must not rely on the
  current switch for this target.
- `provider_default`, `disabled`, and low or minimal effort remain distinct
  states and must not be silently substituted for one another.
- Passing functional live tests does not raise the reasoning assurance level
  when the behavioral comparison contradicts the requested mode.
- The current release may describe the limitation, but it must not advertise
  behaviorally verified Qwen3.8 reasoning disablement through this route.

## Explicitly Deferred Work

The following work is intentionally postponed:

- Any change to Friday's normalized reasoning API.
- Any LM Studio-native transport implementation.
- Any new Qwen, LM Studio, LiteLLM, vLLM, SGLang, Gemini, Anthropic, OpenAI, or
  other provider/model reasoning adapter.
- Any revision of the capability-composition or assurance contracts.
- Any automatic mode-dependent sampling-profile selection.
- Any prompt-template mutation, model preset, `/no_think` injection, proxy, or
  server-wide workaround.
- Any new runtime probe or behavioral-discovery subsystem.
- Any change to the current Friday package version or release artifacts for
  this deferred feature.
- Any downstream Friday package or ART migration motivated solely by this
  finding.

## Conditions For Revisit

A future planning pass may be opened when a maintainer explicitly authorizes
this feature upgrade and at least one concrete operational need requires
behaviorally reliable reasoning control. At that time, evidence should be
refreshed because model cards, LiteLLM translation, LM Studio behavior, prompt
templates, and provider APIs are version-sensitive.

The future investigation should begin by recording, without presupposing a
design:

- exact model family, artifact revision, and quantization;
- provider, API dialect, serving engine, server version, and prompt-template
  identity;
- dependency versions and sanitized final-wire fields;
- whether the provider acknowledges the requested mode;
- observed reasoning-token usage and reasoning-event presence;
- time to first stream event, time to first visible text, and total latency;
- mode-specific sampling behavior and tool-call compatibility;
- behavior under both streaming and non-streaming requests; and
- the required failure or warning policy when effective disablement cannot be
  established.

Candidate mechanisms such as LM Studio's native `reasoning=off`, model-specific
template variables, or provider-specific request fields must be evaluated in
that future work. This document does not approve any of them.

## Closure Statement

The assertion is documented and supported by both live evidence and current
provider documentation. The immediate investigation is closed. No further
development or design for model-aware reasoning disablement is authorized under
the current upgrade.
