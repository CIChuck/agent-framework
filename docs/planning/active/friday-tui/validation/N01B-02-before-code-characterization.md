# TUI-N01B-02 before-code transcript-query adapter characterization

**Date/source:** 2026-10-18; `feature/friday-tui` at
`f0e0786f69243513b9e35d66dc271c2c5f10afab` (clean worktree).

**Evidence limit:** Read-only source inspection and unchanged local tests for a
proposed adapter extraction. This is not approval to edit product code,
independent validation of N01B-02, installed TUI UAT or a Linux result for a
future candidate.

N01B-01 placed the three frozen views and four-method `TranscriptQueryStore`
protocol in `friday_runtime.transcript_views`. Chat re-exports those exact
objects. Its `FrameworkTranscriptAdapter` still combines read-only query
methods with Chat-specific writes, configuration, MCP provenance and session
finalization. Moving that whole adapter would bring Chat policy into Runtime.
The next separable effect is the four persisted query methods and their private
mapping, archive-scan and timestamp-sort helpers.

| Current method | Observed behavior to preserve |
| --- | --- |
| `query_sessions(*, limit=1000, include_archived=False)` | Calls `list_sessions` with `min(max(limit, 0), 1000)` and the requested archive flag. When archived sessions are included, scans every non-archived session in 1000-row pages to derive archive flags. Sorts views by UTC-normalized start time and session ID, descending. |
| `query_session(session_id)` | Returns `None` for a missing exact ID. Otherwise maps the persisted session and derives its archive flag from the full non-archived-ID scan. |
| `query_entries(session_id)` | Reads 1000-row pages until a short page, maps all returned entries, and sorts by turn number, UTC-normalized timestamp and entry ID, ascending. |
| `query_context_logs(session_id)` | Calls `get_context_log_for_session` once with `limit=100_000`, maps the returned rows, and sorts by turn number, UTC-normalized capture time and log ID, ascending. This is an existing cap, not unlimited paging. |

The underlying `SQLiteTranscriptStore` has the needed read APIs and is already
a declared `friday-runtime` dependency through `friday-framework-transcript`.
The older broad `friday_transcript.stores.protocol.TranscriptStore` does not
declare `include_archived` or context-log reads, so it is not a suitable typed
dependency for this extraction. A narrow Runtime read-store protocol can
describe only the four low-level operations actually used, while a disposable
SQLite store and synthetic read store supply independent behavior tests.

`FrameworkTranscriptAdapter` is instantiated with a concrete SQLite store,
`FridayChatConfig` and session ID. Its public four query signatures must stay
unchanged. The Chat command handlers still own `/sessions` and `/transcript`
formatting and export effects; its fake transcript store stays in Chat. The
private `_transcript_*_view`, `_datetime_sort_key` and
`_non_archived_session_ids` helpers have no other references in Chat source or
tests at this source revision. No product or test source was edited for this
characterization.

Before-code command, with network-free fake/disposable-store fixtures:

```text
UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' LITELLM_LOCAL_MODEL_COST_MAP=true uv run --frozen pytest -q packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_session_identity.py packages/friday-cli/tests_cli
```

Result: **171 passed**. These unchanged tests cover persisted and fake query
stores, archived/missing sessions, entries/context logs, export commands,
session identity and the protected `friday-cli` suite. The baseline does not
yet prove a neutral adapter's direct behavior, installed package isolation or
TUI terminal UAT.
