"""Model-library contract and resolution tests."""

from __future__ import annotations

from collections.abc import Mapping

import pytest
from friday_llm import (
    ChatServiceBinding,
    CredentialResolutionError,
    EmbeddingServiceBinding,
    GenerationOverrides,
    LiteLLMEmbeddingService,
    LiteLLMService,
    ModelLibrary,
    ModelLibraryError,
    ReasoningConfig,
    ReasoningMode,
    ResilienceOverrides,
    SamplingConfig,
    UnsupportedControlError,
    resolve_chat_service,
    resolve_embedding_service,
)
from pydantic import ValidationError


def _catalog() -> ModelLibrary:
    return ModelLibrary.model_validate(
        {
            "schema": "friday.model-library/v1",
            "credentials": {
                "local_key": {"env": "FRIDAY_TEST_LLM_KEY"},
                "unused_key": {"env": "FRIDAY_UNUSED_LLM_KEY"},
            },
            "endpoints": {
                "local_lmstudio": {
                    "api_base": "http://127.0.0.1:1234/v1",
                    "provider": "openai_compatible",
                    "serving_engine": "lm_studio",
                    "default_credential": "local_key",
                    "resilience": {
                        "max_retries": 2,
                        "timeout_seconds": 90,
                    },
                }
            },
            "profiles": {
                "qwen_chat": {
                    "kind": "chat",
                    "endpoint": "local_lmstudio",
                    "dialect": "openai_chat_completions",
                    "model": "openai/qwen3.8-27b-mlx",
                    "model_target": {
                        "model_id": "qwen3.8-27b-mlx",
                        "family": "qwen3_8",
                        "revision": "test-revision",
                    },
                    "generation": {
                        "reasoning": {"mode": "enabled", "effort": "medium"},
                        "sampling": {
                            "temperature": 0.2,
                            "top_p": 0.95,
                            "top_k": 40,
                        },
                        "max_tokens": 8000,
                    },
                },
                "nomic_embedding": {
                    "kind": "embedding",
                    "endpoint": "local_lmstudio",
                    "dialect": "openai_embeddings",
                    "model": "openai/nomic-embed-text-v1.5",
                    "model_target": {
                        "model_id": "nomic-embed-text-v1.5",
                        "family": "nomic_embed",
                        "revision": "test-revision",
                    },
                },
            },
        }
    )


def test_catalog_rejects_invalid_names_and_references() -> None:
    with pytest.raises(ValidationError, match="catalog name"):
        ModelLibrary.model_validate(
            {
                "schema": "friday.model-library/v1",
                "credentials": {"Bad Name": {"env": "VALID_ENV"}},
            }
        )

    with pytest.raises(ValidationError, match="missing credential"):
        ModelLibrary.model_validate(
            {
                "schema": "friday.model-library/v1",
                "endpoints": {
                    "local": {
                        "api_base": "http://127.0.0.1:1234/v1",
                        "provider": "openai_compatible",
                        "default_credential": "missing",
                    }
                },
            }
        )


@pytest.mark.parametrize(
    "api_base",
    (
        "ftp://127.0.0.1/model",
        "https://user:secret@example.test/v1",
        "https://example.test/v1?key=secret",
        "https://example.test/v1#secret",
    ),
)
def test_endpoint_rejects_unsafe_urls(api_base: str) -> None:
    with pytest.raises(ValidationError, match="api_base"):
        ModelLibrary.model_validate(
            {
                "schema": "friday.model-library/v1",
                "endpoints": {
                    "unsafe": {
                        "api_base": api_base,
                        "provider": "openai_compatible",
                    }
                },
            }
        )


def test_chat_resolution_merges_explicit_overrides_and_redacts_secret() -> None:
    secret = "secret-that-must-never-be-rendered"
    binding = ChatServiceBinding(
        profile="qwen_chat",
        resilience_overrides=ResilienceOverrides(timeout_seconds=300),
        generation_overrides=GenerationOverrides(
            reasoning=ReasoningConfig(mode=ReasoningMode.DISABLED),
            sampling=SamplingConfig(temperature=0.0),
            max_tokens=1024,
        ),
    )

    spec = resolve_chat_service(
        _catalog(),
        binding,
        {"FRIDAY_TEST_LLM_KEY": secret},
    )

    assert spec.generation_defaults.reasoning is not None
    assert spec.generation_defaults.reasoning.mode is ReasoningMode.DISABLED
    assert spec.generation_defaults.sampling is not None
    assert spec.generation_defaults.sampling.temperature == 0.0
    assert spec.generation_defaults.sampling.top_p == 0.95
    assert spec.generation_defaults.max_tokens == 1024
    assert spec.resilience.max_retries == 2
    assert spec.resilience.timeout_seconds == 300
    assert spec.api_key is not None
    assert spec.api_key.get_secret_value() == secret
    assert secret not in repr(spec)
    assert secret not in spec.model_dump_json()

    service = LiteLLMService.from_spec(spec)
    assert service.api_key == secret
    assert service.execution_target == spec.execution_target


def test_embedding_resolution_and_factory_preserve_target_identity() -> None:
    spec = resolve_embedding_service(
        _catalog(),
        EmbeddingServiceBinding(
            profile="nomic_embedding",
            resilience_overrides=ResilienceOverrides(timeout_seconds=60),
        ),
        {"FRIDAY_TEST_LLM_KEY": "local-secret"},
    )

    service = LiteLLMEmbeddingService.from_spec(spec)

    assert spec.resilience.max_retries == 2
    assert spec.resilience.timeout_seconds == 60
    assert service.execution_target == spec.execution_target
    assert service.model == "openai/nomic-embed-text-v1.5"


def test_resolved_service_spec_is_deeply_immutable() -> None:
    spec = resolve_chat_service(
        _catalog(),
        ChatServiceBinding(profile="qwen_chat"),
        {"FRIDAY_TEST_LLM_KEY": "local-secret"},
    )

    with pytest.raises(ValidationError, match="frozen"):
        spec.resilience.timeout_seconds = 1
    with pytest.raises(ValidationError, match="frozen"):
        spec.resilience.circuit_breaker.enabled = True


def test_unused_credentials_do_not_need_environment_values() -> None:
    spec = resolve_chat_service(
        _catalog(),
        ChatServiceBinding(profile="qwen_chat"),
        {"FRIDAY_TEST_LLM_KEY": "present"},
    )
    assert spec.api_key is not None


@pytest.mark.parametrize("environment", ({}, {"FRIDAY_TEST_LLM_KEY": ""}))
def test_selected_missing_or_empty_credential_is_bounded(
    environment: Mapping[str, str],
) -> None:
    with pytest.raises(CredentialResolutionError) as caught:
        resolve_chat_service(
            _catalog(),
            ChatServiceBinding(profile="qwen_chat"),
            environment,
        )
    assert "FRIDAY_TEST_LLM_KEY" in str(caught.value)
    assert "secret" not in str(caught.value).lower()


def test_binding_kind_mismatch_fails_without_credential_lookup() -> None:
    with pytest.raises(ModelLibraryError, match="not a chat profile"):
        resolve_chat_service(
            _catalog(),
            ChatServiceBinding(profile="nomic_embedding"),
            {},
        )


def test_capability_preflight_precedes_credential_lookup() -> None:
    raw = _catalog().model_dump(mode="python")
    raw["profiles"]["qwen_chat"]["generation"]["reasoning"] = {
        "mode": "enabled",
        "budget_tokens": 100,
    }
    catalog = ModelLibrary.model_validate(raw)

    with pytest.raises(UnsupportedControlError):
        resolve_chat_service(
            catalog,
            ChatServiceBinding(profile="qwen_chat"),
            {},
        )


def test_profile_route_and_target_identity_must_agree() -> None:
    raw = _catalog().model_dump(mode="python")
    raw["profiles"]["qwen_chat"]["model_target"]["model_id"] = "other-model"
    catalog = ModelLibrary.model_validate(raw)

    with pytest.raises(ModelLibraryError, match="routing identity"):
        resolve_chat_service(
            catalog,
            ChatServiceBinding(profile="qwen_chat"),
            {"FRIDAY_TEST_LLM_KEY": "present"},
        )
