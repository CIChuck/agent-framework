# TUI-N01B-03 independent exact-source Ubuntu review

**Verdict:** `VERIFIED` for the bounded N01B-03 exact-source automated Ubuntu
gate. No findings require changes.

**Reviewer and mode:** Fresh-context Codex validation subagent, exact model
version unavailable, read-only post-run work-unit review on 2026-10-19. The
reviewer did not edit, commit or push.

**Reviewed post-run candidate:** `9a68d0c76e8fe4c4be4e4a135f86b67b04d78252`
on `feature/friday-tui`, clean at review and one evidence-only commit ahead
of the pushed source `f7950581c2f65c2a3e5e7e31c80ccd0ecb5e0882`. The
reviewer inspected `f7950581..9a68d0c7` and the full approved-directive
range `23fc6d16..9a68d0c7`. The independently reviewed product candidate
is `782dedbb` under the [local review](VAL-N01B-03-prepush-782dedbb.md).

## Authority, source and packet

The reviewer read [AGENTS.md](../../../../../AGENTS.md), the approved
[directive](../directives/CD-TUI-N01B-03-neutral-transcript-export-serialization.md),
authority manifest, local review, [Ubuntu run report](N01B-03-ubuntu-run-39256858630.md),
board and post-run diff. The supplied SHA-256 pins matched the post-run
candidate:

| Input | SHA-256 |
| --- | --- |
| [Authority manifest](../authority.json) | `3f88a16ca4d64a178f9a1aea803d3f1d7bb1d8b730ae45bfcb464784b116e623` |
| [Approved directive](../directives/CD-TUI-N01B-03-neutral-transcript-export-serialization.md) | `e83625e66202c1e5ce71f91195030b77f3520823e79dec6f035f830728db8163` |
| [Ubuntu report](N01B-03-ubuntu-run-39256858630.md) | `145b09397418c310520809d5cf3728737d892e8787f8b29d45313cc69dbedae4` |
| [Local review](VAL-N01B-03-prepush-782dedbb.md) | `994c0a51f12576c3b04c8132a4378461d6014a251f4ac0c648e434c5a2b86f4a` |
| [Board](../../../board.yaml) | `7db5fdbb13c5d50f6e6fa0cd6570087ce0dabbf9832d0affb6fe88f0597628d5` |

Only eight scoped packet, board, dashboard and evidence paths changed after
the pushed source. The four approved product/test paths are byte-identical
to the first independently reviewed candidate; no other product, test,
workflow, package metadata, dependency lock or script changed in the post-run
commit.

## Ubuntu evidence and checks

The saved GitHub [run 39256858630](https://github.com/CIChuck/agent-framework/actions/runs/39256858630)
job log shows checkout of `f7950581`, Ubuntu 24.04.5 LTS, Python 3.13.12,
356 Runtime passes, 838 Chat passes with 23 skips, 155 unchanged
`friday-cli` passes, seven passing MCP repetitions, 13 distinct wheels and
compatible isolated installed sets. The workflow's installed probe checks
configuration, while the [independent local review](VAL-N01B-03-prepush-782dedbb.md)
separately checked the installed serializer and seven Chat export digests.
The controller also queried GitHub run and job metadata live after completion:
the `push` event, successful run/job and head SHA all matched `f7950581`.

Board validation passed for 34 tasks; the generated dashboard was current;
the authority JSON parsed; 259 changed-document local links resolved; and
the directive diff passed `git diff --check`. The exact-source result is
supported by the job log and these packet checks. The reviewer did not rerun
product tests because post-run changes are evidence-only.

**Residual limit:** The reviewer could not freshly query `api.github.com`
with `gh run view`, so its independent live event, conclusion and job metadata
check was unavailable. The controller's live query and the saved job log are
distinct evidence sources; this limitation does not affect the reviewer's
source-byte, checkout-log or packet findings.

This verdict closes only N01B-03's automated exact-source Ubuntu gate. It
does not establish installed TUI terminal UAT, full TUI parity, real-provider
testing, maintainer acceptance, a later N01B directive, another push, PR,
merge or release. This post-verdict report and status reconciliation do not
change the reviewed product source.
