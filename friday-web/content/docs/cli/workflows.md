---
title: "Workflow Commands"
description: "Run, validate, and list YAML workflow definitions from the CLI."
weight: 3
---

Use `friday workflow run`, `friday workflow validate`, and `friday workflow list` to manage and execute your YAML workflow definitions from the CLI. Workflow commands are part of Phase 4 (Project Hive) features.

**Prerequisites:**
- Workflow definitions in `workflows/` directory (YAML format)
- Workflow engine initialized in config.yaml

---

## `/workflow list`

**Description:** Lists all available workflows from the workflows directory.

**Syntax:**

```
/workflow list
```

**Output Format:**

```
===========================
AVAILABLE WORKFLOWS (3 total)
===========================

newsletter
  Description: Generate newsletter from research and writing workflow
  Version: 1.0.0
  Author: friday-team
  Tasks: 3 (research -> review_gate -> write)
  Estimated Duration: 5-10 minutes
  Tags: content, automation, research

code-review
  Description: Automated code review pipeline with testing and security analysis
  Version: 1.2.0
  Author: friday-team
  Tasks: 4 (analyze -> test -> security_scan -> review_gate)
  Estimated Duration: 2-5 minutes
  Tags: code, quality, security

research-report
  Description: Comprehensive research and report generation workflow
  Version: 1.0.0
  Author: friday-team
  Tasks: 5 (search -> summarize -> synthesize -> fact_check_gate -> format)
  Estimated Duration: 10-15 minutes
  Tags: research, analysis, reporting

===========================
Use /workflow run <name> to execute
Use /workflow run <name> --help for input parameters
```

**Workflow Metadata:**
- **Name**: Workflow identifier for execution
- **Description**: Human-readable purpose
- **Version**: Semantic version for change tracking
- **Tasks**: Task count and workflow structure preview
- **Estimated Duration**: Expected execution time (excluding approval waits)
- **Tags**: Searchable categories

**Use Cases:**
- Workflow discovery: Find available automation workflows
- Capability planning: Understand what workflows can accomplish
- Template selection: Choose appropriate workflow for the task

---

## `/workflow run <name> [inputs]`

**Description:** Executes a workflow with optional input variables.

**Syntax:**

```
/workflow run <workflow_name>
/workflow run <workflow_name> var1="value1" var2="value2"
/workflow run <workflow_name> --help
```

**Parameters:**
- `workflow_name` (required): Workflow to execute
- `inputs` (optional): Space-separated key=value pairs (use quotes for multi-word values)
- `--help`: Show required/optional inputs for workflow

**Example — Newsletter Workflow:**

```
User: /workflow run newsletter user_topic="AI trends in 2026" urgency="high"

Workflow: newsletter
Execution ID: exec_abc123

[Task 1/3] research (assigned to: researcher)
  Status: RUNNING
  Gathering information about AI trends in 2026...

  [Tool: web_search executed...]
  [Tool: scrape_page executed...]

  Research complete (12 sources found)
  Output: research_summary

[Task 2/3] review_gate (APPROVAL REQUIRED)
  Status: WAITING_APPROVAL

  Task: Review research findings before proceeding to writing
  Input: research_summary

  Research Preview:
    - Large language models continue rapid development
    - AI regulation frameworks emerging in EU and US
    - Multimodal AI becoming mainstream
    ...

  Approve this research? (/workflow approve or /workflow skip)

User: /workflow approve

[Task 2/3] review_gate
  Status: APPROVED

[Task 3/3] write (assigned to: coder)
  Status: RUNNING
  Writing newsletter based on approved research...

  Newsletter draft complete
  Output: newsletter_content

===========================
WORKFLOW COMPLETE
===========================

Execution ID: exec_abc123
Duration: 3m 45s
Status: COMPLETED

Final Outputs:
  newsletter_content:
    # AI Trends Newsletter - January 2026

    ## Top Developments This Month

    1. **GPT-5 Release**: OpenAI announced GPT-5 with improved reasoning...
    2. **EU AI Act Implementation**: New regulations take effect...
    3. **Multimodal Breakthroughs**: Models combining text, image, audio...
    ...

    [Full newsletter: 1,234 words]

Use /workflow status for detailed execution log
```

**Example — Input Validation:**

```
User: /workflow run newsletter
Error: Missing required input(s): user_topic

Required Inputs:
  - user_topic (string): Topic for newsletter content

Optional Inputs:
  - urgency (string): Priority level (low/medium/high), default: medium
  - max_sources (integer): Maximum research sources, default: 10

Example: /workflow run newsletter user_topic="AI trends" urgency="high"
```

**Variable Syntax:**
- Simple values: `topic="AI trends"`
- Numbers: `max_sources=10`
- Booleans: `include_images=true`
- Quoted strings: `description="A multi-word description with spaces"`

**Use Cases:**
- Task automation: Execute complex multi-step workflows
- Quality gates: Require human approval before critical operations
- Reproducible processes: Standardize common workflows
- Agent coordination: Orchestrate multiple agents with dependencies

---

## `/workflow status`

**Description:** Shows current workflow execution status with task breakdown.

**Syntax:**

```
/workflow status
```

**Output Format (Running):**

```
===========================
WORKFLOW STATUS
===========================

Workflow: newsletter
Execution ID: exec_abc123
Started: 2026-01-24 14:30:15
Duration: 2m 34s

Overall Status: RUNNING

Tasks:
  [COMPLETED] research (assigned to: researcher)
      Duration: 1m 45s
      Output: research_summary

  [WAITING_APPROVAL] review_gate (approval required)
      Waiting since: 2026-01-24 14:32:00 (34s ago)
      Input: research_summary (12 sources)

  [PENDING] write (assigned to: coder)
      Dependencies: review_gate (waiting)

Variables:
  Inputs:
    user_topic: "AI trends in 2026"
    urgency: "high"

  Outputs:
    research_summary: [loaded, 2,345 chars]
    newsletter_content: (not yet generated)

Next Action:
  Review research findings and approve/skip review_gate
  Commands: /workflow approve | /workflow skip
```

**Output Format (Completed):**

```
===========================
WORKFLOW STATUS
===========================

Workflow: newsletter
Execution ID: exec_abc123
Started: 2026-01-24 14:30:15
Completed: 2026-01-24 14:33:48
Duration: 3m 33s

Overall Status: COMPLETED

Tasks:
  [COMPLETED] research (assigned to: researcher)
      Duration: 1m 45s

  [COMPLETED] review_gate (approved by user)
      Duration: 34s (approval wait time)

  [COMPLETED] write (assigned to: coder)
      Duration: 1m 14s

Final Outputs:
  research_summary: [2,345 chars]
  newsletter_content: [5,678 chars]

Workflow completed successfully.
```

**Output Format (Failed):**

```
===========================
WORKFLOW STATUS
===========================

Workflow: code-review
Execution ID: exec_def456
Started: 2026-01-24 15:00:00
Failed: 2026-01-24 15:01:23
Duration: 1m 23s

Overall Status: FAILED

Tasks:
  [COMPLETED] analyze
      Duration: 45s

  [FAILED] test
      Duration: 38s
      Error: Test suite failed (2/45 tests failed)
      Details:
        - test_authentication.py::test_login_invalid_credentials FAILED
        - test_authentication.py::test_password_hashing FAILED

  [SKIPPED] security_scan (dependency failed)
  [SKIPPED] review_gate (dependency failed)

Failure Reason:
  Task 'test' failed with error: Test suite returned exit code 1

Recovery Options:
  1. Fix failing tests and re-run workflow
  2. Restart workflow from beginning: /workflow run code-review [inputs]
```

**Task Status Types:**
- **PENDING**: Not yet started (waiting for dependencies)
- **RUNNING**: Currently executing
- **WAITING_APPROVAL**: Paused at approval gate
- **COMPLETED**: Successfully finished
- **FAILED**: Execution error
- **SKIPPED**: Manually skipped or dependency failed

**Use Cases:**
- Progress monitoring: Check workflow execution state
- Debugging: Identify which task failed and why
- Approval context: Review what requires approval
- Timing analysis: See task durations for optimization

---

## `/workflow approve`

**Description:** Approves a pending task at an approval gate and continues workflow execution.

**Syntax:**

```
/workflow approve
```

**Behavior:**
- Resumes workflow from WAITING_APPROVAL state
- Executes remaining tasks in topological order
- Records approval decision in transcript
- Only valid when workflow status is WAITING_APPROVAL

**Example:**

```
User: /workflow status
Friday: Workflow: newsletter
        Status: WAITING_APPROVAL
        Task: review_gate

        Research summary:
          - 12 sources found on "AI trends in 2026"
          - Key topics: LLMs, regulation, multimodal AI
          - Quality: High (8.5/10 average source credibility)

        Approve? /workflow approve | /workflow skip

User: /workflow approve
Friday: Approved: review_gate

        Continuing workflow...

        [Task 3/3] write (assigned to: coder)
          Status: RUNNING
          Writing newsletter based on approved research...

        [Workflow completed successfully]
```

**Approval Context:**

The approval gate receives ALL prior task outputs as context:

```yaml
- id: review_gate
  name: "Review Research Findings"
  requires_approval: true
  inputs:
    research_summary: "$research_summary"  # From prior task
    source_count: "$source_count"          # From prior task
```

**Use Cases:**
- Quality control: Verify intermediate results before proceeding
- Cost control: Approve expensive operations (API calls, deployments)
- Safety gates: Human verification before destructive operations
- Compliance: Audit trail of human approvals

Approval gates are blocking. Workflow execution does NOT proceed until approval or skip is received.

---

## `/workflow skip`

**Description:** Skips a pending task at an approval gate and continues with remaining tasks.

**Syntax:**

```
/workflow skip
```

**Behavior:**
- Marks current approval gate as SKIPPED
- Sets task outputs to null
- Continues with tasks that don't depend on skipped outputs
- Skips tasks that depend on null outputs (dependency chain break)

**Example:**

```
User: /workflow status
Friday: Workflow: code-review
        Status: WAITING_APPROVAL
        Task: review_gate

        Security scan found:
          - 1 medium-severity issue (SQL injection potential)

        Approve merge? /workflow approve | /workflow skip

User: /workflow skip
Friday: Skipped: review_gate

        Note: Workflow marked as COMPLETED but review was skipped.
        Address security issue before merging to production.
```

**Effect on Downstream Tasks:**

When a task is skipped:
- Task status is set to SKIPPED
- Task outputs are NOT created (variables remain undefined)
- Tasks that depend on skipped outputs will also be SKIPPED
- Tasks with no dependency on skipped outputs continue normally

**Use Cases:**
- Rejecting work: Decline intermediate results that don't meet quality bar
- Bypassing gates: Skip optional review for low-risk workflows
- Partial execution: Complete only independent branches of a workflow

---

## Agent Orchestration Commands

The CLI also supports multi-agent orchestration through explicit `@mention` routing and delegation.

### `@agent_name <message>`

**Description:** Routes a single message to a specific agent without changing the active agent.

**Syntax:**

```
@<agent_name> <message>
```

**Examples:**

```
User: @researcher Find papers on transformer architectures published after 2023
Researcher: I'll search for recent transformer papers...

Found 8 relevant papers:
1. "Attention Is Still All You Need: Optimizations in 2024" - Smith et al., 2024-01
2. "Efficient Transformers for Edge Devices" - Chen et al., 2023-12
...
```

```
User: @coder Implement a binary search tree in Python with insert and search methods
Coder: I'll implement a BST with proper documentation and type hints.

[Tool: write_file executed...]

Created: bst.py
...
```

**Routing Behavior:**
- Message is sent to specified agent (not active agent)
- Response is attributed to routed agent with provenance
- Active agent does NOT change (unlike `/switch`)

**Differences from `/switch`:**
- `@routing`: Single message to specific agent, then returns to active agent
- `/switch`: Changes active agent for ALL subsequent messages

---

### `/switch [agent]`

**Description:** Switches active agent or displays current agent status.

**Syntax:**

```
/switch              # Show current agent
/switch researcher   # Switch to researcher agent
/switch coder        # Switch to coder agent
```

**Output Format (Switch):**

```
User: /switch researcher
Friday: Switched to agent: researcher

  Role: Research and information gathering specialist
  Goal: Find, analyze, and synthesize information from multiple sources
  Model: gpt-4o
  Tools: 8 tools (web, data)
  Memory Mode: vector_only (semantic search optimized)

  Ready for research tasks!
```

**Behavior:**
- Switches active agent for all subsequent messages
- Preserves conversation history (visible to new agent)
- Maintains session ID and memory access
- Agent-specific tools and prompts take effect immediately

---

### `/agents`

**Description:** Lists all registered agents with their capabilities and configurations.

**Syntax:**

```
/agents
```

**Output Format:**

```
===========================
AVAILABLE AGENTS (4 total)
===========================

friday-assistant [ACTIVE] [DEFAULT]
  Role: General-purpose AI assistant
  Goal: Help users with tasks requiring memory and reasoning
  Capabilities:
    - Full memory access (episodic + semantic + associative)
    - All tool categories (52 tools)
    - Model: gpt-4o (temperature: 0.7)
  Status: Active (12 messages in current session)
  Tags: general, assistant, full-capability

researcher
  Role: Research and information gathering specialist
  Capabilities:
    - Vector-only memory (semantic search optimized)
    - Web and data tools only (8 tools)
    - Model: gpt-4o (temperature: 0.3)
  Status: Registered (not yet loaded)
  Tags: research, web, analysis

coder
  Role: Code generation and debugging specialist
  Capabilities:
    - Full memory access
    - Filesystem, shell, git, code tools (24 tools)
    - Model: claude-3.5-sonnet (temperature: 0.5)
  Status: Cached (instantiated, ready for use)
  Tags: code, development, git

reviewer
  Role: Code review and quality assurance specialist
  Capabilities:
    - Vector-only memory (semantic search for patterns)
    - Code analysis tools only (6 tools)
    - Model: gpt-4o (temperature: 0.2)
  Status: Registered (not yet loaded)
  Tags: review, quality, security

===========================
Use /agent <name> for detailed information
Use /switch <name> to change active agent
```

**Agent Status Types:**
- **Active**: Currently processing messages
- **Cached**: Loaded in memory, ready for immediate use
- **Registered**: Defined in YAML, not yet instantiated

---

### `/delegate <agent> <task>`

**Description:** Delegates a task to another agent and returns the result to the current agent.

**Syntax:**

```
/delegate <agent_name> <task_description>
```

**Example — Multi-Hop Delegation:**

```
User: Build and test a REST API endpoint

Friday (assistant): I'll coordinate this task across specialists.

/delegate coder Implement a REST API endpoint for user registration with email validation

[Coder agent implements endpoint...]

/delegate reviewer Review the implementation for bugs and best practices

[Reviewer agent analyzes code...]

/delegate coder Fix the issues identified: [list of issues]

[Coder agent updates code...]

Friday (assistant): The endpoint is implemented and reviewed. Here's the final code with tests...
```

**Memory Implications:**
- Delegated work is visible to both agents (shared memory)
- Provenance metadata tracks which agent contributed what
- Insights extracted by the delegated agent are available to all agents

**Use Cases:**
- Specialization: Leverage specialist agents for subtasks
- Workflow orchestration: Chain multiple agents for complex tasks
- Quality assurance: Delegate review to specialized reviewer agents

---

### `/status`

**Description:** Shows comprehensive orchestrator status including active and cached agents.

**Syntax:**

```
/status
```

**Output Format:**

```
===========================
ORCHESTRATOR STATUS
===========================

Active Agent: friday-assistant
  Messages in session: 12
  Tool calls: 8
  Average latency: 2.3s
  Total tokens: 18,450

Session Info:
  Session ID: abc123def456
  Started: 2026-01-24 10:15:30
  Duration: 1h 23m

Cached Agents (2):
  friday-assistant [ACTIVE]
    Loaded: 1h 23m ago, Messages: 12

  coder
    Loaded: 45m ago, Messages: 3 (from delegation)

Registered Agents (2):
  researcher - Not yet loaded
  reviewer - Not yet loaded

Resource Usage:
  Memory: 234 MB (all agents)
  LLM Calls: 12 (friday-assistant), 3 (coder)
  Total Cost: $0.45 (estimated)

Orchestration Stats:
  @routing uses: 0
  Delegations: 2
  Agent switches: 1
```

**Use Cases:**
- Session monitoring: Check current orchestration state
- Resource management: See which agents are loaded and consuming memory
- Cost tracking: Monitor LLM API usage across agents
- Performance analysis: Compare latency and token usage per agent

---

## Related Pages

- [Session Commands](/docs/cli/session/) — Start, resume, list, and export conversation sessions
- [Memory Commands](/docs/cli/memory/) — Inspect, search, prune, and export memory stores
- [Workflow Engine](/docs/workflows/engine/) — How Friday parses, validates, and executes YAML workflow definitions
- [Collaboration Patterns](/docs/multi-agent/patterns/) — Multi-agent orchestration patterns
