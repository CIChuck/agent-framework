from pathlib import Path
import ast, hashlib, json, subprocess, re
from datetime import datetime,timezone
b=Path('/private/tmp/friday-mcp-upgrade/credential-cleanup');w=b/'work';out=b/'sec002-review';out.mkdir(exist_ok=True)
base='85f14f249f5fffaf73659aec2a344efa05743c08';candidate='e5a3066c34d53214ab0b406fc9cfb638d2276244'
def git(*args):return subprocess.check_output(['git',*args],cwd=w)
def sha(data):return hashlib.sha256(data).hexdigest()
assert git('rev-parse','HEAD').decode().strip()==candidate
assert not git('status','--porcelain')
packet='docs/planning/active/friday-deprecated-credential-cleanup/'
authority=json.loads((w/(packet+'authority-sec002.json')).read_text());prov=json.loads((w/(packet+'command-baseline-provenance.json')).read_text())
assert sha((w/authority['directive']).read_bytes())==authority['directive_sha256']
legacy=git('show',base+':'+prov['legacy_source_path'])
assert sha(legacy)==prov['legacy_source_sha256']
assert git('rev-parse',base+':'+prov['legacy_source_path']).decode().strip()==prov['legacy_source_blob']
# Interpret only AST nodes, never execute/import legacy source.
commands=set()
for node in ast.walk(ast.parse(legacy)):
 if not (isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='register'):continue
 if node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str) and node.args[0].value:commands.add(node.args[0].value)
 for kw in node.keywords:
  if kw.arg=='aliases' and isinstance(kw.value,ast.List):
   commands.update(el.value for el in kw.value.elts if isinstance(el,ast.Constant) and isinstance(el.value,str) and el.value)
fixture=(w/prov['fixture']).read_bytes(); fixture_names={line[2:] for line in fixture.decode().splitlines() if line.startswith('- ')}
assert len(commands)==50
assert commands|{'debug-retrieval','list-ingested'}==fixture_names
assert len(fixture_names)==52 and sha(fixture)==prov['fixture_sha256']
assert not git('diff',base+'..'+candidate,'--','tests/integration/memory')
report=packet+'validation/VAL-SEC-001/report.md'
assert git('show',base+':'+report)==(w/report).read_bytes()
assert not git('diff',base+'..'+candidate,'--','scripts/check-documentation-lifecycle.py','AGENTS.md',packet+'validation/VAL-SEC-001')
links=re.findall(r'\]\(([^)]+:\d+)\)',(w/report).read_text().splitlines()[20]);assert len(links)==2
assert all(not Path(link).exists() and Path(link.rsplit(':',1)[0]).exists() for link in links)
receipt_verification=[]
for folder in sorted((b/'sec002-final-checks').iterdir()):
 if not (folder/'receipt.json').exists():continue
 r=json.loads((folder/'receipt.json').read_text())
 assert r['candidate']==candidate and r['stdout_sha256']==sha((folder/'stdout').read_bytes()) and r['stderr_sha256']==sha((folder/'stderr').read_bytes())
 assert r['product_before']==r['product_after']
 for p,h in r['product_after'].items():assert sha((w/p).read_bytes())==h
 assert r['exit_code']==(1 if folder.name=='docs' else 0)
 receipt_verification.append({'check':folder.name,'exit_code':r['exit_code'],'stdout':(folder/'stdout').read_text().strip(),'stderr':(folder/'stderr').read_text().strip()})
(out/'static-evidence.json').write_text(json.dumps({'candidate':candidate,'base':base,'directive_sha256':authority['directive_sha256'],'legacy_sha256':sha(legacy),'legacy_blob':prov['legacy_source_blob'],'registered_names':len(commands),'fixture_names':len(fixture_names),'fixture_sha256':sha(fixture),'exact_set_equal':True,'deprecated_directory_unchanged':True,'sec001_report_sha256':sha((w/report).read_bytes()),'sec001_report_and_checker_unchanged':True,'baseline_broken_links':links,'final_receipts_verified':receipt_verification},indent=2)+'\n')
seed=json.loads((b/'sec002-final-checks/compat-without-legacy/receipt.json').read_text())['environment']
commands_to_run=[('compat',['/private/tmp/friday-mcp-upgrade/venv/bin/python','-m','pytest','packages/friday-chat/tests_chat/compat','-q']),('ruff',['/private/tmp/friday-mcp-upgrade/venv/bin/ruff','check',authority['product_paths'][0]]),('mypy',['/private/tmp/friday-mcp-upgrade/venv/bin/python','-m','mypy',authority['product_paths'][0]]),('board',['/private/tmp/friday-mcp-upgrade/venv/bin/python','scripts/friday-dev-board.py','validate']),('render',['/private/tmp/friday-mcp-upgrade/venv/bin/python','scripts/friday-dev-board.py','render','--check']),('docs',['/private/tmp/friday-mcp-upgrade/venv/bin/python','scripts/check-documentation-lifecycle.py']),('whitespace',['git','diff','--check',base+'..'+candidate])]
for label,argv in commands_to_run:
 f=out/label;f.mkdir();home=f/'home';home.mkdir();tmp=f/'tmp';tmp.mkdir();env=dict(seed)
 env.update({'HOME':str(home),'TMPDIR':str(tmp),'PYTEST_ADDOPTS':'--import-mode=importlib -o cache_dir='+str(home/'pytest'),'UV_CACHE_DIR':str(home/'uv'),'MYPY_CACHE_DIR':str(home/'mypy'),'RUFF_CACHE_DIR':str(home/'ruff'),'XDG_CACHE_HOME':str(home/'.cache'),'MPLCONFIGDIR':str(home/'mpl')})
 start=datetime.now(timezone.utc).isoformat();run=subprocess.run(argv,cwd=w,env=env,capture_output=True)
 (f/'stdout').write_bytes(run.stdout);(f/'stderr').write_bytes(run.stderr)
 (f/'receipt.json').write_text(json.dumps({'candidate':candidate,'argv':argv,'environment':env,'cwd':str(w),'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'exit_code':run.returncode,'stdout_sha256':sha(run.stdout),'stderr_sha256':sha(run.stderr)},indent=2)+'\n')
 print(label,run.returncode,run.stdout.decode().strip(),run.stderr.decode().strip(),flush=True)
 assert run.returncode==(1 if label=='docs' else 0)
assert git('rev-parse','HEAD').decode().strip()==candidate and not git('status','--porcelain')
print('unchanged candidate and clean status confirmed')
