from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,sys
b=Path('/private/tmp/friday-mcp-upgrade');c=b/'credential-cleanup';label,*argv=sys.argv[1:];w=c/'work';out=c/'checks'/label;out.mkdir(parents=True,exist_ok=False);home=c/'homes'/label;tmp=c/'tmp'/label;home.mkdir(parents=True);tmp.mkdir(parents=True);p=w/'docs/planning/active/friday-deprecated-credential-cleanup';a=json.loads((p/'authority.json').read_text())
def h(f):return hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else None
raw=subprocess.check_output(['git','show',a['base_commit']+':tests/integration/memory/config.yaml'],cwd=w,text=True);secret_lines=[66,77,104,120,190,711,1007,1015,1023,1031,1568,1578,2221,2237,2265,2384];secrets=[]
for number in secret_lines:
    match=re.search(r'(?:api_key|secret_key|access_token)\s*:\s*[\"\']?([A-Za-z0-9_./+=:\-]{12,})',raw.splitlines()[number-1])
    if match:secrets.append(match.group(1).encode())
env={'PATH':str(b/'venv/bin')+':/opt/homebrew/bin:/usr/bin:/bin','HOME':str(home),'TMPDIR':str(tmp),'PYTHONPATH':':'.join([str(b/'guard')]+[str(x) for x in sorted((w/'packages').glob('*/src'))]+[str(w/'packages/friday-chat'),str(w/'packages/friday-chat/tests_chat')]),'PYTHONDONTWRITEBYTECODE':'1','PYTHONHASHSEED':'0','PYTEST_ADDOPTS':'--import-mode=importlib -o cache_dir='+str(home/'pytest'),'UV_NO_SYNC':'1','UV_OFFLINE':'1','UV_PROJECT_ENVIRONMENT':str(b/'venv'),'UV_CACHE_DIR':str(home/'uv'),'VIRTUAL_ENV':str(b/'venv'),'MYPY_CACHE_DIR':str(home/'mypy'),'RUFF_CACHE_DIR':str(home/'ruff'),'FRIDAY_TELEMETRY_ENABLED':'false','ANONYMIZED_TELEMETRY':'false','TOKENIZERS_PARALLELISM':'false','XDG_CACHE_HOME':str(home/'.cache'),'MPLCONFIGDIR':str(home/'mpl')}
pre={'argv':argv,'candidate':subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip(),'authority_sha256':h(p/'authority.json'),'directive_sha256':h(w/a['directive']),'product_sha256':{x:h(w/x) for x in a['product_paths']},'guard_sha256':h(b/'guard/sitecustomize.py'),'environment':env};(out/'preflight.json').write_text(json.dumps(pre,indent=2)+'\n');start=datetime.now(timezone.utc).isoformat();run=subprocess.run(argv,cwd=w,env=env,capture_output=True);redactions=0
for name,data in [('stdout',run.stdout),('stderr',run.stderr)]:
    for value in set(secrets):
        redactions+=data.count(value);data=data.replace(value,b'[REDACTED EXPOSED CREDENTIAL]')
    (out/name).write_bytes(data)
receipt={'argv':argv,'cwd':str(w),'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'exit_code':run.returncode,'redacted_known_secret_occurrences':redactions,'stdout_sha256':h(out/'stdout'),'stderr_sha256':h(out/'stderr'),'product_sha256_after':{x:h(w/x) for x in a['product_paths']}};(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'check':label,'exit_code':run.returncode,'redacted_known_secret_occurrences':redactions,'evidence':str(out)}))
