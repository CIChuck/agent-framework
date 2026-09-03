# Phase 5-C: Canonical Workflow Artifact Smoke Experiment

**Status:** Proposed  
**Date:** 2026-03-16  
**Audience:** Runtime architects, workflow maintainers, experiment authors, agent-framework integrators

---

## 1. Problem Statement

Phase 5-A established layered prompt composition and transcript-backed runtime execution. Phase 5-B established declarative runtime tool loading in DI. The framework now has the primitives needed for tool-enabled, provider-backed, multi-agent workflow execution, but it still lacks a live experiment that exercises those capabilities together in one end-to-end path.

The missing coverage is not another single-agent smoke test. The missing coverage is a canonical workflow that:

1. executes through the runtime kernel,
2. uses two agents with distinct responsibilities,
3. uses real tools loaded from runtime configuration,
4. produces a physical artifact on disk,
5. publishes a workflow artifact record,
6. persists transcript and memory data under a stable experiment-owned path.

Without that experiment, the framework can claim support for orchestration, transcripts, tools, artifacts, and memory, but it does not yet prove that those surfaces work together under a realistic live run.

---

## 2. Phase Objective

Phase 5-C introduces a new self-contained experiment, `workflow_artifact_smoke`, that validates canonical workflow execution with real provider-backed inference and real tool use.

This phase introduces:

1. a new experiment directory independent of existing experiments,
2. a canonical two-agent workflow,
3. self-contained runtime, scenario, workflow, and agent configuration,
4. stable local persistence for artifacts, transcripts, and memory,
5. a stronger non-deterministic validation contract focused on structure, provenance, and persistence rather than exact generated text.

This phase is intentionally non-deterministic. It is meant to validate the live runtime stack, not replace deterministic framework audit experiments.

---

## 3. Experiment Goal

The experiment should perform a complete agentic run over a current-news task:

1. a researcher agent searches for news articles about agentic AI,
2. the researcher selects the most recent article from a reputable source,
3. a writer agent consumes that selected article only,
4. the writer produces a three-paragraph markdown summary,
5. the writer writes the markdown report to disk,
6. the workflow publishes an artifact record for the generated report.

The experiment should prove the framework can execute a canonical workflow with tool use, agent handoff, artifact persistence, transcript capture, and memory persistence under one runtime-owned configuration.

---

## 4. Architecture Decisions

## 4.1 Self-Contained Experiment Boundary

The experiment must not depend on earlier experiments for its runtime behavior, configuration, or helper files.

All required assets should live under:

`experiments/workflow_artifact_smoke/`

This includes:

1. runtime configuration,
2. local override example,
3. scenario input,
4. agent YAML,
5. workflow and pipeline YAML,
6. run harness,
7. README,
8. artifact output folders,
9. transcript and memory storage roots.

The experiment may reuse framework packages, but it must not reference another experiment directory as a source of configuration or execution logic.

## 4.2 Canonical Workflow Only

This experiment will validate the canonical workflow path only.

It should execute through `RuntimeKernel.execute_workflow(...)` with canonical workflow YAML and canonical pipeline YAML. Legacy workflow compatibility is outside the scope of this experiment because the point is to validate the current workflow contract, not the legacy adapter path.

## 4.3 Live Provider-Backed Execution

The experiment should use a real LLM service from its own runtime YAML, not a fake LLM.

The intent is to validate:

1. real prompt execution,
2. real tool-calling behavior,
3. real web retrieval behavior,
4. real transcript capture,
5. real memory persistence,
6. real artifact creation and publication.

This makes the experiment slower and less deterministic than the audit harnesses, but it is the correct tradeoff for this phase.

## 4.4 Artifact of Record Is Dual

The artifact of record has two parts:

1. a physical markdown file written by the writer agent, and
2. a workflow-published artifact record that captures provenance for that output.

The markdown file is the user-visible work product. The workflow artifact record is the execution-governed metadata record. Both are required for success.

## 4.5 Stronger Contract, Not Exact Text

Because the experiment is non-deterministic and provider-backed, success must be defined structurally rather than by exact wording.

The experiment should validate:

1. workflow success,
2. expected agent participation,
3. persisted markdown artifact,
4. persisted workflow artifact record,
5. transcript persistence,
6. memory persistence,
7. selected article metadata capture,
8. three-paragraph output shape,
9. provenance linking the output to workflow execution.

It should not attempt to assert exact sentences, exact formatting beyond the output contract, or exact provider token-level behavior.

---

## 5. Target Behavior

## 5.1 Researcher Agent

The researcher agent is responsible for discovery and selection.

Expected behavior:

1. search the web for current news on agentic AI,
2. identify candidate articles,
3. choose the most recent article from a reputable source,
4. read the selected article,
5. return structured article metadata and extracted content for the workflow handoff.

Required tool surface:

1. `web_search`
2. `web_reader`

Expected structured output:

1. article title,
2. article URL,
3. source/publication,
4. publication date if available,
5. extracted notes or article text,
6. justification that the source is reputable and the article is the most recent among candidates considered.

## 5.2 Writer Agent

The writer agent is responsible for summarization and artifact creation.

Expected behavior:

1. consume the single article selected by the researcher,
2. produce exactly three paragraphs of summary text,
3. mention the article title or publication,
4. write the result to a markdown file,
5. return data needed for workflow artifact publication.

Required tool surface:

1. `file_write`

Expected output:

1. markdown summary content,
2. output file path,
3. source metadata carried forward from the researcher handoff.

---

## 6. Directory Layout

Recommended structure:

```text
experiments/workflow_artifact_smoke/
  README.md
  run.py
  runtime.py
  config/
    runtime.yaml
    runtime.local.yaml.example
    scenario.yaml
  agents/
    researcher.yaml
    writer.yaml
  workflows/
    wf_agentic_news/
      workflow.yaml
      pipelines/
        pl_research.yaml
        pl_write.yaml
  artifacts/
  outputs/
  runtime_data/
    transcripts/
    memory/
```

The experiment should treat `runtime_data/`, `artifacts/`, and `outputs/` as persistent inspection targets rather than temporary scratch space.
The `workflows/` directory should be a sibling of `agents/`, not a subdirectory inside it.

---

## 7. Configuration Model

## 7.1 Runtime Configuration

`config/runtime.yaml` should be self-contained and define:

1. `agents.dir` pointing to this experiment’s own agent directory,
2. a workflow root or equivalent runtime/harness resolution pointing to this experiment’s own `workflows/` directory, which lives alongside `agents/`,
3. `runtime_data_root` under this experiment directory,
4. transcript enabled with a stable local transcript path,
5. memory persistence rooted under this experiment directory,
6. runtime prompting and transcript settings as needed,
7. tool loading through the new declarative runtime `tools` section,
8. provider-backed LLM settings suitable for live execution.

The runtime YAML should not import or rely on another experiment’s runtime file.

## 7.2 Local Overrides

`config/runtime.local.yaml.example` should exist only for secrets and machine-local overrides, such as:

1. API keys,
2. provider endpoints,
3. optional timeout tuning.

The experiment must run by merging its own `runtime.yaml` with its own local overlay.

## 7.3 Scenario Configuration

`config/scenario.yaml` should hold execution input rather than runtime-global policy.

Examples:

1. topic or query seed, such as `agentic AI news`,
2. target output filename,
3. output directory,
4. optional reputation hints or domain preferences if needed.

This preserves the prompt/runtime separation introduced in Phase 5-A.

---

## 8. Workflow Design

## 8.1 Workflow Identity

The experiment should define one canonical workflow bundle:

`wf_agentic_news`

This workflow should have two pipelines.

## 8.2 Research Pipeline

`pl_research` should:

1. accept the scenario input,
2. declare the intended executing agent in the pipeline task definition, using the canonical task ownership field for the `researcher` agent,
3. include the workflow-step instructions that tell that agent to search current agentic AI news, choose the most recent reputable article, read it, and return structured results,
4. emit a structured `selected_article` payload.

The output contract should be explicit enough that the writer consumes structured handoff data, not ambiguous free-form prose.

## 8.3 Writing Pipeline

`pl_write` should:

1. accept `selected_article`,
2. declare the intended executing agent in the pipeline task definition, using the canonical task ownership field for the `writer` agent,
3. include the workflow-step instructions that tell that agent to use only the selected article, produce exactly three paragraphs, write the markdown file, and return artifact metadata,
4. require creation of the markdown file,
5. publish a workflow artifact record for the generated output.

The writing pipeline is the point where workflow artifact provenance should be attached to the final file.

In this experiment, pipeline YAML is the authoritative place for step-specific task instructions and step-to-agent assignment. Agent YAML remains responsible for persistent identity, role, goal, tool access, and long-lived prompt behavior.

---

## 9. Persistence Model

This experiment should persist all inspection-relevant state under its own folder.

## 9.1 Artifact Persistence

The following should be retained:

1. markdown report under `outputs/`,
2. experiment run summary JSON under `artifacts/`,
3. workflow artifact metadata in the workflow execution result and any persisted artifact record store used by the runtime.

## 9.2 Transcript Persistence

Transcript data should be retained under:

`runtime_data/transcripts/`

Transcript persistence for this experiment must use a stable path under the experiment folder. Temporary transcript roots are not allowed for this experiment, and runtime shutdown must not delete transcript files created during the run.

The retained transcript must make it possible to inspect:

1. both agent turns,
2. tool use across those turns,
3. prompt and response context if transcript context logging is enabled.

## 9.3 Memory Persistence

Memory data should be retained under:

`runtime_data/memory/`

The point of this requirement is not just to write files but to prove that a live workflow run using transcript-backed runtime and memory-enabled execution leaves behind inspectable memory state under an experiment-owned path.

---

## 10. Validation Contract

This experiment should use a stronger contract than earlier smoke tests.

## 10.1 Required Success Conditions

A successful run must satisfy all of the following:

1. the workflow completes successfully,
2. the markdown output file exists,
3. the workflow artifact record exists and references that file,
4. transcript persistence exists under the experiment’s transcript folder and survives process shutdown,
5. memory persistence exists under the experiment’s memory folder,
6. the researcher output contains article title, URL, and source,
7. the selected URL is non-empty and plausibly article-shaped,
8. the writer output is non-empty and has exactly three paragraphs,
9. the written markdown references the selected article title or source,
10. workflow provenance links the output to the producing agent, pipeline, or workflow execution context.

## 10.2 Non-Goals For Validation

The experiment should not require:

1. exact summary wording,
2. exact paragraph wording,
3. exact article choice across all runs,
4. exact transcript payload text,
5. exact memory extraction counts.

Those constraints would make the experiment brittle for the wrong reasons.

---

## 11. Implementation Outline

Implementation should proceed in these steps:

1. create the experiment directory and README,
2. add self-contained runtime and scenario configuration,
3. author the two agent YAML files,
4. author the canonical workflow and pipeline YAML files,
5. implement the runtime harness that loads config and executes the workflow,
6. implement the CLI entrypoint,
7. ensure transcript, artifact, and memory paths are rooted locally,
8. persist a run-summary JSON artifact,
9. add regression coverage for the stronger structural contract.

This phase should use the existing framework runtime, workflow engine, transcript path, memory path, and declarative tool-loading contract rather than adding experiment-local special cases.

---

## 12. Risks and Tradeoffs

This experiment intentionally accepts several risks:

1. provider latency can increase runtime and make failures noisier,
2. web search results can vary over time,
3. article parsing quality may vary by publisher,
4. “reputable source” is partly a prompt-guided judgment rather than a hard-coded ranking rule.

These are acceptable because the purpose of this experiment is to validate live framework behavior. The validation strategy should therefore focus on execution structure, provenance, and persistence, not exact output text.

---

## 13. Expected Outcome

Phase 5-C should produce the first self-contained live workflow experiment that proves the framework can:

1. load tools declaratively,
2. execute a canonical multi-agent workflow,
3. use a real provider-backed model,
4. search and read web content,
5. hand off structured results between agents,
6. write a governed artifact to disk,
7. persist transcript and memory state locally for inspection.

That experiment becomes the natural live counterpart to the deterministic audit experiments introduced earlier in Phase 5.
