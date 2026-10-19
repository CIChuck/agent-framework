# TUI-N01B-03 local construction checks

**Date/branch:** 2026-10-19, `feature/friday-tui`.
**Directive:** [approved CD-TUI-N01B-03](../directives/CD-TUI-N01B-03-neutral-transcript-export-serialization.md).
**Before-code source:** `c1e38d944452ff26edd5a1fa4302fe5d9a2ccfc6`.
**Outcome:** Builder checks passed for local candidate preparation. Independent
review, an exact-source Ubuntu run, installed TUI terminal UAT and maintainer
acceptance are not established by this report.

## Exact construction and behavior

The new `friday_runtime.transcript_export_format` exposes six synchronous,
typed, pure serializers over the N01B-01 Runtime views. Chat's existing export
writers call those serializers. Chat still selects sessions/formats, supplies
display names, resolves and creates export paths, writes UTF-8 files and
returns the same command results and `TranscriptExportResult`. No Chat/CLI
source outside the one approved handler module changed. The `friday-cli`
package, TUI package, dependencies, lock, workflows and runtime configuration
were not edited.

The direct Runtime test compares all seven former Chat files with literal
expected UTF-8 text and their [before-code SHA-256
values](N01B-03-before-code-characterization.md). It also checks empty
outputs, multiple session/entry/context-log records, input order, naive and
aware ISO times, CSV quoting/embedded LF, Unicode, nullable values, Markdown
display names and exact trailing-newline rules. New Chat tests run the actual
slash commands against both a fixed fake query store and disposable SQLite;
both backends produce all seven frozen hashes and unchanged command output.
They also check default/configured export roots, zero entries, missing
sessions, absent prompt logs and write/root failure messages. Existing Chat
and CLI tests remained unchanged.

## Test and static evidence

The test environment used `UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache`,
`PYTHONDONTWRITEBYTECODE=1`, `PYTEST_ADDOPTS='-p no:cacheprovider'` and
`LITELLM_LOCAL_MODEL_COST_MAP=true`; all fixtures were fake or disposable.

| Gate | Local result |
| --- | --- |
| New Runtime and Chat export tests | 9 passed. |
| Frozen Runtime view/query, Chat query/transcript/export/session and full protected `friday-cli` comparison | 204 passed, including the 155 unchanged CLI tests. |
| Full Runtime package | 356 passed with local `127.0.0.1` loopback access. Initial sandboxed attempt had 347 passed and nine MCP fixture bind failures (`PermissionError: [Errno 1]`); no N01B-03 test failed. |
| Full Chat package | 856 passed, five skipped, one existing deprecation warning, with local loopback access. |
| Ruff check and targeted Mypy on the four approved source/test paths | Passed; Mypy found no issues in four files. |
| Ruff format on new Runtime source and both new test files; changed Chat import and export ranges | Passed. Whole-file Chat format check remains red on the pre-code source and current file; formatting unrelated legacy lines is outside this directive. |
| `uv lock --check --offline` | Passed; lock unchanged. |

The full Runtime and Chat suites were run separately to avoid duplicate test
module names. Escalated test execution supplied only local loopback access for
disposable MCP/HTTP fixtures, as in N01B-02; it did not use a live provider.
After the final test-fixture and formatting changes, the 204-test protected
comparison, Ruff checks and targeted Mypy passed again. No product behavior
change followed the full-suite and installed-wheel runs.

## Installed-wheel boundary

Built all 13 relevant wheels offline into
`/private/tmp/friday-tui-n01b03-wheels`. The Runtime wheel contains
`friday_runtime/transcript_export_format.py` and its metadata declares no
Chat/CLI requirement. An isolated Python 3.13 venv installed Runtime and its
dependencies from local wheels/cache: `uv pip check` passed for 111 packages.
From `/private/tmp`, `python -I` found neither `friday_chat` nor `friday_cli`,
imported the installed serializer from the venv and matched the frozen
sessions/entries CSV hashes.

After adding the Chat wheel and its dependencies to that venv, `uv pip check`
passed for 130 packages. A second `/private/tmp` `python -I` process invoked
the installed Chat registry's `/transcript export`, `/export` CSV/JSONL/
training/Markdown and `/export-prompts` commands using deterministic query
views and a disposable export root. All seven resulting file hashes matched
the before-code probe; both the Chat handler and neutral Runtime module came
from the installed venv.

## Remaining gates

Freeze an exact commit and obtain fresh-context, read-only independent review
of the directive, authority manifest, candidate diff and evidence. The
repository-wide documentation lifecycle check has a known unrelated failure
on six absolute `/private/tmp/telem-01/review` links in an unchanged telemetry
report. Board/dashboard validation passed for 34 tasks, authority JSON
parsed, and 219 changed-document local links resolved. Exact staged paths
and whitespace are checked before candidate freeze. No push, PR, merge, release,
installed TUI terminal UAT or maintainer acceptance is claimed.
