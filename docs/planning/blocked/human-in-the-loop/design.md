# HIL System Design

**Version:** 0.3
**Date:** 2026-03-29

---

## 1. Goals

1. Intercept tool calls before execution anywhere in the ReAct loop.
2. Support configurable approval policies (per-tool, per-command, per-mode).
3. Share a single session trust store across both direct (`MemoryChatSession`) and orchestrated (`AgentOrchestrator` → `AgentBase`) execution paths.
4. Provide a clean seam for future Dolt audit logging and Beads task dispatch.
5. Be independently versioned and testable — no coupling to `friday-agent` internals.

---

## 2. Why a Standalone Package

The HIL system will grow in three distinct phases:

| Phase | Features |
|-------|----------|
| **v0.1 (current)** | Per-tool/command approval gates, session trust store, SQLite audit log |
| **v0.2** | Dolt-backed audit log with full version history, branching per agent |
| **v0.3** | Beads integration — denied tool calls become Beads tasks for async human resolution |

Each phase adds dependencies (a Dolt MySQL adapter, eventually Beads client bindings) that are orthogonal to `friday-agent`. Keeping HIL separate prevents `friday-agent` from accumulating unrelated deps, and lets HIL evolve its persistence layer without touching agent execution logic.

---

## 3. Dependency Architecture

```
friday-core
  └── interfaces/hil.py        (HILInterface Protocol, HILDecision Protocol)
       │
       ├── friday-agent         (accepts HILInterface | None, never imports friday-hil)
       │     └── AgentBase._execute_tool_call()  ← HIL gate
       │
       ├── friday-hil           (implements HILInterface; deps: friday-core + aiosqlite + rich)
       │     └── HILController
       │
       └── friday-runtime       (injects hil_controller via agent factory methods)
             └── RuntimeKernel._create_interactive_agent()  ← passes hil_controller
             └── RuntimeKernel._create_autonomous_agent()   ← passes hil_controller
```

Neither `friday-agent` nor `friday-hil` depends on the other. They are connected through two wiring modes:

1. **RuntimeKernel-managed** (runtime/experiment flows): `RuntimeKernel` creates `HILController` during `boot()`, stores it on `DIContainer`, and injects it into agents via its factory methods (`_create_interactive_agent`, `_create_autonomous_agent`). `AgentOrchestrator._ensure_agent()` delegates to `AgentRegistry.create_agent()`, which calls the RuntimeKernel factory — the orchestrator never directly constructs agents or injects HIL.

2. **Manual DI in `friday.py`** (direct-chat): `HILController` is created in `main()` and passed to `MemoryChatSession`. This path covers direct-chat tool interception and `/hil` commands only — orchestrated-agent HIL is handled by the RuntimeKernel path.

This mirrors how `friday-llm` implements `LLMClient` from `friday-core` without `friday-agent` importing `friday-llm` directly.

**Dependency chain position:**
```
friday-core → ... → friday-agent
friday-core → friday-hil
friday-core → ... → friday-agent → friday-runtime  (factory injects hil_controller)
(friday.py) → friday-hil  (manual DI for direct-chat)
```

---

## 4. Package Structure

### 4.1 `packages/friday-hil/`

```
pyproject.toml
src/friday_hil/
├── __init__.py       # Public exports: HILConfig, HILSession, HILDecision, HILController
├── config.py         # HILConfig dataclass + from_dict()
├── session.py        # HILSession — mutable per-session trust state
├── decision.py       # HILDecision — concrete implementation of friday-core Protocol
├── controller.py     # HILController — main decision engine (satisfies HILInterface Protocol)
├── prompt.py         # Rich terminal UI for interactive approval prompts
└── audit.py          # HILAuditWriter — SQLite (aiosqlite) now, Dolt later
tests_hil/
├── test_decision_chain.py
├── test_audit.py
└── test_config.py
```

**`pyproject.toml` dependencies:**
```toml
[project]
name = "friday-hil"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "friday-core",
    "aiosqlite",
    "rich",           # prompt.py uses rich directly — NOT via friday-cli to keep deps lightweight
]

[tool.uv.sources]
friday-core = { workspace = true }
```

`prompt.py` imports `rich` directly (`from rich.panel import Panel`, `from rich.console import Console`) rather than via `friday_cli.get_console()`. This avoids pulling the entire `friday-cli` → `friday-agent` → ... stack into `friday-hil`. The `rich` package is already present in the workspace as a transitive dep.

Future deps will be added as optional extras: `aiomysql` or `asyncmy` (for Dolt v0.2), a Beads client library (for v0.3).

### 4.2 Root `pyproject.toml`

Add `friday-hil` to `[tool.uv.sources]` and the root `dependencies` list:

```toml
[tool.uv.sources]
friday-hil = { workspace = true }
```

### 4.3 `friday_chat/config.py` — validation update

Add `"hil": dict` to the `optional_sections` dict in `_validate_config()`:

```python
optional_sections = {
    ...existing keys...,
    "hil": dict,
}
```

### 4.4 `packages/friday-core/src/friday_core/interfaces/hil.py` (new)

```python
"""
HIL (Human-in-the-Loop) interface protocols for the Friday Framework.

Both HILDecision and HILInterface are @runtime_checkable Protocols,
consistent with the pattern used in friday_core.interfaces.tools
(ToolDefinition, ToolAdapter, ToolRegistry).

Ref: PRD_HIL_Beads_Dolt_Integration.md §5
"""
from __future__ import annotations
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class HILDecision(Protocol):
    """
    Structural type for an HIL approval check result.

    Concrete implementations (e.g., friday_hil.decision.HILDecision dataclass)
    must provide these attributes. Enforced by mypy at type-check time and by
    isinstance() at runtime via @runtime_checkable.

    Attributes:
        allowed: True if the tool call may proceed.
        reason: Machine-readable reason code.
        display_command: Shell command string shown to user, or None.
    """
    allowed: bool
    reason: str
    display_command: str | None


@runtime_checkable
class HILInterface(Protocol):
    """
    Structural type for an approval gate in the ReAct loop.

    Implementations (HILController, MockHILController) satisfy this
    protocol structurally — no subclassing required. This enables
    test doubles without importing the concrete package.
    """

    async def initialize(self) -> None:
        """
        Perform async initialization (e.g., create audit DB).
        Must be awaited before any calls to check_approval().
        """
        ...

    async def check_approval(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        agent_id: str | None = None,
    ) -> HILDecision:
        """
        Apply HIL policy to a pending tool call.

        Args:
            tool_name: The tool being called (e.g., 'command_execute').
            tool_args: The arguments dict as passed to the tool.
            agent_id: Name of the orchestrated agent making the call,
                      or None when called from direct chat.

        Returns:
            HILDecision with allowed=True/False and a reason code.
        """
        ...
```

Also update `friday-core/interfaces/__init__.py` to export `HILDecision` and `HILInterface`.

---

## 5. HIL Decision Chain

Applied inside `HILController.check_approval()`. First matching rule wins.

```
check_approval(tool_name, tool_args, agent_id=None)
      │
      ├─ tool_name in exempt_tools?               → allow  (reason: exempt_tool)
      │
      ├─ tool_name in blocked_tools?              → deny   (reason: blocked_tool)
      │
      ├─ Extract command string:
      │    command_execute → tool_args["command"]
      │    all other tools → None
      │
      ├─ first_word(command) in blocked_commands? → deny   (reason: blocked_command)
      │
      ├─ mode == "yolo"?                          → allow  (reason: yolo_mode)
      │
      ├─ first_word(command) in safe_commands?    → allow  (reason: safe_command)
      │
      ├─ SHA256(tool+args) in trusted_hashes?     → allow  (reason: trusted_hash)
      │
      ├─ first_word(command) in ask_once_commands
      │    AND first_word(command) in session.ask_once_approved?
      │                                           → allow  (reason: ask_once_approved)
      │
      └─ Prompt user (Rich terminal UI)
             [1] yes   → allow once        (reason: user_approved_once)
                         ONE-SHOT ONLY — no trust state change
             [2] no    → deny              (reason: user_denied)
             [3] allow → add hash to trust store, allow  (reason: user_approved_always)
                         ALWAYS: adds SHA256(tool+args) to trusted_command_hashes
                         CONDITIONAL: if tool is command-executing AND first_word(command)
                           is in ask_once_commands, also add first_word to ask_once_approved
```

Every branch calls:
```python
await self._audit.write(
    self._session_id, agent_id, tool_name, command,
    context=self.config.context, decision=decision,
)
```
The `context` parameter captures the mode *active at the time of the decision* — not the context at controller init. This ensures audit records remain accurate after a `/hil context` switch mid-session.

**`strict` mode + `ask_once_commands` interaction:** In `strict` mode, `ask_once_commands` are prompted *every time* — priority 7 only fires in `ask_once` mode. Option [1] ("Yes — execute once") is a one-shot approval with no trust state change — the same call will prompt again on next encounter. Option [3] ("Allow") adds the exact call hash to `trusted_command_hashes` (priority 6) and, for command-executing tools with first-word in `ask_once_commands`, also adds the first-word to `ask_once_approved`. On a subsequent call with identical tool name and args, priority 6 fires first and auto-approves, even in `strict` mode. Practical effect: first call always prompts; option [1] is ephemeral; option [3] silences that *exact call* for the session; calls with the same command first-word but different args still prompt unless individually approved with option [3].

**`ask_once` mode and non-command tools:** In `ask_once` mode, the coarse-grained `ask_once_approved` set (priority 7) only stores first-word command tokens — which is `None` for non-command tools like `file_read`. For these tools, auto-approval is only possible via `trusted_hash` (priority 6), which requires an exact match on tool name + args. This means `ask_once` mode is effectively `strict` for non-command tools unless the user picks option [3] on the exact same call. This is intentional — coarse-grain trust ("approve all `git` commands") makes sense for shell commands, but auto-approving `file_read` for any path because one read was approved would be too permissive.

**`blocked_tools` vs `blocked_commands`:** `blocked_tools` matches on tool name (any tool, by registered name). `blocked_commands` matches on the first word of the shell command string (only for command-executing tools). This symmetry mirrors `exempt_tools` / `safe_commands`.

**`exempt_tools` + `blocked_tools` overlap:** If the same tool name appears in both lists, `exempt_tools` (priority 1) wins and the tool is allowed. `HILController.__init__()` logs a `WARNING` for any overlap so the misconfiguration is visible at startup.

**Auto-allow visibility:** When a tool is allowed by a non-prompt rule (e.g., `safe_command`, `trusted_hash`), a `DEBUG`-level log entry is written. In `INFO` mode the decision is shown inline. This makes the decision chain observable without cluttering normal output.

**Non-TTY guard:** `prompt.py` checks `sys.stdin.isatty()` before blocking on input. If not a TTY (piped input, CI), it auto-denies with a logged warning rather than hanging.

**Async input:** `await asyncio.to_thread(input, "  Choice [1/2/3]: ")` — blocking stdin read runs in a thread pool without blocking the event loop.

---

## 6. Session Trust Store

`HILSession` holds per-session mutable approval state:

```python
@dataclass
class HILSession:
    # SHA256(json({tool, args}, sort_keys=True)) → datetime when approved
    trusted_command_hashes: dict[str, datetime]
    # first-word command names approved at least once this session (ask_once mode)
    ask_once_approved: set[str]
```

The **same `HILController` instance** (and therefore the same `HILSession`) is passed to:
- `MemoryChatSession` (direct ReAct loop in `friday.py`)
- `AgentOrchestrator` → injected into each `AgentBase` subclass at construction time

This means a user approving `command_execute({"command": "git status"})` in the direct chat also trusts it when a workflow delegates to a sub-agent.

**Concurrency safety:** `HILController` holds an `asyncio.Lock` that serializes all `check_approval()` calls. Under asyncio's cooperative scheduling, concurrent calls from multiple orchestrated agents could interleave at `await` points (the prompt input and audit write), leading to duplicate prompts for the same call. The lock ensures only one approval check is active at a time — while one agent's call is being prompted, other agents' calls queue behind the lock. This adds negligible latency (prompts are human-speed) and eliminates the race between "check if hash exists" and "insert hash after approval."

---

## 7. Integration Points

### 7.1 `AgentBase._execute_tool_call()` (`friday-agent`)

Added `hil_controller: HILInterface | None = None` parameter to `AgentBase.__init__()`.

The intercept runs before the tool callable is resolved, passing the agent's profile name as `agent_id` so the audit record identifies the orchestrated agent:

```python
async def _execute_tool_call(self, tool_name: str, arguments: dict) -> str:
    """Execute a single tool call, applying the HIL gate if configured."""
    if self._hil is not None:
        decision = await self._hil.check_approval(
            tool_name,
            arguments,
            agent_id=self.profile.name,
        )
        if not decision.allowed:
            logger.info("[HIL] Denied: %s (reason: %s)", tool_name, decision.reason)
            return (
                f"Tool call denied by Human-in-the-Loop policy. "
                f"Reason: {decision.reason}. The operation was not executed."
            )
    # ... existing execution ...
```

Return value is a string — the denial message becomes the tool result the LLM sees.

Import added to `base.py`:
```python
from friday_core.interfaces.hil import HILInterface
```

### 7.2 Orchestrated Agents (`friday-runtime`)

`AgentOrchestrator._ensure_agent()` does **not** directly construct agents. It delegates to `AgentRegistry.create_agent(name)` (orchestrator.py line 523), which calls a factory callable set by `RuntimeKernel`. HIL injection for orchestrated agents happens in the factory methods, not in the orchestrator.

**RuntimeKernel wiring (the real factory boundary):**

1. `DIContainer` gains an optional `hil_controller: HILInterface | None` slot, created during `boot()` via a config-gated `_create_hil_controller()` method (following the same pattern as `multi_agent_memory`).

2. `RuntimeKernel._create_interactive_agent(profile)` and `_create_autonomous_agent(profile)` (kernel.py lines 596-626) pass `hil_controller=self._di.hil_controller` to the agent constructor alongside existing dependencies (memory, context_engine, llm, tool_registry, etc.).

3. `RuntimeKernel` exposes `hil_controller` as a property for experiment access.

**Agent creation flow with HIL:**
```
RuntimeKernel.boot()
  └── _create_hil_controller()  → stores on DIContainer

AgentOrchestrator._ensure_agent(name)
  └── AgentRegistry.create_agent(name)
      └── factory(profile)  ← set by RuntimeKernel
          └── RuntimeKernel._create_interactive_agent(profile)
              └── InteractiveAgent(..., hil_controller=self._di.hil_controller)
```

`AgentOrchestrator.__init__()` retains an optional `hil_controller: HILInterface | None = None` parameter for backward compatibility with manual-DI flows, but in RuntimeKernel-managed flows the factory handles injection.

### 7.3 `friday.py` — Direct-Chat Integration

`friday.py` wires `friday-hil` into the direct-chat session (`MemoryChatSession`). This covers tool-call interception and `/hil` CLI commands. Orchestrated-agent HIL is handled by RuntimeKernel (see §7.2).

Changes span five locations (A–E, plus the `/hil` command in F).

#### A. Imports

```python
from friday_hil import HILConfig, HILController
from friday_core.interfaces.hil import HILInterface
```

#### B. `main()` — construct and initialize the controller

After `session_id` creation (~line 7758), before `MemoryChatSession` construction (~line 7782):

```python
hil_config_dict = config.get("hil", {})
hil_controller: HILInterface | None = None
if hil_config_dict:
    _parsed_hil = HILConfig.from_dict(hil_config_dict)
    if _parsed_hil.enabled:
        hil_controller = HILController(_parsed_hil, session_id=session_id)
        await hil_controller.initialize()   # creates SQLite DB and schema; raises on bad path
        logger.info(
            "[HIL] Initialized: mode=%s context=%s audit=%s",
            _parsed_hil.mode,
            _parsed_hil.context,
            _parsed_hil.audit_path,
        )
```

`session_id` is the same ID passed to `MemoryChatSession` and `SQLiteTranscriptStore` — all three share the same session anchor. `initialize()` is called eagerly at startup so DB path errors surface immediately rather than mid-session.

**Note:** `tools_config` is extracted much earlier in `main()` (~line 7131), but `session_id` is not created until line ~7758. The HIL init block must be placed after `session_id` creation because `HILController` requires it at construction time.

#### C. `MemoryChatSession.__init__` — accept and store the controller

New parameter (after `sanitization_config`):

```python
hil_controller: "HILInterface | None" = None,
```

Stored directly:

```python
self._hil: HILInterface | None = hil_controller
```

The real `MemoryChatSession.__init__()` (friday.py lines 290-322) has required params: `llm` (LiteLLMService), `controller` (MemoryController), `assembler` (ContextAssembler), `architect` (PromptArchitect), `system_prompt` (str), `session_id` (str), `user_id` (str). `hil_controller` is added as an optional param alongside other optional params like `orchestrator`, `tools_config`, etc.

#### D. `MemoryChatSession` instantiation in `main()`

Add `hil_controller=hil_controller` to the existing `MemoryChatSession(...)` call at line ~7782.

#### E. `MemoryChatSession._process_with_tools()` — intercept before execution

Inserted inside `for tc in tool_calls_to_process:` (line ~6789), after `all_tool_calls.append(...)` (lines ~6801-6807) and before `raw_result = await _execute_tool(...)` (line ~6814). `agent_id` is `None` — this is direct chat, not an orchestrated agent:

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
        continue  # Skip execution, sanitization, lifecycle tracking, and ingestion
```

The `continue` keeps message history structurally valid — every `tool_calls` entry in the assistant message has a matching `tool` result message, which is required by the Anthropic and OpenAI APIs.

#### F. `/hil` CLI command and `/help` update

`cmd_hil()` is `async def` because `/hil audit` calls `await self._hil.show_audit()`.

Added to the `match/case` block in `handle_command()`:

```python
case "hil":
    sub = parts[1] if len(parts) > 1 else ""
    val = parts[2] if len(parts) > 2 else ""
    return await self.cmd_hil(sub, val)
```

`cmd_hil()` method on `MemoryChatSession`:

```python
async def cmd_hil(self, subcommand: str = "", value: str = "") -> str:
    """
    Manage HIL (Human-in-the-Loop) settings for this session.

    Subcommands:
        (none) | status     — show mode, context, trust store size, audit DB path
        mode <name>         — change active mode (yolo | strict | ask_once)
        context <name>      — change active context; re-resolves effective mode
        clear               — clear session trust store and ask_once approvals
        audit [n]           — show last N audit records for this session (default 20)
    """
    from friday_hil import HILController
    if self._hil is None or not isinstance(self._hil, HILController):
        return "HIL is not configured. Add an 'hil:' section to config.yaml."
    match subcommand.lower():
        case "" | "status":
            return self._hil.status_text()
        case "mode":
            return self._hil.set_mode(value) if value else "Usage: /hil mode <yolo|strict|ask_once>"
        case "context":
            return self._hil.set_context(value) if value else "Usage: /hil context <interactive|semi_autonomous|autonomous>"
        case "clear":
            return self._hil.clear_session()
        case "audit":
            n = int(value) if value.isdigit() else 20
            return await self._hil.show_audit(n)
        case _:
            return f"Unknown HIL subcommand: '{subcommand}'. Use: status | mode | context | clear | audit"
```

The command docstring at the top of `friday.py` (lines 54–80) must also be updated to include `/hil` in the command listing.

---

## 8. Audit Log

### Storage Evolution

| Phase | Backend | Why |
|-------|---------|-----|
| v0.1 | SQLite (`aiosqlite`) | Queryable from day one; consistent with `friday-transcript`; Dolt-compatible schema |
| v0.2 | Dolt | Drop-in MySQL-wire-compatible swap via `aiomysql`; schema is unchanged |

### v0.1 — SQLite via `aiosqlite`

`HILAuditWriter` manages a single SQLite database file. Follows the same pattern as `friday-transcript` (`SQLiteTranscriptStore`): async writes via `aiosqlite`, schema initialized at startup, WAL mode for concurrent reads.

**Schema:**

```sql
CREATE TABLE IF NOT EXISTS hil_audit (
    id           TEXT PRIMARY KEY,   -- UUID4
    session_id   TEXT NOT NULL,      -- links to friday-transcript session
    agent_id     TEXT,               -- orchestrated agent name; NULL for direct chat
    timestamp    TEXT NOT NULL,      -- ISO-8601 UTC
    context      TEXT NOT NULL,      -- interactive | semi_autonomous | autonomous
    tool         TEXT NOT NULL,      -- registered tool name
    command      TEXT,               -- shell command string; NULL for non-command tools
    command_hash TEXT NOT NULL,      -- SHA256(json({tool, args}, sort_keys=True))
    decision     TEXT NOT NULL,      -- allowed | denied
    reason       TEXT NOT NULL       -- reason code
);

-- Compound index for the most common query pattern
CREATE INDEX IF NOT EXISTS idx_hil_session_decision
    ON hil_audit (session_id, decision);
```

`session_id` links HIL audit records to the `friday-transcript` session. `agent_id` identifies which orchestrated agent triggered the record; `NULL` means the call originated from direct chat (`MemoryChatSession`).

**`HILController` construction and public API:**

```python
class HILController(HILInterface):
    def __init__(self, config: HILConfig, session_id: str) -> None:
        self.config = config
        self._session_id = session_id   # baked in at construction; same ID as transcript session
        self.session = HILSession()
        self._lock = asyncio.Lock()     # serializes check_approval() — see §6 concurrency note
        self._audit = HILAuditWriter(
            db_path=config.audit_path,
            enabled=config.audit_enabled,
            context=config.context,
        )
        # Warn on exempt/blocked overlap — misconfiguration, not a hard error
        _overlap = set(config.exempt_tools) & set(config.blocked_tools)
        if _overlap:
            logger.warning(
                "[HIL] Tools in both exempt_tools and blocked_tools (exempt wins): %s",
                _overlap,
            )

    async def initialize(self) -> None:
        """
        Create the SQLite DB, run schema + index migrations.
        Must be awaited before any calls to check_approval().
        Raises on DB path errors so callers fail fast at startup.
        """
        await self._audit.initialize()

    async def check_approval(
        self,
        tool_name: str,
        tool_args: dict,
        agent_id: str | None = None,
    ) -> HILDecision:
        """Apply the HIL decision chain under self._lock. Writes audit record before returning."""
        async with self._lock:
            ...
        # All branches call (inside the lock):
        # await self._audit.write(
        #     self._session_id, agent_id, tool_name, command,
        #     context=self.config.context, decision=decision,
        # )
```

`HILController.initialize()` is the single public async entry point — callers never interact with `HILAuditWriter` directly.

**`HILAuditWriter` interface (`audit.py`):**

```python
class HILAuditWriter:
    """
    Async audit log writer backed by SQLite (aiosqlite).
    Schema is Dolt-compatible — migration is a connection-string + driver swap.
    Follows the friday-transcript pattern: WAL mode, schema init on startup.
    """
    def __init__(self, db_path: Path, enabled: bool, context: str) -> None: ...

    async def initialize(self) -> None:
        """
        Open DB connection, enable WAL mode, run CREATE TABLE and CREATE INDEX.
        Raises RuntimeError if the DB file cannot be created (permissions, bad path)
        when enabled=True. No-op when enabled=False.
        Parent directories are created automatically via Path.mkdir(parents=True).
        """

    async def write(
        self,
        session_id: str,
        agent_id: str | None,
        tool_name: str,
        command: str | None,
        context: str,
        decision: HILDecision,
    ) -> None:
        """
        Append one audit record. Silently logs failures at WARNING level —
        audit must never interrupt tool execution.

        `context` must be the effective context at decision time (self.config.context
        on the controller), not the context stored at HILAuditWriter init. This ensures
        records remain accurate after a /hil context switch mid-session.
        """

    async def read_recent(
        self,
        session_id: str,
        n: int = 20,
    ) -> list[dict]:
        """
        Return the last n audit records for the given session as a list of dicts.

        Each dict has keys: timestamp, agent_id, tool, command, decision, reason.
        Returns an empty list when disabled or on read failure.
        Keeps all DB access inside HILAuditWriter — the controller only formats output.
        This ensures the Dolt migration (v0.2) is contained entirely within audit.py.
        """
```

**Concurrent write safety:** `HILAuditWriter.write()` uses `aiosqlite`, which serializes all writes to a single background thread. Multiple concurrent calls from different agents in the same session (e.g., two orchestrated agents executing tools simultaneously) are safe — writes are enqueued, not dropped or interleaved.

**`initialize()` error policy:**
- `enabled=False`: no-op, no DB is created or opened.
- `enabled=True`, DB creation fails: raises `RuntimeError` so `main()` surfaces the error at startup. A misconfigured audit path is a hard failure, not silent degradation.

**Default path:** `./logs/hil_audit.db`

**Sample queries:**

```sql
-- All denials for the current session
SELECT timestamp, tool, command, reason
FROM hil_audit
WHERE session_id = ? AND decision = 'denied'
ORDER BY timestamp DESC;

-- Trust decisions made by a specific sub-agent
SELECT timestamp, tool, command, reason
FROM hil_audit
WHERE session_id = ? AND agent_id = 'researcher' AND reason = 'user_approved_always';

-- Commands blocked most often across all sessions
SELECT command, COUNT(*) AS denials
FROM hil_audit
WHERE decision = 'denied'
GROUP BY command
ORDER BY denials DESC;
```

### `HILController.show_audit(n)` — in-session query

Called by `/hil audit [n]`. Delegates data retrieval to `HILAuditWriter.read_recent()`, then formats output via `rich.table.Table` (not `friday_cli.display_table()` — keeping `rich` direct):

```python
async def show_audit(self, n: int = 20) -> str:
    """
    Return the last n audit records for this session as a plain-text string
    for inline display in the chat UI.
    Filtered by self._session_id — shows only records for the active session.

    Implementation: calls self._audit.read_recent(self._session_id, n) for data,
    renders a rich.table.Table with columns [timestamp, agent_id, tool, command,
    decision, reason], then captures output to string via Console(file=StringIO()).print(table).
    agent_id NULL is displayed as 'direct'. command NULL is displayed as '—'.
    """
```

### v0.2 — Dolt

Dolt is MySQL-wire-compatible. The migration from SQLite → Dolt requires:

1. Change `audit.path` config to a Dolt MySQL connection string.
2. Swap `aiosqlite` for `aiomysql` (or `asyncmy`) in `HILAuditWriter`.
3. Schema is unchanged — the same `CREATE TABLE` and `CREATE INDEX` DDL runs on Dolt.
4. Gain full version history, branching (`feature/{agent_id}`), and `dolt diff` on every audit record.

The `HILController.initialize()` and `HILAuditWriter.write()` signatures do not change.

---

## 9. Approval Prompt UI

```
╔══════════════════════════════════════════════════════════════╗
║  Tool Call Requires Approval                                 ║
║                                                              ║
║  Tool:    command_execute                                    ║
║  Command: grep -r "TODO" ./src                              ║
║                                                              ║
║  [1] Yes    — Execute once                                   ║
║  [2] No     — Skip this command                             ║
║  [3] Allow  — Trust this exact call for remainder of session ║
║                                                              ║
║  Choice [1/2/3]: _                                          ║
╚══════════════════════════════════════════════════════════════╝
```

Rendered via `rich.panel.Panel` and `rich.text.Text` imported directly from `rich` (not via `friday_cli`). Unrecognised input defaults to `no` with a warning.

---

## 10. `/hil` CLI Command Reference

| Command | Description |
|---------|-------------|
| `/hil` | Show current mode, context, trust store size, audit DB path |
| `/hil mode <name>` | Change active mode (`yolo` / `strict` / `ask_once`) for this session |
| `/hil context <name>` | Change active context; re-resolves effective mode from `context_modes` |
| `/hil clear` | Clear session trust store and ask_once approvals |
| `/hil audit [n]` | Show last N audit records for this session from SQLite (default 20) |

**`set_context()` behaviour:** When the context changes, the effective mode is re-resolved from `config.context_modes.get(new_context, config.base_mode)`. `/hil mode` overrides the mode directly and bypasses context resolution — useful for temporary overrides without changing context.

**Cascading override warning:** Calling `/hil context` after a prior `/hil mode` override re-resolves the mode from `context_modes`, silently discarding the manual mode change. To preserve a runtime mode override after a context switch, re-apply `/hil mode` after `/hil context`. Example: `/hil context semi_autonomous` followed by `/hil mode yolo` produces `yolo` mode in the `semi_autonomous` context.

**Example `/hil` output:**
```
HIL Status
  Mode:          strict
  Context:       interactive
  Trust store:   3 hashes, 2 ask_once approvals
  Audit DB:      ./logs/hil_audit.db
  Session:       a1b2c3d4-...
```

---

## 11. Config Schema

See [config-reference.md](./config-reference.md) for the full `hil:` YAML schema.

---

## 12. Testing Strategy

Tests live in `packages/friday-hil/tests_hil/`, following the monorepo convention (`testpaths = ["packages/*/tests_*"]` in root `pyproject.toml`).

### Unit Tests

**`test_decision_chain.py`** — covers every branch of `check_approval()`:
- `exempt_tools` → allow without prompt
- `blocked_tools` → deny without prompt, including in yolo mode
- `blocked_commands` → deny without prompt, including in yolo mode
- `exempt_tools` + `blocked_tools` overlap → allow (exempt wins), WARNING logged
- `yolo_mode` → allow non-blocked tools
- `safe_commands` → allow without prompt
- `trusted_hash` → allow after option [3] in a prior call
- `ask_once_commands` → prompt first time, auto-allow second time (same first word)
- `agent_id` propagated to audit write call
- Non-TTY auto-deny (mock `sys.stdin.isatty()` → `False`)
- Auto-allow decisions emit DEBUG log

**`test_audit.py`** — covers `HILAuditWriter`:
- `initialize()` creates DB, schema, and index
- `initialize()` raises on unwritable path when `enabled=True`
- `initialize()` is no-op when `enabled=False`
- `write()` inserts rows with correct `session_id`, `agent_id`, `decision`, `reason`
- `write()` silently logs (does not raise) on insert failure

**`test_config.py`** — covers `HILConfig.from_dict()`:
- Context mode override resolution
- `base_mode` preserved separately from effective `mode`
- Missing keys default correctly
- `audit_path` coerced to `Path`
- `blocked_tools` defaults to empty list

### Integration Tests

**HIL in `MemoryChatSession`:** inject `command_execute` tool, trigger it via a chat prompt, assert `agent_id=None` in audit row, assert audit row `decision='allowed'` or `'denied'` as expected.

**HIL in `AgentBase`:** mock `_hil.check_approval()` returning denied, assert return string contains denial message, assert tool callable was never invoked, assert `agent_id=self.profile.name` was passed.

**Shared trust store:** approve a call in direct chat (sets trusted hash), verify same `HILController` allows it in an orchestrated agent without prompting.

---

## 13. Relationship to Workflow HITL

The `friday-agent` package already includes workflow-level HITL (Human-in-the-Loop) constructs in `packages/friday-agent/src/friday_agent/workflows/models.py`: `HITLPolicy`, `HITLRequest`, `HITLDecision` (a Pydantic model with `HITLDecisionAction` enum), and `HITLAuthorityPolicy`. These types govern task execution and task state transitions within the workflow engine (`WorkflowEngine` in `workflows/engine.py`), including role-based approval, timeout policies, and structured request/response flows.

Tool-call HIL (this design) operates on a **separate control plane**. Workflow HITL decides whether a *task* should proceed — it has concepts like `TaskStatus.WAITING_APPROVAL`, approval callbacks, and authority policies. Tool-call HIL decides whether a *tool invocation* within a ReAct loop should proceed — it has concepts like `safe_commands`, `blocked_tools`, and session trust stores. They are complementary, not competing: a workflow task may be approved by workflow HITL, and individual tool calls within that task's execution may still be gated by tool-call HIL.

**Naming:** Workflow-level uses "HITL" (Human-in-the-Loop), tool-call-level uses "HIL". This is an intentional abbreviation distinction for different scopes. The types are fully separate — `HITLDecision` (workflow) has fields like `approver_id`, `approver_role`, `request_id`, while `HILDecision` (tool-call) has `allowed`, `reason`, `display_command`. They live in different packages (`friday_agent.workflows.models` vs `friday_hil.decision`). Unification of the two systems is explicitly deferred to a future version.

---

## 14. Open Questions (from PRD §9)

| Question | Current Answer |
|----------|---------------|
| Should `ask_once` approval persist across restarts? | No — session-scoped in v0.1. Dolt integration in v0.2 enables cross-session persistence by querying the audit table for prior `user_approved_always` records at startup. |
| Default timeout for semi-autonomous mode? | No runtime timeout in v0.1. Config stub (`autonomous_fallback.timeout_seconds`) is parsed but ignored. In v0.2, when HIL is in `autonomous` context and a prompt is required, a timer fires; on expiry it applies `autonomous_fallback.action` (`deny` or `allow`) and writes an audit record with `reason='timeout_fallback'`. |
| Should `blocked_commands` throw errors or return empty results? | Return denial message string (same as `user_denied`). The LLM sees it as a tool result and can decide how to proceed. |
| How to handle Dolt merge conflicts from concurrent agents? | Out of scope for v0.1. Addressed in v0.2 branching strategy — each agent writes to its own `feature/{agent_id}` branch and merges to `main` on task completion. |
