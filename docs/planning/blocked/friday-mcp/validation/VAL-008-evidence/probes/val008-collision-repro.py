import asyncio
import contextlib
import io
import json
import val008_probes

async def main():
    captured=[]
    for kind in ('peer_collision','native_collision'):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            result=await val008_probes.real_case(kind)
        records=[json.loads(line) for line in output.getvalue().splitlines() if line.startswith('{')]
        collision=next(row for row in records if 'collision_kind' in row)
        captured.append(collision)
        print(json.dumps({'public_collision':collision,'cleanup_evidence':result}),flush=True)
    print('all_synthetic_tasks_and_processes_settled=True',flush=True)
    assert captured[0]['decisions'] != captured[1]['decisions'], 'MCP/MCP and MCP/native diagnostics are identical; both-source identity/provider labels are missing'

asyncio.run(main())
