# TUI-N01B-04 independent exact-source Ubuntu review

**Verdict:** `VERIFIED` for the bounded N01B-04 automated exact-source Ubuntu
gate. No finding requires a change.

**Reviewer and mode:** Fresh-context Codex validation subagent, exact model
version unavailable, read-only post-run review on 2026-10-19. The reviewer
did not edit, commit or push.

**Reviewed post-run candidate:** Clean `feature/friday-tui` at
`27c84ad9f77eb8c5b33e7a50f98e3252ef20b006`, one evidence-only commit
ahead of pushed `4b2aadd273a501674f0f72c233874094f6dd0878`. The reviewer
inspected `4b2aadd2..27c84ad9` and checked product bytes against locally
independently reviewed candidate `abeeb8951914d5b63ca77be4f48a66ace256bfb3`.

## Authority, source and packet

The reviewer read [AGENTS.md](../../../../../AGENTS.md), repository and
independent-validation policies, the [authority manifest](../authority.json),
the approved [N01B-04 directive](../directives/CD-TUI-N01B-04-neutral-export-destination-paths.md),
the [before-code characterization](N01B-04-before-code-export-path-characterization.md),
[builder checks](N01B-04-local-checks.md), [local independent
review](VAL-N01B-04-prepush-abeeb895.md), [Ubuntu run
report](N01B-04-ubuntu-run-39268960501.md), board and post-run diff. The
supplied SHA-256 pins matched the reviewed candidate:

| Input | SHA-256 |
| --- | --- |
| `AGENTS.md` | `02c6360f0e2532a3ea761d7ae228fb105231c60d447146ead69c01c6ff99d152` |
| Repository engineering policy | `17b830b8990f74d1b0a25a46fc2cf2f62249f4e0d668f45b96cfe03a6cc76aff` |
| Independent-validation policy | `4d951418e0f0c96a4c87d4b8a07cb4025dd94738da50893d19a6d2b7a7f82f4a` |
| Authority manifest | `9ee18ba6bdf9c01e3275fe9dbfcec93b71f4112a7c065360f417aacc938f56d6` |
| Approved directive | `71fe2072bd1566067e1b2d9b99f22b27aae05d55928ccece6780fc75bbce5ed3` |
| Ubuntu report | `ae0388169a4fe1b93790ebd58837f581ff55a4fcb8c0b13be7543ddf1b5c5e46` |
| Local review | `42122e921ed1cb452732f7d7b42a783cee44d9bf1873b15a85e0588943807fc3` |
| Board | `bde4423326b85b7ab62797ef269b1b5fc236a0bed4fa1b37fb7c48d2c3760a3b` |
| Downloaded job log | `37725d4ba31086734d79d24ee38e7d6573f16a6e9f89e29b80c38b6d301fcafc` |

Only seven scoped planning, board, dashboard and evidence paths changed after
the pushed source. Product and test files remain byte-identical to the first
independently reviewed candidate; no workflow, package metadata, dependency
lock or script changed. The worktree was clean.

## Ubuntu evidence and checks

The reviewer independently queried live GitHub metadata for
[run 39268960501](https://github.com/CIChuck/agent-framework/actions/runs/39268960501)
and [job 118115889882](https://github.com/CIChuck/agent-framework/actions/runs/39268960501/job/118115889882):
both succeeded, every named step passed, and the `push` event head was the
full `4b2aadd2` SHA. `git ls-remote` returned that SHA for the remote branch;
the downloaded job log printed the same source and checked-out commit.

The log records Ubuntu 24.04.5 LTS, Python 3.13.12, 21 loader/facade passes,
365 Runtime passes, 842 Chat passes with 23 skips, and 155 unchanged
`friday-cli` passes. Three Runtime MCP repetitions, a direct MCP modern
control and three auto repetitions passed. Thirteen wheels built; Runtime
metadata excluded Chat/CLI dependencies; isolated installed Runtime and Chat
sets passed compatibility and configuration-facade checks at 111 and 130
packages. The existing Chat deprecation warning is recorded in the run report.

Board validation passed for 34 tasks, the dashboard was current, 294 local
links in changed documents resolved, authority JSON parsed, and the relevant
diffs passed `git diff --check`. The reviewer did not rerun product tests
because the post-run diff is evidence-only.

**Residual limit:** The Ubuntu workflow's installed-wheel probe exercises
configuration isolation, not direct N01B-04 path helpers or installed Chat
export commands. The [local independent review](VAL-N01B-04-prepush-abeeb895.md)
separately checked those installed behaviors and seven frozen export hashes.

This verdict closes N01B-04's automated exact-source Ubuntu gate only. It
does not establish an installed TUI terminal, macOS/Linux terminal UAT,
full TUI parity, real-provider testing, maintainer acceptance, a later
construction directive, another push, PR, merge or release. This post-verdict
report and status reconciliation do not change the reviewed product source.
