"""Pure capability preflight and LiteLLM call-spec translation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.metadata import version
from typing import Any, Protocol

from friday_llm.capabilities import (
    CapabilityState,
    ControlCapability,
    OperatorCapabilityDeclaration,
    ProviderCapabilities,
    compose_capabilities,
)
from friday_llm.exceptions import (
    ProviderOptionsError,
    TranslationConflictError,
    UnsupportedControlError,
)
from friday_llm.generation import GenerationConfig, ReasoningMode, SamplingConfig
from friday_llm.provider_options import LMStudioQwenOptions, ProviderOptions
from friday_llm.targets import ExecutionTarget


@dataclass(frozen=True, slots=True)
class TranslationSummary:
    """Safe, bounded metadata for a translated request."""

    requested_fields: tuple[str, ...]
    emitted_fields: tuple[str, ...]
    capability_sources: tuple[str, ...]
    target_profile: tuple[str, ...] = ()
    litellm_version: str = ""


@dataclass(frozen=True, slots=True)
class GenerationTranslation:
    """Provider kwargs produced by pure translation."""

    kwargs: dict[str, Any]
    summary: TranslationSummary


@dataclass(frozen=True, slots=True)
class _ToolSelectionTranslation:
    """Provider-specific tool selection with normalized semantics preserved."""

    tools: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None
    tool_choice: str | dict[str, Any] | None
    requested_fields: tuple[str, ...] = ()
    emitted_fields: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class LiteLLMCallSpec:
    """Frozen canonical per-request call specification reused by every retry."""

    model: str
    messages_json: str
    tools_json: str | None
    tool_choice_json: str | None
    generation_kwargs_json: str
    api_key: str | None
    api_base: str | None
    metadata_json: str | None
    summary: TranslationSummary

    @classmethod
    def from_parts(
        cls,
        *,
        model: str,
        messages: list[dict[str, Any]] | tuple[dict[str, Any], ...],
        tools: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
        tool_choice: str | dict[str, Any] | None,
        generation_kwargs: dict[str, Any],
        api_key: str | None,
        api_base: str | None,
        metadata: dict[str, Any] | None,
        summary: TranslationSummary,
    ) -> LiteLLMCallSpec:
        """Detach mutable input into bounded, canonical JSON snapshots."""

        return cls(
            model=model,
            messages_json=_canonical_json(list(messages)),
            tools_json=_canonical_json(list(tools)) if tools else None,
            tool_choice_json=(
                _canonical_json(tool_choice) if tool_choice is not None else None
            ),
            generation_kwargs_json=_canonical_json(generation_kwargs),
            api_key=api_key,
            api_base=api_base,
            metadata_json=_canonical_json(metadata) if metadata else None,
            summary=summary,
        )

    def to_kwargs(self, *, stream: bool = False) -> dict[str, Any]:
        """Materialize a detached LiteLLM kwargs mapping."""

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": json.loads(self.messages_json),
            **json.loads(self.generation_kwargs_json),
        }
        if self.tools_json is not None:
            kwargs["tools"] = json.loads(self.tools_json)
            kwargs["tool_choice"] = (
                json.loads(self.tool_choice_json)
                if self.tool_choice_json is not None
                else "auto"
            )
        elif self.tool_choice_json is not None:
            kwargs["tool_choice"] = json.loads(self.tool_choice_json)
        if self.api_key:
            kwargs["api_key"] = self.api_key
        if self.api_base:
            kwargs["api_base"] = self.api_base
        if self.metadata_json is not None:
            kwargs["metadata"] = json.loads(self.metadata_json)
        if stream:
            kwargs["stream"] = True
            kwargs["stream_options"] = {"include_usage": True}
        return kwargs


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


_MAX_PROVIDER_KEYS = 32
_MAX_PROVIDER_DEPTH = 4
_MAX_PROVIDER_STRING = 128
_MAX_PROVIDER_BYTES = 4096
_LITELLM_VERSION = version("litellm")


class GenerationAdapter(Protocol):
    """Private adapter contract for target-specific wire translation."""

    def translate(
        self,
        target: ExecutionTarget | None,
        config: GenerationConfig,
        capabilities: ProviderCapabilities,
        provider_options: ProviderOptions | None,
    ) -> GenerationTranslation:
        """Translate normalized intent into provider kwargs."""
        ...


class _LMStudioQwenAdapter:
    def translate(
        self,
        target: ExecutionTarget | None,
        config: GenerationConfig,
        capabilities: ProviderCapabilities,
        provider_options: ProviderOptions | None,
    ) -> GenerationTranslation:
        return _translate_fields(target, config, capabilities, provider_options)


class _StrictUnknownAdapter:
    def translate(
        self,
        target: ExecutionTarget | None,
        config: GenerationConfig,
        capabilities: ProviderCapabilities,
        provider_options: ProviderOptions | None,
    ) -> GenerationTranslation:
        return _translate_fields(target, config, capabilities, provider_options)


def translate_generation(
    target: ExecutionTarget | None,
    config: GenerationConfig,
    provider_options: ProviderOptions | None = None,
    operator_declaration: OperatorCapabilityDeclaration | None = None,
) -> GenerationTranslation:
    """Validate and translate normalized generation intent without I/O."""

    capabilities = (
        compose_capabilities(target, operator_declaration)
        if target is not None
        else ProviderCapabilities(controls=(), record_versions=())
    )
    adapter: GenerationAdapter
    if (
        target is not None
        and _is_lm_studio_openai_chat(target)
        and target.model.family == "qwen3_8"
    ):
        adapter = _LMStudioQwenAdapter()
    else:
        adapter = _StrictUnknownAdapter()
    return adapter.translate(target, config, capabilities, provider_options)


def _translate_tool_selection(
    target: ExecutionTarget | None,
    tools: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
    tool_choice: str | dict[str, Any] | None,
) -> _ToolSelectionTranslation:
    """Translate named OpenAI tool choice for LM Studio's bounded dialect."""

    if not _is_lm_studio_openai_chat(target) or not isinstance(tool_choice, dict):
        return _ToolSelectionTranslation(tools=tools, tool_choice=tool_choice)

    function = tool_choice.get("function")
    name = function.get("name") if isinstance(function, dict) else None
    if tool_choice.get("type") != "function" or not isinstance(name, str):
        raise TranslationConflictError("invalid named function tool choice")
    if not tools:
        raise TranslationConflictError(
            f"named tool choice {name!r} requires a matching tool definition"
        )

    matches: list[dict[str, Any]] = []
    for tool in tools:
        tool_function = tool.get("function")
        if (
            tool.get("type") == "function"
            and isinstance(tool_function, dict)
            and tool_function.get("name") == name
        ):
            matches.append(tool)
    if len(matches) != 1:
        raise TranslationConflictError(
            f"named tool choice {name!r} matched {len(matches)} tool definitions"
        )

    # LM Studio 0.4.x rejects OpenAI's object-form named choice. Restricting the
    # exposed schema to the selected function and emitting `required` preserves
    # the normalized exact-function intent without leaking this dialect quirk.
    return _ToolSelectionTranslation(
        tools=tuple(matches),
        tool_choice="required",
        requested_fields=("tool_choice.function.name",),
        emitted_fields=("tools", "tool_choice.required"),
    )


def _is_lm_studio_openai_chat(target: ExecutionTarget | None) -> bool:
    return bool(
        target is not None
        and target.transport.dialect == "openai_chat_completions"
        and target.transport.serving_engine == "lm_studio"
    )


def translate_with_adapter(
    target: ExecutionTarget,
    config: GenerationConfig,
    adapter: GenerationAdapter,
    provider_options: ProviderOptions | None = None,
) -> GenerationTranslation:
    """Exercise a registered or synthetic adapter against composed capabilities."""

    return adapter.translate(
        target,
        config,
        compose_capabilities(target),
        provider_options,
    )


def _translate_fields(
    target: ExecutionTarget | None,
    config: GenerationConfig,
    capabilities: ProviderCapabilities,
    provider_options: ProviderOptions | None,
) -> GenerationTranslation:
    kwargs: dict[str, Any] = {}
    requested: list[str] = []
    emitted: list[str] = []
    extra_body: dict[str, Any] = {}
    chat_template: dict[str, Any] = {}

    reasoning = config.reasoning
    if reasoning is not None and reasoning.mode is not ReasoningMode.AUTO:
        _require(capabilities, "reasoning.mode")
        requested.append("reasoning.mode")
        chat_template["enable_thinking"] = reasoning.mode is ReasoningMode.ENABLED
        emitted.append("chat_template_kwargs.enable_thinking")
    if reasoning is not None and reasoning.effort is not None:
        capability = _require(capabilities, "reasoning.effort")
        _validate_allowed("reasoning.effort", reasoning.effort, capability)
        requested.append("reasoning.effort")
        chat_template["reasoning_effort"] = reasoning.effort
        emitted.append("chat_template_kwargs.reasoning_effort")
    if reasoning is not None and reasoning.budget_tokens is not None:
        _require(capabilities, "reasoning.budget_tokens")
        requested.append("reasoning.budget_tokens")
    if reasoning is not None and reasoning.preserve is not None:
        _require(capabilities, "reasoning.preserve")
        requested.append("reasoning.preserve")
        chat_template["preserve_thinking"] = reasoning.preserve
        emitted.append("chat_template_kwargs.preserve_thinking")

    if config.sampling is not None:
        _translate_sampling(
            config.sampling,
            capabilities,
            kwargs,
            extra_body,
            requested,
            emitted,
        )
    if config.max_tokens is not None:
        _require(capabilities, "max_tokens")
        requested.append("max_tokens")
        kwargs["max_tokens"] = config.max_tokens
        emitted.append("max_tokens")

    if provider_options is not None:
        _apply_provider_options(
            target,
            provider_options,
            capabilities,
            chat_template,
            requested,
            emitted,
        )

    if chat_template:
        extra_body["chat_template_kwargs"] = chat_template
    if extra_body:
        _validate_translator_owned_json(extra_body)
        kwargs["extra_body"] = extra_body

    return GenerationTranslation(
        kwargs=kwargs,
        summary=TranslationSummary(
            requested_fields=tuple(sorted(set(requested))),
            emitted_fields=tuple(sorted(set(emitted))),
            capability_sources=capabilities.record_versions,
            target_profile=_target_profile(target),
            litellm_version=_LITELLM_VERSION,
        ),
    )


def _target_profile(target: ExecutionTarget | None) -> tuple[str, ...]:
    if target is None:
        return ()
    values = [
        f"provider:{target.transport.provider}",
        f"dialect:{target.transport.dialect}",
        f"family:{target.model.family}",
        f"revision:{target.model.revision}",
    ]
    if target.transport.serving_engine is not None:
        values.append(f"engine:{target.transport.serving_engine}")
    return tuple(values)


def _validate_translator_owned_json(value: dict[str, Any]) -> None:
    key_count = 0

    def walk(item: object, depth: int) -> None:
        nonlocal key_count
        if depth > _MAX_PROVIDER_DEPTH:
            raise TranslationConflictError("translator JSON exceeds maximum depth")
        if isinstance(item, dict):
            key_count += len(item)
            if key_count > _MAX_PROVIDER_KEYS:
                raise TranslationConflictError("translator JSON exceeds maximum keys")
            for key, nested in item.items():
                if len(str(key)) > _MAX_PROVIDER_STRING:
                    raise TranslationConflictError(
                        "translator JSON contains an oversized key"
                    )
                walk(nested, depth + 1)
        elif isinstance(item, (list, tuple)):
            for nested in item:
                walk(nested, depth + 1)
        elif isinstance(item, str) and len(item) > _MAX_PROVIDER_STRING:
            raise TranslationConflictError(
                "translator JSON contains an oversized string"
            )

    walk(value, 1)
    if len(_canonical_json(value).encode("utf-8")) > _MAX_PROVIDER_BYTES:
        raise TranslationConflictError("translator JSON exceeds maximum bytes")


def _translate_sampling(
    sampling: SamplingConfig,
    capabilities: ProviderCapabilities,
    kwargs: dict[str, Any],
    extra_body: dict[str, Any],
    requested: list[str],
    emitted: list[str],
) -> None:
    common = {
        "temperature": sampling.temperature,
        "top_p": sampling.top_p,
        "presence_penalty": sampling.presence_penalty,
        "frequency_penalty": sampling.frequency_penalty,
    }
    for field, value in common.items():
        if value is None:
            continue
        control = f"sampling.{field}"
        capability = _require(capabilities, control)
        _validate_range(control, float(value), capability)
        requested.append(control)
        kwargs[field] = value
        emitted.append(field)

    provider_fields = {
        "top_k": (sampling.top_k, "top_k"),
        "min_p": (sampling.min_p, "min_p"),
        "repetition_penalty": (sampling.repetition_penalty, "repeat_penalty"),
    }
    for normalized, (value, wire_name) in provider_fields.items():
        if value is None:
            continue
        control = f"sampling.{normalized}"
        capability = _require(capabilities, control)
        _validate_range(control, float(value), capability)
        requested.append(control)
        extra_body[wire_name] = value
        emitted.append(wire_name)


def _apply_provider_options(
    target: ExecutionTarget | None,
    options: ProviderOptions,
    capabilities: ProviderCapabilities,
    chat_template: dict[str, Any],
    requested: list[str],
    emitted: list[str],
) -> None:
    if not isinstance(options, LMStudioQwenOptions):
        raise ProviderOptionsError("unregistered provider options type")
    if (
        target is None
        or target.transport.serving_engine != "lm_studio"
        or target.model.family != "qwen3_8"
    ):
        raise ProviderOptionsError(
            "lm_studio.qwen3_8 options require the matching explicit target"
        )
    fields = {
        "enable_thinking": ("reasoning.mode", options.enable_thinking),
        "reasoning_effort": ("reasoning.effort", options.reasoning_effort),
        "preserve_thinking": ("reasoning.preserve", options.preserve_thinking),
    }
    for wire_name, (control, value) in fields.items():
        if value is None:
            continue
        capability = _require(capabilities, control)
        if isinstance(value, str):
            _validate_allowed(control, value, capability)
        existing = chat_template.get(wire_name)
        if existing is not None and existing != value:
            raise TranslationConflictError(
                f"provider option {wire_name!r} conflicts with normalized intent"
            )
        chat_template[wire_name] = value
        requested.append(f"provider_options.{wire_name}")
        emitted.append(f"chat_template_kwargs.{wire_name}")


def _require(
    capabilities: ProviderCapabilities,
    control: str,
) -> ControlCapability:
    capability = capabilities.for_control(control)
    if capability.state is not CapabilityState.SUPPORTED:
        raise UnsupportedControlError(
            control,
            capability.state.value,
            capability.sources,
        )
    return capability


def _validate_allowed(
    control: str,
    value: str,
    capability: ControlCapability,
) -> None:
    if capability.allowed_values and value not in capability.allowed_values:
        raise UnsupportedControlError(control, f"unsupported value {value!r}")


def _validate_range(
    control: str,
    value: float,
    capability: ControlCapability,
) -> None:
    if capability.minimum is not None and value < capability.minimum:
        raise UnsupportedControlError(control, f"below minimum {capability.minimum}")
    if capability.maximum is not None and value > capability.maximum:
        raise UnsupportedControlError(control, f"above maximum {capability.maximum}")
