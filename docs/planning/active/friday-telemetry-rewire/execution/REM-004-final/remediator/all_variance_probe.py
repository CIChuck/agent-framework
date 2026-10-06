import hashlib, importlib.util, json, subprocess, tempfile, sys
from pathlib import Path
root=Path.cwd()
out=Path('/private/tmp/telem-01/REM-004/approved-execution/remediator')
sites=[
 ('MemoryMetric','packages/friday-chat/src/friday_chat/memory_views.py','class MemoryMetric(Generic[T]):','class MemoryMetric[T]:'),
 ('CommandRegistry','packages/friday-cli/src/friday_cli/commands.py','class CommandRegistry(Generic[T]):','class CommandRegistry[T]:'),
 ('SessionContext','packages/friday-cli/src/friday_cli/session.py','class SessionContext(Generic[T]):','class SessionContext[T]:'),
 ('SessionManager','packages/friday-cli/src/friday_cli/session.py','class SessionManager(Generic[T]):','class SessionManager[T]:'),
 ('ToolAdapter','packages/friday-core/src/friday_core/interfaces/tools.py','class ToolAdapter(Protocol, Generic[T]):','class ToolAdapter[T](Protocol):'),
 ('MoltbookResponse','packages/friday-moltbook/src/friday_moltbook/responses.py','class MoltbookResponse(BaseModel, Generic[T]):','class MoltbookResponse[T](BaseModel):'),
]
records=[]
for cls,path,before,after in sites:
 original=(root/path).read_text()
 assert original.count(before)==1
 folder=out/'variance-matrix-source'/cls
 folder.mkdir(parents=True,exist_ok=False)
 (folder/'original.py').write_text(original)
 (folder/'converted.py').write_text(original.replace(before,after))
 parent='from pydantic import BaseModel\nclass Parent(BaseModel):\n    value: str\nclass Child(Parent):\n    extra: int\n' if cls=='MoltbookResponse' else 'class Parent: pass\nclass Child(Parent): pass\n'
 consumer=f'from original import {cls} as Original\nfrom converted import {cls} as Converted\n'+parent+'''def original_parent_to_child(value: Original[Parent]) -> Original[Child]:
    return value

def original_child_to_parent(value: Original[Child]) -> Original[Parent]:
    return value

def converted_parent_to_child(value: Converted[Parent]) -> Converted[Child]:
    return value

def converted_child_to_parent(value: Converted[Child]) -> Converted[Parent]:
    return value
'''
 (folder/'consumer.py').write_text(consumer)
 result=subprocess.run(['/opt/homebrew/bin/uv','run','--no-sync','mypy','--python-version','3.13',str(folder/'consumer.py')],capture_output=True,text=True)
 record={'class':cls,'path':path,'original_sha256':hashlib.sha256(original.encode()).hexdigest(),'header_before':before,'header_after':after,'consumer_sha256':hashlib.sha256(consumer.encode()).hexdigest(),'mypy_exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'consumer':consumer}
 for label,replacement in [('explicit_false','T = TypeVar("T", covariant=False, contravariant=False)'),('no_inference','T = TypeVar("T", infer_variance=False)')]:
  source=original.replace('T = TypeVar("T")',replacement)
  lint=subprocess.run(['/opt/homebrew/bin/uv','run','--no-sync','ruff','check','--select','UP046','--output-format','json','--stdin-filename',path,'-'],input=source,capture_output=True,text=True)
  record[label]={'exit':lint.returncode,'diagnostics':json.loads(lint.stdout),'stderr':lint.stderr}
 records.append(record)
 print(json.dumps({'class':cls,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr}),flush=True)
(out/'variance-matrix-raw.json').write_text(json.dumps(records,indent=2)+'\n')
