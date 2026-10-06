from pathlib import Path
import ast, hashlib, importlib.metadata, importlib.util, json, re, sys, tomllib
from packaging.specifiers import SpecifierSet
import yaml
root=Path.cwd(); pkt=root/'docs/planning/active/friday-telemetry-rewire'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=Path('/private/tmp/telem-01/REM-004/approved-execution')
expanded=json.loads((out/'root-a06-final-expanded.json').read_text())
for p in expanded['changed_python']:ast.parse((root/p).read_text(),feature_version=(3,13))
configs=json.loads(re.search(r'```json\n(.*?)\n```',(pkt/'validation/WVR-002-archived-probe-lint.md').read_text(),re.S).group(1))
for p,h in configs.items():
 if sha(root/p)!=h:raise RuntimeError('Lint configuration drift '+p)
request=json.loads((out/'product-validation-request.json').read_text())
for a in request['authority']:
 if sha(root/a['path'])!=a['sha256']:raise RuntimeError('Authority drift '+a['path'])
if sha(root/request['manifest_path'])!=request['manifest_sha256']:raise RuntimeError('Manifest drift')
scope=json.loads((pkt/'remediation/REM-004-scope.json').read_text())
for p,v in scope['archived_files'].items():
 h=v['sha256'] if isinstance(v,dict) else v
 if sha(root/p)!=h:raise RuntimeError('Archive drift '+p)
wvr=json.loads((pkt/'validation/WVR-003-command-registry-scope.json').read_text())
if sha(root/wvr['diagnostic']['path'])!=wvr['source_sha256']:raise RuntimeError('Registry drift')
projects=[root/'pyproject.toml']+sorted((root/'packages').glob('*/pyproject.toml'))+[root/'tests/integration/memory/pyproject.toml']
# Identify the eighteenth lab project from tracked metadata, without runtime paths.
if not projects[-1].is_file():
 import subprocess
 labs=[root/p for p in subprocess.check_output(['git','ls-files','*pyproject.toml']).decode().splitlines() if not p.startswith('packages/') and p!='pyproject.toml']
 projects=projects[:-1]+labs
metadata={}
for p in projects:
 d=tomllib.loads(p.read_text()); minimum=d.get('project',{}).get('requires-python')
 if minimum is None:continue
 spec=SpecifierSet(minimum)
 if '3.13.3' in spec or '3.13.4' not in spec:raise RuntimeError('Minimum drift '+str(p))
 metadata[str(p.relative_to(root))]={'sha256':sha(p),'requires-python':minimum,'rejects_3_13_3':True,'accepts_3_13_4':True}
if len(metadata)!=18:raise RuntimeError('Expected 18 project minimums: '+str(len(metadata)))
origins={}
for src in sorted((root/'packages').glob('*/src')):
 for module in sorted(src.glob('friday_*')):
  spec=importlib.util.find_spec(module.name)
  locations=([spec.origin] if spec and spec.origin else list(spec.submodule_search_locations) if spec else [])
  if not locations or any(not str(x).startswith(str(root)) for x in locations):raise RuntimeError('Original editable import '+module.name)
  origins[module.name]=locations
versions={p:importlib.metadata.version(p) for p in ['ruff','mypy','pytest','litellm']}
if versions['ruff']!='0.14.10':raise RuntimeError('Ruff version drift')
record={'revision':request['candidate'],'python':sys.version,'versions':versions,'changed_python_ast_313':len(expanded['changed_python']),'authority_matches':len(request['authority']),'lint_configs':configs,'archive_hashes':scope['archived_files'],'registry_sha256':wvr['source_sha256'],'metadata':metadata,'source_origins':origins,'lock_sha256':sha(root/'uv.lock')}
(out/'root-final-integrity.json').write_text(json.dumps(record,indent=2)+'\n')
print('Integrity passed:',len(metadata),'project minimums,',len(configs),'lint configs,',len(origins),'isolated modules,',len(request['authority']),'authority pins,',len(expanded['changed_python']),'Python ASTs')
