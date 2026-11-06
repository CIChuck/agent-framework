# TUI-N01B-05 independent exact-source Ubuntu review

**Verdict:** `VERIFIED` for the bounded N01B-05 automated exact-source Ubuntu
gate. No finding requires a source change.

**Reviewer and mode:** Fresh-context Codex validation subagent, exact model
version unavailable, read-only post-run review on 2026-10-19. The reviewer did
not edit, commit or push.

**Reviewed post-run candidate:** Clean `feature/friday-tui` at
`3d5695d853bfed3152ff40a4da26e81590834d62`, one local evidence-only
commit ahead of pushed `37298e48e90c8fd6d61b831895693c9e6a496975`.
The independently reviewed N01B-05 product candidate is
`c773f2726828b62988428ed3652ca08430b9e346`.

The reviewer read the repository authority and independent-validation rules,
the [N01B-05 directive](../directives/CD-TUI-N01B-05-neutral-single-file-export-effects.md),
[local review](VAL-N01B-05-prepush-c773f272.md), [pre-push authority
review](VAL-N01B-05-prepush-authority-06abf49b.md), [Ubuntu run
report](N01B-05-ubuntu-run-39278047819.md), board, packet and post-run diff.
The live [GitHub run](https://github.com/CIChuck/agent-framework/actions/runs/39278047819)
and [job](https://github.com/CIChuck/agent-framework/actions/runs/39278047819/job/118147042792)
both reported `completed/success` for the `push` event on the full
`37298e48` SHA. The live remote branch also pointed to that SHA. Streaming the
live job log reproduced the saved log SHA-256
`52643484d13170ef46f281cb0d0e439ca4794902c7a7fe6d2ab380c36d6d701c`;
its source and checkout SHAs match. The job completed at
2026-10-19 15:30:49 UTC.

The log records Ubuntu 24.04.5 LTS and Python 3.13.12, 21 loader/facade
passes, 377 Runtime passes, 844 Chat passes with 23 skips and one existing
deprecation warning, and 155 unchanged `friday-cli` passes. Repeated MCP
checks passed. Thirteen wheels built; Runtime metadata excluded Chat/CLI
dependencies. Installed configuration checks passed with 111 Runtime-only
packages and 130 after Chat installation, including dependency checks and
facade identity.

`git diff --exit-code c773f272..HEAD -- packages .github pyproject.toml
uv.lock scripts docs/reference` passed; all 11 later changed paths were
scoped TUI planning/evidence, board and dashboard files. The `packages` tree
matched the reviewed candidate. Board validation passed for 34 tasks, the
dashboard was current, authority JSON parsed, 348 local links in changed
Markdown resolved, and `git diff --check` passed. The worktree was clean.

**Evidence limit:** The Ubuntu installed-wheel probe checks configuration
isolation, not direct installed export-writer behavior. The local
[construction checks](N01B-05-local-checks.md) and
[independent review](VAL-N01B-05-prepush-c773f272.md) separately verified the
installed Runtime and Chat export effects against five and seven frozen
hashes. Ubuntu's full Runtime and Chat suites exercised N01B-05 tests on the
exact pushed source.

This verdict closes only N01B-05's automated exact-source Ubuntu gate.
Installed TUI terminal UAT, full command parity, a controlled real-provider
and tool run, maintainer acceptance, later product authority, another push,
PR, merge and release remain open. This post-verdict report and status
reconciliation do not change the reviewed product source.
