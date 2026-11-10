# DIAG-001 — bounded maintainer acceptance handoff

Status: implementation and independent validation complete; **human acceptance
pending; manual UAT NOT RUN**. Maintainer: Chuck Russell.

Reviewed candidate: `be72a1e8b5904436ec3b9eb844a5db4f71ed95c9`.
Runtime/test/probe and installed artifact source: `28c544fa67e934f03c212aed39ba20802b500b13`.
Package version: `0.1.0a4`; identify this build by commit/artifact hashes as well
as version. [Verification report](verified-report.md) and
[raw council reconciliation](council-round3.json): Sol/Astra/Claude all VERIFIED,
9.7/10 each; no open mandatory findings. Exact subsequent approvals govern
preserved proposal labels in the original documents.

## Proposed acceptance scope — no decision recorded

Accept only the bounded DIAG-001 D1–D3 extraction of `/context`, `/prompt`,
`/debug`, `/debug-budget`, `/timing` and `/debug-retrieval`: approved neutral
models/specs/typed capabilities, shared orchestration, Chat projection/rendering
and fixed-file effects, current tests/docs, full bounded regression, clean
artifacts and isolated installed proof, including the approved format-before-
length correction. Existing pilot/SESSION/retirement acceptance remains intact.

Acceptance would retain the recorded compatibility boundaries and limits. It
would not certify unperformed manual UAT, broader command families, P0/P1, TUI,
full-refactor completion or any external delivery. The whole command-refactor
initiative stays started/local. No next unit starts automatically.

The maintainer may accept this scope, request a bounded change, or run the
manual checklist before deciding. Approval of the earlier amendment authorized
construction; it did not accept this completed unit.

## Manual UAT starting point

Use the [17-case Friday Chat roadmap](../../../../uat/friday-chat-user-acceptance-roadmap.md)
one case at a time. All its results remain NOT RUN. UAT-05–11 directly cover the
six diagnostics and exports; UAT-01–04 and 12–17 cover appearance, conversation,
help/history, display/clear behavior, recovery, repeated use, performance and exit.

The actual candidate-installed launcher exists at the path below. The CLI flags
were checked against the byte-identical installed-source entry point. These
commands are **instructions for the tester**, not an executed UAT run.

Prepare a separate disposable YAML configuration with fresh memory/transcript/
log/export destinations and telemetry disabled. Keep its model-library path
valid. Leave the two edited repository examples and existing exports untouched.
Set UAT_CONFIG to that configuration's absolute path:

```sh
DIAG_CHAT='/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/ec0c884e-2bae-47e1-9aa9-c43c6d9be9e5/scratchpad/d2r2-oUcy/d3build/bundle/installed-chat/bin/friday-chat'
UAT_CONFIG='/absolute/path/to/your/disposable-config.yaml'
FRIDAY_CHAT_RUNTIME=fake LITELLM_LOCAL_MODEL_COST_MAP=True \
  "$DIAG_CHAT" --config "$UAT_CONFIG" --runtime fake
```

Fake mode supports initial interface/control-flow checks. For conversation
quality, retrieval integration and real latency, use your configured real runtime
and disposable data, explicitly selecting `FRIDAY_CHAT_RUNTIME=real` and
`--runtime real`. Those provider/store effects and their UAT outcomes have not
been exercised by this offline construction proof. Record the exact configuration,
provider/model, terminal dimensions and cold/warm timings in the roadmap register.

The installed prefix is a retained local build artifact, not a published release.
If it is moved or removed, reproduce the pinned offline build from the recorded
source/inputs rather than silently substituting another same-version package.

## Evidence and remaining limits

- 1,991 owning-suite passes; frozen observations 68+4 DIAG/25 SESSION/196 pilot.
- Two corrected trials plus three independent rebuilds agree on 154 actual
  artifact hashes; default 138-name/version and neutral 1-distribution closures.
- Actual normal/optimized installed behavior and targeted negative controls pass.
- Root Ruff 534, root test_display collection conflict and registry format stay
  failed/unwaived. Only macOS arm64/Python 3.13.10 is proven.
- Optional debug-path non-string test hardening remains deferred; current code
  strictly refuses it. No cleanup, push, PR, merge or release occurred.

The [approved construction directive](../../../../directives/CD-CMD-DIAG-001-context-diagnostics.md)
requires stopping here for bounded human acceptance. No such acceptance is
recorded by this handoff.
