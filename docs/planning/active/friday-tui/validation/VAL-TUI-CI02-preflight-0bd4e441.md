# TUI-CI02 first candidate pre-push review

**Verdict:** CHANGES_REQUESTED on candidate
`0bd4e4412c661b0bbdf99553ad7b12eb5cb8db8c` against construction base
`fdbf215d952e885f884ba14afcb96810f056d620`.

The fresh-context, read-only reviewer found **CI02-01 (medium)**: the
ANSI-normalized help test asserted only three options, while the CLI declares
six. The approved CI02-B directive requires coverage of every declared option.
The bounded correction is to assert `--replay`, `--replay-delay`, and
`--runtime` in the existing plain/GitHub Actions/forced-color cases, then
rerun focused and full Chat checks and obtain a new independent review.

The reviewer found no other pre-push scope or behavior finding. Authorized
paths, board, dashboard, lock, workflow syntax, Runtime, Chat and unchanged
`friday-cli` local checks passed. The synthetic MCP fixture timeout remains
three seconds. This review does not close the Ubuntu diagnosis, full Linux
gate, or final terminal UAT.
