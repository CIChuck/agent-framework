# TUI-N01B-03 before-code transcript-export characterization

**Date/source:** 2026-10-19; clean `feature/friday-tui` at
`c1e38d944452ff26edd5a1fa4302fe5d9a2ccfc6`. N01B-02's reviewed
product source is unchanged from pushed `07177e6c`. This is planning and
before-code evidence, not approval or validation of N01B-03 construction.

## Current ownership and behavior

`friday_chat.commands.transcript` still serializes every export and writes its
files. Its private `_csv_text`, `_entry_csv_row`, `_entry_json_record` and
`_format_transcript_markdown` are used only by its export writers. The writers
also choose sessions, formats, paths, names, counts, directory creation and
errors; those are Chat command/file effects. `TranscriptExportResult` stays in
`friday_chat.transcripts`. The existing Runtime transcript views and query
adapter are independent of Chat and can supply typed serializer inputs.

| Export content | Current byte behavior to preserve |
| --- | --- |
| All-session `sessions.csv` | Eight columns in current order; CSV quotes every field and uses LF rows. `None` user/end values become empty fields; booleans use Python `True`/`False`. An empty selection still writes the header and LF. |
| All-session `entries.csv` and `/export csv` | The same eight entry columns, quote-all CSV with LF rows. Nullable message/model/token/latency fields become empty fields. An empty entry set still writes the header and LF. |
| `/export jsonl` | One sorted-key, UTF-8 JSON record per entry, joined by LF with no final LF. Nullable values remain JSON null. Empty entries write zero bytes. |
| `/export training` | One sorted-key JSON `messages` record per entry with user then assistant roles. Missing message text becomes `""`. LF joins records with no final LF; empty entries write zero bytes. |
| `/export markdown` or `/export md` | Transcript heading, ordered turn headings and configured Chat user/assistant names; `None` messages become empty text. The output is right-trimmed and ends in exactly one LF. |
| `/export-prompts` | A JSON list in query order with `session_id`, `turn_number`, `entry_id`, ISO `captured_at`, `prompt`, and nullable `raw_response`; `ensure_ascii=False`, sorted keys and two-space indent, no final LF. The handler currently does not write a file when no context logs exist. |

All writers use UTF-8. The all-session writer creates a timestamped
`transcript-export-*` directory containing `sessions.csv` and `entries.csv`;
the other writers use fixed filenames under the configured export root (or
`./exports`). `_safe_export_path` keeps generated files under that root.
Existing handler usage, selected/current session policy, archive filtering,
record counts, error messages and file effects are outside the proposed pure
serialization extraction.

## Frozen comparison probe

A read-only local probe invoked the existing private writers using one
disposable `/private/tmp` directory and these Runtime views: session `s-α`,
`user_id=None`, UTC `2026-01-02T03:04:05+00:00`, model `m`, one turn, zero
tokens, active; entry `e-1`, user text `Hi, "Friday"` followed by LF and
`again`, assistant `Voilà`, and nullable model/token/latency; context log
`l-1` with prompt `raw` followed by LF and `π`, nullable response. Chat
display names were `Chuck` and `FridayX`. The probe used no provider or
existing Friday state. SHA-256 is over the exact UTF-8 file bytes:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `sessions.csv` | 161 | `f259ccf80cb97232e5afaefbba5832a72c997351e82a16084300dc65e42134b2` |
| `entries.csv` | 195 | `4d918ce79fb4525be47f83b65b8fca830614e9a88131736a7bb9bf0e1288cd0c` |
| `friday_current_session.csv` | 195 | `4d918ce79fb4525be47f83b65b8fca830614e9a88131736a7bb9bf0e1288cd0c` |
| `friday_current_session.jsonl` | 235 | `243026aa856dffcb3bcdd700c391f0c1cda1dfc4ed3a40e8970f1c5b707fdb8c` |
| `friday_current_session_training.jsonl` | 112 | `998ffb447b36d5b5e4b0b6e8698447c84fa1c4da48925acb2a2dcd1bb746a09d` |
| `friday_current_session.md` | 82 | `515f2f3516ae6ea8ac8aa70ca19e4a4142939645afa07544d7c9bdf7e36f6c5c` |
| `friday_prompts.json` | 180 | `5b267f343e4fd44207121f0f7142cf4d673459ce91134fb86277c75610b675bf` |

The probe is one nonempty comparison. Construction tests must add exact
expected text/bytes for empty, multiple-record, quoting, Unicode, nullable
and configured-name cases; matching only these hashes is insufficient.

A second disposable probe with no sessions and no entries confirmed that
both all-session CSV files and current-session CSV contain only their quoted
headers plus LF; current-session JSONL and training JSONL are empty strings;
and Markdown for session `empty` is exactly
`"# Transcript: empty\n"`. The Chat `/export-prompts` handler does not call its
writer for an empty context-log query.

The unchanged focused Runtime query/view, Chat transcript/query/export and
entire protected `friday-cli` suites passed **195 tests** with a network-free
test guard:

```text
UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' LITELLM_LOCAL_MODEL_COST_MAP=true uv run --frozen pytest -q packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-runtime/tests_runtime/test_transcript_queries.py packages/friday-chat/tests_chat/test_transcript_query_facade.py packages/friday-chat/tests_chat/test_transcript_query_adapter_delegation.py packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_session_identity.py packages/friday-cli/tests_cli
```

This baseline proves current behavior on local fake/disposable data. It is
not installed TUI terminal UAT or a Linux result for an N01B-03 candidate.
