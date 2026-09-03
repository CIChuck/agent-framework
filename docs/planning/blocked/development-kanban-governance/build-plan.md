# Development Kanban Governance Build Plan

Status: started; independent-validation governance amendment in progress

## Scope

1. Define canonical work states, conditions, delivery states, transition gates,
   and authority boundaries.
2. Add a machine-readable board and deterministic human-readable dashboard.
3. Import every current lifecycle packet conservatively.
4. Add validation and guarded mutation commands.
5. Add a repository-local skill that operates from the board and policy.
6. Add regression tests and integrate board checks with documentation validation.
7. Make `AGENTS.md` the canonical operational entry point for code-generation
   authority and connect it to the board and planning artifact hierarchy.
8. Require a construction directive for every code-generating work unit, with a
   recorded maintainer exemption for qualifying lightweight changes.
9. Define an independent producer-reviewer-remediator gate with frozen candidate
   identity, cold-review provenance, deterministic evidence, stale-review
   invalidation, bounded remediation, and human-only final acceptance.
10. Add reusable repository-local validator and remediation guidance without
    changing package source, tests, runtime behavior, or automation code.

## Acceptance Criteria

- **AC-01:** Every current planning packet appears exactly once on the board.
- **AC-02:** The dashboard is generated from the canonical board without state
  drift.
- **AC-03:** Agent-role commands cannot approve or accept work.
- **AC-04:** Started work requires a branch; completed work requires validation
  evidence.
- **AC-05:** Packet placement matches work state or condition.
- **AC-06:** Accepted work retains explicit maintainer and delivery evidence.
- **AC-07:** The existing documentation lifecycle and local-link checks continue
  to pass.
- **AC-08:** `docs/guides/` and package runtime behavior remain unchanged.
- **AC-09:** Applicable work remains `started` through validation and remediation and may
  become `completed` only after an evidence-backed `VERIFIED` result.
- **AC-10:** A validation subagent cannot edit, self-remediate, accept, push, merge,
  release, deploy, disclose credentials, or create unapproved external effects.
- **AC-11:** Review requests pin authority and candidate revisions; changed reviewed inputs
  invalidate the prior decision.
- **AC-12:** Findings produce bounded remediation directives and no more than two automatic
  remediation cycles before maintainer escalation.
- **AC-13:** The documentation-only amendment receives an independent cold review before
  completion is proposed.

## Out Of Scope

- A hosted web board or third-party issue-tracker integration.
- Automatic creation, push, merge, release, or deletion of Git branches.
- Authentication of a human identity beyond recorded repository process.
- Rewriting historical plan bodies solely to normalize terminology.
- Implementing machine-enforced `execution_phase` or `validation_state` board
  fields; packet metadata provides the approved documentation-only process until
  a separate automation change is planned and authorized.
