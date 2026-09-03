"""Typed, provider-independent model catalog and pure service resolution."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)

from friday_llm.config import CircuitBreakerConfig, ResilienceConfig
from friday_llm.exceptions import (
    CredentialResolutionError,
    ModelLibraryError,
)
from friday_llm.generation import (
    GenerationConfig,
    GenerationOverrides,
    resolve_generation,
)
from friday_llm.provider_options import ProviderOptions
from friday_llm.targets import ExecutionTarget, ModelTarget, TransportTarget
from friday_llm.translation import translate_generation

MODEL_LIBRARY_SCHEMA = "friday.model-library/v1"
MAX_CREDENTIALS = 128
MAX_ENDPOINTS = 128
MAX_PROFILES = 512

_CATALOG_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
_ENVIRONMENT_NAME = re.compile(r"^[A-Z_][A-Z0-9_]{0,127}$")


class _StrictModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class CredentialDefinition(_StrictModel):
    """Reference to a credential environment variable, never its value."""

    env: str = Field(min_length=1, max_length=128)

    @field_validator("env")
    @classmethod
    def validate_environment_name(cls, value: str) -> str:
        if _ENVIRONMENT_NAME.fullmatch(value) is None:
            raise ValueError("credential env must be a valid environment name")
        return value


class EndpointDefinition(_StrictModel):
    """Reusable connection identity shared by model profiles."""

    api_base: str = Field(min_length=1, max_length=2048)
    provider: str = Field(min_length=1, max_length=64)
    serving_engine: str | None = Field(default=None, min_length=1, max_length=64)
    default_credential: str | None = Field(default=None, min_length=1, max_length=64)
    resilience: ResilienceConfig | None = None

    @field_validator("api_base")
    @classmethod
    def validate_api_base(cls, value: str) -> str:
        if value != value.strip() or any(ord(character) < 32 for character in value):
            raise ValueError("api_base must not contain whitespace or controls")
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or parsed.hostname is None:
            raise ValueError("api_base must be an absolute HTTP(S) URL")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("api_base must not contain user information")
        if parsed.query or parsed.fragment:
            raise ValueError("api_base must not contain a query or fragment")
        try:
            port = parsed.port
        except ValueError as error:
            raise ValueError("api_base contains an invalid port") from error
        del port
        return value


class ChatModelProfile(_StrictModel):
    """Chat route, target identity, and provider-neutral defaults."""

    kind: Literal["chat"]
    endpoint: str = Field(min_length=1, max_length=64)
    dialect: str = Field(min_length=1, max_length=64)
    model: str = Field(min_length=1, max_length=256)
    model_target: ModelTarget
    generation: GenerationConfig | None = None
    provider_options: ProviderOptions | None = None

    @model_validator(mode="after")
    def require_complete_target(self) -> ChatModelProfile:
        _require_complete_model_target(self.model_target)
        return self


class EmbeddingOptions(_StrictModel):
    """Bounded options supported by Friday's embedding service."""

    batch_size: int = Field(default=100, ge=1, le=10_000)
    cache_size: int = Field(default=100, ge=0, le=100_000)


class EmbeddingModelProfile(_StrictModel):
    """Embedding route and target identity."""

    kind: Literal["embedding"]
    endpoint: str = Field(min_length=1, max_length=64)
    dialect: str = Field(min_length=1, max_length=64)
    model: str = Field(min_length=1, max_length=256)
    model_target: ModelTarget
    embedding_options: EmbeddingOptions | None = None

    @model_validator(mode="after")
    def require_complete_target(self) -> EmbeddingModelProfile:
        _require_complete_model_target(self.model_target)
        return self


ModelProfile = Annotated[
    ChatModelProfile | EmbeddingModelProfile,
    Field(discriminator="kind"),
]


class CircuitBreakerOverrides(_StrictModel):
    """Explicit per-service circuit-breaker overrides."""

    enabled: bool | None = None
    failure_threshold: int | None = Field(default=None, ge=1, le=50)
    recovery_timeout: float | None = Field(default=None, ge=1.0, le=300.0)
    half_open_max_calls: int | None = Field(default=None, ge=1, le=10)


class ResilienceOverrides(_StrictModel):
    """Explicit per-service resilience overrides."""

    max_retries: int | None = Field(default=None, ge=0, le=10)
    backoff_multiplier: float | None = Field(default=None, ge=0.1, le=10.0)
    backoff_min: float | None = Field(default=None, ge=0.1, le=60.0)
    backoff_max: float | None = Field(default=None, ge=1.0, le=120.0)
    timeout_seconds: float | None = Field(default=None, ge=1.0, le=600.0)
    stream_timeout_seconds: float | None = Field(default=None, ge=5.0, le=600.0)
    circuit_breaker: CircuitBreakerOverrides | None = None


class ChatServiceBinding(_StrictModel):
    """Named runtime role binding to one chat profile."""

    profile: str = Field(min_length=1, max_length=64)
    credential: str | None = Field(default=None, min_length=1, max_length=64)
    resilience_overrides: ResilienceOverrides | None = None
    generation_overrides: GenerationOverrides | None = None


class EmbeddingServiceBinding(_StrictModel):
    """Named runtime role binding to one embedding profile."""

    profile: str = Field(min_length=1, max_length=64)
    credential: str | None = Field(default=None, min_length=1, max_length=64)
    resilience_overrides: ResilienceOverrides | None = None


ServiceBinding = ChatServiceBinding | EmbeddingServiceBinding


class ModelLibrary(_StrictModel):
    """Versioned catalog of credentials, endpoints, and model profiles."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        serialize_by_alias=True,
        validate_by_name=True,
    )

    schema_version: Literal["friday.model-library/v1"] = Field(alias="schema")
    credentials: dict[str, CredentialDefinition] = Field(
        default_factory=dict,
        max_length=MAX_CREDENTIALS,
    )
    endpoints: dict[str, EndpointDefinition] = Field(
        default_factory=dict,
        max_length=MAX_ENDPOINTS,
    )
    profiles: dict[str, ModelProfile] = Field(
        default_factory=dict,
        max_length=MAX_PROFILES,
    )

    @field_validator("credentials", "endpoints", "profiles")
    @classmethod
    def validate_catalog_names(cls, value: dict[str, object]) -> dict[str, object]:
        invalid = sorted(name for name in value if _CATALOG_NAME.fullmatch(name) is None)
        if invalid:
            raise ValueError(f"invalid catalog name: {invalid[0]!r}")
        return value

    @model_validator(mode="after")
    def validate_references(self) -> ModelLibrary:
        for endpoint_name, endpoint in self.endpoints.items():
            credential = endpoint.default_credential
            if credential is not None and credential not in self.credentials:
                raise ValueError(
                    f"endpoint {endpoint_name!r} references missing credential "
                    f"{credential!r}"
                )
        for profile_name, profile in self.profiles.items():
            if profile.endpoint not in self.endpoints:
                raise ValueError(
                    f"profile {profile_name!r} references missing endpoint "
                    f"{profile.endpoint!r}"
                )
        return self


class LLMServiceSpec(_StrictModel):
    """Fully resolved, redacted construction contract for a chat service."""

    model: str
    api_base: str
    api_key: SecretStr | None = Field(default=None, repr=False)
    resilience: ResilienceConfig
    generation_defaults: GenerationConfig
    execution_target: ExecutionTarget
    provider_options_defaults: ProviderOptions | None = None


class EmbeddingServiceSpec(_StrictModel):
    """Fully resolved, redacted construction contract for an embedding service."""

    model: str
    api_base: str
    api_key: SecretStr | None = Field(default=None, repr=False)
    resilience: ResilienceConfig
    execution_target: ExecutionTarget
    batch_size: int = Field(default=100, ge=1, le=10_000)
    cache_size: int = Field(default=100, ge=0, le=100_000)


def resolve_chat_service(
    library: ModelLibrary,
    binding: ChatServiceBinding,
    environment: Mapping[str, str],
) -> LLMServiceSpec:
    """Resolve and preflight a chat binding without provider I/O."""

    profile = _profile(library, binding.profile)
    if not isinstance(profile, ChatModelProfile):
        raise ModelLibraryError(
            f"profile {binding.profile!r} is not a chat profile"
        )
    endpoint = library.endpoints[profile.endpoint]
    target = _execution_target(endpoint, profile.dialect, profile.model_target)
    _validate_route_identity(profile.model, target)
    generation = resolve_generation(profile.generation, binding.generation_overrides)
    translate_generation(target, generation, profile.provider_options)
    resilience = _resolve_resilience(
        endpoint.resilience,
        binding.resilience_overrides,
    )
    credential = _resolve_credential(
        library,
        binding.credential,
        endpoint.default_credential,
        environment,
    )
    return LLMServiceSpec(
        model=profile.model,
        api_base=endpoint.api_base,
        api_key=credential,
        resilience=resilience,
        generation_defaults=generation,
        execution_target=target,
        provider_options_defaults=profile.provider_options,
    )


def resolve_embedding_service(
    library: ModelLibrary,
    binding: EmbeddingServiceBinding,
    environment: Mapping[str, str],
) -> EmbeddingServiceSpec:
    """Resolve and preflight an embedding binding without provider I/O."""

    profile = _profile(library, binding.profile)
    if not isinstance(profile, EmbeddingModelProfile):
        raise ModelLibraryError(
            f"profile {binding.profile!r} is not an embedding profile"
        )
    endpoint = library.endpoints[profile.endpoint]
    target = _execution_target(endpoint, profile.dialect, profile.model_target)
    _validate_route_identity(profile.model, target)
    resilience = _resolve_resilience(
        endpoint.resilience,
        binding.resilience_overrides,
    )
    credential = _resolve_credential(
        library,
        binding.credential,
        endpoint.default_credential,
        environment,
    )
    options = profile.embedding_options or EmbeddingOptions()
    return EmbeddingServiceSpec(
        model=profile.model,
        api_base=endpoint.api_base,
        api_key=credential,
        resilience=resilience,
        execution_target=target,
        batch_size=options.batch_size,
        cache_size=options.cache_size,
    )


def _profile(library: ModelLibrary, name: str) -> ModelProfile:
    try:
        return library.profiles[name]
    except KeyError as error:
        raise ModelLibraryError(f"unknown model profile {name!r}") from error


def _execution_target(
    endpoint: EndpointDefinition,
    dialect: str,
    model_target: ModelTarget,
) -> ExecutionTarget:
    return ExecutionTarget(
        transport=TransportTarget(
            provider=endpoint.provider,
            dialect=dialect,
            serving_engine=endpoint.serving_engine,
        ),
        model=model_target,
    )


def _validate_route_identity(model: str, target: ExecutionTarget) -> None:
    model_id = target.model.model_id
    if model != model_id and not model.endswith(f"/{model_id}"):
        raise ModelLibraryError(
            "model routing identity contradicts model_target.model_id"
        )
    if (
        target.transport.provider == "openai_compatible"
        and target.transport.dialect in {
            "openai_chat_completions",
            "openai_embeddings",
        }
        and not model.startswith("openai/")
    ):
        raise ModelLibraryError(
            "OpenAI-compatible targets require LiteLLM's openai/ routing prefix"
        )


def _require_complete_model_target(target: ModelTarget) -> None:
    if target.family is None or target.revision is None:
        raise ValueError("model_target requires explicit family and revision")


def _resolve_resilience(
    defaults: ResilienceConfig | None,
    overrides: ResilienceOverrides | None,
) -> ResilienceConfig:
    baseline = defaults or ResilienceConfig()
    if overrides is None:
        return baseline.model_copy(deep=True)

    values = baseline.model_dump()
    for field_name in (
        "max_retries",
        "backoff_multiplier",
        "backoff_min",
        "backoff_max",
        "timeout_seconds",
        "stream_timeout_seconds",
    ):
        if field_name in overrides.model_fields_set:
            override = getattr(overrides, field_name)
            if override is not None:
                values[field_name] = override

    circuit_overrides = overrides.circuit_breaker
    if (
        "circuit_breaker" in overrides.model_fields_set
        and circuit_overrides is not None
    ):
        circuit_values = baseline.circuit_breaker.model_dump()
        for field_name in (
            "enabled",
            "failure_threshold",
            "recovery_timeout",
            "half_open_max_calls",
        ):
            if field_name in circuit_overrides.model_fields_set:
                override = getattr(circuit_overrides, field_name)
                if override is not None:
                    circuit_values[field_name] = override
        values["circuit_breaker"] = CircuitBreakerConfig.model_validate(
            circuit_values
        )
    return ResilienceConfig.model_validate(values)


def _resolve_credential(
    library: ModelLibrary,
    binding_credential: str | None,
    endpoint_credential: str | None,
    environment: Mapping[str, str],
) -> SecretStr | None:
    reference = binding_credential or endpoint_credential
    if reference is None:
        return None
    try:
        definition = library.credentials[reference]
    except KeyError as error:
        raise ModelLibraryError(
            f"service binding references unknown credential {reference!r}"
        ) from error
    value = environment.get(definition.env)
    if value is None or not value.strip():
        raise CredentialResolutionError(
            f"required credential environment variable {definition.env} "
            "is unset or empty"
        )
    return SecretStr(value)
