# TUI-N01B-04 independent local review

**Verdict:** `VERIFIED` for the bounded N01B-04 local work unit. No candidate
finding requires changes.

**Reviewer and mode:** Fresh-context Codex (GPT-6) validation subagent,
read-only full work-unit review on 2026-10-19. The reviewer did not edit,
commit or push. The handoff contained pinned authority, the exact candidate,
required checks and baseline limits, without builder private reasoning.

**Candidate:** clean `feature/friday-tui` product candidate
`abeeb8951914d5b63ca77be4f48a66ace256bfb3`, approved planning base
`401d10583a19c1b1689cdeb7046d00e5352e5819`, review diff
`401d1058..abeeb895`. Evidence-only packet tip at handoff was
`ce8bc35af04d774afe93c8cd6adc063bf809543a`; its diff from the product
candidate changed six TUI planning files and no product code or tests.

## Pinned authority and scope

The reviewer matched the supplied SHA-256 pins and read the repository entry
point, engineering and validation policies, [authority manifest](../authority.json),
[approved directive](../directives/CD-TUI-N01B-04-neutral-export-destination-paths.md),
[before-code characterization](N01B-04-before-code-export-path-characterization.md),
[builder checks](N01B-04-local-checks.md), replacement plan, capability map
and board.

| Input at evidence packet `ce8bc35` | SHA-256 |
| --- | --- |
| `AGENTS.md` | `02c6360f0e2532a3ea761d7ae228fb105231c60d447146ead69c01c6ff99d152` |
| Engineering policy | `17b830b8990f74d1b0a25a46fc2cf2f62249f4e0d668f45b96cfe03a6cc76aff` |
| Independent-validation policy | `4d951418e0f0c96a4c87d4b8a07cb4025dd94738da50893d19a6d2b7a7f82f4a` |
| Authority manifest | `de3c85d0fbda89b6795162b549d0c5554fe6e783cf50f9987f9c2583808513b5` |
| Approved N01B-04 directive | `71fe2072bd1566067e1b2d9b99f22b27aae05d55928ccece6780fc75bbce5ed3` |
| Before-code characterization | `5d393b4064fdd60cb3850a467dedea149739af3d70386a2c05f270b27c165067` |
| Builder local report | `a75b42587655d02ebebf3dc78e794ad22d49d58e2ccd37a7aac24836aaa8adfb` |
| Replacement plan | `aff4744f24826bf54f1db7eb3523f2478af9c1426350ba7b90332928e2b643c4` |
| Neutral capability map | `9f79745e2fe6219e5cf75102a5983764efc72fe1709f4f91c458ee5eac85cd93` |
| Board | `8c307efe3ea93b0715ebacafec5a7d36c12733d48eacd6fbacda8c4b996c3567` |

The product diff changes only the four approved Runtime/Chat source/test paths
and scoped packet/dashboard files. Runtime's neutral module retains Chat's
earlier root-creation and containment rules without Chat/CLI imports. Chat
retains effective configuration choice, public export-root entry point,
registry callers, export writers and result identity. `git diff --check`
passed. No protected `friday-cli` source or test changed.

## Independent results

The reviewer reproduced the direct new tests (**13 passed**), focused and
protected comparison (**239 passed**, including unchanged `friday-cli`), full
Runtime (**365 passed**) and full Chat (**860 passed, five skipped**). Board
validation passed for 34 tasks, the generated dashboard was current, scoped
Ruff and targeted Mypy passed, `uv lock --check --offline` passed and
changed-document local links resolved.

The reviewer checked Runtime and Chat wheel source bytes against the checkout.
An offline, isolated Runtime-only install had 111 compatible packages, with
Chat and CLI absent; its direct path probe passed. After Chat was installed
separately, the installed registry probe matched all seven frozen export-file
SHA-256 values, `/context --file` and `/prompt --file` outputs and bytes, and
the Chat-owned `TranscriptExportResult` identity.

The initial full Runtime test attempt encountered nine local-loopback fixture
bind denials in the restricted sandbox. Rerunning with permitted loopback
access passed all 365 tests. Whole-file formatting of the changed Chat file
remains red on four pre-existing, unrelated ranges; the edited ranges are
formatted. A repository-wide Ruff run reported 534 issues on unchanged paths.
The documentation lifecycle checker still reports six unchanged absolute
telemetry-review links. These baseline failures do not implicate N01B-04.

The first Runtime-only import, run without the prescribed local LiteLLM
cost-map setting, logged a failed DNS lookup for the cost map. No remote
response or provider call occurred. The final installed probes used
`LITELLM_LOCAL_MODEL_COST_MAP=true`.

## Boundary of the verdict

`VERIFIED` closes the local N01B-04 work-unit review only. Exact-source Ubuntu
verification, installed macOS/Linux TUI terminal UAT, full TUI acceptance and
external delivery remain open. The verdict grants no push, PR, merge, release
or maintainer acceptance authority.
