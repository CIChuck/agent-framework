# Proposed TELEM-03 verification profile

Status: proposed; not approved. Date: 2026-10-06.
Bound to [CD-003](directives/CD-003-safe-llm-metrics.md) and
[contract](telem03-contract.md). Earlier accepted profiles remain historical.

## Environment, isolation and preflight

Use a fresh tracked snapshot at the preparation base and stable candidate, omitting
the protected tracked runtime paths before checkout (267 at preparation). Never
copy/read original .env/.friday/Chroma/transcript/credential/unrelated dirty payloads.
Freeze omission set, tracked hashes, source resolution, import/conftest/helper effects
and exact permitted nodes before collection. New unit tests use fakes only; no
LiteLLM live call, SDK exporter/thread/channel, provider readiness call, database or
listener from their fixtures. In-memory actual SDK evidence must use owned synthetic
exporters with explicit close and no network, following accepted TELEM-02 preflight.

Use installed Python 3.13.10, Ruff 0.14.10, Mypy 1.19.1 and Pytest 9.0.2; record actual
versions/hashes. No install/sync/build/download or interpreter provisioning. Execute
with uv run --no-sync and explicit offline/no-sync/no-python-download settings,
private temp/cache roots, PYTHONDONTWRITEBYTECODE=1,
LITELLM_LOCAL_MODEL_COST_MAP=true, ANONYMIZED_TELEMETRY=False. Retain the accepted
external socket guard hash and isolated */src plus Chat helper PYTHONPATH. Do not
inherit credentials, live flags, HOME overrides, proxies, OTEL_*/GRPC_*/certificate
variables. Native gRPC bypasses Python hooks: prove literal loopback targets,
accepted retries=0/proxy=0/finite timeout/owned cleanup in the two unchanged nodes.

Proposed CD-003 permissions cover only the exact existing 13 parameter-expanded
nodes in [listener-scope.json](execution/TELEM-03-planning/listener-scope.json),
normal-user localhost sandbox escape, after final fixture/helper/import hash audit.
No remote/TLS/public-root loading/provider services. Any extra listener effect
stops execution; do not replace full gates with selected successes or new exclusions.

## Behavioral evidence

Before construction, run safe fake-only baseline probes on typed/legacy/stream/
embedding paths to record metrics gaps, raw legacy projections, sink failure masking,
cancellation finalization and known alias behavior. Mock provider dispatch before
imports/calls can activate transport. Retain source/API/static inventory separately;
proposal static reads are not those probes. Label later comparisons retrospective.

Candidate evidence must cover every AC03-01–08: exact event counts and identities,
simultaneous independent calls, nested callers, successful/failing setup retries,
blocked circuit/validation/parsing failure, cancellation at setup/read/backoff,
early aclose and cleanup failure, timeout, usage after FinishEvent, repeated/missing/
invalid usage, reasoning/tool-only streams, reported zero, cache hit, empty input,
multibatch success/partial failure and truthful cost coverage/provenance. Malicious
sentinels in every raw model, response ID, context field, error, prompt, reasoning,
tool and embedding value must not appear in serialized events/diagnostics/span data.
Use an exception with a failing __str__ to prove classification does not stringify.

Verify all factories/roles in the pinned inventory, both pools and legacy fallbacks;
assert the same observer by identity, service selection and alias identity, None when
disabled, caller ownership and no constructor-side provider call. Include compaction
and explicit reorganization registry, not just mocked primary runtime plumbing.
Consumer probes exercise Chat observer, Debug, two-child Composite and actual managed
OTel with synthetic in-memory exporter. LLM events export outside/current accepted
spans without introducing a stream-held span or global context/callback state.

Fresh static preparation Mypy checks eight existing prospective source targets and
exits 1 on two no-any-return diagnostics at adapters.py:325/328. CD-003 explicitly
includes their typed snapshot-publisher boundary correction and bool-preservation
consumer probes. These are required fixes, not waived debt. pricing.py currently
has a whole-file ignore; this observed baseline cannot certify its typing. Its
additive API work must remove that ignore and pass genuine changed-source Mypy.

## Mandatory candidate commands

Execute each independently and retain command/cwd/revision/environment/path expansion,
exit, stdout/stderr, counts/skips, source-resolution and before/after hashes:

```text
pytest packages/friday-telemetry/tests_telemetry/test_llm_events.py packages/friday-telemetry/tests_telemetry/test_safe_llm.py packages/friday-llm/tests_llm/test_safe_telemetry.py packages/friday-chat/tests_chat/test_llm_telemetry_injection.py -rA
pytest packages/friday-chat/tests_chat packages/friday-llm/tests_llm packages/friday-telemetry/tests_telemetry --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py --ignore=packages/friday-llm/tests_llm/test_live_lmstudio.py -rA
pytest --import-mode=importlib --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py --ignore=packages/friday-llm/tests_llm/test_live_lmstudio.py --collect-only
pytest --import-mode=importlib --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py --ignore=packages/friday-llm/tests_llm/test_live_lmstudio.py -rA
pytest --import-mode=importlib <exact aggregate owning test trees> --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py --ignore=packages/friday-llm/tests_llm/test_live_lmstudio.py -rA
ruff check <exact changed unit Python paths>
ruff check <exact aggregate changed Python paths>
ruff check . --output-format json
mypy --python-version 3.13 <exact changed unit source paths>
mypy --python-version 3.13 <exact aggregate changed source paths>
uv lock --offline --check --no-python-downloads --no-build
python scripts/friday-dev-board.py validate
python scripts/friday-dev-board.py next
python scripts/friday-dev-board.py show friday-telemetry-rewire
python scripts/friday-dev-board.py render --check
python scripts/check-documentation-lifecycle.py
```

Expand every placeholder to pinned files before execution: unit allowed manifests
contain 25 Python/11 source targets, aggregate derives from 2155a0f, and owning trees
derive from those packages rather than stale prior counts. Record unchanged optional
live/SciPy skips by exact node/reason; any new failure/skip is a finding. New tests
cannot be skipped for missing optional/live prerequisites. Genuine installed tool
runs are required; record desired repo-wide mypy debt separately if run, without
using it to excuse changed-source typing failures.

Parse changed Python with ast.parse(feature_version=(3,13)); verify public call
compatibility, unchanged TypedLLMClient/request/stream shapes, legacy helper API,
legacy pricing calculate results, no new source suppression/blanket config changes,
all 18 >=3.13.4 floors and unchanged dependency selection/lock/config templates.
Check exact delta and aggregate git diff --check, privacy/runtime assertion safety,
source/package boundaries, stable evidence and preservation of accepted manifests.

Raw root Ruff must remain visible as nonzero. Only separately approved
[WVR-005](validation/WVR-005-telem03-lint-disposition.md) may dispose exactly the
327 pinned path/code/start/end/message identities, four archive hashes, registry
source/class AST, 17 configuration hashes, tool version and target. Compare before
construction and at candidate. Any additional identity or input drift fails;
changed-unit/aggregate Ruff and Mypy must exit zero. WVR-004 is expired, not inherited.

Freeze product candidate, exact delta/aggregate paths and immutable authority hashes.
AGENTS.md requires a fresh-context read-only validator after construction, reviewing
all criteria and accepted-unit regressions. Return VERIFIED/CHANGES_REQUESTED/BLOCKED.
If renewed lint authority is approved, obtain its required fresh independent review
before construction; no self-approved waiver or proposal readiness is claimed here.
Maintainer acceptance and external/delivery actions remain separate.
