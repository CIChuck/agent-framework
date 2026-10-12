import hashlib
import json
import os
import socket
import subprocess
import sys
import warnings
from pathlib import Path

out = Path('/private/tmp/friday-mcp-upgrade/idna-probe')
if len(sys.argv) > 1:
    version = sys.argv[1]
    if version == '3.20':
        sys.path.insert(0, str(out / '3.20'))
    def denied(*args, **kwargs):
        raise RuntimeError('Network prohibited in IDNA regression probe')
    socket.getaddrinfo = denied
    socket.socket.connect = denied
    socket.socket.connect_ex = denied
    socket.socket.sendto = denied
    import idna
    import idna.codec
    import httpx
    import requests
    from yarl import URL
    if idna.__version__ != version:
        raise RuntimeError(f'Wrong probe dependency: {idna.__version__}')
    domains = [
        'example.com', 'EXAMPLE.COM', 'localhost', 'localhost.', '127.0.0.1',
        'mcp.example.com', 'xn--bcher-kva.example', 'bücher.example',
        'faß.example', 'Königsgäßchen.example', '例え.テスト', 'παράδειγμα.δοκιμή',
        'مثال.إختبار', 'пример.испытание', 'café.example', 'cafe\u0301.example',
        'fullwidth。example', 'ＦＲＩＤＡＹ.example', 'example.com.',
        'a_b.example', '_service.example', 'a!b.example', 'a b.example',
        '-bad.example', 'bad-.example', 'a..example', '.example', '',
        'xn--', 'xn--abc-.example', 'xn--bcher-kva-.example',
        'xn--BCHER-KVA.example', 'xn--fa-hia.example',
        'a' * 63 + '.example', 'a' * 64 + '.example',
        '.'.join(['a' * 63] * 4), 'a' * 1024, 'a' * 1025,
        'a\u200cb.example', 'a\u200db.example', 'aא.example',
        '💻.example', '\ud800.example', '\ua7f1.example',
    ]
    rows = []
    for index, domain in enumerate(domains):
        operations = {
            'encode-strict': lambda: idna.encode(domain).decode(),
            'encode-uts46': lambda: idna.encode(domain, uts46=True).decode(),
            'decode': lambda: idna.decode(domain),
            'remap-default': lambda: idna.uts46_remap(domain),
            'httpx-url': lambda: str(httpx.URL('https://' + domain + '/probe')),
            'requests-url': lambda: requests.Request('GET', 'https://' + domain + '/probe').prepare().url,
            'yarl-url': lambda: str(URL('https://' + domain + '/probe')),
            'incremental-encode': lambda: idna.codec.IncrementalEncoder().encode(domain, final=True).decode(),
        }
        for operation, call in operations.items():
            with warnings.catch_warnings(record=True) as seen:
                warnings.simplefilter('always')
                try:
                    value = {'status': 'ok', 'value': call()}
                except Exception as exc:
                    value = {'status': 'error', 'exception': type(exc).__name__, 'message': str(exc)}
            rows.append({'case': index, 'operation': operation, 'hostname': domain, **value, 'warnings': [type(w.message).__name__ for w in seen]})
    (out / (version + '-results.json')).write_text(json.dumps({'idna': version, 'idna_source': idna.__file__, 'cases': rows}, indent=2) + '\n')
    print(json.dumps({'idna': version, 'checks': len(rows), 'network': 'prohibited'}))
    sys.exit(0)

receipts = []
for version in ['3.11', '3.20']:
    argv = [sys.executable, str(Path(__file__)), version]
    environment = {'PATH': '/opt/homebrew/bin:/usr/bin:/bin', 'PYTHONHASHSEED': '0', 'PYTHONDONTWRITEBYTECODE': '1'}
    proc = subprocess.run(argv, env=environment, cwd=out, capture_output=True, timeout=30)
    (out / (version + '.stdout')).write_bytes(proc.stdout)
    (out / (version + '.stderr')).write_bytes(proc.stderr)
    receipts.append({'argv': argv, 'environment': environment, 'exit_code': proc.returncode, 'stdout_sha256': hashlib.sha256(proc.stdout).hexdigest(), 'stderr_sha256': hashlib.sha256(proc.stderr).hexdigest()})
    if proc.returncode:
        raise RuntimeError(f'{version} probe failed: {proc.stderr.decode()}')
before = json.loads((out / '3.11-results.json').read_text())['cases']
after = json.loads((out / '3.20-results.json').read_text())['cases']
differences = []
semantic_differences = []
valid_consumer_changes = []
for a, b in zip(before, after, strict=True):
    if a != b:
        item = {'case': a['case'], 'operation': a['operation'], 'hostname': a['hostname'], 'before': {k: v for k,v in a.items() if k not in ['case', 'operation', 'hostname']}, 'after': {k: v for k,v in b.items() if k not in ['case', 'operation', 'hostname']}}
        differences.append(item)
        semantic = a['status'] != b['status'] or (a['status'] == 'ok' and a['value'] != b['value'])
        if semantic:
            semantic_differences.append(item)
            if a['case'] <= 18 and a['operation'] in ['httpx-url', 'requests-url', 'yarl-url']:
                valid_consumer_changes.append(item)
report = {'status': 'passed' if not valid_consumer_changes else 'regression', 'checks_per_version': len(before), 'valid_hostname_consumer_checks': 19 * 3, 'valid_hostname_consumer_changes': valid_consumer_changes, 'semantic_differences': semantic_differences, 'all_differences': differences, 'commands': receipts, 'scope': 'Offline synthetic IDNA encoding/decoding/remapping/codec and existing HTTPX/Requests/YARL URL construction; no DNS, requests, SDK execution, product tests or full construction verification.'}
(out / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'checks_per_version': len(before), 'valid_consumer_changes': len(valid_consumer_changes), 'semantic_differences': len(semantic_differences), 'all_differences': len(differences)}))
for d in semantic_differences:
    host = d['hostname'] if len(d['hostname']) < 80 else f"[{len(d['hostname'])} characters]"
    print(json.dumps({'hostname': host, 'operation': d['operation'], 'before': d['before'], 'after': d['after']}))
if valid_consumer_changes:
    raise RuntimeError('Valid consumer hostname regression')
