import json, subprocess, tempfile
from pathlib import Path
original=(Path.cwd()/'packages/friday-cli/src/friday_cli/commands.py').read_text()
with tempfile.TemporaryDirectory() as directory:
 folder=Path(directory)
 (folder/'original_commands.py').write_text(original)
 (folder/'pep695_commands.py').write_text(original.replace('class CommandRegistry(Generic[T]):','class CommandRegistry[T]:'))
 (folder/'consumer.py').write_text('''from original_commands import CommandRegistry as Original
from pep695_commands import CommandRegistry as Converted
class Parent: pass
class Child(Parent): pass
original_parent: Original[Parent] = Original()
original_child: Original[Child] = original_parent
converted_parent: Converted[Parent] = Converted()
converted_child: Converted[Child] = converted_parent
''')
 result=subprocess.run(['/opt/homebrew/bin/uv','run','--no-sync','mypy','--python-version','3.13',str(folder/'consumer.py')],text=True,capture_output=True)
 print(json.dumps({'command':'uv run --no-sync mypy --python-version 3.13 <private consumer.py>', 'source_variants':'exact CommandRegistry class header replacement only', 'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr}))
