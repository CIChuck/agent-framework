# TELEM-03 accepted: safe LLM metrics and role-service injection

Status: accepted work unit. Accepted by Chuck Russell on2026-10-07.
Decision: **"lets continue with telem-04"**, following the verified-result report
and the explanation that acceptance records sign-off before the next unit.
This record attributes acceptance to that explicit progression instruction,
not to independent verification alone.

Product candidate: `dd543fd6a6819ec0c4fb2529fa384fea886f5509`.
Evidence closeout: `e6209e3156216afde1655758e280690229f7d3e6`.
[Exact decision, approved controls and frozen evidence hashes](acceptance-evidence.json).
[Independent VAL-008 VERIFIED](../../../../planning/active/friday-telemetry-rewire/validation/VAL-008/report.md).
[Builder evidence](../../../../planning/active/friday-telemetry-rewire/execution/TELEM-03-final/report.md).
[Continuing initiative](../../../../planning/active/friday-telemetry-rewire/README.md).

Accepted behavior: safe typed/legacy/stream/embedding request/attempt/batch events,
truthful usage/cost provenance and borrowed provider-neutral injection through
Chat role-service factories. Root2,996 and owning2,978 tests passed with the
unchanged optional SciPy skip; Chat/LLM/telemetry1,115 and new105 passed without
skips. Changed-unit/aggregate lint and typing passed. Raw root Ruff remained
exit1 with exactly327 findings under approved WVR-005.

WVR-005 now expires under its existing terms. Frozen approved controls, contracts,
validation reports and raw evidence stay unchanged at their original locations;
no carry-forward authority is granted. REM-004-HIST-01 and REM-004-GENERIC-01
remain maintainer-owned follow-ups. No new product/delivery/live effects occur.
The continuing initiative remains started/local. TELEM-04 planning is authorized;
its new exact construction scope and lint disposition are separate proposals.
