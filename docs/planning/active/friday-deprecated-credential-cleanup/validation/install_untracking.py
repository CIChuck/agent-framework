from pathlib import Path
import subprocess,json,hashlib,importlib.util,sys
root=Path('/Users/chuckrussell/Dev/gendev/agent-framework');b=Path('/private/tmp/friday-mcp-upgrade/credential-cleanup');private=b/'work';pres=b/'root-preservation-sec003';base='53df04a94d1085aa4f3b6de8dba0db254879c29c'
def git(*args,**kw):return subprocess.check_output(['git',*args],cwd=root,**kw)
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def statfile(f):
 s=f.stat();return {'inode':s.st_ino,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'mode':s.st_mode}
require(git('rev-parse','HEAD',text=True).strip()==base,'Root HEAD changed');require(git('branch','--show-current',text=True).strip()=='security/remove-deprecated-credentials','Wrong branch');require(not git('diff','--cached','--name-only'),'Unexpected staged changes')
local=json.loads((pres/'local-memory-files.json').read_text());hashes=json.loads((pres/'hashes.json').read_text())
def verify():
 for p,expected in local.items():require((root/p).exists() and statfile(root/p)==expected,'Local data changed: '+p)
 for p,expected in hashes.items():
  if p in {'docs/planning/board.yaml','docs/planning/README.md'}:continue
  actual=hashlib.sha256((root/p).read_bytes()).hexdigest() if (root/p).is_file() else None
  require(actual==expected,'Unrelated path changed: '+p)
verify()
for name in ['board.yaml','README.md']:require((root/'docs/planning'/name).read_bytes()==(pres/name).read_bytes(),'Board overlay changed')
candidate=subprocess.check_output(['git','rev-parse','HEAD'],cwd=private,text=True).strip();subprocess.run(['git','fetch','--no-tags',str(private),candidate],cwd=root,check=True,capture_output=True);require(subprocess.run(['git','merge-base','--is-ancestor',base,candidate],cwd=root).returncode==0,'Not a fast-forward')
changes=[line.split('\t',1) for line in git('diff','--no-renames','--name-status',base,candidate,text=True).splitlines()];removed={p for status,p in changes if status=='D'};require(removed==set(local),'Wrong removal scope')
allowed_prefix='docs/planning/active/friday-deprecated-credential-cleanup/'
for status,p in changes:
 require(p in removed or p in {'.gitignore','docs/planning/board.yaml','docs/planning/README.md'} or p.startswith(allowed_prefix),'Unexpected changed path '+p)
 if p in removed or p in {'docs/planning/board.yaml','docs/planning/README.md'}:continue
 old=subprocess.run(['git','show',base+':'+p],cwd=root,capture_output=True)
 require((root/p).read_bytes()==old.stdout if old.returncode==0 else not (root/p).exists(),'Target working file changed: '+p)
records=[]
for status,p in changes:
 if status=='D':records.append(b'0 '+b'0'*40+b'\t'+p.encode()+b'\0');continue
 meta=git('ls-tree',candidate,'--',p,text=True).split('\t',1)[0].split();records.append((meta[0]+' '+meta[2]+'\t'+p+'\0').encode());content=git('show',candidate+':'+p);dest=root/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
# Restore the unrelated planning overlay in the working tree only.
spec=importlib.util.spec_from_file_location('board_untrack_install',root/'scripts/friday-dev-board.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);board=m.load_board(root);overlay=json.loads((pres/'board-overlay.json').read_text());tasks={t['id']:t for t in board['tasks']};tasks.update(overlay['tasks']);board['tasks']=list(tasks.values())
for event in overlay['events']:
 if event not in board['events']:board['events'].append(event)
m._save_board_and_dashboard(board,root);require(not m.validate_board(m.load_board(root),root),'Installed board invalid');verify()
# Update only authorized changed index entries; no working-tree deletion/reset/merge.
subprocess.run(['git','update-index','-z','--index-info'],cwd=root,input=b''.join(records),check=True)
subprocess.run(['git','update-ref','refs/heads/security/remove-deprecated-credentials',candidate,base],cwd=root,check=True)
verify();require(not git('ls-files','--','tests/integration/memory'),'Memory remains tracked');require(not git('diff','--cached','--name-only'),'Unexpected index differences')
require(subprocess.run(['git','check-ignore','--no-index','tests/integration/memory/new-local-file.txt'],cwd=root,capture_output=True).returncode==0,'Folder not ignored')
receipt={'base':base,'installed_candidate':candidate,'local_memory_files_preserved':len(local),'verified_metadata':['inode','size','mtime_ns','mode'],'unrelated_paths_preserved':len(hashes),'tracked_memory_files':0,'memory_folder_ignored':True,'publication':'none','working_tree_deletion_operations':0};(b/'sec003-install-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
