---
title: "YAML Schema Reference"
description: "Complete reference for all workflow schema fields, step types, and conditions."
weight: 2
---

Complete reference for every field in a Friday workflow YAML definition, including step types, input/output bindings, conditions, and retry configuration.

## Root Workflow Schema

Friday workflows are defined in YAML files using a structured schema.

**Required and Optional Fields:**

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

---

## TaskNode Schema

**Required and Optional Fields:**

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

---

## Complete Annotated Example

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

---

## Field Validation Rules

**1. `id` (workflow and task):**
- Must be unique within scope (workflow IDs globally, task IDs within workflow)
- Alphanumeric characters, underscores, hyphens only
- Case-insensitive (normalized to lowercase)

**2. `depends_on`:**
- All referenced task IDs must exist in the workflow
- Cannot create cycles (A → B → C → A)
- Tasks can depend on multiple tasks (fan-in pattern)

**3. `inputs`:**
- Keys are parameter names passed to the agent
- Values starting with `$` are variable references (must exist at runtime)
- Values without `$` are literal values

**4. `outputs`:**
- Array of variable names to create/update
- Variables are created after task completes successfully
- Multiple tasks can write to the same variable (last writer wins)

**5. `timeout_seconds`:**
- Must be positive integer
- Task-level timeout overrides workflow-level timeout
- If exceeded, task fails (can retry if `max_retries > 0`)

**6. `max_retries`:**
- Must be non-negative integer
- Task-level retries override workflow-level default

---

## Retry Strategies

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

**Future Enhancement — Exponential Backoff:**

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

---

## Timeout Enforcement

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

---

## Conditional Execution (Future Enhancement)

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

---

## Error Handling Modes

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

---

## Validation Errors

The `WorkflowLoader` validates all fields at load time, rejecting invalid workflows before execution:

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

---

## Related Pages

- [Workflow Engine](/docs/workflows/engine/) — How Friday parses, validates, and executes YAML workflow definitions
- [Example Workflows](/docs/workflows/examples/) — Annotated real-world workflow definitions
- [Workflow Commands](/docs/cli/workflows/) — CLI commands for running and managing workflows
