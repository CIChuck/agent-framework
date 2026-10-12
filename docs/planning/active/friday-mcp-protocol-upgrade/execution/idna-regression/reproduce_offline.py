import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

out = Path('/private/tmp/friday-mcp-upgrade')
work = out / 'work'
(work / 'uv.lock').write_bytes((out / 'baseline/uv.lock').read_bytes())
environment = {'PATH': '/opt/homebrew/bin:/usr/bin:/bin', 'UV_CACHE_DIR': str(out / 'cache'), 'UV_PYTHON_DOWNLOADS': 'never', 'UV_NO_PROGRESS': '1'}
argv = ['/opt/homebrew/bin/uv', 'lock', '--offline', '--upgrade-package', 'idna==3.20', '--python', '/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python']
start = datetime.now(timezone.utc).isoformat()
proc = subprocess.run(argv, cwd=work, env=environment, capture_output=True)
for suffix, data in [('stdout', proc.stdout), ('stderr', proc.stderr)]:
    (out / ('approved-lock-reproduction.' + suffix)).write_bytes(data)
receipt = {'argv': argv, 'cwd': str(work), 'environment': environment, 'started_utc': start, 'finished_utc': datetime.now(timezone.utc).isoformat(), 'exit_code': proc.returncode, 'lock_sha256': hashlib.sha256((work / 'uv.lock').read_bytes()).hexdigest(), 'stdout_sha256': hashlib.sha256(proc.stdout).hexdigest(), 'stderr_sha256': hashlib.sha256(proc.stderr).hexdigest()}
(out / 'approved-lock-reproduction.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
if proc.returncode or receipt['lock_sha256'] != 'aab33ed773dcdb50a65dd86af84bd1e6e26dc3486da7b04588082d72a7b18ce2':
    raise RuntimeError('Approved lock reproduction failed or diverged')
