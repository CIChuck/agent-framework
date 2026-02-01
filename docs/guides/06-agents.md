# Friday Agent Framework
## Section 6: Agents - Configuration & Capabilities

**Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-01-24

---

## Overview

Agents are the active intelligence layer of Friday—the entities that combine memory, reasoning, and tools to accomplish tasks. While the memory system provides context and tools enable action, agents orchestrate the interaction between these components to achieve goals.

Friday's agent system is built on a **configuration-driven architecture** that separates agent identity and capabilities from implementation code. Through YAML-based profiles, you can define specialized agents for different roles—researchers, coders, reviewers, analysts—each with customized behavior, tool access, and memory strategies.

**This section covers:**
- Agent types and architectural patterns (CopilotAgent, AutonomousAgent)
- Complete agent configuration via YAML profiles
- Tool permission management and security boundaries
- Memory mode configuration for different use cases
- Agent lifecycle, state management, and orchestration

**For Project Leaders:** Agents represent the customizable "personalities" of your AI system. Understanding agent configuration enables you to design specialized AI teams for different business functions—customer support, content creation, data analysis, code review—each optimized for its role while sharing organizational memory.

**For IT Leaders:** Agent configuration determines security boundaries (tool access), resource consumption (model selection, memory modes), and operational behavior (autonomy levels). The YAML-based configuration enables version control, environment-specific deployment, and separation of configuration from code.

**For Users:** Think of agents as specialized colleagues, each with distinct expertise and access. A "researcher" agent has web search tools and broad context, while a "coder" agent has filesystem access and code execution capabilities. Understanding agent capabilities helps you route tasks effectively.

---

## 6.1 Agent Types & Patterns

Friday implements agents as specialized executors with distinct operational patterns. The framework currently supports interactive copilot agents (production-ready) and has planned support for autonomous agents (future development).

### 6.1.1 CopilotAgent: Interactive Re-Act Pattern

**Architecture:** Think → Tool → Observe Loop

The `CopilotAgent` is Friday's flagship implementation, designed for **human-in-the-loop workflows** where an agent assists a user with tasks step-by-step. It implements the Re-Act (Reasoning and Acting) pattern from academic research.

**Re-Act Loop Flow:**

```
┌──────────────────────────────────────────────────────────────┐
│                    COPILOT AGENT FLOW                        │
│                                                              │
│  1. OBSERVE                                                  │
│     └─ User Query + Retrieved Context                       │
│        ├─ Episodic Memory (recent conversation)             │
│        ├─ Semantic Memory (relevant insights)               │
│        └─ Associative Memory (entities/relationships)       │
│                                                              │
│  2. THINK                                                    │
│     └─ LLM Reasoning                                         │
│        ├─ Analyze the task                                   │
│        ├─ Decide next action                                 │
│        └─ Select tool(s) if needed                           │
│                                                              │
│  3. ACT (Optional)                                           │
│     └─ Tool Execution                                        │
│        ├─ Call selected tools                                │
│        ├─ Gather results                                     │
│        └─ Handle errors gracefully                           │
│                                                              │
│  4. OBSERVE (Results)                                        │
│     └─ Feed tool outputs back to LLM                         │
│                                                              │
│  5. REPEAT or RESPOND                                        │
│     └─ If task incomplete: Loop back to THINK                │
│     └─ If task complete: Generate final response             │
│                                                              │
│  6. LEARN                                                    │
│     └─ Archive turn to episodic memory                       │
│     └─ Extract entities/insights (async)                     │
│                                                              │
│  Max Iterations: 10 (prevents infinite loops)               │
└──────────────────────────────────────────────────────────────┘
```

**Implementation Details:**

```python
# From packages/friday-agent/src/friday_agent/copilot.py
class CopilotAgent(AgentBase):
    """
    Interactive agent using the Re-Act pattern.

    Executes a Think → Tool → Observe loop until the LLM
    produces a final response without tool calls.
    """

    MAX_ITERATIONS: int = 10  # Circuit breaker

    async def run(self, input_signal: str) -> str:
        # 1. Assemble context (memory + tools)
        context_payload = await self.context_engine.assemble_context(
            query=input_signal,
            state=self.session_state,
            budget_limit=budget_limit,
        )

        # 2. Format prompt with system instructions
        messages = await self.context_engine.format_prompt(
            system_prompt=self.profile.render_system_prompt(),
            payload=context_payload,
        )

        # 3. Add user message
        messages.append({"role": "user", "content": input_signal})

        # 4. Execute Re-Act loop
        iteration = 0
        while iteration < self.MAX_ITERATIONS:
            iteration += 1

            # Call LLM with tool schemas
            response = await self.llm.chat_completion(
                messages=messages,
                tools=tool_schemas,
                temperature=self.profile.temperature,
            )

            # Check if LLM wants to use tools
            if response.has_tool_calls:
                # Execute tools and continue loop
                for tool_call in response.tool_calls:
                    result = await self._execute_tool_call(
                        tool_call.name,
                        tool_call.arguments,
                    )
                    # Add tool result to messages
                    messages.append(...)
                continue
            else:
                # Final response ready
                final_response = response.content

                # Archive the complete turn
                await self._archive_turn(
                    user_message=input_signal,
                    assistant_message=final_response,
                    tool_calls=accumulated_tool_calls,
                    tool_results=accumulated_tool_results,
                )

                return final_response

        # Max iterations exceeded
        raise RuntimeError("Agent exceeded maximum iterations")
```

**Key Characteristics:**

1. **Human Confirmation Implicit**: Each user query triggers one Re-Act cycle; user must explicitly provide next input for agent to continue
2. **Tool Safety**: Maximum iteration limit prevents runaway execution and excessive API costs
3. **Transparency**: Full tool call history preserved in transcripts for audit and debugging
4. **Streaming Support**: Planned for real-time response display (currently returns complete response)
5. **Memory Integration**: Every turn archived to episodic memory; extraction runs asynchronously

**Circuit Breakers:**

CopilotAgent includes multiple safety mechanisms:
- **Iteration Limit**: Max 10 tool-use iterations per user query
- **Token Budget**: Context assembly respects LLM window limits
- **Timeout**: Tool execution has configurable timeouts (default 30s)
- **Error Handling**: Tool failures return error messages to LLM rather than crashing

**Use Cases:**

| Use Case | Why CopilotAgent | Configuration Notes |
|----------|------------------|---------------------|
| Research Assistant | User guides research direction; agent performs searches | High temperature (0.7), extended context |
| Code Generator | User reviews generated code before execution | Low temperature (0.2), code tools only |
| Data Analysis | User verifies queries before running | Medium temperature (0.5), read-only data tools |
| Content Creation | User iterates on drafts with agent | High temperature (0.8), writing tools |
| Customer Support | Agent suggests responses; human approves | Low temperature (0.3), CRM/knowledge base tools |

**Example Interaction Flow:**

```
User: "Find recent papers on transformer architectures and summarize key innovations"

Turn 1:
  Agent THINK: I need to search for recent papers
  Agent ACT: web_search("transformer architectures recent papers 2024")
  Agent OBSERVE: [Search results with 10 papers]
  Agent THINK: I should read the top 3 papers
  Agent ACT: read_page(url_1), read_page(url_2), read_page(url_3)
  Agent OBSERVE: [Paper contents]
  Agent THINK: Now I can synthesize findings
  Agent RESPOND: "Based on recent research, key innovations include..."

Memory: Entities extracted (Papers, Authors, Techniques)
        Insights stored ("User interested in transformer research")
        Full turn archived to SQLite

User: "Can you compare these to the original Attention Is All You Need paper?"

Turn 2:
  Agent OBSERVE: (Primed with entities from Turn 1)
  Agent THINK: User wants comparison; I remember the papers from Turn 1
  Agent ACT: read_page("attention_is_all_you_need_url")
  Agent OBSERVE: [Original paper content]
  Agent RESPOND: "Comparing the 2017 original to recent work..."
```

**For Project Leaders:** CopilotAgent is production-ready and battle-tested. Use it for any workflow where human oversight is valuable—either for safety (code deployment, data modification) or quality (content review, decision-making). The human-in-the-loop pattern prevents autonomous mistakes while maximizing AI productivity.

**For IT Leaders:** CopilotAgent's circuit breakers make it suitable for production deployment. The 10-iteration limit caps worst-case API costs per user query. Tool execution timeouts prevent resource exhaustion. All tool calls are logged for security audit.

---

### 6.1.2 AutonomousAgent: Event-Driven Execution (Planned)

**Status:** Placeholder implementation; full development planned for future batch

**Architecture:** Goal Decomposition → Self-Directed Execution

The `AutonomousAgent` is designed for **long-running background tasks** that don't require turn-by-turn human confirmation. Unlike CopilotAgent which waits for user input after each response, AutonomousAgent executes a complete goal autonomously.

**Conceptual Flow:**

```
┌──────────────────────────────────────────────────────────────┐
│               AUTONOMOUS AGENT FLOW (PLANNED)                │
│                                                              │
│  1. GOAL ANALYSIS                                            │
│     └─ Break high-level goal into sub-tasks                  │
│        ├─ Identify dependencies                              │
│        ├─ Estimate complexity                                │
│        └─ Plan execution order                               │
│                                                              │
│  2. TASK EXECUTION                                           │
│     └─ Execute tasks in dependency order                     │
│        ├─ Self-select tools for each task                    │
│        ├─ Handle errors with retry logic                     │
│        └─ Checkpoint progress continuously                   │
│                                                              │
│  3. SELF-MONITORING                                          │
│     └─ Track progress toward goal                            │
│        ├─ Detect failures/blockers                           │
│        ├─ Adjust plan if needed                              │
│        └─ Escalate to human if stuck                         │
│                                                              │
│  4. COMPLETION                                               │
│     └─ Deliver final result                                  │
│        ├─ Summarize work completed                           │
│        ├─ Archive full execution trace                       │
│        └─ Notify stakeholders                                │
│                                                              │
│  Human Intervention: Optional approval gates                │
└──────────────────────────────────────────────────────────────┘
```

**Planned Features:**

1. **Goal Decomposition**: LLM breaks high-level objective into actionable sub-tasks
2. **Dependency Management**: Task graph execution respects prerequisites
3. **Progress Checkpointing**: Crash recovery from last successful step
4. **Error Recovery**: Automatic retries with exponential backoff
5. **Escalation Protocol**: Request human help when confidence drops below threshold
6. **Resource Budgets**: Total token/time limits for entire goal execution

**Current Implementation:**

```python
# From packages/friday-agent/src/friday_agent/autonomous.py
class AutonomousAgent(AgentBase):
    """
    Placeholder for autonomous agent implementation.

    Future implementation will support:
    - Goal decomposition into sub-tasks
    - Self-directed execution without human confirmation
    - Long-running background task processing
    - Progress checkpointing and recovery
    """

    async def run(self, input_signal: Any) -> Any:
        raise NotImplementedError(
            "AutonomousAgent is a placeholder for future development. "
            "Use CopilotAgent for interactive workflows."
        )
```

**Planned Use Cases:**

| Use Case | Why AutonomousAgent | Safety Considerations |
|----------|---------------------|----------------------|
| Scheduled Reports | Run weekly without human trigger | Read-only tools, sandboxed data access |
| Data Pipeline Monitoring | Autonomous alert/fix workflows | Approval gate for data modifications |
| Competitive Intelligence | Daily competitor monitoring | Rate limits, robots.txt compliance |
| Code Refactoring | Large-scale codebase improvements | Git branch isolation, test requirement |
| Document Processing | Batch processing uploaded files | File size limits, malware scanning |

**Safety Model (Planned):**

Autonomous execution requires additional safeguards:

1. **Approval Gates**: Configure specific tasks that require human confirmation
   ```yaml
   approval_gates:
     - action: "delete_*"  # Any deletion requires approval
     - cost_threshold: 1000  # Tasks over $10 in API costs
     - confidence_threshold: 0.7  # Low confidence decisions
   ```

2. **Rollback Mechanism**: Checkpoint state before destructive operations
3. **Sandbox Execution**: Run in isolated environment (Docker container)
4. **Resource Limits**: Cap total token usage, execution time, tool calls
5. **Audit Trail**: Detailed logging of all autonomous decisions

**Development Timeline:**

| Phase | Feature | Status |
|-------|---------|--------|
| Phase 1 | Goal decomposition algorithm | Planned |
| Phase 2 | Task graph executor | Planned |
| Phase 3 | Checkpoint/recovery system | Planned |
| Phase 4 | Approval gate integration | Planned |
| Phase 5 | Production deployment | Planned |

**For Project Leaders:** AutonomousAgent will enable Friday to handle background workflows that currently require human initiation. This unlocks use cases like scheduled reporting, continuous monitoring, and batch processing. Wait for production release before deploying to critical workflows.

**For IT Leaders:** Autonomous execution introduces new security and reliability concerns. Plan for additional infrastructure (sandboxing, checkpointing storage, approval workflow) and monitoring (execution tracing, cost tracking, failure alerting) before deploying autonomous agents.

---

### 6.1.3 Comparison: When to Use Which Agent

| Dimension | CopilotAgent | AutonomousAgent (Planned) |
|-----------|--------------|---------------------------|
| **Interaction Model** | Human-in-the-loop (synchronous) | Background execution (asynchronous) |
| **Initiation** | User sends message | Event trigger or schedule |
| **Approval** | Implicit per turn | Explicit gates for sensitive operations |
| **Task Scope** | Single conversation turn | Multi-step workflows |
| **Execution Time** | Seconds to minutes | Minutes to hours |
| **Tool Calls** | Up to 10 per turn | Unlimited (within budget) |
| **Error Handling** | Return error to user | Retry, escalate, or rollback |
| **Use Case** | Interactive assistance | Automated workflows |
| **Production Status** | ✅ Stable | 🚧 Planned |

**Decision Framework:**

```
Does the task require human judgment at each step?
├─ YES → CopilotAgent
│  Examples: Code review, content creation, strategic decisions
│
└─ NO → Can it run unattended?
   ├─ YES → AutonomousAgent (when available)
   │  Examples: Data pipelines, scheduled reports, monitoring
   │
   └─ NO → Consider workflow with approval gates
      Examples: Deployments, financial transactions, data deletion
```

**Hybrid Patterns:**

You can combine both agent types in workflows:

1. **Research → Review**: AutonomousAgent gathers data overnight, CopilotAgent assists with analysis the next day
2. **Draft → Edit**: AutonomousAgent generates first draft, CopilotAgent iterates with user feedback
3. **Monitor → Investigate**: AutonomousAgent detects anomaly, escalates to CopilotAgent for human investigation

---

## 6.2 Agent Configuration with YAML

Friday agents are defined via YAML configuration files that specify identity, capabilities, tool access, model parameters, and memory strategies. This **configuration-as-code** approach enables version control, environment-specific profiles, and team collaboration on agent design.

### 6.2.1 Agent Profile Schema (Complete Reference)

**File Location:** `agents/<agent_name>.yaml`

**Full Schema:**

```yaml
# ==============================================================================
# IDENTITY: Who is this agent?
# ==============================================================================
name: researcher                # REQUIRED: Must match filename (researcher.yaml)
role: "Research Analyst"        # REQUIRED: Role description for prompt
goal: "Find and synthesize information"  # REQUIRED: Primary objective

# System prompt with template variables
system_prompt: |                # REQUIRED: Instructions to the LLM
  You are a research analyst specializing in {{domain}}.

  Your task is to find accurate, relevant information and present it clearly.

  Guidelines:
  - Always cite sources when possible
  - Distinguish between facts and opinions
  - Acknowledge uncertainty when information is incomplete
  - Cross-reference multiple sources for accuracy
  - Summarize findings in a clear, structured format

  Current research focus: {{focus}}

# ==============================================================================
# CAPABILITIES: What can this agent do?
# ==============================================================================
tools:                          # List of tool names from registry
  - web_search                  # Tools available to this agent
  - read_file
  - recall_memory
  - store_fact
  - search_documents

tool_autonomy: auto             # How tools are selected: "manual", "auto", "hybrid"
                                # - manual: Only listed tools, no self-selection
                                # - auto: Agent selects from available_tools pool
                                # - hybrid: Listed tools + can expand from pool

injected_tools: []              # Tools always included (for manual/hybrid modes)
available_tools: []             # Pool for auto-selection (for auto/hybrid modes)
required_tools: []              # Tools that must always be included

# ==============================================================================
# MODEL CONFIGURATION: How does this agent think?
# ==============================================================================
temperature: 0.3                # Sampling temperature (0.0-2.0)
                                # - 0.0-0.3: Deterministic, factual
                                # - 0.4-0.7: Balanced
                                # - 0.8-2.0: Creative, diverse

max_tokens: 8192                # Maximum response length
                                # Model limits: GPT-4: 4096-128K, Claude: 4096-200K

context_strategy: extended      # Context assembly strategy
                                # - minimal: Minimal context (fast, cheap)
                                # - standard: Balanced context
                                # - extended: Maximum context (thorough, expensive)

# ==============================================================================
# MEMORY CONFIGURATION: What does this agent remember?
# ==============================================================================
memory_config:
  enable_graph: true            # Use associative graph store
  enable_vector: true           # Use semantic vector store
  enable_episodic: true         # Use conversation history (default: true)
  max_episodic_turns: 30        # How many recent turns to load

  namespace: "research_team"    # Memory namespace (isolates memories)
                                # - null/omit: No isolation (default)
                                # - "team_name": Share with specific team
                                # - "agent_name": Private to this agent

  priming_depth: 10             # How many entities to prime on session start
  decay_rate: 0.01              # Memory decay lambda (higher = faster decay)

# ==============================================================================
# REGISTRY INTEGRATION: How is this agent discovered?
# ==============================================================================
capabilities:                   # Capability tags for orchestrator routing
  - research
  - information_gathering
  - fact_checking
  - summarization
  - citation

# ==============================================================================
# METADATA: Additional information
# ==============================================================================
metadata:
  version: "1.0.0"              # Agent version (semantic versioning)
  author: "friday-team"         # Creator/maintainer
  tags:                         # Additional classification tags
    - core
    - research
  description: |                # Human-readable description
    Research agent specializing in web-based information gathering
    and multi-source synthesis with citation tracking.

  # Custom metadata (application-specific)
  domain: "general"             # Can be used in system_prompt template
  focus: "current events"       # Template variable
  supported_languages:          # Arbitrary nested metadata
    - english
    - spanish
```

**Field Requirements:**

| Field | Required | Type | Default | Validation |
|-------|----------|------|---------|------------|
| `name` | ✅ Yes | string | - | Must match filename |
| `role` | ✅ Yes | string | - | Non-empty |
| `goal` | ✅ Yes | string | - | Non-empty |
| `system_prompt` | ✅ Yes | string | - | Supports {{variable}} templates |
| `tools` | ❌ No | list[string] | `[]` | Must exist in registry |
| `tool_autonomy` | ❌ No | enum | `"manual"` | "manual", "auto", "hybrid" |
| `temperature` | ❌ No | float | `0.7` | 0.0 to 2.0 |
| `max_tokens` | ❌ No | int | null | Respects model limits |
| `context_strategy` | ❌ No | enum | `"standard"` | "minimal", "standard", "extended" |
| `capabilities` | ❌ No | list[string] | `[]` | Freeform tags |
| `memory_config` | ❌ No | dict | `{}` | See memory section |
| `metadata` | ❌ No | dict | `{}` | Freeform nested data |

**Template Variables:**

The `system_prompt` field supports Jinja2-style template variables:
- **Built-in variables**: `{{name}}`, `{{role}}`, `{{goal}}` (auto-populated from profile)
- **Custom variables**: Any key in `metadata` section (e.g., `{{domain}}`, `{{focus}}`)
- **Runtime variables**: Can be passed when rendering prompt

```python
# Template rendering
prompt = profile.render_system_prompt(
    domain="artificial intelligence",  # Override metadata value
    current_date="2026-01-24",         # Add runtime variable
)
```

**Validation:**

The `AgentLoader` validates profiles on load:

```python
# From packages/friday-agent/src/friday_agent/loader.py
class AgentLoader:
    REQUIRED_FIELDS = ["name", "role", "goal", "system_prompt"]

    def _validate_types(self, config: dict, path: Path) -> None:
        # Type checking
        assert isinstance(config["name"], str)
        assert isinstance(config["tools"], list)
        assert 0 <= config.get("temperature", 0.7) <= 2

        # Enum validation
        assert config.get("tool_autonomy") in ("manual", "auto", "hybrid", None)
        assert config.get("context_strategy") in ("minimal", "standard", "extended", None)

        # Name matches filename
        assert config["name"] == path.stem
```

**Error Handling:**

Invalid configurations raise `AgentConfigError` with helpful messages:

```
AgentConfigError: agents/researcher.yaml: Agent name 'researcher_v2' must match filename 'researcher'
AgentConfigError: agents/coder.yaml: Missing required fields: ['system_prompt']
AgentConfigError: agents/analyst.yaml: Field 'temperature' must be a number
AgentConfigError: agents/writer.yaml: tool_autonomy must be 'manual', 'auto', or 'hybrid'
```

**For Project Leaders:** YAML configuration enables non-developers (product managers, domain experts) to contribute to agent design. Version control provides audit trail of agent behavior changes. Environment-specific profiles (dev vs. prod) enable testing without risk.

**For IT Leaders:** Schema validation prevents deployment of misconfigured agents. Required fields enforce complete specifications. Type checking catches errors at load time rather than runtime. Consider CI/CD validation of agent configs before deployment.

---

### 6.2.2 Tool Permission Management

Tools represent the primary security boundary for agents—they determine what an agent can actually *do* in the real world. Friday provides fine-grained tool access control via the `tools` configuration field and related settings.

**Permission Models:**

1. **Explicit Allowlist** (most secure)
2. **Category-Based Selection**
3. **Wildcard Patterns**
4. **Tool Autonomy Modes**

#### Explicit Allowlist (Manual Mode)

**Configuration:**

```yaml
name: readonly_agent
tool_autonomy: manual           # Agent cannot self-select tools
tools:                          # Explicit list of allowed tools
  - read_file
  - list_directory
  - search_files
  - recall_memory
  # No write_file, execute_command, or network tools
```

**Behavior:**
- Agent can ONLY use the listed tools
- Attempting to call unlisted tools will fail gracefully
- LLM only sees schemas for allowed tools (reduces prompt length)
- Most secure option for untrusted or high-risk scenarios

**Use Cases:**
- Customer support agents (no data modification)
- Code review agents (read-only access)
- Research agents on sensitive data (no external network)

#### Category-Based Selection

Friday tools are organized by category. You can grant access to entire categories:

```yaml
tools:
  - filesystem.*    # All filesystem tools
  - web.*          # All web/network tools
  - git.*          # All git tools
```

**Built-in Categories:**

| Category | Tools Included | Risk Level |
|----------|----------------|------------|
| `filesystem.*` | read_file, write_file, list_directory, delete_file, move_file, append_file, search_files, get_file_info | 🟡 Medium (data modification) |
| `web.*` | http_request, web_search, scrape_page, download_file | 🟡 Medium (external access, rate limits) |
| `git.*` | git_status, git_commit, git_push, git_pull, git_diff, git_log, git_checkout | 🔴 High (code modification, remote push) |
| `shell.*` | execute_command, run_script | 🔴 High (arbitrary code execution) |
| `data.*` | parse_json, parse_yaml, parse_xml, csv_operations, jq_query, xml_query | 🟢 Low (read-only parsing) |
| `text.*` | regex_search, regex_replace, text_transform, format_text | 🟢 Low (string operations) |
| `code.*` | run_python, analyze_code, format_code, lint_code | 🔴 High (code execution) |

**Example:**

```yaml
name: web_researcher
tools:
  - web.*           # All web tools
  - data.*          # All data parsing tools
  - recall_memory   # Specific tool outside categories
```

#### Wildcard Patterns

Use glob-style wildcards for fine-grained selection:

```yaml
tools:
  - read_*         # read_file, read_page, etc.
  - git_status     # Explicit
  - git_diff
  - git_log        # Read-only git operations
  # Excludes: git_commit, git_push (write operations)
```

**Pattern Syntax:**
- `*` matches any characters
- `?` matches single character
- `[abc]` matches any of a, b, c
- `[!abc]` matches any except a, b, c

**Common Patterns:**

```yaml
# Read-only filesystem
tools:
  - read_*
  - list_*
  - search_*
  - get_*
  # Excludes: write_*, delete_*, move_*

# Safe web access (no downloads)
tools:
  - web_search
  - scrape_page
  # Excludes: download_file, http_request (arbitrary URLs)

# Analysis only (no execution)
tools:
  - analyze_*
  - lint_*
  - format_*
  # Excludes: run_*, execute_*
```

#### Tool Autonomy Modes

The `tool_autonomy` setting controls how tools are selected:

**Manual Mode** (Default):
```yaml
tool_autonomy: manual
tools:
  - read_file
  - write_file
```
- Agent uses ONLY the tools in `tools` list
- No self-selection allowed
- Most secure and predictable

**Auto Mode**:
```yaml
tool_autonomy: auto
available_tools:          # Pool of tools agent can select from
  - read_file
  - write_file
  - web_search
  - parse_json
required_tools:           # Tools always included
  - recall_memory         # Memory tool always available
```
- Agent can self-select from `available_tools` based on task needs
- LLM reasons about which tools are needed and requests them
- `required_tools` are always included (typically memory/logging tools)
- More flexible but less predictable

**Hybrid Mode**:
```yaml
tool_autonomy: hybrid
tools:                    # Base set (always available)
  - read_file
  - recall_memory
available_tools:          # Additional pool for expansion
  - web_search
  - write_file
  - execute_command
```
- Agent starts with `tools` list
- Can expand by selecting from `available_tools` as needed
- Balances predictability (base tools) with flexibility (expansion)

**Implementation:**

```python
# From packages/friday-agent/src/friday_agent/base.py
class AgentBase:
    def _initialize_tools_for_autonomy_mode(self) -> None:
        autonomy = self.profile.tool_autonomy

        if autonomy == "manual":
            # Use only listed tools
            tool_names = self.profile.tools
            self.set_tools_for_task(tool_names)

        elif autonomy == "auto":
            # Start with required tools only
            if self.profile.required_tools:
                self.set_tools_for_task(self.profile.required_tools)
            # Agent will call expand_tools() later based on task

        elif autonomy == "hybrid":
            # Start with injected + required tools
            initial_tools = set(self.profile.injected_tools)
            initial_tools.update(self.profile.required_tools)
            self.set_tools_for_task(list(initial_tools))
            # Agent can call expand_tools() from available_tools pool
```

**When to Use Each Mode:**

| Scenario | Recommended Mode | Rationale |
|----------|------------------|-----------|
| Customer support | Manual | Predictable, secure, auditable |
| Code generation | Manual | Control exactly what code can be executed |
| Research (trusted) | Auto | Flexibility to select research tools as needed |
| Research (untrusted) | Manual | Prevent arbitrary web access or data exfiltration |
| General assistant | Hybrid | Balance between control and flexibility |
| Production deployment | Manual | Deterministic behavior, easier to audit |
| Development/testing | Auto | Rapid iteration, agent-driven tool discovery |

#### Security Best Practices

**Principle of Least Privilege:**
- Grant only the tools absolutely necessary for the agent's role
- Prefer read-only tools when possible
- Use explicit allowlists over wildcards

**Risk Categorization:**

```yaml
# LOW RISK: Data analysis agent
tools:
  - read_file
  - parse_json
  - parse_yaml
  - recall_memory

# MEDIUM RISK: Content creator agent
tools:
  - read_file
  - write_file       # Can modify files
  - web_search       # Can access internet
  - recall_memory

# HIGH RISK: DevOps agent
tools:
  - filesystem.*     # Full filesystem access
  - git.*            # Can commit/push code
  - execute_command  # Can run arbitrary commands
  # WARNING: Only deploy with human approval gates
```

**Isolation Strategies:**

1. **Sandboxing**: Run high-risk agents in Docker containers
   ```yaml
   metadata:
     sandbox:
       enabled: true
       image: "friday-sandbox:latest"
       timeout_seconds: 300
   ```

2. **Network Isolation**: Disable network tools for sensitive data
   ```yaml
   tools:
     - filesystem.*
     - data.*
     # No web.* or http_* tools
   ```

3. **Filesystem Constraints**: Configure allowed paths
   ```yaml
   metadata:
     filesystem:
       allowed_paths:
         - /app/data
         - /app/outputs
       blocked_paths:
         - /etc
         - ~/.ssh
         - /app/config
   ```

**Audit Logging:**

All tool executions are logged to transcripts:

```python
# From transcript
Turn:
  tool_calls:
    - id: "call_abc123"
      name: "write_file"
      arguments: {"file_path": "/data/report.txt", "content": "..."}
  tool_results:
    - tool_call_id: "call_abc123"
      output: "File written successfully: 1234 bytes"
      error: null
```

Query tool usage for security audit:
```sql
-- Find all file write operations
SELECT session_id, timestamp, agent_id, tool_calls
FROM turns
WHERE tool_calls LIKE '%write_file%'
ORDER BY timestamp DESC;

-- Find agents using high-risk tools
SELECT agent_id, COUNT(*) as execution_count
FROM turns
WHERE tool_calls LIKE '%execute_command%'
   OR tool_calls LIKE '%git_push%'
GROUP BY agent_id;
```

**For Project Leaders:** Tool permissions define the "scope of responsibility" for each agent. Design agents with minimal required tools, then expand as needed. Document rationale for high-risk tool grants in agent metadata.

**For IT Leaders:** Implement tool access as defense-in-depth. Combine tool permissions (application layer) with OS-level restrictions (filesystem permissions, network policies, container isolation). Monitor tool usage via transcripts for anomaly detection.

---

### 6.2.3 Model Selection Per Agent

Friday supports configuring different LLM models per agent, enabling cost/capability optimization. Route complex reasoning to premium models, simple tasks to budget models, or sensitive data to local models.

**Model Configuration:**

```yaml
# Option 1: Specify in agent YAML (not yet supported, use global config)
model: "gpt-4o"              # Future feature
extraction_model: "gpt-4o-mini"  # Cheaper model for extraction

# Option 2: Configure globally, override programmatically
# Current approach: Set in config.yaml, all agents share
```

**Current Limitation:**

Friday v0.1.0 uses a **single global LLM client** shared by all agents. Per-agent model selection is planned for a future release.

**Workaround:**

Override model at runtime via profile manipulation:

```python
from friday_llm import LiteLLMService

# Create specialized LLM clients
premium_llm = LiteLLMService(
    model="gpt-4o",
    temperature=0.7,
)

budget_llm = LiteLLMService(
    model="gpt-4o-mini",
    temperature=0.3,
)

# Inject different LLM per agent
researcher_agent = CopilotAgent(
    profile=researcher_profile,
    llm=premium_llm,  # Use expensive model for complex reasoning
    memory=memory,
    context_engine=context_engine,
    tool_registry=registry,
)

classifier_agent = CopilotAgent(
    profile=classifier_profile,
    llm=budget_llm,   # Use cheap model for simple classification
    memory=memory,
    context_engine=context_engine,
    tool_registry=registry,
)
```

**Model Selection Guide:**

| Task Complexity | Recommended Model | Cost per 1M Tokens | Use Cases |
|-----------------|-------------------|-------------------|-----------|
| **High Complexity** | GPT-4o, Claude 3.5 Sonnet | $3-15 | Complex reasoning, creative writing, code architecture |
| **Medium Complexity** | GPT-4o-mini, Claude 3 Haiku | $0.15-0.60 | Standard conversations, data analysis, simple coding |
| **Low Complexity** | Llama 3.1 8B (local), Mistral 7B | $0 (self-hosted) | Classification, extraction, templating |

**Cost Optimization Strategies:**

1. **Tiered Agent Teams**:
   ```
   Senior Architect (GPT-4o) → Plans system design
   ├─ Junior Developer (GPT-4o-mini) → Implements features
   └─ Classifier (Llama 3.1) → Tags and categorizes code
   ```

2. **Task Routing**:
   ```python
   if task.complexity > 0.8:
       agent = premium_reasoning_agent  # GPT-4o
   elif task.complexity > 0.4:
       agent = standard_agent            # GPT-4o-mini
   else:
       agent = budget_agent              # Local Llama 3
   ```

3. **Extraction Offloading**:
   ```yaml
   # Configure separate extraction model (when supported)
   model: "gpt-4o"               # Main reasoning
   extraction_model: "gpt-4o-mini"  # Entity/relationship extraction
   ```

**Temperature Settings Per Use Case:**

Temperature controls output randomness (0.0 = deterministic, 2.0 = very random):

```yaml
# Factual tasks: Low temperature
name: fact_checker
temperature: 0.1              # Highly deterministic
# Use case: Data extraction, classification, fact checking

# Balanced tasks: Medium temperature
name: assistant
temperature: 0.7              # Default balanced
# Use case: General conversation, Q&A, analysis

# Creative tasks: High temperature
name: creative_writer
temperature: 1.2              # More diverse outputs
# Use case: Story writing, brainstorming, idea generation
```

**Context Window Management:**

Different models have different context limits:

| Model | Context Window | Recommended `context_strategy` |
|-------|----------------|-------------------------------|
| GPT-4o | 128K tokens | extended (use full window) |
| GPT-4o-mini | 128K tokens | extended |
| Claude 3.5 Sonnet | 200K tokens | extended |
| Claude 3 Haiku | 200K tokens | standard |
| Llama 3.1 8B | 128K tokens | standard (local memory limits) |
| Llama 3.1 70B | 128K tokens | extended |

```yaml
# Match context strategy to model capabilities
model: "gpt-4o"
max_tokens: 8192              # Long responses
context_strategy: extended    # Load maximum context

# vs.

model: "gpt-4o-mini"
max_tokens: 2048              # Shorter responses
context_strategy: standard    # Balanced context (cheaper)
```

**Local vs. Cloud Models:**

**Cloud Models** (OpenAI, Anthropic, Google):
- **Pros**: Latest capabilities, no infrastructure, high reliability, large context windows
- **Cons**: Cost per token, network latency, data privacy concerns, rate limits

**Local Models** (Ollama, LM Studio, vLLM):
- **Pros**: Zero marginal cost, data privacy, no rate limits, low latency, air-gapped deployment
- **Cons**: Hardware requirements (GPU), model quality lag, smaller context windows, maintenance overhead

**Hybrid Architecture:**

```
┌──────────────────────────────────────────────────────┐
│            HYBRID MODEL ARCHITECTURE                 │
│                                                      │
│  Cloud Models (GPT-4o, Claude)                      │
│  ├─ Complex reasoning                               │
│  ├─ Strategic planning                              │
│  └─ High-stakes decisions                           │
│                                                      │
│  Local Models (Llama 3.1, Mistral)                  │
│  ├─ Entity extraction                               │
│  ├─ Classification/tagging                          │
│  ├─ Template filling                                │
│  └─ Sensitive data processing                       │
│                                                      │
│  Cost Savings: 70-90% vs. all-cloud                 │
│  Privacy: Sensitive data never leaves premises      │
└──────────────────────────────────────────────────────┘
```

**Implementation Example:**

```python
# Configure hybrid LLM routing
def get_llm_for_agent(agent_profile: AgentProfile) -> LLMClient:
    # Route based on agent capabilities
    if "complex_reasoning" in agent_profile.capabilities:
        return cloud_llm_premium  # GPT-4o
    elif "extraction" in agent_profile.capabilities:
        return local_llm          # Llama 3.1 8B
    else:
        return cloud_llm_standard # GPT-4o-mini

researcher_agent = CopilotAgent(
    profile=researcher_profile,
    llm=get_llm_for_agent(researcher_profile),
    ...
)
```

**For Project Leaders:** Model selection is a cost/capability tradeoff. Start with premium models for all agents, measure actual usage patterns, then optimize by routing simple tasks to cheaper models. Budget 70-90% cost reduction with thoughtful model tiering.

**For IT Leaders:** Local models require GPU infrastructure (16GB+ VRAM per model) but eliminate per-token costs. For high-volume deployments (>1M tokens/day), local models pay for themselves within months. For sensitive data, local models eliminate data exfiltration risk.

---

### 6.2.4 Memory Mode Configuration

Agents can be configured with different memory access patterns to optimize for performance, cost, or functionality.

**Memory Modes (via `memory_config`):**

```yaml
# FULL MODE: All memory stores enabled (default)
memory_config:
  enable_graph: true          # Associative memory (entities/relationships)
  enable_vector: true         # Semantic memory (insights/facts)
  enable_episodic: true       # Conversation history
  max_episodic_turns: 20      # Recent turns to load

# VECTOR ONLY: Semantic search, no graph
memory_config:
  enable_graph: false
  enable_vector: true
  enable_episodic: true
  max_episodic_turns: 10

# GRAPH ONLY: Entity/relationship focus
memory_config:
  enable_graph: true
  enable_vector: false
  enable_episodic: true
  max_episodic_turns: 5

# EPISODIC ONLY: Recent conversation only
memory_config:
  enable_graph: false
  enable_vector: false
  enable_episodic: true
  max_episodic_turns: 30

# STATELESS: No memory (each turn independent)
memory_config:
  enable_graph: false
  enable_vector: false
  enable_episodic: false
```

**Mode Comparison:**

| Mode | Graph | Vector | Episodic | Use Cases | Context Assembly Time |
|------|-------|--------|----------|-----------|----------------------|
| **full** | ✅ | ✅ | ✅ | Personal assistants, knowledge workers | ~200ms |
| **vector_only** | ❌ | ✅ | ✅ | Research agents, document Q&A | ~120ms |
| **graph_only** | ✅ | ❌ | ✅ | Relationship-focused agents, CRM | ~100ms |
| **episodic_only** | ❌ | ❌ | ✅ | Short-term tasks, ephemeral agents | ~50ms |
| **stateless** | ❌ | ❌ | ❌ | One-off queries, public chatbots | ~10ms |

**Detailed Configuration Options:**

```yaml
memory_config:
  # Store enablement
  enable_graph: true
  enable_vector: true
  enable_episodic: true

  # Episodic memory settings
  max_episodic_turns: 20        # How many recent turns to include in context
                                # Higher = more continuity, more tokens

  # Vector search settings
  vector_similarity_threshold: 0.7  # Minimum similarity for retrieval (0-1)
  vector_max_results: 10            # Maximum insights to retrieve

  # Graph retrieval settings
  graph_max_entities: 15            # Maximum entities to load
  graph_max_depth: 2                # Relationship traversal depth

  # Namespace isolation
  namespace: null                   # No isolation (default)
  # OR
  namespace: "team_research"        # Shared team namespace
  # OR
  namespace: "agent_researcher"     # Private agent namespace

  # Priming configuration
  priming_depth: 10                 # Entities to load on session start
  priming_enabled: true             # Enable/disable session priming

  # Lifecycle tuning
  decay_rate: 0.01                  # Memory decay lambda
  promotion_threshold: 0.7          # Short-term → long-term threshold
```

**When to Use Each Mode:**

#### Full Mode (Default)
```yaml
memory_config:
  enable_graph: true
  enable_vector: true
  enable_episodic: true
  max_episodic_turns: 20
```

**Use Cases:**
- Personal assistant agents (need full user context)
- Project management agents (track entities + relationships)
- Knowledge workers (build expertise over time)

**Pros:**
- Maximum context richness
- Cross-session continuity
- Entity relationship reasoning
- Semantic search for insights

**Cons:**
- Slower context assembly (~200ms)
- Higher token usage (more context)
- More memory storage (all stores)

#### Vector Only Mode
```yaml
memory_config:
  enable_graph: false
  enable_vector: true
  enable_episodic: true
  max_episodic_turns: 10
```

**Use Cases:**
- Research agents (find relevant documents/insights)
- Document Q&A agents (semantic search over corpus)
- Content recommendation agents

**Pros:**
- Fast semantic search
- Scales to large document corpora
- Good for similarity-based retrieval

**Cons:**
- No entity relationship tracking
- Can't answer "who worked with whom" questions
- Loses structured knowledge representation

#### Graph Only Mode
```yaml
memory_config:
  enable_graph: true
  enable_vector: false
  enable_episodic: true
  max_episodic_turns: 5
```

**Use Cases:**
- CRM agents (customer relationships)
- Project tracking agents (dependencies)
- Social network analysis

**Pros:**
- Fast entity lookup
- Relationship traversal
- Multi-hop reasoning ("Alice knows Bob who works with Charlie")

**Cons:**
- No semantic search
- Can't find "similar insights" without exact entity match
- Loses unstructured knowledge (insights without entities)

#### Episodic Only Mode
```yaml
memory_config:
  enable_graph: false
  enable_vector: false
  enable_episodic: true
  max_episodic_turns: 30
```

**Use Cases:**
- Short-lived task agents
- Customer support (session-only context)
- Chatbots with conversation continuity but no cross-session memory

**Pros:**
- Very fast context assembly (~50ms)
- Minimal storage requirements
- Conversation coherence within session

**Cons:**
- No cross-session memory
- No entity tracking
- No semantic search

#### Stateless Mode
```yaml
memory_config:
  enable_graph: false
  enable_vector: false
  enable_episodic: false
```

**Use Cases:**
- Public-facing chatbots (privacy)
- One-off queries (API endpoints)
- Evaluation/testing (no state pollution)

**Pros:**
- Fastest possible (~10ms context assembly)
- No storage costs
- Complete privacy (no data retention)
- Deterministic behavior (no memory influence)

**Cons:**
- No memory at all
- Can't reference prior conversation
- Each turn independent

**Memory Namespace Isolation:**

Namespaces enable memory isolation/sharing across agents:

```yaml
# No namespace: Global shared memory
memory_config:
  namespace: null

# Team namespace: Share memory within team
memory_config:
  namespace: "research_team"
  # All agents with namespace="research_team" share memories

# Agent namespace: Private memory
memory_config:
  namespace: "agent_researcher"
  # Only this agent sees these memories
```

**Use Case: Multi-Tenant Deployment:**

```yaml
# Agent profile template
name: customer_assistant
memory_config:
  namespace: "customer_{{customer_id}}"  # Isolated per customer
```

```python
# Runtime instantiation with customer context
profile = loader.load("customer_assistant")
profile.memory_config["namespace"] = f"customer_{customer_id}"

agent = CopilotAgent(
    profile=profile,
    memory=memory_controller,
    ...
)
```

**Performance Implications:**

| Mode | Context Assembly | Token Usage | Storage |
|------|------------------|-------------|---------|
| Full | 200ms | 4K-8K tokens | High (all stores) |
| Vector Only | 120ms | 3K-5K tokens | Medium (vector + episodic) |
| Graph Only | 100ms | 2K-4K tokens | Medium (graph + episodic) |
| Episodic Only | 50ms | 1K-3K tokens | Low (SQLite only) |
| Stateless | 10ms | 500-1K tokens | None |

**For Project Leaders:** Memory mode is a tradeoff between contextual richness and performance/cost. Start with full mode for important agents, optimize to lighter modes for high-volume or ephemeral agents. Namespace isolation enables safe multi-tenancy.

**For IT Leaders:** Memory configuration directly impacts operational costs (tokens, storage, latency). Monitor context assembly time and token usage per agent. Use stateless mode for public-facing agents to eliminate privacy concerns. Consider read replicas for vector/graph stores under high read load.

---

## 6.3 Agent Lifecycle & State Management

Agents progress through a lifecycle from configuration loading to instantiation to execution to cleanup. Understanding this lifecycle is essential for reliable deployment.

### 6.3.1 Agent Initialization & Loading

**Lifecycle Stages:**

```
1. CONFIGURATION
   └─ Load YAML from filesystem

2. VALIDATION
   └─ Schema validation, type checking

3. REGISTRATION
   └─ Add to AgentRegistry with metadata

4. INSTANTIATION (on-demand)
   └─ Create agent instance with dependencies

5. SESSION INITIALIZATION
   └─ Initialize memory session, set author

6. EXECUTION
   └─ Process user queries

7. SHUTDOWN
   └─ Cleanup resources, save state
```

**Step 1: Configuration Loading**

```python
from pathlib import Path
from friday_agent import AgentLoader

# Initialize loader
loader = AgentLoader(agents_dir=Path("agents/"))

# Load single agent
researcher_profile = loader.load("researcher")
# Reads agents/researcher.yaml, validates, returns AgentProfile

# Load all agents in directory
all_profiles = loader.load_all()
# Returns: {"researcher": AgentProfile, "coder": AgentProfile, ...}

# List available agents without loading
available = loader.list_available()
# Returns: ["researcher", "coder", "reviewer"]
```

**AgentLoader Features:**

1. **Caching**: Loaded profiles cached in memory
   ```python
   profile1 = loader.load("researcher")  # Loads from file
   profile2 = loader.load("researcher")  # Returns cached
   assert profile1 is profile2
   ```

2. **Hot Reload**: Force reload for development
   ```python
   loader.reload("researcher")  # Bypass cache, reload from file
   loader.reload_all()          # Reload all profiles
   ```

3. **Validation**: Comprehensive error checking
   ```python
   try:
       loader.load("invalid_agent")
   except AgentConfigError as e:
       print(e.path)    # Path to invalid file
       print(e)         # Detailed error message
   ```

**Step 2: Validation**

Validation occurs automatically during load:

```python
# From packages/friday-agent/src/friday_agent/loader.py
class AgentLoader:
    REQUIRED_FIELDS = ["name", "role", "goal", "system_prompt"]

    def _parse_yaml(self, path: Path) -> dict:
        # Parse YAML
        config = yaml.safe_load(file)

        # Check required fields
        missing = [f for f in self.REQUIRED_FIELDS if f not in config]
        if missing:
            raise AgentConfigError(f"Missing: {missing}", path)

        # Validate name matches filename
        if config["name"] != path.stem:
            raise AgentConfigError("Name must match filename", path)

        # Validate field types
        self._validate_types(config, path)

        return config
```

**Validation Rules:**

- **Required fields**: name, role, goal, system_prompt
- **Name consistency**: `name` field must match filename
- **Type checking**: All fields validated against expected types
- **Enum validation**: `tool_autonomy`, `context_strategy` checked against valid values
- **Range validation**: `temperature` must be 0.0-2.0

**Step 3: Registration**

Register profiles with the `AgentRegistry`:

```python
from friday_agent import AgentRegistry

# Create registry
registry = AgentRegistry(loader=loader)

# Auto-load all agents from directory
count = registry.load_all_from_directory()
# Loads all YAML files, registers profiles

# Manual registration
custom_profile = AgentProfile(
    name="custom",
    role="Custom Agent",
    goal="Specialized task",
    system_prompt_template="You are {{name}}",
)
registry.register(custom_profile)

# Query registry
profile = registry.get("researcher")
exists = registry.exists("coder")
all_agents = registry.list_agents()
```

**Capability Indexing:**

Registry automatically indexes agents by capabilities:

```python
# Find agents with specific capability
researchers = registry.find_by_capability("research")
# Returns: [researcher_profile, analyst_profile]

# Find agents with multiple capabilities
multi_cap = registry.find_by_capabilities(
    ["coding", "testing"],
    match_all=True  # Must have BOTH capabilities
)

# List all capabilities
caps = registry.list_capabilities()
# Returns: ["research", "coding", "testing", "analysis", ...]
```

**Step 4: Agent Instantiation**

Create agent instances using a factory pattern:

```python
from friday_agent import CopilotAgent
from friday_memory import MemoryController
from friday_llm import LiteLLMService

# Configure factory (typically done by dependency injection container)
def create_agent(profile: AgentProfile) -> CopilotAgent:
    return CopilotAgent(
        profile=profile,
        memory=memory_controller,
        context_engine=context_assembler,
        llm=llm_client,
        tool_registry=tool_registry,
        telemetry=telemetry_service,
    )

registry.set_factory(create_agent)

# Create agent instance
agent = registry.create_agent("researcher")
# Returns: CopilotAgent instance with researcher profile
```

**Lazy Instantiation:**

Agents are created on-demand, not at registration:

```python
# Registration: Fast, no agent instances created
registry.load_all_from_directory()  # Registers 10 agents

# Instantiation: Only when needed
researcher = registry.create_agent("researcher")  # Creates 1 agent instance
coder = registry.create_agent("coder")            # Creates another

# Other 8 agents still not instantiated (saves memory)
```

**Step 5: Session Initialization**

Before first use, initialize agent session:

```python
# Initialize session
session_state = await agent.initialize_session(
    session_id="session_abc123",
    user_id="user_alice",
)

# What happens:
# 1. Memory controller sets author to agent name (provenance tracking)
# 2. Context engine initializes session state
# 3. Priming (if configured): Load top entities, recent insights
# 4. Conversation history cleared for new session

# Session state returned
assert session_state.session_id == "session_abc123"
assert session_state.user_id == "user_alice"
assert session_state.turn_count == 0
```

**Session Restoration:**

Resume existing session:

```python
# Same session ID loads prior context
await agent.initialize_session(
    session_id="session_abc123",  # Existing session
    user_id="user_alice",
)

# Context engine loads:
# - Recent turns from this session (episodic memory)
# - Entities/insights from prior turns (graph/vector memory)
# - Session-scoped variables
```

**Step 6: Execution**

Process user queries:

```python
# Single turn
response = await agent.run("Find papers on transformer architectures")

# Multiple turns (maintains conversation state)
response1 = await agent.run("What's the weather in San Francisco?")
response2 = await agent.run("How about New York?")  # "it" refers to weather
response3 = await agent.run("Compare them")         # Remembers both cities
```

**Step 7: Cleanup**

Release resources when done:

```python
# Clear conversation history (keeps long-term memory)
agent.clear_history()

# Archive session before shutdown
# (Automatically happens after each turn via _archive_turn)

# Release agent instance
del agent
```

**For Project Leaders:** Agent lifecycle is designed for long-running services. Load configurations once at startup, instantiate agents on-demand, reuse instances across multiple sessions. Hot reload enables updating agent behavior without service restart (useful for prompt engineering).

**For IT Leaders:** Lazy instantiation minimizes memory footprint—only active agents consume resources. Session management enables multi-tenant deployments (one agent instance per customer session). Consider agent pooling for high-concurrency scenarios.

---

### 6.3.2 Session Management & Checkpointing

Friday agents maintain session state across conversation turns. Understanding session management is crucial for multi-turn conversations and multi-user deployments.

**Session State Components:**

```python
# From packages/friday-memory/src/friday_memory/models.py
@dataclass
class SessionState:
    session_id: str             # Unique session identifier
    user_id: str                # User identifier
    created_at: datetime        # Session creation timestamp
    turn_count: int             # Number of turns in session

    # Memory context (loaded during session init)
    primed_entities: list       # Entities loaded at session start
    primed_insights: list       # Insights loaded at session start

    # Scoped variables (session-specific data)
    variables: dict             # Key-value pairs for template substitution
```

**Session Creation:**

```python
# New session (generates ID automatically)
await agent.initialize_session(
    user_id="alice@example.com"
)
# agent.session_id = "550e8400-e29b-41d4-a716-446655440000"

# Or provide explicit session ID
await agent.initialize_session(
    session_id="custom_session_id",
    user_id="alice@example.com"
)
```

**Session Persistence:**

Sessions persist across application restarts via the transcript store:

```sql
-- Sessions table
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at DATETIME,
    updated_at DATETIME
);

-- Turns linked to sessions
CREATE TABLE turns (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES sessions(session_id),
    user_message TEXT,
    assistant_message TEXT,
    timestamp DATETIME,
    ...
);
```

**Resume Session:**

```python
# Application restart
# Reinitialize agent with same session ID

await agent.initialize_session(
    session_id="550e8400-e29b-41d4-a716-446655440000",  # Existing session
    user_id="alice@example.com"
)

# Context engine automatically loads:
# - Recent turns from this session
# - Entities mentioned in prior turns
# - Insights learned during session
```

**Multi-Session Management:**

Agents can switch between sessions:

```python
# Session A
await agent.initialize_session(session_id="session_a", user_id="alice")
await agent.run("Remember my favorite color is blue")

# Session B (different context)
await agent.initialize_session(session_id="session_b", user_id="bob")
await agent.run("Remember my favorite color is red")

# Back to Session A
await agent.initialize_session(session_id="session_a", user_id="alice")
response = await agent.run("What's my favorite color?")
# Response: "Your favorite color is blue" (remembers Session A context)
```

**Checkpointing:**

Friday automatically checkpoints after each turn:

```python
# After each agent.run() call:
async def _archive_turn(self, ...):
    # 1. Create turn record
    turn = InteractionTurn(
        id=str(uuid.uuid4()),
        session_id=self.session_id,
        user_message=user_message,
        assistant_message=assistant_message,
        tool_calls=tool_calls,
        tool_results=tool_results,
        timestamp=datetime.now(),
    )

    # 2. Store in episodic memory (SQLite)
    await self.memory.add_turn(self.session_id, turn)

    # 3. Trigger async extraction (non-blocking)
    asyncio.create_task(
        self.context_engine.extract_context(turn, async_execution=True)
    )
    # Extraction learns entities/insights in background
```

**Manual Checkpointing:**

For long-running tasks, add explicit checkpoints:

```python
async def long_workflow(agent: CopilotAgent):
    # Step 1
    result1 = await agent.run("Research topic A")
    # Checkpoint automatically after turn

    # Step 2
    result2 = await agent.run("Research topic B")
    # Another checkpoint

    # Manual checkpoint of intermediate state (future feature)
    # await agent.checkpoint()

    # Step 3
    final_result = await agent.run("Synthesize A and B")
    return final_result
```

**Session Cleanup:**

End session explicitly or rely on automatic cleanup:

```python
# Explicit cleanup
agent.clear_history()  # Clear in-memory conversation
# Note: Episodic memory persists in database

# Or let session expire naturally
# Sessions remain in database indefinitely unless purged
```

**Session-Scoped Variables:**

Store temporary data scoped to session:

```python
# Set session variable
session_state.variables["user_timezone"] = "America/Los_Angeles"
session_state.variables["user_language"] = "en"

# Use in system prompt
prompt = agent.profile.render_system_prompt(
    user_timezone=session_state.variables.get("user_timezone"),
    current_time=datetime.now().strftime("%I:%M %p"),
)
```

**Multi-Tenant Isolation:**

Isolate sessions by user:

```python
# User A session
await agent_a.initialize_session(
    session_id=f"user_alice_{date}",
    user_id="alice@example.com"
)

# User B session (different agent instance or same agent, different session)
await agent_b.initialize_session(
    session_id=f"user_bob_{date}",
    user_id="bob@example.com"
)

# Memory isolation via namespace
researcher_profile.memory_config["namespace"] = f"user_{user_id}"
```

**Session Monitoring:**

Query session state via CLI or API:

```bash
# CLI commands (memory-chat-v2.py)
/sessions              # List all sessions
/transcript            # Show current session transcript
/transcript <id>       # Show specific session
/memory                # Show memory stats for current session
```

```python
# Programmatic access
from friday_memory import TranscriptStoreAdapter

store = TranscriptStoreAdapter("transcript.db")
sessions = await store.get_all_sessions()
for session in sessions:
    print(f"{session.session_id}: {session.user_id}, {session.turn_count} turns")
```

**For Project Leaders:** Session management enables multi-user deployments where each user has isolated conversation state. Checkpointing ensures conversation continuity even across application restarts or crashes. Session-scoped variables enable personalization without polluting long-term memory.

**For IT Leaders:** Sessions are lightweight (metadata + turn references). Storage scales linearly with conversation volume. Consider session expiration policies (archive/delete sessions older than N days) for long-running deployments. Monitor session count and storage growth for capacity planning.

---

### 6.3.3 Agent Registry & Discovery

The `AgentRegistry` provides centralized agent management with capability-based discovery for orchestration.

**Registry Architecture:**

```
┌────────────────────────────────────────────────────────┐
│                   AGENT REGISTRY                       │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Profile Storage (in-memory)                     │ │
│  │  ├─ researcher: AgentProfile                     │ │
│  │  ├─ coder: AgentProfile                          │ │
│  │  └─ reviewer: AgentProfile                       │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Capability Index (fast lookup)                  │ │
│  │  ├─ "research" → [researcher, analyst]           │ │
│  │  ├─ "coding" → [coder, architect]                │ │
│  │  └─ "review" → [reviewer, qa_specialist]         │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Agent Factory (on-demand instantiation)         │ │
│  │  ├─ Creates AgentBase instances                  │ │
│  │  └─ Injects dependencies (memory, LLM, tools)    │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

**Registry Operations:**

```python
from friday_agent import AgentRegistry, AgentLoader

# Initialize registry with loader
loader = AgentLoader(Path("agents/"))
registry = AgentRegistry(loader=loader)

# Load all agents from directory
registry.load_all_from_directory()

# Registration (manual)
registry.register(custom_profile)

# Lookup by name
profile = registry.get("researcher")
profile = registry.get_or_raise("researcher")  # Raises KeyError if not found

# Check existence
exists = registry.exists("coder")

# List all agents
all_agents = registry.list_agents()
# Returns: ["researcher", "coder", "reviewer", "analyst"]
```

**Capability-Based Discovery:**

The primary orchestration feature:

```python
# Find agents with specific capability
research_agents = registry.find_by_capability("research")
# Returns: [researcher_profile, analyst_profile]

# Find agents with multiple capabilities (ANY match)
multi_cap = registry.find_by_capabilities(
    ["coding", "testing"],
    match_all=False  # Has EITHER coding OR testing
)

# Find agents with ALL required capabilities
strict = registry.find_by_capabilities(
    ["coding", "testing"],
    match_all=True   # Must have BOTH
)

# List all available capabilities
capabilities = registry.list_capabilities()
# Returns: ["research", "coding", "testing", "analysis", "review", ...]

# Get capability statistics
stats = registry.get_capability_stats()
# Returns: {"research": 2, "coding": 3, "testing": 2, ...}
```

**Agent Instantiation:**

Registry uses factory pattern for agent creation:

```python
# Configure factory (dependency injection)
def agent_factory(profile: AgentProfile) -> CopilotAgent:
    return CopilotAgent(
        profile=profile,
        memory=container.memory,
        context_engine=container.context_engine,
        llm=container.llm,
        tool_registry=container.tool_registry,
        telemetry=container.telemetry,
    )

registry.set_factory(agent_factory)

# Create agent instance
agent = registry.create_agent("researcher")
# Returns: CopilotAgent with researcher profile and all dependencies injected
```

**Registry Lifecycle:**

```python
# Startup: Load all agents
registry = AgentRegistry(loader=AgentLoader(Path("agents/")))
registry.load_all_from_directory()
registry.set_factory(create_agent_func)

# Runtime: Query and instantiate as needed
if user_query.is_research_task():
    candidates = registry.find_by_capability("research")
    agent = registry.create_agent(candidates[0].name)
    response = await agent.run(user_query)

# Shutdown: Clear registry (if needed)
registry.clear()
```

**Orchestrator Integration:**

Registry powers the `AgentOrchestrator`:

```python
from friday_agent import AgentOrchestrator

# Create orchestrator with registry
orchestrator = AgentOrchestrator(
    registry=registry,
    default_agent="assistant",  # Fallback agent
)

# Orchestrator uses registry for:
# 1. Agent lookup by name
# 2. Agent instantiation via factory
# 3. Capability-based routing (future feature)

# Explicit routing
response = await orchestrator.process("@researcher Find papers on AI")
# Registry looks up "researcher", instantiates via factory, runs query

# Agent switching
orchestrator.switch_agent("coder")
response = await orchestrator.process("Implement this algorithm")
```

**Advanced: Dynamic Registration**

Register agents at runtime:

```python
# Load agent YAML at runtime
new_profile = loader.load("new_agent")
registry.register(new_profile)

# Immediately available
agent = registry.create_agent("new_agent")

# Unregister
registry.unregister("old_agent")
```

**Registry Serialization:**

Export/import registry state:

```python
# Export to dict
state = registry.to_dict()
# Returns: {"researcher": {...}, "coder": {...}, ...}

# Save to JSON
import json
with open("registry_state.json", "w") as f:
    json.dump(state, f)

# Reload (reconstruct from saved state)
# Note: AgentProfile.from_dict() required for full deserialization
```

**For Project Leaders:** Registry enables **agent marketplace** patterns—teams can share agent definitions, download community agents, or version-control agent profiles. Capability-based discovery enables flexible task routing without hardcoding agent names.

**For IT Leaders:** Registry is in-memory (fast lookups) but profiles are loaded from filesystem (persistent, version-controlled). For large deployments with 100+ agents, consider lazy loading (only load profiles when first accessed) or database-backed registry for centralized management.

---

## 6.4 Real-World Configuration Examples

This section demonstrates complete agent configurations for common use cases.

### Example 1: Research Assistant Agent

```yaml
# agents/research_assistant.yaml
name: research_assistant
role: "Senior Research Analyst"
goal: "Find accurate information from multiple sources and synthesize insights"

system_prompt: |
  You are a meticulous research analyst with expertise in {{domain}}.

  Your methodology:
  1. Search for information from multiple credible sources
  2. Cross-reference facts for accuracy
  3. Distinguish between primary sources and commentary
  4. Acknowledge uncertainty when evidence is limited
  5. Cite all sources with proper attribution

  Research focus: {{focus}}
  Current date: {{current_date}}

tools:
  - web_search
  - scrape_page
  - read_file
  - recall_memory
  - store_fact
  - search_documents

tool_autonomy: auto
available_tools:
  - download_file
  - parse_pdf
  - parse_json
required_tools:
  - recall_memory

temperature: 0.3                # Low temperature for factual accuracy
max_tokens: 8192               # Long responses for detailed summaries
context_strategy: extended     # Maximum context for thorough research

memory_config:
  enable_graph: true           # Track sources, authors, topics
  enable_vector: true          # Semantic search over research corpus
  enable_episodic: true        # Conversation continuity
  max_episodic_turns: 30       # Extended history for multi-turn research

  priming_depth: 15            # Prime with many prior research topics
  namespace: "research_team"   # Share findings with research team

capabilities:
  - research
  - information_gathering
  - fact_checking
  - citation
  - summarization
  - web_search

metadata:
  version: "1.2.0"
  author: "research_team"
  description: |
    Research assistant specializing in web-based information gathering,
    fact-checking, and multi-source synthesis with proper citation tracking.

  # Template variables
  domain: "general knowledge"
  focus: "current events and academic research"

  tags:
    - core
    - research
    - web
    - citation
```

**Usage:**

```python
agent = registry.create_agent("research_assistant")
await agent.initialize_session(user_id="alice")

# Multi-turn research workflow
response1 = await agent.run(
    "Research the latest developments in quantum computing for 2025"
)
# Agent searches web, reads multiple sources, synthesizes findings

response2 = await agent.run(
    "Which companies are leading this research?"
)
# Agent remembers context from Turn 1, searches for company info

response3 = await agent.run(
    "Compare their approaches and cite sources"
)
# Agent cross-references prior findings, provides cited comparison
```

---

### Example 2: Code Generation Agent

```yaml
# agents/code_generator.yaml
name: code_generator
role: "Senior Software Engineer"
goal: "Write clean, tested, production-ready code following best practices"

system_prompt: |
  You are an expert software engineer specializing in {{language}}.

  Coding principles:
  - Write clear, self-documenting code
  - Follow language idioms and conventions
  - Handle errors gracefully with proper validation
  - Add inline comments for complex logic
  - Consider edge cases and boundary conditions
  - Write tests for critical functionality

  Code style: {{code_style}}
  Project context: {{project_context}}

tools:
  - read_file
  - write_file
  - list_directory
  - search_code
  - run_tests
  - lint_code
  - format_code
  - execute_code
  - git_status
  - git_diff
  - recall_memory

tool_autonomy: hybrid          # Start with base tools, expand as needed
injected_tools:
  - read_file
  - write_file
  - recall_memory
available_tools:
  - execute_code
  - run_tests
  - git_commit
  - git_push

temperature: 0.2               # Very low for deterministic code generation
max_tokens: 4096               # Moderate length (code files)
context_strategy: standard     # Balanced context

memory_config:
  enable_graph: true           # Track modules, functions, dependencies
  enable_vector: true          # Search prior code examples
  enable_episodic: true        # Remember coding session
  max_episodic_turns: 20

  namespace: "project_{{project_name}}"  # Isolate per project

capabilities:
  - coding
  - testing
  - debugging
  - refactoring
  - code_review

metadata:
  version: "2.0.0"
  author: "engineering_team"

  # Template variables
  language: "python"
  code_style: "PEP 8"
  project_context: "backend API development"
  project_name: "api_service"

  supported_languages:
    - python
    - typescript
    - go
    - rust

  tags:
    - core
    - coding
    - testing
```

**Usage:**

```python
agent = registry.create_agent("code_generator")
await agent.initialize_session(user_id="developer")

response = await agent.run("""
Implement a user authentication function that:
- Accepts username and password
- Validates against database
- Returns JWT token on success
- Handles errors gracefully
- Includes unit tests
""")
# Agent reads existing code, writes new function, generates tests
```

---

### Example 3: Customer Support Agent

```yaml
# agents/customer_support.yaml
name: customer_support
role: "Customer Support Specialist"
goal: "Resolve customer inquiries efficiently with empathy and accuracy"

system_prompt: |
  You are a friendly customer support specialist for {{company_name}}.

  Guidelines:
  - Listen carefully to customer concerns
  - Show empathy and acknowledge frustration
  - Provide accurate information from knowledge base
  - Offer step-by-step solutions
  - Escalate complex issues to human agents
  - Follow up to ensure satisfaction

  Company values: {{company_values}}
  Product knowledge: Available via recall_memory and search_kb tools

tools:
  - recall_memory
  - search_kb
  - create_ticket
  - update_ticket
  - send_email

tool_autonomy: manual          # Strict control for customer interactions

temperature: 0.4               # Balanced: Friendly but accurate
max_tokens: 2048               # Moderate responses
context_strategy: standard

memory_config:
  enable_graph: true           # Track customer relationships, past issues
  enable_vector: true          # Search solutions from prior tickets
  enable_episodic: true        # Conversation continuity
  max_episodic_turns: 20

  namespace: "customer_{{customer_id}}"  # Isolate per customer

capabilities:
  - customer_support
  - troubleshooting
  - ticket_management
  - email_communication

metadata:
  version: "1.0.0"
  author: "support_team"

  company_name: "TechCorp"
  company_values: "customer-first, transparency, continuous improvement"

  tags:
    - customer_facing
    - support
```

---

### Example 4: Stateless Classification Agent

```yaml
# agents/classifier.yaml
name: classifier
role: "Content Classifier"
goal: "Categorize content quickly and accurately"

system_prompt: |
  You are a content classification agent.

  Your task: Classify the given text into one of these categories:
  {{categories}}

  Output format: Return only the category name, nothing else.

tools: []                      # No tools needed

tool_autonomy: manual

temperature: 0.0               # Completely deterministic
max_tokens: 10                 # Just the category name
context_strategy: minimal      # No context needed

memory_config:
  enable_graph: false          # Stateless
  enable_vector: false
  enable_episodic: false       # No memory at all

capabilities:
  - classification
  - categorization

metadata:
  version: "1.0.0"
  author: "ml_team"

  categories: |
    - Bug Report
    - Feature Request
    - Question
    - Feedback
    - Complaint

  tags:
    - stateless
    - classification
    - high_throughput
```

**Usage (High-Throughput):**

```python
# Stateless agent: No session initialization needed
agent = registry.create_agent("classifier")

# Classify 1000 items in parallel
async def classify_batch(items: list[str]) -> list[str]:
    tasks = [agent.run(item) for item in items]
    return await asyncio.gather(*tasks)

results = await classify_batch(user_submissions)
```

---

## 6.5 Best Practices & Patterns

### Configuration Best Practices

**1. Principle of Least Privilege (Tools)**
```yaml
# Good: Minimal tools
tools:
  - read_file
  - recall_memory

# Avoid: Broad access
tools:
  - "*"  # All tools (security risk)
```

**2. Separate Development and Production Profiles**
```yaml
# agents/dev/researcher.yaml
name: researcher
temperature: 0.7       # Higher for exploration
tools:
  - "*"               # Full tool access for testing

# agents/prod/researcher.yaml
name: researcher
temperature: 0.3       # Lower for consistency
tools:
  - web_search
  - read_file
  - recall_memory      # Explicit allowlist
```

**3. Document Configuration Decisions**
```yaml
metadata:
  config_rationale: |
    Temperature 0.2: Requires deterministic code generation
    Manual tool_autonomy: Prevent arbitrary code execution
    No git_push: Requires human review before deployment
```

**4. Use Namespaces for Isolation**
```yaml
# Multi-tenant: One agent, isolated memory per customer
memory_config:
  namespace: "customer_{{customer_id}}"

# Multi-project: Share memory within project team
memory_config:
  namespace: "project_{{project_name}}"
```

**5. Version Control Your Agents**
```yaml
metadata:
  version: "2.1.0"
  changelog: |
    2.1.0: Added web scraping tools for richer research
    2.0.0: Migrated to hybrid tool_autonomy
    1.0.0: Initial release
```

---

### Common Pitfalls

**1. Over-Provisioning Tools**
```yaml
# Pitfall: Giving every agent every tool
tools: ["*"]

# Solution: Grant only necessary tools
tools:
  - read_file
  - recall_memory
```

**2. Wrong Temperature for Task**
```yaml
# Pitfall: High temperature for factual tasks
temperature: 1.2    # Too creative for data extraction

# Solution: Match temperature to task
temperature: 0.2    # Deterministic for facts
```

**3. Ignoring Memory Modes**
```yaml
# Pitfall: Full memory for ephemeral agents
memory_config:
  enable_graph: true
  enable_vector: true
  enable_episodic: true
  # Wastes resources for one-off tasks

# Solution: Stateless for ephemeral agents
memory_config:
  enable_graph: false
  enable_vector: false
  enable_episodic: false
```

**4. Forgetting Namespace Isolation**
```yaml
# Pitfall: Shared memory in multi-tenant deployment
memory_config:
  namespace: null     # All customers share memory (privacy violation)

# Solution: Isolate per customer
memory_config:
  namespace: "customer_{{customer_id}}"
```

**5. No Context Strategy Tuning**
```yaml
# Pitfall: Extended context for simple tasks
context_strategy: extended  # Expensive, slow for simple classification

# Solution: Minimal for simple tasks
context_strategy: minimal
```

---

## Summary

Friday's agent system provides a flexible, configuration-driven architecture for building specialized AI agents:

**Key Takeaways:**

1. **Two Agent Types**: CopilotAgent (production-ready, interactive) and AutonomousAgent (planned, background workflows)

2. **YAML Configuration**: Complete agent definition via YAML—identity, tools, model, memory, capabilities

3. **Tool Permission Management**: Fine-grained control via explicit allowlists, categories, wildcards, and autonomy modes

4. **Memory Modes**: Five modes (full, vector_only, graph_only, episodic_only, stateless) optimize for different use cases

5. **Lifecycle Management**: Configuration → Validation → Registration → Instantiation → Session → Execution

6. **Registry & Discovery**: Centralized agent management with capability-based routing for orchestration

**What's Next:**

- **Section 7: Multi-Agent Orchestration** covers coordinating multiple agents, task delegation, and shared memory patterns
- **Section 8: Workflows** introduces task graphs and automation for complex multi-step processes
- **Section 9: CLI Reference** documents all commands for interacting with Friday agents

**For Project Leaders:** Agent configuration is the "personality" layer of your AI system. Invest time in thoughtful agent design—clear roles, appropriate tool access, optimized memory strategies. Version control agent profiles as you would application code.

**For IT Leaders:** Agent YAML files are infrastructure-as-code. Validate in CI/CD, version with semantic versioning, deploy environment-specific profiles (dev/staging/prod). Monitor agent performance (latency, token usage, tool execution) for operational optimization.

**For Users:** Understanding agent capabilities helps you route tasks effectively. Use specialized agents for specific tasks (research, coding, analysis) rather than a single generalist agent. The right agent for the right task maximizes quality and efficiency.

---

**Document Statistics:**
- **Word Count**: ~12,000 words
- **Code Examples**: 45+
- **Configuration Examples**: 15+
- **Use Cases Covered**: 10+

**Comprehensive Coverage:**
✅ Agent types and patterns
✅ Complete YAML schema reference
✅ Tool permission management
✅ Model selection strategies
✅ Memory mode configuration
✅ Lifecycle and state management
✅ Registry and discovery
✅ Real-world examples
✅ Best practices and pitfalls

**Audience-Specific Insights:**
✅ Project Leaders: Strategic guidance on agent design
✅ IT Leaders: Operational considerations and security
✅ Users: Practical usage patterns and troubleshooting
