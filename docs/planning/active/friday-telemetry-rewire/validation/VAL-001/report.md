CHANGES_REQUESTED

VAL-001 independently reviews TELEM-01 / CD-001 on frozen candidate `0c7b6d4c416402443d140a5ee09abed70be34c69`, base `2155a0fc51f5b20dea4e35c6cfc70f1d52002735`. AC-05 fails a deterministic ownership probe; AC-06 also remains unsatisfied on an independently reproduced baseline timing gate. No fixes were performed.

**Reviewer and independence.** Codex independent validator /root/telem01_validator; GPT-6 family per session instructions; exact runtime model/build/version unavailable; 2026-10-05T13:34:26.966482+00:00. Fresh agent context, detached isolated checkout `/private/tmp/telem-01/review`. No builder reasoning or implementation-report conclusions supplied or relied upon. Controller baseline claims were independently rechecked. Shared .venv is execution infrastructure only; every isolated `packages/*/src` directory was prepended to PYTHONPATH. Historical memory was only orientation; current frozen authority controls.

**Candidate, authority, and scope.** Exact range `2155a0fc51f5b20dea4e35c6cfc70f1d52002735..0c7b6d4c416402443d140a5ee09abed70be34c69`; diff SHA-256 `9042b3ae413dfd430851ad4c207e6ea60d7877bc61dac4b5fdcb58017450b313`. [Complete diff](candidate.diff.gz), [exact changed-path manifest](candidate-manifest.txt), and [changed-path SHA-256s](changed-path-hashes.json) are preserved. All 12 changed product/test/README paths fit CD-001 lines 34–43; board/dashboard changes concern only this initiative. No dependency, exporter, LLM/memory/runtime-framework, example-config, command-registry, or tool-continuity changes occur. Builder execution artifacts are frozen and hashed but do not support this decision. Read AGENTS, all three pinned policies, accepted MCP WS-07 directive, build plan, first-slice contract, tactical plan, CD-001, board/index/execution metadata, and all product/test/README changes.

Every pinned authority SHA-256 matches candidate bytes. Revisions below are last-touch revisions at candidate; the manifest pins content hashes.

| Authority path | Revision | Matching SHA-256 |
| --- | --- | --- |
| AGENTS.md | `0c8095f5132c9cc47573f27481dea59a7cc70c6c` | `7fad2b4063a0dc4201d26e353138da6165060077cc88e097dad2ac57551d987f` |
| docs/reference/policies/repository-engineering-policy.md | `0c8095f5132c9cc47573f27481dea59a7cc70c6c` | `17b830b8990f74d1b0a25a46fc2cf2f62249f4e0d668f45b96cfe03a6cc76aff` |
| docs/reference/policies/development-task-lifecycle.md | `0c8095f5132c9cc47573f27481dea59a7cc70c6c` | `d23f306ab33908f255109152c6c8686423725655184637fe2309e84d8491dc1c` |
| docs/reference/policies/independent-validation-policy.md | `12c1e9e577409bf25f7fdc18fb7bb75a24f5ec07` | `4d951418e0f0c96a4c87d4b8a07cb4025dd94738da50893d19a6d2b7a7f82f4a` |
| docs/archive/completed/2026/friday-mcp/directives/ws-07-telemetry-diagnostics-health.md | `d50788d730e8c3e2c30b01af9b4fa6e2c5146cda` | `4ab5f003951b096ae13a35ce7873a7fe7a45144145a7c403e860f923486e548f` |
| docs/planning/active/friday-telemetry-rewire/build-plan.md | `0c7b6d4c416402443d140a5ee09abed70be34c69` | `ddba6460ee01bf9497af48119489a37fa4969420e1b0e46d1dec2ca438d18c8a` |
| docs/planning/active/friday-telemetry-rewire/telemetry-contract.md | `0c7b6d4c416402443d140a5ee09abed70be34c69` | `ab82f83249385def31cb372a4c252e058a3e5186e11ba6e1ac8e659812c2e8df` |
| docs/planning/active/friday-telemetry-rewire/tactical-plan.md | `0c7b6d4c416402443d140a5ee09abed70be34c69` | `125c5961a660221a1e51c3a605fa51407bbe3b525b0cfceef8b7b9ed52ff3fae` |
| docs/planning/active/friday-telemetry-rewire/directives/CD-001-local-telemetry-assembly.md | `0c7b6d4c416402443d140a5ee09abed70be34c69` | `513ddd2b3eed0e7ffcf2e460d610d725146842993f41f68a25382fa1fea76cba` |

**Finding VAL-001-F01 — medium, priority 1, AC-05.** [Composite start assignment](/private/tmp/telem-01/review/packages/friday-telemetry/src/friday_telemetry/providers/composite.py) (line 76) (lines 76–77) overwrites a live ownership tuple when the current first child returns an ID equal to a previous first child’s ID. [End](/private/tmp/telem-01/review/packages/friday-telemetry/src/friday_telemetry/providers/composite.py) (line 82) then pops only the replacement tuple. Two different conforming providers can each issue `span-0` as their own first unique span ID; no public TelemetryInterface contract defines a global namespace across independent providers. Start old provider’s span, remove it, add the new provider, start another span: both public IDs are `span-0`, and ending them leaves the removed provider’s original span unclosed. This violates [first-slice ownership contract](/private/tmp/telem-01/review/docs/planning/active/friday-telemetry-rewire/telemetry-contract.md) (line 64) (lines 58–72) and [CD-001](/private/tmp/telem-01/review/docs/planning/active/friday-telemetry-rewire/directives/CD-001-local-telemetry-assembly.md) (line 67) (lines 67–69).

The [independent collision probe](test_independent.py.gz) (line 94) (lines 94–110) fails with `old.ends == []` where `["span-0"]` is required; [reproducible log](membership-collision.log.gz). Risk: lost cleanup and incorrect span attribution under supported dynamic provider membership. Required mitigation: preserve existing live ownership when a public ID collides. A compatible bounded approach detects the collision, closes every newly opened child, reports a content-free aggregate failure, and leaves the original entry intact. A different public-ID contract requires explicit approval. Add regression coverage with independent provider-local ID namespaces, verify new rollback and original exactly-once end, and retain ordinary nested/membership/fan-out cases. No config change is required; document collision failure behavior in the telemetry README.

**Acceptance evidence.** PASS applies only to the cited criterion; it does not grant whole-work-unit verification.

| Criterion | Result | Source/test and reproducible evidence |
| --- | --- | --- |
| AC-01 | PASS | Strict default-disabled debug-only configuration, safe loader errors and old compatibility fixtures pass. Sources: packages/friday-chat/src/friday_chat/config.py:591-603; packages/friday-chat/src/friday_chat/config.py:913-925. Tests: packages/friday-chat/tests_chat/test_telemetry.py:46-95; packages/friday-chat/tests_chat/compat/test_config_compatibility.py; test_independent.py:28-33. Logs: focused.log, independent.log. |
| AC-02 | PASS | Fake and stubbed-real assembly create observer before construction; injected override works with disabled YAML; CLI uses shared path. No live providers required. Sources: packages/friday-chat/src/friday_chat/runtime.py:1218-1242; packages/friday-chat/src/friday_chat/runtime.py:1317-1322; packages/friday-chat/src/friday_chat/cli.py:114-123; packages/friday-chat/src/friday_chat/telemetry.py:78-117. Tests: packages/friday-chat/tests_chat/test_telemetry.py:46-57; packages/friday-chat/tests_chat/test_telemetry.py:200-240; packages/friday-chat/tests_chat/test_cli.py:255-269; test_independent.py:19-26. Logs: focused.log, independent.log, origins.log. |
| AC-03 | PASS | Truthful assembly/app lifecycle, existing cleanup ordering, cancellation plus cleanup failure, bounded immutable snapshots and cumulative counts pass. Sources: packages/friday-chat/src/friday_chat/app.py:405-458; packages/friday-chat/src/friday_chat/app.py:536-550; packages/friday-chat/src/friday_chat/app.py:625-644; packages/friday-chat/src/friday_chat/telemetry.py:93-117; packages/friday-chat/src/friday_chat/telemetry.py:166-180. Tests: packages/friday-chat/tests_chat/test_telemetry.py:98-115; packages/friday-chat/tests_chat/test_telemetry.py:244-385; test_independent.py:49-80. Logs: focused.log, independent.log. |
| AC-04 | PASS | All 15 existing MCP event names preserve allowlisted payloads; 135 content-field attempts rejected. No planted content appears in safe diagnostics/healthy sink. Mixed mutating/failing composite sink isolation passes. Sources: packages/friday-chat/src/friday_chat/telemetry.py:27-45; packages/friday-chat/src/friday_chat/telemetry.py:137-180; packages/friday-chat/src/friday_chat/telemetry.py:182-215; packages/friday-telemetry/src/friday_telemetry/models/mcp.py:86-106. Tests: packages/friday-chat/tests_chat/test_telemetry.py:118-197; test_independent.py:19-46; test_independent.py:49-80. Logs: focused.log, independent.log. |
| AC-05 | FAIL | Ordinary nested IDs, empty/duplicate ends, membership changes with globally random IDs, mutation and failure fan-out pass. Provider-local public-ID collision after membership replacement overwrites old ownership and strands removed child; VAL-001-F01. Sources: packages/friday-telemetry/src/friday_telemetry/providers/composite.py:53-88. Tests: packages/friday-telemetry/tests_telemetry/test_providers.py:208-318; packages/friday-chat/tests_chat/test_telemetry.py:168-186; test_independent.py:82-110. Logs: focused.log, independent.log, membership-collision.log. |
| AC-06 | BLOCKED | Focused/static/governance/documentation gates pass; aggregate remains nonzero on a independently reproduced baseline timing test. No approved waiver exists. Regression evidence separated from infrastructure, but required all-green/waived gate is unsatisfied. Sources: docs/planning/active/friday-telemetry-rewire/directives/CD-001-local-telemetry-assembly.md:87-115; docs/reference/policies/independent-validation-policy.md:187-200. Tests: packages/friday-chat/tests_chat/test_reorganization_terminal.py:91-113. Logs: aggregate.log, baseline.log, controlled.log, loopback.log, pty-isolated.log, ruff.log, mypy.log, board.log, docs.log, diff-check.log, stability.json. |

**Commands and results.** All paths below are relative to the isolated candidate except baseline, which runs an exact `git archive` of base in `VAL-001/base`. The runner scripts and per-command JSON record exact commands and environment controls. Cache outputs reside under VAL-001; pytest cache writes are disabled.

`uv run --no-sync pytest -p no:cacheprovider packages/friday-chat/tests_chat/test_telemetry.py packages/friday-chat/tests_chat/test_cli.py packages/friday-chat/tests_chat/test_runtime.py packages/friday-chat/tests_chat/test_app_lifecycle.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-telemetry/tests_telemetry/test_providers.py`

129 passed; exit 0 ([log](focused.log.gz)); runner: `python /private/tmp/telem-01/VAL-001/run_checks.py focused`.

`uv run --no-sync pytest -p no:cacheprovider packages/friday-chat/tests_chat packages/friday-telemetry/tests_telemetry`

716 passed, 5 skipped, 3 failures, 3 setup errors; exit 1 ([log](aggregate.log.gz)); runner: `python /private/tmp/telem-01/VAL-001/run_checks.py aggregate`.

`uv run --no-sync pytest -p no:cacheprovider packages/friday-chat/tests_chat packages/friday-telemetry/tests_telemetry`

674 passed, 5 skipped, same 3 failures and 3 setup errors; exit 1 ([log](baseline.log.gz)); runner: `python /private/tmp/telem-01/VAL-001/run_extra.py baseline`.

`uv run --no-sync pytest -p no:cacheprovider packages/friday-chat/tests_chat packages/friday-telemetry/tests_telemetry`

718 passed, 5 skipped, 1 timing failure, 3 setup errors; exit 1 ([log](controlled.log.gz)); runner: `python /private/tmp/telem-01/VAL-001/run_extra.py controlled`.

`uv run --no-sync pytest -p no:cacheprovider packages/friday-chat/tests_chat/test_llm_adapter_migration.py::test_chat_adapter_controls_reach_final_http_json packages/friday-chat/tests_chat/test_llm_adapter_migration.py::test_chat_adapter_typed_stream_reuses_generation_defaults packages/friday-chat/tests_chat/test_llm_adapter_migration.py::test_provider_option_target_mismatch_fails_before_http`

3 passed using narrow loopback escalation; exit 0 ([log](loopback.log.gz)); runner: `python /private/tmp/telem-01/VAL-001/run_extra.py loopback`.

`uv run --no-sync pytest -p no:cacheprovider packages/friday-chat/tests_chat/test_reorganization_terminal.py::test_provider_free_pty_acknowledges_before_bounded_progress_completes`

Unchanged warmed isolated timing test still fails; exit 1 ([log](pty-isolated.log.gz)); runner: `python /private/tmp/telem-01/VAL-001/pty-isolated via logged subprocess invocation`.

`uv run --no-sync pytest -p no:cacheprovider --basetemp=/private/tmp/telem-01/VAL-001/independent-temp -k 'not membership_replacement' /private/tmp/telem-01/VAL-001/test_independent.py`

13 independent probes passed; exit 0; collision probe executed separately ([log](independent.log.gz)); runner: `python /private/tmp/telem-01/VAL-001/independent via logged subprocess invocation`.

`uv run --no-sync pytest -p no:cacheprovider /private/tmp/telem-01/VAL-001/test_independent.py::test_membership_replacement_cannot_overwrite_preexisting_child_ownership`

1 independent ownership probe failed; exit 1 ([log](membership-collision.log.gz)); runner: `python /private/tmp/telem-01/VAL-001/membership-collision via logged subprocess invocation`.

`uv run --no-sync ruff check packages/friday-chat/src/friday_chat/app.py packages/friday-chat/src/friday_chat/cli.py packages/friday-chat/src/friday_chat/config.py packages/friday-chat/src/friday_chat/runtime.py packages/friday-chat/src/friday_chat/telemetry.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_cli.py packages/friday-chat/tests_chat/test_telemetry.py packages/friday-telemetry/src/friday_telemetry/providers/composite.py packages/friday-telemetry/tests_telemetry/test_providers.py`

All 10 changed Python files pass; exit 0 ([log](ruff.log.gz)); runner: `python /private/tmp/telem-01/VAL-001/run_checks.py ruff`.

`uv run --no-sync mypy --python-version 3.13 packages/friday-chat/src/friday_chat/app.py packages/friday-chat/src/friday_chat/cli.py packages/friday-chat/src/friday_chat/config.py packages/friday-chat/src/friday_chat/runtime.py packages/friday-chat/src/friday_chat/telemetry.py packages/friday-telemetry/src/friday_telemetry/providers/composite.py`

All 6 changed source files pass; exit 0 ([log](mypy.log.gz)); runner: `python /private/tmp/telem-01/VAL-001/run_checks.py mypy`.

`uv run --no-sync python scripts/friday-dev-board.py validate`

24 tasks valid; exit 0 ([log](board.log.gz)); runner: `python /private/tmp/telem-01/VAL-001/run_checks.py board`.

`uv run --no-sync python scripts/check-documentation-lifecycle.py`

391 Markdown files valid with UV_NO_SYNC=true and UV_OFFLINE=true; exit 0 ([log](docs.log.gz)); runner: `python /private/tmp/telem-01/VAL-001/run_checks.py docs`.

`git diff --check 2155a0fc51f5b20dea4e35c6cfc70f1d52002735..0c7b6d4c416402443d140a5ee09abed70be34c69`

Exact base..candidate passes; exit 0 ([log](diff-check.log.gz)); runner: `python /private/tmp/telem-01/VAL-001/run_checks.py diff-check`.

`uv run --no-sync python -c 'import friday_chat,friday_telemetry,friday_mcp,friday_runtime; print("\n".join(x.__file__ for x in [friday_chat,friday_telemetry,friday_mcp,friday_runtime]))'`

Chat, Telemetry, MCP and Runtime modules resolve isolated source roots; exit 0 ([log](origins.log.gz)); runner: `python /private/tmp/telem-01/VAL-001/run_checks.py origins`.

The initial documentation command exited 1 because the existing script launches nested `uv run` without `--no-sync`, which attempted unavailable hatchling resolution and failed DNS before sync. Rerunning with `UV_NO_SYNC=true UV_OFFLINE=true` prevented nested synchronization and passed. No command failure is relabeled as a pass. Existing console OTel tests emit an atexit closed-file exporter traceback on both base and candidate; this is distinct from exit-code/test outcomes.

**Limitation VAL-001-L01 — AC-06 baseline/infrastructure.** Original environment (`TERM=dumb`, `NO_COLOR=1`): exact base is 674 passed / 5 skipped / 3 failures / 3 setup errors; candidate is 716 passed / 5 skipped / the same 3 failures / 3 setup errors. This independently explains the extra display failure absent from the supplied mixed-checkout baseline. With `TERM=xterm-256color` and NO_COLOR removed, both clear-sequence checks pass: candidate becomes 718 passed / 5 skipped / 1 failure / 3 setup errors. The three synthetic HTTP-fixture checks all pass under narrowly permitted 127.0.0.1-only escalation. The [unchanged PTY acknowledgment test](/private/tmp/telem-01/review/packages/friday-chat/tests_chat/test_reorganization_terminal.py) (line 101) requires output within 0.8 seconds; it still fails a warmed isolated rerun ([log](pty-isolated.log.gz)). No changed candidate source/test caused the same-base failure pattern, but the required aggregate command is still nonzero.

The supplied baseline list is evidence, not an approved waiver. [Independent validation policy](/private/tmp/telem-01/review/docs/reference/policies/independent-validation-policy.md) (line 190) requires deterministic checks to pass or have an approved waiver. After F01 remediation, the remaining gate is a passing unchanged required aggregate/timing check in an adequate authorized environment, or a maintainer-recorded narrow baseline exception. Do not change the test deadline in validation, invent a waiver, or mark the work complete. Any changed candidate or controlling authority requires a fresh frozen review.

**Stability and residual risk.** [Stability proof](stability.json): candidate HEAD unchanged; all 2,015 tracked-file SHA-256s match before/after; `git status --porcelain=v1 --untracked-files=all` empty before and after. Report/probe sources/logs/base archive/cache files exist only outside candidate in VAL-001. Required suites used standard OS temporary fixture directories; final independent probe fixtures were confined to VAL-001/independent-temp and TMPDIR=VAL-001/tmp. No original-checkout mutation, commit, remediation, real conversation inspection, secret disclosure, vendor call, remote exporter activation, or external side effect. Shared environment and existing local console-OTel test behavior are disclosed execution exceptions; no exporter/network lifecycle claims are made. Later TELEM units remain deferred. This result permits only a bounded remediation decision, not completion, maintainer acceptance, push, merge or delivery.
