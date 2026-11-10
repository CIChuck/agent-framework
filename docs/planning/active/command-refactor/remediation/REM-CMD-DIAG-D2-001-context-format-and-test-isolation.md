# REM-CMD-DIAG-D2-001 — context formatting and test isolation

Authority: existing exact [DIAG approval](../approval/diagnostics.md), DG-01/03/06
and [CD-CMD-DIAG-001](../directives/CD-CMD-DIAG-001-context-diagnostics.md), with
bounded conformance remediation under the independent-validation policy.
Round1 candidate: `95b58d9169abe143e5aa537b8ad589309167dddf`.
[Raw council/reconciliation](../validation/diagnostics/implementation/d2/council-round1.json).
This is correction cycle1, not a contract/schema amendment or new feature.

## Findings, exactly once

1. **DIAG-D2-ASTRA-001 (medium):** `/context --debug --file` formats accepted
   cached string subclasses once for the export and again for the output. A
   raising/stateful formatter demonstrates a success-to-exception regression.
   Retain the already rendered context body locally for that single invocation,
   matched to the exact typed text identity and character count. Reuse it in the
   same pure context renderer when adapting matching data; a different injected
   outcome must still be consumed. Keep shared flags/export ordering, original
   typed data, neutral APIs, host ownership and write/failure semantics unchanged.
   No global cache, text parsing, source coercion or alternate command engine.
   Add DG-T10/DG-T11 regression assertions for accepted custom formatters,
   `--debug --file`/repeated/reordered flags, file/output equality for the debug
   body, once-only formatting and exception/partial-write behavior. Characterize
   non-debug file behavior against legacy rather than inventing new semantics.
2. **VAL-001 (Claude, medium):** DG-T08 fallback export-failure scenarios depend
   on a patch to prevent writing repository `./exports`; a bypassing mutant
   escapes that patch. Put the capture inside a private pytest working directory
   before any scenario. Do not edit frozen programs, expected rows or fixture.
   Disclose the two existing ignored synthetic export writes in evidence/log,
   inventory hashes/metadata, and preserve them. Cleanup belongs to the maintainer.

## Exact scope and verification

Only new Chat `commands/diagnostics.py` and
`tests_chat/test_command_diagnostics.py` may change outside planning documents.
D1 source/models/API/tests/fixture, registry/wrappers/metadata/helper definitions,
all old tests, dependency/lock/config bytes and accepted authority remain frozen.
The host-only rendered-body snapshot does not cross the neutral boundary or
change any approved schema/signature. Pure rendering still invokes no services.

Show new named-node assertions fail against the unfixed candidate and pass on
the correction. Run the raising formatter against clean base/current sources.
Rerun all seven named nodes and Commands/D2/D3 fast gates (41/478/538/166 unless
additional explicit cases require arithmetic reconciliation), focused Ruff,
new-file format, eleven-source mypy, preservation/AST audit and source captures.
Rerun the declared mutation sweep with an unchanged control and actual call-phase
assertion witnesses; in particular, launch legacy-engine and ignored-outcome
from repository cwd while verifying no repository `exports/` metadata/bytes
change. All resulting exports must remain in the private pytest tree. Canonical
module roots/hashes and final test bytes must match before/session-finish/after.
No setup error earns rejection credit.

Preserve round1 raw reports, original evidence and raw scratch. Label previously
undisclosed ignored side effects and superseded sweeps honestly. Keep the
execution log append-only, board/dashboard/packet status in agreement, and
freeze a new candidate for fresh Sol/Astra/Claude delta followed by full bounded
D2 aggregate review. D3 installed proof, UAT and human acceptance remain pending.
No additional D1 repair, advisory cleanup, delivery, later-family or TUI work.
