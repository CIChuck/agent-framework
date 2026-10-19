# TUI-N01B-06 before-code all-session export characterization

**Date/source:** 2026-10-19; clean `feature/friday-tui` at
`010849f531d2bbc08569d1825eec7e34f4db5489`. N01B-05 product source
remains byte-identical to independently reviewed `c773f272`; its
authorized exact-source Ubuntu gate is independently VERIFIED. This is
read-only planning evidence, not approval or validation of N01B-06 code.

## Existing behavior and proposed boundary

`friday_chat.commands.transcript._export_all_sessions` queries at most 1,000
non-archived sessions, then queries each session's entries before making an
export directory. It catches query, path, directory and write failures and
returns `Unable to export transcript data.`. On success the command reports
session and entry counts and the created directory.

`_write_all_session_export` calls Chat's public `export_directory(context)`
to resolve/create the configured or default root. It generates a
microsecond UTC `transcript-export-YYYYMMDDTHHMMSSffffffZ` directory name,
calls Chat's `_safe_export_path` for that directory, and performs
`directory.mkdir(parents=False, exist_ok=False)`. Only after creating the
directory does it call `_safe_export_path` for `sessions.csv` and
`entries.csv`. It flattens queried session/entry views in their existing
order, writes the N01B-03 serializers' UTF-8 text to `sessions.csv` first
and `entries.csv` second, then returns the Chat-owned
`TranscriptExportResult` with both paths and counts. N01B-04 already
provides neutral root/path rules; N01B-05 provides neutral single-file
writers. This remaining directory-create and two-file write sequence is the
proposed N01B-06 extraction into the Runtime file-effects module.

Chat must continue to choose the timestamp/name, resolve each destination
through its existing path hook, collect and flatten data, wrap the result,
and format the command output. The neutral effects should take caller-
prevalidated paths and typed views, with no Chat/CLI import, query,
filename choice, result class, cleanup or retry. The TUI has no caller yet.

The unchanged [Chat path-delegation test](../../../../../packages/friday-chat/tests_chat/test_transcript_export_path_delegation.py)
requires the three Chat path-hook calls. The unchanged [export-format
test](../../../../../packages/friday-chat/tests_chat/test_transcript_export_format_delegation.py)
pins `sessions.csv` and `entries.csv` hashes as two of seven export files on
fake and disposable SQLite stores. [Production command
tests](../../../../../packages/friday-chat/tests_chat/test_transcript_production_commands.py)
cover archived-session exclusion, empty exports, outputs and failures.
`TranscriptExportResult` remains in `friday_chat.transcripts` with its
current identity, fields and defaults. The shared Chat export root also
serves `/context --file` and `/prompt --file`; they are outside this unit.

## Before-code checks

The unchanged focused Runtime transcript, Chat export/command/session and
full protected `friday-cli` comparison passed **253 tests**:

```text
UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache LITELLM_LOCAL_MODEL_COST_MAP=true PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' uv run --frozen --offline pytest -q packages/friday-runtime/tests_runtime/test_transcript_export_files.py packages/friday-runtime/tests_runtime/test_transcript_export_format.py packages/friday-runtime/tests_runtime/test_transcript_export_paths.py packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-runtime/tests_runtime/test_transcript_queries.py packages/friday-chat/tests_chat/test_transcript_export_file_delegation.py packages/friday-chat/tests_chat/test_transcript_export_format_delegation.py packages/friday-chat/tests_chat/test_transcript_export_path_delegation.py packages/friday-chat/tests_chat/test_transcript_query_facade.py packages/friday-chat/tests_chat/test_transcript_query_adapter_delegation.py packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_session_identity.py packages/friday-chat/tests_chat/test_session_memory_commands.py packages/friday-chat/tests_chat/test_command_registry.py packages/friday-cli/tests_cli
```

A read-only-source, disposable `/private/tmp` probe called the current
private writer with a fixed UTC timestamp. The second call raised
`FileExistsError` and retained the first two files. Injecting a
`PermissionError` for the second `Path.write_text` retained the new
directory and completed `sessions.csv` while leaving `entries.csv` absent.
Injecting a failure at Chat's `entries.csv` path hook retained the created
directory with no files and confirmed the directory, sessions, entries
path-call order.
The probe modified no repository file. Those non-atomic effects are part of
the current compatibility boundary; the proposed unit must not add cleanup
or overwrite on collision.

The proposed directive needs direct Runtime tests for exact two-file bytes,
zero sessions, directory creation flags/collision, write order and
partial-failure effects. Chat delegation tests must retain filenames,
timestamp format, safe-path hook order, query order/limit/archival policy,
result identity/counts, exact output/error prose and the two frozen file
hashes, while all single-file exports and shared `/context --file` and
`/prompt --file` behavior remain protected. This baseline is not installed
TUI terminal UAT or an N01B-06 exact-source Ubuntu result.
