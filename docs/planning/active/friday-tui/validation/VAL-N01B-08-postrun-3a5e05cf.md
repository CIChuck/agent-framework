# TUI-N01B-08 independent exact-source Ubuntu review

**Verdict:** `VERIFIED` for the bounded N01B-08 automated Ubuntu gate. This
does not establish installed TUI terminal UAT or full initiative acceptance.

**Reviewer and mode:** Fresh-context Codex validation subagent, read-only
post-run review on 2026-10-19. Exact model variant was unavailable. No
shared builder context, checkout edit or external mutation.

**Reviewed evidence:** Locally reviewed N01B-08 product candidate
`8ac249d3ad694d886a7b11acf69d2ec2cc817d51`, one authorized pushed
source `c4a5faa6a65d7f6b2259c684336a9a816d481b33`, local builder
[run report](N01B-08-ubuntu-run-39301138733.md) and status commit
`3a5e05cf`. The reviewer checked the controlling authority, directive,
board, local review and push-authorization audit, then independently
queried the live branch, run and job and checked the saved logs.

Live [run 39301138733](https://github.com/CIChuck/agent-framework/actions/runs/39301138733)
and sole [job 118226328033](https://github.com/CIChuck/agent-framework/actions/runs/39301138733/job/118226328033)
were `completed/success`, triggered by `push`. Run head, job head,
log-printed source and checkout, and live
`origin/feature/friday-tui` all matched `c4a5faa6`. Every listed job step
succeeded. The saved log archive, archive member and 1,135-line job stream
matched the builder's recorded SHA-256 values:
`440cd41b770b7d2b03db4a93a0599d0112aeef9da7dd683e6b4c0f8f8ef54ee9`,
`b88bd5b21bd4929ba95346ae51bf03e7e78fe67fbc74ce3d9e2313dad00916ca`
and `ab246c4e6ab9c91ff1298883f6a79d3a37821185d4af651a39f2f3d9657d9e37`.

The logs show 21 neutral-loader/Chat-facade, 402 Runtime, 862 Chat with
23 skips and one warning, and 155 unchanged `friday-cli` passes. Three
repeated Runtime MCP and four direct MCP checks passed. Thirteen wheels
built. Runtime wheel metadata excludes Chat/CLI; the isolated Runtime
install had 111 compatible packages without Chat/CLI, and the subsequent
Chat install had 130 compatible packages with matching configuration
identities.

All four N01B-08 product source and test blob IDs are identical at the
reviewed candidate, pushed source and local status commit. The post-run
commit changed exactly seven scoped planning/evidence paths and remained
local during review. Board validation passed for 34 tasks; dashboard
render check, duplicate-key-rejecting authority JSON parse, local links in
all five changed Markdown files, `git diff --check` and clean worktree
checks passed. The repository-wide documentation check still finds six
preexisting broken absolute `/private/tmp/telem-01` links in an unchanged
telemetry report; no changed-document link failed.

The Ubuntu installed-wheel probe tests configuration isolation. The
[independent local candidate review](VAL-N01B-08-prepush-8ac249d3.md)
covers installed N01B-08 transcript write effects and Chat delegation.
This verdict closes the automated Linux gate only. The one non-force
push authority is consumed. Installed TUI terminal UAT, controlled
real-provider/tool testing, later transcript work, initiative acceptance
and further delivery remain open.
