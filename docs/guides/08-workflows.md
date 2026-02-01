# Friday Agent Framework
## Section 8: Workflows - Task Graphs & Automation

**Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-01-24

---

## Overview

Workflows are Friday's automation engine for complex, multi-step tasks that require coordination across multiple agents, conditional logic, and human oversight. While individual agents excel at focused tasks, workflows orchestrate entire processes—research → analysis → writing → review—with automatic data passing, dependency management, and approval gates.

Friday's workflow system uses declarative YAML definitions to describe directed acyclic graphs (DAGs) of tasks. Each task assigns work to a specific agent, declares inputs from prior tasks, produces outputs for subsequent tasks, and optionally pauses for human approval before executing. This creates repeatable, auditable processes for complex automation.

**This section covers:**
- Workflow engine architecture and execution model
- Complete YAML workflow schema reference
- Workflow loading, execution, and status tracking
- Example workflows and templates for common patterns

**For Project Leaders:** Workflows transform ad-hoc agent interactions into repeatable business processes. Instead of manually orchestrating "ask researcher, then writer, then reviewer," you define the process once and execute it reliably. This enables scaling agent teams to handle production workloads with consistent quality.

**For IT Leaders:** Workflows provide governance and auditability for multi-step agent processes. Approval gates enable human oversight at critical decision points (before deployment, before data deletion, before external API calls). Complete execution history tracks which agent did what, when, and with what inputs—essential for compliance and debugging.

**For Users:** Workflows let Friday handle complex, multi-stage tasks autonomously. Instead of guiding Friday through each step ("first research this, now write that, now review it"), you trigger a workflow and Friday manages the entire process, only pausing when human approval is needed.

---

## 8.1 Workflow Engine Architecture

### 8.1.1 Task Graphs & Dependencies (DAGs)

Friday workflows are **directed acyclic graphs** where:
- **Nodes** represent tasks (units of work assigned to agents)
- **Edges** represent dependencies (task B depends on task A completing)
- **Acyclic** means no circular dependencies (task A → task B → task A is invalid)

**Why DAGs?**

Directed acyclic graphs provide:
1. **Clear Execution Order**: Topological sorting ensures tasks run in correct sequence
2. **Parallel Execution** (future): Tasks with no dependencies can run concurrently
3. **Failure Isolation**: Failed tasks don't affect independent branches
4. **Cycle Detection**: Invalid workflows (circular dependencies) are caught at load time

**Task Graph Example:**

```
┌──────────────────────────────────────────────────────────┐
│                  Newsletter Workflow                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────┐                                         │
│  │  research   │  (no dependencies, runs first)          │
│  └──────┬──────┘                                         │
│         │ produces: $research_results                    │
│         ▼                                                 │
│  ┌─────────────┐                                         │
│  │review_research│  (depends on: research)               │
│  │   [APPROVE]  │  (requires human approval)             │
│  └──────┬──────┘                                         │
│         │ produces: $approved_research                   │
│         ▼                                                 │
│  ┌─────────────┐                                         │
│  │ write_draft │  (depends on: review_research)          │
│  └──────┬──────┘                                         │
│         │ produces: $newsletter_draft                    │
│         ▼                                                 │
│  ┌─────────────┐                                         │
│  │final_review │  (depends on: write_draft)              │
│  │   [APPROVE]  │  (requires human approval)             │
│  └──────┬──────┘                                         │
│         │ produces: $final_newsletter                    │
│         ▼                                                 │
│      SUCCESS                                              │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Dependency Rules:**

1. **No Self-Dependencies**: A task cannot depend on itself
2. **No Cycles**: Task A → B → C → A creates a cycle (detected and rejected)
3. **Valid References**: All dependencies must reference existing task IDs
4. **Execution Readiness**: A task is "ready" when all its dependencies are COMPLETED

**Topological Sorting:**

Friday uses Kahn's algorithm to determine execution order:

```python
# Conceptual algorithm (from models.py)
def get_task_order(self) -> list[str]:
    """Get topologically sorted task order."""
    in_degree = {t.id: len(t.depends_on) for t in self.tasks}
    queue = [tid for tid, deg in in_degree.items() if deg == 0]  # No dependencies
    order = []

    while queue:
        task_id = queue.pop(0)
        order.append(task_id)

        # For each task depending on this one
        for task in self.tasks:
            if task_id in task.depends_on:
                in_degree[task.id] -= 1
                if in_degree[task.id] == 0:  # All dependencies satisfied
                    queue.append(task.id)

    if len(order) != len(self.tasks):
        raise ValueError("Workflow contains cycles")  # Cycle detected!

    return order
```

This produces execution order: `["research", "review_research", "write_draft", "final_review"]`

**Diamond Dependencies:**

Multiple tasks can depend on the same task (diamond pattern):

```
        ┌────────────┐
        │  analyze   │
        └─────┬──────┘
              │
      ┌───────┴───────┐
      ▼               ▼
┌──────────┐    ┌──────────┐
│summarize │    │visualize │
└─────┬────┘    └─────┬────┘
      │               │
      └───────┬───────┘
              ▼
        ┌──────────┐
        │  report  │
        └──────────┘
```

This is valid—the `report` task waits for both `summarize` and `visualize` to complete.

**For Project Leaders:** The DAG model ensures workflows are maintainable and debuggable. If a task fails, you can see exactly which tasks depend on it and won't run. If you need to add a new step, dependencies clearly show where it fits in the process.

**For IT Leaders:** Cycle detection prevents infinite loops in production. Workflows that pass validation are guaranteed to either complete or fail at a specific task—never hang indefinitely. This is essential for SLA guarantees and resource planning.

**For Users:** Dependencies mean you don't need to manually sequence tasks. Define what depends on what, and Friday figures out the order. If you add a new task to an existing workflow, Friday automatically integrates it into the execution sequence.

---

### 8.1.2 Variable Passing with $var Syntax

Tasks communicate via **workflow variables** using the `$var` syntax. This creates a data flow pipeline where each task's outputs become subsequent tasks' inputs.

**Variable System:**

```yaml
tasks:
  - id: research
    outputs:
      - research_results     # Creates $research_results variable

  - id: analyze
    depends_on:
      - research
    inputs:
      data: "$research_results"  # Reads $research_results variable
    outputs:
      - analysis_summary     # Creates $analysis_summary variable

  - id: write_report
    depends_on:
      - analyze
    inputs:
      topic: "$user_topic"         # Reads initial input variable
      findings: "$analysis_summary" # Reads from analyze task
      style: "formal"               # Literal value (not a variable)
    outputs:
      - final_report         # Creates $final_report variable
```

**Variable Resolution:**

When a task executes, Friday resolves inputs:

1. **Variable References** (`$name`): Looked up in the workflow variable store
2. **Literal Values** (no `$` prefix): Passed as-is to the task

**Example Resolution:**

```python
# Workflow execution state
execution.variables = {
    "user_topic": "AI Trends 2025",        # Initial input
    "research_results": "Research summary...",  # From research task
    "analysis_summary": "Key findings..."   # From analyze task
}

# Task definition
task = {
    "id": "write_report",
    "inputs": {
        "topic": "$user_topic",          # Variable reference
        "findings": "$analysis_summary",  # Variable reference
        "style": "formal"                 # Literal value
    }
}

# Resolved inputs passed to agent
resolved_inputs = {
    "topic": "AI Trends 2025",           # Resolved from $user_topic
    "findings": "Key findings...",        # Resolved from $analysis_summary
    "style": "formal"                     # Literal (unchanged)
}
```

**Variable Store:**

The `WorkflowExecution` maintains a variable store (dictionary) that persists for the entire workflow execution:

```python
class WorkflowExecution(BaseModel):
    """Runtime state of a workflow execution."""

    workflow_id: str
    execution_id: str
    variables: dict[str, Any] = Field(
        default_factory=dict,
        description="Variable store for input/output passing"
    )
    # ... other fields
```

**Variable Lifecycle:**

1. **Initialization**: Set from `initial_inputs` when workflow starts
2. **Task Outputs**: Each task output creates/updates a variable
3. **Task Inputs**: Variables are resolved before task execution
4. **Completion**: Variables remain accessible after workflow finishes (for inspection or chaining workflows)

**Missing Variable Error:**

If a task references an undefined variable, execution fails immediately:

```python
# Task references $missing_var but it doesn't exist
if var_name not in variables:
    raise WorkflowError(
        f"Missing variable: ${var_name} (required by task '{task.id}')",
        task_id=task.id
    )
```

This fail-fast behavior prevents tasks from executing with incomplete inputs.

**Variable Naming Conventions:**

By convention (not enforced):
- **`$user_*`**: Initial inputs from user (`$user_topic`, `$user_options`)
- **`$task_*`**: Task-specific outputs (`$research_results`, `$analysis_summary`)
- **`$final_*`**: Final workflow outputs (`$final_report`, `$final_decision`)

**For Project Leaders:** Variable passing eliminates manual data handoff between agents. The workflow engine ensures outputs from one task automatically reach the next task, reducing human error and improving reliability. This is especially valuable for long-running processes where manual data tracking is error-prone.

**For IT Leaders:** Variable resolution is type-agnostic—variables can hold strings, numbers, lists, dicts, or any JSON-serializable data. This flexibility supports diverse workflows (text processing, data analysis, API orchestration) without schema rigidity. However, ensure agents produce outputs in expected formats to avoid runtime type errors.

**For Users:** Variables create a "data pipeline" through your workflow. The output of the research task becomes the input to the writing task automatically. You don't need to copy-paste or manually transfer information between steps—Friday handles it.

---

### 8.1.3 Workflow Status Tracking

The workflow engine tracks detailed execution state for observability, debugging, and resumption.

**Status Types:**

Friday uses a comprehensive status model for both workflows and individual tasks:

```python
class TaskStatus(str, Enum):
    """Status of a workflow task."""

    PENDING = "pending"                 # Not yet started (waiting for dependencies)
    RUNNING = "running"                 # Currently executing
    WAITING_APPROVAL = "waiting_approval"  # Paused for human approval
    COMPLETED = "completed"             # Successfully finished
    FAILED = "failed"                   # Failed with error
    SKIPPED = "skipped"                # Skipped (approval denied or dependency failed)
```

**Status Transitions:**

```
PENDING ──────► RUNNING ──────► COMPLETED
   │               │                 │
   │               ▼                 │
   │          WAITING_APPROVAL       │
   │               │                 │
   │               ▼                 │
   │          (user approves)        │
   │               │                 │
   │               └─────────────────┘
   │
   ▼
SKIPPED (if dependency failed)

PENDING ──────► RUNNING ──────► FAILED (with retry)
                   │                 │
                   │                 ▼
                   │            (reset to PENDING)
                   │                 │
                   └─────────────────┘
                           │
                           ▼ (max retries)
                       FAILED (terminal)
```

**Execution State Model:**

```python
class WorkflowExecution(BaseModel):
    """Runtime state of a workflow execution."""

    # Identity
    workflow_id: str                   # Which workflow definition
    execution_id: str                  # Unique execution instance
    status: TaskStatus = TaskStatus.PENDING  # Overall workflow status

    # Variable store
    variables: dict[str, Any] = Field(default_factory=dict)

    # Execution state
    current_task_id: str | None = None         # Task currently executing
    pending_approval: str | None = None        # Task ID waiting for approval

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # History
    task_history: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Execution history for each task"
    )
```

**Task History:**

Each task execution is recorded in the history with full details:

```python
def record_task(self, task: TaskNode) -> None:
    """Record task execution in history."""
    self.task_history.append({
        "task_id": task.id,
        "status": task.status.value,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "duration_ms": task.duration_ms,
        "error": task.error,
    })
```

**Example Task History:**

```json
{
  "task_history": [
    {
      "task_id": "research",
      "status": "completed",
      "started_at": "2026-01-24T10:15:00.000Z",
      "completed_at": "2026-01-24T10:15:45.000Z",
      "duration_ms": 45000,
      "error": null
    },
    {
      "task_id": "review_research",
      "status": "completed",
      "started_at": "2026-01-24T10:16:00.000Z",
      "completed_at": "2026-01-24T10:16:30.000Z",
      "duration_ms": 30000,
      "error": null
    },
    {
      "task_id": "write_draft",
      "status": "failed",
      "started_at": "2026-01-24T10:17:00.000Z",
      "completed_at": "2026-01-24T10:17:15.000Z",
      "duration_ms": 15000,
      "error": "LLM timeout: Request exceeded 60s limit"
    }
  ]
}
```

**Querying Status:**

The workflow engine provides a status query method:

```python
def get_workflow_status(
    self, workflow: WorkflowDefinition, execution: WorkflowExecution
) -> dict[str, Any]:
    """Get detailed workflow status."""
    task_statuses = {}
    for task in workflow.tasks:
        task_statuses[task.id] = {
            "name": task.name,
            "status": task.status.value,
            "agent": task.agent,
            "duration_ms": task.duration_ms,
            "error": task.error,
        }

    return {
        "workflow_id": execution.workflow_id,
        "execution_id": execution.execution_id,
        "status": execution.status.value,
        "pending_approval": execution.pending_approval,
        "current_task": execution.current_task_id,
        "variables": list(execution.variables.keys()),
        "duration_ms": execution.duration_ms,
        "tasks": task_statuses,
    }
```

**Example Status Output:**

```json
{
  "workflow_id": "newsletter_generation",
  "execution_id": "newsletter_generation_1737718800",
  "status": "waiting_approval",
  "pending_approval": "final_review",
  "current_task": null,
  "variables": ["user_topic", "research_results", "approved_research", "newsletter_draft"],
  "duration_ms": 120000,
  "tasks": {
    "research": {
      "name": "Research Topic",
      "status": "completed",
      "agent": "researcher",
      "duration_ms": 45000,
      "error": null
    },
    "review_research": {
      "name": "Review Research Results",
      "status": "completed",
      "agent": "researcher",
      "duration_ms": 30000,
      "error": null
    },
    "write_draft": {
      "name": "Write Newsletter Draft",
      "status": "completed",
      "agent": "coder",
      "duration_ms": 35000,
      "error": null
    },
    "final_review": {
      "name": "Final Newsletter Review",
      "status": "waiting_approval",
      "agent": "coder",
      "duration_ms": null,
      "error": null
    }
  }
}
```

**For Project Leaders:** Comprehensive status tracking enables real-time monitoring of long-running workflows. You can see which tasks are complete, which are running, and which are waiting for approval—essential for managing workflows that span hours or days.

**For IT Leaders:** Task history provides a complete audit trail for compliance and debugging. Every task execution is timestamped with success/failure status and error details. This enables root cause analysis when workflows fail and demonstrates due diligence for regulated processes.

**For Users:** Status tracking lets you see exactly where Friday is in a multi-step process. If a workflow pauses for approval, you know which task is waiting. If a workflow fails, you can see which task failed and why, helping you decide whether to retry or modify the workflow.

---

## 8.2 YAML Workflow Definitions

### 8.2.1 Workflow Schema Reference

Friday workflows are defined in YAML files using a structured schema. This section provides complete documentation of all available fields.

**Root Workflow Schema:**

```yaml
# Required fields
id: string                    # Unique workflow identifier (alphanumeric, underscore, hyphen)
name: string                  # Human-readable workflow name
description: string           # Workflow description (purpose, context, use cases)
tasks: [TaskNode]            # Array of task definitions (min: 1)

# Optional fields
timeout_seconds: integer      # Overall workflow timeout (default: 3600 = 1 hour)
max_retries: integer         # Default max retries for tasks (default: 1)
version: string              # Workflow version (default: "1.0.0")
author: string               # Workflow author
tags: [string]               # Tags for organization and filtering
```

**TaskNode Schema:**

```yaml
# Required fields
id: string                    # Unique task identifier within workflow
name: string                  # Human-readable task name
description: string           # Task description/prompt for agent (supports multiline)
agent: string                 # Agent name to execute this task

# Optional fields
inputs: object                # Input mappings: {name: source}
  # Each input maps a parameter name to either:
  # - A variable reference: "$variable_name"
  # - A literal value: "literal string" or 123
outputs: [string]            # Output variable names (default: [])
  # Array of variable names to store task result

depends_on: [string]         # Task IDs that must complete first (default: [])
requires_approval: boolean    # Whether task requires human approval (default: false)
timeout_seconds: integer      # Task-specific timeout (overrides workflow default)
max_retries: integer         # Maximum retry attempts on failure (default: 0)

# Runtime fields (automatically set during execution)
status: string               # Task status (pending, running, completed, failed, etc.)
result: any                  # Task result (agent response)
error: string                # Error message if failed
retry_count: integer         # Current retry attempt
started_at: datetime         # Execution start timestamp
completed_at: datetime       # Execution end timestamp
```

**Complete Annotated Example:**

```yaml
# Newsletter Generation Workflow
# Researches a topic, writes a newsletter, and requires human approval

id: newsletter_generation
name: "Newsletter Generation"
description: |
  Research a topic and generate a newsletter article with human review.
  This workflow demonstrates multi-agent collaboration with approval gates.
version: "1.0.0"
author: "friday-team"
tags: ["content", "research", "writing", "approval"]

# Global settings
timeout_seconds: 7200  # 2 hours for entire workflow
max_retries: 2         # Retry failed tasks twice by default

tasks:
  # Task 1: Research the topic
  - id: research
    name: "Research Topic"
    description: |
      Research the given topic and gather key information.
      Focus on:
      - Recent developments (last 6 months)
      - Key statistics and data points
      - Expert opinions and quotes
      - Relevant examples and case studies

      Provide a comprehensive research summary with sources.
    agent: researcher     # Use the 'researcher' agent
    inputs:
      topic: "$user_topic"  # Variable from initial input
    outputs:
      - research_results    # Store result as $research_results
    requires_approval: false

  # Task 2: Human review of research
  - id: review_research
    name: "Review Research Results"
    description: |
      Review the research results for accuracy and completeness.

      Research to review:
      {{research}}

      Provide feedback or approve to continue.
    agent: researcher
    inputs:
      research: "$research_results"  # Output from 'research' task
    outputs:
      - approved_research    # Store approved version
    depends_on:
      - research             # Must wait for 'research' to complete
    requires_approval: true  # Pause for human approval before executing

  # Task 3: Write newsletter draft
  - id: write_draft
    name: "Write Newsletter Draft"
    description: |
      Write a newsletter article based on the approved research.

      Guidelines:
      - Engaging headline (under 60 characters)
      - Clear introduction (2-3 paragraphs)
      - Key points with supporting details (3-5 sections)
      - Conclusion with call to action
      - Target length: 500-800 words
      - Tone: Professional but accessible
      - Include inline citations where appropriate
    agent: coder            # Use 'coder' agent for writing
    inputs:
      research: "$approved_research"  # Output from 'review_research'
    outputs:
      - newsletter_draft     # Store draft
    depends_on:
      - review_research      # Must wait for 'review_research' to complete
    timeout_seconds: 300     # 5 minutes for writing
    max_retries: 3          # Retry up to 3 times if fails

  # Task 4: Final review and approval
  - id: final_review
    name: "Final Newsletter Review"
    description: |
      Review the final newsletter draft.

      Check for:
      - Accuracy (facts match research)
      - Clarity (easy to understand)
      - Tone (appropriate for audience)
      - Grammar and style

      Approve to publish or provide feedback for revision.
    agent: coder
    inputs:
      draft: "$newsletter_draft"  # Output from 'write_draft'
    outputs:
      - final_newsletter      # Final approved version
    depends_on:
      - write_draft           # Must wait for 'write_draft' to complete
    requires_approval: true   # Pause for human approval
```

**Field Validation Rules:**

1. **`id` (workflow and task):**
   - Must be unique within scope (workflow IDs globally, task IDs within workflow)
   - Alphanumeric characters, underscores, hyphens only
   - Case-insensitive (normalized to lowercase)

2. **`depends_on`:**
   - All referenced task IDs must exist in the workflow
   - Cannot create cycles (A → B → C → A)
   - Tasks can depend on multiple tasks (fan-in pattern)

3. **`inputs`:**
   - Keys are parameter names passed to the agent
   - Values starting with `$` are variable references (must exist at runtime)
   - Values without `$` are literal values

4. **`outputs`:**
   - Array of variable names to create/update
   - Variables are created after task completes successfully
   - Multiple tasks can write to the same variable (last writer wins)

5. **`timeout_seconds`:**
   - Must be positive integer
   - Task-level timeout overrides workflow-level timeout
   - If exceeded, task fails (can retry if `max_retries > 0`)

6. **`max_retries`:**
   - Must be non-negative integer
   - Task-level retries override workflow-level default
   - Retries use exponential backoff (future enhancement)

**For Project Leaders:** The YAML schema is human-readable and version-controllable. Workflows can be stored in git, reviewed in pull requests, and deployed via CI/CD. This enables workflow-as-code practices similar to infrastructure-as-code.

**For IT Leaders:** Schema validation catches errors at load time, not runtime. Invalid workflows (missing dependencies, cycles, malformed syntax) are rejected before execution, preventing resource waste and ensuring only valid workflows reach production.

**For Users:** YAML workflows are self-documenting. Reading a workflow file clearly shows what steps happen, in what order, and which require approval. This transparency helps you understand and trust automated processes.

---

### 8.2.2 Task Configuration Options

This section details advanced task configuration options for robust production workflows.

**Retry Strategies:**

```yaml
tasks:
  - id: flaky_api_call
    name: "Call External API"
    description: "Fetch data from external API (may timeout)"
    agent: integration_agent
    max_retries: 3          # Retry up to 3 times
    timeout_seconds: 30     # Timeout each attempt after 30s
```

**Retry Behavior:**

1. Task executes and fails (timeout, LLM error, tool failure)
2. If `retry_count < max_retries`, task resets to PENDING
3. Task re-executes with same inputs
4. Process repeats until success or max retries exceeded
5. On final failure, task status set to FAILED (workflow stops)

**Current Implementation:**

```python
except Exception as e:
    logger.error(f"Task {task.id} failed: {e}")
    task.error = str(e)

    # Retry if allowed
    if task.retry_count < task.max_retries:
        task.retry_count += 1
        task.reset()  # Reset status to PENDING
        logger.info(
            f"Retrying task {task.id} "
            f"({task.retry_count}/{task.max_retries})"
        )
        return  # Exit without failing workflow

    task.status = TaskStatus.FAILED
    raise WorkflowError(f"Task '{task.id}' failed: {e}", task_id=task.id)
```

**Future Enhancement - Exponential Backoff:**

```yaml
tasks:
  - id: rate_limited_api
    name: "Call Rate-Limited API"
    agent: api_agent
    max_retries: 5
    retry_backoff: exponential  # Future: exponential, linear, constant
    retry_delay_ms: 1000        # Future: initial delay
    retry_max_delay_ms: 60000   # Future: cap at 60s
```

**Timeout Enforcement:**

```yaml
# Workflow-level timeout (applies to entire execution)
timeout_seconds: 3600  # 1 hour for entire workflow

tasks:
  # Task-level timeout (overrides workflow timeout for this task)
  - id: quick_task
    timeout_seconds: 60   # This task must complete in 60s

  - id: long_running
    timeout_seconds: 1800 # This task gets 30 minutes

  - id: default_timeout
    # No timeout specified, uses workflow default (3600s)
```

**Timeout Behavior:**

- Workflow timeout: If total execution time exceeds this, workflow fails
- Task timeout: If task execution exceeds this, task fails (can retry)
- Agent tasks delegate to orchestrator, which enforces LLM timeouts

**Conditional Execution (Future Enhancement):**

```yaml
# Future: Conditional task execution based on prior results
tasks:
  - id: analyze_sentiment
    outputs:
      - sentiment_score

  - id: send_alert
    depends_on:
      - analyze_sentiment
    condition: "$sentiment_score < 0.3"  # Only run if negative
```

**Error Handling Modes:**

Currently, Friday uses **fail-fast** mode: any task failure stops the workflow. Future enhancements will add:

```yaml
# Future: Error handling modes
error_handling: fail_fast  # or continue_on_error, best_effort

tasks:
  - id: optional_enhancement
    error_handling: continue  # Don't fail workflow if this task fails
    depends_on:
      - core_task

  - id: critical_task
    error_handling: fail_fast  # Fail workflow immediately if this fails
```

**Task Priority (Future Enhancement):**

```yaml
# Future: Priority for task scheduling (when parallelizing)
tasks:
  - id: high_priority
    priority: 10  # Run first among ready tasks

  - id: low_priority
    priority: 1   # Run last
```

**For Project Leaders:** Retry and timeout configurations make workflows production-ready. External API calls, LLM requests, and tool executions can fail transiently—retries handle this gracefully without manual intervention. Timeouts prevent runaway tasks from consuming resources indefinitely.

**For IT Leaders:** Timeout and retry settings enable SLA guarantees. By setting appropriate values, you can ensure workflows complete within business requirements or fail fast with clear error messages. This is essential for customer-facing processes where delays impact user experience.

**For Users:** Retry logic means workflows can recover from temporary failures (network hiccups, API rate limits, transient LLM errors) without your intervention. Friday automatically retries failed tasks, giving you reliable execution even in unreliable environments.

---

### 8.2.3 Human-in-the-Loop Approval Gates

Approval gates enable human oversight at critical decision points in workflows. When a task requires approval, the workflow pauses until a human reviews and approves (or skips) the task.

**Approval Gate Syntax:**

```yaml
tasks:
  - id: deploy_to_production
    name: "Deploy to Production"
    description: "Deploy the application to production environment"
    agent: devops_agent
    requires_approval: true  # Pause for human approval before executing
    inputs:
      deployment_config: "$config"
```

**Approval Workflow:**

```
┌────────────────────────────────────────────────────────┐
│              Approval Gate Flow                         │
├────────────────────────────────────────────────────────┤
│                                                         │
│  1. Task ready to execute                              │
│     ├─ requires_approval: true                         │
│     └─ dependencies satisfied                          │
│                                                         │
│  2. Engine checks for approval callback               │
│     ├─ Callback configured?                            │
│     │  ├─ YES: Call callback(task)                    │
│     │  │  ├─ Returns True: Continue execution         │
│     │  │  └─ Returns False: Skip task                │
│     │  │                                               │
│     │  └─ NO: Pause execution                         │
│     │     ├─ Set task.status = WAITING_APPROVAL       │
│     │     ├─ Set execution.pending_approval = task_id │
│     │     └─ Return execution to caller               │
│     │                                                   │
│  3. Human reviews task                                 │
│     ├─ View task description and inputs               │
│     ├─ Assess risk and correctness                    │
│     └─ Make decision                                   │
│                                                         │
│  4. Human approves or skips                            │
│     ├─ APPROVE: engine.approve_task(task_id)          │
│     │  ├─ Reset task.status = PENDING                 │
│     │  ├─ Clear requires_approval flag                │
│     │  └─ Resume execution                            │
│     │                                                   │
│     └─ SKIP: engine.skip_task(task_id)                │
│        ├─ Set task.status = SKIPPED                   │
│        ├─ Skip dependent tasks                        │
│        └─ Resume execution                            │
│                                                         │
└────────────────────────────────────────────────────────┘
```

**Approval Callback (Programmatic):**

For automated testing or conditional auto-approval:

```python
from friday_agent.workflows import WorkflowEngine

async def approval_callback(task: TaskNode) -> bool:
    """
    Handle approval gate.

    Args:
        task: Task requiring approval

    Returns:
        True to approve, False to skip
    """
    # Example: Auto-approve low-risk tasks
    if task.id.startswith("test_"):
        print(f"Auto-approving test task: {task.name}")
        return True

    # Example: Prompt user for high-risk tasks
    print(f"\nApproval Required: {task.name}")
    print(f"Description: {task.description}")
    response = input("Approve? (yes/no): ")
    return response.lower() in ["yes", "y"]

# Create engine with callback
engine = WorkflowEngine(
    orchestrator=orchestrator,
    approval_callback=approval_callback
)

execution = await engine.execute(workflow, initial_inputs)
```

**Manual Approval (CLI):**

Without a callback, workflows pause at approval gates:

```bash
# Start workflow
Friday> /workflow run newsletter user_topic="AI in Healthcare"

# Workflow executes until approval gate
⏸️  Workflow paused at approval gate: review_research

Task: Review Research Results
Description: Review the research results for accuracy...
Inputs:
  - research: [3,500 words of research content]

Options:
  /workflow approve    - Approve and continue
  /workflow skip       - Skip this task
  /workflow status     - View current status

# User reviews and approves
Friday> /workflow approve

✓ Task 'review_research' approved
▶️  Resuming workflow execution...
```

**Approval API Methods:**

```python
# Approve a waiting task
execution = await engine.approve_task(
    workflow=workflow,
    execution=execution,
    task_id="review_research"
)

# Skip a waiting task
execution = await engine.skip_task(
    workflow=workflow,
    execution=execution,
    task_id="review_research"
)
```

**Implementation Details:**

```python
async def _handle_approval(self, task: TaskNode, execution: WorkflowExecution) -> bool:
    """Handle approval gate."""
    if self._approval_callback is None:
        # No callback - pause execution
        task.status = TaskStatus.WAITING_APPROVAL
        execution.pending_approval = task.id
        raise WorkflowError(
            f"Task '{task.id}' requires approval",
            task_id=task.id
        )

    # Ask for approval via callback
    logger.info(f"Requesting approval for task: {task.id}")
    approved = await self._approval_callback(task)

    if not approved:
        # User denied approval - skip task
        task.status = TaskStatus.SKIPPED
        task.completed_at = datetime.utcnow()
        execution.record_task(task)
        logger.info(f"Task skipped (not approved): {task.id}")
        return False

    return True  # Approved - continue execution
```

**Common Approval Gate Use Cases:**

1. **Deployment Approval:**
```yaml
- id: deploy_production
  name: "Deploy to Production"
  requires_approval: true  # Human verifies before deploying
```

2. **Data Deletion:**
```yaml
- id: delete_old_records
  name: "Delete Old Records"
  requires_approval: true  # Confirm before irreversible action
```

3. **Expensive API Calls:**
```yaml
- id: run_batch_analysis
  name: "Run Batch Analysis"
  description: "Cost: $50-100 depending on data size"
  requires_approval: true  # Confirm cost before proceeding
```

4. **Content Publication:**
```yaml
- id: publish_article
  name: "Publish Article to Website"
  requires_approval: true  # Editorial review before publishing
```

5. **External Notifications:**
```yaml
- id: send_customer_emails
  name: "Send Email to 10,000 Customers"
  requires_approval: true  # Verify message before sending
```

**Skipping Tasks:**

When a task is skipped (approval denied):
- Task status set to SKIPPED
- Task outputs are NOT created (variables remain undefined)
- Dependent tasks that require skipped task's outputs will fail with "Missing variable" error
- Workflow continues with independent tasks (if any)

**Multiple Approval Gates:**

Workflows can have multiple approval gates:

```yaml
tasks:
  - id: task_a
    requires_approval: false

  - id: task_b
    depends_on: [task_a]
    requires_approval: true   # First approval gate

  - id: task_c
    depends_on: [task_b]
    requires_approval: false

  - id: task_d
    depends_on: [task_c]
    requires_approval: true   # Second approval gate
```

Workflow execution pauses at each gate until approved.

**For Project Leaders:** Approval gates provide governance without blocking automation. Routine tasks run automatically, high-risk tasks pause for review. This enables "trust but verify" workflows where agents handle the bulk of work but humans retain control over critical decisions.

**For IT Leaders:** Approval gates are the compliance boundary. Regulated processes (financial transactions, data access, content publication) require documented human oversight—approval gates provide this with full audit trails (who approved, when, what they approved).

**For Users:** Approval gates give you control over automated processes. You don't need to monitor every step, but Friday pauses at critical moments to ask "should I proceed?" This balance of automation and oversight lets you trust Friday with important tasks.

---

## 8.3 Workflow Loader & Execution

### 8.3.1 Loading Workflows from YAML

The `WorkflowLoader` discovers and loads workflow definitions from YAML files in a designated directory.

**Basic Usage:**

```python
from pathlib import Path
from friday_agent.workflows import WorkflowLoader

# Initialize loader (defaults to ./workflows/ directory)
loader = WorkflowLoader()

# Or specify custom directory
loader = WorkflowLoader(Path("/path/to/workflows"))

# Load specific workflow
workflow = loader.load("newsletter")

# Load all workflows
all_workflows = loader.load_all()  # Returns dict: {name: WorkflowDefinition}

# List available workflows
workflow_names = loader.list_workflows()  # Returns ['newsletter', 'code_review', ...]
```

**Loader Implementation:**

```python
class WorkflowLoader:
    """Load workflow definitions from YAML files."""

    def __init__(self, workflows_dir: Path | str | None = None):
        """
        Initialize loader.

        Args:
            workflows_dir: Directory containing workflow YAML files.
                          Defaults to ./workflows/ relative to cwd.
        """
        if workflows_dir is None:
            self._workflows_dir = Path.cwd() / "workflows"
        else:
            self._workflows_dir = Path(workflows_dir)

        self._cache: dict[str, WorkflowDefinition] = {}
```

**Loading Process:**

```
┌──────────────────────────────────────────────────────┐
│            Workflow Loading Process                   │
├──────────────────────────────────────────────────────┤
│                                                       │
│  1. Check cache                                      │
│     └─ If cached, return immediately                │
│                                                       │
│  2. Locate YAML file                                 │
│     ├─ Try {name}.yaml                               │
│     └─ Try {name}.yml                                │
│                                                       │
│  3. Parse YAML                                       │
│     ├─ Read file with UTF-8 encoding                │
│     ├─ yaml.safe_load() for security                │
│     └─ Validate root structure (dict required)      │
│                                                       │
│  4. Validate required fields                         │
│     ├─ Check: id, name, description, tasks          │
│     └─ Fail if missing                               │
│                                                       │
│  5. Parse tasks                                      │
│     ├─ Create TaskNode for each task                │
│     └─ Pydantic validates fields and types          │
│                                                       │
│  6. Create WorkflowDefinition                        │
│     └─ Set all fields from YAML                     │
│                                                       │
│  7. Validate graph                                   │
│     ├─ Check for duplicate task IDs                 │
│     ├─ Check dependencies exist                     │
│     └─ Check for cycles (topological sort)          │
│                                                       │
│  8. Cache and return                                 │
│     ├─ Store in cache for future loads              │
│     └─ Return WorkflowDefinition                    │
│                                                       │
└──────────────────────────────────────────────────────┘
```

**Error Handling:**

```python
def load(self, name: str) -> WorkflowDefinition:
    """Load workflow by name."""
    # Check cache
    if name in self._cache:
        return self._cache[name]

    # Locate file
    path = self._workflows_dir / f"{name}.yaml"
    if not path.exists():
        path = self._workflows_dir / f"{name}.yml"
        if not path.exists():
            raise WorkflowLoadError(f"Workflow not found: {name}")

    # Parse YAML
    workflow = self._parse_yaml(path)

    # Validate graph
    errors = workflow.validate_graph()
    if errors:
        raise WorkflowLoadError(f"Invalid workflow '{name}': {errors}")

    # Cache and return
    self._cache[name] = workflow
    logger.info(f"Loaded workflow: {name}")
    return workflow
```

**Validation Errors:**

Common validation errors and their meanings:

```python
# Missing required fields
WorkflowLoadError: "Missing required fields: ['description', 'tasks']"

# Invalid YAML syntax
WorkflowLoadError: "Invalid YAML in newsletter.yaml: mapping values are not allowed here"

# Duplicate task IDs
WorkflowLoadError: "Invalid workflow 'newsletter': ['Duplicate task IDs found']"

# Undefined dependencies
WorkflowLoadError: "Invalid workflow 'newsletter': [\"Task 'write_draft' depends on unknown task 'research_v2'\"]"

# Circular dependencies
WorkflowLoadError: "Invalid workflow 'newsletter': ['Workflow contains dependency cycles']"
```

**Caching Behavior:**

The loader caches workflows after first load:

```python
# First load: reads from disk and parses
workflow1 = loader.load("newsletter")  # ~10-50ms

# Second load: returns cached instance
workflow2 = loader.load("newsletter")  # <1ms

# Same object reference
assert workflow1 is workflow2  # True
```

**Cache Management:**

```python
# Force reload (bypass cache)
workflow = loader.reload("newsletter")

# Clear entire cache
loader.clear_cache()
```

**Use Cases for Cache Management:**

1. **Development**: Hot-reload workflows during development
2. **Testing**: Clear cache between test runs for isolation
3. **Production**: Cache workflows for performance, reload on deployment

**Directory Organization:**

```
project/
├── workflows/
│   ├── newsletter.yaml           # Simple filename
│   ├── code-review.yaml          # Hyphenated allowed
│   ├── data_analysis.yaml        # Underscores allowed
│   └── templates/                # Subdirectories (future support)
│       ├── research-report.yaml
│       └── qa-pipeline.yaml
```

Current implementation searches only top-level directory. Subdirectory support is planned.

**For Project Leaders:** The loader's caching and validation ensures workflows are loaded efficiently and correctly. YAML files are version-controllable, enabling workflow-as-code practices with git, code review, and CI/CD integration.

**For IT Leaders:** Validation at load time prevents invalid workflows from reaching production. All structural errors (missing dependencies, cycles, syntax errors) are caught before execution, reducing runtime failures and resource waste.

**For Users:** Loading workflows is transparent—you specify a name, Friday finds and validates it. If there are errors, you get clear messages about what's wrong and where, making workflow development straightforward.

---

### 8.3.2 Executing Workflows via CLI

The `memory-chat-v2.py` CLI provides commands for listing, executing, and managing workflows interactively.

**Workflow Commands:**

```bash
/workflow list                           # List available workflows
/workflow run <name> [inputs]           # Execute a workflow
/workflow status                         # Show execution status
/workflow approve                        # Approve pending task
/workflow skip                           # Skip pending task
```

**Listing Workflows:**

```bash
Friday> /workflow list

Available Workflows:
┌─────────────────────┬──────────────────────────────────┬────────┬─────────┐
│ Name                │ Description                       │ Tasks  │ Version │
├─────────────────────┼──────────────────────────────────┼────────┼─────────┤
│ newsletter          │ Research and write newsletter    │ 4      │ 1.0.0   │
│ code_review         │ Review code with static analysis │ 3      │ 1.0.0   │
│ research_report     │ Research topic and generate PDF  │ 5      │ 1.0.0   │
└─────────────────────┴──────────────────────────────────┴────────┴─────────┘
```

**Running Workflows:**

Basic execution:

```bash
# Without initial inputs (if workflow doesn't require any)
Friday> /workflow run simple_task

# With initial inputs (key=value pairs)
Friday> /workflow run newsletter user_topic="AI in Healthcare 2025"

# Multiple inputs
Friday> /workflow run data_analysis dataset="/path/to/data.csv" output_format="json"

# String values with spaces (use quotes)
Friday> /workflow run report topic="Climate Change Policy" urgency="high"
```

**Execution Flow (No Approval Gates):**

```bash
Friday> /workflow run newsletter user_topic="AI Trends 2025"

🚀 Starting workflow: Newsletter Generation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▶️  Executing task: research (Research Topic)
   Agent: researcher
   Inputs: topic="AI Trends 2025"
   ...
✓  Task completed in 45.2s

▶️  Executing task: review_research (Review Research Results)
   Agent: researcher
   Inputs: research=[research results]
   ...
⏸️  Task requires approval

Task: Review Research Results
Description: Review the research results for accuracy...
Inputs:
  - research: [3,500 words of research]

/workflow approve  - Approve and continue
/workflow skip     - Skip this task
/workflow status   - View status
```

**Approval Workflow:**

```bash
# User reviews content and decides to approve
Friday> /workflow approve

✓ Task 'review_research' approved
▶️  Resuming workflow execution...

▶️  Executing task: write_draft (Write Newsletter Draft)
   Agent: coder
   Inputs: research=[approved research]
   ...
✓  Task completed in 35.8s

▶️  Executing task: final_review (Final Newsletter Review)
   Agent: coder
   Inputs: draft=[newsletter draft]
   ...
⏸️  Task requires approval

# User reviews final draft
Friday> /workflow approve

✓ Task 'final_review' approved
▶️  Resuming workflow execution...
✅ Workflow completed successfully

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Workflow: Newsletter Generation
Status: COMPLETED
Duration: 2m 15s
Tasks: 4/4 completed

Outputs:
  $research_results: [research summary]
  $approved_research: [approved version]
  $newsletter_draft: [draft content]
  $final_newsletter: [final newsletter]

Use `/workflow status` to view detailed status
```

**Checking Status:**

```bash
Friday> /workflow status

Workflow Execution Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Workflow: newsletter_generation
Execution ID: newsletter_generation_1737718800
Status: WAITING_APPROVAL
Started: 2026-01-24 10:15:00
Duration: 1m 20s

Pending Approval: final_review

Tasks:
┌─────────────────┬──────────┬──────────┬─────────────┬────────┐
│ Task ID         │ Name     │ Status   │ Agent       │ Time   │
├─────────────────┼──────────┼──────────┼─────────────┼────────┤
│ research        │ Research │ ✓        │ researcher  │ 45.2s  │
│ review_research │ Review   │ ✓        │ researcher  │ 30.0s  │
│ write_draft     │ Write    │ ✓        │ coder       │ 35.8s  │
│ final_review    │ Final    │ ⏸️       │ coder       │ -      │
└─────────────────┴──────────┴──────────┴─────────────┴────────┘

Variables:
  $user_topic: "AI Trends 2025"
  $research_results: [3,500 words]
  $approved_research: [3,500 words]
  $newsletter_draft: [750 words]

Use `/workflow approve` to approve pending task
```

**Skipping Tasks:**

```bash
# User decides not to approve final review
Friday> /workflow skip

⏭️  Task 'final_review' skipped
▶️  Resuming workflow execution...
⚠️  Workflow completed with skipped tasks

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Workflow: Newsletter Generation
Status: COMPLETED
Duration: 1m 25s
Tasks: 3/4 completed, 1 skipped

Note: Task 'final_review' was skipped
Output variable $final_newsletter not created
```

**Error Handling:**

```bash
# Task fails
▶️  Executing task: write_draft (Write Newsletter Draft)
   Agent: coder
   Inputs: research=[approved research]
   ...
❌ Task failed: LLM timeout after 60s

🔄 Retrying task (attempt 1/3)...
▶️  Executing task: write_draft (Write Newsletter Draft)
   ...
✓  Task completed in 42.1s (retry succeeded)

# Retry exhausted
🔄 Retrying task (attempt 3/3)...
❌ Task failed: LLM timeout after 60s
❌ Max retries exhausted for task 'write_draft'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Workflow FAILED
Task: write_draft
Error: LLM timeout after 60s
Duration: 3m 45s

Use `/workflow status` for full details
```

**For Project Leaders:** CLI workflow execution provides an interactive interface for running and monitoring workflows. This is ideal for development, testing, and manual triggering of production workflows. Approval gates enable collaborative workflows where humans review agent work at critical stages.

**For IT Leaders:** The CLI provides full visibility into workflow execution—real-time status, task-by-task progress, timing metrics, and error details. This transparency enables debugging, performance tuning, and compliance verification without requiring log analysis.

**For Users:** Running workflows via CLI is straightforward—specify the workflow name and initial inputs, then Friday handles the rest. When approval is needed, Friday pauses and clearly explains what needs review, making collaborative automation accessible to non-technical users.

---

### 8.3.3 Workflow Engine Internals

This section provides a technical deep dive into the `WorkflowEngine` implementation for developers wanting to extend or debug the workflow system.

**Engine Architecture:**

```python
class WorkflowEngine:
    """
    Executes workflow task graphs.

    The engine processes a workflow definition by:
    1. Resolving task dependencies (topological order)
    2. Executing tasks via the orchestrator
    3. Passing outputs to inputs via variables
    4. Pausing at approval gates for human review
    5. Handling failures and retries
    """

    def __init__(
        self,
        orchestrator: AgentOrchestrator,
        approval_callback: Callable[[TaskNode], Awaitable[bool]] | None = None,
    ):
        """
        Initialize workflow engine.

        Args:
            orchestrator: Agent orchestrator for task execution
            approval_callback: Optional async function to request human approval
        """
        self._orchestrator = orchestrator
        self._approval_callback = approval_callback
```

**Execution Algorithm:**

```python
async def execute(
    self,
    workflow: WorkflowDefinition,
    initial_inputs: dict[str, Any] | None = None,
) -> WorkflowExecution:
    """Execute a workflow."""
    # 1. Validate workflow graph
    errors = workflow.validate_graph()
    if errors:
        raise WorkflowError(f"Invalid workflow: {errors}")

    # 2. Create execution state
    execution = WorkflowExecution(
        workflow_id=workflow.id,
        execution_id=f"{workflow.id}_{int(datetime.utcnow().timestamp())}",
        variables=initial_inputs or {},
        started_at=datetime.utcnow(),
    )

    # 3. Execute workflow
    try:
        await self._run_workflow(workflow, execution)
        execution.status = TaskStatus.COMPLETED
    except WorkflowError as e:
        if execution.pending_approval:
            execution.status = TaskStatus.WAITING_APPROVAL
        else:
            execution.status = TaskStatus.FAILED
            raise
    finally:
        if execution.status != TaskStatus.WAITING_APPROVAL:
            execution.completed_at = datetime.utcnow()

    return execution
```

**Core Execution Loop:**

```python
async def _run_workflow(
    self,
    workflow: WorkflowDefinition,
    execution: WorkflowExecution,
) -> None:
    """Run workflow until completion or pause."""
    execution.status = TaskStatus.RUNNING

    while True:
        # Get tasks that are ready to execute (dependencies satisfied)
        ready_tasks = workflow.get_ready_tasks()

        if not ready_tasks:
            # Check if all tasks are done
            all_done = all(
                t.status in (TaskStatus.COMPLETED, TaskStatus.SKIPPED, TaskStatus.FAILED)
                for t in workflow.tasks
            )
            if all_done:
                break  # Workflow complete

            # Check for approval gates
            waiting = next(
                (t for t in workflow.tasks if t.status == TaskStatus.WAITING_APPROVAL),
                None
            )
            if waiting:
                execution.pending_approval = waiting.id
                raise WorkflowError(
                    f"Task '{waiting.id}' waiting for approval",
                    task_id=waiting.id
                )

            # Check for failures blocking progress
            failed = [t for t in workflow.tasks if t.status == TaskStatus.FAILED]
            if failed:
                raise WorkflowError(
                    f"Workflow blocked by failed tasks: {[t.id for t in failed]}"
                )

            # Unexpected state
            raise WorkflowError("Workflow stuck: no ready tasks and not complete")

        # Execute ready tasks sequentially
        for task in ready_tasks:
            await self._execute_task(task, workflow, execution)
```

**Task Execution:**

```python
async def _execute_task(
    self,
    task: TaskNode,
    workflow: WorkflowDefinition,
    execution: WorkflowExecution,
) -> None:
    """Execute a single task."""
    execution.current_task_id = task.id
    task.status = TaskStatus.RUNNING
    task.started_at = datetime.utcnow()

    try:
        # 1. Check approval gate
        if task.requires_approval:
            approved = await self._handle_approval(task, execution)
            if not approved:
                task.status = TaskStatus.SKIPPED
                task.completed_at = datetime.utcnow()
                execution.record_task(task)
                return

        # 2. Resolve inputs from variables
        resolved_inputs = self._resolve_inputs(task, execution.variables)

        # 3. Build prompt from task description and inputs
        prompt = self._build_prompt(task, resolved_inputs)

        # 4. Execute via orchestrator (delegates to agent)
        result = await self._orchestrator.delegate(
            task.agent,
            prompt,
            return_to_current=True,
        )

        # 5. Store result in task
        task.result = result

        # 6. Store outputs in variables
        for output_name in task.outputs:
            execution.variables[output_name] = result

        task.status = TaskStatus.COMPLETED

    except WorkflowError:
        raise  # Re-raise workflow errors (approval pausing)
    except Exception as e:
        task.error = str(e)

        # Retry if allowed
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.reset()
            return  # Exit without failing

        task.status = TaskStatus.FAILED
        raise WorkflowError(f"Task '{task.id}' failed: {e}", task_id=task.id)
    finally:
        task.completed_at = datetime.utcnow()
        execution.record_task(task)
        execution.current_task_id = None
```

**Input Resolution:**

```python
def _resolve_inputs(
    self,
    task: TaskNode,
    variables: dict[str, Any],
) -> dict[str, Any]:
    """
    Resolve task inputs from variable store.

    Input values starting with $ are variable references.
    Other values are literal.
    """
    resolved = {}

    for input_name, source in task.inputs.items():
        if source.startswith("$"):
            var_name = source[1:]
            if var_name not in variables:
                raise WorkflowError(
                    f"Missing variable: ${var_name} (required by task '{task.id}')",
                    task_id=task.id
                )
            resolved[input_name] = variables[var_name]
        else:
            resolved[input_name] = source  # Literal value

    return resolved
```

**Prompt Building:**

```python
def _build_prompt(
    self,
    task: TaskNode,
    inputs: dict[str, Any],
) -> str:
    """Build agent prompt from task and inputs."""
    parts = [task.description]

    if inputs:
        parts.append("\n\nInputs:")
        for name, value in inputs.items():
            # Truncate long values for readability
            value_str = str(value)
            if len(value_str) > 500:
                value_str = value_str[:500] + "..."
            parts.append(f"- {name}: {value_str}")

    return "\n".join(parts)
```

**Approval Resumption:**

```python
async def approve_task(
    self,
    workflow: WorkflowDefinition,
    execution: WorkflowExecution,
    task_id: str,
) -> WorkflowExecution:
    """Approve a waiting task and continue execution."""
    task = workflow.get_task(task_id)
    if task is None:
        raise WorkflowError(f"Task not found: {task_id}")

    if task.status != TaskStatus.WAITING_APPROVAL:
        raise WorkflowError(f"Task '{task_id}' not waiting for approval")

    # Mark as approved - clear approval requirement so it doesn't trigger again
    task.status = TaskStatus.PENDING
    task.requires_approval = False  # Already approved
    execution.pending_approval = None

    # Continue execution
    try:
        await self._run_workflow(workflow, execution)
        execution.status = TaskStatus.COMPLETED
        execution.completed_at = datetime.utcnow()
    except WorkflowError as e:
        if execution.pending_approval:
            execution.status = TaskStatus.WAITING_APPROVAL
        else:
            raise

    return execution
```

**Key Design Decisions:**

1. **Sequential Execution**: Currently, ready tasks execute sequentially. Future enhancement: parallel execution for independent tasks.

2. **Approval Pausing**: Approval gates use exception-based control flow to pause execution cleanly without complex state machines.

3. **Agent Delegation**: Tasks execute via `orchestrator.delegate()`, maintaining separation between workflow logic and agent execution.

4. **Stateful Execution**: `WorkflowExecution` is a mutable object tracking state changes. This enables pausing/resuming and status inspection.

5. **Fail-Fast Default**: Any task failure stops the workflow immediately (unless retries succeed). Future: configurable error handling modes.

**Extension Points:**

Developers can extend the workflow engine by:

1. **Custom Approval Callbacks**: Implement custom approval logic (conditional auto-approval, external systems, Slack notifications)

2. **Parallel Execution**: Fork the engine and implement parallel task execution for independent tasks

3. **Custom Task Types**: Subclass `TaskNode` for specialized task behaviors (conditional execution, loops, dynamic task generation)

4. **Workflow Persistence**: Serialize `WorkflowExecution` to database for resumption across process restarts

5. **Monitoring Hooks**: Add lifecycle hooks (on_task_start, on_task_complete) for observability integration

**For Project Leaders:** Understanding the engine internals enables custom workflow features. The architecture is extensible—you can add parallel execution, custom task types, or integration with external workflow systems without rewriting core logic.

**For IT Leaders:** The engine's stateful design enables workflow persistence and resumption. If a process crashes mid-workflow, you can serialize execution state and resume later. This is essential for long-running workflows (hours/days) in production environments.

**For Users:** While you don't need to understand engine internals to use workflows, knowing the execution model helps debug complex workflows. Understanding how tasks become "ready" and how variables flow through the graph clarifies why workflows behave as they do.

---

## 8.4 Example Workflows & Templates

### 8.4.1 Newsletter Generation Workflow

The newsletter generation workflow demonstrates multi-agent collaboration with research, writing, and approval gates.

**Workflow File:** `/Users/chuckrussell/Dev/gendev/agent-framework/workflows/newsletter.yaml`

**Complete Definition:**

```yaml
# Newsletter Generation Workflow
# Researches a topic and generates a newsletter article

id: newsletter_generation
name: "Newsletter Generation"
description: "Research a topic and generate a newsletter article with human review"
version: "1.0.0"
author: "friday-team"
tags: ["content", "research", "writing"]

tasks:
  - id: research
    name: "Research Topic"
    description: |
      Research the given topic and gather key information.
      Focus on:
      - Recent developments
      - Key statistics
      - Expert opinions
      - Relevant examples

      Provide a comprehensive research summary.
    agent: researcher
    inputs:
      topic: "$user_topic"
    outputs:
      - research_results
    requires_approval: false

  - id: review_research
    name: "Review Research Results"
    description: |
      Review the research results for accuracy and completeness.

      Research to review:
      {{research}}

      Provide feedback or approve to continue.
    agent: researcher
    inputs:
      research: "$research_results"
    outputs:
      - approved_research
    depends_on:
      - research
    requires_approval: true

  - id: write_draft
    name: "Write Newsletter Draft"
    description: |
      Write a newsletter article based on the approved research.

      Guidelines:
      - Engaging headline
      - Clear introduction
      - Key points with supporting details
      - Call to action
      - 500-800 words
    agent: coder
    inputs:
      research: "$approved_research"
    outputs:
      - newsletter_draft
    depends_on:
      - review_research
    requires_approval: false

  - id: final_review
    name: "Final Newsletter Review"
    description: |
      Review the final newsletter draft.

      Check for:
      - Accuracy
      - Clarity
      - Tone
      - Grammar

      Approve to publish or provide feedback.
    agent: coder
    inputs:
      draft: "$newsletter_draft"
    outputs:
      - final_newsletter
    depends_on:
      - write_draft
    requires_approval: true

timeout_seconds: 7200
max_retries: 2
```

**Execution Example:**

```bash
Friday> /workflow run newsletter user_topic="Quantum Computing Breakthroughs 2025"

🚀 Starting workflow: Newsletter Generation

▶️  Task: research (Research Topic)
   🔍 Researching "Quantum Computing Breakthroughs 2025"...
   🌐 Using web_search to find recent articles
   📄 Found 12 relevant sources
   📝 Summarizing key findings...
✓  Completed in 48.3s

⏸️  Task: review_research (Review Research Results)
   Approval Required

Research Summary (3,850 words):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quantum Computing Breakthroughs in 2025

Key Developments:
1. IBM's 1000-qubit quantum processor (March 2025)
2. Google's error correction milestone (June 2025)
3. Commercial applications in drug discovery
...
[Full research content displayed]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/workflow approve - Continue    /workflow skip - Skip

Friday> /workflow approve

✓  Task approved, continuing...

▶️  Task: write_draft (Write Newsletter Draft)
   ✍️  Drafting newsletter article...
   📊 Word count: 687
   🎯 Tone: Professional, accessible
✓  Completed in 42.1s

⏸️  Task: final_review (Final Newsletter Review)
   Approval Required

Newsletter Draft:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"Quantum Leap: 2025's Computing Revolution"

The quantum computing landscape transformed dramatically in 2025,
with three major breakthroughs marking a turning point from
laboratory curiosity to practical technology...

[Full newsletter displayed]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/workflow approve - Publish    /workflow skip - Discard

Friday> /workflow approve

✓  Task approved
✅ Workflow completed successfully

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Newsletter Generation - COMPLETED
Duration: 2m 35s
Tasks: 4/4 completed

Output: $final_newsletter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Use Cases:**

- Content marketing teams generating weekly newsletters
- Internal communications creating company updates
- Educational institutions producing research summaries
- Media organizations drafting news articles

**Customization Options:**

```yaml
# Variation: Skip human review for internal drafts
- id: review_research
  requires_approval: false  # Auto-approve for internal use

# Variation: Add SEO optimization task
- id: optimize_seo
  name: "Optimize for SEO"
  description: "Add meta description, keywords, and optimize headings"
  agent: seo_specialist
  depends_on: [write_draft]
  inputs:
    draft: "$newsletter_draft"
  outputs:
    - optimized_draft

# Variation: Add fact-checking task
- id: fact_check
  name: "Verify Facts"
  description: "Cross-reference all claims with sources"
  agent: fact_checker
  depends_on: [write_draft]
  inputs:
    draft: "$newsletter_draft"
    sources: "$research_results"
  outputs:
    - verified_draft
```

---

### 8.4.2 Code Review Workflow

Automated code review workflow with static analysis, testing, and security scanning.

**Workflow Definition:**

```yaml
id: code_review
name: "Automated Code Review"
description: "Review code changes with static analysis, tests, and security checks"
version: "1.0.0"
author: "friday-team"
tags: ["code", "review", "testing", "security"]

tasks:
  - id: analyze_code
    name: "Static Code Analysis"
    description: |
      Run static analysis on the codebase.

      Checks:
      - Code style violations (Ruff, ESLint)
      - Type errors (mypy)
      - Complexity metrics
      - Code smells

      Provide summary of issues found.
    agent: coder
    inputs:
      repo_path: "$repository_path"
      files_changed: "$changed_files"
    outputs:
      - analysis_report
    requires_approval: false

  - id: run_tests
    name: "Run Test Suite"
    description: |
      Execute the full test suite.

      Report:
      - Pass/fail status
      - Coverage metrics
      - Failed test details
      - Performance regressions
    agent: coder
    inputs:
      repo_path: "$repository_path"
    outputs:
      - test_results
    requires_approval: false

  - id: security_scan
    name: "Security Vulnerability Scan"
    description: |
      Scan for security vulnerabilities.

      Tools:
      - Bandit (Python)
      - npm audit (JavaScript)
      - Dependency vulnerability checks

      Flag high-severity issues.
    agent: security_specialist
    inputs:
      repo_path: "$repository_path"
    outputs:
      - security_report
    requires_approval: false

  - id: review_gate
    name: "Review Results"
    description: |
      Review all analysis results:

      Static Analysis: {{analysis}}
      Test Results: {{tests}}
      Security Scan: {{security}}

      Approve if all checks pass or issues are acceptable.
      Skip to reject changes.
    agent: coder
    depends_on:
      - analyze_code
      - run_tests
      - security_scan
    inputs:
      analysis: "$analysis_report"
      tests: "$test_results"
      security: "$security_report"
    outputs:
      - review_decision
    requires_approval: true

  - id: merge_changes
    name: "Merge to Main Branch"
    description: |
      Merge approved changes to main branch.

      Executes: git merge --no-ff {branch}
    agent: coder
    depends_on:
      - review_gate
    inputs:
      branch: "$source_branch"
    outputs:
      - merge_result
    requires_approval: false

timeout_seconds: 1800  # 30 minutes
max_retries: 1
```

**Execution Example:**

```bash
Friday> /workflow run code_review repository_path="/project" changed_files="src/main.py,tests/test_main.py" source_branch="feature/auth"

🚀 Starting workflow: Automated Code Review

▶️  Task: analyze_code (Static Code Analysis)
   🔍 Running Ruff on 2 changed files...
   ✓ No style violations found
   🔍 Running mypy...
   ⚠️  3 type warnings in src/main.py
✓  Completed in 8.4s

▶️  Task: run_tests (Run Test Suite)
   🧪 Running pytest...
   ✓ 127 tests passed
   ✓ Coverage: 92.3% (+1.2%)
✓  Completed in 23.7s

▶️  Task: security_scan (Security Vulnerability Scan)
   🔒 Running Bandit...
   ✓ No high-severity issues
   ⚠️  1 medium-severity warning (hardcoded secret detection)
✓  Completed in 12.1s

⏸️  Task: review_gate (Review Results)
   Approval Required

Code Review Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Static Analysis: ⚠️  3 type warnings
  - Line 45: Argument type mismatch
  - Line 67: Missing return type annotation
  - Line 89: Unreachable code detected

Tests: ✓ All passed (127/127)
Coverage: 92.3% ▲

Security: ⚠️  1 medium-severity issue
  - B105: Possible hardcoded password in config.py:23

Recommendation: Review type warnings and security issue before merging
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/workflow approve - Merge anyway    /workflow skip - Reject

Friday> /workflow skip

⏭️  Task skipped - changes not approved
✅ Workflow completed

Code review failed - changes not merged
Review the flagged issues and resubmit
```

**Use Cases:**

- Pull request validation in CI/CD pipelines
- Pre-commit hooks with comprehensive checks
- Scheduled code quality audits
- Security compliance scanning

---

### 8.4.3 Research & Report Workflow

Comprehensive research workflow with multi-source data gathering, synthesis, and report generation.

**Workflow Definition:**

```yaml
id: research_report
name: "Research & Report Generation"
description: "Conduct multi-source research and generate a comprehensive report"
version: "1.0.0"
author: "friday-team"
tags: ["research", "analysis", "reporting"]

tasks:
  - id: web_research
    name: "Web Research"
    description: |
      Search the web for information on the topic.
      Use multiple search queries to cover different angles.
      Save relevant URLs and key excerpts.
    agent: researcher
    inputs:
      topic: "$user_topic"
      depth: "$research_depth"  # "quick", "standard", "deep"
    outputs:
      - web_sources
    max_retries: 3

  - id: academic_search
    name: "Academic Literature Search"
    description: |
      Search academic databases for peer-reviewed research.
      Focus on recent publications (last 5 years).
      Prioritize highly-cited papers.
    agent: researcher
    inputs:
      topic: "$user_topic"
    outputs:
      - academic_sources
    requires_approval: false

  - id: scrape_sources
    name: "Scrape and Extract Content"
    description: |
      Scrape content from discovered URLs.
      Extract main text, remove ads and navigation.
      Store full-text versions for analysis.
    agent: researcher
    depends_on:
      - web_research
    inputs:
      urls: "$web_sources"
    outputs:
      - scraped_content
    max_retries: 2

  - id: synthesize
    name: "Synthesize Findings"
    description: |
      Synthesize information from all sources.

      Create:
      - Executive summary
      - Key findings (bullet points)
      - Supporting evidence
      - Conflicting viewpoints
      - Research gaps
    agent: analyst
    depends_on:
      - web_research
      - academic_search
      - scrape_sources
    inputs:
      web: "$web_sources"
      academic: "$academic_sources"
      content: "$scraped_content"
    outputs:
      - synthesis
    timeout_seconds: 600  # 10 minutes for synthesis

  - id: generate_report
    name: "Generate Final Report"
    description: |
      Generate a comprehensive report in markdown format.

      Structure:
      1. Executive Summary
      2. Introduction
      3. Methodology
      4. Findings
      5. Analysis
      6. Conclusions
      7. References

      Include charts and visualizations where appropriate.
    agent: writer
    depends_on:
      - synthesize
    inputs:
      synthesis: "$synthesis"
      format: "$output_format"  # "markdown", "pdf", "html"
    outputs:
      - final_report
    requires_approval: false

  - id: save_report
    name: "Save Report to File"
    description: |
      Save the generated report to the filesystem.
      Create necessary directories.
    agent: coder
    depends_on:
      - generate_report
    inputs:
      report: "$final_report"
      output_path: "$save_path"
    outputs:
      - saved_file_path
    requires_approval: false

timeout_seconds: 3600  # 1 hour
max_retries: 2
```

**Execution Example:**

```bash
Friday> /workflow run research_report user_topic="Impact of AI on Healthcare" research_depth="deep" output_format="markdown" save_path="/reports/ai-healthcare-2025.md"

🚀 Starting workflow: Research & Report Generation

▶️  Task: web_research (Web Research)
   🌐 Searching web sources...
   📊 Found 47 relevant articles
   🔍 Extracting key information...
✓  Completed in 52.3s

▶️  Task: academic_search (Academic Literature Search)
   📚 Searching PubMed, arXiv, Google Scholar...
   📄 Found 23 peer-reviewed papers
   ⭐ Prioritizing by citation count...
✓  Completed in 38.7s

▶️  Task: scrape_sources (Scrape and Extract Content)
   🕷️  Scraping 47 URLs...
   📄 Extracted full text from 42 sources (5 failed)
   💾 Total content: 182,500 words
✓  Completed in 67.2s

▶️  Task: synthesize (Synthesize Findings)
   🧠 Analyzing 42 web sources + 23 academic papers...
   📝 Generating synthesis...
   🔗 Cross-referencing findings...
   ⚖️  Identifying consensus and conflicts...
✓  Completed in 145.8s

▶️  Task: generate_report (Generate Final Report)
   ✍️  Writing comprehensive report...
   📊 Adding visualizations...
   📚 Formatting references...
   📄 Final length: 8,750 words
✓  Completed in 89.3s

▶️  Task: save_report (Save Report to File)
   💾 Saving to /reports/ai-healthcare-2025.md...
   ✓ File saved successfully
✓  Completed in 1.2s

✅ Workflow completed successfully

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Research & Report Generation - COMPLETED
Duration: 6m 34s
Tasks: 6/6 completed

Output: /reports/ai-healthcare-2025.md (8,750 words)
Sources: 42 web + 23 academic
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Use Cases:**

- Market research and competitive analysis
- Academic literature reviews
- Due diligence investigations
- Policy research and briefings

**Advanced Variation - Parallel Research:**

```yaml
# Future enhancement: Parallel execution
tasks:
  - id: web_research
    # No dependencies - can run in parallel

  - id: academic_search
    # No dependencies - can run in parallel

  - id: expert_interviews
    # No dependencies - can run in parallel

  - id: synthesize
    depends_on:
      - web_research
      - academic_search
      - expert_interviews
    # Waits for all parallel tasks to complete
```

When parallel execution is implemented, independent research tasks will run concurrently, reducing total workflow time from 6+ minutes to <3 minutes.

---

## Conclusion: Workflows for Production Automation

Workflows transform Friday from an interactive assistant into a production automation platform. By defining task graphs with dependencies, variable passing, and approval gates, you create repeatable, auditable processes for complex multi-agent collaboration.

**Key Takeaways:**

1. **Declarative YAML**: Workflows are defined in human-readable YAML, enabling version control, code review, and CI/CD integration

2. **Task Dependencies**: DAG-based execution ensures tasks run in the correct order with automatic dependency resolution

3. **Variable Passing**: The `$var` syntax creates data pipelines where outputs flow seamlessly to inputs

4. **Approval Gates**: Human-in-the-loop gates provide oversight at critical decision points without blocking routine automation

5. **Robust Execution**: Retries, timeouts, and comprehensive status tracking make workflows production-ready

**For Project Leaders:** Workflows enable scaling agent teams from prototypes to production. Once a workflow is defined and tested, it can execute reliably thousands of times with consistent quality. This transforms ad-hoc agent interactions into reliable business processes.

**For IT Leaders:** Workflows provide the governance, auditability, and reliability needed for production deployments. Approval gates ensure compliance, status tracking enables monitoring, and comprehensive execution history supports debugging and continuous improvement.

**For Users:** Workflows make complex, multi-step processes accessible. Instead of orchestrating multiple agents manually, you trigger a workflow and Friday handles the coordination, only pausing when your approval is needed. This balance of automation and oversight enables trust in agent-driven processes.

---

**Next Section:** [Section 9: CLI Reference - memory-chat-v2.py](09-cli-reference.md)

Comprehensive command reference for Friday's interactive CLI, including session management, memory inspection, tool management, agent orchestration, and workflow commands.
