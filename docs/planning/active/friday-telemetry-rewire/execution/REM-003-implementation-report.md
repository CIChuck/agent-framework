# REM-003 Python support migration implementation report

Date: 2026-10-05. Maintainer approved "Make it happen."; CD-001 A04/REM-003.
Delta base: 09fe69090f33ae9c047e2e101fe87727d52f9734. Fresh CDR-006 READY at
816e64f35d58b4b1334388dd3b5b6fb312534176 preceded product metadata execution.

All 18 project declarations now require Python >=3.13.4; root/package Ruff
uses py313, mypy uses 3.13, and .python-version selects the 3.13 minor series.
Root README, active setup/contributor guides, scaffold and Docker FROM examples
match the new minimum. Generated public web artifacts are excluded from this
source change and await a normal documentation build; no website publication
or Docker image build/pull/run occurred.

The cache-only first lock attempt lacked LiteLLM metadata. Credential-free
public PyPI resolution without --upgrade succeeded but selected PyPika0.51.1;
that result was rejected. The complete original PyPika0.48.9 package/artifact
block (including hashes) was restored before offline regeneration and check.
Both offline uv lock and uv lock --check then passed. Graph comparison finds
201 packages versus208 at delta base: only7 unreachable old-Python package
versions removed; zero newly selected dependency versions/sources. Initial VAL-004 nevertheless
identified supported3.13 grpcio selection drift hidden by set-membership checks.
The corrected candidate restores grpcio1.67.1 for3.13 and1.76.0 for3.14; full
reachable graph comparisons across24 supported Python/platform/architecture
contexts now preserve every selected version/source and1833 artifact URL/hashes. All manifest
dependency constraints remain byte-equivalent as TOML data. LiteLLM stays1.100.1.
No shared environment synchronization, source build or interpreter download.

SpecifierSet checks reject Python3.10/3.11/3.12 and3.13.0-3.13.3, accept3.13.4
and installed3.13.10. These establish metadata semantics, not an exact-floor
runtime run. Actual supported-runtime execution uses3.13.10. Baseline focused
six-module tests pass135; genuine Chat observer/Composite lifecycle passes.
Broader package/root suites remain nonzero and are being compared against the
stable candidate. Static/runtime/governance results and independent review will
be appended in the closeout without altering controlling authority.

No Python source/test body changed. Historical3.10 failures remain intact and
are superseded only as current support obligations; no baseline gate waiver,
aggregate VERIFIED, completion, acceptance or delivery is claimed. Raw commands,
logs, metadata inventory, exact source-resolution/preflight and preservation
records are in /private/tmp/telem-01/REM-003 and will be archived with closeout.

## First frozen candidate review and bounded correction

[VAL-004](../validation/VAL-004/report.md) reviewed285254b. F01 requested exact
supported-runtime lock-selection preservation; only uv.lock was mechanically
corrected within REM-003 scope. R3-03 now checks reachable package selections
as well as set membership. F02 retains unwaived aggregate gates: root Ruff459
versus337 (122 target-driven additions), package724 passed/1 failed/3 errors/5
skipped, root2699 passed/16 failed/11 errors/1 skipped. Failure/error IDs exactly
match baseline. Focused135, changed Ruff, mypy/syntax3.13, genuine public observer
Composite lifecycle, lock consistency, board/docs and diff checks pass.
The original-workspace docs helper attempted nested sync without inherited
UV_NO_SYNC; failed before installation. Corrected no-sync/offline docs passes,
and all195 distribution versions/RECORD hashes plus pyvenv.cfg match the prior
inventory. No completed environment synchronization or dependency install.
Fresh independent review of the corrected stable candidate is required; prior
VAL-004 remains historical and is superseded for subsequent decision purposes.
