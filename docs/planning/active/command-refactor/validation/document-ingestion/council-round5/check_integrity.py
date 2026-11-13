from pathlib import Path
import hashlib,json,os,stat,subprocess,sys
request=Path(sys.argv[1]).resolve();q=json.loads(request.read_text());R=Path(q['workdir']);env=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();fail=[]
def git(*args):return subprocess.check_output(['git',*args],cwd=R,env=env)
logical=hashlib.sha256(git('ls-files','-s','-z')).hexdigest()
if logical!=q['logical_index_sha256']:fail.append('logical_index')
head=git('rev-parse','HEAD').decode().strip();branch=git('branch','--show-current').decode().strip()
if head!=q['candidate']:fail.append('HEAD')
if branch!=q['branch']:fail.append('branch')
if git('status','--porcelain=v1','--untracked-files=all').decode()!=q['status_porcelain_all']:fail.append('status')
if git('diff','--cached','--name-only'):fail.append('staged_diff')
for group in ['authority_pins','document_pins','source_pins']:
 for rel,h in q[group].items():
  if sha(R/rel)!=h:fail.append(group+':'+rel)
m=q['protected_manifest'];mp=Path(m['path'])
if sha(mp)!=m['sha256']:fail.append('manifest_hash')
protected=json.loads(mp.read_text())
for rel,v in protected.items():
 p=R/rel
 try:
  if v.get('kind')=='directory_symlink':
   link=os.readlink(p);good=p.is_symlink() and p.is_dir() and hashlib.sha256(link.encode()).hexdigest()==v['sha256'] and stat.S_IMODE(p.lstat().st_mode)==v['mode'] and link==v['link']
  else:good=sha(p)==v['sha256'] and stat.S_IMODE(p.stat().st_mode)==v['mode'] and (os.readlink(p) if p.is_symlink() else None)==v['link']
 except (FileNotFoundError,OSError):good=False
 if not good:fail.append('protected:'+rel)
pp=Path(q['preserved_state']['path'])
if sha(pp)!=q['preserved_state']['sha256']:fail.append('preserved_hash')
for rel,v in json.loads(pp.read_text()).items():
 p=R/rel;s=p.stat();got=dict(mode=s.st_mode,size=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns)
 if p.is_file():got['sha256']=sha(p)
 if got!=v:fail.append('preserved:'+rel)
for key in ('integrity_helper','command_wrapper'):
 if sha(Path(q[key]['path']))!=q[key]['sha256']:fail.append(key+'_hash')
print(json.dumps({'outcome':'PASS' if not fail else 'FAIL','request_sha256':sha(request),'candidate':head,'branch':branch,'logical_index_sha256':logical,'protected_entries':len(protected),'failures':fail},indent=2))
raise SystemExit(1 if fail else 0)
