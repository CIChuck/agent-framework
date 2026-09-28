import json
import os
import signal
import sys
import time

peer, mode, catalog_path = sys.argv[1:4]
catalog = json.load(open(catalog_path))
calls = 0
if mode.startswith('noisy'):
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
for line in sys.stdin:
    msg = json.loads(line)
    if 'id' not in msg:
        continue
    method = msg['method']
    if method == 'initialize':
        result = {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}}, 'serverInfo': {'name': peer, 'version': '1'}}
    elif method == 'tools/list':
        calls += 1
        result = {'tools': catalog}
    elif method == 'tools/call':
        result = {'content': [{'type': 'text', 'text': json.dumps({'peer': peer, 'name': msg['params']['name'], 'arguments': msg['params']['arguments'], 'list_calls': calls})}]}
    else:
        result = {}
    if mode == 'noisy_list_fail' and method == 'tools/list':
        reply = {'error': {'code': -1, 'message': 'VAL008-PEER-SENTINEL'}}
    else:
        reply = {'result': result}
    print(json.dumps({'jsonrpc': '2.0', 'id': msg['id'], **reply}), flush=True)
    if mode.startswith('noisy') and method == 'tools/list':
        for _ in range(400):
            os.write(sys.stdout.fileno(), b'VAL008-PEER-SENTINEL' + b'x' * 4096)
            os.write(sys.stderr.fileno(), b'VAL008-STDERR-SENTINEL' + b'y' * 4096)
        time.sleep(300)
