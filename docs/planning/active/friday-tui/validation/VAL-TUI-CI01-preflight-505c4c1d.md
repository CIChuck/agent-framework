# TUI-CI01 finance-rerun packet independent preflight

**Outcome:** `VERIFIED` for preflight only on 2026-10-18 for candidate
`505c4c1d0c64e7c4cc73fb62a4889bf8746160ce`. No findings. Linux
verification and final work-unit review remained open.

**Reviewer:** fresh-context, read-only agent
`/root/tui_ci01_packet_review_505c4c1d` (model/version not exposed to the
controller). No repository edits or external calls.

**Authority and revision:** TUI-CI01 base `d69c1d72`; full diff
`d69c1d72..505c4c1d`; packet remediation delta
`89a875ac..505c4c1d`. At the reviewed revision, SHA-256 hashes were:

- `docs/planning/board.yaml`: `793d22a42dd74a5048964c3d617358a024355143d97b3a368366c35a734e5417`
- `authority.json`: `00a00588f3d7fcc8a9e13aad2691d553981c54782e03aefcf2827154469ea18b`
- `CD-TUI-CI01-linux-actions.md`: `707cf689653abc877262d0f0dbbbf83c8b7ca48b72eb4b48110d99b4f7ef3728`
- TUI packet `README.md`: `7456e3cdfa789580e5bd9d88eb4cd207c0f26f027335369612e2d1aeb1985478`

The clean, stable candidate's full diff remained in CI01 scope; its latest
delta changed only seven named planning/evidence paths and left the workflow
unchanged. The packet index and current execution-log header agreed that
validation awaited Ubuntu; the board named the full run, MCP observation and
independent work-unit review. Board validation passed for 34 tasks, as did
dashboard and diff checks, offline lock and exact finance/MCP dependency
selection, workflow YAML, pinned actions, nine Bash scripts and four Python
blocks. Finance's wheel remained outside the initial isolated Runtime
environment.

The prior Ubuntu run tested `7a41004a` and failed. The verdict did not
establish Linux verification for `505c4c1d`; the complete run and final
independent review remained mandatory.
