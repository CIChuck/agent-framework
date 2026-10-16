---
title: Workflows and task graphs
description: Canonical workflow bundles, flat compatibility workflows, dependencies, approval and execution state.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Workflows and task graphs

Friday has two workflow schemas: a retained flat task graph and a canonical
workflow → pipeline → task hierarchy. Choose the loader and execution method
that match your files. A YAML graph describes work; it does not create agents,
provision providers or authorize external mutations.

## Choose the correct surface

| Definition | Loader | Executor |
| --- | --- | --- |
| Flat file `workflows/name.yaml` | `WorkflowLoader.load(name)` | `await WorkflowEngine.execute(definition, inputs)` |
| Canonical directory bundle | `WorkflowLoader.load_canonical(name)` | `await WorkflowEngine.execute_canonical(workflow, pipelines, inputs, role_bindings=...)` |
| Flat-to-canonical adaptation | `load_legacy_as_canonical(name)` | Canonical executor after adaptation and validation |

The headless Runtime's `config_policy.workflow_mode` defaults to `canonical`;
explicit `legacy`/`auto` options are separate compatibility choices. Friday
Chat's command adapter executes **flat** definitions in real mode. It can
describe a canonical bundle in its listing, but its run path calls `load()`;
do not treat a listed canonical name as runnable through `/workflow run`.

Chat's real workflow engine still delegates through its deterministic
`FakeOrchestrator`. Its workflow state/approval behavior does not prove real
specialist-model work ran. For real agents, assemble the framework executor
with your configured `AgentOrchestrator`. See [multi-agent operation](07-multi-agent.md).

## Canonical bundle layout

```text
workflows/
  research/
    workflow.yaml
    pipelines/
      collect.yaml
      review.yaml
```

These three files form a **complete loadable canonical definition**, with no
runtime services or external effects. Save `workflows/research/workflow.yaml`:

```yaml
workflow_id: research
version: 1.0.0
name: Research and review
goal: Produce a draft and a separate review.
pipeline_refs: [collect, review]
entry_pipeline_id: collect
completion_criteria:
  - A draft and review result are available.
```

Save `workflows/research/pipelines/collect.yaml`:

```yaml
pipeline_id: collect
version: 1.0.0
workflow_id: research
goal: Produce a source-grounded draft.
input_contract:
  topic: text
output_contract:
  draft: text
entrypoints: [research_topic]
exit_conditions: [Draft produced]
tasks:
  - task_id: research_topic
    name: Research topic
    description: Draft notes from the explicitly supplied sources.
    owner_agent_id: researcher
    input_contract:
      topic: text
    output_contract:
      draft: text
    completion_criteria: [Preserve source references]
```

Save `workflows/research/pipelines/review.yaml`:

```yaml
pipeline_id: review
version: 1.0.0
workflow_id: research
goal: Review the draft against its sources.
upstream_pipeline_ids: [collect]
input_contract:
  draft: text
output_contract:
  review_notes: text
entrypoints: [review_draft]
exit_conditions: [Review notes produced]
tasks:
  - task_id: review_draft
    name: Review draft
    description: Identify unsupported claims and missing source evidence.
    owner_agent_id: reviewer
    input_contract:
      draft: text
    output_contract:
      review_notes: text
    completion_criteria: [List findings with evidence]
```

Run this **offline Python example** after saving those files:

```python
from friday_agent.workflows import WorkflowLoader

bundle = WorkflowLoader("workflows").load_canonical("research")
order = bundle.workflow.get_pipeline_order(bundle.pipelines)
print(order)
for name in order:
    print(name, bundle.pipelines[name].validate_graph())
```

Expected order: `['collect', 'review']`; each graph reports `[]` validation errors.
Loading validates hierarchy and references, not agent availability, source
quality or external permissions. `researcher` and `reviewer` must be registered
with functional factories before executing this bundle.

## Canonical contracts

`WorkflowPipelineDefinition` names pipeline IDs, entry pipeline, completion
criteria, required artifacts and optional timeout. Each `PipelineDefinition`
names its workflow, tasks, upstream pipelines, inputs/outputs and artifact policy.

`TaskDefinition` requires identity, name, description and an owner selector:
`owner_agent_id` or `owner_role`. Role owners resolve through supplied
`role_bindings`; unresolved owners fail dispatch. Optional fields include
required skills, dependency IDs, input bindings, output artifact declarations,
retry policy, HITL policy reference and completion criteria.

Type labels in `input_contract`/`output_contract` are named contracts used for
handoff/reference checks. They do not by themselves validate arbitrary model
text as a business-domain object. Validate the generated artifact's content in
the application or a separate checker before accepting it.

Cross-pipeline artifacts have producer/consumer identity and lifecycle rules.
`register_artifact` and `transition_artifact` expose draft/validated/final/archived
state transitions under artifact policy. A declared completion criterion is
not automatically a semantic evaluator for a report.

## Flat compatibility workflow

Save this **complete flat definition** as `workflows/draft_review.yaml`:

```yaml
id: draft_review
name: Draft and review
description: Produce notes, then request approval before review.
timeout_seconds: 120
tasks:
  - id: draft
    name: Draft notes
    description: Draft concise notes for the topic.
    agent: researcher
    inputs:
      topic: $topic
    outputs: [draft_notes]
    max_retries: 0
  - id: review
    name: Review notes
    description: Review the supplied draft.
    agent: coder
    depends_on: [draft]
    inputs:
      draft: $draft_notes
    outputs: [review_notes]
    requires_approval: true
    max_retries: 0
```

The owner names match Chat's current deterministic adapter for a local control-flow
demonstration. They do not create real researcher/coder model agents.

Flat `inputs` values beginning with `$` refer to an entire variable name;
other strings are literals. There is no general shell interpolation, expression
engine or implicit `$object.field` traversal. Missing variables fail resolution.
Outputs are populated from task results; multiple names are not proof that a
free-text response contains separately validated fields.

This **offline Python example** validates the flat graph only:

```python
from friday_agent.workflows import WorkflowLoader

workflow = WorkflowLoader("workflows").load("draft_review")
print(workflow.get_task_order())
print(workflow.validate_graph())
```

Expected output: `['draft', 'review']` and `[]`.

## Execution, approval and failure

`WorkflowEngine` receives an already configured orchestrator. Definitions and
mutable execution state are separate: task status/result/error/timing live in
execution objects. Dependencies impose order; a DAG does not imply parallel
agent execution. The current executor iterates dependency-ready work.

Flat `requires_approval: true` gates the task **before** execution. With no
approval callback, execution pauses with `pending_approval` and a waiting task.
The caller can use `approve_task`, `reject_task`, `skip_task` or the typed HITL
decision path. Typed HITL policy adds authority/deadline/default-action rules;
the host must arrange identity and timeout processing.

Keep “waiting for approval,” “task completed,” “artifact validated” and “human
accepted” distinct. Skipping a task can affect dependents and output availability.
Timeout/cancellation does not reverse an external side effect. Do not configure
automatic retries for non-idempotent work without a reconciliation design.

`PipelineDispatchEngine` exposes assignment, claim, heartbeat, lease recovery,
typed handoff and finalization operations. Those are in-process state contracts,
not a durable distributed queue or exactly-once job runner. Persist/coordinate
state explicitly if your application spans workers or restarts.

## Chat commands

With the flat file above in the configured workflows directory:

```text
/workflow list
/workflow run draft_review topic=synthetic-demo
/workflow status
/workflow approve review
```

These commands exercise the current adapter's control flow. `/workflow skip`
resolves a pending task by skipping it. See `/help workflow`. Chat resolves its
directory from `chat.workflows_dir` (compatibility alias `workflow_directory`),
then `FRIDAY_WORKFLOWS_DIR`, then `./workflows`; relative values use process cwd.
Headless Runtime uses its separate `workflows.dir` configuration.

## Implementation references

- [Models and validators](../../packages/friday-agent/src/friday_agent/workflows/models.py)
- [Loader and flat adaptation](../../packages/friday-agent/src/friday_agent/workflows/loader.py)
- [Execution, HITL and dispatch](../../packages/friday-agent/src/friday_agent/workflows/engine.py)
- [Chat adapter](../../packages/friday-chat/src/friday_chat/adapters.py)

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
