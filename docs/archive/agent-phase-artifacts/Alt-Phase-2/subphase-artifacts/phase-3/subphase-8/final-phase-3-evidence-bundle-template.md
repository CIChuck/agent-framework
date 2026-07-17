# Phase 3 Final Evidence Bundle Template

## Purpose

Provide a single checklist-to-evidence package for Phase 3 release disposition.

## Required Bundle Sections

1. Contract and schema conformance
   - Workflow/pipeline/task schema conformance evidence.
   - Skill compatibility evidence (`skills-ref`, schema/layout/mapping checks).
   - HITL/authority policy conformance evidence.
2. Runtime behavior and resilience
   - Dispatch/claim/lease/recovery determinism evidence.
   - Replay/correlation/forensics evidence.
   - Scratch pad lifecycle/isolation/TTL evidence.
3. Compatibility and governance
   - `single_agent` default path compatibility evidence.
   - `friday.py` compatibility report.
   - Federated skill governance/no-expansion evidence.
4. Deployment and operations
   - Path topology conformance evidence (local/container/cloud).
   - Degraded mode/remediation runbooks.
   - Alerting and metrics contract evidence.
5. Decision records
   - FridayContainer disposition decision record.
   - Open risk register and waiver log.

## Minimum Attachment Set

1. Full gate outputs for final candidate:
   - `.venv/bin/pytest -q`
   - `ruff check .`
   - `mypy packages apps tests` (or approved equivalent gate command)
2. Targeted suites for each completed subphase.
3. Subphase artifact triads (`subphase-summary.md`, `verification-summary.md`, `next-subphase-brief.md`).
4. Change-scope manifest (code + docs) aligned to workstreams.

## Release Decision Fields

1. Candidate ID
2. Build timestamp
3. Gate results (pass/fail with baseline debt classification)
4. Blocking issues
5. Waivers approved (owner + expiry)
6. Final disposition (`release`, `hold`, `rollback`)
