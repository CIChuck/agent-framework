import ast,json,gzip,pathlib,hashlib,re,subprocess,collections
p=pathlib.Path('docs/planning/active/command-refactor/validation/document-ingestion/product-construction'); H=lambda b:hashlib.sha256(b).hexdigest();errors=[]
m=json.loads((p/'phase-evidence-map.json').read_text());rem=pathlib.Path('docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md').read_text();defs=dict(re.findall(r'^\| (DI-\d+) \| (.*?) \|$',rem,re.M));ex={x['id']:x for x in m['exit_assertions']}
for r in m['requirements']:
 if defs[r['id']]!=r['parent_definition'] or H(defs[r['id']].encode())!=r['parent_definition_sha256']:errors.append(('DI',r['id']))
 for e in r['scoped_exit_references']:
  if r['id'] not in ex[e]['traces_requirements']: errors.append(('join',r['id'],e))
for e in ex.values():
 for rid in e['traces_requirements']:
  if e['id'] not in next(r for r in m['requirements'] if r['id']==rid)['scoped_exit_references']:errors.append(('reverse',e['id'],rid))
groups=[r for g in m['proof_groups'] for r in g['requirements']];assert len(groups)==36 and set(groups)==set(defs)
seen=set()
for phase in m['phases']:
 assert set(phase['requires'])<=seen;seen.add(phase['id'])
annex=pathlib.Path('docs/planning/active/command-refactor/embedding-compatibility-contract.md').read_text();named=re.findall(r'^\| (FC-\d+) \| `(test_\w+)`',annex,re.M); actual=[(f['id'],w['node'].split('::')[-1]) for f in m['compatibility_requirements'] for w in f['named_witnesses']];assert set(named)==set(actual) and len(actual)==19
v=json.loads(gzip.decompress((p/'baseline-test-inventory.json.gz').read_bytes())); nodecount=0
for module in v['modules']:
 b=pathlib.Path(module['path']).read_bytes();assert H(b)==module['sha256'];tree=ast.parse(b); found={}
 def walk(node,parents=()):
  for n in ast.iter_child_nodes(node):
   if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_'): found['::'.join(parents+(n.name,))]=n
   if isinstance(n,ast.ClassDef):walk(n,parents+(n.name,))
 walk(tree)
 for n in module['static_base_nodes']:
  a=found[n['node']];assert a.lineno==n['line'];assert H(ast.dump(a,include_attributes=False).encode())==n['definition_sha256'];nodecount+=1
 assert set(found)=={n['node'] for n in module['static_base_nodes']}
for f in v['fixtures_and_conftests']:assert H(pathlib.Path(f['path']).read_bytes())==f['sha256']
h=json.loads((p/'baseline-helper-inventory.json').read_text());assert all(H(pathlib.Path(x['path']).read_bytes())==x['sha256'] for x in h['helpers'])
seed=json.loads((p/'test-migration-seed.json').read_text())
for s in seed['entries']:
 mod=next(x for x in v['modules'] if x['path']==s['old_path']);n=next(x for x in mod['static_base_nodes'] if x['node']==s['old_node']);assert n['definition_sha256']==s['old_definition_sha256'] and mod['sha256']==s['old_file_sha256']
result=dict(errors=errors,DI=len(defs),proof_groups=len(m['proof_groups']),exits=len(ex),FC=len(m['compatibility_requirements']),named_FC=len(actual),modules=len(v['modules']),AST_nodes=nodecount,fixtures=len(v['fixtures_and_conftests']),helpers=len(h['helpers']),seed_nodes=len(seed['entries']))
print(json.dumps(result,indent=2))
pathlib.Path('/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/astra-r3-seat-5p7txfct/static-audit.json').write_text(json.dumps(result,indent=2))
