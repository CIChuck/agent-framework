# VAL-005 — Independent MCP-WS-02 Validation

**Overall outcome: CHANGES_REQUESTED**

**Decision status:** Superseded for the current candidate by REM-003 commit
`26f4d7d4bfd0514b6eb76bed71cb4797da91a067`; retained as historical findings.
Fresh VAL-006 delta and complete WS-02 aggregate validation is pending; no
verification or acceptance of the corrected candidate is claimed by this report.

Reviewer: fresh-context Codex validation agent `/root/mcp_ws02_val005`, GPT-6 family; exact deployment version unavailable.
Date: 2026-09-27.
Modes: full review and complete WS-02 work-unit aggregate review.
Candidate: `5a2856dea0f57208906fbd6eae5419d716bbf55a`.
Implementation range: `5c31f7c19f93d8b461dd90936e459ba9e28a4a5d..5a2856dea0f57208906fbd6eae5419d716bbf55a`.
Aggregate range: `a64e423cffca6162c43b8cfa193792508cf87fd6..5a2856dea0f57208906fbd6eae5419d716bbf55a`.

All required check groups completed. One high-severity ownership defect prevents verification.

## Authority, independence, and candidate stability

Read `AGENTS.md`, all thirteen pinned authority documents, the approved WS-02 directive and incorporated readiness amendment, current WS-00/01 contracts/configuration, candidate source/tests, and both selected diffs. Builder implementation documentation was inspected for documentation conformance; its conclusions were not used as review conclusions.

All thirteen authority SHA-256 values in `VAL-005-request.yaml` matched both candidate content and working files at the beginning and closeout.

HEAD initially was `547c49f8f241b777bf0dcfc616b1f776999654fd`; final HEAD was `fe7bd21d5c463caecd90a72a729230a9434f23f8`. The controller’s disclosed metadata commit changed only packet review-state metadata. Final candidate-to-HEAD differences were:

```text
M docs/planning/active/friday-mcp/README.md
M docs/planning/active/friday-mcp/execution-log.md
A docs/planning/active/friday-mcp/validation/VAL-005-request.yaml
```

`git diff --exit-code 5a2856dea0f57208906fbd6eae5419d716bbf55a -- packages tests pyproject.toml uv.lock` passed. Governed source, tests, configuration, and pinned authority remained frozen.

No parent sessions or builder private reasoning were inspected. No edits, repairs, staging, commits, board mutations, credential use, real service connections, or delivery operations occurred. Additional probes used in-process doubles or a local synthetic subprocess and explicitly cleaned their resources. The unrelated dirty-path manifest remained unchanged.

## Finding

### F-001 — High: Startup retry discards ownership after cleanup failure

**Affected source**

- `packages/friday-runtime/src/friday_runtime/mcp_loading.py:80` and `:90`
- `packages/friday-runtime/src/friday_runtime/di.py:105` and `:117`
- Public composition through `packages/friday-runtime/src/friday_runtime/kernel.py:101`

**Violated authority**

- WS-02 directive, MCP-02-02, lines 75–79: the manager must remain runtime-owned and reachable for diagnostics and shutdown.
- WS-02 directive, MCP-02-04, lines 102–104, and security requirement at line 153: preserve cleanup after partial startup.
- VAL-005 acceptance criteria MCP-02-02 and MCP-02-04, specifically “cleanup failures preserve ownership.”

**Observed defect**

A discovery failure followed by a disconnect failure correctly leaves the client in its manager. However, `_started` remains false, and the next `RuntimeMCPProvider.start()` assigns a new manager without first releasing the retained one.

The DI layer independently has the same problem: after failed boot, `_booted` remains false, and another `RuntimeKernel.start()` causes `DIContainer.boot()` to replace `mcp_provider`. The old provider and manager disappear from the runtime’s public cleanup path.

Independent provider-level probe:

```text
attempt 1 ToolProviderLoadError MCP shutdown incomplete
attempt 1 owned_names ['fake']
attempt 2 ToolProviderLoadError MCP shutdown incomplete
attempt 2 owned_names ['fake']
manager_replaced True
first_transport_still_connected True
first_client_owned_by_current_manager False
probe_cleanup_complete True
```

Independent public RuntimeKernel probe:

```text
kernel_attempt 1 ToolProviderLoadError MCP shutdown incomplete
kernel_attempt 2 ToolProviderLoadError MCP shutdown incomplete
kernel_provider_replaced True
first_transport_still_connected True
public_kernel_stop_left_first_client_connected True
probe_cleanup_complete True
```

The second probe allowed cleanup to succeed before calling public `kernel.stop()`. That stop cleaned the second provider only; the first client remained connected. Saved references were used solely to finish explicit probe cleanup.

**Risk**

Retrying startup after a cleanup error can orphan a live client, subprocess, or transport. Subsequent public shutdown cannot release that resource, and diagnostics cease to describe all runtime-owned resources.

**Required mitigation**

Preserve both ownership layers until retained clients have been successfully released. A retry may reuse the existing owner or reject/defer startup until cleanup succeeds; it must not replace an owner that still holds resources.

**Required regression coverage**

1. Provider startup fails during discovery and cleanup; retry preserves the original manager or fails without replacing it.
2. Kernel startup fails with cleanup failure; retry preserves the original provider or fails without replacing it.
3. Once cleanup can succeed, public shutdown releases every retained client without requiring saved/private references.
4. Include a successful peer alongside the failing client and verify draining, ownership, diagnostics, and eventual cleanup.
5. Preserve existing successful-start idempotence and cancellation behavior.

`test_manager_retains_failed_cleanup_for_retry` covers the manager itself, but does not exercise either replacing runtime layer.

**Documentation/configuration impact**

No configuration schema change is required. Update the implementation report’s cleanup/retry claims to match the corrected behavior and record the new candidate and regression evidence.

**Reproduction command**

This uses only in-process doubles. The state path is unused because storage construction is stubbed.

```bash
LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run python - <<'PY'
import asyncio
from unittest.mock import AsyncMock, patch
from friday_core.profiles import MemoryProfile
from friday_mcp.client.base import MCPClientBase
from friday_mcp.client.manager import MCPClientManager
from friday_runtime.config import RuntimeConfig, ToolsConfig
from friday_runtime.kernel import RuntimeKernel

class Transport:
    def __init__(self):
        self.is_connected = False
        self.fail_cleanup = True
    async def connect(self):
        self.is_connected = True
    async def disconnect(self):
        if self.fail_cleanup:
            raise RuntimeError("fake cleanup failure")
        self.is_connected = False
    async def send(self, message):
        pass
    async def receive(self):
        await asyncio.Future()

class Client(MCPClientBase):
    def __init__(self):
        super().__init__("fake")
        self.transport = Transport()
    async def _create_transport(self):
        return self.transport
    async def _initialize(self):
        pass
    async def list_tools(self):
        raise ValueError("fake discovery failure")

async def main():
    tools = ToolsConfig.from_dict({
        "providers": {"mcp": {"enabled": True, "config": {"servers": [{
            "name": "fake", "command": "fake", "retry_attempts": 0
        }]}}}
    })
    kernel = RuntimeKernel(RuntimeConfig(
        install_root=".",
        runtime_data_root="/private/tmp/friday-val005-unused-state",
        workspace_root=".", agents_dir=".", tools_config=tools
    ), MemoryProfile.TESTING)
    clients, providers = [], []

    def create(manager, config):
        client = Client()
        clients.append(client)
        return client

    try:
        with patch.object(MCPClientManager, "_create_client", create):
            with patch.multiple(
                kernel._di,
                _create_telemetry=lambda: None,
                _create_llm_services=lambda: None,
                _create_storage_adapters=AsyncMock(),
                _create_memory_controller=lambda: None,
                _create_multi_agent_stack=lambda: None,
                _create_context_engine=lambda: None,
            ):
                for attempt in (1, 2):
                    try:
                        await kernel.start()
                    except Exception as error:
                        print("kernel_attempt", attempt,
                              type(error).__name__, str(error))
                    providers.append(kernel.mcp_provider)
                print("kernel_provider_replaced",
                      providers[0] is not providers[1])
                print("first_transport_still_connected",
                      clients[0].transport.is_connected)
                for client in clients:
                    client.transport.fail_cleanup = False
                await kernel.stop()
                print("public_kernel_stop_left_first_client_connected",
                      clients[0].transport.is_connected)
    finally:
        for client in clients:
            client.transport.fail_cleanup = False
        for provider in providers:
            if provider is not None:
                await provider.stop()
        print("probe_cleanup_complete",
              all(not client.transport.is_connected for client in clients))

asyncio.run(main())
PY
```

## Acceptance evidence

| Criterion | Assessment and evidence |
| --- | --- |
| MCP-02-01 | Supported. Native registration stays synchronous in `tool_loading.py:25`; DI separately awaits MCP startup at `di.py:120`. The intentional unsupported error is removed. Native/disabled/empty-provider tests and local runtime integration pass. |
| MCP-02-02 | **Not satisfied: F-001.** Explicit non-global ownership and server-specific inputs exist in `mcp_loading.py:67–174`, with the public kernel accessor at `kernel.py:264`; retry can discard retained ownership. |
| MCP-02-03 | Supported. Discovery and admission finish before binding validation: `di.py:120`, `kernel.py:112–113`, and `mcp_loading.py:221–322`. Count/byte admission tests pass. The handoff is immutable, explicitly untrusted JSON with content excluded from representations. No executable MCP registry insertion occurs. Real binding validation rejects the unregistered MCP name after discovery. |
| MCP-02-04 | **Not satisfied: F-001.** Success, partial failure, handshake failure, EOF, and cancellation cleanup tests pass. Manager-level failed cleanup retains clients at `manager.py:81–89` and `:155–157`; runtime retries lose that ownership. |
| MCP-02-05 | Supported for reviewed failure paths. Optional/required connection and list failures are separately tested with doubles and local subprocesses. Disabled servers are excluded before manager construction. Failed tools never enter the registry. Cleanup failure is fatal rather than hidden. |
| MCP-02-06 | Supported. Effective connection/list deadline is `min(server.timeout_seconds, limits.connection_timeout_seconds)` at `mcp_loading.py:192–207`; retries share the connection deadline. Required/optional timeout cases, provider timeout caps, and configured RPC waits pass. |
| MCP-02-07 | Supported. Configured-size batches bound task creation at `mcp_loading.py:113–157`; cancellation drains workers before manager shutdown. Seven-server concurrency tests observe peaks of two for both connection and discovery. Local handshake/list cancellation tests reap their children. |
| MCP-02-08 | Supported. Typed fixed lifecycle outcomes distinguish disabled, connected, failures, timeout categories, cancellation, and cleanup failure. Discovery/diagnostic DTOs contain bounded identifiers, counters, and codes. Sentinel tests cover exception text, arguments, environment, stderr, and peer payload exclusion. |
| Cleanup/redaction amendment | Required ordinary-path tests pass: partial handshake/request/receiver cleanup, EOF, exited child, process-spawn cancellation, repeated disconnect, and captured-log redaction. Raw command/argument/stderr logs were removed; stderr is drained. F-001 remains a runtime ownership exception. |
| API/typing compatibility | Supported within scope. Runtime public startup signatures remain unchanged. Legacy manager boolean connect and unknown-server behavior have regressions. Broad ignores were removed from all three touched MCP modules; affected Python 3.13 mypy passes. No repository typing settings were weakened. |

WS-00/01 interaction remains coherent: the loader consumes the strict stdio-only runtime model, reuses shared limits/discovery/diagnostic contracts, revalidates workspace containment before connecting, and passes only server-specific protocol inputs. Core/MCP/runtime tests and downstream Chat configuration tests pass.

No prohibited registry, Chat turn, memory, transcript, telemetry-emitter, CLI, resources/prompts, server-exposure, live-refresh, or include implementation was found.

## Required command results

All `uv` commands used `UV_CACHE_DIR=/private/tmp/friday-uv-cache`. Pytest commands additionally used `LITELLM_LOCAL_MODEL_COST_MAP=true`.

| Command | Result |
| --- | --- |
| `uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime tests/integration/test_mcp_runtime_lifecycle.py -q` | **316 passed**, 11.36 s |
| `uv run pytest packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_llm_config_migration.py -q` | **46 passed**, 1.48 s |
| `uv run pytest tests/integration -q --tb=short` | **38 passed, 1 declared baseline failure**, 9.07 s |
| `uv run ruff check packages/friday-mcp packages/friday-runtime tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | Passed |
| `uv run mypy packages/friday-mcp packages/friday-runtime` | Declared baseline NumPy syntax failure; exit 2 |
| `uv run mypy --python-version 3.13 packages/friday-mcp packages/friday-runtime tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | Passed, 42 files |
| `uv run python scripts/friday-dev-board.py validate` | Passed, 23 tasks |
| `uv run python scripts/friday-dev-board.py render --check` | Passed |
| `uv run python scripts/check-documentation-lifecycle.py` | Passed, 328 Markdown files |
| `git diff --check 5c31f7c19f93d8b461dd90936e459ba9e28a4a5d..5a2856dea0f57208906fbd6eae5419d716bbf55a` | Passed |
| `git diff --check a64e423cffca6162c43b8cfa193792508cf87fd6..5a2856dea0f57208906fbd6eae5419d716bbf55a` | Passed |

Additional probes confirmed F-001 at provider and kernel levels and explicitly completed cleanup. A bounded local subprocess probe with paused noisy stdout completed transport cleanup and produced no additional finding. An initial kernel probe used overlapping runtime roots and was rejected by existing configuration validation before creating resources; the corrected probe above reproduced F-001.

## Baseline separation and residual limits

The integration failure is the unchanged assertion at `tests/integration/test_development_board.py:75` expecting 22 tasks. The accepted checkpoint already contains 23 tasks; the test is unchanged across the aggregate range.

Default mypy stops on installed NumPy `__init__.pyi:737`, which uses Python 3.12+ type syntax while unchanged `pyproject.toml:126` targets Python 3.10. The prescribed Python 3.13 check passes. Neither baseline issue is F-001 or a candidate regression.

This review establishes local deterministic lifecycle evidence only. Untrusted discovery data still requires WS-03 registration/filtering/sanitization work. No live SSE, provider interoperability, Chat execution, or full application UAT is claimed. Untouched legacy suppression debt remains outside the reviewed changes.

F-001 must be remediated in a new frozen candidate and independently reviewed before the WS-02 validation gate can pass. No completion, acceptance, or delivery authority follows from this report.
