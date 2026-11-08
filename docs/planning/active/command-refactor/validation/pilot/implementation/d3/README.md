# PILOT-001 D3 — regression and installed candidate proof

Execution phase: `closeout`. Validation state: `verified` (PILOT-001 D1-D3).
Claude Opus 5.5 and GPT-6.1 Sol both VERIFIED candidate `eb216421`, each 9.6/10.
Both named findings are independently closed and no mandatory findings remain.
See [reconciled verification](verified-report.md) and [exact reports](council-round2.json).
Pilot acceptance and delivery remain pending.

[Current evidence](remediation-evidence.json) records 1,228 Chat, 217
Commands/cohort and 155 CLI tests passing again, all 196 source observations
unchanged, and two clean offline artifact trials from Git revision `70ebef3a`.
All 154 artifact hashes and the profile agree across replay. Default Chat stays
at 138 distributions; neutral stays at 1. The current [preservation](preservation-round2.json)
proves 784 package/test/root/script files unchanged from the round-one candidate.
Only the authorized neutral README status sentence differs among packages.

The corrected probe enumerates exact installed file AND directory sets, checks
bytes against Git/wheel and refuses symlinks/special members. Dist-info metadata
is outside these source/data trees; bytecode generation is disabled and no extra
package files/cache directories are permitted. Five installed-member controls
(source, data, empty directory, bytecode, symlink) are refused in each mode.
Both file and every package search path are now validated; two mixed-origin
controls are refused in each mode. Together with the original six controls,
all 13 refusal controls pass in normal and optimized execution. All four clean
neutral/Chat installed lanes pass. Entry-point help checks its child origins;
required nonsecret environment and bootstrap hashes are recorded.

The [finding map](council-remediation-round1.json) distinguishes implemented
corrections, addressed advisories and deferred optional improvements. The
current independent reports close both mandatory findings. The [round-one reports](council-round1.json)
and original evidence below remain historical, immutable records.

## Historical round-one builder report

The following report describes the round-one candidate and its passing clean
installations. Its earlier inventory/origin assurances are superseded by the
corrected probe; current independent closure is recorded above.

[Evidence](evidence.json) embeds hash-pinned command/probe/artifact receipts with
explicit roles. Full after-suites pass: **1,228 Chat**, **217 Commands/cohort**,
**155 CLI**. Source capture still matches all **196** frozen observations.
[Preservation](preservation.json) proves 785 package/test/root-metadata/script
files unchanged from D3's start, including all 59 Chat test/fixture files and
2,347 assertions. D3 adds no product behavior or dependency changes.

Two final cold/offline artifact trials build 13 required workspace distributions
from their own verified private Git archives, verify 125 locked third-party
inputs and PyPika lineage, compile hash-pinned profiles and install two isolated
environments. Every final artifact/profile hash agrees across replay. An extra
untracked source file is refused before any build or fetch.

The [installed probe](../../installed_probe.py) runs outside the checkout with
`-I`, explicitly verifies/loads the pinned guard, and uses installed packages.
Neutral closure is exactly Commands alone, with zero dependencies or executable.
Default Chat closure is 138 distributions, with the required Commands edge and
successful finance/tools imports, no diagnostic extras or legacy executable.
[Profile lineage](profile-lineage.json) proves the only change from the locked
137-member D1 baseline is Commands. It separately explains the older assembled
129-member profile; that historical count is not a resolver target.

For both Chat and Commands, the probe compares complete installed/wheel/Git
source and data inventories and bytes (66 files), complete sdist/Git project
inventories (141 files), approved generated metadata/license and dependency
records. It rejects duplicates, unexpected files or non-file sdist entries.
All loaded Friday file/namespace origins must be inside the selected venv.
Neutral standalone execution, aliases, snapshot/sort/focus behavior and host
import isolation pass. Installed Chat matches all 41 metadata rows, 62 help
outputs and 29 dispatch fixtures. Real shared-handler spies, canonical request
identity and injected distinct outcomes prove Chat consumes shared results.
Custom handlers/context catalogs, falsy detail and direct exit/clear purity pass.
The installed entry point loads and prints help with the guard active.
Normal and optimized installed lanes both pass; six separate origin/archive
refusal controls pass in each mode. Artifact checker validates both wheel/sdist
pairs. All package imports/behaviors use synthetic guarded execution.

| Obligation | Evidence |
| --- | --- |
| PILOT-01/02 | Full 217 neutral/cohort suite; installed standalone neutral aliases, immutable map/snapshot, sorted and focused help. D1 council remains pinned history. |
| PILOT-03/04 | Frozen 196-observation source comparison plus installed 41 metadata / 62 help / 29 dispatch checks and real canonical shared invocation. |
| PILOT-05/06 | D2's 190 cases plus installed context/custom handlers, falsy detail and outcome injection; approved amendment remains explicit. |
| PILOT-07/08 | Full Chat app/display/PTY tests, installed direct exit/clear tripwires and exact dispatch effects; app source unchanged. |
| PILOT-09 | All three full suites and byte/assertion preservation; nine retirement negatives remain unchanged. |
| PILOT-10 | Final clean builds/replay; default closure/pip checks, exact dependency/source/member/entry-point/origin proof in both isolated lanes. |

Focused lint, 12-file format and seven-source-file mypy pass. Root Ruff still
fails at 534 findings; root pytest fails on the existing test_display collection
conflict. Legacy registry format remains failing. These are unwaived baseline
gates, not hidden successes. Initial draft/control mistakes and initial build
trials are labeled in evidence; only final current receipts support this gate.

No P0/P1 or full-refactor closure is claimed. Later command families, TUI,
maintainer acceptance, push/PR/merge/release remain separate gates.
