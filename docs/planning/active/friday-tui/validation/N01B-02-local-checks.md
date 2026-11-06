# TUI-N01B-02 local construction checks

**Date:** 2026-10-19 (America/New_York).

**Branch/before-code source:** `feature/friday-tui` /
`f0e0786f69243513b9e35d66dc271c2c5f10afab`.

**Authority:** Chuck Russell's exact approval of
[CD-TUI-N01B-02](../directives/CD-TUI-N01B-02-neutral-transcript-query-adapter.md),
recorded in authority/board commit `b58e8288`. This is builder evidence
before fresh independent review, not a `VERIFIED` verdict, TUI acceptance or
permission for external delivery.

The only product/test changes are the new
`friday_runtime.transcript_queries` module, four Chat query-method delegates,
and one new focused test file in each package. Runtime's read adapter maps
the existing `friday-transcript` records to the previously verified neutral
views. Chat retains its SQLite store, constructor, writes, finalization,
handlers and export effects. No `friday-cli`, package metadata, dependency
lock, workflow, runtime configuration or TUI package changed.

| Check | Local result |
| --- | --- |
| Before-code unchanged transcript/identity/`friday-cli` baseline | 171 passed on `f0e0786f`. |
| New neutral/delegation tests, N01B-01 tests and unchanged protected transcript/identity/`friday-cli` tests | 195 passed. |
| Full `friday-runtime` suite | 352 passed with disposable loopback fixture access. |
| Full `friday-chat` suite | 851 passed, 5 skipped, 1 existing deprecation warning with disposable loopback fixture access. |
| Unchanged full `friday-cli` suite alone | 155 passed. |
| Ruff check and targeted Mypy on four changed source/test files | Passed. |
| Ruff format on three new files and changed ranges of Chat adapter | Passed. Whole-file Chat adapter format remains red on the unchanged before-code source. |
| `uv lock --check --offline`, board validation and dashboard | Passed. |
| Runtime/Chat wheel builds and isolated installed-package probes | Passed; details below. |

## Reproduction commands and environment

The [before-code characterization](N01B-02-before-code-characterization.md)
retains the exact 171-test baseline command. Local tests use synthetic data and
disposable transcript stores; no provider, credential or existing local
Friday state is used.

~~~bash
export UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache
export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS='-p no:cacheprovider'
export LITELLM_LOCAL_MODEL_COST_MAP=true
uv run --frozen pytest -q packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-runtime/tests_runtime/test_transcript_queries.py packages/friday-chat/tests_chat/test_transcript_query_facade.py packages/friday-chat/tests_chat/test_transcript_query_adapter_delegation.py packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_session_identity.py packages/friday-cli/tests_cli
uv run --frozen pytest -q --tb=short packages/friday-runtime/tests_runtime
uv run --frozen pytest -q --tb=short packages/friday-chat/tests_chat
uv run --frozen pytest -q packages/friday-cli/tests_cli
~~~

Run the full Runtime, Chat and CLI suites as separate pytest invocations to
avoid duplicate Chat/CLI `test_display.py` collection names. Their first
sandboxed Runtime/Chat runs failed only at tests/fixtures trying to bind
`127.0.0.1` (`PermissionError: [Errno 1] Operation not permitted`): Runtime
had 9 failed/343 passed; Chat had 10 failed/838 passed/5 skipped/3 setup
errors. The exact full suites above then passed with local loopback access.
No protected test or product source was changed for the runner limitation.

~~~bash
uv run --frozen ruff check packages/friday-runtime/src/friday_runtime/transcript_queries.py packages/friday-chat/src/friday_chat/adapters.py packages/friday-runtime/tests_runtime/test_transcript_queries.py packages/friday-chat/tests_chat/test_transcript_query_adapter_delegation.py
uv run --frozen mypy packages/friday-runtime/src/friday_runtime/transcript_queries.py packages/friday-chat/src/friday_chat/adapters.py packages/friday-runtime/tests_runtime/test_transcript_queries.py packages/friday-chat/tests_chat/test_transcript_query_adapter_delegation.py
uv run --frozen ruff format --check packages/friday-runtime/src/friday_runtime/transcript_queries.py packages/friday-runtime/tests_runtime/test_transcript_queries.py packages/friday-chat/tests_chat/test_transcript_query_adapter_delegation.py
uv run --frozen ruff format --check --range 10-77 packages/friday-chat/src/friday_chat/adapters.py
uv run --frozen ruff format --check --range 1372-1397 packages/friday-chat/src/friday_chat/adapters.py
uv lock --check --offline
uv run --frozen python scripts/friday-dev-board.py validate
uv run --frozen python scripts/friday-dev-board.py render --check
git diff --check
~~~

The whole-file `ruff format --check` for the changed Chat adapter still says
"Would reformat". The same result occurs on the file as stored at pre-code
HEAD `b58e8288`, copied into `/private/tmp` and checked with the repository
Ruff configuration. Ruff's diff shows no format changes in the edited query
methods or import block; both changed ranges pass individually. Formatting
the entire legacy file would alter unrelated Chat code outside the directive.

## Installed-package boundary and behavior

All thirteen relevant local wheels were built offline from this checkout:

~~~bash
for package in friday-framework-telemetry friday-framework-core friday-framework-llm friday-framework-memory friday-framework-agent friday-framework-transcript friday-framework-mcp friday-framework-runtime friday-framework-finance friday-framework-moltbook friday-framework-tools friday-framework-cli friday-chat; do
  uv build --offline --wheel --package "$package" --out-dir /private/tmp/friday-tui-n01b02-wheels || exit 1
done
~~~

The Runtime wheel contains `friday_runtime/transcript_queries.py`; its parsed
wheel metadata has no Chat/CLI `Requires-Dist` entry.

~~~bash
uv venv --offline --python 3.13 /private/tmp/friday-tui-n01b02-venv
uv pip install --offline --python /private/tmp/friday-tui-n01b02-venv/bin/python /private/tmp/friday-tui-n01b02-wheels/friday_framework_telemetry-0.1.0a4-*.whl /private/tmp/friday-tui-n01b02-wheels/friday_framework_core-0.1.0a4-*.whl /private/tmp/friday-tui-n01b02-wheels/friday_framework_llm-0.1.0a4-*.whl /private/tmp/friday-tui-n01b02-wheels/friday_framework_memory-0.1.0a4-*.whl /private/tmp/friday-tui-n01b02-wheels/friday_framework_agent-0.1.0a4-*.whl /private/tmp/friday-tui-n01b02-wheels/friday_framework_transcript-0.1.0a4-*.whl /private/tmp/friday-tui-n01b02-wheels/friday_framework_mcp-0.1.0a4-*.whl /private/tmp/friday-tui-n01b02-wheels/friday_framework_runtime-0.1.0a4-*.whl
uv pip check --python /private/tmp/friday-tui-n01b02-venv/bin/python
~~~

The Runtime-only install resolved 111 compatible packages. An isolated
`python -I` process outside the checkout verified that Chat and CLI were
absent and unloaded, imported the installed neutral module from the venv,
queried a disposable SQLite session, entry and context log directly, then
verified archive filtering and exact-session archive status. It checked the
installed Runtime distribution metadata for no frontend dependency. The
first probe attempted a LiteLLM remote model-cost lookup, which failed under
network restriction and fell back locally; no model request was sent. Later
installed probes set `LITELLM_LOCAL_MODEL_COST_MAP=true`.

~~~bash
uv pip install --offline --python /private/tmp/friday-tui-n01b02-venv/bin/python /private/tmp/friday-tui-n01b02-wheels/friday_framework_finance-0.1.0a4-*.whl /private/tmp/friday-tui-n01b02-wheels/friday_framework_moltbook-0.1.0a4-*.whl /private/tmp/friday-tui-n01b02-wheels/friday_framework_tools-0.1.0a4-*.whl /private/tmp/friday-tui-n01b02-wheels/friday_framework_cli-0.1.0a4-*.whl /private/tmp/friday-tui-n01b02-wheels/friday_chat-0.1.0a4-*.whl
uv pip check --python /private/tmp/friday-tui-n01b02-venv/bin/python
~~~

The Chat-side install resolved 130 compatible packages. A second isolated
`python -I` process constructed an installed Chat runtime with a disposable
SQLite store and verified all four Chat query results equal direct neutral
adapter results. It executed installed `/sessions`, `/transcript` and
`/export csv` handlers, and checked that the CSV contained the seeded
answer. The first version of this probe assumed an incorrect export filename;
the corrected probe enumerated the single exported CSV and passed without a
source change.

**Next gate:** Freeze a stable candidate commit and obtain a fresh-context,
read-only independent review against the exact directive, authority manifest,
before-code baseline and protected comparison. Exact-source Ubuntu execution,
installed TUI terminal UAT, real-provider testing, maintainer acceptance and
external delivery are not claimed by these local checks.
