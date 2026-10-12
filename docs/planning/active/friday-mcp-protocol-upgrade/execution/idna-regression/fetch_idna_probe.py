import gzip
import hashlib
import json
import tomllib
import urllib.request
import zipfile
from pathlib import Path

root = Path('/Users/chuckrussell/Dev/gendev/agent-framework')
out = Path('/private/tmp/friday-mcp-upgrade/idna-probe')
out.mkdir(exist_ok=True)
lock = tomllib.loads(gzip.decompress((root / 'docs/planning/active/friday-mcp-protocol-upgrade/execution/dependency-conflict/proposed-uv.lock.gz').read_bytes()).decode())
artifact = next(p for p in lock['package'] if p['name'] == 'idna')['wheels'][0]
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
with opener.open(artifact['url'], timeout=30) as response:
    data = response.read(1024 * 1024)
expected = artifact['hash'].removeprefix('sha256:')
if hashlib.sha256(data).hexdigest() != expected or len(data) != artifact['size']:
    raise RuntimeError('Wheel artifact mismatch')
wheel = out / 'idna-3.20-py3-none-any.whl'
wheel.write_bytes(data)
with zipfile.ZipFile(wheel) as archive:
    for name in archive.namelist():
        if name.startswith('/') or '..' in Path(name).parts:
            raise RuntimeError('Unsafe archive path')
    archive.extractall(out / '3.20')
history_url = 'https://raw.githubusercontent.com/kjd/idna/v3.20/HISTORY.md'
with opener.open(history_url, timeout=30) as response:
    history = response.read(1024 * 1024)
(out / 'HISTORY-3.20.md').write_bytes(history)
receipt = {'artifact_url': artifact['url'], 'artifact_sha256': expected, 'bytes': len(data), 'history_url': history_url, 'history_sha256': hashlib.sha256(history).hexdigest(), 'effects': 'Public pinned wheel and release-history download only. Extracted to private probe directory; shared environment unchanged.'}
(out / 'artifact-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
