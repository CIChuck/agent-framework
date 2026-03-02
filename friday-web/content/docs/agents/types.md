---
title: "Agent Types"
description: "CopilotAgent, orchestrators, and specialized agent roles."
weight: 1
---

Friday provides `CopilotAgent` as the general-purpose reasoning agent and supports orchestrator and specialist roles for multi-agent deployments.

Agents are the active intelligence layer of Friday—the entities that combine memory, reasoning, and tools to accomplish tasks. While the memory system provides context and tools enable action, agents orchestrate the interaction between these components to achieve goals.

## CopilotAgent: Interactive Re-Act Pattern

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

---

## AutonomousAgent: Event-Driven Execution (Planned)

**Status:** Placeholder implementation; full development planned for a future release.

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

**Planned Use Cases:**

| Use Case | Why AutonomousAgent | Safety Considerations |
|----------|---------------------|----------------------|
| Scheduled Reports | Run weekly without human trigger | Read-only tools, sandboxed data access |
| Data Pipeline Monitoring | Autonomous alert/fix workflows | Approval gate for data modifications |
| Competitive Intelligence | Daily competitor monitoring | Rate limits, robots.txt compliance |
| Code Refactoring | Large-scale codebase improvements | Git branch isolation, test requirement |
| Document Processing | Batch processing uploaded files | File size limits, malware scanning |

---

## Comparison: When to Use Which Agent

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
| **Production Status** | Stable | Planned |

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

## Specialized Agent Roles

Beyond the base agent types, Friday supports specialized roles configured through YAML profiles. Common roles include:

**Researcher**: Web search, document retrieval, information synthesis. Uses `web_search`, `scrape_page`, and `recall_memory` tools. High temperature (0.7) for exploratory reasoning.

**Coder**: Code writing, execution, and review. Uses `file_read`, `file_write`, `python_execute`, and `code_analyze` tools. Low temperature (0.2) for deterministic output.

**Reviewer**: Code review, quality checking, and validation. Uses read-only tools (`file_read`, `code_analyze`, `git_diff`) with no write access.

**Analyst**: Data analysis, pattern recognition, and reporting. Uses `csv_read`, `json_parse`, `python_execute`, and `file_write` for report generation.

**Orchestrator**: Meta-agent that coordinates other agents via delegation. Routes tasks based on content and manages agent switching.

Each role is defined entirely through YAML configuration—see [Agent Configuration](/docs/agents/configuration/) for the full schema.

---

## Related Pages

- [Agent Configuration](/docs/agents/configuration/) — YAML schemas and AgentProfile fields
- [Lifecycle & State](/docs/agents/lifecycle/) — Session initialization, Re-Act loop, and turn archiving
- [Multi-Agent Architecture](/docs/multi-agent/architecture/) — How agents share memory
