# Experiments

This directory contains runnable framework experiments and smoke-test harnesses.

## Purpose

Experiments are isolated execution harnesses used to validate framework behavior
without turning every probe into product surface area.

Experiments are intended for:

- framework smoke tests
- package-quality checks
- controlled runtime probes
- deterministic and provider-backed validation scenarios

## Rules

- Experiments may import from `packages/*`.
- Product packages must not import from `experiments/`.
- Experiments should be isolated from user-local state by default.
- Experiments that become stable quality signals should include automated tests.
- Experiment-local agents belong under that experiment's `agents/` directory.
- Agent-generated files belong under that experiment's `artifacts/` directory.

## Canonical Structure

Each experiment should follow this structure unless there is a strong reason not
to:

```text
experiments/
  <experiment_name>/
    README.md
    run.py
    runtime.py
    schema.py
    config/
      runtime.yaml
    agents/
    workflows/
    fixtures/
    artifacts/
    tests/
```

`schema.py` is optional for very small experiments, but it should be added once
the experiment has a stable structured result contract or artifact manifest.
`config/runtime.yaml` is required for experiments that boot `RuntimeKernel`.
Provider-backed experiments may also use an untracked
`config/runtime.local.yaml` overlay for API keys and machine-local endpoint
overrides.

## Runtime Configuration

Experiments that use the Friday runtime must declare their primary runtime
contract in `config/runtime.yaml`.

Provider-backed experiments should keep secrets out of versioned source by
loading an untracked `config/runtime.local.yaml` overlay on top of the checked-in
`config/runtime.yaml`.

Use `runtime.py` only to:

- load and validate the runtime YAML
- inject ephemeral filesystem roots
- apply deterministic test-double overrides
- handle execution orchestration and teardown

Do not embed the primary runtime configuration contract directly in code.

## Subfolder Semantics

### `agents/`

Canonical home for experiment-specific agent definitions.

Use this directory for:

- YAML agent profiles
- experiment-only agent role definitions
- fixed probe agents such as `quality_probe.yaml`

Do not place product agent definitions here.

### `fixtures/`

Canonical home for static experiment inputs.

Use this directory for:

- prompts
- expected responses
- sample source documents
- sample configs
- deterministic input data

### `artifacts/`

Canonical home for generated experiment outputs created by agent execution.

Use this directory for:

- reports
- markdown outputs
- JSON outputs
- generated files
- artifact manifests
- lineage outputs

Artifacts should be treated as execution outputs, not as source fixtures.

### `tests/`

Canonical home for automated verification of the experiment.

Tests should validate:

- direct runtime/helper execution
- command-line execution where applicable
- result schema expectations
- artifact behavior where applicable

## File Roles

### `README.md`

Documents the purpose, scope, run instructions, expected outputs, and known
limitations for one experiment.

### `run.py`

Provides the human-runnable entrypoint for the experiment.

### `runtime.py`

Owns orchestration logic for:

- runtime config loading
- dependency injection
- execution
- teardown
- artifact placement

### `config/runtime.yaml`

Canonical home for the experiment's declarative runtime contract.

Use this file for:

- llm pool names and service definitions
- embedding model settings
- memory mode
- telemetry defaults
- agents directory
- artifact policy
- workflow mode and other runtime policy settings

### `config/runtime.local.yaml`

Optional untracked local overlay for provider-backed experiments.

Use this file for:

- API keys
- machine-local endpoint overrides
- local-only service tweaks that should not be committed

### `schema.py`

Defines typed experiment contracts when needed, such as:

- run result objects
- artifact records
- artifact manifests
- structured response expectations

## Naming Guidance

Name experiment directories by the quality dimension or framework behavior being
validated.

Good examples:

- `agent_quality`
- `workflow_quality`
- `telemetry_quality`
- `provider_smoke`

Less useful examples:

- `test1`
- `demo_runner`
- `phase4_thing`

## Current Experiments

- `agent_quality`: Phase 4 direct-agent smoke test
- `prompt_transcript_audit`: deterministic Phase 5-A prompt layering and transcript audit
- `provider_memory_smoke`: provider-backed direct turn plus archive-extraction smoke test
- `workflow_artifact_smoke`: provider-backed canonical two-agent workflow with artifact, transcript, and memory persistence
