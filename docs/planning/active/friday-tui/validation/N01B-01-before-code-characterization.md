# TUI-N01B-01 before-code transcript-query characterization

**Date/source:** 2026-10-18; `feature/friday-tui` at
`d7be6459da29b8f46e270c1e1cb38772ded020cc`.

**Authority/evidence limit:** Read-only baseline for a proposed neutral
transcript-query contract. No N01B product code, TUI package, live provider,
existing local Friday state or user UAT was changed or verified.

`friday_chat.transcripts` currently owns three frozen, non-slot dataclasses and
the asynchronous `TranscriptQueryStore` protocol. The proposed extraction is
limited to these four objects. `TranscriptExportResult` and every export/file
effect remain Chat-owned in this slice.

| Object | Before-code shape that must survive the extraction |
| --- | --- |
| `TranscriptSessionView` | Positional fields `session_id`, `user_id`, `started_at`, `ended_at`, `model_name`, `total_turns`, `total_tokens`; `archived=False`. |
| `TranscriptEntryView` | Positional fields `entry_id`, `session_id`, `turn_number`, `user_message`, `assistant_message`, `timestamp`; `model_name=None`, `total_tokens=None`, `latency_ms=None`. |
| `TranscriptContextLogView` | Positional fields `log_id`, `session_id`, `turn_number`, `entry_id`, `raw_prompt`, `raw_response`, `captured_at`; no defaults. |
| `TranscriptQueryStore` | Four `async` methods: `query_sessions(*, limit=1000, include_archived=False)`, `query_session(session_id)`, `query_entries(session_id)`, `query_context_logs(session_id)`; view return types and `None` case as in the current source. |

All three views are frozen dataclasses with generated equality, `repr` and
positional construction. `friday_chat.transcripts.__all__` currently lists
`TranscriptContextLogView`, `TranscriptEntryView`,
`TranscriptExportResult`, `TranscriptQueryStore` and
`TranscriptSessionView` in that order. Historical pickle global lookups for
all four proposed objects resolve through `friday_chat.transcripts`; after a
move, that old path must still resolve to the same neutral objects. The owning
`__module__` will necessarily change, so byte-for-byte pickle output and
module-introspection identity are not parity claims.

Current consumers are `friday_chat.runtime`, its fake transcript store, the
`FrameworkTranscriptAdapter`, and Chat transcript handlers. The production
adapter still owns persistence, query ordering and limits, while the handlers
still own `/sessions` and `/transcript` formatting and export. Moving that
adapter or its export effects would cross additional configuration, provenance
and resource ownership boundaries; those require later directives.

Before-code command, using the existing fake/provider-safe test setup:

```text
UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' LITELLM_LOCAL_MODEL_COST_MAP=true uv run --frozen pytest -q packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_session_identity.py packages/friday-cli/tests_cli
```

Result: **171 passed**. These unchanged tests cover persisted fake/real-adapter
transcript query behavior, export commands, session identity and the protected
`friday-cli` suite. They establish the comparison baseline, not N01B
implementation, installed-package isolation, Linux TUI UAT or independent
validation.
