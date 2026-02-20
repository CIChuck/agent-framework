# Skills Compatibility Profile

**Status:** Proposed for Approval
**Date:** 2026-02-16
**Purpose:** Define environment-bound compatibility requirements for canonical skill artifacts and governance overlays.
**References:**
- `docs/design/agents/Alt-Phase-2/agent-contract.md`
- `docs/design/agents/Alt-Phase-2/technical-specifications.md`
- Phase 2 build baseline (archived)
- `docs/design/agents/Alt-Phase-2/phase-3-build-plan.md`
- `https://github.com/agentskills/agentskills/tree/main`
- `https://github.com/anthropics/skills`

---

## 1. Scope

This profile governs how skill compatibility is enforced for:

1. Canonical skill artifacts (`skills/<skill_id>/<version>/SKILL.md`).
2. Governance overlays (`skills/manifests/...`, `skills/registry/index.yaml`).
3. Runtime discovery, activation, and execution gates.

---

## 2. Compatibility Modes

| Mode | Enforcement |
| :--- | :--- |
| `strict` | Hard-fail on schema, layout, mapping, lifecycle, or policy mismatch. |
| `advisory` | Allow non-critical compatibility drift with warning telemetry and governance review tasks; still hard-fail security/lifecycle-critical violations. |

---

## 3. Environment Policy

1. `strict` is mandatory in all non-development environments:
   - `staging`,
   - `preprod`,
   - `production`.
2. `advisory` is permitted only in explicitly marked development/test environments.
3. Any exception to `strict` in non-development environments requires explicit governance approval and time-bounded waiver metadata.

---

## 4. Validation Baseline

Required validator and references:

1. Canonical schema validation command: `skills-ref validate <skill-path>`.
2. Primary schema/tooling reference:
   - `https://github.com/agentskills/agentskills/tree/main`
3. Additional ecosystem reference:
   - `https://github.com/anthropics/skills`

Required CI conformance checks:

1. `SKILL.md` frontmatter/schema validity.
2. Canonical skill directory/name/layout validity.
3. Deterministic `SKILL.md -> manifest/registry` mapping validity.

---

## 5. Runtime Enforcement Rules

1. Runtime activation MUST fail when canonical skill validation fails.
2. Runtime execution MUST fail in `strict` mode when compatibility checks fail.
3. Runtime MUST reject execution of non-`approved` skills in non-development environments.
4. Runtime MUST emit deterministic failure codes and auditable telemetry for each denial class.
5. Runtime MUST enforce restrictive merge semantics for contract + skill composition.
6. Skills MUST NOT expand contract governance envelope (tools, sandbox/network, workspace scope, HITL bypass).

---

## 5.1 Approval Gating Matrix for Skill Change Impact

| Impact Class | Typical Change Surface | Required Approvals | Required Evidence |
| :--- | :--- | :--- | :--- |
| `content_only` | Editorial/instructional changes with no behavioral/tool/artifact control delta | Standard governance approver | Schema/layout/mapping validation + change summary |
| `behavioral` | Backstory/runtime profile replacement, execution-style changes, artifact expectation changes | Governance approver | Policy-diff report + behavior regression tests |
| `governance_touching` | Tooling behavior shifts, sandbox/HITL/escalation/workspace-impacting directives | Governance + security/safety dual approval | Policy-diff report + no-expansion proof + behavior/safety test reports |

Classifier requirements:

1. Every skill change MUST be assigned one impact class before approval.
2. Classifier output MUST be deterministic and stored as release evidence.
3. If classifier confidence is ambiguous, default to the higher-impact class.

---

## 6. Evidence Requirements

Release evidence bundles MUST include:

1. `skills-ref` validator outputs.
2. Skill schema/layout/mapping CI conformance reports.
3. Lifecycle/approval-state conformance report.
4. Exception/waiver reports for any temporary policy deviations.
