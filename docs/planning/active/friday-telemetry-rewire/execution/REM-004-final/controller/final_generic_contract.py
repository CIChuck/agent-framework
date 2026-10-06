"""Final candidate invariant consumers; negative errors are checked, not waived."""
from pathlib import Path
import hashlib,json,subprocess,sys,os
sites=[('MemoryMetric','packages/friday-chat/src/friday_chat/memory_views.py'),('CommandRegistry','packages/friday-cli/src/friday_cli/commands.py'),('SessionContext','packages/friday-cli/src/friday_cli/session.py'),('SessionManager','packages/friday-cli/src/friday_cli/session.py'),('ToolAdapter','packages/friday-core/src/friday_core/interfaces/tools.py'),('MoltbookResponse','packages/friday-moltbook/src/friday_moltbook/responses.py')]
root=Path.cwd();out=Path(os.environ['TMPDIR'])/'final-generic-consumers';out.mkdir(exist_ok=False);records=[]
for cls,path in sites:
 folder=out/cls;folder.mkdir();source=(root/path).read_bytes();old=subprocess.check_output(['git','show',f'559ae9f:{path}']);(folder/'original.py').write_bytes(old);(folder/'final.py').write_bytes(source)
 parent='from pydantic import BaseModel\nclass Parent(BaseModel):\n    value: str\nclass Child(Parent):\n    extra: int\n' if cls=='MoltbookResponse' else 'class Parent: pass\nclass Child(Parent): pass\n'
 consumer=f'from original import {cls} as Original\nfrom final import {cls} as Final\n'+parent
 functions=[('old_parent_child','Original','Parent','Child'),('old_child_parent','Original','Child','Parent'),('final_parent_child','Final','Parent','Child'),('final_child_parent','Final','Child','Parent')];lines=[]
 for label,module,left,right in functions:
  consumer+=f'def {label}(value: {module}[{left}]) -> {module}[{right}]:\n';lines.append(len(consumer.splitlines())+1);consumer+='    return value\n\n'
 target=folder/'consumer.py';target.write_text(consumer);command=[sys.executable,'-m','mypy','--python-version','3.13','--config-file',str(root/'pyproject.toml'),str(target)];result=subprocess.run(command,capture_output=True,text=True);errors=[s for s in result.stdout.splitlines() if ': error:' in s];expected=[f'{target}:{n}: error: Incompatible return value type' for n in lines];passed=result.returncode==1 and not result.stderr and len(errors)==4 and all(any(s.startswith(e) and s.endswith('[return-value]') for s in errors) for e in expected)
 records.append(dict(cls=cls,path=path,original_sha256=hashlib.sha256(old).hexdigest(),final_sha256=hashlib.sha256(source).hexdigest(),consumer=consumer,command=command,mypy_exit=result.returncode,stdout=result.stdout,stderr=result.stderr,expected_lines=lines,contract_preserved=passed));print(cls,'preserved',passed,flush=True)
(out/'result.json').write_text(json.dumps(records,indent=2)+'\n');print('NEGATIVE CONSUMERS',out/'result.json');sys.exit(0 if all(x['contract_preserved'] for x in records) else 1)
