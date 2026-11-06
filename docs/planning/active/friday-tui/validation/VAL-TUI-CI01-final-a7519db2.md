# TUI-CI01 independent post-run review

**Outcome:** `CHANGES_REQUESTED` on 2026-10-18 for committed candidate
`a7519db2e679449390aea0afc7e71be153a34f6b`. The workflow is deployed,
but the required full Linux test gate is not met. No TUI-CI01 `VERIFIED`,
completion, acceptance, terminal UAT, PR or merge is claimed.

**Reviewer and mode:** Fresh-context, read-only subagent
`/root/tui_ci01_final_review`; model/version was not exposed to the
controller. The reviewer made no repository edits or external changes.

**Inputs and revisions:** `AGENTS.md`, the repository engineering,
development lifecycle and independent validation policies,
`authority.json`, the approved `CD-TUI-CI01-linux-actions.md`, board and
dashboard, packet index, execution log, workflow, and fourth Ubuntu run
record. Reviewed full diff `d69c1d72fb841e4b3e51683ef16d7dcd4eac1f00`
to `a7519db2`, including the evidence-only delta `94f96814..a7519db2`.
The [Ubuntu run](https://github.com/CIChuck/agent-framework/actions/runs/39175010441)
tested source and checkout `94f968143ee9890cf761b0e3be9004735e5a6aaf`.
The reviewer's direct GitHub retrieval was unavailable, but the saved
Actions job log independently supports the recorded failed checks; the
controller separately inspected the run status and job conclusions.

## Findings

1. **CI01-07 — High, Runtime MCP startup.** Full Runtime reported 333
   passed/one failed; the failed required `auto`/modern stdio case also
   failed alone. The error is `ToolProviderLoadError: Required MCP server
   unavailable`. The underlying lifecycle outcome remains unobserved. A
   separately approved directive must authorize Linux diagnosis, capture
   that outcome, and define any Runtime/MCP source or test correction. The
   focused case and full Runtime suite must then pass on Ubuntu. Record
   the diagnosis and regression result in this packet.
2. **CI01-08 — High, Chat `/reorganize` on Linux.** Four full-Chat cases
   received `MaintenancePlatformError` rather than expected command
   results. The production lease guard rejects non-Darwin platforms. A
   separate directive must choose the supported Linux behavior and test
   expectations, then run focused Linux coverage and the full Chat suite
   while preserving macOS and unchanged `friday-cli` behavior. Document
   the compatibility decision in the packet.
3. **CI01-09 — Medium, Chat help assertion.** `test_cli_help` exited
   successfully, but its rendered output lacked the asserted literal
   `--version`; the option exists in Chat CLI source. Capture the complete
   Linux help output and terminal/test settings, then resolve the rendering
   or assertion discrepancy under the separate directive. Run the focused
   case and full Chat suite. This evidence does not show that invoking
   `--version` is broken.
4. **CI01-10 — Medium, exact-candidate green evidence.** The fourth run
   tested `94f96814`, while this reviewed candidate includes a subsequent
   planning/evidence-only commit. Its workflow is unchanged, but no green
   full Ubuntu run exists for the reviewed commit. After authorized fixes,
   freeze the resulting candidate, run the full workflow on its exact
   source/checkout SHA, record both SHAs and the run URL, and obtain fresh
   independent review. Update board, dashboard and authority evidence.

**Passed checks and limits:** The reviewer found only approved workflow and
planning/evidence paths in the CI01 diff, with no product source, tests,
metadata or lockfile changes. The workflow uses pinned actions,
`ubuntu-24.04`, `contents: read`, no secrets and no failure suppression.
Board validation passed for 34 tasks, dashboard check and diff check passed,
and workflow YAML, ten Bash blocks and four embedded Python blocks parsed.
The Ubuntu log confirms 21 focused passes, 155 unchanged CLI passes, 13
wheel builds with hashes, and passing Runtime wheel metadata and installed
isolation checks. None supersedes the failing Runtime/Chat gates.

**Exit gate:** Keep CI01 `started` with validation `changes_requested`.
Draft and obtain maintainer approval for a separately scoped Runtime/MCP and
Chat Linux remediation directive before protected source or test edits; then
obtain a green exact-candidate Ubuntu run and fresh independent review.
