# TUI-N01B-05 before-code single-file export characterization

**Date/source:** 2026-10-19; clean `feature/friday-tui` at
`887e43a02d7213e65436b1d85bfafbe255ac865c`. The N01B-04 product
source is unchanged from independently reviewed candidate `abeeb895` and
pushed exact-source Ubuntu commit `4b2aadd2`. This is read-only planning
evidence, not approval or validation of N01B-05 code.

## Current ownership and proposed boundary

`friday_chat.commands.transcript._write_current_session_export` owns the
four fixed current-session output files:
`friday_current_session.csv`, `friday_current_session.jsonl`,
`friday_current_session_training.jsonl`, and
`friday_current_session.md`. `/export` normalizes `md` to `markdown`
and validates the selected format before querying the current session and
entries. The private writer calls Chat's public `export_directory(context)`,
then `_safe_export_path` for the selected filename, then `Path.write_text`
with UTF-8. It supplies configured user/assistant names for Markdown and
returns Chat-owned `TranscriptExportResult` with one file and the entry
count. A fixed filename is overwritten on a repeated export.

`_write_context_log_export` uses the same root/path seam for
`friday_prompts.json`, writes the N01B-03 neutral serializer's text in
UTF-8 and returns Chat-owned `TranscriptExportResult` with one session and
the context-log count. The `/export-prompts` handler does not create the
file if there are no captured logs. Both handlers catch query, path and
write failures and return the established generic export error.

N01B-03 already supplies the pure Runtime serializers; N01B-04 supplies
neutral export-root and containment helpers. The next proposed subunit
moves only the final single-file serialization-and-write effects into a
neutral Runtime module. Chat still chooses format, session, filename,
configured display names and safe destination; it wraps the neutral write
in its existing result and message. The neutral writer must accept a
caller-prevalidated destination and make no directory, policy or
configuration choice. A future TUI caller must compose it with
`safe_export_path`; this unit does not add that caller.

The two-file `/transcript export` writer is separate: it creates a
microsecond UTC directory with `exist_ok=False` and writes
`sessions.csv` and `entries.csv` without rollback after a partial
failure. It remains Chat-owned for N01B-05. Chat's public
`export_directory` also serves `/context --file` and `/prompt --file`;
those file effects remain outside this subunit.

## Protected behavior and before-code checks

[The Chat compatibility test](../../../../../packages/friday-chat/tests_chat/test_transcript_query_facade.py)
requires `TranscriptExportResult.__module__ == "friday_chat.transcripts"`
and no export-result type in `friday_runtime.transcript_views`. Therefore
moving or aliasing that class is excluded. [The path-delegation
test](../../../../../packages/friday-chat/tests_chat/test_transcript_export_path_delegation.py)
monkeypatches Chat's `safe_export_path` import and observes its calls
for all export commands. Chat must keep those calls before the neutral
single-file writer runs. Existing [export-format
tests](../../../../../packages/friday-chat/tests_chat/test_transcript_export_format_delegation.py)
pin all seven UTF-8 file hashes on fake and disposable SQLite backends,
default/configured roots, empty CSV/JSONL/Markdown, absence of a prompt
file with no logs, and generic errors on root/write failure. The current
single-file outputs account for five of those seven hashes; the other
two belong to the deferred all-session export.

The unchanged Runtime transcript, Chat export/command/session and full
protected `friday-cli` comparison passed **239 tests**:

```text
UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache LITELLM_LOCAL_MODEL_COST_MAP=true PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' uv run --frozen --offline pytest -q packages/friday-runtime/tests_runtime/test_transcript_export_format.py packages/friday-runtime/tests_runtime/test_transcript_export_paths.py packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-runtime/tests_runtime/test_transcript_queries.py packages/friday-chat/tests_chat/test_transcript_export_format_delegation.py packages/friday-chat/tests_chat/test_transcript_export_path_delegation.py packages/friday-chat/tests_chat/test_transcript_query_facade.py packages/friday-chat/tests_chat/test_transcript_query_adapter_delegation.py packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_session_identity.py packages/friday-chat/tests_chat/test_session_memory_commands.py packages/friday-chat/tests_chat/test_command_registry.py packages/friday-cli/tests_cli
```

The proposed directive needs direct neutral write tests for exact bytes,
overwrite, empty content, missing parent and propagated write errors. Chat
delegation must retain all five frozen single-file hashes, file names,
results, path hooks and errors, while the two-file and shared
`/context --file` / `/prompt --file` paths remain protected. This
before-code result is not installed TUI terminal UAT or an N01B-05
exact-source Linux result.
