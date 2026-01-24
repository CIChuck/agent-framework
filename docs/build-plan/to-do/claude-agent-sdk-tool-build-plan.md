# Build Plan: Claude Agent SDK Tools for Friday

**Status:** Approved
**Target Package:** `friday-tools`
**Objective:** Add Friday-tools that integrate with Claude Code via the Claude Agent SDK, enabling task delegation, code generation with sandbox execution, YOLO mode (unsandboxed execution), and dynamic tool generation.

---

## 1. Problem Statement

Friday currently operates as a standalone agent. For complex, exploratory coding tasks, Friday could benefit from delegating work to Claude Code—a specialized coding agent with deep file system access, code search, and execution capabilities.

**Current limitation:** No mechanism for Friday to invoke other AI agents as tools.

**Proposed solution:** Integrate the Claude Agent SDK as Friday-tools, enabling:
- Task delegation to a specialized coding agent
- Code generation with sandbox execution
- YOLO mode for direct execution with full Friday context access
- Dynamic tool generation based on BaseTool specification

---

## 2. Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Integration approach | Python SDK (`claude-code-sdk`) | More powerful than CLI, enables streaming and custom options |
| Session type | One-shot (stateless) | Simpler, cleaner separation, no state management complexity |
| Use cases | All (delegation, codegen, YOLO, tool generation) | Maximum flexibility for different workflows |
| YOLO safety | Full trust (no safety checks) | User-requested for controlled environments |

---

## 3. Architecture

### Tool 1: ClaudeAgentTool (General Delegation)
```
┌─────────────────────────────────────────────────────────────┐
│ Friday Agent                                                │
│   ↓                                                         │
│ ClaudeAgentTool.execute(prompt, allowed_tools, cwd, ...)   │
│   ↓                                                         │
│ claude_code_sdk.query(prompt, options)                      │
│   ↓                                                         │
│ Claude Code Runtime (bundled with SDK)                      │
│   - Read/Write/Edit files                                   │
│   - Run Bash commands                                       │
│   - Search code (Glob, Grep)                                │
│   - Web search/fetch                                        │
└─────────────────────────────────────────────────────────────┘
```

### Tool 2: ClaudeCodeGeneratorTool (Generate + Execute in Sandbox)
```
┌─────────────────────────────────────────────────────────────┐
│ Friday Agent                                                │
│   ↓                                                         │
│ ClaudeCodeGeneratorTool.execute(task, context, execute)     │
│   ↓                                                         │
│ claude_code_sdk.query(code_gen_prompt, options)             │
│   ↓                                                         │
│ Extract Python code from response                           │
│   ↓                                                         │
│ [If execute=True]                                           │
│   ↓                                                         │
│ friday_sandbox.execute(code, timeout, workspace)            │
│   ↓                                                         │
│ ExecutionResult(stdout, stderr, return_value, files)        │
└─────────────────────────────────────────────────────────────┘
```

### Tool 3: ClaudeYoloTool (Generate + Execute UNSANDBOXED)
```
┌─────────────────────────────────────────────────────────────┐
│ Friday Agent                                                │
│   ↓                                                         │
│ ClaudeYoloTool.execute(task, context)                       │
│   ↓                                                         │
│ claude_code_sdk.query(code_gen_prompt, options)             │
│   ↓                                                         │
│ Extract Python code from response                           │
│   ↓                                                         │
│ exec(code, friday_globals)  ← DIRECT EXECUTION              │
│   ↓                                                         │
│ Full access to: memory_controller, tools, session state     │
│   ↓                                                         │
│ Returns: execution result + any side effects                │
└─────────────────────────────────────────────────────────────┘

⚠️  FULL TRUST MODE - No safety checks. Code runs in Friday's process.
```

### Tool 4: ClaudeToolGeneratorTool (Create New Friday Tools)
```
┌─────────────────────────────────────────────────────────────┐
│ User: "Create a tool to query our internal API"             │
│   ↓                                                         │
│ ClaudeToolGeneratorTool.execute(tool_spec, name)            │
│   ↓                                                         │
│ claude_code_sdk.query(tool_gen_prompt, options)             │
│   - Reads: BaseTool spec, existing tool examples            │
│   - Generates: Complete tool class + tests                  │
│   ↓                                                         │
│ Write to: friday_tools/generated/{name}.py                  │
│   ↓                                                         │
│ Tool available for future use (may require restart)         │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Use Cases

### PRIMARY USE CASE: Code Generation & Execution

**Dynamic Script Generation & Execution** ⭐ *Key Use Case*

User: "Analyze the sales.csv file and find the top 10 customers by revenue"
- Friday invokes `ClaudeCodeGeneratorTool` with task description
- Claude Code reads the CSV structure, generates pandas analysis code
- Friday executes the code in sandbox with 30s timeout
- Results returned: top 10 customers with revenue figures
- **No manual code review** - sandbox provides safety guarantees

**Example flow:**
```
User: "Parse the JSON logs in /tmp/logs/ and count errors by type"
  ↓
Claude Code generates:
  import json, glob
  from collections import Counter
  errors = Counter()
  for f in glob.glob('/tmp/logs/*.json'):
      data = json.load(open(f))
      if data.get('level') == 'error':
          errors[data.get('type', 'unknown')] += 1
  __friday_result__ = dict(errors.most_common(10))
  ↓
Sandbox executes → Returns: {"TypeError": 45, "ValueError": 23, ...}
```

### Other Use Cases (ClaudeAgentTool)

1. **Codebase Exploration & Onboarding** - Deep codebase analysis delegation
2. **Parallel Multi-Repository Analysis** - Simultaneous analysis across repos
3. **Automated Code Review** - Security and quality review delegation
4. **Refactoring Scout** - Identify refactoring opportunities
5. **Test Generation Delegation** - Generate unit tests
6. **Documentation Generation** - Generate/update documentation
7. **Dependency Audit** - Check for outdated/vulnerable dependencies
8. **Migration Planning** - Analyze migration requirements
9. **Performance Profiling Analysis** - Find performance bottlenecks
10. **CI/CD Pipeline Debugging** - Debug build failures

---

## 5. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `packages/friday-tools/src/friday_tools/external/__init__.py` | Create | New external tools category |
| `packages/friday-tools/src/friday_tools/external/claude_agent.py` | Create | ClaudeAgentTool (general delegation) |
| `packages/friday-tools/src/friday_tools/external/claude_codegen.py` | Create | ClaudeCodeGeneratorTool (generate + execute) |
| `packages/friday-tools/src/friday_tools/external/claude_yolo.py` | Create | ClaudeYoloTool (unsandboxed execution) |
| `packages/friday-tools/src/friday_tools/external/claude_toolgen.py` | Create | ClaudeToolGeneratorTool (dynamic tool creation) |
| `packages/friday-tools/src/friday_tools/generated/` | Create | Directory for dynamically generated tools |
| `packages/friday-tools/pyproject.toml` | Modify | Add `claude-code-sdk` optional dependency |
| `packages/friday-tools/tests/test_claude_agent.py` | Create | Unit tests for all 4 tools |

**Existing infrastructure (no changes needed):**
- `packages/friday-sandbox/` - DockerSandbox, SubprocessSandbox already implemented
- `packages/friday-tools/src/friday_tools/codegen/` - Code extraction patterns
- `packages/friday-tools/src/friday_tools/definition.py` - BaseTool for tool generation reference

---

## 6. Tool Interfaces

### ClaudeAgentTool Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Task description for Claude Code |
| `cwd` | string | No | Current dir | Working directory |
| `allowed_tools` | array | No | `["Read", "Glob", "Grep", "Bash"]` | Tools Claude Code can use |
| `disallowed_tools` | array | No | `[]` | Tools to block |
| `max_turns` | integer | No | 10 | Max agentic turns |
| `timeout` | integer | No | 300 | Timeout in seconds |

### ClaudeCodeGeneratorTool Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `task` | string | Yes | - | Description of what the code should do |
| `context` | string | No | "" | Additional context (file contents, data samples) |
| `execute` | boolean | No | True | Execute generated code in sandbox |
| `cwd` | string | No | Current dir | Working directory for Claude Code |
| `sandbox_timeout` | integer | No | 30 | Sandbox execution timeout in seconds |

### ClaudeYoloTool Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `task` | string | Yes | - | Description of what the code should do |
| `context` | string | No | "" | Additional context for code generation |
| `cwd` | string | No | Current dir | Working directory for Claude Code |

### ClaudeToolGeneratorTool Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `tool_name` | string | Yes | - | Name for the new tool (snake_case) |
| `tool_description` | string | Yes | - | Brief description of what the tool does |
| `purpose` | string | Yes | - | Detailed explanation of purpose and use cases |
| `context` | string | No | "" | Additional context (API docs, examples) |
| `cwd` | string | No | Current dir | Working directory for Claude Code |
| `dry_run` | boolean | No | False | If true, return code without writing to file |

---

## 7. Usage Examples

### Code Generation & Execution (Primary Use Case)
```python
result = await claude_codegen_tool.execute(
    task="Read sales.csv and calculate total revenue by region",
    context="CSV has columns: date, region, product, quantity, price",
    execute=True,
    sandbox_timeout=30,
)
```

### Basic Task Delegation
```python
result = await claude_agent_tool.execute(
    prompt="Analyze the authentication flow in src/auth/",
    cwd="/path/to/project",
    allowed_tools=["Read", "Glob", "Grep"],
    timeout=120,
)
```

### YOLO Mode - Direct Execution
```python
yolo_tool = ClaudeYoloTool()
yolo_tool.set_context({
    "memory_controller": memory_controller,
    "tools": tool_registry.tools,
    "session": session_state,
})

result = await yolo_tool.execute(
    task="Add a new memory about the user preferring dark mode UI",
    context="User just said they like dark interfaces",
)
```

### Dynamic Tool Generation
```python
result = await toolgen_tool.execute(
    tool_name="internal_api_query",
    tool_description="Query our internal REST API",
    purpose="Fetch data from internal.company.com/api with auth headers",
    context="API uses Bearer tokens from env var INTERNAL_API_KEY",
    dry_run=True,  # Review first
)
```

---

## 8. Verification Plan

1. **Install SDK:** `pip install claude-code-sdk`
2. **Run unit tests:** `pytest packages/friday-tools/tests/test_claude_agent.py -v`
3. **Test ClaudeAgentTool:** Basic delegation task
4. **Test ClaudeCodeGeneratorTool:** Generate + execute Fibonacci code
5. **Test ClaudeYoloTool:** Direct execution with mock context
6. **Test ClaudeToolGeneratorTool:** Dry run tool generation
7. **Integration test:** Use tools via Friday

---

## 9. Risks & Mitigations

| Tool | Risk Level | Mitigation |
|------|------------|------------|
| ClaudeAgentTool | Low | Claude Code has its own sandboxing |
| ClaudeCodeGeneratorTool | Low | Executes in friday-sandbox |
| ClaudeYoloTool | **HIGH** | Full trust only, user choice |
| ClaudeToolGeneratorTool | Medium | dry_run for review, validation |

### YOLO Mode Considerations

⚠️ **ClaudeYoloTool runs generated code WITHOUT ANY SANDBOX.**

- Code executes directly in Friday's Python process
- Full access to memory_controller, tools, session state, file system, network
- No resource limits, no timeouts on execution (only on generation)
- User explicitly chose "Full trust" mode - no safety prompts

**Intended use cases:**
- Memory manipulation (adding/removing memories)
- Tool orchestration (calling multiple tools in sequence)
- Dynamic configuration changes
- Complex automation that needs Friday context

**NOT recommended for:**
- Processing untrusted input
- Tasks from unknown users
- Production environments without human oversight

### Tool Generation Considerations

- Generated tools go to `packages/friday-tools/src/friday_tools/generated/`
- Tools follow BaseTool contract and can be loaded dynamically
- Code validation checks for basic structure but doesn't guarantee safety
- Use `dry_run=True` first to review generated code

---

## 10. Notes

- **API Key:** Uses `ANTHROPIC_API_KEY` (same as Claude Code CLI)
- **Isolation:** Each invocation is stateless; no shared context between calls
- **Costs:** Each invocation uses API credits; monitor usage
- **Tool restrictions:** Use `allowed_tools` to limit scope and cost
- **Dependency:** `claude-code-sdk` is an optional dependency (`pip install friday-tools[claude-agent]`)
