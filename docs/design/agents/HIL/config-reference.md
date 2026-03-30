# HIL Config Reference

The `hil:` section in `config.yaml` controls the HIL approval system.
All fields are optional — HIL is disabled when the `hil:` section is absent.

---

## Full Schema

```yaml
hil:
  # Master on/off switch.
  # When false, HILController is not instantiated and all tools execute freely.
  enabled: true

  # Default approval mode.
  #   yolo      — Execute all tools without prompting (except blocked_tools/blocked_commands).
  #   strict    — Always prompt for non-exempt, non-safe tool calls.
  #   ask_once  — Prompt once per unique call; trusted calls auto-approve for the session.
  mode: strict

  # Active context name.
  # Used to select a mode override from context_modes.
  # Has no effect if context_modes is empty or the key is absent.
  # Can be changed at runtime with: /hil context <name>
  context: interactive

  # Per-context mode overrides (optional).
  # When context matches a key here, that mode is used instead of `mode`.
  context_modes:
    interactive: strict         # Human is present — always prompt
    semi_autonomous: ask_once   # Human available but not watching — prompt once
    autonomous: yolo            # No human — rely on policy and audit log

  # Tool names that always execute without any prompt (allow by tool name).
  # Exact match against the tool's registered name.
  # Symmetric counterpart to blocked_tools.
  # Takes priority over blocked_tools — if a tool appears in both lists,
  # exempt_tools wins (priority 1) and a WARNING is logged at startup.
  exempt_tools:
    - get_current_datetime
    - echo

  # Tool names that are always denied without any prompt (deny by tool name).
  # Exact match against the tool's registered name.
  # Applies to any tool type — not limited to command-executing tools.
  # Symmetric counterpart to exempt_tools.
  # Takes priority over all allow rules including yolo mode.
  # If a tool name appears in both exempt_tools and blocked_tools,
  # exempt_tools wins and HILController.__init__() logs a WARNING.
  blocked_tools: []

  # Shell command prefixes that auto-approve without prompting.
  # Matched against the first whitespace-delimited token of the command string.
  # Only applies to tools that execute shell commands (e.g., command_execute).
  # Intended for read-only, non-destructive commands.
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
    - awk
    - sed

  # Shell command prefixes that prompt once per session, then auto-approve.
  # On first encounter the user sees the approval prompt (options 1/2/3).
  # If approved (1 or 3), the first-word token is added to the session's
  # ask_once_approved set — subsequent calls with the same first word skip prompting.
  # Only applies to command-executing tools.
  ask_once_commands:
    - python
    - git
    - dolt
    - bd

  # Shell command prefixes that are always denied without prompting.
  # Matched against the first whitespace-delimited token of the command string.
  # Takes priority over safe_commands and yolo mode.
  # The LLM receives a denial message as the tool result.
  blocked_commands:
    - rm
    - dd
    - mkfs

  # Timeout behaviour when human is unavailable (reserved for v0.2).
  # In v0.1 this field is parsed but has no runtime effect.
  # In v0.2: when HIL is in `autonomous` context and a prompt is required,
  # a timer fires; on expiry it applies `action` and writes an audit record
  # with reason='timeout_fallback'.
  autonomous_fallback:
    action: deny                # deny | allow — what to do when no human responds
    timeout_seconds: 30         # seconds to wait before applying action (v0.2)

  # Audit logging configuration.
  audit:
    # Whether to write audit records.
    # When false, no DB is created and no I/O is performed.
    enabled: true

    # Path to the SQLite audit database.
    # Relative paths are resolved from the working directory at startup.
    # The DB file and parent directories are created during HILController.initialize().
    # initialize() is called at startup — a bad path raises immediately, not mid-session.
    # v0.1: SQLite file path (aiosqlite, same pattern as friday-transcript).
    # v0.2: Dolt MySQL connection string; schema is unchanged.
    path: ./logs/hil_audit.db
```

---

## Decision Priority

When a tool call is intercepted, rules are evaluated in this order (first match wins):

| Priority | Rule | Config Key | Notes |
|----------|------|-----------|-------|
| 1 | Tool is exempt | `exempt_tools` | Always allowed, no prompt |
| 2 | Tool is blocked | `blocked_tools` | Always denied, no prompt; beats yolo mode |
| 3 | Command is blocked | `blocked_commands` | Always denied, no prompt; beats yolo mode |
| 4 | Mode is yolo | `mode: yolo` | All non-blocked tools allowed |
| 5 | Command is safe | `safe_commands` | Always allowed, no prompt |
| 6 | Call hash trusted | (session state) | Approved via option [3] earlier in session |
| 7 | ask_once already approved | `ask_once_commands` + session | First-word approved this session |
| 8 | Prompt user | — | Shows approval UI; user chooses 1/2/3 |

**Note:** `blocked_tools` and `blocked_commands` deny even in yolo mode — they are unconditional.

**`exempt_tools` + `blocked_tools` overlap:** If the same tool name appears in both lists, `exempt_tools` wins (priority 1). `HILController.__init__()` logs a `WARNING` for any overlap at startup so the misconfiguration is immediately visible.

**Command extraction:** For rules 3, 5, and 7 the system extracts a command string from tool arguments. For `command_execute` this is `args["command"]`; for all other tools it is `None` (rules 3/5/7 are skipped). The matched token is always `first_word(command)` — the first whitespace-delimited token of the command string.

**`agent_id` attribution:** Every audit record includes `agent_id` — the name of the orchestrated agent (`AgentBase.profile.name`) or `None` when the call originated from direct chat (`MemoryChatSession`). This is passed as a keyword argument on `check_approval()` at each integration point.

---

## Mode Comparison

In all modes, `blocked_tools` and `blocked_commands` always deny, and `exempt_tools` always allow.

| Mode | Safe commands | ask_once commands | Trusted hash | All other tools |
|------|:---:|:---:|:---:|:---:|
| `yolo` | allow | allow | allow | allow |
| `strict` | allow | prompt every time† | allow | prompt every time |
| `ask_once` | allow | prompt once → then allow | allow | prompt once → then allow |

**† `strict` + `ask_once_commands` clarification:** In `strict` mode, `ask_once_commands` are prompted *every time*. The `ask_once_approved` set (priority 7) is only populated when the user approves with option [3], which also adds the hash to `trusted_command_hashes`. On a subsequent call in `strict` mode, the `trusted_hash` check (priority 6) fires first — so once the user has chosen [3], that exact call is auto-approved even in `strict` mode. The practical effect: first call always prompts; option [3] silences *that exact call* for the session; other calls with the same first-word still prompt unless approved individually.

**`ask_once` mode clarification:** In `ask_once` mode, *every* tool (not just `ask_once_commands`) is only prompted once. After the first approval, the call hash is stored in `trusted_command_hashes` and subsequent identical calls auto-approve. `ask_once_commands` additionally store the first-word token in `ask_once_approved`, so *any* call sharing that first word also auto-approves — a coarser-grained trust than the exact-hash mechanism.

---

## Non-TTY Behavior

When HIL is active in a **non-interactive environment** (CI, piped input, or any context where `sys.stdin.isatty()` returns `False`), the approval prompt is not shown. Instead, `prompt.py` auto-denies the tool call with `reason: user_denied` and logs a `WARNING`. This prevents the process from hanging indefinitely waiting for user input that will never arrive.

If you intend to run Friday in a non-TTY context and want tool calls to proceed, use one of:
- `mode: yolo` — all non-blocked tools execute freely
- `exempt_tools` — pre-approve specific tools unconditionally
- `safe_commands` — pre-approve specific shell command prefixes unconditionally

---

## Context Resolution

The effective mode is resolved when `HILConfig.from_dict()` is called:

```
effective_mode = context_modes.get(context, mode)
```

The original `mode` value is preserved as `base_mode` so that `/hil context` re-resolution always has a fallback when the new context key is absent from `context_modes`.

Example: `context: interactive` + `context_modes.interactive: strict` → effective mode is `strict` regardless of the `mode:` field.

The context (and therefore the effective mode) can be changed at runtime:

```
/hil context semi_autonomous   # re-resolves mode from context_modes
/hil mode yolo                 # overrides mode directly, regardless of context
```

**`base_mode` is NOT a YAML key.** It is an internal field derived from `mode` at parse time by `HILConfig.from_dict()`. It cannot be set in `config.yaml`.

**Cascading override warning:** Calling `/hil context` after a prior `/hil mode` override re-resolves the mode from `context_modes`, silently discarding the manual mode change. To preserve a runtime mode override after a context switch, re-apply `/hil mode` after `/hil context`. Example: `/hil context semi_autonomous` followed by `/hil mode yolo` produces `yolo` mode in the `semi_autonomous` context.

---

## Audit Storage

The audit log is persisted in **SQLite** (`aiosqlite`), following the same pattern as `friday-transcript`. The schema is designed to be Dolt-compatible — migration is a connection-string + driver swap (`aiosqlite` → `aiomysql`), not a schema change.

**DB initialized at startup** via `await hil_controller.initialize()`. A bad path raises immediately so misconfiguration surfaces before any tool calls are made.

**Default path:** `./logs/hil_audit.db`

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
    reason       TEXT NOT NULL       -- reason code (see table below)
);

-- Compound index for the most common query pattern (session + decision filter)
CREATE INDEX IF NOT EXISTS idx_hil_session_decision
    ON hil_audit (session_id, decision);
```

`session_id` is the same identifier used by `MemoryChatSession` and `SQLiteTranscriptStore` — all three share the same session anchor, enabling cross-table joins between transcript turns and HIL decisions.

`agent_id` is `NULL` when the call originated from direct chat, or the agent's profile name (e.g., `"researcher"`) when the call was made inside an orchestrated `AgentBase` subclass.

`context` records the HIL context *active at the time of the decision* — not the context at controller initialization. `check_approval()` passes `self.config.context` to `write()` at each call, so records remain accurate after a `/hil context` switch mid-session.

**Sample queries:**

```sql
-- All denials for current session
SELECT timestamp, tool, command, reason
FROM hil_audit
WHERE session_id = ? AND decision = 'denied'
ORDER BY timestamp DESC;

-- Trust grants made by a specific sub-agent
SELECT timestamp, tool, command
FROM hil_audit
WHERE session_id = ? AND agent_id = 'researcher' AND reason = 'user_approved_always';

-- Commands the user has blocked most often
SELECT command, COUNT(*) as denials
FROM hil_audit
WHERE decision = 'denied'
GROUP BY command
ORDER BY denials DESC;
```

**`/hil audit [n]`** queries the SQLite DB filtered to the **current session** (`session_id = self._session_id`) and returns the last `n` records as a plain-text Rich table with columns `[timestamp, agent_id, tool, command, decision, reason]`. `agent_id` NULL displays as `direct`; `command` NULL displays as `—`. Default `n = 20`.

**Audit write failures:** If a write to the audit DB fails (e.g., disk full, permissions issue), the failure is logged at `WARNING` level and does **not** interrupt or affect the HIL approval decision. The tool call proceeds (or is denied) based solely on the policy decision, regardless of whether the audit record was persisted.

---

## Reason Codes

| Reason | Decision | Description |
|--------|----------|-------------|
| `exempt_tool` | allowed | Tool name is in `exempt_tools` |
| `blocked_tool` | denied | Tool name is in `blocked_tools` |
| `blocked_command` | denied | First word of command is in `blocked_commands` |
| `safe_command` | allowed | First word of command is in `safe_commands` |
| `yolo_mode` | allowed | Mode is `yolo` and no block rule matched |
| `trusted_hash` | allowed | Exact call was approved with option [3] earlier in session |
| `ask_once_approved` | allowed | First-word command was approved at least once this session |
| `user_approved_once` | allowed | User chose option [1] at the prompt |
| `user_approved_always` | allowed | User chose option [3] — adds to session trust store |
| `user_denied` | denied | User chose option [2], or non-TTY auto-deny |
| `timeout_fallback` | allowed / denied | v0.2 only — `autonomous_fallback.action` applied after timeout |
