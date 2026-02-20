# Phase 4 Build Plan Examples: Developer Workflow Guide

**Status:** Proposed for Approval  
**Date:** 2026-02-20  
**Companion To:** `docs/design/agents/Phase-4/phase-4-build-plan.md`

---

## 1. Purpose

This guide provides developer-facing examples for building against the Phase 4 runtime model:

1. Single-agent workflow.
2. Multi-agent workflow with one or more pipelines.
3. Runtime binding, agent binding, and task ownership binding.
4. Legacy workflow compatibility adapter posture.

This is a design and implementation guide, not a production reference implementation.

---

## 2. Canonical Model Summary

Use this hierarchy for all new designs:

1. Runtime configuration defines execution environment and service pool.
2. Agent profiles bind to runtime services, including `llm_service`.
3. Workflows reference one or more pipelines.
4. Pipelines contain one or more tasks.
5. Tasks bind to concrete owners by `owner_agent_id` or `owner_role`.

---

## 3. Runtime Binding Example (YAML-First)

Example runtime config (conceptual):

```yaml
config_policy:
  allow_env_override: false
  strict_agent_llm_binding: true

runtime_paths:
  install_root: /opt/friday
  runtime_data_root: /var/lib/friday/runtime
  workspace_root: /workspace

memory:
  mode: single_agent

scratch:
  backend: sqlite
  path: scratch/scratch.db

llm_pool:
  default_service: general_openai
  services:
    general_openai:
      provider: openai
      model: gpt-4o
      api_key: ${OPENAI_API_KEY}
      resilience:
        timeout_seconds: 60
        max_retries: 2
    fast_openai:
      provider: openai
      model: gpt-4o-mini
      api_key: ${OPENAI_API_KEY}
      resilience:
        timeout_seconds: 30
        max_retries: 2

embedding:
  model: text-embedding-3-small
```

Binding notes:

1. Runtime is the source of truth for service identities.
2. `llm_pool.services` keys are stable service names used by agents.
3. Strict mode requires every agent to reference one of these services.

---

## 4. Single-Agent Workflow Example

## 4.1 Agent Profile Example

```yaml
name: analyst
role: Data Analyst
goal: Produce a concise analysis from provided input data
system_prompt: |
  You are an analyst focused on traceable, verifiable outputs.
llm_service: general_openai
tools:
  - read_file
  - write_file
skills:
  - analysis_core@1.0.0
```

## 4.2 Workflow/Pipeline/Task Example

```yaml
workflow:
  workflow_id: wf_single_analysis
  version: 1.0.0
  name: Single Agent Analysis
  goal: Build one analysis artifact
  pipeline_refs:
    - pl_analysis

pipelines:
  - pipeline_id: pl_analysis
    version: 1.0.0
    workflow_id: wf_single_analysis
    goal: Analyze and summarize
    tasks:
      - task_id: gather_input
        name: Gather Input
        description: Read source files and normalize inputs.
        owner_agent_id: analyst
        input_contract:
          source_paths: list[str]
        output_contract:
          normalized_data: json
      - task_id: write_summary
        name: Write Summary
        description: Create concise summary output.
        owner_agent_id: analyst
        dependencies:
          - gather_input
        input_contract:
          normalized_data: json
        output_contract:
          summary_artifact: markdown
```

## 4.3 Binding Walkthrough

1. Runtime loads config and validates `llm_pool`.
2. Agent loader validates profile and `llm_service=general_openai`.
3. Workflow loader validates one workflow, one pipeline, two tasks.
4. Dispatch engine creates assignments for both tasks to `analyst`.
5. Task claims/starts/completes with deterministic state transitions.

---

## 5. Multi-Agent Multi-Pipeline Example

## 5.1 Runtime Changes for Multi-Agent

```yaml
memory:
  mode: multi_agent

llm_pool:
  default_service: fast_openai
  services:
    fast_openai:
      provider: openai
      model: gpt-4o-mini
      api_key: ${OPENAI_API_KEY}
      resilience:
        timeout_seconds: 30
        max_retries: 3
    reasoning_openai:
      provider: openai
      model: o3
      api_key: ${OPENAI_API_KEY}
      resilience:
        timeout_seconds: 90
        max_retries: 2
```

## 5.2 Agent Profiles

```yaml
# researcher.yaml
name: researcher
role: Research Specialist
goal: Build evidence set from trusted sources
system_prompt: You gather evidence and cite sources.
llm_service: fast_openai
skills:
  - research_foundation@1.2.0

# synthesizer.yaml
name: synthesizer
role: Synthesis Specialist
goal: Synthesize evidence into recommendations
system_prompt: You produce coherent synthesis from evidence.
llm_service: reasoning_openai
skills:
  - synthesis_core@1.0.0
```

## 5.3 Workflow/Pipeline/Task Example

```yaml
workflow:
  workflow_id: wf_research_synthesis
  version: 1.0.0
  name: Research To Synthesis
  goal: Produce final recommendation package
  pipeline_refs:
    - pl_research
    - pl_synthesis

pipelines:
  - pipeline_id: pl_research
    version: 1.0.0
    workflow_id: wf_research_synthesis
    goal: Gather evidence
    output_contract:
      evidence_bundle: json
    tasks:
      - task_id: collect_sources
        name: Collect Sources
        description: Collect and rank source material.
        owner_agent_id: researcher
        output_contract:
          evidence_bundle: json

  - pipeline_id: pl_synthesis
    version: 1.0.0
    workflow_id: wf_research_synthesis
    goal: Build final recommendations
    upstream_pipeline_ids:
      - pl_research
    input_contract:
      evidence_bundle: json
    output_contract:
      recommendation_report: markdown
    tasks:
      - task_id: produce_recommendations
        name: Produce Recommendations
        description: Produce final recommendations from evidence bundle.
        owner_role: synthesis
        input_contract:
          evidence_bundle: json
        output_contract:
          recommendation_report: markdown
```

## 5.4 Binding Walkthrough

1. Runtime validates multi-agent mode and `llm_pool` services.
2. Agent loader validates `researcher` and `synthesizer` profiles against pool.
3. Owner resolution maps `owner_role: synthesis` to concrete agent.
4. Typed handoff validates `evidence_bundle: json` from `pl_research` to `pl_synthesis`.
5. Dispatch engine tracks assignment, claim, lease, and lineage records.

---

## 6. Legacy Workflow Compatibility Example

Use legacy task-graph definitions only for transitional support:

1. Load legacy `WorkflowDefinition`.
2. Transform through compatibility adapter to canonical pipeline structure.
3. Execute under pipeline dispatch model.
4. Emit compatibility warning and migration metadata.

Migration target:

1. Convert legacy definitions into native workflow/pipeline/task definitions.
2. Remove dependency on adapter before deprecation milestones.

---

## 7. Coverage Checklist for Review

Use this checklist to validate Phase 4 completeness:

1. Runtime config has `llm_pool`, `config_policy`, paths, memory, scratch.
2. Every agent defines valid `llm_service` under strict mode.
3. Every workflow references one or more valid pipelines.
4. Every pipeline has one or more valid tasks.
5. Every task has one ownership selector (`owner_agent_id` or `owner_role`).
6. Role-based ownership resolution is deterministic and auditable.
7. Typed handoff contracts match across pipeline boundaries.
8. Dispatch lifecycle behavior is explicitly testable.
9. Legacy adapter behavior is documented and warnings are expected.
10. Observability data includes workflow/pipeline/task/assignment and LLM binding metadata.
11. Acceptance criteria from Phase 4 plan can be mapped to specific tests and outputs.

---

## 8. Common Failure Conditions

1. Agent profile references missing `llm_service`.
2. Strict mode enabled and `llm_service` omitted.
3. Workflow references unknown pipeline.
4. Pipeline has invalid task dependency graph.
5. Role owner cannot be resolved to a single valid agent.
6. Typed handoff mismatch between pipeline output/input contracts.

Treat all above as fail-fast design-time or startup-time errors where possible.
