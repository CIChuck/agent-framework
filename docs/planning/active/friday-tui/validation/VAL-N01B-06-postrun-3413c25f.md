# TUI-N01B-06 independent exact-source Ubuntu review

**Verdict:** `VERIFIED` for the bounded N01B-06 automated exact-source Ubuntu
gate. No finding requires a source change.

**Reviewer and mode:** Fresh-context Codex validation subagent, read-only
post-run review on 2026-10-19. The reviewer did not edit, commit or push.

**Reviewed post-run candidate:** Clean `feature/friday-tui` at
`3413c25fdaaa746b16e883f2a1d2d02a6fcc404f`, two local planning/evidence
commits ahead of pushed `aa8ae784487cb723130a39e5a8421b881f40178d`.
The independently reviewed N01B-06 product candidate is
`e16aede68c929737874d76bf72fcea98f952bcc4`.

The reviewer read the current authority and approved [N01B-06
directive](../directives/CD-TUI-N01B-06-neutral-all-session-export-effects.md),
the [local review](VAL-N01B-06-prepush-e16aede6.md), [run
report](N01B-06-ubuntu-run-39284711876.md), board, packet and exact post-push
diff. The live [GitHub run](https://github.com/CIChuck/agent-framework/actions/runs/39284711876)
and sole [job](https://github.com/CIChuck/agent-framework/actions/runs/39284711876/job/118167270170)
both reported `completed/success` on the full `aa8ae784` SHA, with one run
attempt and every step successful. The live remote branch, run head, printed
source and checkout SHA matched. The earlier individual-job API lag resolved.

The reviewer independently refetched and hashed the live logs. The archive
SHA-256 was
`15a1c200fab16bc8b18deed2a7dec905d0faa1525bf8589e5e44d46d15697450`,
its combined job member was
`fd0710032775ae6c513345662833ac19325a0c3b48058dd9f2b434a228362e7b`,
and the terminal `gh run view --job 118167270170 --log` stream was
`d3213643838effc20c44187caa24f670ff8e95386b4d156faeec3fd1d3c064e9`.
All match the run report. The terminal stream has CLI-added prefixes; its
source and check results match the archive member.

The log records Ubuntu 24.04.5, Python 3.13.12, 21 loader/facade passes, 382
full Runtime passes, 848 full Chat passes with 23 skips and one warning, and
155 unchanged `friday-cli` passes. Repeated Runtime and direct MCP checks
passed. Thirteen wheels built; Runtime metadata excluded Chat/CLI. The
isolated Runtime-only install had 111 compatible packages and no Chat/CLI;
the later Chat install had 130 compatible packages and passed configuration
identity checks.

`git diff --name-only e16aede6..HEAD -- packages .github pyproject.toml
uv.lock scripts` was empty. The nine paths changed after the push were scoped
TUI planning, authority, dashboard and run evidence. Board validation passed
for 34 tasks, the dashboard was current, authority JSON parsed, 388 changed
Markdown links resolved locally, `git diff --check aa8ae784..HEAD` passed,
and the checkout was clean.

**Evidence limit:** The Ubuntu installed-wheel probe checks neutral
configuration isolation, not the new installed export writers. The
[local construction checks](N01B-06-local-checks.md) and
[independent local review](VAL-N01B-06-prepush-e16aede6.md) separately verified
Runtime and Chat installed-wheel export effects. The exact-source Ubuntu
Runtime and Chat suites exercised N01B-06 tests.

This verdict closes only N01B-06's automated exact-source Ubuntu gate.
N01B-07's [directive](../directives/CD-TUI-N01B-07-neutral-transcript-tool-records.md)
remains proposed, without code or delivery authority. Installed macOS/Linux
TUI terminal UAT, a controlled real-provider/tool run, full initiative
acceptance, another push, PR, merge and release remain open. This report and
post-verdict status reconciliation do not change the reviewed product source.
