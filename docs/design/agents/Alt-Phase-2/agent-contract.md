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

Every agent definition MUST include the required fields below. Optional fields are explicitly marked.

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
20. `skills` (optional): list of pinned skill references (`skill_id@version`) resolved through the skill manifest registry.
21. `scratch_pad_policy` (optional): private working-memory policy for planning/checklists/notes/artifact references.

Composition note:

1. Agent Contract defines the baseline governance envelope.
2. Active `SKILL.md` definitions may augment or replace profile/task/artifact sections at runtime.
3. Runtime composition MUST preserve contract hard limits (skills may narrow policy but MUST NOT widen policy).

Runtime prerequisite:

1. Agent execution environments MUST provide runtime filesystem topology configuration (`install_root`, `runtime_data_root`, `workspace_root`, optional `cache_root`).

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

### 5.3 Agent Skill Contract

An Agent Skill is the runtime profile artifact for an agent invocation. It defines:

1. profile skill behavior (backstory, role framing, operating style),
2. task skill behavior (tool orchestration and task execution),
3. expected artifact behavior (outputs and artifact expectations).

Skill reference model:

1. Agent contracts MUST reference skills as pinned identifiers: `skill_id@version`.
2. `version` MUST use semantic versioning (`major.minor.patch`).
3. Unpinned references (`skill_id` without version or `latest`) are not allowed.
4. Skills are reusable across agents but remain policy-scoped per agent contract.
5. Each active runtime profile is resolved from one or more pinned skills plus contract baseline composition.

Canonical skill artifact model:

1. Canonical portable artifact: `skills/<skill_id>/<version>/SKILL.md`.
2. `SKILL.md` MUST include YAML frontmatter for machine-readable metadata.
3. Governance overlay artifacts MAY exist for runtime control and enterprise governance:
   - `skills/manifests/<skill_id>/<version>.yaml`
   - `skills/registry/index.yaml`

Skill structure (canonical skill + governance mapping):

| Element | Description |
| :--- | :--- |
| Trigger | Activation condition (natural language intent, API call, or event) |
| Goal State | Success criteria for completed execution |
| Tool Chain | Ordered/parallel sequence of tools/resources orchestrated by the skill |
| Context Window | Required inputs from memory, environment, or user |
| Invariant | Constraints that must hold during execution (safety, schema, policy) |
| Output | Deliverable returned to caller (answer, artifact, or state change) |
| Profile Layer | Backstory/instruction layer applied to runtime prompt composition |
| Artifact Expectations | Required/expected artifact types, lifecycle hints, and provenance requirements |
| Lifecycle State | Governance state: `proposed`, `approved`, `deprecated`, `retired` |

Skill characteristics:

1. Repetitive utility: skills represent recurring patterns, not one-off tasks.
2. Tool orchestration: skills may invoke multiple tools sequentially or in parallel.
3. Bounded scope: skills define in-scope boundaries and explicit handoff behavior.
4. State awareness: skills can reuse persisted context across invocations.
5. Profile overlap: skills may overlap with contract fields by design; overlap is governed by precedence and non-expansion rules.

Skill enforcement:

1. Skills MUST be resolved from the skill manifest registry before execution.
2. Only `approved` skill versions may execute in production-like operation.
3. `deprecated` skill versions may execute only when explicitly allowed by policy and must emit deprecation warnings.
4. `retired` skill versions MUST be blocked from execution.
5. Skill tool-chain steps MUST pass existing `tool_policy`, `sandbox_policy`, `guardrail_policy`, and HITL checks where applicable.
6. Skill execution MUST emit auditable lifecycle events with correlation IDs and resolved manifest version.
7. Out-of-scope requests MUST follow explicit skill handoff or escalation behavior.
8. Canonical skill artifacts MUST pass AgentSkills-compatible schema validation before approval and production-like execution.
9. If a skill replaces backstory, tool intent, or artifact behavior, runtime MUST apply composition validation before activation.
10. Skill composition MUST NOT expand:
   - tool permissions beyond contract allowlists,
   - sandbox/network/write authority beyond contract policy,
   - HITL bypass behavior for approval-required actions.

Skill compatibility profiles:

| Profile | Required Behavior | Optional Behavior |
| :--- | :--- | :--- |
| `strict` | Block activation/execution on schema, layout, lifecycle, or policy/tool mismatch. | None. |
| `advisory` | Enforce security/lifecycle hard-blocks (`retired`, missing approval metadata, unsafe policy conflicts). | Permit non-critical compatibility drift with warnings, telemetry, and governance review task creation. |

Default profile guidance:

1. Non-development environments (`staging`, `preprod`, `production`): `strict` is mandatory.
2. Development and exploratory environments: `advisory` allowed when explicitly configured.

### 5.5 Runtime Composition and Precedence Contract

Runtime composition order:

1. Agent Contract baseline.
2. Active skill profile layer(s) from canonical `SKILL.md`.
3. Task execution directives resolved from skill task sections.

Precedence rules:

1. Skill profile/task/artifact sections MAY augment or replace corresponding contract soft fields (for example, backstory text and task-specific artifact expectations).
2. Contract hard governance fields remain authoritative:
   - `tool_policy`,
   - `sandbox_policy`,
   - `guardrail_policy`,
   - `hitl_policy`,
   - `failure_policy`,
   - workspace boundaries.
3. On conflict, runtime MUST take the most restrictive effective policy.

Approval-impact classes for skills:

1. `content_only`: instructional/content changes without policy/tool/artifact control changes.
2. `behavioral`: modifies backstory, execution behavior, or artifact expectations.
3. `governance_touching`: attempts to influence tool/sandbox/HITL/escalation or workspace behavior.

Required approval gates by class:

1. `content_only`: standard lifecycle approval.
2. `behavioral`: enhanced review with policy-diff evidence.
3. `governance_touching`: security/governance dual approval and mandatory test evidence; reject on policy expansion.

### 5.4 Skill Manifest and Registry Contract

Phase 2 establishes a local filesystem-backed skill registry with canonical `SKILL.md` compatibility.

Repository model:

1. Canonical skill definition MUST exist at:
   - `skills/<skill_id>/<version>/SKILL.md`
2. Governance manifest overlay SHOULD exist at:
   - `skills/manifests/<skill_id>/<version>.yaml`
3. A registry index MUST map each `skill_id@version` to canonical skill path, manifest path (if present), status, owner, and review metadata.
4. Runtime discovery MUST resolve canonical skill artifacts through registry metadata and enforce policy/lifecycle gates before activation.

Schema validation reference point:

1. AgentSkills reference repository and schema tooling:
   - `https://github.com/agentskills/agentskills/tree/main`
2. Additional open skill ecosystem reference:
   - `https://github.com/anthropics/skills`
3. Canonical validation command:
   - `skills-ref validate <skill-path>`

Manifest minimum fields:

1. `skill_id`
2. `version`
3. `status` (`proposed`, `approved`, `deprecated`, `retired`)
4. `owner`
5. `description`
6. `triggers`
7. `goal_state`
8. `tool_chain`
9. `context_requirements`
10. `invariants`
11. `outputs`
12. `scope_boundary`
13. `handoff_policy`
14. `sandbox_requirements`
15. `hitl_requirements`
16. `provenance_requirements`

Registry and approval rules:

1. Lifecycle transitions MUST follow: `proposed -> approved -> deprecated -> retired`.
2. Direct transitions that skip governance review are not allowed.
3. Runtime resolution MUST fail fast if:
   - reference is unknown,
   - version is missing,
   - lifecycle state is disallowed for execution,
   - required tools conflict with agent policy.
4. Multi-agent workflows MAY share the same registry, but each agent MUST use explicit contract allowlists.

Skill registry approval authority:

1. Transition `proposed -> approved` MUST be human-authorized in Phase 2.
2. Approval records MUST include:
   - `approval_id`,
   - `approved_by`,
   - `approved_at`,
   - `change_reason`.
3. Registry updates that change lifecycle state MUST be auditable and append immutable review history metadata.
4. Runtime execution MUST reject `approved` transitions missing required approval metadata.

Example manifest and index entries:

```yaml
# skills/manifests/calendar_qna/1.2.0.yaml
skill_id: "calendar_qna"
version: "1.2.0"
status: "approved"
owner: "calendar-platform"
description: "Answer calendar questions with bounded read-only integrations."
triggers: ["intent:calendar_question"]
goal_state: ["Accurate schedule answer with provenance"]
tool_chain: ["search_calendar", "resolve_attendees", "draft_response"]
context_requirements: ["active_session_id", "user_timezone"]
invariants: ["No writes outside workspace roots"]
outputs: ["answer_text", "citation_refs"]
scope_boundary:
  in_scope: ["calendar lookup", "attendee resolution"]
  out_of_scope: ["sending notifications"]
handoff_policy:
  out_of_scope_action: "escalate"
  escalation_reason_code: "skill_scope_exceeded"
sandbox_requirements:
  required: true
hitl_requirements:
  approval_required_for: ["external_side_effect"]
provenance_requirements:
  required_fields: ["skill_ref", "correlation_id", "request_id"]
```

```yaml
# skills/registry/index.yaml
skills:
  - skill_ref: "calendar_qna@1.2.0"
    manifest_path: "skills/manifests/calendar_qna/1.2.0.yaml"
    status: "approved"
    owner: "calendar-platform"
    review_metadata:
      approved_by: "governance-board"
      approved_at: "2026-02-14T12:00:00Z"
```

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

### 8.1 Runtime Filesystem Boundary Contract

Runtime environments MUST separate installation, runtime state, and workspace data:

1. `install_root`: code/package location; may be read-only.
2. `runtime_data_root`: writable internal runtime state (journals, indexes, scratch-pad persistence).
3. `workspace_root`: writable user-facing artifact/intermediary workspace.

Boundary rules:

1. Internal runtime memory/state stores MUST NOT be placed in `workspace_root`.
2. `workspace_root` MUST contain only agent-created artifacts/intermediates and related metadata.
3. Path layout MUST be deployment-agnostic and MUST NOT assume git-repository presence.

---

## 9. Memory and Context Contract

1. Memory mode MUST be explicit (`single_agent` or `multi_agent`).
2. In multi-agent memory mode, namespace and arbitrator policy MUST be enforced.
3. Provenance metadata MUST be attached to memory writes.
4. Retention and deletion behavior MUST be policy-defined.

### 9.1 Scratch Pad Memory Contract

Scratch pad memory is a private, short-horizon operational memory surface for agent execution management.

Required scope and access rules:

1. Scratch pad identity MUST be scoped by `(session_id, agent_id)`.
2. Scratch pad reads/writes are private to the owning agent.
3. Cross-agent scratch pad reads/writes are denied by default.
4. Collaboration across agents MUST use explicit handoff payloads, not scratch pad sharing.

Required behavior:

1. Scratch pad SHOULD support typed planning entries:
   - `plan`,
   - `plan_item`,
   - `note`,
   - `artifact_ref`,
   - `event_log`.
2. Scratch pad retention MUST be TTL-based when enabled.
3. Scratch pad data is operational state and MUST NOT be treated as durable semantic truth by default.
4. Promotion from scratch pad to durable memory MUST be explicit and policy-gated.
5. Scratch pad persisted storage MUST live under `runtime_data_root`.
6. Scratch pad persisted storage MUST NOT live under `workspace_root` except explicit test-only fixtures.

Required policy knobs (when `scratch_pad_policy` is declared):

1. `enabled`
2. `retention_ttl_seconds`
3. `max_entries`
4. `max_note_bytes`
5. `allow_promotion`
6. `backend` (`in_memory` | `sqlite`) via runtime config
7. `path` (required for persistent backends) via runtime config
8. `fallback_mode` (`fail_fast` | `disable_scratch`) via runtime config

### 9.2 Arbitrator Identity and Shared-Write Capability Contract

Arbitrator-only shared writes MUST be enforced with identity plus capability validation.

Required enforcement:

1. Declaring caller identity as `arbitrator` is not sufficient by itself.
2. Shared writes to `shared:/` MUST require a valid runtime-issued internal capability bound to session/run scope.
3. Capability issuance and validation MUST be performed by trusted runtime components only.
4. Capability replay outside allowed scope MUST be rejected.
5. Capability verification MUST be enforced at all shared-write entrypoints (facade and storage-boundary paths).

Required failure behaviors:

1. Missing capability -> reject write.
2. Invalid capability -> reject write.
3. Identity spoof attempt -> reject write and emit security/audit event.

### 9.3 Migration and Backfill Governance Contract

Migration/backfill from legacy records to multi-agent metadata MUST follow a two-stage operational flow.

Required stages:

1. `preflight`:
   - inventory legacy records missing required fields,
   - produce projected change counts by store/domain,
   - validate namespace stamping policy and rollback checkpoint readiness.
2. `apply`:
   - execute staged metadata updates with migration journal entries,
   - run post-apply integrity checks and publish results.

Required controls:

1. Dry-run mode MUST be supported before apply.
2. Explicit rollback criteria MUST be defined before apply.
3. Failed critical validations MUST block cutover and require rollback/remediation workflow.

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
8. skill resolution and lifecycle transitions (`skill_requested`, `skill_selected`, `skill_blocked`, `skill_completed`, `skill_failed`, `skill_delegated`),
9. scratch pad lifecycle and mutation events (`scratchpad_created`, `scratchpad_plan_updated`, `scratchpad_item_status_changed`, `scratchpad_note_added`, `scratchpad_artifact_ref_added`, `scratchpad_expired`, `scratchpad_promoted`),
10. artifact created/updated/finalized,
11. error and recovery events.

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

  scratch_pad_policy:
    enabled: true
    retention_ttl_seconds: 86400
    max_entries: 500
    max_note_bytes: 8192
    allow_promotion: true

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

  skills:
    - "calendar_qna@1.2.0"
    - "research_summarization@2.0.1"

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
10. Skill references are pinned (`skill_id@version`) and resolve through the registry index.
11. Skill manifests are in allowed lifecycle state (`approved` for production execution).
12. Skill-to-policy compatibility validated (tool/sandbox/guardrail/HITL).
13. Skill lifecycle observability and handoff behavior verified.
14. Skill manifest governance evidence (owner/review/state history) verified.
15. Scratch pad scope isolation (`session_id + agent_id`) is enforced.
16. Scratch pad TTL/retention and quota controls are validated.
17. Scratch pad event completeness is verified when scratch pad is enabled.
18. Scratch-to-durable promotion policy is validated (allow/deny paths).
19. Runtime filesystem roots are configured and validated (`install_root`, `runtime_data_root`, `workspace_root`).
20. Scratch persisted path placement under `runtime_data_root` is validated (not `workspace_root`, except test fixtures).
21. Arbitrator shared-write enforcement validates both identity class and runtime-issued capability.
22. Migration preflight/apply/rollback governance outputs are reviewed before multi-agent cutover.
23. Skill registry approval transitions (`proposed -> approved`) include required authority metadata and audit history.
