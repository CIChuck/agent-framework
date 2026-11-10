# PILOT-001 contract and construction approval

Maintainer: Chuck Russell. Recorded: 2026-11-07T19:59:20+00:00.
Instruction: “I approved the documents, invoke the council after each deliverable.”

APPROVED together: [pilot contract](../pilot-command-contract.md), SHA-256
`e625123b8222262fb02b32aeadb2cae5c91d18ff573f04763b0af7ea3f22eb8c`, including the additive API and ownership boundary, and
[CD-CMD-PILOT-001](../directives/CD-CMD-PILOT-001-help-exit-clear.md), SHA-256
`b85be3a04035e1f8318cc6566f7767aad00355b61c49e2650c6327981fd2a982`. Final design/harness readiness was independently VERIFIED at
`dcb982cf9190306c2156c3a8050ac4d5469792be`.

Administrative approval baseline: `2655c3de043f24f3d6dfcd7e06f2bf980f14eacc`. Product/source baseline: `7b80ca01489a52608aafb54b626b74fbb36efbe3`.
Product/test/package/lock bytes match that baseline before construction.
Branch: `feature/command-retirement`; initiative remains started/local.
The immutable directive's draft labels describe pre-approval provenance; this
subsequent exact approval supplies construction authority.

## Deliverables and council checkpoints

1. D1 — neutral shared pilot specs/handlers and standalone tests (G1), after G0.
2. D2 — Chat adapter, dependency/lock edge, compatibility and lifecycle tests
   (G2–G3), after D1 council reconciliation.
3. D3 — full regression, source/assertion proof, documentation, clean artifacts
   and default installed proof (G4–G5), after D2 council reconciliation.

Freeze each deliverable locally and obtain a fresh read-only three-provider
council before advancing. Retain the existing independent score goal of at
least 9 and mandatory formal conformance requirements; scores do not override
findings. Bounded non-destructive remediation stays within the approved unit,
with fresh review after changed bytes and the two-cycle escalation rule.
D1 does not claim later Chat wiring or PILOT-03–10 completion. Council review
and implementation verification do not substitute for final maintainer
acceptance. No remaining command family, TUI unit or external delivery is
approved. Both original dirty example configurations remain excluded.
