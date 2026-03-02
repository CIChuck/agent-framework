---
title: "YAML Configuration"
description: "Configure agents declaratively with AgentProfile YAML schemas."
weight: 2
---

Define agent behavior declaratively using `AgentProfile` YAML schemas that specify the LLM, tools, memory settings, and system prompt for each agent.

Friday agents are defined via YAML configuration files that specify identity, capabilities, tool access, model parameters, and memory strategies. This **configuration-as-code** approach enables version control, environment-specific profiles, and team collaboration on agent design.

## Agent Profile Schema (Complete Reference)

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
```

**Field Requirements:**

| Field | Required | Type | Default | Validation |
|-------|----------|------|---------|------------|
| `name` | Yes | string | - | Must match filename |
| `role` | Yes | string | - | Non-empty |
| `goal` | Yes | string | - | Non-empty |
| `system_prompt` | Yes | string | - | Supports `{{variable}}` templates |
| `tools` | No | list[string] | `[]` | Must exist in registry |
| `tool_autonomy` | No | enum | `"manual"` | "manual", "auto", "hybrid" |
| `temperature` | No | float | `0.7` | 0.0 to 2.0 |
| `max_tokens` | No | int | null | Respects model limits |
| `context_strategy` | No | enum | `"standard"` | "minimal", "standard", "extended" |
| `capabilities` | No | list[string] | `[]` | Freeform tags |
| `memory_config` | No | dict | `{}` | See memory section |
| `metadata` | No | dict | `{}` | Freeform nested data |

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

Invalid configurations raise `AgentConfigError` with helpful messages:

```
AgentConfigError: agents/researcher.yaml: Agent name 'researcher_v2' must match filename 'researcher'
AgentConfigError: agents/coder.yaml: Missing required fields: ['system_prompt']
AgentConfigError: agents/analyst.yaml: Field 'temperature' must be a number
AgentConfigError: agents/writer.yaml: tool_autonomy must be 'manual', 'auto', or 'hybrid'
```

---

## Tool Permission Management

Tools represent the primary security boundary for agents—they determine what an agent can actually *do* in the real world.

### Explicit Allowlist (Manual Mode)

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

### Category-Based Selection

Friday tools are organized by category. Grant access to entire categories:

```yaml
tools:
  - filesystem.*    # All filesystem tools
  - web.*          # All web/network tools
  - git.*          # All git tools
```

**Built-in Categories:**

| Category | Tools Included | Risk Level |
|----------|----------------|------------|
| `filesystem.*` | read_file, write_file, list_directory, delete_file, move_file | Medium (data modification) |
| `web.*` | http_request, web_search, scrape_page, download_file | Medium (external access) |
| `git.*` | git_status, git_commit, git_push, git_pull, git_diff, git_log | High (code modification) |
| `shell.*` | execute_command, run_script | High (arbitrary code execution) |
| `data.*` | parse_json, parse_yaml, parse_xml, csv_operations | Low (read-only parsing) |
| `text.*` | regex_search, regex_replace, text_transform | Low (string operations) |
| `code.*` | run_python, analyze_code, format_code | High (code execution) |

### Wildcard Patterns

Use glob-style wildcards for fine-grained selection:

```yaml
tools:
  - read_*         # read_file, read_page, etc.
  - git_status     # Explicit
  - git_diff
  - git_log        # Read-only git operations
  # Excludes: git_commit, git_push (write operations)
```

### Tool Autonomy Modes

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

**Security Best Practices:**

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

All tool executions are logged to transcripts with full details for security audit:

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

---

## Model Selection Per Agent

Friday supports configuring different LLM models per agent, enabling cost/capability optimization.

{{< callout type="info" >}}
Friday v0.1.0 uses a single global LLM client shared by all agents. Per-agent model selection is planned for a future release. Use programmatic injection as a workaround.
{{< /callout >}}

**Workaround — Programmatic Injection:**

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

**Temperature Settings Per Use Case:**

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

---

## Memory Mode Configuration

Agents can be configured with different memory access patterns to optimize for performance, cost, or functionality.

```yaml
# FULL MODE: All memory stores enabled (default)
memory_config:
  enable_graph: true
  enable_vector: true
  enable_episodic: true
  max_episodic_turns: 20

# VECTOR ONLY: Semantic search, no graph
memory_config:
  enable_graph: false
  enable_vector: true
  enable_episodic: true
  max_episodic_turns: 10

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
| **full** | Yes | Yes | Yes | Personal assistants, knowledge workers | ~200ms |
| **vector_only** | No | Yes | Yes | Research agents, document Q&A | ~120ms |
| **graph_only** | Yes | No | Yes | Relationship-focused agents, CRM | ~100ms |
| **episodic_only** | No | No | Yes | Short-term tasks, ephemeral agents | ~50ms |
| **stateless** | No | No | No | One-off queries, public chatbots | ~10ms |

**Namespace Isolation:**

```yaml
# No namespace: Global shared memory
memory_config:
  namespace: null

# Team namespace: Share memory within team
memory_config:
  namespace: "research_team"

# Agent namespace: Private memory
memory_config:
  namespace: "agent_researcher"
```

**Multi-tenant deployment:**

```yaml
# Agent profile template
name: customer_assistant
memory_config:
  namespace: "customer_{{customer_id}}"  # Isolated per customer
```

---

## Related Pages

- [Agent Types](/docs/agents/types/) — CopilotAgent, AutonomousAgent, and specialized roles
- [Lifecycle & State](/docs/agents/lifecycle/) — Session initialization, Re-Act loop, and turn archiving
- [Tool System Overview](/docs/tools/) — BaseTool architecture and tool schemas
