import pathlib,json,gzip,hashlib,tarfile
p=pathlib.Path('docs/planning/active/command-refactor/validation/document-ingestion/gate-a');H=lambda b:hashlib.sha256(b).hexdigest();out=[]
for d,idx,arc in [('behavior-evaluation','evidence-index.json','behavior-evidence.tar.gz'),('end-to-end-evaluation','evidence-index.json','evidence.tar.gz'),('large-documents','evidence-index-v2.json','evidence-v2.tar.gz')]:
 r=p/d;v=json.loads((r/idx).read_bytes());expected=v.get('archive_sha256') or v['archive']['sha256'];assert H((r/arc).read_bytes())==expected
 if d=='behavior-evaluation':
  b=(r/v['index']['path']).read_bytes();assert H(b)==v['index']['sha256'];raw=gzip.decompress(b);assert H(raw)==v['index']['raw_sha256'];members=json.loads(raw)
 else:members=v['members']
 lookup={x['path']:x for x in members};seen=set()
 with tarfile.open(r/arc,'r|gz') as tar:
  for m in tar:
   if not m.isfile():continue
   assert m.name in lookup,m.name
   b=tar.extractfile(m).read();e=lookup[m.name];assert len(b)==e['size'] and H(b)==e['sha256'],m.name;assert m.name not in seen;seen.add(m.name)
 assert seen==set(lookup)
 out.append(dict(archive=str(r/arc),sha256=expected,verified_members=len(seen),payload_execution=False))
print(json.dumps(out,indent=2));pathlib.Path('/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/astra-r3-seat-5p7txfct/archive-audit.json').write_text(json.dumps(out,indent=2))
