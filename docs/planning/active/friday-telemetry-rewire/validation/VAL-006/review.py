from pathlib import Path
import ast, hashlib, json, os, subprocess, sys, time

REPO=Path('/Users/chuckrussell/Dev/gendev/agent-framework')
OUT=Path('/private/tmp/telem-01/REM-004/approved-execution/product-validation')
ROOT=OUT/'candidate'
REQ=OUT.parent/'product-validation-request.json'
GUARD=Path('/private/tmp/telem-01/REM-001/network-guard')
PY=REPO/'.venv/bin/python'
UV='/opt/homebrew/bin/uv'
request=json.loads(REQ.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,v): (OUT/name).write_text(json.dumps(v,indent=2)+'\n')
def git(*args): return subprocess.check_output(['git','-C',str(REPO),*args]).decode()
def state(root): return {str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file() and '.git' not in p.parts and p.suffix in ('.py','.toml','.yaml','.yml','.md','.lock')}
def env(label):
    temp=OUT/'tmp'/label;temp.mkdir(parents=True,exist_ok=True)
    return dict(PATH=f'{REPO}/.venv/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin',UV_PROJECT_ENVIRONMENT=str(REPO/'.venv'),UV_CACHE_DIR=str(temp/'uv'),UV_NO_SYNC='true',UV_OFFLINE='true',UV_PYTHON_DOWNLOADS='never',LITELLM_LOCAL_MODEL_COST_MAP='true',ANONYMIZED_TELEMETRY='False',TERM='xterm-256color',PYTHONPATH=os.pathsep.join([str(GUARD)]+[str(p) for p in sorted((ROOT/'packages').glob('*/src'))]+[str(ROOT/'packages/friday-chat/tests_chat'),str(ROOT)]),TMPDIR=str(temp),PYTHONDONTWRITEBYTECODE='1',RUFF_CACHE_DIR=str(temp/'ruff'),MYPY_CACHE_DIR=str(temp/'mypy'),PYTEST_ADDOPTS=f'-rA -o cache_dir={temp}/pytest')
def prepare():
    if ROOT.exists(): raise RuntimeError('Fresh snapshot required')
    revision=request['candidate']
    names=git('ls-tree','-r','--name-only',revision).splitlines()
    protected=['tests/integration/memory/.friday/','tests/integration/memory/vector/','tests/integration/memory/vector2_bak/','tests/integration/memory/vector_bak/','tests/integration/memory/.doltcfg/','experiments/provider_memory_smoke/memory/']
    omitted=[p for p in names if any(p.startswith(x) for x in protected) or '.friday' in Path(p).parts or Path(p).name=='.env']
    if any(Path(p).suffix in ('.py','.toml','.yaml','.yml') for p in omitted): raise RuntimeError('Governed source omission')
    subprocess.run(['git','clone','--shared','--no-checkout','--quiet',str(REPO),str(ROOT)],check=True)
    subprocess.run(['git','-C',str(ROOT),'config','core.sparseCheckout','true'],check=True)
    subprocess.run(['git','-C',str(ROOT),'config','core.sparseCheckoutCone','false'],check=True)
    (ROOT/'.git/info/sparse-checkout').write_text('/*\n'+''.join('!/'+p+'\n' for p in omitted))
    subprocess.run(['git','-C',str(ROOT),'checkout','--quiet','--detach',revision],check=True)
    if any((ROOT/p).exists() for p in omitted): raise RuntimeError('Materialized protected data')
    for lane in ['active','queued','review','blocked','deferred','backlog']: (ROOT/'docs/planning'/lane).mkdir(exist_ok=True)
    pins=[dict(x,actual=sha(ROOT/x['path'])) for x in request['authority']]
    if any(x['actual']!=x['sha256'] for x in pins):raise RuntimeError('Authority drift')
    if sha(ROOT/request['manifest_path'])!=request['manifest_sha256']:raise RuntimeError('Manifest drift')
    actual=git('diff','--name-only',request['base'],revision,'--','*.py').splitlines()
    if actual!=request['expanded']['changed_python']:raise RuntimeError('Expanded list drift')
    for key,base in [('delta',request['delta_base']),('aggregate',request['base'])]:
        (OUT/(key+'.diff')).write_text(git('diff',base,revision,'--','*.py','*.toml','*.md','*.sh','uv.lock'))
        (OUT/(key+'-paths.txt')).write_text(git('diff','--name-status',base,revision))
    save('snapshot.json',dict(candidate=revision,authority=pins,manifest_sha256=sha(ROOT/request['manifest_path']),guard_sha256=sha(GUARD/'sitecustomize.py'),omitted=omitted,tracked=state(ROOT),original_status=git('status','--porcelain=v1'),expanded=request['expanded']))
    print('Prepared',revision,'omitted',len(omitted),'Python',len(actual))
def run(label,args):
    snap=json.loads((OUT/'snapshot.json').read_text())
    if state(ROOT)!=snap['tracked']:raise RuntimeError('Source changed')
    if sha(GUARD/'sitecustomize.py')!='6f61ea4ca34c7abef9e0c709eb1e1feb0f3cf7733cbc59bc465d6b01182e9e81':raise RuntimeError('Guard changed')
    if not (OUT/'preflight.json').exists():raise RuntimeError('No frozen preflight')
    command=[UV,'run','--no-sync',*args] if args[0]!='lock' else [UV,*args]
    log=OUT/(label+'.log'); record=OUT/(label+'.json')
    if log.exists():raise RuntimeError('Retain existing evidence')
    start=time.time()
    with log.open('w') as f:r=subprocess.run(command,cwd=ROOT,env=env(label),stdout=f,stderr=subprocess.STDOUT,timeout=600)
    save(label+'.json',dict(command=command,cwd=str(ROOT),candidate=snap['candidate'],environment=env(label),exit_code=r.returncode,seconds=time.time()-start,log_sha256=sha(log),tracked_unchanged=state(ROOT)==snap['tracked'],preflight_sha256=sha(OUT/'preflight.json')))
    print(label,r.returncode,log.read_text()[-1800:])
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='run':run(sys.argv[2],sys.argv[3:])
