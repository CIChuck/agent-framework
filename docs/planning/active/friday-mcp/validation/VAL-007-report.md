# VAL-007 — Independent REM-004 Delta and Complete MCP-WS-02 Review

Remediation delta: **VERIFIED**
Complete WS-02 aggregate: **VERIFIED**
Overall WS-02 validation gate: **VERIFIED**

Findings: none.

VAL-006 F-001 is resolved in the production stdio transport and public runtime shutdown path. Independent noisy-peer probes completed cleanup without caller pipe intervention. Incomplete-cleanup and cancellation controls retained ownership and allowed subsequent public cleanup. REM-003 provider/DI ownership and recovery behavior remain correct.

## Reviewer and review boundary

Reviewer: fresh-context Codex validation agent `/root/mcp_ws02_val007`, GPT-6 family; exact deployment version unavailable.

Date: 2026-09-28.

Modes: read-only remediation delta first, followed by the complete WS-02 work-unit aggregate.

This context did not inherit or inspect controller, builder, or remediator sessions/private reasoning. Implementation reports were reviewed as documentation inputs; their conclusions were not accepted as independent evidence. No additional agents were spawned.

No governed files were edited, repaired, staged or committed. No repository report, board mutation, credential inspection/use, live endpoint, paid call, network request, delivery operation or external effect occurred. Additional probe files were written only under `/private/tmp`.

## Frozen inputs and exact ranges

| Input | Full revision or range |
| --- | --- |
| Request commit | `201f4d19de5ce2d007a5f6a33ef750db6c2a0376` |
| Request path | `docs/planning/active/friday-mcp/validation/VAL-007-request.yaml` |
| Request SHA-256 | `dd3c845e0beda4bd1532c8eb20ca058841c7c12e46da6e66535388abd55dc41a` |
| Candidate | `a257f041d1d68f8aea2f5b9773df1b88acd82379` |
| Previous candidate | `26f4d7d4bfd0514b6eb76bed71cb4797da91a067` |
| Accepted WS-01 predecessor / WS-02 base | `a64e423cffca6162c43b8cfa193792508cf87fd6` |
| WS-02 authorization | `5c31f7c19f93d8b461dd90936e459ba9e28a4a5d` |
| REM-004 authorization | `cdd808ed653f2f5fe4ccc4a695782d97c39c2ce8` |
| Execution baseline | `bd10656fed43083ff1d81ef2232205b50f58ac99` |
| Bounded correction base | `097bbd9eced5e5ba2ffcc97fbe60273285bf605e` |
| Delta | `26f4d7d4bfd0514b6eb76bed71cb4797da91a067..a257f041d1d68f8aea2f5b9773df1b88acd82379` |
| Bounded correction | `097bbd9eced5e5ba2ffcc97fbe60273285bf605e..a257f041d1d68f8aea2f5b9773df1b88acd82379` |
| Complete WS-02 aggregate | `a64e423cffca6162c43b8cfa193792508cf87fd6..a257f041d1d68f8aea2f5b9773df1b88acd82379` |
| Branch | `feature/friday-mcp-ws02-lifecycle` |
| Initial HEAD | `201f4d19de5ce2d007a5f6a33ef750db6c2a0376` |
| Final HEAD / disclosed dispatch metadata | `a4b71d09be731a919b13350c2148b4d2af2b7b56` |

The full request, AGENTS.md, repository policies, all eighteen pinned authority documents, complete approved build/tactical plans and WS-00/01/02 and REM-003/004 directives were read. Historical reports, candidate source/tests/reports, exact selected diffs, and accepted WS-00/01 contracts/configuration were assessed.

The approved WS-02 build/tactical/directive content matches its authorization revision. REM-004 matches its authorization revision.

## Authority verification and stability

All eighteen hashes matched both their pinned revisions and working content at the beginning and closeout.

Seventeen documents are pinned to candidate `a257f041d1d68f8aea2f5b9773df1b88acd82379`. Only `VAL-006-report.md` is pinned to request commit `201f4d19de5ce2d007a5f6a33ef750db6c2a0376`.

| Authority path | Verified SHA-256 |
| --- | --- |
| `AGENTS.md` | `7fad2b4063a0dc4201d26e353138da6165060077cc88e097dad2ac57551d987f` |
| `docs/reference/policies/repository-engineering-policy.md` | `17b830b8990f74d1b0a25a46fc2cf2f62249f4e0d668f45b96cfe03a6cc76aff` |
| `docs/reference/policies/development-task-lifecycle.md` | `d23f306ab33908f255109152c6c8686423725655184637fe2309e84d8491dc1c` |
| `docs/reference/policies/independent-validation-policy.md` | `4d951418e0f0c96a4c87d4b8a07cb4025dd94738da50893d19a6d2b7a7f82f4a` |
| `docs/planning/active/friday-mcp/build-plan.md` | `546e0d3671ca01c25d7810a0aae0b352196deb1644e594939efb5450d9cea33d` |
| `docs/planning/active/friday-mcp/tactical-plan.md` | `3238f0d0ae4f62bbce3f7a2a453c68bdc4fd90d24a173e86f5cbeb2caf647fac` |
| `docs/planning/active/friday-mcp/directives/ws-02-runtime-lifecycle-provider-loading.md` | `a432dc3c17e7cff9e767ed9dc78f6a1f65ea0d51dead3fc7e5421ef04327f55d` |
| `docs/planning/active/friday-mcp/directives/ws-01-configuration-model-validation.md` | `96ed70391066ac4402542f1f4056f4d38ac9e08be787dbd6daa2f8a41c4cb319` |
| `docs/planning/active/friday-mcp/directives/ws-00-contract-policy-foundation.md` | `ec482e46364c9f4edcd7e76f2e4156d2f8af1710cc1811bf3390d6a5a0f99fac` |
| `docs/planning/active/friday-mcp/rebaseline-2026-09-27.md` | `ccc6f1ca9feab180474e85b30e4c5b9319c32fbd56131f341907a452388f461a` |
| `docs/planning/active/friday-mcp/execution/WS-00-closeout.md` | `434c24937dd4eff77d37ab6ec5c031127723fc54c83ee9446c3b088d848da486` |
| `docs/planning/active/friday-mcp/execution/WS-01-closeout.md` | `8e10fcf509102c1faadcc2e56ce06fe6f9333aaa9d164ad82494e960cbfef32b` |
| `docs/planning/active/friday-mcp/validation/VAL-004-report.md` | `d680911d220b0181fa32fca8260e0ce87f24a322d5dc64794951a85809ed2e0f` |
| `docs/planning/active/friday-mcp/remediation/REM-003-directive.md` | `b04504638f1bded4af42c481ba35a89f02217a25fc392fae33b16ca51a57b680` |
| `docs/planning/active/friday-mcp/validation/VAL-005-report.md` | `4643b408008bbe69b39744305d34d6a7e0dd8d3107eae420da52c1a2cf46940c` |
| `docs/planning/active/friday-mcp/remediation/REM-004-directive.md` | `1079756e6f6738c1dd4fb61126d2a1b3159c3ca48ef092470b47f22a09fec37b` |
| `docs/planning/active/friday-mcp/validation/VAL-006-report.md` | `a8288b18bb0690df745a257ca995e51ba7a380aea5871d8f42dec8dc84d70051` |
| `docs/planning/active/friday-mcp/execution/WS-02-readiness-checkpoint.md` | `e09d7114a37ccd9c8cb3a547227bfbf5937eddc5564afc14003b7df6194da976` |

VAL-006’s candidate-to-request difference is exclusively the six-line superseded decision-status note. Its historical verdict, finding, reproduction, evidence and residual risks remain intact.

The controller disclosed later commit `a4b71d09be731a919b13350c2148b4d2af2b7b56`. Its request-to-HEAD difference changes exactly:

```text
docs/planning/README.md
docs/planning/board.yaml
docs/planning/active/friday-mcp/README.md
docs/planning/active/friday-mcp/task-queue.md
docs/planning/active/friday-mcp/execution-log.md
```

Those are dispatch/process metadata. The request and all pinned authority remained unchanged. Candidate-to-final-HEAD differences additionally contain the already-disclosed request and VAL-006 status note.

At closeout, all twelve aggregate product source/test/fixture files byte-matched the candidate. The required full product/configuration comparison passed repeatedly:

```text
git diff --exit-code a257f041d1d68f8aea2f5b9773df1b88acd82379 -- packages tests pyproject.toml uv.lock
```

The unrelated manifest remained exactly:

```text
 M .DS_Store
 D family-tree.md
?? docker-bench-security/
?? packages/friday-chat/config.example.yaml.pre-typed-llm-20260828.bak
?? packages/friday-sandbox/docker/Dockerfile.audit
```

## Remediation delta — VERIFIED

The bounded correction contains exactly the approved six paths:

```text
packages/friday-mcp/src/friday_mcp/client/stdio.py
packages/friday-mcp/tests_mcp/client/test_lifecycle.py
tests/integration/mcp_fake_server.py
tests/integration/test_mcp_runtime_lifecycle.py
docs/planning/active/friday-mcp/execution/REM-004-implementation-report.md
docs/planning/active/friday-mcp/execution/WS-02-implementation-report.md
```

Production teardown now owns its cleanup task, settles the protocol reader before stdout discard, keeps stderr draining, closes stdin, retains the five-second graceful wait, bounds forced-exit and pipe-EOF waits, and clears references only after successful completion.

The phase budgets in `stdio.py:22–31` total at most eleven asynchronous seconds per attempt: reader settlement 1, graceful exit 5, forced exit 2, pipe EOF 2, failed-attempt task settlement 1. The latter phase applies on failure. This is a cooperative event-loop budget, with documented scheduling slack, not a hard real-time guarantee or reinterpretation of VAL-006’s seven-second detector.

| Criterion | Evidence and assessment |
| --- | --- |
| REM-004-AC-01 | Satisfied. `stdio.py:134–204` drains and reaps the production child; forced kill is followed by a bounded wait. Independently constructed oversized, unterminated stdout/SIGTERM-ignoring peer completed direct public disconnect in **5.006 s**, with exit `-9`, stdout/stderr EOF, closed stdin and no owned stdio tasks. Existing real regression: `test_mcp_runtime_lifecycle.py:252`. |
| REM-004-AC-02 | Satisfied. Independent normal discovery followed solely by public `kernel.stop()` completed in **5.008 s**. The public provider manager and prepared handoff were empty, both children exited, pipes reached EOF and receiver/worker/stdio tasks were absent before defensive cleanup. Existing regression at `test_mcp_runtime_lifecycle.py:277` also verifies two start/stop cycles. |
| REM-004-AC-03 | Satisfied. Independent optional and required noisy handshake and list-failure variants cleaned failed peers; optional variants retained only the successful peer until public stop, while required variants aborted and cleaned both peers. Cleanup-bearing startup took approximately **5.026–5.043 s**. No failed tools registered. Existing four variants at `test_mcp_runtime_lifecycle.py:308` passed. |
| REM-004-AC-04 | Satisfied. `_discard_stream`, `stdio.py:245`, requests 4096-byte chunks without accumulating, logging or persisting payloads. Independent peers emitted multiple megabytes across stderr/stdout; captured logs and typed diagnostics excluded peer, argument and environment sentinels. Incremental-read/redaction regression at `test_lifecycle.py:303` and static-error regression at `:477` passed. |
| REM-004-AC-05 | Satisfied. `stdio.py:102–132` shields the explicitly owned cleanup task while propagating caller cancellation; `:221–242` retains process/task slots after incomplete cleanup. Independent unreaped-process, cancellation-resistant drain and canceled-caller probes confirmed retained ownership and successful public retry; the resistant drain had a maximum of one reader. Independent public kernel stop cancellation retained its owner and a subsequent stop completed in **5.002 s**. Existing EOF, already-exited, repeated shutdown, spawn-cancellation, configured RPC and REM-003 recovery tests passed. |
| REM-004-AC-06 | Satisfied. Exact six-path bounded diff; no runtime/core/config/dependency correction. Public runtime signatures and configuration schema are unchanged. No subprocess private internals or cross-package private reach-through were added. Touched source retains meaningful typing; Ruff and prescribed Python 3.13 mypy passed. Reports accurately distinguish historical checks, current implementation evidence, finite budgets and incomplete-cleanup limits. |
| Owned tasks / reader handoff | Satisfied. `receive()` owns its readline task at `stdio.py:263–273`; teardown settles it before starting the stdout drain at `:139–159`. Successful cleanup requires process wait and both drains to finish. Pending resistant tasks remain owned after failure, and retry reuses pending drains rather than introducing competing readers. |
| Assertion-failure teardown | Independently checked separately from public-cleanup assertions. The subprocess fixture’s `finally` at `test_mcp_runtime_lifecycle.py:98–111` follows assertions, retries public cleanup, then defensively kills/drains/reaps. A scratch test deliberately failed after creating the noisy peer; its outer witness confirmed **reaped child, both pipes drained, and no owned stdio tasks** after fixture teardown. The expected deliberate assertion failure was the only failure in that control. New double fixture and event/task `finally` blocks at `test_lifecycle.py:280–299`, `:353–355`, `:390–392`, `:429–432`, and `:471–473` were also inspected. |

## Independent probes and reproducibility

These probes were constructed independently and use in-process doubles or a local synthetic Python stdio peer. Production probes use unchanged production budgets, a 13-second cleanup watchdog, observable protocol/receiver readiness and explicit final kill/drain/reap/task settlement.

Commands:

```text
LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run python /private/tmp/friday-val007-independent.py
LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run python /private/tmp/friday-val007-ownership.py
LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run pytest /private/tmp/test_friday_val007_fixture_teardown.py -q -s --asyncio-mode=auto --tb=short
```

| Scratch evidence | SHA-256 |
| --- | --- |
| `/private/tmp/friday-val007-independent.py` | `090893ded24cefa4c4092b3083bc12e7babcd0008ae24035fd46037b98be1820` |
| `/private/tmp/friday-val007-ownership.py` | `b922e2b9fb630d74641d125ba4b6f8a081773a2c1d8fc72d7f5e7fab5f846d0a` |
| `/private/tmp/test_friday_val007_fixture_teardown.py` | `00517ea10b6b2e4b962a220274bfef2ff24b4feb74a6cec6b21d7d23de716f39` |

Production probe results:

```text
direct noisy transport: 5.006 s; forced -9 exit; public resources released
kernel normal discovery/stop: 5.008 s; public resources released; redaction passed
kernel canceled stop/public retry: 5.002 s; owner retained; resources released
optional noisy handshake: startup cleanup 5.026 s; valid partial peer preserved
required noisy handshake: startup cleanup 5.042 s; required abort and full cleanup
optional noisy list failure: startup cleanup 5.037 s; valid partial peer preserved
required noisy list failure: startup cleanup 5.043 s; required abort and full cleanup
production_probe_final_resources_settled=True
```

Ownership probe results:

```text
unreaped process: incomplete error, owner retained, public retry settled
resistant stdout drain: incomplete error, pending task retained,
                       maximum readers=1, public retry settled
canceled cleanup caller: cancellation propagated, cleanup remained owned/joinable
provider failure/retry: with/without successful peer, with/without retry cancellation
kernel failure/retry: with/without successful peer, with/without retry cancellation
all 8 runtime ownership variants: identity preserved, public cleanup,
                                successful-peer draining, recovery, redaction passed
ownership_probe_final_resources_settled=True
```

The kernel retry-cancellation double releases its synthetic obstruction when cancellation occurs, allowing exception-path cleanup to settle. It does not impose a deadline on an intentionally perpetual fake disconnect or reinterpret that historical observation as another finding.

The deliberate assertion-failure control returned exit 1, as designed:

```text
assertion_failure_fixture_reaped_drained_tasks_settled=True
1 failed in 6.23s
```

That failure was deliberately injected in the scratch test; it is not a candidate test failure.

All asserted production cleanup was performed through public transport/kernel APIs before defensive `finally` cleanup. Saved identities/process observations were used for assertions and final protection, not to make public-cleanup assertions pass.

## Complete WS-02 aggregate — VERIFIED

The aggregate contains seven product source files, five test/fixture files, three implementation reports, and the authorized planning/review/process evidence. Every source/test/report was assessed. The accepted WS-00 contract and WS-01 configuration interactions remain coherent.

| Criterion | Evidence and assessment |
| --- | --- |
| MCP-02-01 | Satisfied. Native registration remains synchronous at `tool_loading.py:21–30`; DI separately awaits MCP startup at `di.py:123`. The unsupported enablement error is removed. Native/disabled/empty-provider coverage at `test_mcp_loading.py:139`, `:402`, changed `test_di.py`, and production integration passed. No executable MCP registry insertion occurs. |
| MCP-02-02 | Satisfied. Explicit non-global provider ownership is at `di.py:95`, `:119–123`, with public `kernel.mcp_provider` access. `mcp_loading.py:83–99` completes cleanup through its existing manager before replacing it. Server-specific conversion at `:164–178` supplies validated stdio inputs, not the full Friday configuration. Independent provider/kernel retry probes preserved owner identity and client count. |
| MCP-02-03 | Satisfied. Discovery completes before binding validation at `di.py:123` and `kernel.py:112–113`. Admission at `mcp_loading.py:225–326` bounds per-server/total count and encoded schema size/cost in deterministic order. `MCPDiscoveredTool` at `:51–56` is frozen, explicitly untrusted and excludes raw content from representation. Cap tests at `test_mcp_loading.py:272`, invalid-catalog/redaction test at `:293`, and real binding-order/rejection test at `:417` passed. |
| MCP-02-04 | Satisfied. `kernel.py:128`, `di.py:134–135`, `mcp_loading.py:328–348`, `manager.py:81–89` / `:155–157`, `base.py:89–106`, and corrected stdio teardown form the public cleanup path. Success, partial startup, required failure, cancellation and repeated shutdown tests passed. Independent production cleanup and retained-owner retry controls passed. Genuine incomplete cleanup returns a static error and preserves ownership. |
| MCP-02-05 | Satisfied. `mcp_loading.py:93–105` excludes disabled peers before construction; `:192–223` classifies/skips optional connection/list failures; `:122–132` makes cleanup failure fatal and required peer failure abortive. Required startup drains successful peers. Real and double optional/required variants passed. Registry and diagnostics retain zero registered MCP tools. |
| MCP-02-06 | Satisfied. Effective connection/discovery timeout is `min(server.timeout_seconds, limits.connection_timeout_seconds)` at `mcp_loading.py:196–210`; connection retries share the outer deadline. `StdioMCPClient.from_config`, `stdio.py:366`, propagates configured RPC timeout to `base.py:154–157`. Optional/required timeout tests, global-cap test at `test_mcp_loading.py:466`, and the configured 77-second RPC argument regression at `test_lifecycle.py:208` passed. Cleanup has its separately documented budget. |
| MCP-02-07 | Satisfied. Configured-width batches at `mcp_loading.py:117–120` bound task creation; `_batch` at `:144–162` drains cancellation before owner shutdown. The seven-server test at `test_mcp_loading.py:243` observes connection and discovery peaks of two. Worker cancellation at `:332` and local handshake/list cancellation integrations passed, with no retained receiver/worker tasks after cleanup. |
| MCP-02-08 | Satisfied. Fixed typed lifecycle outcomes at `mcp_loading.py:29–48` distinguish disabled, auto-connect skipped, connected, connection/list failure, timeout, cancellation and cleanup failure. Shared discovery/diagnostic DTOs carry safe identifiers/counters/codes. Tests and independent sentinel probes excluded raw exception, command/argument/env and peer payload values from logs and typed diagnostics. |
| Cleanup/redaction amendment | Satisfied. `base.py:76–106` cleans partial handshakes; `:169–172` settles request futures; `:186–205` terminates receiver failure/EOF with static diagnostics. Stdio covers exited children, spawn cancellation, bounded drain/kill/reap and repeated disconnect. Existing partial handshake, request, receiver, EOF, exited-child and spawn-cancellation tests passed. Raw stdio logging remains removed. |
| REM-003-AC-01 | Satisfied. `mcp_loading.py:83–86`; provider retry regressions at `test_mcp_loading.py:482`. Independent variants confirmed the original manager/client count survives failed cleanup and canceled retry. |
| REM-003-AC-02 | Satisfied. `di.py:119`; kernel retry regressions at `test_mcp_loading.py:536`. Independent public kernel variants retained the original provider/manager. |
| REM-003-AC-03 | Satisfied. Public provider/kernel stop released every retained client after synthetic obstruction removal, without saved-owner cleanup. Independent recovery probes and tests at `test_mcp_loading.py:565–588` passed. |
| REM-003-AC-04 | Satisfied. Successful-peer variants independently confirmed draining, failed-client retention, empty handoff, safe diagnostics and eventual public cleanup. Existing variants at `test_mcp_loading.py:482` and `:536` passed. |
| REM-003-AC-05 | Satisfied. Successful cleanup permits recovery; repeated starts/stops remain safe. Independent retry-cancellation variants and regression at `test_mcp_loading.py:591` passed. Required/optional failures, caps, native registry, workspace confinement and redaction checks passed. |
| REM-003-AC-06 | Satisfied. REM-004 leaves runtime ownership correction files unchanged. Public APIs/configuration remain compatible, no new broad suppression exists, prescribed typing passes, and both remediation reports accurately describe retained ownership. |
| WS-00/01 interaction | Satisfied. Loader consumes strict stdio-only runtime models, shared limits/discovery/diagnostic contracts and configured server limits. Workspace containment is revalidated before connection at `mcp_loading.py:90`; cwd defaults to the workspace. Workspace-symlink revalidation test at `test_mcp_loading.py:354`, accepted contract/config tests and downstream Chat config compatibility tests passed. |
| Scope and documentation | Satisfied. Aggregate source/test boundaries match approved WS-02/amendment and bounded remediations. Reports distinguish discovery from executable registration and document cleanup errors, retry behavior and finite limits. Registry entries/final filters/schema sanitization remain WS-03. No Chat turn, provenance/storage, memory/transcript, telemetry emitter, CLI, resources/prompts, server-exposure, refresh or include implementation was added. |

Broad ignores were removed from touched MCP `base.py`, `manager.py` and `stdio.py`. Untouched legacy protocol/config/adapter/SSE suppressions remain separately documented debt. No repository typing configuration was weakened.

## Required command results

Every `uv` command used `UV_CACHE_DIR=/private/tmp/friday-uv-cache`. All pytest and diagnostic-import probes additionally used `LITELLM_LOCAL_MODEL_COST_MAP=true`.

| Exact command following those environment prefixes | Independent result |
| --- | --- |
| `uv run pytest packages/friday-mcp/tests_mcp/client/test_lifecycle.py tests/integration/test_mcp_runtime_lifecycle.py -q` | **39 passed**, 41.09 s |
| `uv run pytest packages/friday-runtime/tests_runtime/test_mcp_loading.py -q` | **32 passed**, 7.07 s |
| `uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime tests/integration/test_mcp_runtime_lifecycle.py -q` | **333 passed**, 47.02 s |
| `uv run pytest packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_llm_config_migration.py -q` | **46 passed**, 1.56 s |
| `uv run pytest tests/integration -q --tb=short` | **44 passed, 1 declared baseline failure**, 44.16 s |
| `uv run ruff check packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | Passed |
| `uv run mypy packages/friday-runtime packages/friday-mcp` | Declared NumPy/default-target syntax baseline reproduced; exit 2 |
| `uv run mypy --python-version 3.13 packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | Passed, 42 source files |
| `uv run python scripts/friday-dev-board.py validate` | Passed, 23 tasks |
| `uv run python scripts/friday-dev-board.py render --check` | Passed; dashboard current |
| `uv run python scripts/check-documentation-lifecycle.py` | Passed, 335 Markdown files |
| `git diff --check 26f4d7d4bfd0514b6eb76bed71cb4797da91a067..a257f041d1d68f8aea2f5b9773df1b88acd82379` | Passed |
| `git diff --check 097bbd9eced5e5ba2ffcc97fbe60273285bf605e..a257f041d1d68f8aea2f5b9773df1b88acd82379` | Passed |
| `git diff --check a64e423cffca6162c43b8cfa193792508cf87fd6..a257f041d1d68f8aea2f5b9773df1b88acd82379` | Passed |
| `git diff --exit-code a257f041d1d68f8aea2f5b9773df1b88acd82379 -- packages tests pyproject.toml uv.lock` | Passed repeatedly, including closeout |

No required check was skipped. No infrastructure blocker occurred.

## Baseline separation

The broad integration failure is exactly the unchanged assertion at `tests/integration/test_development_board.py:75`, expecting `"22 tasks"` while board validation reports 23. Independently parsing the board blob at accepted WS-01 predecessor `a64e423cffca6162c43b8cfa193792508cf87fd6` confirmed **23 tasks**.

Default mypy fails at installed NumPy `__init__.pyi:737`, whose type-statement syntax requires Python 3.12+, while the unchanged repository target is Python 3.10. That invocation stops before checking project code. The required Python 3.13 affected-scope check passes.

This comparison passed:

```text
git diff --exit-code a64e423cffca6162c43b8cfa193792508cf87fd6..a257f041d1d68f8aea2f5b9773df1b88acd82379 -- tests/integration/test_development_board.py pyproject.toml
```

Both failures are declared, independently reproduced baselines, not candidate regressions. Neither was repaired or hidden.

## Residual risks and remaining authority gates

Evidence establishes deterministic local stdio lifecycle behavior with synthetic peers and doubles. It does not establish live MCP/provider interoperability, SSE behavior, executable MCP registry integration, Chat execution or full application UAT.

The eleven-second attempt budget assumes cooperative event-loop scheduling. OS reaping failure, descendants holding output pipes open or cancellation-resistant I/O can still produce a static incomplete-cleanup error; ownership is retained and a subsequent public retry requires the obstruction to clear. Process-tree control and broader lifecycle redesign remain outside this work unit.

Cwd validation scopes the working directory; it is not an OS sandbox for arbitrary executable behavior or command arguments. The bounded untrusted handoff still requires WS-03 naming, collision, filtering, sanitization and registration work before tools become executable or prompt-visible.

This review closes the independent validation gate for the current REM-004 delta and complete WS-02 work unit. It does not record maintainer acceptance, complete the wider initiative, authorize WS-03, or authorize push, merge, release, deployment or other delivery effects.
