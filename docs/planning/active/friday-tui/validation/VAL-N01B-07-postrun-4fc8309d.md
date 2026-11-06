# TUI-N01B-07 independent exact-source Ubuntu review

**Verdict:** `VERIFIED` for the bounded N01B-07 automated Ubuntu gate. This
does not establish installed TUI terminal UAT or full initiative acceptance.

**Reviewer and mode:** Fresh-context Codex validation subagent, read-only
post-run review on 2026-10-19. Exact model variant was unavailable. No
shared builder context, checkout edit or external mutation.

**Reviewed evidence:** Locally reviewed N01B-07 product candidate
`a196e95ab17120b6ee9d86d88ee9283485e1eb4f`, one authorized pushed
source `4a646dc73f98b87b65a2f8be95cde71b4bc27221`, local builder
[run report](N01B-07-ubuntu-run-39294625340.md) and status commit
`4fc8309d`. The reviewer read the controlling authority, directive,
board, local review and push-authorization audit, then independently
queried the live branch, run, job and logs.

Live [run 39294625340](https://github.com/CIChuck/agent-framework/actions/runs/39294625340)
and sole [job 118203828817](https://github.com/CIChuck/agent-framework/actions/runs/39294625340/job/118203828817)
were `completed/success`, triggered by `push`. Run head, job head,
log-printed source and checkout, and live
`origin/feature/friday-tui` all matched `4a646dc7`. Every listed job step
succeeded. Freshly fetched log archive, archive member and 1,133-line job
stream matched the builder's recorded SHA-256 values:
`52181eac51811e43258d0b0452e8532d8fccd37ebf5b6811d8e3dbe595ece23e`,
`48977b3c75e0439fefa173f0d66633bc34c648322558f78dfd4215f8b8c424ea`
and `d7e48f9c66d5741ddfb2bbd313ace7468c94954fa2d124f4246f2d33de8b1d26`.

The logs show 21 neutral-loader/Chat-facade, 393 Runtime, 853 Chat with
23 skips and one warning, and 155 unchanged `friday-cli` passes. Three
repeated Runtime MCP and four direct MCP checks passed. Thirteen wheels
built. Runtime wheel metadata excludes Chat/CLI; the isolated Runtime
install had 111 compatible packages without Chat/CLI, and the subsequent
Chat install had 130 compatible packages with matching configuration
identities.

All four N01B-07 product source and test blob IDs are identical at the
reviewed candidate, pushed source and local status commit. The post-run
commit changed exactly seven scoped planning/evidence paths and remained
local during review. Board validation passed for 34 tasks; dashboard
render check, duplicate-key-rejecting authority JSON parse, 409 links
across five changed Markdown files, `git diff --check` and clean tracked
worktree checks passed.

The Ubuntu installed-wheel probe tests configuration isolation. The
[independent local candidate review](VAL-N01B-07-prepush-a196e95a.md)
covers installed N01B-07 tool-record functions and Chat persistence. This
verdict closes the automated Linux gate only. The one non-force push
authority is consumed. Installed TUI terminal UAT, controlled
real-provider/tool testing, later transcript work, initiative acceptance
and further delivery remain open.
