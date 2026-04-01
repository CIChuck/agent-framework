# HIL Build Plan

**Version:** 0.1
**Date:** 2026-03-29
**Status:** Ready for implementation

---

## Context

The PRD defines a HIL approval system that will evolve toward Beads (task queue) and Dolt (version-controlled DB) integration. HIL intercepts tool calls across both `MemoryChatSession._process_with_tools()` and the `friday-agent` ReAct loop (`AgentBase._execute_tool_call()`). A standalone `friday-hil` package avoids circular deps and follows the existing `friday-llm` → `LLMClient` pattern.

**Canonical design docs (read before implementing):**
- `docs/design/agents/HIL/design.md` — architecture, decision chain, integration points
- `docs/design/agents/HIL/config-reference.md` — full YAML schema, mode table, reason codes

---

## Dependency Architecture

```
friday-core  (HILInterface + HILDecision ABCs in interfaces/hil.py)
     ↓              ↓
friday-agent    friday-hil  (implements HILInterface; deps: friday-core + aiosqlite + rich)
     ↓              ↓
     (wired together in friday.py / app layer)
```

Single `HILController` instance shared across `MemoryChatSession` and `AgentOrchestrator` → unified session trust store.

---

## Specification Reference

> These signatures are the authoritative spec. Use them exactly — do not rename parameters or reorder arguments.

### `HILDecision` + `HILInterface` Protocols (`friday-core`)
```python
@runtime_checkable
class HILDecision(Protocol):
    """Structural type — enforced by mypy and isinstance(), not ABC machinery."""
    allowed: bool
    reason: str
    display_command: str | None

@runtime_checkable
class HILInterface(Protocol):
    """Structural type for approval gates. Consistent with tools.py pattern."""
    async def initialize(self) -> None: ...

    async def check_approval(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        agent_id: str | None = None,   # AgentBase.profile.name or None for direct chat
    ) -> HILDecision: ...
```

### `HILConfig` (`config.py`)
```python
@dataclass
class HILConfig:
    enabled: bool = True
    mode: Literal["yolo", "strict", "ask_once"] = "strict"
    base_mode: str = "strict"           # original `mode` before context overrides; NOT a YAML key
    context: str = "interactive"
    context_modes: dict[str, str] = field(default_factory=dict)
    exempt_tools: list[str] = field(default_factory=list)
    blocked_tools: list[str] = field(default_factory=list)
    safe_commands: list[str] = field(default_factory=list)
    ask_once_commands: list[str] = field(default_factory=list)
    blocked_commands: list[str] = field(default_factory=list)
    audit_enabled: bool = True
    audit_path: Path = field(default_factory=lambda: Path("./logs/hil_audit.db"))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HILConfig":
        audit = data.get("audit", {})
        context = data.get("context", "interactive")
        context_modes = data.get("context_modes", {})
        base_mode = data.get("mode", "strict")
        effective_mode = context_modes.get(context, base_mode)
        return cls(
            enabled=data.get("enabled", True),
            mode=effective_mode,
            base_mode=base_mode,
            context=context,
            context_modes=context_modes,
            exempt_tools=data.get("exempt_tools", []),
            blocked_tools=data.get("blocked_tools", []),
            safe_commands=data.get("safe_commands", []),
            ask_once_commands=data.get("ask_once_commands", []),
            blocked_commands=data.get("blocked_commands", []),
            audit_enabled=audit.get("enabled", True),
            audit_path=Path(audit.get("path", "./logs/hil_audit.db")),
        )
```

### `HILSession` (`session.py`)
```python
@dataclass
class HILSession:
    trusted_command_hashes: dict[str, datetime] = field(default_factory=dict)
    ask_once_approved: set[str] = field(default_factory=set)
```

### `HILDecision` concrete (`decision.py`)
```python
@dataclass
class HILDecision(HILDecisionABC):
    allowed: bool
    reason: Literal[
        "exempt_tool", "blocked_tool", "blocked_command", "safe_command",
        "yolo_mode", "trusted_hash", "ask_once_approved",
        "user_approved_once", "user_approved_always", "user_denied",
    ]
    display_command: str | None = None
```

### `HILAuditWriter` (`audit.py`)
```python
class HILAuditWriter:
    def __init__(self, db_path: Path, enabled: bool, context: str) -> None: ...

    async def initialize(self) -> None:
        """Open DB, enable WAL, CREATE TABLE + INDEX. Raises RuntimeError on bad path when enabled=True."""

    async def write(
        self,
        session_id: str,
        agent_id: str | None,
        tool_name: str,
        command: str | None,
        context: str,           # current context at decision time — NOT stored context from __init__
        decision: HILDecision,
    ) -> None:
        """Append one row. Log WARNING on failure — never raises."""

    async def read_recent(
        self,
        session_id: str,
        n: int = 20,
    ) -> list[dict]:
        """Return last n audit rows for session as list of dicts.
        Keys: timestamp, agent_id, tool, command, decision, reason.
        Returns [] when disabled or on read failure."""
```

SQLite schema:
```sql
CREATE TABLE IF NOT EXISTS hil_audit (
    id           TEXT PRIMARY KEY,
    session_id   TEXT NOT NULL,
    agent_id     TEXT,
    timestamp    TEXT NOT NULL,
    context      TEXT NOT NULL,
    tool         TEXT NOT NULL,
    command      TEXT,
    command_hash TEXT NOT NULL,
    decision     TEXT NOT NULL,
    reason       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_hil_session_decision
    ON hil_audit (session_id, decision);
```

### `HILController` (`controller.py`)
```python
class HILController(HILInterface):
    def __init__(self, config: HILConfig, session_id: str) -> None:
        self.config = config
        self._session_id = session_id
        self.session = HILSession()
        self._lock = asyncio.Lock()     # serializes check_approval() — prevents duplicate prompts
        self._audit = HILAuditWriter(config.audit_path, config.audit_enabled, config.context)
        _overlap = set(config.exempt_tools) & set(config.blocked_tools)
        if _overlap:
            logger.warning("[HIL] Tools in both exempt_tools and blocked_tools (exempt wins): %s", _overlap)

    async def initialize(self) -> None:
        await self._audit.initialize()

    async def check_approval(
        self, tool_name: str, tool_args: dict, agent_id: str | None = None
    ) -> HILDecision:
        async with self._lock:
            # Decision chain (first match wins):
            # 1. exempt_tools → allow (reason: exempt_tool)
            # 2. blocked_tools → deny (reason: blocked_tool)  [beats yolo]
            # 3. extract command: command_execute → tool_args["command"], else None
            # 4. first_word(command) in blocked_commands → deny (reason: blocked_command) [beats yolo]
            # 5. mode == "yolo" → allow (reason: yolo_mode)
            # 6. first_word(command) in safe_commands → allow (reason: safe_command)
            # 7. SHA256(tool+args) in trusted_hashes → allow (reason: trusted_hash)
            # 8. first_word(command) in ask_once_commands AND in ask_once_approved → allow (reason: ask_once_approved)
            # 9. prompt user:
            #      [1] user_approved_once — one-shot, NO trust state change
            #      [2] user_denied
            #      [3] user_approved_always — stores hash in trusted_command_hashes;
            #          if command tool AND first_word in ask_once_commands: also adds first_word to ask_once_approved
            # Every branch: await self._audit.write(self._session_id, agent_id, tool_name,
            #                                       command, context=self.config.context, decision=decision)

    def _extract_command(self, tool_name: str, tool_args: dict) -> str | None: ...
    @staticmethod
    def _first_word(command: str) -> str: ...
    def _hash_call(self, tool_name: str, tool_args: dict) -> str: ...

    # /hil subcommands
    def status_text(self) -> str: ...
    def set_mode(self, mode: str) -> str: ...
    def set_context(self, context: str) -> str:
        """Re-resolve effective mode: context_modes.get(new_context, base_mode)."""
    def clear_session(self) -> str: ...
    async def show_audit(self, n: int = 20) -> str:
        """Call self._audit.read_recent(self._session_id, n) for data.
        Render rich.table.Table with columns [timestamp, agent_id, tool, command, decision, reason].
        Capture via Console(file=StringIO()). Return captured string."""
```

### `prompt.py` key requirements
- Import `rich` directly (`from rich.panel import Panel`, `from rich.console import Console`) — NOT via `friday_cli`
- Check `sys.stdin.isatty()` before blocking; if False → auto-deny with `WARNING` log
- Blocking stdin: `await asyncio.to_thread(input, "  Choice [1/2/3]: ")`
- Unrecognised input → `no` with warning

---

## Phased Build Plan

> **How to use:** Execute phases strictly in order. Complete and verify each phase before advancing.
> Each phase names the **exact files to touch**. Do not modify files outside the listed scope for that phase.
> `[STOP]` marks scope boundaries — anything beyond that line is out of scope for the phase.

---

### Phase 1 — friday-core HIL Interface

**Prerequisites:** none

**Touch exactly these files:**
1. CREATE `packages/friday-core/src/friday_core/interfaces/hil.py`
2. MODIFY `packages/friday-core/src/friday_core/interfaces/__init__.py`

**Step 1.1 — Create `hil.py`**
- Implement both `HILDecision` and `HILInterface` as `@runtime_checkable Protocol` classes exactly as shown in Specification Reference
- Add module docstring: `"""HIL (Human-in-the-Loop) interface protocols. Ref: docs/design/agents/HIL/design.md §4.4"""`
- Imports needed: `from __future__ import annotations`, `from typing import Any, Protocol, runtime_checkable`
- No ABC or abstractmethod imports — both types are Protocols

**Step 1.2 — Update `interfaces/__init__.py`**
- Read the file first to find the existing export pattern
- Add `HILDecision` and `HILInterface` to the exports following the same pattern as existing entries

**`[STOP]`** — Do not touch any other file in `friday-core`. Do not implement any concrete classes here.

**Verify:**
```bash
cd packages/friday-core && python -c "from friday_core.interfaces.hil import HILInterface, HILDecision; print('OK')"
```

**Boundary Impact:**
- Package: `friday-core`
- Contract change: New `HILInterface` and `HILDecision` Protocols in `friday_core.interfaces.hil`
- Affected downstream: `friday-agent` (Phase 9), `friday-hil` (Phase 4), `friday-runtime` (Phase 10)
- Validation: import check above

---

### Phase 2 — friday-hil Package Scaffold

**Prerequisites:** Phase 1 complete

**Touch exactly these files:**
1. CREATE `packages/friday-hil/pyproject.toml`
2. CREATE `packages/friday-hil/src/friday_hil/__init__.py` (empty stub only)
3. CREATE `packages/friday-hil/tests_hil/__init__.py` (empty)

**Step 2.1 — `pyproject.toml`**
```toml
[project]
name = "friday-hil"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "friday-core",
    "aiosqlite",
    "rich",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/friday_hil"]

[tool.uv.sources]
friday-core = { workspace = true }
```

**Step 2.2 — Empty `__init__.py`**
- Single line: `# exports added in Phase 8`

**Step 2.3 — Root `pyproject.toml`**
- Read the root `pyproject.toml` first
- Add `"packages/friday-hil"` to the `[tool.uv.workspace] members` list
- Add `friday-hil = { workspace = true }` to `[tool.uv.sources]`
- Add `"friday-hil"` to the root `dependencies` list

**`[STOP]`** — Do not create module files yet. Do not run `uv sync` yet.

**Verify:**
```bash
ls packages/friday-hil/src/friday_hil/__init__.py
ls packages/friday-hil/tests_hil/__init__.py
grep "friday-hil" pyproject.toml
```

---

### Phase 3 — HILConfig

**Prerequisites:** Phase 2 complete

**Touch exactly one file:**
- CREATE `packages/friday-hil/src/friday_hil/config.py`

**Implement:**
- `HILConfig` dataclass with all fields from Specification Reference
- `HILConfig.from_dict()` classmethod exactly as specified
- Module docstring referencing `docs/design/agents/HIL/config-reference.md`
- Imports: `from __future__ import annotations`, `dataclasses`, `pathlib.Path`, `typing`

**`[STOP]`** — Do not touch `__init__.py` or any other module yet.

**Verify:**
```bash
cd packages/friday-hil && python -c "
from src.friday_hil.config import HILConfig
c = HILConfig.from_dict({'mode': 'strict', 'context': 'interactive', 'context_modes': {'interactive': 'strict'}})
assert c.mode == 'strict'
assert c.base_mode == 'strict'
print('OK')
"
```

---

### Phase 4 — HILSession + HILDecision

**Prerequisites:** Phase 3 complete

**Touch exactly two files:**
1. CREATE `packages/friday-hil/src/friday_hil/session.py`
2. CREATE `packages/friday-hil/src/friday_hil/decision.py`

**Step 4.1 — `session.py`**
- `HILSession` dataclass with `trusted_command_hashes: dict[str, datetime]` and `ask_once_approved: set[str]`
- Imports: `dataclasses`, `datetime`

**Step 4.2 — `decision.py`**
- `HILDecision` dataclass subclassing `HILDecisionABC` from `friday_core.interfaces.hil`
- Fields: `allowed: bool`, `reason: Literal[...]` (all 10 reason codes from Specification Reference), `display_command: str | None = None`
- Import: `from friday_core.interfaces.hil import HILDecision as HILDecisionABC`

**`[STOP]`** — Do not start `audit.py` or `controller.py` yet.

**Verify:**
```bash
cd packages/friday-hil && python -c "
from src.friday_hil.session import HILSession
from src.friday_hil.decision import HILDecision
s = HILSession()
d = HILDecision(allowed=True, reason='exempt_tool')
print('OK')
"
```

---

### Phase 5 — HILAuditWriter

**Prerequisites:** Phase 4 complete

**Touch exactly one file:**
- CREATE `packages/friday-hil/src/friday_hil/audit.py`

**Implement `HILAuditWriter`:**
- `__init__(self, db_path: Path, enabled: bool, context: str)` — store all three; `context` stored for reference only (not used for write records — callers pass current context at write time)
- `initialize()` — open `aiosqlite` connection, `PRAGMA journal_mode=WAL`, run `CREATE TABLE IF NOT EXISTS` + `CREATE INDEX IF NOT EXISTS` from schema in Specification Reference; `Path.mkdir(parents=True, exist_ok=True)` before opening DB; raise `RuntimeError` on failure when `enabled=True`; no-op when `enabled=False`
- `write(session_id, agent_id, tool_name, command, context, decision)` — insert one row; `id=str(uuid.uuid4())`, `timestamp=datetime.utcnow().isoformat()`, `command_hash=SHA256(json.dumps({"tool": tool_name, ...}, sort_keys=True))`; catch all exceptions and log at `WARNING` level — never re-raise
- `read_recent(session_id, n=20) -> list[dict]` — query `SELECT timestamp, agent_id, tool, command, decision, reason FROM hil_audit WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?`; return list of dicts with those keys; return `[]` when `enabled=False` or on read failure (log at WARNING)
- Use `friday_core.logging.get_logger(__name__)` for all logging — never `print()` or stdlib `logging`

**`[STOP]`** — Do not implement `HILController` or `prompt.py` yet.

**Verify:**
```bash
cd packages/friday-hil && python -c "
import asyncio, tempfile, os
from pathlib import Path
from src.friday_hil.audit import HILAuditWriter
from src.friday_hil.decision import HILDecision

async def test():
    with tempfile.TemporaryDirectory() as d:
        w = HILAuditWriter(Path(d) / 'test.db', enabled=True, context='interactive')
        await w.initialize()
        d_obj = HILDecision(allowed=True, reason='exempt_tool')
        await w.write('sess1', None, 'file_read', None, 'interactive', d_obj)
        print('OK')
asyncio.run(test())
"
```

---

### Phase 6 — Approval Prompt UI

**Prerequisites:** Phase 5 complete

**Touch exactly one file:**
- CREATE `packages/friday-hil/src/friday_hil/prompt.py`

**Implement `show_approval_prompt(tool_name, command)`:**
- Import `rich` directly: `from rich.panel import Panel`, `from rich.console import Console`, `from rich.text import Text` — do NOT import from `friday_cli`
- Check `sys.stdin.isatty()` before blocking; if False → log `WARNING("[HIL] Non-TTY detected — auto-denying tool call: %s", tool_name)` and return `"2"` (deny)
- Display a `Panel` showing tool name, command (or "N/A"), and options `[1] Yes / [2] No / [3] Allow`
- Await `asyncio.to_thread(input, "  Choice [1/2/3]: ")` for non-blocking stdin
- Unrecognised input → log warning, return `"2"`
- Return value: one of `"1"`, `"2"`, `"3"` (string, not int)

**`[STOP]`** — Do not implement `HILController` yet. Do not modify any other file.

**Verify:**
```bash
cd packages/friday-hil && python -c "
import sys
# Non-TTY test — should not hang
assert not sys.stdin.isatty() or True  # always passes; real test is no hang
from src.friday_hil.prompt import show_approval_prompt
print('import OK')
"
```

---

### Phase 7 — HILController

**Prerequisites:** Phases 1–6 complete

**Touch exactly one file:**
- CREATE `packages/friday-hil/src/friday_hil/controller.py`

**Implement in this order (do not skip ahead):**

**Step 7.1 — Class skeleton and `__init__`**
- Constructor signature: `def __init__(self, config: HILConfig, session_id: str) -> None`
- Store: `self.config`, `self._session_id`, `self.session = HILSession()`, `self._lock = asyncio.Lock()`, `self._audit = HILAuditWriter(...)`
- Log overlap warning for `exempt_tools ∩ blocked_tools`
- `initialize()` → `await self._audit.initialize()`
- Import `asyncio` at module level

**Step 7.2 — Private helpers**
- `_extract_command(tool_name, tool_args) -> str | None` — returns `tool_args["command"]` if `tool_name == "command_execute"`, else `None`. Note: hard-coded to `command_execute` only in v0.1. If future tools also execute shell commands, this method will need updating or a config-driven mapping.
- `_first_word(command) -> str` — `command.split()[0]` (staticmethod)
- `_hash_call(tool_name, tool_args) -> str` — `hashlib.sha256(json.dumps({"tool": tool_name, "args": tool_args}, sort_keys=True).encode()).hexdigest()`

**Step 7.3 — `check_approval()` decision chain**
The entire decision chain runs under `async with self._lock:` to serialize concurrent calls and prevent duplicate prompts (see design.md §6 concurrency note).

Implement exactly the 9-step chain from Specification Reference, in order. After every decision branch (before returning), call:
```python
await self._audit.write(
    self._session_id, agent_id, tool_name, command,
    context=self.config.context, decision=decision,
)
```
Log `DEBUG` for auto-allow decisions (rules 1–8), `INFO` for user-prompted decisions (rule 9).

**`ask_once` mode note:** The coarse-grained `ask_once_approved` fast-path (rule 8) only applies to command-executing tools with first-word in `ask_once_commands`. Non-command tools in `ask_once` mode only get exact-hash trust via option [3] — they are effectively `strict` unless the user picks option [3] for the exact same call.

**Step 7.4 — Runtime command helpers**
- `status_text() -> str` — one-liner per field: mode, context, trust store sizes, audit DB path, session_id
- `set_mode(mode) -> str` — validate against `["yolo", "strict", "ask_once"]`, update `self.config.mode`, return confirmation string
- `set_context(context) -> str` — update `self.config.context`, re-resolve `self.config.mode = self.config.context_modes.get(context, self.config.base_mode)`, return confirmation
- `clear_session() -> str` — reset `self.session = HILSession()`, return confirmation
- `show_audit(n=20) -> str` — call `self._audit.read_recent(self._session_id, n)` for data, render `rich.table.Table` with columns `[timestamp, agent_id, tool, command, decision, reason]`, capture via `Console(file=StringIO())`, return string. `NULL agent_id` → `"direct"`, `NULL command` → `"—"`.

**`[STOP]`** — Do not touch any file outside `controller.py`.

**Verify:**
```bash
cd packages/friday-hil && python -c "
import asyncio, tempfile
from pathlib import Path
from src.friday_hil.config import HILConfig
from src.friday_hil.controller import HILController

async def test():
    cfg = HILConfig.from_dict({
        'mode': 'yolo',
        'exempt_tools': ['echo'],
        'blocked_tools': ['danger_tool'],
        'safe_commands': ['grep'],
    })
    ctrl = HILController(cfg, session_id='test-session-1')
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        ctrl._audit._db_path = Path(d) / 'hil.db'
        ctrl.config.audit_path = ctrl._audit._db_path
        await ctrl.initialize()

        d1 = await ctrl.check_approval('echo', {})
        assert d1.allowed and d1.reason == 'exempt_tool', d1

        d2 = await ctrl.check_approval('danger_tool', {})
        assert not d2.allowed and d2.reason == 'blocked_tool', d2

        d3 = await ctrl.check_approval('unknown_tool', {})
        assert d3.allowed and d3.reason == 'yolo_mode', d3

        cfg2 = HILConfig.from_dict({'mode': 'strict', 'safe_commands': ['grep']})
        ctrl2 = HILController(cfg2, session_id='test-session-2')
        ctrl2._audit._db_path = Path(d) / 'hil2.db'
        await ctrl2.initialize()
        d4 = await ctrl2.check_approval('command_execute', {'command': 'grep -r TODO .'})
        assert d4.allowed and d4.reason == 'safe_command', d4

        print('All assertions passed')
asyncio.run(test())
"
```

---

### Phase 8 — Package Exports + Workspace Registration

**Prerequisites:** Phase 7 complete

**Touch exactly two files:**
1. MODIFY `packages/friday-hil/src/friday_hil/__init__.py`
2. RUN `uv sync`

**Step 8.1 — `__init__.py` exports**
```python
"""
friday-hil: Human-in-the-Loop approval gates for the Friday Framework.
"""
from friday_hil.config import HILConfig
from friday_hil.session import HILSession
from friday_hil.decision import HILDecision
from friday_hil.controller import HILController

__all__ = ["HILConfig", "HILSession", "HILDecision", "HILController"]
```

**Step 8.2 — Sync workspace**
```bash
uv sync
```
Resolve any dependency conflicts before proceeding.

**`[STOP]`** — Do not touch `friday-agent` or `friday.py` yet.

**Verify:**
```bash
python -c "from friday_hil import HILConfig, HILSession, HILDecision, HILController; print('OK')"
```

---

### Phase 9 — friday-agent: AgentBase

**Prerequisites:** Phase 8 complete

**Touch exactly one file:**
- MODIFY `packages/friday-agent/src/friday_agent/base.py`

**Read the file first.** Then make exactly three changes (plus a subclass verification step):

**Change 9.1 — Import**
Add to the imports section (with other conditional/TYPE_CHECKING imports to avoid circular deps):
```python
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from friday_core.interfaces.hil import HILInterface
```
If `from __future__ import annotations` is already present, do not add it again.

**Change 9.2 — `AgentBase.__init__()`**
- Add `hil_controller: "HILInterface | None" = None` as a parameter (after existing params, before `**kwargs` if present)
- Store as `self._hil: "HILInterface | None" = hil_controller`

**Change 9.3 — `_execute_tool_call()`**
- Read the method to find the exact location before tool callable resolution
- Insert immediately before the tool callable is resolved / called:
```python
if self._hil is not None:
    _hil_decision = await self._hil.check_approval(
        tool_name, arguments, agent_id=self.profile.name
    )
    if not _hil_decision.allowed:
        logger.info("[HIL] Denied: %s (reason: %s)", tool_name, _hil_decision.reason)
        return (
            f"Tool call denied by Human-in-the-Loop policy. "
            f"Reason: {_hil_decision.reason}. The operation was not executed."
        )
```

**Change 9.4 — Verify subclass forwarding**
After modifying `AgentBase.__init__()`, check `CopilotAgent.__init__()` and any other `AgentBase` subclasses in `friday-agent` to confirm `hil_controller` is forwarded to `super().__init__()`. If a subclass has its own `__init__` that does not forward `hil_controller` (either explicitly or via `**kwargs`), add it as an explicit parameter in the same phase. Do not defer this to a later phase — the Level 2 integration tests (Phase 19) depend on it.

**`[STOP]`** — Do not modify any other method in `base.py` beyond these changes. Do not touch `orchestrator.py` yet.

**Verify:**
```bash
pytest packages/friday-agent/tests_agent/ -x -q 2>&1 | tail -5
```
All existing tests must still pass.

**Boundary Impact:**
- Package: `friday-agent`
- Contract change: `AgentBase.__init__()` gains optional `hil_controller` param; `_execute_tool_call()` gains HIL gate
- Affected downstream: All `AgentBase` subclasses must forward `hil_controller` to `super().__init__()`. RuntimeKernel factory methods must pass the new param.
- Validation: `pytest packages/friday-agent/tests_agent/ -x -q`

---

### Phase 10 — RuntimeKernel HIL Integration

**Prerequisites:** Phase 9 complete and passing

**Touch exactly these files:**
1. MODIFY `packages/friday-runtime/src/friday_runtime/di.py`
2. MODIFY `packages/friday-runtime/src/friday_runtime/kernel.py`
3. MODIFY `packages/friday-agent/src/friday_agent/orchestrator.py` (optional param only)

**Read each file first.** `AgentOrchestrator._ensure_agent()` delegates agent construction to `AgentRegistry.create_agent()`, which calls a factory callable set by `RuntimeKernel`. HIL injection happens in the factory, not in the orchestrator.

**Change 10.1 — `DIContainer` (`di.py`)**
- Add `self.hil_controller: HILInterface | None = None` as an optional slot (alongside existing optional slots like `multi_agent_memory`)
- Add `_create_hil_controller()` method following the `_create_multi_agent_stack()` config-gated pattern:
  - If HIL is not enabled in config → set `self.hil_controller = None` and return
  - Otherwise create `HILController` from config, store on `self.hil_controller`
- Call `_create_hil_controller()` in `boot()` after `_create_tool_registry()`

**Change 10.2 — `RuntimeKernel` (`kernel.py`)**
- Add `hil_controller` property that accesses `self._di.hil_controller`
- In `_create_interactive_agent(profile)` (line ~596): add `hil_controller=self._di.hil_controller` to the agent constructor call
- In `_create_autonomous_agent(profile)` (line ~612): same addition

**Change 10.3 — `AgentOrchestrator` (`orchestrator.py`) — backward compat only**
- Add `hil_controller: "HILInterface | None" = None` to `AgentOrchestrator.__init__()` for manual-DI flows
- Store as `self._hil: "HILInterface | None" = hil_controller`
- Do NOT modify `_ensure_agent()` — it delegates to the registry factory which already handles injection via RuntimeKernel

**`[STOP]`** — Do not touch `friday.py` yet.

**Verify:**
```bash
pytest packages/friday-agent/tests_agent/ -x -q 2>&1 | tail -5
pytest packages/friday-runtime/ -x -q 2>&1 | tail -5
```
All existing tests must still pass.

**Boundary Impact:**
- Packages: `friday-runtime`, `friday-agent`
- Contract change: `DIContainer` gains optional `hil_controller` slot; RuntimeKernel factory methods inject `hil_controller` into agents; `AgentOrchestrator.__init__()` gains optional `hil_controller` param
- Affected downstream: All experiments using RuntimeKernel gain HIL support automatically when enabled in config
- Validation: test commands above

---

### Phase 11 — friday_chat Config Validation

**Prerequisites:** Phase 10 complete

**Touch exactly one file:**
- MODIFY `tests/integration/memory/friday_chat/config.py`

**Read the file first** to find `_validate_config()` and the `optional_sections` dict.

Add `"hil": dict` to `optional_sections` following the same pattern as existing entries.

**`[STOP]`** — Do not touch any other function in `config.py`.

**Verify:**
```bash
python -c "
import sys; sys.path.insert(0, 'tests/integration/memory')
from friday_chat.config import load_config
print('import OK')
"
```

---

### Phase 12 — friday.py: Imports + HIL Initialization in `main()`

**Prerequisites:** Phase 11 complete

**Touch exactly one file:**
- MODIFY `tests/integration/memory/friday.py`

**Read the file first** — it is ~8000 lines. Identify:
- The import block at the top
- The `main()` function, specifically where `session_id` is created (~line 7758)

**Change 12.1 — Add imports** (near other optional-feature imports):
```python
from friday_hil import HILConfig, HILController
from friday_core.interfaces.hil import HILInterface
```

**Change 12.2 — HIL init block in `main()`**
After `session_id` creation (~line 7758: `session_id = f"session_{uuid.uuid4().hex[:8]}"`), before `MemoryChatSession` construction (~line 7782), add:

**Note:** `tools_config` is extracted much earlier (~line 7131), but `session_id` is not created until ~line 7758. The HIL init block must be placed after `session_id` because `HILController` requires it at construction time.
```python
hil_config_dict = config.get("hil", {})
hil_controller: HILInterface | None = None
if hil_config_dict:
    _parsed_hil = HILConfig.from_dict(hil_config_dict)
    if _parsed_hil.enabled:
        hil_controller = HILController(_parsed_hil, session_id=session_id)
        await hil_controller.initialize()   # raises on bad DB path — fail fast
        logger.info(
            "[HIL] Initialized: mode=%s context=%s audit=%s",
            _parsed_hil.mode, _parsed_hil.context, _parsed_hil.audit_path,
        )
```

**`[STOP]`** — Do not wire `hil_controller` into any class constructors yet. Stop after the init block.

**Verify:**
```bash
python -c "
import sys; sys.path.insert(0, 'tests/integration/memory')
import friday
print('import OK')
"
```

---

### Phase 13 — friday.py: Session Wiring

**Prerequisites:** Phase 12 complete

**Touch exactly one file:**
- MODIFY `tests/integration/memory/friday.py`

**Read the file** to locate `MemoryChatSession.__init__()` and the `MemoryChatSession(...)` instantiation in `main()`.

> **Note:** `friday.py` v0.1 supports direct-chat HIL only. Orchestrated-agent HIL is handled by the RuntimeKernel factory (Phase 10). There is no `AgentOrchestrator(...)` construction in `friday.py` to modify.

**Change 13.1 — `MemoryChatSession.__init__()`**
- Add `hil_controller: "HILInterface | None" = None` parameter (after existing optional params)
- Store as `self._hil: "HILInterface | None" = hil_controller`

**Change 13.2 — `MemoryChatSession` instantiation in `main()`**
Find where `MemoryChatSession(...)` is called in `main()` (line ~7782). Add `hil_controller=hil_controller`.

**`[STOP]`** — Do not add the tool intercept yet. Stop after these two changes.

**Verify:**
```bash
python -c "
import sys; sys.path.insert(0, 'tests/integration/memory')
import friday
print('import OK')
"
```

---

### Phase 14 — friday.py: Tool Intercept in `_process_with_tools()`

**Prerequisites:** Phase 13 complete

**Touch exactly one file:**
- MODIFY `tests/integration/memory/friday.py`

**Read `_process_with_tools()`** — find the `for tc in tool_calls_to_process:` loop and locate:
- The `all_tool_calls.append(...)` call
- The `# Execute the tool` comment that follows it

Insert the HIL gate **between** `all_tool_calls.append(...)` and `# Execute the tool`:
```python
# HIL: check approval before executing
if self._hil is not None:
    _hil_decision = await self._hil.check_approval(
        tool_name, tool_args, agent_id=None
    )
    if not _hil_decision.allowed:
        display_warning(
            f"  [HIL] Denied: {tool_name} (reason: {_hil_decision.reason})"
        )
        _denied_content = (
            "Tool call denied by Human-in-the-Loop policy. "
            f"Reason: {_hil_decision.reason}. "
            "The operation was not executed."
        )
        all_tool_results.append(
            MemoryToolResult(
                tool_call_id=tool_id,
                output=_denied_content,
                error="HIL denied",
                metadata={"hil_denied": True, "reason": _hil_decision.reason},
            )
        )
        working_messages.append({
            "role": "tool",
            "tool_call_id": tool_id,
            "content": _denied_content,
        })
        continue  # skip execution, sanitization, lifecycle, and ingestion
```

**`[STOP]`** — Do not add the `/hil` command yet. Touch only this one insertion point.

**Verify:**
```bash
python -c "
import sys; sys.path.insert(0, 'tests/integration/memory')
import friday
print('import OK')
"
```

---

### Phase 15 — friday.py: `/hil` CLI Command

**Prerequisites:** Phase 14 complete

**Touch exactly one file:**
- MODIFY `tests/integration/memory/friday.py`

**Read `handle_command()`** to find the `match/case` block structure.

**Change 15.1 — Add case to `handle_command()`**
```python
case "hil":
    sub = parts[1] if len(parts) > 1 else ""
    val = parts[2] if len(parts) > 2 else ""
    return await self.cmd_hil(sub, val)
```

**Change 15.2 — Add `cmd_hil()` method**
Add `async def cmd_hil(self, subcommand: str = "", value: str = "") -> str:` to `MemoryChatSession`. Implement exactly as in `docs/design/agents/HIL/design.md §7.3 F`. Subcommands: `status` | `mode <name>` | `context <name>` | `clear` | `audit [n]`.

**Change 15.3 — Update command docstring**
Find the command listing docstring near the top of `friday.py` (lines ~54–80). Add `/hil [status|mode|context|clear|audit]` to the list.

**`[STOP]`** — Stop after these three changes.

**Verify:**
```bash
python -c "
import sys; sys.path.insert(0, 'tests/integration/memory')
import friday
print('import OK')
"
```

---

### Phase 16 — config.yaml: Add `hil:` Section

**Prerequisites:** Phase 15 complete

**Touch exactly one file:**
- MODIFY `tests/integration/memory/config.yaml`

**Read the file first** to find the correct insertion point (after existing top-level sections).

Add the following `hil:` section:
```yaml
hil:
  enabled: true
  mode: strict
  context: interactive
  context_modes:
    interactive: strict
    semi_autonomous: ask_once
    autonomous: yolo
  exempt_tools:
    - get_current_datetime
    - echo
  blocked_tools: []
  safe_commands:
    - tail
    - head
    - grep
    - find
    - ls
    - cat
    - wc
    - sort
    - uniq
    - cut
  ask_once_commands:
    - python
    - git
    - dolt
    - bd
  blocked_commands:
    - rm
    - dd
    - mkfs
  autonomous_fallback:
    action: deny
    timeout_seconds: 30
  audit:
    enabled: true
    path: ./logs/hil_audit.db
```

**`[STOP]`** — Do not touch any other section of `config.yaml`.

---

### Phase 17 — Unit Tests

**Prerequisites:** Phase 16 complete

**Create exactly five files:**
1. CREATE `packages/friday-hil/tests_hil/conftest.py` (shared fixtures — see test-plan.md Level 1)
2. CREATE `packages/friday-hil/tests_hil/test_config.py`
3. CREATE `packages/friday-hil/tests_hil/test_audit.py`
4. CREATE `packages/friday-hil/tests_hil/test_decision_chain.py`
5. CREATE `packages/friday-hil/tests_hil/test_prompt.py`

Follow the test coverage list from `docs/design/agents/HIL/test-plan.md` Level 1.

**`test_config.py`** must cover:
- Context mode override resolution (effective mode from `context_modes`)
- `base_mode` preserved separately from effective `mode`
- All missing keys default correctly
- `audit_path` coerced to `Path`
- `blocked_tools` defaults to `[]`

**`test_audit.py`** must cover:
- `initialize()` creates DB file, `hil_audit` table, and `idx_hil_session_decision` index
- `initialize()` raises `RuntimeError` on unwritable path when `enabled=True`
- `initialize()` is no-op when `enabled=False`
- `write()` inserts row with correct `session_id`, `agent_id`, `decision`, `reason`, `context`
- `write()` silently logs (does not raise) on insert failure
- `context` column stores the value passed to `write()`, not the value from `__init__`
- `read_recent()` returns correct rows as list of dicts, ordered by most recent first
- `read_recent()` filters by `session_id` — rows from other sessions are excluded
- `read_recent()` returns `[]` when `enabled=False`

**`test_decision_chain.py`** must cover every branch of `check_approval()`:
- Rule 1: `exempt_tools` → allow without prompt
- Rule 2: `blocked_tools` → deny in yolo mode (beats yolo)
- Rule 3: `blocked_commands` → deny in yolo mode (beats yolo)
- `exempt_tools` + `blocked_tools` overlap → allow (exempt wins), WARNING logged
- Rule 4: `yolo_mode` → allow non-blocked tools
- Rule 5: `safe_commands` → allow without prompt (in strict mode)
- Rule 6: `trusted_hash` → allow after option [3] was chosen in a prior call
- Rule 7: `ask_once_commands` → prompt first time, auto-allow second time (same first word)
- `agent_id` propagated to audit `write()` call (mock the writer)
- Non-TTY auto-deny (monkeypatch `sys.stdin.isatty` → `False`) — this is the non-TTY path within the prompt rule (rule 8)
- Auto-allow decisions (rules 1–7) emit `DEBUG` log
- Audit `write()` called exactly once per `check_approval()` call

**`test_prompt.py`** must cover:
- `sys.stdin.isatty() = False` → returns `"2"` without blocking
- Warning logged with tool name in non-TTY path
- `prompt.py` imports from `rich.*`, not from `friday_cli`

Use `pytest-asyncio` (`@pytest.mark.asyncio`) for async tests. Use `tmp_path` fixture for DB files.

**`[STOP]`** — Do not add integration tests yet.

**Verify:**
```bash
pytest packages/friday-hil/tests_hil/ -v 2>&1 | tail -20
```
All tests must pass.

---

### Phase 18 — End-to-End Verification (Manual Only)

**Prerequisites:** All prior phases complete and verified

**Note:** This phase is a manual developer verification step, not intended for CI automation. The interactive TTY prompts and Rich panel rendering require a human operator. Automated coverage for all HIL logic is provided by Phases 17, 19–22.

Run the following sequence in order. Each step must produce the stated result before proceeding to the next.

```bash
# 1. Full workspace sync
uv sync

# 2. Confirm audit DB created at startup
python tests/integration/memory/friday.py &
sleep 3
ls -la logs/hil_audit.db   # must exist
kill %1

# 3. Smoke test — run interactively and execute each verification
python tests/integration/memory/friday.py
```

**In the running session, execute in order:**

| Command / Prompt | Expected Result |
|---|---|
| `/hil` | Shows mode=strict, context=interactive, audit DB path |
| Ask: `grep -r TODO .` (via command_execute) | Executes without prompt (`safe_command`) |
| Ask: `run git status` | Shows HIL approval prompt (first time) |
| Ask: `run git log` | No prompt — auto-approved (same first-word `git`, `ask_once_commands`) |
| Ask: `rm -rf /tmp/test_hil_delete` | Denied immediately, LLM sees denial message (`blocked_command`) |
| `/hil mode yolo` | Confirms mode=yolo |
| Ask: `any_tool_call` | Executes without prompt |
| `/hil context semi_autonomous` | Shows mode re-resolved to ask_once |
| `/hil audit 10` | Shows table of last 10 HIL decisions for this session |
| `/hil clear` | Confirms trust store cleared |

```bash
# 4. Run full test suite — must not regress
pytest packages/friday-agent/tests_agent/ packages/friday-hil/tests_hil/ -x -q
```

---

### Phase 19 — `friday_hil.testing` Module + Level 2 Agent Integration Tests

**Prerequisites:** Phases 9–10 complete (AgentBase and Orchestrator wired)

**Touch exactly three files:**
1. CREATE `packages/friday-hil/src/friday_hil/testing.py`
2. MODIFY `packages/friday-hil/src/friday_hil/__init__.py` (add `testing` to docs, no re-export needed)
3. CREATE `packages/friday-agent/tests_agent/test_hil_integration.py`

**Step 19.1 — `testing.py`**
Create `MockHILController` exactly as specified in `docs/design/agents/HIL/test-plan.md` § Shared Helpers.
- Module docstring: `"""friday_hil.testing — Test doubles for the HIL package."""`
- Import `HILDecision` from `friday_hil.decision` (not from `friday_hil` to avoid circular imports)
- The class satisfies the `HILInterface` `Protocol` structurally — no subclassing or import of `HILInterface` is needed. Verify with `isinstance(MockHILController(), HILInterface)` since the protocol is `@runtime_checkable`.

**Step 19.2 — `test_hil_integration.py`**
Implement all tests from `docs/design/agents/HIL/test-plan.md` Level 2:
- `TestAgentBaseHIL` — 8 tests covering gate calls, allow/deny behavior, agent_id, None controller, multi-call, loop continuity
- `TestOrchestratorHIL` — 3 tests covering storage, propagation, None propagation
- Use existing fixtures from `tests_agent/conftest.py` (`profile`, `mock_memory`, `mock_context_engine`, `mock_llm`, `tool_registry`)
- Import `MockHILController` from `friday_hil.testing`
- Import `HILDecision` from `friday_hil.decision`

**`[STOP]`** — Do not touch `friday.py` or any experiment files.

**Verify:**
```bash
pytest packages/friday-agent/tests_agent/test_hil_integration.py -v 2>&1 | tail -20
```
All 11 tests must pass.

---

### Phase 20 — Level 3: friday.py Session Integration Tests

**Prerequisites:** Phases 13–15 complete (friday.py wired with HIL)

**Touch exactly three files:**
1. CREATE `tests/integration/memory/tests_hil/__init__.py` (empty)
2. CREATE `tests/integration/memory/tests_hil/conftest.py`
3. CREATE `tests/integration/memory/tests_hil/test_memory_chat_hil.py`

**Also modify:**
4. MODIFY root `pyproject.toml` — add `"tests/integration/memory/tests_hil"` to `testpaths`

**Step 20.1 — `conftest.py`**
```python
import sys
from pathlib import Path

# Make tests/integration/memory importable so `from friday import MemoryChatSession` works
INTEGRATION_ROOT = Path(__file__).resolve().parents[1]
if str(INTEGRATION_ROOT) not in sys.path:
    sys.path.insert(0, str(INTEGRATION_ROOT))
```

**Step 20.2 — `test_memory_chat_hil.py`**
Implement all tests from `docs/design/agents/HIL/test-plan.md` Level 3:
- `TestMemoryChatSessionHIL` — 7 tests covering approval ordering, allow/deny results, message structure, agent_id=None, metadata
- `TestCmdHil` — 7 tests covering `/hil` subcommands (status, mode, context, clear, audit, unknown, no-controller)
- Import `MockHILController` from `friday_hil.testing`
- Import `MemoryChatSession` from `friday` (via sys.path from conftest)
- Mock heavy dependencies (`llm`, `tool_registry`, `memory_controller`, `context_assembler`) — read `MemoryChatSession.__init__()` to identify required params and create minimal mocks for each

**`[STOP]`** — Do not create the experiment scaffold yet.

**Verify:**
```bash
pytest tests/integration/memory/tests_hil/ -v 2>&1 | tail -20
```
All 14 tests must pass.

---

### Phase 21 — Level 4a: HIL Smoke Experiment

**Prerequisites:** All prior phases complete

**Create the experiment scaffold (7 files):**
1. CREATE `experiments/hil_smoke/__init__.py` (empty)
2. CREATE `experiments/hil_smoke/agents/hil_probe.yaml`
3. CREATE `experiments/hil_smoke/config/runtime.yaml` (copy from `experiments/agent_quality/config/runtime.yaml`)
4. CREATE `experiments/hil_smoke/fake_llm.py`
5. CREATE `experiments/hil_smoke/runtime.py`
6. CREATE `experiments/hil_smoke/run.py`
7. CREATE `experiments/hil_smoke/tests/__init__.py` (empty)
8. CREATE `experiments/hil_smoke/tests/test_hil_smoke.py`

Follow `docs/design/agents/HIL/test-plan.md` Level 4a exactly for:
- `hil_probe.yaml` agent config
- `ToolCallLLMClient` in `fake_llm.py`
- `HilSmokeResult` dataclass and all 8 scenario runner functions in `runtime.py`
- All 10 tests in `test_hil_smoke.py`
- Import `MockHILController` from `friday_hil.testing` (not duplicated locally)

**`[STOP]`** — Do not modify existing experiments yet.

**Verify:**
```bash
pytest experiments/hil_smoke/tests/ -v 2>&1 | tail -20
```
All 10 tests must pass.

---

### Phase 22 — Level 4b: Regression Tests in Existing Experiments

**Prerequisites:** Phase 21 complete

**Touch exactly four files (additive changes only):**
1. CREATE `experiments/agent_quality/tests/test_hil_regression.py`
2. MODIFY `experiments/agent_quality/runtime.py` — add `hil_mode: str = "disabled"` parameter and `hil_enabled: bool` + `hil_decisions_count: int` to result dataclass
3. CREATE `experiments/workflow_artifact_smoke/tests/test_hil_regression.py`
4. MODIFY `experiments/workflow_artifact_smoke/runtime.py` — same additive changes as step 2

Follow `docs/design/agents/HIL/test-plan.md` Level 4b exactly. These tests verify that **HIL in yolo mode does not change existing experiment outcomes**.

**`[STOP]`** — Do not modify any experiment logic beyond adding the `hil_mode` parameter and result fields.

**Verify:**
```bash
pytest experiments/agent_quality/tests/test_hil_regression.py -v
pytest experiments/workflow_artifact_smoke/tests/test_hil_regression.py -v

# Full HIL test sweep — all levels
pytest packages/friday-hil/tests_hil/ \
       packages/friday-agent/tests_agent/test_hil_integration.py \
       tests/integration/memory/tests_hil/ \
       experiments/hil_smoke/tests/ \
       experiments/agent_quality/tests/test_hil_regression.py \
       experiments/workflow_artifact_smoke/tests/test_hil_regression.py \
       -v --tb=short
```
All tests across all levels must pass.
