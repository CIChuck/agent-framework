# Development Kanban Governance Tactical Plan

Status: started

1. Freeze the merged documentation baseline at `63cb579` and create the isolated
   feature branch.
2. Archive the accepted documentation-governance packet and establish the new
   active governance packet.
3. Define and populate `board.yaml` plus its schema.
4. Implement read, validate, render, state-transition, condition, and delivery
   commands with maintainer-only approval and acceptance gates.
5. Extend documentation lifecycle validation to detect board drift.
6. Add the repository-local board skill and navigation links.
7. Run focused tests, Ruff, board validation, documentation validation, link
   checks, and diff checks.
8. Mark the work completed for maintainer review; do not self-accept or push
   without explicit authority.
9. Before final acceptance, add and validate the explicit `AGENTS.md`
   code-generation authority chain requested by the maintainer.
10. Reopen before acceptance and record the documentation-only
    independent-validation governance amendment and lightweight-change
    exemption.
11. Add the canonical independent-validation policy, mandatory construction
    directive gate, validator guidance, remediation loop, and AGENTS entry-point
    requirements.
12. Freeze a documentation candidate, dispatch one fresh-context read-only
    validator, and store its request, report, evidence, and disposition.
13. If the validator requests changes, create a bounded remediation directive,
    update the candidate, and require a fresh review. Stop after two unsuccessful
    cycles.
14. Re-run board and documentation validation, protected-guide comparison, link
    checks, and changed-file scope inspection.
15. Return the packet to `completed` only after `VERIFIED`; leave final
    acceptance, push, merge, and publication to explicit maintainer authority.
