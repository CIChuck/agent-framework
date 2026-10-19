# TUI-N01B-01 local construction checks

**Date:** 2026-10-18 (America/New_York)

**Branch/before-code source:** `feature/friday-tui` /
`9b24588676c3b84d62c262d4937f4b0d2b39fbfc`.

**Authority:** Maintainer-approved
[CD-TUI-N01B-01](../directives/CD-TUI-N01B-01-neutral-transcript-query-contracts.md).
This is builder evidence before independent review, not a `VERIFIED` verdict,
TUI acceptance or authority to push.

The only product/test changes are the new
`friday_runtime.transcript_views` module, the `friday_chat.transcripts`
compatibility facade, and one focused test file in each package. The neutral
module owns the three frozen query views and the four-method asynchronous
protocol. Chat re-exports the same four objects and retains its export result
and all query, persistence, handler and file-export effects. No package
metadata, dependency lock, workflow, CLI source or TUI package changed.

| Check | Local result |
| --- | --- |
| Before-code unchanged transcript/identity/`friday-cli` baseline | 171 passed at the prior planning source. |
| New contract/facade tests plus unchanged transcript, identity and `friday-cli` tests | 179 passed after final formatting. |
| Full `friday-runtime` suite | 339 passed with local loopback fixtures enabled. |
| Full `friday-chat` suite | 848 passed, 5 skipped, 1 existing deprecation warning with local loopback fixtures enabled. |
| Unchanged full `friday-cli` suite | 155 passed. |
| Ruff check, Ruff format check and Mypy on four changed product/test files | Passed. |
| `uv lock --check --offline`, board validation, dashboard and `git diff --check` | Passed. |
| Runtime/Chat wheel builds and isolated installed-package checks | Passed; details below. |

## Reproduction commands and environment

The exact 171-test before-code command is retained in the
[characterization](N01B-01-before-code-characterization.md). After the source
move, the following commands produced the 179 focused passes and the three
full-package counts above. The four exported variables are the same values
used as per-command environment assignments during construction. Run the
Runtime, Chat and CLI full suites as **separate pytest invocations** to avoid
the duplicate `test_display.py` collection name. The full Runtime and Chat
commands need permission to bind local `127.0.0.1` fixture servers; without
it, the sandboxed run fails before candidate code executes.

~~~bash
export UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache
export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS='-p no:cacheprovider'
export LITELLM_LOCAL_MODEL_COST_MAP=true
uv run --frozen pytest -q packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-chat/tests_chat/test_transcript_query_facade.py packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_session_identity.py packages/friday-cli/tests_cli
uv run --frozen pytest -q packages/friday-runtime/tests_runtime
uv run --frozen pytest -q packages/friday-chat/tests_chat
uv run --frozen pytest -q packages/friday-cli/tests_cli
~~~

The source/test static, lock and planning checks used these exact paths and
commands (the two package suites above were rerun with local loopback access
after their sandbox failures):

~~~bash
uv run --frozen ruff check packages/friday-runtime/src/friday_runtime/transcript_views.py packages/friday-chat/src/friday_chat/transcripts.py packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-chat/tests_chat/test_transcript_query_facade.py
uv run --frozen ruff format --check packages/friday-runtime/src/friday_runtime/transcript_views.py packages/friday-chat/src/friday_chat/transcripts.py packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-chat/tests_chat/test_transcript_query_facade.py
uv run --frozen mypy packages/friday-runtime/src/friday_runtime/transcript_views.py packages/friday-chat/src/friday_chat/transcripts.py packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-chat/tests_chat/test_transcript_query_facade.py
uv lock --check --offline
uv run --frozen python scripts/friday-dev-board.py validate
uv run --frozen python scripts/friday-dev-board.py render --check
git diff --check
~~~

The wheel build ran the Runtime package first, then the other twelve local
Friday dependencies and Chat with the same build command per package:

~~~bash
wheel_dir=/private/tmp/friday-tui-n01b01-wheels
uv build --offline --wheel --package friday-framework-runtime --out-dir "$wheel_dir"
for package in friday-framework-telemetry friday-framework-core friday-framework-llm friday-framework-memory friday-framework-agent friday-framework-transcript friday-framework-mcp friday-framework-finance friday-framework-moltbook friday-framework-tools friday-framework-cli friday-chat; do
  uv build --offline --wheel --package "$package" --out-dir "$wheel_dir"
done
uv venv --offline --python 3.13 /private/tmp/friday-tui-n01b01-venv
~~~

The local-wheel install used these exact wheel groups, with version `0.1.0a4`
for each. The first offline install attempt found no cached `litellm`; the
second group likewise lacked cached `massive`. Retrying without `--offline`
downloaded declared third-party dependencies into this disposable venv.
Neither install changed the repository or its lock file.

~~~bash
venv_python=/private/tmp/friday-tui-n01b01-venv/bin/python
uv pip install --python "$venv_python" "$wheel_dir"/friday_framework_telemetry-0.1.0a4-*.whl "$wheel_dir"/friday_framework_core-0.1.0a4-*.whl "$wheel_dir"/friday_framework_llm-0.1.0a4-*.whl "$wheel_dir"/friday_framework_memory-0.1.0a4-*.whl "$wheel_dir"/friday_framework_agent-0.1.0a4-*.whl "$wheel_dir"/friday_framework_transcript-0.1.0a4-*.whl "$wheel_dir"/friday_framework_mcp-0.1.0a4-*.whl "$wheel_dir"/friday_framework_runtime-0.1.0a4-*.whl
uv pip check --python "$venv_python"
uv pip install --python "$venv_python" "$wheel_dir"/friday_framework_finance-0.1.0a4-*.whl "$wheel_dir"/friday_framework_moltbook-0.1.0a4-*.whl "$wheel_dir"/friday_framework_tools-0.1.0a4-*.whl "$wheel_dir"/friday_framework_cli-0.1.0a4-*.whl "$wheel_dir"/friday_chat-0.1.0a4-*.whl
uv pip check --python "$venv_python"
~~~

Before the second install, an isolated `python -I` invocation from
`/private/tmp` checked `importlib.metadata.version()` and
`importlib.util.find_spec()` for both frontends, imported the installed
`friday_runtime.transcript_views`, checked its path under `sys.prefix` and
confirmed neither frontend was loaded in `sys.modules`. After the second
install, the same isolated invocation checked both installed module paths,
four Chat/neutral object identities, four historical Chat pickle global
lookups and Chat ownership of `TranscriptExportResult`. The wheel archive was
also inspected with `zipfile.ZipFile` for
`friday_runtime/transcript_views.py` and parsed with `email.parser.BytesParser`
to confirm no frontend `Requires-Dist` entry. These assertions all passed.

A combined Runtime/Chat/CLI pytest invocation stopped at collection because
both Chat and CLI contain a `test_display.py` module. Separate package suites
completed. The first sandboxed full Runtime/Chat runs had nine Runtime failures
and ten Chat failures plus three Chat setup errors, all at test fixtures that
bind `127.0.0.1` and received `PermissionError`. The same suites passed in
full when rerun with local loopback access. No protected test was changed to
work around either runner limitation.

Built the Runtime and Chat wheels and their local Friday dependency wheels
from this checkout into `/private/tmp/friday-tui-n01b01-wheels`. The Runtime
wheel contains `friday_runtime/transcript_views.py` and declares no
`friday-chat` or `friday-framework-cli` dependency. In a fresh Python 3.13
venv under `/private/tmp`, the eight local Runtime dependency wheels and their
declared third-party dependencies installed; `uv pip check` passed for 111
packages. From outside the checkout with `python -I`, the neutral module came
from the installed venv, while Chat/CLI packages were absent and neither
frontend was importable or loaded. After adding the five local Chat-side
wheels and their declared dependencies, `uv pip check` passed for 130
packages. The installed Chat facade's four query objects were identical to
the installed neutral objects; all four old Chat pickle global lookups
resolved, and `TranscriptExportResult` remained Chat-owned. The isolated
dependency resolver needed public package downloads because `litellm` and
`massive` were not in the offline cache; no live provider or credential was
used.

The unchanged Chat production transcript tests exercised fake and
framework-backed query stores, archived sessions, entries, context logs and
export behavior with disposable state. Source inspection found no pickle use
inside `friday-transcript` persistence. These observations support the
compatibility comparison; new pickle byte streams have a different owning
module by design and are not claimed byte-identical.

**Historical gate at builder signoff:** Freeze the local work and obtain a
fresh-context, read-only independent review. It was committed as `7e5241c8`
and the [first review](VAL-N01B-01-preflight-7e5241c8.md) returned
`CHANGES_REQUESTED` for documentation/evidence findings; those are addressed
under [REM-TUI-N01B-01-01](../remediation/REM-TUI-N01B-01-01.md). No N01B-01
exact-source Ubuntu run, installed terminal UAT, user acceptance or external
delivery is claimed. The green CI03 Ubuntu run predates this source change;
any N01B-01 Linux workflow run requires a separately authorized, reviewed
push.
