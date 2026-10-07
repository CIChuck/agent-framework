# Proposed TELEM-04 verification profile

Status: proposed, not approved; bound to [CD-004](directives/CD-004-correlated-execution.md)
and the [execution contract](telem04-contract.md). Prepared 2026-10-07.

## Isolation and evidence

Use fresh tracked preparation/candidate snapshots, omitting the267 protected runtime
paths before checkout. Never copy original .env/.friday/Chroma/transcript/credential
or unrelated dirty payloads. Record exact revisions, omissions, tracked hashes,
commands, cwd, allowlisted environment, tool/source resolution, timestamps, raw exits,
counts/skips and before/after hashes. Keep prior failures and successful reruns.
Use installed Python3.13.10, Ruff0.14.10, Mypy1.19.1 and Pytest9.0.2; verify actual
versions/hashes. No install/sync/build/download or interpreter provisioning.

Use uv run --no-sync, UV_OFFLINE=true, UV_NO_SYNC=true,
UV_PYTHON_DOWNLOADS=never, private caches/temp roots, PYTHONDONTWRITEBYTECODE=1,
LITELLM_LOCAL_MODEL_COST_MAP=true, ANONYMIZED_TELEMETRY=False, the accepted external
socket guard (SHA6f61ea4ca34c7abef9e0c709eb1e1feb0f3cf7733cbc59bc465d6b01182e9e81),
and isolated */src plus Chat helper paths. Do not inherit credentials, live flags,
HOME overrides, proxies, OTEL/GRPC/certificate variables. New tests use transport
fakes and in-memory adapters only. Inspect imports/fixtures/helpers before collection.

Only CD-004 approval authorizes its [13 existing synthetic nodes](execution/TELEM-04-planning/listener-scope.json),
normal-user loopback effects after fixture hash reconciliation. Native gRPC bypasses
Python hooks: verify literal127.0.0.1 target, finite timeout, accepted retry/proxy
disablement and owned server/channel cleanup. No new listener. A separate actual
SDK consumer may construct an owned in-memory exporter/processor and close it,
without network/global provider registration or borrowed-sink shutdown.

## Required behavioral matrix

Before editing, record fake-only baseline gaps at the preparation snapshot. After
editing, cover all AC04-01–08 with actual behavior, not mirror-schema-only tests:

- Both turn paths: no tools, native/MCP and mixed tools, selection/circuit block,
  successful/failed retry, timeout, cancellation at retrieval/model/tool/persistence,
  streaming callback failure, early iterator close and primary-exception cleanup.
- Multiple concurrent turns/sessions and nested callers: unique identities, correct
  parent references, no foreign binding, restored task/SDK context, closed spans.
  No span held across public generator yield; baseline chunk/result order unchanged.
- Native unknown/disallowed/KeyError and MCP succeeded/failed/blocked/timeout records:
  exact actual dispatches, rejection counts and accepted redaction/provenance/ID repair.
- Retrieval/store/ingestion success/failure/empty inputs; actual returned counts;
  empty/no-extractor and mixed-turn extraction batch, retry/requeue, foreground
  preemption, shutdown flush and ExtractionCommitCompletedUnderCancellation.
- Failure/cancellation after each persistence stage: partial observations preserved,
  no successful turn before complete existing path, accepted MCP receipt_committed
  versus published/pending/skipped/disabled, unchanged raw context capture behavior.
- Multi-iteration reasoning presence/preservation in actual outbound assistant
  history with native and accepted MCP redaction, without raw reasoning export.
- Accepted LLM request/attempt/batch events unchanged and linked inside active
  scopes; accepted MCP payload unchanged and separately correlated; originals
  outside a scope remain uncorrelated, invalid events never generate links.
- Malicious content/IDs/path/exception/model/tool/document sentinels and exceptions
  with failing __str__; strict overflow/bool-count/NaN/Inf/forged-instance rejection.
  Search serialized events, diagnostics, span attributes and metrics for leakage.
- Exporter-off, ordinary sink failures at start/event/end and retention saturation:
  <=256 records, <=128 open spans, <=32 summaries, fixed bounded metric keys/buckets,
  exactly one terminal contribution and failed-turn /debug+/timing output.
- Actual Chat observer → Debug/two-child Composite/managed OTel consumer with a
  synthetic in-memory exporter: safe correlated spans/events, nested/concurrent
  parent restoration, no global/provider/worker leak and caller ownership retained.

## Mandatory candidate gates

Execute independently using the allowlisted environment:

```text
pytest <six exact new test modules from the manifest> -rA
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
git diff --check <unit base> <candidate>
git diff --check 2155a0fc51f5b20dea4e35c6cfc70f1d52002735 <candidate>
```

Expand placeholders to pinned paths before execution; do not omit non-package
aggregate Python changes. Derive owning trees from actual aggregate package paths,
including friday-memory/transcript/core and accepted remediated packages. Preserve
the exact two live module exclusions and existing SciPy optional skip only; any
new failure/skip is a finding. Desired repo-wide Mypy debt, if run, is separate
from mandatory passing changed-source typing. Current nine prospective existing
source files pass genuine lint/Mypy; no typing exception is requested.

Verify public APIs/defaults, unchanged accepted LLM/MCP/interface and persistence
formats, source AST at3.13, no new suppressions, all18 >=3.13.4 floors, unchanged
dependencies/lock/config/templates, accepted authority/evidence pins, exact product
scope and original dirty state. Exercise public generic Parent→Child/Child→Parent
compatibility consumers retained from prior units where aggregate changes apply.

Raw root Ruff stays visible as failing. Only separately approved WVR-006 may
dispose its exact327 identities; compare path/code/start/end/message, four archive
hashes, CommandRegistry source/class AST,17 lint configurations, tool version and
py313 target before construction and at candidate. Drift or any new identity fails.
No waiver for changed/aggregate lint, typing, tests, privacy or lifecycle.

Freeze a stable committed candidate, exact unit/aggregate diff and authority manifest.
AGENTS.md requires a fresh-context read-only validator, with no builder conclusions,
to review the full unit and aggregate. The required result is VERIFIED,
CHANGES_REQUESTED or BLOCKED, with reproducible evidence. Independent review of
renewed lint authority precedes construction; it does not certify product behavior.
