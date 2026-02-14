# Agent Contract

**Status:** Proposed for Approval
**Date:** 2026-02-14
**Scope:** Standard contract for agents in the Friday Agent Framework
**Related Docs:**
- `docs/design/agents/Alt-Phase-2/comprehensive-agent-framework-design.md`
- `docs/design/agents/Alt-Phase-2/technical-specifications.md`
- `docs/design/agents/Alt-Phase-2/phase-1-build-plan.md`
- `docs/design/agents/Alt-Phase-2/phase-2-build-plan.md`
- `docs/design/agents/Alt-Phase-2/phase-3-build-plan.md`
---

## 1. Purpose

An Agent Contract defines the required operational, safety, and quality boundaries for any agent in the framework. It ensures agents can execute goals reliably while remaining auditable, bounded, and secure.

---

## 2. Agent Definition

An agent is a bounded execution unit with:

1. Identity and role.
2. Backstory/context.
3. Goals and objectives.
4. Assigned model(s).
5. Tool access policy.
6. Workspace boundaries.
7. Artifact responsibilities.
8. Guardrails and escalation rules.
9. Logging and evaluation requirements.

Agents operate in one of three modes:

1. **Autonomous:** completes tasks independently within policy bounds.
2. **Semi-autonomous:** requests human input at defined gates.
3. **Co-pilot:** collaborates interactively (for example in `friday.py` REPL).

---

## 3. Required Contract Fields

Every agent definition MUST include:

1. `agent_id`: stable unique identifier.
2. `name`: human-readable identifier.
3. `role`: responsibility domain.
4. `backstory`: bounded context and perspective.
5. `goals`: ordered list of outcomes to achieve.
6. `objectives`: measurable sub-targets.
7. `success_criteria`: explicit acceptance criteria.
8. `stop_conditions`: when the agent must terminate or hand off.
9. `mode`: autonomous | semi_autonomous | copilot.
10. `workspace_roots`: allowed paths and write boundaries.
11. `tool_policy`: allowlist, denylists, approvals, rate constraints.
12. `model_policy`: primary model, fallback model(s), cost/latency limits.
13. `memory_mode`: allowed memory mode (`single_agent` | `multi_agent`).
14. `guardrail_policy`: safety constraints and forbidden behaviors.
15. `escalation_policy`: when and why to escalate.
16. `hitl_policy`: methods, authority rules, state transitions, timeout defaults, and resume/cancel behavior.
17. `artifact_policy`: artifact naming, provenance, versioning, lifecycle.
18. `logging_policy`: required structured events and traceability.
19. `failure_policy`: retries, fallback, rollback, and recovery.

---

## 4. Core Operating Rules

1. Agents MUST operate only within their assigned workspace and permission scope.
2. Agents MUST pursue only assigned goals/objectives and reject out-of-scope tasks unless re-authorized.
3. Agents MUST use tools through policy-governed interfaces; raw bypass paths are prohibited.
4. Agents MUST record decision and execution traces sufficient for audit and replay.
5. Agents MUST stop, escalate, or fail safely when policy or confidence thresholds require it.

---

## 5. Tool Calling Contract

Tool calling is first-class and policy-bound.

### 5.1 Tool Access

1. Tools MUST be explicitly allowlisted per agent.
2. High-impact tools (filesystem writes, network, code execution, external side effects) MUST support approval gates.
3. Tool usage SHOULD include budgets (call count, duration, token/cost constraints).

### 5.2 Tool Invocation Requirements

For each tool call, agent MUST log:

1. intent,
2. inputs (sanitized),
3. policy checks,
4. execution result,
5. side effects,
6. follow-up decision.

---

## 6. Code Execution and Sandboxing Contract

Code execution is a primary mechanism for achieving objectives and is mandatory to govern explicitly.

### 6.1 Execution Lifecycle

1. **Plan:** agent states why code execution is needed.
2. **Generate:** agent produces code artifact(s) in workspace.
3. **Pre-check:** static and policy validation before run.
4. **Execute in sandbox:** run in constrained environment.
5. **Capture:** collect stdout/stderr/artifacts/exit status.
6. **Interpret:** map results to goal/objective progress.
7. **Persist evidence:** log run metadata and outputs.

### 6.2 Sandbox Requirements

1. Execution MUST occur in sandboxed runtime by default.
2. Sandbox MUST enforce filesystem, network, process, and resource constraints.
3. Sandbox policy MUST specify:
   - writable roots,
   - network allowance,
   - command/tool allowlist,
   - timeouts,
   - memory/CPU limits,
   - escalation path for privileged execution.
4. Escape or policy violation attempts MUST terminate execution and emit security events.

### 6.3 Result Integrity

1. Agent MUST not claim execution results not observed in sandbox output.
2. Agent SHOULD include reproducibility metadata (command, environment, artifact hash).
3. Failed runs MUST feed failure policy (retry, modify plan, escalate).

---

## 7. Guardrail Contract

Guardrails MUST include at least:

1. scope guardrails: task/objective boundaries,
2. safety guardrails: prohibited content/actions,
3. data guardrails: secret handling and data classification,
4. execution guardrails: sandbox and tool limits,
5. authority guardrails: approval-required actions.

Guardrails MUST be enforceable at runtime, not only prompt-level guidance.

---

## 8. Workspace and Artifact Contract

1. Agent MUST create artifacts only in designated workspace.
2. Each artifact SHOULD include provenance metadata:
   - creator agent,
   - session/run id,
   - timestamp,
   - source dependencies,
   - revision/version.
3. Artifact lifecycle states SHOULD be explicit: `draft`, `validated`, `final`, `archived`.
4. Intermediary artifacts are permitted and encouraged when they improve reliability and traceability.

---

## 9. Memory and Context Contract

1. Memory mode MUST be explicit (`single_agent` or `multi_agent`).
2. In multi-agent memory mode, namespace and arbitrator policy MUST be enforced.
3. Provenance metadata MUST be attached to memory writes.
4. Retention and deletion behavior MUST be policy-defined.

---

## 10. Human Interaction and Escalation Contract

Human-in-the-loop (HITL) is mandatory for semi-autonomous and co-pilot agents and required for defined high-impact actions in autonomous agents.

### 10.1 Required HITL Methods

The contract MUST identify one or more approved interaction methods:

1. **Approval Gate (binary):** approve/reject a pending action.
2. **Decision Selection (multi-option):** human selects one option from agent-proposed alternatives.
3. **Clarification Loop:** agent asks targeted questions to resolve ambiguity before continuing.
4. **Conflict Adjudication:** human resolves contradictory evidence, policy conflicts, or arbitration escalations.
5. **Override/Interrupt:** human can halt, redirect, or constrain the current plan.
6. **Checkpoint Review:** human validates intermediate artifacts before finalization.

### 10.2 HITL Trigger Classes

At minimum, triggers MUST include:

1. low confidence on critical decisions,
2. policy ambiguity or guardrail uncertainty,
3. irreversible or high-impact side effects,
4. repeated execution/tool failures beyond retry threshold,
5. conflicting evidence requiring judgment,
6. explicit user-requested approval checkpoints.

### 10.3 Mandatory Approval Matrix

Each agent contract MUST define which actions require mandatory human approval. At minimum include:

1. privileged sandbox execution or policy escalation,
2. writes outside standard workspace scope,
3. destructive file/system operations,
4. external side effects (network writes, integrations, notifications, transactions),
5. final artifact publication when configured as review-required.

### 10.4 HITL Execution State Model

Each task involving HITL MUST use explicit states:

1. `running`
2. `awaiting_human`
3. `approved`
4. `rejected`
5. `timed_out`
6. `cancelled`
7. `resumed`
8. `terminated`

### 10.5 Effect on Task Execution

When entering `awaiting_human`, the runtime MUST:

1. pause side-effecting tool calls,
2. block privileged sandbox execution until decision is received,
3. persist checkpoint state (current plan step, pending action, artifact versions),
4. expose a resumable decision request with deadline and default action.

When a decision is received:

1. `approved` resumes from checkpoint,
2. `rejected` terminates or reroutes to safe alternative,
3. `timed_out` applies pre-declared default behavior,
4. `cancelled` terminates task with explicit status and audit record.

### 10.6 HITL Request and Response Payloads

Escalation requests MUST include:

1. `request_id`,
2. `task_id` and `agent_id`,
3. reason code and risk level,
4. concise context summary and evidence,
5. options with tradeoffs,
6. recommended option,
7. deadline/timeout and default action.

Human responses MUST include:

1. `request_id`,
2. selected decision (`approve`, `reject`, `option_x`, `cancel`),
3. optional constraints/comments,
4. responder identity and timestamp.

### 10.7 HITL Timeout and Default Behavior

Every HITL gate MUST define timeout handling:

1. timeout duration,
2. default action on timeout (`safe_abort`, `defer`, or constrained continue),
3. maximum reminder/retry attempts,
4. escalation path if no response is received.

### 10.8 HITL Audit and Metrics

HITL flows MUST be fully auditable and measured. Required metrics:

1. escalation rate per task type,
2. human response latency,
3. approve/reject/override distribution,
4. timeout rate,
5. post-approval failure rate.

---

## 11. Logging, Observability, and Auditability

Agents MUST emit structured logs with correlation IDs.

Minimum event set:

1. task start/stop,
2. goal/objective status updates,
3. tool call started/completed/failed,
4. code execution run metadata and outputs,
5. guardrail checks and policy denials,
6. escalation requests, reminders, and resolutions,
7. HITL state transitions (`awaiting_human`, `approved`, `rejected`, `timed_out`, `cancelled`, `resumed`),
8. artifact created/updated/finalized,
9. error and recovery events.

Logs MUST support post-hoc audit and deterministic replay where applicable.

---

## 12. Failure and Recovery Contract

1. Failure policy MUST define retry limits and backoff.
2. Agent MUST distinguish transient vs terminal errors.
3. For terminal errors, agent MUST return actionable failure state (what failed, why, what is needed).
4. Partial side effects SHOULD be rolled back or clearly marked for compensation.

---

## 13. Multi-Agent Coordination Contract

When agents collaborate:

1. Ownership boundaries MUST be explicit per subtask/artifact.
2. Handoffs MUST include structured context and acceptance criteria.
3. Shared-memory writes in multi-agent mode MUST go through arbitration/promotion policy.
4. Conflict resolution path MUST be defined (automatic or human-mediated).

---

## 14. Quality and Evaluation Contract

Each agent SHOULD be measured on:

1. goal completion rate,
2. objective accuracy,
3. policy compliance rate,
4. tool-call success rate,
5. execution reproducibility,
6. latency and cost,
7. human escalation quality.

---

## 15. Minimal Contract Template (Example)

```yaml
agent_contract:
  agent_id: "researcher-01"
  name: "Research Agent"
  role: "evidence gathering"
  backstory: "Domain analyst focused on verifiable sources"

  mode: "semi_autonomous"

  goals:
    - "Produce validated research summary"
  objectives:
    - "Collect >= 3 corroborating sources"
    - "Flag contradictions"

  success_criteria:
    - "Summary delivered with citations and confidence scores"
  stop_conditions:
    - "Success criteria met"
    - "Policy block requiring human approval"

  workspace_roots:
    - "/workspace/project"

  tool_policy:
    allowed_tools: ["search", "read_file", "write_file", "exec_sandboxed"]
    approval_required_tools: ["network_write", "privileged_exec"]

  sandbox_policy:
    required: true
    timeout_seconds: 120
    network_mode: "restricted"
    writable_roots: ["/workspace/project"]

  memory_mode: "single_agent"

  guardrail_policy:
    scope_rules: ["No out-of-scope file writes"]
    safety_rules: ["No destructive operations without approval"]
    data_rules: ["No secret exfiltration"]
    execution_rules: ["Sandbox execution required"]
    authority_rules: ["Privileged execution requires approval"]

  escalation_policy:
    trigger_classes:
      - "low_confidence_critical_decision"
      - "policy_ambiguity"
      - "high_impact_side_effect"
    mandatory_approval_actions:
      - "privileged_exec"
      - "external_side_effect"
      - "destructive_action"
    default_escalation_method: "approval_gate"

  hitl_policy:
    enabled: true
    methods:
      - "approval_gate"
      - "decision_selection"
      - "clarification_loop"
    state_model:
      pause_on_awaiting_human: true
      block_side_effect_tools: true
      checkpoint_on_pause: true
    timeout:
      seconds: 900
      default_action: "safe_abort"
      reminder_attempts: 2
    decision_payload_required:
      - "request_id"
      - "reason_code"
      - "risk_level"
      - "options"
      - "recommended_option"
      - "deadline"
      - "default_action"

  logging_policy:
    structured: true
    required_events:
      - "task_lifecycle"
      - "tool_calls"
      - "sandbox_execution"
      - "policy_checks"
      - "hitl_requests"
      - "hitl_state_transitions"
```

---

## 16. Approval Checklist

Before approving an agent for production-like operation:

1. Contract fields complete and validated.
2. Guardrails enforceable in runtime.
3. Tool and sandbox policies tested.
4. Logging completeness verified.
5. HITL methods, triggers, and approval matrix validated.
6. HITL timeout/default behavior validated in execution tests.
7. Failure and escalation paths validated.
8. Artifact and workspace boundaries verified.
9. Memory mode and provenance behavior verified.
