from pathlib import Path
import subprocess,json,hashlib,os
from datetime import datetime,timezone
b=Path('/private/tmp/friday-mcp-upgrade/credential-cleanup');w=b/'work';root=Path('/Users/chuckrussell/Dev/gendev/agent-framework');out=b/'sec003-review';base='53df04a94d1085aa4f3b6de8dba0db254879c29c';candidate='494febf7d3eb128ec26b9f777428324cd939ce8e'
def git(cwd,*args):return subprocess.check_output(['git',*args],cwd=cwd,text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
a=json.loads((w/'docs/planning/active/friday-deprecated-credential-cleanup/authority-sec003.json').read_text())
require(a['base_commit']==base,'base mismatch');require(sha(w/a['directive'])==a['directive_sha256'],'directive mismatch')
require(git(w,'rev-parse','HEAD')==candidate,'candidate mismatch');require(not git(w,'status','--porcelain'),'candidate dirty');require(git(root,'rev-parse','HEAD')==candidate,'installed candidate mismatch')
changes=[line.split('\t',1) for line in git(w,'diff','--no-renames','--name-status',base+'..'+candidate).splitlines()]
removed={p for s,p in changes if s=='D'};require(len(removed)==287 and removed==set(a['allowed_index_removals']),'exact removal scope mismatch')
other=[(s,p) for s,p in changes if s!='D'];require(all(p=='.gitignore' or p in ['docs/planning/board.yaml','docs/planning/README.md'] or p.startswith('docs/planning/active/friday-deprecated-credential-cleanup/') for s,p in other),'scope drift')
for d in [w,root]:
 require(not git(d,'ls-files','--','tests/integration/memory'),'tracked memory descendants')
 for p in ['tests/integration/memory/new-hypothetical.txt','tests/integration/memory/deep/nested/new-hypothetical.txt']:
  ignored=git(d,'check-ignore','--no-index','-v',p);require('/tests/integration/memory/' in ignored,'ignore mismatch')
local=json.loads((b/'root-preservation-sec003/local-memory-files.json').read_text());require(set(local)==removed,'preservation inventory scope')
for p,expected in local.items():
 s=(root/p).stat();actual=dict(inode=s.st_ino,size=s.st_size,mtime_ns=s.st_mtime_ns,mode=s.st_mode);require(actual==expected,'local metadata mismatch: '+p)
hashes=json.loads((b/'root-preservation-sec003/hashes.json').read_text());preserved=[]
for p,expected in hashes.items():
 if p in ['docs/planning/board.yaml','docs/planning/README.md']:continue
 actual=sha(root/p) if (root/p).is_file() else None;require(actual==expected,'unrelated mismatch '+p);preserved.append(p)
require(not git(root,'diff','--cached','--name-only'),'unexpected staged differences')
receipts=[]
for label in ['compat-without-legacy','board','docs','render','whitespace']:
 folder=b/'sec003-checks'/label;r=json.loads((folder/'receipt.json').read_text());require(r['candidate']==candidate and r['exit_code']==0,'builder check failed/mismatch');require(r['private_legacy_directory_unavailable_during_test'] and r['private_directory_restored'],'unavailable/restored evidence mismatch');require(sha(folder/'stdout')==r['stdout_sha256'] and sha(folder/'stderr')==r['stderr_sha256'],'check output hash mismatch');require(r['product_before']==r['product_after'],'check product drift');receipts.append({'label':label,'receipt_sha256':sha(folder/'receipt.json'),'exit_code':0,'stdout':(folder/'stdout').read_text()})
# Board overlays were unrelated dirty changes. Compare all prior tasks except the explicitly updated initiative, and all pre-existing events.
import yaml
prior=yaml.safe_load((b/'root-preservation-sec003/board.yaml').read_text());now=yaml.safe_load((root/'docs/planning/board.yaml').read_text());prior_tasks={x['id']:x for x in prior['tasks']};now_tasks={x['id']:x for x in now['tasks']}
require(prior_tasks.keys()==now_tasks.keys(),'board task set drift')
for key in prior_tasks:
 if key!='friday-deprecated-credential-cleanup':require(prior_tasks[key]==now_tasks[key],'unrelated board task drift '+key)
require(all(x in now['events'] for x in prior['events']),'prior board events lost')
# All README edits must be exactly the directive's selected initiative next-gate update.
pread=(b/'root-preservation-sec003/README.md').read_text();nread=(root/'docs/planning/README.md').read_text();old='SEC-002 verified; confirm provider rotation and old-key invalidation; maintainer acceptance; local delivery only';new='SEC-003 independent review; local-file preservation required; credential rotation maintainer-confirmed';require(pread.replace(old,new)==nread,'unrelated README overlay drift')
result={'checked_at':datetime.now(timezone.utc).isoformat(),'base':base,'candidate':candidate,'authority_sha256':sha(w/'docs/planning/active/friday-deprecated-credential-cleanup/authority-sec003.json'),'directive_sha256':a['directive_sha256'],'gitignore_sha256':sha(w/'.gitignore'),'exact_index_removals':len(removed),'other_changes':other,'local_metadata_preserved':len(local),'unrelated_hashes_preserved':len(preserved),'intentional_board_readme_overlays_preserved':True,'builder_receipts_verified':receipts,'candidate_clean':True,'root_unrelated_dirty_expected':True,'network_guard_sha256':sha(Path('/private/tmp/friday-mcp-upgrade/guard/sitecustomize.py'))}
(out/'metadata.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['other_changes','builder_receipts_verified']},indent=2))
