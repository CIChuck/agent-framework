---
title: "Workflow Engine"
description: "How Friday parses, validates, and executes YAML workflow definitions."
weight: 1
---

The Friday workflow engine parses YAML definitions, validates them against the schema, resolves step dependencies, and executes steps with full error handling and retry logic.

Workflows are Friday's automation engine for complex, multi-step tasks that require coordination across multiple agents, conditional logic, and human oversight. Friday's workflow system uses declarative YAML definitions to describe directed acyclic graphs (DAGs) of tasks.

## Task Graphs & Dependencies (DAGs)

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

---

## Variable Passing with `$var` Syntax

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

```python
# Workflow execution state
execution.variables = {
    "user_topic": "AI Trends 2025",        # Initial input
    "research_results": "Research summary...",  # From research task
    "analysis_summary": "Key findings..."   # From analyze task
}

# Resolved inputs passed to agent
resolved_inputs = {
    "topic": "AI Trends 2025",           # Resolved from $user_topic
    "findings": "Key findings...",        # Resolved from $analysis_summary
    "style": "formal"                     # Literal (unchanged)
}
```

**Variable Naming Conventions:**

By convention (not enforced):
- **`$user_*`**: Initial inputs from user (`$user_topic`, `$user_options`)
- **`$task_*`**: Task-specific outputs (`$research_results`, `$analysis_summary`)
- **`$final_*`**: Final workflow outputs (`$final_report`, `$final_decision`)

**Missing Variable Error:**

If a task references an undefined variable, execution fails immediately:

```python
if var_name not in variables:
    raise WorkflowError(
        f"Missing variable: ${var_name} (required by task '{task.id}')",
        task_id=task.id
    )
```

---

## Workflow Status Tracking

The workflow engine tracks detailed execution state for observability, debugging, and resumption.

**Status Types:**

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

---

## Workflow Engine Internals

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
        self._orchestrator = orchestrator
        self._approval_callback = approval_callback
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

        # Execute ready tasks sequentially
        for task in ready_tasks:
            await self._execute_task(task, workflow, execution)
```

**Key Design Decisions:**

1. **Sequential Execution**: Currently, ready tasks execute sequentially. Future enhancement: parallel execution for independent tasks.

2. **Approval Pausing**: Approval gates use exception-based control flow to pause execution cleanly without complex state machines.

3. **Agent Delegation**: Tasks execute via `orchestrator.delegate()`, maintaining separation between workflow logic and agent execution.

4. **Stateful Execution**: `WorkflowExecution` is a mutable object tracking state changes. This enables pausing/resuming and status inspection.

5. **Fail-Fast Default**: Any task failure stops the workflow immediately (unless retries succeed). Future: configurable error handling modes.

---

## Workflow Loader

The `WorkflowLoader` discovers and loads workflow definitions from YAML files.

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

**Validation Errors:**

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

```python
# First load: reads from disk and parses
workflow1 = loader.load("newsletter")  # ~10-50ms

# Second load: returns cached instance
workflow2 = loader.load("newsletter")  # <1ms

# Force reload (bypass cache)
workflow = loader.reload("newsletter")

# Clear entire cache
loader.clear_cache()
```

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

---

## Human-in-the-Loop Approval Gates

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

**Approval Callback (Programmatic):**

```python
from friday_agent.workflows import WorkflowEngine

async def approval_callback(task: TaskNode) -> bool:
    """
    Handle approval gate.

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

**Common Approval Gate Use Cases:**

```yaml
# Deployment approval
- id: deploy_production
  name: "Deploy to Production"
  requires_approval: true

# Data deletion
- id: delete_old_records
  name: "Delete Old Records"
  requires_approval: true

# Expensive API calls
- id: run_batch_analysis
  name: "Run Batch Analysis"
  description: "Cost: $50-100 depending on data size"
  requires_approval: true

# Content publication
- id: publish_article
  name: "Publish Article to Website"
  requires_approval: true
```

**Skipping Tasks:**

When a task is skipped (approval denied):
- Task status set to SKIPPED
- Task outputs are NOT created (variables remain undefined)
- Dependent tasks that require skipped task's outputs will fail with "Missing variable" error
- Workflow continues with independent tasks (if any)

---

## Related Pages

- [YAML Schema Reference](/docs/workflows/yaml-reference/) — Complete field documentation
- [Example Workflows](/docs/workflows/examples/) — Annotated real-world workflow definitions
- [Workflow Commands](/docs/cli/workflows/) — CLI commands for running workflows
