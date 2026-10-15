# Friday Sandbox

Workspace management and interchangeable Docker, subprocess and mock execution backends for agent tools. Backend choice determines the isolation boundary.

**Distribution:** [friday-framework-sandbox](https://pypi.org/project/friday-framework-sandbox/) · **Import:** `friday_sandbox`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-sandbox==0.1.0a3"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: test without executing code

```python
import asyncio

from friday_sandbox import ExecutionResult, get_mock_sandbox

async def main() -> None:
    sandbox = get_mock_sandbox()()
    sandbox.set_response(ExecutionResult(stdout="Hello from a fixture", exit_code=0))
    result = await sandbox.execute("print('not actually executed')")
    print(result.stdout)

asyncio.run(main())
```

Expected output: `Hello from a fixture`. The mock records the request and returns the configured result; it does not execute the string or verify real isolation.

## Backends and ownership

| API | Purpose and prerequisites |
| --- | --- |
| `get_docker_sandbox()` | Returns the Docker backend class; needs the Docker SDK and an available daemon/image |
| `get_subprocess_sandbox()` | Returns the host subprocess backend class; runs with host process privileges |
| `get_mock_sandbox()` | Returns the configurable mock class for tests |
| `WorkspaceManager` | Creates, tracks and cleans application-owned workspaces |

The factory helpers return **classes**, not connected instances. Inspect the selected backend's constructor and lifecycle before use. Workspace TTL and cleanup policies manage files; they do not create an operating-system security boundary. Subprocess execution is not container isolation. Docker isolation still depends on image, mounts, capabilities, network and daemon configuration; do not describe any backend as safe for arbitrary hostile code by default.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
Run the focused suite:

```bash
uv run --no-sync pytest packages/friday-sandbox/tests_sandbox -q
```

## Documentation and support

[Execution tools](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-tools/README.md) · [Sandbox design and contracts](https://github.com/CIChuck/agent-framework/blob/master/docs/reference/specs/sandbox_specifications.md) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-sandbox/src/friday_sandbox) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).
