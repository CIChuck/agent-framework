# TUI-N01B-04 before-code export destination characterization

**Date/source:** 2026-10-19; clean `feature/friday-tui` at
`3b91c5b55a567fd5225a6430bf27fbaef35fefbf`. The reviewed N01B-03
product source is unchanged from the pushed `f7950581` source. This is
read-only planning evidence, not approval or validation of N01B-04 code.

## Current ownership and boundary

`friday_chat.commands.transcript.export_directory(context)` reads
`context.runtime.config.transcript.export_directory` when truthy, otherwise
uses `./exports`; it resolves the path with `strict=False`, creates the root
with `parents=True, exist_ok=True`, and returns the resolved `Path`.
The private `_safe_export_path(root, *parts)` resolves root and candidate and
raises `ValueError("export path escaped configured root")` if the candidate
is outside. It does not write a file.

All three transcript export writers call these helpers. Current-session and
prompt exports write fixed filenames directly under the root; all-session
export creates a `transcript-export-<UTC timestamp>` subdirectory with
`exist_ok=False`, then writes `sessions.csv` and `entries.csv`. Chat owns
session/format choice, filenames, clock, writes, `TranscriptExportResult`,
counts and handler errors. [N01B-03](VAL-N01B-03-prepush-782dedbb.md)
already moved only the file *content* serializers into Runtime.

`friday_chat.commands.registry` imports the public Chat
`export_directory()` for `/context --file` and `/prompt --file`. That shared
root behavior is a protected compatibility seam even though neither command
is a transcript export. `friday_chat.transcripts.TranscriptExportResult`
must retain its Chat identity and defaults, as checked by the existing
query-facade test. The next proposed subunit extracts only root creation and
safe child-path resolution to Runtime. It leaves names and file writes for a
later directive.

## Protected behavior and before-code checks

Existing [Chat export tests](../../../../../packages/friday-chat/tests_chat/test_transcript_export_format_delegation.py)
assert seven exact UTF-8 hashes, command outputs, default/configured roots,
empty exports, no prompt-log file, and root/write failures on fake and
disposable SQLite stores. The [session/memory command tests](../../../../../packages/friday-chat/tests_chat/test_session_memory_commands.py)
assert `/context --file` and `/prompt --file` use the configured root.
Source inspection confirms `Path.write_text` overwrites fixed-name files;
the all-session directory uses a microsecond UTC name with `exist_ok=False`
(a name collision raises), and is not cleaned up if a later write fails.
These effects are to remain in
Chat for N01B-04.

A disposable `/private/tmp` probe of the current `_safe_export_path`
confirmed a direct child path, rejected `../outside.csv`, and rejected an
existing child symlink to a file outside the root; both rejections used the
exact `ValueError` text above. It used no existing Friday state or provider.

The unchanged Runtime transcript, Chat transcript/command/context and full
protected `friday-cli` comparison passed **226 tests**:

```text
UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' LITELLM_LOCAL_MODEL_COST_MAP=true uv run --frozen --offline pytest -q packages/friday-runtime/tests_runtime/test_transcript_export_format.py packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-runtime/tests_runtime/test_transcript_queries.py packages/friday-chat/tests_chat/test_transcript_export_format_delegation.py packages/friday-chat/tests_chat/test_transcript_query_facade.py packages/friday-chat/tests_chat/test_transcript_query_adapter_delegation.py packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_session_identity.py packages/friday-chat/tests_chat/test_session_memory_commands.py packages/friday-chat/tests_chat/test_command_registry.py packages/friday-cli/tests_cli
```

The proposed directive needs explicit negative tests for traversal, symlink
escape, root-as-file, relative cwd anchoring and the registry's two shared
exports. This before-code result is not installed TUI terminal UAT or an
exact-source Linux result for N01B-04.
