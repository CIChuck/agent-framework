"""Isolated, guarded REM-004 execution. No original runtime state or synchronization."""
from pathlib import Path
import ast
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time

REPO=Path('/Users/chuckrussell/Dev/gendev/agent-framework')
OUT=Path('/private/tmp/telem-01/REM-004/approved-execution')
GUARD=Path('/private/tmp/telem-01/REM-001/network-guard')
PY=REPO/'.venv/bin/python'
UV=Path('/opt/homebrew/bin/uv')
PKT='docs/planning/active/friday-telemetry-rewire/'
ROOT_ARGS=['--import-mode=importlib','--ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py','--ignore=packages/friday-llm/tests_llm/test_live_lmstudio.py']
FOCUSED=['packages/friday-chat/tests_chat/'+p for p in ['test_telemetry.py','test_cli.py','test_runtime.py','test_app_lifecycle.py','compat/test_config_compatibility.py']]+['packages/friday-telemetry/tests_telemetry/test_providers.py']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args]).decode().strip()
def allowed():
    v=json.loads((REPO/PKT/'remediation/REM-004-scope.json').read_text())
    extra=['packages/friday-agent/tests_agent/conftest.py','packages/friday-runtime/tests_runtime/test_di.py','packages/friday-tools/tests_tools/test_filesystem_readers.py','packages/friday-tools/src/friday_tools/web/validators.py','packages/friday-tools/tests_tools/test_web_validators.py','packages/friday-tools/tests_tools/test_web_reader.py','packages/friday-chat/tests_chat/test_reorganization_terminal.py','packages/friday-core/tests_core/test_interfaces.py','packages/friday-cli/tests_cli/test_cancellation.py','packages/friday-memory/tests_memory/test_llm_completion.py','packages/friday-chat/tests_chat/test_llm_adapter_migration.py']
    return set(v['live_lint_files'])|set(extra)
def paths(root):
    names=subprocess.check_output(['git','-C',str(root),'ls-files','-z']).decode().split('\0')
    return {p:sha(root/p) if (root/p).is_file() else None for p in names if p}
def env(root,lane):
    tmp=OUT/'tmp'/root.name/lane;tmp.mkdir(parents=True,exist_ok=True)
    return dict(PATH=f'{REPO}/.venv/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin',
        UV_PROJECT_ENVIRONMENT=str(REPO/'.venv'),UV_CACHE_DIR='/private/tmp/friday-uv-cache',
        UV_NO_SYNC='true',UV_OFFLINE='true',UV_PYTHON_DOWNLOADS='never',
        LITELLM_LOCAL_MODEL_COST_MAP='true',ANONYMIZED_TELEMETRY='False',TERM='xterm-256color',
        PYTHONPATH=os.pathsep.join([str(GUARD)]+[str(p) for p in sorted((root/'packages').glob('*/src'))]+[str(root/'packages/friday-chat/tests_chat'),str(root)]),
        TMPDIR=str(tmp),PYTHONDONTWRITEBYTECODE='1',RUFF_CACHE_DIR=str(tmp/'ruff'),
        MYPY_CACHE_DIR=str(tmp/'mypy'),PYTEST_ADDOPTS=f'-o cache_dir={tmp}/pytest')
def prepare(name,overlay=False,tests_only=False,exclude_overlay=()):
    root=OUT/name
    if root.exists():raise RuntimeError('Use a fresh snapshot name; preserve earlier evidence')
    revision=git('rev-parse','HEAD')
    # Materialize committed code/evidence only; never copy tracked application data.
    omitted_roots=['tests/integration/memory/.friday/', 'tests/integration/memory/vector/',
        'tests/integration/memory/vector2_bak/', 'tests/integration/memory/vector_bak/',
        'tests/integration/memory/.doltcfg/', 'experiments/provider_memory_smoke/memory/']
    tracked=git('ls-tree','-r','--name-only',revision).splitlines()
    omitted=[p for p in tracked if any(p.startswith(prefix) for prefix in omitted_roots)
        or '.friday' in Path(p).parts or Path(p).name=='.env']
    if any(p.endswith(('.py','.toml','.yaml')) for p in omitted):
        raise RuntimeError('Protected-state omission intersects governed source/config; reconcile first')
    subprocess.run(['git','clone','--shared','--no-checkout','--quiet',str(REPO),str(root)],check=True)
    subprocess.run(['git','-C',str(root),'config','core.sparseCheckout','true'],check=True)
    subprocess.run(['git','-C',str(root),'config','core.sparseCheckoutCone','false'],check=True)
    (root/'.git/info/sparse-checkout').write_text('/*\n'+''.join('!/'+p+'\n' for p in omitted))
    subprocess.run(['git','-C',str(root),'checkout','--quiet','--detach',revision],check=True)
    if any((root/p).exists() for p in omitted):raise RuntimeError('Protected tracked state materialized')
    before=paths(root); selected=[]
    if overlay:
        for p in sorted(allowed()):
            if (tests_only and '/tests_' not in p) or p in exclude_overlay:continue
            if (REPO/p).read_bytes()!=(root/p).read_bytes():
                (root/p).write_bytes((REPO/p).read_bytes());selected.append(p)
    for lane in ['active','queued','review','blocked','deferred','backlog']:(root/'docs/planning'/lane).mkdir(exist_ok=True)
    if any((root/p).exists() for p in ['.env','.friday','chroma_db']):raise RuntimeError('Copied runtime state present')
    save(OUT/(name+'-snapshot.json'),dict(revision=revision,root=str(root),overlay=selected,excluded_overlay=list(exclude_overlay),tracked=paths(root),tracked_before_overlay=before,omitted_tracked_runtime_paths=omitted,guard_sha256=sha(GUARD/'sitecustomize.py')))
    print(root,revision,'overlay',len(selected),flush=True)
def run(name,label,args,timeout=300):
    root=OUT/name;record=json.loads((OUT/(name+'-snapshot.json')).read_text())
    if paths(root)!=record['tracked']:raise RuntimeError('Snapshot tracked contents changed before execution')
    if sha(GUARD/'sitecustomize.py')!='6f61ea4ca34c7abef9e0c709eb1e1feb0f3cf7733cbc59bc465d6b01182e9e81':raise RuntimeError('Guard changed')
    command=([str(UV),'run','--no-sync']+args[1:]) if args[0]=='uv' else ([str(PY)]+args[1:]) if args[0]=='python' else args
    e=env(root,label);folder=OUT/'runs'/name;folder.mkdir(parents=True,exist_ok=True);log=folder/(label+'.log')
    if log.exists():raise RuntimeError('Choose a new label; retain previous evidence')
    start=time.time()
    with log.open('w') as f: result=subprocess.run(command,cwd=root,env=e,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    save(folder/(label+'.json'),dict(command=command,cwd=str(root),revision=record['revision'],overlay=record['overlay'],snapshot_hash=sha(OUT/(name+'-snapshot.json')),environment=e,exit_code=result.returncode,seconds=time.time()-start,log_sha256=sha(log),tracked_unchanged=paths(root)==record['tracked']))
    if paths(root)!=record['tracked']:raise RuntimeError('Execution changed tracked snapshot')
    print(label,result.returncode,log,flush=True);print(log.read_text()[-3500:],flush=True)
    return result.returncode

if __name__=='__main__':
    mode=sys.argv[1];name=sys.argv[2]
    if mode=='prepare':prepare(name,'--overlay' in sys.argv[3:],'--tests-only' in sys.argv[3:], [x.split('=',1)[1] for x in sys.argv[3:] if x.startswith('--exclude-overlay=')])
    elif mode=='run':sys.exit(run(name,sys.argv[3],sys.argv[4:]))
    elif mode=='lists':
        names=git('diff','--name-only','2155a0f','HEAD','--','*.py').splitlines()
        source=[p for p in names if '/src/' in p]; owners=sorted({p.split('/')[1] for p in source})
        root=OUT/name
        save(OUT/(name+'-expanded.json'),dict(changed_python=names,sources=source,owning_packages=[str(t.relative_to(root)) for owner in owners for t in sorted((root/'packages'/owner).glob('tests_*')) if t.is_dir()],focused=FOCUSED,root_args=ROOT_ARGS))
    else:raise RuntimeError('Unknown mode')
