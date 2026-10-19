# TUI-CI03 exact-source Ubuntu verification

**Run:** [Friday TUI Linux verification 39183895627](https://github.com/CIChuck/agent-framework/actions/runs/39183895627)
**Job:** `117842178499`, success, completed 2026-10-19 01:11:20 UTC.
**Source and checked-out SHA:** `315a30e441a1fed5f4e2fa553a66e563aabb4972`.
**Environment:** Ubuntu 24.04.5 LTS, Python 3.13.12, uv 0.11.3, locked
`mcp` 2.3.0.

The pushed SHA matches the [independently VERIFIED pre-push
candidate](VAL-TUI-CI03-preflight-315a30e4.md). The source and checkout SHA
were printed in the job log and the GitHub run reports the same head SHA.
Every required job step concluded successfully:

| Ubuntu gate | Result |
| --- | --- |
| Neutral loader and Chat facade | 21 passed |
| Full Runtime suite | 334 passed |
| Previously failing Runtime auto/modern stdio case, repeated | 1 passed on each of 3 runs |
| Official SDK direct stdio explicit-modern control | 1 passed |
| Previously failing official SDK direct stdio `auto`, repeated | 1 passed on each of 3 runs |
| Chat help output, plain and colored | Both exit code 0 |
| Full Chat suite | 827 passed, 23 skipped, 1 warning |
| Unchanged `friday-cli` suite | 155 passed |
| Runtime and Chat dependency wheels | 13 wheels built |
| Runtime wheel metadata | Direct `pydantic` and `pyyaml`; no frontend dependency |
| Installed Runtime isolation and Chat facade | `uv pip check` and both isolated import/identity assertions passed |

The full MCP package suite passed locally (2,682 tests); this Ubuntu workflow
does not run that whole package suite. The Ubuntu result resolves the red
Runtime and direct MCP checks from
[CI02 run 39181571549](TUI-CI02-ubuntu-run-39181571549.md) on the new exact
source. A fresh final independent review of the run and packet reconciliation
is pending. The job verifies infrastructure and regressions for TUI
development; it does not constitute an implemented TUI, installed terminal
UAT, maintainer acceptance, PR, merge or release.
