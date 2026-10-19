# TUI-N01B-03 independent local review

**Verdict:** `VERIFIED` for the bounded N01B-03 local work unit. No findings
require changes.

**Reviewer and mode:** Fresh-context Codex validation subagent, GPT-6 family
(exact version unavailable), read-only full work-unit review on 2026-10-19.
The reviewer did not edit, commit or push. The handoff contained pinned
authority, the candidate and required checks, but not the builder's private
reasoning. The reviewer reproduced the material checks independently.

**Candidate:** `782dedbbd0ee4896288793286080180a6a70c04a` on
`feature/friday-tui`, clean at review. **Approved pre-code base:**
`23fc6d16f5ed3bab1d4625f0329aeb0ad4a7c920`. The reviewed diff was
`23fc6d16..782dedbb`; the seven-file before-code probe was made at
`c1e38d944452ff26edd5a1fa4302fe5d9a2ccfc6`.

## Pinned authority and scope

The reviewer read [AGENTS.md](../../../../../AGENTS.md), the engineering and
independent-validation policies, the authority manifest, the approved exact
directive, the characterization, plans, builder report and candidate diff. All
six supplied SHA-256 pins matched the candidate:

| Input | SHA-256 |
| --- | --- |
| [Authority manifest](../authority.json) | `87758747a623123f7791a7bb3751ac90e24ac83fe6c24def7af0c5028c839d22` |
| [Approved exact directive](../directives/CD-TUI-N01B-03-neutral-transcript-export-serialization.md) | `e83625e66202c1e5ce71f91195030b77f3520823e79dec6f035f830728db8163` |
| [Before-code characterization](N01B-03-before-code-characterization.md) | `8a5f9f182bef51d992015d53bb71bca4913b0788c2dca8070f6d262709345db7` |
| [Replacement plan](../replacement-plan.md) | `8ef8b4e293751b98242461855fc6d6c83148266c28fc36783e9ef7878d1ce4a2` |
| [Neutral capability map](../neutral-capability-map.md) | `89cabc4a5921714fc08904b3193f1c31f1007706a9ae57aff75fd84bef3cdc2a` |
| [Board](../../../board.yaml) | `84c5fbdf3bac8e68aff13ce17a2f67b1c54a5595e5a1ff623546708c19bf246b` |

The diff changes only the four approved Runtime/Chat source/test paths and
scoped TUI packet, board and dashboard evidence. The six Runtime serializers
depend on Runtime transcript views and the standard library, with no Chat or
CLI import. Chat retains session and path selection, UTF-8 writes, names,
counts, command results and errors while delegating content serialization.
Protected Chat and `friday-cli` tests are unchanged.

## Independent results

The reviewer ran the focused and protected comparison (**204 passed**), full
Runtime (**356 passed**), full Chat (**856 passed, five skipped**) and the
unchanged `friday-cli` comparison. The full Runtime and Chat suites needed
local loopback access for disposable `127.0.0.1` fixtures; initial sandbox
bind failures cleared on rerun (nine Runtime and 13 Chat fixture failures or
errors in the restricted attempts). New tests cover the frozen bytes, empty and
multiple records, ordering, Unicode, nulls, quoting, command results,
configured and default roots, and failure paths.

The independent test commands were:

```sh
UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' LITELLM_LOCAL_MODEL_COST_MAP=true uv run --frozen --offline pytest -q packages/friday-runtime/tests_runtime/test_transcript_export_format.py packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-runtime/tests_runtime/test_transcript_queries.py packages/friday-chat/tests_chat/test_transcript_export_format_delegation.py packages/friday-chat/tests_chat/test_transcript_query_facade.py packages/friday-chat/tests_chat/test_transcript_query_adapter_delegation.py packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_session_identity.py packages/friday-cli/tests_cli
UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' LITELLM_LOCAL_MODEL_COST_MAP=true uv run --frozen --offline pytest -q --tb=short packages/friday-runtime/tests_runtime
UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' LITELLM_LOCAL_MODEL_COST_MAP=true uv run --frozen --offline pytest -q --tb=short packages/friday-chat/tests_chat
```

Ruff lint, targeted Mypy, format checks on the new files, the builder's
changed-Chat-range format check, `uv lock --check --offline`, board validation, dashboard render check,
261 changed-document local links and `git diff --check` passed. Whole-file
Ruff format remains red on the same untouched Chat lines at base and
candidate. The repository-wide documentation lifecycle check remains red
only on six unchanged absolute telemetry-report links.

The independent static and board commands were `uv run --frozen --offline
ruff check` and `uv run --frozen --offline mypy` on the four approved
source/test paths, `uv run --frozen --offline ruff format --check` on the three
new files, `uv lock --check --offline`, `uv run --frozen --offline python
scripts/friday-dev-board.py validate`, `uv run --frozen --offline python
scripts/friday-dev-board.py render --check`, and `git diff --check
23fc6d16..782dedbb`. The `uv` commands used
`UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache`.

Fresh offline Runtime and Chat wheels were built. A Runtime-only isolated
install had no Chat or CLI import available, passed `uv pip check` for 111
packages and matched all seven frozen UTF-8 export digests. After installing
Chat, `uv pip check` passed for 127 packages and installed Chat commands
matched all seven digests. The builder's separate isolated resolve contained
130 packages; both installed environments passed dependency checks and the
same byte comparison. An initial isolated import attempted LiteLLM's optional
cost-map fetch, which the network restriction blocked; the guarded
Runtime-only rerun passed without that attempt. The [builder report](N01B-03-local-checks.md)
contains its commands and fixture details.

The reviewer independently built `friday-runtime` and `friday-chat` with
`uv build <package> --wheel --offline`, installed those wheels with `uv pip
install --offline --python <isolated-venv-python> --find-links
/private/tmp/friday-tui-n01b03-wheels <wheel>`, then ran `uv pip check` and
`python -I` probes from `/private/tmp` with
`LITELLM_LOCAL_MODEL_COST_MAP=true`. The unchanged dependency wheels came
from the builder's local wheel directory; the two changed wheels were freshly
built by the reviewer.

## Boundary and remaining gates

This verdict verifies N01B-03 local source and installed-wheel behavior at
the pinned candidate. It does not establish an exact-source Ubuntu run,
installed TUI terminal UAT, full TUI parity, maintainer acceptance or external
delivery. A separately authorized non-force feature-branch push is needed for
exact-source Ubuntu execution. This post-review report and scoped packet/board
status updates do not alter the reviewed product source.
