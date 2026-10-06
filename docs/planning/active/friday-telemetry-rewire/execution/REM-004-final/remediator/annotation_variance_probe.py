import json,subprocess
from pathlib import Path
out=Path('/private/tmp/telem-01/REM-004/approved-execution/remediator')
source=(Path.cwd()/'packages/friday-cli/src/friday_cli/commands.py').read_text()
variants={
 'object_bound':source.replace('class CommandRegistry(Generic[T]):','class CommandRegistry[T: object]:'),
 'explicit_self_execute':source.replace('class CommandRegistry(Generic[T]):','class CommandRegistry[T]:').replace('    async def execute(\n        self,','    async def execute(\n        self: CommandRegistry[T],'),
 'explicit_self_command':source.replace('class CommandRegistry(Generic[T]):','class CommandRegistry[T]:').replace('    def command(\n        self,','    def command(\n        self: CommandRegistry[T],'),
 'explicit_self_init':source.replace('class CommandRegistry(Generic[T]):','class CommandRegistry[T]:').replace('    def __init__(self):','    def __init__(self: CommandRegistry[T]) -> None:'),
}
records=[]
for name,text in variants.items():
 folder=out/'annotation-probes'/name;folder.mkdir(parents=True,exist_ok=False)
 (folder/'converted.py').write_text(text)
 (folder/'consumer.py').write_text('''from converted import CommandRegistry
class Parent: pass
class Child(Parent): pass
def parent_to_child(value: CommandRegistry[Parent]) -> CommandRegistry[Child]:
    return value

def child_to_parent(value: CommandRegistry[Child]) -> CommandRegistry[Parent]:
    return value
''')
 result=subprocess.run(['/opt/homebrew/bin/uv','run','--no-sync','mypy','--python-version','3.13',str(folder/'consumer.py')],text=True,capture_output=True)
 records.append(dict(variant=name,exit=result.returncode,stdout=result.stdout,stderr=result.stderr))
 print(json.dumps(records[-1]),flush=True)
(out/'annotation-probes.json').write_text(json.dumps(records,indent=2)+'\n')
