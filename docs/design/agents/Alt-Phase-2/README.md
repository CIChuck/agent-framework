# Alt Phase 2 Documentation Set

This folder contains an alternate planning track for Phase 2 that introduces **Multi-Agent Memory as an additive mode**, **Scratch Pad Memory** as private operational memory, and a **deployment-agnostic runtime filesystem topology** while preserving default single-agent behavior.

## Approval State

This document set is currently marked **Proposed for Approval**.

## Documents

1. `phase-1-build-plan.md`
   - Historical baseline retained locally in this folder for transition context.
2. `comprehensive-agent-framework-design.md`
   - Architectural rationale, control-plane overview diagrams, workflow/pipeline/task framing, and component responsibilities.
3. `technical-specifications.md`
   - Additive interfaces, schemas (including workflow/pipeline/task contracts), state machines, policy rules, and runtime path/topology requirements.
4. Phase 2 build baseline (archived)
   - Detailed implementation plan for Alt Phase 2.
5. Phase 2 execution baseline (archived)
   - AI-executable decomposition of Phase 2 into bounded subphases with handoff artifacts and exit criteria.
6. Phase 2 file-impact baseline (archived)
   - Pre-implementation file scope lock (by subphase) for AI-agent execution control.
7. `phase-3-transition-plan.md`
   - Transition contract from Alt Phase 2 to Phase 3.
8. `phase-3-build-plan.md`
   - Updated Phase 3 build direction aligned to dual-memory architecture.
9. `agent-contract.md`
   - Standard contract for agent goals, guardrails, scratch-pad and skill governance, tool usage, sandboxed code execution, logging, and escalation.
10. `agent-contract-compliance-matrix.md`
   - Clause-by-clause compliance analysis and upgrade plan for the Alt document set.
11. `agent-contract-schema-spec.md`
   - Canonical schema and validation specification for Agent Contract governance.
12. `agent-contract-test-strategy.md`
   - Verification and CI gate strategy for contract compliance.
13. `agent-integration-test-plan.md`
   - End-to-end integration test planning for solitary-agent and multi-agent workflows, including environment construction.
14. `gap-closure-addendum.md`
   - Focused closure plan and status for identity/capability hardening, migration governance, and skill approval authority.
15. `skills-compatibility-profile.md`
   - Canonical compatibility profile for skill validation/enforcement modes across environments.
16. `phase-3-execution-plan.md`
   - AI-executable decomposition of Phase 3 into bounded subphases with gate-driven evidence handoffs.
17. `phase-3-file-impact-manifest.md`
   - Pre-implementation file scope lock (by subphase) for Phase 3 execution control.
18. `docs/design/agents/Phase-4/phase-4-build-plan.md`
   - Runtime coherence plan for YAML-first runtime config, multi-LLM pool, canonical workflow/pipeline/task execution, and compatibility migration.
19. `docs/design/agents/Phase-4/phase-4-build-plan-examples.md`
   - Developer-focused examples for single-agent and multi-agent workflow construction, including runtime and agent binding patterns.
20. `docs/design/agents/Phase-4/phase-4-ai-agent-implementation-guide.md`
   - AI synthetic developer execution guide for implementing the Phase 4 runtime/workflow model with deterministic gates and evidence requirements.

## Source Inputs

This alt track incorporates findings from:

- Legacy Phase 2 commentary and baseline planning notes (archived).
- Skill reference ecosystems:
  - `https://github.com/agentskills/agentskills/tree/main`
  - `https://github.com/anthropics/skills`

## Compliance Posture

Per `agent-contract-compliance-matrix.md`, this document set is now broadly contract-aligned with remaining precision work focused on:

1. Agent-class KPI/SLO calibration.
2. Authority-policy template standardization.
3. Package-level failure/rollback runbook depth.
4. Phase 3 depth for dynamic skill routing/delegation governance.
5. Phase 3 extension strategy for optional federated/remote skill registry operations.
6. Scratch pad TTL/quota defaults and workflow integration depth calibration.
7. Deployment-profile defaults for runtime filesystem roots and scratch backend selection.

## Canonical Terminology

This glossary is the single source of truth for skill terms used across Alt-Phase-2 documents.

1. `SkillRef`: pinned contract reference in `skill_id@version` format.
2. `SKILL.md`: canonical portable skill artifact at `skills/<skill_id>/<version>/SKILL.md` with YAML frontmatter.
3. `SkillManifest`: governance overlay artifact, typically `skills/manifests/<skill_id>/<version>.yaml`.
4. `SkillRegistryEntry`: discovery and governance metadata row, typically in `skills/registry/index.yaml`.
5. `Strict compatibility`: block execution on schema/layout/mapping/policy conflicts.
6. `Advisory compatibility`: allow controlled non-critical compatibility drift with warning telemetry and governance review.
7. `Skill activation`: runtime operation that loads and enables a resolved skill for execution.
8. `Skill discovery`: runtime operation that enumerates policy-eligible skills for a contract/session context.

## Reader Path

1. Start with `comprehensive-agent-framework-design.md` for the architecture overview and control-plane gestalt.
2. Continue to `technical-specifications.md` for canonical workflow/pipeline/task schemas and execution semantics.
3. Use Phase 2 build baseline (archived) and `phase-3-build-plan.md` for macro sequencing and release gates.
4. Use `phase-3-execution-plan.md` and `phase-3-file-impact-manifest.md` for bounded AI-executable implementation planning.
5. Use `docs/design/agents/Phase-4/phase-4-build-plan.md` for coherence contracts and acceptance gates, then `docs/design/agents/Phase-4/phase-4-build-plan-examples.md` and `docs/design/agents/Phase-4/phase-4-ai-agent-implementation-guide.md` for developer and AI-implementer execution guidance.
