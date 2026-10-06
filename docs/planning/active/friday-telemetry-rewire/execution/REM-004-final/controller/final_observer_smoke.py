import sys
import importlib.metadata as md
from pathlib import Path
from friday_chat.telemetry import ChatTelemetryObserver
from friday_telemetry import CompositeProvider, DebugTelemetryRecorder
if sys.version_info < (3,13,4): raise RuntimeError('Unsupported interpreter')
recorders=[DebugTelemetryRecorder(),DebugTelemetryRecorder()]
composite=CompositeProvider(recorders)
observer=ChatTelemetryObserver(enabled=True,session_id='reviewer-synthetic',provider=composite)
root=observer.start_span('chat.runtime');child=observer.start_span('chat.application',root)
observer.emit('runtime_ready');observer.emit('application_start');observer.end_span(child);observer.emit('application_stop');observer.end_span(root)
for r in recorders:
 if len(r.spans)!=2 or any(s.end_time is None for s in r.spans.values()):raise RuntimeError('Unclosed child spans')
 spans=list(r.spans.items());parents=[k for k,s in spans if s.name=='chat.runtime'];children=[s for k,s in spans if s.name=='chat.application']
 if len(parents)!=1 or len(children)!=1 or children[0].parent_id!=parents[0]:raise RuntimeError('Parent mapping wrong')
 if r.event_names != ['chat.runtime_ready','chat.application_start','chat.application_stop']:raise RuntimeError('Event lifecycle wrong')
if observer.snapshot().state!='active' or observer.snapshot().failure_count:raise RuntimeError('Observer unhealthy')
for name in ['friday_chat.telemetry','friday_telemetry.providers.composite']:
 p=Path(sys.modules[name].__file__).resolve()
 if not p.is_relative_to('/private/tmp/telem-01/REM-004/approved-execution/root-a06-final'):raise RuntimeError('Original editable source imported')
 print(name,p)
print('Genuine Chat observer and Composite lifecycle passed',sys.version.split()[0],'LiteLLM',md.version('litellm'))
