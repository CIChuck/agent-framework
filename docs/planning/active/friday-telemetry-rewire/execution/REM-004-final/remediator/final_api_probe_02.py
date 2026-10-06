from pathlib import Path
import ast, asyncio, hashlib, importlib.util, json, subprocess, sys
from datetime import UTC, timezone
from pydantic import BaseModel, ValidationError
out=Path('/private/tmp/telem-01/REM-004/approved-execution/remediator')
folder=out/'final-api-source-02';folder.mkdir(exist_ok=False)
old=json.loads((out/'variance-matrix-raw.json').read_text());records=[]
for site in old:
 cls=site['class'];path=site['path'];case=folder/cls;case.mkdir()
 original=out/'variance-matrix-source'/cls/'original.py'
 current=Path.cwd()/path
 (case/'original.py').write_bytes(original.read_bytes());(case/'current.py').write_bytes(current.read_bytes())
 parent='from pydantic import BaseModel\nclass Parent(BaseModel):\n    value: str\nclass Child(Parent):\n    extra: int\n' if cls=='MoltbookResponse' else 'class Parent: pass\nclass Child(Parent): pass\n'
 text=f'from original import {cls} as Original\nfrom current import {cls} as Current\n'+parent
 for variant in ['Original','Current']:
  for a,b in [('Parent','Child'),('Child','Parent')]:
   text+=f'def {variant.lower()}_{a.lower()}_to_{b.lower()}(value: {variant}[{a}]) -> {variant}[{b}]:\n    return value\n'
 text+=f'def current_same(value: Current[Parent]) -> Current[Parent]:\n    return value\n'
 (case/'consumer.py').write_text(text)
 r=subprocess.run(['/opt/homebrew/bin/uv','run','--no-sync','mypy','--python-version','3.13',str(case/'consumer.py')],capture_output=True,text=True)
 assert r.returncode==1 and r.stdout.count('[return-value]')==4,(cls,r.stdout,r.stderr)
 record={'class':cls,'path':path,'baseline_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'current_sha256':hashlib.sha256(current.read_bytes()).hexdigest(),'consumer_sha256':hashlib.sha256(text.encode()).hexdigest(),'stdout':r.stdout,'stderr':r.stderr,'exit':r.returncode,'baseline_and_current_invariant':True,'same_type_positive_accepted':True}
 records.append(record);print(cls,'four intended direction rejects; same type accepted',flush=True)
# Compare actual final Moltbook Pydantic behavior with original source.
class Parent(BaseModel):
 value:str
class Child(Parent):
 extra:int
schemas={}
for variant in ['original','current']:
 path=folder/'MoltbookResponse'/f'{variant}.py';name=f'rem004_final_{variant}'
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 parent_model=module.MoltbookResponse[Parent];child_model=module.MoltbookResponse[Child]
 rejected=False
 try:child_model.model_validate({'success':True,'data':{'value':'synthetic'}})
 except ValidationError:rejected=True
 schemas[variant]={'parent_schema':parent_model.model_json_schema(),'child_schema':child_model.model_json_schema(),'parent_dump':parent_model.model_validate({'success':True,'data':{'value':'synthetic'}}).model_dump(),'child_dump':child_model.model_validate({'success':True,'data':{'value':'synthetic','extra':1}}).model_dump(),'negative_child_required_field':rejected,'public_subscriptability':parent_model.__name__=='MoltbookResponse[Parent]'}
assert schemas['original']==schemas['current']
assert UTC is timezone.utc and asyncio.TimeoutError is TimeoutError
positive="""from collections.abc import Coroutine
from typing import Any
from pydantic import BaseModel
from friday_cli.cancellation import run_cancellable
from friday_chat.memory_views import MemoryMetric
from friday_chat.commands.memory import _metric_text
from friday_memory.llm_completion import MemoryLLMClient, LegacyMemoryLLMClient, complete_structured_memory_request
from friday_llm import TypedLLMClient
from friday_sandbox.serialization import validate_return_type
class Fact(BaseModel):
    fact: str
async def positive(client: TypedLLMClient, legacy: LegacyMemoryLLMClient, operation: Coroutine[Any, Any, str]) -> None:
    typed_alias: MemoryLLMClient = client
    legacy_alias: MemoryLLMClient = legacy
    typed_result: Fact | None = await complete_structured_memory_request(typed_alias, messages=[{'role':'user','content':'synthetic'}], response_model=Fact)
    legacy_result: Fact | None = await complete_structured_memory_request(legacy_alias, messages=[{'role':'user','content':'synthetic'}], response_model=Fact)
    result: str | None = await run_cancellable(operation)
    fact: Fact = validate_return_type({'fact':'synthetic'}, Fact)
    rendered: str = _metric_text(MemoryMetric.available(0))
"""
negative="""from pydantic import BaseModel
from friday_memory.llm_completion import MemoryLLMClient, complete_structured_memory_request
from friday_sandbox.serialization import validate_return_type
async def negative(client: MemoryLLMClient) -> None:
    await complete_structured_memory_request(client, messages=[{'role':'user','content':'synthetic'}], response_model=str)
    validate_return_type({}, str)
"""
function_results={}
for name,text in [('positive',positive),('negative',negative)]:
 path=folder/f'function_{name}.py';path.write_text(text)
 r=subprocess.run(['/opt/homebrew/bin/uv','run','--no-sync','mypy','--python-version','3.13',str(path), 'packages/friday-memory/src/friday_memory/llm_completion.py', 'packages/friday-sandbox/src/friday_sandbox/serialization.py', 'packages/friday-cli/src/friday_cli/cancellation.py', 'packages/friday-chat/src/friday_chat/memory_views.py', 'packages/friday-chat/src/friday_chat/commands/memory.py'],capture_output=True,text=True)
 assert r.returncode==(0 if name=='positive' else 1),(name,r.stdout,r.stderr)
 if name=='negative':assert r.stdout.count('[type-var]')==2,r.stdout
 function_results[name]={'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'sha256':hashlib.sha256(text.encode()).hexdigest()}
 print('function',name,r.returncode,r.stdout,flush=True)
from friday_sandbox.serialization import validate_return_type
try:validate_return_type({},str)
except TypeError:pass
else:raise AssertionError('Non-model bound not enforced at runtime')
try:validate_return_type({},Parent)
except ValidationError:pass
else:raise AssertionError('Malformed required fields accepted')
assert validate_return_type({'value':'synthetic'},Parent).value=='synthetic'
result={'snapshot':str(Path.cwd()),'classes':records,'pydantic':schemas,'pydantic_equal':True,'UTC_identity':True,'TimeoutError_identity':True,'functions':function_results,'runtime_validate_return_type_positive_negative':True}
(out/'final-api-probe-results-02.json').write_text(json.dumps(result,indent=2)+'\n')
print('FINAL_API_PROBE_PASS',flush=True)
