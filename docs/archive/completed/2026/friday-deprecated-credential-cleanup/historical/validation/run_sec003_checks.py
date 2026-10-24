from pathlib import Path
import os,subprocess,json,hashlib,tempfile
from datetime import datetime,timezone
b=Path('/private/tmp/friday-mcp-upgrade/credential-cleanup');w=b/'work';out=b/'sec003-checks';out.mkdir()
seed=json.loads((b/'checks/corrected-chat-full/preflight.json').read_text())['environment']
product=['.gitignore']
def hashes():return {p:hashlib.sha256((w/p).read_bytes()).hexdigest() for p in product}
commands=[('compat-without-legacy',['/private/tmp/friday-mcp-upgrade/venv/bin/python','-m','pytest','packages/friday-chat/tests_chat/compat','-q']),('board',['/private/tmp/friday-mcp-upgrade/venv/bin/python','scripts/friday-dev-board.py','validate']),('docs',['/private/tmp/friday-mcp-upgrade/venv/bin/python','scripts/check-documentation-lifecycle.py']),('render',['/private/tmp/friday-mcp-upgrade/venv/bin/python','scripts/friday-dev-board.py','render','--check']),('whitespace',['git','diff','--check','53df04a94d1085aa4f3b6de8dba0db254879c29c..HEAD'])]
receipts=[]
for label,argv in commands:
 folder=out/label;folder.mkdir();home=folder/'home';home.mkdir();tmp=folder/'tmp';tmp.mkdir();env=dict(seed);env.update({'HOME':str(home),'TMPDIR':str(tmp),'PYTEST_ADDOPTS':'--import-mode=importlib -o cache_dir='+str(home/'pytest'),'UV_CACHE_DIR':str(home/'uv'),'MYPY_CACHE_DIR':str(home/'mypy'),'RUFF_CACHE_DIR':str(home/'ruff'),'XDG_CACHE_HOME':str(home/'.cache'),'MPLCONFIGDIR':str(home/'mpl')})
 original=w/'tests/integration/memory';hidden=b/'sec003-hidden-memory';hide=True;before=hashes();start=datetime.now(timezone.utc).isoformat()
 if hide:
  if hidden.exists():raise RuntimeError('Unexpected hidden private directory')
  original.rename(hidden)
 try:run=subprocess.run(argv,cwd=w,env=env,capture_output=True)
 finally:
  if hide:hidden.rename(original)
 (folder/'stdout').write_bytes(run.stdout);(folder/'stderr').write_bytes(run.stderr)
 receipt={'label':label,'candidate':subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip(),'argv':argv,'cwd':str(w),'environment':env,'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'exit_code':run.returncode,'private_legacy_directory_unavailable_during_test':hide,'private_directory_restored':original.exists(),'main_checkout_touched':False,'product_before':before,'product_after':hashes(),'stdout_sha256':hashlib.sha256(run.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(run.stderr).hexdigest()};(folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');receipts.append({'check':label,'exit_code':run.returncode})
 print(json.dumps(receipts[-1]),flush=True)
 if run.returncode:raise SystemExit(run.returncode)
