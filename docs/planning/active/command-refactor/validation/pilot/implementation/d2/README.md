# PILOT-001 D2 — Chat integration and lifecycle

Execution phase: `validation`. Validation state: `verified` (D2 only).
[Round-two council](council-round2.json): Claude 9.7, Sol 9.6, Gemini 9.8; all
VERIFIED, metadata finding closed. Approved D3 is now in progress.
The next paragraph records the pre-review builder checkpoint historically.
The [exact metadata amendment](../../../../approval/pilot-metadata-compatibility.md)
is approved. Its [correction evidence](remediation-evidence.json) records G1 217,
G2 428, G3 246, 190 cases in the new test file and all 196 frozen observations.
Fresh D2 council round2 precedes D3. The [first council](council-round1.json)
remains historical CHANGES_REQUESTED evidence for the uncorrected candidate.

The following original builder results describe the pre-correction candidate;
current correction results above and in remediation-evidence.json supersede
its counts. Original receipts and baseline captures remain unchanged. The exact pilot approval
covers construction; this builder report grants no acceptance or delivery.

Chat now projects shared help/exit/cls definitions into its public metadata,
provides exact-key help catalogs and delegates each parsed invocation once to a
shared typed handler. Chat retains rendering, parser, other handlers, terminal
effects and lifecycle. The exact required Commands dependency and workspace
source are recorded; the lock adds only Chat's dependency/requires-dist edges.

[Evidence](evidence.json) embeds hash-pinned command receipts and roles. G2:
**400 passed**; G3: **218 passed**, including existing PTY and app lifecycle tests.
The 162 new tests prove shared delegation, exact canonical requests, projection,
custom/context registries, permissive metadata, unsupported outcomes, error and
cancellation propagation, and real-app effect/output/cleanup order.

[Clean candidate observations](observations-after.json) match the independent
frozen baseline exactly: 41 metadata, 62 help, 29 dispatch, 61 custom and three
lifecycle cases. They came from source commit `99f19f69`, not a regenerated
expected baseline. Later evidence/status commits contain no product changes.

[Source/assertion disposition](source-disposition.json) compares all 58 prior
Chat test files byte for byte (858 definitions including classes; 2,262 asserts),
all retained registry definitions, 38 untouched default specs and other package
source. The three moved renderer bodies are AST-identical. The
[before inventory](before-inventory.json) preserves the initial owned inputs.
[Lock disposition](lock-disposition.json) records no version or other-package
changes. Both dirty example configurations remain protected and excluded.

Affected Ruff, explicit seven-source-file mypy and new adapter/test/session
format checks pass. Root Ruff remains failed at 534 findings; root pytest fails
on the existing Chat/CLI `test_display` import-file mismatch. Registry format
fails in both lanes. These are unwaived baseline failures. The first new-test
normalization expectation failed and was corrected to the frozen behavior;
its receipt remains labeled historical. No source or oracle repair hid it.

D3 still owes full after-regression and candidate artifact/default-install proof
(G4/G5). Earlier G0 builds/install receipts are baseline controls. No complete
PILOT-09/10, P0/P1, whole-pilot acceptance, push, PR, merge or release is claimed.
