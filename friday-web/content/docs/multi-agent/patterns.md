---
title: "Collaboration Patterns"
description: "Fan-out, pipeline, consensus, and other multi-agent interaction patterns."
weight: 3
---

Friday supports fan-out, pipeline, consensus voting, and critic-revisor collaboration patterns for building reliable multi-agent systems.

## Pipeline Pattern

The pipeline pattern chains agents in sequence, where each agent's output becomes the next agent's input. This is the most common multi-agent pattern and the foundation of Friday's workflow system.

**Structure:**

```
User Input
    │
    ▼
┌───────────┐
│ Researcher│  (gather information)
└─────┬─────┘
      │ $research_results
      ▼
┌───────────┐
│  Analyst  │  (synthesize findings)
└─────┬─────┘
      │ $analysis
      ▼
┌───────────┐
│  Writer   │  (generate report)
└─────┬─────┘
      │ $final_report
      ▼
Final Output
```

**Implementation — Direct Delegation:**

```python
# Sequential pipeline via delegation
orchestrator = AgentOrchestrator(registry, memory_controller)

async def run_pipeline(topic: str) -> str:
    # Stage 1: Research
    research = await orchestrator.delegate(
        "researcher",
        f"Research the following topic: {topic}",
        return_to_current=False,
    )

    # Stage 2: Analysis
    analysis = await orchestrator.delegate(
        "analyst",
        f"Analyze these research findings:\n\n{research}",
        return_to_current=False,
    )

    # Stage 3: Writing
    report = await orchestrator.delegate(
        "writer",
        f"Write a report based on this analysis:\n\n{analysis}",
        return_to_current=False,
    )

    return report
```

**Implementation — Workflow YAML:**

```yaml
id: research_pipeline
name: "Research Pipeline"
description: "Research, analyze, and report on a topic"

tasks:
  - id: research
    name: "Research Topic"
    agent: researcher
    inputs:
      topic: "$user_topic"
    outputs:
      - research_results

  - id: analyze
    name: "Analyze Findings"
    agent: analyst
    depends_on: [research]
    inputs:
      findings: "$research_results"
    outputs:
      - analysis_summary

  - id: write_report
    name: "Write Report"
    agent: writer
    depends_on: [analyze]
    inputs:
      analysis: "$analysis_summary"
    outputs:
      - final_report
```

**Use Cases:**
- Content creation (research → draft → edit → publish)
- Software development (spec → implement → test → review)
- Data analysis (gather → clean → analyze → visualize)
- Document processing (extract → transform → validate → store)

---

## Fan-Out Pattern

The fan-out pattern distributes work to multiple specialist agents in parallel (or sequentially with the current MVP), then aggregates their results.

**Structure:**

```
                  ┌─────────────┐
                  │   Router    │
                  └──────┬──────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
   ┌────────────┐ ┌────────────┐ ┌────────────┐
   │ Researcher │ │  Analyst   │ │  Reviewer  │
   └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
                  ┌─────────────┐
                  │ Aggregator  │
                  └─────────────┘
```

**Current Implementation (Sequential Fan-Out):**

```python
async def fan_out_research(topic: str) -> str:
    results = {}

    # Dispatch to multiple specialists (currently sequential)
    results["web"] = await orchestrator.delegate(
        "web_researcher",
        f"Search the web for: {topic}",
        return_to_current=True,
    )

    results["academic"] = await orchestrator.delegate(
        "academic_researcher",
        f"Search academic databases for: {topic}",
        return_to_current=True,
    )

    results["internal"] = await orchestrator.delegate(
        "knowledge_researcher",
        f"Search internal knowledge base for: {topic}",
        return_to_current=True,
    )

    # Aggregate with synthesis agent
    synthesis = await orchestrator.delegate(
        "synthesizer",
        f"""Synthesize these research results:

Web Sources: {results['web']}

Academic Sources: {results['academic']}

Internal Knowledge: {results['internal']}""",
        return_to_current=True,
    )

    return synthesis
```

**Future Implementation (Parallel Fan-Out):**

When parallel execution is added to the workflow engine, independent tasks will run concurrently:

```yaml
tasks:
  - id: web_research
    agent: web_researcher
    inputs:
      topic: "$user_topic"
    # No depends_on — can run in parallel

  - id: academic_research
    agent: academic_researcher
    inputs:
      topic: "$user_topic"
    # No depends_on — can run in parallel

  - id: synthesize
    agent: synthesizer
    depends_on:
      - web_research
      - academic_research
    inputs:
      web_results: "$web_sources"
      academic_results: "$academic_sources"
    # Waits for both to complete
```

**Use Cases:**
- Multi-source research gathering
- Parallel validation (multiple reviewers checking the same code)
- A/B content generation (multiple writers, best chosen)
- Distributed data processing

---

## Consensus Pattern

The consensus pattern asks multiple agents independently to answer the same question, then uses a judge agent to determine the best answer or synthesize a consensus.

**Structure:**

```
Question
    │
    ├────────────────────────────────┐
    ▼                    ▼           ▼
┌────────┐         ┌────────┐  ┌────────┐
│Agent A │         │Agent B │  │Agent C │
│(Answer)│         │(Answer)│  │(Answer)│
└───┬────┘         └───┬────┘  └───┬────┘
    │                  │           │
    └──────────────────┼───────────┘
                       ▼
               ┌──────────────┐
               │ Judge Agent  │
               │ (Consensus)  │
               └──────────────┘
```

**Implementation:**

```python
async def consensus_answer(question: str, num_agents: int = 3) -> str:
    """Get consensus answer from multiple agents."""
    agent_names = ["analyst_1", "analyst_2", "analyst_3"][:num_agents]
    answers = []

    # Collect independent answers
    for agent_name in agent_names:
        answer = await orchestrator.delegate(
            agent_name,
            question,
            return_to_current=True,
        )
        answers.append(f"**{agent_name}**: {answer}")

    # Judge synthesizes consensus
    consensus = await orchestrator.delegate(
        "judge",
        f"""You have received {num_agents} independent answers to this question:

Question: {question}

Independent Answers:
{chr(10).join(answers)}

Synthesize the most accurate consensus answer, noting areas of agreement and disagreement.""",
        return_to_current=True,
    )

    return consensus
```

**Voting Variant:**

Instead of synthesis, use majority voting:

```python
async def voting_decision(question: str) -> str:
    """Use majority vote to make a decision."""
    votes = {}

    for agent_name in ["voter_1", "voter_2", "voter_3", "voter_4", "voter_5"]:
        vote = await orchestrator.delegate(
            agent_name,
            f"Answer with only YES or NO: {question}",
            return_to_current=True,
        )
        vote = vote.strip().upper()
        votes[vote] = votes.get(vote, 0) + 1

    # Majority vote
    decision = max(votes, key=votes.get)
    confidence = votes[decision] / sum(votes.values())

    return f"Decision: {decision} (confidence: {confidence:.0%}, votes: {votes})"
```

**Use Cases:**
- High-stakes decisions requiring validation
- Fact verification (multiple sources must agree)
- Code review (multiple reviewers must approve)
- Risk assessment (independent risk analysts)

---

## Critic-Revisor Pattern

The critic-revisor pattern uses one agent to create work and another to critique it, iterating until quality meets a threshold.

**Structure:**

```
User Request
    │
    ▼
┌─────────┐
│ Creator │ ──── Creates first draft
└────┬────┘
     │
     ▼
┌─────────┐
│  Critic │ ──── Reviews and identifies issues
└────┬────┘
     │
     ├── Issues found? ──── YES ──→ (back to Creator)
     │
     └── Issues found? ──── NO ──→ Final Output
```

**Implementation:**

```python
async def critic_revisor_workflow(
    task: str,
    max_iterations: int = 3,
) -> str:
    """Iterative improvement through critic-revisor pattern."""
    iteration = 0
    current_work = None

    while iteration < max_iterations:
        iteration += 1

        # Creator produces or revises work
        if current_work is None:
            prompt = f"Create: {task}"
        else:
            prompt = f"Revise your previous work based on this feedback:\n\n{feedback}\n\nOriginal work:\n\n{current_work}"

        current_work = await orchestrator.delegate(
            "creator",
            prompt,
            return_to_current=True,
        )

        # Critic reviews the work
        critique = await orchestrator.delegate(
            "critic",
            f"""Review this work critically. List specific issues that need fixing.
If the work is acceptable, respond with APPROVED.

Work to review:
{current_work}""",
            return_to_current=True,
        )

        # Check if approved
        if "APPROVED" in critique.upper():
            return current_work

        # Store feedback for next iteration
        feedback = critique

    # Return best version after max iterations
    return current_work
```

**Quality Threshold Variant:**

```python
async def quality_assured_output(task: str) -> str:
    """Generate output that meets a quality threshold."""
    best_score = 0.0
    best_output = None

    for attempt in range(3):
        # Generate output
        output = await orchestrator.delegate("creator", task, return_to_current=True)

        # Score quality
        score_response = await orchestrator.delegate(
            "quality_scorer",
            f"""Rate this output on a scale from 0.0 to 1.0.
Respond with only a number (e.g., 0.85).

Output to rate:
{output}""",
            return_to_current=True,
        )

        try:
            score = float(score_response.strip())
        except ValueError:
            score = 0.5

        if score > best_score:
            best_score = score
            best_output = output

        if score >= 0.9:  # Quality threshold met
            break

    return best_output
```

**Use Cases:**
- Code generation with code review
- Content creation with editorial review
- Report writing with fact-checking
- Translation with quality verification

---

## Router Pattern

The router pattern uses a classifier agent to analyze the user's request and dispatch it to the most appropriate specialist agent.

**Implementation:**

```python
async def smart_router(user_request: str) -> str:
    """Route requests to appropriate specialist agents."""

    # Classifier determines the right agent
    classification = await orchestrator.delegate(
        "classifier",
        f"""Classify this request and respond with exactly one of:
RESEARCH, CODE, ANALYSIS, WRITING, DATA, GENERAL

Request: {user_request}""",
        return_to_current=True,
    )

    # Route to appropriate specialist
    routing_map = {
        "RESEARCH": "researcher",
        "CODE": "coder",
        "ANALYSIS": "analyst",
        "WRITING": "writer",
        "DATA": "data_analyst",
        "GENERAL": "assistant",
    }

    specialist = routing_map.get(classification.strip(), "assistant")

    return await orchestrator.delegate(
        specialist,
        user_request,
        return_to_current=False,
    )
```

**YAML-Based Routing:**

```yaml
# In agent YAML — classifier agent
name: classifier
role: "Request Classifier"
goal: "Route user requests to the appropriate specialist agent"
system_prompt: |
  You are a request classifier. Analyze user requests and output
  exactly one routing keyword: RESEARCH, CODE, ANALYSIS, WRITING,
  DATA, or GENERAL.

  Base your classification on:
  - RESEARCH: finding information, web searches, literature review
  - CODE: writing, debugging, or reviewing code
  - ANALYSIS: data analysis, trend identification, interpretation
  - WRITING: drafting documents, editing, summarizing text
  - DATA: working with structured data, CSV, databases
  - GENERAL: everything else
tools: []  # Classifier needs no tools
temperature: 0.0  # Deterministic classification
```

**Use Cases:**
- Customer support routing (billing, technical, general)
- Content moderation with specialist reviewers
- Multi-domain knowledge bases
- Tiered support (simple → complex escalation)

---

## Pattern Selection Guide

| Pattern | Best For | Agents Needed | Complexity |
|---------|----------|---------------|------------|
| **Pipeline** | Sequential processing steps | 3-6 ordered agents | Low |
| **Fan-Out** | Parallel independent tasks | 3-5 parallel + 1 aggregator | Medium |
| **Consensus** | High-stakes decisions | 3-5 validators + 1 judge | Medium |
| **Critic-Revisor** | Iterative quality improvement | 1 creator + 1 critic | Low |
| **Router** | Diverse request types | 1 classifier + N specialists | Medium |

**Combining Patterns:**

Patterns can be combined for sophisticated workflows:

```python
# Router → Pipeline → Critic-Revisor
user_request = "Write and review a technical blog post about async Python"

# 1. Router classifies as WRITING
# 2. Pipeline: research → outline → draft
# 3. Critic-Revisor: writer ↔ editor until approved
```

```yaml
id: full_content_pipeline
tasks:
  - id: classify
    agent: classifier
    inputs:
      request: "$user_request"
    outputs: [request_type]

  - id: research
    agent: researcher
    depends_on: [classify]
    inputs:
      topic: "$user_request"
    outputs: [research_results]

  - id: draft
    agent: writer
    depends_on: [research]
    inputs:
      research: "$research_results"
      request: "$user_request"
    outputs: [draft_content]

  - id: edit_review
    agent: editor
    depends_on: [draft]
    inputs:
      draft: "$draft_content"
    outputs: [final_content]
    requires_approval: true
```

---

## Related Pages

- [Shared Memory Architecture](/docs/multi-agent/architecture/) — How agents share context and provenance
- [Orchestrator Patterns](/docs/multi-agent/orchestrator/) — Routing, delegation, and agent switching
- [Workflow Engine](/docs/workflows/engine/) — Declarative multi-agent workflows with YAML
