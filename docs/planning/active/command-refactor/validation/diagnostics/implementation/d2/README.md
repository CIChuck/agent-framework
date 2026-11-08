# DIAG-001 D2 — round1 CHANGES_REQUESTED; correction cycle1

Execution phase: remediation. Validation state: changes_requested.
[Raw council and reconciliation](council-round1.json) identify two mandatory
findings. The [bounded correction](../../../../remediation/REM-CMD-DIAG-D2-001-context-format-and-test-isolation.md)
requires once-only cached context formatting and private-cwd fallback tests.
Original evidence is retained as historical and does not close either finding.

The unsafe mutation lane created/overwrote ignored repository
`exports/friday_context.txt` and `exports/friday_prompt.txt` with synthetic bytes.
Both currently have SHA256 `3673014e72b67383be302485694555a57ad393afdebaed6ded110a775bd0556d`.
Builder-created files and subsequent observed rewrites are disclosed; later
attribution beyond the observed windows is not asserted. They remain untouched;
only the maintainer may authorize cleanup. Final correction evidence will bind
before/after metadata and hashes as well as tracked/dirty state.

## Historical round1 implementation freeze

# DIAG-001 D2 — Chat diagnostics integration

Execution phase: validation. Validation state: in_review (council round 1).
D1 is independently verified. D3 candidate artifacts and installed proof, human
UAT and bounded DIAG acceptance remain pending. Delivery remains local.

The [exact approval](../../../../approval/diagnostics.md) binds the frozen
[contract](../../../../diagnostics-command-contract.md) and
[directive](../../../../directives/CD-CMD-DIAG-001-context-diagnostics.md).
This deliverable changes only the six permitted package paths: the new typed
Chat diagnostics module, six registry wrappers/projected entries, package-local
fixture and tests, and the two package READMEs. D1 source/tests remain frozen.

The shared handlers own exact flags, character-count/export order and retrieval
availability/usage/await decisions. Chat retains dynamic host projection,
English rendering, public memory/telemetry ownership and fixed UTF-8 exports.
The three moved helper definitions are AST-identical; the other 33 tuple entries,
registration/parser/dispatch/admission and handler map remain unchanged.

All required assertions run under the exact DG-T08–14 names. The seven nodes
collect 41 cases (1 / 6 / 11 / 12 / 9 / 1 / 1). DG-T08 additionally executes all
72 frozen diagnostics scenarios, 25 SESSION scenarios and 196 accepted pilot
observations. The fixture is exact preparation bytes. Pilot expected values are
pinned by five independent canonical JSON digests in the new test file; new tests
read only package-local fixtures. The macOS `/var` to `/private/var` export-root
alias is canonicalized in the in-process fixture comparison, without changing
relative paths, written bytes, events or exception expectations.

The diagnostic result is **68 exact rows + four approved cache refusals**.
The frozen comparer prints its historical generic success sentence even when
its explicitly authorized refusal mode is used; it does not establish 72
unchanged successes. Truthy non-string cached context/prompt values now raise
TypeError; falsy caches retain fallback. Direct non-string args retain the
approved shared-request refusal before factory/context access.

[Evidence](evidence.json), [coverage map](test-coverage-map.json),
[preservation](preservation.json) and [before inventory](before-inventory.json)
retain exact commands, exits, source identity and raw-file hashes. Source tests
and captures do not establish installed candidate behavior. The old D0/D1 build
receipts remain baseline machinery only. D3 owes its own S4/S5-equivalent DIAG
full regression, artifacts/replay and installed aggregate proof.

The DIAG standalone nodes require the pinned guard. Create a fresh private lane
using `validation/pilot/harness/prepare.py --wheelhouse SUPPLIED`, then invoke
its `pilot_run.py LABEL python -B -m pytest ...`. Labels and capture output paths
must differ. Use explicit private mypy cache paths; every supplied builder lane
is read-only to reviewers. Plain pytest does not supply the required standalone
guard. The earlier D1 review's equivalent exact-type mutant is not a defect.

Known root Ruff534, the sole root Chat/CLI test_display collection conflict and
legacy registry formatting remain failed and unwaived. No whole-repository-green,
D3, acceptance, later-family, full-refactor, TUI or delivery claim is made here.
