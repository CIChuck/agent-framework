import gzip
import hashlib
import itertools
import json
import tomllib
from pathlib import Path

from packaging.markers import Marker, default_environment

root = Path('/Users/chuckrussell/Dev/gendev/agent-framework')
out = Path('/private/tmp/friday-mcp-upgrade')
proposal = root / 'docs/planning/active/friday-mcp-protocol-upgrade/execution/dependency-conflict'
old = tomllib.loads((out / 'baseline/uv.lock').read_text())
new_bytes = gzip.decompress((proposal / 'proposed-uv.lock.gz').read_bytes())
new = tomllib.loads(new_bytes.decode())
old_names = {p['name'] for p in old['package']}

def active(marker, environment):
    return not marker or Marker(marker).evaluate(environment=environment)

def selected(doc, environment):
    result = {}
    for p in doc['package']:
        markers = p.get('resolution-markers', [])
        if markers and not any(active(m, environment) for m in markers):
            continue
        if p['name'] in result:
            raise RuntimeError(f"Ambiguous selection {p['name']}")
        result[p['name']] = p
    return result

def identity(p, normalize=False):
    version = '3.11' if normalize and p['name'] == 'idna' and p['version'] == '3.20' else p['version']
    return p['name'], version, json.dumps(p['source'], sort_keys=True)

def edges(p, selections, environment, normalize=False):
    sections = [('runtime', '', p.get('dependencies', []))]
    sections += [('optional', extra, deps) for extra, deps in p.get('optional-dependencies', {}).items()]
    sections += [('development', group, deps) for group, deps in p.get('dev-dependencies', {}).items()]
    result = set()
    for section, profile, deps in sections:
        env = {**environment, 'extra': profile if section == 'optional' else ''}
        for dep in deps:
            if dep['name'] not in old_names or not active(dep.get('marker'), env):
                continue
            target = selections.get(dep['name'])
            if target is None:
                raise RuntimeError(f"No target {dep['name']}")
            if dep.get('version') and dep['version'] != target['version']:
                raise RuntimeError(f"Wrong target {dep['name']}: {dep['version']} vs {target['version']}")
            result.add((section, profile, identity(target, normalize), tuple(dep.get('extra', []))))
    return result

contexts = []
for python, platform, arch in itertools.product(['3.13.4', '3.13.10', '3.14.0', '3.15.0'], ['darwin', 'linux', 'win32'], ['x86_64', 'arm64']):
    system = {'darwin': 'Darwin', 'linux': 'Linux', 'win32': 'Windows'}[platform]
    machine = 'aarch64' if platform == 'linux' and arch == 'arm64' else ('AMD64' if platform == 'win32' and arch == 'x86_64' else arch)
    env = {**default_environment(), 'python_full_version': python, 'python_version': '.'.join(python.split('.')[:2]), 'implementation_version': python, 'sys_platform': platform, 'platform_system': system, 'platform_machine': machine, 'os_name': 'nt' if platform == 'win32' else 'posix', 'extra': ''}
    a, b = selected(old, env), selected(new, env)
    before = {identity(p) for p in a.values()}
    after = {identity(p, True) for p in b.values() if p['name'] in old_names}
    if before != after:
        raise RuntimeError(f'Selection drift {env}: {before ^ after}')
    edge_count = 0
    added_edges = []
    for name, p in a.items():
        ea, eb = edges(p, a, env), edges(b[name], b, env, True)
        removed = ea - eb
        added = eb - ea
        allowed = name == 'friday-framework-mcp' and all(e[0] == 'runtime' and e[2][0] in {'jsonschema', 'referencing'} for e in added)
        if removed or (added and not allowed):
            raise RuntimeError(f'Existing edge drift {name}: {removed}, {added}')
        added_edges += [{'from': name, 'edge': list(e)} for e in sorted(added)]
        edge_count += len(ea)
    contexts.append({'python': python, 'platform': platform, 'architecture': machine, 'existing_selected_packages': len(a), 'existing_edges': edge_count, 'permitted_direct_edges': added_edges, 'preserved': True})
for p in old['package']:
    if p['name'] == 'idna':
        continue
    match = next(q for q in new['package'] if identity(q) == identity(p))
    for field in ['sdist', 'wheels']:
        if p.get(field) != match.get(field):
            raise RuntimeError(f'Artifact drift {p["name"]} {field}')
report = {'status': 'passed', 'baseline_lock_sha256': hashlib.sha256((out / 'baseline/uv.lock').read_bytes()).hexdigest(), 'approved_lock_sha256': hashlib.sha256(new_bytes).hexdigest(), 'existing_version_exception': {'idna': ['3.11', '3.20']}, 'contexts': contexts, 'all_other_existing_artifacts_preserved': True, 'limits': 'Static lock/marker/edge selection checks; not a runtime test on 24 machines. All original package selections and their existing runtime/extra/development edges are compared. New SDK packages are additional.'}
(out / 'context-preservation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'contexts': len(contexts), 'artifact_preservation': True}))
