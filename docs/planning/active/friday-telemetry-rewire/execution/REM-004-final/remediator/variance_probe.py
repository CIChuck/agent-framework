import json, subprocess
from pathlib import Path
root=Path.cwd()
path='packages/friday-cli/src/friday_cli/commands.py'
original=(root/path).read_text()
probes={
 'baseline':original,
 'explicit_invariant':original.replace('T = TypeVar("T")','T = TypeVar("T", covariant=False, contravariant=False)'),
 'explicit_no_inference':original.replace('T = TypeVar("T")','T = TypeVar("T", infer_variance=False)'),
}
for label,source in probes.items():
 result=subprocess.run(['/opt/homebrew/bin/uv','run','--no-sync','ruff','check','--select','UP046','--output-format','json','--stdin-filename',path,'-'],input=source,text=True,capture_output=True)
 print(json.dumps({'label':label,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr}))
