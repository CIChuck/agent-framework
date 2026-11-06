# TUI-N01B-01 independent exact-source Ubuntu reconciliation

**Verdict:** `VERIFIED` for N01B-01 post-run Ubuntu evidence and packet delta.

**Reviewer/mode:** Fresh-context Codex validation subagent, GPT-6 family
(exact build unavailable), read-only, 2026-10-18 America/New_York. No files
were edited. **Evidence candidate:**
`4febb6f681401d0314a23608d46eed6f428c3c19`; **pushed source:**
`62d3ae3bcaab2975b1e311a6ace86739c3dfab1e`. The reviewer checked the
docs-only diff `62d3ae3b..4febb6f6` and confirmed the pushed commit added
only the [pre-push review report](VAL-N01B-01-final-closeout-35e297e8.md)
after its `35e297e8` product/authority candidate. Product and test source did
not change after that pre-push review.

The reviewer confirmed the supplied SHA-256 hashes for the
[approved directive](../directives/CD-TUI-N01B-01-neutral-transcript-query-contracts.md),
[authority manifest](../authority.json), [replacement plan](../replacement-plan.md),
[board](../../../board.yaml), and [Ubuntu evidence report](N01B-01-ubuntu-run-39190668231.md)
at `4febb6f6`. The candidate was clean. JSON parsing, board validation (34
tasks), generated-dashboard check, `git diff --check`, and local links in all
six changed Markdown files passed. The repository-wide documentation checker
still reports six links in an unchanged telemetry review whose file hash
matches the base.

The reviewer checked public [GitHub run 39190668231](https://github.com/CIChuck/agent-framework/actions/runs/39190668231)
and its job metadata: push event, completed/success, head SHA `62d3ae3b`,
job `117862521897` success, and every named step green. The job log prints
the same full source and checked-out SHA on Ubuntu 24.04.5 and Python 3.13.12.
Its result lines show 21 neutral-loader/Chat-facade tests, 339 full Runtime
tests, three passing Runtime MCP auto repeats, one direct MCP modern control
and three passing direct auto repeats, both Chat help exits zero, 830 full
Chat passes with 23 skips and one warning, and 155 unchanged `friday-cli`
passes. It built 13 wheels; Runtime metadata declared no Chat or CLI
dependency. Installed Runtime-only isolation checked 111 compatible packages
without either frontend, then 130 compatible packages with Chat and matching
configuration-facade objects.

The Ubuntu workflow's installed-wheel probe covers the configuration facade,
not the new transcript-query objects. The earlier independent
[pre-push review](VAL-N01B-01-final-closeout-35e297e8.md) separately checked
installed Runtime/Chat wheels for transcript-specific import closure, object
identity and historical pickle lookups on unchanged product source. The
Ubuntu full Runtime and Chat suites exercised the new transcript tests on
the exact pushed source. The reviewer concluded that the directive's
exact-source automated Linux criterion is met. No findings require changes.

**Provenance limit:** The detailed raw job log was inspected from downloaded
`gh` output; unauthenticated GitHub log-archive access returned 403. Its run,
job, step and source identity were cross-checked against live GitHub metadata
and the browser job page.

This verdict closes the N01B-01 automated Linux validation gate only. The
initiative remains `started`; later N01B effects need their own directive and
approval. Installed macOS/Linux terminal UAT, complete TUI parity,
real-provider/tool UAT, aggregate branch review, maintainer acceptance, PR,
merge and release remain open. This review authorizes no additional push.
