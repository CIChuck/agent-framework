# REM-003 execution closeout: Python support minimum

Date: 2026-10-05. Approved scope: CD-001 A04/REM-003, maintainer "Make it happen."
Reviewed corrected candidate: 4c0afdb11b663e11ae08a927950dd3e968bbb566.
Delta base: 09fe69090f33ae9c047e2e101fe87727d52f9734.

The requested support migration is implemented: all18 projects require Python
>=3.13.4; Ruff targets py313, mypy targets3.13, .python-version selects3.13.
Current setup/contributor guides, scaffold and Docker FROM statements agree.
Existing3.13.10 meets the requirement. Users on older Python must select a
supported interpreter and recreate their environment through normal uv sync.
No Python source/test edit, dependency constraint change, interpreter download,
completed shared-environment synchronization, image execution or publication occurred.
The failed nested documentation-helper sync attempt and unchanged195 installed
distribution/RECORD hashes are recorded in the implementation/evidence reports.

Fresh [VAL-005](../validation/VAL-005/report.md) independently supports all
REM-003 migration-specific criteria, including154 supported interpreter,
platform and default/all-extra graph contexts with zero selected version/source
or dependency-edge drift, and1833 retained artifact records preserved. LiteLLM
remains1.100.1, PyPika0.48.9, grpcio1.67.1 on3.13 and1.76.0 on3.14.
Offline lock consistency, negative/positive patch-floor metadata checks,
changed-source mypy/syntax3.13, changed-file Ruff, focused135 tests, genuine
public Chat observer/Composite lifecycle on3.13.10 and governance/diff checks pass.
The three permitted synthetic localhost Chat fixture tests also pass.
This is not an exact3.13.4 runtime or Docker build claim.

The aggregate verdict remains CHANGES_REQUESTED because AC-06 mandatory root
lint and complete package/root suites remain nonzero and unwaived. Root Ruff
now has459 diagnostics versus337 at the prior3.10 target (122 additions from
retargeting existing code). No source suppression or opportunistic cleanup.
Remaining test/permission failure IDs and command outcomes are preserved in
VAL-005; narrower successes do not turn those commands into PASS.

The prior3.10 import failure remains true historical evidence. It is no longer
a current support obligation under the explicit maintainer-approved minimum
change. VAL-004's lock-selection finding is resolved in the corrected reviewed
candidate; prior reports are retained and superseded for decision purposes.
No baseline waiver, aggregate VERIFIED, task completion, maintainer acceptance,
push, merge or release is claimed. The initiative stays started/remediation with
validation_state changes_requested; next gate is remaining AC-06 lint/test scope.

Controller raw commands, scripts, preflight, lock/version/artifact inventory and
preservation results are retained in [builder evidence](REM-003-builder-evidence.tar.gz).
Only this initiative's board/dashboard hunks were staged; unrelated original
working-tree edits, user config, data and caches were preserved.
