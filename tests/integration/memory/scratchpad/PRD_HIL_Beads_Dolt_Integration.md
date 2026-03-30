# Friday Framework: HIL + Beads + Dolt Integration PRD

**Version:** 0.1  
**Date:** 2026-03-28  
**Author:** Chuck Russell  

---

## 1. Overview

This PRD defines the integration of three systems into the Friday Framework:

1. **Beads** - Task queue and orchestration layer
2. **Dolt** - Version-controlled database for task state and artifacts
3. **HIL (Human-in-the-Loop)** - Approval system for tool execution

**Goals:**
- Enable Friday to dispatch tasks to agents via Beads
- Store task state and artifacts in Dolt with full version history
- Provide configurable human oversight via HIL
- Support interactive, semi-autonomous, and fully autonomous operation modes

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         HUMAN (Chuck)                                    │
│                    ┌─────────────────────┐                              │
│                    │  HIL Interface      │                              │
│                    │  yes/no/allow-exact │                              │
│                    └─────────────────────┘                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     FRIDAY ORCHESTRATOR                                  │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │ friday_agent │  │ friday_tools │  │  HIL Module  │                  │
│  │              │  │              │  │              │                  │
│  │ • ReAct loop │  │ • Tool exec  │  │ • Config     │                  │
│  │ • Task split │  │ • Beads call │  │ • Prompts    │                  │
│  │ • Assembly   │  │ • Dolt call  │  │ • Audit log  │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌─────────────────────────┐         ┌─────────────────────────┐
│         BEADS            │         │         DOLT             │
│                         │         │                         │
│  • Task queue           │         │  • Task state           │
│  • Dispatch to agents    │         │  • Artifacts            │
│  • Dependency graph      │         │  • Version history      │
│  • Version 1.9.0         │         │  • Branches             │
└─────────────────────────┘         └─────────────────────────┘
```

---

## 3. Beads Integration

### 3.1 Purpose
- Task queue for multi-agent orchestration
- Task dispatch to specialized agents
- Dependency tracking between tasks

### 3.2 Data Model

```python
class BeadsTask:
    id: str              # Unique task identifier
    title: str           # Human-readable task name
    description: str    # Detailed task description
    status: str          # pending | in_progress | complete | failed
    agent_id: str        # Assigned agent (None if unassigned)
    dependencies: list   # List of task IDs this task depends on
    artifact_ref: str    # Reference to artifact in Dolt (optional)
    created_at: datetime
    updated_at: datetime
```

### 3.3 Operations

| Operation | Description |
|-----------|-------------|
| `beads_create_task` | Create new task in queue |
| `beads_get_task` | Retrieve task by ID |
| `beads_update_task` | Update task status/assignee |
| `beads_query` | Query tasks by status, agent, etc. |
| `beads_dispatch` | Assign task to agent |
| `beads_complete` | Mark task complete with artifact |

---

## 4. Dolt Integration

### 4.1 Purpose
- Persist task state with full version history
- Store artifacts (files, results, documents)
- Enable branching for parallel agent work
- Conflict resolution for concurrent updates

### 4.2 Schema

```sql
-- Tasks table
CREATE TABLE tasks (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    status ENUM('pending', 'in_progress', 'complete', 'failed'),
    agent_id VARCHAR(255),
    dependencies JSON,
    artifact_ref VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Artifacts table
CREATE TABLE artifacts (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36),
    name VARCHAR(255),
    type ENUM('file', 'result', 'document'),
    content LONGTEXT,
    branch VARCHAR(255),
    commit_hash VARCHAR(40),
    created_at TIMESTAMP
);

-- Audit log table
CREATE TABLE hil_audit (
    id VARCHAR(36) PRIMARY KEY,
    timestamp TIMESTAMP,
    context ENUM('interactive', 'semi_autonomous', 'autonomous'),
    tool VARCHAR(255),
    command_hash VARCHAR(64),
    decision ENUM('allowed', 'denied', 'trusted'),
    reason TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
```

### 4.3 Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production task state |
| `feature/{agent_id}` | Per-agent work branches |
| `task/{task_id}` | Per-task artifact branches |

---

## 5. HIL (Human-in-the-Loop) System

### 5.1 Operation Modes

| Mode | Description |
|------|-------------|
| `yolo` | No prompts, execute all approved commands |
| `strict` | Always prompt for non-exempt commands |
| `ask_once` | Prompt once, then auto-approve for session |

### 5.2 Context Types

| Context | Human Available | Behavior |
|---------|-----------------|----------|
| `interactive` | Yes | Block and wait for response |
| `semi_autonomous` | Limited | Batch prompts, timeout with default |
| `autonomous` | No | Policy-driven, log all decisions |

### 5.3 Config Schema

```yaml
hil:
  mode: strict
  
  # Per-context mode overrides
  context_modes:
    interactive: strict
    semi_autonomous: ask_once
    autonomous: yolo
  
  # Tools that never prompt
  exempt_tools:
    - file_read
    - file_write
    - beads_query
    - beads_get_task
  
  # Commands auto-approved (command name only)
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
  
  # Prompt once per session, then auto-approve
  ask_once_commands:
    - python
    - git status
    - dolt
    - bd
  
  # Always denied
  blocked_commands:
    - rm
    - dd
    - mkfs
  
  # Autonomous fallback when human doesn't respond
  autonomous_fallback:
    action: ask_once  # deny | ask_once | allow
    timeout_seconds: 30
  
  # Audit logging
  audit:
    enabled: true
    path: ./logs/hil_audit.log
```

### 5.4 User Prompts

When HIL intercepts a command:

```
┌─────────────────────────────────────────────────────────────┐
│ ⚠️  Tool Call Requires Approval                             │
│                                                              │
│  Tool: command_execute                                      │
│  Command: grep -r "TODO" ./src                              │
│                                                              │
│  [1] Yes - Execute once                                      │
│  [2] No - Skip this command                                 │
│  [3] Allow this exact command for remainder of session      │
│                                                              │
│  Choice: _                                                  │
└─────────────────────────────────────────────────────────────┘
```

### 5.5 Session Trust Store

Commands approved with option [3] are stored as SHA256 hashes:

```python
class HILSession:
    mode: Literal["yolo", "strict", "ask_once"]
    context: Literal["interactive", "semi_autonomous", "autonomous"]
    trusted_command_hashes: dict[str, datetime]  # hash -> approval time
    ask_once_approved: set[str]  # command names approved this session
```

---

## 6. ReAct Loop Integration

```
┌─────────────────────────────────────────────────────────────┐
│                    ReAct Loop                                │
│                                                              │
│  1. OBSERVE ─── Get input, context, tool results            │
│         │                                                   │
│         ▼                                                   │
│  2. THINK ──── LLM selects tool + args                     │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  HIL INTERCEPT                                       │   │
│  │                                                       │   │
│  │  • Check exempt_tools → execute if match             │   │
│  │  • Check safe_commands → execute if match            │   │
│  │  • Check ask_once → prompt first time                │   │
│  │  • Check trusted hash → execute if match            │   │
│  │  • Check hil.mode=yolo → execute if set             │   │
│  │  • Else → show HIL prompt                            │   │
│  │    → User: yes/no/allow                              │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  3. ACT ───── Execute approved tool call                   │
│         │                                                   │
│         ▼                                                   │
│  4. REFLECT ─ Feed result back to LLM                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Testing Strategy

### 7.1 HIL Testing (Outside Sandbox)

**Purpose:** Test HIL system in real environment before production

1. **Unit tests** - HIL decision logic per config
2. **Integration tests** - HIL intercepts in ReAct loop
3. **Manual tests** - Interactive prompts in Friday Chat

**Test commands:**
```bash
# Test safe command bypass
grep "test" ./README.md  # Should execute without prompt

# Test HIL prompt
rm -rf ./temp_dir        # Should prompt (if rm not in safe_commands)
```

### 7.2 Beads/Dolt Testing

```bash
# Initialize workspace
bd init --workspace friday_test

# Create task
bd task create --title "Test task" --description "Testing HIL integration"

# Verify in Dolt
dolt sql -q "SELECT * FROM tasks"
```

---

## 8. Acceptance Criteria

- [ ] HIL intercepts tool calls according to config
- [ ] `safe_commands` execute without prompts
- [ ] `exempt_tools` execute without prompts
- [ ] `ask_once_commands` prompt once, then auto-approve
- [ ] Option [3] adds command hash to session trust store
- [ ] YOLO mode bypasses all prompts
- [ ] Audit log records all decisions
- [ ] Beads creates and dispatches tasks
- [ ] Dolt stores task state with version history
- [ ] Friday Chat operates in interactive mode
- [ ] Autonomous mode logs decisions without prompting

---

## 9. Open Questions

1. Should `ask_once` approval persist across restarts?
2. What is the default timeout for semi-autonomous mode?
3. Should blocked_commands throw errors or return empty results?
4. How to handle Dolt merge conflicts from concurrent agents?

---

## 10. References

- Beads: https://github.com/beads/beads (v1.9.0)
- Dolt: https://github.com/dolthub/dolt (v1.84.0)
- GasTown: Steve Yegge's multi-agent orchestration system
- ReAct: Synergizing Reasoning and Acting in Language Models
