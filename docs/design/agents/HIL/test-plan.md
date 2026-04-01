# HIL Test Plan

**Version:** 0.1
**Date:** 2026-03-29

---

## Overview

This plan covers four testing levels for the HIL package:

| Level | Scope | Location |
|-------|-------|----------|
| 1 | HIL package unit tests | `packages/friday-hil/tests_hil/` |
| 2 | friday-agent integration | `packages/friday-agent/tests_agent/test_hil_integration.py` |
| 3 | friday.py session integration | `tests/integration/memory/tests_hil/` |
| 4 | End-to-end via RuntimeKernel | `experiments/hil_smoke/` + regression in existing experiments |

**Design principles:**
- Levels 1–2 are fully automated (no TTY, no interactive prompts). All `prompt.py` calls use non-TTY auto-deny.
- Level 3 tests `MemoryChatSession._process_with_tools()` directly via import.
- Level 4 uses the established experiment harness pattern (`RuntimeKernel` + `DeterministicLLMClient`).
- Every level has a fast `pytest` entry point — no subprocess-only tests.

---

## Shared Helpers to Create

### `MockHILController` — lives in `packages/friday-hil/src/friday_hil/testing.py`

Public test-utilities module, importable as `from friday_hil.testing import MockHILController`. This follows the `django.test` pattern — test doubles ship with the package so that downstream consumers (package tests, experiments, integration tests) can import them without cross-boundary dependencies.

Used by Levels 1–4 to inject pre-configured HIL decisions without a real controller.

```python
"""
friday_hil.testing — Test doubles for the HIL package.

Import as: from friday_hil.testing import MockHILController
"""
from __future__ import annotations
from dataclasses import dataclass, field
from friday_hil.decision import HILDecision

@dataclass
class MockHILController:
    """Test double that satisfies `HILInterface` Protocol structurally.

    No subclassing or import of HILInterface needed — the Protocol is
    @runtime_checkable, so ``isinstance(MockHILController(), HILInterface)``
    returns True.  Records all calls; returns pre-configured decisions.
    """

    # Map tool_name → decision to return (default: allow/yolo_mode)
    decisions: dict[str, HILDecision] = field(default_factory=dict)
    default_decision: HILDecision = field(
        default_factory=lambda: HILDecision(allowed=True, reason="yolo_mode")
    )

    # Call log: list of (tool_name, tool_args, agent_id)
    calls: list[tuple[str, dict, str | None]] = field(default_factory=list)

    async def initialize(self) -> None:
        pass

    async def check_approval(
        self, tool_name: str, tool_args: dict, agent_id: str | None = None
    ) -> HILDecision:
        self.calls.append((tool_name, tool_args, agent_id))
        return self.decisions.get(tool_name, self.default_decision)

    # Inspection helpers
    def was_called_for(self, tool_name: str) -> bool:
        return any(c[0] == tool_name for c in self.calls)

    def call_count_for(self, tool_name: str) -> int:
        return sum(1 for c in self.calls if c[0] == tool_name)

    def agent_ids_seen(self) -> list[str | None]:
        return [c[2] for c in self.calls]
```

### `ToolCallLLMClient` — lives in `experiments/hil_smoke/fake_llm.py`

Extends the `DeterministicLLMClient` pattern to return tool calls, enabling controlled ReAct loops in tests.

```python
@dataclass
class ToolCallLLMClient:
    """LLM client that emits a scripted sequence of tool calls then a final text response."""

    # Each inner list is the tool_calls for one LLM turn.
    # After the sequence is exhausted, final_response is returned.
    tool_calls_sequence: list[list[dict]]
    final_response: str = "Task complete."
    _call_count: int = field(default=0, init=False)

    async def chat_completion(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        response_model=None,
        temperature: float = 0.7,
    ) -> ChatCompletionResponse:
        if self._call_count < len(self.tool_calls_sequence):
            calls = self.tool_calls_sequence[self._call_count]
            self._call_count += 1
            return ChatCompletionResponse(
                content=None,
                tool_calls=[ToolCall(**c) for c in calls],
                model="tool-call-llm",
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            )
        return ChatCompletionResponse(
            content=self.final_response,
            tool_calls=[],
            model="tool-call-llm",
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        )
```

---

## Level 1 — HIL Package Unit Tests

**Location:** `packages/friday-hil/tests_hil/`
**Pytest discovery:** Already in `packages/*/tests_*` testpath.
**Dependencies:** Only `friday-hil` and standard test deps. No `RuntimeKernel`, no `friday.py`.

### `conftest.py` (new)

```python
import pytest, pytest_asyncio, tempfile
from pathlib import Path
from friday_hil.config import HILConfig
from friday_hil.controller import HILController

@pytest.fixture
def tmp_db(tmp_path) -> Path:
    return tmp_path / "hil_audit.db"

@pytest.fixture
def yolo_config(tmp_db) -> HILConfig:
    return HILConfig.from_dict({"mode": "yolo", "audit": {"path": str(tmp_db)}})

@pytest.fixture
def strict_config(tmp_db) -> HILConfig:
    return HILConfig.from_dict({
        "mode": "strict",
        "safe_commands": ["grep", "ls"],
        "ask_once_commands": ["git"],
        "blocked_commands": ["rm"],
        "blocked_tools": ["danger_tool"],
        "exempt_tools": ["echo"],
        "audit": {"path": str(tmp_db)},
    })

@pytest_asyncio.fixture
async def yolo_controller(yolo_config) -> HILController:
    ctrl = HILController(yolo_config, session_id="test-session")
    await ctrl.initialize()
    return ctrl

@pytest_asyncio.fixture
async def strict_controller(strict_config) -> HILController:
    ctrl = HILController(strict_config, session_id="test-session")
    await ctrl.initialize()
    return ctrl
```

### `test_config.py`

| Test | Verifies |
|------|---------|
| `test_context_mode_override_resolves_effective_mode` | `context: interactive` + `context_modes.interactive: strict` → `mode == "strict"` |
| `test_base_mode_preserved_after_context_override` | `base_mode` always equals the raw YAML `mode` field |
| `test_defaults_when_keys_absent` | Missing all optional keys → sensible defaults (strict, interactive, empty lists) |
| `test_audit_path_coerced_to_path` | `audit.path` string → `Path` object |
| `test_blocked_tools_defaults_to_empty_list` | No `blocked_tools` key → `[]` |
| `test_from_dict_full_schema` | All fields parse correctly when all keys present |

### `test_audit.py`

| Test | Verifies |
|------|---------|
| `test_initialize_creates_db_and_table` | `initialize()` creates DB file + `hil_audit` table |
| `test_initialize_creates_compound_index` | `idx_hil_session_decision` index exists after init |
| `test_initialize_raises_on_bad_path` | Unwritable path raises `RuntimeError` when `enabled=True` |
| `test_initialize_noop_when_disabled` | `enabled=False` → no DB file created |
| `test_write_inserts_correct_columns` | Row inserted with `session_id`, `agent_id`, `decision`, `reason`, `context` |
| `test_write_context_uses_call_time_value` | `context` column = value passed to `write()`, not value from `__init__` |
| `test_write_silently_logs_on_failure` | Injected DB error → no exception raised, WARNING logged |
| `test_write_null_agent_id_for_direct_chat` | `agent_id=None` stored as SQL NULL |
| `test_read_recent_returns_correct_rows` | After 3 writes, `read_recent(session_id, 2)` returns 2 most recent rows as dicts |
| `test_read_recent_filters_by_session_id` | Rows from other sessions are not returned |
| `test_read_recent_returns_empty_when_disabled` | `enabled=False` → returns `[]` |

### `test_decision_chain.py`

All tests use `asyncio_mode = "auto"` (already configured globally). No real TTY — all prompt paths use monkeypatched non-TTY.

| Test | Rule | Verifies |
|------|------|---------|
| `test_rule1_exempt_tool_always_allowed` | 1 | `exempt_tools` → `reason=exempt_tool`, `allowed=True` |
| `test_rule2_blocked_tool_denied_in_yolo_mode` | 2 | `blocked_tools` beats yolo → `reason=blocked_tool`, `allowed=False` |
| `test_rule3_blocked_command_denied_in_yolo_mode` | 3 | First-word in `blocked_commands` beats yolo |
| `test_exempt_blocked_overlap_exempt_wins` | 1 | Tool in both lists → allowed, WARNING logged |
| `test_rule4_yolo_allows_unknown_tool` | 4 | Non-blocked tool in yolo → `reason=yolo_mode` |
| `test_rule5_safe_command_allowed_in_strict` | 5 | First-word in `safe_commands` → `reason=safe_command` |
| `test_rule6_trusted_hash_allows_after_option3` | 6 | Seed `trusted_command_hashes` → second call auto-allowed |
| `test_rule7_ask_once_command_auto_allows_second_call` | 7 | Seed `ask_once_approved` → `reason=ask_once_approved` |
| `test_agent_id_propagated_to_audit_write` | all | `agent_id` kwarg passed through to mocked `write()` |
| `test_nontty_auto_deny` | 8 | Monkeypatch `sys.stdin.isatty → False` → `reason=user_denied`, no hang (non-TTY path within prompt rule) |
| `test_debug_log_emitted_for_auto_allow` | 1–8 | `caplog` captures DEBUG entry for exempt/safe/yolo decisions |
| `test_audit_write_called_on_every_branch` | all | `_audit.write()` called exactly once per `check_approval()` call |
| `test_ask_once_option1_no_trust_state_change` | 8 | Option [1] approval does not populate `trusted_command_hashes` or `ask_once_approved` |
| `test_ask_once_option3_populates_both_stores` | 6,7 | Option [3] stores hash in `trusted_command_hashes` AND, for command tools with first-word in `ask_once_commands`, adds first-word to `ask_once_approved` |
| `test_ask_once_non_command_tool_exact_hash_only` | 6 | Non-command tool in `ask_once` mode: option [3] stores exact hash only; different args still prompt |

### `test_prompt.py`

| Test | Verifies |
|------|---------|
| `test_nontty_returns_deny` | `sys.stdin.isatty() = False` → returns `"2"` without blocking |
| `test_nontty_logs_warning` | Warning logged with tool name in non-TTY path |
| `test_import_uses_rich_directly` | `prompt.py` imports from `rich.*`, not from `friday_cli` |

---

## Level 2 — friday-agent Integration

**New file:** `packages/friday-agent/tests_agent/test_hil_integration.py`
**Pytest discovery:** Already in `packages/*/tests_*` testpath.

Uses existing `CopilotAgent` test fixture patterns from `test_copilot.py`. Adds a `mock_hil` fixture backed by `MockHILController`.

### Fixtures (in `test_hil_integration.py`)

```python
@pytest.fixture
def mock_hil_allow():
    """HIL that approves everything."""
    return MockHILController()   # default_decision = allowed/yolo_mode

@pytest.fixture
def mock_hil_deny_echo():
    """HIL that denies the 'echo' tool."""
    return MockHILController(
        decisions={"echo": HILDecision(allowed=False, reason="blocked_tool")}
    )

@pytest.fixture
def agent_with_hil(profile, mock_memory, mock_context_engine, mock_llm, tool_registry, mock_hil_allow):
    return CopilotAgent(
        profile=profile,
        memory=mock_memory,
        context_engine=mock_context_engine,
        llm=mock_llm,
        tool_registry=tool_registry,
        hil_controller=mock_hil_allow,
    )
```

### `class TestAgentBaseHIL`

| Test | Verifies |
|------|---------|
| `test_hil_gate_called_for_each_tool_call` | LLM requests tool → `check_approval()` called once with tool_name + args |
| `test_hil_allowed_tool_executes_normally` | `allowed=True` → tool callable invoked, result returned to LLM |
| `test_hil_denied_tool_not_executed` | `allowed=False` → tool callable never called, denial string returned |
| `test_hil_denial_message_contains_reason` | Denial string contains `decision.reason` |
| `test_hil_passes_agent_id` | `agent_id == profile.name` in all `check_approval()` calls |
| `test_hil_none_runs_normally` | `hil_controller=None` → no gate, existing behavior unchanged |
| `test_hil_multiple_tool_calls_all_checked` | LLM returns 2 tool calls → `check_approval()` called twice |
| `test_hil_deny_does_not_break_react_loop` | After denial, LLM receives denial as tool result and continues |

### `class TestOrchestratorHIL`

| Test | Verifies |
|------|---------|
| `test_orchestrator_stores_hil_controller` | `AgentOrchestrator(hil_controller=mock)` → `self._hil == mock` |
| `test_orchestrator_none_hil_propagates` | `hil_controller=None` propagates; agents' `_hil` is `None` |
| `test_runtime_kernel_factory_injects_hil` | `RuntimeKernel` factory methods (`_create_interactive_agent`, `_create_autonomous_agent`) pass `hil_controller=self._di.hil_controller` to agent constructor |

---

## Level 3 — friday.py Session Integration

**New directory:** `tests/integration/memory/tests_hil/`
**Pytest discovery:** Add `"tests/integration/memory/tests_hil"` to `testpaths` in root `pyproject.toml`.

Tests `MemoryChatSession._process_with_tools()` and `cmd_hil()` directly by importing from `friday.py`.

### `conftest.py`

```python
import sys
from pathlib import Path

# Make tests/integration/memory importable
INTEGRATION_ROOT = Path(__file__).resolve().parents[1]
if str(INTEGRATION_ROOT) not in sys.path:
    sys.path.insert(0, str(INTEGRATION_ROOT))
```

### `test_memory_chat_hil.py` — Fixtures

> **Note:** These fixtures use the real `MemoryChatSession` constructor signature. Minimal
> mocks are provided for every required parameter — check the current `MemoryChatSession.__init__()`
> if the signature evolves.

```python
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_hil():
    return MockHILController()

@pytest.fixture
def deny_hil():
    return MockHILController(
        decisions={"command_execute": HILDecision(allowed=False, reason="blocked_command")}
    )

@pytest.fixture
def mock_llm():
    """Minimal LiteLLMService stand-in."""
    return AsyncMock()

@pytest.fixture
def mock_controller():
    """Minimal MemoryController stand-in."""
    return AsyncMock()

@pytest.fixture
def mock_assembler():
    """Minimal ContextAssembler stand-in."""
    return AsyncMock()

@pytest.fixture
def mock_architect():
    """Minimal PromptArchitect stand-in."""
    return MagicMock()

@pytest.fixture
def session(mock_hil, mock_llm, mock_controller, mock_assembler, mock_architect):
    """MemoryChatSession with all heavy deps mocked and mock HIL injected."""
    from friday import MemoryChatSession
    sess = MemoryChatSession(
        controller=mock_controller,
        assembler=mock_assembler,
        architect=mock_architect,
        system_prompt="Test system prompt",
        session_id="test-session-hil",
        user_id="test-user",
        hil_controller=mock_hil,
    )
    return sess
```

### `class TestMemoryChatSessionHIL`

| Test | Verifies |
|------|---------|
| `test_hil_check_approval_called_before_tool_execution` | `_process_with_tools()` calls `check_approval()` before the tool runs |
| `test_allowed_tool_result_in_messages` | `allowed=True` → normal tool result appended to `working_messages` |
| `test_denied_tool_appended_as_tool_result` | `allowed=False` → denial content in `all_tool_results` and `working_messages` |
| `test_denied_tool_skips_execution` | Tool callable never invoked when HIL denies |
| `test_denied_tool_continue_preserves_message_structure` | Every tool_call entry has matching tool result (API contract) |
| `test_hil_agent_id_is_none_for_direct_chat` | `agent_id=None` passed to `check_approval()` in direct chat context |
| `test_hil_metadata_on_denied_result` | `MemoryToolResult.metadata["hil_denied"] == True` |

### `class TestCmdHil`

| Test | Verifies |
|------|---------|
| `test_cmd_hil_status_no_controller` | `_hil=None` → returns "HIL is not configured" message |
| `test_cmd_hil_status_shows_mode_and_context` | `status` subcommand returns mode, context, trust store sizes |
| `test_cmd_hil_mode_changes_effective_mode` | `mode yolo` → `_hil.config.mode == "yolo"` |
| `test_cmd_hil_context_re_resolves_mode` | `context semi_autonomous` → mode re-resolved from `context_modes` |
| `test_cmd_hil_clear_resets_trust_store` | `clear` → `session.trusted_command_hashes` is empty |
| `test_cmd_hil_audit_returns_session_records` | `audit 5` → returns string containing this session's records only |
| `test_cmd_hil_unknown_subcommand` | `hil bogus` → returns usage error string |

---

## Level 4 — End-to-End via RuntimeKernel

### 4a. New Experiment: `experiments/hil_smoke/`

Follows `experiments/agent_quality/` conventions exactly.

**Directory structure:**
```
experiments/hil_smoke/
├── __init__.py
├── README.md
├── agents/
│   └── hil_probe.yaml
├── config/
│   └── runtime.yaml              (copy from agent_quality, no changes needed)
├── fake_llm.py                   # ToolCallLLMClient (see Shared Helpers)
├── runtime.py                    # HilSmokeRuntime
├── run.py                        # CLI entry with --json flag
└── tests/
    ├── __init__.py
    └── test_hil_smoke.py
```

**Note:** `MockHILController` is imported from `friday_hil.testing`, not duplicated here.

**`agents/hil_probe.yaml`:**
```yaml
name: hil_probe
role: "HIL Probe"
goal: "Execute controlled tool calls to validate HIL approval gates."
system_prompt: "You are {name}, a {role}. Goal: {goal}. Execute the requested tool."
tools: [command_execute]
temperature: 0.0
llm_service: tool_call_llm
agent_type: interactive
tool_autonomy: manual
context_strategy: minimal
```

**`HilSmokeResult` dataclass:**
```python
@dataclass
class HilSmokeResult:
    success: bool
    scenario: str
    hil_calls: list[dict]      # {tool_name, allowed, reason, agent_id}
    final_response: str
    error: str | None = None

    def to_dict(self) -> dict: ...
```

**Scenario runner functions in `runtime.py`:**

```python
async def run_yolo_mode_scenario() -> HilSmokeResult
    # HIL config: mode=yolo
    # LLM: calls command_execute({"command": "ls ."})
    # Expected: decision.reason == "yolo_mode", tool executes

async def run_safe_command_scenario() -> HilSmokeResult
    # HIL config: mode=strict, safe_commands=["ls"]
    # LLM: calls command_execute({"command": "ls ."})
    # Expected: decision.reason == "safe_command", no prompt

async def run_blocked_command_scenario() -> HilSmokeResult
    # HIL config: mode=yolo, blocked_commands=["rm"]
    # LLM: calls command_execute({"command": "rm -rf /tmp/x"})
    # Expected: decision.reason == "blocked_command", denial to LLM, final_response = "Task complete"

async def run_blocked_tool_scenario() -> HilSmokeResult
    # HIL config: mode=yolo, blocked_tools=["command_execute"]
    # LLM: calls command_execute({"command": "ls ."})
    # Expected: decision.reason == "blocked_tool", beats yolo

async def run_exempt_tool_scenario() -> HilSmokeResult
    # HIL config: mode=strict, exempt_tools=["command_execute"]
    # LLM: calls command_execute({"command": "ls ."})
    # Expected: decision.reason == "exempt_tool", no prompt

async def run_nontty_strict_auto_deny_scenario() -> HilSmokeResult
    # HIL config: mode=strict, no safe/exempt rules for the tool used
    # LLM: calls command_execute({"command": "python run.py"})
    # Non-TTY env (CI) → auto-deny
    # Expected: decision.reason == "user_denied"

async def run_agent_id_attribution_scenario() -> HilSmokeResult
    # Uses AgentOrchestrator to route to hil_probe agent
    # LLM: calls command_execute
    # Expected: hil_call.agent_id == "hil_probe" (not None)

async def run_audit_db_populated_scenario() -> HilSmokeResult
    # Runs 3 tool calls (2 allowed, 1 denied)
    # After run: query SQLite audit DB
    # Expected: 3 rows, session_id consistent, decisions correct
```

**`test_hil_smoke.py`:**

| Test | Scenario | Verifies |
|------|----------|---------|
| `test_yolo_mode_allows_all_tools` | yolo | `reason == "yolo_mode"`, tool executes, no denial |
| `test_safe_command_bypasses_prompt` | safe_command | `reason == "safe_command"`, `allowed=True` |
| `test_blocked_command_denied_in_yolo` | blocked_command | `reason == "blocked_command"`, `allowed=False`, LLM gets denial |
| `test_blocked_tool_denied_in_yolo` | blocked_tool | `reason == "blocked_tool"`, beats yolo |
| `test_exempt_tool_always_allowed` | exempt_tool | `reason == "exempt_tool"`, strict mode |
| `test_nontty_auto_deny_in_strict` | nontty_strict | `reason == "user_denied"`, no hang |
| `test_agent_id_set_for_orchestrated_agent` | agent_id | `hil_call["agent_id"] == "hil_probe"` |
| `test_audit_db_has_correct_row_count` | audit_db | 3 rows after 3 calls |
| `test_audit_db_session_id_consistent` | audit_db | All rows share same `session_id` |
| `test_audit_db_decision_reasons_correct` | audit_db | Allowed/denied reasons match expected |

---

### 4b. Regression Tests in Existing Experiments

Add `test_hil_regression.py` to each existing experiment's `tests/` directory. These verify that **HIL in yolo mode does not change existing experiment outcomes**.

#### `experiments/agent_quality/tests/test_hil_regression.py`

```python
@pytest.mark.asyncio
async def test_agent_quality_unaffected_by_hil_yolo():
    """Agent quality experiment produces identical result with HIL in yolo mode."""
    result = await run_agent_quality_experiment(hil_mode="yolo")

    assert result.success is True
    assert result.response == DEFAULT_RESPONSE
    assert result.hil_enabled is True
    assert result.hil_decisions_count >= 0   # may be 0 if no tool calls
```

Requires adding `hil_mode: str = "disabled"` parameter to `run_agent_quality_experiment()` and `hil_enabled: bool` + `hil_decisions_count: int` fields to `AgentQualityExperimentResult`.

#### `experiments/workflow_artifact_smoke/tests/test_hil_regression.py`

```python
@pytest.mark.asyncio
async def test_workflow_pipeline_unaffected_by_hil_yolo():
    """Workflow artifact pipeline completes with HIL in yolo mode."""
    result = await run_workflow_artifact_smoke_experiment(hil_mode="yolo")

    assert result.success is True
    assert result.artifact_published is True
    assert result.hil_enabled is True
```

Requires similar additive changes to the workflow experiment runtime.

---

## Pytest Configuration Changes

### `pyproject.toml` — add Level 3 testpath

```toml
[tool.pytest.ini_options]
testpaths = [
    "packages/*/tests_*",
    "experiments/*/tests",
    "tests/integration/memory/tests_hil",   # ADD THIS
]
```

### `packages/friday-hil/pyproject.toml` — add pytest-asyncio

```toml
[project.optional-dependencies]
test = ["pytest>=8.0.0", "pytest-asyncio>=0.23.0"]
```

---

## Test Execution Matrix

```bash
# Level 1 — HIL package unit tests
pytest packages/friday-hil/tests_hil/ -v

# Level 2 — Agent framework integration
pytest packages/friday-agent/tests_agent/test_hil_integration.py -v

# Level 3 — friday.py session integration
pytest tests/integration/memory/tests_hil/ -v

# Level 4a — HIL smoke experiment
pytest experiments/hil_smoke/tests/ -v

# Level 4b — Experiment regressions
pytest experiments/agent_quality/tests/test_hil_regression.py -v
pytest experiments/workflow_artifact_smoke/tests/test_hil_regression.py -v

# Full HIL test sweep
pytest packages/friday-hil/tests_hil/ \
       packages/friday-agent/tests_agent/test_hil_integration.py \
       tests/integration/memory/tests_hil/ \
       experiments/hil_smoke/tests/ \
       experiments/agent_quality/tests/test_hil_regression.py \
       experiments/workflow_artifact_smoke/tests/test_hil_regression.py \
       -v --tb=short
```

---

## Build Order

The tests depend on HIL implementation phases from `build-plan.md`. Build order within the test plan:

1. **`friday_hil/testing.py` (MockHILController)** — created during Phase 8 (package exports); **`ToolCallLLMClient`** — created during Level 4 setup
2. **`packages/friday-hil/tests_hil/conftest.py`** + all 4 unit test files
3. **`packages/friday-agent/tests_agent/test_hil_integration.py`** — after Phase 9–10 of build-plan
4. **`tests/integration/memory/tests_hil/`** — after Phase 13–15 of build-plan
5. **`experiments/hil_smoke/`** — full experiment scaffold, after all build phases
6. **Regression test files** in existing experiments — additive changes only
