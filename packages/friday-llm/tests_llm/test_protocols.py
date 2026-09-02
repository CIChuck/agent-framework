"""Structural client-protocol conformance tests."""

from friday_core.interfaces.llm import LLMClient
from friday_llm import LiteLLMService, TypedLLMClient


def _accepts_legacy_client(client: LLMClient) -> LLMClient:
    return client


def test_litellm_service_satisfies_typed_client_protocol() -> None:
    service = LiteLLMService(model_name="gpt-4")
    assert isinstance(service, TypedLLMClient)
    assert _accepts_legacy_client(service) is service
