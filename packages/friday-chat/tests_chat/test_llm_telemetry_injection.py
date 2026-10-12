"""Construction roles, preserved aliases, and the real observer with fake sinks."""

from types import SimpleNamespace as NS
from unittest.mock import AsyncMock

import litellm
import pytest
import yaml
from friday_chat import adapters
from friday_chat.config import FridayChatConfig, load_friday_py_config
from friday_chat.reorganization.mutation import (
    build_explicit_maintenance_provider_registry,
)
from friday_chat.telemetry import ChatTelemetryObserver
from friday_telemetry import CompositeProvider, DebugTelemetryRecorder
from friday_telemetry.models.llm_events import RequestStart

SECRET = "PRIVATE_CHAT_CONTENT_SENTINEL"
ROLES = ("synthesizer", "classifier", "researcher", "judge")


def configured(tmp_path, mode):
    values = {
        "llm": {"model": "gpt-4", "max_retries": 0},
        "embedding": {"model": "text-embedding-3-small"},
        "lifecycle": {"enabled": False},
        "extraction": {"model": "gpt-4"},
        "maintenance": {"llm": {role: {"model": "gpt-4"} for role in ROLES},
                        "embedding": {"model": "text-embedding-3-small"}},
        "memory": {"passage_router": {"enabled": True}, "compaction": {"enabled": True}},
    }
    if mode == "typed":
        values["llm"].update(model="openai/qwen3.8", transport_target={
            "provider": "openai_compatible", "dialect": "openai_chat_completions",
            "serving_engine": "lm_studio"}, model_target={
                "model_id": "qwen3.8", "family": "qwen3_8", "revision": "exact"})
    if mode != "canonical":
        return FridayChatConfig.model_validate(values)
    library = {
        "schema": "friday.model-library/v1",
        "endpoints": {"local": {"api_base": "http://127.0.0.1:1234/v1",
                                "provider": "openai_compatible", "serving_engine": "lm_studio"}},
        "profiles": {
            "chat": {"kind": "chat", "endpoint": "local", "dialect": "openai_chat_completions",
                     "model": "openai/qwen3.8", "model_target": {
                         "model_id": "qwen3.8", "family": "qwen3_8", "revision": "exact"}},
            "embedding": {"kind": "embedding", "endpoint": "local", "dialect": "openai_embeddings",
                          "model": "openai/nomic-embed", "model_target": {
                              "model_id": "nomic-embed", "family": "nomic_embed", "revision": "exact"}},
        },
    }
    (tmp_path / "models.yaml").write_text(yaml.safe_dump(library))
    names = ["chat", *ROLES, "extraction", "passage_router", "compaction",
             "smart_file_summarizer", "smart_file_synthesizer"]
    values.update(model_library={"path": "./models.yaml"},
                  llm_pool={"default_service": "chat", "services": {n: {"profile": "chat"} for n in names}},
                  embedding_pool={"default_service": "memory", "services": {"memory": {"profile": "embedding"}}})
    values["maintenance"] = {"llm": {r: {"llm_service": r} for r in ROLES},
                             "embedding": {"embedding_service": "memory"}}
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(values))
    return load_friday_py_config(path, env={})


def fake_backend(**kwargs):
    return NS(**kwargs)


def assert_service(service, sink, role):
    assert service._telemetry_helper.safe.telemetry is sink
    assert service._telemetry_helper.safe.identity.service_role == role


@pytest.mark.parametrize("mode", ["legacy", "typed", "canonical"])
@pytest.mark.parametrize("enabled", [False, True])
def test_all_role_factories_preserve_model_selection_and_injection(tmp_path, monkeypatch, mode, enabled):
    config = configured(tmp_path, mode)
    sink = ChatTelemetryObserver(enabled=True, session_id=SECRET) if enabled else None
    # Store, extraction and compaction collaborators are inert; no readiness or persistence.
    for name in ["MemoryExtractor", "InSessionCompactor", "ContextBudgetMonitor", "PassageRouter"]:
        monkeypatch.setattr(adapters, name, fake_backend)
    primary = adapters.build_framework_chat_model(config, telemetry=sink).service
    embedding = adapters.build_framework_embedding_service(config, telemetry=sink).service
    assert_service(primary, sink, "primary")
    assert_service(embedding, sink, "embedding")
    assert primary.model == ("openai/qwen3.8" if mode != "legacy" else "gpt-4")
    assert embedding.model == ("openai/nomic-embed" if mode == "canonical" else "text-embedding-3-small")
    default = adapters._build_legacy_primary_llm_service(config, telemetry=sink)
    assert_service(default, sink, "maintenance_default")
    router = adapters._build_passage_router(config, telemetry=sink)
    assert_service(router.llm, sink, "passage_router")
    for role in ROLES:
        service = adapters._build_role_llm_service(config, role, "gpt-4", telemetry=sink)
        assert_service(service, sink, "maintenance_" + role)
    for role in ["summarizer", "synthesizer"]:
        service = adapters._build_smart_file_llm_service(config, role=role,
                    default_name="smart_file_" + role, telemetry=sink)
        assert_service(service, sink, "smart_file_" + role)
    extraction = adapters._build_extraction_llm_service(config, default, telemetry=sink)
    assert_service(extraction, sink, "extraction")
    memory = NS(controller=NS(graph=object()), collection_manager=object(), access_buffer=None)
    diagnostics = NS(framework_upgrade_gaps=[])
    maintenance = adapters.build_framework_maintenance_adapter(config, session_id=SECRET,
        memory=memory, embedding=NS(service=embedding), llm_models={r: "gpt-4" for r in ROLES},
        diagnostics=diagnostics, maintenance_layout=NS(), telemetry=sink)
    assert not diagnostics.framework_upgrade_gaps
    assert_service(maintenance.extractor.llm, sink, "extraction")
    if mode == "canonical":
        assert_service(maintenance.compactor.llm_client, sink, "compaction")
    else:
        assert maintenance.compactor.llm_client is maintenance.llm_services["researcher"]
        assert_service(maintenance.compactor.llm_client, sink, "maintenance_researcher")
    registry = build_explicit_maintenance_provider_registry(config, telemetry=sink)
    assert not registry.configuration_errors
    for role, provider in registry.llms.items():
        assert_service(provider.service, sink, "maintenance_" + role.value)
    assert_service(registry.embedding.service, sink, "maintenance_embedding")
    if sink is not None:
        assert sink.snapshot().events == ()


def test_extraction_default_alias_is_not_relabelled_and_unknown_role_is_closed(tmp_path):
    config = configured(tmp_path, "legacy")
    config.extraction.model = None
    sink = ChatTelemetryObserver(enabled=True, session_id=SECRET)
    default = adapters._build_legacy_primary_llm_service(config, telemetry=sink)
    assert adapters._build_extraction_llm_service(config, default, telemetry=sink) is default
    assert_service(default, sink, "maintenance_default")
    service = adapters._build_role_llm_service(config, SECRET, "gpt-4", telemetry=sink)
    assert_service(service, sink, "unspecified")


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["legacy", "typed", "canonical"])
async def test_real_chat_observer_and_composite_preserve_scalars_without_content(tmp_path, monkeypatch, mode):
    left, right = DebugTelemetryRecorder(), DebugTelemetryRecorder()
    sink = ChatTelemetryObserver(enabled=False, session_id=SECRET,
                                 provider=CompositeProvider([left, right]))
    service = adapters.build_framework_chat_model(configured(tmp_path, mode), telemetry=sink)
    raw = NS(choices=[NS(message=NS(content=SECRET, tool_calls=[], reasoning_content=SECRET),
                        finish_reason="stop")], usage=NS(prompt_tokens=3, completion_tokens=4, total_tokens=7))
    dispatch = AsyncMock(return_value=raw)
    monkeypatch.setattr(litellm, "acompletion", dispatch)
    result = await service.complete([{"role": "user", "content": SECRET}])
    assert result.content == SECRET and dispatch.await_count == 1
    assert [e.name for e in sink.snapshot().events] == ["llm.request_start", "llm.attempt_finish", "llm.request_finish"]
    assert [(e.name, e.data) for e in left.events] == [(e.name, e.data) for e in right.events]
    assert len(left.events) == 3
    end = dict(sink.snapshot().events[-1].attributes)
    assert isinstance(end["duration_ms"], float) and end["total_tokens"] == 7
    assert len(end["session_ref"]) == 16
    assert SECRET not in repr(sink.snapshot())
    # Legacy/foreign/malformed payloads never bypass the closed parser.
    payload = RequestStart(request_id="1" * 32, operation="chat", api="typed_completion",
                           service_role="primary", model_ref="2" * 32).model_dump(exclude={"name"})
    for fields in [{"content": SECRET}, {"session_ref": "0" * 16}, {"schema_version": True}]:
        sink.capture_event("llm.request_start", payload | fields)
    sink.capture_event("llm_completion_success", {"content": SECRET})
    assert len(left.events) == 3 and sink.snapshot().rejected_count == 4


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [False, True])
async def test_declared_snapshot_publisher_preserves_underlying_boolean(value):
    snapshot = object()
    publisher = NS(publish_mcp_snapshot=AsyncMock(return_value=value),
                   discard_mcp_snapshot=AsyncMock(return_value=value))
    adapter = adapters.FrameworkMemoryAdapter(controller=None, collection_manager=publisher,
                config=FridayChatConfig(), session_id=SECRET, episodic_store=None, graph_store=None)
    assert await adapter.publish_mcp_memory(snapshot) is value
    assert await adapter.discard_mcp_memory(snapshot) is value
    publisher.publish_mcp_snapshot.assert_awaited_once_with(snapshot)
    publisher.discard_mcp_snapshot.assert_awaited_once_with(snapshot)


@pytest.mark.parametrize("enabled,injected", [(False, False), (True, False), (False, True)])
def test_real_runtime_entry_passes_enabled_observer_and_retains_borrowed_sink(monkeypatch, enabled, injected):
    from friday_chat import runtime
    calls = []
    def factory(config, **kwargs):
        calls.append(kwargs["telemetry"])
        return NS(telemetry=None)
    monkeypatch.setattr(runtime, "_build_framework_runtime", factory)
    borrowed = DebugTelemetryRecorder() if injected else None
    config = FridayChatConfig.model_validate({"telemetry": {"enabled": enabled}})
    result = runtime.build_runtime(config, fake=False, session_id=SECRET, telemetry=borrowed)
    assert calls == [result.telemetry if enabled or injected else None]
    assert result.telemetry.snapshot().provider == ("injected" if injected else "debug" if enabled else "disabled")
    assert not borrowed or borrowed.event_names == ["chat.runtime_ready"]


@pytest.mark.parametrize("mode", ["legacy", "typed", "canonical"])
def test_smart_file_constructor_and_memory_router_forward_same_observer(tmp_path, monkeypatch, mode):
    config = configured(tmp_path, mode)
    observer = ChatTelemetryObserver(enabled=True, session_id=SECRET)
    class SmartFileReadTool:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
    monkeypatch.setattr(adapters.importlib, "import_module", lambda name: NS(SmartFileReadTool=SmartFileReadTool))
    tool = adapters._instantiate_tool({"module": "synthetic", "class": "SmartFileReadTool"},
                                      config, telemetry=observer)
    assert tool.kwargs["fallback_llm"] is tool.kwargs["summarizer_llm"]
    assert_service(tool.kwargs["summarizer_llm"], observer, "smart_file_summarizer")
    assert_service(tool.kwargs["synthesizer_llm"], observer, "smart_file_synthesizer")
    for name in ["CollectionManager", "SimpleVectorStore", "NullGraphStore", "InMemoryEpisodicStore", "MemoryController", "PassageRouter"]:
        monkeypatch.setattr(adapters, name, lambda **kwargs: NS(**kwargs))
    layout = NS(vector_directory=tmp_path/"unused-vector", graph_path=tmp_path/"unused-graph")
    memory = adapters.build_framework_memory_adapter(config, NS(), session_id=SECRET,
                maintenance_layout=layout, telemetry=observer)
    assert_service(memory.passage_router.llm, observer, "passage_router")
    assert not layout.vector_directory.exists() and not layout.graph_path.exists()
    assert observer.snapshot().events == ()
