"""Verification failures retain safe evidence through provider and rollback."""

import json
import traceback
from types import MappingProxyType
from unittest.mock import AsyncMock

import pytest
from friday_chat.commands.registry import _format_reorganization_result
from friday_chat.reorganization import mutation as m
from friday_chat.reorganization.contracts import (
    MutationStepStatus,
    OperationTrigger,
    ReorganizationMode,
    ReorganizationRequest,
    ResultStatus,
)
from friday_llm import CompletionAssurance, LiteLLMService, TypedChatCompletionResponse


def provider(role, payload, *, finish_reason="stop"):
    client = AsyncMock(spec=LiteLLMService)
    client.chat_completion_request.return_value = TypedChatCompletionResponse(
        content=payload,
        reasoning_content="private-reasoning",
        model="provider-reported-fixture",
        finish_reason=finish_reason,
        assurance=CompletionAssurance(),
    )
    return m.LiteLlmMaintenanceProvider(
        role=role,
        service=client,
        config=m.MaintenanceProviderConfig(model="openrouter/diagnostic-fixture"),
    ), client


@pytest.mark.asyncio
@pytest.mark.parametrize("role", list(m.MaintenanceLlmRole))
async def test_verification_schema_error_identifies_role_model_and_safe_fields(role):
    secret = "private-provider-content-and-credential"
    p, client = provider(
        role,
        json.dumps(
            {
                "decisions": [
                    {
                        "collection": "primary",
                        "memory_id": "a",
                        "status": "verified",
                        "confidence": secret,
                    }
                ],
                secret: secret,
            }
        ),
    )
    with pytest.raises(m.MaintenanceResponseValidationError) as caught:
        await p.complete_model(
            m.VerificationResponse, system_prompt="Fixture", user_payload="{}"
        )
    error = caught.value
    assert error.diagnostic.role == role.value
    assert error.diagnostic.configured_model == "openrouter/diagnostic-fixture"
    assert error.diagnostic.schema == "VerificationResponse"
    assert error.diagnostic.finish_reason == "stop"
    assert "decisions.0.confidence:float_type" in str(error)
    assert "<field>:extra_forbidden" in str(error)
    assert secret not in str(error)
    assert secret not in "".join(traceback.format_exception(error))
    assert "private-reasoning" not in str(error)
    assert client.chat_completion_request.await_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("finish_reason", ["length", "max_tokens", "model_length"])
@pytest.mark.parametrize(
    "text", ['{"decisions":[]}', '{"decisions":[{"status":"verified"}']
)
async def test_length_termination_is_incomplete_even_with_a_complete_object(
    finish_reason, text
):
    p, client = provider(m.MaintenanceLlmRole.JUDGE, text, finish_reason=finish_reason)
    with pytest.raises(m.MaintenanceResponseIncompleteError) as caught:
        await p.complete_model(
            m.VerificationResponse, system_prompt="Fixture", user_payload="{}"
        )
    assert caught.value.diagnostic.finish_reason == finish_reason
    assert caught.value.diagnostic.role == "judge"
    assert caught.value.diagnostic.issues == ()
    assert client.chat_completion_request.await_count == 1


@pytest.mark.asyncio
async def test_234_record_control_and_truncated_reply_have_distinct_results():
    payload = json.dumps(
        {
            "decisions": [
                {
                    "collection": "fixture",
                    "memory_id": f"record-{i}",
                    "status": "verified",
                    "confidence": 0.9,
                }
                for i in range(234)
            ]
        }
    )
    p, _ = provider(m.MaintenanceLlmRole.CLASSIFIER, payload)
    response = await p.complete_model(
        m.VerificationResponse, system_prompt="Fixture", user_payload="{}"
    )
    assert len(response.decisions) == 234
    p, client = provider(
        m.MaintenanceLlmRole.CLASSIFIER,
        payload[: len(payload) // 2],
        finish_reason=None,
    )
    with pytest.raises(m.MaintenanceResponseParseError) as caught:
        await p.complete_model(
            m.VerificationResponse, system_prompt="Fixture", user_payload="{}"
        )
    assert type(caught.value) is m.MaintenanceResponseParseError
    assert caught.value.diagnostic.finish_reason == "unavailable"
    assert caught.value.diagnostic.issues == ()
    assert client.chat_completion_request.await_count == 1


@pytest.mark.asyncio
async def test_unknown_finish_metadata_is_redacted():
    p, _ = provider(
        m.MaintenanceLlmRole.JUDGE, "{}", finish_reason="private-finish-details"
    )
    with pytest.raises(m.MaintenanceResponseValidationError) as caught:
        await p.complete_model(
            m.VerificationResponse, system_prompt="Fixture", user_payload="{}"
        )
    assert caught.value.diagnostic.finish_reason == "other"
    assert "private-finish-details" not in str(caught.value)


def failing_adapter(payload, *, finish_reason="stop", role=m.MaintenanceLlmRole.JUDGE):
    from test_reorganization_mutation import _adapter

    adapter, providers, _embedding, memory, _lifecycle = _adapter()
    failing, client = provider(role, payload, finish_reason=finish_reason)
    replacements = dict(providers)
    replacements[role] = failing
    adapter.providers = m.ExplicitMaintenanceProviderRegistry(
        llms=MappingProxyType(replacements), embedding=adapter.providers.embedding
    )
    adapter._pipeline.providers = adapter.providers
    return adapter, memory, client


async def observed_failure(adapter, request):
    from friday_chat.reorganization.coordinator import present_stage_result
    from friday_memory.maintenance.pipeline import ShieldedMemoryMaintenanceBoundary
    from test_maintenance_order import CaptureObserver

    observer = CaptureObserver()
    with pytest.raises(m.MaintenanceResponseError):
        await adapter.execute_pipeline(
            adapter.memory_request(request),
            run_id="1" * 32,
            observer=observer,
            boundary=ShieldedMemoryMaintenanceBoundary(),
        )
    return present_stage_result(observer.results[-1])


@pytest.mark.asyncio
async def test_step_errors_keep_safe_diagnostics_without_applying_a_partial_plan():
    adapter, memory, client = failing_adapter(
        '{"decisions":[{"confidence":"private-value"}]}'
    )
    request = ReorganizationRequest(
        trigger=OperationTrigger.MANUAL, mode=ReorganizationMode.VERIFY, execute=True
    )
    result = await observed_failure(adapter, request)
    assert result.status is MutationStepStatus.FAILED
    assert "role=judge" in result.errors[0].message
    assert "model=openrouter/diagnostic-fixture" in result.errors[0].message
    assert "schema=VerificationResponse" in result.errors[0].message
    assert "finish_reason=stop" in result.errors[0].message
    assert "private-value" not in result.errors[0].message
    assert memory.commands == []
    assert client.chat_completion_request.await_count == 1


@pytest.mark.asyncio
async def test_preflight_diagnostics_are_safe_and_do_not_apply_changes():
    adapter, memory, client = failing_adapter(
        '{"ready":"private-value"}', role=m.MaintenanceLlmRole.SYNTHESIZER
    )
    request = ReorganizationRequest(
        trigger=OperationTrigger.MANUAL,
        mode=ReorganizationMode.SYNTHESIZE,
        execute=True,
    )
    result = await adapter.preflight(request)
    assert not result.supported
    assert "role=synthesizer" in result.errors[0].message
    assert "schema=ProviderProbeResponse" in result.errors[0].message
    assert "ready:bool_type" in result.errors[0].message
    assert "private-value" not in result.errors[0].message
    assert memory.commands == []
    assert client.chat_completion_request.await_count == 1


@pytest.mark.asyncio
async def test_typed_exception_without_diagnostic_does_not_leak_its_message(
    monkeypatch,
):
    adapter, memory, _ = failing_adapter("{}")
    failing = adapter.providers.llms[m.MaintenanceLlmRole.JUDGE]
    monkeypatch.setattr(
        failing,
        "complete_model",
        AsyncMock(
            side_effect=m.MaintenanceResponseValidationError("private-provider-content")
        ),
    )
    request = ReorganizationRequest(
        trigger=OperationTrigger.MANUAL, mode=ReorganizationMode.VERIFY, execute=True
    )
    result = await observed_failure(adapter, request)
    assert result.status is MutationStepStatus.FAILED
    assert "private-provider-content" not in result.errors[0].message
    assert memory.commands == []


@pytest.mark.asyncio
async def test_safe_diagnostic_survives_verified_rollback_journal_and_terminal(
    tmp_path, monkeypatch
):
    from pathlib import Path

    import chromadb
    from test_maintenance_order import real_coordinator

    fixture, real_adapter, providers = await real_coordinator(tmp_path)
    collection = chromadb.PersistentClient(
        path=str(fixture.layout.vector_directory)
    ).get_collection("coordinator-test")
    collection.update(
        ids=["memory-1"], metadatas=[{"type": "insight", "topic": "synthetic"}]
    )
    collection.add(
        ids=["memory-duplicate"],
        documents=["synthetic memory"],
        metadatas=[{"type": "insight", "topic": "synthetic"}],
        embeddings=[[1.0, 0.0]],
    )
    failing, client = provider(
        m.MaintenanceLlmRole.JUDGE, '{"decisions":[{"confidence":"private-value"}]}'
    )
    providers[m.MaintenanceLlmRole.JUDGE] = failing
    real_adapter._pipeline.providers = m.ExplicitMaintenanceProviderRegistry(
        llms=providers, embedding=None
    )
    request = ReorganizationRequest(
        trigger=OperationTrigger.MANUAL,
        mode=ReorganizationMode.FULL,
        execute=True,
        skip_synthesis=True,
        skip_lifecycle=True,
    )
    result = await fixture.coordinator.run(request)
    assert result.status is ResultStatus.FAILED_ROLLED_BACK
    assert await fixture.graph.get_node("mutation-node") is None
    assert await fixture.graph.get_node("baseline-node") is not None
    assert client.chat_completion_request.await_count == 1
    collection = chromadb.PersistentClient(
        path=str(fixture.layout.vector_directory)
    ).get_collection("coordinator-test")
    assert collection.count() == 2
    assert all(
        (metadata or {}).get("verification_status") is None
        for metadata in collection.get(include=["metadatas"])["metadatas"]
    )
    journal = Path(result.journal_path).read_text()
    terminal = _format_reorganization_result(result, dry_run=False)
    for text in [journal, terminal]:
        assert "role=judge" in text
        assert "model=openrouter/diagnostic-fixture" in text
        assert "schema=VerificationResponse" in text
        assert "finish_reason=stop" in text
        assert "MaintenanceResponseValidationError" in text
        assert "private-value" not in text
        assert "private-reasoning" not in text
