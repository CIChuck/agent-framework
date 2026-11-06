# VAL-N01A: neutral configuration-loader work-unit review

**Outcome:** BLOCKED — required automated Linux smoke has no execution evidence.
This is an infrastructure/evidence blocker, not a code finding or a TUI UAT
result.

**Reviewer:** `/root/n01a_independent_validation`, separate fresh-context
Codex GPT-6 agent (exact variant unavailable).

**Date/mode:** 2026-10-18; full, read-only work-unit review.

**Initiative/unit:** `friday-tui` / TUI-N01A. The initiative remains `started`;
this result does not establish maintainer acceptance or authorize delivery.

## Frozen inputs

- Branch: `feature/friday-tui`.
- Base: `ab56cbc61ac8f9ec54fc8d6e0b1753fe18411332`.
- Candidate: `4a5311f2340adfbbf9cd5c4289db325e6b420b6b`.
- Exact diff: `git diff ab56cbc61ac8f9ec54fc8d6e0b1753fe18411332..4a5311f2340adfbbf9cd5c4289db325e6b420b6b`.
- `authority.json` SHA256: `b63afd23b91182aa14c5f0af588e8c7b25773b9653a1bf7358b3c956941c9c37`.
- `directives/CD-TUI-N01A-neutral-config-loader.md` SHA256:
  `4c2300f0568db07367230faf69e911727d595afa745f712d9e3acfa77f98b42c`.
- `neutral-config-loader-contract.md` SHA256:
  `e9ecf6c8564fd9a57a495f9d23d4855670273c5b310fd99418df78a71ae76cec`.
- `replacement-plan.md` SHA256:
  `7d686261e31f45c46a2ab8738dd67927a364323e43f5ee76ec568d2c9e458b54`.
- `validation/N01A-before-code-characterization.md` SHA256:
  `39e5b90742f362ef63c6c4688373e1db79f5fc4f03a64e38bf7fa836de92e1e0`.
- `docs/planning/board.yaml` SHA256:
  `47ec1765b1beafb53203040fc771d4e55a643f982a294a120f612e3d7025b4e1`.

The reviewer checked these candidate bytes, `AGENTS.md`, the engineering,
lifecycle and independent-validation policies, the construction directive,
contract, characterization and diff. The shared checkout stayed clean at the
candidate commit; the reviewer made no edit. No detached worktree was used.
Later process-only updates to the board and packet record this verdict but do
not change the reviewed candidate or its frozen authority hashes.

## Reviewed criteria and evidence

The mandatory work-unit criteria are the public API, compatibility, stop
conditions and construction gates in
[CD-TUI-N01A](../directives/CD-TUI-N01A-neutral-config-loader.md). The
TUI-N01A row of the [replacement plan](../replacement-plan.md) scopes this
unit; the complete TUI and user UAT remain later gates.

- The 15-file diff changes only the six product/test/metadata/lock paths
  permitted by the directive and scoped planning records. `git diff --check`
  passes. The neutral model/error aliases and loader are in
  `friday_runtime.application_config:683-705`; the Chat facade delegates with
  current module diagnostic maps in `friday_chat.config:108-130`.
- Independent baseline/candidate probes matched typed dumps, ordered
  diagnostics, canonical example service specs, raw paths, exception messages
  and chaining. The reviewer AST-compared 42 shared classes/functions; only
  the intended diagnostic-rule injection differs. Historical Chat imports
  and pickle global lookup pass. New Runtime and Chat tests cover the neutral
  import, rule snapshots, symlink catalog, diagnostics, errors and facade
  identity (`test_application_config.py`, `test_config_facade.py`).
- Focused tests: **390 passed**. Full Runtime: **334 passed**. Full Chat:
  **839 passed, 5 skipped**. Unchanged `friday-cli`: **155 passed**.
  Affected cross-package tests: **280 passed**. Local socket fixtures needed
  permitted ephemeral loopback binding; the reruns passed. Changed-file
  Ruff/Mypy, lock, package/board/dashboard and whitespace checks pass.
- Both Runtime and Chat wheels built. Runtime wheel metadata declares direct
  `pydantic>=2.0` and `pyyaml>=6.0.0`, and no Chat/CLI requirement. Installed
  source-file hashes match the newly built wheels. The disposable installed
  environment passes `uv pip check` with **127 compatible packages**. An
  installed neutral import loads no Chat/CLI module; installed Chat and
  Runtime expose the same model/error objects and match canonical example
  results, including 10 chat and two embedding service specs.
- Checkout and installed `friday-chat --version` report `0.1.0a4`; help
  options match. Both retain the characterized `friday --help` import failure
  for missing `friday_cli.main.app`; no CLI source changed.

The reviewer reproduced the core checks with `UV_OFFLINE=1`, `uv run
--no-sync pytest -q` over the named focused suites, full package test
directories and affected cross-package tests; `uv build --wheel` for Runtime
and Chat; `uv pip check` on the disposable venv; wheel metadata inspection;
installed-versus-wheel source hashes; and isolated installed Python imports.
The decisive test invocations, from the repository root, were:

```sh
env UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' uv run --no-sync pytest -q packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_llm_config_migration.py packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/test_cli.py packages/friday-runtime/tests_runtime/test_config.py packages/friday-runtime/tests_runtime/test_mcp_runtime_config.py packages/friday-runtime/tests_runtime/test_model_library.py packages/friday-cli/tests_cli packages/friday-chat/tests_chat/test_config_facade.py packages/friday-runtime/tests_runtime/test_application_config.py
env UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' uv run --no-sync pytest -q packages/friday-runtime/tests_runtime
env UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' uv run --no-sync pytest -q packages/friday-chat/tests_chat
env UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' uv run --no-sync pytest -q packages/friday-cli/tests_cli
env UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' uv run --no-sync pytest -q packages/friday-telemetry/tests_telemetry packages/friday-mcp/tests_mcp/test_upgrade_aggregate.py tests/integration/test_mcp_execution_provenance.py tests/integration/test_mcp_memory_ingestion.py tests/integration/reorganization/test_gate_a_reproductions.py
```

The focused tests, full Runtime, full Chat, unchanged CLI and cross-package
groups passed in that order. The reviewer also ran `uv build --wheel` for
Runtime and Chat, inspected the Runtime wheel `METADATA` and file list,
compared SHA256 hashes of installed source against both newly built wheel
payloads, and ran `uv pip check --python
/private/tmp/friday-tui-n01a-venv/bin/python`. An earlier combined Chat/CLI
collection encountered their existing duplicate `test_display.py` module
names; the separate suites above collected cleanly.

The [local construction checks](N01A-local-checks.md) give the builder's
separate evidence. No real provider request or credential was used. An
initial installed import attempted LiteLLM's public cost-map fetch and failed
under network restriction; the subsequent deterministic import checks set
`LITELLM_LOCAL_MODEL_COST_MAP=True`. The unchanged Runtime import path causes
that attempt, not the N01A extraction. A second fresh offline installation
could not resolve uncached `litellm==1.100.1`; the installed-wheel check uses
the existing disposable environment and matches its files to reviewer-built
wheels.

## Blocker and exit gate

**B-01 — Linux execution evidence unavailable.** Directive gate 4 requires
an automated neutral smoke on Linux. The reviewer ran `uname -s` and probed
`docker`, `podman`, `colima`, Lima and QEMU plus both Docker contexts. The
host is Darwin; only Docker's client is present, neither context has a
daemon, and the Docker app executable is absent. The neutral test module is
runnable, but it was not run on Linux. Under the [independent-validation
policy](../../../../reference/policies/independent-validation-policy.md),
unavailable mandatory infrastructure prevents `VERIFIED`.

The exit gate is to run and retain an automated neutral-loader smoke on a
Linux runner against **candidate `4a5311f2`**, including
`test_application_config.py`, `test_config_facade.py`, a wheel install with
declared dependencies outside the checkout, and an isolated installed
`friday_runtime.application_config` import that loads no `friday_chat` or
`friday_cli` modules. Record Linux distribution/Python version, commands,
exit codes, wheel hashes and source revision; then request fresh-context
independent closure of B-01 against the unchanged candidate. A changed
candidate or controlling authority requires a fresh full review. The board
must not mark N01A `VERIFIED` before that evidence exists.

No TUI executable or terminal user UAT exists yet. The repository-wide
documentation lifecycle checker still reports six pre-existing broken
absolute links in an unchanged telemetry review report. No push, merge,
release or publication is authorized by this work-unit review.
