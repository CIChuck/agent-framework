# Workflow Artifact Smoke

Live, non-deterministic Phase 5-C experiment for the Friday Agent Framework.

This experiment validates a self-contained canonical workflow with:

1. two agents (`researcher` and `writer`)
2. runtime-loaded `friday_tools` (`web_search`, `web_reader`, `file_write`)
3. provider-backed inference
4. a typed cross-pipeline handoff artifact (`selected_article`)
5. a physical markdown output file written by the writer
6. a workflow-published artifact record for that output
7. persistent transcript and memory state under this experiment folder

## Run

From the repo root:

```bash
uv run python experiments/workflow_artifact_smoke/run.py
uv run python experiments/workflow_artifact_smoke/run.py --json
```

This experiment requires:

1. [runtime.local.yaml.example](/Users/chuckrussell/Dev/gendev/agent-framework/experiments/workflow_artifact_smoke/config/runtime.local.yaml.example) copied to `runtime.local.yaml`
2. valid provider credentials for the configured LLM and embedding services

## Outputs

Persistent outputs are written here:

1. markdown report:
   `experiments/workflow_artifact_smoke/outputs/summary_report.md`
2. experiment result summary:
   `experiments/workflow_artifact_smoke/artifacts/`
3. transcript database:
   `experiments/workflow_artifact_smoke/runtime_data/transcripts/`
4. memory persistence:
   `experiments/workflow_artifact_smoke/runtime_data/memory/`

## Contract

Success means:

1. the canonical workflow completes
2. the researcher returns a valid `selected_article` JSON payload
3. the writer creates a three-paragraph markdown report
4. the workflow publishes a `summary_report` artifact record
5. the artifact record `output_ref` points at the written markdown file
6. transcript entries persist for the workflow session
7. memory persistence exists under the experiment-local runtime data root
