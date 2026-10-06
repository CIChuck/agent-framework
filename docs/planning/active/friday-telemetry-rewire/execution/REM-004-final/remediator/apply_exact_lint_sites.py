"""Apply reviewed REM-004 diagnostic sites; do not run broad unsafe Ruff fixes."""
from pathlib import Path
import ast,hashlib,json,re,textwrap
repo=Path('/Users/chuckrussell/Dev/gendev/agent-framework')
out=Path('/private/tmp/telem-01/REM-004/approved-execution/remediator')
scope=json.loads((repo/'docs/planning/active/friday-telemetry-rewire/remediation/REM-004-scope.json').read_text())
protected='packages/friday-cli/src/friday_cli/commands.py'
headers={
 'packages/friday-chat/src/friday_chat/memory_views.py':[('class MemoryMetric(Generic[T]):','class MemoryMetric[T]:')],
 'packages/friday-cli/src/friday_cli/session.py':[('class SessionContext(Generic[T]):','class SessionContext[T]:'),('class SessionManager(Generic[T]):','class SessionManager[T]:')],
 'packages/friday-core/src/friday_core/interfaces/tools.py':[('class ToolAdapter(Protocol, Generic[T]):','class ToolAdapter[T](Protocol):')],
 'packages/friday-moltbook/src/friday_moltbook/responses.py':[('class MoltbookResponse(BaseModel, Generic[T]):','class MoltbookResponse[T](BaseModel):')],
}
function_parameters={'_metric_text':'[T]','run_cancellable':'[T]','complete_structured_memory_request':'[ResponseModelT: BaseModel]','validate_return_type':'[T: BaseModel]'}
records=[]
for path,meta in scope['live_lint_files'].items():
 original=(repo/path).read_text()
 if hashlib.sha256(original.encode()).hexdigest()!=meta['sha256']:raise RuntimeError('Baseline drift: '+path)
 if path==protected:continue
 lines=original.splitlines(keepends=True);edits=[];diagnostics=[]
 for d in scope['root_ruff']['diagnostics']:
  if d['path']!=path:continue
  diagnostics.append(d)
  begin=sum(map(len,lines[:d['location']['row']-1]))+d['location']['column']-1
  end=sum(map(len,lines[:d['end_location']['row']-1]))+d['end_location']['column']-1
  site=original[begin:end];rule=d['code'];replacement=None
  if rule=='UP017':
   if site not in ['timezone.utc','dt.timezone.utc']:raise RuntimeError(site)
   replacement='dt.UTC' if site.startswith('dt.') else 'UTC'
  elif rule=='UP041':
   if site!='asyncio.TimeoutError':raise RuntimeError(site)
   replacement='TimeoutError'
  elif rule=='UP043':
   replacement=re.sub(r', None(?:, None)?\]$',']',site)
  elif rule=='UP035':
   if site!='from typing_extensions import Self':raise RuntimeError(site)
   replacement='from typing import Self'
  elif rule=='UP040':
   replacement=re.sub(r'^(\w+): TypeAlias =',r'type \1 =',site)
  elif rule=='UP047':
   name=site.split('(',1)[0]
   replacement=site.replace(name,name+function_parameters[name],1)
  elif rule=='E501':
   row=d['location']['row']-1;begin=sum(map(len,lines[:row]));end=begin+len(lines[row]);line=lines[row].rstrip('\n')
   replacement='\n'.join(textwrap.wrap(line,width=88,break_long_words=False,break_on_hyphens=False))+'\n'
  elif rule in ['I001','UP046']:continue
  else:raise RuntimeError('Unapproved rule '+rule)
  if replacement is not None:
   if replacement==site:raise RuntimeError('No transformation '+path+' '+rule)
   edits.append((begin,end,replacement))
 text=original
 for begin,end,replacement in sorted(edits,reverse=True):text=text[:begin]+replacement+text[end:]
 for before,after in headers.get(path,[]):
  if text.count(before)!=1:raise RuntimeError('Header mismatch '+path)
  text=text.replace(before,after,1)
 # Necessary imports only. Keep original module-global TypeVars/public names.
 tree=ast.parse(text);used={n.id for n in ast.walk(tree) if isinstance(n,ast.Name)}
 lines=text.splitlines(keepends=True);import_edits=[]
 for node in ast.walk(tree):
  if not isinstance(node,ast.ImportFrom) or node.module not in ['datetime','typing']:continue
  aliases=[a for a in node.names if a.name not in {'timezone','TypeAlias','Generic'} or (a.asname or a.name) in used]
  if node.module=='datetime' and 'UTC' in used and not any(a.name=='UTC' for a in aliases):aliases.append(ast.alias(name='UTC'))
  if len(aliases)==len(node.names) and all(a.name==b.name for a,b in zip(aliases,node.names)):continue
  start=sum(map(len,lines[:node.lineno-1]))+node.col_offset;end=sum(map(len,lines[:node.end_lineno-1]))+node.end_col_offset
  replacement=('from '+node.module+' import '+', '.join(a.name+((' as '+a.asname) if a.asname else '') for a in aliases)) if aliases else ''
  import_edits.append((start,end,replacement))
 for begin,end,replacement in sorted(import_edits,reverse=True):text=text[:begin]+replacement+text[end:]
 ast.parse(text,feature_version=(3,13))
 if text!=original:(repo/path).write_text(text)
 records.append({'path':path,'before_sha256':meta['sha256'],'after_sha256':hashlib.sha256(text.encode()).hexdigest(),'diagnostics':diagnostics,'notes':'Exact reviewed sites and necessary imports only; two original I001 sites left for pinned import sorting'})
assert hashlib.sha256((repo/protected).read_bytes()).hexdigest()==scope['live_lint_files'][protected]['sha256']
(out/'lint-site-transformations.json').write_text(json.dumps(records,indent=2)+'\n')
print('Reviewed files',len(records),'inventoried findings',sum(len(r['diagnostics']) for r in records),'protected invariant source unchanged')
