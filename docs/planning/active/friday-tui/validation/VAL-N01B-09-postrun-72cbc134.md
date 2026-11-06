# TUI-N01B-09 independent exact-source Ubuntu review

**Verdict:** `VERIFIED` for the bounded N01B-09 automated Ubuntu gate. This
does not establish installed TUI terminal UAT or full initiative acceptance.

**Reviewer and mode:** Fresh-context Codex validation subagent, read-only
post-run review on 2026-10-19. Exact model variant was unavailable. No
shared builder context, checkout edit or external mutation.

**Reviewed evidence:** Independently reviewed local product candidate
`cda7419d7fe147a7c5d8c6509af7ad8025c9b830`, authorized pushed source
`371c1387c8932002be858b1d7166e07ccace57ba`, builder [run
report](N01B-09-ubuntu-run-39307201390.md) and frozen status commit
`72cbc134`. The review range was `371c1387..72cbc134`. The reviewer checked
`AGENTS.md`, controlling policy, TUI authority and [exact
directive](../directives/CD-TUI-N01B-09-neutral-transcript-session-ensure.md),
board, local candidate and final-status reviews, and the one-push record.
The authority JSON, directive, board and builder run-report SHA-256 values
provided to the reviewer were respectively `ee3b88cc88f5bf71a1ec8a3c9b682e66f8f83a57ea7efcbd8ac3436fde0246d0`,
`61bd71ab34cd2f461ee68a2f2ea3a7fc2852d10d56cb950818389ff012fa75e3`,
`b2c64be18c3a1aac3844dc9681b2b73f1778845ebbb15f6ab0f7bd2540a4ced7`
and `45fcd778c663d6fb18ce4f2fe8d5624a9cb2c6d7f1a3c215c43175dbe6e7f09d`.

Live [run 39307201390](https://github.com/CIChuck/agent-framework/actions/runs/39307201390)
and sole [job 118247251923](https://github.com/CIChuck/agent-framework/actions/runs/39307201390/job/118247251923)
were `completed/success`. Live remote head, run head, job head and logged
source/checkout matched `371c1387`. Independently fetched live run and job
logs matched the two saved 171,707-byte logs, both SHA-256
`233519c5ec719289730f1f8138bcf51a764572013c35552f1dd2d2607ff6ad03`.

The logs show 21 neutral loader/Chat facade tests, 414 Runtime tests,
three synthetic Runtime MCP checks, modern plus three direct MCP checks,
872 Chat tests with 23 skips and one unchanged warning, and 155 unchanged
`friday-cli` tests passed. Thirteen selected wheels built. Runtime wheel
metadata has no Chat/CLI dependency. The isolated Runtime and subsequent
Chat environments passed package compatibility checks with 111 and 130
packages respectively.

All four N01B-09 product source/test blob IDs are identical across first
candidate `36028fbf`, reviewed candidate `cda7419d`, pushed source
`371c1387` and reviewed status commit `72cbc134`. The post-run commit
changed eight scoped planning/evidence paths and remained local during
review. Board validation passed for 34 tasks; the generated dashboard was
current. Duplicate-key-rejecting authority JSON parse, 481 changed-document
local links, whitespace and clean-worktree checks passed. The repository-wide
documentation checker still reports six unchanged telemetry report links
outside this diff.

The Ubuntu installed-wheel probe tests configuration isolation; new
session-ensure behavior is exercised by the Runtime/Chat suites and direct
installed helper evidence from the [independent local candidate
review](VAL-N01B-09-prepush-cda7419d.md). This verdict closes the N01B-09
automated Linux gate only. The one non-force push authority is consumed.
Installed TUI terminal UAT, later product units, initiative acceptance,
PR, merge and release remain open.
