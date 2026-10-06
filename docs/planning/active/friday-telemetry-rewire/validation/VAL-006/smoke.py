import asyncio, importlib.util, json, sys, types, typing
from pathlib import Path
from pydantic import BaseModel, ValidationError
from friday_chat.config import FridayChatConfig
from friday_chat.app import FridayChatApp, ListInputSource
from friday_chat.runtime import build_runtime
from friday_chat.telemetry import ChatTelemetryObserver
from friday_telemetry import CompositeProvider, DebugTelemetryRecorder
from friday_chat.memory_views import MemoryMetric
from friday_cli.commands import CommandRegistry
from friday_cli.session import SessionContext, SessionManager
from friday_core.interfaces.tools import ToolAdapter
from friday_moltbook.responses import MoltbookResponse
from friday_memory.llm_completion import MemoryLLMClient
from friday_sandbox.serialization import validate_return_type

class Item(BaseModel):
    value: int
async def main():
    first, second = DebugTelemetryRecorder(), DebugTelemetryRecorder()
    composite = CompositeProvider([first,second])
    config=FridayChatConfig.model_validate({'telemetry':{'enabled':False},'llm':{'model':'openai/synthetic'}})
    runtime=build_runtime(config, telemetry=composite)
    observer=runtime.telemetry
    assert isinstance(observer,ChatTelemetryObserver)
    parent=observer.start_span('chat.runtime')
    child=observer.start_span('chat.application',parent)
    observer.end_span(child,{'outcome':'succeeded','count':0})
    observer.end_span(parent)
    observer.end_span(child)
    result=await FridayChatApp(runtime=runtime,input_source=ListInputSource([])).run()
    assert result.exit_reason=='eof'
    for sink in (first,second):
        p=sink.get_span_by_name('chat.runtime');c=sink.get_span_by_name('chat.application')
        assert p and c and p.end_time and c.end_time and sink.spans[c.parent_id] is p
        assert sink.event_names==['chat.runtime_ready','chat.application_start','chat.application_stop']
    assert [e.data for e in first.events]==[e.data for e in second.events]
    assert observer.snapshot().state=='active'
    assert all('session_id' not in e.data for e in first.events)
    for generic in (MemoryMetric,CommandRegistry,SessionContext,SessionManager,ToolAdapter):
        assert typing.get_origin(generic[Item]) is generic
    valid=MoltbookResponse[Item](success=True,data={'value':3})
    assert isinstance(valid.data,Item)
    assert valid.model_dump()['data']=={'value':3}
    schema=valid.model_json_schema()
    try:MoltbookResponse[Item](success=True,data={'value':'invalid'})
    except ValidationError:pass
    else:raise AssertionError('Invalid generic Pydantic data accepted')
    assert validate_return_type({'value':3},Item)==Item(value=3)
    assert isinstance(MemoryLLMClient,typing.TypeAliasType)
    oldfile=Path(__file__).with_name('baseline_moltbook.py')
    spec=importlib.util.spec_from_file_location('baseline_moltbook',oldfile);old=importlib.util.module_from_spec(spec);sys.modules[spec.name]=old;spec.loader.exec_module(old)
    assert old.MoltbookResponse[Item].model_json_schema()==schema
    print(json.dumps({'python':sys.version,'observer':type(observer).__name__,'providers':2,'nested_spans_per_sink':2,'lifecycle':first.event_names,'generic_schema_unchanged':True,'specialization_and_validation':'passed','alias':'TypeAliasType; callers use annotation-only'},indent=2))
asyncio.run(main())
